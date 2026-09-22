using System.Linq;
using NUnit.Framework;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Esneider.Tests
{
    public class LegacyHeadTests
    {
        [Test]
        public void LegacyHeadRestsOnBenchWithoutOverlappingThePartsTray()
        {
            const string path="Assets/_Game/Scenes/Regions/REG-S2.unity";var previous=SceneManager.GetActiveScene();var scene=SceneManager.GetSceneByPath(path);bool opened=!scene.IsValid()||!scene.isLoaded;
            if(opened)scene=EditorSceneManager.OpenScene(path,OpenSceneMode.Additive);
            try
            {
                var all=scene.GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<Transform>(true)).ToArray();var head=all.Single(t=>t.name=="LegacyHead_EX39");
                Assert.AreEqual(0,head.GetComponentsInChildren<Collider>().Length);Assert.AreEqual(0,head.GetComponentsInChildren<Animator>().Length);
                Physics.SyncTransforms();RaycastHit hit;Assert.IsTrue(Physics.Raycast(head.position+Vector3.up*.005f,Vector3.down,out hit,.02f,Esneider.Core.GameLayers.Mask(Esneider.Core.GameLayers.WorldStatic)));
                Assert.IsTrue(hit.transform.IsChildOf(head.parent));Assert.That(hit.distance,Is.EqualTo(.005f).Within(.0001f));
                var bounds=head.GetComponentInChildren<Renderer>().bounds;bounds.Expand(-.001f);
                var trays=all.Select(t=>t.GetComponent<MeshFilter>()).Where(m=>m&&m.sharedMesh&&m.sharedMesh.name.Contains("OBJ-023_BandejaPiezas")).Select(m=>m.GetComponent<Renderer>()).ToArray();Assert.IsNotEmpty(trays);
                foreach(var tray in trays)Assert.IsFalse(bounds.Intersects(tray.bounds),"Head intersects a parts tray");
            }
            finally{if(opened)EditorSceneManager.CloseScene(scene,true);if(previous.IsValid()&&previous.isLoaded)SceneManager.SetActiveScene(previous);}
        }
    }
}
