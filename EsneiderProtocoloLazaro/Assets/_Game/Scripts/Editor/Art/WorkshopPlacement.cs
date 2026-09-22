using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Esneider.Core;
using Esneider.Core.Data;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using Object=UnityEngine.Object;

namespace Esneider.EditorTools
{
    public static class WorkshopPlacement
    {
        public static readonly string[] Assets={"OBJ-019_TaladroFijo","OBJ-023_BandejaPiezas","OBJ-031_BombaIndustrial","OBJ-032_GeneradorLocal","OBJ-034_ValvulaBridada","OBJ-035_Extintor","OBJ-036_SoldadorCarrito","OBJ-037_Herramientas"};
        const string Dressing="Workshop_EX14_Dressing";
        static bool Overlaps(float x,float z,float w,float d,float px,float pz,float radius)
        {
            float dx=px-Mathf.Clamp(px,x-w*.5f,x+w*.5f), dz=pz-Mathf.Clamp(pz,z-d*.5f,z+d*.5f);
            return dx*dx+dz*dz<radius*radius;
        }
        public static string Apply(LevelPlan plan,string region,Transform furniture)
        {
            if(region!="REG-S2") return "";
            var prefabs=Assets.ToDictionary(id=>id,id=>AssetDatabase.LoadAssetAtPath<GameObject>(FurnitureReview.Prefab(id)));
            if(prefabs.Values.Any(p=>!p)) return "EX14: waiting for all workshop prefabs";
            var bench=furniture.GetComponentsInChildren<Transform>(true).FirstOrDefault(t=>t.name=="M023_EX13");
            var generator=furniture.GetComponentsInChildren<Transform>(true).FirstOrDefault(t=>t.name=="M034_generador" || t.name=="M034_EX14");
            if(!bench || !generator) throw new InvalidOperationException("Workshop requires M023 bench and M034 generator placement");
            var room=plan.Room("S2-R06");var floor=plan.Floor(room.floor);var origin=floor.origin.ToVector3();
            void ValidateGround(string label,float x,float z,float width,float depth)
            {
                if(x-width*.5f<room.x+.1f || x+width*.5f>room.x+room.w-.1f || z-depth*.5f<room.z+.1f || z+depth*.5f>room.z+room.d-.1f) throw new InvalidOperationException(label+" outside workshop");
                var reserves=new List<(string id,float x,float z,float r)>();
                foreach(var p in plan.pickups.Where(p=>p.space==floor.id)) reserves.Add((p.id,p.x,p.z,.65f));
                foreach(var p in plan.documents.Where(p=>p.space==floor.id)) reserves.Add((p.id,p.x,p.z,.65f));
                foreach(var p in plan.spawns.Where(p=>p.space==floor.id)) reserves.Add((p.id,p.x,p.z,.6f));
                foreach(var p in plan.mechanisms.Where(p=>p.space==floor.id)) reserves.Add((p.id,p.x,p.z,1.2f));
                foreach(var p in plan.checkpoints.Where(p=>p.space==floor.id)) reserves.Add((p.id,p.x,p.z,1.5f));
                foreach(var p in plan.doors.Where(p=>p.floor==floor.id)) reserves.Add((p.id,p.x,p.z,p.width*.5f+.6f));
                foreach(var reserve in reserves) if(Overlaps(x,z,width,depth,reserve.x,reserve.z,reserve.r)) throw new InvalidOperationException(label+" invades "+reserve.id);
            }
            ValidateGround("drill",30.6f,7.5f,.5f,.6f);ValidateGround("welder",33,8.2f,.87f,.5f);
            var old=furniture.Find(Dressing);if(old) Object.DestroyImmediate(old.gameObject);
            var group=new GameObject(Dressing).transform;group.SetParent(furniture);group.localPosition=Vector3.zero;group.localRotation=Quaternion.identity;
            var records=new List<string>();
            GameObject Place(string asset,string name,Vector3 position,float yaw,Transform parent)
            {
                var go=(GameObject)PrefabUtility.InstantiatePrefab(prefabs[asset],parent);go.name=name;
                go.transform.SetPositionAndRotation(position,Quaternion.Euler(0,yaw,0));
                records.Add(name+": "+asset+" "+position);return go;
            }
            Place(Assets[0],"EX14_Drill",origin+new Vector3(30.6f,0,7.5f),270,group);
            Place(Assets[6],"EX14_Welder",origin+new Vector3(33,0,8.2f),0,group);
            Place(Assets[1],"EX14_PartsTray",bench.position+new Vector3(-2.3f,.9002f,0),0,group);
            Place(Assets[7],"EX14_ToolSet",bench.position+new Vector3(1.7f,.9002f,0),0,group);
            Place(Assets[4],"EX14_SpareValve",bench.position+new Vector3(-.3f,.9002f,0),0,group);
            Physics.SyncTransforms();
            var mount=origin+new Vector3(32.5f,1.1f,2.4f);RaycastHit wall;
            if(!Physics.Raycast(mount+Vector3.up*.22f,Vector3.back,out wall,.8f,GameLayers.CoverMask,QueryTriggerInteraction.Ignore)) throw new InvalidOperationException("No wall behind extinguisher bracket");
            mount=wall.point+wall.normal*.1055f-Vector3.up*.22f;
            Place(Assets[5],"EX14_WallExtinguisher",mount,180,group);
            var generatorPosition=generator.position-(generator.name=="M034_generador" ? Vector3.up*plan.furniture.First(f=>f.id=="M034").h*.5f : Vector3.zero);
            var machinery=new GameObject("M034_EX14").transform;machinery.SetParent(furniture);machinery.SetPositionAndRotation(generatorPosition,Quaternion.identity);
            Place(Assets[3],"EX14_Generator",generatorPosition+new Vector3(0,0,-.6f),0,machinery);
            Place(Assets[2],"EX14_ServicePump",generatorPosition+new Vector3(0,0,1.2f),0,machinery);
            Object.DestroyImmediate(generator.gameObject);
            foreach(var t in group.GetComponentsInChildren<Transform>()) { t.gameObject.layer=GameLayers.WorldStatic;t.gameObject.isStatic=true; }
            foreach(var t in machinery.GetComponentsInChildren<Transform>()) { t.gameObject.layer=GameLayers.WorldStatic;t.gameObject.isStatic=true; }
            return string.Join("\n",records);
        }
        public static string ApplyExisting()
        {
            const string path="Assets/_Game/Scenes/Regions/REG-S2.unity";
            var scene=SceneManager.GetSceneByPath(path);bool opened=!scene.IsValid() || !scene.isLoaded;
            if(opened) scene=EditorSceneManager.OpenScene(path,OpenSceneMode.Additive);
            else if(scene.isDirty) throw new InvalidOperationException("Review unsaved S2 edits before placing workshop models");
            try
            {
                var plan=JsonUtility.FromJson<LevelPlan>(File.ReadAllText("Assets/_Game/Data/LevelPlan/bunker_plan.json"));
                var root=scene.GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<Transform>(true)).Single(t=>t.name=="Furniture");
                var report=Apply(plan,"REG-S2",root);EditorSceneManager.SaveScene(scene);
                File.WriteAllText("../SourceArt/_evidence/EX-14/placements.txt",report);return report;
            }
            finally { if(opened) EditorSceneManager.CloseScene(scene,true); }
        }
    }
}
