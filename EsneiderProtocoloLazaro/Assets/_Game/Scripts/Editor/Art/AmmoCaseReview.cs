using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using Esneider.World;
using Object = UnityEngine.Object;

namespace Esneider.EditorTools
{
    public static class AmmoCaseReview
    {
        public const string Pistol = "OBJ-027_CajaMunicionPistola", Shotgun = "OBJ-027B_CajaMunicionEscopeta";
        public static string Integrate(string asset)
        {
            if (asset != Pistol && asset != Shotgun) throw new ArgumentException("Unknown ammunition case");
            var folder = FurnitureReview.Evidence(asset);
            var geometry = JsonUtility.FromJson<FurnitureReview.Geometry>(File.ReadAllText(Path.Combine(folder,"geometry.json")));
            var report = AssetIntegrator.Integrate(asset,"Environment",false,"none");
            if (report.tris != geometry.triangles || report.tris > 1000 || report.submeshes != 2 || report.warnings.Count > 0)
                throw new InvalidOperationException("Case import mismatch");
            FurnitureReview.VerifyAxes(asset);
            var root = PrefabUtility.LoadPrefabContents(FurnitureReview.Prefab(asset));
            try
            {
                if (PrefabUtility.IsAnyPrefabInstanceRoot(root)) PrefabUtility.UnpackPrefabInstance(root,PrefabUnpackMode.Completely,InteractionMode.AutomatedAction);
                var contents = root.GetComponentsInChildren<MeshFilter>().Single(m=>m.name.Contains("-Contents")).gameObject;
                foreach(var t in root.GetComponentsInChildren<Transform>()) { t.gameObject.layer=Esneider.Core.GameLayers.WorldStatic; t.gameObject.isStatic=false; }
                root.AddComponent<AmmoCaseVisual>().contents=contents;
                PrefabUtility.SaveAsPrefabAsset(root,FurnitureReview.Prefab(asset));
            }
            finally { PrefabUtility.UnloadPrefabContents(root); }
            File.WriteAllText(Path.Combine(folder,"unity_import.json"),JsonUtility.ToJson(report,true));AssetDatabase.SaveAssets();
            return asset+": "+report.tris+" triangles, case and contents";
        }
        public static string Apply(Transform root, string region)
        {
            if(!AssetDatabase.LoadAssetAtPath<GameObject>(FurnitureReview.Prefab(Pistol)) || !AssetDatabase.LoadAssetAtPath<GameObject>(FurnitureReview.Prefab(Shotgun)))return "";
            var all=root.GetComponentsInChildren<Transform>(true);int changed=0;
            foreach(var pickup in root.GetComponentsInChildren<Pickup>(true))
            {
                if(pickup.kind!=PickupKind.PistolAmmo && pickup.kind!=PickupKind.ShotgunAmmo)continue;
                var support=all.FirstOrDefault(t=>t.name=="Support_"+pickup.stableId);
                var surface=support ? support.GetComponent<Collider>() : null;
                if(!surface)throw new InvalidOperationException("No verified support for "+pickup.stableId);
                Physics.SyncTransforms();
                var position=surface.bounds.center;position.y=surface.bounds.max.y;
                var desiredName=pickup.stableId+"_AmmoCase_EX33";
                var existing=pickup.GetComponentInParent<AmmoCaseVisual>();
                if(existing)
                {
                    bool repaired=false;
                    if(existing.pickup!=pickup) { existing.pickup=pickup;PrefabUtility.RecordPrefabInstancePropertyModifications(existing);repaired=true; }
                    // Replacing imported model roots can invalidate the old file-ID overrides.
                    // The preserved support, keyed by stable pickup ID, is the placement authority.
                    if(existing.name!=desiredName || Vector3.Distance(existing.transform.position,position)>.0001f || Quaternion.Angle(existing.transform.rotation,Quaternion.identity)>.01f)
                    {
                        existing.name=desiredName;existing.transform.SetPositionAndRotation(position,Quaternion.identity);
                        PrefabUtility.RecordPrefabInstancePropertyModifications(existing.gameObject);
                        PrefabUtility.RecordPrefabInstancePropertyModifications(existing.transform);repaired=true;
                    }
                    if(repaired)changed++;
                    continue;
                }
                if(surface.bounds.size.x<.31f || surface.bounds.size.z<.30f)throw new InvalidOperationException("Support too small for "+pickup.stableId);
                var model=AssetDatabase.LoadAssetAtPath<GameObject>(FurnitureReview.Prefab(pickup.kind==PickupKind.PistolAmmo?Pistol:Shotgun));
                var box=(GameObject)PrefabUtility.InstantiatePrefab(model,pickup.transform.parent);
                box.name=desiredName;box.transform.SetPositionAndRotation(position,Quaternion.identity);
                PrefabUtility.RecordPrefabInstancePropertyModifications(box);
                PrefabUtility.RecordPrefabInstancePropertyModifications(box.transform);
                // Leave the visual root active when Pickup.Interact deactivates the exhausted pickup.
                pickup.transform.SetParent(box.transform,false);pickup.transform.localPosition=new Vector3(0,.075f,0);
                pickup.transform.localRotation=Quaternion.identity;pickup.transform.localScale=Vector3.one;
                foreach(var renderer in pickup.GetComponents<Renderer>())renderer.enabled=false;
                foreach(var collider in pickup.GetComponents<Collider>())Object.DestroyImmediate(collider);
                var hitbox=pickup.gameObject.AddComponent<BoxCollider>();hitbox.size=new Vector3(.304f,.15f,.224f);
                pickup.gameObject.layer=Esneider.Core.GameLayers.Interactable;
                var visual=box.GetComponent<AmmoCaseVisual>();visual.pickup=pickup;visual.Refresh();
                PrefabUtility.RecordPrefabInstancePropertyModifications(visual);changed++;
            }
            return changed>0?region+": "+changed+" ammunition cases":"";
        }
        public static string ApplyExisting()
        {
            var previous=SceneManager.GetActiveScene();var results=new System.Collections.Generic.List<string>();
            foreach(var region in new[]{"REG-S2","REG-S3","REG-S4"})
            {
                var path="Assets/_Game/Scenes/Regions/"+region+".unity";var scene=SceneManager.GetSceneByPath(path);
                bool opened=!scene.IsValid()||!scene.isLoaded;
                if(opened)scene=EditorSceneManager.OpenScene(path,OpenSceneMode.Additive);
                else if(scene.isDirty)throw new InvalidOperationException("Unsaved "+region);
                try
                {
                    var result=Apply(scene.GetRootGameObjects().Single(g=>g.name==region).transform,region);
                    if(result!=""){EditorSceneManager.SaveScene(scene);results.Add(result);}
                }
                finally{if(opened)EditorSceneManager.CloseScene(scene,true);}
            }
            if(previous.IsValid()&&previous.isLoaded)SceneManager.SetActiveScene(previous);
            return string.Join("\n",results.ToArray());
        }
    }
}
