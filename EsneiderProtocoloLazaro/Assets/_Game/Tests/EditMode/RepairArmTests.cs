using System.Linq;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;

namespace Esneider.Tests
{
    public class RepairArmTests
    {
        [Test]
        public void RigidChainKeepsJointAnchorsAndToolContactWhenArticulated()
        {
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Game/Prefabs/Environment/OBJ-020_BrazoReparacion.prefab");
            Assert.IsNotNull(prefab);
            var root = Object.Instantiate(prefab);
            try
            {
                var shoulder = root.transform.Find("ShoulderPivot");
                var elbow = shoulder.Find("ElbowPivot");
                var wrist = elbow.Find("WristPivot");
                var contact = wrist.Find("ToolContact");
                Assert.That(Vector3.Distance(shoulder.position, new Vector3(0, .56f, 0)), Is.LessThan(.001f));
                Assert.That(Vector3.Distance(elbow.position, new Vector3(.72f, 1.22f, 0)), Is.LessThan(.001f));
                Assert.That(Vector3.Distance(wrist.position, new Vector3(1.42f, .95f, 0)), Is.LessThan(.001f));
                Assert.That(Vector3.Distance(contact.position, new Vector3(1.535f, .631f, 0)), Is.LessThan(.001f));
                var meshes = root.GetComponentsInChildren<MeshFilter>();
                Assert.AreEqual(4, meshes.Length);
                Assert.LessOrEqual(meshes.Sum(m => m.sharedMesh.triangles.Length / 3), 6000);
                var baseMesh = meshes.Single(m => m.name.Contains("020-Base"));
                var basePosition = baseMesh.transform.position;
                float upperLength = Vector3.Distance(shoulder.position, elbow.position);
                float foreLength = Vector3.Distance(elbow.position, wrist.position);
                var toolOffset = contact.localPosition;
                shoulder.localRotation = Quaternion.AngleAxis(12, Vector3.forward);
                elbow.localRotation = Quaternion.AngleAxis(-18, Vector3.forward);
                wrist.localRotation = Quaternion.AngleAxis(8, Vector3.forward);
                Assert.That(Vector3.Distance(shoulder.position, elbow.position), Is.EqualTo(upperLength).Within(.0001f));
                Assert.That(Vector3.Distance(elbow.position, wrist.position), Is.EqualTo(foreLength).Within(.0001f));
                Assert.AreEqual(toolOffset, contact.localPosition);
                Assert.AreEqual(basePosition, baseMesh.transform.position);
                foreach (var pair in new[] { (shoulder, "020-Upper"), (elbow, "020-Forearm"), (wrist, "020-Tool") })
                {
                    var mesh = meshes.Single(m => m.name.Contains(pair.Item2));
                    Assert.AreEqual(pair.Item1, mesh.transform.parent);
                    Assert.That(mesh.transform.localPosition.magnitude, Is.LessThan(.001f));
                }
                Assert.AreEqual(1, root.GetComponentsInChildren<Collider>().Length);
                Assert.AreEqual(root, root.GetComponent<BoxCollider>().gameObject);
                Assert.AreEqual(0, root.GetComponentsInChildren<Esneider.AI.EnemyBrain>().Length);
            }
            finally { Object.DestroyImmediate(root); }
        }
    }
}
