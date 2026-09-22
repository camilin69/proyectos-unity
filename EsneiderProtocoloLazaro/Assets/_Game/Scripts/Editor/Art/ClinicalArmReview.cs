using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;
using Esneider.World;

namespace Esneider.EditorTools
{
    public static class ClinicalArmReview
    {
        public const string Asset="OBJ-050_BrazoClinico";
        public static string Apply(Transform root)
        {
            var prefab=AssetDatabase.LoadAssetAtPath<GameObject>(FurnitureReview.Prefab(Asset));if(!prefab)return "";
            var all=root.GetComponentsInChildren<Transform>(true);int count=0;
            foreach(var id in new[]{"M056","M057"})
            {
                var column=all.FirstOrDefault(t=>t.name==id+"_Services_EX25");
                if(!column||column.Find(id+"_ClinicalArm"))continue;
                var go=(GameObject)PrefabUtility.InstantiatePrefab(prefab,column);
                go.name=id+"_ClinicalArm";go.transform.localPosition=new Vector3(.45f,0,0);go.transform.localRotation=Quaternion.identity;
                go.GetComponent<ClinicalArmMotion>().enabled=id=="M056";count++;
            }
            return count>0 ? "Clinical arms mounted: "+count : "";
        }
        public static string ApplyExisting()
        {
            const string path="Assets/_Game/Scenes/Regions/REG-S3.unity";
            var previous=UnityEngine.SceneManagement.SceneManager.GetActiveScene();var scene=UnityEngine.SceneManagement.SceneManager.GetSceneByPath(path);
            bool opened=!scene.IsValid()||!scene.isLoaded;
            if(opened)scene=UnityEditor.SceneManagement.EditorSceneManager.OpenScene(path,UnityEditor.SceneManagement.OpenSceneMode.Additive);
            else if(scene.isDirty)throw new InvalidOperationException("Unsaved S3 changes");
            try
            {
                var result=Apply(scene.GetRootGameObjects().Single(g=>g.name=="REG-S3").transform);
                if(result!="")UnityEditor.SceneManagement.EditorSceneManager.SaveScene(scene);return result;
            }
            finally
            {
                if(opened)UnityEditor.SceneManagement.EditorSceneManager.CloseScene(scene,true);
                if(previous.IsValid()&&previous.isLoaded)UnityEngine.SceneManagement.SceneManager.SetActiveScene(previous);
            }
        }
        public static string CaptureCycle()
        {
            var paths=new System.Collections.Generic.List<string>();
            foreach(var seconds in new[]{0f,14f,15.5f,17f,18.5f,20f})
            {
                float sample=seconds;
                paths.Add(FurnitureReview.Capture(Asset,null,Path.Combine(FurnitureReview.Evidence(Asset),"frame_"+seconds.ToString("F1",System.Globalization.CultureInfo.InvariantCulture)),g=>g.GetComponent<ClinicalArmMotion>().Sample(sample),new Bounds(new Vector3(.70f,1.5f,0),new Vector3(1.7f,1,.65f))));
            }
            return string.Join("\n",paths.ToArray());
        }
        public static string Integrate()
        {
            var folder=FurnitureReview.Evidence(Asset);
            var geometry=JsonUtility.FromJson<FurnitureReview.Geometry>(File.ReadAllText(Path.Combine(folder,"geometry.json")));
            var report=AssetIntegrator.Integrate(Asset,"Environment",false,"none");
            if(report.tris!=geometry.triangles||report.submeshes!=3||report.warnings.Count>0)throw new InvalidOperationException("Arm topology mismatch");
            var axes=FurnitureReview.VerifyAxes(Asset);
            if(axes.signX!=1||axes.signZ!=1)throw new InvalidOperationException("Unexpected arm axis mapping");
            var root=PrefabUtility.LoadPrefabContents(FurnitureReview.Prefab(Asset));
            try
            {
                if(PrefabUtility.IsAnyPrefabInstanceRoot(root))
                    PrefabUtility.UnpackPrefabInstance(root,PrefabUnpackMode.Completely,InteractionMode.AutomatedAction);
                var upper=root.GetComponentsInChildren<Transform>().Single(t=>t.name.Contains("050-Upper"));
                var fore=root.GetComponentsInChildren<Transform>().Single(t=>t.name.Contains("050-Forearm"));
                if(Vector3.Distance(upper.position,new Vector3(.12f,1.35f,0))>.001f||Vector3.Distance(fore.position,new Vector3(.72f,1.75f,0))>.001f)throw new InvalidOperationException("Arm source pivots changed");
                var shoulder=new GameObject("ShoulderPivot").transform;shoulder.SetParent(root.transform,false);shoulder.localPosition=new Vector3(.12f,1.35f,0);
                var elbow=new GameObject("ElbowPivot").transform;elbow.SetParent(shoulder,false);elbow.position=new Vector3(.72f,1.75f,0);
                upper.SetParent(shoulder,true);fore.SetParent(elbow,true);
                var box=root.AddComponent<BoxCollider>();box.center=new Vector3(0,1.35f,0);box.size=new Vector3(.06f,.4f,.27f);
                foreach(var t in root.GetComponentsInChildren<Transform>()){t.gameObject.layer=Esneider.Core.GameLayers.WorldStatic;t.gameObject.isStatic=false;}
                root.AddComponent<SurfaceTag>().surfaceId="SUR-MET";
                var motion=root.AddComponent<ClinicalArmMotion>();motion.shoulder=shoulder;motion.elbow=elbow;
                var audio=root.AddComponent<AudioSource>();audio.clip=AssetDatabase.LoadAssetAtPath<AudioClip>("Assets/_Game/Audio/World/SND-ClinicalServo.wav");
                audio.playOnAwake=false;audio.loop=true;audio.volume=.06f;audio.spatialBlend=1;audio.minDistance=.3f;audio.maxDistance=3;audio.rolloffMode=AudioRolloffMode.Linear;motion.servo=audio;
                PrefabUtility.SaveAsPrefabAsset(root,FurnitureReview.Prefab(Asset));
            }
            finally{PrefabUtility.UnloadPrefabContents(root);}
            File.WriteAllText(Path.Combine(folder,"unity_import.json"),JsonUtility.ToJson(report,true));AssetDatabase.SaveAssets();return Asset+": "+report.tris+" triangles, verified shoulder and elbow";
        }
    }
}
