using System.Linq;
using Esneider.Core;
using Esneider.Core.Data;
using Esneider.Core.Persistence;
using Esneider.Player;
using Esneider.World;
using NUnit.Framework;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Esneider.Tests
{
    public class AmmoCaseTests
    {
        static Pickup RestorePickup(GameObject box, PickupKind kind, int amount, string guid)
        {
            var child=new GameObject("Ammo pickup");child.transform.SetParent(box.transform,false);
            var p=child.AddComponent<Pickup>();p.kind=kind;p.amount=amount;p.guid=guid;
            var pe=child.AddComponent<PersistentEntity>();pe.guid=guid;pe.kind=EntityKind.Pickup;pe.regionId="TEST";pe.EnsureRegistered();
            box.GetComponent<AmmoCaseVisual>().pickup=p;box.GetComponent<AmmoCaseVisual>().Refresh();return p;
        }
        [TestCase(PickupKind.PistolAmmo,10,"OBJ-027_CajaMunicionPistola")]
        [TestCase(PickupKind.ShotgunAmmo,4,"OBJ-027B_CajaMunicionEscopeta")]
        public void PartialPickupAndReloadKeepRemainderThenLeaveEmptyCase(PickupKind kind,int amount,string asset)
        {
            var registry=WorldStateRegistry.Session;var saved=registry.Snapshot();registry.Restore(new RegistrySnapshot());
            var box=Object.Instantiate(AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Game/Prefabs/Environment/"+asset+".prefab"));
            var who=new GameObject("Ammo collector");
            try
            {
                var inv=who.AddComponent<Inventory>();var type=kind==PickupKind.PistolAmmo?AmmoType.Pistol:AmmoType.Shotgun;
                if(type==AmmoType.Pistol)inv.pistolReserve=inv.ReserveMax(type)-2;else inv.shotgunReserve=inv.ReserveMax(type)-2;
                var guid=LevelPlan.StableGuid("EX33-"+kind).ToString();var p=RestorePickup(box,kind,amount,guid);
                var visual=box.GetComponent<AmmoCaseVisual>();p.Interact(who);visual.Refresh();
                Assert.AreEqual(amount-2,p.amount);Assert.IsTrue(p.gameObject.activeSelf);Assert.IsTrue(visual.contents.activeSelf);
                Assert.AreEqual(inv.ReserveMax(type),inv.Reserve(type));
                long sequence=registry.Sequence;p.Interact(who);Assert.AreEqual(sequence,registry.Sequence,"Full inventory must not consume or publish");Assert.AreEqual(amount-2,p.amount);
                var checkpoint=registry.Snapshot();Object.DestroyImmediate(p.gameObject);registry.Restore(checkpoint);
                p=RestorePickup(box,kind,999,guid);Assert.AreEqual(amount-2,p.amount);Assert.IsTrue(visual.contents.activeSelf);
                Assert.AreEqual(sequence,registry.Sequence,"Hydration must not replay pickup events");
                if(type==AmmoType.Pistol)inv.pistolReserve=0;else inv.shotgunReserve=0;
                p.Interact(who);visual.Refresh();Assert.AreEqual(0,p.amount);Assert.IsFalse(p.gameObject.activeSelf);
                Assert.IsTrue(box.activeSelf);Assert.IsFalse(visual.contents.activeSelf);Assert.IsTrue(box.GetComponentsInChildren<MeshRenderer>().Any(),"Empty case must remain visible");
                checkpoint=registry.Snapshot();sequence=registry.Sequence;Object.DestroyImmediate(p.gameObject);registry.Restore(checkpoint);
                p=RestorePickup(box,kind,999,guid);Assert.IsFalse(p.gameObject.activeSelf);Assert.IsFalse(visual.contents.activeSelf);Assert.IsTrue(box.activeSelf);Assert.AreEqual(sequence,registry.Sequence);
            }
            finally { Object.DestroyImmediate(box);Object.DestroyImmediate(who);registry.Restore(saved); }
        }
        [TestCase("REG-S2",5)] [TestCase("REG-S3",11)] [TestCase("REG-S4",6)]
        public void RegionalCasesPreservePickupIdentityAndReachableSupportedPlacement(string region,int count)
        {
            var previous=SceneManager.GetActiveScene();var path="Assets/_Game/Scenes/Regions/"+region+".unity";
            var scene=SceneManager.GetSceneByPath(path);bool opened=!scene.IsValid()||!scene.isLoaded;
            if(opened)scene=EditorSceneManager.OpenScene(path,OpenSceneMode.Additive);
            try
            {
                var roots=scene.GetRootGameObjects();var cases=roots.SelectMany(g=>g.GetComponentsInChildren<AmmoCaseVisual>(true)).ToArray();Assert.AreEqual(count,cases.Length);
                var all=roots.SelectMany(g=>g.GetComponentsInChildren<Transform>(true)).ToArray();
                Physics.SyncTransforms();
                foreach(var visual in cases)
                {
                    var p=visual.pickup;Assert.IsNotNull(p);Assert.AreEqual(p.kind==PickupKind.PistolAmmo?10:4,p.amount);
                    Assert.AreEqual(LevelPlan.StableGuid(p.stableId).ToString(),p.guid);var pe=p.GetComponent<PersistentEntity>();Assert.AreEqual(p.guid,pe.guid);Assert.AreEqual(region,pe.regionId);
                    Assert.AreEqual(1,p.GetComponents<Collider>().Length);Assert.AreEqual(0,visual.GetComponents<Collider>().Length);
                    var support=all.Single(t=>t.name=="Support_"+p.stableId).GetComponent<Collider>();
                    Assert.That(visual.transform.position.y-support.bounds.max.y,Is.EqualTo(0).Within(.001f));
                    RaycastHit hit;var origin=visual.transform.position+new Vector3(0,.09f,-.8f);
                    Assert.IsTrue(Physics.Raycast(origin,Vector3.forward,out hit,1,GameLayers.Mask(GameLayers.WorldStatic,GameLayers.Interactable),QueryTriggerInteraction.Collide),p.stableId);
                    Assert.AreSame(p,hit.collider.GetComponentInParent<Pickup>(),p.stableId+" interaction occluded by "+hit.collider.name);
                }
            }
            finally { if(opened)EditorSceneManager.CloseScene(scene,true);if(previous.IsValid()&&previous.isLoaded)SceneManager.SetActiveScene(previous); }
        }
    }
}
