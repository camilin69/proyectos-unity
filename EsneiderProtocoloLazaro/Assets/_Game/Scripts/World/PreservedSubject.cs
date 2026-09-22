using UnityEngine;

namespace Esneider.World
{
    // Ambient presentation only. A preserved person is never an enemy or damage target.
    public class PreservedSubject : MonoBehaviour
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
