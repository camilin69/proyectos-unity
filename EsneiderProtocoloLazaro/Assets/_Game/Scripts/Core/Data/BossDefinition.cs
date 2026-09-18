using System;
using System.Collections.Generic;
using UnityEngine;

namespace Esneider.Core.Data
{
    [Serializable]
    public class BossAttackDefinition
    {
        public string id;
        public int damage;
        public float telegraph, recovery;
        public float radius;
        public int phaseFrom = 1;
    }

    [CreateAssetMenu(menuName = "Esneider/Data/Boss", fileName = "BossDefinition")]
    public class BossDefinition : GameDefinition
    {
        [Header("15/61/79/103")] public int maxHp = 1200;
        public int phase2Threshold = 800, phase3Threshold = 400;
        public float phaseTransitionSeconds = 2f;
        public float doubleSequenceGap = 0.8f, doubleSequenceRecovery = 2.5f;
        public List<BossAttackDefinition> attacks = new List<BossAttackDefinition>();
    }
}
