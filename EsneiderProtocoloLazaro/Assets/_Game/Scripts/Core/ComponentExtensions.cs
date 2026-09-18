using UnityEngine;

namespace Esneider.Core
{
    // GetComponent devuelve un "falso nulo" en el editor: ?? no sirve. Comparar con == null (unity-lifecycle: fake-null).
    public static class ComponentExtensions
    {
        public static T GetOrAdd<T>(this GameObject go) where T : Component
        {
            var c = go.GetComponent<T>();
            return c == null ? go.AddComponent<T>() : c;
        }
        public static T GetOrAdd<T>(this Component owner) where T : Component => owner.gameObject.GetOrAdd<T>();
        public static T OrNull<T>(this T obj) where T : Object => obj == null ? null : obj;
    }
}
