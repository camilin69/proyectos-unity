using System.Collections;
using System.Linq;
using Esneider.Combat;
using Esneider.Core;
using Esneider.Core.Data;
using Esneider.Player;
using Esneider.UI;
using Esneider.World;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;
using UnityEditor;

namespace Esneider.Tests
{
    public class AmmoAndProjectilePlayTests
    {
        static PlayerController Player()
        {
            var root = Object.Instantiate(AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Game/Prefabs/Player/Player_Esneider.prefab"));
            var pc = root.GetComponent<PlayerController>(); pc.enabled = false; pc.motor.enabled = false;
            pc.motor.Teleport(new Vector3(2000, 100, 2000), 0);
            return pc;
        }

        [UnityTest] public IEnumerator BothWeaponsSpendOneTotalWithoutAmmoSlotsOrReload()
        {
            var pc = Player(); var pickup = new GameObject("Ammo regression pickup").AddComponent<Pickup>();
            var ui = new GameObject("Ammo regression HUD", typeof(Canvas), typeof(InventoryHotbar));
            var wall = GameObject.CreatePrimitive(PrimitiveType.Cube);
            try
            {
                ui.GetComponent<InventoryHotbar>().player = pc;
                wall.layer = GameLayers.WorldStatic; wall.transform.position = pc.transform.position + new Vector3(0, 1, 4);
                wall.transform.localScale = new Vector3(8, 4, .2f); Physics.SyncTransforms();
                var inv = pc.inventory; var actions = pc.actions;
                foreach (var type in new[] { AmmoType.Pistol, AmmoType.Shotgun })
                {
                    var weapon = type == AmmoType.Pistol ? WeaponKind.Pistol : WeaponKind.Shotgun;
                    var ammo = type == AmmoType.Pistol ? PickupKind.PistolAmmo : PickupKind.ShotgunAmmo;
                    var def = type == AmmoType.Pistol ? inv.pistol : inv.shotgun;
                    inv.AddAmmo(type, 7); pickup.kind = Inventory.ItemFor(weapon); Assert.AreEqual(1, inv.TryPickup(pickup));
                    Assert.AreEqual(7 + def.pickupReserve, inv.Reserve(type), "Picking up a weapon must retain earlier ammo");
                    Assert.IsTrue(actions.RequestEquip(weapon)); yield return new WaitForSeconds(1.1f); yield return null;
                    var visual = pc.GetComponentInChildren<WeaponFireVisual>(); Assert.IsNotNull(visual);
                    int before = inv.TotalAmmo(type); Assert.AreEqual(before, inv.Count(ammo));
                    Vector3[] endpoints = null;
                    System.Action<WeaponKind, Vector3[]> onFire = (k, points) => endpoints = points;
                    actions.Fired += onFire;
                    Assert.IsTrue(actions.RequestAttack()); actions.Fired -= onFire;
                    Assert.AreEqual(before - 1, inv.Count(ammo)); Assert.AreEqual(1, visual.ShotsShown);
                    Assert.IsNotNull(endpoints); Assert.AreEqual(type == AmmoType.Pistol ? 1 : def.pellets, endpoints.Length);
                    Assert.IsTrue(endpoints.All(p => p.z <= wall.GetComponent<Collider>().bounds.min.z + .01f), "Every visible trail must end at the wall");
                    Assert.IsTrue(visual.GetComponentsInChildren<LineRenderer>().Any(l => l.enabled));
                    yield return null;
                    Assert.IsFalse(inv.hotbarOrder.Contains(ammo), "Ammo must not occupy a hotbar slot");
                    StringAssert.Contains(inv.AmmoLabel(type), ui.GetComponent<InventoryHotbar>().SlotText(inv.hotbarOrder.IndexOf(Inventory.ItemFor(weapon))));
                    yield return new WaitForSeconds(def.attackCycle + .1f);
                    int total = inv.TotalAmmo(type); Assert.IsFalse(actions.RequestReload());
                    Assert.AreEqual(total, inv.TotalAmmo(type), "R cannot change the total or block firing");
                    if (type == AmmoType.Pistol) { inv.pistolMag = 0; inv.pistolReserve = 10; }
                    else { inv.shotgunMag = 0; inv.shotgunReserve = 10; }
                    Assert.AreEqual(10, inv.AddAmmo(type, 10)); Assert.AreEqual(20, inv.TotalAmmo(type));
                    Assert.IsTrue(actions.RequestAttack(), "Legacy reserve is immediately spendable without reloading");
                    Assert.AreEqual(19, inv.TotalAmmo(type));
                    yield return new WaitForSeconds(def.attackCycle + .1f);
                    while (inv.ConsumeRound(type)) { }
                    int shots = visual.ShotsShown; int reserve = inv.Reserve(type);
                    Assert.IsFalse(actions.RequestAttack()); Assert.AreEqual(shots, visual.ShotsShown, "Empty click has no bullet effect");
                    Assert.AreEqual(reserve, inv.Count(ammo));
                    yield return new WaitForSeconds(.3f);
                }
                inv.RestoreHotbar(new[] { "PistolAmmo", "Pistol", "ShotgunAmmo", "Shotgun" }, 3);
                Assert.AreEqual(PickupKind.Shotgun, inv.SelectedItem, "Removing legacy ammo slots preserves the selected weapon");
                CollectionAssert.AreEqual(new[] { PickupKind.Pistol, PickupKind.Shotgun }, inv.hotbarOrder);
            }
            finally { Object.Destroy(pc.gameObject); Object.Destroy(pickup.gameObject); Object.Destroy(ui); Object.Destroy(wall); }
        }

        [UnityTest] public IEnumerator EnemyBoltsDamageStandingCrouchingAndOverlappingPlayer()
        {
            var pc = Player(); Projectile bullet = null;
            try
            {
                foreach (var kind in new[] { ProjectileKind.Bolt, ProjectileKind.BossBolt })
                foreach (var overlap in new[] { false, true })
                {
                    pc.health.ResetTo(90); var cc = pc.GetComponent<CharacterController>();
                    cc.height = overlap ? 1.1f : 1.75f; cc.center = Vector3.up * (cc.height / 2);
                    var origin = pc.transform.position + Vector3.up * .7f + Vector3.forward * (overlap ? 0 : 5);
                    Physics.SyncTransforms();
                    bullet = Projectile.Spawn(kind, origin, Vector3.back, null, AttackIds.Next(), 30);
                    bullet.speed = 400; // Cross the whole capsule in a single step.
                    yield return new WaitForFixedUpdate(); yield return new WaitForFixedUpdate();
                    Assert.AreEqual(60, pc.health.Current, kind + " overlap=" + overlap);
                    Assert.IsFalse(bullet.Active);
                    yield return new WaitForFixedUpdate(); Assert.AreEqual(60, pc.health.Current, "Only one application per projectile");
                }
            }
            finally { if (bullet != null) { bullet.Despawn(); Object.Destroy(bullet.gameObject); } Object.Destroy(pc.gameObject); }
        }

        [UnityTest] public IEnumerator CoverStopsBoltsAndIgnoringShooterDoesNotSkipPlayer()
        {
            var pc = Player(); var obstacle = GameObject.CreatePrimitive(PrimitiveType.Cube); Projectile bullet = null;
            try
            {
                obstacle.layer = GameLayers.DynamicProp;
                obstacle.transform.position = pc.transform.position + new Vector3(0, 1, 2.5f);
                obstacle.transform.localScale = new Vector3(2, 2, .1f); Physics.SyncTransforms();
                var origin = pc.transform.position + new Vector3(0, 1, 5);
                bullet = Projectile.Spawn(ProjectileKind.Bolt, origin, Vector3.back, null, AttackIds.Next(), 30); bullet.speed = 400;
                yield return new WaitForFixedUpdate(); yield return new WaitForFixedUpdate();
                Assert.AreEqual(90, pc.health.Current); Assert.IsFalse(bullet.Active);
                Assert.Greater(bullet.transform.position.z, obstacle.transform.position.z, "Impact stops on the near side of cover");
                bullet = Projectile.Spawn(ProjectileKind.Bolt, origin, Vector3.back, obstacle, AttackIds.Next(), 30); bullet.speed = 400;
                yield return new WaitForFixedUpdate(); yield return new WaitForFixedUpdate();
                Assert.AreEqual(60, pc.health.Current, "Ignore only the shooter, not the rest of the sweep"); Assert.IsFalse(bullet.Active);
            }
            finally { if (bullet != null) { bullet.Despawn(); Object.Destroy(bullet.gameObject); } Object.Destroy(pc.gameObject); Object.Destroy(obstacle); }
        }
    }
}
