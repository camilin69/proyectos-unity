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
    public class GraftedAdultPlayTests
    {
        [UnityTest]
        public IEnumerator PreservedSubjectStartsDesynchronisedAndFreezesWithGamePause()
        {
#if UNITY_EDITOR
            var root = Object.Instantiate(AssetDatabase.LoadAssetAtPath<GameObject>(
                "Assets/_Game/Prefabs/Environment/HUM-02_AdultoInjertos.prefab"));
            var subject = root.GetComponent<PreservedSubject>(); subject.phaseOffset = .61f;
            var animator = subject.animator; animator.cullingMode = AnimatorCullingMode.AlwaysAnimate;
            float oldTimeScale = Time.timeScale;
            try
            {
                Time.timeScale = 1; yield return null; yield return null;
                Assert.That(animator.GetCurrentAnimatorStateInfo(0).normalizedTime, Is.InRange(.60f, .80f));
                var chest = root.GetComponentsInChildren<Transform>().Single(t => t.name == "chest");
                var before = chest.position; yield return new WaitForSeconds(.45f);
                Assert.Greater(Vector3.Distance(before, chest.position), .0001f);
                Time.timeScale = 0; yield return null; before = chest.position;
                yield return new WaitForSecondsRealtime(.1f);
                Assert.Less(Vector3.Distance(before, chest.position), .00001f);
            }
            finally { Time.timeScale = oldTimeScale; Object.Destroy(root); }
#else
            Assert.Ignore("Editor prefab integration test"); yield break;
#endif
        }
    }
}
