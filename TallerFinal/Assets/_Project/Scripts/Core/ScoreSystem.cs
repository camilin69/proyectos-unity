using System;
using UnityEngine;

namespace Dream
{
    // Puntaje del sueño. Cada recuerdo vale 1000; cuanto antes se encuentra dentro de su escenario, mas bono
    // (hasta 500). Al llegar al final la puntuacion queda cerrada: Lock() hace que nada mas sume.
    public class ScoreSystem : MonoBehaviour
    {
        public static ScoreSystem Instance { get; private set; }

        public const int MemoryValue = 1000, MaxQuickBonus = 500;
        public const float QuickBonusWindow = 240f;   // s dentro del escenario hasta que el bono llega a 0

        public int Score { get; private set; }
        public int Memories { get; private set; }
        public bool Locked { get; private set; }
        public float JourneyTime { get; private set; }
        public event Action Changed;

        float _sceneStart;

        void Awake() => Instance = this;
        void OnDestroy() { if (Instance == this) Instance = null; }

        void Update()
        {
            if (!Locked && GameFlow.Instance != null && GameFlow.Instance.State is GameState.Playing or GameState.Cinematic)
                JourneyTime += Time.deltaTime;
        }

        public void ResetAll() { Score = 0; Memories = 0; Locked = false; JourneyTime = 0f; _sceneStart = 0f; Changed?.Invoke(); }

        public void MarkSceneStart() => _sceneStart = JourneyTime;

        public static int QuickBonus(float secondsInScene) =>
            Mathf.RoundToInt(MaxQuickBonus * Mathf.Clamp01(1f - secondsInScene / QuickBonusWindow));

        public int AddMemory()
        {
            if (Locked) return 0;
            int gained = MemoryValue + QuickBonus(JourneyTime - _sceneStart);
            Memories++;
            Score += gained;
            Changed?.Invoke();
            return gained;
        }

        public void Lock() { Locked = true; Changed?.Invoke(); }
    }
}
