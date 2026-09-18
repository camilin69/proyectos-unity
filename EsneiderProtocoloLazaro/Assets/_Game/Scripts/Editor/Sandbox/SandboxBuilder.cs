using System.IO;
using Esneider.Core;
using Esneider.Core.Data;
using Esneider.World;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Esneider.EditorTools
{
    public static class SandboxBuilder
    {
        public const string ScenePath = "Assets/_Game/Scenes/Combat_Sandbox.unity";
        public const string CatalogPath = "Assets/_Game/Data/Definitions/GameDataCatalog.asset";

        [MenuItem("Esneider/Sandbox/Build Combat_Sandbox")]
        public static void BuildMenu() => Build();

        public static string Build()
        {
            var catalog = AssetDatabase.LoadAssetAtPath<GameDataCatalog>(CatalogPath);
            if (catalog == null) return "Catálogo no encontrado: ejecutar Esneider/Data primero";
            ApplyCollisionMatrix();
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var r = SandboxFactory.Build(catalog);
            // prefabs reutilizables (20: Prefabs/Player, Prefabs/Enemies)
            Directory.CreateDirectory("Assets/_Game/Prefabs/Player"); Directory.CreateDirectory("Assets/_Game/Prefabs/Enemies");
            PrefabUtility.SaveAsPrefabAssetAndConnect(r.player, "Assets/_Game/Prefabs/Player/Player_Esneider.prefab", InteractionMode.AutomatedAction);
            PrefabUtility.SaveAsPrefabAssetAndConnect(r.vigia, "Assets/_Game/Prefabs/Enemies/Vigia_Placeholder.prefab", InteractionMode.AutomatedAction);
            PrefabUtility.SaveAsPrefabAssetAndConnect(r.custodio, "Assets/_Game/Prefabs/Enemies/Custodio_Placeholder.prefab", InteractionMode.AutomatedAction);
            Directory.CreateDirectory(Path.GetDirectoryName(ScenePath));
            EditorSceneManager.SaveScene(scene, ScenePath);
            var scenes = new System.Collections.Generic.List<EditorBuildSettingsScene>(EditorBuildSettings.scenes);
            if (!scenes.Exists(s => s.path == ScenePath)) { scenes.Add(new EditorBuildSettingsScene(ScenePath, true)); EditorBuildSettings.scenes = scenes.ToArray(); }
            return "Combat_Sandbox guardada en " + ScenePath;
        }

        // Sección 20.3: matriz de colisión documentada en el proyecto.
        public static void ApplyCollisionMatrix()
        {
            int P = GameLayers.Player, E = GameLayers.Enemy, W = GameLayers.WorldStatic, D = GameLayers.DynamicProp, PP = GameLayers.PlayerProjectile, EP = GameLayers.EnemyProjectile, I = GameLayers.Interactable, T = GameLayers.Trigger, C = GameLayers.Corpse, V = GameLayers.VFX;
            int[] all = { P, E, W, D, PP, EP, I, T, C, V };
            foreach (var a in all) foreach (var b in all) Physics.IgnoreLayerCollision(a, b, false);
            // proyectil enemigo: solo Player, WorldStatic, DynamicProp (colisión por barrido, pero se documenta igual)
            foreach (var b in all) if (b != P && b != W && b != D) Physics.IgnoreLayerCollision(EP, b, true);
            foreach (var b in all) if (b != E && b != W && b != D) Physics.IgnoreLayerCollision(PP, b, true);
            // cadáver: no bloquea sensores ni jugador/enemigos; solo apoya en mundo
            foreach (var b in all) if (b != W && b != D) Physics.IgnoreLayerCollision(C, b, true);
            // triggers y VFX no colisionan físicamente con nadie
            foreach (var b in all) { Physics.IgnoreLayerCollision(T, b, true); Physics.IgnoreLayerCollision(V, b, true); }
            // enemigos entre sí sí colisionan (agentes evitan); interactuables no empujan al jugador
            Physics.IgnoreLayerCollision(I, P, true); Physics.IgnoreLayerCollision(I, E, true);
        }
    }
}
