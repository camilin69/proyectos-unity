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
        static double _startedAt, _teleportedAt, _captureAt; static bool _captured, _loading; static string _path;

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
            if (_startedAt == 0) { _startedAt = EditorApplication.timeSinceStartup; _captured = false; _loading = false; _teleportedAt = 0; _captureAt = 0; _path = Path.Combine(Dir, label + ".png"); return; }
            float delay = EditorPrefs.GetFloat(KeyDelay, 3f);
            double t = EditorApplication.timeSinceStartup - _startedAt;
            // teleport "REG-XX|x,y,z,yaw": carga la región por el streamer (a los 2 s) y teletransporta 1 s antes de la captura
            var tp = EditorPrefs.GetString(KeyTeleport, "");
            if (!string.IsNullOrEmpty(tp) && tp.Contains("|") && t >= 2.0 && !_loading)
            {
                _loading = true; var region = tp.Split('|')[0]; var pc = Object.FindFirstObjectByType<Player.PlayerController>();
                if (pc != null && World.RegionStreamer.Instance != null) { Object.FindFirstObjectByType<World.OpeningSequence>()?.RequestSkip(); pc.StartCoroutine(World.RegionStreamer.Instance.LoadForCheckpoint(region)); }
            }
            if (!_captured && t >= 2.0 && !string.IsNullOrEmpty(tp)) // en cuanto la región esté lista (S1 se descarga al cambiar de contexto)
            {
                // no teletransportar hasta que la región destino esté Ready (o tras 25 s de espera máxima)
                bool ready = !tp.Contains("|") || World.RegionStreamer.Instance == null || World.RegionStreamer.Instance.IsReady(tp.Split('|')[0]) || t > delay + 25.0;
                if (ready)
                {
                    var p = (tp.Contains("|") ? tp.Split('|')[1] : tp).Split(','); var pc = Object.FindFirstObjectByType<Player.PlayerController>();
                    if (pc != null && p.Length == 4) { pc.motor.Teleport(new Vector3(float.Parse(p[0]), float.Parse(p[1]), float.Parse(p[2])), float.Parse(p[3])); pc.look.lookEnabled = true; pc.look.cameraPivot.localRotation = Quaternion.identity; }
                    EditorPrefs.SetString(KeyTeleport, ""); _teleportedAt = t;
                }
                else return;
            }
            if (!_captured && t >= delay && t >= _teleportedAt + 1.5) { ScreenCapture.CaptureScreenshot(_path); _captured = true; _captureAt = t; return; }
            if (_captured && t >= _captureAt + 1.5)
            {
                EditorPrefs.DeleteKey(KeyLabel); _startedAt = 0;
                var pcd = Object.FindFirstObjectByType<Player.PlayerController>(); var st = World.RegionStreamer.Instance;
                string diag = pcd != null ? $" player={pcd.transform.position} grounded={pcd.motor.IsGrounded}" : " player=null";
                if (st != null) diag += $" current={st.CurrentRegion} states=" + string.Join(",", System.Array.ConvertAll(World.RegionCatalog.Chain, r => r + ":" + st.State(r)));
                File.WriteAllText(Path.Combine(Dir, label + ".done"), (File.Exists(_path) ? "OK " + _path : "MISSING " + _path) + diag);
                EditorApplication.ExitPlaymode();
            }
        }
    }
}
