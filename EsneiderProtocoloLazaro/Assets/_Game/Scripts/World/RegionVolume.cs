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

        void OnTriggerEnter(Collider other)
        {
            var pc = other.GetComponent<Player.PlayerController>();
            if (pc == null) return;
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
