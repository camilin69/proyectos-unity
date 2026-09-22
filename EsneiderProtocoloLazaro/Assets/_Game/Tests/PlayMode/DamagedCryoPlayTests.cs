using System.Collections;
using System.Linq;
using Esneider.World;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;
#if UNITY_EDITOR
using UnityEditor;
#endif

namespace Esneider.Tests
{
    public class DamagedCryoPlayTests
    {
        [UnityTest]
        public IEnumerator JamAttemptPlaysOnceAndHoldsDamagedRestPose()
        {
#if UNITY_EDITOR
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Game/Prefabs/Environment/OBJ-002_CamaraVaciaDanada.prefab");
            var root = Object.Instantiate(prefab); float oldScale = Time.timeScale;
            try
            {
                Time.timeScale = 4f; yield return null; yield return null;
                var sequence = root.GetComponent<DamagedCryoSequence>();
                var lid = root.GetComponentsInChildren<Transform>(true).Single(t => t.name == "lid");
                sequence.TriggerNow(); Assert.IsTrue(sequence.Attempted);
                yield return new WaitForSeconds(2.1f);
                Assert.IsTrue(sequence.Stable); Assert.That(sequence.NormalizedProgress, Is.EqualTo(1f).Within(.001f));
                Quaternion held = lid.localRotation;
                sequence.TriggerNow(); yield return new WaitForSeconds(.2f);
                Assert.Less(Quaternion.Angle(held, lid.localRotation), .01f);
            }
            finally { Time.timeScale = oldScale; Object.Destroy(root); }
#else
            Assert.Ignore("Editor prefab integration test"); yield break;
#endif
        }
    }
}
