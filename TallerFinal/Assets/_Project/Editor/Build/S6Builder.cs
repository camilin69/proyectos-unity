using UnityEngine;
using static Dream.EditorTools.Build.BuildKit;

namespace Dream.EditorTools.Build
{
    // 6 · La piscina liminal, 22:40. Una sala enorme de azulejo blanco con el agua quieta; al fondo, una pared de cielo
    // pintado como la de El show de Truman, con su escalera y su puerta. El recuerdo esta bajo el agua, al pie de la escalera.
    public static class S6Builder
    {
        public static void Build()
        {
            var scene = NewScene();
            var a = Anchor(5, "La piscina liminal", new Vector3(0f, 0.02f, -20f), 0f, 22.67f, 23.4f, 4f);
            a.musicLowPass = 4500f; a.musicVolume = 0.7f; a.musicReverb = 0.9f; a.respawnBelowY = -10f;
            var cue = Cue(a.transform);
            var hall = Group("Sala");
            var tile = Palette.WhiteTile;
            var poolTile = ScanMat("M_Azulejo_Piscina", "long_white_tiles", new Color(0.62f, 0.88f, 0.93f), 0.8f, 0.5f, 0.95f);

            // cubierta solida alrededor del vaso (sus lados son las paredes de la piscina)
            BoxMinMax("Cubierta_O", hall, new Vector3(-20f, -1.8f, -30f), new Vector3(-12f, 0f, 46f), tile, SurfaceType.WetTile);
            BoxMinMax("Cubierta_E", hall, new Vector3(12f, -1.8f, -30f), new Vector3(20f, 0f, 46f), tile, SurfaceType.WetTile);
            BoxMinMax("Cubierta_S", hall, new Vector3(-12f, -1.8f, -30f), new Vector3(12f, 0f, -15f), tile, SurfaceType.WetTile);
            BoxMinMax("Cubierta_N", hall, new Vector3(-12f, -1.8f, 38f), new Vector3(12f, 0f, 46f), tile, SurfaceType.WetTile);
            BoxMinMax("Fondo_piscina", hall, new Vector3(-12f, -2.1f, -15f), new Vector3(12f, -1.8f, 38f), poolTile, SurfaceType.WetTile);
            var water = new GameObject("Agua");
            water.transform.SetParent(hall, false);
            water.transform.position = new Vector3(0f, -0.95f, 11.5f);
            water.AddComponent<BoxCollider>().size = new Vector3(24f, 1.7f, 53f);
            water.AddComponent<WaterZone>();
            Water("Superficie", hall, UnityEngine.Rendering.HighDefinition.WaterSurfaceType.Pool, new Vector3(0f, -0.1f, 11.5f), new Vector2(24f, 53f));

            // paredes, columnas y techo (abierto sobre la pared de cielo)
            BoxMinMax("Pared_O", hall, new Vector3(-20.5f, 0f, -30f), new Vector3(-20f, 14f, 46f), tile);
            BoxMinMax("Pared_E", hall, new Vector3(20f, 0f, -30f), new Vector3(20.5f, 14f, 46f), tile);
            BoxMinMax("Pared_S", hall, new Vector3(-20.5f, 0f, -30.5f), new Vector3(20.5f, 14f, -30f), tile);
            BoxMinMax("Techo", hall, new Vector3(-20.5f, 14f, -30.5f), new Vector3(20.5f, 14.4f, 28f), Palette.Cream);
            for (float z = -26f; z <= 26f; z += 7.5f)
                for (int s = -1; s <= 1; s += 2)
                    Prim(PrimitiveType.Cylinder, "Columna", hall, new Vector3(s * 16f, 7f, z), new Vector3(1.1f, 7f, 1.1f), tile, SurfaceType.Stone);
            for (float z = -24f; z <= 24f; z += 12f)
                for (int s = -1; s <= 1; s += 2)
                    AddLight("Luz_techo", hall, LightType.Rectangle, new Vector3(s * 8f, 13.8f, z), new Vector3(90f, 0f, 0f), new Color(0.9f, 0.95f, 1f), 5200f, 30f, 60f, new Vector2(3f, 1.2f));
            for (float z = -10f; z <= 34f; z += 11f)
                for (int s = -1; s <= 1; s += 2)
                    AddLight("Luz_bajo_agua", hall, LightType.Point, new Vector3(s * 11.6f, -1.3f, z), Vector3.zero, new Color(0.55f, 0.9f, 1f), 700f, 9f, 60f, null, false);

            // la pared de cielo pintado, con su puerta en (7.5, 7.6)
            var skyM = Mat("M_Cielo_Pintado", new Color(0.72f, 0.84f, 0.97f), 0.1f, 0f, new Color(0.75f, 0.86f, 1f), 260f);
            const float wz = 46f, wt = 0.5f, doorX0 = 6.88f, doorX1 = 8.12f, doorY0 = 7.6f, doorY1 = 9.92f;
            BoxMinMax("Cielo_I", hall, new Vector3(-30f, -1.8f, wz), new Vector3(doorX0, 34f, wz + wt), skyM);
            BoxMinMax("Cielo_D", hall, new Vector3(doorX1, -1.8f, wz), new Vector3(30f, 34f, wz + wt), skyM);
            BoxMinMax("Cielo_Bajo", hall, new Vector3(doorX0, -1.8f, wz), new Vector3(doorX1, doorY0, wz + wt), skyM);
            BoxMinMax("Cielo_Alto", hall, new Vector3(doorX0, doorY1, wz), new Vector3(doorX1, 34f, wz + wt), skyM);
            var door = Door("Puerta_Truman", hall, new Vector3(7.5f, doorY0, wz - 0.02f), 0f, Palette.Cream, Mat("M_Puerta_Cielo", new Color(0.72f, 0.84f, 0.97f), 0.2f));
            BoxMinMax("Mas_alla", hall, new Vector3(doorX0, doorY0 - 0.3f, wz + wt), new Vector3(doorX1, doorY0, wz + 3f), Palette.Carpet, SurfaceType.Carpet);
            Prim(PrimitiveType.Quad, "Resplandor_rosa", hall, new Vector3(7.5f, doorY0 + 1.2f, wz + 2.8f), new Vector3(2f, 3f, 1f),
                 Mat("M_Resplandor_Rosa", new Color(1f, 0.8f, 0.88f), 0f, 0f, new Color(1f, 0.72f, 0.84f), 8000f), null, Vector3.zero, false);

            // la escalera junto a la pared
            for (int i = 0; i < 20; i++)
            {
                float x0 = -10f + i * 0.8f;
                BoxMinMax($"Peldano_{i:00}", hall, new Vector3(x0, -1.8f, 43.5f), new Vector3(x0 + 0.8f, (i + 1) * 0.38f, 45.9f), tile, SurfaceType.Stone);
            }
            BoxMinMax("Descanso", hall, new Vector3(6f, -1.8f, 43.5f), new Vector3(9.5f, doorY0, 45.9f), tile, SurfaceType.Stone);
            CheckpointAt(a.transform, new Vector3(-11f, 0.05f, 41f), 90f, new Vector3(3f, 3f, 3f));
            Memory(a.transform, new Vector3(-9f, -0.95f, 35.5f), "Un eco que repite tu nombre en una sala vacía.");

            // llegada: sale de un hoyo oscuro en el piso
            Prim(PrimitiveType.Cylinder, "Hoyo_de_llegada", hall, new Vector3(0f, 0.01f, -25f), new Vector3(2.4f, 0.005f, 2.4f), Palette.Black, null, null, false);
            var wall = Point("Mira_pared_de_cielo", a.transform, new Vector3(0f, 9f, 46f));
            var w0 = Shot(1.2f, "negro");
            w0.from = CamPoint("Cam_Sala_A", a.transform, new Vector3(9f, 5f, -12f), new Vector3(0f, 1f, -24f));
            var w1 = Shot(5.5f, "sale del hoyo a la gran sala");
            w1.fadeColor = Color.black; w1.fadeInSeconds = 2.5f;
            w1.actorTeleport = Point("Desde_el_hoyo", a.transform, new Vector3(0f, 0.02f, -25f), 0f);
            w1.actorWalkTo = a.spawn; w1.actorSpeed = 1f;
            w1.from = w0.from; w1.to = CamPoint("Cam_Sala_B", a.transform, new Vector3(7f, 4f, -13f), Vector3.zero);
            w1.lookAtActorHead = true; w1.focalLength = 24f;
            var w2 = Shot(3.5f, "la pared de cielo al fondo");
            w2.from = CamPoint("Cam_Sala_C", a.transform, new Vector3(0.3f, 1.7f, -22.5f), Vector3.zero);
            w2.to = CamPoint("Cam_Sala_D", a.transform, new Vector3(0.3f, 1.7f, -21.2f), Vector3.zero);
            w2.lookAt = wall; w2.focalLength = 24f; w2.headLookAt = wall;
            a.arrival = Sequence("Cine_La_Sala", a.transform, w0, w1, w2);

            // salida: la puerta tipo Truman
            var beyond = Point("Mira_mas_alla", a.transform, new Vector3(7.5f, doorY0 + 1.2f, 47.5f));
            var d1 = Shot(4.5f, "la puerta del cielo pintado se abre");
            d1.from = CamPoint("Cam_Truman_A", a.transform, new Vector3(2f, 9.6f, 38.5f), Vector3.zero);
            d1.to = CamPoint("Cam_Truman_B", a.transform, new Vector3(3.6f, 10.2f, 39.5f), Vector3.zero);
            d1.lookAtActorHead = true; d1.focalLength = 50f; d1.headLookAt = beyond;
            d1.actorWalkTo = Point("Ante_la_puerta", a.transform, new Vector3(7.5f, doorY0, 45.2f), 0f); d1.actorSpeed = 0.8f;
            OnStart(d1, door.Open); OnStart(d1, cue.LightHum);
            var d2 = Shot(3.5f, "la cruza");
            d2.from = CamPoint("Cam_Truman_C", a.transform, new Vector3(5.6f, doorY0 + 1.3f, 42.6f), Vector3.zero);
            d2.lookAt = beyond; d2.focalLength = 35f;
            d2.actorWalkTo = Point("Al_otro_lado", a.transform, new Vector3(7.5f, doorY0, 48.4f), 0f); d2.actorSpeed = 1f;
            d2.fadeColor = Color.white; d2.fadeOutSeconds = 2.5f;
            Gate("Puerta_del_cielo", a.transform, new Vector3(7.5f, doorY0 + 1.1f, 44.9f), new Vector3(1.6f, 2.2f, 1.2f), Sequence("Cine_Truman", a.transform, d1, d2));

            GlobalVolume("Ambiente_Piscina", a.transform, Profile("S6_Piscina", p =>
            {
                Fog(p, 80f, 40f, new Color(0.92f, 0.96f, 1f));
                NightSky(p, 1f);
                ExposureLimits(p, 1.5f, 9f, 0.3f);
            }), 1f);
            Save(scene, "S6_Piscina");
        }
    }
}
