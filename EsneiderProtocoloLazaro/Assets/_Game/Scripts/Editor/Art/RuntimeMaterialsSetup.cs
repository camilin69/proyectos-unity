using System.IO;
using UnityEditor;
using UnityEngine;

namespace Esneider.EditorTools
{
    // Materiales que el runtime crea por código (proyectiles, anillo de pulso, placeholders). `Shader.Find` devuelve null en la build
    // cuando el shader no está referenciado por ningún material incluido (stripping): la primera medición de sesión registró 392 211
    // excepciones en Projectile.Create y los bots nunca disparaban en la build. Se materializan como assets bajo Resources/.
    public static class RuntimeMaterialsSetup
    {
        public const string Dir = "Assets/_Game/Resources/Materials";

        public static string Ensure()
        {
            Directory.CreateDirectory(Dir);
            Make("Projectile_Net", "Universal Render Pipeline/Unlit", new Color(0.4f, 0.7f, 1f));
            Make("Projectile_Bolt", "Universal Render Pipeline/Unlit", new Color(1f, 0.9f, 0.3f));
            Make("Projectile_BossBolt", "Universal Render Pipeline/Unlit", new Color(1f, 0.55f, 0.25f));
            Make("Placeholder_Lit", "Universal Render Pipeline/Lit", new Color(0.6f, 0.6f, 0.6f));
            Make("Pulse_Ring", "Universal Render Pipeline/Unlit", new Color(0.9f, 0.3f, 0.2f));
            AssetDatabase.SaveAssets();
            return "runtime materials ok";
        }

        static void Make(string name, string shaderName, Color c)
        {
            string path = $"{Dir}/{name}.mat";
            var m = AssetDatabase.LoadAssetAtPath<Material>(path);
            var shader = Shader.Find(shaderName);
            if (m == null) { m = new Material(shader); AssetDatabase.CreateAsset(m, path); }
            else if (m.shader != shader) m.shader = shader;
            if (m.HasProperty("_BaseColor")) m.SetColor("_BaseColor", c); m.color = c;
            EditorUtility.SetDirty(m);
        }
    }
}
