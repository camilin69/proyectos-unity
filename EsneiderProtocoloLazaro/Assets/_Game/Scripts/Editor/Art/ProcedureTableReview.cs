using System;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using Object=UnityEngine.Object;

namespace Esneider.EditorTools
{
    public static class ProcedureTableReview
    {
        public const string Asset="OBJ-044_MesaProcedimientos";
        public static string Integrate()
        {
            string result=FurnitureReview.Integrate(Asset);
            var root=PrefabUtility.LoadPrefabContents(FurnitureReview.Prefab(Asset));
            try
            {
                var nav=root.AddComponent<UnityEngine.AI.NavMeshObstacle>();
                nav.shape=UnityEngine.AI.NavMeshObstacleShape.Box;
                nav.center=new Vector3(0,.45f,0);nav.size=new Vector3(2.1f,.9f,.83f);nav.carving=true;
                PrefabUtility.SaveAsPrefabAsset(root,FurnitureReview.Prefab(Asset));
            }
            finally { PrefabUtility.UnloadPrefabContents(root); }
            AssetDatabase.SaveAssets(); return result;
        }
        public static string ApplyExisting()
        {
            var prefab=AssetDatabase.LoadAssetAtPath<GameObject>(FurnitureReview.Prefab(Asset));
            if(!prefab) throw new InvalidOperationException("Missing procedure table");
            const string path="Assets/_Game/Scenes/Regions/REG-S3.unity";
            var previous=SceneManager.GetActiveScene();var scene=SceneManager.GetSceneByPath(path);
            bool opened=!scene.IsValid()||!scene.isLoaded;
            if(opened)scene=EditorSceneManager.OpenScene(path,OpenSceneMode.Additive);
            else if(scene.isDirty)throw new InvalidOperationException("Unsaved S3 changes");
            try
            {
                int count=0;
                var all=scene.GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<Transform>(true)).ToArray();
                foreach(var id in new[]{"M056","M057"})
                {
                    var old=all.FirstOrDefault(t=>t && t.name==id+"_OBJ-043");
                    if(!old)continue;
                    if(old.GetComponentsInChildren<MonoBehaviour>(true).Length>0)
                        throw new InvalidOperationException("Review attached behaviour before replacing "+id);
                    var go=(GameObject)PrefabUtility.InstantiatePrefab(prefab,old.parent);
                    go.name=id+"_OBJ-044";go.transform.SetPositionAndRotation(old.position,old.rotation);
                    Object.DestroyImmediate(old.gameObject);count++;
                }
                if(count>0)EditorSceneManager.SaveScene(scene);
                return "Procedure tables replaced: "+count;
            }
            finally
            {
                if(opened)EditorSceneManager.CloseScene(scene,true);
                if(previous.IsValid()&&previous.isLoaded)SceneManager.SetActiveScene(previous);
            }
        }
    }
}
