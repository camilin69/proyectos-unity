using System.Collections.Generic;
using System.IO;
using System.Linq;
using Esneider.Core;
using Esneider.Core.Data;
using Esneider.World;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Esneider.EditorTools
{
    // 45.3/44: escena de revisión con los assets hero bajo luz neutra conmutable y luz de juego (linterna real), con jugador.
    public static class ShowcaseBuilder
    {
        public const string ScenePath = "Assets/_Game/Scenes/Art_Showcase.unity";
        public static readonly string[] Heroes = { "BOT-01_Vigia", "BOT-02_Custodio", "BOT-03_Archivista", "CHR-01_Arms", "WPN-01_Crowbar", "WPN-02_Pistol", "WPN-03_Shotgun", "WPN-04_Flashlight", "PRP-Syringe", "PRP-Ration", "OBJ-001_Criocamara", "OBJ-041_Jaula", "OBJ-070_PuertaCorrediza", "OBJ-059_Terminal", "OBJ-043_Camilla", "OBJ-029_Carro" };

        [MenuItem("Esneider/Art/Build showcase")]
        public static void BuildMenu() => Build();

        public static string Build()
        {
            var catalog = AssetDatabase.LoadAssetAtPath<GameDataCatalog>(SandboxBuilder.CatalogPath);
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var root = new GameObject("Showcase");
            var sys = new GameObject("Systems"); sys.transform.SetParent(root.transform); sys.AddComponent<GameFlowController>(); sys.AddComponent<AI.EncounterDirector>();
            var floorMat = AssetDatabase.LoadAssetAtPath<Material>("Assets/_Game/Art/Materials/Blockout/Blockout_Floor.mat") ?? SandboxFactory.Mat(new Color(0.42f, 0.44f, 0.45f));
            var floor = GameObject.CreatePrimitive(PrimitiveType.Cube); floor.name = "Floor"; floor.layer = GameLayers.WorldStatic; floor.transform.SetParent(root.transform); floor.transform.position = new Vector3(12, -0.1f, 0); floor.transform.localScale = new Vector3(40, 0.2f, 16); floor.GetComponent<MeshRenderer>().sharedMaterial = floorMat; floor.isStatic = true;
            var wall = GameObject.CreatePrimitive(PrimitiveType.Cube); wall.name = "Backwall"; wall.layer = GameLayers.WorldStatic; wall.transform.SetParent(root.transform); wall.transform.position = new Vector3(12, 2.5f, 6f); wall.transform.localScale = new Vector3(40, 5, 0.3f); wall.GetComponent<MeshRenderer>().sharedMaterial = AssetDatabase.LoadAssetAtPath<Material>("Assets/_Game/Art/Materials/Blockout/Blockout_Solid.mat") ?? floorMat; wall.isStatic = true;
            var found = new List<string>();
            float x = 0f;
            foreach (var id in Heroes)
            {
                var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(Prefab(id));
                if (prefab == null) continue;
                var inst = (GameObject)PrefabUtility.InstantiatePrefab(prefab); inst.transform.SetParent(root.transform); inst.transform.position = new Vector3(x, 0, 2f);
                var b = new Bounds(inst.transform.position, Vector3.zero); bool first = true;
                foreach (var r in inst.GetComponentsInChildren<Renderer>()) { if (first) { b = r.bounds; first = false; } else b.Encapsulate(r.bounds); }
                if (b.size.y < 0.5f) inst.transform.position = new Vector3(x, 1.0f, 2f); // objetos pequeños a la altura de la mano sobre un pedestal
                if (b.size.y < 0.5f) { var ped = GameObject.CreatePrimitive(PrimitiveType.Cube); ped.name = "Pedestal_" + id; ped.layer = GameLayers.WorldStatic; ped.transform.SetParent(root.transform); ped.transform.position = new Vector3(x, 0.45f, 2f); ped.transform.localScale = new Vector3(0.5f, 0.9f, 0.5f); ped.GetComponent<MeshRenderer>().sharedMaterial = floorMat; }
                var label = new GameObject("Label_" + id); label.transform.SetParent(root.transform); label.transform.position = new Vector3(x, Mathf.Max(b.size.y, 1.2f) + 0.3f, 2f);
                found.Add(id); x += Mathf.Max(1.6f, b.size.x + 1.2f);
            }
            var player = SandboxFactory.BuildPlayer(catalog, new Vector3(2f, 0, -4f)); player.transform.SetParent(root.transform);
            var pc = player.GetComponent<Player.PlayerController>(); pc.inventory.hasFlashlight = true; pc.inventory.hasCrowbar = true; pc.inventory.hasPistol = true; pc.inventory.hasShotgun = true; pc.inventory.pistolMag = 12; pc.inventory.pistolReserve = 40; pc.inventory.shotgunMag = 6; pc.inventory.shotgunReserve = 20;
            AttachViewmodel(player);
            var neutral = new GameObject("Light_Neutral"); neutral.transform.SetParent(root.transform);
            var l1 = neutral.AddComponent<Light>(); l1.type = LightType.Directional; l1.intensity = 1.2f; l1.color = new Color(1f, 0.98f, 0.95f); neutral.transform.rotation = Quaternion.Euler(45, -30, 0);
            var fillGo = new GameObject("Light_Fill"); fillGo.transform.SetParent(neutral.transform); var l2 = fillGo.AddComponent<Light>(); l2.type = LightType.Directional; l2.intensity = 0.35f; l2.color = new Color(0.85f, 0.9f, 1f); fillGo.transform.rotation = Quaternion.Euler(30, 150, 0);
            var horror = new GameObject("Light_Game"); horror.transform.SetParent(root.transform); horror.SetActive(false);
            var l3 = horror.AddComponent<Light>(); l3.type = LightType.Point; l3.intensity = 0.6f; l3.range = 12f; l3.color = new Color(0.55f, 0.65f, 0.75f); horror.transform.position = new Vector3(6, 3.5f, 0);
            var toggle = root.AddComponent<ShowcaseLightToggle>(); toggle.neutral = neutral; toggle.game = horror;
            RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Flat; RenderSettings.ambientLight = new Color(0.25f, 0.26f, 0.28f);
            Directory.CreateDirectory(Path.GetDirectoryName(ScenePath));
            EditorSceneManager.SaveScene(scene, ScenePath);
            var scenes = new List<EditorBuildSettingsScene>(EditorBuildSettings.scenes);
            if (!scenes.Exists(s => s.path == ScenePath)) { scenes.Add(new EditorBuildSettingsScene(ScenePath, true)); EditorBuildSettings.scenes = scenes.ToArray(); }
            return $"showcase: {found.Count}/{Heroes.Length} assets: " + string.Join(", ", found);
        }

        public static string Prefab(string id) => id.StartsWith("BOT") ? $"Assets/_Game/Prefabs/Enemies/{id}.prefab" : id.StartsWith("CHR") ? $"Assets/_Game/Prefabs/Player/{id}.prefab" : id.StartsWith("WPN") || id.StartsWith("PRP") ? $"Assets/_Game/Prefabs/Weapons/{id}.prefab" : $"Assets/_Game/Prefabs/Environment/{id}.prefab";

        // 38: viewmodel de brazos + arma activa bajo la cámara del jugador
        public static void AttachViewmodel(GameObject player)
        {
            var pivot = player.transform.Find("CameraPivot"); if (pivot == null) return;
            var old = pivot.Find("Hands_Placeholder"); if (old != null) Object.DestroyImmediate(old.gameObject);
            var vm = pivot.GetComponent<Player.ViewmodelController>() ?? pivot.gameObject.AddComponent<Player.ViewmodelController>();
            vm.actions = player.GetComponent<Player.PlayerActions>(); vm.cameraPivot = pivot;
            vm.armsPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(Prefab("CHR-01_Arms"));
            vm.crowbarPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(Prefab("WPN-01_Crowbar")); vm.pistolPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(Prefab("WPN-02_Pistol")); vm.shotgunPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(Prefab("WPN-03_Shotgun")); vm.flashlightPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(Prefab("WPN-04_Flashlight"));
            vm.armClips = AssetDatabase.LoadAllAssetsAtPath("Assets/_Game/Art/Models/CHR-01_Arms.fbx").OfType<AnimationClip>().Where(c => !c.name.StartsWith("__")).ToArray();
        }
    }
}
