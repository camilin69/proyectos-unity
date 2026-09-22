using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;

namespace Esneider.EditorTools
{
    // Source-only swivel contract. Regional pan/servo must be explicitly authored later.
    public static class SurveillanceCameraReview
    {
        public static readonly string[] Assets = { "OBJ-061_CamaraVigilancia", "OBJ-061B_CamaraVigilanciaDanada" };
        public static string Integrate(string asset)
        {
            if (!Assets.Contains(asset)) throw new ArgumentException("Unknown surveillance asset");
            var folder = FurnitureReview.Evidence(asset);
            var geometry = JsonUtility.FromJson<FurnitureReview.Geometry>(File.ReadAllText(Path.Combine(folder, "geometry.json")));
            foreach (var suffix in new[] { "BaseColor", "Normal", "Metallic", "Roughness" })
                if (!File.Exists(AssetIntegrator.TexDir + "/" + asset + "_" + suffix + ".png")) throw new InvalidOperationException("Missing camera map " + suffix);
            var report = AssetIntegrator.Integrate(asset, "Environment", false, "none");
            if (report.tris != geometry.triangles || report.tris > 2000 || report.submeshes != 2 || report.warnings.Count > 0)
                throw new InvalidOperationException("Camera topology or import mismatch");
            var axes = FurnitureReview.VerifyAxes(asset);
            if (axes.signX != 1 || axes.signZ != 1) throw new InvalidOperationException("Unexpected camera axes");
            var root = PrefabUtility.LoadPrefabContents(FurnitureReview.Prefab(asset));
            try
            {
                if (PrefabUtility.IsAnyPrefabInstanceRoot(root))
                    PrefabUtility.UnpackPrefabInstance(root, PrefabUnpackMode.Completely, InteractionMode.AutomatedAction);
                var head = root.GetComponentsInChildren<MeshFilter>().Single(m => m.name.Contains("-Head")).transform;
                var mount = root.GetComponentsInChildren<MeshFilter>().Single(m => m.name.Contains("-Mount")).transform;
                var sourcePivot = new Vector3(0, .09f, .055f);
                if (Vector3.Distance(head.position, sourcePivot) > .0002f) throw new InvalidOperationException("Camera pivot differs from source");
                var swivel = new GameObject("SwivelPivot").transform;
                swivel.SetParent(root.transform, false); swivel.localPosition = sourcePivot;
                head.SetParent(swivel, true);
                // Keep the maintained head ready for an authored rotation, with no behaviour by default.
                foreach (var t in root.GetComponentsInChildren<Transform>())
                { t.gameObject.layer = Esneider.Core.GameLayers.WorldStatic; t.gameObject.isStatic = false; }
                mount.gameObject.isStatic = true;
                PrefabUtility.SaveAsPrefabAsset(root, FurnitureReview.Prefab(asset));
            }
            finally { PrefabUtility.UnloadPrefabContents(root); }
            File.WriteAllText(Path.Combine(folder, "unity_import.json"), JsonUtility.ToJson(report, true));
            AssetDatabase.SaveAssets();
            return asset + ": " + report.tris + " triangles, two meshes, one shared atlas, swivel verified";
        }
    }
}
