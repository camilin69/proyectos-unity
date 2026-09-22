using System.Collections;
using System.Reflection;
using Esneider.AI;
using Esneider.Core;
using Esneider.Core.Data;
using Esneider.World;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;

namespace Esneider.Tests
{
    public class RobotAttackFacingPlayTests
    {
        [UnityTest]
        public IEnumerator AttackCannotFireBackwardAndNavigationYieldsDuringPreparation()
        {
            var definition=ScriptableObject.CreateInstance<EnemyDefinition>();definition.kind=EnemyKind.Vigia;
            definition.visionRangeLit=20;definition.visionAngleLit=120;definition.closeRange=10;
            var robot=SandboxFactory.BuildEnemy(definition,"FacingRegression",new Vector3(1000,100,1000),Color.white,1.36f);
            var target=new GameObject("FacingTarget");
            try
            {
                var brain=robot.GetComponent<EnemyBrain>();brain.enabled=false;
                var perception=robot.GetComponent<EnemyPerception>();perception.enabled=false;perception.target=target.transform;EnemyPerception.PlayerInDarkness=false;
                target.transform.position=robot.transform.position+Vector3.forward*4;
                typeof(EnemyBrain).GetField("_player",BindingFlags.Instance|BindingFlags.NonPublic).SetValue(brain,target.transform);
                typeof(EnemyBrain).GetMethod("Transition",BindingFlags.Instance|BindingFlags.NonPublic).Invoke(brain,new object[]{EnemyState.Prepare});
                Assert.IsFalse(robot.GetComponent<UnityEngine.AI.NavMeshAgent>().updateRotation);
                robot.transform.rotation=Quaternion.Euler(0,180,0);Physics.SyncTransforms();
                var emit=typeof(EnemyBrain).GetMethod("Emit",BindingFlags.Instance|BindingFlags.NonPublic);
                Assert.IsFalse(brain.FacingTarget);emit.Invoke(brain,null);Assert.AreEqual(0,brain.attacksEmitted);
                robot.transform.rotation=Quaternion.identity;Physics.SyncTransforms();
                Assert.IsTrue(brain.FacingTarget);emit.Invoke(brain,null);Assert.AreEqual(1,brain.attacksEmitted);
                yield return null;
            }
            finally
            {
                foreach(var projectile in Object.FindObjectsByType<Esneider.Combat.Projectile>(FindObjectsSortMode.None)) projectile.Despawn();
                Object.Destroy(robot);Object.Destroy(target);Object.Destroy(definition);
            }
        }
    }
}
