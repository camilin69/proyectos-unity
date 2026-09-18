using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace Esneider.Core
{
    // 91.4/105.2/FIN-11: mediana y p95 de tiempo de frame, hitches >100 ms, memoria; se escribe a persistentDataPath/perf_*.json.
    // -autotest: recorre una ruta y sale solo (medición en build sin operador).
    //   -perfroute <S1_apertura|S2_nave|S3_jaulasA|S3_clinica|S4_control|S4_boss>  → los seis tramos de 91.4 (60 s tras 2 s de warmup)
    //   -perfsession <minutos>                                                     → sesión con ≥20 cambios regionales; memoria por retorno a S1
    public class PerfProbe : MonoBehaviour
    {
        public string label = "run";
        public float sampleSeconds = 30f;
        public Vector3[] route;
        public float routeSpeed = 2.5f;
        readonly List<float> _frames = new List<float>(8192);
        int _hitches; float _elapsed; bool _done; int _routeIndex; bool _auto, _ready = true, _combat;
        Player.PlayerController _pc; string _region = ""; float _sessionMinutes; readonly List<MemSample> _mem = new List<MemSample>();

        class RouteDef { public string region, space; public float[,] pts; public bool boss; }
        static readonly Dictionary<string, RouteDef> Routes = new Dictionary<string, RouteDef>
        {
            ["S1_apertura"] = new RouteDef { region = "REG-S1", space = "P01", pts = new float[,] { { 11, 10 }, { 17, 10 }, { 17, 24 }, { 8, 24 }, { 17, 24 }, { 17, 8 }, { 30, 13 } } },
            ["S2_nave"] = new RouteDef { region = "REG-S2", space = "P03", pts = new float[,] { { 12, 30 }, { 14, 20 }, { 15, 10 }, { 22, 16 }, { 24, 26 }, { 12, 30 } } },
            ["S3_jaulasA"] = new RouteDef { region = "REG-S3", space = "P05", pts = new float[,] { { 11, 4 }, { 11, 24 }, { 20, 13 }, { 3, 13 }, { 11, 4 } } },
            ["S3_clinica"] = new RouteDef { region = "REG-S3", space = "P05", pts = new float[,] { { 29, 34 }, { 29, 52 }, { 38, 45 }, { 24, 45 }, { 29, 34 } } },
            ["S4_control"] = new RouteDef { region = "REG-S4", space = "P06", pts = new float[,] { { 12, 4 }, { 12, 24 }, { 20, 12 }, { 4, 12 }, { 12, 4 } } },
            ["S4_boss"] = new RouteDef { region = "REG-S4", space = "P06", pts = new float[,] { { 40, 22 }, { 33, 16 }, { 40, 8 }, { 47, 16 }, { 40, 22 } }, boss = true },
        };
        static readonly (string region, string space, float x, float z)[] SessionLegs =
        {
            ("REG-S1", "P01", 11, 10), ("REG-C1", "C-01", 6, 0), ("REG-S2", "P03", 12, 30), ("REG-C2", "C-02", 6, 0), ("REG-S3", "P05", 11, 12), ("REG-C3", "C-03", 6, 0), ("REG-S4", "P06", 12, 12),
            ("REG-C3", "C-03", 30, 10), ("REG-S3", "P05", 29, 45), ("REG-C2", "C-02", 36, 16), ("REG-S2", "P04", 8, 10), ("REG-C1", "C-01", 30, 12),
        };

        static string Arg(string name) { var a = System.Environment.GetCommandLineArgs(); int i = System.Array.IndexOf(a, name); return i >= 0 && i + 1 < a.Length ? a[i + 1] : null; }

        void Start()
        {
            _auto = System.Array.IndexOf(System.Environment.GetCommandLineArgs(), "-autotest") >= 0;
            _pc = FindFirstObjectByType<Player.PlayerController>();
            if (!_auto) return;
            UI.MenuController.SkipTitle = true; // sin operador: no mostrar Inicio (dejaría el mundo congelado y la medición sería falsa)
            Screen.SetResolution(1280, 720, FullScreenMode.Windowed); // 91.4: 1280×720 perfil local, ventana
            if (_pc != null) _pc.motor.movementEnabled = false;
            var r = Arg("-perfroute"); var s = Arg("-perfsession");
            if (!string.IsNullOrEmpty(s) && float.TryParse(s, out _sessionMinutes)) { label = "session"; _ready = false; StartCoroutine(Session()); }
            else if (!string.IsNullOrEmpty(r) && Routes.ContainsKey(r)) { label = r; sampleSeconds = 62f; _ready = false; StartCoroutine(Prepare(Routes[r])); }
        }

        IEnumerator WaitPlan() { float t0 = Time.realtimeSinceStartup; while (World.RoomDiscovery.Plan == null && Time.realtimeSinceStartup - t0 < 10f) yield return null; }
        Vector3 W(string space, float x, float z) { World.RoomDiscovery.Plan.TryToWorld(space, x, z, out var w); return w; }

        IEnumerator Prepare(RouteDef def)
        {
            yield return null; yield return WaitPlan();
            FindFirstObjectByType<World.OpeningSequence>()?.RequestSkip();
            var pts = new Vector3[def.pts.GetLength(0)]; for (int i = 0; i < pts.Length; i++) pts[i] = W(def.space, def.pts[i, 0], def.pts[i, 1]);
            route = pts; _region = def.region;
            var st = World.RegionStreamer.Instance;
            if (st != null) yield return st.LoadForCheckpoint(def.region, pts[0], 0f);
            yield return null;
            if (def.boss)
            {
                // fase III: el jefe recibe 900 de daño de prueba; el jugador se mantiene vivo para medir el combate completo
                var boss = FindFirstObjectByType<AI.BossBrain>(); var hp = boss != null ? boss.GetComponent<Health>() : null;
                if (hp != null) { hp.ApplyDamage(new DamageInfo { amount = 900f, attackId = AttackIds.Next(), kind = "PerfProbe" }); _combat = true; }
            }
            _elapsed = 0f; _frames.Clear(); _hitches = 0; _ready = true;
        }

        IEnumerator Session()
        {
            yield return null; yield return WaitPlan();
            FindFirstObjectByType<World.OpeningSequence>()?.RequestSkip();
            var st = World.RegionStreamer.Instance; _ready = true; _elapsed = 0f;
            float legSeconds = Mathf.Max(20f, _sessionMinutes * 60f / 24f); int changes = 0;
            float t0 = Time.realtimeSinceStartup;
            while (Time.realtimeSinceStartup - t0 < _sessionMinutes * 60f)
            {
                var leg = SessionLegs[changes % SessionLegs.Length];
                if (st != null) yield return st.LoadForCheckpoint(leg.region, W(leg.space, leg.x, leg.z), 0f);
                changes++; _region = leg.region;
                yield return new WaitForSecondsRealtime(legSeconds);
                if (leg.region == "REG-S1" || changes % SessionLegs.Length == 0)
                {
                    System.GC.Collect();
                    _mem.Add(new MemSample { t = Time.realtimeSinceStartup - t0, region = leg.region, changes = changes, allocatedMB = UnityEngine.Profiling.Profiler.GetTotalAllocatedMemoryLong() / (1024f * 1024f), reservedMB = UnityEngine.Profiling.Profiler.GetTotalReservedMemoryLong() / (1024f * 1024f), monoMB = UnityEngine.Profiling.Profiler.GetMonoUsedSizeLong() / (1024f * 1024f) });
                }
            }
            sampleSeconds = _elapsed; Finish();
        }

        void LateUpdate()
        {
            if (!_auto) return;
            var opening = FindFirstObjectByType<World.OpeningSequence>();
            if (opening != null && opening.IsPlaying) opening.RequestSkip();
            if (_combat && _pc != null && _pc.health.Current < 45f) _pc.health.ResetTo(90f);
        }

        void Update()
        {
            if (_done || !_ready) return;
            float dt = Time.unscaledDeltaTime;
            if (_elapsed > 2f) { _frames.Add(dt * 1000f); if (dt > 0.1f) _hitches++; }
            _elapsed += dt;
            if (_auto && _pc != null && route != null && route.Length > 0 && label != "session")
            {
                var target = route[_routeIndex % route.Length];
                var p = _pc.transform.position; var to = target - p; to.y = 0;
                if (to.magnitude < 0.5f) _routeIndex++;
                else { _pc.motor.Teleport(p + to.normalized * routeSpeed * Time.deltaTime, Quaternion.LookRotation(to).eulerAngles.y); }
            }
            if (label != "session" && _elapsed >= sampleSeconds) Finish();
        }

        public void Finish()
        {
            if (_done) return; _done = true;
            var sorted = new List<float>(_frames); sorted.Sort();
            float med = sorted.Count > 0 ? sorted[sorted.Count / 2] : 0, p95 = sorted.Count > 0 ? sorted[Mathf.Min(sorted.Count - 1, (int)(sorted.Count * 0.95f))] : 0;
            var report = new Report
            {
                label = label, frames = sorted.Count, medianMs = med, p95Ms = p95, hitches = _hitches, fpsMedian = med > 0 ? 1000f / med : 0, seconds = _elapsed,
                width = Screen.width, height = Screen.height, vsync = QualitySettings.vSyncCount, quality = QualitySettings.names[QualitySettings.GetQualityLevel()], fullscreen = Screen.fullScreenMode.ToString(), minFps = sorted.Count > 0 ? 1000f / sorted[sorted.Count - 1] : 0, gpu = SystemInfo.graphicsDeviceName, api = SystemInfo.graphicsDeviceType.ToString(), cpu = SystemInfo.processorType,
                totalReservedMB = UnityEngine.Profiling.Profiler.GetTotalReservedMemoryLong() / (1024f * 1024f), totalAllocatedMB = UnityEngine.Profiling.Profiler.GetTotalAllocatedMemoryLong() / (1024f * 1024f),
                gfxMB = UnityEngine.Profiling.Profiler.GetAllocatedMemoryForGraphicsDriver() / (1024f * 1024f), isEditor = Application.isEditor, build = Application.version, region = !string.IsNullOrEmpty(_region) ? _region : (World.RegionStreamer.Instance != null ? World.RegionStreamer.Instance.CurrentRegion : ""),
                combat = _combat, memory = _mem.ToArray()
            };
            if (_mem.Count >= 2) { var first = _mem[0]; var last = _mem[_mem.Count - 1]; report.memoryGrowthPercent = first.allocatedMB > 0 ? (last.allocatedMB - first.allocatedMB) / first.allocatedMB * 100f : 0; report.regionChanges = last.changes; }
            var path = Path.Combine(Application.persistentDataPath, $"perf_{label}.json");
            File.WriteAllText(path, JsonUtility.ToJson(report, true));
            Debug.Log($"PerfProbe {label}: median {med:F1} ms (fps {report.fpsMedian:F0}), p95 {p95:F1} ms, hitches {_hitches}, frames {sorted.Count} → {path}");
            if (_auto) Application.Quit();
        }

        [System.Serializable] public class MemSample { public float t, allocatedMB, reservedMB, monoMB; public string region; public int changes; }
        [System.Serializable]
        public class Report { public string label, gpu, api, cpu, build, region, quality, fullscreen; public int frames, hitches, width, height, vsync, regionChanges; public float medianMs, p95Ms, fpsMedian, minFps, totalReservedMB, totalAllocatedMB, gfxMB, seconds, memoryGrowthPercent; public bool isEditor, combat; public MemSample[] memory; }
    }
}
