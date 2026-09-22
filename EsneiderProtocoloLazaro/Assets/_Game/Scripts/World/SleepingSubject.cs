using UnityEngine;

namespace Esneider.World
{
    // Presentation only: no combat, health, navigation, or independent story state.
    public class SleepingSubject : MonoBehaviour
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
