using UnityEngine;
using UnityEngine.UI;

namespace Dream.UI
{
    // Pausa: seguir, vaiven de camara, sensibilidad del raton, volumen, calidad y salir.
    public class PauseMenu : MonoBehaviour
    {
        CanvasGroup _group;
        Text _sway, _sens, _quality, _vol;

        public void Build()
        {
            var root = UIKit.Stretch(transform, "Pausa");
            _group = root.gameObject.AddComponent<CanvasGroup>();
            _group.alpha = 0f;
            var dim = root.gameObject.AddComponent<Image>();
            dim.color = new Color(UIKit.Ink.r, UIKit.Ink.g, UIKit.Ink.b, 0.55f);
            UIKit.Label(root, "Titulo", UIKit.Spaced("PAUSA"), 64, TextAnchor.MiddleCenter, UIKit.Cream, new Vector2(0.3f, 0.66f), new Vector2(0.7f, 0.78f));
            UIKit.Button(root, "Seguir", "Seguir soñando", new Vector2(0.38f, 0.57f), new Vector2(0.62f, 0.63f), () => GameFlow.Instance?.Resume());
            _sway = UIKit.Button(root, "Vaiven", "", new Vector2(0.38f, 0.49f), new Vector2(0.62f, 0.55f), CycleSway, 24).GetComponentInChildren<Text>();
            UIKit.Button(root, "Menos", "−", new Vector2(0.38f, 0.41f), new Vector2(0.42f, 0.47f), () => Sens(-0.01f));
            _sens = UIKit.Label(root, "Sens", "", 24, TextAnchor.MiddleCenter, UIKit.Cream, new Vector2(0.42f, 0.41f), new Vector2(0.58f, 0.47f));
            UIKit.Button(root, "Mas", "+", new Vector2(0.58f, 0.41f), new Vector2(0.62f, 0.47f), () => Sens(0.01f));
            _vol = UIKit.Label(root, "Volumen", "", 24, TextAnchor.MiddleLeft, UIKit.Cream, new Vector2(0.38f, 0.33f), new Vector2(0.5f, 0.39f));
            UIKit.Slider(root, "Barra_volumen", new Vector2(0.5f, 0.33f), new Vector2(0.62f, 0.39f), DreamSettings.Volume, v => { DreamSettings.Volume = v; Refresh(); });
            _quality = UIKit.Button(root, "Calidad", "", new Vector2(0.38f, 0.25f), new Vector2(0.62f, 0.31f), () => { DreamSettings.Quality = 1 - DreamSettings.Quality; Refresh(); }, 24).GetComponentInChildren<Text>();
            UIKit.Button(root, "Salir", "Despertar (salir)", new Vector2(0.38f, 0.17f), new Vector2(0.62f, 0.23f), () => GameFlow.Instance?.Quit());
            Refresh();
        }

        void CycleSway() { DreamSettings.Sway = (SwayMode)(((int)DreamSettings.Sway + 1) % 3); Refresh(); }
        void Sens(float d) { DreamSettings.MouseSensitivity = Mathf.Clamp(DreamSettings.MouseSensitivity + d, 0.02f, 0.3f); Refresh(); }

        void Refresh()
        {
            if (_sway) _sway.text = $"Vaivén de cámara:  {DreamSettings.Sway}";
            if (_quality) _quality.text = $"Calidad:  {DreamSettings.QualityName}";
            if (_sens) _sens.text = $"Ratón  {DreamSettings.MouseSensitivity:0.00}";
            if (_vol) _vol.text = $"Volumen  {Mathf.RoundToInt(DreamSettings.Volume * 100f)} %";
        }

        void Update()
        {
            bool show = GameFlow.Instance && GameFlow.Instance.State == GameState.Paused;
            _group.alpha = show ? 1f : 0f;
            _group.blocksRaycasts = show; _group.interactable = show;
        }
    }
}
