using Esneider.Core;
using Esneider.World;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Esneider.Player
{
    // Raíz de composición del jugador: enruta input a motor/mirada/acciones e implementa captura, muerte y reinicio (12/20/25).
    [RequireComponent(typeof(PlayerInput), typeof(PlayerMotor), typeof(PlayerLook))]
    public class PlayerController : MonoBehaviour
    {
        public PlayerInput input;
        public PlayerMotor motor;
        public PlayerLook look;
        public PlayerActions actions;
        public Inventory inventory;
        public Health health;
        public Light flashlight;
        [Header("Escape de la red del Vigía")]
        [Min(1)] public int captureEscapePresses = 8;
        [Min(0.1f)] public float captureDamageInterval = 1f;
        [Min(0)] public float captureDamagePerTick = 4f;
        [Min(0)] public float captureEscapeGraceSeconds = 2f;

        public bool IsCaptured { get; private set; }
        public string Prompt { get; private set; } = "";
        IInteractable _target;
        float _nextCaptureDamage, _captureImmuneUntil;
        public int CapturePresses { get; private set; }
        public GameObject CaptureSource { get; private set; }
        public string CapturePrompt => $"Presiona F varias veces para escapar ({CapturePresses}/{Mathf.Max(1,captureEscapePresses)})";

        void Awake()
        {
            input = input ?? GetComponent<PlayerInput>(); motor = motor ?? GetComponent<PlayerMotor>(); look = look ?? GetComponent<PlayerLook>();
            actions = actions ?? GetComponent<PlayerActions>(); inventory = inventory ?? GetComponent<Inventory>(); health = health ?? GetComponent<Health>();
            if (health != null) health.Died += OnDied;
        }

        void Start()
        {
            Cursor.lockState = CursorLockMode.Locked; Cursor.visible = false;
            if (GameFlowController.Instance != null && GameFlowController.Instance.State == GameState.Boot) GameFlowController.Instance.StartAttempt();
        }

        void Update()
        {
            var flow = GameFlowController.Instance;
            var menu = UI.MenuController.Instance;
            if (input.PausePressed && flow != null && (flow.State == GameState.Playing || flow.State == GameState.Paused) && (menu == null || !menu.Modal)) { if (menu != null && menu.IsOpen && flow.State == GameState.Paused) menu.Resume(); else flow.TogglePause(); }
            if (input.RestartPressed && flow != null && flow.State == GameState.Won) { if (menu != null) menu.ShowVictory(); input.ConsumeFrame(); return; }
            if (input.RestartPressed && flow != null && (flow.State == GameState.Dead || flow.State == GameState.Captured) && (menu == null || !menu.IsOpen)) { Restart(); input.ConsumeFrame(); return; }

            bool active = flow == null || flow.State == GameState.Playing;
            if (!active) { input.ConsumeFrame(); return; }
            if (IsCaptured)
            {
                look.Tick(input.Look * 0.3f);
                if (input.EscapeNetPressed || input.FlashlightPressed) RegisterEscapePress();
                if (IsCaptured && Time.time >= _nextCaptureDamage)
                {
                    _nextCaptureDamage = Time.time + Mathf.Max(.1f,captureDamageInterval);
                    health?.ApplyDamage(new DamageInfo { amount=captureDamagePerTick, attackId=AttackIds.Next(), source=CaptureSource, kind="NetStruggle" });
                }
                input.ConsumeFrame();
                return;
            }

            // El editor suelta el bloqueo del cursor al perder el foco o al pulsar Escape, y la build lo pierde
            // al alternar de ventana. Sin esto el ratón se queda fuera del juego hasta abrir y cerrar el menú.
            if ((menu == null || !menu.IsOpen) && Cursor.lockState != CursorLockMode.Locked && input.FirePressed)
            {
                Cursor.lockState = CursorLockMode.Locked; Cursor.visible = false;
                input.ConsumeFrame(); return;
            }

            look.Tick(input.Look);
            motor.Tick(input.Move, input.RunHeld, input.CrouchPressed, input.JumpPressed, Time.deltaTime);
            if (look.cameraPivot != null && motor.movementEnabled) look.cameraPivot.localPosition = new Vector3(0, motor.EyeHeight, 0);

            if (input.FlashlightPressed && inventory.hasFlashlight && flashlight != null) flashlight.enabled = !flashlight.enabled; // 25: modificar componente
            if (input.WeaponSlotPressed >= 1 && input.WeaponSlotPressed <= Inventory.SlotCount) actions.RequestSelectSlot(input.WeaponSlotPressed - 1);
            else if (input.ScrollDelta != 0) actions.RequestSelectSlot((inventory.selectedSlot + input.ScrollDelta + Inventory.SlotCount) % Inventory.SlotCount);
            if (input.FirePressed || (input.FireHeld && actions.ActiveWeapon == Core.Data.WeaponKind.Melee)) actions.RequestUseSelected();
            if (input.ReloadPressed) actions.RequestReload();
            if (input.HealPressed) actions.RequestHeal();

            UpdateInteraction();
            if (input.InteractPressed && _target != null && _target.CanInteract(gameObject)) _target.Interact(gameObject);
            input.ConsumeFrame();
        }

        void CycleWeapon(int dir)
        {
            var order = new[] { Core.Data.WeaponKind.Melee, Core.Data.WeaponKind.Pistol, Core.Data.WeaponKind.Shotgun };
            int cur = actions.ActiveWeapon.HasValue ? System.Array.IndexOf(order, actions.ActiveWeapon.Value) : -1;
            for (int i = 1; i <= 3; i++)
            {
                var k = order[((cur + dir * i) % 3 + 3) % 3];
                if (inventory.HasWeapon(k)) { actions.RequestEquip(k); return; }
            }
        }

        void UpdateInteraction()
        {
            _target = null; Prompt = "";
            var ray = look.AimRay;
            if (Physics.Raycast(ray, out var hit, motor.interactionRange, GameLayers.Mask(GameLayers.Interactable, GameLayers.WorldStatic, GameLayers.DynamicProp), QueryTriggerInteraction.Collide))
            {
                var it = hit.collider.GetComponentInParent<IInteractable>();
                if (it != null && it.CanInteract(gameObject)) { _target = it; Prompt = "[E] " + it.Prompt; }
                else if (it is Door door) Prompt = door.Prompt;
            }
        }

        // La captura es una restricción recuperable dentro de Playing, no una derrota.
        public void Capture(GameObject byWhom)
        {
            if (IsCaptured || Time.time < _captureImmuneUntil || (health != null && health.IsDead)) return;
            var flow=GameFlowController.Instance;
            if (flow != null && flow.State != GameState.Playing) return;
            IsCaptured = true; CapturePresses=0; CaptureSource=byWhom;
            _nextCaptureDamage=Time.time+Mathf.Max(.1f,captureDamageInterval);
            Prompt=CapturePrompt; _target=null;
            actions.ForceCancelAll("captured"); actions.actionsEnabled = false; motor.movementEnabled = false;
            inventory.Notify("¡Atrapado en la red!");
        }

        public void RegisterEscapePress()
        {
            if (!IsCaptured || health.IsDead || (GameFlowController.Instance != null && !GameFlowController.Instance.GameplayActive)) return;
            CapturePresses++; Prompt=CapturePrompt;
            if (CapturePresses < Mathf.Max(1,captureEscapePresses)) return;
            var captor=CaptureSource;
            IsCaptured=false; CaptureSource=null; Prompt="";
            _captureImmuneUntil=Time.time+captureEscapeGraceSeconds;
            actions.actionsEnabled=true; motor.movementEnabled=true;
            captor?.GetComponent<AI.EnemyBrain>()?.OnCaptureEscaped();
            inventory.Notify("Has escapado de la red");
        }

        void OnDied(DamageInfo info) { IsCaptured=false; CaptureSource=null; Prompt=""; actions.ForceCancelAll("dead"); Defeat("DERROTA_DANO"); }

        void Defeat(string result)
        {
            actions.actionsEnabled = false; motor.movementEnabled = false;
            GameFlowController.Instance?.EndAttempt(result, health != null ? health.Current : 0);
        }

        public void Win()
        {
            actions.actionsEnabled = false; motor.movementEnabled = false;
            GameFlowController.Instance?.EndAttempt("ESCAPE", health != null ? health.Current : 0);
        }

        // Reintento (19/89): restaurar el último checkpoint confirmado; sin checkpoint, recargar la escena.
        public void Restart()
        {
            Time.timeScale = 1f;
            var cps = Core.Persistence.CheckpointService.Instance;
            if (cps != null && cps.LastConfirmed != null)
            {
                if (RegionStreamer.Instance != null) StartCoroutine(RestartAtCheckpoint(cps));
                else cps.RestoreInto(cps.LastConfirmed, this);
                return;
            }
            SceneManager.LoadScene(SceneManager.GetActiveScene().buildIndex >= 0 ? SceneManager.GetActiveScene().name : SceneManager.GetActiveScene().path);
        }

        public void ResetForRestore()
        {
            IsCaptured = false; CaptureSource=null; CapturePresses=0; _captureImmuneUntil=0; Prompt = ""; _target = null;
            actions.ForceCancelAll("restore"); actions.actionsEnabled = true; motor.movementEnabled = true;
        }

        System.Collections.IEnumerator RestartAtCheckpoint(Core.Persistence.CheckpointService cps)
        {
            var data = cps.LastConfirmed;
            GameFlowController.Instance?.SetState(GameState.Loading);
            Core.Persistence.WorldStateRegistry.Session.Restore(data.world);
            yield return RegionStreamer.Instance.LoadForCheckpoint(data.regionId, data.playerPosition, data.playerYaw);
            cps.RestoreInto(data, this);
        }
    }
}
