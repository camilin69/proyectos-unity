using System;
using System.Linq;
using Esneider.Core;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using Object = UnityEngine.Object;

namespace Esneider.EditorTools
{
    public static class ClinicalPlacement
    {
        static GameObject Place(string asset, Transform parent, Vector3 pos, float yaw = 0)
        {
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(FurnitureReview.Prefab(asset));
            if (!prefab) throw new InvalidOperationException("Missing clinical prefab " + asset);
            var go = (GameObject)PrefabUtility.InstantiatePrefab(prefab, parent);
            go.transform.SetPositionAndRotation(pos, Quaternion.Euler(0, yaw, 0)); return go;
        }
        public static string Apply(Transform root)
        {
            var all = root.GetComponentsInChildren<Transform>(true);
            var existing = all.FirstOrDefault(t => t.name == "Clinic_EX21");
            if (existing) return EnsureNavigation(existing);
            var old = all.FirstOrDefault(t => t.name == "M059_instrumental");
            if (!old) return "";
            foreach (var asset in new[] { "OBJ-006_CarroSanitario", "OBJ-047_SoporteFluidos", "OBJ-049_BandejaInstrumental", "OBJ-051_LavamanosIndustrial", "OBJ-052_RejillaDrenaje" })
                if (!AssetDatabase.LoadAssetAtPath<GameObject>(FurnitureReview.Prefab(asset))) return "Clinical prefabs pending";
            var floor = old.position - Vector3.up * .6f;
            // M059 is the clinical instrument station; the sink shares its floor and backs onto the east wall.
            Physics.SyncTransforms(); RaycastHit hit;
            var ray = floor + new Vector3(0, .5f, 6);
            if (!Physics.Raycast(ray, Vector3.right, out hit, 4, GameLayers.Mask(GameLayers.WorldStatic), QueryTriggerInteraction.Ignore))
                throw new InvalidOperationException("No clinic wall for sink drain");
            var group = new GameObject("Clinic_EX21").transform; group.SetParent(old.parent); group.position = floor;
            for (int i = 0; i < 2; i++)
            {
                var cart = Place("OBJ-006_CarroSanitario", group, floor + Vector3.forward * (i == 0 ? -.55f : .55f));
                cart.name = "M059_Cart_" + i;
                var tray = Place("OBJ-049_BandejaInstrumental", group, cart.transform.position + Vector3.up * .799f, i == 0 ? 0 : 180);
                tray.name = "M059_Tray_" + i;
            }
            var sinkPosition = new Vector3(hit.point.x - .318f, floor.y, ray.z);
            var sink = Place("OBJ-051_LavamanosIndustrial", group, sinkPosition, 90); sink.name = "Clinic_Sink_EX21";
            var drain = Place("OBJ-052_RejillaDrenaje", group, sinkPosition + new Vector3(-.65f, -.032f, 0), 90); drain.name = "Clinic_Drain_EX21";
            // Near the procedure table, beyond its original 2 m footprint.
            var stand = Place("OBJ-047_SoporteFluidos", group, floor + new Vector3(-10.6f, 0, 1)); stand.name = "Clinic_FluidStand_EX21";
            EnsureNavigation(group);
            Object.DestroyImmediate(old.gameObject);
            return "M059: two carts and trays; fluid stand; sink at " + sinkPosition + " backing onto " + hit.collider.name + "; floor drain";
        }
        static string EnsureNavigation(Transform group)
        {
            bool changed = false;
            foreach (var name in new[] { "Clinic_Sink_EX21", "Clinic_FluidStand_EX21" })
            {
                var target = group.Find(name);
                if (!target || target.GetComponent<UnityEngine.AI.NavMeshObstacle>()) continue;
                var obstacle = target.gameObject.AddComponent<UnityEngine.AI.NavMeshObstacle>();
                obstacle.shape = UnityEngine.AI.NavMeshObstacleShape.Box;
                obstacle.size = name.Contains("Sink") ? new Vector3(.8f, .9f, .62f) : new Vector3(.6f, 1.7f, .6f);
                obstacle.center = Vector3.up * obstacle.size.y * .5f; obstacle.carving = true; changed = true;
            }
            return changed ? "Clinical navigation obstacles added" : "";
        }
        public static string ApplyExisting()
        {
            const string path = "Assets/_Game/Scenes/Regions/REG-S3.unity";
            var previous = SceneManager.GetActiveScene(); var scene = SceneManager.GetSceneByPath(path);
            bool opened = !scene.IsValid() || !scene.isLoaded;
            if (opened) scene = EditorSceneManager.OpenScene(path, OpenSceneMode.Additive);
            else if (scene.isDirty) throw new InvalidOperationException("Unsaved S3 changes");
            try
            {
                var result = Apply(scene.GetRootGameObjects().Single(g => g.name == "REG-S3").transform);
                if (!string.IsNullOrEmpty(result)) EditorSceneManager.SaveScene(scene);
                if (!string.IsNullOrEmpty(result)) System.IO.File.AppendAllText("../SourceArt/_evidence/EX-21/placement.txt", "\n" + result); return result;
            }
            finally
            {
                if (opened) EditorSceneManager.CloseScene(scene, true);
                if (previous.IsValid() && previous.isLoaded) SceneManager.SetActiveScene(previous);
            }
        }
    }
}
