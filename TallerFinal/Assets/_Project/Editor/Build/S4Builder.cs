using UnityEngine;
using static Dream.EditorTools.Build.BuildKit;

namespace Dream.EditorTools.Build
{
    // 4 · El jardin inundado de noche, 20:00. Despierta en el pozo hondo del centro y sale del agua tomando aire;
    // vadea el agua poco profunda siguiendo los nenufares hasta el tunel en la orilla.
    public static class S4Builder
    {
        public static void Build()
        {
            var scene = NewScene();
            var a = Anchor(3, "El jardín inundado", new Vector3(0f, -2.6f, 0f), 45f, 20f, 20.6f, 4f);
            a.ambienceKind = AmbienceKind.NocheSuave; a.musicLowPass = 3500f; a.musicVolume = 0.75f; a.musicReverb = 0.55f; a.respawnBelowY = -12f;
            var cue = Cue(a.transform);
            var g = Group("Jardin");
            var stone = Mat("M_Fondo_Estanque", new Color(0.32f, 0.38f, 0.42f), 0.35f);
            var bank = Mat("M_Orilla", new Color(0.33f, 0.43f, 0.32f), 0.2f);

            // fondo: poco profundo alrededor, hondo en el centro
            const float shallow = -0.35f;
            BoxMinMax("Fondo_N", g, new Vector3(-18f, -1f, 5f), new Vector3(18f, shallow, 18f), stone, SurfaceType.Stone);
            BoxMinMax("Fondo_S", g, new Vector3(-18f, -1f, -18f), new Vector3(18f, shallow, -5f), stone, SurfaceType.Stone);
            BoxMinMax("Fondo_E", g, new Vector3(5f, -1f, -5f), new Vector3(18f, shallow, 5f), stone, SurfaceType.Stone);
            BoxMinMax("Fondo_O", g, new Vector3(-18f, -1f, -5f), new Vector3(-5f, shallow, 5f), stone, SurfaceType.Stone);
            BoxMinMax("Pozo", g, new Vector3(-5f, -3.6f, -5f), new Vector3(5f, -3.2f, 5f), stone, SurfaceType.Stone);
            BoxMinMax("Pozo_paredes_N", g, new Vector3(-5f, -3.2f, 4.8f), new Vector3(5f, -1f, 5f), stone);
            BoxMinMax("Pozo_paredes_S", g, new Vector3(-5f, -3.2f, -5f), new Vector3(5f, -1f, -4.8f), stone);
            BoxMinMax("Pozo_paredes_E", g, new Vector3(4.8f, -3.2f, -5f), new Vector3(5f, -1f, 5f), stone);
            BoxMinMax("Pozo_paredes_O", g, new Vector3(-5f, -3.2f, -5f), new Vector3(-4.8f, -1f, 5f), stone);

            var waterGo = new GameObject("Agua");
            waterGo.transform.SetParent(g, false);
            waterGo.transform.position = new Vector3(0f, -1.8f, 0f);
            waterGo.AddComponent<BoxCollider>().size = new Vector3(36f, 3.6f, 36f);
            waterGo.AddComponent<WaterZone>();
            Water("Superficie", g, UnityEngine.Rendering.HighDefinition.WaterSurfaceType.Pool, Vector3.zero, new Vector2(36f, 36f));
            ShootingStarsIn(a.transform);

            // orillas, con un hueco en la del este para el tunel y dos escalones para salir del agua
            const float top = 0.3f;
            BoxMinMax("Orilla_N", g, new Vector3(-30f, -2f, 18f), new Vector3(30f, top, 30f), bank, SurfaceType.Grass);
            BoxMinMax("Orilla_S", g, new Vector3(-30f, -2f, -30f), new Vector3(30f, top, -18f), bank, SurfaceType.Grass);
            BoxMinMax("Orilla_O", g, new Vector3(-30f, -2f, -18f), new Vector3(-18f, top, 18f), bank, SurfaceType.Grass);
            BoxMinMax("Orilla_E1", g, new Vector3(18f, -2f, -18f), new Vector3(30f, top, 5.1f), bank, SurfaceType.Grass);
            BoxMinMax("Orilla_E2", g, new Vector3(18f, -2f, 6.9f), new Vector3(30f, top, 18f), bank, SurfaceType.Grass);
            BoxMinMax("Orilla_E3", g, new Vector3(18f, -2f, 5.1f), new Vector3(23.1f, top, 6.9f), bank, SurfaceType.Grass);
            BoxMinMax("Orilla_E4", g, new Vector3(24.9f, -2f, 5.1f), new Vector3(30f, top, 6.9f), bank, SurfaceType.Grass);
            BoxMinMax("Escalon_1", g, new Vector3(16.6f, -1f, 2.5f), new Vector3(17.3f, -0.02f, 9f), Palette.Stone, SurfaceType.Stone);
            BoxMinMax("Escalon_2", g, new Vector3(17.3f, -1f, 2.5f), new Vector3(18f, top - 0.33f + 0.33f, 9f), Palette.Stone, SurfaceType.Stone);
            var shaftM = Palette.Black;
            BoxMinMax("Tunel_N", g, new Vector3(23.1f, -40f, 6.9f), new Vector3(24.9f, top - 0.01f, 7.1f), shaftM);
            BoxMinMax("Tunel_S", g, new Vector3(23.1f, -40f, 4.9f), new Vector3(24.9f, top - 0.01f, 5.1f), shaftM);
            BoxMinMax("Tunel_E", g, new Vector3(24.9f, -40f, 5.1f), new Vector3(25.1f, top - 0.01f, 6.9f), shaftM);
            BoxMinMax("Tunel_O", g, new Vector3(22.9f, -40f, 5.1f), new Vector3(23.1f, top - 0.01f, 6.9f), shaftM);
            var tunnel = Point("Mira_tunel", g, new Vector3(24f, top, 6f));

            // setos, estatuas y faroles
            for (int i = 0; i < 10; i++)
            {
                float x = -16f + i * 3.6f;
                Box($"Seto_N_{i}", g, new Vector3(x, top + 1.1f, 21f), new Vector3(2.8f, 2.2f, 1.2f), Palette.Hedge);
                Box($"Seto_S_{i}", g, new Vector3(x, top + 1.1f, -21f), new Vector3(2.8f, 2.2f, 1.2f), Palette.Hedge);
            }
            var statue = ScanMat("M_Marmol", "marble_01", new Color(1f, 1f, 1f), 1.5f, 0.3f, 0.9f);
            Vector3[] statues = { new(-21f, top, 10f), new(-21f, top, -10f), new(10f, top, -21.5f), new(-10f, top, 21.5f) };
            foreach (var s in statues)
            {
                Box("Pedestal", g, s + Vector3.up * 0.5f, new Vector3(1f, 1f, 1f), statue, SurfaceType.Stone);
                Prim(PrimitiveType.Capsule, "Estatua", g, s + Vector3.up * 2f, new Vector3(0.6f, 1f, 0.6f), statue, SurfaceType.Stone);
            }
            Vector3[] lamps = { new(-19f, top, 0f), new(0f, top, 19.5f), new(0f, top, -19.5f), new(19.5f, top, -8f), new(19.5f, top, 12f), new(-19f, top, 14f) };
            foreach (var l in lamps)
            {
                Prim(PrimitiveType.Cylinder, "Poste", g, l + Vector3.up * 1.2f, new Vector3(0.1f, 1.2f, 0.1f), Mat("M_Hierro", new Color(0.12f, 0.12f, 0.13f), 0.5f, 1f), SurfaceType.Stone);
                Prim(PrimitiveType.Sphere, "Farol", g, l + Vector3.up * 2.5f, Vector3.one * 0.35f, Mat("M_Farol", new Color(1f, 0.9f, 0.75f), 0.2f, 0f, new Color(1f, 0.78f, 0.55f), 3000f), null, null, false);
                AddLight("Luz_farol", g, LightType.Point, l + Vector3.up * 2.5f, Vector3.zero, new Color(1f, 0.78f, 0.55f), 520f, 10f);
            }

            // nenufares: el camino al tunel
            var pad = Mat("M_Nenufar", new Color(0.36f, 0.56f, 0.38f), 0.6f);
            var flower = Mat("M_Flor_Loto", new Color(1f, 0.82f, 0.9f), 0.3f, 0f, new Color(1f, 0.75f, 0.85f), 120f);
            Vector3 p0 = new(3f, 0f, 1f), p1 = new(16.3f, 0f, 5.3f);
            for (int i = 0; i < 11; i++)
            {
                var pos = Vector3.Lerp(p0, p1, i / 10f) + new Vector3(Mathf.Sin(i * 1.7f) * 1.2f, 0.02f, Mathf.Cos(i * 2.3f) * 1.0f);
                Prim(PrimitiveType.Cylinder, $"Nenufar_{i:00}", g, pos, new Vector3(1.4f, 0.01f, 1.4f), pad, null, null, false);
                if (i % 3 == 1) Prim(PrimitiveType.Sphere, "Flor", g, pos + Vector3.up * 0.12f, new Vector3(0.3f, 0.2f, 0.3f), flower, null, null, false);
            }
            Memory(a.transform, new Vector3(16.3f, 0.9f, 5.3f), "El agua guarda el cielo para que no se pierda.");

            // llegada: abre los ojos bajo el agua y sale tomando aire
            var w0 = Shot(1.6f, "negro y silencio");
            w0.from = CamPoint("Cam_Agua_A", a.transform, new Vector3(-3.5f, 0.18f, -2.5f), new Vector3(0f, 0.2f, 0f));
            var w1 = Shot(6f, "sale del agua con una respiracion profunda");
            w1.fadeColor = Color.black; w1.fadeInSeconds = 3f;
            w1.from = w0.from;
            w1.to = CamPoint("Cam_Agua_B", a.transform, new Vector3(-3f, 0.3f, -2f), new Vector3(0f, 0.2f, 0f));
            w1.lookAtActorHead = true; w1.focalLength = 35f; w1.actorTrigger = "Emerge";
            a.arrival = Sequence("Cine_Despertar_en_el_Agua", a.transform, w0, w1);

            // salida: se deja caer por el tunel
            var d1 = Shot(4.5f, "llega al tunel");
            d1.from = CamPoint("Cam_Tunel_A", a.transform, new Vector3(27f, 2.4f, 9f), Vector3.zero);
            d1.to = CamPoint("Cam_Tunel_B", a.transform, new Vector3(26.4f, 2f, 8.5f), Vector3.zero);
            d1.lookAt = tunnel; d1.focalLength = 35f; d1.headLookAt = tunnel;
            d1.actorWalkTo = Point("Sobre_el_tunel", a.transform, new Vector3(24f, top, 6f)); d1.actorSpeed = 1f;
            var d2 = Shot(2f, "cae");
            d2.from = CamPoint("Cam_Tunel_C", a.transform, new Vector3(24.6f, 3.5f, 7.2f), new Vector3(24f, -6f, 6f));
            d2.lookAt = Point("Fondo_tunel", a.transform, new Vector3(24f, -6f, 6f)); d2.focalLength = 28f;
            d2.fadeColor = Color.black; d2.fadeOutSeconds = 1.6f;
            Gate("El_tunel", a.transform, new Vector3(24f, top + 1f, 6f), new Vector3(1.6f, 2f, 1.6f), Sequence("Cine_El_Tunel", a.transform, d1, d2));
            CheckpointAt(a.transform, new Vector3(19f, top + 0.05f, 6f), 90f, new Vector3(2f, 3f, 4f));

            GlobalVolume("Ambiente_Jardin", a.transform, Profile("S4_Jardin", p => { Fog(p, 90f, 30f, new Color(0.62f, 0.72f, 0.92f)); NightSky(p, 1f); ExposureLimits(p, 0.3f, 4f, 0f); }), 1f);
            Save(scene, "S4_Jardin");
        }
    }
}
