using System;
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEngine;
using Object = UnityEngine.Object;

namespace Esneider.EditorTools
{
    public static class RemainingModelsReview
    {
        public static readonly string[] Assets = {
            "OBJ-015_PulseraLazaro", "OBJ-042_CierreContencion", "OBJ-071_EsclusaPresion",
            "OBJ-073_ConsolaPrincipal", "OBJ-075_BarandaPasarela", "OBJ-077_PanelEscape",
            "OBJ-078_CompuertaMonumental", "OBJ-080_ArchivoFisico", "ENV-EXIT_ExteriorEscape"
        };

        public static string IntegrateAll()
        {
            var results = new List<string>();
            foreach (string asset in Assets)
            {
                string fbx = AssetIntegrator.ModelsDir + "/" + asset + ".fbx";
                AssetDatabase.ImportAsset(fbx, ImportAssetOptions.ForceUpdate);
                var importer = (ModelImporter)AssetImporter.GetAtPath(fbx);
                importer.useFileScale = true; importer.globalScale = 1; importer.bakeAxisConversion = true;
                importer.importNormals = ModelImporterNormals.Import; importer.importTangents = ModelImporterTangents.CalculateMikk;
                importer.materialImportMode = ModelImporterMaterialImportMode.None; importer.isReadable = true;
                importer.importAnimation = false; importer.SaveAndReimport();
                var report = AssetIntegrator.Integrate(asset, "Environment", false, "none");
                if (report.tris <= 0 || report.size.sqrMagnitude <= .0001f) throw new InvalidOperationException("Invalid geometry: " + asset);
                string prefabPath = "Assets/_Game/Prefabs/Environment/" + asset + ".prefab";
                var root = PrefabUtility.LoadPrefabContents(prefabPath);
                try
                {
                    foreach (var c in root.GetComponentsInChildren<Collider>(true)) Object.DestroyImmediate(c);
                    if (asset != "OBJ-015_PulseraLazaro" && asset != "OBJ-080_ArchivoFisico")
                    {
                        var box = root.AddComponent<BoxCollider>();
                        box.center = new Vector3(0, report.size.y * .5f, 0); box.size = report.size;
                    }
                    PrefabUtility.SaveAsPrefabAsset(root, prefabPath);
                }
                finally { PrefabUtility.UnloadPrefabContents(root); }
                string folder = Path.GetFullPath(Path.Combine(Application.dataPath, "../../SourceArt/_evidence/EX-50/" + asset));
                Directory.CreateDirectory(folder); File.WriteAllText(Path.Combine(folder, "unity_import.json"), JsonUtility.ToJson(report, true));
                results.Add(asset + ":" + report.tris);
            }
            AssetDatabase.SaveAssets(); return string.Join(" | ", results);
        }
    }
}
