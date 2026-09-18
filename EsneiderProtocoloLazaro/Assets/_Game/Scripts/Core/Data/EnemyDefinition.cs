using UnityEngine;

namespace Esneider.Core.Data
{
    public enum EnemyKind { Vigia, Custodio }

    [CreateAssetMenu(menuName = "Esneider/Data/Enemy", fileName = "EnemyDefinition")]
    public class EnemyDefinition : GameDefinition
    {
        public EnemyKind kind;
        [Header("Vida y velocidad (12/13/77)")] public int maxHp = 60;
        public float patrolSpeed = 0.7f, chaseSpeed = 2.6f;
        [Header("Percepción (14/78): normal / alerta")] public float visionRangeLit = 12f, visionAngleLit = 90f;
        public float visionRangeAlert = 16f, visionAngleAlert = 100f;
        public float visionRangeDark = 6f, visionRangeDarkAlert = 8f;
        public float closeRange = 3f, closeReaction = 0.35f;
        public float searchSeconds = 12f, combatSearchSeconds = 18f;
        [Header("Ataque (12/13/78)")] public float attackRangeMin = 3f, attackRangeMax = 9f;
        public float telegraph = 1.1f, telegraphTutorial = 1.2f;
        public float recovery = 1.4f, cooldown = 3.5f;
        public int attackDamage = 0;
        [Tooltip("Red: duración máxima de captura hasta derrota")] public float captureSeconds = 2.5f;
        public float staggerSeconds = 0.3f;
    }
}
