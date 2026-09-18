using UnityEngine;

namespace Esneider.Core
{
    // Capas de la sección 20.3, resueltas por nombre desde TagManager.
    public static class GameLayers
    {
        public static int Player => LayerMask.NameToLayer("Player");
        public static int Enemy => LayerMask.NameToLayer("Enemy");
        public static int WorldStatic => LayerMask.NameToLayer("WorldStatic");
        public static int DynamicProp => LayerMask.NameToLayer("DynamicProp");
        public static int PlayerProjectile => LayerMask.NameToLayer("PlayerProjectile");
        public static int EnemyProjectile => LayerMask.NameToLayer("EnemyProjectile");
        public static int Interactable => LayerMask.NameToLayer("Interactable");
        public static int Trigger => LayerMask.NameToLayer("Trigger");
        public static int Corpse => LayerMask.NameToLayer("Corpse");
        public static int VFX => LayerMask.NameToLayer("VFX");

        public static int Mask(params int[] layers) { int m = 0; foreach (var l in layers) if (l >= 0) m |= 1 << l; return m; }

        // Cobertura: lo que bloquea proyectiles, visión y golpes.
        public static int CoverMask => Mask(WorldStatic, DynamicProp);
        public static int EnemyProjectileHitMask => Mask(Player, WorldStatic, DynamicProp);
        public static int PlayerAttackMask => Mask(Enemy, WorldStatic, DynamicProp);
        public static int VisionBlockMask => Mask(WorldStatic, DynamicProp);
    }
}
