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
            var summary = new List<string>();
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
                BuildLighting(plan, region, floors, connectors, root.transform);
                BuildNarrative(plan, region, root.transform.Find("Entities"));
                BuildVolume(plan, region, floors, connectors, root.transform);
                var vol = root.transform.Find("Volume_" + region);
                if (vol != null) { var ra = vol.gameObject.AddComponent<Audio.RegionAudio>(); ra.regionId = region; ra.ambienceBank = "SND-AMBI-" + region.Replace("REG-", ""); ra.reverb = region.StartsWith("REG-C") ? AudioReverbPreset.Hangar : region == "REG-S3" ? AudioReverbPreset.Room : region == "REG-S4" ? AudioReverbPreset.Auditorium : AudioReverbPreset.StoneCorridor; }
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
            return string.Join(" | ", summary);
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
                var go = SandboxFactory.BuildEnemy(def, s.id, w, boss ? new Color(0.9f, 0.85f, 0.9f) : s.kind == "Vigia" ? new Color(0.85f, 0.85f, 0.8f) : new Color(0.6f, 0.4f, 0.35f), boss ? 3.1f : s.kind == "Vigia" ? 1.25f : 2.15f, heroPrefab, heroClips);
                go.transform.SetParent(ents); go.transform.rotation = Quaternion.Euler(0, s.yaw, 0);
                var brain = go.GetComponent<EnemyBrain>(); brain.tutorialTelegraph = s.id == "V01";
                brain.startActive = region != "REG-S1" && region != "REG-C1"; // 104.3: sin ataques antes de D06; EVT-C1 activa S1/C1
                if (boss) { go.name = "B01_Archivista_Placeholder"; brain.enabled = false; } // el jefe real llega en EX-07; placeholder inerte
                // patrulla inicial: punto de spawn y segundo punto a 3–6 m (68.7, se valida en blockout)
                var wps = new GameObject(s.id + "_Waypoints"); wps.transform.SetParent(ents);
                var w0 = new GameObject("WP0"); w0.transform.SetParent(wps.transform); w0.transform.position = w; brain.waypoints.Add(w0.transform);
                var second = w + Quaternion.Euler(0, s.yaw, 0) * Vector3.forward * 4f;
                var w1 = new GameObject("WP1"); w1.transform.SetParent(wps.transform); w1.transform.position = second; brain.waypoints.Add(w1.transform);
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
                var cryo = ents.Find("OBJ-001_Criocamara");
                var go = new GameObject("EVT-01_Opening"); go.transform.SetParent(ents);
                var op = go.AddComponent<OpeningSequence>();
                op.cryoLidAnimatorRoot = cryo; op.cryoOpenClip = AssetDatabase.LoadAllAssetsAtPath("Assets/_Game/Art/Models/OBJ-001_Criocamara.fbx").OfType<AnimationClip>().FirstOrDefault(c => c.name == "Cryo_Open");
                op.lyingPosition = plan.Floor("P01").origin.ToVector3() + new Vector3(6f, 0.75f, 8f); op.lyingYaw = 90f;
            }
            if (region == "REG-C1")
            {
                var c = plan.Connector("C-01"); var w = c.origin.ToVector3() + new Vector3(4f, c.height - 0.8f, -c.width / 2f + 0.3f);
                var sp = GameObject.CreatePrimitive(PrimitiveType.Cube); sp.name = "OBJ-065_Altavoz"; sp.layer = GameLayers.WorldStatic; sp.transform.SetParent(ents); sp.transform.position = w; sp.transform.localScale = new Vector3(0.4f, 0.3f, 0.25f);
                sp.AddComponent<AnnouncementSpeaker>().doorId = "D06";
            }
        }

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
            var probe = systems.AddComponent<PerfProbe>(); probe.label = "S1_C1"; probe.sampleSeconds = 40f;
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
            var light = new GameObject("Light").AddComponent<Light>(); light.type = LightType.Directional; light.transform.rotation = Quaternion.Euler(50, 30, 0); light.intensity = 0.7f;
            EditorSceneManager.SaveScene(scene, BootPath);
        }

        static Material BlockoutMat(string name, Color c)
        {
            string path = $"Assets/_Game/Art/Materials/Blockout/{name}.mat";
            var m = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (m == null) { m = new Material(Shader.Find("Universal Render Pipeline/Lit")); m.SetColor("_BaseColor", c); AssetDatabase.CreateAsset(m, path); }
            return m;
        }
    }
}
