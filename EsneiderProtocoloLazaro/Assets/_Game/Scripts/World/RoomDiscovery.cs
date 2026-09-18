using Esneider.Core.Data;
using Esneider.Core.Persistence;
using UnityEngine;

namespace Esneider.World
{
    // 87.3: revelar sala al atravesarla (RoomGuid en el registro, separado del estado físico). El plano es la misma fuente que el blockout.
    public class RoomDiscovery : MonoBehaviour
    {
        public TextAsset planJson;
        public static LevelPlan Plan { get; private set; }
        Transform _player; float _next;
        public string CurrentRoom { get; private set; } = "";
        public string CurrentFloor { get; private set; } = "";

        void Start() { if (planJson != null) Plan = LevelPlan.FromJson(planJson.text); }

        void Update()
        {
            if (Plan == null || Time.time < _next) return; _next = Time.time + 0.4f;
            if (_player == null) { var pc = FindFirstObjectByType<Player.PlayerController>(); if (pc == null) return; _player = pc.transform; }
            var p = _player.position; PlanFloor best = null; float bestDy = 99f;
            foreach (var f in Plan.floors)
            {
                var o = f.origin.ToVector3(); float dy = p.y - o.y;
                if (dy < -1f || dy > f.height + 1f) continue;
                if (p.x < o.x - 1f || p.x > o.x + f.w + 1f || p.z < o.z - 1f || p.z > o.z + f.d + 1f) continue;
                if (Mathf.Abs(dy) < bestDy) { bestDy = Mathf.Abs(dy); best = f; }
            }
            CurrentFloor = best != null ? best.id : ""; CurrentRoom = "";
            if (best == null) return;
            var o2 = best.origin.ToVector3(); float lx = p.x - o2.x, lz = p.z - o2.z;
            foreach (var r in Plan.rooms) if (r.floor == best.id && r.Contains(lx, lz)) { CurrentRoom = r.id; WorldStateRegistry.Session.DiscoverRoom(r.id); break; }
        }
    }
}
