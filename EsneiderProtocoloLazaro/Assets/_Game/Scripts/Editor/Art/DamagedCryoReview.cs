using System;
using System.IO;
using System.Linq;
using Esneider.Core;
using Esneider.Core.Persistence;
using Esneider.World;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using Object = UnityEngine.Object;

namespace Esneider.EditorTools
{
    public static class DamagedCryoReview
    {
        public const string Asset = "OBJ-002_CamaraVaciaDanada";
        public const string Prefab = "Assets/_Game/Prefabs/Environment/OBJ-002_CamaraVaciaDanada.prefab";
        public const string Evidence = "SourceArt/_evidence/EX-49/OBJ-002_CamaraVaciaDanada";

        public static string Integrate()
        {
            string fbx = AssetIntegrator.ModelsDir + "/" + Asset + ".fbx";
            AssetDatabase.ImportAsset(fbx, ImportAssetOptions.ForceUpdate);
            var importer = (ModelImporter)AssetImporter.GetAtPath(fbx);
            importer.useFileScale = true; importer.globalScale = 1; importer.bakeAxisConversion = true;
            importer.importNormals = ModelImporterNormals.Import; importer.importTangents = ModelImporterTangents.CalculateMikk;
            importer.materialImportMode = ModelImporterMaterialImportMode.None;
            importer.animationType = ModelImporterAnimationType.Generic; importer.importAnimation = true;
            importer.optimizeGameObjects = false; importer.isReadable = true; importer.SaveAndReimport();

            // Blender may suffix action names when the source-locked scene already
            // contains data-blocks with the same names. Keep stable Unity clip IDs.
            var importedClips = importer.defaultClipAnimations;
            foreach (var clip in importedClips)
            {
                if (clip.name.StartsWith("Cryo_Damaged_Jam", StringComparison.Ordinal)) clip.name = "Cryo_Damaged_Jam";
                if (clip.name.StartsWith("Cryo_Damaged_Rest", StringComparison.Ordinal)) clip.name = "Cryo_Damaged_Rest";
            }
            importer.clipAnimations = importedClips;
            importer.SaveAndReimport();

            var report = AssetIntegrator.Integrate(Asset, "Environment", false, "none");
            if (report.warnings.Count > 0) throw new InvalidOperationException(string.Join("; ", report.warnings));
            if (report.tris != 10676 || report.size.x < 2.7f || report.size.z < 1.1f) throw new InvalidOperationException("Unexpected damaged cryo geometry");
            var clips = AssetDatabase.LoadAllAssetsAtPath(fbx).OfType<AnimationClip>().Where(c => !c.name.StartsWith("__preview")).ToArray();
            var jam = clips.Single(c => c.name == "Cryo_Damaged_Jam");
            if (jam.length < 1.95f || jam.length > 2.05f) throw new InvalidOperationException("Unexpected jam clip length");

            var root = PrefabUtility.LoadPrefabContents(Prefab);
            try
            {
                foreach (var c in root.GetComponentsInChildren<Collider>(true)) Object.DestroyImmediate(c);
                var baseCollider = root.AddComponent<BoxCollider>(); baseCollider.center = new Vector3(0, .36f, 0);
                baseCollider.size = new Vector3(2.78f, .72f, 1.14f);
                var animator = root.GetComponent<Animator>(); if (!animator) animator = root.AddComponent<Animator>(); animator.applyRootMotion = false;
                var sequence = root.GetComponent<DamagedCryoSequence>(); if (!sequence) sequence = root.AddComponent<DamagedCryoSequence>();
                sequence.animator = animator; sequence.jamClip = jam; sequence.triggerDistance = 4.5f;
                foreach (var t in root.GetComponentsInChildren<Transform>(true)) t.gameObject.layer = GameLayers.WorldStatic;
                PrefabUtility.SaveAsPrefabAsset(root, Prefab);
            }
            finally { PrefabUtility.UnloadPrefabContents(root); }

            string outDir = Path.GetFullPath(Path.Combine(Application.dataPath, "../../" + Evidence)); Directory.CreateDirectory(outDir);
            File.WriteAllText(Path.Combine(outDir, "unity_import.json"), JsonUtility.ToJson(report, true));
            AssetDatabase.SaveAssets(); return report.tris + " tris, " + clips.Length + " clips, damaged cryo integrated";
        }

        public static string Apply(Transform regionRoot, string region)
        {
            if (region != "REG-S1") return "";
            var furniture = regionRoot.Find("Entities/Furniture"); if (!furniture) return "";
            var old = furniture.Find("M011_OBJ-001"); if (!old || furniture.Find("M011_OBJ-002")) return "";
            var model = AssetDatabase.LoadAssetAtPath<GameObject>(Prefab); if (!model) return "";
            var instance = (GameObject)PrefabUtility.InstantiatePrefab(model, furniture);
            instance.name = "M011_OBJ-002"; instance.transform.SetPositionAndRotation(old.position, old.rotation); instance.transform.localScale = old.localScale;
            var src = old.GetComponent<PersistentEntity>();
            if (src)
            {
                var dst = instance.GetComponent<PersistentEntity>() ?? instance.AddComponent<PersistentEntity>();
                dst.stableId = src.stableId; dst.guid = src.guid; dst.regionId = src.regionId; dst.prefabId = "OBJ-002"; dst.kind = src.kind;
            }
            Object.DestroyImmediate(old.gameObject); return "M011 replaced by damaged empty cryo chamber";
        }

        public static string ApplyExisting()
        {
            var previous = SceneManager.GetActiveScene(); const string path = "Assets/_Game/Scenes/Regions/REG-S1.unity";
            var scene = SceneManager.GetSceneByPath(path); bool opened = !scene.IsValid() || !scene.isLoaded;
            if (opened) scene = EditorSceneManager.OpenScene(path, OpenSceneMode.Additive); else if (scene.isDirty) throw new InvalidOperationException("Unsaved REG-S1");
            try
            {
                var result = Apply(scene.GetRootGameObjects().Single(g => g.name == "REG-S1").transform, "REG-S1");
                if (result != "") EditorSceneManager.SaveScene(scene); return result;
            }
            finally
            {
                if (opened) EditorSceneManager.CloseScene(scene, true);
                if (previous.IsValid() && previous.isLoaded) SceneManager.SetActiveScene(previous);
            }
        }
    }
}
