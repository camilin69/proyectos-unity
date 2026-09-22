using System.IO;
using System.Linq;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;

namespace Esneider.Tests
{
    public class BlanketTests
    {
        const string Asset = "OBJ-054_VendajesManta";
        [System.Serializable] class Coordinates { public Vector3[] vertices; }
        static Vector3[] Bake(SkinnedMeshRenderer r)
        {
            var m = new Mesh(); try { r.BakeMesh(m); return m.vertices.Select(v => r.transform.TransformPoint(v)).ToArray(); }
            finally { Object.DestroyImmediate(m); }
        }

        [Test]
        public void BlanketHasThicknessWeightsAndBreathingDeformation()
        {
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Game/Prefabs/Environment/" + Asset + ".prefab");
            Assert.IsNotNull(prefab); var root = Object.Instantiate(prefab);
            try
            {
                var r = root.GetComponentInChildren<SkinnedMeshRenderer>(); Assert.IsNotNull(r);
                Assert.LessOrEqual(r.sharedMesh.triangles.Length / 3, 2000);
                Assert.IsTrue(r.sharedMesh.boneWeights.All(w => w.weight0 + w.weight1 + w.weight2 + w.weight3 > .999f));
                Assert.AreEqual(0, root.GetComponentsInChildren<Collider>().Length);
                var bounds = r.sharedMesh.bounds.size; Assert.That(bounds.x, Is.EqualTo(1.56f).Within(.01f));
                Assert.That(bounds.z, Is.EqualTo(1f).Within(.01f)); Assert.Greater(bounds.y, .24f);
                var raw = r.sharedMesh.vertices.Select(v => r.transform.TransformPoint(v)).ToArray();
                var samples = JsonUtility.FromJson<Coordinates>(File.ReadAllText(Path.GetFullPath(Path.Combine(
                    Application.dataPath, "../../SourceArt/_evidence/EX-47/" + Asset + "/source_coordinates.json")))).vertices;
                Assert.Less(samples.Max(p => raw.Min(v => Vector3.Distance(v, new Vector3(p.x, p.z, p.y)))), .0003f);
                var clip = AssetDatabase.LoadAllAssetsAtPath("Assets/_Game/Art/Models/" + Asset + ".fbx")
                    .OfType<AnimationClip>().Single(c => !c.name.StartsWith("__preview"));
                clip.SampleAnimation(root, 0); var rest = Bake(r); clip.SampleAnimation(root, 2); var peak = Bake(r);
                Assert.Greater(rest.Zip(peak, Vector3.Distance).Max(), .002f);
            }
            finally { Object.DestroyImmediate(root); }
        }

        [Test]
        public void SleepingAssemblyUsesNewBlanketAndDisablesLegacyPlane()
        {
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Game/Prefabs/Environment/HUM-01_CamillaDormido.prefab");
            Assert.IsNotNull(prefab); var root = Object.Instantiate(prefab);
            try
            {
                Assert.IsNotNull(root.GetComponentInChildren<Esneider.World.AmbientLoopPhase>());
                var old = root.GetComponentsInChildren<Renderer>(true).Single(r => r.name == "blanket"); Assert.IsFalse(old.enabled);
                Assert.AreEqual(1, root.GetComponentsInChildren<SkinnedMeshRenderer>().Count(r => r.name.Contains(Asset)));
            }
            finally { Object.DestroyImmediate(root); }
        }
    }
}
