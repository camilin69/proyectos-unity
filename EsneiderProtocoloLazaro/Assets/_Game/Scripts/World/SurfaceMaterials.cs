using System.Collections.Generic;
using Esneider.Core.Data;
using UnityEngine;

namespace Esneider.World
{
    // 96.1/25: la fricción es UN dato (SurfaceDefinition), no un literal repetido en cada builder. Aquí se convierte
    // ese dato en PhysicsMaterial de Unity una sola vez y se pega al collider junto con su SurfaceTag, de modo que
    // "el carro rueda distinto sobre goma que sobre suelo mojado" sea observable y medible, no una afirmación.
    public static class SurfaceMaterials
    {
        static readonly Dictionary<string, PhysicsMaterial> _cache = new Dictionary<string, PhysicsMaterial>();

        public static void Clear() => _cache.Clear();

        public static PhysicsMaterial For(string surfaceId, GameDataCatalog catalog)
        {
            if (string.IsNullOrEmpty(surfaceId)) return null;
            if (_cache.TryGetValue(surfaceId, out var m) && m != null) return m;
            var def = catalog != null && catalog.surfaces != null ? catalog.surfaces.Find(s => s.id == surfaceId) : null;
            // SUR-WHEEL no es una superficie del mundo (96.1) sino el contacto de rodadura de un carro: no vive en el
            // catálogo de superficies porque no genera pasos ni impactos propios.
            bool wheel = surfaceId == "SUR-WHEEL";
            m = new PhysicsMaterial(surfaceId)
            {
                staticFriction = wheel ? 0.12f : (def != null ? def.staticFriction : 0.65f),
                dynamicFriction = wheel ? 0.10f : (def != null ? def.dynamicFriction : 0.55f),
                bounciness = 0f,
                frictionCombine = PhysicsMaterialCombine.Average,
                bounceCombine = PhysicsMaterialCombine.Minimum,
            };
            _cache[surfaceId] = m;
            return m;
        }

        /// Aplica material físico + etiqueta de superficie a un collider (para pasos, impactos y fricción).
        public static void AttachTo(Collider c, string surfaceId, GameDataCatalog catalog)
        {
            if (c == null) return;
            var m = For(surfaceId, catalog);
            if (m != null) c.sharedMaterial = m;
            var tag = c.GetComponent<SurfaceTag>() ?? c.gameObject.AddComponent<SurfaceTag>();
            tag.surfaceId = surfaceId;
        }

        /// Marca el suelo bajo un objeto: sin esto, el prop rueda sobre el material por defecto de Unity y la
        /// diferencia entre superficies no existe físicamente.
        public static Collider TagFloorUnder(Vector3 worldPos, string surfaceId, GameDataCatalog catalog, float maxDistance = 4f)
        {
            if (Physics.Raycast(worldPos + Vector3.up * 0.5f, Vector3.down, out var hit, maxDistance,
                                Core.GameLayers.Mask(Core.GameLayers.WorldStatic), QueryTriggerInteraction.Ignore))
            {
                AttachTo(hit.collider, surfaceId, catalog);
                return hit.collider;
            }
            return null;
        }
    }
}
