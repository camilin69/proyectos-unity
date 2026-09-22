using UnityEngine;
using UnityEngine.UI;

namespace Esneider.UI
{
    // Resolution-independent eyelids with a soft edge; no render textures or blur passes.
    [RequireComponent(typeof(CanvasRenderer))]
    public class WakeVision : MaskableGraphic
    {
        public const float Duration = 9f;
        static readonly AnimationCurve Aperture = new AnimationCurve(
            new Keyframe(0, 0), new Keyframe(.8f, 0), new Keyframe(1.8f, .09f),
            new Keyframe(2.6f, 0), new Keyframe(4.2f, .3f), new Keyframe(4.65f, .02f),
            new Keyframe(6f, .65f), new Keyframe(6.5f, .45f), new Keyframe(8.5f, 1), new Keyframe(9, 1));
        float aperture, darkness = 1;
        public float Openness => aperture;
        public float Darkness => darkness;

        public static WakeVision Create(Transform owner)
        {
            var go = new GameObject("AwakeningVision", typeof(RectTransform), typeof(Canvas));
            go.transform.SetParent(owner, false);
            var canvas = go.GetComponent<Canvas>(); canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvas.sortingOrder = 40; // Pause/title menus remain above the waking effect.
            var image = new GameObject("SoftEyelids", typeof(RectTransform), typeof(WakeVision));
            image.transform.SetParent(go.transform, false);
            var vision = image.GetComponent<WakeVision>(); vision.raycastTarget = false;
            vision.rectTransform.anchorMin = Vector2.zero; vision.rectTransform.anchorMax = Vector2.one;
            vision.rectTransform.offsetMin = vision.rectTransform.offsetMax = Vector2.zero;
            vision.Sample(0); return vision;
        }

        public void Sample(float seconds)
        {
            aperture = Mathf.Clamp01(Aperture.Evaluate(seconds));
            darkness = 1 - Mathf.SmoothStep(0, 1, Mathf.Clamp01(seconds / Duration));
            SetVerticesDirty();
        }

        protected override void OnPopulateMesh(VertexHelper vh)
        {
            vh.Clear(); var r = rectTransform.rect;
            Quad(vh, r.xMin, r.xMax, r.yMin, r.yMin, r.yMax, r.yMax, darkness, darkness);
            float feather = r.height * .035f;
            const int segments = 64;
            for (int i = 0; i < segments; i++)
            {
                float a = i / (float)segments, b = (i + 1f) / segments;
                float x0 = Mathf.Lerp(r.xMin, r.xMax, a), x1 = Mathf.Lerp(r.xMin, r.xMax, b);
                float gap0 = aperture * r.height * .95f * (1 - .35f * Mathf.Pow(a * 2 - 1, 2));
                float gap1 = aperture * r.height * .95f * (1 - .35f * Mathf.Pow(b * 2 - 1, 2));
                float top0 = Mathf.Min(r.yMax, r.center.y + gap0), top1 = Mathf.Min(r.yMax, r.center.y + gap1);
                float bot0 = Mathf.Max(r.yMin, r.center.y - gap0), bot1 = Mathf.Max(r.yMin, r.center.y - gap1);
                Quad(vh, x0, x1, top0, top1, r.yMax, r.yMax, 1, 1);
                Quad(vh, x0, x1, Mathf.Min(r.yMax, r.center.y + gap0 - feather), Mathf.Min(r.yMax, r.center.y + gap1 - feather), top0, top1, 0, 1);
                Quad(vh, x0, x1, r.yMin, r.yMin, bot0, bot1, 1, 1);
                Quad(vh, x0, x1, bot0, bot1, Mathf.Max(r.yMin, r.center.y - gap0 + feather), Mathf.Max(r.yMin, r.center.y - gap1 + feather), 1, 0);
            }
        }

        static void Quad(VertexHelper vh, float x0, float x1, float low0, float low1, float high0, float high1, float lowAlpha, float highAlpha)
        {
            int first = vh.currentVertCount;
            vh.AddVert(new Vector3(x0, low0, 0), new Color(0, 0, 0, lowAlpha), Vector2.zero);
            vh.AddVert(new Vector3(x1, low1, 0), new Color(0, 0, 0, lowAlpha), Vector2.zero);
            vh.AddVert(new Vector3(x1, high1, 0), new Color(0, 0, 0, highAlpha), Vector2.zero);
            vh.AddVert(new Vector3(x0, high0, 0), new Color(0, 0, 0, highAlpha), Vector2.zero);
            vh.AddTriangle(first, first + 1, first + 2); vh.AddTriangle(first, first + 2, first + 3);
        }
    }
}
