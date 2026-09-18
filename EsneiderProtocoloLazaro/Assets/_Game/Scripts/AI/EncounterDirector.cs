using System.Collections.Generic;
using UnityEngine;

namespace Esneider.AI
{
    // Sección 14/78.3: máximo dos slots ofensivos, emisiones separadas ≥ 0.65 s, liberación por muerte/pérdida/bloqueo 2 s.
    public class EncounterDirector : MonoBehaviour
    {
        public static EncounterDirector Instance { get; private set; }
        public int maxSlots = 2;
        public float minEmissionGap = 0.65f;
        public float slotBlockedTimeout = 2f;
        readonly Dictionary<EnemyBrain, float> _slots = new Dictionary<EnemyBrain, float>();
        public float lastEmissionTime = -10f;
        public int SlotsInUse => _slots.Count;

        void Awake() { if (Instance != null && Instance != this) { Destroy(this); return; } Instance = this; }
        void OnDestroy() { if (Instance == this) Instance = null; }

        public bool TryAcquireSlot(EnemyBrain b, bool reserveAll = false)
        {
            if (_slots.ContainsKey(b)) { _slots[b] = Time.time; return true; }
            if (reserveAll) { _slots.Clear(); for (int i = 0; i < maxSlots; i++) _slots[b] = Time.time; return true; }
            if (_slots.Count >= maxSlots) return false;
            _slots[b] = Time.time; return true;
        }

        public void Heartbeat(EnemyBrain b) { if (_slots.ContainsKey(b)) _slots[b] = Time.time; }
        public void Release(EnemyBrain b) => _slots.Remove(b);
        public bool CanEmitNow() => Time.time - lastEmissionTime >= minEmissionGap;
        public void RegisterEmission() => lastEmissionTime = Time.time;

        void Update()
        {
            var expired = new List<EnemyBrain>();
            foreach (var kv in _slots) if (kv.Key == null || Time.time - kv.Value > slotBlockedTimeout) expired.Add(kv.Key);
            foreach (var e in expired) _slots.Remove(e);
        }

        public static EncounterDirector Ensure()
        {
            if (Instance == null) Instance = new GameObject("EncounterDirector").AddComponent<EncounterDirector>();
            return Instance;
        }
    }
}
