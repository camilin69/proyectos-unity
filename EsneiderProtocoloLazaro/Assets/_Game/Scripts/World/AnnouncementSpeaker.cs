using System.Collections;
using Esneider.Core;
using Esneider.Core.Persistence;
using UnityEngine;

namespace Esneider.World
{
    // EVT-C1 / OBJ-065 (5.2, 72.3, 93.2): al abrir D06 con la red reconectada, compromete DETECTADO y O03, reproduce la voz
    // desde el altavoz del corredor (filtrada, una vez por avance) y una alerta breve; activa las unidades del sector.
    public class AnnouncementSpeaker : MonoBehaviour
    {
        public string doorId = "D06";
        public float alertDelay = 0.4f;
        public string subtitle = "Atención. Se ha detectado presencia humana no registrada en las instalaciones. Unidades de contención: procedan con cautela. Recuperación prioritaria.";
        Door _door; bool _armed = true;
        public void ResetForCheckpoint() { StopAllCoroutines(); _armed=!WorldStateRegistry.Session.IsEventDone("EVT-C1"); }

        void Update()
        {
            if(GameFlowController.Instance != null && !GameFlowController.Instance.GameplayActive) return;
            if (!_armed || EventRunner.Instance == null) return;
            if (_door == null) { foreach (var d in FindObjectsByType<Door>(FindObjectsSortMode.None)) if (d.doorId == doorId) _door = d; if (_door == null) return; }
            if (!_door.isOpen) return;
            _armed = false;
            EventRunner.Instance.TryRunOnce("EVT-C1", () =>
            {
                ObjectiveService.Grant(ObjectiveService.Detected);
                WorldStateRegistry.Session.CompleteObjective("O03");
                foreach (var b in FindObjectsByType<AI.EnemyBrain>(FindObjectsSortMode.None)) b.Activate();
                StartCoroutine(Speak());
            });
        }

        IEnumerator Speak()
        {
            var svc = Audio.AudioService.Instance; var hud = FindFirstObjectByType<UI.HudController>();
            if (svc != null) svc.Play("SND-Alert-Short", transform.position, 0.9f, 8, 0f, svc.voice, false);
            yield return new WaitForSeconds(alertDelay + 1.6f);
            if (svc != null) { var s = svc.Play("SND-PA-Detection", transform.position, 1f, 8, 0f, svc.voice, false); if (s != null) { s.minDistance = 4f; s.maxDistance = 60f; } }
            hud?.ShowMessage("[Altavoz] " + subtitle, 9f);
            yield return new WaitForSeconds(9.5f);
            // el último eco da paso al silencio y al servo del primer Vigía (50.3): nada más aquí
        }
    }
}
