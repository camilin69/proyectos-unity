using System;
using UnityEngine;

namespace Esneider.Core
{
    public enum GameState { Boot, Playing, Paused, Captured, Dead, Won, Loading }

    // Sección 20.1/25: estados de partida y una línea de consola por intento.
    public class GameFlowController : MonoBehaviour
    {
        public static GameFlowController Instance { get; private set; }

        public GameState State { get; private set; } = GameState.Boot;
        public event Action<GameState, GameState> StateChanged;

        [Header("Estadísticas del intento (25)")]
        public string currentSector = "SANDBOX";
        public float attemptTime;
        public int enemiesKilled;
        public int shotsFired;
        public int physicsImpacts;
        public int attempts;
        bool _attemptOpen;
        public bool AttemptOpen => _attemptOpen;
        public string LastResult { get; private set; } = "";

        void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
        }

        void OnDestroy() { if (Instance == this) Instance = null; }

        void Update()
        {
            if (State == GameState.Playing) attemptTime += Time.deltaTime;
        }

        public void StartAttempt()
        {
            attemptTime = 0; enemiesKilled = 0; shotsFired = 0; physicsImpacts = 0; attempts++;
            _attemptOpen = true;
            SetState(GameState.Playing);
        }

        public void SetState(GameState next)
        {
            if (State == next) return;
            var prev = State; State = next;
            Time.timeScale = next == GameState.Paused ? 0f : 1f;
            StateChanged?.Invoke(prev, next);
        }

        public void TogglePause()
        {
            if (State == GameState.Playing) SetState(GameState.Paused);
            else if (State == GameState.Paused) SetState(GameState.Playing);
        }

        public void EndAttempt(string result, float playerHp)
        {
            if (!_attemptOpen) return;
            _attemptOpen = false; LastResult = result;
            SetState(result == "ESCAPE" ? GameState.Won : result == "DERROTA_RED" ? GameState.Captured : GameState.Dead);
            Debug.Log($"Resultado: {result} | Sector: {currentSector} | Vida: {Mathf.RoundToInt(playerHp)} | Enemigos: {enemiesKilled} | Disparos: {shotsFired} | Impactos físicos: {physicsImpacts} | Tiempo: {Mathf.RoundToInt(attemptTime)} s");
        }

        public bool GameplayActive => State == GameState.Playing;
    }
}
