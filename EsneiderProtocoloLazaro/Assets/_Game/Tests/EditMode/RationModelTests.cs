using System.Linq;
using Esneider.Core;
using Esneider.Core.Data;
using Esneider.World;
using NUnit.Framework;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Esneider.Tests
{
    public class RationModelTests
    {
        [TestCase("REG-S1",1)] [TestCase("REG-S2",2)] [TestCase("REG-S3",2)] [TestCase("REG-S4",1)]
        public void RationsKeepIdentityAndFitTheirSupports(string region,int expected)
        {
            var previous=SceneManager.GetActiveScene();var path="Assets/_Game/Scenes/Regions/"+region+".unity";
            var scene=SceneManager.GetSceneByPath(path);bool opened=!scene.IsValid()||!scene.isLoaded;
            if(opened)scene=EditorSceneManager.OpenScene(path,OpenSceneMode.Additive);
            try
            {
                var all=scene.GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<Transform>(true)).ToArray();
                var pickups=all.Select(t=>t.GetComponent<Pickup>()).Where(p=>p&&p.kind==PickupKind.Ration).ToArray();Assert.AreEqual(expected,pickups.Length);
                Physics.SyncTransforms();
                foreach(var p in pickups)
                {
                    Assert.AreEqual(1,p.amount);Assert.AreEqual(LevelPlan.StableGuid(p.stableId).ToString(),p.guid);
                    var pe=p.GetComponent<PersistentEntity>();Assert.AreEqual(p.guid,pe.guid);Assert.AreEqual(region,pe.regionId);
                    var model=p.transform.Find("RationModel_EX35");Assert.IsNotNull(model);Assert.AreEqual(Vector3.one,p.transform.localScale);
                    Assert.IsTrue(p.GetComponentsInChildren<Renderer>(true).Where(r=>!r.transform.IsChildOf(model)).All(r=>!r.enabled),"Legacy ration geometry must be hidden");
                    var mesh=model.GetComponentInChildren<MeshFilter>().sharedMesh;Assert.AreEqual(788,mesh.triangles.Length/3);Assert.AreEqual(1,mesh.subMeshCount);
                    var renderer=model.GetComponentInChildren<Renderer>();var size=renderer.bounds.size;
                    Assert.That(size.x,Is.EqualTo(.20f).Within(.0002f));Assert.That(size.y,Is.EqualTo(.04f).Within(.0002f));Assert.That(size.z,Is.EqualTo(.12f).Within(.0002f));
                    var support=all.Single(t=>t.name=="Support_"+p.stableId).GetComponent<Collider>();
                    Assert.That(renderer.bounds.min.y-support.bounds.max.y,Is.EqualTo(0).Within(.0002f));
                    Assert.AreEqual(1,p.GetComponentsInChildren<Collider>().Length);
                    RaycastHit hit;Assert.IsTrue(Physics.Raycast(p.transform.position+new Vector3(0,.4f,0),Vector3.down,out hit,.5f,GameLayers.Mask(GameLayers.WorldStatic,GameLayers.Interactable)));
                    Assert.AreSame(p,hit.collider.GetComponentInParent<Pickup>());
                    Assert.AreEqual(512,renderer.sharedMaterial.GetTexture("_BaseMap").width);
                }
            }
            finally{if(opened)EditorSceneManager.CloseScene(scene,true);if(previous.IsValid()&&previous.isLoaded)SceneManager.SetActiveScene(previous);}
        }
    }
}
