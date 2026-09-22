using System;
using System.Linq;
using Esneider.Core;
using Esneider.World;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using Object=UnityEngine.Object;

namespace Esneider.EditorTools
{
    public static class DistributionPanelReview
    {
        public const string Asset="OBJ-033_CuadroDistribucion";
        public static string Integrate()
        {
            var result=FurnitureReview.Integrate(Asset);var root=PrefabUtility.LoadPrefabContents(FurnitureReview.Prefab(Asset));
            try
            {
                var visual=root.AddComponent<ServicePanelVisual>();
                visual.powerLamp=ServicePanelReview.CreateIndicator(root.transform,"PowerAvailable",new Vector3(.275f,1.25f,-.138f),.026f);
                visual.networkLamp=ServicePanelReview.CreateIndicator(root.transform,"AuthorizationA",new Vector3(.50f,1.25f,-.138f),.026f);
                visual.SnapToState();
                var nav=root.AddComponent<UnityEngine.AI.NavMeshObstacle>();nav.shape=UnityEngine.AI.NavMeshObstacleShape.Box;nav.center=new Vector3(0,.90f,.015f);nav.size=new Vector3(1.4f,1.8f,.27f);nav.carving=true;
                PrefabUtility.SaveAsPrefabAsset(root,FurnitureReview.Prefab(Asset));
            }
            finally{PrefabUtility.UnloadPrefabContents(root);}
            AssetDatabase.SaveAssets();return result+"; 32 indicator triangles";
        }
        public static string Apply(Transform root)
        {
            var existing=root.GetComponentsInChildren<Transform>(true).SingleOrDefault(t=>t.name=="DistributionPanel_EX30");
            if(existing)
            {
                var state=existing.GetComponent<ServicePanelVisual>();var control=existing.GetComponentInChildren<Mechanism>(true);
                if(!state||!control)throw new InvalidOperationException("Incomplete distribution panel instance");
                if(state.mechanism==control)return "";
                state.mechanism=control;PrefabUtility.RecordPrefabInstancePropertyModifications(state);
                return "Distribution panel permission binding restored after prefab import";
            }
            var mech=root.GetComponentsInChildren<Mechanism>(true).SingleOrDefault(m=>m.mechanismId=="MECH-PANEL-A");
            var prefab=AssetDatabase.LoadAssetAtPath<GameObject>(FurnitureReview.Prefab(Asset));if(!mech||!prefab)return "";
            RaycastHit wall;
            if(!Physics.Raycast(new Vector3(116,mech.transform.position.y,7),Vector3.back,out wall,5,1<<GameLayers.WorldStatic)||Mathf.Abs(wall.point.z-3)>.05f)throw new InvalidOperationException("Distribution wall changed");
            var panel=(GameObject)PrefabUtility.InstantiatePrefab(prefab,mech.transform.parent);panel.name="DistributionPanel_EX30";
            panel.transform.SetPositionAndRotation(new Vector3(116,-8,wall.point.z+.1505f),Quaternion.Euler(0,180,0));
            mech.transform.SetParent(panel.transform,false);mech.transform.localPosition=new Vector3(.39f,1.14f,-.155f);mech.transform.localRotation=Quaternion.identity;mech.transform.localScale=Vector3.one;
            foreach(var collider in mech.GetComponents<Collider>())Object.DestroyImmediate(collider);
            var button=mech.gameObject.AddComponent<BoxCollider>();button.size=new Vector3(.14f,.14f,.04f);
            mech.GetComponent<MeshRenderer>().enabled=false;var visual=panel.GetComponent<ServicePanelVisual>();visual.mechanism=mech;PrefabUtility.RecordPrefabInstancePropertyModifications(visual);
            return "Distribution panel: MECH-PANEL-A preserved, floor-supported and wall-mounted";
        }
        public static string ApplyExisting()
        {
            const string path="Assets/_Game/Scenes/Regions/REG-S2.unity";var previous=SceneManager.GetActiveScene();var scene=SceneManager.GetSceneByPath(path);bool opened=!scene.IsValid()||!scene.isLoaded;
            if(opened)scene=EditorSceneManager.OpenScene(path,OpenSceneMode.Additive);else if(scene.isDirty)throw new InvalidOperationException("Unsaved S2 changes");
            try{var result=Apply(scene.GetRootGameObjects().Single(g=>g.name=="REG-S2").transform);if(result!="")EditorSceneManager.SaveScene(scene);return result;}
            finally{if(opened)EditorSceneManager.CloseScene(scene,true);if(previous.IsValid()&&previous.isLoaded)SceneManager.SetActiveScene(previous);}
        }
    }
}
