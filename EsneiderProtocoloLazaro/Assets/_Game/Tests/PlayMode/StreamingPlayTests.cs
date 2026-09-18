using System.Collections;
using System.IO;
using Esneider.Core;
using Esneider.Core.Persistence;
using Esneider.Player;
using Esneider.World;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

namespace Esneider.Tests
{
    // 88/101 EX-03: regiones aditivas, precarga por permiso, descarga segura, reentrada ≠ retry, cero duplicación.
    public class StreamingPlayTests
    {
        PlayerController _pc; RegionStreamer _st; CheckpointService _cps; string _dir;

        [UnitySetUp]
        public IEnumerator SetUp()
        {
            Health.Clock = () => Time.time; WorldStateRegistry.ResetSession();
            _dir = Path.Combine(Path.GetTempPath(), "esneider-tests", System.Guid.NewGuid().ToString("N"));
#if UNITY_EDITOR
            yield return UnityEditor.SceneManagement.EditorSceneManager.LoadSceneAsyncInPlayMode("Assets/_Game/Scenes/BOOT.unity", new LoadSceneParameters(LoadSceneMode.Single));
#endif
            yield return null;
            _pc = Object.FindFirstObjectByType<PlayerController>(); _st = RegionStreamer.Instance; _cps = CheckpointService.Instance;
            _cps.saveDirectoryOverride = _dir;
            float t0 = Time.time;
            while (!_st.IsReady("REG-S1") && Time.time - t0 < 20f) yield return null;
            Assert.IsTrue(_st.IsReady("REG-S1"), "REG-S1 lista al iniciar");
            foreach (var b in Object.FindObjectsByType<AI.EnemyBrain>(FindObjectsSortMode.None)) b.enabled = false;
            yield return null;
        }

        [UnityTearDown]
        public IEnumerator TearDown()
        {
            Time.timeScale = 1f;
            try { Directory.Delete(_dir, true); } catch { }
            yield return SceneManager.LoadSceneAsync("Combat_Sandbox", LoadSceneMode.Single);
            var pc = Object.FindFirstObjectByType<PlayerController>(); if (pc != null) Object.Destroy(pc.transform.root.gameObject);
            yield return null;
        }

        static Vector3 W(string space, float x, float z)
        {
            var plan = Core.Data.LevelPlan.FromJson(File.ReadAllText(Core.Data.LevelPlan.DefaultAssetPath));
            plan.TryToWorld(space, x, z, out var w); return w;
        }

        [UnityTest]
        public IEnumerator PermissionPreloadsConnector_CrossingLoadsNextSector_AndReleasesPrevious()
        {
            Assert.AreEqual(RegionState.Unloaded, _st.State("REG-S2"), "S2 no se carga antes de tiempo");
            Assert.IsTrue(_st.IsReady("REG-C1") || _st.State("REG-C1") == RegionState.Loading, "C1 es vecina de S1: precargada");
            var lever = GameObject.Find("Mech_MECH-LEVER-S1").GetComponent<Mechanism>();
            lever.Interact(_pc.gameObject);
            Assert.IsTrue(ObjectiveService.Has(ObjectiveService.PermisoServicio));
            Door d06 = null; foreach (var d in Object.FindObjectsByType<Door>(FindObjectsSortMode.None)) if (d.doorId == "D06") d06 = d;
            Assert.IsNotNull(d06, "puerta D06 presente (caja o modelo OBJ-070)");
            Assert.IsTrue(d06.Allowed, "D06 permitida tras la palanca");
            float t0 = Time.time; while (!_st.IsReady("REG-C1") && Time.time - t0 < 20f) yield return null;
            Assert.IsTrue(_st.IsReady("REG-C1"));
            // cruzar a C-01 (origen mundo (40,-18,21)) y avanzar dentro
            _pc.motor.Teleport(W("C-01", 6f, 0f), 90f);
            t0 = Time.time; while (_st.CurrentRegion != "REG-C1" && Time.time - t0 < 10f) yield return null;
            Assert.AreEqual("REG-C1", _st.CurrentRegion);
            t0 = Time.time; while (!_st.IsReady("REG-S2") && Time.time - t0 < 30f) yield return null;
            Assert.IsTrue(_st.IsReady("REG-S2"), "S2 lista antes de D07");
            Assert.IsTrue(_st.IsReady("REG-S1"), "S1 se conserva mientras el jugador permanece en C1");
            // entrar en S2 (P03) y avanzar ≥ 8 m
            _pc.motor.Teleport(W("P03", 12f, 32f), 180f);
            t0 = Time.time; while (_st.CurrentRegion != "REG-S2" && Time.time - t0 < 10f) yield return null;
            Assert.AreEqual("REG-S2", _st.CurrentRegion);
            t0 = Time.time; while (_st.State("REG-S1") != RegionState.Unloaded && Time.time - t0 < 40f) yield return null;
            Assert.AreEqual(RegionState.Unloaded, _st.State("REG-S1"), "S1 se libera al avanzar dentro de S2");
            Assert.IsFalse(SceneManager.GetSceneByName("REG-S1").isLoaded);
            Assert.IsTrue(_st.IsReady("REG-C2") || _st.State("REG-C2") == RegionState.Loading, "C2 vecina de S2: precarga");
        }

        [UnityTest]
        public IEnumerator ReentryKeepsChanges_RetryRestoresSnapshot_NoDuplication()
        {
            // checkpoint en CP-00 con la linterna todavía en el mundo
            Assert.IsTrue(_cps.CommitNow("CP-00", _pc, "REG-S1", false, 0, 0, 0), _cps.LastNotice);
            var flash = GameObject.Find("Pickup_PICK-F01").GetComponent<Pickup>();
            flash.Interact(_pc.gameObject);
            Assert.IsTrue(_pc.inventory.hasFlashlight); Assert.IsFalse(flash.gameObject.activeSelf);
            // reentrada por streaming: salir de S1 hasta que se descargue y volver
            ObjectiveService.Grant(ObjectiveService.PermisoServicio);
            _pc.motor.Teleport(W("C-01", 6f, 0f), 90f);
            float t0 = Time.time; while (!_st.IsReady("REG-S2") && Time.time - t0 < 30f) yield return null;
            _pc.motor.Teleport(W("P03", 12f, 32f), 180f);
            t0 = Time.time; while (_st.State("REG-S1") != RegionState.Unloaded && Time.time - t0 < 40f) yield return null;
            Assert.AreEqual(RegionState.Unloaded, _st.State("REG-S1"));
            _pc.motor.Teleport(W("C-01", 6f, 0f), 270f);
            t0 = Time.time; while (!_st.IsReady("REG-S1") && Time.time - t0 < 30f) yield return null;
            Assert.IsTrue(_st.IsReady("REG-S1"), "S1 recargada al volver");
            yield return null;
            var flash2 = GameObject.Find("Pickup_PICK-F01");
            Assert.IsTrue(flash2 == null || !flash2.activeSelf, "reentrar no reinicia el pickup recogido (registro global)");
            Assert.IsTrue(_pc.inventory.hasFlashlight);
            // retry: restaurar el checkpoint revierte el progreso
            Assert.IsTrue(_cps.RestoreInto(_cps.LastConfirmed, _pc)); yield return null;
            Assert.IsFalse(_pc.inventory.hasFlashlight, "retry devuelve el estado del snapshot");
            var flash3 = Object.FindObjectsByType<Pickup>(FindObjectsInactive.Include, FindObjectsSortMode.None);
            bool back = false; foreach (var p in flash3) if (p.stableId == "PICK-F01" && p.gameObject.activeSelf) back = true;
            Assert.IsTrue(back, "el pickup vuelve al mundo tras el retry");
        }

        [UnityTest]
        public IEnumerator UnknownRegionFailsSafely()
        {
            var op = _st.Preload("REG-XX"); yield return op;
            Assert.AreEqual(RegionState.Unloaded, _st.State("REG-XX"));
            Assert.AreEqual(GameState.Playing, GameFlowController.Instance.State, "un fallo de carga no rompe la sesión");
        }
    }
}
