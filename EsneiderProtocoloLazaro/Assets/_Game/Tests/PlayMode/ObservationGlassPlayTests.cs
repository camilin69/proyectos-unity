using System.Collections;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;
using Esneider.Combat;
#if UNITY_EDITOR
using UnityEditor;
#endif

namespace Esneider.Tests
{
    public class ObservationGlassPlayTests
    {
        [UnityTest]
        public IEnumerator NetBoltAndBossBoltStopAtGlassFromEitherSide()
        {
#if UNITY_EDITOR
            var root = Object.Instantiate(AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Game/Prefabs/Environment/OBJ-060_VidrioObservacion.prefab"));
            root.transform.position = new Vector3(10000, 0, 0); float oldTimeScale = Time.timeScale; Projectile projectile = null;
            try
            {
                Time.timeScale = 1; Physics.SyncTransforms();
                foreach (var kind in new[] { ProjectileKind.Net, ProjectileKind.Bolt, ProjectileKind.BossBolt })
                    foreach (int sign in new[] { -1, 1 })
                    {
                        projectile = Projectile.Spawn(kind, root.transform.position + new Vector3(0, 1.25f, sign), Vector3.forward * -sign, null, 4141, 10);
                        yield return new WaitForSeconds(.3f);
                        Assert.IsFalse(projectile.Active, kind + " must hit the glass before its lifetime expires");
                        Assert.Greater(projectile.transform.position.z * sign, 0, "Projectile must stop on its original side");
                        Assert.IsTrue(root.activeSelf); Assert.IsTrue(root.GetComponent<Collider>().enabled);
                    }
            }
            finally { if (projectile && projectile.Active) projectile.Despawn(); Time.timeScale = oldTimeScale; Object.Destroy(root); }
#else
            Assert.Ignore("Editor prefab integration test"); yield break;
#endif
        }
    }
}
