using System.Collections;
using System.Linq;
using Esneider.Core;
using Esneider.Core.Data;
using Esneider.Player;
using Esneider.UI;
using Esneider.World;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;
#if UNITY_EDITOR
using UnityEditor;
#endif

namespace Esneider.Tests
{
    public class GameplayRepairPlayTests
    {
        [UnityTest]
        public IEnumerator RobotFaceMatchesVisionAndWallsBlockDetection()
        {
#if UNITY_EDITOR
            var robot = new GameObject("FacingTest"); robot.transform.position = new Vector3(1000, 100, 1000);
            var target = new GameObject("FacingTarget");
            var wall = GameObject.CreatePrimitive(PrimitiveType.Cube);
            var definition = ScriptableObject.CreateInstance<EnemyDefinition>();
            try
            {
                definition.visionRangeLit = 15; definition.visionAngleLit = 100; definition.closeRange = 1;
                var perception = robot.AddComponent<Esneider.AI.EnemyPerception>(); perception.definition = definition; perception.target = target.transform;
                Esneider.AI.EnemyPerception.PlayerInDarkness = false;
                var model = Object.Instantiate(AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Game/Prefabs/Enemies/BOT-01_Vigia.prefab"), robot.transform);
                var animation = robot.AddComponent<Esneider.AI.EnemyAnimator>(); animation.enabled = false;
                animation.animator = model.GetOrAdd<Animator>(); animation.prefix = "Vigia"; animation.AlignVisualFacing();
                Assert.Greater(Vector3.Dot(model.transform.TransformDirection(Vector3.back), robot.transform.forward), .999f, "The authored face must point along the sensor cone");
                target.transform.position = robot.transform.position + robot.transform.forward * 5;
                wall.transform.position = robot.transform.position + Vector3.right * 20;
                Physics.SyncTransforms(); perception.Sense(1.3f);
                Assert.IsTrue(perception.SeesTarget); Assert.IsTrue(perception.Confirmed);
                target.transform.position = robot.transform.position - robot.transform.forward * 5;
                perception.Sense(3); Assert.IsFalse(perception.SeesTarget); Assert.IsFalse(perception.Confirmed);
                robot.transform.rotation = Quaternion.Euler(0,180,0);
                perception.Sense(1.3f); Assert.IsTrue(perception.SeesTarget, "Turning the face must turn vision too");
                wall.layer = GameLayers.WorldStatic; wall.transform.position = robot.transform.position + new Vector3(0,1,-2.5f); wall.transform.localScale = new Vector3(4,3,.3f);
                Physics.SyncTransforms(); perception.Sense(3); Assert.IsFalse(perception.SeesTarget); Assert.IsFalse(perception.Confirmed);
                Assert.AreEqual(0f, NoiseSystem.EffectiveRadius(new NoiseEvent { position = target.transform.position + Vector3.up, radius=20, source=target }, robot.transform.position + Vector3.up));
                yield return null;
            }
            finally { Object.Destroy(robot); Object.Destroy(target); Object.Destroy(wall); Object.Destroy(definition); }
#else
            Assert.Ignore("Editor integration test"); yield break;
#endif
        }

        [UnityTest]
        public IEnumerator ReadingPickupImmediatelyShowsFullTextAndResumes()
        {
            bool skip=MenuController.SkipTitle;MenuController.SkipTitle=true;
            var flowObject=new GameObject("ReadingFlow",typeof(GameFlowController));
            var menuObject=new GameObject("ReadingMenus",typeof(MenuController));
            var reader=new GameObject("Reader",typeof(Inventory));
            var paper=new GameObject("Document",typeof(Pickup));
            try
            {
                var flow=flowObject.GetComponent<GameFlowController>();flow.StartAttempt();
                yield return null;yield return null;
                var pickup=paper.GetComponent<Pickup>();pickup.kind=PickupKind.Document;pickup.documentId="DOC-01";
                pickup.Interact(reader);
                var menu=menuObject.GetComponent<MenuController>();Assert.AreEqual("ReadDocument",menu.Current);
                Assert.AreEqual(GameState.Paused,flow.State);
                var body=menu.GetComponentsInChildren<UnityEngine.UI.Text>().Single(t=>t.name=="DocumentText");
                StringAssert.Contains(DocumentLibrary.Get("DOC-01").text,body.text);
                menu.Resume();Assert.IsFalse(menu.IsOpen);Assert.AreEqual(GameState.Playing,flow.State);
            }
            finally {Time.timeScale=1;MenuController.SkipTitle=skip;Object.Destroy(flowObject);Object.Destroy(menuObject);Object.Destroy(reader);Object.Destroy(paper);}
        }

        [UnityTest]
        public IEnumerator RealPlayerShowsHandsKeepsWeaponsAndPlaysAttack()
        {
#if UNITY_EDITOR
            var root = Object.Instantiate(AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Game/Prefabs/Player/Player_Esneider.prefab"));
            var ui = new GameObject("TestHotbar", typeof(Canvas), typeof(InventoryHotbar));
            var pickup = new GameObject("TestPistol", typeof(Pickup));
            try
            {
                var player = root.GetComponent<PlayerController>(); player.enabled = false;
                var inv = player.inventory; inv.hasCrowbar = true;
                ui.GetComponent<InventoryHotbar>().player = player;
                yield return null; yield return null;
                yield return null;
                var cameraTransform = root.GetComponentInChildren<Camera>().transform;
                var rig = cameraTransform.Find("Arms").GetComponentInChildren<Animator>();
                foreach (var side in new[] { "L", "R" })
                {
                    var hand = rig.GetComponentsInChildren<Transform>().Single(t => t.name == "hand_" + side);
                    var thumb = hand.GetComponentsInChildren<Transform>().Single(t => t.name == "thumb_" + side);
                    float handX = cameraTransform.InverseTransformPoint(hand.position).x;
                    float thumbX = cameraTransform.InverseTransformPoint(thumb.position).x;
                    Assert.That(side == "L" ? handX < 0 : handX > 0, "Each anatomical hand must occupy its own screen side");
                    Assert.Less(Mathf.Abs(thumbX), Mathf.Abs(handX), "Thumbs must face inward in the idle pose");
                }
                Assert.IsTrue(player.actions.RequestEquip(WeaponKind.Melee)); yield return new WaitForSeconds(.65f);
                pickup.GetComponent<Pickup>().kind = PickupKind.Pistol; pickup.GetComponent<Pickup>().Interact(root);
                Assert.IsTrue(inv.hasCrowbar && inv.hasPistol); Assert.AreEqual(WeaponKind.Melee, player.actions.ActiveWeapon);
                var cam = root.GetComponentInChildren<Camera>();
                var hands = cam.transform.Find("Arms"); Assert.IsNotNull(hands);
                var palm = hands.GetComponentsInChildren<SkinnedMeshRenderer>().First(r=>r.name=="palm_R");
                var mesh = new Mesh(); palm.BakeMesh(mesh);
                Vector3 center = palm.transform.TransformPoint(mesh.bounds.center); Object.Destroy(mesh);
                var view = cam.WorldToViewportPoint(center);
                Assert.That(view.z, Is.GreaterThan(cam.nearClipPlane), "Hands must be in front of the camera");
                Assert.That(view.x, Is.InRange(0f,1f)); Assert.That(view.y, Is.InRange(0f,1f));
                Assert.IsNotNull(hands.GetComponentsInChildren<Transform>().FirstOrDefault(t=>t.name=="Weapon_Melee"));
                Assert.IsTrue(player.actions.RequestAttack()); yield return new WaitForSeconds(.15f);
                Assert.AreEqual(ActionKind.Attack, player.actions.CurrentKind);
                yield return new WaitForSeconds(.85f);
                Assert.IsTrue(player.actions.RequestEquip(WeaponKind.Pistol)); yield return new WaitForSeconds(.75f);
                Assert.AreEqual(1, ui.GetComponent<InventoryHotbar>().SelectedSlot);
                var gun=hands.GetComponentsInChildren<Transform>().Single(t=>t.name=="Weapon_Pistol");
                Assert.Greater(Vector3.Dot(gun.forward,cam.transform.forward),.9f,"Pistol barrel must point forward rather than into the floor");
                var torch=hands.GetComponentsInChildren<Transform>(true).Single(t=>t.name=="FlashlightModel");
                Assert.Greater(Vector3.Dot(torch.forward,cam.transform.forward),.9f,"Flashlight model must match the beam direction");
                StringAssert.Contains("VARILLA", ui.GetComponent<InventoryHotbar>().SlotText(0));
                Assert.IsTrue(player.actions.RequestAttack()); yield return new WaitForSeconds(.08f);
                Assert.AreEqual("PistolFire", player.actions.Current.Type);
                Assert.Greater(Quaternion.Angle(hands.localRotation, Quaternion.Euler(0,180,0)), .5f);
                yield return new WaitForSeconds(.5f);
                var enemy = GameObject.CreatePrimitive(PrimitiveType.Capsule);
                try
                {
                    enemy.layer=GameLayers.Enemy;enemy.transform.position=root.transform.position+Vector3.forward*1.4f;
                    var cap=enemy.GetComponent<CapsuleCollider>();cap.height=1.36f;cap.radius=.28f;cap.center=new Vector3(0,.68f,0);
                    var health=enemy.AddComponent<Health>();health.maxHp=60;health.ResetTo(60);
                    cam.transform.LookAt(enemy.transform.position+Vector3.up*1.18f);
                    Physics.SyncTransforms();
                    Assert.IsTrue(player.actions.RequestEquip(WeaponKind.Melee));yield return new WaitForSeconds(.75f);
                    for(int i=0;i<4&&!health.IsDead;i++)
                    {
                        Assert.IsTrue(player.actions.RequestAttack());yield return new WaitForSeconds(1.1f);
                    }
                    Assert.IsTrue(health.IsDead,"Aiming down at the short robot must damage and kill it");
                }
                finally {Object.Destroy(enemy);}
            }
            finally { Object.Destroy(root); Object.Destroy(ui); Object.Destroy(pickup); }
#else
            Assert.Ignore("Editor integration test"); yield break;
#endif
        }
    }
}
