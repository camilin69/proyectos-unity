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
            if (staminaText != null) staminaText.gameObject.SetActive(false);
            if (player == null) player = FindFirstObjectByType<PlayerController>();
            var hotbar = GetComponent<InventoryHotbar>();
            if (!hotbar) hotbar = gameObject.AddComponent<InventoryHotbar>();
            hotbar.player = player;
            if (ammoText != null)
            {
                // Ammunition sits just above stamina, clear of the nine hotbar slots.
                var rect = ammoText.rectTransform;
                rect.anchorMin = rect.anchorMax = rect.pivot = Vector2.zero;
                rect.anchoredPosition = new Vector2(20, 90); rect.sizeDelta = new Vector2(400, 35);
                ammoText.alignment = TextAnchor.LowerLeft;
            }
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
            if (crosshair != null) { bool hit = Time.time - player.actions.LastHitTime < .18f; crosshair.text = hit ? "×" : "·"; crosshair.color = hit ? new Color(1f,.7f,.3f) : Color.white; }
            if (hpText != null && player.health != null) hpText.text = $"VIDA {Mathf.CeilToInt(Mathf.Clamp01(player.health.Current / Mathf.Max(1f, player.health.maxHp)) * 100f)}%";
            if (ammoText != null)
            {
                var w = player.actions.ActiveWeapon;
                var inv = player.inventory;
                ammoText.text = w == Core.Data.WeaponKind.Pistol ? "PISTOLA · " + inv.AmmoLabel(AmmoType.Pistol) : w == Core.Data.WeaponKind.Shotgun ? "ESCOPETA · " + inv.AmmoLabel(AmmoType.Shotgun) : "";
            }
            if (staminaText != null && staminaText.gameObject.activeSelf) staminaText.gameObject.SetActive(false);
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
                stateText.text = player.IsCaptured && s==GameState.Playing ? "ATRAPADO EN LA RED" : s switch
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
