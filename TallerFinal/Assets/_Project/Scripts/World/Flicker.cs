using UnityEngine;

namespace Dream
{
    // La luz de una antorcha: no es constante, respira y da tironcitos como una llama de verdad.
    [RequireComponent(typeof(Light))]
    public class Flicker : MonoBehaviour
    {
        public float amount = 0.35f, speed = 9f;
        Light _l;
        float _base, _seed;
        Vector3 _pos;

        void Awake()
        {
            _l = GetComponent<Light>();
            _base = _l.intensity;
            _seed = Random.value * 100f;
            _pos = transform.localPosition;
        }

        void Update()
        {
            float t = Time.time * speed + _seed;
            float n = Mathf.PerlinNoise(t, _seed) * 0.7f + Mathf.PerlinNoise(t * 2.7f, _seed + 3f) * 0.3f;
            _l.intensity = _base * (1f - amount * 0.5f + amount * n);
            transform.localPosition = _pos + new Vector3(Mathf.PerlinNoise(t * 0.5f, 1f) - 0.5f, Mathf.PerlinNoise(t * 0.5f, 2f) - 0.5f, 0f) * 0.04f;
        }
    }
}
