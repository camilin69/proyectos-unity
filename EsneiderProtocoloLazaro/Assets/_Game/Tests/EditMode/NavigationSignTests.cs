using System;
using System.IO;
using System.Linq;
using Esneider.Core;
using Esneider.Core.Data;
using NUnit.Framework;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Esneider.Tests
{
    public class NavigationSignTests
    {
        [Serializable] class Node { public string id,asset,floor,region;public float x,z,yaw; }
        [Serializable] class Manifest { public Node[] nodes; }
        [TestCase("REG-S1",2)] [TestCase("REG-S2",2)] [TestCase("REG-S3",2)] [TestCase("REG-S4",1)]
        public void PanelsUsePlanCoordinatesAndHaveSupportedCeilingMountsWithoutColliders(string region,int expected)
        {
            var manifest=JsonUtility.FromJson<Manifest>(File.ReadAllText("Assets/_Game/Data/LevelPlan/navigation_signs_ex34.json"));
            var plan=LevelPlan.FromJson(File.ReadAllText(LevelPlan.DefaultAssetPath));
            var previous=SceneManager.GetActiveScene();var path="Assets/_Game/Scenes/Regions/"+region+".unity";
            var scene=SceneManager.GetSceneByPath(path);bool opened=!scene.IsValid()||!scene.isLoaded;
            if(opened)scene=EditorSceneManager.OpenScene(path,OpenSceneMode.Additive);
            try
            {
                var group=scene.GetRootGameObjects().Single(g=>g.name==region).transform.Find("Wayfinding_EX34");Assert.IsNotNull(group);
                Assert.AreEqual(expected,group.Cast<Transform>().Count(t=>t.name.StartsWith("NAV-")));Physics.SyncTransforms();
                foreach(var node in manifest.nodes.Where(n=>n.region==region))
                {
                    var panel=group.Find(node.id);Assert.IsNotNull(panel,node.id);
                    var location=plan.Floor(node.floor).origin.ToVector3()+new Vector3(node.x,2.4f,node.z);
                    Assert.Less(Vector3.Distance(location,panel.position),.001f);Assert.Less(Quaternion.Angle(panel.rotation,Quaternion.Euler(0,node.yaw,0)),.01f);
                    Assert.AreEqual(0,panel.GetComponentsInChildren<Collider>(true).Length,"No route obstruction or invisible interaction collider");
                    var model=panel.Find(node.asset);Assert.IsNotNull(model);Assert.AreEqual(380,model.GetComponentInChildren<MeshFilter>().sharedMesh.triangles.Length/3);
                    for(int i=0;i<2;i++)
                    {
                        var anchor=panel.Find("CeilingAnchor_"+i).GetComponent<Renderer>();
                        var rod=panel.Find("Suspension_"+i).GetComponent<Renderer>();RaycastHit hit;
                        Assert.IsTrue(Physics.Raycast(anchor.bounds.center-Vector3.up*.1f,Vector3.up,out hit,.3f,1<<GameLayers.WorldStatic,QueryTriggerInteraction.Ignore),node.id);
                        Assert.That(anchor.bounds.max.y,Is.EqualTo(hit.point.y).Within(.001f));
                        Assert.That(rod.bounds.max.y,Is.EqualTo(anchor.bounds.min.y).Within(.001f));
                        Assert.That(rod.bounds.min.y,Is.EqualTo(location.y+.644f).Within(.001f));
                    }
                }
                if(region=="REG-S1")
                {
                    var plate=group.Find("D06_IsolationPlate");Assert.IsNotNull(plate);Assert.AreEqual(0,plate.GetComponentsInChildren<Collider>().Length);
                    RaycastHit wall;Assert.IsTrue(Physics.Raycast(plate.position+Vector3.up*.15f,Vector3.right,out wall,.1f,1<<GameLayers.WorldStatic));
                    Assert.That(wall.distance,Is.EqualTo(.0205f).Within(.001f));
                }
            }
            finally { if(opened)EditorSceneManager.CloseScene(scene,true);if(previous.IsValid()&&previous.isLoaded)SceneManager.SetActiveScene(previous); }
        }
    }
}
