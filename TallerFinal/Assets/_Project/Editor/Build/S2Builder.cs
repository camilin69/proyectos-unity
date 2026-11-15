using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering.HighDefinition;
using static Dream.EditorTools.Build.BuildKit;

namespace Dream.EditorTools.Build
{
    // 2 · La pradera infinita con puertas sueltas, 09:00. Una de las puertas da a otro cielo: el recuerdo esta a su
    // pie y al cruzarla el viento levanta al sonador.
    public static class S2Builder
    {
        // Vegetacion escaneada (Poly Haven, CC0), mas grande de lo normal: es un sueno. El camino hacia la puerta del otro cielo queda despejado.
        // Bosque en las colinas: tarjetas con la imagen del arbol real (renderizado en Blender), en arboledas que se
        // espesan hacia el horizonte.
        internal static void Forest(Transform root, System.Func<float, float, float> G) =>
            Forest(root, G, new Vector2(0f, 18f), 48f, 265f, 520, (x, z) => Mathf.Abs(x) < 10f && z > -10f && z < 70f);

        // Arboledas de tarjetas alrededor de un centro, entre dos radios; skip deja libres los caminos.
        internal static void Forest(Transform root, System.Func<float, float, float> G, Vector2 center, float rMin, float rMax,
                                    int count, System.Func<float, float, bool> skip)
        {
            var forest = Group("Bosque", root);
            forest.gameObject.AddComponent<Billboards>();
            var mats = new Material[3];
            for (int i = 0; i < 3; i++)
            {
                string path = $"{Root}/Art/Textures/Impostores/arbol_isla_{i}.png";
                var imp = (TextureImporter)AssetImporter.GetAtPath(path);
                if (!imp.alphaIsTransparency) { imp.alphaIsTransparency = true; imp.SaveAndReimport(); }
                var m = Mat($"M_Arbol_Impostor_{i}", new Color(1.05f, 1.08f, 1f), 0.08f, 0f, null, 0f, false, true);
                m.SetTexture("_BaseColorMap", AssetDatabase.LoadAssetAtPath<Texture2D>(path));
                m.SetFloat("_AlphaCutoffEnable", 1f); m.SetFloat("_AlphaCutoff", 0.45f);
                m.enableInstancing = true;
                HDMaterial.ValidateMaterial(m);
                mats[i] = m;
            }
            var rng = new System.Random(21);
            for (int n = 0; n < count; n++)
            {
                float ang = (float)(rng.NextDouble() * Mathf.PI * 2f);
                float r = Mathf.Lerp(rMin, rMax, Mathf.Sqrt((float)rng.NextDouble()));
                float x = Mathf.Cos(ang) * r + center.x, z = Mathf.Sin(ang) * r + center.y;
                if (skip != null && skip(x, z)) continue;                                      // caminos y vistas despejados
                if (Mathf.PerlinNoise(x * 0.018f + 4f, z * 0.018f) < 0.38f - r / 900f) continue; // arboledas, no un tablero
                float k = 2.2f + (float)rng.NextDouble() * 1.6f;
                var card = Prim(PrimitiveType.Quad, $"Arbol_{n:000}", forest, new Vector3(x, G(x, z) + 1.74f * k - 0.15f, z),
                                new Vector3(5.6f * k, 5.6f * k, 1f), mats[rng.Next(3)], null, null, false);
                GameObjectUtility.SetStaticEditorFlags(card, 0);
            }
        }

        // Cookie del sol: manchas suaves y grandes, como las sombras de nubes de algodon pasando sobre el campo.
        static Texture2D CloudShadows()
        {
            string path = TexDir + "/T_Sombras_Nubes.png";
            const int n = 512;
            var t = new Texture2D(n, n, TextureFormat.RGBA32, false);
            for (int y = 0; y < n; y++)
                for (int x = 0; x < n; x++)
                {
                    float u = x / (float)n, v = y / (float)n;
                    // ruido periodico (suma de senos desfasados) para que el cookie se repita sin costura
                    float c = Mathf.Sin(u * 6.283f * 2f + Mathf.Sin(v * 6.283f) * 1.3f) * Mathf.Sin(v * 6.283f * 2f + Mathf.Sin(u * 6.283f * 2f) * 0.9f)
                              + 0.5f * Mathf.Sin(u * 6.283f * 5f + v * 6.283f * 3f);
                    float shade = Mathf.Lerp(1f, 0.42f, Mathf.SmoothStep(0.35f, 1.0f, c));
                    t.SetPixel(x, y, new Color(shade, shade, shade, 1f));
                }
            System.IO.File.WriteAllBytes(System.IO.Path.Combine(System.IO.Directory.GetCurrentDirectory(), path), t.EncodeToPNG());
            Object.DestroyImmediate(t);
            AssetDatabase.ImportAsset(path);
            var imp = (TextureImporter)AssetImporter.GetAtPath(path);
            imp.wrapMode = TextureWrapMode.Repeat; imp.sRGBTexture = false; imp.SaveAndReimport();
            return AssetDatabase.LoadAssetAtPath<Texture2D>(path);
        }

        static void Dress(Transform root, System.Func<float, float, float> G)
        {
            var veg = Group("Vegetacion", root);
            var field = veg.gameObject.AddComponent<WindField>();
            bool Path(float x, float z) => Mathf.Abs(x) < 1.4f && z > -3f && z < 42f;
            System.Func<System.Random, Vector2?> Near(float radius, float minR = 0f, float patch = 0.22f) => rng =>
            {
                float ang = (float)(rng.NextDouble() * Mathf.PI * 2f);
                float r = Mathf.Lerp(minR, radius, Mathf.Sqrt((float)rng.NextDouble()));
                float x = Mathf.Cos(ang) * r, z = Mathf.Sin(ang) * r + 18f;
                if (Path(x, z)) return null;
                if (Mathf.PerlinNoise(x * 0.07f + 3f, z * 0.07f) < patch) return null;   // manchas, como crece de verdad
                return new Vector2(x, z);
            };
            // pasto alto y silvestre por todas partes, flores en manchas, arbustos que se mecen
            ScatterInstanced(field, "grass_medium_02", 4200, Near(70f, 0f, 0.3f), G, new Vector2(2.2f, 3.0f), 1, 1f);
            ScatterInstanced(field, "flower_gazania", 2200, Near(50f, 0f, 0.42f), G, new Vector2(2.0f, 2.9f), 3, 0.8f);
            ScatterInstanced(field, "flower_ursinia", 1400, Near(50f, 0f, 0.45f), G, new Vector2(2.0f, 2.9f), 4, 0.8f);
            ScatterInstanced(field, "dandelion_01", 600, Near(45f, 0f, 0.35f), G, new Vector2(2.0f, 2.6f), 5, 0.9f);
            ScatterInstanced(field, "shrub_02", 70, Near(110f, 18f, 0.3f), G, new Vector2(0.9f, 1.4f), 6, 0.25f, true);
            Scatter("boulder_01", veg, 9, Near(80f, 12f), G, new Vector2(0.8f, 1.8f), 7, 0.004f, SurfaceType.Stone, true);
            PolyModel("tree_stump_01", veg, new Vector3(-7f, G(-7f, 12f), 12f), 35f, SurfaceType.Wood);
            Forest(root, G);
            var shadows = new GameObject("Sombras_de_nubes").AddComponent<SunCookie>();
            shadows.transform.SetParent(root, false);
            shadows.cookie = CloudShadows();
            // una banca sola en medio del campo, mirando la puerta del otro cielo
            PolyModel("painted_wooden_bench", veg, new Vector3(4.5f, G(4.5f, 27f), 27f), 200f, SurfaceType.Wood);
        }

        public static void Build()
        {
            var scene = NewScene();
            var terrain = MakeTerrain("T_Pradera", null, new Vector3(-300f, 0f, -300f), new Vector3(600f, 90f, 600f), 257,
                (u, v) =>
                {
                    // valle suave donde se camina y colinas redondas alrededor, cada vez mas altas hacia el horizonte
                    float r = Mathf.Sqrt((u - 0.5f) * (u - 0.5f) + (v - 0.5f) * (v - 0.5f));
                    float hills = Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(0.16f, 0.46f, r))
                                  * (0.18f + 0.32f * Mathf.PerlinNoise(u * 5f + 2f, v * 5f + 9f));
                    return 0.08f + 0.022f * Mathf.PerlinNoise(u * 4f, v * 4f) + 0.01f * Mathf.PerlinNoise(u * 13f + 5f, v * 13f + 3f) + hills;
                },
                ("Pasto", new Color(0.4f, 0.82f, 0.26f), 5f), ("Flores", new Color(0.46f, 0.86f, 0.3f), 4f));
            PaintLayer(terrain, 1, (u, v) => (Mathf.PerlinNoise(u * 9f, v * 9f) - 0.6f) * 5f);
            terrain.gameObject.AddComponent<TerrainSurfaces>().layerSurfaces = new[] { SurfaceType.Grass, SurfaceType.Grass };
            float G(float x, float z) => Ground(terrain, x, z);

            var a = Anchor(1, "La pradera", new Vector3(0f, G(0f, 0f) + 0.05f, 0f), 0f, 9f, 11.5f, 5f);
            a.ambienceKind = AmbienceKind.Viento; a.musicLowPass = 22000f; a.musicVolume = 0.85f; a.musicReverb = 0.05f; a.respawnBelowY = -20f;
            var cue = Cue(a.transform);
            CheckpointAt(a.transform, a.spawn.position, 0f, new Vector3(3f, 3f, 3f));

            // puertas sueltas en el pasto
            var doors = Group("Puertas");
            var rng = new System.Random(7);
            Material[] frames = { Palette.Pink, Palette.MintTile, Palette.Cream, Palette.Wood };
            for (int i = 0; i < 16; i++)
            {
                float ang = (float)(rng.NextDouble() * Mathf.PI * 2f), r = 14f + (float)rng.NextDouble() * 80f;
                float x = Mathf.Cos(ang) * r, z = Mathf.Sin(ang) * r;
                if (Mathf.Abs(x) < 6f && z > -4f && z < 48f) continue;      // el camino a la puerta especial queda libre
                Door($"Puerta_{i:00}", doors, new Vector3(x, G(x, z), z), (float)rng.NextDouble() * 360f,
                     frames[i % frames.Length], frames[(i + 2) % frames.Length], 1f, 2.2f, rng.NextDouble() < 0.4);
            }

            // la puerta que da a otro cielo
            float gz = G(0f, 40f);
            var special = Door("Puerta_Otro_Cielo", doors, new Vector3(0f, gz, 40f), 0f, Palette.Cream, Palette.MintTile, 1f, 2.2f, true);
            var otherSky = EmissiveTexMat("M_Otro_Cielo", GradientTex("T_Otro_Cielo", new Color(1f, 0.78f, 0.62f), new Color(0.55f, 0.5f, 0.95f)), 2500f);
            Prim(PrimitiveType.Quad, "Otro_cielo", special.transform, new Vector3(0f, gz + 1.1f, 40.0f), new Vector3(1f, 2.2f, 1f), otherSky, null, Vector3.zero, false);
            AddLight("Resplandor", special.transform, LightType.Point, new Vector3(0f, gz + 1.2f, 39.4f), Vector3.zero, new Color(1f, 0.8f, 0.85f), 900f, 9f);
            Memory(a.transform, new Vector3(0.8f, gz + 0.35f, 39.2f), "Una puerta que no lleva a ninguna parte, y aun así quisiste abrirla.");

            // salida: el viento lo levanta
            var skyPoint = Point("Mira_cielo", a.transform, new Vector3(0f, gz + 25f, 90f));
            var d1 = Shot(3.5f, "camina hacia la puerta del otro cielo");
            d1.from = CamPoint("Cam_Vuelo_A", a.transform, new Vector3(2.8f, gz + 0.5f, 35.5f), Vector3.zero);
            d1.lookAtActorHead = true; d1.focalLength = 28f; d1.headLookAt = skyPoint;
            d1.actorWalkTo = Point("En_la_puerta", a.transform, new Vector3(0f, gz, 40.6f)); d1.actorSpeed = 1.1f;
            var d2 = Shot(4.5f, "una brisa levanta la tela; sube");
            d2.from = CamPoint("Cam_Vuelo_B", a.transform, new Vector3(1.5f, gz + 0.3f, 43f), Vector3.zero);
            d2.to = CamPoint("Cam_Vuelo_C", a.transform, new Vector3(2.5f, gz + 0.6f, 44f), Vector3.zero);
            d2.lookAtActorHead = true; d2.focalLength = 24f;
            d2.actorVelocity = new Vector3(0f, 3.2f, 1.2f); d2.actorTrigger = "Jump";
            d2.fadeColor = Color.white; d2.fadeOutSeconds = 2.2f;
            OnStart(d2, cue.Duck);
            Gate("Paso_Otro_Cielo", a.transform, new Vector3(0f, gz + 1.1f, 40.3f), new Vector3(1f, 2.2f, 0.6f), Sequence("Cine_El_Vuelo", a.transform, d1, d2));

            // llegada: la luz se disuelve y aparece la pradera
            float g0 = G(0f, 0f);
            var w1 = Shot(7f, "el blanco se disuelve; la camara orbita la pradera");
            w1.fadeColor = Color.white; w1.fadeInSeconds = 3.5f;
            w1.orbitCenter = Point("Centro_orbita", a.transform, new Vector3(0f, g0 + 1.3f, 0f));
            w1.from = CamPoint("Cam_Pradera_A", a.transform, new Vector3(0f, g0 + 1.7f, -3.8f), Vector3.zero);
            w1.orbitDegrees = 80f; w1.focalLength = 24f;
            w1.headLookAt = Point("Mira_puertas", a.transform, new Vector3(0f, g0 + 1.6f, 30f));
            var w2 = Shot(2.5f, "vuelve a sus ojos");
            w2.to = CamPoint("Cam_Pradera_B", a.transform, new Vector3(0.3f, g0 + 1.66f, -0.6f), new Vector3(0f, g0 + 1.5f, 30f));
            w2.focalLength = 30f;
            a.arrival = Sequence("Cine_Llegada_Pradera", a.transform, w1, w2);

            GlobalVolume("Ambiente_Pradera", a.transform, Profile("S2_Pradera", p =>
            {
                // el cielo de nubes de dream/ con nubes de algodon de azucar: rosas, magenta, moradas y violetas
                HdriSkyOverride(p, Hdri("dream_cotton_sky.png"), 0f, 26000f);
                // euforia: neblina luminosa que hace brillar las colinas, bloom amplio y color saturado y calido
                Fog(p, 650f, 55f, new Color(1f, 0.97f, 0.93f));
                var bl = p.Add<Bloom>(); bl.intensity.Override(0.45f); bl.scatter.Override(0.8f); bl.threshold.Override(0.8f);
                var ca = p.Add<ColorAdjustments>(); ca.saturation.Override(28f); ca.contrast.Override(6f); ca.postExposure.Override(0.35f);
                var wb = p.Add<WhiteBalance>(); wb.temperature.Override(5f); wb.tint.Override(3f);
            }), 1f);
            Dress(a.transform, G);
            CottonSky(null, new Vector3(0f, 0f, 18f), 46, 260f, 1300f, 140f, 320f, 9f, 16f,
                      new[] { new Color(1f, 0.72f, 0.86f), new Color(0.95f, 0.55f, 0.85f), new Color(0.78f, 0.6f, 0.95f), new Color(0.66f, 0.55f, 0.95f), new Color(1f, 0.88f, 0.94f) }, 61);
            Save(scene, "S2_Pradera");
        }
    }
}
