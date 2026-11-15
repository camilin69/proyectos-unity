using System;
using UnityEngine;

namespace Dream
{
    // Estado global: intro -> jugando <-> cinematica / pausa -> final. Tambien es el unico que toca el cursor:
    // jugando queda bloqueado y oculto; en cualquier menu queda libre.
    [DefaultExecutionOrder(-90)]
    public class GameFlow : MonoBehaviour
    {
        public static GameFlow Instance { get; private set; }
        public GameState State { get; private set; } = GameState.Intro;
        public event Action<GameState> StateChanged;

        GameState _beforePause;

        void Awake() => Instance = this;
        void OnDestroy() { if (Instance == this) Instance = null; }
        void Start()
        {
            SetState(State);
            // Play directo en un escenario (DevBoot): se salta la intro y se empieza ahi
            if (DevBoot.PendingStart >= 0 && JourneyManager.Instance)
            {
                JourneyManager.Instance.startAt = DevBoot.PendingStart;
                DevBoot.PendingStart = -1;
                StartJourney();
            }
        }

        public void SetState(GameState s)
        {
            State = s;
            Time.timeScale = s == GameState.Paused ? 0f : 1f;
            ApplyCursor();
            StateChanged?.Invoke(s);
        }

        public void ApplyCursor()
        {
            bool locked = State is GameState.Playing or GameState.Cinematic;
            Cursor.lockState = locked ? CursorLockMode.Locked : CursorLockMode.None;
            Cursor.visible = !locked;
        }

        // Al volver a la ventana el sistema suelta el cursor; se recupera aqui.
        void OnApplicationFocus(bool focus) { if (focus) ApplyCursor(); }

        void Update()
        {
            var input = DreamInput.Instance;
            if (input == null) return;
            if (input.ConsumePause())
            {
                if (State is GameState.Playing or GameState.Cinematic) { _beforePause = State; SetState(GameState.Paused); }
                else if (State == GameState.Paused) Resume();
            }
            // un clic dentro de la ventana mientras se juega vuelve a capturar el raton
            var mouse = UnityEngine.InputSystem.Mouse.current;
            if (State == GameState.Playing && Cursor.lockState != CursorLockMode.Locked && mouse != null && mouse.leftButton.wasPressedThisFrame)
                ApplyCursor();
        }

        public void Resume() { if (State == GameState.Paused) SetState(_beforePause); }

        public void StartJourney()
        {
            if (State != GameState.Intro) return;
            ScoreSystem.Instance?.ResetAll();
            SetState(GameState.Playing);
            JourneyManager.Instance?.Begin();
        }

        public void Quit()
        {
#if UNITY_EDITOR
            UnityEditor.EditorApplication.isPlaying = false;
#else
            Application.Quit();
#endif
        }
    }
}
