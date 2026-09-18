using System.Collections;
using System.IO;
using Esneider.AI;
using Esneider.Core;
using Esneider.Core.Data;
using Esneider.Core.Persistence;
using Esneider.Player;
using Esneider.World;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;

namespace Esneider.Tests
{
    // QA-09 (guardar, consumir, matar, mover caja, cargar), QA-10 (continuar desde archivo), QA-11 (guardado inválido → backup).
    public class PersistencePlayTests
    {
        SandboxFactory.Result _r; PlayerController _pc; CheckpointService _cps; string _dir;

        [UnitySetUp]
        public IEnumerator SetUp()
        {
            Health.Clock = () => Time.time; WorldStateRegistry.ResetSession();
#if UNITY_EDITOR
            var cat = UnityEditor.AssetDatabase.LoadAssetAtPath<GameDataCatalog>("Assets/_Game/Data/Definitions/GameDataCatalog.asset");
#else
            GameDataCatalog cat = null;
#endif
            _dir = Path.Combine(Path.GetTempPath(), "esneider-tests", System.Guid.NewGuid().ToString("N"));
            _r = SandboxFactory.Build(cat);
            _cps = _r.root.GetComponentInChildren<CheckpointService>();
            _cps.saveDirectoryOverride = _dir;
            _pc = _r.player.GetComponent<PlayerController>();
            yield return null; yield return null;
            foreach (var b in Object.FindObjectsByType<EnemyBrain>(FindObjectsSortMode.None)) b.enabled = false;
        }

        [UnityTearDown]
        public IEnumerator TearDown()
        {
            Time.timeScale = 1f;
            if (_r != null && _r.root != null) Object.Destroy(_r.root);
            try { Directory.Delete(_dir, true); } catch { }
            yield return null;
        }

        [UnityTest]
        public IEnumerator QA09_SnapshotRestoresInventoryEnemiesPickupsAndCrate()
        {
            var inv = _pc.inventory; inv.hasPistol = true; inv.pistolMag = 8; inv.pistolReserve = 30; inv.syringes = 2;
            var ammo = GameObject.Find("Pickup_A-SB1").GetComponent<Pickup>();
            var vigiaHp = _r.vigia.GetComponent<Health>();
            _r.crate.transform.position = new Vector3(2f, 0.5f, -2f);
            yield return new WaitForFixedUpdate(); yield return new WaitForSeconds(0.6f);
            Assert.IsTrue(_cps.CommitNow("CP-01", _pc, "REG-SANDBOX", false, 0, 0, 0), _cps.LastNotice);

            // cambios posteriores al snapshot
            ammo.Interact(_pc.gameObject); Assert.AreEqual(0, ammo.amount, "pickup consumido"); Assert.AreEqual(40, inv.pistolReserve, "reserva tras pickup");
            inv.pistolMag = 2; inv.syringes = 0;
            vigiaHp.ApplyDamage(new DamageInfo { amount = 60, attackId = AttackIds.Next(), kind = "Crowbar" });
            Assert.IsTrue(vigiaHp.IsDead, "Vigía muerto tras 60 de daño");
            _r.crate.transform.position = new Vector3(-4f, 0.5f, 4f);
            _pc.health.ApplyDamage(new DamageInfo { amount = 50, attackId = AttackIds.Next() });
            yield return null;

            // cargar el snapshot
            Assert.IsTrue(_cps.RestoreInto(_cps.LastConfirmed, _pc), "RestoreInto");
            yield return null;
            Assert.AreEqual(8, inv.pistolMag, "cargador restaurado"); Assert.AreEqual(30, inv.pistolReserve, "la munición del pickup recogido tras el snapshot no se conserva");
            Assert.AreEqual(2, inv.syringes, "jeringas restauradas"); Assert.AreEqual(90f, _pc.health.Current, "vida restaurada");
            WorldStateRegistry.Session.TryGet(ammo.GetComponent<PersistentEntity>().guid, out var ammoState);
            Assert.IsTrue(ammo.gameObject.activeSelf, $"el pickup vuelve al mundo (estado: amount={ammoState?.amount} taken={ammoState?.taken} v={ammoState?.stateVersion})"); Assert.AreEqual(10, ammo.amount, "cantidad del pickup restaurada");
            Assert.IsFalse(vigiaHp.IsDead); Assert.AreEqual(60f, vigiaHp.Current, "el Vigía vuelve vivo con su HP del snapshot");
            Assert.AreEqual(EnemyState.Patrol, _r.vigia.GetComponent<EnemyBrain>().State);
            Assert.Less(Vector3.Distance(_r.crate.transform.position, new Vector3(2f, 0.5f, -2f)), 0.6f, "la caja vuelve a su posición guardada");
            Assert.AreEqual(GameState.Playing, GameFlowController.Instance.State);
        }

        [UnityTest]
        public IEnumerator QA10_LoadFromDiskAfterRestart_NoDuplication()
        {
            var inv = _pc.inventory; inv.hasShotgun = true; inv.shotgunMag = 4; inv.shotgunReserve = 10;
            var shells = GameObject.Find("Pickup_S-SB1").GetComponent<Pickup>();
            shells.Interact(_pc.gameObject); Assert.AreEqual(14, inv.shotgunReserve); Assert.IsFalse(shells.gameObject.activeSelf);
            Assert.IsTrue(_cps.CommitNow("CP-02", _pc, "REG-SANDBOX", false, 0, 0, 0), _cps.LastNotice);
            // simular reinicio: nuevo registro de sesión y lectura desde disco
            WorldStateRegistry.ResetSession();
            var fromDisk = _cps.LoadFromDisk(out var src);
            Assert.IsNotNull(fromDisk); Assert.AreEqual("checkpoint.json", src);
            inv.shotgunReserve = 0; shells.gameObject.SetActive(true); shells.amount = 4;
            Assert.IsTrue(_cps.RestoreInto(fromDisk, _pc)); yield return null;
            Assert.AreEqual(14, inv.shotgunReserve, "continúa desde archivo, no desde memoria temporal");
            WorldStateRegistry.Session.TryGet(shells.GetComponent<PersistentEntity>().guid, out var shellState);
            Assert.IsFalse(shells.gameObject.activeSelf, $"el pickup recogido no reaparece: sin duplicación (estado: {(shellState == null ? "null" : $"amount={shellState.amount} taken={shellState.taken} v={shellState.stateVersion}")}, entidades={fromDisk.world.entities.Count})");
            // cargar dos veces no suma
            Assert.IsTrue(_cps.RestoreInto(fromDisk, _pc)); yield return null;
            Assert.AreEqual(14, inv.shotgunReserve);
        }

        [UnityTest]
        public IEnumerator QA11_InvalidActiveSaveRecoversBackup()
        {
            Assert.IsTrue(_cps.CommitNow("CP-01", _pc, "REG-SANDBOX", false, 0, 0, 0));
            _pc.inventory.syringes = 3;
            Assert.IsTrue(_cps.CommitNow("CP-02", _pc, "REG-SANDBOX", false, 0, 0, 0));
            File.WriteAllText(_cps.Store.ActivePath, "{corrupto");
            var d = _cps.LoadFromDisk(out var src);
            Assert.IsNotNull(d); Assert.AreEqual("checkpoint.bak1.json", src); Assert.AreEqual("CP-01", d.checkpointId);
            StringAssert.Contains("Se recuperó", _cps.LastNotice);
            yield return null;
        }

        [UnityTest]
        public IEnumerator CP06_GuaranteeAppliesOnceAndNeverReduces()
        {
            var inv = _pc.inventory; inv.hasPistol = true; inv.hasShotgun = true; inv.pistolMag = 3; inv.pistolReserve = 10; inv.shotgunMag = 1; inv.shotgunReserve = 2;
            _pc.health.ApplyDamage(new DamageInfo { amount = 70, attackId = AttackIds.Next() });
            Assert.IsTrue(_cps.CommitNow("CP-06", _pc, "REG-S4", true, 90, 50, 24));
            Assert.AreEqual(90f, _pc.health.Current); Assert.AreEqual(50, inv.pistolMag + inv.pistolReserve); Assert.AreEqual(24, inv.shotgunMag + inv.shotgunReserve);
            inv.pistolReserve = 70; // ya tiene más: no reducir
            Assert.IsTrue(_cps.CommitNow("CP-06", _pc, "REG-S4", true, 90, 50, 24));
            Assert.AreEqual(73, inv.pistolMag + inv.pistolReserve, "no reduce ni suma por segunda entrada");
            Assert.IsTrue(WorldStateRegistry.Session.HasFlag(ObjectiveService.FinalCabinet));
            yield return null;
        }

        [UnityTest]
        public IEnumerator NoCheckpointWhileCapturedOrBusy()
        {
            Assert.IsTrue(_cps.CanCheckpoint(_pc, out _));
            _pc.inventory.hasPistol = true; _pc.inventory.pistolMag = 2; _pc.inventory.pistolReserve = 5;
            _pc.actions.RequestEquip(WeaponKind.Pistol); yield return null;
            Assert.IsFalse(_cps.CanCheckpoint(_pc, out var why)); StringAssert.Contains("acción", why);
            yield return new WaitForSeconds(0.8f);
            _pc.Capture(_r.vigia);
            Assert.IsFalse(_cps.CanCheckpoint(_pc, out why)); StringAssert.Contains("capturado", why);
        }
    }
}
