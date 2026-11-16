using UnityEngine;

namespace Dream
{
    // Un patito que nada en el laguito: va y viene en vueltas lentas y desparejas, a ratos se detiene, se mece en el
    // agua (medio cuerpo hundido) y mira hacia donde va. De vez en cuando hace cuac.
    public class DuckSwim : MonoBehaviour
    {
        public Vector3 center;
        public float radius = 1f, speed = 0.18f, phase, sink = 0.05f;
        public Vector2 bounds = new Vector2(2.6f, 1.15f);   // semiejes del laguito: nunca se sale del agua

        float _t, _nextQuack;
        AudioSource _voice;
        static AudioClip[] _quacks;

        void Start()
        {
            _t = phase;
            _voice = gameObject.AddComponent<AudioSource>();
            _voice.spatialBlend = 1f; _voice.minDistance = 1.5f; _voice.maxDistance = 22f; _voice.rolloffMode = AudioRolloffMode.Linear;
            _voice.playOnAwake = false; _voice.volume = 0.55f;
            _nextQuack = Time.time + 2f + phase * 2.3f;
            if (_quacks == null) _quacks = new[] { Quack(1f, 2), Quack(1.08f, 3), Quack(0.94f, 1) };
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
            if (Time.time > _nextQuack && _voice)
            {
                _voice.pitch = Random.Range(0.92f, 1.1f);
                _voice.PlayOneShot(_quacks[Random.Range(0, _quacks.Length)]);
                _nextQuack = Time.time + Random.Range(5f, 14f);
            }
        }

        // Cuac sintetizado: una voz nasal (diente de sierra con formantes) que cae de tono, repetida 1-3 veces.
        static AudioClip Quack(float pitch, int times)
        {
            const int rate = 44100;
            float one = 0.17f, gap = 0.07f;
            int n = (int)(rate * (times * (one + gap) + 0.05f));
            var data = new float[n];
            float ph = 0f, b1 = 0f, b2 = 0f, l1 = 0f, l2 = 0f;
            for (int i = 0; i < n; i++)
            {
                float t = i / (float)rate;
                float k = t % (one + gap);
                if (k > one) { data[i] = 0f; continue; }
                float env = Mathf.Sin(Mathf.PI * Mathf.Clamp01(k / one)) * Mathf.Exp(-k * 6f);
                float f0 = pitch * Mathf.Lerp(480f, 330f, k / one) * (1f - 0.08f * Mathf.Floor(t / (one + gap)));
                ph += f0 / rate; ph -= Mathf.Floor(ph);
                float saw = ph * 2f - 1f;
                // dos resonancias (nasal): ~1100 Hz y ~2600 Hz
                b1 += (saw - b1) * 0.16f; l1 += (b1 - l1) * 0.16f;
                b2 += (saw - b2) * 0.36f; l2 += (b2 - l2) * 0.36f;
                float v = (b1 - l1) * 1.6f + (b2 - l2) * 0.9f;
                data[i] = Mathf.Clamp(v * env * 1.4f, -1f, 1f);
            }
            var clip = AudioClip.Create("Cuac", n, 1, rate, false);
            clip.SetData(data, 0);
            return clip;
        }
    }
}
