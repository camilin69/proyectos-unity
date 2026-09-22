using UnityEngine;
using UnityEngine.InputSystem;

namespace Esneider.Player
{
    // Sección 9: mapa de controles. Botones mantenidos se guardan como intención; pulsaciones se consumen por frame (86.1).
    public class PlayerInput : MonoBehaviour
    {
        public Vector2 Move { get; private set; }
        public Vector2 Look { get; private set; }
        public bool RunHeld { get; private set; }
        public bool AimHeld { get; private set; }
        public bool FireHeld { get; private set; }
        public bool CrouchHeld { get; private set; }
        public bool CrouchPressed, JumpPressed, InteractPressed, FlashlightPressed, FirePressed, ReloadPressed, HealPressed, InventoryPressed, PausePressed, RestartPressed;
        public int WeaponSlotPressed = -1;
        public int ScrollDelta;
        public bool EscapeNetPressed;
        public bool crouchToggle = true;

        InputActionMap _map;

        void Awake()
        {
            _map = new InputActionMap("Esneider");
            var move = _map.AddAction("Move", InputActionType.Value);
            move.AddCompositeBinding("2DVector").With("Up", "<Keyboard>/w").With("Down", "<Keyboard>/s").With("Left", "<Keyboard>/a").With("Right", "<Keyboard>/d");
            var look = _map.AddAction("Look", InputActionType.Value, "<Mouse>/delta");
            var run = _map.AddAction("Run", InputActionType.Button, "<Keyboard>/leftShift");
            var crouch = _map.AddAction("Crouch", InputActionType.Button, "<Keyboard>/leftCtrl");
            var jump = _map.AddAction("Jump", InputActionType.Button, "<Keyboard>/space");
            var interact = _map.AddAction("Interact", InputActionType.Button, "<Keyboard>/e");
            var flash = _map.AddAction("Flashlight", InputActionType.Button, "<Mouse>/rightButton");
            var escapeNet = _map.AddAction("EscapeNet", InputActionType.Button, "<Keyboard>/f");
            var fire = _map.AddAction("Fire", InputActionType.Button, "<Mouse>/leftButton");
            var aim = _map.AddAction("Aim", InputActionType.Button);
            var reload = _map.AddAction("Reload", InputActionType.Button, "<Keyboard>/r");
            for (int i = 1; i <= Inventory.SlotCount; i++)
            {
                int slot = i;
                var select = _map.AddAction("Slot" + slot, InputActionType.Button, "<Keyboard>/" + slot);
                select.performed += _ => WeaponSlotPressed = slot;
            }
            var heal = _map.AddAction("Heal", InputActionType.Button, "<Keyboard>/h");
            var inv = _map.AddAction("Inventory", InputActionType.Button, "<Keyboard>/tab");
            var pause = _map.AddAction("Pause", InputActionType.Button, "<Keyboard>/escape");
            var restart = _map.AddAction("Restart", InputActionType.Button, "<Keyboard>/enter");
            var scroll = _map.AddAction("Scroll", InputActionType.Value, "<Mouse>/scroll/y");

            crouch.performed += _ => CrouchPressed = true;
            jump.performed += _ => JumpPressed = true;
            interact.performed += _ => InteractPressed = true;
            flash.performed += _ => FlashlightPressed = true;
            escapeNet.performed += _ => EscapeNetPressed = true;
            fire.performed += _ => FirePressed = true;
            reload.performed += _ => ReloadPressed = true;
            heal.performed += _ => HealPressed = true;
            inv.performed += _ => InventoryPressed = true;
            pause.performed += _ => PausePressed = true;
            restart.performed += _ => RestartPressed = true;
            scroll.performed += c => { float v = c.ReadValue<float>(); if (Mathf.Abs(v) > 0.01f) ScrollDelta = v > 0 ? 1 : -1; };
            _move = move; _look = look; _run = run; _aim = aim; _fire = fire; _crouch = crouch;
        }

        InputAction _move, _look, _run, _aim, _fire, _crouch;

        void OnEnable() { _map.Enable(); }
        void OnDisable() { _map.Disable(); }
        void OnDestroy() { _map.Dispose(); }

        void Update()
        {
            Move = Vector2.ClampMagnitude(_move.ReadValue<Vector2>(), 1f);
            Look = _look.ReadValue<Vector2>();
            RunHeld = _run.IsPressed();
            AimHeld = _aim.IsPressed();
            FireHeld = _fire.IsPressed();
            CrouchHeld = _crouch.IsPressed();
        }

        // Llamar al final del frame por el controlador que consume las pulsaciones.
        public void ConsumeFrame()
        {
            CrouchPressed = JumpPressed = InteractPressed = FlashlightPressed = FirePressed = ReloadPressed = HealPressed = InventoryPressed = PausePressed = RestartPressed = false;
            WeaponSlotPressed = -1; ScrollDelta = 0;
            EscapeNetPressed = false;
        }
    }
}
