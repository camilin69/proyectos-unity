using UnityEngine;
using static Dream.EditorTools.Build.BuildKit;

namespace Dream.EditorTools.Build
{
    // 6 · La playa del oceano infinito y el bosque de palmeras que se cierra, 21:20. Cae sobre una hoja de palmera
    // y queda mirando el mar; tierra adentro, el camino de palmeras se vuelve bosque y la niebla lo traga todo.
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

            // palmeras: el camino se vuelve bosque
            var palms = Group("Palmeras");
            var rng = new System.Random(11);
            Palm(palms, new Vector3(-0.6f, G(-0.6f, -16.5f), -16.5f), 3.6f, -14f, rng, out var leafTop);
            var landingLeaf = Box("Hoja_de_aterrizaje", palms, new Vector3(0.4f, G(0.4f, -19.2f) + 2.3f, -19.2f), new Vector3(1.0f, 0.06f, 3.2f), Palette.Leaf, SurfaceType.Leaves);
            landingLeaf.transform.rotation = Quaternion.Euler(18f, 10f, 0f);
            for (float z = 6f; z < 136f; z += 5.5f)
            {
                int perSide = 1 + Mathf.FloorToInt(z / 22f);
                for (int s = -1; s <= 1; s += 2)
                    for (int k = 0; k < perSide; k++)
                    {
                        float x = s * (2.6f + k * 2.4f + (float)rng.NextDouble() * 1.4f);
                        float zz = z + (float)(rng.NextDouble() - 0.5) * 3f;
                        Palm(palms, new Vector3(x, G(x, zz), zz), 6f + (float)rng.NextDouble() * 5f, (float)(rng.NextDouble() - 0.5) * 16f, rng, out _);
                    }
                int bushes = Mathf.FloorToInt(z / 18f);
                for (int b = 0; b < bushes; b++)
                {
                    float x = (rng.NextDouble() < 0.5 ? -1 : 1) * (1.8f + (float)rng.NextDouble() * 9f);
                    float sz = 1f + (float)rng.NextDouble() * 1.6f;
                    Prim(PrimitiveType.Sphere, "Mata", palms, new Vector3(x, G(x, z) + sz * 0.3f, z), new Vector3(sz * 1.4f, sz, sz * 1.4f), Palette.Hedge, null, null, false);
                }
            }
            // al fondo el bosque se cierra del todo
            for (int i = 0; i < 18; i++)
            {
                float x = -14f + i * 1.65f;
                if (Mathf.Abs(x) < 1.8f) continue;
                Prim(PrimitiveType.Sphere, "Muro_de_hojas", palms, new Vector3(x, G(x, 143f) + 2f, 143f + (float)rng.NextDouble()), new Vector3(3f, 5f, 3f), Mat("M_Hojas_Oscuras", new Color(0.08f, 0.11f, 0.08f), 0.1f));
            }
            Memory(a.transform, new Vector3(1.4f, G(1.4f, 70f) + 1.0f, 70f), "El mar sigue hablando aunque nadie lo escuche.");

            float gh = G(0f, 140f);
            Prim(PrimitiveType.Cylinder, "Hoyo_oscuro", a.transform, new Vector3(0f, gh + 0.02f, 140f), new Vector3(3f, 0.01f, 3f), Palette.Black, null, null, false);
            var holePoint = Point("Mira_hoyo", a.transform, new Vector3(0f, gh, 140f));
            var dark = Profile("S6_Bosque_Cerrado", p => Fog(p, 5f, 40f, new Color(0.08f, 0.1f, 0.08f)));
            LocalVolume("Bosque_que_se_cierra", a.transform, new Vector3(0f, 6f, 112f), new Vector3(70f, 40f, 70f), dark, 2f, 38f);

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

            var d1 = Shot(4.5f, "entra en lo oscuro");
            d1.from = CamPoint("Cam_Hoyo_A", a.transform, new Vector3(1.2f, gh + 1.7f, 130f), Vector3.zero);
            d1.lookAt = holePoint; d1.focalLength = 35f;
            d1.actorWalkTo = Point("En_el_hoyo", a.transform, new Vector3(0f, gh, 140.5f)); d1.actorSpeed = 0.9f;
            d1.fadeColor = Color.black; d1.fadeOutSeconds = 2.6f;
            OnStart(d1, cue.Duck);
            Gate("El_hoyo", a.transform, new Vector3(0f, gh + 1.1f, 139f), new Vector3(3f, 2.4f, 3f), Sequence("Cine_El_Bosque", a.transform, d1));

            GlobalVolume("Ambiente_Playa", a.transform, Profile("S6_Playa", p => { Fog(p, 160f, 60f, new Color(0.55f, 0.62f, 0.82f)); NightSky(p, 1f); ExposureLimits(p, 0.3f, 4f, 0f); }), 1f);
            Save(scene, "S6_Playa");
        }

        static void Palm(Transform parent, Vector3 basePos, float height, float leanDeg, System.Random rng, out Vector3 top)
        {
            var root = Group("Palmera", parent);
            root.position = basePos;
            float yaw = (float)rng.NextDouble() * 360f;
            var lean = Quaternion.Euler(0f, yaw, 0f) * Quaternion.Euler(leanDeg, 0f, 0f);
            var trunkM = ScanMat("M_Tronco_Palmera", "palm_bark", new Color(0.95f, 0.9f, 0.85f), 1.2f);
            int seg = 4; var p = basePos;
            for (int i = 0; i < seg; i++)
            {
                var q = Quaternion.Slerp(Quaternion.identity, lean, (i + 1f) / seg);
                var dir = q * Vector3.up;
                float l = height / seg;
                Prim(PrimitiveType.Cylinder, $"Tronco_{i}", root, p + dir * l * 0.5f, new Vector3(0.36f - i * 0.04f, l * 0.52f, 0.36f - i * 0.04f), trunkM, SurfaceType.Wood, q.eulerAngles);
                p += dir * l;
            }
            top = p;
            for (int i = 0; i < 9; i++)
            {
                var q = Quaternion.Euler(0f, i * 40f + (float)rng.NextDouble() * 15f, 0f) * Quaternion.Euler(28f + (float)rng.NextDouble() * 18f, 0f, 0f);
                var dir = q * Vector3.forward;
                var leaf = Prim(PrimitiveType.Cube, $"Hoja_{i}", root, p + dir * 1.5f, new Vector3(0.7f, 0.03f, 3.2f), Palette.Leaf, null, q.eulerAngles, false);
                Static(leaf, true);
            }
        }
    }
}
