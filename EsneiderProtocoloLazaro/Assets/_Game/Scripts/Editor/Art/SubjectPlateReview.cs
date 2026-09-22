using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Esneider.EditorTools
{
    public static class SubjectPlateReview
    {
        [Serializable] public class Entry { public string id,asset,cage,name,serial,admission_year,document; public float yaw; }
        [Serializable] public class Registry { public Entry[] subjects; }
        public static Registry Read() => JsonUtility.FromJson<Registry>(File.ReadAllText("Assets/_Game/Data/LevelPlan/subject_plates_ex36.json"));
        public static string Apply(Transform root,string region)
        {
            if(region!="REG-S3")return "";
            var entries=Read().subjects;
            if(entries.Any(e=>!AssetDatabase.LoadAssetAtPath<GameObject>(FurnitureReview.Prefab(e.asset))))return "";
            var all=root.GetComponentsInChildren<Transform>(true);int count=0;
            foreach(var e in entries)
            {
                var cage=all.Single(t=>t.name==e.cage+"_jaula");
                if(cage.Find("SubjectPlate_EX36"))continue;
                // Use an actual vertical perimeter bar, toward the central aisle.
                var bars=cage.GetComponentsInChildren<BoxCollider>().Where(c=>c.name=="bar"&&c.bounds.size.y>2).ToArray();
                if(bars.Length==0)throw new InvalidOperationException("Missing cage bars: "+e.cage);
                bool west=e.yaw==90;
                float edge=west?bars.Min(b=>b.bounds.center.x):bars.Max(b=>b.bounds.center.x);
                var bar=bars.Where(b=>Mathf.Abs(b.bounds.center.x-edge)<.001f).OrderBy(b=>Mathf.Abs(b.bounds.center.z-cage.position.z)).First();
                float wall=west?bar.bounds.min.x:bar.bounds.max.x;
                var position=new Vector3(wall+(west?-.0105f:.0105f),cage.position.y+1.45f,bar.bounds.center.z);
                var wrapper=new GameObject("SubjectPlate_EX36");wrapper.transform.SetParent(cage,false);wrapper.transform.SetPositionAndRotation(position,Quaternion.Euler(0,e.yaw,0));
                var instance=(GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(FurnitureReview.Prefab(e.asset)),wrapper.transform);
                instance.transform.localPosition=Vector3.zero;instance.transform.localRotation=Quaternion.identity;instance.transform.localScale=Vector3.one;
                count++;
            }
            return count==0?"":count+" clamped subject plates";
        }
        public static string ApplyExisting()
        {
            var previous=SceneManager.GetActiveScene();const string path="Assets/_Game/Scenes/Regions/REG-S3.unity";
            var scene=SceneManager.GetSceneByPath(path);bool opened=!scene.IsValid()||!scene.isLoaded;
            if(opened)scene=EditorSceneManager.OpenScene(path,OpenSceneMode.Additive);else if(scene.isDirty)throw new InvalidOperationException("Unsaved REG-S3");
            try {var result=Apply(scene.GetRootGameObjects().Single(g=>g.name=="REG-S3").transform,"REG-S3");if(result!="")EditorSceneManager.SaveScene(scene);return result;}
            finally {if(opened)EditorSceneManager.CloseScene(scene,true);if(previous.IsValid()&&previous.isLoaded)SceneManager.SetActiveScene(previous);}
        }
    }
}
