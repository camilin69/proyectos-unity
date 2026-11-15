using System.Collections;
using UnityEngine;
using UnityEngine.UI;

namespace Dream.Cinematic
{
    // Fundidos a blanco (la puerta de luz) y a negro (el hueco del arbol). Siempre encima de todo.
    public class ScreenFader : MonoBehaviour
    {
        public static ScreenFader Instance { get; private set; }
        public Image image;

        void Awake() { Instance = this; if (image) { image.color = new Color(0, 0, 0, 0); image.raycastTarget = false; } }
        void OnDestroy() { if (Instance == this) Instance = null; }

        public float Alpha => image ? image.color.a : 0f;

        public void Set(Color c, float alpha) { if (image) image.color = new Color(c.r, c.g, c.b, alpha); }

        public IEnumerator Fade(Color c, float toAlpha, float seconds)
        {
            if (!image) yield break;
            float from = image.color.a;
            // si cambia el color con la pantalla tapada, el cambio es instantaneo
            if (from > 0.99f && toAlpha < from) { } else if (from < 0.01f) Set(c, 0f);
            for (float t = 0f; t < seconds; t += Time.deltaTime)
            {
                float k = t / seconds; k = k * k * (3f - 2f * k);
                var cur = image.color;
                image.color = new Color(Mathf.Lerp(cur.r, c.r, k), Mathf.Lerp(cur.g, c.g, k), Mathf.Lerp(cur.b, c.b, k), Mathf.Lerp(from, toAlpha, k));
                yield return null;
            }
            Set(c, toAlpha);
        }
    }
}
