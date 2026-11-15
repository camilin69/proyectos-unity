using System.Collections.Generic;
using UnityEngine;

namespace Dream.Audio
{
    // Pasos sintetizados por superficie, para cuando un banco no tiene grabaciones. Cada paso es un golpe grave
    // (el peso del pie) mas una textura propia de la superficie: clic seco en azulejo, crujido de granos en arena,
    // roce de hojas en pasto, chapoteo en agua, golpe sordo en moqueta, resonancia de madera.
    public static class ProceduralSteps
    {
        const int Rate = 48000;
        static readonly Dictionary<SurfaceType, AudioClip[]> Cache = new();

        public static AudioClip Pick(SurfaceType s)
        {
            if (!Cache.TryGetValue(s, out var set))
            {
                set = new AudioClip[5];
                for (int i = 0; i < set.Length; i++) set[i] = Make(s, i);
                Cache[s] = set;
            }
            return set[Random.Range(0, set.Length)];
        }

        static AudioClip Make(SurfaceType s, int seed)
        {
            var rng = new System.Random((int)s * 101 + seed * 7 + 3);
            float len = s switch { SurfaceType.ShallowWater => 0.45f, SurfaceType.Grass or SurfaceType.Leaves or SurfaceType.Sand => 0.32f, _ => 0.22f };
            int n = (int)(Rate * len);
            var d = new float[n];
            float lp = 0f, lp2 = 0f, hpPrev = 0f, hpOut = 0f;
            float thumpHz = s switch { SurfaceType.Wood => 150f, SurfaceType.Carpet => 70f, SurfaceType.Cloud => 55f, _ => 95f } * (0.9f + (float)rng.NextDouble() * 0.2f);
            float grain = 0f;
            for (int i = 0; i < n; i++)
            {
                float t = i / (float)Rate;
                float noise = (float)rng.NextDouble() * 2f - 1f;
                // golpe grave del pie
                float thump = Mathf.Sin(2f * Mathf.PI * thumpHz * t) * Mathf.Exp(-t * 38f) * 0.55f;
                float tex = 0f;
                switch (s)
                {
                    case SurfaceType.Stone:
                    case SurfaceType.WetTile:
                        hpOut = 0.92f * (hpOut + noise - hpPrev); hpPrev = noise;          // pasa altos: clic
                        tex = hpOut * Mathf.Exp(-t * 90f) * 0.6f;
                        if (s == SurfaceType.WetTile) { lp += (noise - lp) * 0.25f; tex += lp * Mathf.Exp(-(t - 0.02f) * (t - 0.02f) * 900f) * 0.35f; }
                        break;
                    case SurfaceType.Grass:
                    case SurfaceType.Leaves:
                        lp += (noise - lp) * 0.45f; hpOut = 0.8f * (hpOut + lp - hpPrev); hpPrev = lp;
                        grain = rng.NextDouble() < 0.02 ? 1f : grain * 0.995f;
                        tex = hpOut * (0.35f + grain * 0.65f) * Mathf.Exp(-t * 11f) * Mathf.Clamp01(t * 60f) * 0.7f;
                        thump *= 0.45f;
                        break;
                    case SurfaceType.Sand:
                        grain = rng.NextDouble() < 0.06 ? (float)rng.NextDouble() : grain * 0.9f;
                        lp += (noise * grain - lp) * 0.35f;
                        tex = lp * Mathf.Exp(-t * 9f) * Mathf.Clamp01(t * 40f) * 1.6f;
                        thump *= 0.5f;
                        break;
                    case SurfaceType.ShallowWater:
                        lp += (noise - lp) * 0.12f; lp2 += (lp - lp2) * 0.3f;
                        float env = Mathf.Clamp01(t * 25f) * Mathf.Exp(-t * 7f);
                        float bubble = Mathf.Sin(2f * Mathf.PI * (600f + 900f * t) * t) * Mathf.Exp(-((t - 0.12f) * (t - 0.12f)) * 600f) * 0.15f;
                        tex = (lp2 * 1.4f) * env + bubble;
                        thump *= 0.3f;
                        break;
                    case SurfaceType.Carpet:
                        lp += (noise - lp) * 0.05f;
                        tex = lp * Mathf.Exp(-t * 30f) * 0.8f;
                        break;
                    case SurfaceType.Wood:
                        tex = (Mathf.Sin(2f * Mathf.PI * 320f * t) * 0.3f + Mathf.Sin(2f * Mathf.PI * 517f * t) * 0.15f) * Mathf.Exp(-t * 45f)
                              + noise * Mathf.Exp(-t * 200f) * 0.25f;
                        break;
                    case SurfaceType.Cloud:
                        lp += (noise - lp) * 0.08f;
                        tex = lp * Mathf.Sin(Mathf.PI * Mathf.Clamp01(t / len)) * 0.5f;
                        thump *= 0.15f;
                        break;
                }
                d[i] = (thump + tex) * 0.8f;
            }
            var clip = AudioClip.Create($"Paso_{s}_{seed}", n, 1, Rate, false);
            clip.SetData(d, 0);
            return clip;
        }
    }
}
