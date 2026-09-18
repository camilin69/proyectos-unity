using System.Collections;
using System.Collections.Generic;
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
using UnityEngine.AI;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

namespace Esneider.Tests
{
    // 104.3 por sector: rutas 77.1 completas sobre el NavMesh, reservas 76.1 sin conflicto, eventos U una sola vez,
    // V15 protegido hasta la lectura (EVT-16), V23 despierta al salir del control tras DOC-11 (EVT-18), ventana C-02 (EVT-C2).
    public class SectorPlayTests
    {
        PlayerController _pc; RegionStreamer _st; string _dir; LevelPlan _plan;

        [UnitySetUp]
        public IEnumerator SetUp()
        {
            Health.Clock = () => Time.time; WorldStateRegistry.ResetSession();
            _dir = Path.Combine(Path.GetTempPath(), "esneider-tests", System.Guid.NewGuid().ToString("N"));
            _plan = LevelPlan.FromJson(File.ReadAllText(LevelPlan.DefaultAssetPath));
#if UNITY_EDITOR
            yield return UnityEditor.SceneManagement.EditorSceneManager.LoadSceneAsyncInPlayMode("Assets/_Game/Scenes/BOOT.unity", new LoadSceneParameters(LoadSceneMode.Single));
#endif
            yield return null;
            _pc = Object.FindFirstObjectByType<PlayerController>(); _st = RegionStreamer.Instance;
            CheckpointService.Instance.saveDirectoryOverride = _dir;
            float t0 = Time.time; while (!_st.IsReady("REG-S1") && Time.time - t0 < 20f) yield return null;
            Object.FindFirstObjectByType<OpeningSequence>()?.RequestSkip();
            t0 = Time.time; while (!_pc.motor.movementEnabled && Time.time - t0 < 25f) yield return null;
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
        static EnemyBrain Unit(string id) => Object.FindObjectsByType<EnemyBrain>(FindObjectsInactive.Include, FindObjectsSortMode.None).FirstOrDefault(b => b.stableId == id);
        static Pickup Doc(string id) => Object.FindObjectsByType<Pickup>(FindObjectsInactive.Include, FindObjectsSortMode.None).FirstOrDefault(p => p.documentId == id);

        IEnumerator Go(string region, string space, float x, float z, float yaw)
        {
            yield return _st.LoadForCheckpoint(region);
            _pc.motor.Teleport(W(space, x, z), yaw); yield return null; yield return null;
        }

        [UnityTest]
        public IEnumerator Patrols_AllWaypointsReachable_EveryRegion()
        {
            var failures = new List<string>(); int checkedUnits = 0;
            foreach (var region in RegionCatalog.Chain)
            {
                yield return _st.LoadForCheckpoint(region); yield return null;
                foreach (var b in Object.FindObjectsByType<EnemyBrain>(FindObjectsInactive.Include, FindObjectsSortMode.None).Where(b => b.gameObject.scene.name == region))
                {
                    if (b.stableId == "B01") continue; checkedUnits++;
                    if (!NavMesh.SamplePosition(b.transform.position, out var start, 1.5f, NavMesh.AllAreas)) { failures.Add($"{region} {b.stableId}: spawn fuera del NavMesh {b.transform.position}"); continue; }
                    var plan = _plan.PatrolOf(b.stableId);
                    if (plan != null) Assert.AreEqual(plan.points.Count, b.waypoints.Count, $"{b.stableId}: waypoints del plano cableados");
                    for (int i = 0; i < b.waypoints.Count; i++)
                    {
                        if (!NavMesh.SamplePosition(b.waypoints[i].position, out var hit, 1.0f, NavMesh.AllAreas)) { failures.Add($"{region} {b.stableId} WP{i} fuera del NavMesh {b.waypoints[i].position}"); continue; }
                        var path = new NavMeshPath();
                        if (!NavMesh.CalculatePath(start.position, hit.position, NavMesh.AllAreas, path) || path.status != NavMeshPathStatus.PathComplete) failures.Add($"{region} {b.stableId} WP{i}: ruta {path.status}");
                    }
                }
            }
            Assert.Greater(checkedUnits, 30, "se comprobaron las unidades del catálogo");
            Assert.IsEmpty(failures, string.Join("\n", failures));
        }

        [UnityTest]
        public IEnumerator Furniture_ReportHasNoUnresolvedConflicts()
        {
            var rep = Path.GetFullPath(Path.Combine(Application.dataPath, "../../docs/produccion/evidencia/EX-06_furniture_report.md"));
            Assert.IsTrue(File.Exists(rep), "informe de mobiliario generado por RegionSceneBuilder");
            var text = File.ReadAllText(rep);
            Assert.IsFalse(text.Contains("SIN CORRECCIÓN"), "toda invasión de reserva quedó corregida:\n" + text);
            yield return null;
        }

        [UnityTest]
        public IEnumerator S3_V15_InactiveUntilDoc09Read_ThenPatrols()
        {
            yield return Go("REG-S3", "P05", 47f, 40f, 90f);
            var v15 = Unit("V15"); Assert.IsNotNull(v15);
            yield return new WaitForSeconds(1f);
            Assert.AreEqual(EnemyState.Inactive, v15.State, "V15 protegido durante la primera lectura (EVT-16)");
            var doc = Doc("DOC-09"); Assert.IsNotNull(doc, "DOC-09 en observación"); doc.Interact(_pc.gameObject);
            float t0 = Time.time; while (v15.State == EnemyState.Inactive && Time.time - t0 < 3f) yield return null;
            Assert.AreNotEqual(EnemyState.Inactive, v15.State, "V15 patrulla tras cerrar la lectura");
            Assert.IsTrue(WorldStateRegistry.Session.HasFlag("V15_RELEASED"));
            Assert.IsTrue(EventRunner.Instance.IsDone("EVT-16"));
        }

        [UnityTest]
        public IEnumerator S4_V23_WakesOnlyAfterDoc11AndLeavingControl()
        {
            yield return Go("REG-S4", "P06", 12f, 12f, 0f);
            var v23 = Unit("V23"); Assert.IsNotNull(v23);
            yield return new WaitForSeconds(0.5f);
            _pc.motor.Teleport(W("P06", 12f, 30f), 0f); yield return new WaitForSeconds(1f); // salir sin leer: nada
            Assert.AreEqual(EnemyState.Inactive, v23.State, "sin DOC-11 no hay despertar");
            Assert.IsFalse(EventRunner.Instance.IsDone("EVT-18"));
            _pc.motor.Teleport(W("P06", 12f, 12f), 0f); yield return null; yield return null;
            var doc = Doc("DOC-11"); Assert.IsNotNull(doc); doc.Interact(_pc.gameObject); yield return null;
            _pc.motor.Teleport(W("P06", 12f, 30f), 0f);
            float t0 = Time.time; while (v23.State == EnemyState.Inactive && Time.time - t0 < 3f) yield return null;
            Assert.AreNotEqual(EnemyState.Inactive, v23.State, "V23 despierta con servo al salir tras leer DOC-11 (EVT-18)");
            Assert.IsTrue(EventRunner.Instance.IsDone("EVT-18"));
        }

        [UnityTest]
        public IEnumerator C2_WindowRevealsHumans_CompletesO06Once()
        {
            yield return Go("REG-C2", "C-02", 24f, 8f, 0f);
            float t0 = Time.time; while (!WorldStateRegistry.Session.HasObjective("O06") && Time.time - t0 < 3f) yield return null;
            Assert.IsTrue(WorldStateRegistry.Session.HasObjective("O06"), "EVT-C2 compromete O06");
            Assert.IsTrue(WorldStateRegistry.Session.HasFlag("HUMANS_SEEN"));
            _pc.motor.Teleport(W("C-02", 24f, -1f), 0f); yield return new WaitForSeconds(0.3f);
            _pc.motor.Teleport(W("C-02", 24f, 8f), 0f); yield return new WaitForSeconds(0.5f);
            Assert.AreEqual(1, WorldStateRegistry.Session.EventsDone.Count(e => e == "EVT-C2"), "política U: una vez");
        }
    }
}
