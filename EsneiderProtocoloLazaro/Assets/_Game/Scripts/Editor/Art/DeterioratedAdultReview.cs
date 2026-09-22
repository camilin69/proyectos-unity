using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.Animations;
using UnityEngine;
using Object = UnityEngine.Object;

namespace Esneider.EditorTools
{
    public static class DeterioratedAdultReview
    {
        public const string Asset = "HUM-03_AdultoDeteriorado";
        public const string Support = "HUM-03_SoporteLateral";
        public const string Prefab = "Assets/_Game/Prefabs/Environment/HUM-03_AdultoDeteriorado.prefab";
        public const string Assembly = "Assets/_Game/Prefabs/Environment/HUM-03_SujetoLateral.prefab";

        public static string Integrate()
        {
            string fbx = AssetIntegrator.ModelsDir + "/" + Asset + ".fbx";
            AssetDatabase.ImportAsset(fbx, ImportAssetOptions.ForceUpdate);
            var importer = (ModelImporter)AssetImporter.GetAtPath(fbx);
            importer.useFileScale = true; importer.globalScale = 1; importer.bakeAxisConversion = true;
            importer.importNormals = ModelImporterNormals.Import;
            importer.importTangents = ModelImporterTangents.CalculateMikk;
            importer.materialImportMode = ModelImporterMaterialImportMode.None;
            importer.animationType = ModelImporterAnimationType.Generic;
            importer.importAnimation = true; importer.optimizeGameObjects = false; importer.isReadable = true;
            importer.SaveAndReimport();
            var clips = importer.defaultClipAnimations;
            foreach (var c in clips) c.loopTime = true;
            importer.clipAnimations = clips; importer.SaveAndReimport();
            var report = new AssetIntegrator.Report { asset = Asset, fbx = fbx, prefab = Prefab };
            var skin = AssetIntegrator.BuildMaterial(Asset + "_Skin", report);
            var cloth = AssetIntegrator.BuildMaterial(Asset + "_Cloth", report);
            skin.SetFloat("_BumpScale", .22f); skin.SetFloat("_Smoothness", .55f);
            cloth.SetFloat("_BumpScale", .55f);
            EditorUtility.SetDirty(skin); EditorUtility.SetDirty(cloth);
            if (report.warnings.Count > 0) throw new InvalidOperationException(string.Join("; ", report.warnings));
            var instance = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(fbx));
            try
            {
                PrefabUtility.UnpackPrefabInstance(instance, PrefabUnpackMode.Completely, InteractionMode.AutomatedAction);
                var renderers = instance.GetComponentsInChildren<SkinnedMeshRenderer>();
                if (renderers.Length != 2) throw new InvalidOperationException("Expected skin and cloth meshes");
                foreach (var r in renderers)
                {
                    r.sharedMaterial = r.name.Contains("Skin") ? skin : cloth; r.updateWhenOffscreen = false;
                    report.tris += r.sharedMesh.triangles.Length / 3; report.submeshes += r.sharedMesh.subMeshCount;
                    if (r.sharedMesh.boneWeights.Any(w => w.weight0 + w.weight1 + w.weight2 + w.weight3 < .999f))
                        throw new InvalidOperationException("Unweighted subject vertex");
                }
                if (report.tris > 20000 || report.submeshes != 2) throw new InvalidOperationException("Subject exceeds budget");
                var clip = AssetDatabase.LoadAllAssetsAtPath(fbx).OfType<AnimationClip>()
                    .Single(c => !c.name.StartsWith("__preview") && c.name.Contains("Side_Breathe"));
                if (clip.length < 6.9f || clip.length > 7.1f) throw new InvalidOperationException("Unexpected ambient clip duration");
                const string controllerPath = "Assets/_Game/Art/HUM03_Side.controller";
                var controller = AssetDatabase.LoadAssetAtPath<AnimatorController>(controllerPath);
                if (!controller) controller = AnimatorController.CreateAnimatorControllerAtPath(controllerPath);
                var machine = controller.layers[0].stateMachine;
                foreach (var state in machine.states) machine.RemoveState(state.state);
                var idle = machine.AddState("Side breathing"); idle.motion = clip; machine.defaultState = idle;
                var animator = instance.GetComponent<Animator>(); if (!animator) animator = instance.AddComponent<Animator>();
                animator.runtimeAnimatorController = controller; animator.applyRootMotion = false;
                animator.cullingMode = AnimatorCullingMode.CullUpdateTransforms;
                var subject = instance.AddComponent<Esneider.World.PreservedSubject>(); subject.animator = animator;
                foreach (var t in instance.GetComponentsInChildren<Transform>())
                {
                    t.gameObject.isStatic = false; t.gameObject.layer = Esneider.Core.GameLayers.Corpse;
                }
                PrefabUtility.SaveAsPrefabAsset(instance, Prefab);
                report.clips = 1; report.clipNames.Add(clip.name); report.materials.Add(skin.name); report.materials.Add(cloth.name);
                File.WriteAllText(Path.Combine(FurnitureReview.Evidence(Asset), "unity_import.json"), JsonUtility.ToJson(report, true));
                AssetDatabase.SaveAssets(); return report.tris + " tris, two skinned meshes, seven-second side loop";
            }
            finally { Object.DestroyImmediate(instance); }
        }

        public static string Assemble()
        {
            FurnitureReview.Integrate(Support);
            var root = new GameObject("HUM-03_SujetoLateral");
            try
            {
                var rack = (GameObject)PrefabUtility.InstantiatePrefab(
                    AssetDatabase.LoadAssetAtPath<GameObject>(FurnitureReview.Prefab(Support)), root.transform);
                rack.transform.localRotation = Quaternion.Euler(0, 90f, 0);
                var human = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(Prefab), root.transform);
                // Local left side points down; head points along +Z and face toward the west aisle.
                human.transform.localRotation = Quaternion.LookRotation(Vector3.right, Vector3.forward);
                human.transform.localPosition = new Vector3(0, .50f, -.87f);
                var subject = human.GetComponent<Esneider.World.PreservedSubject>(); subject.phaseOffset = .32f;
                PrefabUtility.RecordPrefabInstancePropertyModifications(subject);
                PrefabUtility.SaveAsPrefabAsset(root, Assembly);
                return "Atrophied adult placed on left side over a fitted low support";
            }
            finally { Object.DestroyImmediate(root); }
        }

        public static string Apply(Transform regionRoot, string region)
        {
            if (region != "REG-S3") return "";
            var model = AssetDatabase.LoadAssetAtPath<GameObject>(Assembly); if (!model) return "";
            var cage = regionRoot.GetComponentsInChildren<Transform>(true).Single(t => t.name == "M046_jaula");
            if (cage.Find("M046_DeterioratedAdult_EX46")) return "";
            var old = cage.Find("Sujeto_placeholder_M046");
            if (!old) throw new InvalidOperationException("M046 subject placeholder missing");
            var wrapper = new GameObject("M046_DeterioratedAdult_EX46").transform;
            wrapper.SetParent(cage, false); wrapper.localPosition = new Vector3(0, 0, .6f);
            var instance = (GameObject)PrefabUtility.InstantiatePrefab(model, wrapper);
            instance.transform.localPosition = Vector3.zero; instance.transform.localRotation = Quaternion.identity;
            old.gameObject.SetActive(false);
            return "M046 capsule replaced by side-lying deteriorated adult";
        }

        public static string ApplyExisting()
        {
            var previous = UnityEngine.SceneManagement.SceneManager.GetActiveScene();
            const string path = "Assets/_Game/Scenes/Regions/REG-S3.unity";
            var scene = UnityEngine.SceneManagement.SceneManager.GetSceneByPath(path);
            bool opened = !scene.IsValid() || !scene.isLoaded;
            if (opened) scene = UnityEditor.SceneManagement.EditorSceneManager.OpenScene(path, UnityEditor.SceneManagement.OpenSceneMode.Additive);
            else if (scene.isDirty) throw new InvalidOperationException("Unsaved REG-S3");
            try
            {
                var result = Apply(scene.GetRootGameObjects().Single(g => g.name == "REG-S3").transform, "REG-S3");
                if (result != "") UnityEditor.SceneManagement.EditorSceneManager.SaveScene(scene);
                return result;
            }
            finally
            {
                if (opened) UnityEditor.SceneManagement.EditorSceneManager.CloseScene(scene, true);
                if (previous.IsValid() && previous.isLoaded) UnityEngine.SceneManagement.SceneManager.SetActiveScene(previous);
            }
        }
    }
}
