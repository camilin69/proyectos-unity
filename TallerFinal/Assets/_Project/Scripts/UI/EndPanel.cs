using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

namespace Dream.UI
{
    // Panel final: de vuelta en el cuarto, a medianoche. Muestra recuerdos, puntaje y tiempo; nada mas suma.
    public class EndPanel : MonoBehaviour
    {
        CanvasGroup _group;
        Text _stats;

        public void Build()
        {
            var root = UIKit.Stretch(transform, "Final");
            _group = root.gameObject.AddComponent<CanvasGroup>();
            _group.alpha = 0f;
            var bg = root.gameObject.AddComponent<Image>();
            var a = UIKit.Pink; a.a = 0.78f; var b = UIKit.Mint; b.a = 0.6f;
            bg.sprite = UIKit.Gradient(b, a);
            UIKit.Label(root, "Pregunta", UIKit.Spaced("¿DESPERTASTE?"), 84, TextAnchor.MiddleCenter, UIKit.Ink, new Vector2(0.05f, 0.62f), new Vector2(0.95f, 0.78f));
            _stats = UIKit.Label(root, "Datos", "", 32, TextAnchor.MiddleCenter, UIKit.Ink, new Vector2(0.15f, 0.40f), new Vector2(0.85f, 0.60f));
            UIKit.Button(root, "Otra", "Soñar otra vez", new Vector2(0.30f, 0.22f), new Vector2(0.48f, 0.30f), () =>
            {
                Time.timeScale = 1f;
                SceneManager.LoadScene("Boot");
            });
            UIKit.Button(root, "Salir", "Despertar", new Vector2(0.52f, 0.22f), new Vector2(0.70f, 0.30f), () => GameFlow.Instance?.Quit());
        }

        void Update()
        {
            bool show = GameFlow.Instance && GameFlow.Instance.State == GameState.Ended;
            _group.alpha = Mathf.MoveTowards(_group.alpha, show ? 1f : 0f, Time.unscaledDeltaTime * 0.5f);
            _group.blocksRaycasts = show; _group.interactable = show;
            var sc = ScoreSystem.Instance;
            if (show && sc)
            {
                int m = Mathf.FloorToInt(sc.JourneyTime / 60f), s = Mathf.FloorToInt(sc.JourneyTime % 60f);
                _stats.text = $"Recuerdos  {sc.Memories} / {JourneyManager.Scenes.Length}\n<size=56><b>{sc.Score:N0}</b></size>\n" +
                              $"<i>soñaste {m} min {s:00} s  ·  son las 00:00</i>";
            }
        }
    }
}
