using UnityEngine;

namespace Dream
{
    // El viento del sueno: una fuerza lenta con rafagas. La misma senal mece el pasto (WindField) y sube el sonido del
    // viento (MusicPlayer), asi lo que se ve y lo que se oye van juntos.
    public static class Wind
    {
        public static Vector3 Direction = new Vector3(0.8f, 0f, 0.6f).normalized;

        // 0..1: brisa de fondo con rafagas cada 10-25 s
        public static float Strength
        {
            get
            {
                float t = Time.time;
                float baseline = 0.35f + 0.15f * Mathf.Sin(t * 0.11f);
                float gust = Mathf.Pow(Mathf.PerlinNoise(t * 0.06f, 7.3f), 2.2f) * 1.4f;
                return Mathf.Clamp01(baseline + gust * 0.6f);
            }
        }
    }
}
