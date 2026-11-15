using UnityEngine;
using UnityEngine.Rendering.HighDefinition;
using static Dream.EditorTools.Build.BuildKit;

namespace Dream.EditorTools.Build
{
    // 6 · La playa del oceano infinito, 21:20. Cae sobre una hoja de palmera y queda mirando el mar; tierra adentro,
    // un pasillo corto de palmeras altisimas que tapan el cielo lleva al recuerdo y a un laberinto de setos podados
    // como murallas de castillo. Al entrar todo se oscurece; del otro lado, un tunel bajito, de la altura del
    // sonador, con una luz al final.
    public static class S6Builder
    {
        public static void Build()
        {
            var scene = NewScene();
            const float y0 = -6f, height = 30f, oz = -300f, len = 700f;
            float WorldY(float z, float x)
            {
                float y;
                if (z < -60f) y = -3f - (-60f - z) * 0.03f;
                else if (z < -40f) y = Mathf.Lerp(-3f, 0.3f, (z + 60f) / 20f);
                else if (z < 0f) y = Mathf.Lerp(0.3f, 1f, (z + 40f) / 40f);
                else y = 1f + Mathf.Min(z, 120f) / 120f * 1.5f;
                return y + Mathf.PerlinNoise(x * 0.02f + 10f, z * 0.02f) * 1.2f * Mathf.Clamp01((z + 40f) / 60f);
            }
            var terrain = MakeTerrain("T_Playa", null, new Vector3(-400f, y0, oz), new Vector3(800f, height, len), 257,
                (u, v) => (WorldY(oz + v * len, -400f + u * 800f) - y0) / height,
                ("Arena", new Color(0.93f, 0.86f, 0.72f), 5f), ("Bosque", new Color(0.3f, 0.36f, 0.26f), 5f));
            PaintLayer(terrain, 1, (u, v) => ((oz + v * len) - 25f) / 25f + (Mathf.PerlinNoise(u * 20f, v * 20f) - 0.5f));
            terrain.gameObject.AddComponent<TerrainSurfaces>().layerSurfaces = new[] { SurfaceType.Sand, SurfaceType.Leaves };
            float G(float x, float z) => Ground(terrain, x, z);

            var a = Anchor(5, "La playa infinita", new Vector3(1.6f, G(1.6f, -21f) + 0.05f, -21f), 180f, 21.33f, 22.4f, 5f);
            a.ambienceKind = AmbienceKind.Mar; a.ambienceVolume = 0.8f; a.musicLowPass = 9000f; a.musicVolume = 0.75f; a.musicReverb = 0.12f; a.respawnBelowY = -20f;
            var cue = Cue(a.transform);

            var oceanGo = new GameObject("Oceano");
            oceanGo.transform.position = new Vector3(0f, -6f, -500f);
            oceanGo.AddComponent<BoxCollider>().size = new Vector3(2000f, 12f, 920f);
            oceanGo.AddComponent<WaterZone>();
            Water("Oceano_infinito", null, UnityEngine.Rendering.HighDefinition.WaterSurfaceType.OceanSeaLake, Vector3.zero, Vector2.zero);
            ShootingStarsIn(a.transform);

            // pasillo corto de palmeras altisimas, inclinadas hacia el camino: sus copas se cierran arriba
            var palms = Group("Palmeras");
            var rng = new System.Random(11);
            Palm(palms, new Vector3(-0.6f, G(-0.6f, -16.5f), -16.5f), 3.6f, -14f, rng, out var leafTop);
            var landingLeaf = Box("Hoja_de_aterrizaje", palms, new Vector3(0.4f, G(0.4f, -19.2f) + 2.3f, -19.2f), new Vector3(1.0f, 0.06f, 3.2f), Palette.Leaf, SurfaceType.Leaves);
            landingLeaf.transform.rotation = Quaternion.Euler(18f, 10f, 0f);
            for (float z = 4f; z < 42f; z += 3.2f)
                for (int s = -1; s <= 1; s += 2)
                    for (int k = 0; k < 2; k++)
                    {
                        float x = s * (2.3f + k * 3.2f + (float)rng.NextDouble() * 1.2f);
                        float zz = z + (float)(rng.NextDouble() - 0.5) * 2f;
                        float yawIn = s < 0 ? 90f : -90f;                       // se inclinan hacia el camino
                        Palm(palms, new Vector3(x, G(x, zz), zz), 14f + (float)rng.NextDouble() * 8f, 7f + (float)rng.NextDouble() * 8f, rng, out _, yawIn, 14);
                    }
            Memory(a.transform, new Vector3(0.6f, G(0.6f, 30f) + 1.0f, 30f), "El mar sigue hablando aunque nadie lo escuche.");

            // laberinto de setos podados con almenas (z 46..70); adentro todo se oscurece
            const float u = 1.7f, mz0 = 46f; const int cells = 7, n = cells * 2 + 1;
            float mx0 = -n * u * 0.5f;
            var wall = Maze(cells, 23);
            var hedge = ScanMat("M_Seto_Podado", "leafy_grass", new Color(0.32f, 0.5f, 0.3f), 1.1f, 0f, 0.25f);
            var maze = Group("Laberinto");
            for (int i = 0; i < n; i++)
                for (int j = 0; j < n; j++)
                {
                    if (!wall[i, j]) continue;
                    float x = mx0 + (i + 0.5f) * u, z = mz0 + (j + 0.5f) * u, g = G(x, z);
                    BoxMinMax($"Seto_{i}_{j}", maze, new Vector3(x - u * 0.5f, g - 1f, z - u * 0.5f), new Vector3(x + u * 0.5f, g + 3.1f, z + u * 0.5f), hedge, SurfaceType.Leaves);
                    if ((i + j) % 2 == 0)                                     // almenas: el seto podado como muralla
                        Box($"Almena_{i}_{j}", maze, new Vector3(x, g + 3.4f, z), new Vector3(u * 0.55f, 0.6f, u * 0.55f), hedge);
                }
            float mazeTop = mz0 + n * u;
            var dark = Profile("S6_Laberinto_Oscuro", p =>
            {
                Fog(p, 9f, 40f, new Color(0.05f, 0.07f, 0.06f));
                var ca = p.Add<ColorAdjustments>(); ca.postExposure.Override(-1.3f); ca.saturation.Override(-35f);
            });
            LocalVolume("Laberinto_que_oscurece", a.transform, new Vector3(0f, G(0f, 62f) + 5f, (mz0 + mazeTop) * 0.5f + 8f), new Vector3(n * u + 4f, 30f, n * u + 18f), dark, 2f, 4f);

            // el tunel bajito: 2 m de alto, 1.2 de ancho, paredes oscuras y la luz al final
            var tunnel = Group("Tunel");
            var stone = Mat("M_Tunel_Oscuro", new Color(0.07f, 0.07f, 0.075f), 0.35f);
            float t0 = mazeTop, t1 = mazeTop + 14f;
            for (float z = t0 - 0.4f; z < t1; z += 2f)
            {
                float g = G(0f, z + 1f);
                BoxMinMax("Pared_I", tunnel, new Vector3(-0.85f, g - 1f, z), new Vector3(-0.6f, g + 2.25f, z + 2f), stone);
                BoxMinMax("Pared_D", tunnel, new Vector3(0.6f, g - 1f, z), new Vector3(0.85f, g + 2.25f, z + 2f), stone);
                BoxMinMax("Techo", tunnel, new Vector3(-0.85f, g + 2.0f, z), new Vector3(0.85f, g + 2.25f, z + 2f), stone);
            }
            float ge = G(0f, t1);
            BoxMinMax("Tapa_final", tunnel, new Vector3(-0.85f, ge - 1f, t1 + 0.1f), new Vector3(0.85f, ge + 2.25f, t1 + 0.3f), stone);
            Prim(PrimitiveType.Quad, "Luz_al_final", tunnel, new Vector3(0f, ge + 1f, t1 + 0.08f), new Vector3(1.2f, 2f, 1f), Palette.BlindingLight, null, Vector3.zero, false);
            AddLight("Luz_del_tunel", tunnel, LightType.Rectangle, new Vector3(0f, ge + 1f, t1 + 0.05f), new Vector3(0f, 180f, 0f), new Color(1f, 0.97f, 0.92f), 1400f, 16f, 60f, new Vector2(1.1f, 1.9f), false);
            var lightPoint = Point("Mira_luz", a.transform, new Vector3(0f, ge + 1f, t1));

            // llegada: cae sobre la hoja de palmera, rueda al suelo y queda mirando el mar
            float gs = G(1.6f, -21f);
            var w0 = Shot(1.2f, "negro");
            w0.from = CamPoint("Cam_Hoja_A", a.transform, new Vector3(7f, gs + 2.5f, -12.5f), new Vector3(0.4f, gs + 2.3f, -19.2f));
            var w1 = Shot(3f, "cae sobre la hoja");
            w1.fadeColor = Color.black; w1.fadeInSeconds = 1.5f;
            w1.actorTeleport = Point("Sobre_la_hoja", a.transform, new Vector3(0.4f, gs + 6f, -19.2f), 180f);
            w1.from = w0.from; w1.lookAt = Point("Mira_hoja", a.transform, new Vector3(0.4f, gs + 2.6f, -19.2f)); w1.focalLength = 35f;
            var w2 = Shot(2.6f, "rueda al suelo");
            w2.actorTeleport = a.spawn;
            w2.from = CamPoint("Cam_Hoja_B", a.transform, new Vector3(3.5f, gs + 0.6f, -17f), Vector3.zero);
            w2.to = CamPoint("Cam_Hoja_C", a.transform, new Vector3(2.5f, gs + 1.2f, -15.5f), Vector3.zero);
            w2.lookAtActorHead = true; w2.focalLength = 28f;
            var sea = Point("Mira_mar", a.transform, new Vector3(0f, 2f, -220f));
            var w3 = Shot(5f, "el oceano infinito");
            w3.from = CamPoint("Cam_Mar_A", a.transform, new Vector3(2.4f, gs + 1.7f, -17.4f), Vector3.zero);
            w3.to = CamPoint("Cam_Mar_B", a.transform, new Vector3(2f, gs + 1.62f, -19f), Vector3.zero);
            w3.lookAt = sea; w3.focalLength = 24f; w3.headLookAt = sea;
            a.arrival = Sequence("Cine_La_Hoja", a.transform, w0, w1, w2, w3);

            var d1 = Shot(4.5f, "camina hacia la luz del tunel");
            d1.from = CamPoint("Cam_Tunel_A", a.transform, new Vector3(0.2f, ge + 1.55f, t1 - 9f), Vector3.zero);
            d1.to = CamPoint("Cam_Tunel_B", a.transform, new Vector3(0.15f, ge + 1.5f, t1 - 6f), Vector3.zero);
            d1.lookAt = lightPoint; d1.focalLength = 28f;
            d1.actorWalkTo = Point("En_la_luz", a.transform, new Vector3(0f, ge, t1 - 0.4f)); d1.actorSpeed = 0.9f;
            d1.fadeColor = Color.white; d1.fadeOutSeconds = 2.2f;
            OnStart(d1, cue.Duck);
            Gate("La_luz_del_tunel", a.transform, new Vector3(0f, ge + 1f, t1 - 3f), new Vector3(1.2f, 2f, 1f), Sequence("Cine_El_Tunel_de_Luz", a.transform, d1));

            GlobalVolume("Ambiente_Playa", a.transform, Profile("S6_Playa", p => { Fog(p, 160f, 60f, new Color(0.55f, 0.62f, 0.82f)); NightSky(p, 1f); ExposureLimits(p, 0.3f, 4f, 0f); }), 1f);
            Save(scene, "S6_Playa");
        }

        static void Palm(Transform parent, Vector3 basePos, float height, float leanDeg, System.Random rng, out Vector3 top,
                         float? leanYaw = null, int leaves = 9)
        {
            var root = Group("Palmera", parent);
            root.position = basePos;
            float yaw = leanYaw ?? (float)rng.NextDouble() * 360f;
            var lean = Quaternion.Euler(0f, yaw, 0f) * Quaternion.Euler(leanDeg, 0f, 0f);
            var trunkM = ScanMat("M_Tronco_Palmera", "palm_bark", new Color(0.95f, 0.9f, 0.85f), 1.2f);
            int seg = height > 8f ? 7 : 4; var p = basePos;
            for (int i = 0; i < seg; i++)
            {
                var q = Quaternion.Slerp(Quaternion.identity, lean, Mathf.Pow((i + 1f) / seg, 1.6f));   // la curva crece hacia arriba
                var dir = q * Vector3.up;
                float l = height / seg, w = Mathf.Lerp(0.42f, 0.24f, i / (float)seg);
                Prim(PrimitiveType.Cylinder, $"Tronco_{i}", root, p + dir * l * 0.5f, new Vector3(w, l * 0.52f, w), trunkM, SurfaceType.Wood, q.eulerAngles);
                p += dir * l;
            }
            top = p;
            float len = height > 8f ? 4.2f : 3.2f;
            for (int i = 0; i < leaves; i++)
            {
                float ang = i * 360f / leaves + (float)rng.NextDouble() * 15f;
                // cada hoja en dos tramos: sale hacia arriba y cae, como una palmera de verdad
                var q1 = Quaternion.Euler(0f, ang, 0f) * Quaternion.Euler(-12f + (float)rng.NextDouble() * 10f, 0f, 0f);
                var d1 = q1 * Vector3.forward;
                var l1 = Prim(PrimitiveType.Cube, $"Hoja_{i}_a", root, p + d1 * len * 0.5f, new Vector3(0.8f, 0.03f, len), Palette.Leaf, null, q1.eulerAngles, false);
                var mid = p + d1 * len;
                var q2 = Quaternion.Euler(0f, ang, 0f) * Quaternion.Euler(35f + (float)rng.NextDouble() * 20f, 0f, 0f);
                var d2 = q2 * Vector3.forward;
                var l2 = Prim(PrimitiveType.Cube, $"Hoja_{i}_b", root, mid + d2 * len * 0.45f, new Vector3(0.65f, 0.03f, len * 0.9f), Palette.Leaf, null, q2.eulerAngles, false);
                Static(l1, true); Static(l2, true);
            }
        }

        // Laberinto perfecto (backtracker con semilla): bloques de la grilla (2c+1)^2; entrada abajo al centro y
        // salida arriba al centro.
        static bool[,] Maze(int c, int seed)
        {
            int n = c * 2 + 1; var w = new bool[n, n];
            for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) w[i, j] = true;
            var rng = new System.Random(seed); var seen = new bool[c, c];
            var stack = new System.Collections.Generic.Stack<(int, int)>();
            stack.Push((c / 2, 0)); seen[c / 2, 0] = true; w[c / 2 * 2 + 1, 1] = false;
            int[] dx = { 1, -1, 0, 0 }, dz = { 0, 0, 1, -1 };
            while (stack.Count > 0)
            {
                var (x, z) = stack.Peek();
                var opts = new System.Collections.Generic.List<int>();
                for (int k = 0; k < 4; k++) { int nx = x + dx[k], nz = z + dz[k]; if (nx >= 0 && nz >= 0 && nx < c && nz < c && !seen[nx, nz]) opts.Add(k); }
                if (opts.Count == 0) { stack.Pop(); continue; }
                int d = opts[rng.Next(opts.Count)];
                int ax = x + dx[d], az = z + dz[d];
                seen[ax, az] = true;
                w[x * 2 + 1 + dx[d], z * 2 + 1 + dz[d]] = false;
                w[ax * 2 + 1, az * 2 + 1] = false;
                stack.Push((ax, az));
            }
            w[c / 2 * 2 + 1, 0] = false;            // entrada
            w[c / 2 * 2 + 1, n - 1] = false;        // salida al tunel
            return w;
        }
    }
}
