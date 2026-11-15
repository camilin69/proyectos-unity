using System;
using System.IO;
using Dream.Cinematic;
using UnityEditor;
using UnityEditor.Events;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.Rendering;
using UnityEngine.Rendering.HighDefinition;
using UnityEngine.SceneManagement;
using Object = UnityEngine.Object;

namespace Dream.EditorTools.Build
{
    // Utilidades del constructor de escenas: materiales HDRP, primitivas con superficie de pasos, terrenos,
    // volumenes, luces, puertas, recuerdos, pasos y planos de cinematica. Todo lo que construye queda en
    // Assets/_Project y se puede reconstruir igual cuantas veces haga falta.
    public static class BuildKit
    {
        public const string Root = "Assets/_Project";
        public const string MatDir = Root + "/Art/Materials/Gris", TexDir = Root + "/Art/Textures/Gris",
            TerrainDir = Root + "/Art/Terrain", VolDir = Root + "/Settings/Volumes", SceneDir = Root + "/Scenes";

        public static void EnsureDir(string path)
        {
            if (AssetDatabase.IsValidFolder(path)) return;
            var parent = Path.GetDirectoryName(path).Replace('\\', '/');
            EnsureDir(parent);
            AssetDatabase.CreateFolder(parent, Path.GetFileName(path));
        }

        public static Scene NewScene() => EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

        public static string Save(Scene s, string name)
        {
            EnsureDir(SceneDir);
            var path = $"{SceneDir}/{name}.unity";
            EditorSceneManager.SaveScene(s, path);
            return path;
        }

        // ---------- materiales ----------

        public static Material Mat(string name, Color c, float smooth = 0.45f, float metal = 0f, Color? emission = null,
                                   float emissionNits = 0f, bool transparent = false, bool doubleSided = false)
        {
            EnsureDir(MatDir);
            string path = $"{MatDir}/{name}.mat";
            var m = AssetDatabase.LoadAssetAtPath<Material>(path);
            var shader = Shader.Find("HDRP/Lit");
            if (!m) { m = new Material(shader) { name = name }; AssetDatabase.CreateAsset(m, path); }
            else if (m.shader != shader) m.shader = shader;
            m.SetColor("_BaseColor", c);
            m.SetFloat("_Smoothness", smooth);
            m.SetFloat("_Metallic", metal);
            HDMaterial.SetSurfaceType(m, transparent);
            m.SetFloat("_DoubleSidedEnable", doubleSided ? 1f : 0f);
            if (emission.HasValue && emissionNits > 0f)
            {
                HDMaterial.SetUseEmissiveIntensity(m, true);
                HDMaterial.SetEmissiveColor(m, emission.Value);
                HDMaterial.SetEmissiveIntensity(m, emissionNits, EmissiveIntensityUnit.Nits);
            }
            else HDMaterial.SetEmissiveColor(m, Color.black);
            HDMaterial.ValidateMaterial(m);
            EditorUtility.SetDirty(m);
            return m;
        }

        public static ShootingStars ShootingStarsIn(Transform parent)
        {
            var go = new GameObject("Estrellas_fugaces");
            if (parent) go.transform.SetParent(parent, false);
            var s = go.AddComponent<ShootingStars>();
            var m = Unlit("M_Estrella_Fugaz", new Color(1f, 0.95f, 0.9f) * 6f);
            HDMaterial.SetSurfaceType(m, true);
            m.SetFloat("_BlendMode", 1f);
            HDMaterial.ValidateMaterial(m);
            s.trail = m;
            return s;
        }

        public const string ScanDir = Root + "/Art/Textures/PolyHaven";

        static Texture2D ScanTex(string id, string kind)
        {
            string path = $"{ScanDir}/{id}/{id}_{kind}.{(kind == "mask" ? "png" : "jpg")}";
            var imp = AssetImporter.GetAtPath(path) as TextureImporter;
            if (imp == null) return null;
            bool changed = false;
            if (kind == "normal" && imp.textureType != TextureImporterType.NormalMap) { imp.textureType = TextureImporterType.NormalMap; changed = true; }
            if (kind == "mask" && imp.sRGBTexture) { imp.sRGBTexture = false; changed = true; }
            if (changed) imp.SaveAndReimport();
            return AssetDatabase.LoadAssetAtPath<Texture2D>(path);
        }

        public static (Texture2D albedo, Texture2D normal, Texture2D mask) Scan(string id) => (ScanTex(id, "albedo"), ScanTex(id, "normal"), ScanTex(id, "mask"));

        // Material con un escaneo de Poly Haven, proyectado en triplanar del mundo (las cajas escaladas no lo estiran)
        // y tenido a la paleta con el color base. metersPerTile: cuantos metros cubre una repeticion.
        public static Material ScanMat(string name, string id, Color tint, float metersPerTile, float smoothMin = 0f, float smoothMax = 1f)
        {
            var m = Mat(name, tint, 0.5f);
            var (a, n, k) = Scan(id);
            if (!a) return m;
            m.SetTexture("_BaseColorMap", a);
            if (n) { m.SetTexture("_NormalMap", n); m.SetFloat("_NormalScale", 1f); }
            if (k) { m.SetTexture("_MaskMap", k); m.SetFloat("_SmoothnessRemapMin", smoothMin); m.SetFloat("_SmoothnessRemapMax", smoothMax); m.SetFloat("_AORemapMin", 0f); m.SetFloat("_AORemapMax", 1f); }
            m.SetFloat("_UVBase", 5f);                       // triplanar
            m.SetFloat("_TexWorldScale", 1f / Mathf.Max(0.05f, metersPerTile));
            m.SetFloat("_ObjectSpaceUVMapping", 0f);
            HDMaterial.ValidateMaterial(m);
            EditorUtility.SetDirty(m);
            return m;
        }

        public const string ModelDir = Root + "/Art/Models/PolyHaven";

        static Texture2D ModelTex(string id, string tag, string kind)
        {
            foreach (var ext in kind == "albedo" ? new[] { "png", "jpg" } : kind == "mask" ? new[] { "png" } : new[] { "jpg" })
            {
                string path = $"{ModelDir}/{id}/{tag}_{kind}.{ext}";
                var imp = AssetImporter.GetAtPath(path) as TextureImporter;
                if (imp == null) continue;
                bool changed = false;
                if (kind == "normal" && imp.textureType != TextureImporterType.NormalMap) { imp.textureType = TextureImporterType.NormalMap; changed = true; }
                if (kind == "mask" && imp.sRGBTexture) { imp.sRGBTexture = false; changed = true; }
                if (kind == "albedo" && ext == "png" && !imp.alphaIsTransparency) { imp.alphaIsTransparency = true; changed = true; }
                if (changed) imp.SaveAndReimport();
                return AssetDatabase.LoadAssetAtPath<Texture2D>(path);
            }
            return null;
        }

        // Material Lit con los mapas escaneados del modelo (UV del propio modelo). cutout: hojas con recorte alfa.
        public static Material ModelMat(string id, string tag, bool cutout, Color tint)
        {
            var m = Mat("M_" + tag, tint, 0.5f, 0f, null, 0f, false, cutout);
            var a = ModelTex(id, tag, "albedo"); var n = ModelTex(id, tag, "normal"); var k = ModelTex(id, tag, "mask");
            if (a) m.SetTexture("_BaseColorMap", a);
            if (n) m.SetTexture("_NormalMap", n);
            if (k) { m.SetTexture("_MaskMap", k); m.SetFloat("_SmoothnessRemapMin", 0f); m.SetFloat("_SmoothnessRemapMax", 1f); m.SetFloat("_MetallicRemapMin", 0f); m.SetFloat("_MetallicRemapMax", 1f); }
            if (cutout) { m.SetFloat("_AlphaCutoffEnable", 1f); m.SetFloat("_AlphaCutoff", 0.45f); }
            m.enableInstancing = true;
            HDMaterial.ValidateMaterial(m);
            EditorUtility.SetDirty(m);
            return m;
        }

        // Instancia un modelo de Poly Haven apoyado en 'floor' (su base toca ese punto), con materiales HDRP por parte
        // y un collider de caja. Devuelve la raiz y sus limites en el mundo.
        public static GameObject PolyModel(string id, Transform parent, Vector3 floor, float yaw, SurfaceType? surface = null,
                                           bool collider = true, Color? tint = null, float scale = 1f)
        {
            var src = AssetDatabase.LoadAssetAtPath<GameObject>($"{ModelDir}/{id}/{id}.fbx");
            if (!src) { Debug.LogWarning("Falta el modelo " + id); return null; }
            var go = (GameObject)PrefabUtility.InstantiatePrefab(src);
            go.name = id;
            if (parent) go.transform.SetParent(parent, false);
            // los FBX exportados desde Blender traen escala y rotacion propias en la raiz (conversion de unidades y ejes):
            // se conservan y solo se les suma el giro y la escala pedidos
            var srcRot = src.transform.rotation;
            go.transform.SetPositionAndRotation(floor, Quaternion.Euler(0f, yaw, 0f) * srcRot);
            go.transform.localScale = src.transform.localScale * scale;
            var glass = Mat("M_Vidrio_Modelo", new Color(0.95f, 0.97f, 1f, 0.12f), 0.98f, 0f, null, 0f, true);
            foreach (var r in go.GetComponentsInChildren<Renderer>())
            {
                var mats = r.sharedMaterials;
                for (int i = 0; i < mats.Length; i++)
                {
                    string n = mats[i] ? mats[i].name.Replace(" (Instance)", "") : id;
                    if (n.EndsWith("_glass")) mats[i] = glass;
                    else if (n.Contains("globe")) mats[i] = Mat("M_Globo_Lampara", new Color(1f, 0.97f, 0.92f), 0.6f, 0f, new Color(1f, 0.9f, 0.78f), 600f);
                    else
                    {
                        string tag = n.StartsWith(id) ? n : id;
                        mats[i] = ModelMat(id, tag, HasAlpha(id, tag), tint ?? Color.white);
                    }
                }
                r.sharedMaterials = mats;
            }
            // apoyar la base exactamente en el piso
            var b = Bounds(go);
            go.transform.position += new Vector3(0f, floor.y - b.min.y, 0f);
            if (collider)
            {
                // collider en un objeto aparte sin escala: alineado a los ejes del mundo con los limites del modelo
                b = Bounds(go);
                var col = new GameObject(id + "_colision");
                col.transform.SetParent(go.transform.parent, false);
                col.transform.position = b.center;
                col.AddComponent<BoxCollider>().size = b.size;
                if (surface.HasValue) col.AddComponent<SurfaceTag>().type = surface.Value;
            }
            GameObjectUtility.SetStaticEditorFlags(go, StaticEditorFlags.BatchingStatic);
            return go;
        }

        public static bool HasAlpha(string id, string tag) => System.IO.File.Exists($"{ModelDir}/{id}/{tag}_albedo.png");

        // Los modelos de Poly Haven de vegetacion traen varias variantes en fila. Esto reparte copias de cada variante
        // apoyadas en el terreno, con giro y escala al azar, y un LODGroup que las apaga cuando se ven pequenas
        // (la GPU integrada no dibuja pasto a 200 m).
        public static void Scatter(string id, Transform parent, int count, System.Func<System.Random, Vector2?> spot,
                                   System.Func<float, float, float> groundY, Vector2 scale, int seed, float cull = 0.02f,
                                   SurfaceType? surface = null, bool collider = false)
        {
            var temp = PolyModel(id, null, Vector3.zero, 0f, null, false);
            if (!temp) return;
            var variants = temp.GetComponentsInChildren<MeshRenderer>();
            var group = Group(id, parent);
            var rng = new System.Random(seed);
            for (int n = 0; n < count; n++)
            {
                var pos = spot(rng);
                if (!pos.HasValue) continue;
                var v = variants[rng.Next(variants.Length)];
                var mf = v.GetComponent<MeshFilter>();
                var go = new GameObject($"{id}_{n:000}", typeof(MeshFilter), typeof(MeshRenderer));
                go.transform.SetParent(group, false);
                go.GetComponent<MeshFilter>().sharedMesh = mf.sharedMesh;
                var mr = go.GetComponent<MeshRenderer>();
                mr.sharedMaterials = v.sharedMaterials;
                mr.shadowCastingMode = cull > 0.03f ? UnityEngine.Rendering.ShadowCastingMode.Off : UnityEngine.Rendering.ShadowCastingMode.On;
                float s = Mathf.Lerp(scale.x, scale.y, (float)rng.NextDouble());
                float yaw = (float)rng.NextDouble() * 360f;
                go.transform.rotation = Quaternion.Euler(0f, yaw, 0f) * v.transform.rotation;
                go.transform.localScale = v.transform.lossyScale * s;
                // apoyar la base de esta variante en el suelo, centrada en el punto elegido
                go.transform.position = Vector3.zero;
                var b = mr.bounds;
                var target = new Vector3(pos.Value.x, groundY(pos.Value.x, pos.Value.y), pos.Value.y);
                go.transform.position = target - new Vector3(b.center.x, b.min.y, b.center.z) - Vector3.up * 0.02f;
                var lod = go.AddComponent<LODGroup>();
                lod.SetLODs(new[] { new LOD(cull, new Renderer[] { mr }) });
                if (collider)
                {
                    go.AddComponent<BoxCollider>();
                    if (surface.HasValue) go.AddComponent<SurfaceTag>().type = surface.Value;
                }
                GameObjectUtility.SetStaticEditorFlags(go, StaticEditorFlags.BatchingStatic);
            }
            Object.DestroyImmediate(temp);
        }

        // Igual que Scatter, pero sin objetos: las matas van a un WindField (instancing + vaiven del viento).
        public static void ScatterInstanced(WindField field, string id, int count, System.Func<System.Random, Vector2?> spot,
                                            System.Func<float, float, float> groundY, Vector2 scale, int seed, float stiffness = 1f, bool shadows = false)
        {
            var temp = PolyModel(id, null, Vector3.zero, 0f, null, false);
            if (!temp) return;
            var variants = temp.GetComponentsInChildren<MeshRenderer>();
            var mats = new System.Collections.Generic.List<Matrix4x4>[variants.Length];
            var pts = new System.Collections.Generic.List<Vector3>[variants.Length];
            for (int i = 0; i < variants.Length; i++) { mats[i] = new(); pts[i] = new(); }
            var rng = new System.Random(seed);
            for (int n = 0; n < count; n++)
            {
                var pos = spot(rng);
                if (!pos.HasValue) continue;
                int k = rng.Next(variants.Length);
                var v = variants[k];
                var mesh = v.GetComponent<MeshFilter>().sharedMesh;
                float s = Mathf.Lerp(scale.x, scale.y, (float)rng.NextDouble());
                var rot = Quaternion.Euler(0f, (float)rng.NextDouble() * 360f, 0f) * v.transform.rotation;
                var scl = v.transform.lossyScale * s;
                var m0 = Matrix4x4.TRS(Vector3.zero, rot, scl);
                var mb = mesh.bounds;
                float minY = float.MaxValue; var c = Vector3.zero;
                for (int j = 0; j < 8; j++)
                {
                    var corner = mb.center + Vector3.Scale(mb.extents, new Vector3((j & 1) == 0 ? -1 : 1, (j & 2) == 0 ? -1 : 1, (j & 4) == 0 ? -1 : 1));
                    var w = m0.MultiplyPoint3x4(corner);
                    minY = Mathf.Min(minY, w.y); c += w;
                }
                c /= 8f;
                var target = new Vector3(pos.Value.x, groundY(pos.Value.x, pos.Value.y), pos.Value.y);
                var offset = target - new Vector3(c.x, minY, c.z) - Vector3.up * 0.03f;
                mats[k].Add(Matrix4x4.TRS(offset, rot, scl));
                pts[k].Add(target);
            }
            for (int i = 0; i < variants.Length; i++)
            {
                if (mats[i].Count == 0) continue;
                field.batches.Add(new WindField.Batch
                {
                    mesh = variants[i].GetComponent<MeshFilter>().sharedMesh,
                    materials = variants[i].sharedMaterials,
                    matrices = mats[i].ToArray(),
                    basePoints = pts[i].ToArray(),
                    stiffness = stiffness,
                    castShadows = shadows
                });
            }
            Object.DestroyImmediate(temp);
        }

        public static Bounds Bounds(GameObject go)
        {
            var rs = go.GetComponentsInChildren<Renderer>();
            var b = rs[0].bounds;
            foreach (var r in rs) b.Encapsulate(r.bounds);
            return b;
        }

        public static Material Unlit(string name, Color c)
        {
            EnsureDir(MatDir);
            string path = $"{MatDir}/{name}.mat";
            var m = AssetDatabase.LoadAssetAtPath<Material>(path);
            var shader = Shader.Find("HDRP/Unlit");
            if (!m) { m = new Material(shader) { name = name }; AssetDatabase.CreateAsset(m, path); }
            else m.shader = shader;
            m.SetColor("_UnlitColor", c);
            HDMaterial.ValidateMaterial(m);
            EditorUtility.SetDirty(m);
            return m;
        }

        public static Texture2D SolidTex(string name, Color c, float noise = 0.06f, int size = 64)
        {
            EnsureDir(TexDir);
            string path = $"{TexDir}/{name}.png";
            var full = Path.Combine(Directory.GetCurrentDirectory(), path);
            var t = new Texture2D(size, size, TextureFormat.RGBA32, false);
            var rng = new System.Random(name.GetHashCode());
            for (int y = 0; y < size; y++)
                for (int x = 0; x < size; x++)
                {
                    float n = 1f + ((float)rng.NextDouble() - 0.5f) * 2f * noise;
                    t.SetPixel(x, y, new Color(c.r * n, c.g * n, c.b * n, 1f));
                }
            File.WriteAllBytes(full, t.EncodeToPNG());
            Object.DestroyImmediate(t);
            AssetDatabase.ImportAsset(path);
            return AssetDatabase.LoadAssetAtPath<Texture2D>(path);
        }

        // Degradado vertical como textura (cielos pintados, la luz detras de las puertas).
        public static Texture2D GradientTex(string name, Color bottom, Color top, int h = 256)
        {
            EnsureDir(TexDir);
            string path = $"{TexDir}/{name}.png";
            var full = Path.Combine(Directory.GetCurrentDirectory(), path);
            var t = new Texture2D(4, h, TextureFormat.RGBA32, false);
            for (int y = 0; y < h; y++)
            {
                float k = y / (h - 1f); k = k * k * (3f - 2f * k);
                var c = Color.Lerp(bottom, top, k);
                for (int x = 0; x < 4; x++) t.SetPixel(x, y, c);
            }
            File.WriteAllBytes(full, t.EncodeToPNG());
            Object.DestroyImmediate(t);
            AssetDatabase.ImportAsset(path);
            var imp = (TextureImporter)AssetImporter.GetAtPath(path);
            imp.wrapMode = TextureWrapMode.Clamp; imp.SaveAndReimport();
            return AssetDatabase.LoadAssetAtPath<Texture2D>(path);
        }

        public static Material EmissiveTexMat(string name, Texture2D tex, float nits)
        {
            var m = Mat(name, Color.white, 0f, 0f, Color.white, nits);
            m.SetTexture("_BaseColorMap", tex);
            m.SetTexture("_EmissiveColorMap", tex);
            HDMaterial.ValidateMaterial(m);
            return m;
        }

        // ---------- objetos ----------

        public static Transform Group(string name, Transform parent = null)
        {
            var go = new GameObject(name);
            if (parent) go.transform.SetParent(parent, false);
            return go.transform;
        }

        public static Transform Point(string name, Transform parent, Vector3 pos, float yaw = 0f)
        {
            var t = Group(name, parent);
            t.position = pos;
            t.rotation = Quaternion.Euler(0f, yaw, 0f);
            return t;
        }

        public static Transform CamPoint(string name, Transform parent, Vector3 pos, Vector3 lookAt)
        {
            var t = Group(name, parent);
            t.position = pos;
            if ((lookAt - pos).sqrMagnitude > 1e-4f) t.rotation = Quaternion.LookRotation(lookAt - pos, Vector3.up);
            return t;
        }

        public static GameObject Prim(PrimitiveType type, string name, Transform parent, Vector3 pos, Vector3 scale, Material m,
                                      SurfaceType? surface = null, Vector3? euler = null, bool collider = true)
        {
            var go = GameObject.CreatePrimitive(type);
            go.name = name;
            if (parent) go.transform.SetParent(parent, false);
            go.transform.position = pos;
            go.transform.rotation = Quaternion.Euler(euler ?? Vector3.zero);
            go.transform.localScale = scale;
            if (m) go.GetComponent<Renderer>().sharedMaterial = m;
            var col = go.GetComponent<Collider>();
            if (!collider) Object.DestroyImmediate(col);
            else if (type == PrimitiveType.Cylinder && scale.y < scale.x * 0.5f)
            {
                // un cilindro chato (nenufar, disco) con capsula queda como una pelota: mejor una caja
                Object.DestroyImmediate(col);
                go.AddComponent<BoxCollider>();
            }
            if (surface.HasValue) go.AddComponent<SurfaceTag>().type = surface.Value;
            GameObjectUtility.SetStaticEditorFlags(go, StaticEditorFlags.BatchingStatic | StaticEditorFlags.OccluderStatic | StaticEditorFlags.OccludeeStatic);
            return go;
        }

        public static GameObject Box(string name, Transform parent, Vector3 center, Vector3 size, Material m, SurfaceType? s = null, float yaw = 0f)
            => Prim(PrimitiveType.Cube, name, parent, center, size, m, s, new Vector3(0f, yaw, 0f));

        // Caja definida por sus esquinas (paredes con huecos).
        public static GameObject BoxMinMax(string name, Transform parent, Vector3 min, Vector3 max, Material m, SurfaceType? s = null)
            => Box(name, parent, (min + max) * 0.5f, max - min, m, s);

        public static Light AddLight(string name, Transform parent, LightType type, Vector3 pos, Vector3 euler, Color color,
                                     float intensity, float range = 10f, float spotAngle = 60f, Vector2? area = null, bool shadows = true)
        {
            var go = new GameObject(name);
            if (parent) go.transform.SetParent(parent, false);
            go.transform.SetPositionAndRotation(pos, Quaternion.Euler(euler));
            var l = go.AddComponent<Light>();
            if (!go.GetComponent<HDAdditionalLightData>()) go.AddComponent<HDAdditionalLightData>();
            l.type = type;
            l.color = color;
            l.intensity = intensity;
            l.range = range;
            l.spotAngle = spotAngle;
            if (area.HasValue) l.areaSize = area.Value;
            l.shadows = shadows ? LightShadows.Soft : LightShadows.None;
            return l;
        }

        // ---------- volumenes ----------

        public static VolumeProfile Profile(string name, Action<VolumeProfile> setup)
        {
            EnsureDir(VolDir);
            string path = $"{VolDir}/{name}.asset";
            if (AssetDatabase.LoadAssetAtPath<VolumeProfile>(path)) AssetDatabase.DeleteAsset(path);
            var p = ScriptableObject.CreateInstance<VolumeProfile>();
            AssetDatabase.CreateAsset(p, path);
            setup(p);
            foreach (var c in p.components) { c.name = c.GetType().Name; AssetDatabase.AddObjectToAsset(c, p); }
            EditorUtility.SetDirty(p);
            return p;
        }

        public static Volume GlobalVolume(string name, Transform parent, VolumeProfile p, float priority)
        {
            var go = new GameObject(name);
            if (parent) go.transform.SetParent(parent, false);
            var v = go.AddComponent<Volume>();
            v.isGlobal = true; v.priority = priority; v.sharedProfile = p;
            return v;
        }

        public static Volume LocalVolume(string name, Transform parent, Vector3 center, Vector3 size, VolumeProfile p, float priority, float blend)
        {
            var go = new GameObject(name);
            if (parent) go.transform.SetParent(parent, false);
            go.transform.position = center;
            var box = go.AddComponent<BoxCollider>();
            box.isTrigger = true; box.size = size;
            var v = go.AddComponent<Volume>();
            v.isGlobal = false; v.priority = priority; v.blendDistance = blend; v.sharedProfile = p;
            return v;
        }

        public static void Fog(VolumeProfile p, float meanFreePath, float maxHeight, Color albedo, bool volumetric = true, float baseHeight = 0f)
        {
            var f = p.Add<Fog>();
            f.enabled.Override(true);
            f.meanFreePath.Override(meanFreePath);
            f.baseHeight.Override(baseHeight);
            f.maximumHeight.Override(maxHeight);
            f.albedo.Override(albedo);
            f.enableVolumetricFog.Override(volumetric);
        }

        // Niebla que solo llena lo cercano (un cuarto, una sala): el cielo y el paisaje lejano quedan limpios.
        public static void RoomFog(VolumeProfile p, float meanFreePath, float maxDistance, Color albedo)
        {
            var f = p.Add<Fog>();
            f.enabled.Override(true);
            f.meanFreePath.Override(meanFreePath);
            f.maxFogDistance.Override(maxDistance);
            f.globalLightProbeDimmer.Override(0.01f);  f.anisotropy.Override(0.25f);     // el aire solo brilla donde le da luz directa: el haz del sol se ve, lo demas no se vela
            f.albedo.Override(albedo);
            f.enableVolumetricFog.Override(true);
        }

        public static void Clouds(VolumeProfile p, VolumetricClouds.CloudPresets preset)
        {
            var c = p.Add<VolumetricClouds>();
            c.enable.Override(true);
            c.cloudPreset = preset;
        }

        public static void ExposureLimits(VolumeProfile p, float limitMin, float limitMax, float compensation)
        {
            var e = p.Add<Exposure>();
            e.mode.Override(ExposureMode.AutomaticHistogram);
            e.limitMin.Override(limitMin);
            e.limitMax.Override(limitMax);
            e.compensation.Override(compensation);
        }

        // Capa de nubes volumetricas a una altura dada: en el cielo del vuelo se atraviesan.
        public static void CloudLayer(VolumeProfile p, float bottom, float range, float density, float shape = 0.9f)
        {
            var c = p.Add<VolumetricClouds>();
            c.enable.Override(true);
            c.cloudPreset = VolumetricClouds.CloudPresets.Custom;
            c.bottomAltitude.Override(bottom);
            c.altitudeRange.Override(range);
            c.densityMultiplier.Override(density);
            c.shapeFactor.Override(shape);
        }

        // Cielo de noche: el Physically Based Sky con un cubemap de estrellas como emision del espacio.
        public static void NightSky(VolumeProfile p, float starNits)
        {
            var sky = p.Add<PhysicallyBasedSky>();
            sky.spaceEmissionTexture.Override(Stars());
            sky.spaceEmissionMultiplier.Override(starNits);
        }

        // Cielo fotografiado (HDRI de Poly Haven): por la ventana se ve un paisaje real, no el cielo generico.
        public static Cubemap Hdri(string file)
        {
            string path = $"{ScanDir}/HDRI/{file}";
            var imp = AssetImporter.GetAtPath(path) as TextureImporter;
            if (imp != null && (imp.textureShape != TextureImporterShape.TextureCube || imp.maxTextureSize != 2048))
            {
                imp.textureShape = TextureImporterShape.TextureCube;
                imp.generateCubemap = TextureImporterGenerateCubemap.AutoCubemap;
                imp.maxTextureSize = 2048;          // 2k: igual de nitido por la ventana y mucho mas liviano para la GPU
                imp.textureCompression = TextureImporterCompression.CompressedHQ;
                imp.SaveAndReimport();
            }
            return AssetDatabase.LoadAssetAtPath<Cubemap>(path);
        }

        public static void HdriSkyOverride(VolumeProfile p, Cubemap cube, float rotation, float lux)
        {
            var ve = p.Add<VisualEnvironment>();
            ve.skyType.Override((int)SkyType.HDRI);
            ve.skyAmbientMode.Override(SkyAmbientMode.Dynamic);
            var sky = p.Add<HDRISky>();
            sky.hdriSky.Override(cube);
            sky.rotation.Override(rotation);
            sky.skyIntensityMode.Override(SkyIntensityMode.Lux);
            sky.desiredLuxValue.Override(lux);
        }

        // Cielo de los disenos de dream/: azul cobalto profundo, despejado, que parece no tener fin.
        public static void DreamSky(VolumeProfile p, float exposure = 13.9f)
        {
            var ve = p.Add<VisualEnvironment>();
            ve.skyType.Override((int)SkyType.Gradient);
            ve.skyAmbientMode.Override(SkyAmbientMode.Dynamic);
            var sky = p.Add<GradientSky>();
            sky.top.Override(new Color(0.01f, 0.12f, 0.62f));         // cenit cobalto profundo
            sky.middle.Override(new Color(0.05f, 0.33f, 0.95f));      // el azul saturado de los disenos
            sky.bottom.Override(new Color(0.55f, 0.78f, 1f));         // horizonte claro
            sky.gradientDiffusion.Override(1.2f);
            sky.exposure.Override(exposure);
            // el ACES lava los azules: un poco mas de saturacion y contraste en los paisajes de dia
            var ca = p.Add<ColorAdjustments>(); ca.saturation.Override(18f); ca.contrast.Override(8f);
        }

        public static Cubemap Stars()
        {
            EnsureDir(TexDir);
            string path = $"{TexDir}/CM_Estrellas.cubemap";
            var existing = AssetDatabase.LoadAssetAtPath<Cubemap>(path);
            if (existing) return existing;
            const int size = 512;
            var cm = new Cubemap(size, TextureFormat.RGBAHalf, false);
            var rng = new System.Random(42);
            var black = new Color[size * size];
            for (int f = 0; f < 6; f++)
            {
                var px = (Color[])black.Clone();
                int count = 2600;
                for (int i = 0; i < count; i++)
                {
                    int x = rng.Next(size), y = rng.Next(size);
                    double r = rng.NextDouble();
                    float b = (float)(0.04 + 0.9 * System.Math.Pow(r, 9.0));        // casi todas tenues, unas pocas brillantes
                    float t = (float)rng.NextDouble();
                    var tint = Color.Lerp(new Color(0.75f, 0.83f, 1f), new Color(1f, 0.88f, 0.78f), t);
                    px[y * size + x] = tint * b * 4f;
                    if (b > 0.5f)                                                  // las brillantes tienen un halo de un pixel
                    {
                        if (x + 1 < size) px[y * size + x + 1] += tint * b;
                        if (y + 1 < size) px[(y + 1) * size + x] += tint * b;
                    }
                }
                cm.SetPixels(px, (CubemapFace)f);
            }
            cm.Apply();
            AssetDatabase.CreateAsset(cm, path);
            return cm;
        }

        // Ruido 3D para nubes locales: Perlin por capas con un borde redondeado, para que cada caja parezca un cumulo.
        public static Texture3D CloudNoise()
        {
            EnsureDir(TexDir);
            string path = $"{TexDir}/T3D_Nube.asset";
            var existing = AssetDatabase.LoadAssetAtPath<Texture3D>(path);
            if (existing) return existing;
            const int n = 48;
            var tex = new Texture3D(n, n, n, TextureFormat.RGBA32, false) { wrapMode = TextureWrapMode.Clamp };
            var c = new Color[n * n * n];
            for (int z = 0; z < n; z++)
                for (int y = 0; y < n; y++)
                    for (int x = 0; x < n; x++)
                    {
                        float u = x / (n - 1f), v = y / (n - 1f), w = z / (n - 1f);
                        float noise = 0f, amp = 0.55f, freq = 3f;
                        for (int o = 0; o < 4; o++)
                        {
                            noise += amp * (Mathf.PerlinNoise(u * freq + w * 1.7f + o * 13f, v * freq + o * 7f)
                                          + Mathf.PerlinNoise(w * freq + o * 5f, u * freq + v * 0.9f)) * 0.5f;
                            amp *= 0.5f; freq *= 2.1f;
                        }
                        float dx = u - 0.5f, dy = (v - 0.42f) * 1.3f, dz = w - 0.5f;
                        float shape = Mathf.Clamp01(1f - Mathf.Sqrt(dx * dx + dy * dy + dz * dz) * 2.1f);
                        float d = Mathf.Clamp01((noise * 1.4f - 0.35f) * 2f) * Mathf.SmoothStep(0f, 1f, shape * 1.6f);
                        c[x + y * n + z * n * n] = new Color(1f, 1f, 1f, d);
                    }
            tex.SetPixels(c);
            tex.Apply();
            AssetDatabase.CreateAsset(tex, path);
            return tex;
        }

        public static LocalVolumetricFog CloudPuff(string name, Transform parent, Vector3 center, Vector3 size, float meanFreePath, Color albedo, bool collider = false)
        {
            var go = new GameObject(name);
            if (parent) go.transform.SetParent(parent, false);
            go.transform.position = center;
            var f = go.AddComponent<LocalVolumetricFog>();
            var prm = f.parameters;
            prm.albedo = albedo;
            prm.meanFreePath = meanFreePath;
            prm.size = size;
            prm.volumeMask = CloudNoise();
            prm.textureScrollingSpeed = new Vector3(0.004f, 0f, 0.002f);
            prm.textureTiling = Vector3.one;
            prm.positiveFade = prm.negativeFade = new Vector3(0.25f, 0.35f, 0.25f);
            prm.falloffMode = LocalVolumetricFogFalloffMode.Exponential;
            f.parameters = prm;
            if (collider)
            {
                var b = go.AddComponent<BoxCollider>();
                b.size = new Vector3(size.x * 0.6f, size.y * 0.45f, size.z * 0.6f);
                go.AddComponent<SurfaceTag>().type = SurfaceType.Cloud;
            }
            return f;
        }

        public static WaterSurface Water(string name, Transform parent, WaterSurfaceType type, Vector3 pos, Vector2 size)
        {
            var go = new GameObject(name);
            if (parent) go.transform.SetParent(parent, false);
            go.transform.position = pos;
            var w = go.AddComponent<WaterSurface>();
            w.surfaceType = type;
            if (type == WaterSurfaceType.OceanSeaLake) w.geometryType = WaterGeometryType.Infinite;
            else { w.geometryType = WaterGeometryType.Quad; go.transform.localScale = new Vector3(size.x, 1f, size.y); }
            return w;
        }

        // ---------- terreno ----------

        public static Terrain MakeTerrain(string name, Transform parent, Vector3 origin, Vector3 size, int res,
                                          Func<float, float, float> height01, params (string name, Color color, float tile)[] layers)
        {
            EnsureDir(TerrainDir);
            var td = new TerrainData { heightmapResolution = res };
            td.size = size;
            var h = new float[res, res];
            for (int z = 0; z < res; z++)
                for (int x = 0; x < res; x++)
                    h[z, x] = Mathf.Clamp01(height01(x / (res - 1f), z / (res - 1f)));
            td.SetHeights(0, 0, h);

            var tls = new TerrainLayer[layers.Length];
            for (int i = 0; i < layers.Length; i++)
            {
                string lp = $"{TerrainDir}/{name}_{layers[i].name}.terrainlayer";
                var tl = AssetDatabase.LoadAssetAtPath<TerrainLayer>(lp);
                if (!tl) { tl = new TerrainLayer(); AssetDatabase.CreateAsset(tl, lp); }
                string scan = layers[i].name switch { "Pasto" => "leafy_grass", "Arena" => "coast_sand_01", "Bosque" => "forest_leaves_02", _ => null };
                var (sa, sn, sk) = scan != null ? Scan(scan) : (null, null, null);
                if (sa)
                {
                    tl.diffuseTexture = sa; tl.normalMapTexture = sn; tl.maskMapTexture = sk;
                    var c = layers[i].color * 1.6f;                  // tinte suave hacia la paleta
                    tl.diffuseRemapMax = new Vector4(Mathf.Min(1.2f, c.r), Mathf.Min(1.2f, c.g), Mathf.Min(1.2f, c.b), 1f);
                    tl.maskMapRemapMax = new Vector4(0f, 1f, 1f, 0.35f);
                }
                else tl.diffuseTexture = SolidTex($"T_{name}_{layers[i].name}", layers[i].color, 0.09f);
                tl.tileSize = new Vector2(layers[i].tile, layers[i].tile);
                tl.smoothness = 0.1f;
                EditorUtility.SetDirty(tl);
                tls[i] = tl;
            }
            td.terrainLayers = tls;
            string path = $"{TerrainDir}/{name}.asset";
            if (AssetDatabase.LoadAssetAtPath<TerrainData>(path)) AssetDatabase.DeleteAsset(path);
            AssetDatabase.CreateAsset(td, path);

            var go = Terrain.CreateTerrainGameObject(td);
            go.name = name;
            if (parent) go.transform.SetParent(parent, false);
            go.transform.position = origin;
            var terrain = go.GetComponent<Terrain>();
            terrain.materialTemplate = TerrainMaterial();
            terrain.drawInstanced = true;
            terrain.heightmapPixelError = 3f;
            return terrain;
        }

        // Copia propia del material de terreno de HDRP: el del paquete es inmutable y el Terrain lo modifica al usarlo.
        static Material TerrainMaterial()
        {
            EnsureDir(MatDir);
            string path = $"{MatDir}/M_Terreno.mat";
            var m = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (m) return m;
            var rp = GraphicsSettings.currentRenderPipeline;
            m = new Material(rp.defaultTerrainMaterial) { name = "M_Terreno" };
            AssetDatabase.CreateAsset(m, path);
            return m;
        }

        // Pinta la capa 'layer' donde mask(x01, z01) > 0 (el resto queda en la capa 0).
        public static void PaintLayer(Terrain t, int layer, Func<float, float, float> mask)
        {
            var d = t.terrainData;
            int w = d.alphamapWidth, h = d.alphamapHeight, n = d.alphamapLayers;
            var a = new float[h, w, n];
            for (int z = 0; z < h; z++)
                for (int x = 0; x < w; x++)
                {
                    float m = Mathf.Clamp01(mask(x / (w - 1f), z / (h - 1f)));
                    for (int i = 0; i < n; i++) a[z, x, i] = 0f;
                    a[z, x, 0] = 1f - m;
                    a[z, x, layer] += m;
                }
            d.SetAlphamaps(0, 0, a);
            // las texturas de pesos deben vivir dentro del asset del terreno o se pierden al recargar la escena
            foreach (var tex in d.alphamapTextures)
                if (tex && !AssetDatabase.Contains(tex)) AssetDatabase.AddObjectToAsset(tex, d);
            EditorUtility.SetDirty(d);
        }

        public static float Ground(Terrain t, float x, float z) => t.SampleHeight(new Vector3(x, 0f, z)) + t.transform.position.y;

        // ---------- piezas del sueno ----------

        public static SceneAnchor Anchor(int index, string title, Vector3 spawn, float yaw, float startHour, float endHour, float minutes)
        {
            var go = new GameObject("Escenario");
            var a = go.AddComponent<SceneAnchor>();
            a.index = index; a.title = title;
            a.spawn = Point("Aparece", go.transform, spawn, yaw);
            a.startHour = startHour; a.endHour = endHour; a.minutesToEndHour = minutes;
            return a;
        }

        public static MemoryFragment Memory(Transform parent, Vector3 pos, string text, bool flight = false)
        {
            var go = new GameObject("Recuerdo");
            go.transform.SetParent(parent, false);
            go.transform.position = pos;
            var mf = go.AddComponent<MemoryFragment>();
            mf.memoryText = text;
            mf.unlocksFlight = flight;
            var prism = Group("Prisma_4D", go.transform);
            prism.position = pos;
            var tess = prism.gameObject.AddComponent<Tesseract>();
            var edge = Unlit("M_Arista_Prisma", new Color(160f, 160f, 160f, 1f));   // alfa 1 (en aditivo el alfa tambien multiplica)
            HDMaterial.SetSurfaceType(edge, true);
            edge.SetFloat("_BlendMode", 1f);                       // aditivo: las aristas suman luz
            HDMaterial.ValidateMaterial(edge);
            tess.edgeTemplate = edge;
            var core = Prim(PrimitiveType.Sphere, "Nucleo", prism, pos, Vector3.one * 0.09f,
                            Mat("M_Nucleo_Recuerdo", new Color(1f, 0.96f, 1f), 0.98f, 0f, Color.white, 160f), null, null, false);
            GameObjectUtility.SetStaticEditorFlags(core, 0);
            tess.core = core.GetComponent<Renderer>();
            mf.visual = prism;
            mf.glow = AddLight("Brillo", go.transform, LightType.Point, pos, Vector3.zero, new Color(1f, 0.84f, 0.95f), 220f, 6f, 60f, null, false);
            mf.glow.GetComponent<HDAdditionalLightData>().volumetricDimmer = 0f;   // no enciende la niebla: brilla el prisma, no el aire
            tess.glow = mf.glow;
            return mf;
        }

        public static TransitionGate Gate(string name, Transform parent, Vector3 center, Vector3 size, CinematicSequence departure,
                                          bool advance = true, bool requireMemory = true)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            go.transform.position = center;
            var box = go.AddComponent<BoxCollider>();
            box.isTrigger = true; box.size = size;
            var g = go.AddComponent<TransitionGate>();
            g.departure = departure; g.advanceScene = advance; g.requireMemory = requireMemory;
            return g;
        }

        public static DoorSwing Door(string name, Transform parent, Vector3 floorCenter, float yaw, Material frame, Material panel,
                                     float width = 1.0f, float height = 2.2f, bool open = false)
        {
            var root = Point(name, parent, floorCenter, yaw);
            var rot = Quaternion.Euler(0f, yaw, 0f);
            Vector3 W(float x, float y, float z) => floorCenter + rot * new Vector3(x, y, z);
            float t = 0.12f;
            Prim(PrimitiveType.Cube, "Jamba_I", root, W(-width / 2f - t / 2f, height / 2f, 0f), new Vector3(t, height + t, 0.18f), frame, SurfaceType.Wood, new Vector3(0, yaw, 0));
            Prim(PrimitiveType.Cube, "Jamba_D", root, W(width / 2f + t / 2f, height / 2f, 0f), new Vector3(t, height + t, 0.18f), frame, SurfaceType.Wood, new Vector3(0, yaw, 0));
            Prim(PrimitiveType.Cube, "Dintel", root, W(0f, height + t / 2f, 0f), new Vector3(width + 2f * t, t, 0.18f), frame, SurfaceType.Wood, new Vector3(0, yaw, 0));
            var hinge = Point("Bisagra", root, W(-width / 2f, 0f, 0f), yaw);
            var p = Prim(PrimitiveType.Cube, "Hoja", hinge, W(0f, height / 2f, 0f), new Vector3(width - 0.02f, height - 0.02f, 0.05f), panel, SurfaceType.Wood, new Vector3(0, yaw, 0));
            GameObjectUtility.SetStaticEditorFlags(p, 0);
            var knob = Prim(PrimitiveType.Sphere, "Pomo", hinge, W(width * 0.4f, 1.0f, -0.05f), Vector3.one * 0.06f, Mat("M_Laton", new Color(0.85f, 0.7f, 0.45f), 0.8f, 1f), null, null, false);
            GameObjectUtility.SetStaticEditorFlags(knob, 0);
            var d = root.gameObject.AddComponent<DoorSwing>();
            d.hinge = hinge;
            if (open) hinge.rotation = Quaternion.Euler(0f, yaw - 100f, 0f);
            return d;
        }

        public static Checkpoint CheckpointAt(Transform parent, Vector3 pos, float yaw, Vector3 size)
        {
            var go = new GameObject("Punto_seguro");
            go.transform.SetParent(parent, false);
            go.transform.SetPositionAndRotation(pos, Quaternion.Euler(0f, yaw, 0f));
            var b = go.AddComponent<BoxCollider>(); b.size = size;
            return go.AddComponent<Checkpoint>();
        }

        public static SfxCue Cue(Transform parent)
        {
            var go = new GameObject("Sonidos");
            go.transform.SetParent(parent, false);
            return go.AddComponent<SfxCue>();
        }

        // ---------- cinematicas ----------

        public static Shot Shot(float duration, string note)
            => new() { duration = duration, note = note, onStart = new UnityEvent(), onEnd = new UnityEvent(), actorSpeed = 1.25f, focalLength = 35f, cut = true };

        public static void OnStart(Shot s, UnityAction a) => UnityEventTools.AddVoidPersistentListener(s.onStart, a);
        public static void OnEnd(Shot s, UnityAction a) => UnityEventTools.AddVoidPersistentListener(s.onEnd, a);

        public static ShotSequence Sequence(string name, Transform parent, params Shot[] shots)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            var seq = go.AddComponent<ShotSequence>();
            seq.shots = shots;
            return seq;
        }

        public static void Static(GameObject go, bool on)
        {
            GameObjectUtility.SetStaticEditorFlags(go, on ? StaticEditorFlags.BatchingStatic : 0);
        }
    }
}
