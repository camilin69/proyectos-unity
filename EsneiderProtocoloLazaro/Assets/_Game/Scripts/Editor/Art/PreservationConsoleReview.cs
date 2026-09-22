using System;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using Esneider.World;

namespace Esneider.EditorTools
{
    public static class PreservationConsoleReview
    {
        public const string Asset = "OBJ-003_ConsolaPreservacion";
        public static string Integrate()
        {
            string report = FurnitureReview.Integrate(Asset);
            var root = PrefabUtility.LoadPrefabContents(FurnitureReview.Prefab(Asset));
            try
            {
                var screen = new GameObject("Preservation readout"); screen.transform.SetParent(root.transform, false);
                screen.transform.localRotation = Quaternion.Euler(20, 0, 0);
                screen.transform.localPosition = new Vector3(0, .958f, 0) + screen.transform.localRotation * new Vector3(0, .035f, -.107f);
                var text = screen.AddComponent<TextMesh>(); text.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
                text.fontSize = 64; text.characterSize = .01f; text.anchor = TextAnchor.MiddleCenter; text.alignment = TextAlignment.Center;
                text.color = new Color(.60f, .90f, .80f); text.text = "LÁZARO / ESNEIDER\nTIEMPO TRANSCURRIDO\n2000 AÑOS\nREGISTRO CONFIRMADO";
                screen.GetComponent<MeshRenderer>().sharedMaterial = AssetDatabase.LoadAssetAtPath<Material>("Assets/_Game/Art/S1/WorldSign.mat");
                var bounds = screen.GetComponent<MeshRenderer>().localBounds;
                screen.transform.localScale = Vector3.one * Mathf.Min(.51f / bounds.size.x, .24f / bounds.size.y);
                var status = root.AddComponent<PreservationConsole>(); status.display = text;
                var sound = root.AddComponent<AudioSource>(); sound.clip = AssetDatabase.LoadAssetAtPath<AudioClip>("Assets/_Game/Audio/World/SND-RELAY.wav");
                sound.playOnAwake = false; sound.loop = false; sound.volume = .06f; sound.spatialBlend = 1; sound.minDistance = .3f; sound.maxDistance = 3; sound.rolloffMode = AudioRolloffMode.Linear;
                status.confirmationSound = sound; status.RefreshDisplay();
                foreach (var t in root.GetComponentsInChildren<Transform>()) { t.gameObject.layer = Esneider.Core.GameLayers.WorldStatic; t.gameObject.isStatic = false; }
                PrefabUtility.SaveAsPrefabAsset(root, FurnitureReview.Prefab(Asset));
            }
            finally { PrefabUtility.UnloadPrefabContents(root); }
            AssetDatabase.SaveAssets(); return report;
        }
        public static string Apply(Transform root, string region)
        {
            if (region != "REG-S1") return "";
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(FurnitureReview.Prefab(Asset)); if (!prefab) return "";
            var all = root.GetComponentsInChildren<Transform>(true); if (all.Any(t => t.name == "M002_Preservation_EX42")) return "";
            var old = all.Single(t => t.name == "M002_OBJ-059");
            var wrapper = new GameObject("M002_Preservation_EX42").transform; wrapper.SetParent(old.parent, false); wrapper.SetPositionAndRotation(old.position, old.rotation);
            var go = (GameObject)PrefabUtility.InstantiatePrefab(prefab, wrapper); go.transform.localPosition = Vector3.zero; go.transform.localRotation = Quaternion.identity; go.transform.localScale = Vector3.one;
            old.gameObject.SetActive(false); return "M002 preservation console installed";
        }
        public static string ApplyExisting()
        {
            var previous = SceneManager.GetActiveScene(); const string path = "Assets/_Game/Scenes/Regions/REG-S1.unity";
            var scene = SceneManager.GetSceneByPath(path); bool opened = !scene.IsValid() || !scene.isLoaded;
            if (opened) scene = EditorSceneManager.OpenScene(path, OpenSceneMode.Additive); else if (scene.isDirty) throw new InvalidOperationException("Unsaved REG-S1");
            try { var result = Apply(scene.GetRootGameObjects().Single(g => g.name == "REG-S1").transform, "REG-S1"); if (result != "") EditorSceneManager.SaveScene(scene); return result; }
            finally { if (opened) EditorSceneManager.CloseScene(scene, true); if (previous.IsValid() && previous.isLoaded) SceneManager.SetActiveScene(previous); }
        }
    }
}
