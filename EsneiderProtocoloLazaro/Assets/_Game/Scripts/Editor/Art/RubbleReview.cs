using System;
using System.IO;
using System.Linq;
using Esneider.Core;
using Esneider.World;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using Object = UnityEngine.Object;

namespace Esneider.EditorTools
{
    public static class RubbleReview
    {
        public const string Asset = "OBJ-012_EscombrosConcreto";
        public static string Integrate()
        {
            var geo = JsonUtility.FromJson<FurnitureReview.Geometry>(File.ReadAllText(Path.Combine(FurnitureReview.Evidence(Asset), "geometry.json")));
            var report = AssetIntegrator.Integrate(Asset, "Environment", false, "none");
            if (report.tris != geo.triangles || report.submeshes != 3 || report.warnings.Count > 0) throw new InvalidOperationException("Rubble import differs from source");
            var axes = FurnitureReview.VerifyAxes(Asset);
            var root = PrefabUtility.LoadPrefabContents(FurnitureReview.Prefab(Asset));
            try
            {
                foreach (var box in geo.collision_boxes_blender)
                {
                    var c = root.AddComponent<BoxCollider>();
                    c.center = new Vector3(axes.signX * box.center[0], box.center[2], axes.signZ * box.center[1]);
                    c.size = new Vector3(box.size[0], box.size[2], box.size[1]);
                }
                foreach (var t in root.GetComponentsInChildren<Transform>()) { t.gameObject.layer = GameLayers.WorldStatic; t.gameObject.isStatic = false; }
                root.AddComponent<SurfaceTag>().surfaceId = "SUR-RUB";
                var extraction = root.AddComponent<RubbleExtraction>();
                extraction.chips = root.GetComponentsInChildren<Transform>().Where(t => t.name.Contains("Loose")).OrderBy(t => t.name).ToArray();
                if (extraction.chips.Length != 2) throw new InvalidOperationException("Expected two independent rubble chips");
                foreach (var t in extraction.chips) t.gameObject.layer = GameLayers.VFX;
                PrefabUtility.SaveAsPrefabAsset(root, FurnitureReview.Prefab(Asset));
            }
            finally { PrefabUtility.UnloadPrefabContents(root); }
            File.WriteAllText(Path.Combine(FurnitureReview.Evidence(Asset), "unity_import.json"), JsonUtility.ToJson(report, true));
            return Asset + ": " + report.tris + " tris, 3 meshes, two movable chips";
        }

        public static string Apply(Transform root)
        {
            var all = root.GetComponentsInChildren<Transform>(true);
            var old = all.FirstOrDefault(t => t.name == "M013_cascote");
            if (!old) return "";
            var pickup = all.Single(t => t.name == "Pickup_PICK-W01");
            var support = all.Single(t => t.name == "Support_PICK-W01");
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(FurnitureReview.Prefab(Asset));
            if (!prefab) return "Rubble prefab pending";
            var placed = (GameObject)PrefabUtility.InstantiatePrefab(prefab, old.parent);
            placed.name = "M013_EX20"; placed.transform.position = old.position - Vector3.up * .55f;
            var extraction = placed.GetComponent<RubbleExtraction>(); extraction.pickupGuid = pickup.GetComponent<Pickup>().guid;
            var visible = pickup.Find("Visual");
            visible.localRotation = Quaternion.Euler(0, 0, 90);
            var renderers = visible.GetComponentsInChildren<Renderer>(); var bounds = renderers[0].bounds;
            foreach (var r in renderers.Skip(1)) bounds.Encapsulate(r.bounds);
            var chipCenter = (extraction.chips[0].position + extraction.chips[1].position) * .5f;
            pickup.position += new Vector3(chipCenter.x, chipCenter.y + .025f, chipCenter.z) - bounds.center;
            Object.DestroyImmediate(old.gameObject); Object.DestroyImmediate(support.gameObject);
            return "M013: rubble at " + placed.transform.position + "; PICK-W01 at " + pickup.position + "; guid=" + extraction.pickupGuid;
        }
        public static string ApplyExisting()
        {
            var s = SceneManager.GetActiveScene();
            if (s.name != "REG-S1" || s.isDirty) throw new InvalidOperationException("S1 must be loaded and clean");
            var root = s.GetRootGameObjects().Single(g => g.name == "REG-S1");
            var result = Apply(root.transform); EditorSceneManager.SaveScene(s);
            File.WriteAllText("../SourceArt/_evidence/EX-20/placement.txt", result); return result;
        }
    }
}
