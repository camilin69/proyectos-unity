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
