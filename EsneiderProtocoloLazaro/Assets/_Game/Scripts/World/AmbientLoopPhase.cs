using UnityEngine;

namespace Esneider.World
{
    public class AmbientLoopPhase : MonoBehaviour
    {
        public Animator animator;
        [Range(0, 1)] public float phaseOffset;
        void Start()
        {
            if (animator && animator.runtimeAnimatorController)
                animator.Play(0, 0, phaseOffset);
        }
    }
}
