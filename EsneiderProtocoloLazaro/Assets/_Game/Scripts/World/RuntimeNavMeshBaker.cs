using Esneider.Core;
using Unity.AI.Navigation;
using UnityEngine;
using UnityEngine.AI;

namespace Esneider.World
{
    // Hornea el NavMesh al iniciar (sandbox y pruebas); la campaña usará superficies regionales guardadas (88.4).
    public class RuntimeNavMeshBaker : MonoBehaviour
    {
        public NavMeshSurface Surface { get; private set; }

        void Awake()
        {
            Surface = gameObject.GetOrAdd<NavMeshSurface>();
            Surface.collectObjects = CollectObjects.All; Surface.useGeometry = NavMeshCollectGeometry.PhysicsColliders;
            Surface.layerMask = GameLayers.Mask(GameLayers.WorldStatic);
            Surface.BuildNavMesh();
            foreach (var a in FindObjectsByType<NavMeshAgent>(FindObjectsSortMode.None)) { a.enabled = false; a.enabled = true; }
        }
    }
}
