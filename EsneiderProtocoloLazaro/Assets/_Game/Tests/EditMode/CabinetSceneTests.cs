using System.Linq;
using Esneider.Core;
using Esneider.Core.Data;
using Esneider.World;
using NUnit.Framework;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Esneider.Tests
{
    public class CabinetSceneTests
    {
        [TestCase("REG-S1", 4, null, 0)]
        [TestCase("REG-S2", 1, "PICK-W02", 20)]
        [TestCase("REG-S3", 1, "PICK-W03", 10)]
        [TestCase("REG-S4", 1, null, 0)]
        public void CampaignCabinetsOpenAndPreserveWeaponAccess(string region, int count, string pickupId, int amount)
        {
            string path = "Assets/_Game/Scenes/Regions/" + region + ".unity";
            var previous = SceneManager.GetActiveScene();
            var scene = SceneManager.GetSceneByPath(path); bool opened = !scene.IsValid() || !scene.isLoaded;
            if (opened) scene = EditorSceneManager.OpenScene(path, OpenSceneMode.Additive);
            try
            {
                var all = scene.GetRootGameObjects().SelectMany(g => g.GetComponentsInChildren<Transform>(true)).ToArray();
                var cabinets = all.Select(t => t.GetComponent<HingedCabinet>()).Where(c => c).ToArray();
                Assert.That(cabinets.Length, Is.EqualTo(count));
                foreach (var cabinet in cabinets)
                {
                    var pe = cabinet.GetComponent<PersistentEntity>();
                    Assert.That(pe.guid, Is.EqualTo(LevelPlan.StableGuid(pe.stableId).ToString()));
                    Assert.That(pe.regionId, Is.EqualTo(region));
                    Assert.That(cabinet.leaves.All(t => !t.gameObject.isStatic), Is.True);
                    string stable = pe.stableId, guid = pe.guid;
                    // Exercise real collision stepping without writing to the editor's session registry.
                    pe.stableId = pe.guid = "";
                    try
                    {
                        Pickup pickup = pickupId == null ? null : all.Select(t => t.GetComponent<Pickup>()).Single(p => p && p.stableId == pickupId);
                        Ray ray = default;
                        if (pickup)
                        {
                            Assert.That(pickup.amount, Is.EqualTo(amount));
                            Assert.That(pickup.guid, Is.EqualTo(LevelPlan.StableGuid(pickupId).ToString()));
                            var target = pickup.GetComponent<Collider>().bounds.center;
                            ray = new Ray(target - cabinet.transform.forward * 1.5f, cabinet.transform.forward);
                            Physics.SyncTransforms();
                            Assert.That(First(ray).GetComponentInParent<HingedCabinet>(), Is.EqualTo(cabinet), "Closed leaf must hide the pickup trigger");
                        }
                        cabinet.Interact(null); cabinet.Advance(2);
                        Assert.That(cabinet.isOpen, Is.True, cabinet.name + ": " + cabinet.Prompt);
                        if (pickup) Assert.That(First(ray).GetComponentInParent<Pickup>(), Is.EqualTo(pickup), "Open cabinet must expose the real pickup");
                    }
                    finally { cabinet.SnapOpen(false); pe.stableId = stable; pe.guid = guid; Physics.SyncTransforms(); }
                }
            }
            finally
            {
                if (opened) EditorSceneManager.CloseScene(scene, true);
                if (previous.IsValid() && previous.isLoaded) SceneManager.SetActiveScene(previous);
            }
        }
        static Collider First(Ray ray)
        {
            RaycastHit hit;
            Assert.That(Physics.Raycast(ray, out hit, 2f, GameLayers.Mask(GameLayers.Interactable, GameLayers.WorldStatic, GameLayers.DynamicProp), QueryTriggerInteraction.Collide), Is.True);
            return hit.collider;
        }
    }
}
