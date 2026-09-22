using System.Collections.Generic;
using System.IO;
using System.Linq;
using Esneider.Core;
using Esneider.Core.Data;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Esneider.EditorTools
{
    public static class FurniturePlacement
    {
        public static bool TryPlace(PlanFurniture f, Vector3 world, Transform parent)
        {
            string asset; int count=1; float spacing=0, angle=0; bool alongZ=false;
            switch(f.id)
            {
                case "M014": asset="OBJ-013_VigaDeformada"; break;
                case "M023": asset="OBJ-017_BancoTrabajo"; count=3; spacing=2; angle=180; break;
                case "M025": asset="OBJ-028_EstanteriaIndustrial"; count=3; spacing=2.5f; angle=90; alongZ=true; break;
                case "M030": case "M031": asset="OBJ-028_EstanteriaIndustrial"; count=4; spacing=2.5f; angle=f.id=="M030" ? 270 : 90; alongZ=true; break;
                case "M022": case "M039": asset="OBJ-030_ContenedorTecnico"; break;
                case "M027": asset="OBJ-038_MesaOficina"; angle=180; break;
                case "M029": asset="OBJ-039_SillaUsada"; break;
                case "M063": case "M064": asset="OBJ-072_RackControl"; count=7; spacing=.8f; angle=f.id=="M063" ? 270 : 90; alongZ=true; break;
                default: return false;
            }
            var prefab=AssetDatabase.LoadAssetAtPath<GameObject>(FurnitureReview.Prefab(asset));
            if(!prefab) return false;
            var group=new GameObject(f.id+(f.id=="M014" ? "_EX19" : "_EX13")); group.transform.SetParent(parent);
            group.transform.SetPositionAndRotation(world,Quaternion.Euler(0,f.yaw,0));
            group.layer=GameLayers.WorldStatic; group.isStatic=true;
            for(int i=0;i<count;i++)
            {
                var go=(GameObject)PrefabUtility.InstantiatePrefab(prefab,group.transform);
                float offset=(i-(count-1)*.5f)*spacing;
                go.transform.localPosition=alongZ ? new Vector3(0,0,offset) : new Vector3(offset,0,0);
                go.transform.localRotation=Quaternion.Euler(0,angle,0);
            }
            return true;
        }

        public static string ApplyExistingRegions()
        {
            var plan=JsonUtility.FromJson<LevelPlan>(File.ReadAllText("Assets/_Game/Data/LevelPlan/bunker_plan.json"));
            var changes=new List<string>(); var previous=SceneManager.GetActiveScene();
            foreach(var region in new[]{"REG-S2","REG-S4"})
            {
                string path="Assets/_Game/Scenes/Regions/"+region+".unity";
                var scene=SceneManager.GetSceneByPath(path); bool opened=!scene.IsValid() || !scene.isLoaded;
                if(opened) scene=EditorSceneManager.OpenScene(path,OpenSceneMode.Additive);
                else if(scene.isDirty) throw new System.InvalidOperationException("Save or review existing edits before placement: "+path);
                bool changed=false;
                try
                {
                    var transforms=scene.GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<Transform>(true)).ToArray();
                    foreach(var f in plan.furniture)
                    {
                        var old=transforms.FirstOrDefault(t=>t && (t.name==f.id+"_"+f.family || t.name==f.id+"_EX13"));
                        if(!old) continue;
                        var basePosition=old.name.EndsWith("_EX13") ? old.position : old.position-Vector3.up*f.h*.5f;
                        if(!TryPlace(f,basePosition,old.parent)) continue;
                        Object.DestroyImmediate(old.gameObject); changes.Add(region+"/"+f.id); changed=true;
                    }
                    if(changed) EditorSceneManager.SaveScene(scene);
                }
                finally { if(opened) EditorSceneManager.CloseScene(scene,true); }
            }
            if(previous.IsValid() && previous.isLoaded) SceneManager.SetActiveScene(previous);
            string result=string.Join("\n",changes);
            File.WriteAllText(Path.GetFullPath(Path.Combine(Application.dataPath,"../../SourceArt/_evidence/EX-13/placements.txt")),result);
            return result;
        }
    }
}
