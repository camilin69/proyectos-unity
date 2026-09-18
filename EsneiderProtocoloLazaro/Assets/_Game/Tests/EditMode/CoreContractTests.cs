using Esneider.Core;
using Esneider.Core.Data;
using Esneider.Player;
using Esneider.World;
using NUnit.Framework;
using UnityEngine;

namespace Esneider.Tests
{
    // Contratos puros de 86.6, 10 y 11.1: no repiten constantes, comprueban comportamiento.
    public class ActionTransactionTests
    {
        [Test]
        public void CommitFiresOnceAndSurvivesCancel()
        {
            int fired = 0;
            var t = new ActionTransaction("Reload", 1.9f).AddCommit(1.35f, () => fired++);
            t.Begin();
            t.Tick(1.0f); Assert.AreEqual(0, fired);
            t.Tick(0.4f); Assert.AreEqual(1, fired);
            t.Cancel("test"); t.Cancel("again");
            Assert.AreEqual(ActionPhase.Cancelled, t.Phase); Assert.AreEqual(1, fired);
            t.Complete(); Assert.AreEqual(1, fired, "completar tras cancelar no re-ejecuta commit");
        }

        [Test]
        public void CancelBeforeCommitDoesNothing()
        {
            int fired = 0;
            var t = new ActionTransaction("Heal", 1.6f).AddCommit(1.1f, () => fired++);
            t.Begin(); t.Tick(0.9f); t.Cancel("hit");
            Assert.AreEqual(0, fired); Assert.IsFalse(t.AnyCommitDone);
        }

        [Test]
        public void CompleteRunsPendingCommitsExactlyOnce()
        {
            int fired = 0;
            var t = new ActionTransaction("X", 1f).AddCommit(0.5f, () => fired++);
            t.Begin(); t.Complete(); t.Complete();
            Assert.AreEqual(1, fired); Assert.AreEqual(ActionPhase.Completed, t.Phase);
        }

        [Test]
        public void CommitOutsideDurationIsRejected()
        {
            Assert.Throws<System.ArgumentException>(() => new ActionTransaction("X", 1f).AddCommit(1.5f, null));
        }
    }

    public class HealthTests
    {
        float _clock;
        Health NewHealth(int max, float invuln)
        {
            _clock = 100f; Health.Clock = () => _clock;
            var h = new GameObject("hp").AddComponent<Health>(); h.maxHp = max; h.invulnerabilitySeconds = invuln; h.ResetTo(max); return h;
        }

        [Test]
        public void ThreeBoltsKillFromFull_90_60_30_0()
        {
            var h = NewHealth(90, 0.65f);
            for (int i = 1; i <= 3; i++) { Assert.IsTrue(h.ApplyDamage(new DamageInfo { amount = 30, attackId = i })); _clock += 1f; }
            Assert.IsTrue(h.IsDead); Assert.AreEqual(0f, h.Current);
        }

        [Test]
        public void SameAttackIdAppliesOnce()
        {
            var h = NewHealth(90, 0f);
            Assert.IsTrue(h.ApplyDamage(new DamageInfo { amount = 30, attackId = 7 }));
            Assert.IsFalse(h.ApplyDamage(new DamageInfo { amount = 30, attackId = 7 }));
            Assert.AreEqual(60f, h.Current);
        }

        [Test]
        public void InvulnerabilityWindowBlocksSecondHit()
        {
            var h = NewHealth(90, 0.65f);
            Assert.IsTrue(h.ApplyDamage(new DamageInfo { amount = 30, attackId = 1 }));
            _clock += 0.3f; Assert.IsFalse(h.ApplyDamage(new DamageInfo { amount = 30, attackId = 2 }));
            _clock += 0.4f; Assert.IsTrue(h.ApplyDamage(new DamageInfo { amount = 30, attackId = 3 }));
            Assert.AreEqual(30f, h.Current);
        }

        [Test]
        public void CrowbarCounts_3And6()
        {
            var v = NewHealth(60, 0f); var k = NewHealth(120, 0f);
            int hitsV = 0, hitsK = 0;
            while (!v.IsDead) { v.ApplyDamage(new DamageInfo { amount = 20, attackId = ++hitsV }); }
            while (!k.IsDead) { k.ApplyDamage(new DamageInfo { amount = 20, attackId = 1000 + ++hitsK }); }
            Assert.AreEqual(3, hitsV); Assert.AreEqual(6, hitsK);
        }

        [Test]
        public void HealNeverExceedsMax()
        {
            var h = NewHealth(90, 0f);
            h.ApplyDamage(new DamageInfo { amount = 10, attackId = 1 });
            Assert.AreEqual(10f, h.Heal(45)); Assert.AreEqual(90f, h.Current);
        }
    }

    public class InventoryTests
    {
        Inventory NewInv()
        {
            var go = new GameObject("inv"); var inv = go.AddComponent<Inventory>();
            var p = ScriptableObject.CreateInstance<WeaponDefinition>(); p.kind = WeaponKind.Pistol; p.magazineSize = 12; p.reserveMax = 80; p.pickupLoaded = 10; p.pickupReserve = 10;
            var s = ScriptableObject.CreateInstance<WeaponDefinition>(); s.kind = WeaponKind.Shotgun; s.magazineSize = 6; s.reserveMax = 36; s.pickupLoaded = 5; s.pickupReserve = 5;
            inv.pistol = p; inv.shotgun = s; return inv;
        }

        [Test]
        public void PistolReload_5_20_Becomes_12_13()
        {
            var inv = NewInv(); inv.hasPistol = true; inv.pistolMag = 5; inv.pistolReserve = 20;
            Assert.AreEqual(7, inv.CommitPistolReload());
            Assert.AreEqual(12, inv.pistolMag); Assert.AreEqual(13, inv.pistolReserve);
            Assert.AreEqual(0, inv.CommitPistolReload(), "cargador lleno: sin transferencia");
        }

        [Test]
        public void ShotgunTwoCommits_2_10_Becomes_4_8()
        {
            var inv = NewInv(); inv.hasShotgun = true; inv.shotgunMag = 2; inv.shotgunReserve = 10;
            Assert.IsTrue(inv.CommitShotgunShell()); Assert.IsTrue(inv.CommitShotgunShell());
            Assert.AreEqual(4, inv.shotgunMag); Assert.AreEqual(8, inv.shotgunReserve);
        }

        [Test]
        public void PartialPickupKeepsRemainderInWorld()
        {
            var inv = NewInv(); inv.hasShotgun = true; inv.shotgunReserve = 34;
            var p = new GameObject("pick").AddComponent<Pickup>(); p.kind = PickupKind.ShotgunAmmo; p.amount = 4;
            int accepted = inv.TryPickup(p);
            Assert.AreEqual(2, accepted);
            p.amount -= accepted; Assert.AreEqual(2, p.amount, "los cartuchos que no caben permanecen");
            Assert.AreEqual(36, inv.shotgunReserve);
        }

        [Test]
        public void WeaponPickupGivesLoadedAndReserve()
        {
            var inv = NewInv();
            var p = new GameObject("pick").AddComponent<Pickup>(); p.kind = PickupKind.Pistol; p.amount = 1;
            Assert.AreEqual(1, inv.TryPickup(p)); Assert.IsTrue(inv.hasPistol); Assert.AreEqual(10, inv.pistolMag); Assert.AreEqual(10, inv.pistolReserve);
            Assert.AreEqual(0, inv.TryPickup(p), "arma ya obtenida");
        }
    }
}
