using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering.HighDefinition;
using static Dream.EditorTools.Build.BuildKit;

namespace Dream.EditorTools.Build
{
    // 5 · El pasillo de las ondas, 20:40 (video 42 de dream/, 12-17 s). Un pasillo angosto de paredes rosadas que
    // baja por dos tramos de escalera; techo turquesa con lamparas de domo blancas, pasamanos oscuros, puertas
    // cerradas a la izquierda, carteles EXIT rojos y un piso brillante de ondas pastel. Abajo se bifurca: a la
    // derecha, una luz al final del pasillo (la salida a la playa); a la izquierda, un pasillo que devuelve,
    // sin aviso, al principio de la escalera.
    public static class S5Builder
    {
        const string DreamDir = DreamScene.Dir + "/Pasillo_Ondas/tex";
        const float HalfW = 1.2f, Rise = 0.17f, Run = 0.3f;
        const int Steps = 10;

        public static void Build()
        {
            var scene = NewScene();
            var a = Anchor(4, "El pasillo de las ondas", new Vector3(0f, 0.02f, -0.8f), 0f, 20.67f, 21.3f, 4f);
            a.ambienceKind = AmbienceKind.Ninguno; a.musicLowPass = 5200f; a.musicVolume = 0.7f; a.musicReverb = 0.65f; a.respawnBelowY = -12f;
            a.arrivalHint = "Baja las escaleras.";
            Cue(a.transform);
            var g = Group("Pasillo");

            // ---------- materiales (texturas de dream/) ----------
            var floor = Mat("M_Pasillo_Piso_Ondas", Color.white, 0.9f);
            floor.SetTexture("_BaseColorMap", SwirlTexture());
            floor.SetTexture("_NormalMap", Tex("wave_floor_normal.png", true)); floor.SetFloat("_NormalScale", 0.25f);
            floor.SetFloat("_UVBase", 4f);                    // proyeccion planar desde arriba: las ondas corren por todo el pasillo
            floor.SetFloat("_TexWorldScale", 1f / 6f);
            HDMaterial.ValidateMaterial(floor);
            var wall = Mat("M_Pasillo_Pared_Rosa", Color.white, 0.32f);
            wall.SetTexture("_BaseColorMap", Tex("wave_wall_albedo.png"));
            wall.SetTexture("_NormalMap", Tex("wave_paint_normal.png", true)); wall.SetFloat("_NormalScale", 0.35f);
            wall.SetFloat("_UVBase", 5f); wall.SetFloat("_TexWorldScale", 1f / 2f);
            HDMaterial.ValidateMaterial(wall);
            var ceiling = Mat("M_Pasillo_Techo_Turquesa", Color.white, 0.12f);
            ceiling.SetTexture("_BaseColorMap", Tex("wave_ceiling_albedo.png"));
            ceiling.SetTexture("_NormalMap", Tex("wave_paint_normal.png", true)); ceiling.SetFloat("_NormalScale", 0.9f);
            ceiling.SetFloat("_UVBase", 5f); ceiling.SetFloat("_TexWorldScale", 1f / 1.2f);
            HDMaterial.ValidateMaterial(ceiling);
            var rail = ScanMat("M_Pasamanos", "metal_plate", new Color(0.18f, 0.19f, 0.21f), 0.5f, 0.45f, 0.85f);
            var door = ScanMat("M_Puerta_Crema", "white_planks_clean", new Color(0.88f, 0.84f, 0.76f), 1.2f, 0.25f, 0.55f);
            var trim = ScanMat("M_Marco_Puerta", "white_planks_clean", new Color(0.74f, 0.68f, 0.54f), 0.8f, 0.3f, 0.6f);
            var dome = Mat("M_Lampara_Domo", new Color(1f, 0.97f, 0.92f), 0.6f, 0f, new Color(1f, 0.95f, 0.88f), 9000f);
            var exitMat = EmissiveTexMat("M_Cartel_Salida", Tex("wave_exit_albedo_dark.png"), 140f);
            var box = ScanMat("M_Caja_Cartel", "metal_plate", new Color(0.25f, 0.18f, 0.18f), 0.4f, 0.3f, 0.6f);

            // ---------- piso: descanso alto, dos tramos de escalera, descanso medio y el pasillo de abajo ----------
            float y1 = -Steps * Rise, y2 = 2f * y1;            // -1.7 y -3.4
            BoxMinMax("Piso_Arriba", g, new Vector3(-HalfW, -0.4f, -3f), new Vector3(HalfW, 0f, 6f), floor, SurfaceType.WetTile);
            Flight(g, floor, 6f, 0f);
            BoxMinMax("Piso_Descanso", g, new Vector3(-HalfW, y1 - 0.4f, 9f), new Vector3(HalfW, y1, 15f), floor, SurfaceType.WetTile);
            Flight(g, floor, 15f, y1);
            BoxMinMax("Piso_Abajo", g, new Vector3(-HalfW, y2 - 0.4f, 18f), new Vector3(HalfW, y2, 29.4f), floor, SurfaceType.WetTile);
            BoxMinMax("Piso_Rama_Der", g, new Vector3(HalfW, y2 - 0.4f, 27f), new Vector3(10f, y2, 29.4f), floor, SurfaceType.WetTile);
            BoxMinMax("Piso_Rama_Izq", g, new Vector3(-10f, y2 - 0.4f, 27f), new Vector3(-HalfW, y2, 29.4f), floor, SurfaceType.WetTile);

            // ---------- paredes rosadas ----------
            const float wallTop = 3.0f, wallBot = -3.8f;
            BoxMinMax("Pared_Izq", g, new Vector3(-HalfW - 0.12f, wallBot, -3f), new Vector3(-HalfW, wallTop, 27f), wall);
            BoxMinMax("Pared_Der", g, new Vector3(HalfW, wallBot, -3f), new Vector3(HalfW + 0.12f, wallTop, 27f), wall);
            BoxMinMax("Pared_Fondo_Arriba", g, new Vector3(-HalfW, -0.4f, -3.12f), new Vector3(HalfW, wallTop, -3f), wall);
            BoxMinMax("Pared_Frente_Bifurcacion", g, new Vector3(-10f, wallBot, 29.4f), new Vector3(10f, 0f, 29.52f), wall);
            BoxMinMax("Pared_Rama_Der", g, new Vector3(HalfW, wallBot, 26.88f), new Vector3(10f, 0f, 27f), wall);
            BoxMinMax("Pared_Rama_Izq", g, new Vector3(-10f, wallBot, 26.88f), new Vector3(-HalfW, 0f, 27f), wall);
            BoxMinMax("Pared_Final_Izq", g, new Vector3(-10.12f, wallBot, 27f), new Vector3(-10f, 0f, 29.4f), wall);

            // ---------- techo turquesa, que baja con la escalera ----------
            float c1 = 2.8f, c2 = y1 + 2.8f, c3 = y2 + 2.8f;
            // plano sobre los descansos e inclinado sobre cada tramo, como en el video
            BoxMinMax("Techo_1", g, new Vector3(-HalfW, c1, -3f), new Vector3(HalfW, c1 + 0.1f, 6f), ceiling);
            Slab("Techo_Tramo_1", g, ceiling, new Vector3(0f, c1, 6f), new Vector3(0f, c2, 9f));
            BoxMinMax("Techo_2", g, new Vector3(-HalfW, c2, 9f), new Vector3(HalfW, c2 + 0.1f, 15f), ceiling);
            Slab("Techo_Tramo_2", g, ceiling, new Vector3(0f, c2, 15f), new Vector3(0f, c3, 18f));
            BoxMinMax("Techo_3", g, new Vector3(-HalfW, c3, 18f), new Vector3(HalfW, c3 + 0.1f, 29.4f), ceiling);
            BoxMinMax("Techo_Ramas", g, new Vector3(-10f, c3, 27f), new Vector3(10f, c3 + 0.1f, 29.4f), ceiling);

            // ---------- pasamanos oscuros a los dos lados, con su soporte a la pared ----------
            foreach (float s in new[] { -1f, 1f })
            {
                float x = s * (HalfW - 0.07f);
                Rail(g, rail, new Vector3(x, 0.9f, 3f), new Vector3(x, 0.9f, 6f));
                Rail(g, rail, new Vector3(x, 0.9f, 6f), new Vector3(x, y1 + 0.9f, 9f));
                Rail(g, rail, new Vector3(x, y1 + 0.9f, 9f), new Vector3(x, y1 + 0.9f, 15f));
                Rail(g, rail, new Vector3(x, y1 + 0.9f, 15f), new Vector3(x, y2 + 0.9f, 18f));
                Rail(g, rail, new Vector3(x, y2 + 0.9f, 18f), new Vector3(x, y2 + 0.9f, 21f));
            }

            // ---------- puertas cerradas a la izquierda (y una a la derecha en el descanso) ----------
            DoorPanel(g, door, trim, -1f, 1.2f, 0f);
            DoorPanel(g, door, trim, -1f, 4.0f, 0f);
            DoorPanel(g, door, trim, -1f, 10.6f, y1);
            DoorPanel(g, door, trim, -1f, 13.2f, y1);
            DoorPanel(g, door, trim, 1f, 12.0f, y1);
            DoorPanel(g, door, trim, -1f, 22.5f, y2);

            // ---------- carteles EXIT rojos, cerca del techo ----------
            ExitSign(g, exitMat, box, new Vector3(-HalfW + 0.03f, c1 - 0.35f, 5.4f), 90f);
            ExitSign(g, exitMat, box, new Vector3(HalfW - 0.03f, c1 - 0.35f, 5.9f), -90f);
            ExitSign(g, exitMat, box, new Vector3(-HalfW + 0.03f, c2 - 0.35f, 14.5f), 90f);
            ExitSign(g, exitMat, box, new Vector3(-9.97f, c3 - 0.45f, 28.2f), 90f);

            // ---------- lamparas de domo: luz blanca calida que se repite y brilla en el piso mojado ----------
            var lamps = new[]
            {
                new Vector3(0f, c1, 0f), new Vector3(0f, c1, 3.2f), new Vector3(0f, c1, 6.6f),
                new Vector3(0f, c2, 10.6f), new Vector3(0f, c2, 13.8f), new Vector3(0f, c2, 17f),
                new Vector3(0f, c3, 20.5f), new Vector3(0f, c3, 23.8f), new Vector3(0f, c3, 27.2f),
                new Vector3(4.2f, c3, 28.2f), new Vector3(7.6f, c3, 28.2f), new Vector3(-4.2f, c3, 28.2f),
            };
            for (int i = 0; i < lamps.Length; i++)
            {
                var p = lamps[i];
                Prim(PrimitiveType.Sphere, $"Lampara_{i:00}", g, p - Vector3.up * 0.02f, new Vector3(0.62f, 0.16f, 0.62f), dome, null, null, false);
                bool shadows = i == 1 || i == 4 || i == 7;
                AddLight($"Luz_lampara_{i:00}", g, LightType.Point, p - Vector3.up * 0.18f, Vector3.zero, new Color(1f, 0.94f, 0.86f), 900f, 7f, 60f, null, shadows);
            }
            // (el fondo del pasillo izquierdo no tiene lampara: se queda en penumbra)

            // ---------- bifurcacion ----------
            // derecha: la luz al final del pasillo
            Prim(PrimitiveType.Quad, "Luz_al_final", g, new Vector3(9.95f, y2 + 1.4f, 28.2f), new Vector3(2.4f, 2.8f, 1f), Palette.BlindingLight, null, new Vector3(0f, 90f, 0f), false);
            AddLight("Luz_del_final", g, LightType.Rectangle, new Vector3(9.9f, y2 + 1.4f, 28.2f), new Vector3(0f, -90f, 0f), new Color(1f, 0.97f, 0.92f), 3500f, 14f, 60f, new Vector2(2.3f, 2.7f), false);
            // izquierda: un pasillo que devuelve al principio de la escalera
            var top = Point("Otra_vez_arriba", a.transform, new Vector3(0f, 0.02f, 0.4f), 0f);
            var loop = new GameObject("Pasillo_que_vuelve");
            loop.transform.SetParent(g, false);
            loop.transform.position = new Vector3(-8.6f, y2 + 1.2f, 28.2f);
            var lb = loop.AddComponent<BoxCollider>(); lb.isTrigger = true; lb.size = new Vector3(0.6f, 2.4f, 2.4f);
            loop.AddComponent<LoopBack>().target = top;

            Memory(a.transform, new Vector3(0f, y2 + 1.05f, 27.9f), "Todas las puertas daban al mismo pasillo; solo una tenía luz.");
            CheckpointAt(a.transform, new Vector3(0f, y1 + 0.05f, 12f), 0f, new Vector3(2.4f, 2.4f, 1f));

            // ---------- llegada: abre los ojos arriba de la escalera ----------
            var w0 = Shot(2.2f, "negro, despierta arriba");
            w0.fadeColor = Color.black; w0.fadeInSeconds = 2.2f;
            w0.from = CamPoint("Cam_Arriba_A", a.transform, new Vector3(0.5f, 1.9f, -2.6f), new Vector3(0f, -0.5f, 8f));
            w0.to = CamPoint("Cam_Arriba_B", a.transform, new Vector3(0.45f, 1.8f, -2.2f), new Vector3(0f, -0.8f, 8f));
            w0.focalLength = 24f;
            var w1 = Shot(4f, "mira escaleras abajo");
            w1.from = CamPoint("Cam_Escalera_A", a.transform, new Vector3(-0.6f, y1 + 1.2f, 10.5f), new Vector3(0f, 1.2f, 2f));
            w1.to = CamPoint("Cam_Escalera_B", a.transform, new Vector3(-0.5f, y1 + 1.3f, 10f), new Vector3(0f, 1.2f, 2f));
            w1.lookAtActorHead = true; w1.focalLength = 35f;
            w1.actorWalkTo = Point("Borde_escalera", a.transform, new Vector3(0f, 0.02f, 4.6f)); w1.actorSpeed = 0.9f;
            w1.headLookAt = Point("Abajo", a.transform, new Vector3(0f, y2, 26f));
            a.arrival = Sequence("Cine_El_Pasillo", a.transform, w0, w1);

            // ---------- salida: camina hacia la luz ----------
            var d1 = Shot(4.5f, "camina hacia la luz");
            d1.from = CamPoint("Cam_Luz_A", a.transform, new Vector3(1.6f, y2 + 1.7f, 28.9f), new Vector3(9.9f, y2 + 1.3f, 28.2f));
            d1.to = CamPoint("Cam_Luz_B", a.transform, new Vector3(2.8f, y2 + 1.6f, 28.7f), new Vector3(9.9f, y2 + 1.3f, 28.2f));
            d1.lookAt = Point("Mira_luz", a.transform, new Vector3(9.9f, y2 + 1.3f, 28.2f)); d1.focalLength = 28f;
            d1.actorWalkTo = Point("Dentro_de_la_luz", a.transform, new Vector3(9.4f, y2 + 0.02f, 28.2f)); d1.actorSpeed = 1.1f;
            d1.fadeColor = Color.white; d1.fadeOutSeconds = 2f;
            Gate("La_luz_del_final", a.transform, new Vector3(8.4f, y2 + 1.2f, 28.2f), new Vector3(0.8f, 2.4f, 2.4f), Sequence("Cine_La_Luz", a.transform, d1));

            // ---------- aire: un poco de niebla para que las lamparas tengan halo; el cielo no entra ----------
            GlobalVolume("Ambiente_Pasillo", a.transform, Profile("S5_Pasillo", p =>
            {
                Fog(p, 38f, 6f, new Color(1f, 0.93f, 0.9f), true, -6f);
                NightSky(p, 0.2f);
                ExposureLimits(p, 2f, 9f, 0.2f);
                var ind = p.Add<IndirectLightingController>();
                ind.indirectDiffuseLightingMultiplier.Override(0.15f);
                ind.reflectionLightingMultiplier.Override(0.5f);
            }), 1f);
            Save(scene, "S5_Pasillo");
        }

        static Texture2D Tex(string file, bool normal = false)
        {
            string path = $"{DreamDir}/{file}";
            var imp = AssetImporter.GetAtPath(path) as TextureImporter;
            if (imp != null && normal && imp.textureType != TextureImporterType.NormalMap) { imp.textureType = TextureImporterType.NormalMap; imp.SaveAndReimport(); }
            return AssetDatabase.LoadAssetAtPath<Texture2D>(path);
        }

        // Un tramo de 10 peldanos que baja hacia +Z desde (z0, yTop).
        static void Flight(Transform g, Material m, float z0, float yTop)
        {
            for (int i = 0; i < Steps; i++)
            {
                float y = yTop - (i + 1) * Rise, z = z0 + i * Run;
                BoxMinMax($"Peldano_{z0:00}_{i:00}", g, new Vector3(-HalfW, y - 0.4f, z), new Vector3(HalfW, y, z + Run), m, SurfaceType.WetTile);
            }
        }

        // Losa de techo inclinada entre dos puntos del eje del pasillo (cara de abajo en la linea a-b).
        static void Slab(string name, Transform g, Material m, Vector3 a, Vector3 b)
        {
            var d = b - a;
            var go = Box(name, g, (a + b) * 0.5f, new Vector3(HalfW * 2f, 0.1f, d.magnitude + 0.06f), m);
            go.transform.rotation = Quaternion.LookRotation(d.normalized, Vector3.up);
            go.transform.position += go.transform.up * 0.05f;
        }

        static void Rail(Transform g, Material m, Vector3 a, Vector3 b)
        {
            var d = b - a;
            var go = Prim(PrimitiveType.Cylinder, "Pasamanos", g, (a + b) * 0.5f, new Vector3(0.045f, d.magnitude * 0.5f, 0.045f), m, null, null, false);
            go.transform.rotation = Quaternion.FromToRotation(Vector3.up, d.normalized);
            foreach (var p in new[] { a, b })
            {
                float wx = Mathf.Sign(p.x) * HalfW;
                Prim(PrimitiveType.Cylinder, "Soporte", g, new Vector3((p.x + wx) * 0.5f, p.y - 0.04f, p.z), new Vector3(0.02f, Mathf.Abs(wx - p.x) * 0.5f, 0.02f), m, null, new Vector3(0f, 0f, 90f), false);
            }
        }

        // Puerta cerrada empotrada en la pared (side -1 izquierda, +1 derecha).
        static void DoorPanel(Transform g, Material panel, Material trim, float side, float z, float floorY)
        {
            float x = side * (HalfW - 0.01f);
            Box("Puerta", g, new Vector3(x, floorY + 1.05f, z), new Vector3(0.04f, 2.1f, 0.92f), panel);
            Box("Marco_Arriba", g, new Vector3(x, floorY + 2.14f, z), new Vector3(0.06f, 0.08f, 1.08f), trim);
            Box("Marco_A", g, new Vector3(x, floorY + 1.07f, z - 0.5f), new Vector3(0.06f, 2.14f, 0.08f), trim);
            Box("Marco_B", g, new Vector3(x, floorY + 1.07f, z + 0.5f), new Vector3(0.06f, 2.14f, 0.08f), trim);
            Prim(PrimitiveType.Cylinder, "Manija", g, new Vector3(x - side * 0.05f, floorY + 1.0f, z + 0.34f), new Vector3(0.03f, 0.06f, 0.03f), trim, null, new Vector3(0f, 0f, 90f), false);
        }

        // Cartel EXIT sobre la pared (yaw 90 en la pared izquierda, -90 en la derecha), con su caja y un brillo rojo.
        static void ExitSign(Transform g, Material sign, Material box, Vector3 pos, float yaw)
        {
            var q = Prim(PrimitiveType.Quad, "Cartel_EXIT", g, pos, new Vector3(0.36f, 0.18f, 1f), sign, null, new Vector3(0f, yaw, 0f), false);
            var outward = -q.transform.forward;                 // el quad se ve desde -forward
            Box("Caja_EXIT", g, pos - outward * 0.026f, new Vector3(0.38f, 0.2f, 0.05f), box, null, yaw);
            AddLight("Brillo_EXIT", g, LightType.Point, pos + outward * 0.15f, Vector3.zero, new Color(1f, 0.15f, 0.1f), 25f, 1.5f, 60f, null, false);
        }

        // El piso del video: fondo turquesa con cintas de colores pastel que serpentean a lo largo del pasillo.
        // Baldosa de 6 m; las cintas viven alrededor de u = 0 (el centro del pasillo) y se repiten sin costura.
        static Texture2D SwirlTexture()
        {
            string path = TexDir + "/T_Pasillo_Ondas.png";
            const int n = 1024;
            var t = new Texture2D(n, n, TextureFormat.RGB24, false);
            var teal = new Color(0.36f, 0.6f, 0.58f);
            Color[] band = { new(0.93f, 0.79f, 0.45f), new(0.92f, 0.55f, 0.5f), new(0.9f, 0.62f, 0.72f), new(0.6f, 0.58f, 0.8f), new(0.55f, 0.75f, 0.85f) };
            for (int y = 0; y < n; y++)
            {
                float v = y / (float)n;
                for (int x = 0; x < n; x++)
                {
                    float u = x / (float)n;
                    var c = teal * (0.96f + 0.04f * Mathf.PerlinNoise(u * 40f, v * 40f));
                    // dos cintas: una ancha que serpentea y otra mas fina a contrafase
                    for (int r = 0; r < 2; r++)
                    {
                        float center = (r == 0 ? 0f : 0.1f) + (r == 0 ? 0.11f : 0.08f) * Mathf.Sin(2f * Mathf.PI * (v + r * 0.37f))
                                       + 0.03f * Mathf.Sin(6f * Mathf.PI * v + r);
                        float du = Mathf.Repeat(u - center + 0.5f, 1f) - 0.5f;
                        float width = r == 0 ? 0.16f : 0.09f;
                        float k = (du + width * 0.5f) / width;
                        if (k >= 0f && k < 1f) c = band[(int)(k * band.Length) % band.Length];
                    }
                    t.SetPixel(x, y, c);
                }
            }
            System.IO.File.WriteAllBytes(System.IO.Path.Combine(System.IO.Directory.GetCurrentDirectory(), path), t.EncodeToPNG());
            Object.DestroyImmediate(t);
            AssetDatabase.ImportAsset(path);
            var imp = (TextureImporter)AssetImporter.GetAtPath(path);
            imp.wrapMode = TextureWrapMode.Repeat; imp.maxTextureSize = 1024; imp.SaveAndReimport();
            return AssetDatabase.LoadAssetAtPath<Texture2D>(path);
        }
    }
}
