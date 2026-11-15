using UnityEngine;

namespace Dream
{
    // Las copas del arbol se mecen a sacudidas, como en el video de referencia: un vaiven lento y, cuando entra una
    // rafaga, un golpe brusco que se amortigua. Cada copa gira desde el punto donde nace (su base), con su propia fase.
    public class LeafSway : MonoBehaviour
    {
        public float maxDeg = 4.5f, gustDeg = 7f;
        public Vector3 pivotLocal;

        Quaternion _rest;
        Vector3 _restPos, _pivotWorld;
        float _phase, _kick, _kickVel;

        void Start()
        {
            _rest = transform.localRotation;
            _restPos = transform.localPosition;
            _pivotWorld = transform.TransformPoint(pivotLocal);
            _phase = (transform.position.x * 0.71f + transform.position.z * 0.43f) % 6.28f;
        }

        void Update()
        {
            float t = Time.time, w = Wind.Strength;
            // rafaga: cuando el viento sube de golpe, la copa recibe un empujon que oscila y se apaga
            if (w > 0.75f && Random.value < Time.deltaTime * 0.8f) _kickVel += gustDeg * (0.6f + Random.value);
            _kickVel += (-_kick * 22f - _kickVel * 3.2f) * Time.deltaTime;
            _kick += _kickVel * Time.deltaTime;
            float a = (Mathf.Sin(t * 1.3f + _phase) * 0.6f + Mathf.Sin(t * 2.9f + _phase * 1.3f) * 0.25f) * maxDeg * w + _kick;
            var axis = Vector3.Cross(Vector3.up, Wind.Direction).normalized;
            transform.localRotation = _rest;
            transform.localPosition = _restPos;
            transform.RotateAround(_pivotWorld, axis, a);
        }
    }
}
