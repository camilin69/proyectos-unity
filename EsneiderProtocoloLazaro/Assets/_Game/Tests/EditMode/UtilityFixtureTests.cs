using System.Linq;
using NUnit.Framework;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using Esneider.Core;
using Esneider.World;

namespace Esneider.Tests
{
    public class UtilityFixtureTests
    {
        [TestCase("OBJ-066_LuminariaTecnica")]
        [TestCase("OBJ-067_LamparaEmergencia")]
        public void EmissionUsesMaskAndFollowsSourceOffState(string asset)
        {
            var root=Object.Instantiate(AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Game/Prefabs/Environment/"+asset+".prefab"));
            try
            {
                var glow=root.GetComponent<FixtureEmission>();Assert.IsNotNull(glow.surface.sharedMaterial.GetTexture("_EmissionMap"));
                var light=root.AddComponent<Light>();glow.source=light;light.intensity=.8f;light.color=new Color(.5f,.7f,.9f);glow.Refresh();
                var block=new MaterialPropertyBlock();glow.surface.GetPropertyBlock(block);Assert.That(block.GetColor("_EmissionColor").b,Is.GreaterThan(.5f));
                light.enabled=false;glow.Refresh();glow.surface.GetPropertyBlock(block);Assert.AreEqual(0,block.GetColor("_EmissionColor").maxColorComponent);
                light.enabled=true;light.intensity=0;glow.Refresh();glow.surface.GetPropertyBlock(block);Assert.AreEqual(0,block.GetColor("_EmissionColor").maxColorComponent);
                Assert.AreEqual(0,root.GetComponentsInChildren<Collider>().Length);
            }
            finally{Object.DestroyImmediate(root);}
        }
        [TestCase("REG-S1")][TestCase("REG-S2")][TestCase("REG-S3")][TestCase("REG-S4")]
        public void ExistingRoomLightsAreBoundToCeilingMountedHousings(string region)
        {
            var previous=SceneManager.GetActiveScene();string path="Assets/_Game/Scenes/Regions/"+region+".unity";var scene=SceneManager.GetSceneByPath(path);bool opened=!scene.IsValid()||!scene.isLoaded;
            if(opened)scene=EditorSceneManager.OpenScene(path,OpenSceneMode.Additive);
            try
            {
                var fixtures=scene.GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<FixtureEmission>(true)).ToArray();Assert.That(fixtures.Length,Is.GreaterThan(0));Physics.SyncTransforms();
                foreach(var fixture in fixtures)
                {
                    Assert.IsNotNull(fixture.source,fixture.name);Assert.IsTrue(fixture.source.transform.IsChildOf(fixture.transform));Assert.AreEqual(1,fixture.GetComponentsInChildren<Light>().Length);
                    Assert.That(fixture.source.transform.localPosition.y,Is.EqualTo(-.01f).Within(.001f));
                    RaycastHit hit;Assert.IsTrue(Physics.Raycast(fixture.source.transform.position,Vector3.up,out hit,1,1<<GameLayers.WorldStatic));
                    Assert.That(Mathf.Abs(hit.point.y-fixture.surface.bounds.max.y),Is.LessThan(.003f),fixture.name+" ceiling anchor contact");
                }
            }
            finally{if(opened)EditorSceneManager.CloseScene(scene,true);if(previous.IsValid()&&previous.isLoaded)SceneManager.SetActiveScene(previous);}
        }
        [Test] public void CorridorSpeakerPreservesNarrativeComponentWithoutDetectionTrigger()
        {
            var previous=SceneManager.GetActiveScene();const string path="Assets/_Game/Scenes/Regions/REG-C1.unity";var scene=SceneManager.GetSceneByPath(path);bool opened=!scene.IsValid()||!scene.isLoaded;
            if(opened)scene=EditorSceneManager.OpenScene(path,OpenSceneMode.Additive);
            try
            {
                var speaker=scene.GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<AnnouncementSpeaker>(true)).Single();Assert.AreEqual("D06",speaker.doorId);
                Assert.IsTrue(speaker.transform.Find("SpeakerVisual_EX31"));Assert.IsTrue(speaker.GetComponentsInChildren<Collider>().All(c=>!c.isTrigger));
                Assert.AreEqual(0,speaker.GetComponentsInChildren<AudioSource>().Length,"Audio remains dispatched by the existing narrative service");
            }
            finally{if(opened)EditorSceneManager.CloseScene(scene,true);if(previous.IsValid()&&previous.isLoaded)SceneManager.SetActiveScene(previous);}
        }
    }
}
