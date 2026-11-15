using UnityEngine;
using UnityEngine.InputSystem;

namespace Dream
{
    // Mapa de controles del sueño. Los botones mantenidos se leen cada frame; las pulsaciones quedan como bandera
    // hasta que alguien las consume (Consume*), para que ninguna se pierda entre Update y LateUpdate.
    [DefaultExecutionOrder(-100)]
    public class DreamInput : MonoBehaviour
    {
        public static DreamInput Instance { get; private set; }

        public Vector2 Move { get; private set; }
        public Vector2 Look { get; private set; }
        public bool RunHeld { get; private set; }
        public bool AscendHeld { get; private set; }
        public bool DescendHeld { get; private set; }

        bool _jump, _interact, _fly, _camera, _pause, _confirm, _skip;
        InputActionMap _map;
        InputAction _move, _look, _run, _ascend, _descend;

        void Awake()
        {
            Instance = this;
            _map = new InputActionMap("Sueno");
            _move = _map.AddAction("Move", InputActionType.Value);
            _move.AddCompositeBinding("2DVector").With("Up", "<Keyboard>/w").With("Down", "<Keyboard>/s")
                 .With("Left", "<Keyboard>/a").With("Right", "<Keyboard>/d");
            _move.AddCompositeBinding("2DVector").With("Up", "<Keyboard>/upArrow").With("Down", "<Keyboard>/downArrow")
                 .With("Left", "<Keyboard>/leftArrow").With("Right", "<Keyboard>/rightArrow");
            _look = _map.AddAction("Look", InputActionType.Value, "<Mouse>/delta");
            _run = _map.AddAction("Run", InputActionType.Button, "<Keyboard>/leftShift");
            _ascend = _map.AddAction("Ascend", InputActionType.Button, "<Keyboard>/space");
            _descend = _map.AddAction("Descend", InputActionType.Button, "<Keyboard>/leftCtrl");
            _map.AddAction("Jump", InputActionType.Button, "<Keyboard>/space").performed += _ => _jump = true;
            _map.AddAction("Interact", InputActionType.Button, "<Keyboard>/e").performed += _ => _interact = true;
            _map.AddAction("Fly", InputActionType.Button, "<Keyboard>/q").performed += _ => _fly = true;
            _map.AddAction("Camera", InputActionType.Button, "<Keyboard>/f").performed += _ => _camera = true;
            _map.AddAction("Pause", InputActionType.Button, "<Keyboard>/escape").performed += _ => _pause = true;
            var confirm = _map.AddAction("Confirm", InputActionType.Button, "<Keyboard>/enter");
            confirm.AddBinding("<Keyboard>/numpadEnter");
            confirm.performed += _ => _confirm = true;
            _map.AddAction("Skip", InputActionType.Button, "<Keyboard>/tab").performed += _ => _skip = true;
        }

        void OnEnable() => _map.Enable();
        void OnDisable() => _map.Disable();
        void OnDestroy() { _map.Dispose(); if (Instance == this) Instance = null; }

        void Update()
        {
            Move = Vector2.ClampMagnitude(_move.ReadValue<Vector2>(), 1f);
            Look = _look.ReadValue<Vector2>();
            RunHeld = _run.IsPressed();
            AscendHeld = _ascend.IsPressed();
            DescendHeld = _descend.IsPressed();
        }

        // Una pulsacion vale solo el frame en que llega: si nadie la consumio en Update se descarta, para que una E
        // pulsada lejos de un recuerdo no se dispare segundos despues al acercarse.
        void LateUpdate() => ClearPresses();

        static bool Take(ref bool b) { bool v = b; b = false; return v; }
        public bool ConsumeJump() => Take(ref _jump);
        public bool ConsumeInteract() => Take(ref _interact);
        public bool ConsumeFly() => Take(ref _fly);
        public bool ConsumeCamera() => Take(ref _camera);
        public bool ConsumePause() => Take(ref _pause);
        public bool ConsumeConfirm() => Take(ref _confirm);
        public bool ConsumeSkip() => Take(ref _skip);
        public void ClearPresses() { _jump = _interact = _fly = _camera = _pause = _confirm = _skip = false; }
    }
}
