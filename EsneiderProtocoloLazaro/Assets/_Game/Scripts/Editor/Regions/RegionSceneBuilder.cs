using System.Collections.Generic;
using System.IO;
using System.Linq;
using Esneider.AI;
using Esneider.Core;
using Esneider.Core.Data;
using Esneider.Core.Persistence;
using Esneider.Player;
using Esneider.World;
using Unity.AI.Navigation;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.AI;

namespace Esneider.EditorTools
{
    // 88.1: escena persistente BOOT + siete regiones aditivas generadas desde bunker_plan.json con entidades persistentes reales.
    public static class RegionSceneBuilder
    {
        const string ScenesDir = "Assets/_Game/Scenes/Regions";
        const string BootPath = "Assets/_Game/Scenes/BOOT.unity";

        [MenuItem("Esneider/Regions/Build BOOT + regions")]
        public static void BuildMenu() => Build();

        public static string Build()
        {
            var plan = LevelPlan.FromJson(File.ReadAllText(LevelPlan.DefaultAssetPath));
            var catalog = AssetDatabase.LoadAssetAtPath<GameDataCatalog>(SandboxBuilder.CatalogPath);
            if (catalog == null) return "Catálogo no encontrado";
            SandboxBuilder.ApplyCollisionMatrix();
            BlockoutBuilder.EnsureMaterials();
            Directory.CreateDirectory(ScenesDir);
            var summary = new List<string>(); var corrections = new List<string>();
            var buildScenes = new List<EditorBuildSettingsScene> { new EditorBuildSettingsScene(BootPath, true) };

            foreach (var region in RegionCatalog.Chain)
            {
                var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
                var root = new GameObject(region);
                var stats = new Dictionary<string, int>();
                var floors = plan.floors.Where(f => f.region == region).ToList();
                var connectors = plan.connectors.Where(c => c.region == region).ToList();
                foreach (var f in floors) BlockoutBuilder.BuildFloor(plan, f, root.transform, stats);
                foreach (var c in connectors) BlockoutBuilder.BuildConnector(plan, c, root.transform, stats);
                var spaces = floors.Select(f => f.id).Concat(connectors.Select(c => c.id)).ToList();

                int ents = BuildEntities(plan, catalog, region, spaces, root.transform);
                var hero = HeroDressing.Apply(plan, region, spaces, root.transform.Find("Entities"));
                var furniture = FurnitureBuilder.Apply(plan, region, spaces, root.transform.Find("Entities"), corrections);
                summary.Add($"{region} mobiliario: {furniture.Count}");
                BuildLighting(plan, region, floors, connectors, root.transform);
                BuildNarrative(plan, region, root.transform.Find("Entities"));
                BuildVolume(plan, region, floors, connectors, root.transform);
                var vol = root.transform.Find("Volume_" + region);
                if (vol != null) { var ra = vol.gameObject.AddComponent<Audio.RegionAudio>(); ra.regionId = region; ra.ambienceBank = "SND-AMBI-" + region.Replace("REG-", ""); ra.reverb = region.StartsWith("REG-C") ? AudioReverbPreset.Hangar : region == "REG-S3" ? AudioReverbPreset.Room : region == "REG-S4" ? AudioReverbPreset.Auditorium : AudioReverbPreset.StoneCorridor; }
                BuildExteriorDressing(plan, region, root.transform, root.transform.Find("Entities"));
                summary.Add("hero: " + string.Join(",", hero));
                BakeNavMesh(root, region);

                var path = RegionCatalog.ScenePath(region);
                EditorSceneManager.SaveScene(scene, path);
                buildScenes.Add(new EditorBuildSettingsScene(path, true));
                summary.Add($"{region}: {stats.Values.Sum()} cajas, {ents} entidades");
            }

            BuildBoot(plan, catalog);
            var existing = EditorBuildSettings.scenes.Where(s => !buildScenes.Any(b => b.path == s.path)).ToList();
            EditorBuildSettings.scenes = buildScenes.Concat(existing).ToArray();
            // 76.1: correcciones de composición registradas (no se suman listados: el plano manda)
            var rep = Path.GetFullPath(Path.Combine(Application.dataPath, "../../docs/produccion/evidencia/EX-06_furniture_report.md"));
            Directory.CreateDirectory(Path.GetDirectoryName(rep));
            File.WriteAllText(rep, $"# Mobiliario 76.2 · validación de reservas · {System.DateTime.Now:yyyy-MM-dd HH:mm}\n\nInstancias del plano: {plan.furniture.Count}. Correcciones: {corrections.Count}.\n\n" + (corrections.Count == 0 ? "Sin correcciones.\n" : "- " + string.Join("\n- ", corrections) + "\n"));
            return string.Join(" | ", summary) + $" | correcciones mobiliario: {corrections.Count}";
        }

        static int BuildEntities(LevelPlan plan, GameDataCatalog catalog, string region, List<string> spaces, Transform root)
        {
            int n = 0;
            var ents = new GameObject("Entities").transform; ents.SetParent(root);
            var vigDef = catalog.enemies.Find(e => e.kind == EnemyKind.Vigia); var kDef = catalog.enemies.Find(e => e.kind == EnemyKind.Custodio);

            foreach (var p in plan.pickups.Where(x => spaces.Contains(x.space)))
            {
                plan.TryToWorld(p.space, p.x, p.z, out var w);
                var kind = p.kind switch { "Flashlight" => PickupKind.Flashlight, "Crowbar" => PickupKind.Crowbar, "Pistol" => PickupKind.Pistol, "Shotgun" => PickupKind.Shotgun, "PistolAmmo" => PickupKind.PistolAmmo, "ShotgunAmmo" => PickupKind.ShotgunAmmo, "Syringe" => PickupKind.Syringe, _ => PickupKind.Ration };
                var go = GameObject.CreatePrimitive(PrimitiveType.Sphere); go.name = "Pickup_" + p.id; go.layer = GameLayers.Interactable; go.transform.SetParent(ents); go.transform.position = w + Vector3.up * p.height; go.transform.localScale = Vector3.one * 0.25f;
                go.GetComponent<MeshRenderer>().sharedMaterial = BlockoutMat(kind == PickupKind.Syringe || kind == PickupKind.Ration ? "Blockout_Pickup_Heal" : "Blockout_Pickup", kind == PickupKind.Syringe || kind == PickupKind.Ration ? Color.green : Color.yellow);
                var pk = go.AddComponent<Pickup>(); pk.kind = kind; pk.amount = p.amount; pk.stableId = p.id; pk.guid = LevelPlan.StableGuid(p.id).ToString();
                // soporte placeholder bajo el pickup (68.8: colocar soporte OBJ real debajo)
                var sup = GameObject.CreatePrimitive(PrimitiveType.Cube); sup.name = "Support_" + p.id; sup.layer = GameLayers.WorldStatic; sup.transform.SetParent(ents); sup.transform.position = w + Vector3.up * (p.height - 0.15f) / 2f; sup.transform.localScale = new Vector3(0.5f, Mathf.Max(0.1f, p.height - 0.15f), 0.5f); sup.isStatic = true;
                SandboxFactory.Persist(go, p.id, region, EntityKind.Pickup); n++;
            }
            foreach (var d in plan.documents.Where(x => spaces.Contains(x.space)))
            {
                plan.TryToWorld(d.space, d.x, d.z, out var w);
                var go = GameObject.CreatePrimitive(PrimitiveType.Cube); go.name = "Doc_" + d.id; go.layer = GameLayers.Interactable; go.transform.SetParent(ents); go.transform.position = w + Vector3.up * 0.95f; go.transform.localScale = new Vector3(0.21f, 0.01f, 0.3f);
                go.GetComponent<MeshRenderer>().sharedMaterial = BlockoutMat("Blockout_Doc", Color.cyan);
                var pk = go.AddComponent<Pickup>(); pk.kind = PickupKind.Document; pk.amount = 1; pk.stableId = d.id; pk.documentId = d.id; pk.guid = LevelPlan.StableGuid(d.id).ToString();
                var sup = GameObject.CreatePrimitive(PrimitiveType.Cube); sup.name = "Support_" + d.id; sup.layer = GameLayers.WorldStatic; sup.transform.SetParent(ents); sup.transform.position = w + Vector3.up * 0.45f; sup.transform.localScale = new Vector3(0.6f, 0.9f, 0.6f); sup.isStatic = true;
                SandboxFactory.Persist(go, d.id, region, EntityKind.Pickup); n++;
            }
            foreach (var s in plan.spawns.Where(x => spaces.Contains(x.space)))
            {
                plan.TryToWorld(s.space, s.x, s.z, out var w);
                bool boss = s.kind == "Boss";
                var def = s.kind == "Vigia" ? vigDef : kDef;
                string heroId = boss ? "BOT-03_Archivista" : s.kind == "Vigia" ? "BOT-01_Vigia" : "BOT-02_Custodio";
                var heroPrefab = AssetDatabase.LoadAssetAtPath<GameObject>($"Assets/_Game/Prefabs/Enemies/{heroId}.prefab");
                var heroClips = heroPrefab != null ? AssetDatabase.LoadAllAssetsAtPath($"Assets/_Game/Art/Models/{heroId}.fbx").OfType<AnimationClip>().Where(c => !c.name.StartsWith("__")).ToArray() : null;
                if (boss)
                {
                    // 15/61/79: EL ARCHIVISTA con BossBrain; arena = S4-R03 (24×28, cuatro pilares); D27 se cierra al despertar
                    var bgo = SandboxFactory.BuildBoss(catalog.boss, s.id, w, heroPrefab, heroClips);
                    bgo.transform.SetParent(ents); bgo.transform.rotation = Quaternion.Euler(0, s.yaw, 0);
                    var arena = plan.Room("S4-R03"); var af = plan.Floor(arena.floor);
                    var bb = bgo.GetComponent<BossBrain>(); bb.arenaCenter = af.origin.ToVector3() + new Vector3(arena.x + arena.w / 2f, af.height / 2f, arena.z + arena.d / 2f); bb.arenaSize = new Vector3(arena.w, af.height, arena.d);
                    SandboxFactory.Persist(bgo, s.id, region, EntityKind.Boss); n++;
                    continue;
                }
                var go = SandboxFactory.BuildEnemy(def, s.id, w, s.kind == "Vigia" ? new Color(0.85f, 0.85f, 0.8f) : new Color(0.6f, 0.4f, 0.35f), s.kind == "Vigia" ? 1.25f : 2.15f, heroPrefab, heroClips);
                go.transform.SetParent(ents); go.transform.rotation = Quaternion.Euler(0, s.yaw, 0);
                var brain = go.GetComponent<EnemyBrain>(); brain.tutorialTelegraph = s.id == "V01";
                brain.startActive = region != "REG-S1" && region != "REG-C1"; // 104.3: sin ataques antes de D06; EVT-C1 activa S1/C1
                // 77.1: ruta del plano (ida/vuelta o cerrada, espera inicial); sin ruta → spawn + punto a 4 m
                var wps = new GameObject(s.id + "_Waypoints"); wps.transform.SetParent(ents);
                var pat = plan.PatrolOf(s.id);
                if (pat != null && pat.points != null && pat.points.Count > 0)
                {
                    for (int i = 0; i < pat.points.Count; i++) { plan.TryToWorld(pat.space, pat.points[i].x, pat.points[i].z, out var pw); var wp = new GameObject("WP" + i); wp.transform.SetParent(wps.transform); wp.transform.position = pw; brain.waypoints.Add(wp.transform); }
                    brain.patrolLoop = pat.mode == "loop"; brain.patrolDelay = pat.delay; wps.name = pat.id + "_" + s.id;
                }
                else
                {
                    var w0 = new GameObject("WP0"); w0.transform.SetParent(wps.transform); w0.transform.position = w; brain.waypoints.Add(w0.transform);
                    var second = w + Quaternion.Euler(0, s.yaw, 0) * Vector3.forward * 4f;
                    var w1 = new GameObject("WP1"); w1.transform.SetParent(wps.transform); w1.transform.position = second; brain.waypoints.Add(w1.transform);
                }
                if (s.id == "V15" || s.id == "V23") brain.startActive = false; // EVT-16 protección de lectura; EVT-18 despertar anunciado
                SandboxFactory.Persist(go, s.id, region, boss ? EntityKind.Boss : EntityKind.Enemy); n++;
            }
            foreach (var d in plan.doors.Where(x => spaces.Contains(x.floor)))
            {
                var f = plan.Floor(d.floor); var w = f.origin.ToVector3() + new Vector3(d.x, 0, d.z);
                bool alongX = d.edge == "N" || d.edge == "S";
                // DynamicProp: bloquea visión/proyectiles pero no se hornea en el NavMesh (el obstáculo carve lo bloquea en runtime)
                var go = GameObject.CreatePrimitive(PrimitiveType.Cube); go.name = "Door_" + d.id; go.layer = GameLayers.DynamicProp; go.transform.SetParent(ents);
                go.transform.position = w + Vector3.up * d.height / 2f;
                go.transform.localScale = alongX ? new Vector3(d.width, d.height, 0.2f) : new Vector3(0.2f, d.height, d.width);
                go.GetComponent<MeshRenderer>().sharedMaterial = BlockoutMat("Blockout_Door", new Color(0.45f, 0.3f, 0.2f));
                var door = go.AddComponent<Door>(); door.doorId = d.id; door.leaf = go.transform; door.openOffset = (alongX ? Vector3.right : Vector3.forward) * d.width; door.openSeconds = d.width > 2 ? 2.0f : 1.2f;
                door.requiresPermission = RegionCatalog.FrontierDoors.ContainsKey(d.id) || d.id.StartsWith("D28") || d.id.StartsWith("D29");
                door.isOpen = !door.requiresPermission && d.state.StartsWith("Abierta") && !d.id.StartsWith("D2");
                var obs = go.AddComponent<NavMeshObstacle>(); obs.carving = true; obs.carveOnlyStationary = false;
                SandboxFactory.Persist(go, "DOOR-" + d.id, region, EntityKind.Door); n++;
            }
            foreach (var m in plan.mechanisms.Where(x => spaces.Contains(x.space)))
            {
                plan.TryToWorld(m.space, m.x, m.z, out var w);
                var go = GameObject.CreatePrimitive(PrimitiveType.Cube); go.name = "Mech_" + m.id; go.layer = GameLayers.Interactable; go.transform.SetParent(ents); go.transform.position = w + Vector3.up * 1.1f; go.transform.localScale = new Vector3(0.4f, 0.5f, 0.2f);
                go.GetComponent<MeshRenderer>().sharedMaterial = BlockoutMat("Blockout_Mech", Color.blue);
                var mech = go.AddComponent<Mechanism>(); mech.mechanismId = m.id;
                mech.grantsFlag = m.id switch { "MECH-LEVER-S1" => ObjectiveService.PermisoServicio, "MECH-PANEL-A" => ObjectiveService.PermisoA, "MECH-PANEL-B" => ObjectiveService.PermisoB, "MECH-PANEL-EXIT" => ObjectiveService.PanelExit, _ => "" };
                mech.preloadRegion = m.id switch { "MECH-LEVER-S1" => "REG-C1", "MECH-PANEL-A" => "REG-C2", "MECH-PANEL-B" => "REG-C3", _ => "" };
                if (m.id == "MECH-CABINET-CP06") { Object.DestroyImmediate(mech); go.name = "Cabinet_CP06_Placeholder"; }
                n++;
            }
            foreach (var cp in plan.checkpoints.Where(x => spaces.Contains(x.space)))
            {
                plan.TryToWorld(cp.space, cp.x, cp.z, out var w);
                var go = new GameObject("CP_" + cp.id); go.transform.SetParent(ents); go.transform.position = w + Vector3.up;
                var bc = go.AddComponent<BoxCollider>(); bc.size = new Vector3(2.5f, 2f, 2.5f);
                var t = go.AddComponent<CheckpointTrigger>(); t.checkpointId = cp.id; t.regionId = region; t.isShelter = cp.id == "CP-06";
                if (t.isShelter) { t.guaranteeHp = 90; t.guaranteePistolTotal = 50; t.guaranteeShotgunTotal = 24; }
                n++;
            }
            foreach (var p in plan.pillars.Where(x => spaces.Contains(x.space))) { /* ya construidos por BlockoutBuilder */ }
            if (plan.exterior != null && spaces.Contains(plan.exterior.space))
            {
                plan.TryToWorld(plan.exterior.space, plan.exterior.victoryX, plan.exterior.victoryZ, out var w);
                var go = new GameObject("VictoryTrigger"); go.transform.SetParent(ents); go.transform.position = w + Vector3.up;
                var bc = go.AddComponent<BoxCollider>(); bc.size = new Vector3(4f, 3f, 6f); go.AddComponent<VictoryTrigger>(); n++;
            }
            return n;
        }

        // ---------- ENV-EXIT: vestido del mirador de escape (97.1/97.2/97.4, 61.4) ----------
        // La geometría estructural (fachada, parapeto, ladera) la pone BlockoutBuilder; aquí van placa, siluetas,
        // sol de amanecer y el control de ambiente que ejecuta END-01/END-02.
        static void BuildExteriorDressing(LevelPlan plan, string region, Transform root, Transform ents)
        {
            if (region != "REG-S4" || plan.exterior == null) return;
            var f = plan.Floor(plan.exterior.space); if (f == null) return;
            var o = f.origin.ToVector3();
            var ex = plan.exterior;
            var env = new GameObject("ENV-EXIT_Dressing").transform; env.SetParent(root);

            GameObject Box(string name, Vector3 center, Vector3 size, Material m, float yaw = 0f, int layer = -1)
            {
                var g = GameObject.CreatePrimitive(PrimitiveType.Cube); g.name = name; g.transform.SetParent(env);
                g.transform.position = center; g.transform.localScale = size; g.transform.rotation = Quaternion.Euler(0, yaw, 0);
                g.GetComponent<MeshRenderer>().sharedMaterial = m; g.layer = layer < 0 ? GameLayers.WorldStatic : layer; g.isStatic = true;
                return g;
            }

            var matPlate = BlockoutMat("Exit_Plate", new Color(0.62f, 0.60f, 0.55f));
            var matTower = BlockoutMat("Exit_TowerSilhouette", new Color(0.28f, 0.30f, 0.33f));
            var matPost = BlockoutMat("Exit_Post", new Color(0.33f, 0.34f, 0.32f));

            // 97.2 END-04: placa junto al parapeto. Se descubre mirando; la victoria no exige leerla.
            float pz = BlockoutBuilder.ExtWalkMaxZ;                       // parapeto norte
            var plateCenter = o + new Vector3(76f, 1.05f, pz + 0.05f);
            Box("Exit_PlatePost_L", plateCenter + new Vector3(-0.62f, -0.35f, 0), new Vector3(0.07f, 0.9f, 0.07f), matPost);
            Box("Exit_PlatePost_R", plateCenter + new Vector3(0.62f, -0.35f, 0), new Vector3(0.07f, 0.9f, 0.07f), matPost);
            var plate = Box("Exit_Plate", plateCenter, new Vector3(1.45f, 0.42f, 0.04f), matPlate);
            var txt = new GameObject("Exit_PlateText"); txt.transform.SetParent(plate.transform, false);
            txt.transform.localPosition = new Vector3(0, 0, -0.55f);
            txt.transform.localRotation = Quaternion.Euler(0, 180f, 0);
            txt.transform.localScale = new Vector3(1f / 1.45f, 1f / 0.42f, 1f) * 0.06f;
            var tm = txt.AddComponent<TextMesh>();
            tm.text = "NÉMESIS\nRESERVA BIOLÓGICA 04\nCONTINUIDAD OPERATIVA";
            tm.characterSize = 0.1f; tm.fontSize = 72; tm.anchor = TextAnchor.MiddleCenter; tm.alignment = TextAlignment.Center;
            tm.color = new Color(0.12f, 0.12f, 0.11f);

            // 97.1: siluetas de torre y estructura lejana = composición, no ciudad explorable. Fuera del parapeto.
            Box("Tower_A", o + new Vector3(ex.x + ex.w + 34f, 6f, ex.z - 10f), new Vector3(7f, 26f, 7f), matTower, 12f);
            Box("Tower_A_cap", o + new Vector3(ex.x + ex.w + 34f, 19.4f, ex.z - 10f), new Vector3(9f, 1.2f, 9f), matTower, 12f);
            Box("Tower_B", o + new Vector3(ex.x + ex.w + 52f, 2.5f, ex.z + ex.d + 14f), new Vector3(10f, 19f, 8f), matTower, -8f);
            Box("Ridge_Far", o + new Vector3(ex.x + ex.w + 44f, -3.5f, ex.z + ex.d / 2f), new Vector3(40f, 7f, 90f), matTower, 0f);

            // 87.1: la salida final debe ser físicamente visible tras el jefe → señal EVACUACIÓN sobre la compuerta
            var sign = Box("Sign_EVACUACION", o + new Vector3(f.w + 0.55f, 5.4f, 12f), new Vector3(0.12f, 0.5f, 2.6f), matPlate);
            var stm = new GameObject("Sign_Text"); stm.transform.SetParent(sign.transform, false);
            stm.transform.localPosition = new Vector3(-0.7f, 0, 0); stm.transform.localRotation = Quaternion.Euler(0, -90f, 0);
            stm.transform.localScale = new Vector3(1f / 0.12f, 1f / 0.5f, 1f) * 0.02f;
            var stt = stm.AddComponent<TextMesh>();
            stt.text = "EVACUACIÓN →"; stt.characterSize = 0.1f; stt.fontSize = 64; stt.anchor = TextAnchor.MiddleCenter; stt.color = new Color(0.9f, 0.75f, 0.2f);

            // Sol de amanecer propio del exterior: arranca apagado y sube al salir (ExteriorAmbience lo controla).
            var sunGo = new GameObject("Sun_Exterior"); sunGo.transform.SetParent(env);
            sunGo.transform.rotation = Quaternion.Euler(14f, 205f, 0f);      // bajo y rasante: amanecer, no mediodía
            var sun = sunGo.AddComponent<Light>();
            sun.type = LightType.Directional; sun.color = new Color(0.78f, 0.80f, 0.84f); sun.intensity = 0f;
            sun.shadows = LightShadows.None; sun.lightmapBakeType = LightmapBakeType.Realtime;

            // Control de ambiente (END-01/02): volumen del patio transitable.
            var ctrl = new GameObject("ExteriorAmbience"); ctrl.transform.SetParent(env);
            ctrl.transform.position = o + new Vector3((f.w + BlockoutBuilder.ExtWalkMaxX) / 2f, 1.5f, (BlockoutBuilder.ExtWalkMinZ + BlockoutBuilder.ExtWalkMaxZ) / 2f);
            var amb = ctrl.AddComponent<ExteriorAmbience>();
            amb.area = new Bounds(ctrl.transform.position, new Vector3(BlockoutBuilder.ExtWalkMaxX - f.w + 2f, 8f, BlockoutBuilder.ExtWalkMaxZ - BlockoutBuilder.ExtWalkMinZ + 2f));
            amb.sunLight = sun;
            amb.interiorReverb = root.GetComponentInChildren<AudioReverbZone>();
        }

        // 42.3/16: luminaria técnica por sala (fría, tenue), emergencia ámbar junto a puertas, luz lateral escasa en corredores. Sin sombras dinámicas (71.3).
        static void BuildLighting(LevelPlan plan, string region, List<PlanFloor> floors, List<PlanConnector> connectors, Transform root)
        {
            var lights = new GameObject("Lighting").transform; lights.SetParent(root);
            Light L(string name, Vector3 pos, Color c, float intensity, float range)
            {
                var go = new GameObject(name); go.transform.SetParent(lights); go.transform.position = pos;
                var l = go.AddComponent<Light>(); l.type = LightType.Point; l.color = c; l.intensity = intensity; l.range = range; l.shadows = LightShadows.None; l.lightmapBakeType = LightmapBakeType.Mixed;
                return l;
            }
            var cool = new Color(0.62f, 0.72f, 0.8f); var amber = new Color(1f, 0.62f, 0.25f); var clinic = new Color(0.7f, 0.82f, 0.9f);
            foreach (var f in floors)
            {
                foreach (var r in plan.rooms.Where(x => x.floor == f.id))
                {
                    var c = f.origin.ToVector3() + new Vector3(r.x + r.w / 2f, f.height - 0.3f, r.z + r.d / 2f);
                    float area = r.w * r.d; int n = area > 300 ? 3 : area > 150 ? 2 : 1;
                    for (int i = 0; i < n; i++) L("Lum_" + r.id + "_" + i, c + new Vector3((i - (n - 1) / 2f) * r.w / (n + 0.5f), 0, 0), f.sector == "S3" ? clinic : cool, f.sector == "S4" ? 1.3f : 1.0f, Mathf.Max(6f, Mathf.Max(r.w, r.d) * 0.7f));
                }
                foreach (var d in plan.doors.Where(x => x.floor == f.id && x.width >= 2.8f))
                    L("Emerg_" + d.id, f.origin.ToVector3() + new Vector3(d.x, d.height + 0.3f, d.z), amber, 0.6f, 4f);
                foreach (var c in plan.circulation.Where(x => x.floor == f.id && x.w * x.d > 40))
                    L("Circ_" + c.id, f.origin.ToVector3() + new Vector3(c.x + c.w / 2f, f.height - 0.3f, c.z + c.d / 2f), cool, 0.5f, Mathf.Max(5f, Mathf.Max(c.w, c.d) * 0.5f));
            }
            foreach (var c in connectors)
                for (int i = 1; i < c.points.Count; i++)
                {
                    var a = c.points[i - 1]; var b = c.points[i]; var mid = c.origin.ToVector3() + new Vector3((a.x + b.x) / 2f, c.height - 0.5f, (a.z + b.z) / 2f);
                    L("Side_" + c.id + "_" + i, mid + new Vector3(0, 0, c.width * 0.4f), cool, 0.45f, 9f);
                }
        }

        // EVT-01 apertura en S1 y EVT-C1 altavoz OBJ-065 en C-01 (fuera del sótano, filtrado por la puerta 5.2).
        static void BuildNarrative(LevelPlan plan, string region, Transform ents)
        {
            if (region == "REG-S1")
            {
                var m001 = plan.furniture.Find(f => f.id == "M001");
                var cryo = ents.Find("Furniture/M001_OBJ-001");
                var go = new GameObject("EVT-01_Opening"); go.transform.SetParent(ents);
                var op = go.AddComponent<OpeningSequence>();
                op.cryoLidAnimatorRoot = cryo; op.cryoOpenClip = AssetDatabase.LoadAllAssetsAtPath("Assets/_Game/Art/Models/OBJ-001_Criocamara.fbx").OfType<AnimationClip>().FirstOrDefault(c => c.name == "Cryo_Open");
                op.lyingPosition = cryo != null ? cryo.position + Vector3.up * 0.75f : plan.Floor("P01").origin.ToVector3() + new Vector3(m001 != null ? m001.x : 7f, 0.75f, m001 != null ? m001.z : 7f); op.lyingYaw = 90f;
                RoomEvt(plan, ents, "EVT-03", "S1-R05", e => { e.sound = "SND-PIPE-Hit"; e.message = "Cámaras vacías. Mantenimiento reciente: alguien sigue aquí."; });
            }
            if (region == "REG-C1")
            {
                var c = plan.Connector("C-01"); var w = c.origin.ToVector3() + new Vector3(4f, c.height - 0.8f, -c.width / 2f + 0.3f);
                var sp = GameObject.CreatePrimitive(PrimitiveType.Cube); sp.name = "OBJ-065_Altavoz"; sp.layer = GameLayers.WorldStatic; sp.transform.SetParent(ents); sp.transform.position = w; sp.transform.localScale = new Vector3(0.4f, 0.3f, 0.25f);
                sp.AddComponent<AnnouncementSpeaker>().doorId = "D06";
            }
            if (region == "REG-S2")
            {
                RoomEvt(plan, ents, "EVT-06", "S2-R01", e => { e.requiresAliveUnit = "K01"; e.sound = "SND-KUS-Step-A"; e.soundOffset = SpawnOffset(plan, "K01", "S2-R01"); e.message = "Unidad de contención grande. Rodéala o golpea seis veces; el rayo se anuncia."; });
                RoomEvt(plan, ents, "EVT-07", "S2-R06", e => { e.delay = 1.5f; e.sound = "SND-RELAY"; e.soundOffset = FurnitureOffset(plan, "M024", "S2-R06"); e.message = "El brazo desmontado se reajusta… y vuelve al reposo."; });
                RoomEvt(plan, ents, "EVT-11", "S2-R05", e => { e.once = false; e.cooldown = 45f; e.message = "Rostros sin boca y números de serie: no son cabezas humanas."; });
            }
            if (region == "REG-C2")
            {
                var c = plan.Connector("C-02");
                Evt(plan, ents, "EVT-C2", "C-02", 21.5f, 4f, 5f, 8f, c.height, e => { e.deferWhileCombat = true; e.objectiveId = "O06"; e.setFlag = "HUMANS_SEEN"; e.message = "Tras el vidrio, una mano humana se mueve. Siguen vivos."; e.messageSeconds = 5f; });
            }
            if (region == "REG-S3")
            {
                RoomEvt(plan, ents, "EVT-12", "S3-R01", e => { e.message = "Admisión. Reclasificación de sujetos."; });
                RoomEvt(plan, ents, "EVT-13", "S3-R02A", e => { e.deferWhileCombat = true; e.delay = 1f; e.message = "Respiración irregular tras los barrotes. Una mano se mueve apenas."; e.messageSeconds = 6f; });
                RoomEvt(plan, ents, "EVT-14", "S3-R02B", e => { e.sound = "SND-RELAY"; e.soundOffset = FurnitureOffset(plan, "M049", "S3-R02B"); e.message = "La bomba inicia su ciclo: mantenimiento reciente."; });
                RoomEvt(plan, ents, "EVT-15", "S3-R03", e => { e.once = false; e.cooldown = 20f; e.sound = "SND-PIPE-Hit"; e.soundOffset = FurnitureOffset(plan, "M056", "S3-R03"); e.soundVolume = 0.4f; });
                RoomEvt(plan, ents, "EVT-16", "S3-R04", e => { e.watchDocument = "DOC-09"; e.setFlag = "V15_RELEASED"; e.activateUnits.Add("V15"); });
                RoomEvt(plan, ents, "EVT-16-EXIT", "S3-R04", e => { e.onExit = true; e.setFlag = "V15_RELEASED"; e.activateUnits.Add("V15"); });
            }
            if (region == "REG-C3")
            {
                var c = plan.Connector("C-03");
                Evt(plan, ents, "EVT-C3", "C-03", 22f, 7f, 18f, 6f, c.height, e => { e.forbiddenFlag = ObjectiveService.BossDefeated; e.sound = "SND-BOSS-Step-A"; e.soundOffset = new Vector3(14f, 0, 0); e.soundVolume = 0.6f; e.message = "Un impacto lejano, pesado, hace vibrar el corredor."; });
            }
            if (region == "REG-S4")
            {
                RoomEvt(plan, ents, "EVT-18", "S4-R05", e => { e.onExit = true; e.requiredDocument = "DOC-11"; e.requiresAliveUnit = "V23"; e.sound = "SND-VIG-Step-A"; e.soundOffset = SpawnOffset(plan, "V23", "S4-R05"); e.activateUnits.Add("V23"); e.message = "Un servo despierta en el control."; });
                RoomEvt(plan, ents, "EVT-20", "S4-R01", e => { e.sound = "SND-RELAY"; e.message = "Un relé rompe el silencio."; });
            }
        }

        static RoomEvent Evt(LevelPlan plan, Transform ents, string id, string space, float x, float z, float w, float d, float h, System.Action<RoomEvent> cfg)
        {
            plan.TryToWorld(space, x + w / 2f, z + d / 2f, out var c);
            var go = new GameObject(id); go.transform.SetParent(ents); go.transform.position = c + Vector3.up * h / 2f;
            var bc = go.AddComponent<BoxCollider>(); bc.size = new Vector3(w, h, d);
            var e = go.AddComponent<RoomEvent>(); e.eventId = id; cfg(e); return e;
        }
        static RoomEvent RoomEvt(LevelPlan plan, Transform ents, string id, string roomId, System.Action<RoomEvent> cfg)
        { var r = plan.Room(roomId); return Evt(plan, ents, id, r.floor, r.x, r.z, r.w, r.d, plan.Floor(r.floor).height, cfg); }
        static Vector3 SpawnOffset(LevelPlan plan, string unit, string roomId) { var s = plan.spawns.Find(x => x.id == unit); var r = plan.Room(roomId); return s == null ? Vector3.zero : new Vector3(s.x - (r.x + r.w / 2f), 1f, s.z - (r.z + r.d / 2f)); }
        static Vector3 FurnitureOffset(LevelPlan plan, string id, string roomId) { var f = plan.furniture.Find(x => x.id == id); var r = plan.Room(roomId); return f == null ? Vector3.zero : new Vector3(f.x - (r.x + r.w / 2f), 1f, f.z - (r.z + r.d / 2f)); }

        static void BuildVolume(LevelPlan plan, string region, List<PlanFloor> floors, List<PlanConnector> connectors, Transform root)
        {
            var vol = new GameObject("Volume_" + region); vol.transform.SetParent(root);
            var bounds = new Bounds();
            bool first = true;
            foreach (var f in floors)
            {
                var b = new Bounds(f.origin.ToVector3() + new Vector3(f.w / 2f, f.height / 2f, f.d / 2f), new Vector3(f.w + 1f, f.height + 1f, f.d + 1f));
                if (plan.exterior != null && plan.exterior.space == f.id) b.Encapsulate(f.origin.ToVector3() + new Vector3(plan.exterior.x + plan.exterior.w, 0, plan.exterior.z + plan.exterior.d));
                if (first) { bounds = b; first = false; } else bounds.Encapsulate(b);
            }
            foreach (var c in connectors)
            {
                var o = c.origin.ToVector3();
                foreach (var p in c.points) { var b = new Bounds(o + new Vector3(p.x, c.height / 2f, p.z), new Vector3(c.width + 1f, c.height + 1f, c.width + 1f)); if (first) { bounds = b; first = false; } else bounds.Encapsulate(b); }
            }
            vol.transform.position = bounds.center;
            var bc = vol.AddComponent<BoxCollider>(); bc.size = bounds.size;
            var rv = vol.AddComponent<RegionVolume>(); rv.regionId = region;
        }

        static void BakeNavMesh(GameObject root, string region)
        {
            var surf = root.AddComponent<NavMeshSurface>();
            surf.collectObjects = CollectObjects.Children; surf.useGeometry = NavMeshCollectGeometry.PhysicsColliders; surf.layerMask = GameLayers.Mask(GameLayers.WorldStatic);
            surf.BuildNavMesh();
            if (surf.navMeshData != null)
            {
                var path = $"{ScenesDir}/{region}_NavMesh.asset";
                AssetDatabase.CreateAsset(surf.navMeshData, path);
            }
        }

        static void BuildBoot(LevelPlan plan, GameDataCatalog catalog)
        {
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var systems = new GameObject("Systems");
            systems.AddComponent<GameFlowController>().currentSector = "S1";
            systems.AddComponent<EncounterDirector>();
            systems.AddComponent<CheckpointService>();
            AudioSetup.Attach(systems);
            systems.AddComponent<EventRunner>();
            var probe = systems.AddComponent<PerfProbe>(); probe.label = "S1_C1"; probe.sampleSeconds = 62f; // 91.4: 60 s tras 2 s de warmup
            var p01 = plan.Floor("P01").origin.ToVector3();
            probe.route = new[] { p01 + new Vector3(11, 0, 10), p01 + new Vector3(17, 0, 10), p01 + new Vector3(17, 0, 24), p01 + new Vector3(8, 0, 24), p01 + new Vector3(17, 0, 24), p01 + new Vector3(17, 0, 8), p01 + new Vector3(30, 0, 13) };
            // 16: niebla global moderada, ambiente bajo (luz de terror); la luz neutra de revisión vive en Art_Showcase
            RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Flat; RenderSettings.ambientLight = new Color(0.045f, 0.05f, 0.06f);
            RenderSettings.fog = true; RenderSettings.fogMode = FogMode.ExponentialSquared; RenderSettings.fogDensity = 0.018f; RenderSettings.fogColor = new Color(0.03f, 0.035f, 0.04f);
            var streamer = systems.AddComponent<RegionStreamer>(); streamer.initialRegion = "REG-S1";
            var cp0 = plan.checkpoints.Find(c => c.id == "CP-00"); plan.TryToWorld(cp0.space, cp0.x, cp0.z, out var start);
            var player = SandboxFactory.BuildPlayer(catalog, start);
            player.transform.rotation = Quaternion.Euler(0, 90, 0);
            ShowcaseBuilder.AttachViewmodel(player);
            PrefabUtility.SaveAsPrefabAssetAndConnect(player, "Assets/_Game/Prefabs/Player/Player_Esneider.prefab", InteractionMode.AutomatedAction);
            var hudRoot = new GameObject("HUD_Root");
            typeof(SandboxFactory).GetMethod("BuildHud", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Static).Invoke(null, new object[] { hudRoot.transform, player.GetComponent<PlayerController>() });
            // 81/87: menús (inicio/pausa/derrota/victoria/ajustes/documentos/mapa) y descubrimiento de salas desde el mismo plano
            var planText = AssetDatabase.LoadAssetAtPath<TextAsset>(LevelPlan.DefaultAssetPath);
            var menu = new GameObject("Menus").AddComponent<UI.MenuController>(); menu.planJson = planText;
            systems.AddComponent<RoomDiscovery>().planJson = planText;
            var light = new GameObject("Light").AddComponent<Light>(); light.type = LightType.Directional; light.transform.rotation = Quaternion.Euler(50, 30, 0); light.intensity = 0.7f;
            EditorSceneManager.SaveScene(scene, BootPath);
        }

        internal static Material BlockoutMat(string name, Color c)
        {
            string path = $"Assets/_Game/Art/Materials/Blockout/{name}.mat";
            var m = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (m == null) { m = new Material(Shader.Find("Universal Render Pipeline/Lit")); m.SetColor("_BaseColor", c); AssetDatabase.CreateAsset(m, path); }
            return m;
        }
    }
}
