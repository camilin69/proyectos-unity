using System.Collections;
using Esneider.Core.Persistence;
using Esneider.Player;
using Esneider.World;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;

namespace Esneider.Tests
{
    public class RubblePlayTests
    {
        [UnityTest]
        public IEnumerator PickingUpCrowbarAnimatesPrefabOnceAndRespectsPause()
        {
            GameObject prefab = null;
#if UNITY_EDITOR
            prefab = UnityEditor.AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Game/Prefabs/Environment/OBJ-012_EscombrosConcreto.prefab");
#endif
            Assert.IsNotNull(prefab);
            var root = new GameObject("Rubble play test"); root.transform.position = Vector3.up * 500;
            var instance = Object.Instantiate(prefab, root.transform);
            var rubble = instance.GetComponent<RubbleExtraction>();
            var guid = System.Guid.NewGuid().ToString(); rubble.pickupGuid = guid;
            var actor = new GameObject("Inventory actor"); actor.transform.SetParent(root.transform, false);
            var inv = actor.AddComponent<Inventory>();
            var item = new GameObject("Crowbar pickup"); item.transform.SetParent(root.transform, false);
            var pickup = item.AddComponent<Pickup>(); pickup.kind = PickupKind.Crowbar; pickup.amount = 1; pickup.guid = guid;
            var persistent = item.AddComponent<PersistentEntity>(); persistent.guid = guid; persistent.kind = EntityKind.Pickup;
            float oldScale = Time.timeScale; Time.timeScale = 1;
            try
            {
                yield return null;
                pickup.Interact(actor);
                Assert.IsTrue(inv.hasCrowbar); Assert.IsTrue(rubble.Released); Assert.IsFalse(item.activeSelf);
                Time.timeScale = 0;
                var pos = rubble.chips[0].localPosition;
                yield return new WaitForSecondsRealtime(.1f);
                Assert.That(rubble.chips[0].localPosition, Is.EqualTo(pos));
                Time.timeScale = 1;
                yield return new WaitForSeconds(1f);
                Assert.That(rubble.ImpactsPlayed, Is.EqualTo(2));
                Assert.That(rubble.chips[0].localPosition.y, Is.EqualTo(0));
                rubble.Hydrate(); yield return null;
                Assert.That(rubble.ImpactsPlayed, Is.EqualTo(2), "Restore must not replay extraction impacts");
            }
            finally { Time.timeScale = oldScale; Object.Destroy(root); }
        }
    }
}
