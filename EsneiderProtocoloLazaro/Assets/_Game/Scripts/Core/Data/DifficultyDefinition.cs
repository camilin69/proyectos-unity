using UnityEngine;

namespace Esneider.Core.Data
{
    [CreateAssetMenu(menuName = "Esneider/Data/Difficulty", fileName = "DifficultyDefinition")]
    public class DifficultyDefinition : GameDefinition
    {
        public string presetName = "Normal";
        [Header("Modificadores explícitos (80.3/95.2). Normal = 1")] public float enemyDamageMultiplier = 1f;
        public float playerDamageMultiplier = 1f;
        public float telegraphMultiplier = 1f;
        public float perceptionRangeMultiplier = 1f;
        public float ammoDropMultiplier = 1f;
    }
}
