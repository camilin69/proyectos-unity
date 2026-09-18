using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using Esneider.AI;
using Esneider.Core;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Esneider.World
{
    public enum RegionState { Unloaded, Loading, Restoring, Ready, Active, Quiescing, Unloading, Failed }

    // 88: carga aditiva por región con estados explícitos, una operación por región, precarga de vecinas y descarga segura.
    public class RegionStreamer : MonoBehaviour
    {
        public static RegionStreamer Instance { get; private set; }
        public string initialRegion = "REG-S1";
        public bool loadOnStart = true;
        public float unloadSafetyDistance = 8f;
        public string CurrentRegion { get; private set; } = "";
        public event Action<string, RegionState> StateChanged;

        readonly Dictionary<string, RegionState> _states = new Dictionary<string, RegionState>();
        readonly HashSet<string> _pending = new HashSet<string>();
        readonly Dictionary<string, float> _insideSince = new Dictionary<string, float>();
        int _generation;

        void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(this); return; }
            Instance = this;
            foreach (var r in RegionCatalog.Chain) _states[r] = RegionState.Unloaded;
        }
        void OnDestroy() { if (Instance == this) Instance = null; }

        void Start() { if (loadOnStart) StartCoroutine(EnterRegion(initialRegion, true)); }

        public RegionState State(string region) => _states.TryGetValue(region, out var s) ? s : RegionState.Unloaded;
        public bool IsReady(string region) => State(region) == RegionState.Ready || State(region) == RegionState.Active;
        public IEnumerable<string> Loaded => _states.Where(kv => kv.Value != RegionState.Unloaded && kv.Value != RegionState.Failed).Select(kv => kv.Key);

        void Set(string region, RegionState s) { _states[region] = s; StateChanged?.Invoke(region, s); }

        // ---- solicitudes ----
        public void NotifyPlayerEntered(string region)
        {
            if (region == CurrentRegion) return;
            _insideSince[region] = Time.time;
            StartCoroutine(EnterRegion(region, false));
        }

        public void NotifyPlayerInside(string region) { if (!_insideSince.ContainsKey(region)) _insideSince[region] = Time.time; }

        // 88.2: preparar una región vecina antes de cruzar (palanca/permisos).
        public Coroutine Preload(string region) => StartCoroutine(EnsureLoaded(region));

        IEnumerator EnterRegion(string region, bool initial)
        {
            int gen = ++_generation;
            Player.PlayerController held = null;
            if (initial)
            {
                // 89.4: ningún frame en posición por defecto ni caída sin suelo; el jugador espera a la región Ready
                held = FindFirstObjectByType<Player.PlayerController>();
                if (held != null) { held.motor.movementEnabled = false; held.GetComponent<CharacterController>().enabled = false; }
            }
            yield return EnsureLoaded(region);
            if (held != null) { held.GetComponent<CharacterController>().enabled = true; held.motor.movementEnabled = true; held.motor.Teleport(held.transform.position, held.transform.eulerAngles.y); }
            if (gen != _generation && !initial) yield break;
            var prev = CurrentRegion; CurrentRegion = region;
            if (!string.IsNullOrEmpty(prev) && prev != region && State(prev) == RegionState.Active) Set(prev, RegionState.Ready);
            if (IsReady(region)) Set(region, RegionState.Active);
            // precargar vecinas de la cadena
            foreach (var n in RegionCatalog.Neighbors(region)) StartCoroutine(EnsureLoaded(n));
            // liberar regiones que ya no son actual ni vecina, solo si es seguro
            foreach (var r in RegionCatalog.Chain.ToArray())
                if (r != region && !RegionCatalog.Neighbors(region).Contains(r) && State(r) != RegionState.Unloaded) StartCoroutine(UnloadWhenSafe(r));
        }

        IEnumerator EnsureLoaded(string region)
        {
            if (string.IsNullOrEmpty(region) || RegionCatalog.Index(region) < 0) yield break;
            if (State(region) == RegionState.Ready || State(region) == RegionState.Active) yield break;
            if (_pending.Contains(region)) { while (_pending.Contains(region)) yield return null; yield break; }
            _pending.Add(region);
            try
            {
                if (State(region) == RegionState.Unloading || State(region) == RegionState.Quiescing)
                    while (State(region) != RegionState.Unloaded) yield return null;
                Set(region, RegionState.Loading);
                var scene = SceneManager.GetSceneByName(RegionCatalog.SceneName(region));
                if (!scene.isLoaded)
                {
                    AsyncOperation op = null;
                    try { op = SceneManager.LoadSceneAsync(RegionCatalog.SceneName(region), LoadSceneMode.Additive); }
                    catch (Exception e) { Debug.LogError($"Región {region}: {e.Message}"); }
                    if (op == null) { Set(region, RegionState.Failed); yield break; }
                    while (!op.isDone) yield return null;
                }
                Set(region, RegionState.Restoring);
                yield return null; // Start() de PersistentEntity hidrata desde el registro
                Set(region, RegionState.Ready);
            }
            finally { _pending.Remove(region); }
        }

        // 88.3: solo descargar sin jugador, sin ataque/perseguidor que cruce frontera, y fuera de contexto.
        IEnumerator UnloadWhenSafe(string region)
        {
            if (_pending.Contains(region) || State(region) == RegionState.Unloaded) yield break;
            _pending.Add(region);
            try
            {
                Set(region, RegionState.Quiescing);
                float t0 = Time.time;
                while (!SafeToUnload(region) && Time.time - t0 < 30f) { if (region == CurrentRegion || RegionCatalog.Neighbors(CurrentRegion).Contains(region)) { Set(region, RegionState.Ready); yield break; } yield return null; }
                if (region == CurrentRegion || RegionCatalog.Neighbors(CurrentRegion).Contains(region)) { Set(region, RegionState.Ready); yield break; }
                // consolidar estado estable en el registro antes de descargar (los bots congelan su patrulla)
                var scene = SceneManager.GetSceneByName(RegionCatalog.SceneName(region));
                if (scene.isLoaded)
                {
                    foreach (var root in scene.GetRootGameObjects()) foreach (var pe in root.GetComponentsInChildren<PersistentEntity>(true)) pe.CaptureStable();
                    Set(region, RegionState.Unloading);
                    var op = SceneManager.UnloadSceneAsync(scene);
                    while (op != null && !op.isDone) yield return null;
                }
                Set(region, RegionState.Unloaded);
            }
            finally { _pending.Remove(region); }
        }

        bool SafeToUnload(string region)
        {
            var flow = GameFlowController.Instance;
            if (flow != null && (flow.State == GameState.Captured || flow.State == GameState.Loading)) return false;
            var scene = SceneManager.GetSceneByName(RegionCatalog.SceneName(region));
            if (!scene.isLoaded) return true;
            var pc = FindFirstObjectByType<Player.PlayerController>();
            foreach (var root in scene.GetRootGameObjects())
                foreach (var b in root.GetComponentsInChildren<EnemyBrain>())
                    if (b.State == EnemyState.Chase || b.State == EnemyState.Prepare || b.State == EnemyState.Attack || b.State == EnemyState.Executing) return false;
            if (pc != null && _insideSince.TryGetValue(CurrentRegion, out var since) && Time.time - since < 1f) return false;
            return true;
        }

        // Carga de checkpoint (88.5/89.4): cancelar intención anterior con token de generación y restaurar solo el contexto del checkpoint.
        public IEnumerator LoadForCheckpoint(string region)
        {
            _generation++;
            yield return EnterRegion(region, true);
        }
    }
}
