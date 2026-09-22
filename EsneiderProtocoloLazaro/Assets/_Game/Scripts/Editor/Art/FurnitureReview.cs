using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using Object = UnityEngine.Object;

namespace Esneider.EditorTools
{
    // EX-13: preserve authored openings with compound boxes; never stretch furniture meshes.
    public static class FurnitureReview
    {
        [Serializable] public class CollisionBox { public float[] center, size; }
        [Serializable] public class Geometry { public string asset; public int triangles; public float[] dimensions_blender; public CollisionBox[] collision_boxes_blender; }
        [Serializable] public class Coordinates { public Vector3[] vertices; }
        [Serializable] public class AxisReport { public float signX, signZ, maxError; }
        public static string Evidence(string asset)
        {
            string root = Path.GetFullPath(Path.Combine(Application.dataPath, "../../SourceArt/_evidence"));
            var candidates = Directory.GetDirectories(root, "EX-*").Select(d => Path.Combine(d, asset)).Where(d => File.Exists(Path.Combine(d, "geometry.json"))).ToArray();
            if (candidates.Length != 1) throw new InvalidOperationException("Expected one authoritative geometry report for " + asset + ", found " + candidates.Length);
            return candidates[0];
        }
        public static string Prefab(string asset) => "Assets/_Game/Prefabs/Environment/" + asset + ".prefab";

        public static AxisReport VerifyAxes(string asset)
        {
            var samples = JsonUtility.FromJson<Coordinates>(File.ReadAllText(Path.Combine(Evidence(asset), "source_coordinates.json"))).vertices;
            if (samples == null || samples.Length < 8) throw new InvalidOperationException("Missing source coordinate samples");
            var model = AssetDatabase.LoadAssetAtPath<GameObject>(AssetIntegrator.ModelsDir + "/" + asset + ".fbx");
            var vertices = model.GetComponentsInChildren<MeshFilter>().SelectMany(m => m.sharedMesh.vertices.Select(v => m.transform.TransformPoint(v))).ToArray();
            var best = new AxisReport { maxError = float.PositiveInfinity };
            foreach (float sx in new[] { 1f, -1f }) foreach (float sz in new[] { 1f, -1f })
            {
                float error = samples.Max(p => vertices.Min(v => Vector3.Distance(v, new Vector3(sx*p.x, p.z, sz*p.y))));
                if (error < best.maxError) best = new AxisReport { signX = sx, signZ = sz, maxError = error };
            }
            if (best.maxError > .0002f) throw new InvalidOperationException("FBX coordinates differ from source: " + best.maxError);
            File.WriteAllText(Path.Combine(Evidence(asset), "axis_conversion.json"), JsonUtility.ToJson(best, true));
            return best;
        }

        public static string Integrate(string asset)
        {
            var geometry = JsonUtility.FromJson<Geometry>(File.ReadAllText(Path.Combine(Evidence(asset), "geometry.json")));
            foreach (var suffix in new[] { "BaseColor", "Normal", "Metallic", "Roughness" })
                if (!File.Exists(AssetIntegrator.TexDir + "/" + asset + "_" + suffix + ".png")) throw new InvalidOperationException("Missing baked texture: " + suffix);
            var report = AssetIntegrator.Integrate(asset, "Environment", false, "none");
            if (report.warnings.Count > 0) throw new InvalidOperationException(string.Join("; ", report.warnings));
            if (report.tris != geometry.triangles || report.submeshes != 1) throw new InvalidOperationException("Unexpected imported mesh topology");
            var axes = VerifyAxes(asset);
            var root = PrefabUtility.LoadPrefabContents(Prefab(asset));
            try
            {
                foreach (var box in geometry.collision_boxes_blender)
                {
                    var collider = root.AddComponent<BoxCollider>();
                    collider.center = new Vector3(axes.signX * box.center[0], box.center[2], axes.signZ * box.center[1]);
                    collider.size = new Vector3(box.size[0], box.size[2], box.size[1]);
                }
                foreach (var t in root.GetComponentsInChildren<Transform>()) { t.gameObject.layer = Esneider.Core.GameLayers.WorldStatic; t.gameObject.isStatic = true; }
                var tag = root.AddComponent<Esneider.World.SurfaceTag>();
                tag.surfaceId = asset.StartsWith("OBJ-017") || asset.StartsWith("OBJ-038") || asset.StartsWith("OBJ-039") ? "SUR-FAB" : "SUR-MET";
                PrefabUtility.SaveAsPrefabAsset(root, Prefab(asset));
            }
            finally { PrefabUtility.UnloadPrefabContents(root); }
            File.WriteAllText(Path.Combine(Evidence(asset), "unity_import.json"), JsonUtility.ToJson(report, true));
            AssetDatabase.SaveAssets();
            return asset + ": " + report.tris + " tris, " + geometry.collision_boxes_blender.Length + " compound boxes";
        }

        public static string Capture(string asset, string prefabPath = null, string outputDirectory = null, Action<GameObject> prepare = null, Bounds? framing = null)
        {
            var scene = EditorSceneManager.NewPreviewScene();
            RenderTexture rt = null; Texture2D image = null; Cubemap studio = null; Camera camera = null; var previous = RenderTexture.active;
            try
            {
                var obj = Object.Instantiate(AssetDatabase.LoadAssetAtPath<GameObject>(prefabPath ?? Prefab(asset)));
                SceneManager.MoveGameObjectToScene(obj, scene); obj.transform.SetPositionAndRotation(Vector3.zero, Quaternion.identity);
                prepare?.Invoke(obj);
                foreach(var lod in obj.GetComponentsInChildren<LODGroup>()) lod.ForceLOD(0);
                var renderers = obj.GetComponentsInChildren<Renderer>(); var bounds = renderers[0].bounds;
                foreach (var renderer in renderers.Skip(1)) bounds.Encapsulate(renderer.bounds);
                if(framing.HasValue) bounds=framing.Value;
                // An isolated preview has no room probes. Supply a neutral studio reflection
                // so metallic materials can be judged without changing the game's lighting.
                studio = new Cubemap(16,TextureFormat.RGBAHalf,true);
                for(int face=0;face<6;face++)
                {
                    float value=face==2 ? .42f : face==3 ? .06f : face==0 ? .28f : .16f;
                    studio.SetPixels(Enumerable.Repeat(new Color(value,value,value,1),256).ToArray(),(CubemapFace)face);
                }
                studio.Apply(true);
                var probeObject=new GameObject("FurnitureStudioReflection");SceneManager.MoveGameObjectToScene(probeObject,scene);
                var probe=probeObject.AddComponent<ReflectionProbe>();probe.mode=UnityEngine.Rendering.ReflectionProbeMode.Custom;
                probe.customBakedTexture=studio;probe.center=bounds.center;probe.size=Vector3.one*(bounds.size.magnitude*8);probe.importance=100;
                var cameraObject = new GameObject("FurnitureReviewCamera"); SceneManager.MoveGameObjectToScene(cameraObject, scene);
                camera = cameraObject.AddComponent<Camera>(); camera.scene = scene;
                float span = bounds.size.magnitude;
                camera.transform.position = bounds.center + new Vector3(1,.65f,-1).normalized * span * 2;
                camera.transform.LookAt(bounds.center); camera.orthographic = true; camera.orthographicSize = span * .57f;
                camera.clearFlags = CameraClearFlags.SolidColor; camera.backgroundColor = new Color(.13f,.15f,.17f);
                camera.nearClipPlane = .01f; camera.farClipPlane = 40;
                for (int i=0;i<2;i++)
                {
                    var lightObject = new GameObject("FurnitureReviewLight" + i); SceneManager.MoveGameObjectToScene(lightObject, scene);
                    var light = lightObject.AddComponent<Light>(); light.type = LightType.Directional; light.intensity = i==0 ? 1.8f : .6f;
                    light.color = i==0 ? new Color(1,.96f,.90f) : new Color(.7f,.84f,1);
                    light.transform.rotation = Quaternion.Euler(i==0 ? 40 : 20, i==0 ? -30 : 130,0);
                }
                rt = new RenderTexture(640,640,24); camera.targetTexture = rt; camera.Render();
                RenderTexture.active = rt; image = new Texture2D(640,640,TextureFormat.RGB24,false);
                image.ReadPixels(new Rect(0,0,640,640),0,0); image.Apply();
                var directory = outputDirectory ?? Evidence(asset); Directory.CreateDirectory(directory);
                var path = Path.Combine(directory, "unity_preview.png"); File.WriteAllBytes(path,image.EncodeToPNG()); return path;
            }
            finally { RenderTexture.active=previous; if(camera) camera.targetTexture=null; if(image) Object.DestroyImmediate(image); if(rt) Object.DestroyImmediate(rt); EditorSceneManager.ClosePreviewScene(scene); if(studio) Object.DestroyImmediate(studio); }
        }
    }
}
