using Esneider.Core;
using Esneider.Core.Persistence;
using UnityEngine;

namespace Esneider.World
{
    // 97/EVT-EXIT: se gana cruzando el exterior seguro con el jefe derrotado, una sola vez.
    [RequireComponent(typeof(BoxCollider))]
    public class VictoryTrigger : MonoBehaviour
    {
        bool _fired;
        public bool SaveEndConfirmed { get; private set; }
        public float resultsAfterSeconds = 20f;
        void Awake() { var c = GetComponent<BoxCollider>(); c.isTrigger = true; gameObject.layer = GameLayers.Trigger; }

        void OnTriggerEnter(Collider other)
        {
            if (_fired) return;
            var pc = other.GetComponent<Player.PlayerController>();
            if (pc == null || !ObjectiveService.Has(ObjectiveService.BossDefeated)) return;
            _fired = true;
            // END-03: comprometer ESCAPE/O11 y estadísticas (evento único); el arma baja gradualmente sin quitar la mirada
            WorldStateRegistry.Session.SetFlag("CAMPAIGN_WON"); ObjectiveService.Complete("O11");
            pc.Win();
            // 97.3: SAVE-END derivado del último checkpoint (CP-07), pose exterior estable; solo IO confirmado lo hace persistente
            var cps = CheckpointService.Instance;
            if (cps != null) { SaveEndConfirmed = cps.CommitNow("SAVE-END", pc, "REG-S4", false, 0, 0, 0); if (!SaveEndConfirmed) pc.inventory.Notify("No se pudo guardar el final; se conserva CP-07"); }
            StartCoroutine(EndSequence(pc));
        }

        // 97.2: END-03 → END-06
        System.Collections.IEnumerator EndSequence(Player.PlayerController pc)
        {
            var hud = FindFirstObjectByType<UI.HudController>(); var svc = Audio.AudioService.Instance;
            hud?.ShowMessage("Esneider: «Salí».", 3f);
            yield return new WaitForSeconds(3f);
            hud?.ShowMessage("Placa junto al parapeto: NÉMESIS · RESERVA BIOLÓGICA 04 · CONTINUIDAD OPERATIVA", 6f);
            yield return new WaitForSeconds(5f);
            if (svc != null) { svc.Play("SND-RELAY", transform.position + new Vector3(30f, 0, 20f), 0.4f, 100, 0f, svc.ambient, false); }
            float t0 = Time.time;
            while (Time.time - t0 < resultsAfterSeconds - 8f) { if (GameFlowController.Instance != null && GameFlowController.Instance.State != GameState.Won) yield break; yield return null; }
            UI.MenuController.Instance?.ShowVictory();
        }
    }
}
