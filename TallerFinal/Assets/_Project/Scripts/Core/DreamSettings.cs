using UnityEngine;

namespace Dream
{
    // Preferencias del jugador que sobreviven entre partidas.
    public static class DreamSettings
    {
        const string SwayKey = "sueno.sway", SensKey = "sueno.sens";

        public static SwayMode Sway
        {
            get => (SwayMode)PlayerPrefs.GetInt(SwayKey, (int)SwayMode.Completo);
            set { PlayerPrefs.SetInt(SwayKey, (int)value); PlayerPrefs.Save(); }
        }

        public static float SwayScale => Sway switch { SwayMode.Completo => 1f, SwayMode.Suave => 0.45f, _ => 0f };

        public static float MouseSensitivity
        {
            get => PlayerPrefs.GetFloat(SensKey, 0.08f);
            set { PlayerPrefs.SetFloat(SensKey, value); PlayerPrefs.Save(); }
        }
    }
}
