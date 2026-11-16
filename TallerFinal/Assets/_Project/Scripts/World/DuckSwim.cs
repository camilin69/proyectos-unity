using UnityEngine;

namespace Dream
{
    // Un patito que nada en el laguito: da vueltas lentas y desparejas alrededor del centro, se mece sobre el agua y
    // mira hacia donde va.
    public class DuckSwim : MonoBehaviour
    {
        public Vector3 center;
        public float radius = 1f, speed = 0.18f, phase;
        float _r;

        void Start() => _r = radius;

        void Update()
        {
            float t = Time.time * speed / Mathf.Max(0.2f, radius) + phase;
            float r = _r * (0.75f + 0.25f * Mathf.Sin(t * 1.7f + phase));
            var p = center + new Vector3(Mathf.Cos(t) * r, 0f, Mathf.Sin(t) * r);
            var dir = p - transform.position; dir.y = 0f;
            p.y = center.y + Mathf.Sin(Time.time * 1.6f + phase * 3f) * 0.008f;
            transform.position = p;
            if (dir.sqrMagnitude > 1e-6f)
                transform.rotation = Quaternion.LookRotation(dir.normalized) * Quaternion.Euler(Mathf.Sin(Time.time * 1.3f + phase) * 3f, 0f, 0f);
        }
    }
}
