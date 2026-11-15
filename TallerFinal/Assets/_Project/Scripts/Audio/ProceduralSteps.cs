using System.Collections.Generic;
using UnityEngine;

namespace Dream.Audio
{
    // Pasos suaves, casi susurros: el pie que roza el pasto, la arena que cede, la moqueta que apaga el golpe. Nada de
    // clics ni golpes secos. Ataque lento (10-25 ms), cola larga y sin agudos: el ruido pasa por dos pasos bajos, asi
    // suena a contacto, no a percusion. La fuente lleva ademas un poco de reverb y eco (BootBuilder).
    public static class ProceduralSteps
    {
        const int Rate = 48000;
        static readonly Dictionary<SurfaceType, AudioClip[]> Cache = new();

        public static AudioClip Pick(SurfaceType s)
        {
            if (!Cache.TryGetValue(s, out var set))
            {
                set = new AudioClip[6];
                for (int i = 0; i < set.Length; i++) set[i] = Make(s, i);
                Cache[s] = set;
            }
            return set[Random.Range(0, set.Length)];
        }

        static AudioClip Make(SurfaceType s, int seed)
        {
            var rng = new System.Random((int)s * 131 + seed * 17 + 5);
            // brillo (frecuencia del paso bajo), duracion y textura por superficie, todo en la zona suave
            float cutoff, len, attack, grainy, thumpGain;
            switch (s)
            {
                case SurfaceType.Grass: case SurfaceType.Leaves: cutoff = 2200f; len = 0.42f; attack = 0.03f; grainy = 0.5f; thumpGain = 0.15f; break;
                case SurfaceType.Sand: cutoff = 1600f; len = 0.38f; attack = 0.025f; grainy = 0.8f; thumpGain = 0.2f; break;
                case SurfaceType.ShallowWater: cutoff = 1300f; len = 0.55f; attack = 0.04f; grainy = 0.2f; thumpGain = 0.1f; break;
                case SurfaceType.Carpet: case SurfaceType.Cloud: cutoff = 700f; len = 0.3f; attack = 0.02f; grainy = 0f; thumpGain = 0.35f; break;
                case SurfaceType.Wood: cutoff = 1200f; len = 0.28f; attack = 0.012f; grainy = 0.1f; thumpGain = 0.45f; break;
                default: cutoff = 1500f; len = 0.26f; attack = 0.01f; grainy = 0.15f; thumpGain = 0.35f; break;   // azulejo, piedra
            }
            cutoff *= 0.85f + (float)rng.NextDouble() * 0.3f;
            int n = (int)(Rate * len);
            var d = new float[n];
            float a1 = 1f - Mathf.Exp(-2f * Mathf.PI * cutoff / Rate);
            float lp1 = 0f, lp2 = 0f, grain = 0f, peak = 0f;
            float thumpHz = 70f + (float)rng.NextDouble() * 25f;
            for (int i = 0; i < n; i++)
            {
                float t = i / (float)Rate;
                float noise = (float)rng.NextDouble() * 2f - 1f;
                if (grainy > 0f) { grain = rng.NextDouble() < 0.03 * grainy ? 1f : grain * 0.992f; noise *= 1f - grainy + grainy * grain; }
                lp1 += (noise - lp1) * a1; lp2 += (lp1 - lp2) * a1;
                float env = Mathf.Clamp01(t / attack) * Mathf.Exp(-(t - attack) * 4.2f / len);
                if (t < attack) env = Mathf.SmoothStep(0f, 1f, t / attack);
                float thump = Mathf.Sin(2f * Mathf.PI * thumpHz * t) * Mathf.Exp(-t * 22f) * Mathf.Clamp01(t / 0.008f) * thumpGain;
                if (s == SurfaceType.ShallowWater)
                    thump += Mathf.Sin(2f * Mathf.PI * (380f + 500f * t) * t) * Mathf.Exp(-Mathf.Pow((t - 0.16f) * 14f, 2f)) * 0.06f;
                d[i] = lp2 * env * 2.2f + thump;
                peak = Mathf.Max(peak, Mathf.Abs(d[i]));
            }
            float norm = 0.5f / Mathf.Max(peak, 1e-4f);
            for (int i = 0; i < n; i++) d[i] *= norm;
            var clip = AudioClip.Create($"Paso_{s}_{seed}", n, 1, Rate, false);
            clip.SetData(d, 0);
            return clip;
        }
    }
}
