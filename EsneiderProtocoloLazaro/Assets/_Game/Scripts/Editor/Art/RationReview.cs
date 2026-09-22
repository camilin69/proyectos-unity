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
    public static class RationReview
    {
        public const string Asset = "OBJ-057_RacionSellada";
        public static string Integrate()
        {
            var result=FurnitureReview.Integrate(Asset);
            var root=PrefabUtility.LoadPrefabContents(FurnitureReview.Prefab(Asset));
            try
            {
                foreach(var t in root.GetComponentsInChildren<Transform>()) {t.gameObject.isStatic=false;t.gameObject.layer=Esneider.Core.GameLayers.Interactable;}
                root.GetComponent<SurfaceTag>().surfaceId="SUR-FAB";
                PrefabUtility.SaveAsPrefabAsset(root,FurnitureReview.Prefab(Asset));
            }
            finally {PrefabUtility.UnloadPrefabContents(root);}
            return result;
        }
        public static string Apply(Transform root,string region)
        {
            var prefab=AssetDatabase.LoadAssetAtPath<GameObject>(FurnitureReview.Prefab(Asset));if(!prefab)return "";
            var all=root.GetComponentsInChildren<Transform>(true);int count=0;
            foreach(var pickup in root.GetComponentsInChildren<Pickup>(true))
            {
                if(pickup.kind!=PickupKind.Ration)continue;
                var existing=pickup.transform.Find("RationModel_EX35");
                if(existing)
                {
                    bool repaired=false;
                    foreach(var r in pickup.GetComponentsInChildren<Renderer>(true))
                        if(!r.transform.IsChildOf(existing)&&r.enabled){r.enabled=false;repaired=true;}
                    if(repaired)count++;
                    continue;
                }
                var support=all.SingleOrDefault(t=>t.name=="Support_"+pickup.stableId);
                var surface=support?support.GetComponent<Collider>():null;
                if(!surface)throw new InvalidOperationException("Missing support for "+pickup.stableId);
                Physics.SyncTransforms();
                if(surface.bounds.size.x<.2f||surface.bounds.size.z<.12f)throw new InvalidOperationException("Small ration support");
                var position=surface.bounds.center;position.y=surface.bounds.max.y;
                pickup.transform.SetPositionAndRotation(position,Quaternion.identity);pickup.transform.localScale=Vector3.one;
                foreach(var r in pickup.GetComponentsInChildren<Renderer>(true))r.enabled=false;
                foreach(var c in pickup.GetComponents<Collider>())Object.DestroyImmediate(c);
                var collider=pickup.gameObject.AddComponent<BoxCollider>();collider.center=new Vector3(0,.02f,0);collider.size=new Vector3(.2f,.04f,.12f);
                pickup.gameObject.layer=Esneider.Core.GameLayers.Interactable;
                // Scene-owned wrapper retains the local placement across FBX root regeneration.
                var wrapper=new GameObject("RationModel_EX35");wrapper.transform.SetParent(pickup.transform,false);
                var model=(GameObject)PrefabUtility.InstantiatePrefab(prefab,wrapper.transform);
                model.transform.localPosition=Vector3.zero;model.transform.localRotation=Quaternion.identity;model.transform.localScale=Vector3.one;
                count++;
            }
            return count==0?"":region+": "+count+" ration packages";
        }
        public static string ApplyExisting()
        {
            var previous=SceneManager.GetActiveScene();var results=new System.Collections.Generic.List<string>();
            foreach(var region in new[]{"REG-S1","REG-S2","REG-S3","REG-S4"})
            {
                var path="Assets/_Game/Scenes/Regions/"+region+".unity";var scene=SceneManager.GetSceneByPath(path);bool opened=!scene.IsValid()||!scene.isLoaded;
                if(opened)scene=EditorSceneManager.OpenScene(path,OpenSceneMode.Additive);else if(scene.isDirty)throw new InvalidOperationException("Unsaved "+region);
                try {var result=Apply(scene.GetRootGameObjects().Single(g=>g.name==region).transform,region);if(result!=""){EditorSceneManager.SaveScene(scene);results.Add(result);}}
                finally {if(opened)EditorSceneManager.CloseScene(scene,true);}
            }
            if(previous.IsValid()&&previous.isLoaded)SceneManager.SetActiveScene(previous);
            return string.Join("\n",results.ToArray());
        }
    }
}
