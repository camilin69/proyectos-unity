using System.Collections;
using System.Linq;
using Esneider.AI;
using Esneider.Combat;
using Esneider.Core;
using Esneider.Core.Data;
using Esneider.World;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;
#if UNITY_EDITOR
using UnityEditor;
#endif

namespace Esneider.Tests
{
    public class RobotDestructionPlayTests
    {
        [UnityTest] public IEnumerator BothRobotsExplodeOnceAndCheckpointCanReviveTheirOriginalShell()
        {
#if UNITY_EDITOR
            foreach (var kind in new[] { EnemyKind.Vigia, EnemyKind.Custodio })
            {
                var definition = AssetDatabase.LoadAssetAtPath<EnemyDefinition>("Assets/_Game/Data/Definitions/Enemy_" + kind + ".asset");
                string asset = kind == EnemyKind.Vigia ? "BOT-01_Vigia" : "BOT-02_Custodio";
                var prefab = AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Game/Prefabs/Enemies/" + asset + ".prefab");
                var robot = SandboxFactory.BuildEnemy(definition, "ExplosionTest", new Vector3(2000, 100, 2000), Color.white, 2, prefab);
                try
                {
                    var brain = robot.GetComponent<EnemyBrain>(); brain.enabled = false;
                    yield return null;
                    var original = robot.GetComponentsInChildren<Renderer>(true);
                    var health = robot.GetComponent<Health>();
                    health.ApplyDamage(new DamageInfo { amount = 9999, attackId = AttackIds.Next() });
                    var destruction = robot.GetComponent<RobotDestruction>();
                    Assert.IsNotNull(destruction); Assert.IsTrue(destruction.Hidden);
                    Assert.AreEqual(1, destruction.BurstCount); Assert.Greater(destruction.FragmentCount, 20);
                    Assert.IsTrue(original.All(r => !r.enabled));
                    Assert.IsFalse(robot.GetComponentsInChildren<Collider>().Any(c => c.enabled), "Broken robots must not block the route");
                    destruction.Explode(false); Assert.AreEqual(1, destruction.BurstCount);
                    yield return new WaitForSeconds(.3f);
                    brain.ReviveForRestore(); brain.enabled = false; health.ResetTo(health.maxHp);
                    Assert.IsFalse(destruction.Hidden); Assert.AreEqual(0, destruction.FragmentCount);
                    Assert.IsTrue(original.Any(r => r.enabled));
                    brain.MarkDeadFromSnapshot();
                    Assert.IsTrue(destruction.Hidden); Assert.AreEqual(1, destruction.BurstCount, "Loading a dead robot must not explode again");
                }
                finally { Object.Destroy(robot); }
            }
#else
            yield break;
#endif
        }
    }
}
