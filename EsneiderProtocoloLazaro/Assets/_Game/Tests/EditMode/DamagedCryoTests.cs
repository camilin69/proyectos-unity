using System.Linq;
using Esneider.World;
using NUnit.Framework;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Esneider.Tests
{
    public class DamagedCryoTests
    {
        const string Asset = "OBJ-002_CamaraVaciaDanada";

        [Test]
        public void Obj002HasDamageFeaturesAnimationAndCollider()
        {
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Game/Prefabs/Environment/" + Asset + ".prefab");
            Assert.IsNotNull(prefab); var root = Object.Instantiate(prefab);
            try
            {
                var names = root.GetComponentsInChildren<Transform>(true).Select(t => t.name).ToArray();
                foreach (var required in new[] { "broken_glass_00", "broken_glass_01", "broken_glass_02", "broken_glass_03", "impact_torn_lip", "previous_subject_imprint" })
                    CollectionAssert.Contains(names, required);
                int tris = root.GetComponentsInChildren<MeshFilter>(true).Sum(m => m.sharedMesh.triangles.Length / 3)
                    + root.GetComponentsInChildren<SkinnedMeshRenderer>(true).Sum(m => m.sharedMesh.triangles.Length / 3);
                Assert.AreEqual(10676, tris);
                var bounds = root.GetComponent<BoxCollider>(); Assert.IsNotNull(bounds);
                Assert.That(bounds.size.x, Is.EqualTo(2.78f).Within(.01f));
                var sequence = root.GetComponent<DamagedCryoSequence>(); Assert.IsNotNull(sequence);
                Assert.IsNotNull(sequence.animator); Assert.IsNotNull(sequence.jamClip);
                Assert.AreEqual("Cryo_Damaged_Jam", sequence.jamClip.name);
                Assert.That(sequence.jamClip.length, Is.InRange(1.95f, 2.05f));
                var curves = AnimationUtility.GetCurveBindings(sequence.jamClip)
                    .Select(b => AnimationUtility.GetEditorCurve(sequence.jamClip, b)).Where(c => c != null).ToArray();
                Assert.IsTrue(curves.Any(c => c.keys.Length > 2 && c.keys.Max(k => k.value) - c.keys.Min(k => k.value) > .1f),
                    "el intento atascado debe contener movimiento real, no un clip plano");
            }
            finally { Object.DestroyImmediate(root); }

            var clips = AssetDatabase.LoadAllAssetsAtPath("Assets/_Game/Art/Models/" + Asset + ".fbx")
                .OfType<AnimationClip>().Where(c => !c.name.StartsWith("__preview")).Select(c => c.name).ToArray();
            CollectionAssert.AreEquivalent(new[] { "Cryo_Damaged_Jam", "Cryo_Damaged_Rest" }, clips);
        }

        [Test]
        public void RegS1UsesDamagedCryoForM011()
        {
            const string path = "Assets/_Game/Scenes/Regions/REG-S1.unity";
            var scene = EditorSceneManager.OpenScene(path, OpenSceneMode.Additive);
            try
            {
                var furniture = scene.GetRootGameObjects().Single(g => g.name == "REG-S1").transform.Find("Entities/Furniture");
                Assert.IsNotNull(furniture.Find("M011_OBJ-002"));
                Assert.IsNull(furniture.Find("M011_OBJ-001"));
            }
            finally { EditorSceneManager.CloseScene(scene, true); }
        }
    }
}
