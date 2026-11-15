using UnityEngine;

namespace Dream
{
    // Una superficie por capa del Terrain: al pisar se elige la capa con mas peso bajo el pie.
    [RequireComponent(typeof(Terrain))]
    public class TerrainSurfaces : MonoBehaviour
    {
        public SurfaceType[] layerSurfaces = { SurfaceType.Grass };

        public SurfaceType At(Vector3 world)
        {
            var t = GetComponent<Terrain>();
            var d = t.terrainData;
            if (layerSurfaces.Length == 0) return SurfaceType.Grass;
            if (d.alphamapLayers == 0) return layerSurfaces[0];
            var local = world - t.transform.position;
            int x = Mathf.Clamp(Mathf.RoundToInt(local.x / d.size.x * (d.alphamapWidth - 1)), 0, d.alphamapWidth - 1);
            int z = Mathf.Clamp(Mathf.RoundToInt(local.z / d.size.z * (d.alphamapHeight - 1)), 0, d.alphamapHeight - 1);
            var w = d.GetAlphamaps(x, z, 1, 1);
            int best = 0;
            for (int i = 1; i < d.alphamapLayers; i++) if (w[0, 0, i] > w[0, 0, best]) best = i;
            return layerSurfaces[Mathf.Min(best, layerSurfaces.Length - 1)];
        }
    }
}
