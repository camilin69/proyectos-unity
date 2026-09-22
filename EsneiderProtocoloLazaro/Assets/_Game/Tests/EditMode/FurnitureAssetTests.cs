using System.Linq;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;

namespace Esneider.Tests
{
    public class FurnitureAssetTests
    {
        static GameObject Load(string asset) => AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Game/Prefabs/Environment/"+asset+".prefab");

        [TestCase("OBJ-017_BancoTrabajo")]
        [TestCase("OBJ-018_Mordaza")]
        [TestCase("OBJ-028_EstanteriaIndustrial")]
        [TestCase("OBJ-030_ContenedorTecnico")]
        [TestCase("OBJ-038_MesaOficina")]
        [TestCase("OBJ-039_SillaUsada")]
        [TestCase("OBJ-072_RackControl")]
        public void FurnitureHasBakedMaterialAndPrimitiveColliders(string asset)
        {
            var prefab=Load(asset); Assert.IsNotNull(prefab,asset);
            Assert.That(prefab.transform.localPosition.sqrMagnitude,Is.LessThan(.000001f),"Prefab root must remain at floor origin");
            var meshes=prefab.GetComponentsInChildren<MeshFilter>(); Assert.That(meshes.Length,Is.EqualTo(1));
            Assert.That(meshes[0].sharedMesh.subMeshCount,Is.EqualTo(1));
            Assert.That(Mathf.Abs(meshes[0].sharedMesh.vertices.Min(v=>meshes[0].transform.TransformPoint(v).y)),Is.LessThan(.002f),"Mesh does not touch its placement floor");
            var material=prefab.GetComponentInChildren<Renderer>().sharedMaterial;
            Assert.That(material.shader.name,Is.EqualTo("Universal Render Pipeline/Lit"));
            foreach(var property in new[]{"_BaseMap","_BumpMap","_MetallicGlossMap"}) Assert.IsNotNull(material.GetTexture(property),asset+"/"+property);
            var colliders=prefab.GetComponentsInChildren<Collider>(); Assert.That(colliders.Length,Is.GreaterThan(0));
            Assert.IsTrue(colliders.All(c=>c is BoxCollider && !c.isTrigger));
        }

        [TestCase("OBJ-017_BancoTrabajo",-.6f,.4f,0f,.87f)]
        [TestCase("OBJ-038_MesaOficina",-.3f,.2f,.54f,.3f)]
        [TestCase("OBJ-028_EstanteriaIndustrial",0f,.5f,-.62f,.45f)]
        public void OpenSpacePassesRayButSolidFurnitureStopsIt(string asset,float openX,float openY,float solidX,float solidY)
        {
            var root=Object.Instantiate(Load(asset));
            try
            {
                root.transform.SetPositionAndRotation(Vector3.zero,Quaternion.identity); Physics.SyncTransforms();
                var colliders=root.GetComponentsInChildren<Collider>();
                bool Hit(float x,float y) => colliders.Any(c=>c.Raycast(new Ray(new Vector3(x,y,-2),Vector3.forward),out _,4));
                Assert.IsFalse(Hit(openX,openY),"Invisible wall across authored opening: "+asset);
                Assert.IsTrue(Hit(solidX,solidY),"Ray passed through a solid load or furniture body: "+asset);
            }
            finally { Object.DestroyImmediate(root); }
        }
    }
}
