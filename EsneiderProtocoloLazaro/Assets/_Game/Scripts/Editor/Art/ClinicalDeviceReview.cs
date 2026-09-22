using System;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using Esneider.World;
using Object = UnityEngine.Object;

namespace Esneider.EditorTools
{
    public static class ClinicalDeviceReview
    {
        static GameObject Place(string asset, Transform parent, Vector3 local)
        {
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(FurnitureReview.Prefab(asset));
            if (!prefab) throw new InvalidOperationException("Missing " + asset);
            var go = (GameObject)PrefabUtility.InstantiatePrefab(prefab, parent);
            go.transform.localPosition = local; go.transform.localRotation = Quaternion.identity;
            return go;
        }
        public static string Apply(Transform root)
        {
            var all = root.GetComponentsInChildren<Transform>(true);
            if (all.Any(t => t.name == "Clinic_Devices_EX22")) return "";
            var old = all.FirstOrDefault(t => t.name == "M044_biomonitor");
            var stand = all.FirstOrDefault(t => t.name == "Clinic_FluidStand_EX21");
            if (!old || !stand) return "";
            foreach (var asset in new[]{"OBJ-045_MonitorBiometrico", "OBJ-046_BombaPerfusion", "OBJ-006_CarroSanitario"})
                if (!AssetDatabase.LoadAssetAtPath<GameObject>(FurnitureReview.Prefab(asset))) return "";
            var group = new GameObject("Clinic_Devices_EX22").transform;
            group.SetParent(old.parent); group.position = old.position - Vector3.up * .8f;
            var cart = Place("OBJ-006_CarroSanitario",group,Vector3.zero);
            cart.name = "M044_MonitorCart";
            Place("OBJ-045_MonitorBiometrico",cart.transform,Vector3.up*.799f);
            var pump = Place("OBJ-046_BombaPerfusion",stand,new Vector3(0,.534f,-.09f));
            pump.name = "Clinic_Perfusion_EX22";
            Object.DestroyImmediate(old.gameObject);
            return "M044 monitor/cart; perfusion pump mounted on fluid stand with aligned ports";
        }
        public static string ApplyExisting()
        {
            const string path = "Assets/_Game/Scenes/Regions/REG-S3.unity";
            var previous = SceneManager.GetActiveScene(); var scene = SceneManager.GetSceneByPath(path);
            bool opened = !scene.IsValid() || !scene.isLoaded;
            if (opened) scene = EditorSceneManager.OpenScene(path,OpenSceneMode.Additive);
            else if(scene.isDirty) throw new InvalidOperationException("Unsaved S3 changes");
            try
            {
                var result = Apply(scene.GetRootGameObjects().Single(g=>g.name=="REG-S3").transform);
                if(!string.IsNullOrEmpty(result)) EditorSceneManager.SaveScene(scene);
                return result;
            }
            finally
            {
                if(opened) EditorSceneManager.CloseScene(scene,true);
                if(previous.IsValid() && previous.isLoaded) SceneManager.SetActiveScene(previous);
            }
        }
        public static string Integrate(string asset)
        {
            string result = FurnitureReview.Integrate(asset);
            bool pump = asset.StartsWith("OBJ-046");
            var root = PrefabUtility.LoadPrefabContents(FurnitureReview.Prefab(asset));
            try
            {
                var screen = new GameObject("Status display");
                screen.transform.SetParent(root.transform, false);
                screen.transform.localPosition = pump ? new Vector3(-.012f,.177f,-.080f) : new Vector3(-.029f,.22f,-.065f);
                screen.transform.localRotation = Quaternion.identity;
                var text = screen.AddComponent<TextMesh>();
                text.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
                text.fontSize = 64; text.characterSize = .01f;
                text.anchor = TextAnchor.MiddleCenter; text.alignment = TextAlignment.Center;
                text.color = new Color(.6f,.93f,.75f);
                screen.GetComponent<MeshRenderer>().sharedMaterial = AssetDatabase.LoadAssetAtPath<Material>("Assets/_Game/Art/S1/WorldSign.mat");
                var status = root.AddComponent<ClinicalDeviceStatus>();
                status.display = text; status.isPump = pump; status.unitId = pump ? "PER-01" : "MON-01";
                status.RefreshDisplay();
                var size = screen.GetComponent<MeshRenderer>().bounds.size;
                float scale = Mathf.Min((pump ? .108f : .30f)/size.x, (pump ? .05f : .16f)/size.y);
                screen.transform.localScale = Vector3.one * scale;
                if (pump)
                {
                    var audio = root.AddComponent<AudioSource>();
                    audio.clip = AssetDatabase.LoadAssetAtPath<AudioClip>("Assets/_Game/Audio/World/SND-RELAY.wav");
                    audio.playOnAwake = false; audio.loop = false; audio.volume = .04f;
                    audio.spatialBlend = 1; audio.minDistance = .2f; audio.maxDistance = 2.5f;
                    audio.rolloffMode = AudioRolloffMode.Linear; status.clickSource = audio;
                }
                PrefabUtility.SaveAsPrefabAsset(root, FurnitureReview.Prefab(asset));
            }
            finally { PrefabUtility.UnloadPrefabContents(root); }
            AssetDatabase.SaveAssets(); return result;
        }
    }
}
