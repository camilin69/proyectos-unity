using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Esneider.Core;
using Esneider.Core.Data;
using Esneider.World;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using Object = UnityEngine.Object;

namespace Esneider.EditorTools
{
    public static class CabinetPlacement
    {
        static GameObject Place(string asset, string id, string region, Transform parent, Vector3 position, float yaw)
        {
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(FurnitureReview.Prefab(asset));
            if (!prefab) throw new InvalidOperationException("Missing cabinet: " + asset);
            var go = (GameObject)PrefabUtility.InstantiatePrefab(prefab, parent);
            go.name = id + "_EX18";
            go.transform.SetPositionAndRotation(position, Quaternion.Euler(0, yaw, 0));
            var pe = go.GetComponent<PersistentEntity>();
            pe.stableId = id; pe.guid = LevelPlan.StableGuid(id).ToString(); pe.regionId = region; pe.prefabId = asset;
            // Leaves move at runtime and must not be included in static batching.
            foreach (var t in go.GetComponentsInChildren<Transform>(true)) t.gameObject.isStatic = false;
            return go;
        }

        static Bounds VisibleBounds(Transform target)
        {
            var renderers = target.GetComponentsInChildren<Renderer>().Where(r => r.enabled).ToArray();
            if (renderers.Length == 0) throw new InvalidOperationException("No pickup visual: " + target.name);
            var bounds = renderers[0].bounds;
            foreach (var r in renderers.Skip(1)) bounds.Encapsulate(r.bounds);
            return bounds;
        }

        static void FitWeapon(Transform pickup, Transform cabinet, bool shotgun)
        {
            var visual = pickup.Find("Visual");
            if (!visual) throw new InvalidOperationException("Missing weapon visual");
            pickup.rotation = cabinet.rotation;
            visual.localRotation = shotgun ? Quaternion.Euler(-90, 0, 0) : Quaternion.identity;
            var bounds = VisibleBounds(pickup);
            var target = cabinet.TransformPoint(shotgun ? new Vector3(-.26f, .328f, .07f) : new Vector3(.22f, .595f, -.04f));
            pickup.position += target - new Vector3(bounds.center.x, bounds.min.y, bounds.center.z);
            // The old sphere was wider than the pistol. Keep interaction wholly inside the closed cabinet.
            foreach (var c in pickup.GetComponents<Collider>()) Object.DestroyImmediate(c);
            bounds = VisibleBounds(pickup);
            var trigger = pickup.gameObject.AddComponent<BoxCollider>(); trigger.isTrigger = true;
            trigger.center = pickup.InverseTransformPoint(bounds.center);
            trigger.size = new Vector3(Mathf.Max(.10f, bounds.size.x), Mathf.Max(.10f, bounds.size.y), Mathf.Max(.08f, bounds.size.z)) / pickup.lossyScale.x;
        }

        public static string Apply(Transform root, string region)
        {
            var all = root.GetComponentsInChildren<Transform>(true);
            var changes = new List<string>();
            var old = all.FirstOrDefault(t => t.name == "M006_taquillas");
            if (old)
            {
                var floor = old.position - Vector3.up * 1.05f;
                var group = new GameObject("M006_EX18").transform; group.SetParent(old.parent); group.position = floor;
                for (int i = 0; i < 3; i++) Place("OBJ-007_ArmarioPreparacion", "CAB-M006-" + i, region, group, floor + Vector3.forward * (i - 1) * 1.04f, 270);
                Object.DestroyImmediate(old.gameObject); changes.Add("M006: 3 armarios");
            }
            foreach (var id in new[] { "PICK-W02", "PICK-W03" })
            {
                old = all.FirstOrDefault(t => t && t.name == "Support_" + id);
                if (!old) continue;
                var pickup = all.Single(t => t && t.name == "Pickup_" + id);
                bool shotgun = id == "PICK-W03";
                var floor = new Vector3(old.position.x, old.position.y - old.lossyScale.y * .5f, old.position.z);
                var cabinet = Place(shotgun ? "OBJ-025_ArmarioEscopeta" : "OBJ-024_LockerSeguridad", "CAB-" + id, region, old.parent, floor, 0);
                FitWeapon(pickup, cabinet.transform, shotgun);
                Object.DestroyImmediate(old.gameObject); changes.Add(id + ": soporte sustituido, identidad conservada");
            }
            old = all.FirstOrDefault(t => t && t.name == "Cabinet_CP06_Placeholder");
            if (old)
            {
                Place("OBJ-026_GabineteSuministros", "CAB-CP06", region, old.parent, old.position - Vector3.up * 1.1f, 0);
                Object.DestroyImmediate(old.gameObject); changes.Add("CP06: gabinete; garantías permanecen en CheckpointService");
            }
            foreach (var cabinet in root.GetComponentsInChildren<HingedCabinet>(true))
            {
                if(cabinet.GetComponent<ServicePanelVisual>())continue; // Wall cabinet does not occupy the floor route.
                if (cabinet.GetComponent<UnityEngine.AI.NavMeshObstacle>()) continue;
                var obstacle = cabinet.gameObject.AddComponent<UnityEngine.AI.NavMeshObstacle>();
                obstacle.shape = UnityEngine.AI.NavMeshObstacleShape.Box;
                obstacle.center = new Vector3(0, .95f, 0);
                obstacle.size = new Vector3(cabinet.name.Contains("W03") ? 1.2f : 1f, 1.9f, .55f);
                obstacle.carving = true;
                changes.Add(cabinet.name + ": obstáculo de navegación");
            }
            return string.Join("\n", changes);
        }

        public static string ApplyExisting()
        {
            var previous = SceneManager.GetActiveScene(); var result = new List<string>();
            foreach (var region in new[] { "REG-S1", "REG-S2", "REG-S3", "REG-S4" })
            {
                var path = "Assets/_Game/Scenes/Regions/" + region + ".unity";
                var scene = SceneManager.GetSceneByPath(path); bool opened = !scene.IsValid() || !scene.isLoaded;
                if (opened) scene = EditorSceneManager.OpenScene(path, OpenSceneMode.Additive);
                else if (scene.isDirty) throw new InvalidOperationException("Unsaved scene: " + region);
                try
                {
                    var root = scene.GetRootGameObjects().Single(g => g.name == region);
                    string changes = Apply(root.transform, region);
                    if (!string.IsNullOrEmpty(changes)) { EditorSceneManager.SaveScene(scene); result.Add(region + "\n" + changes); }
                }
                finally { if (opened) EditorSceneManager.CloseScene(scene, true); }
            }
            if (previous.IsValid() && previous.isLoaded) SceneManager.SetActiveScene(previous);
            return string.Join("\n", result);
        }

        public static string Audit(bool capture = false)
        {
            string dir = Path.GetFullPath("../SourceArt/_evidence/EX-18"); Directory.CreateDirectory(dir);
            var rows = new List<string>(); var previous = SceneManager.GetActiveScene();
            foreach (var region in new[] { "REG-S1", "REG-S2", "REG-S3", "REG-S4" })
            {
                var path = "Assets/_Game/Scenes/Regions/" + region + ".unity";
                var scene = SceneManager.GetSceneByPath(path); bool opened = !scene.IsValid() || !scene.isLoaded;
                if (opened) scene = EditorSceneManager.OpenScene(path, OpenSceneMode.Additive);
                try
                {
                    var cabinets = scene.GetRootGameObjects().SelectMany(g => g.GetComponentsInChildren<HingedCabinet>(true)).ToArray();
                    foreach (var cabinet in cabinets)
                    {
                        var rotations = cabinet.leaves.Select(t => t.localRotation).ToArray();
                        var pe = cabinet.GetComponent<PersistentEntity>();
                        rows.Add(region + "/" + cabinet.name + " guid=" + pe.guid + " pos=" + cabinet.transform.position);
                        var obstacles = new HashSet<string>();
                        try
                        {
                            for (int step = 0; step <= 60; step++)
                            {
                                for (int i = 0; i < cabinet.leaves.Length; i++) cabinet.leaves[i].localRotation = Quaternion.Euler(0, cabinet.openAngles[i] * step / 60f, 0) * rotations[i];
                                Physics.SyncTransforms();
                                foreach (var leaf in cabinet.leaves)
                                {
                                    var box = leaf.GetComponent<BoxCollider>();
                                    foreach (var other in Physics.OverlapBox(box.bounds.center, box.bounds.extents, Quaternion.identity, GameLayers.Mask(GameLayers.Player, GameLayers.Enemy, GameLayers.DynamicProp, GameLayers.WorldStatic), QueryTriggerInteraction.Ignore))
                                    {
                                        if (other.transform.IsChildOf(cabinet.transform)) continue;
                                        Vector3 direction; float depth;
                                        if (Physics.ComputePenetration(box, box.transform.position, box.transform.rotation, other, other.transform.position, other.transform.rotation, out direction, out depth) && depth > .002f)
                                            obstacles.Add(other.name + " depth=" + depth.ToString("F3"));
                                    }
                                }
                            }
                            rows.Add("sweep: " + (obstacles.Count == 0 ? "clear" : string.Join(", ", obstacles.OrderBy(s => s))));
                            if (capture)
                            {
                                string name = cabinet.name + "_open";
                                var pos = cabinet.transform.TransformPoint(new Vector3(1.7f, 1.6f, -2.7f));
                                var target = cabinet.transform.TransformPoint(Vector3.up * .92f);
                                string image = S1VisualPass.Capture(name, pos, target);
                                File.Copy(image, Path.Combine(dir, name + ".png"), true);
                            }
                        }
                        finally
                        {
                            for (int i = 0; i < cabinet.leaves.Length; i++) cabinet.leaves[i].localRotation = rotations[i];
                            Physics.SyncTransforms();
                        }
                    }
                }
                finally { if (opened) EditorSceneManager.CloseScene(scene, true); }
            }
            if (previous.IsValid() && previous.isLoaded) SceneManager.SetActiveScene(previous);
            string result = string.Join("\n", rows); File.WriteAllText(Path.Combine(dir, "placements-audit.txt"), result); return result;
        }
    }
}
