using NUnit.Framework;
using UnityEditor;
using UnityEngine;
using Esneider.World;

namespace Esneider.Tests
{
    public class ClinicalArmTests
    {
        [Test] public void PrefabWaitsMovesSlowlyReturnsAndFreezesOnPause()
        {
            var prefab=AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Game/Prefabs/Environment/OBJ-050_BrazoClinico.prefab");
            Assert.IsNotNull(prefab);var root=Object.Instantiate(prefab);
            try
            {
                var motion=root.GetComponent<ClinicalArmMotion>();
                Assert.AreEqual(2,motion.shoulder.GetComponentsInChildren<MeshFilter>().Length,"Both moving meshes must follow the pivots");
                var fore=motion.elbow.GetComponentInChildren<MeshFilter>();Assert.IsNotNull(fore);
                var point=fore.transform.TransformPoint(fore.sharedMesh.vertices[0]);
                motion.Advance(14);Assert.IsFalse(motion.Moving);
                Assert.That(Quaternion.Angle(motion.shoulder.localRotation,Quaternion.identity),Is.LessThan(.001f));
                motion.Advance(3);Assert.IsTrue(motion.Moving);
                Assert.That(Vector3.Distance(point,fore.transform.TransformPoint(fore.sharedMesh.vertices[0])),Is.GreaterThan(.005f),"Actual imported geometry must move");
                Assert.That(Quaternion.Angle(motion.shoulder.localRotation,Quaternion.identity),Is.EqualTo(6).Within(.01f));
                var before=motion.elbow.rotation;motion.Advance(0);Assert.AreEqual(before,motion.elbow.rotation);
                motion.Advance(3);Assert.IsFalse(motion.Moving);
                Assert.That(Quaternion.Angle(motion.elbow.localRotation,Quaternion.identity),Is.LessThan(.001f));
                Assert.AreEqual(1,root.GetComponentsInChildren<Collider>().Length,"Only mount collision; no tool damage collider");
                Assert.IsNotNull(motion.servo.clip);
            }
            finally{Object.DestroyImmediate(root);}
        }
    }
}
