using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering.HighDefinition;
using static Dream.EditorTools.Build.BuildKit;

namespace Dream.EditorTools.Build
{
    // Trae una escena de dream/blender (exportada con tools/taller_final/dream_export_blender.py): instancia el FBX,
    // le pone materiales HDRP con los mapas de dream/ (color, normal, mascara desde la rugosidad, emision) y vuelve a
    // crear sus luces donde estaban, con la misma direccion. Asi el escenario es el de dream/, no una copia aproximada.
    public static class DreamScene
    {
        [System.Serializable] public class Mat { public string name, albedo, normal, emission, alpha_map, mask; public float[] base_color, emission_color; public float roughness, metallic, emission_strength, alpha; public bool has_alpha; public int uv_index; }
        [System.Serializable] public class Lgt { public string name, type; public float[] color; public float energy, size, size_y, spot_deg; }
        [System.Serializable] public class Cam { public string name; public float lens_mm, sensor_mm; }
        [System.Serializable] public class Manifest { public Mat[] materials; public Lgt[] lights; public Cam[] cameras; }

        public const string Dir = Root + "/Art/Models/Dream";

        public class Result
        {
            public GameObject root;
            public Manifest manifest;
            public Transform Find(string name) => root.GetComponentsInChildren<Transform>(true).FirstOrDefault(t => t.name == name);
        }

        static Texture2D Tex(string folder, string rel, bool normal = false, bool linear = false)
        {
            if (string.IsNullOrEmpty(rel)) return null;
            string path = $"{folder}/{rel}";
            var imp = AssetImporter.GetAtPath(path) as TextureImporter;
            if (imp == null) return null;
            bool ch = false;
            if (normal && imp.textureType != TextureImporterType.NormalMap) { imp.textureType = TextureImporterType.NormalMap; ch = true; }
            if (linear && imp.sRGBTexture) { imp.sRGBTexture = false; ch = true; }
            if (ch) imp.SaveAndReimport();
            return AssetDatabase.LoadAssetAtPath<Texture2D>(path);
        }

        static Color Srgb(float[] c) => c == null ? Color.white : new Color(c[0], c[1], c[2], c.Length > 3 ? c[3] : 1f).gamma;

        public static Material Material(string folder, Mat m, float emissionNitsPerUnit)
        {
            var mat = BuildKit.Mat("M_" + m.name, string.IsNullOrEmpty(m.albedo) ? Srgb(m.base_color) : Color.white,
                                   1f - m.roughness, m.metallic);
            var a = Tex(folder, m.albedo);
            if (a) mat.SetTexture("_BaseColorMap", a);
            var n = Tex(folder, m.normal, true);
            if (n) { mat.SetTexture("_NormalMap", n); mat.SetFloat("_NormalScale", 0.8f); }
            var k = Tex(folder, m.mask, false, true);
            if (k) { mat.SetTexture("_MaskMap", k); mat.SetFloat("_SmoothnessRemapMin", 0f); mat.SetFloat("_SmoothnessRemapMax", 1f); }
            if (m.emission_strength > 0f)
            {
                HDMaterial.SetUseEmissiveIntensity(mat, true);
                HDMaterial.SetEmissiveColor(mat, Srgb(m.emission_color));
                HDMaterial.SetEmissiveIntensity(mat, m.emission_strength * emissionNitsPerUnit, EmissiveIntensityUnit.Nits);
                var e = Tex(folder, m.emission);
                if (e) mat.SetTexture("_EmissiveColorMap", e);
            }
            mat.SetFloat("_UVBase", m.uv_index);              // el mismo canal UV que eligio dream/ con su nodo UVMap
            mat.SetFloat("_UVDetail", m.uv_index);
            HDMaterial.ValidateMaterial(mat);
            EditorUtility.SetDirty(mat);
            return mat;
        }

        // lumensPerWatt: cuanto vale en HDRP un vatio de Blender (las escenas de dream/ estan calibradas en Eevee).
        public static Result Place(string name, Transform parent, Vector3 position, float yaw, float lumensPerWatt = 70f,
                                   float emissionNitsPerUnit = 220f, bool colliders = true)
        {
            string folder = $"{Dir}/{name}";
            var man = JsonUtility.FromJson<Manifest>(File.ReadAllText($"{folder}/manifest_unity.json"));
            var src = AssetDatabase.LoadAssetAtPath<GameObject>($"{folder}/{name}.fbx");
            var go = (GameObject)PrefabUtility.InstantiatePrefab(src);
            go.name = name;
            if (parent) go.transform.SetParent(parent, false);
            go.transform.SetPositionAndRotation(position, Quaternion.Euler(0f, yaw, 0f) * src.transform.rotation);
            go.transform.localScale = src.transform.localScale;

            var mats = man.materials.ToDictionary(x => x.name, x => Material(folder, x, emissionNitsPerUnit));
            foreach (var r in go.GetComponentsInChildren<Renderer>())
            {
                var ms = r.sharedMaterials;
                for (int i = 0; i < ms.Length; i++)
                    if (ms[i] && mats.TryGetValue(ms[i].name.Replace(" (Instance)", ""), out var hd)) ms[i] = hd;
                r.sharedMaterials = ms;
                if (colliders && r.GetComponent<MeshFilter>() && !r.GetComponent<Collider>()) r.gameObject.AddComponent<MeshCollider>();
                GameObjectUtility.SetStaticEditorFlags(r.gameObject, StaticEditorFlags.BatchingStatic);
            }

            // ejes de Blender en Unity: los marcadores EJE_X/Y/Z estaban a 1 m del origen
            var res = new Result { root = go, manifest = man };
            var origin = go.transform.position;
            var ez = res.Find("EJE_Z");
            var bz = ez ? (ez.position - origin).normalized : Vector3.up;
            foreach (var l in man.lights)
            {
                if (l.type == "SUN") continue;                      // el sol es el del viaje (TimeOfDay)
                var e = res.Find(l.name);
                if (!e) continue;
                // una luz de Blender apunta a su -Z local; en Unity ese eje es -EJE_Z expresado en el marco de la luz
                var localZ = go.transform.InverseTransformDirection(bz);
                var fwd = e.TransformDirection(-localZ).normalized;
                var lt = l.type == "AREA" ? LightType.Rectangle : l.type == "SPOT" ? LightType.Spot : LightType.Point;
                var c = new Color(l.color[0], l.color[1], l.color[2]);
                AddLight("Luz_" + l.name, go.transform, lt, e.position, Quaternion.LookRotation(fwd).eulerAngles, c,
                         l.energy * lumensPerWatt, 14f, l.spot_deg > 0 ? l.spot_deg : 60f,
                         lt == LightType.Rectangle ? new Vector2(Mathf.Max(0.1f, l.size), Mathf.Max(0.1f, l.size_y > 0 ? l.size_y : l.size)) : (Vector2?)null,
                         lt != LightType.Rectangle);
            }
            return res;
        }
    }
}
