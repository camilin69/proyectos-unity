using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Dream.EditorTools.Build
{
    // Construye el viaje completo: Animator desde la spec, Boot y los 8 escenarios, y deja las escenas en Build
    // Settings en orden. Es la unica forma de generar las escenas: si algo cambia, se cambia aqui y se reconstruye.
    public static class JourneyBuilder
    {
        [MenuItem("Sueno Lucido/Construir viaje completo")]
        public static string BuildAll()
        {
            var log = AnimatorBuilder.Build();
            BootBuilder.Build();
            S1Builder.Build();
            S2Builder.Build();
            S3Builder.Build();
            S4Builder.Build();
            S5Builder.Build();
            S6Builder.Build();
            S7Builder.Build();
            S8Builder.Build();
            var scenes = new[] { "Boot" }.Concat(JourneyManager.Scenes)
                .Select(n => new EditorBuildSettingsScene($"{BuildKit.SceneDir}/{n}.unity", true)).ToArray();
            EditorBuildSettings.scenes = scenes;
            AssetDatabase.SaveAssets();
            EditorSceneManager.OpenScene($"{BuildKit.SceneDir}/Boot.unity");
            return log + " | escenas: " + string.Join(", ", scenes.Select(s => System.IO.Path.GetFileNameWithoutExtension(s.path)));
        }
    }
}
