using System.IO;
using System.Linq;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;

namespace Esneider.Tests
{
    public class SleepingAdultTests
    {
        const string Asset = "HUM-01_AdultoDormido";
        [System.Serializable] class Coordinates { public Vector3[] vertices; }
        [Test]
        public void SubjectKeepsSourceScaleWeightsAndMovesChestWithoutMovingHeadOrFeet()
        {
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Game/Prefabs/Environment/" + Asset + ".prefab"); Assert.IsNotNull(prefab);
            var root = Object.Instantiate(prefab);
            try
            {
                var renderers = root.GetComponentsInChildren<SkinnedMeshRenderer>(); Assert.AreEqual(2, renderers.Length);
                Assert.LessOrEqual(renderers.Sum(r => r.sharedMesh.triangles.Length / 3), 20000);
                Assert.IsTrue(renderers.All(r => r.sharedMesh.boneWeights.All(w => w.weight0 + w.weight1 + w.weight2 + w.weight3 > .999f)));
                Assert.AreEqual(0, root.GetComponentsInChildren<Collider>().Length); Assert.AreEqual(0, root.GetComponentsInChildren<Esneider.AI.EnemyBrain>().Length);
                var clip = AssetDatabase.LoadAllAssetsAtPath("Assets/_Game/Art/Models/" + Asset + ".fbx").OfType<AnimationClip>().Single(c => !c.name.StartsWith("__preview"));
                Assert.That(clip.length, Is.EqualTo(5).Within(.01f));
                clip.SampleAnimation(root, 0); var bones = root.GetComponentsInChildren<Transform>();
                var chest = bones.Single(t => t.name == "chest"); var head = bones.Single(t => t.name == "head"); var foot = bones.Single(t => t.name == "foot_L");
                var c0 = chest.position; var h0 = head.position; var f0 = foot.position;
                var vertices = renderers.SelectMany(r => Bake(r)).ToArray();
                var samples = JsonUtility.FromJson<Coordinates>(File.ReadAllText(Path.GetFullPath(Path.Combine(Application.dataPath, "../../SourceArt/_evidence/EX-44/" + Asset + "/source_coordinates.json")))).vertices;
                Assert.Less(samples.Max(p => vertices.Min(v => Vector3.Distance(v, new Vector3(p.x, p.z, p.y)))), .0003f, "FBX must preserve source coordinates");
                var cloth = renderers.Single(r => r.name.Contains("Cloth")); var rest = Bake(cloth);
                clip.SampleAnimation(root, 2);
                Assert.That(Vector3.Distance(c0, chest.position), Is.EqualTo(.0028f).Within(.0002f));
                Assert.Less(Vector3.Distance(h0, head.position), .0001f); Assert.Less(Vector3.Distance(f0, foot.position), .0001f);
                var peak = Bake(cloth); Assert.Greater(rest.Zip(peak, Vector3.Distance).Max(), .002f, "Clothing must deform, not just the bone transform");
                clip.SampleAnimation(root, 5); Assert.Less(Vector3.Distance(c0, chest.position), .0001f);
            }
            finally { Object.DestroyImmediate(root); }
        }
        static Vector3[] Bake(SkinnedMeshRenderer renderer)
        {
            var mesh = new Mesh();
            try { renderer.BakeMesh(mesh); return mesh.vertices.Select(v => renderer.transform.TransformPoint(v)).ToArray(); }
            finally { Object.DestroyImmediate(mesh); }
        }
        [Test]
        public void CamillaSupportsHeadTorsoAndHeelsAtRestAndPeakBreath()
        {
            var root = Object.Instantiate(AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Game/Prefabs/Environment/HUM-01_CamillaDormido.prefab"));
            try
            {
                var subject = root.GetComponentInChildren<Esneider.World.SleepingSubject>();
                Assert.Greater(Vector3.Dot(subject.transform.TransformDirection(Vector3.back), Vector3.up), .999f, "Face must point upwards");
                Assert.AreEqual(Vector3.one, subject.transform.localScale);
                var targets = root.GetComponentsInChildren<MeshFilter>().Where(m => m.name == "mattress" || m.sharedMesh.name.Contains("ApoyosCamilla"))
                    .Select(m => { var c = m.gameObject.AddComponent<MeshCollider>(); c.sharedMesh = m.sharedMesh; return c; }).ToArray();
                Assert.AreEqual(2, targets.Length); Physics.SyncTransforms();
                var clip = AssetDatabase.LoadAllAssetsAtPath("Assets/_Game/Art/Models/" + Asset + ".fbx").OfType<AnimationClip>().Single(c => !c.name.StartsWith("__preview"));
                foreach (float seconds in new[] { 0f, 2f })
                {
                    clip.SampleAnimation(subject.gameObject, seconds);
                    var vertices = subject.GetComponentsInChildren<SkinnedMeshRenderer>().SelectMany(Bake).ToArray();
                    foreach (var region in new[] { new[] { -.90f, -.64f, .09f }, new[] { -.50f, -.15f, .10f }, new[] { .79f, .90f, .20f } })
                    {
                        var point = vertices.Where(v => v.x >= region[0] && v.x <= region[1] && Mathf.Abs(v.z) <= region[2]).OrderBy(v => v.y).First();
                        float top = float.NegativeInfinity;
                        foreach (var c in targets) { RaycastHit hit; if (c.Raycast(new Ray(point + Vector3.up * .1f, Vector3.down), out hit, .5f)) top = Mathf.Max(top, hit.point.y); }
                        Assert.IsFalse(float.IsNegativeInfinity(top), "Missing supporting mesh");
                        Assert.That(point.y - top, Is.InRange(-.008f, .012f), "Sampled anatomical support must not float or sink excessively");
                    }
                }
            }
            finally { Object.DestroyImmediate(root); }
        }
    }
}
