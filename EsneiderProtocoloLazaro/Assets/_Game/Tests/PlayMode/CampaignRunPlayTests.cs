using System.Collections;
using System.IO;
using System.Linq;
using Esneider.AI;
using Esneider.Core;
using Esneider.Core.Data;
using Esneider.Core.Persistence;
using Esneider.Player;
using Esneider.World;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

namespace Esneider.Tests
{
    // 70.2 RUN completo por teletransporte: O01…O11 en orden, permisos de puertas solo por servicio de objetivos, CP-06 con garantía,
    // jefe, panel final, D29, victoria única y SAVE-END confirmado (97.3). Ninguna llave depende de leer documentos.
    public class CampaignRunPlayTests
    {
        PlayerController _pc; RegionStreamer _st; string _dir; LevelPlan _plan;

        [UnitySetUp]
        public IEnumerator SetUp()
        {
            Health.Clock = () => Time.time; WorldStateRegistry.ResetSession(); UI.MenuController.SkipTitle = true;
            _dir = Path.Combine(Path.GetTempPath(), "esneider-tests", System.Guid.NewGuid().ToString("N"));
            _plan = LevelPlan.FromJson(File.ReadAllText(LevelPlan.DefaultAssetPath));
#if UNITY_EDITOR
            yield return UnityEditor.SceneManagement.EditorSceneManager.LoadSceneAsyncInPlayMode("Assets/_Game/Scenes/BOOT.unity", new LoadSceneParameters(LoadSceneMode.Single));
#endif
            yield return null;
            _pc = Object.FindFirstObjectByType<PlayerController>(); _st = RegionStreamer.Instance;
            CheckpointService.Instance.saveDirectoryOverride = _dir;
            float t0 = Time.time; while (!_st.IsReady("REG-S1") && Time.time - t0 < 20f) yield return null;
        }

        [UnityTearDown]
        public IEnumerator TearDown()
        {
            Time.timeScale = 1f; try { Directory.Delete(_dir, true); } catch { }
            yield return SceneManager.LoadSceneAsync("Combat_Sandbox", LoadSceneMode.Single);
            var pc = Object.FindFirstObjectByType<PlayerController>(); if (pc != null) Object.Destroy(pc.transform.root.gameObject);
            yield return null;
        }

        Vector3 W(string space, float x, float z) { _plan.TryToWorld(space, x, z, out var w); return w; }
        static T Find<T>(System.Func<T, bool> pred) where T : Component => Object.FindObjectsByType<T>(FindObjectsInactive.Include, FindObjectsSortMode.None).FirstOrDefault(pred);
        Pickup Pick(string id) => Find<Pickup>(p => p.stableId == id);
        Mechanism Mech(string id) => Find<Mechanism>(m => m.mechanismId == id);
        Door Door(string id) => Find<Door>(d => d.doorId == id);
        bool O(string id) => WorldStateRegistry.Session.HasObjective(id);
        IEnumerator Go(string region, string space, float x, float z) { yield return _st.LoadForCheckpoint(region, W(space, x, z), 0f); yield return null; yield return null; }
        IEnumerator WaitCp(string id) { float t0 = Time.time; while ((CheckpointService.Instance.LastConfirmed == null || CheckpointService.Instance.LastConfirmed.checkpointId != id) && Time.time - t0 < 6f) yield return null; }

        [UnityTest]
        public IEnumerator MainRoute_EndToEnd_ObjectivesDoorsBossExitVictory()
        {
            // RUN-01 apertura → O01, CP-00
            Object.FindFirstObjectByType<OpeningSequence>()?.RequestSkip();
            float t0 = Time.time; while (!_pc.motor.movementEnabled && Time.time - t0 < 25f) yield return null;
            yield return WaitCp("CP-00"); Assert.IsTrue(O("O01"), "O01 despertar");
            // RUN-03/06: linterna y varilla → O02; D06 bloqueada sin palanca
            Pick("PICK-F01").Interact(_pc.gameObject); Assert.IsTrue(_pc.inventory.hasFlashlight);
            Pick("PICK-W01").Interact(_pc.gameObject); Assert.IsTrue(O("O02"), "O02 equipo básico");
            Assert.IsFalse(Door("D06").Allowed, "D06 exige permiso de servicio");
            // RUN-07/08: palanca → D06 → detección/O03 (EVT-C1)
            Mech("MECH-LEVER-S1").Interact(_pc.gameObject); Assert.IsTrue(Door("D06").Allowed);
            _pc.motor.Teleport(W("P02", 30f, 8f), 0f); yield return null;
            Door("D06").SetOpen(true); t0 = Time.time; while (!O("O03") && Time.time - t0 < 5f) yield return null;
            Assert.IsTrue(O("O03"), "O03 salir de S1"); Assert.IsTrue(ObjectiveService.Has(ObjectiveService.Detected));
            // RUN-15: pistola → O04; D14 bloqueada hasta panel A
            yield return Go("REG-S2", "P04", 6f, 10f);
            Pick("PICK-W02").Interact(_pc.gameObject); Assert.IsTrue(O("O04"), "O04 pistola"); Assert.IsTrue(_pc.inventory.hasPistol);
            Assert.IsFalse(Door("D14").Allowed);
            // RUN-18: panel A → O05, A, D14
            _pc.motor.Teleport(W("P04", 40f, 8f), 0f); yield return null;
            Mech("MECH-PANEL-A").Interact(_pc.gameObject); Assert.IsTrue(O("O05"), "O05 autorización A"); Assert.IsTrue(Door("D14").Allowed);
            // RUN-20: ventana C-02 → O06
            yield return Go("REG-C2", "C-02", 24f, 8f);
            t0 = Time.time; while (!O("O06") && Time.time - t0 < 4f) yield return null; Assert.IsTrue(O("O06"), "O06 descubrir contención");
            // RUN-26/28: escopeta → O07; panel B → O08, D22
            yield return Go("REG-S3", "P05", 54f, 7f);
            Pick("PICK-W03").Interact(_pc.gameObject); Assert.IsTrue(O("O07"), "O07 escopeta");
            Assert.IsFalse(Door("D22").Allowed);
            _pc.motor.Teleport(W("P05", 60f, 26f), 0f); yield return null;
            Mech("MECH-PANEL-B").Interact(_pc.gameObject); Assert.IsTrue(O("O08"), "O08 autorización B"); Assert.IsTrue(Door("D22").Allowed);
            // RUN-34: refugio CP-06 → O09 + garantía (80.1: max, no suma)
            _pc.inventory.pistolMag = 2; _pc.inventory.pistolReserve = 0; _pc.inventory.shotgunMag = 0; _pc.inventory.shotgunReserve = 3; _pc.health.ResetTo(40f);
            yield return Go("REG-S4", "P06", 6f, 42f);
            yield return WaitCp("CP-06"); Assert.AreEqual("CP-06", CheckpointService.Instance.LastConfirmed.checkpointId, "CP-06 en el refugio");
            Assert.IsTrue(O("O09"), "O09 refugio");
            Assert.AreEqual(90f, _pc.health.Current, 0.5f); Assert.AreEqual(50, _pc.inventory.pistolMag + _pc.inventory.pistolReserve); Assert.AreEqual(24, _pc.inventory.shotgunMag + _pc.inventory.shotgunReserve);
            Assert.IsFalse(Door("D28A").Allowed, "D28 cerrada hasta derrotar al jefe");
            // RUN-35..39: jefe
            var boss = Find<BossBrain>(b => b.stableId == "B01"); var bhp = boss.GetComponent<Health>();
            _pc.motor.Teleport(W("P06", 40f, 22f), 180f);
            t0 = Time.time; while (boss.State == BossState.Dormant && Time.time - t0 < 4f) yield return null;
            Assert.AreNotEqual(BossState.Dormant, boss.State, "EVT-21 activa al jefe");
            bhp.ApplyDamage(new DamageInfo { amount = 1200f, attackId = AttackIds.Next(), source = _pc.gameObject, kind = "Test" }); yield return null;
            Assert.IsTrue(O("O10"), "O10 Archivista"); Assert.IsTrue(Door("D28A").Allowed);
            yield return WaitCp("CP-07"); Assert.AreEqual("CP-07", CheckpointService.Instance.LastConfirmed.checkpointId);
            // RUN-40: panel final → D29
            Assert.IsFalse(Door("D29").Allowed);
            _pc.motor.Teleport(W("P06", 64f, 10f), 90f); yield return null;
            Mech("MECH-PANEL-EXIT").Interact(_pc.gameObject); Assert.IsTrue(Door("D29").Allowed, "D29: jefe + panel");
            // RUN-41: exterior → victoria única, O11, SAVE-END
            var vt = Object.FindFirstObjectByType<VictoryTrigger>(); Assert.IsNotNull(vt);
            _pc.motor.Teleport(vt.transform.position - Vector3.up * 0.9f, 90f);
            t0 = Time.time; while (GameFlowController.Instance.State != GameState.Won && Time.time - t0 < 4f) yield return null;
            Assert.AreEqual(GameState.Won, GameFlowController.Instance.State, "ESCAPE");
            Assert.IsTrue(O("O11")); Assert.IsTrue(vt.SaveEndConfirmed, "SAVE-END confirmado por IO");
            Assert.AreEqual("SAVE-END", CheckpointService.Instance.LastConfirmed.checkpointId); Assert.IsTrue(CheckpointService.Instance.LastConfirmed.campaignWon);
            var fromDisk = CheckpointService.Instance.LoadFromDisk(out var src); Assert.IsNotNull(fromDisk); Assert.IsTrue(fromDisk.campaignWon, "victoria persistente en disco (" + src + ")");
            Assert.AreEqual(11, WorldStateRegistry.Session.Objectives.Count(), "O01–O11 completos");
        }
    }
}
