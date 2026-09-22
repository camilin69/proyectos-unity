using System.Linq;
using Esneider.Player;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;

namespace Esneider.Tests
{
    public class SyringeModelTests
    {
        [Test]
        public void Obj056HasRequiredPartsExactLengthAndPlayerWiring()
        {
            var syringe = AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Game/Prefabs/Weapons/PRP-Syringe.prefab");
            Assert.IsNotNull(syringe);
            var root = Object.Instantiate(syringe);
            try
            {
                var names = root.GetComponentsInChildren<Transform>(true).Select(t => t.name).ToArray();
                foreach (var required in new[] { "body", "liquid", "stopper", "plunger", "plunger_rib", "plunger_head", "cap", "cap_ribs" })
                    CollectionAssert.Contains(names, required);
                Assert.AreEqual(988, root.GetComponentsInChildren<MeshFilter>().Sum(m => m.sharedMesh.triangles.Length / 3));
                var bounds = root.GetComponent<BoxCollider>(); Assert.IsNotNull(bounds);
                Assert.That(bounds.size.z, Is.EqualTo(.15f).Within(.002f));
                Assert.That(bounds.size.x, Is.EqualTo(.032f).Within(.002f));
                Assert.That(bounds.size.y, Is.EqualTo(.026f).Within(.002f));
            }
            finally { Object.DestroyImmediate(root); }

            var player = AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Game/Prefabs/Player/Player_Esneider.prefab");
            var viewmodel = player.GetComponentInChildren<ViewmodelController>(true);
            Assert.IsNotNull(viewmodel); Assert.AreSame(syringe, viewmodel.syringePrefab);
        }
    }
}
