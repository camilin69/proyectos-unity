using UnityEngine;

namespace Dream
{
    // Dice que suena al pisar este collider. Los Terrain usan TerrainSurfaces (una superficie por capa).
    public class SurfaceTag : MonoBehaviour
    {
        public SurfaceType type = SurfaceType.Stone;
    }
}
