using UnityEngine;

namespace Esneider.Core
{
    // 80.3/81.3: ajustes persistentes fuera del snapshot de campaña (PlayerPrefs). La asistencia es explícita y nunca cambia sola:
    // telegraphs +25 %, daño de rayos −20 %. Dificultad normal = 90 HP y rayo de 30.
    public static class AccessibilitySettings
    {
        public static bool Assist { get; private set; }
        public static float Sensitivity = 0.12f, Fov = 75f, TextScale = 1f, MasterVolume = 1f;
        public static bool InvertY, Subtitles = true, HeadBob = true;
        public static bool Fullscreen;
        public static float TelegraphScale => Assist ? 1.25f : 1f;
        public static float RayDamageScale => Assist ? 0.8f : 1f;

        public static void SetAssist(bool on) { Assist = on; }

        public static void Load()
        {
            Fullscreen = PlayerPrefs.GetInt("esn.borderless", 0) == 1;
            Assist = PlayerPrefs.GetInt("esn.assist", 0) == 1; Sensitivity = PlayerPrefs.GetFloat("esn.sens", 0.12f); Fov = PlayerPrefs.GetFloat("esn.fov", 75f);
            TextScale = PlayerPrefs.GetFloat("esn.text", 1f); MasterVolume = PlayerPrefs.GetFloat("esn.vol", 1f); InvertY = PlayerPrefs.GetInt("esn.inv", 0) == 1;
            Subtitles = PlayerPrefs.GetInt("esn.subs", 1) == 1; HeadBob = PlayerPrefs.GetInt("esn.bob", 1) == 1;
        }

        public static void Save()
        {
            PlayerPrefs.SetInt("esn.borderless", Fullscreen ? 1 : 0);
            PlayerPrefs.SetInt("esn.assist", Assist ? 1 : 0); PlayerPrefs.SetFloat("esn.sens", Sensitivity); PlayerPrefs.SetFloat("esn.fov", Fov); PlayerPrefs.SetFloat("esn.text", TextScale);
            PlayerPrefs.SetFloat("esn.vol", MasterVolume); PlayerPrefs.SetInt("esn.inv", InvertY ? 1 : 0); PlayerPrefs.SetInt("esn.subs", Subtitles ? 1 : 0); PlayerPrefs.SetInt("esn.bob", HeadBob ? 1 : 0);
            PlayerPrefs.Save();
        }

        public static void ApplyDisplay()
        {
            // The editor Game view and automated probes own their own dimensions.
            if (Application.isEditor || System.Array.IndexOf(System.Environment.GetCommandLineArgs(), "-autotest") >= 0) return;
            var mode = Fullscreen ? FullScreenMode.FullScreenWindow : FullScreenMode.Windowed;
            if (Screen.fullScreenMode == mode) return;
            var desktop = Screen.currentResolution;
            int width = Fullscreen ? desktop.width : Mathf.Min(1280, Mathf.RoundToInt(desktop.width * .85f));
            int height = Fullscreen ? desktop.height : Mathf.Min(720, Mathf.RoundToInt(desktop.height * .85f));
            Screen.SetResolution(width, height, mode);
        }
    }
}
