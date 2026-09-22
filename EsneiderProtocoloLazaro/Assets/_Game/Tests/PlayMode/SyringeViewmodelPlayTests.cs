using System.Collections;
using System.Linq;
using Esneider.Combat;
using Esneider.Core;
using Esneider.Player;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;
#if UNITY_EDITOR
using UnityEditor;
#endif

namespace Esneider.Tests
{
    public class SyringeViewmodelPlayTests
    {
        [UnityTest]
        public IEnumerator HealingShowsPropMovesPlungerAtCommitAndRestoresWeapon()
        {
#if UNITY_EDITOR
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Game/Prefabs/Player/Player_Esneider.prefab");
            var root = Object.Instantiate(prefab); float oldScale = Time.timeScale;
            try
            {
                Time.timeScale = 1f; yield return null; yield return null;
                var actions = root.GetComponent<PlayerActions>(); var inventory = root.GetComponent<Inventory>();
                var health = root.GetComponent<Health>(); var viewmodel = root.GetComponentInChildren<ViewmodelController>();
                Assert.IsNotNull(viewmodel); inventory.syringes = 1;
                health.ApplyDamage(new DamageInfo { amount = 50, attackId = Esneider.Core.AttackIds.Next() });
                float beforeHealth = health.Current;
                Assert.IsTrue(actions.RequestHeal()); yield return null;
                Assert.IsNotNull(viewmodel.ActiveSyringeModel, "la jeringa debe aparecer durante la acción");
                var stopper = viewmodel.ActiveSyringeModel.GetComponentsInChildren<Transform>(true).Single(t => t.name == "stopper");
                float startZ = stopper.localPosition.z;
                yield return new WaitForSeconds(.9f);
                Assert.Greater(viewmodel.SyringePress01, .2f); Assert.Less(stopper.localPosition.z, startZ - .004f);
                Assert.AreEqual(beforeHealth, health.Current, "la cura no ocurre antes del commit");
                yield return new WaitForSeconds(.35f);
                Assert.AreEqual(0, inventory.syringes); Assert.Greater(health.Current, beforeHealth);
                Assert.Greater(viewmodel.SyringePress01, .95f);
                yield return new WaitForSeconds(.5f);
                Assert.IsNull(viewmodel.ActiveSyringeModel, "el prop se retira al terminar la acción");
            }
            finally { Time.timeScale = oldScale; Object.Destroy(root); }
#else
            Assert.Ignore("Editor prefab integration test"); yield break;
#endif
        }
    }
}
