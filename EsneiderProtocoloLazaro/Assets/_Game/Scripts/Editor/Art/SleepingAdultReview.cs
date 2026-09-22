using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.Animations;
using UnityEngine;
using Object = UnityEngine.Object;

namespace Esneider.EditorTools
{
    public static class SleepingAdultReview
    {
        public const string Asset = "HUM-01_AdultoDormido";
        public const string Prefab = "Assets/_Game/Prefabs/Environment/HUM-01_AdultoDormido.prefab";
        public const string Assembly = "Assets/_Game/Prefabs/Environment/HUM-01_CamillaDormido.prefab";
        public static string Apply(Transform regionRoot, string region)
        {
            if (region != "REG-S3") return "";
            var model = AssetDatabase.LoadAssetAtPath<GameObject>(Assembly); if (!model) return "";
            var cage = regionRoot.GetComponentsInChildren<Transform>(true).Single(t => t.name == "M041_jaula");
            if (cage.Find("M041_SleepingAdult_EX44")) return "";
            var old = cage.Find("Sujeto_placeholder_M041");
            if (!old) throw new InvalidOperationException("M041 subject placeholder missing");
            var wrapper = new GameObject("M041_SleepingAdult_EX44").transform; wrapper.SetParent(cage, false); wrapper.localPosition = new Vector3(0, 0, .6f);
            var instance = (GameObject)PrefabUtility.InstantiatePrefab(model, wrapper); instance.transform.localPosition = Vector3.zero; instance.transform.localRotation = Quaternion.identity;
            var subject = instance.GetComponentInChildren<Esneider.World.SleepingSubject>(); subject.phaseOffset = .17f; PrefabUtility.RecordPrefabInstancePropertyModifications(subject);
            old.gameObject.SetActive(false); return "M041 capsule replaced by sleeping adult on supported camilla";
        }
        public static string ApplyExisting()
        {
            var previous = UnityEngine.SceneManagement.SceneManager.GetActiveScene(); const string path = "Assets/_Game/Scenes/Regions/REG-S3.unity";
            var scene = UnityEngine.SceneManagement.SceneManager.GetSceneByPath(path); bool opened = !scene.IsValid() || !scene.isLoaded;
            if (opened) scene = UnityEditor.SceneManagement.EditorSceneManager.OpenScene(path, UnityEditor.SceneManagement.OpenSceneMode.Additive);
            else if (scene.isDirty) throw new InvalidOperationException("Unsaved REG-S3");
            try { var result = Apply(scene.GetRootGameObjects().Single(g => g.name == "REG-S3").transform, "REG-S3"); if (result != "") UnityEditor.SceneManagement.EditorSceneManager.SaveScene(scene); return result; }
            finally { if (opened) UnityEditor.SceneManagement.EditorSceneManager.CloseScene(scene, true); if (previous.IsValid() && previous.isLoaded) UnityEngine.SceneManagement.SceneManager.SetActiveScene(previous); }
        }
        public static string Assemble()
        {
            FurnitureReview.Integrate("HUM-01_ApoyosCamilla");
            BlanketReview.Integrate();
            var root = new GameObject("HUM-01_CamillaDormido");
            try
            {
                var bed = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(FurnitureReview.Prefab("OBJ-043_Camilla")), root.transform);
                var legacyBlanket = bed.GetComponentsInChildren<Renderer>().Single(r => r.name == "blanket"); legacyBlanket.enabled = false;
                PrefabUtility.RecordPrefabInstancePropertyModifications(legacyBlanket);
                PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(FurnitureReview.Prefab("HUM-01_ApoyosCamilla")), root.transform);
                var subject = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(Prefab), root.transform);
                subject.transform.localRotation = Quaternion.LookRotation(Vector3.down, Vector3.left);
                subject.transform.localPosition = new Vector3(.90f, .95f, 0); subject.transform.localScale = Vector3.one;
                PrefabUtility.RecordPrefabInstancePropertyModifications(subject.transform);
                var weightedBlanket = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(BlanketReview.Prefab), root.transform);
                weightedBlanket.transform.localPosition = Vector3.zero; weightedBlanket.transform.localRotation = Quaternion.identity;
                var phase = weightedBlanket.GetComponent<Esneider.World.AmbientLoopPhase>(); phase.phaseOffset = .17f;
                PrefabUtility.RecordPrefabInstancePropertyModifications(phase);
                PrefabUtility.SaveAsPrefabAsset(root, Assembly); return "Subject on camilla with anatomical supports and weighted breathing blanket";
            }
            finally { Object.DestroyImmediate(root); }
        }
        public static string Integrate()
        {
            string fbx = AssetIntegrator.ModelsDir + "/" + Asset + ".fbx";
            AssetDatabase.ImportAsset(fbx, ImportAssetOptions.ForceUpdate);
            var importer = (ModelImporter)AssetImporter.GetAtPath(fbx);
            importer.useFileScale = true; importer.globalScale = 1; importer.bakeAxisConversion = true;
            importer.importNormals = ModelImporterNormals.Import; importer.importTangents = ModelImporterTangents.CalculateMikk;
            importer.materialImportMode = ModelImporterMaterialImportMode.None; importer.animationType = ModelImporterAnimationType.Generic;
            importer.importAnimation = true; importer.optimizeGameObjects = false; importer.isReadable = true; importer.SaveAndReimport();
            var clips = importer.defaultClipAnimations; foreach (var c in clips) c.loopTime = true; importer.clipAnimations = clips; importer.SaveAndReimport();
            var report = new AssetIntegrator.Report { asset = Asset, fbx = fbx, prefab = Prefab };
            var skin = AssetIntegrator.BuildMaterial(Asset + "_Skin", report); var cloth = AssetIntegrator.BuildMaterial(Asset + "_Cloth", report);
            skin.SetFloat("_BumpScale", .25f); skin.SetFloat("_Smoothness", .65f); EditorUtility.SetDirty(skin);
            cloth.SetFloat("_BumpScale", .5f); EditorUtility.SetDirty(cloth);
            if (report.warnings.Count > 0) throw new InvalidOperationException(string.Join("; ", report.warnings));
            var model = AssetDatabase.LoadAssetAtPath<GameObject>(fbx); var instance = (GameObject)PrefabUtility.InstantiatePrefab(model);
            try
            {
                PrefabUtility.UnpackPrefabInstance(instance, PrefabUnpackMode.Completely, InteractionMode.AutomatedAction);
                var renderers = instance.GetComponentsInChildren<SkinnedMeshRenderer>();
                if (renderers.Length != 2) throw new InvalidOperationException("Expected separate skin and clothing");
                foreach (var r in renderers)
                {
                    r.sharedMaterial = r.name.Contains("Skin") ? skin : cloth; r.updateWhenOffscreen = false;
                    report.tris += r.sharedMesh.triangles.Length / 3; report.submeshes += r.sharedMesh.subMeshCount;
                    if (r.sharedMesh.boneWeights.Any(w => w.weight0 + w.weight1 + w.weight2 + w.weight3 < .999f)) throw new InvalidOperationException("Unweighted subject vertex");
                }
                if (report.tris > 20000 || report.submeshes != 2) throw new InvalidOperationException("Subject exceeds budget");
                var clip = AssetDatabase.LoadAllAssetsAtPath(fbx).OfType<AnimationClip>().Single(c => !c.name.StartsWith("__preview") && c.name.Contains("Sleep_Breathe"));
                if (clip.length < 4.9f || clip.length > 5.1f) throw new InvalidOperationException("Unexpected breathing duration");
                string controllerPath = "Assets/_Game/Art/HUM01_Sleep.controller";
                var controller = AssetDatabase.LoadAssetAtPath<AnimatorController>(controllerPath);
                if (!controller) controller = AnimatorController.CreateAnimatorControllerAtPath(controllerPath);
                var machine = controller.layers[0].stateMachine;
                foreach (var state in machine.states) machine.RemoveState(state.state);
                var sleep = machine.AddState("Sleep"); sleep.motion = clip; machine.defaultState = sleep;
                var animator = instance.GetComponent<Animator>(); if (!animator) animator = instance.AddComponent<Animator>();
                animator.runtimeAnimatorController = controller; animator.applyRootMotion = false; animator.cullingMode = AnimatorCullingMode.CullUpdateTransforms;
                var subject = instance.AddComponent<Esneider.World.SleepingSubject>(); subject.animator = animator;
                foreach (var t in instance.GetComponentsInChildren<Transform>()) { t.gameObject.isStatic = false; t.gameObject.layer = Esneider.Core.GameLayers.Corpse; }
                PrefabUtility.SaveAsPrefabAsset(instance, Prefab);
                report.clips = 1; report.clipNames.Add(clip.name); report.materials.Add(skin.name); report.materials.Add(cloth.name);
                File.WriteAllText(Path.Combine(FurnitureReview.Evidence(Asset), "unity_import.json"), JsonUtility.ToJson(report, true));
                AssetDatabase.SaveAssets(); return report.tris + " tris, two skinned meshes, 5-second breathing clip";
            }
            finally { Object.DestroyImmediate(instance); }
        }
    }
}
