using System;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Esneider.EditorTools
{
    public static class ClinicalColumnReview
    {
        public const string Asset="OBJ-076_ColumnaServicios";
        public static string Integrate()
        {
            string result=FurnitureReview.Integrate(Asset);
            var root=PrefabUtility.LoadPrefabContents(FurnitureReview.Prefab(Asset));
            try
            {
                root.GetComponent<Esneider.World.SurfaceTag>().surfaceId="SUR-CON";
                var nav=root.AddComponent<UnityEngine.AI.NavMeshObstacle>();
                nav.shape=UnityEngine.AI.NavMeshObstacleShape.Box;nav.center=Vector3.up*2.5f;
                nav.size=new Vector3(1,5,1);nav.carving=true;
                PrefabUtility.SaveAsPrefabAsset(root,FurnitureReview.Prefab(Asset));
            }
            finally{PrefabUtility.UnloadPrefabContents(root);}
            AssetDatabase.SaveAssets();return result;
        }
        public static string Apply(Transform root)
        {
            var column=AssetDatabase.LoadAssetAtPath<GameObject>(FurnitureReview.Prefab(Asset));
            var lamp=AssetDatabase.LoadAssetAtPath<GameObject>(FurnitureReview.Prefab("OBJ-048_LamparaClinica"));
            if(!column||!lamp)return "";
            var all=root.GetComponentsInChildren<Transform>(true);int count=0;
            foreach(var id in new[]{"M056","M057"})
            {
                if(all.Any(t=>t.name==id+"_Services_EX25"))continue;
                var table=all.FirstOrDefault(t=>t.name==id+"_OBJ-044");if(!table)continue;
                bool reverse=id=="M057";
                var position=table.position+Vector3.right*(reverse?1.681f:-1.681f);
                Physics.SyncTransforms();RaycastHit hit;
                if(!Physics.Raycast(position+Vector3.up*3,Vector3.up,out hit,3,1<<Esneider.Core.GameLayers.WorldStatic,QueryTriggerInteraction.Ignore)||Mathf.Abs(hit.point.y-position.y-5)>.025f)
                    throw new InvalidOperationException("Column must meet the 5 m clinic ceiling");
                var support=(GameObject)PrefabUtility.InstantiatePrefab(column,table.parent);
                support.name=id+"_Services_EX25";
                support.transform.SetPositionAndRotation(position,Quaternion.Euler(0,reverse?180:0,0));
                var fixture=(GameObject)PrefabUtility.InstantiatePrefab(lamp,support.transform);
                fixture.name=id+"_ClinicalLamp";fixture.transform.localPosition=new Vector3(.461f,0,0);
                fixture.transform.localRotation=Quaternion.identity;
                // The focal procedure table owns one dynamic task light.
                fixture.GetComponentInChildren<Light>(true).enabled=!reverse;
                count++;
            }
            return count>0 ? "Clinical service columns and lamps: "+count : "";
        }
        public static string ApplyExisting()
        {
            const string path="Assets/_Game/Scenes/Regions/REG-S3.unity";
            var previous=SceneManager.GetActiveScene();var scene=SceneManager.GetSceneByPath(path);
            bool opened=!scene.IsValid()||!scene.isLoaded;
            if(opened)scene=EditorSceneManager.OpenScene(path,OpenSceneMode.Additive);
            else if(scene.isDirty)throw new InvalidOperationException("Unsaved S3 changes");
            try
            {
                var result=Apply(scene.GetRootGameObjects().Single(g=>g.name=="REG-S3").transform);
                if(result!="")EditorSceneManager.SaveScene(scene);return result;
            }
            finally
            {
                if(opened)EditorSceneManager.CloseScene(scene,true);
                if(previous.IsValid()&&previous.isLoaded)SceneManager.SetActiveScene(previous);
            }
        }
    }
}
