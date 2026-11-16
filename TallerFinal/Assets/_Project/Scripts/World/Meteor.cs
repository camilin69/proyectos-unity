using System.Collections;
using UnityEngine;

namespace Dream
{
    // El meteorito de la escalera al cielo: un cuerpo en llamas, de tamano planetario, que se acerca a medida que el
    // sonador sube. Avanza con el punto mas alto que haya alcanzado: si el sonador baja, el meteorito se queda donde
    // estaba pero sigue girando, como si siguiera viniendo. Arriba, cuando la ultima puerta se abre, cae de verdad:
    // llena el cielo, la tierra tiembla y la luz lo blanquea todo.
    [DefaultExecutionOrder(32000)]          // despues de las camaras: el temblor se suma a donde ya esten
    public class Meteor : MonoBehaviour
    {
        public Transform body, halo;
        public float stairStartZ, stairEndZ;
        public Vector3 farPosition, nearPosition, impactPosition;
        public float farRadius = 260f, nearRadius = 1100f, impactRadius = 2300f;
        public float spinDegPerSec = 6f;
        public AudioSource rumble;
        public Light glowLight;                 // luz anaranjada que baja del meteorito y crece al acercarse
        public float glowFar = 0.5f, glowNear = 18f, glowImpact = 220f;

        float _progress, _shown, _impact, _quake;
        readonly Vector3 _spinAxis = new Vector3(0.3f, 1f, 0.2f).normalized;

        void Start()
        {
            if (!rumble) return;
            // retumbo grave: ruido marron filtrado, en bucle; el volumen lo sube la cercania
            const int rate = 44100, n = rate * 4;
            var data = new float[n];
            float b = 0f, lp = 0f;
            var rng = new System.Random(5);
            for (int i = 0; i < n; i++)
            {
                b = Mathf.Clamp(b + ((float)rng.NextDouble() * 2f - 1f) * 0.02f, -1f, 1f);
                lp += (b - lp) * 0.03f;
                data[i] = lp * 2.2f;
            }
            for (int i = 0; i < 2000; i++) { float f = i / 2000f; data[i] *= f; data[n - 1 - i] *= f; }
            var clip = AudioClip.Create("Retumbo", n, 1, rate, false);
            clip.SetData(data, 0);
            rumble.clip = clip; rumble.loop = true; rumble.volume = 0f; rumble.Play();
        }

        void Update()
        {
            var rig = PlayerRig.Instance;
            if (rig != null)
            {
                float p = Mathf.InverseLerp(stairStartZ, stairEndZ, rig.transform.position.z);
                _progress = Mathf.Max(_progress, p);                                  // si retrocede, se queda
            }
            _shown = Mathf.MoveTowards(_shown, _progress, Time.deltaTime * 0.08f);
            float k = Mathf.SmoothStep(0f, 1f, _shown);
            var pos = Vector3.Lerp(farPosition, nearPosition, k);
            float r = Mathf.Lerp(farRadius, nearRadius, k * k);
            if (_impact > 0f)
            {
                float e = _impact * _impact;
                pos = Vector3.Lerp(pos, impactPosition, e);
                r = Mathf.Lerp(r, impactRadius, e);
            }
            transform.position = pos;
            if (body)
            {
                body.localScale = Vector3.one * r * 2f;
                body.Rotate(_spinAxis, spinDegPerSec * Time.deltaTime, Space.World);  // siempre gira, aunque no avance
            }
            var cam = Camera.main;
            if (halo && cam)
            {
                halo.rotation = Quaternion.LookRotation(halo.position - cam.transform.position);
                halo.localScale = Vector3.one * r * 5.5f;
            }
            if (rumble) rumble.volume = Mathf.Lerp(0.15f * k, 1f, _impact);
            if (glowLight)
            {
                glowLight.intensity = Mathf.Lerp(Mathf.Lerp(glowFar, glowNear, k), glowImpact, _impact * _impact);
                if (cam) glowLight.transform.rotation = Quaternion.LookRotation(cam.transform.position - transform.position);
            }
        }

        void LateUpdate()
        {
            if (_quake <= 0f) return;
            var cam = Camera.main;
            if (!cam) return;
            float t = Time.time * 28f;
            var off = new Vector3(Mathf.PerlinNoise(t, 0f) - 0.5f, Mathf.PerlinNoise(0f, t) - 0.5f, Mathf.PerlinNoise(t, t) - 0.5f) * (0.22f * _quake);
            cam.transform.position += off;
            cam.transform.rotation *= Quaternion.Euler(off.y * 6f, off.x * 6f, off.z * 9f);
        }

        // La ultima puerta: el meteorito cae (dura lo que la cinematica de salida, ~8 s).
        public void Impact() => StartCoroutine(ImpactRoutine());

        IEnumerator ImpactRoutine()
        {
            _progress = 1f;
            for (float t = 0f; t < 8f; t += Time.deltaTime)
            {
                _impact = Mathf.Clamp01(t / 7.5f);
                _quake = Mathf.SmoothStep(0f, 1f, Mathf.Clamp01(t / 2.5f)) * (1f + 0.6f * _impact);
                yield return null;
            }
            for (float t = 0f; t < 2f; t += Time.deltaTime) { _quake = 1.6f * (1f - t / 2f); yield return null; }
            _quake = 0f;
        }
    }
}
