using System.Collections;
using System.Linq;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;
using Esneider.World;
#if UNITY_EDITOR
using UnityEditor;
#endif
namespace Esneider.Tests
{
    public class SleepingAdultPlayTests
    {
        [UnityTest]
        public IEnumerator AmbientBreathingAdvancesFromPhaseAndStopsWhenPaused()
        {
#if UNITY_EDITOR
            var root = Object.Instantiate(AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Game/Prefabs/Environment/HUM-01_AdultoDormido.prefab"));
            var subject = root.GetComponent<SleepingSubject>(); subject.phaseOffset = .2f; var animator = subject.animator;
            animator.cullingMode = AnimatorCullingMode.AlwaysAnimate; float oldTimeScale = Time.timeScale;
            try
            {
                Time.timeScale = 1; yield return null; yield return null;
                var bones = root.GetComponentsInChildren<Transform>(); var chest = bones.Single(t => t.name == "chest"); var head = bones.Single(t => t.name == "head");
                float phase = animator.GetCurrentAnimatorStateInfo(0).normalizedTime;
                Assert.That(phase, Is.InRange(.19f, .4f)); var before = chest.position; var supportedHead = head.position;
                yield return new WaitForSeconds(.4f); Assert.Greater(Vector3.Distance(before, chest.position), .0001f); Assert.Less(Vector3.Distance(supportedHead, head.position), .0001f);
                Time.timeScale = 0; yield return null; before = chest.position; yield return new WaitForSecondsRealtime(.1f);
                Assert.Less(Vector3.Distance(before, chest.position), .00001f);
            }
            finally { Time.timeScale = oldTimeScale; Object.Destroy(root); }
#else
            Assert.Ignore("Editor prefab integration test"); yield break;
#endif
        }
    }
}
