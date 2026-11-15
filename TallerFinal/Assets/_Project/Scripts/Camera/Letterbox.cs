using UnityEngine;

namespace Dream
{
    // Bandas negras de cine: recortan el cuadro a 2.39:1 sea cual sea la pantalla. Entran y salen suaves.
    public class Letterbox : MonoBehaviour
    {
        public const float CinemaAspect = 2.39f;
        public RectTransform top, bottom;
        public float seconds = 1.1f;

        float _t, _target;

        public void Show(bool on) => _target = on ? 1f : 0f;
        public float Amount => _t;

        public static float BarFraction(float screenW, float screenH)
        {
            if (screenH <= 0f) return 0f;
            float visibleH = screenW / CinemaAspect;
            return Mathf.Max(0f, (screenH - visibleH) * 0.5f / screenH);
        }

        void Update()
        {
            _t = Mathf.MoveTowards(_t, _target, Time.unscaledDeltaTime / seconds);
            float e = _t * _t * (3f - 2f * _t);
            float h = BarFraction(Screen.width, Screen.height) * e;
            if (top) { top.anchorMin = new Vector2(0f, 1f - h); top.anchorMax = Vector2.one; top.offsetMin = top.offsetMax = Vector2.zero; }
            if (bottom) { bottom.anchorMin = Vector2.zero; bottom.anchorMax = new Vector2(1f, h); bottom.offsetMin = bottom.offsetMax = Vector2.zero; }
        }
    }
}
