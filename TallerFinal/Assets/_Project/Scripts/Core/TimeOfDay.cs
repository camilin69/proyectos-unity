using UnityEngine;

namespace Dream
{
    // El cielo cambia contigo: la hora del sueno mueve el sol y la luna del Physically Based Sky.
    // Unidades fisicas: el sol en lux (hasta ~110 000 al mediodia) y temperatura de color en kelvin, de
    // 2 000 K a ras del horizonte a 5 800 K arriba. La exposicion automatica de HDRP hace el resto.
    [ExecuteAlways]
    public class TimeOfDay : MonoBehaviour
    {
        public static TimeOfDay Instance { get; private set; }

        [Range(0f, 24f)] public float hour = 7f;
        public Light sun, moon;
        public float sunrise = 6f, sunset = 18.5f, maxElevation = 64f;
        public float noonLux = 110000f, moonLux = 2.5f;

        float _target = -1f, _rate;

        void OnEnable() => Instance = this;
        void OnDisable() { if (Instance == this) Instance = null; }

        // Lleva la hora a h en 'seconds'. Con seconds = 0 salta (el hueco del arbol: 12:00 -> 20:00 a oscuras).
        public void GoTo(float h, float seconds)
        {
            if (seconds <= 0f) { hour = h; _target = -1f; Apply(); return; }
            _target = h; _rate = Mathf.Abs(h - hour) / seconds;
        }

        public bool IsNight => SunElevation(hour, sunrise, sunset, maxElevation) < -4f;

        public static string Format(float h)
        {
            h = Mathf.Repeat(h, 24f);
            int hh = Mathf.FloorToInt(h), mm = Mathf.FloorToInt((h - hh) * 60f);
            return $"{hh:00}:{mm:00}";
        }

        void Update()
        {
            if (_target >= 0f && Application.isPlaying)
            {
                hour = Mathf.MoveTowards(hour, _target, _rate * Time.deltaTime);
                if (Mathf.Approximately(hour, _target)) _target = -1f;
            }
            Apply();
        }

        // Elevacion del sol en grados. De dia sigue un arco; de noche cae bajo el horizonte y vuelve antes del alba.
        public static float SunElevation(float h, float rise, float set, float maxElev)
        {
            h = Mathf.Repeat(h, 24f);
            if (h >= rise && h <= set) return maxElev * Mathf.Sin(Mathf.PI * (h - rise) / (set - rise));
            float nightLen = 24f - (set - rise);
            float n = Mathf.Repeat(h - set, 24f) / nightLen;          // 0 al ocaso, 1 al alba
            return -40f * Mathf.Sin(Mathf.PI * n);
        }

        public void Apply()
        {
            float elev = SunElevation(hour, sunrise, sunset, maxElevation);
            float t = Mathf.Clamp01((Mathf.Repeat(hour, 24f) - sunrise) / (sunset - sunrise));
            float az = Mathf.Lerp(80f, 280f, t);
            if (sun)
            {
                sun.transform.rotation = Quaternion.Euler(Mathf.Max(elev, -8f), az, 0f);
                float up = Mathf.Clamp01(Mathf.Sin(elev * Mathf.Deg2Rad));
                sun.enabled = elev > -4f;
                sun.intensity = Mathf.Lerp(400f, noonLux, Mathf.Pow(up, 0.75f)) * Mathf.Clamp01((elev + 4f) / 6f);
                sun.useColorTemperature = true;
                sun.colorTemperature = Mathf.Lerp(2000f, 5800f, Mathf.Pow(up, 0.5f));
            }
            if (moon)
            {
                float night = Mathf.Clamp01((-elev - 2f) / 8f);
                moon.enabled = night > 0.001f;
                float mh = Mathf.Repeat(hour - 18f, 24f) / 12f;            // 18:00 -> 0, 06:00 -> 1
                moon.transform.rotation = Quaternion.Euler(Mathf.Lerp(18f, 52f, Mathf.Sin(Mathf.PI * Mathf.Clamp01(mh))), 150f + 60f * mh, 0f);
                moon.intensity = moonLux * night;
                moon.useColorTemperature = true;
                moon.colorTemperature = 8200f;
            }
        }
    }
}
