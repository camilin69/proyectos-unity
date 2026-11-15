using UnityEngine;
using UnityEngine.Rendering.HighDefinition;
using static Dream.EditorTools.Build.BuildKit;

namespace Dream.EditorTools.Build
{
    // 3 · Vuelo entre nubes cada vez mas espesas hasta la colina del arbol monumental, 12:00. El recuerdo esta en lo
    // alto de una nube densa; despues una cinematica deja al sonador en la colina, ya sin poder volar, y el hueco
    // negro del arbol es el paso a la noche.
    public static class S3Builder
    {
        public static void Build()
        {
            var scene = NewScene();
            var terrain = MakeTerrain("T_Colina", null, new Vector3(-450f, 0f, -450f), new Vector3(900f, 90f, 900f), 257,
                (u, v) =>
                {
                    float du = u - 0.5f, dv = v - 0.5f;
                    float hill = 0.5f * Mathf.Exp(-(du * du + dv * dv) / (2f * 0.075f * 0.075f));
                    return 0.06f + hill + 0.03f * Mathf.PerlinNoise(u * 6f, v * 6f) + 0.012f * Mathf.PerlinNoise(u * 25f, v * 25f);
                },
                ("Pasto", new Color(0.6f, 0.74f, 0.45f), 6f), ("Flores", new Color(0.97f, 0.86f, 0.62f), 4f));
            PaintLayer(terrain, 1, (u, v) => (Mathf.PerlinNoise(u * 12f + 3f, v * 12f) - 0.62f) * 5f);
            terrain.gameObject.AddComponent<TerrainSurfaces>().layerSurfaces = new[] { SurfaceType.Grass, SurfaceType.Grass };
            float G(float x, float z) => Ground(terrain, x, z);

            var a = Anchor(2, "La colina del árbol", new Vector3(0f, 150f, -330f), 0f, 12f, 12.6f, 6f);
            a.allowFlight = true; a.startFlying = true;
            a.arrivalHint = "Q  volar / posarse     ·     Espacio subir     ·     Ctrl bajar     ·     Shift más rápido";
            a.ambienceKind = AmbienceKind.VientoAlto; a.musicLowPass = 22000f; a.musicVolume = 0.9f; a.musicReverb = 0.12f; a.respawnBelowY = -20f;
            var cue = Cue(a.transform);

            // nubes: la capa volumetrica del cielo se atraviesa volando; la densa es niebla local con ruido 3D y un
            // suelo invisible encima, donde espera el recuerdo
            var clouds = Group("Nubes");
            var dense = new Vector3(0f, 139f, -278f);      // justo delante de donde aparece, a la altura de los ojos
            CloudPuff("Nube_densa", clouds, dense + Vector3.up * 4f, new Vector3(64f, 28f, 64f), 2.5f, new Color(1f, 0.97f, 0.98f), true);
            var rng = new System.Random(3);
            for (int i = 0; i < 9; i++)
            {
                var pos = new Vector3((float)(rng.NextDouble() - 0.5) * 260f, 125f + (float)rng.NextDouble() * 60f, -300f + (float)rng.NextDouble() * 220f);
                if (Vector3.Distance(pos, dense) < 55f || Mathf.Abs(pos.x) < 20f && pos.z < -270f) continue;
                CloudPuff($"Nube_{i:00}", clouds, pos, new Vector3(70f, 24f, 55f) * (0.7f + (float)rng.NextDouble() * 0.6f), 6f, Color.white);
            }
            var memory = Memory(a.transform, dense + Vector3.up * 11.6f, "Desde arriba todo cabe en la palma de la mano.");

            // la colina y el arbol monumental
            float g0 = G(0f, 0f);
            var tree = Group("Arbol_monumental");
            Prim(PrimitiveType.Cylinder, "Tronco", tree, new Vector3(0f, g0 + 15f, 0f), new Vector3(7f, 16f, 7f), Palette.Bark, SurfaceType.Wood);
            for (int i = 0; i < 6; i++)
            {
                float ang = i * 60f + 15f;
                var dir = Quaternion.Euler(0f, ang, 0f) * Vector3.forward;
                Prim(PrimitiveType.Capsule, $"Raiz_{i}", tree, new Vector3(0f, g0 + 0.6f, 0f) + dir * 4.2f, new Vector3(1.6f, 3f, 1.6f), Palette.Bark, SurfaceType.Wood, new Vector3(70f, ang, 0f));
            }
            var crownM = Mat("M_Copa", new Color(0.47f, 0.64f, 0.42f), 0.2f);
            Vector3[] crown = { new(0, 40, 0), new(12, 37, 4), new(-11, 38, -5), new(4, 36, -13), new(-5, 39, 12), new(9, 44, -6), new(-8, 45, 6), new(0, 48, 0) };
            for (int i = 0; i < crown.Length; i++)
                Prim(PrimitiveType.Sphere, $"Copa_{i}", tree, new Vector3(crown[i].x, g0 + crown[i].y, crown[i].z), new Vector3(24f, 17f, 24f) * (i == 0 ? 1.3f : 1f), crownM, null, null, false);
            var hole = Prim(PrimitiveType.Cube, "Hueco_negro", tree, new Vector3(0f, g0 + 1.35f, -3.42f), new Vector3(1.8f, 2.6f, 0.4f), Palette.Black, null, null, false);
            Static(hole, false);
            var holePoint = Point("Mira_hueco", tree, new Vector3(0f, g0 + 1.4f, -3.4f));

            // tras el recuerdo: cinematica de llegada a la colina (sin cambiar de escenario)
            float gl = G(0f, -95f);
            var crownPoint = Point("Mira_copa", tree, new Vector3(0f, g0 + 34f, 0f));
            var l1 = Shot(4f, "angulo amplio: el sonador llega al cielo abierto");
            l1.from = CamPoint("Cam_Llegada_A", a.transform, new Vector3(45f, 160f, -112f), Vector3.zero);
            l1.to = CamPoint("Cam_Llegada_B", a.transform, new Vector3(35f, 157f, -98f), Vector3.zero);
            l1.lookAtActorHead = true; l1.focalLength = 135f; l1.focalLengthEnd = 85f;
            l1.actorVelocity = new Vector3(0f, -1.5f, 7f);
            var l2 = Shot(5.5f, "la colina y el arbol al mediodia");
            l2.actorTeleport = Point("Aterriza", a.transform, new Vector3(0f, gl + 0.05f, -95f), 0f);
            l2.from = CamPoint("Cam_Colina_A", a.transform, new Vector3(-55f, G(-55f, -150f) + 18f, -150f), Vector3.zero);
            l2.to = CamPoint("Cam_Colina_B", a.transform, new Vector3(-35f, G(-35f, -140f) + 13f, -125f), Vector3.zero);
            l2.lookAt = crownPoint; l2.focalLength = 35f;
            var l3 = Shot(3f, "camina hacia el arbol");
            l3.from = CamPoint("Cam_Colina_C", a.transform, new Vector3(1.2f, gl + 1.6f, -99f), Vector3.zero);
            l3.lookAt = crownPoint; l3.focalLength = 30f;
            l3.actorWalkTo = Point("Sube", a.transform, new Vector3(0f, G(0f, -91f), -91f), 0f); l3.actorSpeed = 1.1f;
            var landing = Gate("Hacia_la_colina", a.transform, new Vector3(0f, 150f, -120f), new Vector3(140f, 110f, 12f),
                               Sequence("Cine_Llegada_Colina", a.transform, l1, l2, l3), false, true);
            landing.revokesFlight = true;
            memory.autoGate = landing;
            landing.lockedHint = "Las nubes no te dejan pasar todavía. Busca arriba, en la más densa.";
            CheckpointAt(a.transform, new Vector3(0f, gl + 0.05f, -95f), 0f, new Vector3(6f, 4f, 6f));

            // el hueco: se asoma, tropieza y cae a la oscuridad (12:00 -> 20:00)
            var h1 = Shot(4.5f, "se acerca despacio al hueco");
            h1.from = CamPoint("Cam_Hueco_A", a.transform, new Vector3(3.8f, g0 + 1.7f, -8.5f), Vector3.zero);
            h1.to = CamPoint("Cam_Hueco_B", a.transform, new Vector3(3f, g0 + 1.6f, -7.2f), Vector3.zero);
            h1.lookAt = holePoint; h1.focalLength = 35f; h1.headLookAt = holePoint;
            h1.actorWalkTo = Point("Ante_el_hueco", a.transform, new Vector3(0f, g0, -4.5f), 0f); h1.actorSpeed = 0.75f;
            var h2 = Shot(2.4f, "asoma la cabeza");
            h2.from = CamPoint("Cam_Hueco_C", a.transform, new Vector3(2.7f, g0 + 1.55f, -5.3f), Vector3.zero);
            h2.lookAtActorHead = true; h2.focalLength = 50f; h2.actorTrigger = "Peek"; h2.headLookAt = holePoint;
            var h3 = Shot(1.2f, "tropieza y cae dentro");
            h3.from = h2.from; h3.lookAt = holePoint; h3.focalLength = 50f;
            h3.actorVelocity = new Vector3(0f, 0f, 1.6f); h3.actorTrigger = "Stumble";
            h3.fadeColor = Color.black; h3.fadeOutSeconds = 0.9f;
            OnStart(h3, cue.Silence);
            var h4 = Shot(2.2f, "negro total y silencio");
            h4.hideActor = true; h4.setHour = 20f; h4.hourSeconds = 0f;
            Gate("El_hueco", a.transform, new Vector3(0f, g0 + 1.2f, -4.4f), new Vector3(2.2f, 2.4f, 1.4f), Sequence("Cine_El_Hueco", a.transform, h1, h2, h3, h4));

            // llegada desde la pradera: el cielo
            var w1 = Shot(6f, "llega al cielo; abajo, muy lejos, la colina");
            w1.fadeColor = Color.white; w1.fadeInSeconds = 3f;
            w1.from = CamPoint("Cam_Cielo_A", a.transform, new Vector3(6f, 146f, -326f), Vector3.zero);
            w1.to = CamPoint("Cam_Cielo_B", a.transform, new Vector3(4f, 147.5f, -322f), Vector3.zero);
            w1.lookAtActorHead = true; w1.focalLength = 24f;
            w1.actorVelocity = new Vector3(0f, 0.6f, 1.5f);
            a.arrival = Sequence("Cine_Llegada_Cielo", a.transform, w1);

            GlobalVolume("Ambiente_Colina", a.transform, Profile("S3_Colina", p =>
            {
                Fog(p, 900f, 400f, new Color(0.95f, 0.93f, 1f));
                DreamSky(p, 14.1f);
            }), 1f);
            Save(scene, "S3_Colina");
        }
    }
}
