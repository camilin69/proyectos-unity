using System.Collections;
using UnityEngine;
using UnityEngine.Rendering;

namespace Dream
{
    // Estrellas fugaces: cada pocos segundos una estela cruza la cupula del cielo, lejos de la camara, en una
    // direccion al azar y un poco hacia abajo, como las de verdad.
    public class ShootingStars : MonoBehaviour
    {
        public Material trail;
        public Vector2 interval = new(2.5f, 7f);
        public float distance = 1400f;
        float _next;

        void OnEnable() => _next = Time.time + 1.5f;

        void Update()
        {
            if (Time.time < _next || !trail) return;
            _next = Time.time + Random.Range(interval.x, interval.y);
            var cam = Camera.main;
            if (cam) StartCoroutine(Shoot(cam.transform.position));
        }

        IEnumerator Shoot(Vector3 origin)
        {
            var dir = Quaternion.Euler(-Random.Range(25f, 65f), Random.Range(0f, 360f), 0f) * Vector3.forward;
            var tangent = Vector3.Cross(dir, Vector3.up).normalized * (Random.value < 0.5f ? -1f : 1f);
            var vel = (tangent + Vector3.down * Random.Range(0.3f, 0.7f)).normalized * Random.Range(700f, 1100f);
            var go = new GameObject("Estrella_fugaz");
            go.transform.SetParent(transform, true);
            go.transform.position = origin + dir * distance;
            var tr = go.AddComponent<TrailRenderer>();
            tr.sharedMaterial = trail;
            tr.time = 0.35f;
            tr.widthMultiplier = 6f;
            tr.widthCurve = AnimationCurve.Linear(0f, 1f, 1f, 0f);
            tr.shadowCastingMode = ShadowCastingMode.Off;
            tr.receiveShadows = false;
            float life = Random.Range(0.6f, 1.1f);
            for (float t = 0f; t < life; t += Time.deltaTime)
            {
                go.transform.position += vel * Time.deltaTime;
                yield return null;
            }
            Destroy(go, tr.time + 0.1f);
        }
    }
}
