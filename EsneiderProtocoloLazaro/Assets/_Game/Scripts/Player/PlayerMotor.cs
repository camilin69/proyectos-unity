using Esneider.Core;
using Esneider.Core.Data;
using UnityEngine;

namespace Esneider.Player
{
    // Sección 9/20.2: CharacterController, agacharse con comprobación de techo, resistencia, salto corto, empuje limitado a props.
    [RequireComponent(typeof(CharacterController))]
    public class PlayerMotor : MonoBehaviour
    {
        public PlayerDefinition definition;
        [Header("Parámetros 9 (VAL)")] public float walkSpeed = 3f, runSpeed = 5f, crouchSpeed = 1.5f;
        public float standHeight = 1.75f, crouchHeight = 1.1f, radius = 0.3f;
        public float interactionRange = 2f;
        public float staminaMax = 100f, staminaDrain = 22f, staminaRegen = 18f, staminaRegenDelay = 1.5f;
        public float gravity = -20f, jumpSpeed = 3.2f, acceleration = 30f;
        public float pushForceMax = 4f;
        [Header("Estado")] public float stamina = 100f;
        public bool IsCrouched { get; private set; }
        public bool IsRunning { get; private set; }
        public bool IsGrounded => _cc.isGrounded;
        public Vector3 Velocity => _velocity;
        public float SpeedFactor = 1f; // acciones (curar/recargar) pueden reducirlo
        public bool movementEnabled = true;

        CharacterController _cc;
        Vector3 _velocity, _planar;
        float _verticalVel, _lastDrainTime = -10f, _stepDistance;

        void Awake()
        {
            _cc = GetComponent<CharacterController>();
            if (definition != null)
            {
                walkSpeed = definition.walkSpeed; runSpeed = definition.runSpeed; crouchSpeed = definition.crouchSpeed;
                standHeight = definition.capsuleHeight; crouchHeight = definition.crouchHeight; radius = definition.capsuleRadius;
            }
            _cc.height = standHeight; _cc.radius = radius; _cc.center = new Vector3(0, standHeight / 2f, 0);
            _cc.slopeLimit = 45f; _cc.stepOffset = 0.35f;
            stamina = staminaMax;
        }

        public void Tick(Vector2 move, bool runHeld, bool crouchRequest, bool jumpRequest, float dt)
        {
            if (!_cc.enabled) return; // en espera de región (89.4)
            if (!movementEnabled) { move = Vector2.zero; runHeld = false; jumpRequest = false; }
            if (crouchRequest) SetCrouch(!IsCrouched);

            bool wantsRun = runHeld && !IsCrouched && move.sqrMagnitude > 0.01f && stamina > 0f;
            IsRunning = wantsRun;
            float speed = (IsCrouched ? crouchSpeed : wantsRun ? runSpeed : walkSpeed) * SpeedFactor;

            var wish = (transform.right * move.x + transform.forward * move.y);
            if (wish.sqrMagnitude > 1f) wish.Normalize();
            _planar = Vector3.MoveTowards(_planar, wish * speed, acceleration * dt);

            if (wantsRun) { stamina = Mathf.Max(0, stamina - staminaDrain * dt); _lastDrainTime = Time.time; }
            else if (Time.time - _lastDrainTime >= staminaRegenDelay) stamina = Mathf.Min(staminaMax, stamina + staminaRegen * dt);

            if (_cc.isGrounded)
            {
                _verticalVel = -2f;
                if (jumpRequest && !IsCrouched) _verticalVel = jumpSpeed;
            }
            else _verticalVel += gravity * dt;

            _velocity = _planar + Vector3.up * _verticalVel;
            _cc.Move(_velocity * dt);

            // ruido de pasos por distancia recorrida (14/96.2)
            float planarSpeed = new Vector3(_cc.velocity.x, 0, _cc.velocity.z).magnitude;
            if (_cc.isGrounded && planarSpeed > 0.2f)
            {
                _stepDistance += planarSpeed * dt;
                float stride = IsCrouched ? 1.4f : wantsRun ? 1.9f : 1.6f;
                if (_stepDistance >= stride)
                {
                    _stepDistance = 0f;
                    float r = IsCrouched ? (definition != null ? definition.noiseCrouch : 1.5f) : wantsRun ? (definition != null ? definition.noiseRun : 10f) : (definition != null ? definition.noiseWalk : 4f);
                    NoiseSystem.Emit(transform.position, r, gameObject, "footstep");
                }
            }
            else _stepDistance = 0f;
        }

        public void SetCrouch(bool crouch)
        {
            if (crouch == IsCrouched) return;
            if (!crouch && !CanStand()) return;
            IsCrouched = crouch;
            float h = crouch ? crouchHeight : standHeight;
            _cc.height = h; _cc.center = new Vector3(0, h / 2f, 0);
        }

        // 9: comprobar techo antes de levantarse.
        public bool CanStand()
        {
            var origin = transform.position + Vector3.up * (crouchHeight - radius);
            float extra = standHeight - crouchHeight + 0.05f;
            return !Physics.SphereCast(origin, radius * 0.95f, Vector3.up, out _, extra, GameLayers.Mask(GameLayers.WorldStatic, GameLayers.DynamicProp), QueryTriggerInteraction.Ignore);
        }

        public float EyeHeight => (IsCrouched ? crouchHeight : standHeight) - 0.15f;

        // 20.2/84.3: empuje de cuerpos dinámicos desde contactos del controlador (EVT-10 exige poder llevar el carro
        // hasta el panel A, así que esto es jugabilidad, no adorno).
        //
        // No se aplica un impulso fijo por frame: eso hace que la aceleración del prop dependa del framerate (a 60 fps
        // el doble de impulsos que a 30). Se controla la VELOCIDAD del prop: se lleva hacia la del jugador, con la
        // aceleración limitada por una fuerza máxima y por deltaTime, de modo que el resultado en 1 s es el mismo a
        // cualquier framerate. 84.3 acota lo alcanzable a 2 m/s lineales y 3 rad/s angulares: un prop empujado nunca
        // se convierte en proyectil.
        [Header("Empuje de props (20.2/84.3)")]
        public float pushSpeedMax = 2.0f, pushAngularMax = 3.0f;
        public float pushForceNewtons = 420f;   // fuerza de una persona empujando; con 24 kg da ~17 m/s² antes de fricción

        void OnControllerColliderHit(ControllerColliderHit hit)
        {
            var rb = hit.collider.attachedRigidbody;
            if (rb == null || rb.isKinematic || hit.moveDirection.y < -0.3f) return;
            // La dirección NO puede salir de hit.moveDirection: cuando el jugador queda bloqueado contra el prop, el
            // controlador apenas se desplaza y ese vector se anula, de modo que el empuje se apagaba justo al apoyarse.
            // La normal de contacto siempre está definida: -normal apunta del jugador hacia dentro del prop.
            // Solo se empuja de LADO. Con contacto por arriba o por abajo, la normal tiene gran componente vertical y
            // el empuje mete el prop contra la cápsula del jugador: el solver resuelve el solape desplazándolo hacia
            // arriba y el objeto acaba por los aires (84.3 lo prohíbe expresamente).
            if (Mathf.Abs(hit.normal.y) > 0.5f) return;
            var push = new Vector3(-hit.normal.x, 0f, -hit.normal.z);
            if (push.sqrMagnitude < 1e-4f) return;
            push.Normalize();
            // solo se empuja hacia donde el jugador realmente quiere ir
            if (_planar.sqrMagnitude > 1e-4f && Vector3.Dot(_planar.normalized, push) < 0.25f) return;

            float dt = Mathf.Min(Time.deltaTime, 0.05f);
            float desired = Mathf.Min(Mathf.Max(_planar.magnitude, walkSpeed * 0.6f), pushSpeedMax);
            float current = Vector3.Dot(rb.linearVelocity, push);
            if (current >= desired) return;
            float maxDv = (pushForceNewtons / Mathf.Max(0.5f, rb.mass)) * dt;   // Δv permitido este frame
            float dv = Mathf.Min(desired - current, maxDv);
            // Se empuja a la altura del centro de masas, no en el punto exacto del pie: una persona empuja un carro
            // con las manos, no le da una patada en la base. Aplicarlo abajo genera un par que lo hace girar sobre sí.
            var at = new Vector3(hit.point.x, rb.worldCenterOfMass.y, hit.point.z);
            rb.AddForceAtPosition(push * dv * rb.mass, at, ForceMode.Impulse);

            var v = rb.linearVelocity; var planar = new Vector3(v.x, 0f, v.z);
            if (planar.magnitude > pushSpeedMax) { planar = planar.normalized * pushSpeedMax; rb.linearVelocity = new Vector3(planar.x, v.y, planar.z); }
            if (rb.angularVelocity.magnitude > pushAngularMax) rb.angularVelocity = rb.angularVelocity.normalized * pushAngularMax;
        }

        public void Teleport(Vector3 position, float yaw)
        {
            // sincronizar antes de reactivar: si no, el collider renace en la posición vieja y dispara triggers de la región anterior
            _cc.enabled = false; transform.position = position; transform.rotation = Quaternion.Euler(0, yaw, 0); Physics.SyncTransforms(); _cc.enabled = true;
            World.RegionStreamer.Instance?.NotifyPlayerAt(position);
            _planar = Vector3.zero; _verticalVel = 0f;
        }
    }
}
