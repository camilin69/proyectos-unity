using UnityEngine;

namespace Dream
{
    // Un patito que nada en el laguito: va y viene en vueltas lentas y desparejas, a ratos se detiene, se mece en el
    // agua (medio cuerpo hundido) y mira hacia donde va.
    public class DuckSwim : MonoBehaviour
    {
        public Vector3 center;
        public float radius = 1f, speed = 0.18f, phase, sink = 0.05f;
        public Vector2 bounds = new Vector2(2.6f, 1.15f);   // semiejes del laguito: nunca se sale del agua

        float _t;

        void Start()
        {
            _t = phase;
        }

        void Update()
        {
            // velocidad que respira: a ratos casi se queda quieto
            float pace = 0.55f + 0.45f * Mathf.Sin(Time.time * 0.21f + phase * 2f);
            _t += Time.deltaTime * speed * pace / Mathf.Max(0.3f, radius);
            float r = radius * (0.8f + 0.2f * Mathf.Sin(_t * 1.7f + phase));
            var p = center + new Vector3(Mathf.Cos(_t) * r * bounds.x / Mathf.Max(bounds.x, bounds.y), 0f, Mathf.Sin(_t) * r * bounds.y / Mathf.Max(bounds.x, bounds.y));
            p.x = center.x + Mathf.Clamp(p.x - center.x, -bounds.x, bounds.x);
            p.z = center.z + Mathf.Clamp(p.z - center.z, -bounds.y, bounds.y);
            var dir = p - transform.position; dir.y = 0f;
            p.y = center.y - sink + Mathf.Sin(Time.time * 1.6f + phase * 3f) * 0.006f;
            transform.position = p;
            if (dir.sqrMagnitude > 1e-7f)
            {
                var want = Quaternion.LookRotation(dir.normalized) * Quaternion.Euler(Mathf.Sin(Time.time * 1.3f + phase) * 2.5f, 0f, Mathf.Sin(Time.time * 0.9f + phase) * 2f);
                transform.rotation = Quaternion.Slerp(transform.rotation, want, 1f - Mathf.Exp(-4f * Time.deltaTime));
            }
        }
    }
}
