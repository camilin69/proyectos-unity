using UnityEngine;
using UnityEngine.UI;

namespace Dream.UI
{
    // HUD discreto: arriba el sueno actual y la hora; abajo los recuerdos y el puntaje; al centro el aviso de E,
    // las pistas y el texto del recuerdo recogido. Desaparece en las camaras de cine y en las cinematicas.
    public class HudView : MonoBehaviour
    {
        public static HudView Instance { get; private set; }

        CanvasGroup _main, _toast, _hintGroup;
        Text _dream, _title, _clock, _score, _prompt, _toastText, _toastGain, _hint;
        float _toastUntil, _hintUntil;

        void OnDestroy() { if (Instance == this) Instance = null; }

        public void Build()
        {
            Instance = this;
            var main = UIKit.Stretch(transform, "Principal");
            _main = main.gameObject.AddComponent<CanvasGroup>();
            _main.alpha = 0f;
            var shade = new Color(UIKit.Cream.r, UIKit.Cream.g, UIKit.Cream.b, 0.92f);
            _dream = UIKit.Label(main, "Sueno", "", 20, TextAnchor.UpperLeft, shade, new Vector2(0.03f, 0.88f), new Vector2(0.5f, 0.965f));
            _title = UIKit.Label(main, "Titulo", "", 40, TextAnchor.UpperLeft, UIKit.Cream, new Vector2(0.03f, 0.82f), new Vector2(0.6f, 0.935f), FontStyle.Italic);
            _clock = UIKit.Label(main, "Hora", "", 34, TextAnchor.UpperRight, UIKit.Cream, new Vector2(0.6f, 0.88f), new Vector2(0.97f, 0.965f));
            _score = UIKit.Label(main, "Puntaje", "", 24, TextAnchor.LowerLeft, shade, new Vector2(0.03f, 0.035f), new Vector2(0.6f, 0.1f));
            _prompt = UIKit.Label(main, "Aviso", "", 26, TextAnchor.MiddleCenter, UIKit.Cream, new Vector2(0.3f, 0.3f), new Vector2(0.7f, 0.36f));
            foreach (var t in new[] { _dream, _title, _clock, _score, _prompt }) Shadow(t);

            var toast = UIKit.Rect(transform, "Recuerdo", new Vector2(0.2f, 0.56f), new Vector2(0.8f, 0.76f));
            _toast = toast.gameObject.AddComponent<CanvasGroup>(); _toast.alpha = 0f;
            _toastText = UIKit.Label(toast, "Texto", "", 34, TextAnchor.MiddleCenter, UIKit.Cream, new Vector2(0f, 0.3f), Vector2.one, FontStyle.Italic);
            _toastGain = UIKit.Label(toast, "Suma", "", 24, TextAnchor.UpperCenter, UIKit.Gold, Vector2.zero, new Vector2(1f, 0.3f));
            Shadow(_toastText); Shadow(_toastGain);

            var hint = UIKit.Rect(transform, "Pista", new Vector2(0.25f, 0.18f), new Vector2(0.75f, 0.26f));
            _hintGroup = hint.gameObject.AddComponent<CanvasGroup>(); _hintGroup.alpha = 0f;
            _hint = UIKit.Label(hint, "Texto", "", 26, TextAnchor.MiddleCenter, UIKit.Cream, Vector2.zero, Vector2.one, FontStyle.Italic);
            Shadow(_hint);
        }

        static void Shadow(Text t)
        {
            var s = t.gameObject.AddComponent<Shadow>();
            s.effectColor = new Color(0f, 0f, 0f, 0.45f);
            s.effectDistance = new Vector2(1.5f, -1.5f);
        }

        public void SetPrompt(string text) { if (_prompt) _prompt.text = text ?? ""; }

        public void ShowMemory(string text, int gained, bool flight)
        {
            _toastText.text = $"“{text}”";
            _toastGain.text = gained > 0 ? $"+{gained:N0}" + (flight ? "\n<size=22>ahora puedes volar  ·  Q</size>" : "") : "";
            _toastUntil = Time.time + 7f;
        }

        public void ShowHint(string text) { _hint.text = text; _hintUntil = Time.time + 4.5f; }

        void Update()
        {
            var flow = GameFlow.Instance;
            var cams = CameraModeController.Instance;
            bool playing = flow && flow.State == GameState.Playing;
            bool show = playing && (cams == null || !cams.ShowingBody);
            float dt = Time.unscaledDeltaTime;
            _main.alpha = Mathf.MoveTowards(_main.alpha, show ? 1f : 0f, dt * 1.5f);
            _toast.alpha = Mathf.MoveTowards(_toast.alpha, Time.time < _toastUntil && flow && flow.State != GameState.Ended ? 1f : 0f, dt * 0.8f);
            _hintGroup.alpha = Mathf.MoveTowards(_hintGroup.alpha, Time.time < _hintUntil && playing ? 1f : 0f, dt * 1.5f);

            var j = JourneyManager.Instance;
            if (j && j.Anchor)
            {
                _dream.text = UIKit.Spaced($"SUEÑO {j.Current + 1} / {JourneyManager.Scenes.Length}");
                _title.text = j.Anchor.title;
            }
            if (TimeOfDay.Instance) _clock.text = TimeOfDay.Format(TimeOfDay.Instance.hour);
            var sc = ScoreSystem.Instance;
            if (sc) _score.text = $"Recuerdos  {sc.Memories} / {JourneyManager.Scenes.Length}     ·     {sc.Score:N0}";
        }
    }
}
