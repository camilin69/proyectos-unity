using Esneider.Core;
using Esneider.Core.Persistence;
using UnityEngine;

namespace Esneider.World
{
    // 68.9: trigger de checkpoint; comprueba identidad del Player (no cualquier Rigidbody) y condiciones seguras (89.2 paso 1).
    [RequireComponent(typeof(BoxCollider))]
    public class CheckpointTrigger : MonoBehaviour
    {
        public string checkpointId;
        public string regionId;
        public bool isShelter;
        public int guaranteeHp, guaranteePistolTotal, guaranteeShotgunTotal;
        public float retrySeconds = 2f;
        float _nextTry;
        public int commits;

        void Awake() { var c = GetComponent<BoxCollider>(); c.isTrigger = true; gameObject.layer = GameLayers.Trigger; }

        void OnTriggerStay(Collider other)
        {
            if (Time.time < _nextTry) return;
            var pc = other.GetComponent<Player.PlayerController>();
            if (pc == null) return;
            var cps = CheckpointService.Instance;
            if (cps == null) return;
            // un checkpoint normal se consolida una vez por visita segura; el refugio puede repetirse (garantía idempotente)
            if (!isShelter && cps.LastConfirmed != null && cps.LastConfirmed.checkpointId == checkpointId) return;
            _nextTry = Time.time + retrySeconds;
            if (cps.RequestCheckpoint(checkpointId, pc, regionId, isShelter, guaranteeHp, guaranteePistolTotal, guaranteeShotgunTotal))
            {
                commits++;
                if (isShelter) ObjectiveService.Complete("O09"); // EVT-19: refugio alcanzado
            }
        }
    }
}
