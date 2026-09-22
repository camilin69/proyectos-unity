using System.Linq;
using Esneider.AI;
using NUnit.Framework;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Esneider.Tests
{
    public class RobotSceneIntegrityTests
    {
        [Test]
        public void EveryCampaignRobotHasRenderableMeshesAndValidBones()
        {
            var setup=EditorSceneManager.GetSceneManagerSetup();int robots=0;
            try
            {
                foreach(var guid in AssetDatabase.FindAssets("t:Scene",new[]{"Assets/_Game/Scenes/Regions"}))
                {
                    var scene=EditorSceneManager.OpenScene(AssetDatabase.GUIDToAssetPath(guid));
                    foreach(var brain in scene.GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<EnemyBrain>(true)))
                    {
                        robots++;var view=brain.GetComponent<EnemyAnimator>();Assert.IsNotNull(view,brain.stableId);
                        var skins=view.animator.GetComponentsInChildren<SkinnedMeshRenderer>(true);Assert.IsNotEmpty(skins,brain.stableId);
                        foreach(var skin in skins)
                        {
                            Assert.IsNotNull(skin.sharedMesh,scene.name+"/"+brain.stableId+"/"+skin.name);
                            Assert.Greater(skin.sharedMesh.vertexCount,0);Assert.IsFalse(skin.bones.Any(b=>!b));
                            Assert.IsTrue(skin.enabled);Assert.IsTrue(skin.gameObject.activeSelf);
                        }
                        foreach(var lod in view.animator.GetComponentsInChildren<LODGroup>())
                            foreach(var level in lod.GetLODs())Assert.IsTrue(level.renderers.Length>0 && level.renderers.All(r=>r!=null),brain.stableId);
                    }
                }
                Assert.GreaterOrEqual(robots,45);
            }
            finally
            {
                if(setup.Any(s=>s.isLoaded && s.isActive && !string.IsNullOrEmpty(s.path))) EditorSceneManager.RestoreSceneManagerSetup(setup);
                else EditorSceneManager.NewScene(NewSceneSetup.EmptyScene);
            }
        }

        [TestCase("BOT-01_Vigia","Vigia")]
        [TestCase("BOT-02_Custodio","Custodio")]
        [TestCase("BOT-03_Archivista","Archivista")]
        public void AnimatedHeadKeepsAuthoredFaceTowardGameplayForward(string asset,string prefix)
        {
            var root=new GameObject("FacingContract");
            try
            {
                var model=Object.Instantiate(AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Game/Prefabs/Enemies/"+asset+".prefab"),root.transform);
                var view=root.AddComponent<EnemyAnimator>();view.enabled=false;view.animator=model.GetComponent<Animator>();
                if(!view.animator)view.animator=model.AddComponent<Animator>();view.prefix=prefix;view.AlignVisualFacing();
                var head=model.GetComponentsInChildren<Transform>().Single(t=>t.name=="head" && !t.GetComponent<Renderer>());
                var faceInBone=head.InverseTransformDirection(model.transform.TransformDirection(Vector3.back));
                var clips=AssetDatabase.LoadAllAssetsAtPath("Assets/_Game/Art/Models/"+asset+".fbx").OfType<AnimationClip>().Where(c=>!c.name.StartsWith("__")&&!c.name.EndsWith("_Death"));
                foreach(var clip in clips)foreach(float t in new[]{0f,.25f,.5f,.75f,1f})
                {
                    clip.SampleAnimation(model,clip.length*t);
                    var forward=head.TransformDirection(faceInBone);forward.y=0;
                    Assert.Greater(Vector3.Dot(forward.normalized,root.transform.forward),.6f,clip.name+" at "+t);
                }
            }
            finally {Object.DestroyImmediate(root);}
        }
    }
}
