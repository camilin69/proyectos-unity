using Esneider.Core;
using UnityEngine;

namespace Esneider.World
{
    // Volumen de una región: al entrar el jugador (entidad principal, no cada collider) el streamer cambia la región actual.
    [RequireComponent(typeof(BoxCollider))]
    public class RegionVolume : MonoBehaviour
    {
        public string regionId;

        void Awake() { var c = GetComponent<BoxCollider>(); c.isTrigger = true; gameObject.layer = GameLayers.Trigger; }

        BoxCollider _box;
        public bool Contains(Vector3 p) { if (_box == null) _box = GetComponent<BoxCollider>(); return _box.bounds.Contains(p + Vector3.up * 0.5f); }
        void OnTriggerEnter(Collider other)
        {
            var pc = other.GetComponent<Player.PlayerController>();
            if (pc == null) return;
            // 88.3: solo cuenta la entidad principal realmente dentro del volumen (un teletransporte puede disparar el trigger viejo)
            if (!Contains(pc.transform.position)) return;
            RegionStreamer.Instance?.NotifyPlayerEntered(regionId);
        }

        void OnTriggerStay(Collider other)
        {
            var pc = other.GetComponent<Player.PlayerController>();
            if (pc == null) return;
            RegionStreamer.Instance?.NotifyPlayerInside(regionId);
        }
    }
}
