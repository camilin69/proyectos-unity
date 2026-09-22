using System.Linq;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;

namespace Esneider.Tests
{
    public class CabinetAssetTests
    {
        [TestCase("OBJ-007_ArmarioPreparacion")]
        [TestCase("OBJ-024_LockerSeguridad")]
        [TestCase("OBJ-025_ArmarioEscopeta")]
        [TestCase("OBJ-026_GabineteSuministros")]
        public void SeparateLeavesOpenOutwardsAndClearTheInterior(string asset)
        {
            var prefab=AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Game/Prefabs/Environment/"+asset+".prefab");
            Assert.That(prefab,Is.Not.Null);
            var go=Object.Instantiate(prefab);go.transform.position=Vector3.up*1000;
            try
            {
                Assert.That(go.GetComponentsInChildren<MeshFilter>().Length,Is.EqualTo(3));
                var leaves=go.GetComponentsInChildren<Transform>().Where(t=>t.name.Contains("DoorL") || t.name.Contains("DoorR")).ToArray();
                Assert.That(leaves.Length,Is.EqualTo(2));
                var ray=new Ray(new Vector3(.20f,1000.9f,-2),Vector3.forward);
                Physics.SyncTransforms();
                Assert.That(leaves.Any(t=>{RaycastHit hit;return t.GetComponent<BoxCollider>().Raycast(ray,out hit,3);}),Is.True,"Closed cabinet must block access");
                var hinges=leaves.Select(t=>t.position).ToArray();
                for(int i=0;i<leaves.Length;i++)leaves[i].localRotation=Quaternion.Euler(0,leaves[i].name.Contains("DoorL") ? 108 : -108,0)*leaves[i].localRotation;
                Physics.SyncTransforms();
                Assert.That(leaves.Any(t=>{RaycastHit hit;return t.GetComponent<BoxCollider>().Raycast(ray,out hit,3);}),Is.False,"Open leaves must clear interior access");
                for(int i=0;i<leaves.Length;i++)
                {
                    Assert.That(Vector3.Distance(leaves[i].position,hinges[i]),Is.LessThan(.00001f));
                    Assert.That(leaves[i].GetComponent<BoxCollider>().bounds.min.z,Is.LessThan(-.55f),"Leaf must swing out, not into shelves");
                }
            }
            finally {Object.DestroyImmediate(go);}
        }
    }
}
