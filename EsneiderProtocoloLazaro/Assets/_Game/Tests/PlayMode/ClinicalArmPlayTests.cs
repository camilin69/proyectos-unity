using System.Collections;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;
using Esneider.World;

namespace Esneider.Tests
{
    public class ClinicalArmPlayTests
    {
        [UnityTest] public IEnumerator RuntimeCycleFreezesDuringGamePauseAndStopsServoAtRest()
        {
            GameObject prefab=null;
#if UNITY_EDITOR
            prefab=UnityEditor.AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Game/Prefabs/Environment/OBJ-050_BrazoClinico.prefab");
#endif
            Assert.IsNotNull(prefab);var root=Object.Instantiate(prefab);root.transform.position=Vector3.up*500;
            var motion=root.GetComponent<ClinicalArmMotion>();float old=Time.timeScale;
            try
            {
                Time.timeScale=1;motion.Sample(16);
                yield return null;yield return null;
                Assert.IsTrue(motion.Moving);Assert.IsTrue(motion.servo.isPlaying);
                Time.timeScale=0;float phase=motion.PhaseSeconds;var rotation=motion.elbow.rotation;
                yield return new WaitForSecondsRealtime(.12f);
                Assert.AreEqual(phase,motion.PhaseSeconds);Assert.AreEqual(rotation,motion.elbow.rotation);
                Assert.IsFalse(motion.servo.isPlaying);
                Time.timeScale=1;motion.Sample(19.95f);
                yield return new WaitForSeconds(.15f);
                Assert.IsFalse(motion.Moving);Assert.IsFalse(motion.servo.isPlaying);
            }
            finally{Time.timeScale=old;Object.Destroy(root);}
        }
    }
}
