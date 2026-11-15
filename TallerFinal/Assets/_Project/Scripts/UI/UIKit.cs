using UnityEngine;
using UnityEngine.Events;
using UnityEngine.UI;

namespace Dream.UI
{
    // Piezas de interfaz hechas por codigo. Paleta del sueno: rosa palido, menta, crema y tinta.
    public static class UIKit
    {
        public static readonly Color Pink = new(0.957f, 0.776f, 0.827f), Mint = new(0.749f, 0.910f, 0.851f),
            Cream = new(1f, 0.965f, 0.925f), Ink = new(0.176f, 0.165f, 0.208f), Gold = new(0.91f, 0.76f, 0.48f);

        static Font _font;
        public static Font Font => _font ? _font : (_font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf"));

        public static Canvas Canvas(Transform parent, string name, int order)
        {
            var go = new GameObject(name, typeof(RectTransform));
            go.transform.SetParent(parent, false);
            var c = go.AddComponent<Canvas>();
            c.renderMode = RenderMode.ScreenSpaceOverlay;
            c.sortingOrder = order;
            var s = go.AddComponent<CanvasScaler>();
            s.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            s.referenceResolution = new Vector2(1920, 1080);
            s.matchWidthOrHeight = 0.5f;
            go.AddComponent<GraphicRaycaster>();
            return c;
        }

        public static RectTransform Rect(Transform parent, string name, Vector2 min, Vector2 max, Vector2 offMin = default, Vector2 offMax = default)
        {
            var go = new GameObject(name, typeof(RectTransform));
            go.transform.SetParent(parent, false);
            var r = (RectTransform)go.transform;
            r.anchorMin = min; r.anchorMax = max; r.offsetMin = offMin; r.offsetMax = offMax;
            return r;
        }

        public static RectTransform Stretch(Transform parent, string name) => Rect(parent, name, Vector2.zero, Vector2.one);

        public static Image Panel(Transform parent, string name, Color c)
        {
            var img = Stretch(parent, name).gameObject.AddComponent<Image>();
            img.color = c;
            img.raycastTarget = false;
            return img;
        }

        public static Text Label(Transform parent, string name, string text, int size, TextAnchor align, Color color,
                                 Vector2 min, Vector2 max, FontStyle style = FontStyle.Normal)
        {
            var t = Rect(parent, name, min, max).gameObject.AddComponent<Text>();
            t.font = Font; t.text = text; t.fontSize = size; t.alignment = align; t.color = color; t.fontStyle = style;
            t.horizontalOverflow = HorizontalWrapMode.Wrap; t.verticalOverflow = VerticalWrapMode.Overflow;
            t.raycastTarget = false;
            t.supportRichText = true;
            return t;
        }

        public static Button Button(Transform parent, string name, string text, Vector2 min, Vector2 max, UnityAction onClick, int size = 30)
        {
            var r = Rect(parent, name, min, max);
            var img = r.gameObject.AddComponent<Image>();
            img.color = new Color(1f, 1f, 1f, 0.16f);
            var b = r.gameObject.AddComponent<Button>();
            var colors = b.colors;
            colors.normalColor = new Color(1f, 1f, 1f, 0.16f);
            colors.highlightedColor = new Color(1f, 1f, 1f, 0.42f);
            colors.pressedColor = new Color(1f, 1f, 1f, 0.6f);
            colors.selectedColor = colors.highlightedColor;
            colors.colorMultiplier = 1f;
            b.colors = colors;
            img.color = Color.white;
            b.targetGraphic = img;
            img.color = new Color(1f, 1f, 1f, 1f);
            var lbl = Label(r, "Texto", text, size, TextAnchor.MiddleCenter, Ink, Vector2.zero, Vector2.one);
            lbl.raycastTarget = false;
            if (onClick != null) b.onClick.AddListener(onClick);
            return b;
        }

        // Degradado vertical para fondos (abajo -> arriba).
        public static Sprite Gradient(Color bottom, Color top)
        {
            var tex = new Texture2D(2, 256, TextureFormat.RGBA32, false) { wrapMode = TextureWrapMode.Clamp, filterMode = FilterMode.Bilinear };
            for (int y = 0; y < 256; y++)
            {
                float k = y / 255f; k = k * k * (3f - 2f * k);
                var c = Color.Lerp(bottom, top, k);
                tex.SetPixel(0, y, c); tex.SetPixel(1, y, c);
            }
            tex.Apply();
            return Sprite.Create(tex, new Rect(0, 0, 2, 256), new Vector2(0.5f, 0.5f));
        }

        public static string Spaced(string s) => string.Join(" ", s.ToCharArray()).Replace("   ", "    ");
    }
}
