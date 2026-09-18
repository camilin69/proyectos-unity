using System;
using System.Collections.Generic;
using UnityEngine;

namespace Esneider.Core
{
    public struct DamageInfo
    {
        public float amount;
        public int attackId;
        public GameObject source;
        public Vector3 point;
        public Vector3 direction;
        public string kind; // "Crowbar", "Pistol", "Shotgun", "Bolt", "Net", "Boss:*"
    }

    // Sección 10/79/86: un daño por AttackID + invulnerabilidad tras daño válido. Compartido por jugador y enemigos.
    public class Health : MonoBehaviour
    {
        public int maxHp = 90;
        public float invulnerabilitySeconds = 0f;
        [SerializeField] float current;
        public float Current => current;
        public bool IsDead => current <= 0f;
        public float LastValidDamageTime { get; private set; } = -999f;

        public event Action<DamageInfo, float> Damaged;
        public event Action<DamageInfo> Died;
        public event Action<float> Healed;

        readonly Dictionary<int, float> _seenAttacks = new Dictionary<int, float>();
        const float AttackMemorySeconds = 5f;
        // Reloj inyectable para pruebas en Edit Mode.
        public static System.Func<float> Clock = () => Time.time;

        void Awake() { if (current <= 0f) current = maxHp; }

        public void ResetTo(float hp) { current = Mathf.Clamp(hp, 0, maxHp); _seenAttacks.Clear(); LastValidDamageTime = -999f; }

        // Devuelve true solo si el daño se aplicó.
        public bool ApplyDamage(DamageInfo info)
        {
            if (IsDead) return false;
            float now = Clock();
            if (info.attackId != 0)
            {
                Prune(now);
                if (_seenAttacks.ContainsKey(info.attackId)) return false;
                _seenAttacks[info.attackId] = now;
            }
            if (invulnerabilitySeconds > 0f && now - LastValidDamageTime < invulnerabilitySeconds) return false;
            if (info.amount <= 0f) return false;
            current = Mathf.Max(0f, current - info.amount);
            LastValidDamageTime = now;
            Damaged?.Invoke(info, current);
            if (current <= 0f) Died?.Invoke(info);
            return true;
        }

        public float Heal(float amount)
        {
            if (IsDead || amount <= 0f) return 0f;
            float before = current;
            current = Mathf.Min(maxHp, current + amount);
            float applied = current - before;
            if (applied > 0f) Healed?.Invoke(applied);
            return applied;
        }

        void Prune(float now)
        {
            if (_seenAttacks.Count < 64) return;
            var dead = new List<int>();
            foreach (var kv in _seenAttacks) if (now - kv.Value > AttackMemorySeconds) dead.Add(kv.Key);
            foreach (var k in dead) _seenAttacks.Remove(k);
        }
    }

    public static class AttackIds
    {
        static int _next = 1;
        public static int Next() => _next++;
    }
}
