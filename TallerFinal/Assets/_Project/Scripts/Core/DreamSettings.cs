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
            get => PlayerPrefs.GetInt(QualityKey, IntegratedGpu ? 1 : 0);
            set { PlayerPrefs.SetInt(QualityKey, value); PlayerPrefs.Save(); QualitySettings.SetQualityLevel(value, true); }
        }
        public static string QualityName => Quality == 0 ? (IntegratedGpu ? "Cine (necesita GPU dedicada)" : "Cine") : "Ligero";

        // Una GPU integrada (Intel HD / UHD / Iris) no aguanta las nubes volumetricas del perfil Cine: Windows la reinicia
        // por tiempo de espera (TDR) y el juego se cierra. Ahi el juego empieza en Ligero.
        public static bool IntegratedGpu
        {
            get
            {
                var n = SystemInfo.graphicsDeviceName ?? "";
                return n.Contains("Intel") && (n.Contains("HD") || n.Contains("UHD") || n.Contains("Iris"));
            }
        }

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
        static void ApplyQuality()
        {
            QualitySettings.SetQualityLevel(Quality, true);
        }

        public static float MouseSensitivity
        {
            get => PlayerPrefs.GetFloat(SensKey, 0.08f);
            set { PlayerPrefs.SetFloat(SensKey, value); PlayerPrefs.Save(); }
        }
    }
}
