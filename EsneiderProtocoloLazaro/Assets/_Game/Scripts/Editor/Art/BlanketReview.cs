using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.Animations;
using UnityEngine;
using Object = UnityEngine.Object;

namespace Esneider.EditorTools
{
    public static class BlanketReview
    {
        public const string Asset = "OBJ-054_VendajesManta";
        public const string Prefab = "Assets/_Game/Prefabs/Environment/OBJ-054_VendajesManta.prefab";

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
            var clips = importer.defaultClipAnimations; foreach (var c in clips) c.loopTime = true;
            importer.clipAnimations = clips; importer.SaveAndReimport();
            var report = new AssetIntegrator.Report { asset = Asset, fbx = fbx, prefab = Prefab };
            var material = AssetIntegrator.BuildMaterial(Asset, report);
            material.SetFloat("_BumpScale", .55f); EditorUtility.SetDirty(material);
            if (report.warnings.Count > 0) throw new InvalidOperationException(string.Join("; ", report.warnings));
            var instance = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(fbx));
            try
            {
                PrefabUtility.UnpackPrefabInstance(instance, PrefabUnpackMode.Completely, InteractionMode.AutomatedAction);
                var renderer = instance.GetComponentInChildren<SkinnedMeshRenderer>();
                if (instance.GetComponentsInChildren<SkinnedMeshRenderer>().Length != 1) throw new InvalidOperationException("Expected one skinned blanket mesh");
                renderer.sharedMaterial = material; renderer.updateWhenOffscreen = false;
                report.tris = renderer.sharedMesh.triangles.Length / 3; report.submeshes = renderer.sharedMesh.subMeshCount;
                if (report.tris > 2000 || report.submeshes != 1) throw new InvalidOperationException("Blanket budget exceeded");
                if (renderer.sharedMesh.boneWeights.Any(w => w.weight0 + w.weight1 + w.weight2 + w.weight3 < .999f))
                    throw new InvalidOperationException("Unweighted blanket vertex");
                var clip = AssetDatabase.LoadAllAssetsAtPath(fbx).OfType<AnimationClip>()
                    .Single(c => !c.name.StartsWith("__preview") && c.name.Contains("Blanket_Breathe"));
                if (clip.length < 4.9f || clip.length > 5.1f) throw new InvalidOperationException("Unexpected blanket clip duration");
                const string controllerPath = "Assets/_Game/Art/OBJ054_Blanket.controller";
                var controller = AssetDatabase.LoadAssetAtPath<AnimatorController>(controllerPath);
                if (!controller) controller = AnimatorController.CreateAnimatorControllerAtPath(controllerPath);
                var machine = controller.layers[0].stateMachine;
                foreach (var state in machine.states) machine.RemoveState(state.state);
                var breathing = machine.AddState("Follow breathing"); breathing.motion = clip; machine.defaultState = breathing;
                var animator = instance.GetComponent<Animator>(); if (!animator) animator = instance.AddComponent<Animator>();
                animator.runtimeAnimatorController = controller; animator.applyRootMotion = false;
                animator.cullingMode = AnimatorCullingMode.CullUpdateTransforms;
                var phase = instance.AddComponent<Esneider.World.AmbientLoopPhase>(); phase.animator = animator;
                foreach (var t in instance.GetComponentsInChildren<Transform>())
                {
                    t.gameObject.isStatic = false; t.gameObject.layer = Esneider.Core.GameLayers.Corpse;
                }
                PrefabUtility.SaveAsPrefabAsset(instance, Prefab);
                report.clips = 1; report.clipNames.Add(clip.name); report.materials.Add(material.name);
                File.WriteAllText(Path.Combine(FurnitureReview.Evidence(Asset), "unity_import.json"), JsonUtility.ToJson(report, true));
                AssetDatabase.SaveAssets(); return report.tris + " tris, weighted blanket with five-second loop";
            }
            finally { Object.DestroyImmediate(instance); }
        }
    }
}
