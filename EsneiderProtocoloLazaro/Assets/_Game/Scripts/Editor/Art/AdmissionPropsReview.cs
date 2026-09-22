using System;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using Object=UnityEngine.Object;

namespace Esneider.EditorTools
{
    public static class AdmissionPropsReview
    {
        static GameObject Place(string asset,Transform parent,Vector3 position,float yaw=0)
        {
            var p=AssetDatabase.LoadAssetAtPath<GameObject>(FurnitureReview.Prefab(asset));
            if(!p)throw new InvalidOperationException("Missing "+asset);
            var go=(GameObject)PrefabUtility.InstantiatePrefab(p,parent);go.transform.SetPositionAndRotation(position,Quaternion.Euler(0,yaw,0));return go;
        }
        public static string Apply(Transform root,string region)
        {
            var all=root.GetComponentsInChildren<Transform>(true);
            if(all.Any(t=>t.name=="EX27_Props"))return "";
            if(region=="REG-S2")
            {
                var desk=all.FirstOrDefault(t=>t.name=="M027_EX13");if(!desk)return "";
                if(!AssetDatabase.LoadAssetAtPath<GameObject>(FurnitureReview.Prefab("OBJ-040_TazaTermo")))return "";
                var group=new GameObject("EX27_Props").transform;group.SetParent(root,false);
                var cup=Place("OBJ-040_TazaTermo",group,desk.position+new Vector3(.28f,.751f,-.06f),180);
                cup.name="M027_CupThermos";return "Cup and thermos on M027";
            }
            if(region!="REG-S3")return "";
            foreach(var name in new[]{"OBJ-058_AtrilAdmision","OBJ-063_PizarraTurnos","OBJ-064_ContenedorClinico"})
                if(!AssetDatabase.LoadAssetAtPath<GameObject>(FurnitureReview.Prefab(name)))return "";
            var old=all.FirstOrDefault(t=>t.name=="Support_DOC-06");var doc=all.FirstOrDefault(t=>t.name=="Doc_DOC-06");
            if(!old||!doc)return "";
            var floor=old.position-Vector3.up*.45f;
            Physics.SyncTransforms();RaycastHit hit;
            if(!Physics.Raycast(new Vector3(187,floor.y+1.5f,60),Vector3.left,out hit,5,1<<Esneider.Core.GameLayers.WorldStatic,QueryTriggerInteraction.Ignore))
                throw new InvalidOperationException("No admission wall for shift board");
            var props=new GameObject("EX27_Props").transform;props.SetParent(root,false);
            var lectern=Place("OBJ-058_AtrilAdmision",props,floor);lectern.name="DOC06_AdmissionLectern";
            doc.position=floor+new Vector3(-.055f,1.162f,-.015f);doc.rotation=Quaternion.Euler(-14.323945f,0,0);doc.localScale=Vector3.one;
            // The source mesh owns the printed page. Preserve the existing document identity and pickup.
            doc.GetComponent<MeshRenderer>().enabled=false;
            var box=doc.GetComponent<BoxCollider>();box.size=new Vector3(.355f,.12f,.288f);box.center=Vector3.up*.025f;
            Object.DestroyImmediate(old.gameObject);
            var board=Place("OBJ-063_PizarraTurnos",props,new Vector3(hit.point.x+.0175f,floor.y+1.2f,60),270);board.name="Admission_ShiftBoard";
            var bin=Place("OBJ-064_ContenedorClinico",props,new Vector3(222.5f,floor.y,59));bin.name="Clinic_WasteContainer";
            return "DOC-06 lectern, admission shift board, clinic waste container";
        }
        public static string ApplyExisting()
        {
            var previous=SceneManager.GetActiveScene();var results=new System.Collections.Generic.List<string>();
            foreach(var region in new[]{"REG-S2","REG-S3"})
            {
                string path="Assets/_Game/Scenes/Regions/"+region+".unity";var scene=SceneManager.GetSceneByPath(path);
                bool opened=!scene.IsValid()||!scene.isLoaded;
                if(opened)scene=EditorSceneManager.OpenScene(path,OpenSceneMode.Additive);
                else if(scene.isDirty)throw new InvalidOperationException("Unsaved "+region+" changes");
                try
                {
                    var result=Apply(scene.GetRootGameObjects().Single(g=>g.name==region).transform,region);
                    if(result!=""){EditorSceneManager.SaveScene(scene);results.Add(result);}
                }
                finally{if(opened)EditorSceneManager.CloseScene(scene,true);}
            }
            if(previous.IsValid()&&previous.isLoaded)SceneManager.SetActiveScene(previous);return string.Join("\n",results.ToArray());
        }
    }
}
