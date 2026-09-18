using UnityEngine;

namespace Esneider.Core.Data
{
    [CreateAssetMenu(menuName = "Esneider/Data/Player", fileName = "PlayerDefinition")]
    public class PlayerDefinition : GameDefinition
    {
        [Header("Salud (10/103)")] public int maxHp = 90;
        public float invulnerabilitySeconds = 0.65f;
        [Header("Cápsula y movimiento (9)")] public float capsuleHeight = 1.75f;
        public float capsuleRadius = 0.3f;
        public float crouchHeight = 1.1f;
        public float walkSpeed = 3f;
        public float runSpeed = 5f;
        public float crouchSpeed = 1.5f;
        [Header("Curación (10/86)")] public int syringeHeal = 45;
        public float syringeDuration = 1.6f, syringeCommit = 1.1f;
        public int rationHeal = 20;
        public float rationDuration = 2.0f, rationCommit = 1.4f;
        public int maxSyringes = 3, maxRations = 2;
        [Header("Cámara (9/81)")] public float fovVertical = 75f;
        public float fovMin = 70f, fovMax = 100f;
        [Header("Ruido base (14/78)")] public float noiseCrouch = 1.5f, noiseWalk = 4f, noiseRun = 10f;
    }
}
