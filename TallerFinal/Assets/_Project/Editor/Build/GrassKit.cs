using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering.HighDefinition;
using static Dream.EditorTools.Build.BuildKit;

namespace Dream.EditorTools.Build
{
    // Pasto de verdad: mechones de decenas de briznas finas (malla generada aqui), dibujados por miles con instancing
    // y mecidos por el viento (WindField, con rafagas que recorren el campo). El material es humedo, con una capa de
    // rocio que brilla, y alrededor del que camina hay destellos de rocio y polen que vuela con el viento.
    public static class GrassKit
    {
        const string MeshDir = Root + "/Art/Models/Generados";

        // Un mechon: blades briznas finas que nacen en un circulo, se afinan y se curvan hacia afuera.
        static Mesh Tuft(int variant, int blades, float minH, float maxH)
        {
            string path = $"{MeshDir}/Pasto_Mechon_{variant}.asset";
            var rng = new System.Random(100 + variant);
            var verts = new List<Vector3>(); var norms = new List<Vector3>(); var uvs = new List<Vector2>(); var tris = new List<int>();
            const int seg = 4;
            for (int b = 0; b < blades; b++)
            {
                float ang = (float)rng.NextDouble() * Mathf.PI * 2f, rad = Mathf.Sqrt((float)rng.NextDouble()) * 0.26f;
                var root = new Vector3(Mathf.Cos(ang) * rad, 0f, Mathf.Sin(ang) * rad);
                float h = Mathf.Lerp(minH, maxH, (float)rng.NextDouble());
                float w = 0.008f + (float)rng.NextDouble() * 0.008f;
                float lean = ang + ((float)rng.NextDouble() - 0.5f) * 1.2f;               // se inclina hacia afuera del mechon
                var leanDir = new Vector3(Mathf.Cos(lean), 0f, Mathf.Sin(lean));
                float bendAmt = 0.15f + (float)rng.NextDouble() * 0.35f;
                var side = Vector3.Cross(Vector3.up, leanDir).normalized;
                side = Quaternion.AngleAxis(((float)rng.NextDouble() - 0.5f) * 80f, Vector3.up) * side;
                int start = verts.Count;
                for (int i = 0; i <= seg; i++)
                {
                    float t = i / (float)seg;
                    var c = root + Vector3.up * (h * t) + leanDir * (h * bendAmt * t * t);
                    float ww = w * (1f - t * 0.92f);
                    var tangent = (leanDir * 2f * bendAmt * t + Vector3.up).normalized;
                    var n = Vector3.Lerp(Vector3.Cross(side, tangent).normalized, Vector3.up, 0.45f).normalized;
                    verts.Add(c - side * ww); verts.Add(c + side * ww);
                    norms.Add(n); norms.Add(n);
                    uvs.Add(new Vector2(0f, t)); uvs.Add(new Vector2(1f, t));
                }
                for (int i = 0; i < seg; i++)
                {
                    int a = start + i * 2;
                    tris.Add(a); tris.Add(a + 2); tris.Add(a + 1);
                    tris.Add(a + 1); tris.Add(a + 2); tris.Add(a + 3);
                }
            }
            var m = AssetDatabase.LoadAssetAtPath<Mesh>(path);
            bool isNew = !m;
            if (isNew) m = new Mesh { name = $"Pasto_Mechon_{variant}" };
            m.Clear();
            m.SetVertices(verts); m.SetNormals(norms); m.SetUVs(0, uvs); m.SetTriangles(tris, 0);
            m.RecalculateBounds();
            if (isNew) AssetDatabase.CreateAsset(m, path);
            EditorUtility.SetDirty(m);
            return m;
        }

        // Brizna: verde oscuro en la base, claro y amarillento en la punta; humeda (capa de rocio que brilla).
        static Material BladeMat(string name, Color baseCol, Color tipCol)
        {
            var tex = GradientTex($"T_{name}", baseCol, tipCol);
            var m = Mat(name, Color.white, 0.22f, 0f, null, 0f, false, true);   // poco liso: en angulo rasante una brizna lisa refleja el cielo y se ve azul
            m.SetTexture("_BaseColorMap", tex);
            m.SetFloat("_CoatMask", 0f);
            m.SetFloat("_DoubleSidedNormalMode", 2f);            // las dos caras con la misma normal (hacia arriba): si no, el dorso queda a la sombra y azul                       // rocio: una capa transparente apenas, que brilla con el sol
            m.enableInstancing = true;
            HDMaterial.ValidateMaterial(m);
            EditorUtility.SetDirty(m);
            return m;
        }

        // Siembra count mechones donde spot diga, sobre el suelo groundY. Los batches se suman al WindField.
        public static void Meadow(WindField field, int count, System.Func<System.Random, Vector2?> spot, System.Func<float, float, float> groundY,
                                  Color baseCol, Color tipCol, float minH = 0.45f, float maxH = 0.85f, int seed = 1, int blades = 36)
        {
            var mats = new[] { BladeMat($"M_Brizna_{ColorUtility.ToHtmlStringRGB(tipCol)}", baseCol, tipCol) };
            var meshes = new[] { Tuft(0, blades, minH, maxH), Tuft(1, blades, minH * 0.85f, maxH * 0.9f), Tuft(2, blades, minH * 1.1f, maxH * 1.15f) };
            var lists = new[] { new List<Matrix4x4>(), new List<Matrix4x4>(), new List<Matrix4x4>() };
            var pts = new[] { new List<Vector3>(), new List<Vector3>(), new List<Vector3>() };
            var rng = new System.Random(seed);
            for (int i = 0; i < count; i++)
            {
                var p = spot(rng);
                if (!p.HasValue) continue;
                int k = rng.Next(3);
                var g = new Vector3(p.Value.x, groundY(p.Value.x, p.Value.y) - 0.02f, p.Value.y);
                float s = 0.8f + (float)rng.NextDouble() * 0.5f;
                lists[k].Add(Matrix4x4.TRS(g, Quaternion.Euler(0f, (float)rng.NextDouble() * 360f, 0f), new Vector3(s, s * (0.85f + (float)rng.NextDouble() * 0.3f), s)));
                pts[k].Add(g);
            }
            for (int k = 0; k < 3; k++)
                if (lists[k].Count > 0)
                    field.batches.Add(new WindField.Batch { mesh = meshes[k], materials = mats, matrices = lists[k].ToArray(), basePoints = pts[k].ToArray(), stiffness = 1.2f });
            field.drawDistance = Mathf.Max(field.drawDistance, 38f);
        }

        // Destellos de rocio entre el pasto y polen que vuela con el viento, siempre alrededor del que mira.
        public static void DewAndPollen(Transform parent, float dewNits, Color pollenColor)
        {
            var dot = AssetDatabase.LoadAssetAtPath<Texture2D>(TexDir + "/T_Punto_Estrella.png");

            var dew = new GameObject("Rocio_que_brilla");
            dew.transform.SetParent(parent, false);
            dew.AddComponent<FollowCamera>();
            var ps = dew.AddComponent<ParticleSystem>();
            var main = ps.main;
            main.loop = true; main.prewarm = true; main.maxParticles = 1500;
            main.startLifetime = new ParticleSystem.MinMaxCurve(0.6f, 2.2f);
            main.startSpeed = 0f; main.startSize = new ParticleSystem.MinMaxCurve(0.012f, 0.03f);
            main.simulationSpace = ParticleSystemSimulationSpace.World;
            var em = ps.emission; em.rateOverTime = 600f;
            var sh = ps.shape; sh.shapeType = ParticleSystemShapeType.Box; sh.scale = new Vector3(16f, 0.5f, 16f); sh.position = new Vector3(0f, -1.2f, 0f);
            var sz = ps.sizeOverLifetime; sz.enabled = true;
            sz.size = new ParticleSystem.MinMaxCurve(1f, new AnimationCurve(new Keyframe(0f, 0f), new Keyframe(0.15f, 1f), new Keyframe(0.3f, 0.2f), new Keyframe(0.5f, 0.9f), new Keyframe(1f, 0f)));
            var r = dew.GetComponent<ParticleSystemRenderer>();
            r.sharedMaterial = Additive("M_Destello_Rocio", dot, new Color(dewNits, dewNits, dewNits * 1.05f, 1f));
            r.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;

            var pollen = new GameObject("Polen_en_el_viento");
            pollen.transform.SetParent(parent, false);
            pollen.AddComponent<FollowCamera>();
            var pp = pollen.AddComponent<ParticleSystem>();
            var pm = pp.main;
            pm.loop = true; pm.prewarm = true; pm.maxParticles = 600;
            pm.startLifetime = new ParticleSystem.MinMaxCurve(6f, 10f);
            pm.startSpeed = 0f; pm.startSize = new ParticleSystem.MinMaxCurve(0.015f, 0.04f);
            pm.simulationSpace = ParticleSystemSimulationSpace.World;
            var pe = pp.emission; pe.rateOverTime = 70f;
            var psh = pp.shape; psh.shapeType = ParticleSystemShapeType.Box; psh.scale = new Vector3(24f, 3f, 24f); psh.position = new Vector3(0f, -0.3f, 0f);
            var vel = pp.velocityOverLifetime; vel.enabled = true; vel.space = ParticleSystemSimulationSpace.World;
            vel.x = new ParticleSystem.MinMaxCurve(Wind.Direction.x * 0.9f, Wind.Direction.x * 1.8f);
            vel.y = new ParticleSystem.MinMaxCurve(-0.05f, 0.15f);
            vel.z = new ParticleSystem.MinMaxCurve(Wind.Direction.z * 0.9f, Wind.Direction.z * 1.8f);
            var noise = pp.noise; noise.enabled = true; noise.strength = 0.4f; noise.frequency = 0.4f; noise.scrollSpeed = 0.3f;
            var col = pp.colorOverLifetime; col.enabled = true;
            var gr = new Gradient();
            gr.SetKeys(new[] { new GradientColorKey(Color.white, 0f), new GradientColorKey(Color.white, 1f) },
                       new[] { new GradientAlphaKey(0f, 0f), new GradientAlphaKey(1f, 0.15f), new GradientAlphaKey(1f, 0.85f), new GradientAlphaKey(0f, 1f) });
            col.color = gr;
            var prr = pollen.GetComponent<ParticleSystemRenderer>();
            prr.sharedMaterial = Additive("M_Polen", dot, pollenColor);
            prr.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
        }

        static Material Additive(string name, Texture2D tex, Color c)
        {
            var m = Unlit(name, c);
            HDMaterial.SetSurfaceType(m, true);
            m.SetFloat("_BlendMode", 1f);
            if (tex) m.SetTexture("_UnlitColorMap", tex);
            m.enableInstancing = true;
            HDMaterial.ValidateMaterial(m);
            EditorUtility.SetDirty(m);
            return m;
        }
    }
}
