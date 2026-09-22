using System.Linq;
using NUnit.Framework;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using Esneider.Core;
using Esneider.Core.Data;
using Esneider.World;

namespace Esneider.Tests
{
    public class AdmissionSceneTests
    {
        [Test] public void LecternPreservesDocumentIdentityAndReadableApproach()
        {
            const string path="Assets/_Game/Scenes/Regions/REG-S3.unity";
            var previous=SceneManager.GetActiveScene();var scene=SceneManager.GetSceneByPath(path);
            bool opened=!scene.IsValid()||!scene.isLoaded;
            if(opened)scene=EditorSceneManager.OpenScene(path,OpenSceneMode.Additive);
            try
            {
                var all=scene.GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<Transform>(true)).ToArray();
                var doc=all.Select(t=>t.GetComponent<Pickup>()).Single(p=>p&&p.documentId=="DOC-06");
                Assert.AreEqual(LevelPlan.StableGuid("DOC-06").ToString(),doc.guid);
                Assert.AreEqual(1,doc.amount);
                var lectern=all.Single(t=>t.name=="DOC06_AdmissionLectern");
                Assert.That(doc.transform.position.y-lectern.position.y,Is.EqualTo(1.162f).Within(.002f));
                Physics.SyncTransforms();
                var origin=lectern.position+new Vector3(-.055f,1.65f,-1);
                var target=doc.GetComponent<Collider>().bounds.center;
                RaycastHit hit;
                Assert.IsTrue(Physics.Raycast(origin,(target-origin).normalized,out hit,2,GameLayers.Mask(GameLayers.WorldStatic,GameLayers.Interactable),QueryTriggerInteraction.Collide));
                Assert.AreSame(doc,hit.collider.GetComponent<Pickup>(),"Reading ray must reach the actual document before housing");
            }
            finally
            {
                if(opened)EditorSceneManager.CloseScene(scene,true);
                if(previous.IsValid()&&previous.isLoaded)SceneManager.SetActiveScene(previous);
            }
        }
    }
}
