using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;

namespace Esneider.EditorTools
{
    public static class RepairArmReview
    {
        public const string Asset = "OBJ-020_BrazoReparacion";
        public static string Integrate()
        {
            var folder = FurnitureReview.Evidence(Asset);
            var geometry = JsonUtility.FromJson<FurnitureReview.Geometry>(File.ReadAllText(Path.Combine(folder, "geometry.json")));
            var report = AssetIntegrator.Integrate(Asset, "Environment", false, "none");
            if (report.tris != geometry.triangles || report.tris > 6000 || report.submeshes != 4 || report.warnings.Count > 0)
                throw new InvalidOperationException("Repair arm topology mismatch");
            var axes = FurnitureReview.VerifyAxes(Asset);
            if (axes.signX != 1 || axes.signZ != 1) throw new InvalidOperationException("Unexpected repair arm axes");
            var root = PrefabUtility.LoadPrefabContents(FurnitureReview.Prefab(Asset));
            try
            {
                if (PrefabUtility.IsAnyPrefabInstanceRoot(root))
                    PrefabUtility.UnpackPrefabInstance(root, PrefabUnpackMode.Completely, InteractionMode.AutomatedAction);
                var meshes = root.GetComponentsInChildren<MeshFilter>();
                var upper = meshes.Single(m => m.name.Contains("020-Upper")).transform;
                var forearm = meshes.Single(m => m.name.Contains("020-Forearm")).transform;
                var tool = meshes.Single(m => m.name.Contains("020-Tool")).transform;
                var shoulder = Joint(root.transform, upper, "ShoulderPivot", new Vector3(0, .56f, 0));
                var elbow = Joint(shoulder, forearm, "ElbowPivot", new Vector3(.72f, 1.22f, 0));
                var wrist = Joint(elbow, tool, "WristPivot", new Vector3(1.42f, .95f, 0));
                var contact = new GameObject("ToolContact").transform;
                contact.SetParent(wrist, false); contact.position = new Vector3(1.535f, .631f, 0);
                var box = root.AddComponent<BoxCollider>();
                box.center = new Vector3(0, .315f, 0); box.size = new Vector3(.48f, .63f, .48f);
                foreach (var t in root.GetComponentsInChildren<Transform>())
                { t.gameObject.layer = Esneider.Core.GameLayers.WorldStatic; t.gameObject.isStatic = false; }
                root.AddComponent<Esneider.World.SurfaceTag>().surfaceId = "SUR-MET";
                PrefabUtility.SaveAsPrefabAsset(root, FurnitureReview.Prefab(Asset));
            }
            finally { PrefabUtility.UnloadPrefabContents(root); }
            File.WriteAllText(Path.Combine(folder, "unity_import.json"), JsonUtility.ToJson(report, true));
            AssetDatabase.SaveAssets();
            return Asset + ": " + report.tris + " triangles; three verified joint pivots";
        }
        static Transform Joint(Transform parent, Transform mesh, string name, Vector3 position)
        {
            if (Vector3.Distance(mesh.position, position) > .001f)
                throw new InvalidOperationException("Unexpected source pivot: " + mesh.name);
            var joint = new GameObject(name).transform;
            joint.SetParent(parent, false); joint.position = position;
            mesh.SetParent(joint, true);
            return joint;
        }
    }
}
