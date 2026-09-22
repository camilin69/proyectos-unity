using System;
using System.IO;
using System.Linq;
using Esneider.Core;
using Esneider.Core.Data;
using Esneider.Core.Persistence;
using Esneider.World;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using Object=UnityEngine.Object;

namespace Esneider.EditorTools
{
    public static class ServicePanelReview
    {
        public const string Asset="OBJ-009_TableroAntiguo";
        public static Renderer CreateIndicator(Transform parent,string name,Vector3 position,float radius=.016f)
        {
            const string meshPath="Assets/_Game/Art/Models/ServicePanelLens.asset";
            var mesh=AssetDatabase.LoadAssetAtPath<Mesh>(meshPath);
            if(!mesh)
            {
                mesh=new Mesh();mesh.name="Panel lens 16 sides";
                var vertices=new Vector3[17];var triangles=new int[48];
                for(int i=0;i<16;i++){float a=i*Mathf.PI/8;vertices[i+1]=new Vector3(Mathf.Cos(a)*.016f,Mathf.Sin(a)*.016f,0);triangles[i*3]=0;triangles[i*3+1]=(i+1)%16+1;triangles[i*3+2]=i+1;}
                mesh.vertices=vertices;mesh.triangles=triangles;mesh.RecalculateNormals();mesh.RecalculateBounds();AssetDatabase.CreateAsset(mesh,meshPath);
            }
            const string matPath="Assets/_Game/Art/Materials/ServicePanelLens.mat";
            var mat=AssetDatabase.LoadAssetAtPath<Material>(matPath);
            if(!mat){mat=new Material(Shader.Find("Universal Render Pipeline/Lit"));mat.EnableKeyword("_EMISSION");mat.SetFloat("_Smoothness",.5f);AssetDatabase.CreateAsset(mat,matPath);}
            var go=new GameObject(name);go.transform.SetParent(parent,false);go.transform.localPosition=position;go.transform.localScale=Vector3.one*(radius/.016f);
            go.AddComponent<MeshFilter>().sharedMesh=mesh;var renderer=go.AddComponent<MeshRenderer>();renderer.sharedMaterial=mat;return renderer;
        }
        public static string Integrate()
        {
            var folder=FurnitureReview.Evidence(Asset);var geometry=JsonUtility.FromJson<FurnitureReview.Geometry>(File.ReadAllText(Path.Combine(folder,"geometry.json")));
            var report=AssetIntegrator.Integrate(Asset,"Environment",false,"none");
            if(report.tris!=geometry.triangles||report.submeshes!=3||report.warnings.Count>0)throw new InvalidOperationException("Panel topology mismatch");
            var axes=FurnitureReview.VerifyAxes(Asset);if(axes.signX!=1||axes.signZ!=1)throw new InvalidOperationException("Unexpected axes");
            var root=PrefabUtility.LoadPrefabContents(FurnitureReview.Prefab(Asset));
            try
            {
                if(PrefabUtility.IsAnyPrefabInstanceRoot(root))PrefabUtility.UnpackPrefabInstance(root,PrefabUnpackMode.Completely,InteractionMode.AutomatedAction);
                var door=root.GetComponentsInChildren<Transform>().Single(t=>t.name.Contains("009-Door"));
                var lever=root.GetComponentsInChildren<Transform>().Single(t=>t.name.Contains("009-Lever"));
                var hinge=new GameObject("DoorPivot").transform;hinge.SetParent(root.transform,false);hinge.localPosition=new Vector3(-.382f,.55f,-.110f);door.SetParent(hinge,true);
                var handle=new GameObject("LeverPivot").transform;handle.SetParent(root.transform,false);handle.localPosition=new Vector3(.18f,.43f,-.075f);lever.SetParent(handle,true);
                foreach(var box in geometry.collision_boxes_blender){var c=root.AddComponent<BoxCollider>();c.center=new Vector3(box.center[0],box.center[2],box.center[1]);c.size=new Vector3(box.size[0],box.size[2],box.size[1]);}
                var leafBox=hinge.gameObject.AddComponent<BoxCollider>();leafBox.center=new Vector3(.375f,0,-.003f);leafBox.size=new Vector3(.75f,1.06f,.012f);
                var cabinet=root.AddComponent<HingedCabinet>();cabinet.leaves=new[]{hinge};cabinet.openAngles=new[]{108f};cabinet.openSeconds=.9f;
                root.AddComponent<SurfaceTag>().surfaceId="SUR-MET";
                root.AddComponent<PersistentEntity>().kind=EntityKind.Door;
                var visual=root.AddComponent<ServicePanelVisual>();visual.lever=handle;visual.powerLamp=CreateIndicator(root.transform,"PowerLocal",new Vector3(.075f,.72f,-.058f));visual.networkLamp=CreateIndicator(root.transform,"NetworkLink",new Vector3(.25f,.72f,-.058f));visual.SnapToState();
                var fuse=AssetDatabase.LoadAssetAtPath<GameObject>(FurnitureReview.Prefab("OBJ-010_FusibleModulo"));if(!fuse)throw new InvalidOperationException("Missing fuse");
                foreach(float x in new[]{-.25f,-.13f}){var go=(GameObject)PrefabUtility.InstantiatePrefab(fuse,root.transform);go.transform.localPosition=new Vector3(x,.69f,.01f);}
                foreach(var t in root.GetComponentsInChildren<Transform>()){t.gameObject.layer=GameLayers.WorldStatic;t.gameObject.isStatic=false;}
                PrefabUtility.SaveAsPrefabAsset(root,FurnitureReview.Prefab(Asset));
            }
            finally{PrefabUtility.UnloadPrefabContents(root);}
            File.WriteAllText(Path.Combine(folder,"unity_import.json"),JsonUtility.ToJson(report,true));AssetDatabase.SaveAssets();return Asset+": "+report.tris+" tris + 720 fuse + 32 indicator";
        }
        public static string Apply(Transform root)
        {
            if(root.GetComponentsInChildren<Transform>(true).Any(t=>t.name=="ServicePanel_EX29"))return "";
            var mech=root.GetComponentsInChildren<Mechanism>(true).SingleOrDefault(m=>m.mechanismId=="MECH-LEVER-S1");
            var prefab=AssetDatabase.LoadAssetAtPath<GameObject>(FurnitureReview.Prefab(Asset));if(!mech||!prefab)return "";
            var all=root.GetComponentsInChildren<Transform>(true);
            var doc=all.Single(t=>t.name=="Doc_DOC-02");var support=all.Single(t=>t.name=="Support_DOC-02");
            RaycastHit wall;if(!Physics.Raycast(new Vector3(30,mech.transform.position.y,6),Vector3.right,out wall,5,1<<GameLayers.WorldStatic)||Mathf.Abs(wall.point.x-34)>.05f)throw new InvalidOperationException("S1 service wall changed");
            var panel=(GameObject)PrefabUtility.InstantiatePrefab(prefab,mech.transform.parent);panel.name="ServicePanel_EX29";
            panel.transform.SetPositionAndRotation(new Vector3(wall.point.x-.1005f,-17.45f,6),Quaternion.Euler(0,90,0));
            var pe=panel.GetComponent<PersistentEntity>();pe.stableId="CAB-SERVICE-S1";pe.guid=LevelPlan.StableGuid(pe.stableId).ToString();pe.regionId="REG-S1";pe.prefabId=Asset;
            mech.transform.SetParent(panel.transform,false);mech.transform.localPosition=new Vector3(.18f,.50f,-.063f);mech.transform.localRotation=Quaternion.identity;mech.transform.localScale=Vector3.one;
            foreach(var c in mech.GetComponents<Collider>())Object.DestroyImmediate(c);
            var control=mech.gameObject.AddComponent<BoxCollider>();control.center=Vector3.zero;control.size=new Vector3(.14f,.24f,.085f);
            mech.GetComponent<MeshRenderer>().enabled=false;
            panel.GetComponent<ServicePanelVisual>().mechanism=mech;
            doc.SetParent(panel.transform,false);doc.localPosition=new Vector3(-.18f,.30f,.037f);doc.localRotation=Quaternion.identity;doc.localScale=Vector3.one;
            foreach(var c in doc.GetComponents<Collider>())Object.DestroyImmediate(c);
            var note=doc.gameObject.AddComponent<BoxCollider>();note.size=new Vector3(.24f,.30f,.018f);note.isTrigger=true;doc.GetComponent<MeshRenderer>().enabled=false;
            Object.DestroyImmediate(support.gameObject);
            var old=all.FirstOrDefault(t=>t && t.name=="M018_tablero");
            if(old && old.GetComponentsInChildren<MonoBehaviour>().Length==0)Object.DestroyImmediate(old.gameObject);
            return "S1 service cabinet: preserved mechanism and DOC-02; two fuse modules";
        }
        public static string ApplyExisting()
        {
            const string path="Assets/_Game/Scenes/Regions/REG-S1.unity";var previous=SceneManager.GetActiveScene();var scene=SceneManager.GetSceneByPath(path);bool opened=!scene.IsValid()||!scene.isLoaded;
            if(opened)scene=EditorSceneManager.OpenScene(path,OpenSceneMode.Additive);else if(scene.isDirty)throw new InvalidOperationException("Unsaved S1 changes");
            try{var result=Apply(scene.GetRootGameObjects().Single(g=>g.name=="REG-S1").transform);if(result!="")EditorSceneManager.SaveScene(scene);return result;}
            finally{if(opened)EditorSceneManager.CloseScene(scene,true);if(previous.IsValid()&&previous.isLoaded)SceneManager.SetActiveScene(previous);}
        }
    }
}
