using System.Linq;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;

namespace Esneider.Tests
{
    public class WorkshopAssetTests
    {
        static GameObject Load(string id) => AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Game/Prefabs/Environment/"+id+".prefab");
        [TestCase("OBJ-019_TaladroFijo",.6f,1.6f,.5f,true)]
        [TestCase("OBJ-023_BandejaPiezas",.45f,.07f,.3f,true)]
        [TestCase("OBJ-031_BombaIndustrial",1.5f,1f,.8f,true)]
        [TestCase("OBJ-032_GeneradorLocal",3f,1.8f,1.5f,true)]
        [TestCase("OBJ-034_ValvulaBridada",.73f,.7025f,.45f,true)]
        [TestCase("OBJ-035_Extintor",.214f,.55f,.20f,false)]
        [TestCase("OBJ-036_SoldadorCarrito",.9f,.8f,.5f,true)]
        [TestCase("OBJ-037_Herramientas",.274f,.032f,.274f,false)]
        [TestCase("OBJ-004_UnidadTermica",1.2f,1f,.67f,true)]
        [TestCase("OBJ-011_NucleoSellado",1f,.81f,.645f,true)]
        [TestCase("OBJ-013_VigaDeformada",4.025f,.95f,.3274f,true)]
        [TestCase("OBJ-047_SoporteFluidos",.548f,1.692f,.5762f,true)]
        [TestCase("OBJ-049_BandejaInstrumental",.5f,.06f,.35f,true)]
        [TestCase("OBJ-051_LavamanosIndustrial",.8f,.8998f,.618f,true)]
        [TestCase("OBJ-052_RejillaDrenaje",.6f,.0377f,.2f,true)]
        [TestCase("OBJ-053_Biombo",1.502f,1.8f,.498f,true)]
        [TestCase("OBJ-044_MesaProcedimientos",2.1f,.9f,.8217f,true)]
        [TestCase("OBJ-076_ColumnaServicios",1f,5f,1f,true)]
        [TestCase("OBJ-040_TazaTermo",.302f,.25f,.088f,false)]
        [TestCase("OBJ-040B_TazaTermoRota",.30f,.25f,.088f,false)]
        [TestCase("OBJ-058_AtrilAdmision",.6f,1.2005f,.4673f,true)]
        [TestCase("OBJ-063_PizarraTurnos",1.2f,.8f,.0935f,false)]
        [TestCase("OBJ-064_ContenedorClinico",.4f,.6f,.3155f,true)]
        [TestCase("OBJ-021_PlataformaRobot",2.6f,.35f,1.3985f,true)]
        [TestCase("OBJ-022_CabezaCustodioAntigua",.3f,.35f,.2473f,false)]
        public void WorkshopDeliveryHasCorrectSizeMaterialAndCollisionPolicy(string id,float x,float y,float z,bool solid)
        {
            var prefab=Load(id);Assert.IsNotNull(prefab,id);
            Assert.That(prefab.transform.localPosition.sqrMagnitude,Is.LessThan(.000001f),"Nonzero export origin");
            var mf=prefab.GetComponentInChildren<MeshFilter>();Assert.IsNotNull(mf);
            Assert.That(mf.sharedMesh.subMeshCount,Is.EqualTo(1));
            var size=mf.sharedMesh.bounds.size;
            Assert.That(size.x,Is.EqualTo(x).Within(.035f));Assert.That(size.y,Is.EqualTo(y).Within(.015f));Assert.That(size.z,Is.EqualTo(z).Within(.015f));
            Assert.That(Mathf.Abs(mf.sharedMesh.bounds.min.y),Is.LessThan(.002f),"No floor contact");
            var material=prefab.GetComponentInChildren<Renderer>().sharedMaterial;
            foreach(var property in new[]{"_BaseMap","_BumpMap","_MetallicGlossMap"}) Assert.IsNotNull(material.GetTexture(property),id+"/"+property);
            var colliders=prefab.GetComponentsInChildren<Collider>();Assert.That(colliders.Length>0,Is.EqualTo(solid));
            Assert.IsTrue(colliders.All(c=>c is BoxCollider && !c.isTrigger));
        }

        [TestCase("OBJ-031_BombaIndustrial",-.33f,.46f)]
        [TestCase("OBJ-032_GeneradorLocal",-1.02f,.70f)]
        [TestCase("OBJ-019_TaladroFijo",0f,1.34f)]
        public void MachineBodyStopsProjectileRay(string id,float x,float y)
        {
            var root=Object.Instantiate(Load(id));
            try
            {
                root.transform.SetPositionAndRotation(Vector3.zero,Quaternion.identity);Physics.SyncTransforms();
                Assert.IsTrue(root.GetComponentsInChildren<Collider>().Any(c=>c.Raycast(new Ray(new Vector3(x,y,-2),Vector3.forward),out _,4)),id+" has a nonblocking housing");
            }
            finally { Object.DestroyImmediate(root); }
        }
    }
}
