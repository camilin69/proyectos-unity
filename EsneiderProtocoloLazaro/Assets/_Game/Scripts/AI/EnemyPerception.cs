using Esneider.Core;
using Esneider.Core.Data;
using UnityEngine;

namespace Esneider.AI
{
    // Sección 14/78.1: visión con raycast a torso y cabeza, acumulación de sospecha, oscuridad, indicio de linterna y oído con oclusión.
    public class EnemyPerception : MonoBehaviour
    {
        public EnemyDefinition definition;
        public Transform sensor; // cabeza
        public Transform target; // jugador
        public bool alertMode;
        public float suspicion;           // umbral 1.0 confirma
        public bool Confirmed => suspicion >= 1f;
        public bool HasIndicio => suspicion > 0.05f || Time.time - lastHeardTime < 1f;
        public Vector3 lastKnownPosition;
        public float lastSeenTime = -999f, lastHeardTime = -999f, lastKnownTime = -999f;
        public bool SeesTarget { get; private set; }
        public static bool PlayerInDarkness = false; // volúmenes de visibilidad (14): baseline sandbox iluminado
        public Light targetFlashlight;
        public float updateHz = 10f;
        float _nextUpdate;

        void OnEnable() { NoiseSystem.Emitted += OnNoise; }
        void OnDisable() { NoiseSystem.Emitted -= OnNoise; }

        void Update()
        {
            if (Time.time < _nextUpdate) return;
            float dt = 1f / updateHz; _nextUpdate = Time.time + dt;
            Sense(dt);
        }

        public void Sense(float dt)
        {
            SeesTarget = false;
            if (target == null || definition == null) return;
            var s = sensor != null ? sensor.position : transform.position + Vector3.up * 1.2f;
            var torso = target.position + Vector3.up * 1.2f; var head = target.position + Vector3.up * 1.6f;
            var to = torso - s; float dist = to.magnitude;
            float range = alertMode ? definition.visionRangeAlert : definition.visionRangeLit;
            float angle = alertMode ? definition.visionAngleAlert : definition.visionAngleLit;
            if (PlayerInDarkness) range = Mathf.Min(range, alertMode ? definition.visionRangeDarkAlert : definition.visionRangeDark);
            float rate = 0f;
            bool inCone = dist <= range && Vector3.Angle(new Vector3(transform.forward.x, 0, transform.forward.z), new Vector3(to.x, 0, to.z)) <= angle / 2f;
            bool los = false;
            if (inCone || dist < definition.closeRange) los = !Blocked(s, torso) || !Blocked(s, head);
            if (los && (inCone || dist < definition.closeRange))
            {
                SeesTarget = true;
                rate = dist < definition.closeRange ? 1f / definition.closeReaction : 1f / 1.2f;
            }
            else if (targetFlashlight != null && targetFlashlight.enabled && dist <= 14f && !Blocked(s, torso))
            {
                // linterna dirigida al sensor: indicio, sin confirmación instantánea
                float a = Vector3.Angle(targetFlashlight.transform.forward, s - targetFlashlight.transform.position);
                if (a < 15f) rate = 0.25f;
            }
            if (rate > 0f)
            {
                suspicion = Mathf.Min(1.5f, suspicion + rate * dt);
                if (SeesTarget) { lastSeenTime = Time.time; lastKnownPosition = target.position; lastKnownTime = Time.time; }
            }
            else suspicion = Mathf.Max(0f, suspicion - 0.5f * dt);
        }

        bool Blocked(Vector3 from, Vector3 to)
        {
            var d = to - from; float len = d.magnitude;
            return len > 0.01f && Physics.Raycast(from, d / len, len, GameLayers.VisionBlockMask, QueryTriggerInteraction.Ignore);
        }

        void OnNoise(NoiseEvent e)
        {
            if (e.source == gameObject || target == null) return;
            if (e.source != target.gameObject && !(e.kind == "prop-impact" || e.kind == "door")) return;
            var listener = sensor != null ? sensor.position : transform.position;
            float eff = NoiseSystem.EffectiveRadius(e, listener);
            if (eff <= 0f || Vector3.Distance(e.position, listener) > eff) return;
            // 78.2: un nuevo ruido reemplaza solo si es más prioritario (mayor radio) o claramente más próximo
            bool newer = Time.time - lastHeardTime > 1.5f || e.radius >= _lastHeardRadius || Vector3.Distance(e.position, transform.position) < Vector3.Distance(lastKnownPosition, transform.position) * 0.7f;
            if (!newer) return;
            lastHeardTime = Time.time; _lastHeardRadius = e.radius; lastKnownPosition = e.position; lastKnownTime = Time.time;
            heardRecently = true;
        }
        float _lastHeardRadius;
        public bool heardRecently;

        // Daño recibido confirma agresor si su posición es conocida por el impacto (78.1).
        public void OnDamaged(DamageInfo info)
        {
            if (info.source != null) { lastKnownPosition = info.source.transform.position; lastKnownTime = Time.time; suspicion = 1f; }
        }
    }
}
