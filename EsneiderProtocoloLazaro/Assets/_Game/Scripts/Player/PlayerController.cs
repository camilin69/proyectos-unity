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
        public float captureDefeatSeconds = 2.5f;

        public bool IsCaptured { get; private set; }
        public string Prompt { get; private set; } = "";
        IInteractable _target;
        float _capturedAt;

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
            if (input.PausePressed && flow != null && (flow.State == GameState.Playing || flow.State == GameState.Paused)) flow.TogglePause();
            if (input.RestartPressed && flow != null && (flow.State == GameState.Dead || flow.State == GameState.Captured || flow.State == GameState.Won)) { Restart(); input.ConsumeFrame(); return; }

            bool active = flow == null || flow.State == GameState.Playing;
            if (IsCaptured)
            {
                look.Tick(input.Look * 0.3f);
                if (Time.time - _capturedAt >= captureDefeatSeconds) Defeat("DERROTA_RED");
                input.ConsumeFrame();
                return;
            }
            if (!active) { input.ConsumeFrame(); return; }

            look.Tick(input.Look);
            motor.Tick(input.Move, input.RunHeld, input.CrouchPressed, input.JumpPressed, Time.deltaTime);
            if (look.cameraPivot != null && motor.movementEnabled) look.cameraPivot.localPosition = new Vector3(0, motor.EyeHeight, 0);

            if (input.FlashlightPressed && inventory.hasFlashlight && flashlight != null) flashlight.enabled = !flashlight.enabled; // 25: modificar componente
            if (input.WeaponSlotPressed == 1) actions.RequestEquip(Core.Data.WeaponKind.Melee);
            else if (input.WeaponSlotPressed == 2) actions.RequestEquip(Core.Data.WeaponKind.Pistol);
            else if (input.WeaponSlotPressed == 3) actions.RequestEquip(Core.Data.WeaponKind.Shotgun);
            else if (input.ScrollDelta != 0) CycleWeapon(input.ScrollDelta);
            if (input.FirePressed || (input.FireHeld && actions.ActiveWeapon == Core.Data.WeaponKind.Melee)) actions.RequestAttack();
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
            }
        }

        // 12.1: red válida → Captured; arma deshabilitada; derrota en ≤ 2.5 s.
        public void Capture(GameObject byWhom)
        {
            if (IsCaptured || (health != null && health.IsDead)) return;
            IsCaptured = true; _capturedAt = Time.time;
            actions.ForceCancelAll("captured"); actions.actionsEnabled = false; motor.movementEnabled = false;
            GameFlowController.Instance?.SetState(GameState.Captured);
            inventory.Notify("¡Capturado!");
        }

        void OnDied(DamageInfo info) { actions.ForceCancelAll("dead"); Defeat("DERROTA_DANO"); }

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
            if (cps != null && cps.LastConfirmed != null) { cps.RestoreInto(cps.LastConfirmed, this); return; }
            SceneManager.LoadScene(SceneManager.GetActiveScene().buildIndex >= 0 ? SceneManager.GetActiveScene().name : SceneManager.GetActiveScene().path);
        }

        public void ResetForRestore()
        {
            IsCaptured = false; Prompt = ""; _target = null;
            actions.ForceCancelAll("restore"); actions.actionsEnabled = true; motor.movementEnabled = true;
        }
    }
}
