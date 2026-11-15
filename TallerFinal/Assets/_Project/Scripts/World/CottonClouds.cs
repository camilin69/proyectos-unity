using UnityEngine;

namespace Dream
{
    // Nubes de algodon de azucar: mallas densas (modeladas en Blender) que viajan despacio con el viento y respiran
    // un poco, como si se estuvieran formando. Cuando una se aleja demasiado del centro, reaparece del otro lado.
    public class CottonClouds : MonoBehaviour
    {
        public float speed = 4f, radius = 1400f;
        public Vector3 center;

        Transform[] _clouds;
        Vector3[] _scale;
        float[] _phase;

        void Awake()
        {
            int n = transform.childCount;
            _clouds = new Transform[n]; _scale = new Vector3[n]; _phase = new float[n];
            for (int i = 0; i < n; i++)
            {
                _clouds[i] = transform.GetChild(i);
                _scale[i] = _clouds[i].localScale;
                _phase[i] = i * 1.7f;
            }
        }

        void Update()
        {
            var step = Wind.Direction * (speed * Time.deltaTime);
            float t = Time.time;
            for (int i = 0; i < _clouds.Length; i++)
            {
                var c = _clouds[i];
                var p = c.position + step;
                var flat = new Vector3(p.x - center.x, 0f, p.z - center.z);
                if (flat.magnitude > radius) p -= flat.normalized * radius * 1.9f;   // vuelve a entrar por el otro lado
                c.position = p;
                float b = 1f + 0.025f * Mathf.Sin(t * 0.15f + _phase[i]);
                c.localScale = new Vector3(_scale[i].x * b, _scale[i].y * (2f - b), _scale[i].z * b);
            }
        }
    }
}
