using UnityEngine;

namespace Dream
{
    // El recuerdo como un prisma de cuatro dimensiones: un teseracto (hipercubo) que gira en los planos XW, YW y ZW y
    // se proyecta en perspectiva a 3D. Sus 32 aristas son luz pura; cada familia de aristas (las que corren por x, y,
    // z o w) tiene su color y los cuatro recorren el arcoiris desfasados, como un prisma.
    public class Tesseract : MonoBehaviour
    {
        public Material edgeTemplate;
        public float size = 0.2f, width = 0.012f, intensity = 14f, viewDistance = 3f;
        public Renderer core;
        public Light glow;

        static readonly Vector4[] V = new Vector4[16];
        static readonly int[,] E = new int[32, 2];
        static readonly int[] Axis = new int[32];
        LineRenderer[] _lines;
        Material[] _mats;
        Material _coreMat;

        static Tesseract()
        {
            for (int i = 0; i < 16; i++)
                V[i] = new Vector4((i & 1) == 0 ? -1 : 1, (i & 2) == 0 ? -1 : 1, (i & 4) == 0 ? -1 : 1, (i & 8) == 0 ? -1 : 1);
            int e = 0;
            for (int i = 0; i < 16; i++)
                for (int b = 0; b < 4; b++)
                {
                    int j = i ^ (1 << b);
                    if (j > i) { E[e, 0] = i; E[e, 1] = j; Axis[e] = b; e++; }
                }
        }

        void Awake()
        {
            _mats = new Material[4];
            for (int a = 0; a < 4; a++) _mats[a] = new Material(edgeTemplate);
            _lines = new LineRenderer[32];
            for (int e = 0; e < 32; e++)
            {
                var go = new GameObject("Arista");
                go.transform.SetParent(transform, false);
                var lr = go.AddComponent<LineRenderer>();
                lr.useWorldSpace = false; lr.positionCount = 2; lr.widthMultiplier = width;
                lr.numCapVertices = 2; lr.sharedMaterial = _mats[Axis[e]];
                lr.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off; lr.receiveShadows = false;
                _lines[e] = lr;
            }
            if (core) _coreMat = core.material;
        }

        static Vector4 Rot(Vector4 p, int a, int b, float ang)
        {
            float c = Mathf.Cos(ang), s = Mathf.Sin(ang);
            float pa = p[a], pb = p[b];
            p[a] = pa * c - pb * s; p[b] = pa * s + pb * c;
            return p;
        }

        void Update()
        {
            float t = Time.time;
            var proj = new Vector3[16];
            for (int i = 0; i < 16; i++)
            {
                var p = V[i];
                p = Rot(p, 0, 3, t * 0.61f);      // XW
                p = Rot(p, 1, 3, t * 0.37f);      // YW
                p = Rot(p, 2, 3, t * 0.23f);      // ZW
                p = Rot(p, 0, 2, t * 0.29f);      // XZ
                float k = viewDistance / (viewDistance - p.w);
                proj[i] = new Vector3(p.x, p.y, p.z) * k * size;
            }
            for (int e = 0; e < 32; e++)
            {
                _lines[e].SetPosition(0, proj[E[e, 0]]);
                _lines[e].SetPosition(1, proj[E[e, 1]]);
            }
            for (int a = 0; a < 4; a++)
            {
                var c = Color.HSVToRGB(Mathf.Repeat(t * 0.08f + a * 0.25f, 1f), 0.75f, 1f);
                _mats[a].SetColor("_UnlitColor", c * intensity);
            }
            var hue = Color.HSVToRGB(Mathf.Repeat(t * 0.08f + 0.6f, 1f), 0.5f, 1f);
            float pulse = 1f + 0.35f * Mathf.Sin(t * 2.6f);
            if (_coreMat) _coreMat.SetColor("_EmissiveColor", hue * 160f * pulse);
            if (glow) { glow.color = hue; }
        }
    }
}
