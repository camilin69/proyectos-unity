using System.Linq;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;
using Esneider.World;

namespace Esneider.Tests
{
    public class PreservationConsoleTests
    {
        [Test]
        public void ConsoleKeepsScreenInsideHousingAndInteractionOnSolidBody()
        {
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Game/Prefabs/Environment/OBJ-003_ConsolaPreservacion.prefab"); Assert.IsNotNull(prefab);
            var root = Object.Instantiate(prefab);
            try
            {
                var console = root.GetComponent<PreservationConsole>(); Assert.IsNotNull(console);
                var mesh = root.GetComponentInChildren<MeshFilter>(); Assert.LessOrEqual(mesh.sharedMesh.triangles.Length / 3, 3000);
                var bounds = mesh.GetComponent<Renderer>().bounds;
                Assert.That(bounds.size.x, Is.EqualTo(.7f).Within(.001f)); Assert.That(bounds.size.y, Is.EqualTo(1.2f).Within(.006f));
                Assert.That(bounds.size.z, Is.EqualTo(.45f).Within(.001f));
                var screen = console.display.GetComponent<Renderer>();
                Assert.LessOrEqual(screen.localBounds.size.x * console.display.transform.localScale.x, .512f);
                Assert.LessOrEqual(screen.localBounds.size.y * console.display.transform.localScale.y, .242f);
                Assert.That(Quaternion.Angle(console.display.transform.localRotation, Quaternion.Euler(20, 0, 0)), Is.LessThan(.01f));
                var colliders = root.GetComponentsInChildren<Collider>(); Assert.AreEqual(2, colliders.Length);
                Assert.IsTrue(colliders.All(c => !c.isTrigger && c.GetComponentInParent<IInteractable>() == console));
                Assert.AreEqual(0, console.display.GetComponents<Collider>().Length);
            }
            finally { Object.DestroyImmediate(root); }
        }
    }
}
