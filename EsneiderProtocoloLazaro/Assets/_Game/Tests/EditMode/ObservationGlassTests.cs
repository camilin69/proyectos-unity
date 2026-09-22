using System.Linq;
using NUnit.Framework;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using Esneider.Core;

namespace Esneider.Tests
{
    public class ObservationGlassTests
    {
        [Test]
        public void TransparentPaneRetainsSolidAttackCoverFromBothSides()
        {
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Game/Prefabs/Environment/OBJ-060_VidrioObservacion.prefab");
            Assert.IsNotNull(prefab); var root = Object.Instantiate(prefab); root.transform.position = new Vector3(10000, 0, 0);
            try
            {
                var meshes = root.GetComponentsInChildren<MeshFilter>(); Assert.AreEqual(2, meshes.Length);
                Assert.LessOrEqual(meshes.Sum(m => m.sharedMesh.triangles.Length / 3), 1000);
                var pane = meshes.Single(m => m.name.Contains("060-Pane"));
                Assert.That(pane.sharedMesh.bounds.size.z, Is.EqualTo(.024f).Within(.0001f));
                var material = pane.GetComponent<Renderer>().sharedMaterial;
                Assert.AreEqual(3000, material.renderQueue); Assert.AreEqual(0, material.GetFloat("_ZWrite"));
                Assert.IsTrue(material.IsKeywordEnabled("_SURFACE_TYPE_TRANSPARENT")); Assert.AreEqual(2, material.GetFloat("_Cull"));
                Assert.IsNotNull(material.GetTexture("_BaseMap"));
                Assert.AreEqual(1, root.GetComponentsInChildren<Collider>().Length); Assert.IsFalse(root.GetComponent<Collider>().isTrigger);
                Physics.SyncTransforms();
                foreach (int sign in new[] { -1, 1 }) foreach (int mask in new[] { GameLayers.PlayerAttackMask, GameLayers.EnemyProjectileHitMask, GameLayers.VisionBlockMask })
                {
                    RaycastHit hit;
                    Assert.IsTrue(Physics.Raycast(root.transform.position + new Vector3(0, 1.25f, sign), Vector3.forward * -sign, out hit, 2, mask, QueryTriggerInteraction.Ignore));
                    Assert.AreEqual(root.GetComponent<Collider>(), hit.collider);
                    Assert.That(hit.distance, Is.EqualTo(.925f).Within(.001f));
                }
            }
            finally { Object.DestroyImmediate(root); }
        }
        [Test]
        public void ObservationSceneUsesTwoUnscaledModulesAndDisablesOpaqueBlock()
        {
            const string path = "Assets/_Game/Scenes/Regions/REG-S3.unity";
            var previous = SceneManager.GetActiveScene(); var scene = SceneManager.GetSceneByPath(path); bool opened = !scene.IsValid() || !scene.isLoaded;
            if (opened) scene = EditorSceneManager.OpenScene(path, OpenSceneMode.Additive);
            try
            {
                var all = scene.GetRootGameObjects().SelectMany(g => g.GetComponentsInChildren<Transform>(true)).ToArray();
                Assert.IsFalse(all.Single(t => t.name == "M060_vidrio").gameObject.activeSelf);
                var root = all.Single(t => t.name == "M060_Observation_EX41"); Assert.AreEqual(2, root.childCount);
                foreach (Transform child in root) Assert.AreEqual(Vector3.one, child.lossyScale);
                var boxes = root.GetComponentsInChildren<BoxCollider>(); Assert.AreEqual(2, boxes.Length);
                var bounds = boxes[0].bounds; bounds.Encapsulate(boxes[1].bounds);
                Assert.That(bounds.size.x, Is.EqualTo(8).Within(.001f)); Assert.That(bounds.min.y, Is.EqualTo(-8).Within(.001f));
                Assert.That(Vector3.Distance(bounds.center, new Vector3(235.5f, -6.75f, 50.2f)), Is.LessThan(.001f));
                Assert.That(Mathf.Abs(boxes[0].bounds.max.x - boxes[1].bounds.min.x), Is.LessThan(.001f));
            }
            finally { if (opened) EditorSceneManager.CloseScene(scene, true); if (previous.IsValid() && previous.isLoaded) SceneManager.SetActiveScene(previous); }
        }
    }
}
