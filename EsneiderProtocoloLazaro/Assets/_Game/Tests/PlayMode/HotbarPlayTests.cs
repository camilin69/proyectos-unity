using System.Collections;
using System.Linq;
using Esneider.Core;
using Esneider.Core.Persistence;
using Esneider.Player;
using Esneider.World;
using Esneider.UI;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;
using UnityEngine.SceneManagement;
#if UNITY_EDITOR
using UnityEditor;
#endif

namespace Esneider.Tests
{
    public class HotbarPlayTests
    {
        [UnityTest]
        public IEnumerator CollectionOrderSelectionHandsAndCheckpointStayConsistent()
        {
#if UNITY_EDITOR
            var root=Object.Instantiate(AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Game/Prefabs/Player/Player_Esneider.prefab"));
            var ui=new GameObject("HotbarTest",typeof(Canvas),typeof(InventoryHotbar));
            var pickup=new GameObject("PickupTest",typeof(Pickup));
            var service=new GameObject("CheckpointTest",typeof(CheckpointService));
            try
            {
                var pc=root.GetComponent<PlayerController>();pc.enabled=false;pc.motor.enabled=false;
                var inv=pc.inventory;var actions=pc.actions;ui.GetComponent<InventoryHotbar>().player=pc;
                yield return null;yield return null;
                var p=pickup.GetComponent<Pickup>();
                foreach(var kind in new[]{PickupKind.Ration,PickupKind.Flashlight,PickupKind.Syringe,PickupKind.Crowbar,PickupKind.Pistol})
                {p.kind=kind;p.amount=1;Assert.Greater(inv.TryPickup(p),0);}
                CollectionAssert.AreEqual(new[]{PickupKind.Ration,PickupKind.Flashlight,PickupKind.Syringe,PickupKind.Crowbar,PickupKind.Pistol},inv.hotbarOrder);
                Assert.IsTrue(actions.RequestSelectSlot(3));yield return new WaitForSeconds(.7f);
                Assert.AreEqual(3,inv.selectedSlot);Assert.AreEqual(Core.Data.WeaponKind.Melee,actions.ActiveWeapon);
                p.kind=PickupKind.Shotgun;p.amount=1;inv.TryPickup(p);Assert.AreEqual(3,inv.selectedSlot);
                Assert.IsTrue(actions.RequestSelectSlot(0));yield return null;yield return null;
                Assert.IsNull(actions.ActiveWeapon);
                var held=root.GetComponentsInChildren<Transform>().Single(t=>t.name=="Held_Ration");Assert.AreEqual("hand_R",held.parent.name);
                var flash=root.GetComponentsInChildren<Transform>().Single(t=>t.name=="FlashlightModel");Assert.AreEqual("hand_L",flash.parent.name);
                pc.health.ResetTo(30);Assert.IsTrue(actions.RequestUseSelected());yield return new WaitForSeconds(2.2f);
                Assert.AreEqual(0,inv.rations);Assert.AreEqual(1,inv.syringes,"Using selected ration must not consume syringe");
                Assert.IsTrue(actions.RequestSelectSlot(8));yield return null;yield return null;
                var bar=ui.GetComponent<InventoryHotbar>();Assert.AreEqual(8,bar.SelectedSlot);StringAssert.StartsWith("9",bar.SlotText(8));
                Assert.AreEqual(9,ui.GetComponentsInChildren<Transform>().Count(t=>t.name.StartsWith("Slot_")));
                var cps=service.GetComponent<CheckpointService>();var saved=JsonUtility.FromJson<SaveData>(JsonUtility.ToJson(cps.Capture("CP-TEST",pc,"REG-S1")));
                inv.hotbarOrder.Reverse();inv.selectedSlot=2;inv.rations=2;
                Assert.IsTrue(cps.RestoreInto(saved,pc));CollectionAssert.AreEqual(saved.hotbarOrder,inv.CaptureHotbar());Assert.AreEqual(8,inv.selectedSlot);Assert.AreEqual(0,inv.rations);
            }
            finally{Object.Destroy(root);Object.Destroy(ui);Object.Destroy(pickup);Object.Destroy(service);Time.timeScale=1;}
#else
            yield break;
#endif
        }

        [UnityTest]
        public IEnumerator AnimatedDoorCanOpenCloseAndOpenAgain()
        {
#if UNITY_EDITOR
            WorldStateRegistry.ResetSession();
            yield return UnityEditor.SceneManagement.EditorSceneManager.LoadSceneAsyncInPlayMode("Assets/_Game/Scenes/Regions/REG-S1.unity",new LoadSceneParameters(LoadSceneMode.Additive));
            var scene=SceneManager.GetSceneByName("REG-S1");
            try
            {
                var animated=scene.GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<DoorAnimated>()).First(d=>d.door.doorId=="D01");
                var door=animated.door;door.openSeconds=.1f;door.SnapOpen(false);yield return new WaitForSeconds(.2f);
                var col=animated.leafColliders[0];Vector3 closed=col.bounds.center;
                door.SetOpen(true);yield return new WaitForSeconds(.3f);Assert.Greater(Vector3.Distance(closed,col.bounds.center),.5f);
                door.SetOpen(false);yield return new WaitForSeconds(.3f);Assert.Less(Vector3.Distance(closed,col.bounds.center),.05f);
                door.SetOpen(true);yield return new WaitForSeconds(.3f);Assert.Greater(Vector3.Distance(closed,col.bounds.center),.5f);
                var gate=scene.GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<Door>()).First(d=>d.doorId=="D06");
                WorldStateRegistry.ResetSession();Assert.IsFalse(gate.Allowed);StringAssert.Contains("palanca",gate.Prompt);
                var lever=scene.GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<Mechanism>()).First(m=>m.grantsFlag==ObjectiveService.PermisoServicio);
                lever.Interact(gate.gameObject);Assert.IsTrue(gate.Allowed);
                foreach(var entry in scene.GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<Door>()).Where(d=>d.doorId=="D04" || d.doorId=="D06"))
                {
                    entry.openSeconds=.1f;entry.SnapOpen(false);yield return new WaitForSeconds(.2f);
                    entry.Interact(gate.gameObject);yield return new WaitForSeconds(.3f);
                    Assert.IsTrue(entry.isOpen,entry.doorId);Physics.SyncTransforms();
                    var start=entry.transform.position-Vector3.right*1.5f;
                    var blockers=Physics.CapsuleCastAll(start+Vector3.up*.4f,start+Vector3.up*1.4f,.3f,Vector3.right,3f,GameLayers.Mask(GameLayers.WorldStatic,GameLayers.DynamicProp),QueryTriggerInteraction.Ignore);
                    Assert.IsEmpty(blockers,entry.doorId+" must clear a player-sized passage");
                }
            }
            finally {SceneManager.UnloadSceneAsync(scene);}
#else
            yield break;
#endif
        }
    }
}
