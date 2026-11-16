using UnityEngine;
using static Dream.EditorTools.Build.BuildKit;

namespace Dream.EditorTools.Build
{
    // 8 · La escalera de moqueta rosa al cielo, 23:30 -> 00:00. Muros de piedra a los lados con antorchas de fuego,
    // nubes bajo los pies y un cielo morado de estrellas que titilan. Mientras sube, un meteorito en llamas de tamano
    // planetario se acerca; arriba, cuando se abre la ultima puerta, cae: la tierra tiembla y la luz lo blanquea todo.
    public static class S8Builder
    {
        public static void Build()
        {
            var scene = NewScene();
            var a = Anchor(7, "La escalera al cielo", new Vector3(0f, 0.02f, -3.5f), 0f, 23.5f, 23.98f, 3.5f);
            a.ambienceKind = AmbienceKind.VientoAlto; a.ambienceVolume = 0.35f; a.musicLowPass = 22000f; a.musicVolume = 0.95f; a.musicReverb = 0.4f; a.respawnBelowY = -25f;
            var cue = Cue(a.transform);
            var st = Group("Escalera");
            const int steps = 70; const float rise = 0.3f, run = 0.45f, half = 2f;
            BoxMinMax("Base", st, new Vector3(-4f, -0.6f, -7f), new Vector3(4f, 0f, 0f), Palette.Stone, SurfaceType.Stone);
            var trim = ScanMat("M_Moldura_Crema", "painted_plaster_wall", new Color(1f, 0.95f, 0.88f), 0.8f, 0.35f, 0.65f);
            var stone = ScanMat("M_Muro_Piedra", "mossy_stone_wall", new Color(0.92f, 0.86f, 0.9f), 2.2f, 0f, 0.35f);
            var wood = ScanMat("M_Palo_Antorcha", "bark_willow", new Color(0.45f, 0.32f, 0.22f), 0.6f, 0f, 0.3f);
            var iron = ScanMat("M_Hierro", "metal_plate", new Color(0.3f, 0.3f, 0.32f), 0.6f, 0.3f, 0.75f);
            NightKit.ResetCache();
            for (int i = 0; i < steps; i++)
            {
                float y = (i + 1) * rise, z0 = i * run;
                BoxMinMax($"Peldano_{i:00}", st, new Vector3(-half, y - 0.6f, z0), new Vector3(half, y, z0 + run), Palette.Carpet, SurfaceType.Carpet);
                BoxMinMax($"Moldura_I_{i:00}", st, new Vector3(-half - 0.16f, y - 0.6f, z0), new Vector3(-half, y + 0.05f, z0 + run), trim);
                BoxMinMax($"Moldura_D_{i:00}", st, new Vector3(half, y - 0.6f, z0), new Vector3(half + 0.16f, y + 0.05f, z0 + run), trim);
                // muros de piedra a los lados, escalonados con la escalera
                for (int s = -1; s <= 1; s += 2)
                    BoxMinMax($"Muro_{(s < 0 ? "I" : "D")}_{i:00}", st, new Vector3(s < 0 ? -half - 0.66f : half + 0.16f, y - 1.2f, z0),
                              new Vector3(s < 0 ? -half - 0.16f : half + 0.66f, y + 2.4f, z0 + run), stone, SurfaceType.Stone);
                if (i % 7 == 3)
                    for (int s = -1; s <= 1; s += 2)
                        NightKit.Torch(st, new Vector3(s * (half + 0.16f), y + 1.5f, z0 + run * 0.5f), new Vector3(-s, 0f, 0f), wood, iron);
                if (i % 15 == 7) CheckpointAt(a.transform, new Vector3(0f, y + 0.05f, z0 + run * 0.5f), 0f, new Vector3(4f, 3f, 1f));
            }
            float topY = steps * rise, topZ = steps * run;
            BoxMinMax("Descanso", st, new Vector3(-4f, topY - 0.6f, topZ), new Vector3(4f, topY, topZ + 5.5f), Palette.Carpet, SurfaceType.Carpet);
            var door = Door("Ultima_puerta", st, new Vector3(0f, topY, topZ + 5f), 0f, trim, Palette.Cream);
            BoxMinMax("Mas_alla", st, new Vector3(-0.7f, topY - 0.6f, topZ + 5.5f), new Vector3(0.7f, topY, topZ + 8f), Palette.Carpet, SurfaceType.Carpet);
            Prim(PrimitiveType.Quad, "Luz_final", st, new Vector3(0f, topY + 1.3f, topZ + 7.5f), new Vector3(3f, 3.5f, 1f), Palette.BlindingLight, null, Vector3.zero, false);
            var memory = Memory(a.transform, new Vector3(0f, topY + 0.9f, topZ + 2.5f), "Al final de la escalera estaba la habitación de siempre.");

            // nubes bajo los pies: niebla volumetrica local, rosada por la luz de la escalera
            var clouds = Group("Nubes");
            var rng = new System.Random(5);
            for (int i = 0; i < 22; i++)
            {
                var pos = new Vector3((float)(rng.NextDouble() - 0.5) * 150f, -8f + (float)rng.NextDouble() * 10f, -30f + (float)rng.NextDouble() * 100f);
                if (Mathf.Abs(pos.x) < 9f) pos.x += Mathf.Sign(pos.x + 0.01f) * 12f;
                CloudPuff($"Nube_{i:00}", clouds, pos, new Vector3(48f, 16f, 40f) * (0.7f + (float)rng.NextDouble() * 0.7f), 4f, new Color(1f, 0.93f, 0.95f));
            }
            ShootingStarsIn(a.transform);

            // el cielo morado con estrellas que titilan y el meteorito que se acerca con la subida
            NightKit.TwinklingStars(a.transform, 420, new Color(3f, 2.9f, 3.4f, 1f));
            // el meteorito baja desde arriba, a 50 grados sobre el horizonte y por delante de la cima: se ve por encima de
            // la escalera mientras se sube y, al final, cae casi encima (sin ser vertical, para poder mirarlo)
            var summit = new Vector3(0f, topY, topZ + 4f);
            var fallDir = new Vector3(0f, Mathf.Sin(50f * Mathf.Deg2Rad), Mathf.Cos(50f * Mathf.Deg2Rad));
            var meteor = NightKit.MeteorRig(a.transform, 0f, topZ, summit + fallDir * 6500f, summit + fallDir * 4200f, summit + fallDir * 2300f);
            meteor.farRadius = 220f; meteor.nearRadius = 800f; meteor.impactRadius = 1500f;
            var meteorLook = Point("Mira_meteorito", a.transform, summit + fallDir * 60f);
            a.gameObject.AddComponent<MoonOverhead>().direction = new Vector3(-0.6f, 0.5f, -0.62f);

            // llegada: abajo, mirando la subida
            var stairTop = Point("Mira_arriba", a.transform, new Vector3(0f, topY, topZ + 5f));
            var w1 = Shot(7f, "la escalera majestuosa; la camara sube con el");
            w1.fadeColor = Color.white; w1.fadeInSeconds = 3.5f;
            w1.from = CamPoint("Cam_Escalera_A", a.transform, new Vector3(3f, 0.6f, -9f), Vector3.zero);
            w1.to = CamPoint("Cam_Escalera_B", a.transform, new Vector3(2.2f, 3.5f, -7f), Vector3.zero);
            w1.lookAt = Point("Mira_mitad", a.transform, new Vector3(0f, 12f, 18f)); w1.focalLength = 24f; w1.headLookAt = stairTop;
            a.arrival = Sequence("Cine_La_Escalera", a.transform, w1);

            // salida: la ultima puerta
            var light = Point("Mira_luz_final", a.transform, new Vector3(0f, topY + 1.2f, topZ + 7f));
            var d1 = Shot(4.5f, "la ultima puerta se abre");
            d1.from = CamPoint("Cam_Final_A", a.transform, new Vector3(1.8f, topY + 0.5f, topZ - 3.2f), Vector3.zero);
            d1.to = CamPoint("Cam_Final_B", a.transform, new Vector3(1.4f, topY + 0.6f, topZ - 2.2f), Vector3.zero);
            d1.lookAt = meteorLook; d1.focalLength = 18f; d1.headLookAt = meteorLook;   // desde abajo: el sonador y el cielo que cae
            d1.actorWalkTo = Point("Ante_la_ultima", a.transform, new Vector3(0f, topY, topZ + 4.3f), 0f); d1.actorSpeed = 0.8f;
            OnStart(d1, door.Open); OnStart(d1, cue.LightHum); OnStart(d1, meteor.Impact);
            var d2 = Shot(3.5f, "entra en la luz");
            d2.from = CamPoint("Cam_Final_C", a.transform, new Vector3(0.5f, topY + 1.6f, topZ + 1f), Vector3.zero);
            d2.lookAt = Point("Mira_luz_y_cielo", a.transform, Vector3.Lerp(new Vector3(0f, topY + 1.2f, topZ + 7f), summit + fallDir * 12f, 0.5f)); d2.focalLength = 22f;
            d2.actorWalkTo = Point("Dentro", a.transform, new Vector3(0f, topY, topZ + 7.6f), 0f); d2.actorSpeed = 1f;
            d2.fadeColor = Color.white; d2.fadeOutSeconds = 2.6f;
            memory.autoGate = Gate("La_ultima_puerta", a.transform, new Vector3(0f, topY + 1.1f, topZ + 4.1f), new Vector3(2f, 2.2f, 1.2f), Sequence("Cine_El_Regreso", a.transform, d1, d2));

            GlobalVolume("Ambiente_Escalera", a.transform, Profile("S8_Escalera", p => { Fog(p, 400f, 40f, new Color(0.72f, 0.58f, 0.92f)); NightSky(p, 2.4f, "dream_noche_morada.png"); ExposureLimits(p, 0f, 6f, 0.3f); }), 1f);
            Save(scene, "S8_Escalera");
        }
    }
}
