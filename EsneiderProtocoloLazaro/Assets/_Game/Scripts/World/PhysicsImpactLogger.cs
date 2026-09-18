using Esneider.Core;
using UnityEngine;

namespace Esneider.World
{
    // 20.3/25: colisión por código en prop dinámico; consecuencia observable (ruido para robots + contador).
    [RequireComponent(typeof(Rigidbody))]
    public class PhysicsImpactLogger : MonoBehaviour
    {
        public float minImpactSpeed = 1.5f;
        public float noiseRadius = 10f;
        public float cooldown = 0.5f;
        public int impacts;
        float _last = -10f;

        void OnCollisionEnter(Collision c)
        {
            if (c.relativeVelocity.magnitude < minImpactSpeed || Time.time - _last < cooldown) return;
            _last = Time.time; impacts++;
            NoiseSystem.Emit(transform.position, noiseRadius, gameObject, "prop-impact");
            if (GameFlowController.Instance != null) GameFlowController.Instance.physicsImpacts++;
            Debug.Log($"Impacto físico #{impacts}: {name} contra {c.collider.name} a {c.relativeVelocity.magnitude:F1} m/s");
        }
    }
}
