using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Esneider.EditorTools
{
    // Captura de evidencia (106): abre una escena, entra en Play, espera N segundos y guarda la Game View en docs/produccion/evidencia/<label>.png.
    // Sobrevive al domain reload de Play Mode mediante EditorPrefs; al terminar sale de Play y escribe <label>.done.
    [InitializeOnLoad]
    public static class EvidenceCapture
    {
        const string KeyLabel = "esn.evidence.label", KeyDelay = "esn.evidence.delay", KeyTeleport = "esn.evidence.teleport";
        static double _startedAt; static bool _captured; static string _path;

        static EvidenceCapture() { EditorApplication.update += Tick; }

        public static string Dir => Path.GetFullPath(Path.Combine(Application.dataPath, "../../docs/produccion/evidencia"));

        // teleport: "x,y,z,yaw" opcional para colocar al jugador antes de capturar.
        public static void Run(string scenePath, string label, float delaySeconds, string teleport = "")
        {
            Directory.CreateDirectory(Dir);
            var done = Path.Combine(Dir, label + ".done"); if (File.Exists(done)) File.Delete(done);
            EditorSceneManager.OpenScene(scenePath, OpenSceneMode.Single);
            EditorPrefs.SetString(KeyLabel, label); EditorPrefs.SetFloat(KeyDelay, delaySeconds); EditorPrefs.SetString(KeyTeleport, teleport);
            EditorApplication.EnterPlaymode();
        }

        static void Tick()
        {
            var label = EditorPrefs.GetString(KeyLabel, "");
            if (string.IsNullOrEmpty(label) || !Application.isPlaying) return;
            if (_startedAt == 0) { _startedAt = EditorApplication.timeSinceStartup; _captured = false; _path = Path.Combine(Dir, label + ".png"); return; }
            float delay = EditorPrefs.GetFloat(KeyDelay, 3f);
            double t = EditorApplication.timeSinceStartup - _startedAt;
            if (!_captured && t >= delay - 0.5f)
            {
                var tp = EditorPrefs.GetString(KeyTeleport, "");
                if (!string.IsNullOrEmpty(tp))
                {
                    var p = tp.Split(','); var pc = Object.FindFirstObjectByType<Player.PlayerController>();
                    if (pc != null && p.Length == 4) pc.motor.Teleport(new Vector3(float.Parse(p[0]), float.Parse(p[1]), float.Parse(p[2])), float.Parse(p[3]));
                    EditorPrefs.SetString(KeyTeleport, "");
                }
            }
            if (!_captured && t >= delay) { ScreenCapture.CaptureScreenshot(_path); _captured = true; return; }
            if (_captured && t >= delay + 1.5)
            {
                EditorPrefs.DeleteKey(KeyLabel); _startedAt = 0;
                File.WriteAllText(Path.Combine(Dir, label + ".done"), File.Exists(_path) ? "OK " + _path : "MISSING " + _path);
                EditorApplication.ExitPlaymode();
            }
        }
    }
}
