using UnityEngine;
using UnityEngine.UI;

namespace Dream.UI
{
    // Pantalla inicial: titulo, objetivo, controles y la opcion del vaiven. Enter o el boton empiezan el viaje.
    public class IntroPanel : MonoBehaviour
    {
        CanvasGroup _group;
        Text _swayLabel, _quality;

        public void Build()
        {
            var root = UIKit.Stretch(transform, "Intro");
            _group = root.gameObject.AddComponent<CanvasGroup>();
            var bg = root.gameObject.AddComponent<Image>();
            bg.sprite = UIKit.Gradient(UIKit.Mint, UIKit.Pink);
            bg.raycastTarget = true;

            UIKit.Label(root, "Titulo", UIKit.Spaced("SUEÑO LÚCIDO"), 92, TextAnchor.MiddleCenter, UIKit.Ink,
                        new Vector2(0.05f, 0.70f), new Vector2(0.95f, 0.86f));
            UIKit.Label(root, "Sub", "ocho sueños entre el amanecer y la medianoche", 30, TextAnchor.MiddleCenter,
                        new Color(UIKit.Ink.r, UIKit.Ink.g, UIKit.Ink.b, 0.75f), new Vector2(0.1f, 0.64f), new Vector2(0.9f, 0.70f), FontStyle.Italic);
            UIKit.Label(root, "Objetivo",
                "En cada sueño hay un recuerdo escondido. Encuéntralo y el sueño te dejará pasar al siguiente.\n" +
                "Cada recuerdo suma; cuanto antes lo encuentres, más vale. Al final del viaje, despiertas.",
                26, TextAnchor.MiddleCenter, UIKit.Ink, new Vector2(0.14f, 0.50f), new Vector2(0.86f, 0.62f));
            UIKit.Label(root, "Controles",
                "<b>WASD</b>  caminar        <b>Shift</b>  trotar        <b>Espacio</b>  saltar        <b>Ratón</b>  mirar\n" +
                "<b>E</b>  recordar        <b>Q</b>  volar (cuando el sueño lo permita)        <b>F</b>  cámara de cine        " +
                "<b>Tab</b>  saltar cinemática        <b>Esc</b>  pausa",
                22, TextAnchor.MiddleCenter, new Color(UIKit.Ink.r, UIKit.Ink.g, UIKit.Ink.b, 0.85f), new Vector2(0.06f, 0.36f), new Vector2(0.94f, 0.47f));

            _swayLabel = UIKit.Button(root, "Vaiven", "", new Vector2(0.26f, 0.26f), new Vector2(0.49f, 0.31f), CycleSway, 22)
                              .GetComponentInChildren<Text>();
            _quality = UIKit.Button(root, "Calidad", "", new Vector2(0.51f, 0.26f), new Vector2(0.74f, 0.31f), CycleQuality, 22)
                              .GetComponentInChildren<Text>();
            UIKit.Button(root, "Dormir", "D O R M I R", new Vector2(0.40f, 0.14f), new Vector2(0.60f, 0.22f),
                         () => GameFlow.Instance?.StartJourney(), 40);
            UIKit.Label(root, "Enter", "o pulsa Enter", 18, TextAnchor.UpperCenter, new Color(UIKit.Ink.r, UIKit.Ink.g, UIKit.Ink.b, 0.6f),
                        new Vector2(0.4f, 0.10f), new Vector2(0.6f, 0.135f), FontStyle.Italic);
            UIKit.Label(root, "Creditos", "Taller Final · Electiva IV · UPTC", 16, TextAnchor.LowerCenter,
                        new Color(UIKit.Ink.r, UIKit.Ink.g, UIKit.Ink.b, 0.5f), new Vector2(0.3f, 0.02f), new Vector2(0.7f, 0.06f));
            RefreshSway();
        }

        void CycleSway() { DreamSettings.Sway = (SwayMode)(((int)DreamSettings.Sway + 1) % 3); RefreshSway(); }
        void RefreshSway()
        {
            if (_swayLabel) _swayLabel.text = $"Vaivén de cámara:  {DreamSettings.Sway}";
            if (_quality) _quality.text = $"Calidad:  {DreamSettings.QualityName}";
        }

        void CycleQuality() { DreamSettings.Quality = 1 - DreamSettings.Quality; RefreshSway(); }

        void Update()
        {
            bool show = GameFlow.Instance && GameFlow.Instance.State == GameState.Intro;
            _group.alpha = Mathf.MoveTowards(_group.alpha, show ? 1f : 0f, Time.unscaledDeltaTime * 1.2f);
            _group.blocksRaycasts = show; _group.interactable = show;
            if (show && DreamInput.Instance != null && DreamInput.Instance.ConsumeConfirm()) GameFlow.Instance.StartJourney();
        }
    }
}
