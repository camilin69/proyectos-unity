using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace Esneider.Core
{
    // 91.4/105.2/FIN-11: mediana y p95 de tiempo de frame, hitches >100 ms, memoria; se escribe a persistentDataPath/perf_*.json.
    // Con -autotest en la línea de comandos recorre una ruta de puntos y sale solo (medición en build sin operador).
    public class PerfProbe : MonoBehaviour
    {
        public string label = "run";
        public float sampleSeconds = 30f;
        public Vector3[] route;
        public float routeSpeed = 2.5f;
        readonly List<float> _frames = new List<float>(4096);
        int _hitches; float _elapsed; bool _done; int _routeIndex; bool _auto;
        Player.PlayerController _pc;

        void Start()
        {
            _auto = System.Array.IndexOf(System.Environment.GetCommandLineArgs(), "-autotest") >= 0;
            _pc = FindFirstObjectByType<Player.PlayerController>();
            if (_auto && _pc != null) { _pc.motor.movementEnabled = false; }
        }

        void Update()
        {
            if (_done) return;
            float dt = Time.unscaledDeltaTime;
            if (_elapsed > 2f) { _frames.Add(dt * 1000f); if (dt > 0.1f) _hitches++; }
            _elapsed += dt;
            if (_auto && _pc != null && route != null && route.Length > 0)
            {
                var target = route[_routeIndex % route.Length];
                var p = _pc.transform.position; var to = target - p; to.y = 0;
                if (to.magnitude < 0.5f) _routeIndex++;
                else { _pc.motor.Teleport(p + to.normalized * routeSpeed * Time.deltaTime, Quaternion.LookRotation(to).eulerAngles.y); }
            }
            if (_elapsed >= sampleSeconds) Finish();
        }

        public void Finish()
        {
            if (_done) return; _done = true;
            _frames.Sort();
            float med = _frames.Count > 0 ? _frames[_frames.Count / 2] : 0, p95 = _frames.Count > 0 ? _frames[Mathf.Min(_frames.Count - 1, (int)(_frames.Count * 0.95f))] : 0;
            var report = new Report
            {
                label = label, frames = _frames.Count, medianMs = med, p95Ms = p95, hitches = _hitches, fpsMedian = med > 0 ? 1000f / med : 0,
                width = Screen.width, height = Screen.height, gpu = SystemInfo.graphicsDeviceName, api = SystemInfo.graphicsDeviceType.ToString(), cpu = SystemInfo.processorType,
                totalReservedMB = UnityEngine.Profiling.Profiler.GetTotalReservedMemoryLong() / (1024f * 1024f), totalAllocatedMB = UnityEngine.Profiling.Profiler.GetTotalAllocatedMemoryLong() / (1024f * 1024f),
                gfxMB = UnityEngine.Profiling.Profiler.GetAllocatedMemoryForGraphicsDriver() / (1024f * 1024f), isEditor = Application.isEditor, build = Application.version, region = World.RegionStreamer.Instance != null ? World.RegionStreamer.Instance.CurrentRegion : ""
            };
            var path = Path.Combine(Application.persistentDataPath, $"perf_{label}.json");
            File.WriteAllText(path, JsonUtility.ToJson(report, true));
            Debug.Log($"PerfProbe {label}: median {med:F1} ms (fps {report.fpsMedian:F0}), p95 {p95:F1} ms, hitches {_hitches}, frames {_frames.Count} → {path}");
            if (_auto) Application.Quit();
        }

        [System.Serializable]
        public class Report { public string label, gpu, api, cpu, build, region; public int frames, hitches, width, height; public float medianMs, p95Ms, fpsMedian, totalReservedMB, totalAllocatedMB, gfxMB; public bool isEditor; }
    }
}
