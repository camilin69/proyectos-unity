using System.Collections;
using System.Linq;
using Esneider.AI;
using Esneider.Combat;
using Esneider.Core;
using Esneider.Core.Data;
using Esneider.Player;
using Esneider.World;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.LowLevel;

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
        public IEnumerator QA04_NetDealsGradualDamageAndRepeatedFEscapes()
        {
            _pc.motor.Teleport(new Vector3(3, 0, -3), 0f); yield return null;
            Projectile.Spawn(ProjectileKind.Net, new Vector3(3, 1.2f, 2f), Vector3.back, _r.vigia, AttackIds.Next(), 0f);
            float t0 = Time.time;
            while (!_pc.IsCaptured && Time.time - t0 < 2f) yield return null;
            Assert.IsTrue(_pc.IsCaptured, "red válida captura");
            Assert.AreEqual(90,_pc.health.Current,"capturar no hace daño instantáneo");
            StringAssert.Contains("Presiona F varias veces para escapar",_pc.Prompt);
            yield return new WaitForSeconds(3.2f);
            Assert.IsTrue(GameFlowController.Instance.AttemptOpen,"no hay derrota automática a los 2.5 s");
            Assert.That(_pc.health.Current,Is.InRange(74f,82f),"4 HP por segundo, menos que el rayo de 30");
            for(int i=0;i<_pc.captureEscapePresses;i++) { _pc.input.FlashlightPressed=true; yield return null; }
            Assert.IsFalse(_pc.IsCaptured); Assert.IsTrue(_pc.motor.movementEnabled); Assert.IsTrue(_pc.actions.actionsEnabled);
            Assert.AreEqual(GameState.Playing,GameFlowController.Instance.State);
            float escapedHp=_pc.health.Current;
            _pc.Capture(_r.vigia); Assert.IsFalse(_pc.IsCaptured,"gracia contra recaptura inmediata");
            yield return new WaitForSeconds(1.1f); Assert.AreEqual(escapedHp,_pc.health.Current,"el daño termina al escapar");
        }

        [UnityTest]
        public IEnumerator CapturePausesAndCanKillOnlyThroughHealthLoss()
        {
            _pc.Capture(_r.vigia); _pc.health.ResetTo(6);
            GameFlowController.Instance.TogglePause();
            yield return new WaitForSecondsRealtime(1.2f);
            Assert.AreEqual(6,_pc.health.Current); _pc.RegisterEscapePress(); Assert.AreEqual(0,_pc.CapturePresses);
            GameFlowController.Instance.TogglePause();
            yield return new WaitForSeconds(1.1f); Assert.AreEqual(2,_pc.health.Current); Assert.IsTrue(GameFlowController.Instance.AttemptOpen);
            yield return new WaitForSeconds(1.1f); Assert.IsTrue(_pc.health.IsDead); Assert.IsFalse(_pc.IsCaptured);
            Assert.AreEqual("DERROTA_DANO",GameFlowController.Instance.LastResult);
        }

        [UnityTest]
        public IEnumerator QA06_LegacyReserveFiresWithoutReload()
        {
            yield return Give(WeaponKind.Pistol);
            var inv = _pc.inventory; inv.pistolMag = 0; inv.pistolReserve = 20;
            Assert.IsFalse(_pc.actions.RequestReload()); Assert.IsFalse(_pc.actions.Busy);
            Assert.IsTrue(_pc.actions.RequestAttack()); Assert.AreEqual(19, inv.TotalAmmo(AmmoType.Pistol));
            yield return new WaitForSeconds(.6f);
            Assert.IsTrue(_pc.actions.RequestAttack()); Assert.AreEqual(18, inv.TotalAmmo(AmmoType.Pistol));
        }

        [UnityTest]
        public IEnumerator CaptureRequiresDistinctKeyboardFPressesAndShowsHud()
        {
            var settings=InputSystem.settings;
            var originalEditorBehavior=settings.editorInputBehaviorInPlayMode;
            var originalBackgroundBehavior=settings.backgroundBehavior;
            settings.editorInputBehaviorInPlayMode=InputSettings.EditorInputBehaviorInPlayMode.AllDeviceInputAlwaysGoesToGameView;
            settings.backgroundBehavior=InputSettings.BackgroundBehavior.IgnoreFocus;
            var keyboard=InputSystem.AddDevice<Keyboard>();
            try
            {
                _pc.Capture(_r.vigia); yield return null;
                var hud=Object.FindObjectsByType<Esneider.UI.HudController>(FindObjectsSortMode.None).FirstOrDefault(h=>h.player==_pc);
                Assert.IsNotNull(hud); StringAssert.Contains("Presiona F varias veces para escapar",hud.promptText.text);
                InputSystem.QueueStateEvent(keyboard,new KeyboardState(Key.F)); InputSystem.Update(); yield return null;
                Assert.AreEqual(1,_pc.CapturePresses);
                yield return null; yield return null; Assert.AreEqual(1,_pc.CapturePresses,"mantener F no cuenta otra pulsación");
                for(int i=1;i<_pc.captureEscapePresses;i++)
                {
                    InputSystem.QueueStateEvent(keyboard,new KeyboardState()); InputSystem.Update(); yield return null;
                    InputSystem.QueueStateEvent(keyboard,new KeyboardState(Key.F)); InputSystem.Update(); yield return null;
                }
                Assert.IsFalse(_pc.IsCaptured); yield return null;
                Assert.IsFalse(hud.promptText.text.Contains("para escapar"));
            }
            finally { InputSystem.RemoveDevice(keyboard); settings.editorInputBehaviorInPlayMode=originalEditorBehavior; settings.backgroundBehavior=originalBackgroundBehavior; }
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
