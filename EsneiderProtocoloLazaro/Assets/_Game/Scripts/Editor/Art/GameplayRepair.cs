using System.Linq;
using Esneider.Core;
using Esneider.Core.Data;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Esneider.EditorTools
{
    public static class GameplayRepair
    {
        public static string Apply()
        {
            var plan = JsonUtility.FromJson<LevelPlan>(AssetDatabase.LoadAssetAtPath<TextAsset>(LevelPlan.DefaultAssetPath).text);
            int walls = 0;
            foreach (string region in new[] { "REG-S1", "REG-S2" })
            {
                var path = "Assets/_Game/Scenes/Regions/" + region + ".unity";
                var scene = UnityEngine.SceneManagement.SceneManager.GetSceneByPath(path);
                bool opened = !scene.IsValid() || !scene.isLoaded;
                if (opened) scene = EditorSceneManager.OpenScene(path, OpenSceneMode.Additive);
                if (scene.isDirty) throw new System.InvalidOperationException("Unsaved scene: " + path);
                foreach (var s in plan.stairs.Where(s => plan.Floor(s.lowerFloor).region == region))
                {
                    var root = scene.GetRootGameObjects().SelectMany(g => g.GetComponentsInChildren<Transform>(true)).First(t => t.name == s.id);
                    var floor = plan.Floor(s.lowerFloor);
                    float gap = s.rise - floor.height;
                    if (gap <= 0 || root.Find("ShaftGapClosure")) continue;
                    var shell = new GameObject("ShaftGapClosure").transform; shell.SetParent(root, false);
                    var material = root.GetComponentInChildren<Renderer>().sharedMaterial;
                    void Wall(string name, Vector3 center, Vector3 size)
                    {
                        var go = GameObject.CreatePrimitive(PrimitiveType.Cube); go.name = name; go.transform.SetParent(shell, false);
                        go.transform.localPosition = center; go.transform.localScale = size; go.layer = GameLayers.WorldStatic;
                        go.GetComponent<Renderer>().sharedMaterial = material; go.isStatic = true; walls++;
                    }
                    float y = (floor.height + s.rise) * .5f;
                    Wall("West", new Vector3(s.x-.1f,y,s.z+s.d*.5f), new Vector3(.2f,gap+.04f,s.d+.4f));
                    Wall("East", new Vector3(s.x+s.w+.1f,y,s.z+s.d*.5f), new Vector3(.2f,gap+.04f,s.d+.4f));
                    Wall("South", new Vector3(s.x+s.w*.5f,y,s.z-.1f), new Vector3(s.w,.04f+gap,.2f));
                    Wall("North", new Vector3(s.x+s.w*.5f,y,s.z+s.d+.1f), new Vector3(s.w,.04f+gap,.2f));
                }
                EditorSceneManager.SaveScene(scene);
                if (opened) EditorSceneManager.CloseScene(scene,true);
            }
            return walls + " shaft walls added";
        }
    }
}
