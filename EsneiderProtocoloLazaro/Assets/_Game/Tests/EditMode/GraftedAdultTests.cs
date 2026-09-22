using System.IO;
using System.Linq;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;

namespace Esneider.Tests
{
    public class GraftedAdultTests
    {
        const string Asset = "HUM-02_AdultoInjertos";
        [System.Serializable] class Coordinates { public Vector3[] vertices; }

        static Vector3[] Bake(SkinnedMeshRenderer renderer)
        {
            var mesh = new Mesh();
            try { renderer.BakeMesh(mesh); return mesh.vertices.Select(v => renderer.transform.TransformPoint(v)).ToArray(); }
            finally { Object.DestroyImmediate(mesh); }
        }

        [Test]
        public void GraftHasThreeWeightedMeshesAndArticulatesWithTheHumanRig()
        {
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Game/Prefabs/Environment/" + Asset + ".prefab");
            Assert.IsNotNull(prefab); var root = Object.Instantiate(prefab);
            try
            {
                var renderers = root.GetComponentsInChildren<SkinnedMeshRenderer>(); Assert.AreEqual(3, renderers.Length);
                Assert.LessOrEqual(renderers.Sum(r => r.sharedMesh.triangles.Length / 3), 21000);
                Assert.IsTrue(renderers.All(r => r.sharedMesh.boneWeights.All(w => w.weight0 + w.weight1 + w.weight2 + w.weight3 > .999f)));
                Assert.AreEqual(0, root.GetComponentsInChildren<Collider>().Length);
                Assert.AreEqual(0, root.GetComponentsInChildren<Esneider.AI.EnemyBrain>().Length);
                var clip = AssetDatabase.LoadAllAssetsAtPath("Assets/_Game/Art/Models/" + Asset + ".fbx")
                    .OfType<AnimationClip>().Single(c => !c.name.StartsWith("__preview"));
                Assert.That(clip.length, Is.EqualTo(6).Within(.01f));
                // Shared vertices prove the FBX coordinate conversion independently of the
                // authored frame-one head pose in the ambient clip.
                var sourcePose = renderers.SelectMany(r => r.sharedMesh.vertices.Select(v => r.transform.TransformPoint(v))).ToArray();
                clip.SampleAnimation(root, 0);
                var implant = renderers.Single(r => r.name.Contains("Implant")); var rest = Bake(implant);
                var head = root.GetComponentsInChildren<Transform>().Single(t => t.name == "head"); var h0 = head.position;
                clip.SampleAnimation(root, 73f / 30f); var adjusted = Bake(implant);
                Assert.Greater(rest.Zip(adjusted, Vector3.Distance).Max(), .001f, "Implant joint must visibly adjust with its rig bone");
                Assert.Less(Vector3.Distance(h0, head.position), .0001f, "Cervical support keeps the head stable");
                var samples = JsonUtility.FromJson<Coordinates>(File.ReadAllText(Path.GetFullPath(Path.Combine(
                    Application.dataPath, "../../SourceArt/_evidence/EX-45/" + Asset + "/source_coordinates.json")))).vertices;
                Assert.Less(samples.Max(p => sourcePose.Min(v => Vector3.Distance(v, new Vector3(p.x, p.z, p.y)))), .0003f);
            }
            finally { Object.DestroyImmediate(root); }
        }

        [Test]
        public void AssemblyUsesDistinctReclinedRackAndKeepsFeetSupported()
        {
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Game/Prefabs/Environment/HUM-02_SujetoRestringido.prefab");
            Assert.IsNotNull(prefab); var root = Object.Instantiate(prefab);
            try
            {
                var subject = root.GetComponentInChildren<Esneider.World.PreservedSubject>(); Assert.IsNotNull(subject);
                var pivot = root.transform.Find("ReclinePivot"); Assert.That(pivot.localEulerAngles.x, Is.EqualTo(12).Within(.01f));
                Assert.IsNotNull(root.GetComponentsInChildren<MeshFilter>().Single(m => m.sharedMesh.name.Contains("SoporteInclinado")));
                var feet = subject.GetComponentsInChildren<Transform>().Where(t => t.name.StartsWith("foot_")).ToArray();
                Assert.AreEqual(2, feet.Length);
                Assert.That(Mathf.Abs(feet[0].position.y - feet[1].position.y), Is.LessThan(.005f));
            }
            finally { Object.DestroyImmediate(root); }
        }
    }
}
