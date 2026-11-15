using UnityEngine;
using static Dream.EditorTools.Build.BuildKit;

namespace Dream.EditorTools.Build
{
    // 7 · La escalera de moqueta rosa al cielo, 23:30 -> 00:00. Setos a los lados, nubes bajo los pies, figuras de
    // luz que acompanan la subida y rayos que caen desde arriba. Arriba, la ultima puerta devuelve al cuarto.
    public static class S7Builder
    {
        public static void Build()
        {
            var scene = NewScene();
            var a = Anchor(6, "La escalera al cielo", new Vector3(0f, 0.02f, -3.5f), 0f, 23.5f, 23.98f, 3.5f);
            a.ambienceKind = AmbienceKind.VientoAlto; a.ambienceVolume = 0.35f; a.musicLowPass = 22000f; a.musicVolume = 0.95f; a.musicReverb = 0.4f; a.respawnBelowY = -25f;
            var cue = Cue(a.transform);
            var st = Group("Escalera");
            const int steps = 70; const float rise = 0.3f, run = 0.45f, half = 2f;
            BoxMinMax("Base", st, new Vector3(-4f, -0.6f, -7f), new Vector3(4f, 0f, 0f), Palette.Stone, SurfaceType.Stone);
            var trim = Mat("M_Moldura_Crema", new Color(1f, 0.95f, 0.88f), 0.5f);
            for (int i = 0; i < steps; i++)
            {
                float y = (i + 1) * rise, z0 = i * run;
                BoxMinMax($"Peldano_{i:00}", st, new Vector3(-half, y - 0.6f, z0), new Vector3(half, y, z0 + run), Palette.Carpet, SurfaceType.Carpet);
                BoxMinMax($"Moldura_I_{i:00}", st, new Vector3(-half - 0.16f, y - 0.6f, z0), new Vector3(-half, y + 0.05f, z0 + run), trim);
                BoxMinMax($"Moldura_D_{i:00}", st, new Vector3(half, y - 0.6f, z0), new Vector3(half + 0.16f, y + 0.05f, z0 + run), trim);
                if (i % 6 == 0)
                    for (int s = -1; s <= 1; s += 2)
                        Box($"Seto_{i:00}", st, new Vector3(s * 2.65f, y + 0.25f, z0 + 1.35f), new Vector3(0.7f, 1.0f, 2.6f), Palette.Hedge);
                if (i % 15 == 7) CheckpointAt(a.transform, new Vector3(0f, y + 0.05f, z0 + run * 0.5f), 0f, new Vector3(4f, 3f, 1f));
                if (i % 10 == 5) AddLight("Luz_calida", st, LightType.Point, new Vector3(0f, y + 1.2f, z0), Vector3.zero, new Color(1f, 0.78f, 0.82f), 420f, 7f, 60f, null, false);
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

            // los que acompanan: figuras de luz a los lados
            var angels = Group("Acompanantes");
            var glow = Mat("M_Figura_de_Luz", new Color(1f, 0.95f, 0.86f), 0.2f, 0f, new Color(1f, 0.9f, 0.78f), 1400f);
            var wing = Mat("M_Ala_de_Luz", new Color(1f, 0.96f, 0.9f), 0.1f, 0f, new Color(1f, 0.93f, 0.85f), 700f, false, true);
            for (int i = 0; i < 12; i++)
            {
                int side = i % 2 == 0 ? -1 : 1;
                float z = 2f + i * 2.6f;
                float y = (z / run) * rise + 1.5f + (float)rng.NextDouble() * 2.5f;
                var root = Point($"Figura_{i:00}", angels, new Vector3(side * (5.5f + (float)rng.NextDouble() * 3f), y, z), side < 0 ? 90f : -90f);
                Prim(PrimitiveType.Capsule, "Cuerpo", root, root.position, new Vector3(0.55f, 1.2f, 0.55f), glow, null, null, false);
                Prim(PrimitiveType.Sphere, "Cabeza", root, root.position + Vector3.up * 1.45f, Vector3.one * 0.42f, glow, null, null, false);
                for (int w = -1; w <= 1; w += 2)
                    Prim(PrimitiveType.Quad, "Ala", root, root.position + Vector3.up * 0.7f + root.right * w * 0.75f - root.forward * 0.2f,
                         new Vector3(1.4f, 1.1f, 1f), wing, null, new Vector3(0f, root.eulerAngles.y + w * 25f, w * -20f), false);
                foreach (Transform c in root) Static(c.gameObject, false);
                var b = root.gameObject.AddComponent<Bob>(); b.amplitude = 0.3f; b.speed = 0.25f + i * 0.02f;
            }
            for (int i = 0; i < 5; i++)
                AddLight("Rayo", st, LightType.Spot, new Vector3(((i % 2) * 2 - 1) * 3f, 48f, 4f + i * 7f), new Vector3(78f, 180f, 0f), new Color(1f, 0.93f, 0.85f), 42000f, 80f, 22f);

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
            d1.from = CamPoint("Cam_Final_A", a.transform, new Vector3(1.3f, topY + 0.9f, topZ - 2.6f), Vector3.zero);
            d1.to = CamPoint("Cam_Final_B", a.transform, new Vector3(1.0f, topY + 1.2f, topZ - 1.0f), Vector3.zero);
            d1.lookAtActorHead = true; d1.focalLength = 50f; d1.headLookAt = light;
            d1.actorWalkTo = Point("Ante_la_ultima", a.transform, new Vector3(0f, topY, topZ + 4.3f), 0f); d1.actorSpeed = 0.8f;
            OnStart(d1, door.Open); OnStart(d1, cue.LightHum);
            var d2 = Shot(3.5f, "entra en la luz");
            d2.from = CamPoint("Cam_Final_C", a.transform, new Vector3(0.5f, topY + 1.6f, topZ + 1f), Vector3.zero);
            d2.lookAt = light; d2.focalLength = 35f;
            d2.actorWalkTo = Point("Dentro", a.transform, new Vector3(0f, topY, topZ + 7.6f), 0f); d2.actorSpeed = 1f;
            d2.fadeColor = Color.white; d2.fadeOutSeconds = 2.6f;
            memory.autoGate = Gate("La_ultima_puerta", a.transform, new Vector3(0f, topY + 1.1f, topZ + 4.1f), new Vector3(2f, 2.2f, 1.2f), Sequence("Cine_El_Regreso", a.transform, d1, d2));

            GlobalVolume("Ambiente_Escalera", a.transform, Profile("S7_Escalera", p => { Fog(p, 180f, 70f, new Color(1f, 0.88f, 0.92f)); NightSky(p, 1.6f); ExposureLimits(p, 0.5f, 6f, 0.3f); }), 1f);
            Save(scene, "S7_Escalera");
        }
    }
}
