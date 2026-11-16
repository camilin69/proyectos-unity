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

        // "Seguir soñando": de vuelta en el cuarto, ya sin viaje. Son las 3:33 para siempre: todo oscuro, la luna grande
        // en la ventana, el cielo rosado con nubes de algodon. No hay recuerdo ni puerta: solo el cuarto para mirarlo.
        public bool Lingering { get; private set; }

        public void ContinueDreaming() => StartCoroutine(ContinueRoutine());

        System.Collections.IEnumerator ContinueRoutine()
        {
            var fader = Cinematic.ScreenFader.Instance;
            if (fader) yield return fader.Fade(Color.black, 1f, 1.2f);
            Lingering = true;
            var scene = UnityEngine.SceneManagement.SceneManager.GetActiveScene();
            foreach (var g in FindObjectsByType<TransitionGate>(FindObjectsInactive.Include))
                if (g.gameObject.scene == scene) g.gameObject.SetActive(false);
            foreach (var m in FindObjectsByType<MemoryFragment>(FindObjectsInactive.Include))
                if (m.gameObject.scene == scene) m.gameObject.SetActive(false);
            foreach (var l in FindObjectsByType<Light>(FindObjectsInactive.Exclude))          // todo oscuro: solo la luna
                if (l.gameObject.scene == scene) l.enabled = false;
            foreach (var f in FindObjectsByType<UnityEngine.Rendering.HighDefinition.LocalVolumetricFog>(FindObjectsInactive.Exclude))
                if (f.gameObject.scene == scene && !f.GetComponentInParent<CottonClouds>()) f.gameObject.SetActive(false);   // sin polvo flotando
            var tod = TimeOfDay.Instance;
            if (tod)
            {
                var room = GameObject.Find("Cuarto");
                var win = room ? room.transform.TransformDirection(Vector3.forward) : Vector3.forward;
                tod.moonDirection = (Quaternion.AngleAxis(-11f, Vector3.Cross(Vector3.up, win)) * win).normalized;   // baja: se ve por la ventana
                tod.GoTo(3f + 33f / 60f + 0.001f, 0f);                         // 03:33, y ahi se queda
            }
            SetState(GameState.Playing);
            UI.HudView.Instance?.ShowHint("Son las 3:33. El tiempo se detuvo.");
            if (fader) yield return fader.Fade(Color.black, 0f, 2f);
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
