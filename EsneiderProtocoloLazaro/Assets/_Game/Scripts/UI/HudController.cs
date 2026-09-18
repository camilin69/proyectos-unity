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
        public Text hpText, ammoText, staminaText, promptText, messageText, stateText, crosshair;
        float _messageUntil;

        void Start()
        {
            if (player == null) player = FindFirstObjectByType<PlayerController>();
            if (player != null && player.inventory != null) player.inventory.Message += ShowMessage;
        }

        public void ShowMessage(string msg) => ShowMessage(msg, 2.5f);
        public void ShowMessage(string msg, float seconds) { if (messageText != null) messageText.text = msg; _messageUntil = Time.unscaledTime + seconds; }

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
