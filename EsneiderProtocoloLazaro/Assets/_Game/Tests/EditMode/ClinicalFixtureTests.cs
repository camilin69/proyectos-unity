using NUnit.Framework;
using UnityEngine;
using UnityEditor;

namespace Esneider.Tests
{
    public class ClinicalFixtureTests
    {
        [Test] public void LampConeOriginBelongsToHeadAndPointsDown()
        {
            var prefab=AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Game/Prefabs/Environment/OBJ-048_LamparaClinica.prefab");
            Assert.IsNotNull(prefab);
            var light=prefab.GetComponentInChildren<Light>(true);
            Assert.IsNotNull(light); Assert.IsFalse(light.enabled);
            Assert.That(Vector3.Distance(light.transform.localPosition,new Vector3(1.22f,2.085f,0)),Is.LessThan(.001f));
            Assert.That(Vector3.Dot(light.transform.forward,Vector3.down),Is.GreaterThan(.999f));
            Assert.That(prefab.GetComponentInChildren<MeshFilter>().sharedMesh.triangles.Length/3,Is.LessThanOrEqualTo(3000));
        }
    }
}
