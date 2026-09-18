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

        // 20.2: empuje limitado a cuerpos dinámicos desde contactos del controlador.
        void OnControllerColliderHit(ControllerColliderHit hit)
        {
            var rb = hit.collider.attachedRigidbody;
            if (rb == null || rb.isKinematic || hit.moveDirection.y < -0.3f) return;
            var push = new Vector3(hit.moveDirection.x, 0, hit.moveDirection.z);
            rb.AddForceAtPosition(push * Mathf.Min(pushForceMax, 2f + _planar.magnitude), hit.point, ForceMode.Impulse);
        }

        public void Teleport(Vector3 position, float yaw)
        {
            _cc.enabled = false; transform.position = position; transform.rotation = Quaternion.Euler(0, yaw, 0); _cc.enabled = true;
            _planar = Vector3.zero; _verticalVel = 0f;
        }
    }
}
