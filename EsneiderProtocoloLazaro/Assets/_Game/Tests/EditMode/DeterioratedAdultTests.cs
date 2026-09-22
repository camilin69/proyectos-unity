using System.IO;
using System.Linq;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;

namespace Esneider.Tests
{
    public class DeterioratedAdultTests
    {
        const string Asset = "HUM-03_AdultoDeteriorado";
        [System.Serializable] class Coordinates { public Vector3[] vertices; }
        static Vector3[] Bake(SkinnedMeshRenderer r)
        {
            var m = new Mesh(); try { r.BakeMesh(m); return m.vertices.Select(v => r.transform.TransformPoint(v)).ToArray(); }
            finally { Object.DestroyImmediate(m); }
        }

        [Test]
        public void DeterioratedBasePreservesWeightsCoordinatesAndSubtleMovement()
        {
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Game/Prefabs/Environment/" + Asset + ".prefab");
            Assert.IsNotNull(prefab); var root = Object.Instantiate(prefab);
            try
            {
                var rs = root.GetComponentsInChildren<SkinnedMeshRenderer>(); Assert.AreEqual(2, rs.Length);
                Assert.LessOrEqual(rs.Sum(r => r.sharedMesh.triangles.Length / 3), 20000);
                Assert.IsTrue(rs.All(r => r.sharedMesh.boneWeights.All(w => w.weight0 + w.weight1 + w.weight2 + w.weight3 > .999f)));
                Assert.AreEqual(0, root.GetComponentsInChildren<Collider>().Length);
                Assert.AreEqual(0, root.GetComponentsInChildren<Esneider.AI.EnemyBrain>().Length);
                var raw = rs.SelectMany(r => r.sharedMesh.vertices.Select(v => r.transform.TransformPoint(v))).ToArray();
                var samples = JsonUtility.FromJson<Coordinates>(File.ReadAllText(Path.GetFullPath(Path.Combine(
                    Application.dataPath, "../../SourceArt/_evidence/EX-46/" + Asset + "/source_coordinates.json")))).vertices;
                Assert.Less(samples.Max(p => raw.Min(v => Vector3.Distance(v, new Vector3(p.x, p.z, p.y)))), .0003f);
                var clip = AssetDatabase.LoadAllAssetsAtPath("Assets/_Game/Art/Models/" + Asset + ".fbx")
                    .OfType<AnimationClip>().Single(c => !c.name.StartsWith("__preview"));
                Assert.That(clip.length, Is.EqualTo(7).Within(.01f));
                clip.SampleAnimation(root, 0); var cloth = rs.Single(r => r.name.Contains("Cloth")); var rest = Bake(cloth);
                clip.SampleAnimation(root, 105f/30f); var peak = Bake(cloth);
                Assert.Greater(rest.Zip(peak, Vector3.Distance).Max(), .001f);
            }
            finally { Object.DestroyImmediate(root); }
        }

        [Test]
        public void AssemblyLiesOnLeftSideAndUsesItsOwnLowSupport()
        {
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Game/Prefabs/Environment/HUM-03_SujetoLateral.prefab");
            Assert.IsNotNull(prefab); var root = Object.Instantiate(prefab);
            try
            {
                var subject = root.GetComponentInChildren<Esneider.World.PreservedSubject>(); Assert.IsNotNull(subject);
                Assert.Greater(Vector3.Dot(subject.transform.TransformDirection(Vector3.left), Vector3.down), .999f);
                Assert.Greater(Vector3.Dot(subject.transform.TransformDirection(Vector3.back), Vector3.left), .999f);
                Assert.IsNotNull(root.GetComponentsInChildren<MeshFilter>().Single(m => m.sharedMesh.name.Contains("SoporteLateral")));
            }
            finally { Object.DestroyImmediate(root); }
        }
    }
}
