using System.Collections.Generic;

namespace Esneider.World
{
    // 88.1: siete regiones en cadena. Orígenes de 68 se conservan; cada puerta frontera tiene un único propietario.
    public static class RegionCatalog
    {
        public static readonly string[] Chain = { "REG-S1", "REG-C1", "REG-S2", "REG-C2", "REG-S3", "REG-C3", "REG-S4" };
        public const string BootScene = "BOOT";
        public static string SceneName(string regionId) => regionId;
        public static string ScenePath(string regionId) => $"Assets/_Game/Scenes/Regions/{regionId}.unity";
        public static int Index(string regionId) => System.Array.IndexOf(Chain, regionId);

        public static IEnumerable<string> Neighbors(string regionId)
        {
            int i = Index(regionId);
            if (i > 0) yield return Chain[i - 1];
            if (i >= 0 && i < Chain.Length - 1) yield return Chain[i + 1];
        }

        // Puerta frontera → (región propietaria, región al otro lado)
        public static readonly Dictionary<string, (string owner, string other)> FrontierDoors = new Dictionary<string, (string, string)>
        {
            { "D06", ("REG-S1", "REG-C1") }, { "D07", ("REG-C1", "REG-S2") },
            { "D14", ("REG-S2", "REG-C2") }, { "D15", ("REG-C2", "REG-S3") },
            { "D22", ("REG-S3", "REG-C3") }, { "D23", ("REG-C3", "REG-S4") },
        };
    }
}
