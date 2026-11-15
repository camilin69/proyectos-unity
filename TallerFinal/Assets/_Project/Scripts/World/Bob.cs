using UnityEngine;

namespace Dream
{
    // Flotar despacio: nubes, angeles, plumas. Cada objeto con su propia fase para que nada se mueva al unisono.
    public class Bob : MonoBehaviour
    {
        public float amplitude = 0.3f, speed = 0.35f, yawSpeed;
        Vector3 _base;
        float _phase;

        void Start() { _base = transform.localPosition; _phase = (transform.position.x * 0.37f + transform.position.z * 0.21f) % 6.28f; }

        void Update()
        {
            float t = Time.time * speed + _phase;
            transform.localPosition = _base + Vector3.up * Mathf.Sin(t) * amplitude;
            if (yawSpeed != 0f) transform.Rotate(0f, yawSpeed * Time.deltaTime, 0f, Space.World);
        }
    }
}
