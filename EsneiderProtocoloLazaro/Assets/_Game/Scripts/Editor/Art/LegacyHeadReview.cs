using System;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Esneider.EditorTools
{
    public static class LegacyHeadReview
    {
        public const string Asset="OBJ-022_CabezaCustodioAntigua";
        public static string Apply(Transform root,string region)
        {
            if(region!="REG-S2")return "";
            var model=AssetDatabase.LoadAssetAtPath<GameObject>(FurnitureReview.Prefab(Asset));if(!model)return "";
            var bench=root.GetComponentsInChildren<Transform>(true).Single(t=>t.name=="M023_EX13");
            var top=bench.GetComponentsInChildren<BoxCollider>().Where(c=>c.bounds.size.x>1.9f&&c.bounds.size.y<.1f).OrderBy(c=>c.bounds.center.x).First();
            var pos=top.bounds.center+new Vector3(.15f,0,-.05f);pos.y=top.bounds.max.y;
            var existing=bench.Find("LegacyHead_EX39");
            if(existing)
            {
                if(Vector3.Distance(existing.position,pos)<.0001f)return "";
                existing.position=pos;return "Repositioned legacy head clear of parts tray";
            }
            var wrapper=new GameObject("LegacyHead_EX39");wrapper.transform.SetParent(bench,false);wrapper.transform.SetPositionAndRotation(pos,Quaternion.Euler(0,180,0));
            var instance=(GameObject)PrefabUtility.InstantiatePrefab(model,wrapper.transform);instance.transform.localPosition=Vector3.zero;instance.transform.localRotation=Quaternion.identity;instance.transform.localScale=Vector3.one;
            return "Legacy head on M023 workbench";
        }
        public static string ApplyExisting()
        {
            var previous=SceneManager.GetActiveScene();const string path="Assets/_Game/Scenes/Regions/REG-S2.unity";var scene=SceneManager.GetSceneByPath(path);bool opened=!scene.IsValid()||!scene.isLoaded;
            if(opened)scene=EditorSceneManager.OpenScene(path,OpenSceneMode.Additive);else if(scene.isDirty)throw new InvalidOperationException("Unsaved REG-S2");
            try {var result=Apply(scene.GetRootGameObjects().Single(g=>g.name=="REG-S2").transform,"REG-S2");if(result!="")EditorSceneManager.SaveScene(scene);return result;}
            finally {if(opened)EditorSceneManager.CloseScene(scene,true);if(previous.IsValid()&&previous.isLoaded)SceneManager.SetActiveScene(previous);}
        }
    }
}
