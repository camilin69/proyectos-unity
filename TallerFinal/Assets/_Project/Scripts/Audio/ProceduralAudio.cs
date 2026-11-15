using UnityEngine;

namespace Dream.Audio
{
    // Sonidos sintetizados para lo que no necesita grabacion: la campanilla del recuerdo (parciales de campana con
    // caida exponencial) y un zumbido de luz que crece. Asi el juego suena aunque falten los archivos grabados.
    public static class ProceduralAudio
    {
        const int Rate = 48000;

        public static AudioClip Chime()
        {
            float len = 3.2f;
            int n = (int)(Rate * len);
            var data = new float[n];
            float[] partials = { 1f, 2.76f, 5.40f, 8.93f, 13.34f };
            float[] amps = { 0.55f, 0.28f, 0.16f, 0.09f, 0.05f };
            float[] decay = { 1.2f, 1.9f, 2.8f, 3.9f, 5.2f };
            float f0 = 880f;
            for (int i = 0; i < n; i++)
            {
                float t = i / (float)Rate, s = 0f;
                for (int p = 0; p < partials.Length; p++)
                    s += amps[p] * Mathf.Sin(2f * Mathf.PI * f0 * partials[p] * t) * Mathf.Exp(-decay[p] * t);
                // segunda campana una quinta arriba, un poco despues: suena a recuerdo, no a alarma
                float t2 = t - 0.18f;
                if (t2 > 0f) s += 0.35f * Mathf.Sin(2f * Mathf.PI * f0 * 1.5f * t2) * Mathf.Exp(-1.6f * t2);
                float attack = Mathf.Clamp01(t / 0.004f);
                data[i] = s * attack * 0.45f;
            }
            var clip = AudioClip.Create("Chime", n, 1, Rate, false);
            clip.SetData(data, 0);
            return clip;
        }

        static readonly System.Collections.Generic.Dictionary<AmbienceKind, AudioClip> _amb = new();

        public static AudioClip Ambience(AmbienceKind k)
        {
            if (k == AmbienceKind.Ninguno) return null;
            if (_amb.TryGetValue(k, out var c)) return c;
            c = k switch
            {
                AmbienceKind.Mar => Sea(36f),
                AmbienceKind.VientoAlto => WindNoise(32f, 900f, 0.9f),
                AmbienceKind.NocheSuave => WindNoise(32f, 420f, 0.45f),
                _ => WindNoise(32f, 650f, 0.7f),
            };
            _amb[k] = c;
            return c;
        }

        // Viento: ruido marron filtrado con un silbido suave que sube en las rafagas. Bucle sin costura: los extremos se
        // funden entre si.
        static AudioClip WindNoise(float seconds, float brightness, float gain)
        {
            int n = (int)(Rate * seconds);
            var d = new float[n];
            var rng = new System.Random(11);
            float brown = 0f, lp = 0f, bp = 0f, a = 1f - Mathf.Exp(-2f * Mathf.PI * brightness / Rate);
            for (int i = 0; i < n; i++)
            {
                float t = i / (float)Rate;
                float w = (float)rng.NextDouble() * 2f - 1f;
                brown = Mathf.Clamp(brown * 0.997f + w * 0.03f, -1f, 1f);
                lp += (w - lp) * a; bp += (lp - bp) * a * 0.5f;
                float gust = 0.45f + 0.55f * Mathf.Pow(0.5f + 0.5f * Mathf.Sin(2f * Mathf.PI * t / seconds * 3f + Mathf.Sin(t * 0.37f)), 2f);
                d[i] = (brown * 0.8f + (lp - bp) * 0.6f * gust) * gust * gain;
            }
            return Seamless("Viento", d, n);
        }

        // Mar: oleaje lento (una ola cada ~9 s) con la espuma que se arrastra por la arena.
        static AudioClip Sea(float seconds)
        {
            int n = (int)(Rate * seconds);
            var d = new float[n];
            var rng = new System.Random(23);
            float lp = 0f, lp2 = 0f, hiss = 0f;
            float a = 1f - Mathf.Exp(-2f * Mathf.PI * 500f / Rate), ah = 1f - Mathf.Exp(-2f * Mathf.PI * 3500f / Rate);
            for (int i = 0; i < n; i++)
            {
                float t = i / (float)Rate;
                float w = (float)rng.NextDouble() * 2f - 1f;
                lp += (w - lp) * a; lp2 += (lp - lp2) * a; hiss += (w - hiss) * ah;
                float wave = t % 9f / 9f;                                   // fase de la ola
                float swell = Mathf.Pow(Mathf.Sin(Mathf.PI * Mathf.Clamp01(wave / 0.45f)), 2f);
                float foam = wave > 0.35f ? Mathf.Exp(-(wave - 0.35f) * 5f) * Mathf.Clamp01((wave - 0.35f) * 20f) : 0f;
                d[i] = lp2 * 3.2f * (0.25f + swell) + (hiss - lp) * 0.35f * foam;
            }
            return Seamless("Mar", d, n);
        }

        static AudioClip Seamless(string name, float[] d, int n)
        {
            int fade = Rate * 2;
            for (int i = 0; i < fade; i++)
            {
                float k = i / (float)fade;
                d[i] = d[i] * Mathf.Sin(k * Mathf.PI * 0.5f) + d[n - fade + i] * Mathf.Cos(k * Mathf.PI * 0.5f);
            }
            var outData = new float[n - fade];
            System.Array.Copy(d, 0, outData, 0, n - fade);
            float peak = 0f; foreach (var v in outData) peak = Mathf.Max(peak, Mathf.Abs(v));
            for (int i = 0; i < outData.Length; i++) outData[i] *= 0.6f / Mathf.Max(peak, 1e-4f);
            var clip = AudioClip.Create(name, outData.Length, 1, Rate, false);
            clip.SetData(outData, 0);
            return clip;
        }

        public static AudioClip LightHum(float seconds = 6f)
        {
            int n = (int)(Rate * seconds);
            var data = new float[n];
            for (int i = 0; i < n; i++)
            {
                float t = i / (float)Rate, k = t / seconds;
                float s = Mathf.Sin(2f * Mathf.PI * 110f * t) * 0.4f + Mathf.Sin(2f * Mathf.PI * 220.5f * t) * 0.25f
                        + Mathf.Sin(2f * Mathf.PI * 330.8f * t) * 0.15f * k;
                data[i] = s * k * k * 0.5f;
            }
            var clip = AudioClip.Create("LightHum", n, 1, Rate, false);
            clip.SetData(data, 0);
            return clip;
        }
    }
}
