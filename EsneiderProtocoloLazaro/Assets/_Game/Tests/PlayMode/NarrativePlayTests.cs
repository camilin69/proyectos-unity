using System.Collections;
using System.IO;
using Esneider.AI;
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
    // EVT-01 (apertura U, omisible, no se repite tras retry) y EVT-C1 (detección una vez: flag, O03, activación de bots, voz desde el altavoz).
    public class NarrativePlayTests
    {
        PlayerController _pc; RegionStreamer _st; string _dir;

        [UnitySetUp]
        public IEnumerator SetUp()
        {
            Health.Clock = () => Time.time; WorldStateRegistry.ResetSession();
            _dir = Path.Combine(Path.GetTempPath(), "esneider-tests", System.Guid.NewGuid().ToString("N"));
#if UNITY_EDITOR
            yield return UnityEditor.SceneManagement.EditorSceneManager.LoadSceneAsyncInPlayMode("Assets/_Game/Scenes/BOOT.unity", new LoadSceneParameters(LoadSceneMode.Single));
#endif
            yield return null;
            _pc = Object.FindFirstObjectByType<PlayerController>(); _st = RegionStreamer.Instance;
            CheckpointService.Instance.saveDirectoryOverride = _dir;
            float t0 = Time.time; while (!_st.IsReady("REG-S1") && Time.time - t0 < 20f) yield return null;
            yield return null; yield return null;
        }

        [UnityTearDown]
        public IEnumerator TearDown()
        {
            Time.timeScale = 1f; try { Directory.Delete(_dir, true); } catch { }
            yield return SceneManager.LoadSceneAsync("Combat_Sandbox", LoadSceneMode.Single);
            var pc = Object.FindFirstObjectByType<PlayerController>(); if (pc != null) Object.Destroy(pc.transform.root.gameObject);
            yield return null;
        }

        [UnityTest]
        public IEnumerator Opening_RunsOnce_IsSkippable_AndCommitsCP00()
        {
            float tw = Time.time; while (_pc.motor.movementEnabled && Time.time - tw < 3f) yield return null;
            Assert.IsTrue(EventRunner.Instance.IsDone("EVT-01"), "la apertura queda comprometida al iniciar (política U)");
            Assert.IsFalse(_pc.motor.movementEnabled, "sin control durante la apertura");
            // omitir (E/Espacio)
            var opening = Object.FindFirstObjectByType<OpeningSequence>(); Assert.IsNotNull(opening, "OpeningSequence en REG-S1");
            int commits = 0; CheckpointService.Instance.Committed += d => { if (d.checkpointId == "CP-00") commits++; };
            float t0 = Time.time; opening.RequestSkip();
            while (!_pc.motor.movementEnabled && Time.time - t0 < 25f) yield return null;
            Assert.IsTrue(_pc.motor.movementEnabled, "control disponible tras omitir la apertura");
            Assert.Less(Time.time - t0, 3f, "omitir corta la apertura de inmediato");
            Assert.IsTrue(WorldStateRegistry.Session.HasFlag("OPENING_DONE"), "flag OPENING_DONE");
            t0 = Time.time; while (commits == 0 && Time.time - t0 < 6f) yield return null;
            Assert.AreEqual(1, commits, "la apertura confirma CP-00 al terminar: " + CheckpointService.Instance.LastNotice);
            Assert.IsTrue(CheckpointService.Instance.LastConfirmed.world.eventsDone.Contains("EVT-01"), "el snapshot de CP-00 incluye EVT-01 hecho");
            Assert.AreEqual("CP-00", CheckpointService.Instance.LastConfirmed.checkpointId, "CP-00 es el último confirmado");
            // retry: restaurar CP-00 no reinicia la apertura
            Assert.IsTrue(CheckpointService.Instance.RestoreInto(CheckpointService.Instance.LastConfirmed, _pc), "RestoreInto"); yield return null;
            Assert.IsTrue(EventRunner.Instance.IsDone("EVT-01"), "EVT-01 sigue hecho tras restaurar");
            Assert.IsTrue(_pc.motor.movementEnabled, "tras cargar CP-00 el jugador está en control, sin repetir la cinemática");
        }

        [UnityTest]
        public IEnumerator Detection_FiresOnceWhenD06Opens_ActivatesUnits()
        {
            float tw = Time.time; while (_pc.motor.movementEnabled && Time.time - tw < 3f) yield return null;
            Object.FindFirstObjectByType<OpeningSequence>()?.RequestSkip();
            float t0 = Time.time; while (!_pc.motor.movementEnabled && Time.time - t0 < 25f) yield return null;
            // antes de D06: bots de S1/C1 inactivos (104.3)
            var v01 = FindBrain("V01");
            Assert.IsNotNull(v01, "V01 cargado con C1 (vecina de S1)");
            Assert.AreEqual(EnemyState.Inactive, v01.State, "sin ataques antes de D06");
            // palanca → permiso; abrir D06
            GameObject.Find("Mech_MECH-LEVER-S1").GetComponent<Mechanism>().Interact(_pc.gameObject);
            Door d06 = null; foreach (var d in Object.FindObjectsByType<Door>(FindObjectsSortMode.None)) if (d.doorId == "D06") d06 = d;
            Assert.IsNotNull(d06); Assert.IsTrue(d06.Allowed);
            d06.SetOpen(true);
            t0 = Time.time; while (!ObjectiveService.Has(ObjectiveService.Detected) && Time.time - t0 < 5f) yield return null;
            Assert.IsTrue(ObjectiveService.Has(ObjectiveService.Detected), "EVT-C1 compromete DETECTADO");
            Assert.IsTrue(WorldStateRegistry.Session.HasObjective("O03"));
            Assert.IsTrue(EventRunner.Instance.IsDone("EVT-C1"));
            Assert.AreNotEqual(EnemyState.Inactive, v01.State, "las unidades se activan tras la detección");
            // cerrar y reabrir no repite el evento
            d06.SnapOpen(false); yield return null; d06.SetOpen(true); yield return new WaitForSeconds(0.5f);
            int count = 0; foreach (var e in WorldStateRegistry.Session.EventsDone) if (e == "EVT-C1") count++;
            Assert.AreEqual(1, count);
        }

        static EnemyBrain FindBrain(string id) { foreach (var b in Object.FindObjectsByType<EnemyBrain>(FindObjectsInactive.Include, FindObjectsSortMode.None)) if (b.stableId == id) return b; return null; }
    }
}
