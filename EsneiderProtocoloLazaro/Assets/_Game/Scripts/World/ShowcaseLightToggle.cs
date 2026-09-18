using UnityEngine;

namespace Esneider.World
{
    // 44.1: luz neutra de inspección conmutable frente a luz de terror final (tecla L).
    public class ShowcaseLightToggle : MonoBehaviour
    {
        public GameObject neutral, game;
        public bool neutralOn = true;
        public void Toggle() { neutralOn = !neutralOn; if (neutral) neutral.SetActive(neutralOn); if (game) game.SetActive(!neutralOn); }
        void Update() { if (UnityEngine.InputSystem.Keyboard.current != null && UnityEngine.InputSystem.Keyboard.current.lKey.wasPressedThisFrame) Toggle(); }
    }
}
