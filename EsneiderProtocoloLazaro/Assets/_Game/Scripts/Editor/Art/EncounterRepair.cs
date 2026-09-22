using System;
using System.Linq;
using Esneider.AI;
using Esneider.Core;
using Esneider.Core.Data;
using Esneider.Core.Persistence;
using Esneider.World;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Esneider.EditorTools
{
    public static class EncounterRepair
    {
        public static readonly string[] Rooms = { "S1-R05", "S1-R04", "S2-R03", "S2-R06", "S2-R05", "S3-R01", "S3-R04", "S4-R01" };
        public static string ApplyRegion(Transform root, string region)
        {
            var plan = LevelPlan.FromJson(AssetDatabase.LoadAssetAtPath<TextAsset>(LevelPlan.DefaultAssetPath).text);
            var catalog = AssetDatabase.LoadAssetAtPath<GameDataCatalog>("Assets/_Game/Data/Definitions/GameDataCatalog.asset");
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Game/Prefabs/Enemies/BOT-01_Vigia.prefab");
            var clips = AssetDatabase.LoadAllAssetsAtPath("Assets/_Game/Art/Models/BOT-01_Vigia.fbx").OfType<AnimationClip>().Where(c=>!c.name.StartsWith("__")).ToArray();
            int added = 0;
            foreach(var ambience in root.GetComponentsInChildren<ExteriorAmbience>(true)) ambience.interiorAmbient=new Color(.004f,.005f,.007f);
            foreach(var animation in root.GetComponentsInChildren<EnemyAnimator>(true)) animation.AlignVisualFacing();
            foreach(var brain in root.GetComponentsInChildren<EnemyBrain>(true).Where(b=>b.definition && b.definition.kind==EnemyKind.Vigia))
            {
                var capsule=brain.GetComponent<CapsuleCollider>();if(capsule){capsule.height=1.36f;capsule.center=new Vector3(0,.68f,0);}
            }
            foreach(string roomId in new[]{"S1-R05","S2-R05","S3-R04","S4-R01"})
            {
                var room=plan.Room(roomId);var floor=plan.Floor(room.floor);if(floor.region!=region)continue;
                string name="DarkZone_"+roomId;if(root.Find(name))continue;
                var center=floor.origin.ToVector3()+new Vector3(room.x+room.w*.5f,floor.height*.5f,room.z+room.d*.5f);
                var bounds=new Bounds(center,new Vector3(room.w,floor.height+.5f,room.d));
                foreach(var light in root.GetComponentsInChildren<Light>(true))
                    if(bounds.Contains(light.transform.position)) { light.intensity*=.12f; light.shadows=LightShadows.Soft; }
                var zone=new GameObject(name);zone.transform.SetParent(root,false);zone.transform.position=center;
                zone.AddComponent<DarknessVolume>().size=new Vector3(room.w,floor.height,room.d);
            }
            foreach (string roomId in Rooms)
            {
                var room = plan.Room(roomId); var floor = plan.Floor(room.floor);
                if (floor.region != region) continue;
                string id = "V-EX51-" + roomId;
                if (root.GetComponentsInChildren<EnemyBrain>(true).Any(b=>b.stableId==id)) continue;
                Physics.SyncTransforms(); Vector3 position = Vector3.zero; bool found = false;
                for (int z=2; z<room.d-2 && !found; z+=2)
                    for (int x=2; x<room.w-2 && !found; x+=2)
                    {
                        var p = floor.origin.ToVector3()+new Vector3(room.x+x,0,room.z+z);
                        if (Physics.CheckCapsule(p+Vector3.up*.45f,p+Vector3.up*1.1f,.4f,GameLayers.Mask(GameLayers.WorldStatic,GameLayers.DynamicProp,GameLayers.Enemy),QueryTriggerInteraction.Ignore)) continue;
                        if (!Physics.Raycast(p+Vector3.up*.2f,Vector3.down,.5f,GameLayers.CoverMask,QueryTriggerInteraction.Ignore)) continue;
                        position=p; found=true;
                    }
                if (!found) throw new InvalidOperationException("No clear supported spawn in " + roomId);
                var enemy = SandboxFactory.BuildEnemy(catalog.enemies.First(e=>e.kind==EnemyKind.Vigia),id,position,Color.white,1.36f,prefab,clips);
                enemy.transform.SetParent(root.Find("Entities"),true);
                var brain = enemy.GetComponent<EnemyBrain>(); brain.startActive = region != "REG-S1";
                if (region == "REG-S1") enemy.AddComponent<ArmedEncounter>();
                var wp = new GameObject(id+"_GuardPost"); wp.transform.SetParent(root.Find("Entities"),false); wp.transform.position=position;
                brain.waypoints.Add(wp.transform);
                SandboxFactory.Persist(enemy,id,region,EntityKind.Enemy); added++;
            }
            foreach (var pickup in root.GetComponentsInChildren<Pickup>(true).Where(p=>p.stableId=="PICK-W02" || p.stableId=="PICK-W03"))
            {
                var cabinet=root.GetComponentsInChildren<HingedCabinet>(true).Single(c=>c.name.Contains(pickup.stableId));
                if (cabinet.transform.Find("WeaponNotice")) continue;
                var plate=new GameObject("WeaponNotice"); plate.transform.SetParent(cabinet.transform,false);
                plate.transform.localPosition=new Vector3(0,1.65f,-.32f); plate.transform.localRotation=Quaternion.identity;
                var text=plate.AddComponent<TextMesh>(); text.text=pickup.kind==PickupKind.Pistol ? "PISTOLA\n[E] ABRIR" : "ESCOPETA\n[E] ABRIR";
                text.anchor=TextAnchor.MiddleCenter;text.alignment=TextAlignment.Center;text.fontSize=48;text.characterSize=.025f;text.color=new Color(.75f,.95f,.94f);
                var lightObject=new GameObject("WeaponCabinetLight"); lightObject.transform.SetParent(cabinet.transform,false);
                lightObject.transform.localPosition=new Vector3(0,1.45f,-.15f);
                var lamp=lightObject.AddComponent<Light>(); lamp.type=LightType.Point; lamp.range=1.4f; lamp.intensity=.8f;lamp.color=new Color(.6f,.85f,1f);
            }
            return region+": "+added+" additional enemies";
        }
        public static string ApplyExisting()
        {
            var results=new System.Collections.Generic.List<string>();
            foreach (string region in new[]{"REG-S1","REG-S2","REG-S3","REG-S4"})
            {
                var path="Assets/_Game/Scenes/Regions/"+region+".unity";
                var s=SceneManager.GetSceneByPath(path);bool opened=!s.IsValid()||!s.isLoaded;
                if(opened)s=EditorSceneManager.OpenScene(path,OpenSceneMode.Additive);
                if(s.isDirty)throw new InvalidOperationException("Unsaved scene: "+path);
                results.Add(ApplyRegion(s.GetRootGameObjects().Single(g=>g.name==region).transform,region));
                EditorSceneManager.SaveScene(s);if(opened)EditorSceneManager.CloseScene(s,true);
            }
            return string.Join("\n",results);
        }
    }
}
