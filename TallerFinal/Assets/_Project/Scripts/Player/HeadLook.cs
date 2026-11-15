using UnityEngine;

namespace Dream
{
    // Mirada Humanoid: la cabeza gira hacia un objetivo (la puerta de luz, el hueco del arbol). Necesita IK Pass
    // en la capa base, que AnimatorBuilder activa.
    [RequireComponent(typeof(Animator))]
    public class HeadLook : MonoBehaviour
    {
        public Transform target;
        [Range(0f, 1f)] public float bodyWeight = 0.15f, headWeight = 0.9f, clamp = 0.55f;
        public float blendSpeed = 1.6f;
        float _w;
        Animator _a;

        void Awake() => _a = GetComponent<Animator>();

        void OnAnimatorIK(int layer)
        {
            _w = Mathf.MoveTowards(_w, target ? 1f : 0f, blendSpeed * Time.deltaTime);
            if (_w <= 0f) { _a.SetLookAtWeight(0f); return; }
            _a.SetLookAtWeight(_w, bodyWeight, headWeight, 0f, clamp);
            if (target) _a.SetLookAtPosition(target.position);
        }
    }
}
