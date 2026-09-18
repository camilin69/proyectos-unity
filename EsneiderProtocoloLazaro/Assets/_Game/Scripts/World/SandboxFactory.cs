using Esneider.AI;
using Esneider.Core;
using Esneider.Core.Data;
using Esneider.Player;
using Esneider.UI;
using Unity.AI.Navigation;
using UnityEngine;
using UnityEngine.AI;
using UnityEngine.UI;

namespace Esneider.World
{
    // Construye por código la habitación de combate H1/EX-02 (26: 12×12 m con pilar, Esneider, varilla, Vigía y Custodio placeholder).
    // Se usa desde el menú de editor (guarda escena/prefabs) y desde las pruebas Play Mode (escena en memoria).
    public static class SandboxFactory
    {
        public class Result
        {
            public GameObject root, player, vigia, custodio, crate, pillar;
            public GameFlowController flow;
        }

        public static Result Build(GameDataCatalog catalog, float size = 12f, float height = 4f)
        {
            var r = new Result();
            r.root = new GameObject("Combat_Sandbox");
            var flowGo = new GameObject("Systems"); flowGo.transform.SetParent(r.root.transform);
            r.flow = flowGo.AddComponent<GameFlowController>();
            flowGo.AddComponent<EncounterDirector>();

            var geo = new GameObject("Geometry"); geo.transform.SetParent(r.root.transform);
            var matFloor = Mat(new Color(0.42f, 0.44f, 0.45f)); var matWall = Mat(new Color(0.30f, 0.32f, 0.36f)); var matPillar = Mat(new Color(0.35f, 0.38f, 0.5f));
            Box(geo, "Floor", new Vector3(0, -0.1f, 0), new Vector3(size, 0.2f, size), matFloor, GameLayers.WorldStatic);
            Box(geo, "Ceiling", new Vector3(0, height + 0.1f, 0), new Vector3(size, 0.2f, size), matWall, GameLayers.WorldStatic);
            float h = size / 2f;
            Box(geo, "Wall_N", new Vector3(0, height / 2f, h + 0.2f), new Vector3(size + 0.8f, height, 0.4f), matWall, GameLayers.WorldStatic);
            Box(geo, "Wall_S", new Vector3(0, height / 2f, -h - 0.2f), new Vector3(size + 0.8f, height, 0.4f), matWall, GameLayers.WorldStatic);
            Box(geo, "Wall_E", new Vector3(h + 0.2f, height / 2f, 0), new Vector3(0.4f, height, size), matWall, GameLayers.WorldStatic);
            Box(geo, "Wall_W", new Vector3(-h - 0.2f, height / 2f, 0), new Vector3(0.4f, height, size), matWall, GameLayers.WorldStatic);
            r.pillar = Box(geo, "Pillar", new Vector3(0, height / 2f, 1.5f), new Vector3(0.8f, height, 0.8f), matPillar, GameLayers.WorldStatic);
            // carriles con fricción distinta (25: Physic Material observable)
            var rubber = new PhysicsMaterial("SUR-RUB") { staticFriction = 0.8f, dynamicFriction = 0.7f, bounciness = 0f, frictionCombine = PhysicsMaterialCombine.Maximum };
            var wet = new PhysicsMaterial("SUR-WET") { staticFriction = 0.55f, dynamicFriction = 0.45f, bounciness = 0f, frictionCombine = PhysicsMaterialCombine.Minimum };
            var laneR = Box(geo, "Lane_Rubber", new Vector3(-3.5f, 0.02f, -3f), new Vector3(2.5f, 0.05f, 5f), Mat(new Color(0.2f, 0.2f, 0.2f)), GameLayers.WorldStatic); laneR.GetComponent<Collider>().sharedMaterial = rubber;
            var laneW = Box(geo, "Lane_Wet", new Vector3(3.5f, 0.02f, -3f), new Vector3(2.5f, 0.05f, 5f), Mat(new Color(0.25f, 0.35f, 0.45f)), GameLayers.WorldStatic); laneW.GetComponent<Collider>().sharedMaterial = wet;

            // prop dinámico (20.2/25): Rigidbody + colisión por código
            r.crate = Box(geo, "Crate_Dynamic", new Vector3(-3.5f, 0.5f, -1f), new Vector3(0.9f, 0.9f, 0.9f), Mat(new Color(0.5f, 0.35f, 0.2f)), GameLayers.DynamicProp);
            var rb = r.crate.AddComponent<Rigidbody>(); rb.mass = 20f; rb.linearDamping = 0.3f; rb.centerOfMass = new Vector3(0, -0.3f, 0); rb.collisionDetectionMode = CollisionDetectionMode.Continuous;
            r.crate.AddComponent<PhysicsImpactLogger>();

            // pickups
            Pick(geo, "PICK-F01", PickupKind.Flashlight, new Vector3(-4.5f, 0.9f, 4.5f), 1);
            Pick(geo, "PICK-W01", PickupKind.Crowbar, new Vector3(-3.5f, 0.9f, 4.5f), 1);
            Pick(geo, "PICK-W02", PickupKind.Pistol, new Vector3(-2.5f, 0.9f, 4.5f), 1);
            Pick(geo, "PICK-W03", PickupKind.Shotgun, new Vector3(-1.5f, 0.9f, 4.5f), 1);
            Pick(geo, "A-SB1", PickupKind.PistolAmmo, new Vector3(-0.5f, 0.9f, 4.5f), 10);
            Pick(geo, "S-SB1", PickupKind.ShotgunAmmo, new Vector3(0.5f, 0.9f, 4.5f), 4);
            Pick(geo, "H-SB1", PickupKind.Syringe, new Vector3(1.5f, 0.9f, 4.5f), 1);
            Pick(geo, "R-SB1", PickupKind.Ration, new Vector3(2.5f, 0.9f, 4.5f), 1);
            for (int i = 0; i < 8; i++) Box(geo, "Shelf", new Vector3(-4.5f + i, 0.4f, 4.5f), new Vector3(0.6f, 0.8f, 0.6f), matWall, GameLayers.WorldStatic);

            r.player = BuildPlayer(catalog, new Vector3(0, 0, -4.5f));
            r.player.transform.SetParent(r.root.transform);
            var vigDef = catalog.enemies.Find(e => e.kind == EnemyKind.Vigia);
            var kDef = catalog.enemies.Find(e => e.kind == EnemyKind.Custodio);
            r.vigia = BuildEnemy(vigDef, "V-SB", new Vector3(-3.5f, 0, 2.5f), new Color(0.85f, 0.85f, 0.8f), 1.25f);
            r.custodio = BuildEnemy(kDef, "K-SB", new Vector3(3.5f, 0, 3f), new Color(0.6f, 0.4f, 0.35f), 2.15f);
            r.vigia.transform.SetParent(r.root.transform); r.custodio.transform.SetParent(r.root.transform);
            AddWaypoints(r.vigia, new Vector3(-3.5f, 0, 2.5f), new Vector3(-4.5f, 0, -1f));
            AddWaypoints(r.custodio, new Vector3(3.5f, 0, 3f), new Vector3(4.5f, 0, -1.5f));

            BuildHud(r.root.transform, r.player.GetComponent<PlayerController>());
            var light = new GameObject("Light").AddComponent<Light>(); light.type = LightType.Directional; light.transform.rotation = Quaternion.Euler(50, 30, 0); light.intensity = 0.6f; light.transform.SetParent(r.root.transform);
            var fill = new GameObject("Fill").AddComponent<Light>(); fill.type = LightType.Point; fill.range = 30f; fill.intensity = 1.5f; fill.transform.position = new Vector3(0, 3.5f, 0); fill.transform.SetParent(r.root.transform);
            flowGo.AddComponent<RuntimeNavMeshBaker>(); // al final: la geometría ya existe
            return r;
        }

        public static GameObject BuildPlayer(GameDataCatalog catalog, Vector3 position)
        {
            var go = new GameObject("Player"); go.layer = GameLayers.Player; go.tag = "Player";
            go.transform.position = position;
            var cc = go.AddComponent<CharacterController>();
            var input = go.AddComponent<PlayerInput>();
            var motor = go.AddComponent<PlayerMotor>(); motor.definition = catalog.player;
            var look = go.AddComponent<PlayerLook>();
            var inv = go.AddComponent<Inventory>(); inv.player = catalog.player;
            inv.crowbar = catalog.weapons.Find(w => w.kind == WeaponKind.Melee); inv.pistol = catalog.weapons.Find(w => w.kind == WeaponKind.Pistol); inv.shotgun = catalog.weapons.Find(w => w.kind == WeaponKind.Shotgun);
            var hp = go.AddComponent<Health>(); hp.maxHp = catalog.player.maxHp; hp.invulnerabilitySeconds = catalog.player.invulnerabilitySeconds; hp.ResetTo(hp.maxHp);
            var actions = go.AddComponent<PlayerActions>();
            var pivot = new GameObject("CameraPivot"); pivot.transform.SetParent(go.transform, false); pivot.transform.localPosition = new Vector3(0, 1.6f, 0);
            var cam = pivot.AddComponent<Camera>(); cam.tag = "MainCamera"; cam.nearClipPlane = 0.05f; cam.fieldOfView = catalog.player.fovVertical; pivot.AddComponent<AudioListener>();
            var flashGo = new GameObject("Flashlight"); flashGo.transform.SetParent(pivot.transform, false); flashGo.transform.localPosition = new Vector3(0.2f, -0.2f, 0.2f);
            var flash = flashGo.AddComponent<Light>(); flash.type = LightType.Spot; flash.spotAngle = 50f; flash.range = 14f; flash.intensity = 4f; flash.shadows = LightShadows.Soft; flash.enabled = false;
            var muzzle = new GameObject("Muzzle"); muzzle.transform.SetParent(pivot.transform, false); muzzle.transform.localPosition = new Vector3(0.18f, -0.15f, 0.45f);
            var hands = GameObject.CreatePrimitive(PrimitiveType.Cube); hands.name = "Hands_Placeholder"; Kill(hands.GetComponent<Collider>()); hands.transform.SetParent(pivot.transform, false); hands.transform.localPosition = new Vector3(0.2f, -0.25f, 0.4f); hands.transform.localScale = new Vector3(0.08f, 0.08f, 0.35f); hands.GetComponent<MeshRenderer>().sharedMaterial = Mat(new Color(0.75f, 0.6f, 0.5f)); hands.layer = GameLayers.Player;
            look.cameraPivot = pivot.transform; look.playerCamera = cam; look.fovVertical = catalog.player.fovVertical;
            actions.inventory = inv; actions.look = look; actions.health = hp; actions.motor = motor; actions.muzzle = muzzle.transform;
            var pc = go.AddComponent<PlayerController>();
            pc.input = input; pc.motor = motor; pc.look = look; pc.actions = actions; pc.inventory = inv; pc.health = hp; pc.flashlight = flash;
            return go;
        }

        public static GameObject BuildEnemy(EnemyDefinition def, string id, Vector3 position, Color color, float height)
        {
            var go = new GameObject(id); go.layer = GameLayers.Enemy; go.transform.position = position;
            var vis = GameObject.CreatePrimitive(PrimitiveType.Capsule); vis.name = "Body"; vis.layer = GameLayers.Enemy;
            vis.transform.SetParent(go.transform, false); vis.transform.localPosition = new Vector3(0, height / 2f, 0); vis.transform.localScale = new Vector3(0.6f, height / 2f, 0.6f);
            vis.GetComponent<MeshRenderer>().sharedMaterial = Mat(color);
            var head = new GameObject("Head"); head.transform.SetParent(go.transform, false); head.transform.localPosition = new Vector3(0, height - 0.15f, 0.1f);
            var eye = GameObject.CreatePrimitive(PrimitiveType.Cube); eye.name = "Face"; Kill(eye.GetComponent<Collider>()); eye.transform.SetParent(head.transform, false); eye.transform.localPosition = new Vector3(0, 0, 0.25f); eye.transform.localScale = new Vector3(0.3f, 0.2f, 0.1f); eye.GetComponent<MeshRenderer>().sharedMaterial = Mat(Color.black); eye.layer = GameLayers.Enemy;
            var muzzle = new GameObject("Muzzle"); muzzle.transform.SetParent(go.transform, false); muzzle.transform.localPosition = new Vector3(0.3f, height * 0.6f, 0.4f);
            var agent = go.AddComponent<NavMeshAgent>(); agent.height = height; agent.radius = 0.35f; agent.baseOffset = 0f;
            agent.enabled = false; // RuntimeNavMeshBaker lo activa cuando existe superficie
            var hp = go.AddComponent<Health>(); hp.maxHp = def.maxHp; hp.ResetTo(def.maxHp);
            var per = go.AddComponent<EnemyPerception>(); per.definition = def; per.sensor = head.transform;
            var brain = go.AddComponent<EnemyBrain>(); brain.definition = def; brain.stableId = id; brain.muzzle = muzzle.transform;
            return go;
        }

        static void AddWaypoints(GameObject enemy, params Vector3[] points)
        {
            var brain = enemy.GetComponent<EnemyBrain>();
            var root = new GameObject(enemy.name + "_Waypoints"); root.transform.SetParent(enemy.transform.parent);
            foreach (var p in points) { var w = new GameObject("WP"); w.transform.SetParent(root.transform); w.transform.position = p; brain.waypoints.Add(w.transform); }
        }

        static void BuildHud(Transform parent, PlayerController player)
        {
            var canvasGo = new GameObject("HUD"); canvasGo.transform.SetParent(parent);
            var canvas = canvasGo.AddComponent<Canvas>(); canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            var scaler = canvasGo.AddComponent<CanvasScaler>(); scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize; scaler.referenceResolution = new Vector2(1280, 720);
            var hud = canvasGo.AddComponent<HudController>(); hud.player = player;
            var font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            Text T(string n, Vector2 anchor, Vector2 pos, int size, TextAnchor align)
            {
                var g = new GameObject(n); g.transform.SetParent(canvasGo.transform, false);
                var t = g.AddComponent<Text>(); t.font = font; t.fontSize = size; t.color = Color.white; t.alignment = align;
                var rt = t.rectTransform; rt.anchorMin = rt.anchorMax = anchor; rt.pivot = anchor; rt.anchoredPosition = pos; rt.sizeDelta = new Vector2(600, 40);
                return t;
            }
            hud.hpText = T("HP", new Vector2(0, 0), new Vector2(20, 20), 22, TextAnchor.LowerLeft);
            hud.staminaText = T("Stamina", new Vector2(0, 0), new Vector2(20, 50), 16, TextAnchor.LowerLeft);
            hud.ammoText = T("Ammo", new Vector2(1, 0), new Vector2(-20, 20), 22, TextAnchor.LowerRight);
            hud.promptText = T("Prompt", new Vector2(0.5f, 0.5f), new Vector2(0, -60), 18, TextAnchor.MiddleCenter);
            hud.messageText = T("Message", new Vector2(0.5f, 1), new Vector2(0, -40), 18, TextAnchor.UpperCenter);
            hud.stateText = T("State", new Vector2(0.5f, 0.5f), new Vector2(0, 60), 30, TextAnchor.MiddleCenter);
            hud.crosshair = T("Crosshair", new Vector2(0.5f, 0.5f), Vector2.zero, 18, TextAnchor.MiddleCenter); hud.crosshair.text = "·";
        }

        static GameObject Pick(GameObject parent, string id, PickupKind kind, Vector3 pos, int amount)
        {
            var go = GameObject.CreatePrimitive(kind == PickupKind.Pistol || kind == PickupKind.Shotgun || kind == PickupKind.Crowbar ? PrimitiveType.Cylinder : PrimitiveType.Sphere);
            go.name = "Pickup_" + id; go.layer = GameLayers.Interactable; go.transform.SetParent(parent.transform); go.transform.position = pos; go.transform.localScale = Vector3.one * 0.25f;
            go.GetComponent<MeshRenderer>().sharedMaterial = Mat(kind == PickupKind.Syringe || kind == PickupKind.Ration ? Color.green : kind == PickupKind.Flashlight ? Color.yellow : new Color(0.8f, 0.8f, 0.2f));
            var p = go.AddComponent<Pickup>(); p.kind = kind; p.amount = amount; p.stableId = id; p.guid = LevelPlan.StableGuid(id).ToString();
            return go;
        }

        static GameObject Box(GameObject parent, string name, Vector3 center, Vector3 size, Material mat, int layer)
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Cube); go.name = name; go.layer = layer;
            go.transform.SetParent(parent.transform); go.transform.position = center; go.transform.localScale = size;
            go.GetComponent<MeshRenderer>().sharedMaterial = mat; go.isStatic = layer == GameLayers.WorldStatic;
            return go;
        }

        static void Kill(Object o) { if (o == null) return; if (Application.isPlaying) Object.Destroy(o); else Object.DestroyImmediate(o); }

        public static Material Mat(Color c)
        {
            var shader = Shader.Find("Universal Render Pipeline/Lit") ?? Shader.Find("Standard");
            var m = new Material(shader); m.SetColor("_BaseColor", c); m.color = c; return m;
        }
    }
}
