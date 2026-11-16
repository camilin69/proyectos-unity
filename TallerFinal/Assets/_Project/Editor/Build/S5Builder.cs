using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering.HighDefinition;
using static Dream.EditorTools.Build.BuildKit;

namespace Dream.EditorTools.Build
{
    // 5 · El pasillo de las ondas, 20:40 (video 42 de dream/, 12-17 s). Un pasillo angosto de paredes rosadas que
    // baja por dos tramos de escalera; techo turquesa con lamparas de domo blancas, pasamanos oscuros, puertas
    // cerradas, carteles EXIT rojos y un piso brillante de ondas pastel. Abajo se bifurca: a la derecha, una luz al
    // final del pasillo (la salida a la playa); a la izquierda el techo se abre en un hueco alto que termina en un
    // vidrio con la luna llena justo encima, y al fondo una fuente pequena con un angel de marmol.
    public static class S5Builder
    {
        const string DreamDir = DreamScene.Dir + "/Pasillo_Ondas/tex";
        const float HalfW = 1.9f, Rise = 0.17f, Run = 0.3f;
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
            var wall = Mat("M_Pasillo_Pared_Rosa", Color.white, 0.86f);          // pintura laqueada: refleja las lamparas como el piso
            wall.SetTexture("_BaseColorMap", Tex("wave_wall_albedo.png"));
            wall.SetTexture("_NormalMap", Tex("wave_paint_normal.png", true)); wall.SetFloat("_NormalScale", 0.12f);
            wall.SetFloat("_UVBase", 5f); wall.SetFloat("_TexWorldScale", 1f / 2f);
            HDMaterial.ValidateMaterial(wall);
            var ceiling = Mat("M_Pasillo_Techo_Turquesa", Color.white, 0.55f);
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
            // el pasillo de abajo y la bifurcacion (el doble de largos que antes)
            const float F0 = 36f, F1 = F0 + 2f * HalfW, BL = 18f;
            float Fm = (F0 + F1) * 0.5f;
            BoxMinMax("Piso_Abajo", g, new Vector3(-HalfW, y2 - 0.4f, 18f), new Vector3(HalfW, y2, F1), floor, SurfaceType.WetTile);
            BoxMinMax("Piso_Rama_Der", g, new Vector3(HalfW, y2 - 0.4f, F0), new Vector3(BL, y2, F1), floor, SurfaceType.WetTile);
            BoxMinMax("Piso_Rama_Izq", g, new Vector3(-BL, y2 - 0.4f, F0), new Vector3(-HalfW, y2, F1), floor, SurfaceType.WetTile);

            // ---------- paredes rosadas ----------
            const float wallTop = 3.0f, wallBot = -3.8f;
            float c1 = 2.8f, c2 = y1 + 2.8f, c3 = y2 + 2.8f, shaftTop = y2 + 16f;
            BoxMinMax("Pared_Izq", g, new Vector3(-HalfW - 0.12f, wallBot, -3f), new Vector3(-HalfW, wallTop, F0), wall);
            BoxMinMax("Pared_Der", g, new Vector3(HalfW, wallBot, -3f), new Vector3(HalfW + 0.12f, wallTop, F0), wall);
            BoxMinMax("Pared_Fondo_Arriba", g, new Vector3(-HalfW, -0.4f, -3.12f), new Vector3(HalfW, wallTop, -3f), wall);
            BoxMinMax("Pared_Frente_Bifurcacion", g, new Vector3(-BL, wallBot, F1), new Vector3(BL, shaftTop, F1 + 0.12f), wall);
            BoxMinMax("Pared_Rama_Der", g, new Vector3(HalfW, wallBot, F0 - 0.12f), new Vector3(BL, c3, F0), wall);
            BoxMinMax("Pared_Rama_Izq", g, new Vector3(-BL, wallBot, F0 - 0.12f), new Vector3(-HalfW, shaftTop, F0), wall);
            DarkMirror(g, wall, -BL, F0, F1, y2, shaftTop, wallBot);
            BoxMinMax("Pared_Final_Der", g, new Vector3(BL, wallBot, F0), new Vector3(BL + 0.12f, c3 + 0.1f, F1), wall);
            // el hueco: sobre el cruce y la rama izquierda el techo no esta; las paredes suben hasta el vidrio
            BoxMinMax("Hueco_Pared_Sur", g, new Vector3(-HalfW, c3, F0 - 0.12f), new Vector3(HalfW, shaftTop, F0), wall);
            BoxMinMax("Hueco_Pared_Este", g, new Vector3(HalfW, c3, F0), new Vector3(HalfW + 0.12f, shaftTop, F1), wall);

            // ---------- techo turquesa, que baja con la escalera ----------
            BoxMinMax("Techo_1", g, new Vector3(-HalfW, c1, -3f), new Vector3(HalfW, c1 + 0.1f, 6f), ceiling);
            Slab("Techo_Tramo_1", g, ceiling, new Vector3(0f, c1, 6f), new Vector3(0f, c2, 9f));
            BoxMinMax("Techo_2", g, new Vector3(-HalfW, c2, 9f), new Vector3(HalfW, c2 + 0.1f, 15f), ceiling);
            Slab("Techo_Tramo_2", g, ceiling, new Vector3(0f, c2, 15f), new Vector3(0f, c3, 18f));
            BoxMinMax("Techo_3", g, new Vector3(-HalfW, c3, 18f), new Vector3(HalfW, c3 + 0.1f, F0), ceiling);
            BoxMinMax("Techo_Rama_Der", g, new Vector3(HalfW, c3, F0), new Vector3(BL, c3 + 0.1f, F1), ceiling);

            // ---------- el vidrio arriba del hueco, con su marco, y la luna justo encima ----------
            var glass = Mat("M_Vidrio_Claraboya", new Color(0.82f, 0.9f, 1f, 0.18f), 0.98f, 0f, null, 0f, true);
            var frameM = ScanMat("M_Marco_Claraboya", "metal_plate", new Color(0.2f, 0.21f, 0.23f), 0.5f, 0.4f, 0.8f);
            BoxMinMax("Claraboya", g, new Vector3(-BL, shaftTop, F0), new Vector3(HalfW, shaftTop + 0.04f, F1), glass);
            for (float x = -BL; x <= HalfW + 0.01f; x += 3.6f)
                BoxMinMax("Marco", g, new Vector3(x - 0.06f, shaftTop - 0.08f, F0), new Vector3(x + 0.06f, shaftTop + 0.06f, F1), frameM);
            BoxMinMax("Marco_S", g, new Vector3(-BL, shaftTop - 0.08f, F0), new Vector3(HalfW, shaftTop + 0.06f, F0 + 0.12f), frameM);
            BoxMinMax("Marco_N", g, new Vector3(-BL, shaftTop - 0.08f, F1 - 0.12f), new Vector3(HalfW, shaftTop + 0.06f, F1), frameM);
            BoxMinMax("Marco_C", g, new Vector3(-BL, shaftTop - 0.08f, Fm - 0.05f), new Vector3(HalfW, shaftTop + 0.06f, Fm + 0.05f), frameM);
            a.gameObject.AddComponent<MoonOverhead>();

            // ---------- pasamanos oscuros a los dos lados, con su soporte a la pared ----------
            foreach (float s in new[] { -1f, 1f })
            {
                float x = s * (HalfW - 0.07f);
                Rail(g, rail, new Vector3(x, 0.9f, 3f), new Vector3(x, 0.9f, 6f));
                Rail(g, rail, new Vector3(x, 0.9f, 6f), new Vector3(x, y1 + 0.9f, 9f));
                Rail(g, rail, new Vector3(x, y1 + 0.9f, 9f), new Vector3(x, y1 + 0.9f, 15f));
                Rail(g, rail, new Vector3(x, y1 + 0.9f, 15f), new Vector3(x, y2 + 0.9f, 18f));
                Rail(g, rail, new Vector3(x, y2 + 0.9f, 18f), new Vector3(x, y2 + 0.9f, 24f));
            }

            // ---------- puertas cerradas ----------
            DoorPanel(g, door, trim, -1f, 1.2f, 0f);
            DoorPanel(g, door, trim, -1f, 4.0f, 0f);
            DoorPanel(g, door, trim, -1f, 10.6f, y1);
            DoorPanel(g, door, trim, -1f, 13.2f, y1);
            DoorPanel(g, door, trim, 1f, 12.0f, y1);
            DoorPanel(g, door, trim, -1f, 22.5f, y2);
            DoorPanel(g, door, trim, -1f, 28.5f, y2);
            DoorPanel(g, door, trim, 1f, 26f, y2);
            DoorPanel(g, door, trim, 1f, 32.5f, y2);

            // ---------- carteles EXIT rojos, cerca del techo ----------
            ExitSign(g, exitMat, box, new Vector3(-HalfW + 0.03f, c1 - 0.35f, 5.4f), 90f);
            ExitSign(g, exitMat, box, new Vector3(HalfW - 0.03f, c1 - 0.35f, 5.9f), -90f);
            ExitSign(g, exitMat, box, new Vector3(-HalfW + 0.03f, c2 - 0.35f, 14.5f), 90f);
            ExitSign(g, exitMat, box, new Vector3(BL - 0.03f, c3 - 0.45f, Fm), -90f);

            // ---------- lamparas de domo: luz blanca calida que se repite y brilla en el piso mojado ----------
            var lamps = new System.Collections.Generic.List<Vector3>
            {
                new Vector3(0f, c1, 0f), new Vector3(0f, c1, 3.2f), new Vector3(0f, c1, 6.6f),
                new Vector3(0f, c2, 10.6f), new Vector3(0f, c2, 13.8f), new Vector3(0f, c2, 17f),
            };
            for (float z = 20.5f; z < F0 - 0.5f; z += 3.4f) lamps.Add(new Vector3(0f, c3, z));
            for (float x = 4.5f; x < BL - 1f; x += 4.2f) lamps.Add(new Vector3(x, c3, Fm));
            for (int i = 0; i < lamps.Count; i++)
            {
                var p = lamps[i];
                Prim(PrimitiveType.Sphere, $"Lampara_{i:00}", g, p - Vector3.up * 0.02f, new Vector3(0.62f, 0.16f, 0.62f), dome, null, null, false);
                bool shadows = i == 1 || i == 4 || i == 8;
                AddLight($"Luz_lampara_{i:00}", g, LightType.Point, p - Vector3.up * 0.18f, Vector3.zero, new Color(1f, 0.94f, 0.86f), 900f, 7f, 60f, null, shadows);
            }

            // ---------- bifurcacion ----------
            // derecha: la luz al final del pasillo
            Prim(PrimitiveType.Quad, "Luz_al_final", g, new Vector3(BL - 0.05f, y2 + 1.6f, Fm), new Vector3(2f * HalfW, 3.2f, 1f), Palette.BlindingLight, null, new Vector3(0f, 90f, 0f), false);
            AddLight("Luz_del_final", g, LightType.Rectangle, new Vector3(BL - 0.1f, y2 + 1.6f, Fm), new Vector3(0f, -90f, 0f), new Color(1f, 0.97f, 0.92f), 3500f, 16f, 60f, new Vector2(3.6f, 3f), false);
            // izquierda: bajo el hueco de la luna, la fuente del angel
            Fountain(g, new Vector3(-BL + 2.6f, y2, Fm));
            AddLight("Luz_de_luna", g, LightType.Spot, new Vector3(-BL + 2.6f, shaftTop - 0.5f, Fm), new Vector3(90f, 0f, 0f), new Color(0.78f, 0.84f, 1f), 4200f, 22f, 40f, null, true);
            // luz de luna que baja por el hueco y llena la rama izquierda, suave y fria
            for (float x = -4f; x > -BL + 3f; x -= 5f)
                AddLight("Luna_en_el_hueco", g, LightType.Point, new Vector3(x, y2 + 4.5f, Fm), Vector3.zero, new Color(0.8f, 0.85f, 1f), 1100f, 9f, 60f, null, false);

            Memory(a.transform, new Vector3(0f, y2 + 1.05f, Fm), "Todas las puertas daban al mismo pasillo; solo una tenía luz.");
            CheckpointAt(a.transform, new Vector3(0f, y1 + 0.05f, 12f), 0f, new Vector3(2f * HalfW, 2.4f, 1f));
            CheckpointAt(a.transform, new Vector3(0f, y2 + 0.05f, 30f), 0f, new Vector3(2f * HalfW, 2.4f, 1f));

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
            var d1 = Shot(5f, "camina hacia la luz");
            d1.from = CamPoint("Cam_Luz_A", a.transform, new Vector3(BL - 9.5f, y2 + 1.7f, Fm + 1.2f), new Vector3(BL, y2 + 1.4f, Fm));
            d1.to = CamPoint("Cam_Luz_B", a.transform, new Vector3(BL - 7.5f, y2 + 1.6f, Fm + 1f), new Vector3(BL, y2 + 1.4f, Fm));
            d1.lookAt = Point("Mira_luz", a.transform, new Vector3(BL - 0.1f, y2 + 1.4f, Fm)); d1.focalLength = 28f;
            d1.actorWalkTo = Point("Dentro_de_la_luz", a.transform, new Vector3(BL - 0.6f, y2 + 0.02f, Fm)); d1.actorSpeed = 1.1f;
            d1.fadeColor = Color.white; d1.fadeOutSeconds = 2f;
            Gate("La_luz_del_final", a.transform, new Vector3(BL - 1.8f, y2 + 1.2f, Fm), new Vector3(0.8f, 2.4f, 2f * HalfW), Sequence("Cine_La_Luz", a.transform, d1));

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

        // Fuente pequena con un angel de marmol de Carrara (blanco con vetas grises, pulido): la estatua tallada de
        // Poly Haven con alas de plumas modeladas en Blender (Art/Models/Generados/Alas_Angel.fbx), pila y pedestal del
        // mismo marmol, agua clara como la de la piscina y un chorro de manantial que cae del cantaro.
        static void Fountain(Transform g, Vector3 c)
        {
            var carrara = TexMat("M_Marmol_Carrara", "T_Marmol_Carrara.png", Color.white, 0.92f, false, null, 0.9f);
            var f = Point("Fuente_del_angel", g, c, 0f);
            AddLight("Luz_del_angel", f, LightType.Point, c + new Vector3(2.4f, 2.6f, 0f), Vector3.zero, new Color(0.95f, 0.95f, 1f), 450f, 6f, 60f, null, false);

            // pila de dos escalones con borde moldurado
            Prim(PrimitiveType.Cylinder, "Pila", f, c + Vector3.up * 0.28f, new Vector3(2.4f, 0.28f, 2.4f), carrara, SurfaceType.Stone);
            Prim(PrimitiveType.Cylinder, "Zocalo", f, c + Vector3.up * 0.05f, new Vector3(2.7f, 0.05f, 2.7f), carrara, null, null, false);
            Prim(PrimitiveType.Cylinder, "Borde", f, c + Vector3.up * 0.58f, new Vector3(2.55f, 0.04f, 2.55f), carrara, null, null, false);
            // agua clara (agua HDRP de piscina): se ve el fondo de marmol
            var water = Water("Agua_fuente", f, WaterSurfaceType.Pool, c + Vector3.up * 0.5f, new Vector2(2.1f, 2.1f));
            water.scatteringColor = new Color(0.2f, 0.75f, 0.8f);
            water.absorptionDistance = 3f;
            Prim(PrimitiveType.Cylinder, "Fondo_pila", f, c + Vector3.up * 0.3f, new Vector3(2.2f, 0.02f, 2.2f), carrara, null, null, false);
            Prim(PrimitiveType.Cylinder, "Pedestal", f, c + Vector3.up * 1.0f, new Vector3(0.9f, 0.45f, 0.9f), carrara, null, null, false);
            Prim(PrimitiveType.Cylinder, "Capitel", f, c + Vector3.up * 1.47f, new Vector3(1.1f, 0.04f, 1.1f), carrara, null, null, false);
            var body = c + Vector3.up * 1.5f;

            // la figura tallada
            var statue = PolyModel("gothic_statue", f, body, 180f, null, false);
            if (statue)
            {
                var b0 = Bounds(statue);
                float k = 1.55f / Mathf.Max(0.01f, b0.size.y);
                statue.transform.localScale *= k;
                var b1 = Bounds(statue);
                statue.transform.position += new Vector3(body.x - b1.center.x, body.y - b1.min.y, body.z - b1.center.z);
                var white = TexMat("M_Angel_Carrara", "T_Marmol_Carrara.png", Color.white, 0.9f, false, null, 0.6f);
                var nrmPath = ModelDir + "/gothic_statue/gothic_statue_normal.jpg";
                var imp = AssetImporter.GetAtPath(nrmPath) as TextureImporter;
                if (imp && imp.textureType != TextureImporterType.NormalMap) { imp.textureType = TextureImporterType.NormalMap; imp.SaveAndReimport(); }
                var nrm = AssetDatabase.LoadAssetAtPath<Texture2D>(nrmPath);
                if (nrm) { white.SetTexture("_NormalMap", nrm); white.SetFloat("_NormalScale", 1.3f); white.SetFloat("_UVBase", 0f); }
                HDMaterial.ValidateMaterial(white);
                foreach (var r in statue.GetComponentsInChildren<Renderer>())
                    r.sharedMaterials = Enumerable.Repeat(white, r.sharedMaterials.Length).ToArray();
            }

            // las alas de plumas (Blender), abiertas a la espalda
            var wingsSrc = AssetDatabase.LoadAssetAtPath<GameObject>(Root + "/Art/Models/Generados/Alas_Angel.fbx");
            if (wingsSrc)
            {
                var wings = (GameObject)Object.Instantiate(wingsSrc, f);
                wings.name = "Alas";
                wings.transform.position = new Vector3(c.x - 0.18f, body.y + 1.0f, c.z);
                wings.transform.rotation = Quaternion.Euler(0f, 90f, 0f) * wingsSrc.transform.rotation;   // la espalda mira a -X (al espejo)
                wings.transform.localScale = wingsSrc.transform.localScale * 1.05f;
                foreach (var r in wings.GetComponentsInChildren<Renderer>()) r.sharedMaterial = carrara;
            }

            // el cantaro y el chorro de manantial: agua clara, continua, que salpica al caer
            Prim(PrimitiveType.Sphere, "Cantaro", f, body + new Vector3(0.62f, -0.05f, 0f), new Vector3(0.22f, 0.26f, 0.22f), carrara, null, null, false);
            var jet = new GameObject("Chorro");
            jet.transform.SetParent(f, false);
            jet.transform.position = body + new Vector3(0.75f, 0.02f, 0f);
            jet.transform.rotation = Quaternion.LookRotation(Vector3.right);
            var ps = jet.AddComponent<ParticleSystem>();
            var main = ps.main;
            main.loop = true; main.prewarm = true; main.maxParticles = 600;
            main.startLifetime = 0.5f; main.startSpeed = new ParticleSystem.MinMaxCurve(0.45f, 0.55f);
            main.startSize = new ParticleSystem.MinMaxCurve(0.035f, 0.05f); main.gravityModifier = 1f;
            var em = ps.emission; em.rateOverTime = 700f;
            var sh = ps.shape; sh.shapeType = ParticleSystemShapeType.Cone; sh.angle = 1.5f; sh.radius = 0.012f;
            var col = ps.collision; col.enabled = true; col.type = ParticleSystemCollisionType.World; col.bounce = 0.15f; col.lifetimeLoss = 0.6f;
            var pr = jet.GetComponent<ParticleSystemRenderer>();
            pr.renderMode = ParticleSystemRenderMode.Stretch; pr.velocityScale = 0.12f; pr.lengthScale = 1.5f;
            pr.sharedMaterial = Mat("M_Agua_Manantial", new Color(0.82f, 0.94f, 1f, 0.45f), 0.98f, 0f, new Color(0.75f, 0.9f, 1f), 12f, true);
            pr.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
        }

        // Toda la pared del fondo es un espejo grande con marco: un vidrio oscuro que apenas devuelve el reflejo.
        // Detras hay una minisala vacia y a oscuras; se intuye que hay algo al otro lado, pero solo se ve negro.
        static void DarkMirror(Transform g, Material wall, float x, float z0, float z1, float floorY, float top, float bottom)
        {
            const float depth = 4f;
            var dark = Mat("M_Sala_Oscura", new Color(0.03f, 0.03f, 0.035f), 0.3f);
            // la minisala de atras (cerrada, sin luces)
            BoxMinMax("Sala_oscura_piso", g, new Vector3(x - depth, floorY - 0.4f, z0), new Vector3(x, floorY, z1), dark);
            BoxMinMax("Sala_oscura_fondo", g, new Vector3(x - depth - 0.12f, bottom, z0), new Vector3(x - depth, top, z1), dark);
            BoxMinMax("Sala_oscura_N", g, new Vector3(x - depth, bottom, z1), new Vector3(x, top, z1 + 0.12f), dark);
            BoxMinMax("Sala_oscura_S", g, new Vector3(x - depth, bottom, z0 - 0.12f), new Vector3(x, top, z0), dark);
            BoxMinMax("Sala_oscura_techo", g, new Vector3(x - depth, top, z0), new Vector3(x, top + 0.12f, z1), dark);
            // un banco y una silueta de puerta apenas insinuados en la penumbra
            Box("Banco_en_la_oscuridad", g, new Vector3(x - 2.6f, floorY + 0.25f, (z0 + z1) * 0.5f), new Vector3(0.5f, 0.5f, 1.6f), dark);
            // el vidrio-espejo: liso, casi negro, muy brillante (refleja poco y oscuro)
            float h = 5.2f;
            var glass = Mat("M_Espejo_Oscuro", new Color(0.02f, 0.02f, 0.025f, 0.78f), 1f, 0.6f, null, 0f, true);
            BoxMinMax("Espejo_oscuro", g, new Vector3(x - 0.03f, floorY + 0.15f, z0 + 0.25f), new Vector3(x, floorY + h, z1 - 0.25f), glass);
            // el marco dorado envejecido
            var gold = ScanMat("M_Marco_Espejo", "metal_plate", new Color(0.62f, 0.5f, 0.3f), 0.5f, 0.45f, 0.8f);
            gold.SetFloat("_Metallic", 1f);
            BoxMinMax("Marco_arriba", g, new Vector3(x, floorY + h, z0 + 0.1f), new Vector3(x + 0.12f, floorY + h + 0.22f, z1 - 0.1f), gold);
            BoxMinMax("Marco_abajo", g, new Vector3(x, floorY, z0 + 0.1f), new Vector3(x + 0.12f, floorY + 0.15f, z1 - 0.1f), gold);
            BoxMinMax("Marco_S", g, new Vector3(x, floorY, z0 + 0.1f), new Vector3(x + 0.12f, floorY + h + 0.22f, z0 + 0.25f), gold);
            BoxMinMax("Marco_N", g, new Vector3(x, floorY, z1 - 0.25f), new Vector3(x + 0.12f, floorY + h + 0.22f, z1 - 0.1f), gold);
            // la pared rosa sigue por encima del espejo hasta el vidrio del techo, y a los lados del marco
            BoxMinMax("Pared_sobre_espejo", g, new Vector3(x - 0.12f, floorY + h + 0.22f, z0), new Vector3(x, top, z1), wall);
            BoxMinMax("Pared_lado_S", g, new Vector3(x - 0.12f, bottom, z0), new Vector3(x, floorY + h + 0.22f, z0 + 0.1f), wall);
            BoxMinMax("Pared_lado_N", g, new Vector3(x - 0.12f, bottom, z1 - 0.1f), new Vector3(x, floorY + h + 0.22f, z1), wall);
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
