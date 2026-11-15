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

        // Calidad: 0 = Cine (HDRP High Fidelity, para la GPU dedicada de la presentacion), 1 = Ligero (Balanced).
        const string QualityKey = "sueno.calidad";
        public static int Quality
        {
            get => PlayerPrefs.GetInt(QualityKey, QualitySettings.GetQualityLevel() == 0 ? 0 : 1);
            set { PlayerPrefs.SetInt(QualityKey, value); PlayerPrefs.Save(); QualitySettings.SetQualityLevel(value, true); }
        }
        public static string QualityName => Quality == 0 ? "Cine" : "Ligero";

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
        static void ApplyQuality()
        {
            if (PlayerPrefs.HasKey(QualityKey)) QualitySettings.SetQualityLevel(PlayerPrefs.GetInt(QualityKey), true);
        }

        public static float MouseSensitivity
        {
            get => PlayerPrefs.GetFloat(SensKey, 0.08f);
            set { PlayerPrefs.SetFloat(SensKey, value); PlayerPrefs.Save(); }
        }
    }
}
