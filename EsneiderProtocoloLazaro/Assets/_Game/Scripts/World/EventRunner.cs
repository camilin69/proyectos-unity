using System;
using System.Collections.Generic;
using Esneider.Core;
using Esneider.Core.Persistence;
using UnityEngine;

namespace Esneider.World
{
    // 93.1: eventos con EventGuid/RoomGuid, políticas U (una vez por campaña respecto al snapshot), R (cooldown), A (ambiente), I (interacción).
    // Los eventos de progreso comprometen datos lógicos antes del feedback; reentrar por streaming no los reinicia.
    public class EventRunner : MonoBehaviour
    {
        public static EventRunner Instance { get; private set; }
        readonly Dictionary<string, float> _lastRun = new Dictionary<string, float>();
        readonly HashSet<string> _running = new HashSet<string>();
        public event Action<string> EventCompleted;

        void Awake() { if (Instance != null && Instance != this) { Destroy(this); return; } Instance = this; }
        void OnDestroy() { if (Instance == this) Instance = null; }

        public bool IsDone(string eventId) => WorldStateRegistry.Session.IsEventDone(eventId);
        public void ResetForCheckpoint() { _lastRun.Clear(); _running.Clear(); }

        // Política U: elegible solo si no está completado en el registro; commit lógico inmediato al iniciar.
        public bool TryRunOnce(string eventId, Action action)
        {
            if (IsDone(eventId) || _running.Contains(eventId)) return false;
            WorldStateRegistry.Session.MarkEventDone(eventId);
            WorldStateRegistry.Session.Apply(WorldEventKind.FlagSet, "", null, "EVT:" + eventId);
            Run(eventId, action); return true;
        }

        // Política R: repetible con cooldown.
        public bool TryRunRepeatable(string eventId, float cooldown, Action action)
        {
            if (_lastRun.TryGetValue(eventId, out var t) && Time.time - t < cooldown) return false;
            _lastRun[eventId] = Time.time; Run(eventId, action); return true;
        }

        void Run(string id, Action action)
        {
            _running.Add(id);
            try { action?.Invoke(); }
            catch (Exception e) { Debug.LogError($"EVT {id}: fallback por excepción ({e.Message}); el progreso lógico ya está comprometido (93.3)"); }
            finally { _running.Remove(id); EventCompleted?.Invoke(id); }
        }
    }
}
