using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering.HighDefinition;
using static Dream.EditorTools.Build.BuildKit;

namespace Dream.EditorTools.Build
{
    // Lo de la noche del final: la luna grande como un planeta, las estrellas que titilan, las antorchas de fuego
    // (con el aire que tiembla sobre la llama) y el meteorito en llamas de tamano planetario.
    public static class NightKit
    {
        const string HdriDir = ScanDir + "/HDRI";

        // ---------- texturas generadas ----------

        static Texture2D SaveTex(string file, Texture2D t, bool linear = false, bool repeat = false)
        {
            string path = $"{TexDir}/{file}";
            System.IO.File.WriteAllBytes(System.IO.Path.Combine(System.IO.Directory.GetCurrentDirectory(), path), t.EncodeToPNG());
            Object.DestroyImmediate(t);
            AssetDatabase.ImportAsset(path);
            var imp = (TextureImporter)AssetImporter.GetAtPath(path);
            imp.alphaIsTransparency = true; imp.sRGBTexture = !linear;
            imp.wrapMode = repeat ? TextureWrapMode.Repeat : TextureWrapMode.Clamp;
            imp.SaveAndReimport();
            return AssetDatabase.LoadAssetAtPath<Texture2D>(path);
        }

        // Llama: una gota con el nucleo casi blanco, amarillo y un borde naranja que se deshace hacia la punta.
        static Texture2D FlameTex()
        {
            const int w = 128, h = 256;
            var t = new Texture2D(w, h, TextureFormat.RGBA32, false);
            for (int y = 0; y < h; y++)
                for (int x = 0; x < w; x++)
                {
                    float u = (x + 0.5f) / w * 2f - 1f, v = (y + 0.5f) / h;
                    float width = Mathf.Lerp(0.85f, 0.05f, Mathf.Pow(v, 0.8f)) * Mathf.Sqrt(Mathf.Clamp01(v * 6f));
                    float d = Mathf.Abs(u) / Mathf.Max(0.001f, width);
                    float a = Mathf.Clamp01(1f - d) * Mathf.Clamp01((1f - v) * 1.4f);
                    a = Mathf.Pow(a, 1.2f);
                    float core = Mathf.Clamp01(1f - d * 1.6f) * Mathf.Clamp01(1f - v * 1.5f);
                    var c = Color.Lerp(new Color(1f, 0.35f, 0.05f), new Color(1f, 0.85f, 0.4f), core);
                    c = Color.Lerp(c, Color.white, core * core * 0.7f);
                    t.SetPixel(x, y, new Color(c.r * a, c.g * a, c.b * a, a));
                }
            return SaveTex("T_Llama.png", t);
        }

        // Punto suave (estrellas y halos).
        static Texture2D DotTex(string file, float falloff)
        {
            const int n = 128;
            var t = new Texture2D(n, n, TextureFormat.RGBA32, false);
            for (int y = 0; y < n; y++)
                for (int x = 0; x < n; x++)
                {
                    float d = new Vector2(x + 0.5f - n / 2f, y + 0.5f - n / 2f).magnitude / (n / 2f);
                    float a = Mathf.Pow(Mathf.Clamp01(1f - d), falloff);
                    t.SetPixel(x, y, new Color(a, a, a, a));
                }
            return SaveTex(file, t);
        }

        // Vectores de distorsion (RG en 0..1, 0.5 = sin desplazar) con ruido suave y borde que se apaga.
        static Texture2D DistortionTex()
        {
            const int n = 128;
            var t = new Texture2D(n, n, TextureFormat.RGBA32, false);
            for (int y = 0; y < n; y++)
                for (int x = 0; x < n; x++)
                {
                    float d = new Vector2(x + 0.5f - n / 2f, y + 0.5f - n / 2f).magnitude / (n / 2f);
                    float fade = Mathf.Clamp01(1f - d);
                    float r = 0.5f + (Mathf.PerlinNoise(x * 0.09f, y * 0.09f) - 0.5f) * fade;
                    float g = 0.5f + (Mathf.PerlinNoise(x * 0.09f + 13f, y * 0.09f + 7f) - 0.5f) * fade;
                    t.SetPixel(x, y, new Color(r, g, fade * 0.5f, fade));
                }
            return SaveTex("T_Distorsion_Calor.png", t, true);
        }

        // Lava del meteorito: corteza oscura con grietas encendidas (el color sale por la emision).
        static Texture2D LavaTex()
        {
            const int n = 1024;
            var t = new Texture2D(n, n, TextureFormat.RGBA32, false);
            for (int y = 0; y < n; y++)
                for (int x = 0; x < n; x++)
                {
                    float u = x / (float)n, v = y / (float)n;
                    float f = Mathf.PerlinNoise(u * 8f, v * 8f) * 0.6f + Mathf.PerlinNoise(u * 22f + 5f, v * 22f) * 0.3f + Mathf.PerlinNoise(u * 60f, v * 60f + 3f) * 0.1f;
                    float crack = Mathf.Pow(Mathf.Clamp01(1f - Mathf.Abs(f - 0.5f) * 9f), 2f);
                    float hot = Mathf.Clamp01(crack + Mathf.Clamp01((f - 0.66f) * 4f));
                    var c = Color.Lerp(new Color(0.02f, 0.01f, 0.01f), new Color(1f, 0.45f, 0.08f), hot);
                    c = Color.Lerp(c, new Color(1f, 0.9f, 0.5f), hot * hot * 0.6f);
                    t.SetPixel(x, y, c);
                }
            return SaveTex("T_Lava_Meteorito.png", t, false, true);
        }

        static Material Additive(string name, Texture2D tex, Color c)
        {
            var m = Unlit(name, c);
            HDMaterial.SetSurfaceType(m, true);
            m.SetFloat("_BlendMode", 1f);
            m.SetTexture("_UnlitColorMap", tex);
            m.SetFloat("_EnableFogOnTransparent", 0f);
            m.enableInstancing = true;
            HDMaterial.ValidateMaterial(m);
            EditorUtility.SetDirty(m);
            return m;
        }

        // ---------- la luna ----------

        // Luna llena grande como un planeta (cuerpo celeste del Physically Based Sky), con poco resplandor.
        public static void ConfigureMoon(Light moon)
        {
            string path = $"{HdriDir}/T_Luna_llena.png";
            var imp = AssetImporter.GetAtPath(path) as TextureImporter;
            if (imp != null && (imp.wrapMode != TextureWrapMode.Clamp || !imp.alphaIsTransparency))
            {
                imp.wrapMode = TextureWrapMode.Clamp; imp.alphaIsTransparency = true; imp.mipmapEnabled = true; imp.SaveAndReimport();
            }
            var d = moon.GetComponent<HDAdditionalLightData>();
            // la luna que se ve es el disco texturizado (SunDisc con moon = true); la luz solo ilumina, sin dibujar su
            // propio punto brillante en el cielo
            d.angularDiameter = 0.5f;
            d.surfaceTexture = null;
            d.flareSize = 0f; d.flareMultiplier = 0f;
            d.interactsWithSky = false;
            EditorUtility.SetDirty(d);
        }

        // ---------- estrellas que titilan ----------

        public static void TwinklingStars(Transform parent, int rate, Color tint)
        {
            var go = new GameObject("Estrellas_que_titilan");
            go.transform.SetParent(parent, false);
            go.AddComponent<FollowCamera>();
            var ps = go.AddComponent<ParticleSystem>();
            var main = ps.main;
            main.loop = true; main.prewarm = true; main.maxParticles = rate * 5;
            main.startLifetime = new ParticleSystem.MinMaxCurve(1.5f, 5f);
            main.startSpeed = 0f;
            main.startSize = new ParticleSystem.MinMaxCurve(1.6f, 4.2f);
            main.simulationSpace = ParticleSystemSimulationSpace.Local;
            var em = ps.emission; em.rateOverTime = rate;
            var sh = ps.shape; sh.shapeType = ParticleSystemShapeType.Hemisphere; sh.radius = 520f; sh.radiusThickness = 0f;
            sh.rotation = new Vector3(-90f, 0f, 0f);
            var sz = ps.sizeOverLifetime; sz.enabled = true;
            var curve = new AnimationCurve(new Keyframe(0f, 0f), new Keyframe(0.2f, 1f), new Keyframe(0.35f, 0.45f), new Keyframe(0.55f, 1f),
                                           new Keyframe(0.75f, 0.5f), new Keyframe(0.9f, 0.9f), new Keyframe(1f, 0f));
            sz.size = new ParticleSystem.MinMaxCurve(1f, curve);
            var r = go.GetComponent<ParticleSystemRenderer>();
            r.sharedMaterial = Additive("M_Estrella_Titila", DotTex("T_Punto_Estrella.png", 3f), tint);
            r.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
        }

        // ---------- antorcha ----------

        // Antorcha clavada en un muro: palo, copa de hierro, llama de particulas, aire que tiembla encima y luz viva.
        // outDir: hacia donde mira la cara del muro (la antorcha se inclina hacia alla).
        public static void Torch(Transform parent, Vector3 wallPoint, Vector3 outDir, Material wood, Material iron)
        {
            var root = Point("Antorcha", parent, wallPoint, 0f);
            var dir = (Vector3.up * 0.85f + outDir * 0.45f).normalized;
            var stick = Prim(PrimitiveType.Cylinder, "Palo", root, wallPoint + dir * 0.32f, new Vector3(0.06f, 0.32f, 0.06f), wood, null, null, false);
            stick.transform.rotation = Quaternion.FromToRotation(Vector3.up, dir);
            var tip = wallPoint + dir * 0.66f;
            var cup = Prim(PrimitiveType.Cylinder, "Copa", root, tip, new Vector3(0.16f, 0.06f, 0.16f), iron, null, null, false);
            cup.transform.rotation = Quaternion.FromToRotation(Vector3.up, dir);
            Prim(PrimitiveType.Cube, "Abrazadera", root, wallPoint + outDir * 0.02f, new Vector3(0.12f, 0.2f, 0.12f), iron, null, null, false)
                .transform.rotation = Quaternion.LookRotation(outDir);

            // llama
            var flame = new GameObject("Llama");
            flame.transform.SetParent(root, false);
            flame.transform.position = tip + Vector3.up * 0.04f;
            var ps = flame.AddComponent<ParticleSystem>();
            var main = ps.main;
            main.loop = true; main.prewarm = true; main.maxParticles = 80;
            main.startLifetime = new ParticleSystem.MinMaxCurve(0.45f, 0.8f);
            main.startSpeed = new ParticleSystem.MinMaxCurve(0.35f, 0.7f);
            main.startSize = new ParticleSystem.MinMaxCurve(0.22f, 0.38f);
            main.startRotation = new ParticleSystem.MinMaxCurve(-0.25f, 0.25f);
            main.gravityModifier = -0.15f;
            main.simulationSpace = ParticleSystemSimulationSpace.World;
            var em = ps.emission; em.rateOverTime = 38f;
            var sh = ps.shape; sh.shapeType = ParticleSystemShapeType.Cone; sh.angle = 6f; sh.radius = 0.05f;
            sh.rotation = new Vector3(-90f, 0f, 0f);
            var sz = ps.sizeOverLifetime; sz.enabled = true;
            sz.size = new ParticleSystem.MinMaxCurve(1f, new AnimationCurve(new Keyframe(0f, 0.6f), new Keyframe(0.25f, 1f), new Keyframe(1f, 0.1f)));
            var nz = ps.noise; nz.enabled = true; nz.strength = 0.35f; nz.frequency = 2.2f; nz.scrollSpeed = 1.6f;
            var fr = flame.GetComponent<ParticleSystemRenderer>();
            fr.sharedMaterial = Additive("M_Llama", FlameTexCached, new Color(9f, 6f, 4f, 1f));
            fr.renderMode = ParticleSystemRenderMode.Billboard;
            fr.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;

            // el aire que tiembla sobre la llama (distorsion de HDRP)
            var heat = new GameObject("Calor");
            heat.transform.SetParent(root, false);
            heat.transform.position = tip + Vector3.up * 0.35f;
            var hp = heat.AddComponent<ParticleSystem>();
            var hm = hp.main;
            hm.loop = true; hm.prewarm = true; hm.maxParticles = 20;
            hm.startLifetime = new ParticleSystem.MinMaxCurve(0.9f, 1.4f);
            hm.startSpeed = new ParticleSystem.MinMaxCurve(0.5f, 0.9f);
            hm.startSize = new ParticleSystem.MinMaxCurve(0.45f, 0.75f);
            hm.startRotation = new ParticleSystem.MinMaxCurve(0f, 6.28f);
            hm.simulationSpace = ParticleSystemSimulationSpace.World;
            var he = hp.emission; he.rateOverTime = 9f;
            var hs = hp.shape; hs.shapeType = ParticleSystemShapeType.Cone; hs.angle = 8f; hs.radius = 0.08f; hs.rotation = new Vector3(-90f, 0f, 0f);
            var hn = hp.noise; hn.enabled = true; hn.strength = 0.3f; hn.frequency = 1.5f;
            var hr = heat.GetComponent<ParticleSystemRenderer>();
            hr.sharedMaterial = HeatMaterialCached;
            hr.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;

            var l = AddLight("Luz_antorcha", root, LightType.Point, tip + Vector3.up * 0.25f + outDir * 0.1f, Vector3.zero, new Color(1f, 0.56f, 0.22f), 520f, 8f, 60f, null, false);
            l.gameObject.AddComponent<Flicker>();
        }

        static Texture2D _flame;
        static Texture2D FlameTexCached => _flame ? _flame : (_flame = FlameTex());
        static Material _heat;
        static Material HeatMaterialCached
        {
            get
            {
                if (_heat) return _heat;
                var m = Unlit("M_Aire_Caliente", new Color(0f, 0f, 0f, 0f));
                HDMaterial.SetSurfaceType(m, true);
                m.SetFloat("_DistortionEnable", 1f);
                m.SetFloat("_DistortionOnly", 1f);
                m.SetFloat("_DistortionDepthTest", 1f);
                m.SetTexture("_DistortionVectorMap", DistortionTex());
                m.SetFloat("_DistortionVectorScale", 2f);
                m.SetFloat("_DistortionVectorBias", -1f);
                m.SetFloat("_DistortionScale", 0.5f);
                m.SetFloat("_DistortionBlurScale", 0f); m.SetFloat("_DistortionBlurRemapMin", 0f); m.SetFloat("_DistortionBlurRemapMax", 0f);   // sin desenfoque: en Ligero no hay piramide de color y se veria negro
                m.SetFloat("_DistortionBlendMode", 0f);
                HDMaterial.ValidateMaterial(m);
                EditorUtility.SetDirty(m);
                return _heat = m;
            }
        }

        public static void ResetCache() { _flame = null; _heat = null; }

        // ---------- el meteorito ----------

        public static Meteor MeteorRig(Transform parent, float stairStartZ, float stairEndZ, Vector3 far, Vector3 near, Vector3 impact)
        {
            var root = new GameObject("Meteorito");
            root.transform.SetParent(parent, false);
            root.transform.position = far;
            var lava = LavaTex();
            var crust = Mat("M_Meteorito", new Color(0.12f, 0.08f, 0.07f), 0.15f, 0f, new Color(1f, 0.5f, 0.15f), 2600f);
            crust.SetTexture("_BaseColorMap", lava);
            crust.SetTexture("_EmissiveColorMap", lava);
            HDMaterial.ValidateMaterial(crust);
            var body = Prim(PrimitiveType.Sphere, "Cuerpo", root.transform, far, Vector3.one, crust, null, null, false);
            Static(body, false);
            body.GetComponent<Renderer>().shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
            var halo = Prim(PrimitiveType.Quad, "Halo_de_fuego", root.transform, far, Vector3.one, Additive("M_Halo_Meteorito", DotTex("T_Halo.png", 2.2f), new Color(6f, 2.2f, 0.6f, 1f)), null, null, false);
            Static(halo, false);
            // estela de fuego: particulas grandes alrededor del cuerpo
            var trail = new GameObject("Estela");
            trail.transform.SetParent(body.transform, false);
            var ps = trail.AddComponent<ParticleSystem>();
            var main = ps.main;
            main.loop = true; main.prewarm = true; main.maxParticles = 160;
            main.startLifetime = new ParticleSystem.MinMaxCurve(2.5f, 4f);
            main.startSpeed = new ParticleSystem.MinMaxCurve(0.25f, 0.5f);
            main.startSize = new ParticleSystem.MinMaxCurve(0.7f, 1.3f);
            main.startRotation = new ParticleSystem.MinMaxCurve(0f, 6.28f);
            main.scalingMode = ParticleSystemScalingMode.Hierarchy;
            main.simulationSpace = ParticleSystemSimulationSpace.Local;
            var em = ps.emission; em.rateOverTime = 40f;
            var sh = ps.shape; sh.shapeType = ParticleSystemShapeType.Sphere; sh.radius = 0.5f;
            var sz = ps.sizeOverLifetime; sz.enabled = true;
            sz.size = new ParticleSystem.MinMaxCurve(1f, new AnimationCurve(new Keyframe(0f, 0.8f), new Keyframe(1f, 0f)));
            var tr = trail.GetComponent<ParticleSystemRenderer>();
            tr.sharedMaterial = Additive("M_Fuego_Meteorito", FlameTexCached, new Color(14f, 6f, 2f, 1f));
            tr.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;

            var glow = AddLight("Luz_del_meteorito", root.transform, LightType.Directional, far, Vector3.zero, new Color(1f, 0.5f, 0.2f), 0.5f, 10f, 60f, null, false);
            var rumble = root.AddComponent<AudioSource>();
            rumble.playOnAwake = false; rumble.spatialBlend = 0f;
            var m = root.AddComponent<Meteor>();
            m.body = body.transform; m.halo = halo.transform; m.glowLight = glow; m.rumble = rumble;
            m.stairStartZ = stairStartZ; m.stairEndZ = stairEndZ;
            m.farPosition = far; m.nearPosition = near; m.impactPosition = impact;
            return m;
        }
    }
}
