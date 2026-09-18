using Esneider.Core;
using Esneider.Player;
using UnityEngine;
using UnityEngine.UI;

namespace Esneider.UI
{
    // Sección 18: HUD discreto (salud, munición del arma actual, resistencia solo al correr, prompt, mensajes de cambios reales).
    // Placeholder uGUI para el sandbox; el HUD final migra a UI Toolkit en EX-07 (81).
    public class HudController : MonoBehaviour
    {
        public PlayerController player;
        public Text hpText, ammoText, staminaText, promptText, messageText, stateText, crosshair, bossText, objectiveText, checkpointText;
        public bool subtitles = true;
        float _messageUntil, _objectiveUntil, _checkpointUntil, _bossNameUntil; AI.BossBrain _boss; readonly System.Collections.Generic.Dictionary<Text, int> _baseSizes = new System.Collections.Generic.Dictionary<Text, int>();

        void Start()
        {
            if (player == null) player = FindFirstObjectByType<PlayerController>();
            if (player != null && player.inventory != null) player.inventory.Message += ShowMessage;
            var cps = Core.Persistence.CheckpointService.Instance;
            if (cps != null) cps.Committed += d => { if (checkpointText != null) checkpointText.text = "Checkpoint guardado · " + d.checkpointId; _checkpointUntil = Time.unscaledTime + 2f; }; // 81.1: 2 s tras snapshot exitoso, nunca antes
            foreach (var t in new[] { hpText, ammoText, staminaText, promptText, messageText, stateText, bossText, objectiveText, checkpointText }) if (t != null) _baseSizes[t] = t.fontSize;
        }

        public void ShowMessage(string msg) => ShowMessage(msg, 2.5f);
        public void ShowMessage(string msg, float seconds)
        {
            if (!subtitles && msg.StartsWith("[")) return; // subtítulos de voz desactivados
            if (msg.StartsWith("Checkpoint")) { if (checkpointText != null) checkpointText.text = msg; _checkpointUntil = Time.unscaledTime + 2f; return; }
            if (msg.StartsWith("Objetivo")) { if (objectiveText != null) objectiveText.text = msg; _objectiveUntil = Time.unscaledTime + 4f; return; }
            if (messageText != null) messageText.text = msg; _messageUntil = Time.unscaledTime + seconds;
        }
        public void ShowBoss(string name) { _boss = FindFirstObjectByType<AI.BossBrain>(); _bossNameUntil = Time.unscaledTime + 4f; if (bossText != null) bossText.text = name; }
        public void HideBoss() { _boss = null; if (bossText != null) bossText.text = ""; }
        public void SetTextScale(float k) { foreach (var kv in _baseSizes) if (kv.Key != null) kv.Key.fontSize = Mathf.RoundToInt(kv.Value * k); }

        void Update()
        {
            if (player == null) return;
            if (hpText != null && player.health != null) hpText.text = $"VIDA {Mathf.CeilToInt(player.health.Current)}";
            if (ammoText != null)
            {
                var w = player.actions.ActiveWeapon;
                var inv = player.inventory;
                ammoText.text = !w.HasValue ? "" : w == Core.Data.WeaponKind.Melee ? "VARILLA" : w == Core.Data.WeaponKind.Pistol ? $"PISTOLA {inv.pistolMag}/{inv.pistolReserve}" : $"ESCOPETA {inv.shotgunMag}/{inv.shotgunReserve}";
                if (player.actions.Busy) ammoText.text += $"  [{player.actions.CurrentKind} {player.actions.Current.Elapsed:F1}s]";
            }
            if (staminaText != null) staminaText.text = player.motor.IsRunning || player.motor.stamina < player.motor.staminaMax - 1f ? $"RESISTENCIA {Mathf.RoundToInt(player.motor.stamina)}" : "";
            if (promptText != null) promptText.text = player.Prompt;
            if (messageText != null && Time.unscaledTime > _messageUntil) messageText.text = "";
            if (objectiveText != null && Time.unscaledTime > _objectiveUntil) objectiveText.text = "";
            if (checkpointText != null && Time.unscaledTime > _checkpointUntil) checkpointText.text = "";
            if (bossText != null && _boss != null && !_boss.IsDead)
            {
                // 61.1: barra discreta; el nombre se muestra una vez
                var h = _boss.GetComponent<Core.Health>(); int seg = h != null ? Mathf.CeilToInt(h.Current / h.maxHp * 24f) : 0;
                bossText.text = (Time.unscaledTime < _bossNameUntil ? "EL ARCHIVISTA\n" : "") + new string('▮', Mathf.Max(0, seg)) + new string('▯', 24 - Mathf.Clamp(seg, 0, 24));
            }
            if (stateText != null)
            {
                var s = GameFlowController.Instance != null ? GameFlowController.Instance.State : GameState.Playing;
                stateText.text = s switch
                {
                    GameState.Paused => "PAUSA (Esc)",
                    GameState.Captured => "CAPTURADO",
                    GameState.Dead => "DERROTA — Enter para reiniciar",
                    GameState.Won => "ESCAPE — Enter para reiniciar",
                    _ => ""
                };
            }
        }
    }
}
