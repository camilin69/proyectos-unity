using UnityEditor;
using UnityEngine;
using static Dream.EditorTools.Build.BuildKit;

namespace Dream.EditorTools.Build
{
    // 1 · El cuarto de azulejo rosa y menta, 07:00. Suelo inundado con una lamina de agua, ventana con cortina de
    // cuadros y la puerta que se abre a una luz tan blanca que no deja ver nada.
    public static class S1Builder
    {
        // gira el HDRI para que el resplandor del amanecer quede en la ventana (pared +Z)
        public const float HdriRotation = 0f;
        // la ventana (pared +Z) mira al sol de la manana, que sale por -X a las 07:00
        public const float RoomYaw = -84f;
        const string DreamTex = "Assets/_Project/Art/Textures/Dream";

        public static void Build()
        {
            var scene = NewScene();
            var a = Anchor(0, "El cuarto", new Vector3(-1.3f, 0.02f, 0.3f), 55f, 7f, 8.6f, 4f);
            a.finaleSpawn = Point("Regreso", a.transform, new Vector3(2.3f, 0.02f, 0f), 270f);
            a.musicLowPass = 2400f; a.musicVolume = 0.7f; a.musicReverb = 0.35f; a.respawnBelowY = -10f;
            var cue = Cue(a.transform);

            var room = Group("Cuarto");
            var pink = DreamWall(); var mint = pink; var cream = Mat("M_Techo_Blanco", new Color(0.97f, 0.96f, 0.94f), 0.4f); var wood = Palette.Wood;
            var ivory = Mat("M_Marfil", new Color(0.96f, 0.94f, 0.9f), 0.65f);
            BoxMinMax("Piso", room, new Vector3(-3f, -0.1f, -2.5f), new Vector3(3f, 0f, 2.5f), DreamFloor(), SurfaceType.WetTile);
            // el suelo inundado es el propio azulejo muy liso: refleja la ventana como una lamina de agua
            BoxMinMax("Umbral", room, new Vector3(3f, -0.1f, -0.62f), new Vector3(5f, 0f, 0.62f), Palette.Stone, SurfaceType.Stone);

            const float t = 0.15f, H = 3.2f;
            BoxMinMax("Pared_Fondo_I", room, new Vector3(-3f, 0f, 2.5f), new Vector3(-1f, H, 2.5f + t), mint);
            BoxMinMax("Pared_Fondo_D", room, new Vector3(1f, 0f, 2.5f), new Vector3(3f, H, 2.5f + t), mint);
            BoxMinMax("Pared_Fondo_Bajo", room, new Vector3(-1f, 0f, 2.5f), new Vector3(1f, 1f, 2.5f + t), mint);
            BoxMinMax("Pared_Fondo_Alto", room, new Vector3(-1f, 2.4f, 2.5f), new Vector3(1f, H, 2.5f + t), mint);
            BoxMinMax("Pared_Frente", room, new Vector3(-3f, 0f, -2.5f - t), new Vector3(3f, H, -2.5f), pink);
            BoxMinMax("Pared_Izq", room, new Vector3(-3f - t, 0f, -2.5f), new Vector3(-3f, H, 2.5f), pink);
            BoxMinMax("Pared_Der_A", room, new Vector3(3f, 0f, -2.5f), new Vector3(3f + t, H, -0.62f), pink);
            BoxMinMax("Pared_Der_B", room, new Vector3(3f, 0f, 0.62f), new Vector3(3f + t, H, 2.5f), pink);
            BoxMinMax("Pared_Der_Dintel", room, new Vector3(3f, 2.32f, -0.62f), new Vector3(3f + t, H, 0.62f), pink);
            BoxMinMax("Techo", room, new Vector3(-3.2f, H, -2.7f), new Vector3(3.2f, H + 0.15f, 2.7f), cream);
            BoxMinMax("Zocalo_I", room, new Vector3(-2.99f, 0f, -2.5f), new Vector3(-2.93f, 0.12f, 2.5f), ivory);
            BoxMinMax("Zocalo_F", room, new Vector3(-3f, 0f, -2.49f), new Vector3(3f, 0.12f, -2.43f), ivory);
            BoxMinMax("Cornisa", room, new Vector3(-3f, 3.12f, -2.5f), new Vector3(3f, 3.2f, 2.5f), ivory);

            // cama, mesa de noche, lampara

            // ventana: luz de manana que entra baja y la cortina de cuadros
            var checker = Mat("M_Cortina_Escocesa", Color.white, 0.12f, 0f, null, 0f, false, true);
            checker.SetTexture("_BaseColorMap", AssetDatabase.LoadAssetAtPath<Texture2D>(DreamTex + "/curtain_plaid.png"));
            checker.SetTextureScale("_BaseColorMap", new Vector2(2f, 3f));
            Prim(PrimitiveType.Quad, "Cortina_I", room, new Vector3(-0.55f, 1.75f, 2.36f), new Vector3(1.0f, 1.6f, 1f), checker, null, new Vector3(0f, 180f, 0f), false);
            Prim(PrimitiveType.Quad, "Cortina_D", room, new Vector3(0.78f, 1.75f, 2.36f), new Vector3(0.5f, 1.6f, 1f), checker, null, new Vector3(0f, 180f, 0f), false);

            Details(room);
            Memory(room, new Vector3(0.62f, 0.32f, 2.2f), "La luz de la mañana en el azulejo. Alguien abre la ventana para que entre el día.");

            // la puerta y la luz cegadora detras
            var door = Door("Puerta", room, new Vector3(3.07f, 0f, 0f), 90f, ivory, ivory);
            for (int side = -1; side <= 1; side += 2)                       // seis paneles por cara, como en dream/
                foreach (var (py, ph) in new[] { (0.45f, 0.62f), (1.18f, 0.5f), (1.8f, 0.5f) })
                    foreach (var px in new[] { -0.22f, 0.22f })
                    {
                        var pn = Box("Panel", door.hinge, new Vector3(3.07f + side * 0.032f, py, -px), new Vector3(0.012f, ph, 0.34f), ivory);
                        Static(pn, false);
                    }
            door.hinge.rotation = Quaternion.Euler(0f, 90f + 100f, 0f);     // abierta hacia adentro: afuera, las nubes
            var doorLight = Group("Luz_de_la_puerta", room);
            Prim(PrimitiveType.Quad, "Luz_cegadora", doorLight, new Vector3(4.2f, 1.4f, 0f), new Vector3(3f, 3.2f, 1f), Palette.BlindingLight, null, new Vector3(0f, 90f, 0f), false);
            AddLight("Foco_de_luz", doorLight, LightType.Spot, new Vector3(4.0f, 1.5f, 0f), new Vector3(0f, -90f, 0f), new Color(1f, 0.97f, 0.92f), 30000f, 14f, 110f);
            doorLight.gameObject.SetActive(false);
            var lightTarget = Point("Mira_luz", room, new Vector3(4.1f, 1.5f, 0f));
            var window = Point("Mira_ventana", room, new Vector3(0f, 1.7f, 2.6f));

            // llegada: despertar
            var w1 = Shot(5.5f, "despierta: la cara sin rostro a la luz de la ventana");
            w1.fadeColor = Color.white; w1.fadeInSeconds = 3.5f;
            w1.from = CamPoint("Cam_Despertar_A", a.transform, new Vector3(0.9f, 1.25f, -1.6f), Vector3.zero);
            w1.to = CamPoint("Cam_Despertar_B", a.transform, new Vector3(0.5f, 1.4f, -1.25f), Vector3.zero);
            w1.lookAtActorHead = true; w1.focalLength = 40f; w1.focalLengthEnd = 55f; w1.headLookAt = window;
            var w2 = Shot(2.5f, "mira hacia la ventana");
            w2.to = CamPoint("Cam_Despertar_C", a.transform, new Vector3(-1.1f, 1.62f, 0.05f), new Vector3(0f, 1.7f, 2.5f));
            w2.focalLength = 30f; w2.headLookAt = window;
            a.arrival = Sequence("Cine_Despertar", a.transform, w1, w2);

            // salida: la puerta de luz
            var d1 = Shot(4.5f, "la puerta se abre; el sonador gira la cabeza hacia la luz");
            d1.from = CamPoint("Cam_Puerta_A", a.transform, new Vector3(1.1f, 1.45f, -1.35f), Vector3.zero);
            d1.to = CamPoint("Cam_Puerta_B", a.transform, new Vector3(1.45f, 1.52f, -1.0f), Vector3.zero);
            d1.lookAtActorHead = true; d1.focalLength = 50f; d1.headLookAt = lightTarget;
            d1.actorWalkTo = Point("Ante_la_puerta", a.transform, new Vector3(2.35f, 0f, 0f), 90f); d1.actorSpeed = 0.8f;
            UnityEditor.Events.UnityEventTools.AddBoolPersistentListener(d1.onStart, doorLight.gameObject.SetActive, true);
            OnStart(d1, cue.LightHum);
            var d2 = Shot(4f, "entra en la luz");
            d2.from = CamPoint("Cam_Puerta_C", a.transform, new Vector3(0.6f, 1.62f, 0.25f), Vector3.zero);
            d2.to = CamPoint("Cam_Puerta_D", a.transform, new Vector3(1.7f, 1.58f, 0.1f), Vector3.zero);
            d2.lookAt = lightTarget; d2.focalLength = 35f;
            d2.actorWalkTo = Point("Dentro_de_la_luz", a.transform, new Vector3(4.4f, 0f, 0f), 90f); d2.actorSpeed = 1f;
            d2.fadeColor = Color.white; d2.fadeOutSeconds = 2.8f;
            var gate = Gate("Paso_Puerta", room, new Vector3(2.55f, 1.1f, 0f), new Vector3(0.7f, 2.2f, 1.2f), Sequence("Cine_Puerta_de_Luz", a.transform, d1, d2));
            gate.lockedHint = "La puerta no cede. Algo en el cuarto quiere que lo recuerdes.";

            // regreso: medianoche en el mismo cuarto
            var f1 = Shot(6f, "vuelve al cuarto: es medianoche");
            f1.fadeColor = Color.white; f1.fadeInSeconds = 4f;
            f1.from = CamPoint("Cam_Regreso_A", a.transform, new Vector3(-2.2f, 1.5f, -1.9f), Vector3.zero);
            f1.to = CamPoint("Cam_Regreso_B", a.transform, new Vector3(-1.8f, 1.55f, -1.5f), Vector3.zero);
            f1.lookAtActorHead = true; f1.focalLength = 35f; f1.headLookAt = window;
            var f2 = Shot(5f, "la ventana y el cielo de medianoche");
            f2.from = CamPoint("Cam_Regreso_C", a.transform, new Vector3(-0.5f, 1.6f, 0.8f), Vector3.zero);
            f2.to = CamPoint("Cam_Regreso_D", a.transform, new Vector3(0f, 1.7f, 1.7f), Vector3.zero);
            f2.lookAt = window; f2.focalLength = 30f;
            a.finaleArrival = Sequence("Cine_Regreso", a.transform, f1, f2);

            var p = Profile("S1_Cuarto", pr =>
            {
                Fog(pr, 70f, 8f, new Color(1f, 0.93f, 0.95f));
                var ex = pr.Add<UnityEngine.Rendering.HighDefinition.Exposure>();
                ex.compensation.Override(0.4f);
                // el cielo no entra entero a un cuarto cerrado: menos luz indirecta del cielo (si no, el pasto del HDRI tine de verde el techo)
                var ind = pr.Add<UnityEngine.Rendering.HighDefinition.IndirectLightingController>();
                ind.indirectDiffuseLightingMultiplier.Override(0.06f);   // cuarto cerrado: la luz es la del sol que entra
                ind.reflectionLightingMultiplier.Override(0.3f);
            });
            GlobalVolume("Ambiente_Cuarto", a.transform, p, 1f);
            // de dia, por la ventana se ve un amanecer fotografiado; en el regreso (00:00), el cielo de estrellas
            var clouds = Hdri("dream_cloud_sky.png");                     // el panorama de nubes del proyecto dream/
            a.dayOnly = GlobalVolume("Cielo_de_Nubes", a.transform, Profile("S1_Cielo_de_Nubes", pr =>
            {
                HdriSkyOverride(pr, clouds, HdriRotation, 7000f);
                RoomFog(pr, 30f, 12f, new Color(1f, 0.97f, 0.93f));         // aire leve afuera; el polvo denso esta dentro del cuarto (DustMotes)
            }), 2f).gameObject;
            a.nightOnly = GlobalVolume("Cielo_Medianoche", a.transform, Profile("S1_Cielo_Medianoche", pr =>
            {
                NightSky(pr, 1.4f);
                ExposureLimits(pr, 0.5f, 6f, 0.4f);
            }), 2f).gameObject;
            a.nightOnly.SetActive(false);
            room.RotateAround(Vector3.zero, Vector3.up, RoomYaw);
            a.transform.RotateAround(Vector3.zero, Vector3.up, RoomYaw);
            Save(scene, "S1_Cuarto");
        }

        // Los detalles que hacen que el cuarto se sienta habitado.
        static void Details(Transform room)
        {
            var d = Group("Detalles", room);
            var white = Mat("M_Pintura_Blanca", new Color(0.95f, 0.94f, 0.92f), 0.55f);
            var wood = Palette.Wood;
            var brass = Mat("M_Laton", new Color(0.85f, 0.7f, 0.45f), 0.8f, 1f);

            // ventana: marco, travesanos, vidrio, alfeizar y barra de la cortina
            const float wz = 2.5f;
            BoxMinMax("Marco_I", d, new Vector3(-1.06f, 0.94f, wz - 0.04f), new Vector3(-0.98f, 2.46f, wz + 0.16f), white);
            BoxMinMax("Marco_D", d, new Vector3(0.98f, 0.94f, wz - 0.04f), new Vector3(1.06f, 2.46f, wz + 0.16f), white);
            BoxMinMax("Marco_Alto", d, new Vector3(-1.06f, 2.38f, wz - 0.04f), new Vector3(1.06f, 2.46f, wz + 0.16f), white);
            BoxMinMax("Alfeizar", d, new Vector3(-1.15f, 0.94f, wz - 0.16f), new Vector3(1.15f, 1.0f, wz + 0.16f), white, SurfaceType.Wood);
            BoxMinMax("Travesano_V", d, new Vector3(-0.025f, 1f, wz + 0.05f), new Vector3(0.025f, 2.38f, wz + 0.1f), white);
            BoxMinMax("Travesano_H", d, new Vector3(-0.98f, 1.68f, wz + 0.05f), new Vector3(0.98f, 1.73f, wz + 0.1f), white);
            var glass = Mat("M_Vidrio", new Color(0.92f, 0.96f, 1f, 0.06f), 1f, 0f, null, 0f, true);
            var pane = Prim(PrimitiveType.Quad, "Vidrio", d, new Vector3(0f, 1.69f, wz + 0.075f), new Vector3(1.96f, 1.38f, 1f), glass, null, new Vector3(0f, 180f, 0f), false);
            Static(pane, false);
            pane.GetComponent<Renderer>().shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;   // el sol entra y dibuja el marco en el piso
            Prim(PrimitiveType.Cylinder, "Barra_cortina", d, new Vector3(0f, 2.58f, wz - 0.12f), new Vector3(0.025f, 1.3f, 0.025f), brass, null, new Vector3(0f, 0f, 90f), false);

            // zocalos de madera en las cuatro paredes
            BoxMinMax("Zocalo_Fondo", d, new Vector3(-3f, 0f, 2.47f), new Vector3(3f, 0.1f, 2.5f), wood);
            BoxMinMax("Zocalo_Der_A", d, new Vector3(2.97f, 0f, -2.5f), new Vector3(3f, 0.1f, -0.62f), wood);
            BoxMinMax("Zocalo_Der_B", d, new Vector3(2.97f, 0f, 0.62f), new Vector3(3f, 0.1f, 2.5f), wood);

            // muebles reales (Poly Haven, CC0): cama de hierro, mesa de noche, reloj, espejo, planta y lampara
            Radiator(d);
            DustMotes(d);

            // lampara de techo

            // sin sonda de reflejos en tiempo real: en la Intel HD 630 su render de 6 caras provocaba un reinicio de la GPU (TDR).
            // El espejo y el azulejo reflejan con SSR y el cielo.
        }

        static void Furniture(Transform d)
        {
            // cama de hierro con su colchon, cobija y almohadas; el cabecero alto contra la pared del fondo
            var bed = PolyModel("old_bed_frame", d, new Vector3(-2.15f, 0f, 1.05f), 0f, SurfaceType.Wood);
            if (bed)
            {
                // el cabecero (el extremo mas alto) va contra la pared del fondo (+Z)
                var mf = bed.GetComponentInChildren<MeshFilter>();
                float hiPos = -9f, hiNeg = -9f;
                foreach (var v in mf.sharedMesh.vertices)
                {
                    var w = mf.transform.TransformPoint(v);
                    if (w.z > 1.6f) hiPos = Mathf.Max(hiPos, w.y);
                    if (w.z < 0.5f) hiNeg = Mathf.Max(hiNeg, w.y);
                }
                if (hiNeg > hiPos) bed.transform.RotateAround(new Vector3(-2.15f, 0f, 1.05f), Vector3.up, 180f);
            }
            var cotton = ScanMat("M_Colchon", "cotton_jersey", new Color(1f, 0.98f, 0.95f), 0.6f, 0f, 0.25f);
            var blanket = ScanMat("M_Cobija", "cotton_jersey", new Color(1f, 0.74f, 0.82f), 0.5f, 0f, 0.3f);
            Box("Colchon", d, new Vector3(-2.15f, 0.47f, 1.0f), new Vector3(0.84f, 0.2f, 1.9f), cotton, SurfaceType.Carpet);
            Box("Cobija", d, new Vector3(-2.15f, 0.585f, 0.55f), new Vector3(0.9f, 0.05f, 1.15f), blanket);
            Box("Doblez", d, new Vector3(-2.15f, 0.62f, 1.12f), new Vector3(0.9f, 0.04f, 0.18f), blanket);
            Box("Almohada", d, new Vector3(-2.15f, 0.64f, 1.72f), new Vector3(0.62f, 0.13f, 0.34f), Palette.MintTile);

            // mesa de noche con reloj despertador y libros
            PolyModel("painted_wooden_nightstand", d, new Vector3(-2.7f, 0f, -0.75f), 90f, SurfaceType.Wood);
            PolyModel("alarm_clock_01", d, new Vector3(-2.62f, 0.62f, -0.62f), 115f, null, false);

            // espejo ornamentado en la pared rosa del frente, mirando al cuarto
            PolyModel("ornate_mirror_01", d, new Vector3(0.9f, 1.15f, -2.48f), 0f, null, false);

            // planta en la esquina junto a la ventana
            PolyModel("potted_plant_01", d, new Vector3(2.45f, 0f, 2.0f), 30f, SurfaceType.Stone);

            // lampara colgante con su luz calida
            var lamp = PolyModel("modern_ceiling_lamp_01", d, new Vector3(0f, 2.25f, 0f), 0f, null, false);
            AddLight("Luz_lampara", d, LightType.Point, new Vector3(0f, 2.45f, 0f), Vector3.zero, new Color(1f, 0.86f, 0.72f), 650f, 8f);

            // rebote del piso: en un cuarto real el techo se ilumina con la luz que rebota en el suelo
            AddLight("Rebote_suelo", d, LightType.Rectangle, new Vector3(0f, 0.05f, 0f), new Vector3(-90f, 0f, 0f), new Color(1f, 0.9f, 0.88f), 5000f, 6f, 60f, new Vector2(5f, 4f), false);
        }

        // Azulejo de 20 cm con la regla de color de dream/blender/build_room.py: franja menta arriba, franja rosa debajo
        // y bloques rosa/menta en el resto. Una textura cuadrada de 9,6 m en triplanar del mundo cubre todas las paredes.
        static Material DreamWall()
        {
            string path = TexDir + "/T_Azulejo_Dream.png";
            const int px = 2048; const float span = 9.6f, tile = 0.2f;
            var tex = new Texture2D(px, px, TextureFormat.RGBA32, false);
            var pink = new Color(0.95f, 0.6f, 0.72f); var mint = new Color(0.55f, 0.8f, 0.71f); var grout = new Color(0.93f, 0.92f, 0.9f);
            var rng = new System.Random(35);
            var shade = new float[48 * 48];
            for (int i = 0; i < shade.Length; i++) shade[i] = 0.95f + (float)rng.NextDouble() * 0.08f;   // cada azulejo un poco distinto
            for (int y = 0; y < px; y++)
                for (int x = 0; x < px; x++)
                {
                    float along = x / (float)px * span, z = y / (float)px * span;
                    float fx = along / tile % 1f, fz = z / tile % 1f;
                    bool g = fx < 0.025f || fz < 0.025f;
                    Color c;
                    if (z > 3.08f) c = mint;
                    else if (z > 2.55f) c = pink;
                    else c = ((int)((z + 0.1f) / 0.55f) + (int)(along / 0.8f)) % 3 != 1 ? pink : mint;
                    c *= shade[(int)(z / tile) % 48 * 48 + (int)(along / tile) % 48];
                    tex.SetPixel(x, y, g ? grout : c);
                }
            System.IO.File.WriteAllBytes(System.IO.Path.Combine(System.IO.Directory.GetCurrentDirectory(), path), tex.EncodeToPNG());
            Object.DestroyImmediate(tex);
            AssetDatabase.ImportAsset(path);
            var m = Mat("M_Azulejo_Dream", Color.white, 0.86f);
            m.SetTexture("_BaseColorMap", AssetDatabase.LoadAssetAtPath<Texture2D>(path));
            m.SetFloat("_UVBase", 5f);
            m.SetFloat("_TexWorldScale", 1f / span);
            UnityEngine.Rendering.HighDefinition.HDMaterial.ValidateMaterial(m);
            return m;
        }

        // Piso inundado de dream/: damero rosa y menta con charcos iridiscentes y las ondas del agua en el normal.
        static Material DreamFloor()
        {
            var nrm = DreamTex + "/floor_normal.png";
            var imp = (TextureImporter)AssetImporter.GetAtPath(nrm);
            if (imp.textureType != TextureImporterType.NormalMap) { imp.textureType = TextureImporterType.NormalMap; imp.SaveAndReimport(); }
            var m = Mat("M_Piso_Inundado", Color.white, 0.94f);
            m.SetTexture("_BaseColorMap", AssetDatabase.LoadAssetAtPath<Texture2D>(DreamTex + "/floor_surface_albedo.png"));
            m.SetTexture("_NormalMap", AssetDatabase.LoadAssetAtPath<Texture2D>(nrm));
            m.SetFloat("_NormalScale", 0.6f);
            m.SetFloat("_UVBase", 5f);
            m.SetFloat("_TexWorldScale", 1f / 3.6f);
            UnityEngine.Rendering.HighDefinition.HDMaterial.ValidateMaterial(m);
            return m;
        }

        // Radiador de columnas bajo la ventana (24 columnas cromadas, como en dream/)
        static void Radiator(Transform d)
        {
            var chrome = Mat("M_Cromo", new Color(0.92f, 0.93f, 0.95f), 0.88f, 1f);
            var r = Group("Radiador", d);
            for (int i = 0; i < 24; i++)
            {
                float x = -0.78f + i * 1.56f / 23f;
                Prim(PrimitiveType.Cylinder, $"Columna_{i:00}", r, new Vector3(x, 0.55f, 2.4f), new Vector3(0.032f, 0.375f, 0.032f), chrome, null, null, false);
            }
            foreach (var y in new[] { 0.22f, 0.88f })
                Prim(PrimitiveType.Cylinder, "Tubo", r, new Vector3(0f, y, 2.36f), new Vector3(0.048f, 0.82f, 0.048f), chrome, null, new Vector3(0f, 0f, 90f), false);
            // rebote del piso: el techo se ilumina con la luz que rebota en el suelo
            AddLight("Rebote_suelo", d, LightType.Rectangle, new Vector3(0f, 0.05f, 0f), new Vector3(-90f, 0f, 0f), new Color(1f, 0.9f, 0.88f), 5000f, 6f, 60f, new Vector2(5f, 4f), false);
        }

        // Polvo que flota en el rayo de sol que entra por la ventana.
        static void DustMotes(Transform d)
        {
            var go = new GameObject("Polvo_en_el_rayo");
            go.transform.SetParent(d, false);
            go.transform.position = new Vector3(0f, 1.5f, 0f);
            var ps = go.AddComponent<ParticleSystem>();
            var main = ps.main;
            main.loop = true; main.startLifetime = 16f; main.startSpeed = 0.015f; main.maxParticles = 900;
            main.startSize = new ParticleSystem.MinMaxCurve(0.003f, 0.008f);
            main.startColor = new Color(1f, 0.95f, 0.85f, 0.55f);
            main.simulationSpace = ParticleSystemSimulationSpace.World;
            main.prewarm = true;
            var em = ps.emission; em.rateOverTime = 60f;
            var sh = ps.shape; sh.shapeType = ParticleSystemShapeType.Box; sh.scale = new Vector3(5.6f, 2.8f, 4.6f);
            var noise = ps.noise; noise.enabled = true; noise.strength = 0.04f; noise.frequency = 0.25f; noise.scrollSpeed = 0.05f;
            var col = ps.colorOverLifetime; col.enabled = true;
            var grad = new Gradient();
            grad.SetKeys(new[] { new GradientColorKey(Color.white, 0f), new GradientColorKey(Color.white, 1f) },
                         new[] { new GradientAlphaKey(0f, 0f), new GradientAlphaKey(1f, 0.2f), new GradientAlphaKey(1f, 0.8f), new GradientAlphaKey(0f, 1f) });
            col.color = grad;
            // polvo iluminado de verdad (Lit transparente): a la sombra no se ve; en el rayo de sol brilla
            var mat = Mat("M_Polvo", new Color(1f, 0.97f, 0.92f, 0.55f), 0.2f, 0f, null, 0f, true);
            go.GetComponent<ParticleSystemRenderer>().sharedMaterial = mat;

            // el aire del cuarto con polvo: niebla volumetrica densa solo adentro. Donde entra el sol se ve el haz con
            // el polvo flotando; a la sombra el aire no brilla (casi sin luz ambiente en la niebla)
            var air = new GameObject("Polvo_en_el_aire");
            air.transform.SetParent(d, false);
            air.transform.localPosition = new Vector3(0f, 1.55f, 0f);
            var lv = air.AddComponent<UnityEngine.Rendering.HighDefinition.LocalVolumetricFog>();
            lv.parameters.size = new Vector3(5.9f, 3.1f, 4.9f);
            lv.parameters.meanFreePath = 3f;
            lv.parameters.albedo = new Color(1f, 0.95f, 0.9f);
            lv.parameters.blendingMode = UnityEngine.Rendering.HighDefinition.LocalVolumetricFogBlendingMode.Additive;
        }

        static Texture2D Checker(string name, Color a, Color b, int n)
        {
            EnsureDir(TexDir);
            string path = $"{TexDir}/{name}.png";
            int size = 256, cell = size / n;
            var t = new Texture2D(size, size, TextureFormat.RGBA32, false);
            for (int y = 0; y < size; y++)
                for (int x = 0; x < size; x++)
                    t.SetPixel(x, y, ((x / cell + y / cell) % 2 == 0) ? a : b);
            System.IO.File.WriteAllBytes(System.IO.Path.Combine(System.IO.Directory.GetCurrentDirectory(), path), t.EncodeToPNG());
            Object.DestroyImmediate(t);
            UnityEditor.AssetDatabase.ImportAsset(path);
            return UnityEditor.AssetDatabase.LoadAssetAtPath<Texture2D>(path);
        }
    }
}
