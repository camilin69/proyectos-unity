using UnityEngine;
using UnityEngine.Rendering.HighDefinition;
using static Dream.EditorTools.Build.BuildKit;

namespace Dream.EditorTools.Build
{
    // 7 · La piscina liminal, 22:40 (video 42 de dream/, 17-24 s). Una nave mas chica de azulejo blanco: una pasarela
    // angosta de azulejo brillante cruza entre dos bandas de agua oscura sin fondo (quien cae, cae al vacio y vuelve
    // a aparecer en la pasarela), pilares gruesos que salen del agua y un techo de paneles de luz de colores que se
    // reflejan en el piso. Al fondo, la pared de cielo pintado como la de El show de Truman, con su escalera y su
    // puerta; el recuerdo espera al pie de la escalera.
    public static class S7Builder
    {
        public static void Build()
        {
            var scene = NewScene();
            var a = Anchor(6, "La piscina liminal", new Vector3(0f, 0.02f, -17f), 0f, 22.67f, 23.4f, 4f);
            a.musicLowPass = 4500f; a.musicVolume = 0.7f; a.musicReverb = 0.9f; a.respawnBelowY = -6f;
            var cue = Cue(a.transform);
            var hall = Group("Sala");
            var tile = Palette.WhiteTile;
            const float hx = 8f, z0 = -20f, z1 = 30f, low = 5f, high = 14f, deckZ = 24f;

            // ---------- la pasarela y el piso del fondo; a los lados, agua sin fondo ----------
            var walk = ScanMat("M_Pasarela_Iridiscente", "long_white_tiles", new Color(0.86f, 0.9f, 1f), 0.45f, 0.75f, 0.98f);
            var curb = ScanMat("M_Borde_Rosa", "long_white_tiles", new Color(1f, 0.8f, 0.88f), 0.45f, 0.6f, 0.95f);
            BoxMinMax("Pasarela", hall, new Vector3(-1.1f, -0.6f, z0), new Vector3(1.1f, 0f, deckZ), walk, SurfaceType.WetTile);
            BoxMinMax("Borde_I", hall, new Vector3(-1.3f, -0.6f, z0), new Vector3(-1.1f, 0.06f, deckZ), curb);
            BoxMinMax("Borde_D", hall, new Vector3(1.1f, -0.6f, z0), new Vector3(1.3f, 0.06f, deckZ), curb);
            BoxMinMax("Entrada", hall, new Vector3(-hx, -0.6f, z0 - 1f), new Vector3(hx, 0f, z0), tile, SurfaceType.WetTile);
            BoxMinMax("Cubierta_Fondo", hall, new Vector3(-hx, -0.6f, deckZ), new Vector3(hx, 0f, z1), tile, SurfaceType.WetTile);
            var water = Water("Agua_oscura", hall, WaterSurfaceType.Pool, new Vector3(0f, -0.12f, (z0 + deckZ) * 0.5f), new Vector2(hx * 2f, deckZ - z0));
            water.scatteringColor = new Color(0.01f, 0.025f, 0.05f);
            water.absorptionDistance = 1.2f;
            // debajo no hay nada: un negro que se traga la luz
            Prim(PrimitiveType.Quad, "Vacio", hall, new Vector3(0f, -30f, (z0 + deckZ) * 0.5f), new Vector3(60f, 80f, 1f), Palette.Black, null, new Vector3(90f, 0f, 0f), false);
            for (float z = z0 + 3f; z < deckZ; z += 9f)
                CheckpointAt(a.transform, new Vector3(0f, 0.05f, z), 0f, new Vector3(2.2f, 3f, 1f));

            // ---------- paredes, techo bajo con paneles de colores y, al fondo, el atrio alto ----------
            BoxMinMax("Pared_O", hall, new Vector3(-hx - 0.5f, -12f, z0 - 1f), new Vector3(-hx, high, z1), tile);
            BoxMinMax("Pared_E", hall, new Vector3(hx, -12f, z0 - 1f), new Vector3(hx + 0.5f, high, z1), tile);
            BoxMinMax("Pared_S_I", hall, new Vector3(-hx, -12f, z0 - 1.5f), new Vector3(-0.6f, low, z0 - 1f), tile);
            BoxMinMax("Pared_S_D", hall, new Vector3(0.6f, -12f, z0 - 1.5f), new Vector3(hx, low, z0 - 1f), tile);
            BoxMinMax("Pared_S_Alta", hall, new Vector3(-0.6f, 2.05f, z0 - 1.5f), new Vector3(0.6f, low, z0 - 1f), tile);
            Prim(PrimitiveType.Quad, "Tunel_de_donde_viene", hall, new Vector3(0f, 1f, z0 - 1.3f), new Vector3(1.2f, 2.1f, 1f), Palette.Black, null, new Vector3(0f, 180f, 0f), false);
            BoxMinMax("Techo_Bajo", hall, new Vector3(-hx, low, z0 - 1.5f), new Vector3(hx, low + 0.3f, deckZ), Palette.Cream);
            BoxMinMax("Dintel_Atrio", hall, new Vector3(-hx, low, deckZ - 0.3f), new Vector3(hx, high, deckZ), Palette.Cream);
            BoxMinMax("Techo_Atrio", hall, new Vector3(-hx, high, deckZ), new Vector3(hx, high + 0.3f, z1), Palette.Cream);
            Color[] glow = { new(1f, 0.55f, 0.75f), new(0.55f, 0.85f, 1f), new(1f, 0.92f, 0.6f), new(0.75f, 0.62f, 1f), new(1f, 0.97f, 0.94f) };
            var panelMats = new Material[glow.Length];
            for (int i = 0; i < glow.Length; i++) panelMats[i] = Mat($"M_Panel_Techo_{i}", glow[i], 0.3f, 0f, glow[i], 3500f);
            int k = 0;
            for (float z = z0 + 1f; z < deckZ - 1f; z += 3f)
                for (int s = -1; s <= 1; s += 2, k++)
                {
                    int c = (k * 3 + (int)(z * 7f)) % glow.Length; if (c < 0) c += glow.Length;
                    Prim(PrimitiveType.Quad, "Panel", hall, new Vector3(s * 2.6f, low - 0.01f, z), new Vector3(1.3f, 0.9f, 1f), panelMats[c], null, new Vector3(-90f, 0f, 0f), false);
                    if (k % 2 == 0)
                        AddLight("Luz_panel", hall, LightType.Point, new Vector3(s * 2.6f, low - 0.4f, z), Vector3.zero, glow[c], 650f, 9f, 60f, null, false);
                }

            // ---------- pilares gruesos que salen del agua, con su base ----------
            for (float z = z0 + 4f; z < deckZ; z += 7f)
                for (int s = -1; s <= 1; s += 2)
                {
                    Prim(PrimitiveType.Cylinder, "Pilar", hall, new Vector3(s * 4.8f, (low - 1f) * 0.5f, z), new Vector3(2.4f, (low + 1f) * 0.5f, 2.4f), tile, SurfaceType.Stone);
                    Prim(PrimitiveType.Cylinder, "Base_Pilar", hall, new Vector3(s * 4.8f, -0.1f, z), new Vector3(3.2f, 0.35f, 3.2f), tile, SurfaceType.Stone);
                    Prim(PrimitiveType.Cylinder, "Capitel", hall, new Vector3(s * 4.8f, low - 0.25f, z), new Vector3(3.0f, 0.25f, 3.0f), tile, null, null, false);
                }

            // ---------- la pared de cielo pintado, la escalera y la puerta ----------
            var skyM = Mat("M_Cielo_Pintado", new Color(0.72f, 0.84f, 0.97f), 0.1f, 0f, new Color(0.75f, 0.86f, 1f), 70f);
            const float wz = z1, wt = 0.5f, doorX0 = 3.0f, doorX1 = 4.24f, doorY0 = 6f, doorY1 = 8.32f;
            BoxMinMax("Cielo_I", hall, new Vector3(-hx, -0.6f, wz), new Vector3(doorX0, high, wz + wt), skyM);
            BoxMinMax("Cielo_D", hall, new Vector3(doorX1, -0.6f, wz), new Vector3(hx, high, wz + wt), skyM);
            BoxMinMax("Cielo_Bajo", hall, new Vector3(doorX0, -0.6f, wz), new Vector3(doorX1, doorY0, wz + wt), skyM);
            BoxMinMax("Cielo_Alto", hall, new Vector3(doorX0, doorY1, wz), new Vector3(doorX1, high, wz + wt), skyM);
            float doorX = (doorX0 + doorX1) * 0.5f;
            var door = Door("Puerta_Truman", hall, new Vector3(doorX, doorY0, wz - 0.02f), 0f, Palette.Cream, ScanMat("M_Puerta_Cielo", "painted_plaster_wall", new Color(0.72f, 0.84f, 0.97f), 1f, 0.15f, 0.45f));
            BoxMinMax("Mas_alla", hall, new Vector3(doorX0, doorY0 - 0.3f, wz + wt), new Vector3(doorX1, doorY0, wz + 3f), Palette.Carpet, SurfaceType.Carpet);
            Prim(PrimitiveType.Quad, "Resplandor_rosa", hall, new Vector3(doorX, doorY0 + 1.2f, wz + 2.8f), new Vector3(2f, 3f, 1f),
                 Mat("M_Resplandor_Rosa", new Color(1f, 0.8f, 0.88f), 0f, 0f, new Color(1f, 0.72f, 0.84f), 8000f), null, Vector3.zero, false);
            // escalera pegada a la pared: sube hacia +X hasta el descanso de la puerta
            const int steps = 16; const float rise = doorY0 / steps, run = 0.45f, sx0 = -5f;
            for (int i = 0; i < steps; i++)
            {
                float x = sx0 + i * run;
                BoxMinMax($"Peldano_{i:00}", hall, new Vector3(x, 0f, wz - 1.6f), new Vector3(x + run, (i + 1) * rise, wz), tile, SurfaceType.Stone);
            }
            float landX = sx0 + steps * run;
            BoxMinMax("Descanso", hall, new Vector3(landX, 0f, wz - 1.6f), new Vector3(hx, doorY0, wz), tile, SurfaceType.Stone);
            for (int i = 0; i < steps; i += 3)
                AddLight("Luz_escalera", hall, LightType.Point, new Vector3(sx0 + i * run, (i + 1) * rise + 1.4f, wz - 0.8f), Vector3.zero, new Color(1f, 0.8f, 0.88f), 220f, 4f, 60f, null, false);
            AddLight("Luz_Atrio", hall, LightType.Rectangle, new Vector3(0f, high - 0.05f, (deckZ + wz) * 0.5f), new Vector3(90f, 0f, 0f), new Color(1f, 0.9f, 0.95f), 6000f, 20f, 60f, new Vector2(10f, 3f), true);
            Memory(a.transform, new Vector3(sx0 - 0.8f, 1.0f, wz - 0.9f), "Un eco que repite tu nombre en una sala vacía.");
            CheckpointAt(a.transform, new Vector3(-2f, 0.05f, deckZ + 2f), 0f, new Vector3(4f, 3f, 3f));

            // ---------- llegada: sale de la luz del tunel a la pasarela ----------
            var wall = Point("Mira_pared_de_cielo", a.transform, new Vector3(0f, 6f, wz));
            var w0 = Shot(1.0f, "blanco");
            w0.from = CamPoint("Cam_Sala_A", a.transform, new Vector3(1.8f, 2.6f, -12f), new Vector3(0f, 1f, -19f));
            var w1 = Shot(5f, "sale del tunel a la pasarela entre el agua oscura");
            w1.fadeColor = Color.white; w1.fadeInSeconds = 2.5f;
            w1.actorTeleport = Point("Desde_el_tunel", a.transform, new Vector3(0f, 0.02f, z0 - 0.6f), 0f);
            w1.actorWalkTo = a.spawn; w1.actorSpeed = 0.9f;
            w1.from = w0.from; w1.to = CamPoint("Cam_Sala_B", a.transform, new Vector3(1.6f, 2.2f, -11f), Vector3.zero);
            w1.lookAtActorHead = true; w1.focalLength = 28f;
            var w2 = Shot(3.5f, "la pasarela hasta la pared de cielo");
            w2.from = CamPoint("Cam_Sala_C", a.transform, new Vector3(0.2f, 1.65f, -18.8f), Vector3.zero);
            w2.to = CamPoint("Cam_Sala_D", a.transform, new Vector3(0.2f, 1.65f, -17.8f), Vector3.zero);
            w2.lookAt = wall; w2.focalLength = 24f; w2.headLookAt = wall;
            a.arrival = Sequence("Cine_La_Sala", a.transform, w0, w1, w2);

            // ---------- salida: la puerta tipo Truman ----------
            var beyond = Point("Mira_mas_alla", a.transform, new Vector3(doorX, doorY0 + 1.2f, wz + 1.5f));
            var d1 = Shot(4.5f, "la puerta del cielo pintado se abre");
            d1.from = CamPoint("Cam_Truman_A", a.transform, new Vector3(-1f, 7.6f, wz - 6f), Vector3.zero);
            d1.to = CamPoint("Cam_Truman_B", a.transform, new Vector3(0.5f, 8f, wz - 5.2f), Vector3.zero);
            d1.lookAtActorHead = true; d1.focalLength = 50f; d1.headLookAt = beyond;
            d1.actorWalkTo = Point("Ante_la_puerta", a.transform, new Vector3(doorX, doorY0, wz - 0.8f), 0f); d1.actorSpeed = 0.8f;
            OnStart(d1, door.Open); OnStart(d1, cue.LightHum);
            var d2 = Shot(3.5f, "la cruza");
            d2.from = CamPoint("Cam_Truman_C", a.transform, new Vector3(doorX - 1.9f, doorY0 + 1.3f, wz - 3.2f), Vector3.zero);
            d2.lookAt = beyond; d2.focalLength = 35f;
            d2.actorWalkTo = Point("Al_otro_lado", a.transform, new Vector3(doorX, doorY0, wz + 2.4f), 0f); d2.actorSpeed = 1f;
            d2.fadeColor = Color.white; d2.fadeOutSeconds = 2.5f;
            Gate("Puerta_del_cielo", a.transform, new Vector3(doorX, doorY0 + 1.1f, wz - 1.1f), new Vector3(1.6f, 2.2f, 1.2f), Sequence("Cine_Truman", a.transform, d1, d2));

            GlobalVolume("Ambiente_Piscina", a.transform, Profile("S7_Piscina", p =>
            {
                Fog(p, 60f, 20f, new Color(0.95f, 0.92f, 1f));
                NightSky(p, 1f);
                ExposureLimits(p, 1.5f, 9f, 0.3f);
                var ind = p.Add<IndirectLightingController>();
                ind.indirectDiffuseLightingMultiplier.Override(0.3f);
            }), 1f);
            Save(scene, "S7_Piscina");
        }
    }
}
