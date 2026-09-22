using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using Esneider.Core;
using Esneider.Core.Data;
using Object=UnityEngine.Object;

namespace Esneider.EditorTools
{
    public static class NavigationSignReview
    {
        public const string ManifestPath="Assets/_Game/Data/LevelPlan/navigation_signs_ex34.json";
        public const string Isolation="OBJ-016_PlacaEmergencia";
        [Serializable] public class Node { public string id,asset,floor,region;public float x,z,yaw; }
        [Serializable] public class Manifest { public Node[] nodes; }
        public static Node[] Nodes()=>JsonUtility.FromJson<Manifest>(File.ReadAllText(ManifestPath)).nodes;
        static Material MountMaterial()
        {
            const string path="Assets/_Game/Art/Materials/NavigationMount.mat";
            var material=AssetDatabase.LoadAssetAtPath<Material>(path);
            if(!material)
            {
                material=new Material(Shader.Find("Universal Render Pipeline/Lit"));material.SetColor("_BaseColor",new Color(.15f,.18f,.17f));
                material.SetFloat("_Metallic",.7f);material.SetFloat("_Smoothness",.35f);AssetDatabase.CreateAsset(material,path);
            }
            return material;
        }
        static void Hardware(Transform parent,string name,Vector3 world,Vector3 size)
        {
            var go=GameObject.CreatePrimitive(PrimitiveType.Cube);go.name=name;go.transform.SetParent(parent,true);
            go.transform.position=world;go.transform.localScale=size;go.layer=GameLayers.WorldStatic;go.isStatic=true;
            Object.DestroyImmediate(go.GetComponent<Collider>());go.GetComponent<Renderer>().sharedMaterial=MountMaterial();
        }
        static Transform Wrapper(Transform parent,string name,Vector3 position,Quaternion rotation,string asset)
        {
            var wrapper=new GameObject(name).transform;wrapper.SetParent(parent,false);wrapper.SetPositionAndRotation(position,rotation);
            var model=AssetDatabase.LoadAssetAtPath<GameObject>(FurnitureReview.Prefab(asset));
            if(!model)throw new InvalidOperationException("Missing sign "+asset);
            var child=(GameObject)PrefabUtility.InstantiatePrefab(model,wrapper);child.transform.localPosition=Vector3.zero;child.transform.localRotation=Quaternion.identity;
            return wrapper;
        }
        public static string Apply(Transform root,string region)
        {
            if(!File.Exists(ManifestPath))return "";
            var nodes=Nodes().Where(n=>n.region==region).ToArray();
            if(nodes.Length==0)return "";
            if(nodes.Any(n=>!AssetDatabase.LoadAssetAtPath<GameObject>(FurnitureReview.Prefab(n.asset))))return "";
            var plan=LevelPlan.FromJson(File.ReadAllText(LevelPlan.DefaultAssetPath));int count=0;
            var group=root.Find("Wayfinding_EX34");if(!group){group=new GameObject("Wayfinding_EX34").transform;group.SetParent(root,false);}
            Physics.SyncTransforms();
            foreach(var node in nodes)
            {
                if(group.Find(node.id))continue;
                var floor=plan.Floor(node.floor);var position=floor.origin.ToVector3()+new Vector3(node.x,2.4f,node.z);var rotation=Quaternion.Euler(0,node.yaw,0);
                var anchors=new Vector3[2];var roof=new Vector3[2];
                for(int i=0;i<2;i++)
                {
                    anchors[i]=position+rotation*new Vector3(i==0?-.7f:.7f,.644f,0);RaycastHit hit;
                    if(!Physics.Raycast(anchors[i]+Vector3.up*.05f,Vector3.up,out hit,12,1<<GameLayers.WorldStatic,QueryTriggerInteraction.Ignore)||hit.normal.y>-.9f)
                        throw new InvalidOperationException("Missing ceiling anchor for "+node.id+" "+i);
                    roof[i]=hit.point;
                }
                var wrapper=Wrapper(group,node.id,position,rotation,node.asset);
                for(int i=0;i<2;i++)
                {
                    float top=roof[i].y-.008f;float height=top-anchors[i].y;
                    if(height<.02f)throw new InvalidOperationException("No suspension clearance "+node.id);
                    Hardware(wrapper,"Suspension_"+i,new Vector3(anchors[i].x,(top+anchors[i].y)/2,anchors[i].z),new Vector3(.016f,height,.016f));
                    Hardware(wrapper,"CeilingAnchor_"+i,roof[i]-Vector3.up*.004f,new Vector3(.09f,.008f,.09f));
                }
                count++;
            }
            if(region=="REG-S1"&&!group.Find("D06_IsolationPlate"))
            {
                RaycastHit hit;var origin=new Vector3(39,-16.4f,23.2f);
                if(!Physics.Raycast(origin,Vector3.right,out hit,2,1<<GameLayers.WorldStatic,QueryTriggerInteraction.Ignore)||hit.normal.x>-.9f)
                    throw new InvalidOperationException("Missing D06 isolation mounting wall");
                Wrapper(group,"D06_IsolationPlate",new Vector3(hit.point.x-.0205f,-16.5f,23.2f),Quaternion.Euler(0,90,0),Isolation);count++;
            }
            return count>0?region+": "+count+" orientation signs":"";
        }
        public static string ApplyExisting()
        {
            var previous=SceneManager.GetActiveScene();var results=new System.Collections.Generic.List<string>();
            foreach(var region in new[]{"REG-S1","REG-S2","REG-S3","REG-S4"})
            {
                var path="Assets/_Game/Scenes/Regions/"+region+".unity";var scene=SceneManager.GetSceneByPath(path);bool opened=!scene.IsValid()||!scene.isLoaded;
                if(opened)scene=EditorSceneManager.OpenScene(path,OpenSceneMode.Additive);else if(scene.isDirty)throw new InvalidOperationException("Unsaved "+region);
                try
                {
                    var result=Apply(scene.GetRootGameObjects().Single(g=>g.name==region).transform,region);
                    if(result!=""){EditorSceneManager.SaveScene(scene);results.Add(result);}
                }
                finally{if(opened)EditorSceneManager.CloseScene(scene,true);}
            }
            if(previous.IsValid()&&previous.isLoaded)SceneManager.SetActiveScene(previous);AssetDatabase.SaveAssets();return string.Join("\n",results.ToArray());
        }
    }
}
