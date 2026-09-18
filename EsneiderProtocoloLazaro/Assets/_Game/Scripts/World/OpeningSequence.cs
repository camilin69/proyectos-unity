using System.Collections;
using Esneider.Core;
using Esneider.Core.Persistence;
using Esneider.Player;
using UnityEngine;
using UnityEngine.Playables;
using UnityEngine.Animations;

namespace Esneider.World
{
    // EVT-01 (5.1/58): negro parcial + respiración/goteo → tapa abre (Cryo_Open) → cámara sube a posición de pie → control gradual →
    // pantalla "LÁZARO / SUJETO: ESNEIDER / 2000 AÑOS" → CP-00. Omitible (Espacio/E); tras morir no se repite (política U).
    public class OpeningSequence : MonoBehaviour
    {
        public Transform cryoLidAnimatorRoot;
        public AnimationClip cryoOpenClip;
        public Vector3 lyingPosition;
        public float lyingYaw = 90f;
        public float riseSeconds = 12f;
        public string checkpointId = "CP-00";
        public string regionId = "REG-S1";
        bool _started;

        IEnumerator Start()
        {
            yield return null;
            // esperar a que el streamer libere al jugador (Ready) para que no vuelva a habilitar el control tras quitarlo aquí
            float w0 = Time.time;
            while (RegionStreamer.Instance != null && !RegionStreamer.Instance.IsReady(regionId) && Time.time - w0 < 20f) yield return null;
            yield return null;
            var pc = FindFirstObjectByType<PlayerController>();
            if (pc == null || EventRunner.Instance == null) yield break;
            if (EventRunner.Instance.IsDone("EVT-01")) yield break; // CP-00 omite apertura y coloca al jugador seguro
            if (!EventRunner.Instance.TryRunOnce("EVT-01", () => { })) yield break;
            _started = true;
            yield return StartCoroutine(Play(pc));
        }

        IEnumerator Play(PlayerController pc)
        {
            var hud = FindFirstObjectByType<UI.HudController>();
            pc.motor.movementEnabled = false; pc.actions.actionsEnabled = false; pc.look.lookEnabled = false;
            var standPos = pc.transform.position; float standYaw = pc.transform.eulerAngles.y;
            pc.motor.Teleport(lyingPosition, lyingYaw);
            var pivot = pc.look.cameraPivot; float eyeStand = pc.motor.EyeHeight; float eyeLying = 0.45f;
            pivot.localPosition = new Vector3(0, eyeLying, 0); pivot.localRotation = Quaternion.Euler(-70f, 0, 0);
            hud?.ShowMessage("…"); // 0–8 s: negro parcial, respiración contenida, goteo (sin música)
            if (Audio.AudioService.Instance != null) { Audio.AudioService.Instance.Play2D("SND-BREATH", 0.6f, Audio.AudioService.Instance.voice); Audio.AudioService.Instance.Play("SND-PIPE-Hit", lyingPosition + Vector3.up, 0.4f, 100, 0f, Audio.AudioService.Instance.ambient); }
            float t0 = Time.time;
            while (Time.time - t0 < 4f) { if (Skip(pc)) break; yield return null; }
            // 8–20 s: la compuerta abre
            PlayableGraph graph = default; AnimationClipPlayable clip = default;
            if (cryoLidAnimatorRoot != null && cryoOpenClip != null)
            {
                var animator = cryoLidAnimatorRoot.GetOrAdd<Animator>();
                graph = PlayableGraph.Create("cryo_open"); clip = AnimationClipPlayable.Create(graph, cryoOpenClip); clip.SetDuration(cryoOpenClip.length);
                var o = AnimationPlayableOutput.Create(graph, "cryo", animator); o.SetSourcePlayable(clip); graph.Play();
                if (Audio.AudioService.Instance != null) Audio.AudioService.Instance.Play("SND-DOOR-Slide-Start", cryoLidAnimatorRoot.position + Vector3.up, 0.7f, 64, 0f, Audio.AudioService.Instance.ambient);
            }
            t0 = Time.time;
            while (Time.time - t0 < 3f) { if (Skip(pc)) break; yield return null; }
            // cámara desciende suavemente hasta posición de pie
            float rise = Mathf.Max(1f, riseSeconds); t0 = Time.time;
            while (Time.time - t0 < rise)
            {
                float k = Mathf.SmoothStep(0, 1, (Time.time - t0) / rise);
                pivot.localPosition = new Vector3(0, Mathf.Lerp(eyeLying, eyeStand, k), 0);
                pivot.localRotation = Quaternion.Euler(Mathf.Lerp(-70f, 0f, k), 0, 0);
                pc.transform.position = Vector3.Lerp(lyingPosition, standPos, k); pc.transform.rotation = Quaternion.Euler(0, Mathf.LerpAngle(lyingYaw, standYaw, k), 0);
                if (Skip(pc)) break;
                yield return null;
            }
            if (graph.IsValid()) { clip.SetTime(cryoOpenClip.length); graph.Evaluate(0f); }
            pc.motor.Teleport(standPos, standYaw); pivot.localPosition = new Vector3(0, eyeStand, 0); pivot.localRotation = Quaternion.identity;
            // 20–35 s: control disponible; pantalla indica nombre y tiempo transcurrido
            pc.look.lookEnabled = true; pc.motor.movementEnabled = true; pc.actions.actionsEnabled = true;
            hud?.ShowMessage("LÁZARO / SUJETO: ESNEIDER / TIEMPO TRANSCURRIDO: 2000 AÑOS");
            WorldStateRegistry.Session.SetFlag("OPENING_DONE"); ObjectiveService.Complete("O01");
            var cps = CheckpointService.Instance;
            if (cps != null && !cps.RequestCheckpoint(checkpointId, pc, regionId)) Debug.LogWarning("OpeningSequence: CP-00 no solicitado: " + cps.LastNotice);
            if (graph.IsValid()) graph.Destroy();
            _finished = true;
        }

        public bool SkipRequested { get; private set; }
        public bool IsPlaying => _started && !_finished;
        bool _finished;
        public void RequestSkip() => SkipRequested = true;

        // PlayerController consume las pulsaciones en su Update (antes de que esta corrutina las lea), así que se lee el teclado directamente.
        bool Skip(PlayerController pc)
        {
            if (SkipRequested) return true;
            var kb = UnityEngine.InputSystem.Keyboard.current;
            if (kb != null && (kb.eKey.wasPressedThisFrame || kb.spaceKey.wasPressedThisFrame)) SkipRequested = true;
            return SkipRequested;
        }
    }
}
