using System.Collections;
using Esneider.AI;
using Esneider.Combat;
using Esneider.Core;
using Esneider.Core.Data;
using Esneider.Player;
using Esneider.World;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;

namespace Esneider.Tests
{
    // QA-01..04, QA-06, QA-08 (sección 28) sobre el sandbox construido en memoria.
    public class SandboxPlayTests
    {
        SandboxFactory.Result _r;
        PlayerController _pc;

        GameDataCatalog LoadCatalog()
        {
#if UNITY_EDITOR
            return UnityEditor.AssetDatabase.LoadAssetAtPath<GameDataCatalog>("Assets/_Game/Data/Definitions/GameDataCatalog.asset");
#else
            return null;
#endif
        }

        [UnitySetUp]
        public IEnumerator SetUp()
        {
            Health.Clock = () => Time.time; Esneider.Core.Persistence.WorldStateRegistry.ResetSession();
            _r = SandboxFactory.Build(LoadCatalog());
            _pc = _r.player.GetComponent<PlayerController>();
            yield return null; yield return null; // Start(): flujo Playing, enemigos en Patrol
            _r.vigia.GetComponent<EnemyBrain>().enabled = false; _r.custodio.GetComponent<EnemyBrain>().enabled = false; // pruebas controladas
            var agents = Object.FindObjectsByType<UnityEngine.AI.NavMeshAgent>(FindObjectsSortMode.None); foreach (var a in agents) if (a.isOnNavMesh) a.isStopped = true;
        }

        [UnityTearDown]
        public IEnumerator TearDown()
        {
            Time.timeScale = 1f;
            if (_r != null && _r.root != null) Object.Destroy(_r.root);
            foreach (var p in Object.FindObjectsByType<Projectile>(FindObjectsSortMode.None)) Object.Destroy(p.gameObject);
            var dir = Object.FindFirstObjectByType<EncounterDirector>(); if (dir != null) Object.Destroy(dir.gameObject);
            yield return null;
        }

        IEnumerator PlaceFacing(GameObject target, float distance)
        {
            var t = target.transform.position; var pos = t + new Vector3(0, 0, -distance);
            _pc.motor.Teleport(pos, 0f);
            yield return new WaitForFixedUpdate(); yield return null;
        }

        IEnumerator Give(WeaponKind kind)
        {
            var inv = _pc.inventory;
            if (kind == WeaponKind.Melee) inv.hasCrowbar = true; else if (kind == WeaponKind.Pistol) { inv.hasPistol = true; inv.pistolMag = 12; inv.pistolReserve = 80; } else { inv.hasShotgun = true; inv.shotgunMag = 6; inv.shotgunReserve = 36; }
            Assert.IsTrue(_pc.actions.RequestEquip(kind));
            yield return new WaitForSeconds(1.0f);
            Assert.AreEqual(kind, _pc.actions.ActiveWeapon);
        }

        [UnityTest]
        public IEnumerator QA01_CrowbarKillsVigiaIn3AndCustodioIn6()
        {
            yield return Give(WeaponKind.Melee);
            yield return PlaceFacing(_r.vigia, 1.0f);
            var vh = _r.vigia.GetComponent<Health>(); int swings = 0;
            while (!vh.IsDead && swings < 10) { if (_pc.actions.RequestAttack()) swings++; yield return new WaitForSeconds(0.9f); }
            Assert.AreEqual(3, swings, "Vigía muere en el tercer golpe");
            yield return PlaceFacing(_r.custodio, 1.0f);
            var kh = _r.custodio.GetComponent<Health>(); swings = 0;
            while (!kh.IsDead && swings < 12) { if (_pc.actions.RequestAttack()) swings++; yield return new WaitForSeconds(0.9f); }
            Assert.AreEqual(6, swings, "Custodio muere en el sexto golpe");
        }

        [UnityTest]
        public IEnumerator QA02_ThreeBolts_90_60_30_0()
        {
            var hp = _pc.health; var origin = _pc.transform.position + new Vector3(0, 1.2f, 5f);
            float[] expected = { 60, 30, 0 };
            for (int i = 0; i < 3; i++)
            {
                Projectile.Spawn(ProjectileKind.Bolt, origin, Vector3.back, _r.custodio, AttackIds.Next(), 30f);
                yield return new WaitForSeconds(1.0f);
                Assert.AreEqual(expected[i], hp.Current, $"rayo {i + 1}");
            }
            Assert.AreEqual("DERROTA_DANO", GameFlowController.Instance.LastResult);
        }

        [UnityTest]
        public IEnumerator QA03_NetBehindPillarIsBlocked()
        {
            // pilar en (0,*,1.5): jugador en z=-1.5 detrás del pilar, red disparada desde z=4.5 hacia -z
            _pc.motor.Teleport(new Vector3(0, 0, -1.5f), 0f); yield return null;
            var p = Projectile.Spawn(ProjectileKind.Net, new Vector3(0, 1.2f, 4.5f), Vector3.back, _r.vigia, AttackIds.Next(), 0f);
            yield return new WaitForSeconds(1.2f);
            Assert.IsFalse(_pc.IsCaptured, "la cobertura destruye la red");
            Assert.IsFalse(p.Active);
        }

        [UnityTest]
        public IEnumerator QA04_NetCaptureEndsWithin2_5Seconds()
        {
            _pc.motor.Teleport(new Vector3(3, 0, -3), 0f); yield return null;
            Projectile.Spawn(ProjectileKind.Net, new Vector3(3, 1.2f, 2f), Vector3.back, _r.vigia, AttackIds.Next(), 0f);
            float t0 = Time.time;
            while (!_pc.IsCaptured && Time.time - t0 < 2f) yield return null;
            Assert.IsTrue(_pc.IsCaptured, "red válida captura");
            float captured = Time.time;
            while (GameFlowController.Instance.AttemptOpen && Time.time - captured < 3f) yield return null;
            Assert.IsFalse(GameFlowController.Instance.AttemptOpen, "derrota en tiempo acotado");
            Assert.LessOrEqual(Time.time - captured, 2.6f);
            Assert.AreEqual("DERROTA_RED", GameFlowController.Instance.LastResult);
        }

        [UnityTest]
        public IEnumerator QA06_ReloadCancelBeforeAndAfterCommit()
        {
            yield return Give(WeaponKind.Pistol);
            var inv = _pc.inventory; inv.pistolMag = 5; inv.pistolReserve = 20;
            Assert.IsTrue(_pc.actions.RequestReload());
            yield return new WaitForSeconds(0.6f);
            _pc.actions.CancelCurrent("test"); yield return null;
            Assert.AreEqual(5, inv.pistolMag); Assert.AreEqual(20, inv.pistolReserve);
            Assert.IsTrue(_pc.actions.RequestReload());
            yield return new WaitForSeconds(1.5f);
            _pc.actions.CancelCurrent("test"); yield return null;
            Assert.AreEqual(12, inv.pistolMag); Assert.AreEqual(13, inv.pistolReserve);
            Assert.IsFalse(_pc.actions.Busy);
        }

        [UnityTest]
        public IEnumerator QA08_HealAtFullDoesNotConsume_AndCancelBeforeCommitKeepsUnit()
        {
            var inv = _pc.inventory; inv.syringes = 2;
            Assert.IsFalse(_pc.actions.RequestHeal(), "vida llena: no consumir");
            _pc.health.ApplyDamage(new DamageInfo { amount = 50, attackId = AttackIds.Next() });
            Assert.IsTrue(_pc.actions.RequestHeal());
            yield return new WaitForSeconds(0.5f);
            _pc.actions.CancelCurrent("test"); yield return null;
            Assert.AreEqual(2, inv.syringes); Assert.AreEqual(40f, _pc.health.Current);
            Assert.IsTrue(_pc.actions.RequestHeal());
            yield return new WaitForSeconds(1.7f);
            Assert.AreEqual(1, inv.syringes); Assert.AreEqual(85f, _pc.health.Current);
        }

        [UnityTest]
        public IEnumerator Pistol_ShotThroughCoverIsBlocked_ShotgunFalloffApplies()
        {
            yield return Give(WeaponKind.Pistol);
            // Custodio detrás del pilar: jugador en z=-2 mirando +z, pilar en z=1.5, custodio en z=4
            _r.custodio.transform.position = new Vector3(0, 0, 4f); _pc.motor.Teleport(new Vector3(0, 0, -2f), 0f); yield return new WaitForFixedUpdate();
            var kh = _r.custodio.GetComponent<Health>();
            Assert.IsTrue(_pc.actions.RequestAttack()); yield return null;
            Assert.AreEqual(120f, kh.Current, "el pilar bloquea el disparo");
            // sin cobertura, a 2 m
            _r.custodio.transform.position = new Vector3(-4, 0, 0f); _pc.motor.Teleport(new Vector3(-4, 0, -2f), 0f); yield return new WaitForFixedUpdate(); yield return new WaitForSeconds(0.4f);
            Assert.IsTrue(_pc.actions.RequestAttack()); yield return null;
            Assert.AreEqual(90f, kh.Current, "pistola 30 de daño");
            yield return Give(WeaponKind.Shotgun);
            Assert.IsTrue(_pc.actions.RequestAttack()); yield return null;
            Assert.AreEqual(30f, kh.Current, "escopeta a 2 m: 8×7.5 = 60 sumados una vez");
        }
    }
}
