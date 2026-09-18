using System.Collections.Generic;
using System.IO;
using System.Linq;
using Esneider.Core;
using UnityEditor;
using UnityEngine;

namespace Esneider.EditorTools
{
    // 24.1 pasos 8–9 / 94.3: importar FBX exportado desde Blender, reconstruir materiales URP con las texturas horneadas (41.1),
    // crear prefab con colliders simplificados y reportar tris/dimensiones/clips contra la ficha 90.
    public static class AssetIntegrator
    {
        public const string ModelsDir = "Assets/_Game/Art/Models";
        public const string TexDir = "Assets/_Game/Art/Textures";
        public const string MatDir = "Assets/_Game/Art/Materials/Assets";
        public const string PrefabDir = "Assets/_Game/Prefabs";

        [System.Serializable]
        public class Report { public string asset, fbx, prefab; public int tris, submeshes, clips; public Vector3 size; public List<string> clipNames = new List<string>(), materials = new List<string>(), warnings = new List<string>(); }

        public static Report Integrate(string assetId, string prefabSubdir, bool humanoid = false, string colliderKind = "capsule", Vector3? colliderSize = null)
        {
            var r = new Report { asset = assetId };
            string fbxPath = $"{ModelsDir}/{assetId}.fbx";
            AssetDatabase.ImportAsset(fbxPath, ImportAssetOptions.ForceUpdate);
            var importer = AssetImporter.GetAtPath(fbxPath) as ModelImporter;
            if (importer == null) { r.warnings.Add("FBX no encontrado: " + fbxPath); return r; }
            importer.useFileScale = true; importer.globalScale = 1f; importer.bakeAxisConversion = true; // raíz identidad: el visual se instancia como hijo sin rotación heredada
            importer.importNormals = ModelImporterNormals.Import; importer.importTangents = ModelImporterTangents.CalculateMikk;
            importer.materialImportMode = ModelImporterMaterialImportMode.None;
            importer.animationType = ModelImporterAnimationType.Generic; importer.importAnimation = true;
            importer.generateSecondaryUV = false;
            importer.SaveAndReimport();

            // texturas horneadas → material URP Lit (Metallic workflow; smoothness = 1 − roughness vía mapa MetallicSmoothness generado)
            Directory.CreateDirectory(MatDir);
            var mat = BuildMaterial(assetId, r);

            var model = AssetDatabase.LoadAssetAtPath<GameObject>(fbxPath);
            var clips = AssetDatabase.LoadAllAssetsAtPath(fbxPath).OfType<AnimationClip>().Where(c => !c.name.StartsWith("__preview")).ToList();
            r.clips = clips.Count; r.clipNames = clips.Select(c => c.name).ToList();
            foreach (var c in clips) { var s = AnimationUtility.GetAnimationClipSettings(c); s.loopTime = c.name.Contains("Idle") || c.name.Contains("Walk"); AnimationUtility.SetAnimationClipSettings(c, s); }

            var inst = (GameObject)PrefabUtility.InstantiatePrefab(model);
            inst.name = assetId;
            var bounds = new Bounds(inst.transform.position, Vector3.zero); bool first = true;
            foreach (var mr in inst.GetComponentsInChildren<Renderer>())
            {
                mr.sharedMaterials = Enumerable.Repeat(mat, mr.sharedMaterials.Length).ToArray();
                if (first) { bounds = mr.bounds; first = false; } else bounds.Encapsulate(mr.bounds);
                var mf = mr.GetComponent<MeshFilter>(); if (mf != null && mf.sharedMesh != null) { r.tris += mf.sharedMesh.triangles.Length / 3; r.submeshes += mf.sharedMesh.subMeshCount; }
                var smr = mr as SkinnedMeshRenderer; if (smr != null && smr.sharedMesh != null) { r.tris += smr.sharedMesh.triangles.Length / 3; r.submeshes += smr.sharedMesh.subMeshCount; }
            }
            r.size = bounds.size;
            // collider simplificado por función (contrato común de entrega)
            if (colliderKind == "capsule") { var cc = inst.AddComponent<CapsuleCollider>(); cc.center = new Vector3(0, bounds.size.y / 2f, 0); cc.height = bounds.size.y; cc.radius = Mathf.Max(0.2f, Mathf.Min(bounds.size.x, bounds.size.z) / 2f); }
            else if (colliderKind == "box") { var bc = inst.AddComponent<BoxCollider>(); bc.center = bounds.center - inst.transform.position; bc.size = colliderSize ?? bounds.size; }
            Directory.CreateDirectory($"{PrefabDir}/{prefabSubdir}");
            string prefabPath = $"{PrefabDir}/{prefabSubdir}/{assetId}.prefab";
            PrefabUtility.SaveAsPrefabAsset(inst, prefabPath);
            Object.DestroyImmediate(inst);
            r.fbx = fbxPath; r.prefab = prefabPath; r.materials.Add(mat.name);
            File.WriteAllText(Path.GetFullPath(Path.Combine(Application.dataPath, $"../../SourceArt/_evidence/EX-04/{assetId}_unity.json")), JsonUtility.ToJson(r, true));
            return r;
        }

        static Material BuildMaterial(string assetId, Report r)
        {
            string path = $"{MatDir}/M_{assetId}.mat";
            var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (mat == null) { mat = new Material(Shader.Find("Universal Render Pipeline/Lit")); AssetDatabase.CreateAsset(mat, path); }
            var baseColor = LoadTex($"{TexDir}/{assetId}_BaseColor.png", true);
            var rough = LoadTex($"{TexDir}/{assetId}_Roughness.png", false);
            var metal = LoadTex($"{TexDir}/{assetId}_Metallic.png", false);
            var normal = LoadTex($"{TexDir}/{assetId}_Normal.png", false, isNormal: true);
            if (baseColor != null) mat.SetTexture("_BaseMap", baseColor); else r.warnings.Add("sin BaseColor");
            if (normal != null) { mat.SetTexture("_BumpMap", normal); mat.EnableKeyword("_NORMALMAP"); }
            // URP Lit espera Metallic en R y Smoothness en A de _MetallicGlossMap: empaquetar desde Roughness/Metallic horneados (41.1)
            var packed = PackMetallicSmoothness(assetId, metal, rough, r);
            if (packed != null) { mat.SetTexture("_MetallicGlossMap", packed); mat.EnableKeyword("_METALLICSPECGLOSSMAP"); mat.SetFloat("_Smoothness", 1f); }
            mat.SetFloat("_Metallic", 0f);
            EditorUtility.SetDirty(mat); AssetDatabase.SaveAssets();
            return mat;
        }

        static Texture2D LoadTex(string path, bool srgb, bool isNormal = false)
        {
            if (!File.Exists(path)) return null;
            AssetDatabase.ImportAsset(path);
            var ti = AssetImporter.GetAtPath(path) as TextureImporter;
            if (ti != null)
            {
                bool changed = ti.sRGBTexture != srgb || (isNormal && ti.textureType != TextureImporterType.NormalMap) || ti.isReadable != !isNormal;
                ti.sRGBTexture = srgb; ti.textureType = isNormal ? TextureImporterType.NormalMap : TextureImporterType.Default; ti.isReadable = !isNormal; ti.maxTextureSize = 2048;
                if (changed) ti.SaveAndReimport();
            }
            return AssetDatabase.LoadAssetAtPath<Texture2D>(path);
        }

        static Texture2D PackMetallicSmoothness(string assetId, Texture2D metal, Texture2D rough, Report r)
        {
            if (rough == null) { r.warnings.Add("sin Roughness: sin mapa MetallicSmoothness"); return null; }
            int w = rough.width, h = rough.height;
            var rp = rough.GetPixels(); var mp = metal != null && metal.width == w ? metal.GetPixels() : null;
            var outPx = new Color[rp.Length];
            for (int i = 0; i < rp.Length; i++) { float m = mp != null ? mp[i].r : 0f; outPx[i] = new Color(m, m, m, 1f - rp[i].r); }
            var tex = new Texture2D(w, h, TextureFormat.RGBA32, true); tex.SetPixels(outPx); tex.Apply();
            string path = $"{TexDir}/{assetId}_MetallicSmoothness.png";
            File.WriteAllBytes(path, tex.EncodeToPNG()); Object.DestroyImmediate(tex);
            AssetDatabase.ImportAsset(path);
            var ti = AssetImporter.GetAtPath(path) as TextureImporter; if (ti != null) { ti.sRGBTexture = false; ti.SaveAndReimport(); }
            return AssetDatabase.LoadAssetAtPath<Texture2D>(path);
        }
    }
}
