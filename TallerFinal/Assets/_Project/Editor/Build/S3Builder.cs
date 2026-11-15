using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering.HighDefinition;
using static Dream.EditorTools.Build.BuildKit;

namespace Dream.EditorTools.Build
{
    // 3 · Un vuelo corto entre nubes hasta la colina del arbol monumental, 12:00 (video 51 de dream/). El arbol es el
    // de dream/blender (tronco gris claro, nudoso, raices de contrafuerte y una copa oscura de pino) sobre una ladera
    // verde en diagonal bajo un cielo azul profundo. La copa se mece con el viento, a sacudidas. Abajo, durante el
    // vuelo, el campo tiene arboledas, rocas y pasto. El hueco negro del tronco es el paso a la noche.
    public static class S3Builder
    {
        public static void Build()
        {
            var scene = NewScene();
            // ladera: sube hacia -Z hasta una cresta detras del arbol; hacia +Z baja en diagonal (por donde se llega)
            float Hw(float x, float z)
            {
                float y = z >= -25f ? 10f - (z + 25f) * 0.4f : 10f - (-25f - z) * 0.12f;
                y = Mathf.Max(y, -24f + Mathf.Max(0f, z - 85f) * 0.02f);
                float side = Mathf.Max(0f, Mathf.Abs(x) - 38f);
                y -= Mathf.Min(side * side * 0.006f, 20f);
                y += 1.2f * Mathf.PerlinNoise(x * 0.02f + 5f, z * 0.02f) + 0.3f * Mathf.PerlinNoise(x * 0.09f, z * 0.09f);
                // un rellano suave al pie del arbol: las raices se apoyan en tierra pareja en vez de flotar ladera abajo
                float d = Mathf.Sqrt(x * x + z * z), w = Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(17f, 8f, d));
                y = Mathf.Lerp(y, -1.2f + 0.6f, w);
                // alrededor, colinas que siguen hasta el horizonte; al fondo, montes que cierran la vista entre la bruma
                float f = 0.6f * Mathf.PerlinNoise(x * 0.004f + 11f, z * 0.004f + 3f) + 0.3f * Mathf.PerlinNoise(x * 0.011f, z * 0.011f + 7f)
                          + 0.1f * Mathf.PerlinNoise(x * 0.03f + 2f, z * 0.03f);
                float hills = -16f + 44f * f;
                float rc = Mathf.Sqrt(x * x + (z - 30f) * (z - 30f));
                float blend = Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(110f, 230f, rc));
                float ring = Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(650f, 1150f, rc)) * (55f + 30f * Mathf.PerlinNoise(x * 0.006f, z * 0.006f));
                return Mathf.Lerp(y, hills, blend) + ring;
            }
            const float y0 = -40f, h = 170f, size = 2400f;
            var terrain = MakeTerrain("T_Colina", null, new Vector3(-size / 2f, y0, -size / 2f), new Vector3(size, h, size), 1025,
                (u, v) => (Hw(-size / 2f + u * size, -size / 2f + v * size) - y0) / h,
                ("Pasto", new Color(0.4f, 0.62f, 0.27f), 6f), ("Flores", new Color(0.52f, 0.7f, 0.3f), 4f));
            PaintLayer(terrain, 1, (u, v) => (Mathf.PerlinNoise(u * 60f + 3f, v * 60f) - 0.6f) * 4f);
            terrain.gameObject.AddComponent<TerrainSurfaces>().layerSurfaces = new[] { SurfaceType.Grass, SurfaceType.Grass };
            float G(float x, float z) => Ground(terrain, x, z);

            var a = Anchor(2, "La colina del árbol", new Vector3(0f, 78f, 185f), 180f, 12f, 12.6f, 5f);
            a.allowFlight = true; a.startFlying = true;
            a.arrivalHint = "Q  volar / posarse     ·     Espacio subir     ·     Ctrl bajar     ·     Shift más rápido";
            a.ambienceKind = AmbienceKind.VientoAlto; a.musicLowPass = 22000f; a.musicVolume = 0.9f; a.musicReverb = 0.12f; a.respawnBelowY = -40f;
            var cue = Cue(a.transform);

            // ---------- el arbol de dream/ ----------
            float gb = G(0f, 0f);
            var treeRoot = Group("Arbol_monumental");
            // en el modelo el tronco nace en (5.92, 1.9, 0); se hunde un poco para que las raices salgan de la tierra
            // mas grande que en dream/: en el video la figura es diminuta al pie del arbol
            const float scale = 1.7f;
            var tree = DreamScene.Place("Arbol_Monumental", treeRoot, Vector3.zero, 0f, 70f, 220f, true);
            PrefabUtility.UnpackPrefabInstance(tree.root, PrefabUnpackMode.Completely, InteractionMode.AutomatedAction);
            tree.root.transform.localScale *= scale;
            tree.root.transform.position = new Vector3(0f, gb - 1.1f, 0f) - scale * new Vector3(5.92f, 1.9f, 0f);
            // copa de pino oscura, casi negra contra el cielo, como en el video
            foreach (var r in tree.root.GetComponentsInChildren<MeshRenderer>())
                foreach (var m in r.sharedMaterials)
                    if (m && m.name.Contains("Canopy"))
                    {
                        var c = m.name.Contains("Shadow") ? new Color(0.16f, 0.24f, 0.17f) : m.name.Contains("Olive") ? new Color(0.27f, 0.36f, 0.23f) : new Color(0.21f, 0.31f, 0.21f);
                        m.SetColor("_BaseColor", c);
                        UnityEditor.EditorUtility.SetDirty(m);
                    }
            foreach (var junk in new[] { "sloped-grass-hill", "grass-blades", "distant-person", "runtime-canopy-shadow", "main-trunk", "buttress-root" })
                foreach (var t in tree.root.GetComponentsInChildren<Transform>(true).Where(t => t && t.name.Contains(junk)).ToArray())
                    if (t) Object.DestroyImmediate(t.gameObject);
            // la copa y las ramas se mecen juntas desde donde se abre el tronco; el tronco y las raices quedan quietos
            var sway = new GameObject("Copa_que_se_mece");
            sway.transform.SetParent(tree.root.transform, true);
            sway.transform.position = new Vector3(0f, gb + 13f * scale, 0f);
            foreach (var r in tree.root.GetComponentsInChildren<MeshRenderer>().ToArray())
            {
                string n = r.name;
                bool crown = n.Contains("primary") || n.Contains("outer") || n.Contains("crossing") || n.Contains("crown") || n.Contains("twig") || n.Contains("canopy");
                if (!crown) { r.gameObject.AddComponent<SurfaceTag>().type = SurfaceType.Wood; continue; }
                var col = r.GetComponent<Collider>(); if (col) Object.DestroyImmediate(col);
                r.transform.SetParent(sway.transform, true);
                Static(r.gameObject, false);
            }
            var leaf = sway.AddComponent<LeafSway>();
            leaf.maxDeg = 2.2f; leaf.gustDeg = 5f; leaf.pivotLocal = Vector3.zero;

            // el tronco nudoso (tools/taller_final/tronco_nudoso_blender.py): estrias retorcidas, contrafuertes que se
            // hunden en la tierra y un hueco tallado de verdad en la cara que mira a la ladera
            var trunkSrc = UnityEditor.AssetDatabase.LoadAssetAtPath<GameObject>(DreamScene.Dir + "/Arbol_Monumental/Tronco_Nudoso.fbx");
            var trunk = (GameObject)Object.Instantiate(trunkSrc, tree.root.transform);
            trunk.name = "Tronco_Nudoso";
            trunk.transform.localPosition = new Vector3(5.92f, 1.9f, 0f);
            trunk.transform.localRotation = trunkSrc.transform.localRotation;
            trunk.transform.localScale = trunkSrc.transform.localScale;
            var barkMat = UnityEditor.AssetDatabase.LoadAssetAtPath<Material>(MatDir + "/M_DREAM_TREE_Bark_Limestone.mat");
            foreach (var r in trunk.GetComponentsInChildren<MeshRenderer>())
            {
                r.sharedMaterials = new[] { barkMat, Palette.Black };
                r.gameObject.AddComponent<MeshCollider>();
                r.gameObject.AddComponent<SurfaceTag>().type = SurfaceType.Wood;
            }
            // la boca del hueco (en el modelo, a 2.3 del eje y 1.15 de alto); adentro, oscuridad total
            var mouth = trunk.transform.TransformPoint(new Vector3(0f, 1.15f, 2.15f));
            var inside = trunk.transform.TransformPoint(new Vector3(0f, 1.1f, 1.2f));
            var dark = Prim(PrimitiveType.Sphere, "Hueco_fondo", treeRoot, inside, new Vector3(1.25f, 2.0f, 1.6f) * scale, Palette.Black, null, null, false);
            Static(dark, false);
            float hz = mouth.z, gf = G(mouth.x, mouth.z + 1.5f);
            var holePoint = Point("Mira_hueco", treeRoot, mouth);
            // ---------- el campo de abajo: pasto que se mece, flores, arbustos, rocas y arboledas ----------
            var veg = Group("Campo");
            var field = veg.gameObject.AddComponent<WindField>();
            System.Func<System.Random, Vector2?> Near(float cx, float cz, float radius, float minR, float patch) => rng =>
            {
                float ang = (float)(rng.NextDouble() * Mathf.PI * 2f);
                float r = Mathf.Lerp(minR, radius, Mathf.Sqrt((float)rng.NextDouble()));
                float x = Mathf.Cos(ang) * r + cx, z = Mathf.Sin(ang) * r + cz;
                if (Mathf.Abs(x) < 3f && z > 0f && z < 40f) return null;                // la subida al hueco, despejada
                if (Mathf.PerlinNoise(x * 0.07f + 3f, z * 0.07f) < patch) return null;
                return new Vector2(x, z);
            };
            ScatterInstanced(field, "grass_medium_02", 3600, Near(0f, 20f, 60f, 4f, 0.3f), G, new Vector2(1.8f, 2.6f), 11, 1f);
            ScatterInstanced(field, "flower_gazania", 1200, Near(0f, 30f, 55f, 6f, 0.45f), G, new Vector2(1.8f, 2.6f), 12, 0.8f);
            ScatterInstanced(field, "dandelion_01", 500, Near(0f, 30f, 50f, 6f, 0.4f), G, new Vector2(1.8f, 2.4f), 13, 0.9f);
            ScatterInstanced(field, "shrub_02", 90, Near(0f, 60f, 140f, 30f, 0.3f), G, new Vector2(1f, 1.6f), 14, 0.25f, true);
            Scatter("boulder_01", veg, 14, Near(0f, 60f, 130f, 25f, 0.2f), G, new Vector2(1f, 2.4f), 15, 0.004f, SurfaceType.Stone, true);
            PolyModel("tree_stump_01", veg, new Vector3(-9f, G(-9f, 26f), 26f), 20f, SurfaceType.Wood);
            S2Builder.Forest(veg, G, new Vector2(0f, 40f), 45f, 1150f, 4500,
                             (x, z) => (Mathf.Abs(x) < 26f && z > -40f && z < 80f) || (Mathf.Abs(x) < 14f && z > 80f && z < 200f));

            // ---------- nubes y el recuerdo: un vuelo corto ----------
            var clouds = Group("Nubes");
            var dense = new Vector3(0f, 66f, 150f);        // justo delante de donde aparece, a la altura de los ojos
            CloudPuff("Nube_densa", clouds, dense + Vector3.up * 4f, new Vector3(48f, 22f, 44f), 2.5f, new Color(1f, 0.97f, 0.98f), true);
            var rng2 = new System.Random(3);
            for (int i = 0; i < 7; i++)
            {
                var pos = new Vector3((float)(rng2.NextDouble() - 0.5) * 180f, 55f + (float)rng2.NextDouble() * 35f, 60f + (float)rng2.NextDouble() * 160f);
                if (Vector3.Distance(pos, dense) < 45f || Mathf.Abs(pos.x) < 18f && pos.z > 165f) continue;
                CloudPuff($"Nube_{i:00}", clouds, pos, new Vector3(56f, 20f, 44f) * (0.7f + (float)rng2.NextDouble() * 0.6f), 6f, Color.white);
            }
            var memory = Memory(a.transform, dense + Vector3.up * 9.6f, "Desde arriba todo cabe en la palma de la mano.");

            // ---------- tras el recuerdo: baja a la ladera (angulo bajo, como el video) ----------
            const float landZ = 34f;
            float gl = G(0.4f, landZ);
            var crownPoint = Point("Mira_copa", treeRoot, new Vector3(0f, gb + 20f, 0f));
            var l1 = Shot(4f, "angulo amplio: baja del cielo hacia la colina");
            l1.from = CamPoint("Cam_Llegada_A", a.transform, new Vector3(30f, 80f, 120f), Vector3.zero);
            l1.to = CamPoint("Cam_Llegada_B", a.transform, new Vector3(24f, 76f, 112f), Vector3.zero);
            l1.lookAtActorHead = true; l1.focalLength = 85f; l1.focalLengthEnd = 50f;
            l1.actorVelocity = new Vector3(0f, -2.5f, -7f);
            var l2 = Shot(6f, "la colina y el arbol al mediodia, desde abajo");
            l2.actorTeleport = Point("Aterriza", a.transform, new Vector3(0.4f, gl + 0.05f, landZ), 180f);
            l2.from = CamPoint("Cam_Colina_A", a.transform, new Vector3(-16f, G(-16f, 52f) + 0.5f, 52f), Vector3.zero);
            l2.to = CamPoint("Cam_Colina_B", a.transform, new Vector3(-12f, G(-12f, 47f) + 0.45f, 47f), Vector3.zero);
            l2.lookAt = crownPoint; l2.focalLength = 24f;
            var l3 = Shot(3f, "camina hacia el arbol");
            l3.from = CamPoint("Cam_Colina_C", a.transform, new Vector3(1.6f, gl + 1.6f, landZ + 4f), Vector3.zero);
            l3.lookAt = crownPoint; l3.focalLength = 30f;
            l3.actorWalkTo = Point("Sube", a.transform, new Vector3(0.4f, G(0.4f, landZ - 4f), landZ - 4f), 180f); l3.actorSpeed = 1.1f;
            var landing = Gate("Hacia_la_colina", a.transform, new Vector3(0f, 72f, 95f), new Vector3(120f, 90f, 10f),
                               Sequence("Cine_Llegada_Colina", a.transform, l1, l2, l3), false, true);
            landing.revokesFlight = true;
            memory.autoGate = landing;
            landing.lockedHint = "Las nubes no te dejan pasar todavía. Busca arriba, en la más densa.";
            CheckpointAt(a.transform, new Vector3(0.4f, gl + 0.05f, landZ), 180f, new Vector3(6f, 4f, 6f));

            // ---------- el hueco: se asoma, tropieza y cae a la oscuridad (12:00 -> 20:00) ----------
            float gh = G(mouth.x, hz + 1.2f);
            var h1 = Shot(4.5f, "se acerca despacio al hueco");
            h1.from = CamPoint("Cam_Hueco_A", a.transform, new Vector3(-3.4f, gh + 1.7f, hz + 6.5f), Vector3.zero);
            h1.to = CamPoint("Cam_Hueco_B", a.transform, new Vector3(-2.8f, gh + 1.6f, hz + 5.2f), Vector3.zero);
            h1.lookAt = holePoint; h1.focalLength = 35f; h1.headLookAt = holePoint;
            h1.actorWalkTo = Point("Ante_el_hueco", a.transform, new Vector3(mouth.x, gh, hz + 1.2f), 180f); h1.actorSpeed = 0.75f;
            var h2 = Shot(2.4f, "asoma la cabeza");
            h2.from = CamPoint("Cam_Hueco_C", a.transform, new Vector3(-2.3f, gh + 1.55f, hz + 2.6f), Vector3.zero);
            h2.lookAtActorHead = true; h2.focalLength = 50f; h2.actorTrigger = "Peek"; h2.headLookAt = holePoint;
            var h3 = Shot(1.2f, "tropieza y cae dentro");
            h3.from = h2.from; h3.lookAt = holePoint; h3.focalLength = 50f;
            h3.actorVelocity = new Vector3(0f, 0f, -1.6f); h3.actorTrigger = "Stumble";
            h3.fadeColor = Color.black; h3.fadeOutSeconds = 0.9f;
            OnStart(h3, cue.Silence);
            var h4 = Shot(2.2f, "negro total y silencio");
            h4.hideActor = true; h4.setHour = 20f; h4.hourSeconds = 0f;
            Gate("El_hueco", a.transform, new Vector3(mouth.x, gh + 1.2f, hz + 1.1f), new Vector3(2.2f, 2.4f, 1.4f), Sequence("Cine_El_Hueco", a.transform, h1, h2, h3, h4));

            // ---------- llegada desde la pradera: el cielo ----------
            var w1 = Shot(5f, "llega al cielo; abajo, la colina y el arbol");
            w1.fadeColor = Color.white; w1.fadeInSeconds = 3f;
            w1.from = CamPoint("Cam_Cielo_A", a.transform, new Vector3(-6f, 74f, 181f), Vector3.zero);
            w1.to = CamPoint("Cam_Cielo_B", a.transform, new Vector3(-4f, 75.5f, 177f), Vector3.zero);
            w1.lookAtActorHead = true; w1.focalLength = 24f;
            w1.actorVelocity = new Vector3(0f, 0.6f, -1.5f);
            a.arrival = Sequence("Cine_Llegada_Cielo", a.transform, w1);

            GlobalVolume("Ambiente_Colina", a.transform, Profile("S3_Colina", p =>
            {
                Fog(p, 650f, 260f, new Color(0.86f, 0.9f, 1f));
                DreamSky(p, 14.1f);
            }), 1f);
            CottonSky(null, new Vector3(0f, 0f, 40f), 50, 250f, 1300f, 120f, 300f, 9f, 16f,
                      new[] { Color.white, new Color(1f, 0.9f, 0.95f), new Color(1f, 0.8f, 0.9f), new Color(0.9f, 0.86f, 1f) }, 62);
            Save(scene, "S3_Colina");
        }
    }
}
