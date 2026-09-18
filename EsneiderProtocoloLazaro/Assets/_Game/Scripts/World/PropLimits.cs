using UnityEngine;

namespace Esneider.World
{
    // 84.3: "ningún objeto empujado se convierte en proyectil". El tope es una propiedad DEL PROP, no de quien lo
    // empuja: un golpe de varilla, un impacto o una puerta al cerrarse también pueden acelerarlo. Se aplica cada paso
    // de física, no solo en el frame del contacto.
    [RequireComponent(typeof(Rigidbody))]
    public class PropLimits : MonoBehaviour
    {
        public float maxLinearSpeed = 2.0f;
        public float maxAngularSpeed = 3.0f;
        // Un prop empujado contra el jugador puede trepar por la cápsula del controlador y salir volando: el solver
        // resuelve el solape a lo largo de la normal de la cápsula, que cerca de la base apunta hacia arriba. Eso es
        // exactamente "convertirse en proyectil". La caída libre sigue permitida (solo se acota el impulso hacia arriba).
        public float maxUpwardSpeed = 0.6f;
        Rigidbody _rb;

        void Awake()
        {
            _rb = GetComponent<Rigidbody>();
            _rb.maxAngularVelocity = maxAngularSpeed;   // tope duro del motor, además del recorte por paso
        }

        void FixedUpdate()
        {
            if (_rb == null || _rb.isKinematic) return;
            var v = _rb.linearVelocity;
            var planar = new Vector3(v.x, 0f, v.z);
            float vy = Mathf.Min(v.y, maxUpwardSpeed);
            if (planar.magnitude > maxLinearSpeed) planar = planar.normalized * maxLinearSpeed;
            if (planar != new Vector3(v.x, 0f, v.z) || !Mathf.Approximately(vy, v.y))
                _rb.linearVelocity = new Vector3(planar.x, Mathf.Max(vy, -25f), planar.z);
            if (_rb.angularVelocity.magnitude > maxAngularSpeed)
                _rb.angularVelocity = _rb.angularVelocity.normalized * maxAngularSpeed;
        }
    }
}
