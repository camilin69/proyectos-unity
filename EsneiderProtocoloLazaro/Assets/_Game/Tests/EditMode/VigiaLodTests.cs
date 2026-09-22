using System.Linq;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;

namespace Esneider.Tests
{
    public class VigiaLodTests
    {
        [Test]
        public void BothLodsShareSkeletonAndDeformWithImportedWalk()
        {
            var root=Object.Instantiate(AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Game/Prefabs/Enemies/BOT-01_Vigia.prefab"));
            var mesh=new Mesh();
            try
            {
                var lods=root.GetComponent<LODGroup>().GetLODs(); Assert.AreEqual(2,lods.Length);
                var near=(SkinnedMeshRenderer)lods[0].renderers.Single();
                var far=(SkinnedMeshRenderer)lods[1].renderers.Single();
                Assert.That(far.sharedMesh.triangles.Length,Is.LessThan(near.sharedMesh.triangles.Length*.6f));
                CollectionAssert.AreEqual(near.bones,far.bones);
                Assert.That(near.bones.Length,Is.EqualTo(17)); Assert.IsFalse(near.bones.Any(b=>b==null));
                var clips=AssetDatabase.LoadAllAssetsAtPath("Assets/_Game/Art/Models/BOT-01_Vigia.fbx").OfType<AnimationClip>().Where(c=>!c.name.StartsWith("__")).ToArray();
                CollectionAssert.AreEquivalent(new[]{"Vigia_Idle","Vigia_Walk","Vigia_Anticipation","Vigia_Net","Vigia_Death"},clips.Select(c=>c.name));
                var walk=clips.Single(c=>c.name=="Vigia_Walk");
                foreach(var renderer in new[]{near,far})
                {
                    Assert.AreEqual(1,renderer.sharedMesh.subMeshCount);
                    walk.SampleAnimation(root,0); renderer.BakeMesh(mesh); var first=mesh.vertices;
                    walk.SampleAnimation(root,walk.length*.5f); renderer.BakeMesh(mesh); var second=mesh.vertices;
                    Assert.That(first.Zip(second,(a,b)=>Vector3.Distance(a,b)).Max(),Is.GreaterThan(.03f),renderer.name+" exported without deformation");
                    foreach(var clip in clips)
                        for(int sample=0;sample<=8;sample++)
                        {
                            clip.SampleAnimation(root,clip.length*sample/8f); renderer.BakeMesh(mesh);
                            Assert.IsTrue(renderer.localBounds.Contains(mesh.bounds.min),renderer.name+" bounds crop "+clip.name);
                            Assert.IsTrue(renderer.localBounds.Contains(mesh.bounds.max),renderer.name+" bounds crop "+clip.name);
                        }
                }
            }
            finally { Object.DestroyImmediate(mesh); Object.DestroyImmediate(root); }
        }
    }
}
