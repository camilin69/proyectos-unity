using System.Linq;
using Esneider.World;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;

namespace Esneider.Tests
{
    public class IndustrialFanTests
    {
        const string Path="Assets/_Game/Prefabs/Environment/OBJ-079_VentiladorIndustrial.prefab";
        [Test]
        public void GuardedFanPreservesRotorAxisAndBudget()
        {
            var root=AssetDatabase.LoadAssetAtPath<GameObject>(Path);Assert.IsNotNull(root);
            var fan=root.GetComponent<IndustrialFan>();Assert.IsNotNull(fan);Assert.AreEqual(new Vector3(0,.85f,0),fan.rotor.localPosition);
            var meshes=root.GetComponentsInChildren<MeshFilter>();Assert.AreEqual(2,meshes.Length);Assert.LessOrEqual(meshes.Sum(m=>m.sharedMesh.triangles.Length/3),4000);
            Assert.AreEqual(0,fan.rotor.GetComponentsInChildren<Collider>().Length);Assert.AreEqual(0,root.GetComponentsInChildren<AudioSource>().Length);
            Assert.AreEqual(UnityEngine.Rendering.ShadowCastingMode.Off,fan.rotorRenderer.shadowCastingMode);
            Assert.AreEqual(1024,fan.rotorRenderer.sharedMaterial.GetTexture("_BaseMap").width);
            var localVertices=meshes.Single(m=>m.transform.IsChildOf(fan.rotor)).sharedMesh.vertices;
            Assert.Greater(localVertices.Length,100);
        }
        [Test]
        public void RotorAdvancementPreservesPivotAndPausesAtZeroDelta()
        {
            var root=Object.Instantiate(AssetDatabase.LoadAssetAtPath<GameObject>(Path));
            try
            {
                var fan=root.GetComponent<IndustrialFan>();var position=fan.rotor.localPosition;var before=fan.rotor.localRotation;
                fan.Advance(0);Assert.Less(Quaternion.Angle(before,fan.rotor.localRotation),.001f);
                fan.Advance(.5f);Assert.That(Quaternion.Angle(before,fan.rotor.localRotation),Is.EqualTo(36).Within(.01f));
                Assert.AreEqual(position,fan.rotor.localPosition);
                fan.revolutionsPerMinute=10000;before=fan.rotor.localRotation;fan.Advance(.5f);
                Assert.That(Quaternion.Angle(before,fan.rotor.localRotation),Is.EqualTo(45).Within(.01f));
            }
            finally{Object.DestroyImmediate(root);}
        }
    }
}
