using UnityEngine;

namespace Esneider.Core.Data
{
    // Sección 95.1: definiciones tipadas, inmutables en runtime. El estado mutable vive aparte.
    public abstract class GameDefinition : ScriptableObject
    {
        [Tooltip("ID estable de catálogo (GDD). Nunca cambia tras publicarse.")] public string id;
        [Tooltip("Sección del GDD que fija estos valores")] public string gddSource;
    }
}
