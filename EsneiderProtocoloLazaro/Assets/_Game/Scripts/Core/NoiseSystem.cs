using System;
using UnityEngine;

namespace Esneider.Core
{
    public struct NoiseEvent
    {
        public Vector3 position;
        public float radius;
        public GameObject source;
        public string kind;
        public float time;
    }

    // Sección 14/78.1: ruido lógico de gameplay, independiente del volumen del usuario.
    public static class NoiseSystem
    {
        public static event Action<NoiseEvent> Emitted;

        public static void Emit(Vector3 position, float radius, GameObject source, string kind)
        {
            if (radius <= 0f) return;
            Emitted?.Invoke(new NoiseEvent { position = position, radius = radius, source = source, kind = kind, time = Time.time });
        }

        // 78.1: puerta sólida cerrada reduce el radio efectivo al 35%; pared completa impide propagación directa.
        public static float EffectiveRadius(NoiseEvent e, Vector3 listener)
        {
            var dir = listener - e.position; float dist = dir.magnitude;
            if (dist < 0.01f) return e.radius;
            int hits = Physics.RaycastNonAlloc(e.position, dir / dist, _buffer, dist, GameLayers.VisionBlockMask, QueryTriggerInteraction.Ignore);
            if (hits == 0) return e.radius;
            if (hits == _buffer.Length) return 0f; // Never infer a clear path from truncated obstruction data.
            for (int i = 0; i < hits; i++)
                if (_buffer[i].collider.GetComponentInParent<World.Door>() == null) return 0f;
            return e.radius * 0.35f;
        }

        static readonly RaycastHit[] _buffer = new RaycastHit[8];
    }
}
