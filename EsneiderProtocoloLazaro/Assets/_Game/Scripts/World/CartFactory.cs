using Esneider.Core;
using Esneider.Core.Data;
using UnityEngine;

namespace Esneider.World
{
    // 25 (Rigidbody funcional + colisión por código) y 84.1/84.3: montaje único del carro empujable.
    // El builder de escena y la prueba PlayMode llaman AQUÍ, para que lo que se verifica sea exactamente lo que se juega.
    public static class CartFactory
    {
        public const float Mass = 24f;
        public const float LinearDamping = 0.4f, AngularDamping = 1.5f;
        public static readonly Vector3 ColliderSize = new Vector3(1.0f, 0.9f, 0.6f);
        public static readonly Vector3 ColliderCenter = new Vector3(0f, 0.45f, 0f);
        public static readonly Vector3 CenterOfMass = new Vector3(0f, 0.15f, 0f);

        /// Convierte un visual ya instanciado en carro físico. Devuelve el Rigidbody.
        public static Rigidbody Make(GameObject go, string stableId, string regionId, string floorSurface, GameDataCatalog catalog)
        {
            foreach (var c in go.GetComponentsInChildren<Collider>())
            {
                if (Application.isPlaying) Object.Destroy(c); else Object.DestroyImmediate(c);
            }
            go.layer = GameLayers.DynamicProp;
            foreach (var t in go.GetComponentsInChildren<Transform>()) t.gameObject.layer = GameLayers.DynamicProp;

            var bc = go.AddComponent<BoxCollider>(); bc.center = ColliderCenter; bc.size = ColliderSize;
            // El carro RUEDA: su contacto con el suelo es de rodadura, no de arrastre. Darle la fricción del caucho de
            // la rueda (SUR-BOT) dejaría el carro clavado; se usa una resistencia baja propia para que la diferencia
            // que el jugador percibe venga del SUELO (goma del taller contra suelo mojado del patio), como pide 96.
            if (catalog != null) SurfaceMaterials.AttachTo(bc, "SUR-WHEEL", catalog);

            var rb = go.AddComponent<Rigidbody>();
            rb.mass = Mass; rb.centerOfMass = CenterOfMass;
            rb.linearDamping = LinearDamping; rb.angularDamping = AngularDamping;
            rb.collisionDetectionMode = CollisionDetectionMode.Continuous;
            rb.interpolation = RigidbodyInterpolation.Interpolate;   // 84.3: sin micro-tembleque al reposar
            go.AddComponent<PropLimits>();                            // 84.3: 2 m/s y 3 rad/s como tope del prop
            go.AddComponent<PhysicsImpactLogger>();

            // 96: el suelo bajo el carro recibe su material físico; sin esto la fricción por superficie no existe
            if (catalog != null && !string.IsNullOrEmpty(floorSurface))
                SurfaceMaterials.TagFloorUnder(go.transform.position, floorSurface, catalog);

            if (!string.IsNullOrEmpty(stableId)) SandboxFactory.Persist(go, stableId, regionId, Core.Persistence.EntityKind.Movable);
            return rb;
        }
    }
}
