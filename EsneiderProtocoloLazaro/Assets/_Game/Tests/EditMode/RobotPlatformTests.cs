using System.Linq;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;

namespace Esneider.Tests
{
    public class RobotPlatformTests
    {
        [Test]
        public void MaintenanceRobotFitsAtOriginalScaleWithoutCombatComponents()
        {
            var prefab=AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Game/Prefabs/Environment/RobotMaintenance_EX38.prefab");Assert.IsNotNull(prefab);
            var root=Object.Instantiate(prefab);
            try
            {
                var robot=root.transform.Find("InertCustodio");Assert.IsNotNull(robot);Assert.AreEqual(Vector3.one,robot.localScale);
                Assert.AreEqual(0,robot.GetComponentsInChildren<MonoBehaviour>(true).Length);Assert.AreEqual(0,robot.GetComponentsInChildren<Collider>(true).Length);
                Assert.AreEqual(0,robot.GetComponentsInChildren<Animator>(true).Length);Assert.AreEqual(0,robot.GetComponentsInChildren<AudioSource>(true).Length);
                var rs=robot.GetComponentsInChildren<Renderer>();Assert.Greater(rs.Length,10);var bounds=rs[0].bounds;foreach(var r in rs)bounds.Encapsulate(r.bounds);
                Assert.LessOrEqual(bounds.size.x,2.6f);Assert.LessOrEqual(bounds.size.z,1f);Assert.That(bounds.min.y,Is.EqualTo(.28f).Within(.001f));
                Assert.That(bounds.center.x,Is.EqualTo(0).Within(.001f));Assert.That(bounds.center.z,Is.EqualTo(0).Within(.001f));
                Assert.AreEqual(1,root.GetComponentsInChildren<Collider>().Length);
                var platform=root.GetComponentsInChildren<MeshFilter>().Single(m=>m.sharedMesh.name.Contains("Plataforma"));Assert.LessOrEqual(platform.sharedMesh.triangles.Length/3,3000);
            }
            finally{Object.DestroyImmediate(root);}
        }
    }
}
