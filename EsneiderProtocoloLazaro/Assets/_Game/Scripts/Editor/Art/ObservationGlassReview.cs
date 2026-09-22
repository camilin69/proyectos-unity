using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

namespace Esneider.EditorTools
{
    public static class ObservationGlassReview
    {
        public const string Asset = "OBJ-060_VidrioObservacion";
        public static string Integrate()
        {
            var report = AssetIntegrator.Integrate(Asset, "Environment", false, "none");
            if (report.tris != 924 || report.tris > 1000 || report.submeshes != 2 || report.warnings.Count > 0)
                throw new InvalidOperationException("Unexpected observation window topology");
            FurnitureReview.VerifyAxes(Asset);
            string texturePath = AssetIntegrator.TexDir + "/" + Asset + "_Glazing.png";
            var importer = (TextureImporter)AssetImporter.GetAtPath(texturePath);
            importer.alphaSource = TextureImporterAlphaSource.FromInput; importer.alphaIsTransparency = true;
            importer.wrapMode = TextureWrapMode.Clamp; importer.maxTextureSize = 512; importer.SaveAndReimport();
            string materialPath = AssetIntegrator.MatDir + "/M_" + Asset + "_Glass.mat";
            var glass = AssetDatabase.LoadAssetAtPath<Material>(materialPath);
            if (!glass) { glass = new Material(Shader.Find("Universal Render Pipeline/Lit")); AssetDatabase.CreateAsset(glass, materialPath); }
            glass.SetTexture("_BaseMap", AssetDatabase.LoadAssetAtPath<Texture2D>(texturePath)); glass.SetColor("_BaseColor", Color.white);
            glass.SetFloat("_Metallic", 0); glass.SetFloat("_Smoothness", .88f);
            glass.SetFloat("_Surface", 1); glass.SetFloat("_Blend", 0);
            glass.SetFloat("_SrcBlend", (float)BlendMode.SrcAlpha); glass.SetFloat("_DstBlend", (float)BlendMode.OneMinusSrcAlpha);
            glass.SetFloat("_SrcBlendAlpha", (float)BlendMode.One); glass.SetFloat("_DstBlendAlpha", (float)BlendMode.OneMinusSrcAlpha);
            glass.SetFloat("_ZWrite", 0); glass.SetFloat("_Cull", (float)CullMode.Back);
            glass.EnableKeyword("_SURFACE_TYPE_TRANSPARENT"); glass.DisableKeyword("_ALPHATEST_ON"); glass.DisableKeyword("_ALPHAPREMULTIPLY_ON");
            glass.SetOverrideTag("RenderType", "Transparent"); glass.renderQueue = 3000;
            glass.SetShaderPassEnabled("ShadowCaster", false); EditorUtility.SetDirty(glass);
            var root = PrefabUtility.LoadPrefabContents(FurnitureReview.Prefab(Asset));
            try
            {
                if (PrefabUtility.IsAnyPrefabInstanceRoot(root)) PrefabUtility.UnpackPrefabInstance(root, PrefabUnpackMode.Completely, InteractionMode.AutomatedAction);
                var pane = root.GetComponentsInChildren<MeshRenderer>().Single(r => r.name.Contains("060-Pane"));
                pane.sharedMaterial = glass; pane.shadowCastingMode = ShadowCastingMode.Off;
                var box = root.AddComponent<BoxCollider>(); box.center = new Vector3(0, 1.25f, 0); box.size = new Vector3(4, 2.5f, .15f);
                root.AddComponent<Esneider.World.SurfaceTag>().surfaceId = "SUR-GLS";
                foreach (var t in root.GetComponentsInChildren<Transform>()) { t.gameObject.layer = Esneider.Core.GameLayers.WorldStatic; t.gameObject.isStatic = true; }
                PrefabUtility.SaveAsPrefabAsset(root, FurnitureReview.Prefab(Asset));
            }
            finally { PrefabUtility.UnloadPrefabContents(root); }
            File.WriteAllText(Path.Combine(FurnitureReview.Evidence(Asset), "unity_import.json"), JsonUtility.ToJson(report, true));
            AssetDatabase.SaveAssets(); return Asset + ": 924 tris, opaque frame and transparent thick pane";
        }
        public static string Apply(Transform root, string region)
        {
            if (region != "REG-S3") return "";
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(FurnitureReview.Prefab(Asset)); if (!prefab) return "";
            var all = root.GetComponentsInChildren<Transform>(true);
            if (all.Any(t => t.name == "M060_Observation_EX41")) return "";
            var old = all.Single(t => t.name == "M060_vidrio");
            var bounds = old.GetComponent<Renderer>().bounds;
            if (Mathf.Abs(bounds.size.x - 8) > .01f || Mathf.Abs(bounds.size.y - 2.5f) > .01f) throw new InvalidOperationException("M060 footprint changed");
            var wrapper = new GameObject("M060_Observation_EX41").transform; wrapper.SetParent(old.parent, false);
            wrapper.position = new Vector3(bounds.center.x, bounds.min.y, bounds.center.z);
            foreach (float x in new[] { -2f, 2f })
            {
                var instance = (GameObject)PrefabUtility.InstantiatePrefab(prefab, wrapper);
                instance.transform.localPosition = new Vector3(x, 0, 0); instance.transform.localRotation = Quaternion.identity; instance.transform.localScale = Vector3.one;
            }
            old.gameObject.SetActive(false);
            return "M060 replaced by two 4m observation modules";
        }
        public static string ApplyExisting()
        {
            var previous = SceneManager.GetActiveScene(); const string path = "Assets/_Game/Scenes/Regions/REG-S3.unity";
            var scene = SceneManager.GetSceneByPath(path); bool opened = !scene.IsValid() || !scene.isLoaded;
            if (opened) scene = EditorSceneManager.OpenScene(path, OpenSceneMode.Additive); else if (scene.isDirty) throw new InvalidOperationException("Unsaved REG-S3");
            try { var result = Apply(scene.GetRootGameObjects().Single(g => g.name == "REG-S3").transform, "REG-S3"); if (result != "") EditorSceneManager.SaveScene(scene); return result; }
            finally { if (opened) EditorSceneManager.CloseScene(scene, true); if (previous.IsValid() && previous.isLoaded) SceneManager.SetActiveScene(previous); }
        }
    }
}
