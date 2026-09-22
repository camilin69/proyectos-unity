using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Esneider.EditorTools
{
    public static class VigiaReview
    {
        public const string Prefab = "Assets/_Game/Prefabs/Enemies/BOT-01_Vigia.prefab";
        public static string Capture(string label, string clipName = "", float time = 0, bool side = false, int lod = 0, bool front = false)
        {
            var scene = EditorSceneManager.NewPreviewScene();
            RenderTexture rt = null; Texture2D image = null;
            var previous = RenderTexture.active;
            try
            {
                var obj = Object.Instantiate(AssetDatabase.LoadAssetAtPath<GameObject>(Prefab));
                SceneManager.MoveGameObjectToScene(obj, scene);
                obj.transform.SetPositionAndRotation(Vector3.zero, Quaternion.identity);
                if (front) obj.transform.rotation = Quaternion.Euler(0,180,0);
                var group = obj.GetComponent<LODGroup>(); if (group) group.ForceLOD(lod);
                if (!string.IsNullOrEmpty(clipName))
                {
                    var clip = AssetDatabase.LoadAllAssetsAtPath("Assets/_Game/Art/Models/BOT-01_Vigia.fbx").OfType<AnimationClip>().First(c => c.name.EndsWith(clipName));
                    clip.SampleAnimation(obj, time);
                }
                var cameraObject = new GameObject("ReviewCamera"); SceneManager.MoveGameObjectToScene(cameraObject, scene);
                var camera = cameraObject.AddComponent<Camera>(); camera.scene = scene;
                camera.transform.position = side ? new Vector3(1.8f, 1.0f, 2.2f) : new Vector3(0, .83f, 2.8f);
                camera.transform.LookAt(new Vector3(0, .66f, 0)); camera.orthographic = true; camera.orthographicSize = .76f;
                camera.clearFlags = CameraClearFlags.SolidColor; camera.backgroundColor = new Color(.13f,.15f,.17f);
                camera.nearClipPlane = .01f; camera.farClipPlane = 20;
                for (int i=0;i<2;i++)
                {
                    var lightObject = new GameObject("ReviewLight" + i); SceneManager.MoveGameObjectToScene(lightObject, scene);
                    var light = lightObject.AddComponent<Light>(); light.type = LightType.Directional; light.intensity = i==0 ? 1.8f : .6f;
                    light.color = i==0 ? new Color(1,.96f,.90f) : new Color(.7f,.84f,1);
                    light.transform.rotation = Quaternion.Euler(i==0 ? 40 : 20, i==0 ? 155 : -55,0);
                }
                rt = new RenderTexture(800,800,24); camera.targetTexture = rt; camera.Render();
                RenderTexture.active = rt; image = new Texture2D(800,800,TextureFormat.RGB24,false); image.ReadPixels(new Rect(0,0,800,800),0,0); image.Apply();
                string dir = Path.GetFullPath(Path.Combine(Application.dataPath,"../../SourceArt/_evidence/EX-11")); Directory.CreateDirectory(dir);
                string path = Path.Combine(dir,label + ".png"); File.WriteAllBytes(path,image.EncodeToPNG()); return path;
            }
            finally { RenderTexture.active = previous; if(image) Object.DestroyImmediate(image); if(rt) Object.DestroyImmediate(rt); EditorSceneManager.ClosePreviewScene(scene); }
        }
        public static string ConfigureLOD()
        {
            var root = PrefabUtility.LoadPrefabContents(Prefab);
            try
            {
                var renderers = root.GetComponentsInChildren<SkinnedMeshRenderer>(true);
                var near = renderers.FirstOrDefault(r => r.name.Contains("LOD0"));
                var far = renderers.FirstOrDefault(r => r.name.Contains("LOD1"));
                if (!near || !far) return "Legacy source without authored LODs; no LOD configuration applied.";
                foreach(var r in renderers) { r.enabled=true; r.gameObject.SetActive(true); }
                var transforms = root.GetComponentsInChildren<Transform>(true);
                var positions = transforms.Select(t=>t.localPosition).ToArray();
                var rotations = transforms.Select(t=>t.localRotation).ToArray();
                var scales = transforms.Select(t=>t.localScale).ToArray();
                var bounds = renderers.Select(r=>r.localBounds).ToArray();
                var baked = new Mesh();
                try
                {
                    foreach(var clip in AssetDatabase.LoadAllAssetsAtPath("Assets/_Game/Art/Models/BOT-01_Vigia.fbx").OfType<AnimationClip>().Where(c=>!c.name.StartsWith("__")))
                        for(int sample=0;sample<=32;sample++)
                        {
                            clip.SampleAnimation(root,clip.length*sample/32f);
                            for(int i=0;i<renderers.Length;i++) { renderers[i].BakeMesh(baked); bounds[i].Encapsulate(baked.bounds); }
                        }
                }
                finally
                {
                    Object.DestroyImmediate(baked);
                    for(int i=0;i<transforms.Length;i++) { transforms[i].localPosition=positions[i]; transforms[i].localRotation=rotations[i]; transforms[i].localScale=scales[i]; }
                }
                for(int i=0;i<renderers.Length;i++) { bounds[i].Expand(.08f); renderers[i].localBounds=bounds[i]; }
                var material=near.sharedMaterial; material.SetFloat("_BumpScale",.3f); material.SetFloat("_Smoothness",.45f); EditorUtility.SetDirty(material);
                var group = root.GetComponent<LODGroup>() ?? root.AddComponent<LODGroup>();
                group.SetLODs(new [] { new LOD(.18f,new Renderer[]{near}), new LOD(.015f,new Renderer[]{far}) });
                group.fadeMode=LODFadeMode.None; group.RecalculateBounds(); group.localReferencePoint = new Vector3(0,.65f,0); group.size=1.3f;
                PrefabUtility.SaveAsPrefabAsset(root,Prefab);
                AssetDatabase.SaveAssets();
                return "LOD0="+near.sharedMesh.triangles.Length/3+" LOD1="+far.sharedMesh.triangles.Length/3+" bones="+near.bones.Length+"/"+far.bones.Length;
            }
            finally { PrefabUtility.UnloadPrefabContents(root); }
        }
    }
}
