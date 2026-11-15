using System;
using UnityEngine;

namespace Dream
{
    // Andar tranquilo (1,25 m/s), trote con Shift (2,1 m/s), salto, vuelo (Q, solo donde el sueno lo permite) y
    // nado. Las velocidades coinciden con las medidas en los clips (Walk 1,27 m/s, Jog 2,07 m/s), asi los pies no
    // patinan. Base: el PlayerMotor de Esneider, con su margen de coyote y su buffer de salto.
    [RequireComponent(typeof(CharacterController))]
    public class PlayerMotor : MonoBehaviour
    {
        [Header("Suelo")] public float walkSpeed = 1.25f, jogSpeed = 2.1f;
        public float acceleration = 4.5f, deceleration = 6f;
        public float gravity = -13f, jumpSpeed = 4.3f, coyoteTime = 0.12f, jumpBufferTime = 0.15f;
        public float height = 1.7f, radius = 0.26f;
        [Header("Vuelo")] public float flySpeed = 5f, flyBoostSpeed = 11f, flyAcceleration = 3f, flyVertical = 3.5f;
        [Header("Agua")] public float swimSpeed = 1.1f, swimDepth = 1.05f, floatDepth = 1.32f, buoyancy = 3f;

        public bool controlEnabled = true;
        public bool FlightAllowed { get; private set; }
        public bool Flying { get; private set; }
        public bool Swimming { get; private set; }
        public bool Grounded { get; private set; }
        public Vector3 Velocity { get; private set; }
        public float PlanarSpeed { get; private set; }
        public bool Running { get; private set; }
        public event Action Jumped, Landed;

        [NonSerialized] public Vector3? scriptedVelocity;   // las cinematicas caminan al sonador con esto
        [NonSerialized] public Transform view;              // de donde sale la direccion del vuelo (con su inclinacion)

        CharacterController _cc;
        Vector3 _planar;
        float _vertical, _lastGrounded = -100f, _lastJumpRequest = -100f, _airTime;
        WaterZone _water;

        void Awake()
        {
            _cc = GetComponent<CharacterController>();
            _cc.height = height; _cc.radius = radius; _cc.center = new Vector3(0f, height / 2f, 0f);
            _cc.slopeLimit = 48f; _cc.stepOffset = 0.36f; _cc.skinWidth = 0.03f;
        }

        public void SetFlightAllowed(bool allowed)
        {
            FlightAllowed = allowed;
            if (!allowed) Flying = false;
        }

        public void SetFlying(bool on) { Flying = on && FlightAllowed; if (Flying) _vertical = Mathf.Max(_vertical, 1.5f); }

        public void EnterWater(WaterZone w) => _water = w;
        public void ExitWater(WaterZone w) { if (_water == w) _water = null; }

        void Update()
        {
            var input = DreamInput.Instance;
            bool playing = GameFlow.Instance == null || GameFlow.Instance.State == GameState.Playing;
            bool can = controlEnabled && playing && input != null;
            Vector2 move = can ? input.Move : Vector2.zero;
            bool run = can && input.RunHeld;
            bool jump = can && input.ConsumeJump();
            bool fly = can && input.ConsumeFly();
            float vert = can ? (input.AscendHeld ? 1f : 0f) - (input.DescendHeld ? 1f : 0f) : 0f;
            Tick(move, run, jump, fly, vert, Time.deltaTime);
        }

        public void Tick(Vector2 move, bool runHeld, bool jumpRequest, bool flyToggle, float vertical, float dt)
        {
            if (!_cc.enabled || dt <= 0f) return;
            if (flyToggle && FlightAllowed) SetFlying(!Flying);

            float submerged = _water != null ? _water.SurfaceY - transform.position.y : -1f;
            Swimming = !Flying && _water != null && submerged > swimDepth;

            if (scriptedVelocity.HasValue) TickScripted(scriptedVelocity.Value, dt);
            else if (Flying) TickFly(move, runHeld, vertical, dt);
            else if (Swimming) TickSwim(move, submerged, dt);
            else TickGround(move, runHeld, jumpRequest, dt);

            var v = new Vector3(_cc.velocity.x, 0f, _cc.velocity.z);
            PlanarSpeed = v.magnitude;
        }

        void TickGround(Vector2 move, bool runHeld, bool jumpRequest, float dt)
        {
            Running = runHeld && move.sqrMagnitude > 0.01f;
            float speed = Running ? jogSpeed : walkSpeed;
            var wish = transform.right * move.x + transform.forward * move.y;
            if (wish.sqrMagnitude > 1f) wish.Normalize();
            float rate = wish.sqrMagnitude > 0.001f ? acceleration : deceleration;
            _planar = Vector3.MoveTowards(_planar, wish * speed, rate * dt);

            bool wasGrounded = Grounded;
            Grounded = _cc.isGrounded || ProbeGround(0.12f);
            if (Grounded) _lastGrounded = Time.time;
            if (jumpRequest) _lastJumpRequest = Time.time;
            bool jump = Time.time - _lastGrounded <= coyoteTime && Time.time - _lastJumpRequest <= jumpBufferTime;
            if (jump)
            {
                _vertical = jumpSpeed;
                _lastGrounded = _lastJumpRequest = -100f;
                Grounded = false;
                Jumped?.Invoke();
            }
            else if (Grounded && _vertical <= 0f) _vertical = -2f;
            else _vertical += gravity * dt;

            Move(_planar + Vector3.up * _vertical, dt);
            if (!wasGrounded && Grounded && _airTime > 0.25f) Landed?.Invoke();
            _airTime = Grounded ? 0f : _airTime + dt;
        }

        void TickFly(Vector2 move, bool boost, float vertical, float dt)
        {
            var basis = view ? view : transform;
            var wish = basis.forward * move.y + basis.right * move.x;
            if (wish.sqrMagnitude > 1f) wish.Normalize();
            float speed = boost ? flyBoostSpeed : flySpeed;
            var target = wish * speed + Vector3.up * vertical * flyVertical;
            var cur = _planar + Vector3.up * _vertical;
            cur = Vector3.Lerp(cur, target, 1f - Mathf.Exp(-flyAcceleration * dt));
            cur.y += Mathf.Sin(Time.time * 0.9f) * 0.12f * dt;   // se flota, no se esta suspendido
            _planar = new Vector3(cur.x, 0f, cur.z); _vertical = cur.y;
            Move(cur, dt);
            Grounded = false;
            Running = boost;
            if (_cc.isGrounded && _vertical < -0.2f) { Flying = false; Landed?.Invoke(); }   // tocar suelo bajando: aterriza
        }

        void TickSwim(Vector2 move, float submerged, float dt)
        {
            var wish = transform.right * move.x + transform.forward * move.y;
            if (wish.sqrMagnitude > 1f) wish.Normalize();
            _planar = Vector3.MoveTowards(_planar, wish * swimSpeed, 2.5f * dt);
            float err = submerged - floatDepth;          // flota con la cabeza fuera: muelle amortiguado
            _vertical += (err * buoyancy * 4f - _vertical * 2.2f) * dt;
            Move(_planar + Vector3.up * _vertical, dt);
            Grounded = false;
            Running = false;
            if (wish.sqrMagnitude > 0.01f && (_cc.collisionFlags & CollisionFlags.Sides) != 0) TryClimbOut(wish.normalized);
        }

        // Nadando contra una orilla o el borde de la piscina: si arriba hay suelo a menos de 70 cm sobre el agua,
        // el sonador sale. Sin esto el nado quedaba atrapado contra cualquier borde mas alto que el stepOffset.
        void TryClimbOut(Vector3 dir)
        {
            var probe = transform.position + dir * (radius + 0.45f) + Vector3.up * (floatDepth + 1.2f);
            if (!Physics.Raycast(probe, Vector3.down, out var hit, 2.6f, ~0, QueryTriggerInteraction.Ignore)) return;
            if (hit.normal.y < 0.7f || hit.point.y <= transform.position.y + 0.1f) return;
            if (_water != null && hit.point.y - _water.SurfaceY > 0.7f) return;
            if (Physics.CheckCapsule(hit.point + Vector3.up * (radius + 0.05f), hit.point + Vector3.up * (height - radius), radius * 0.9f, ~0, QueryTriggerInteraction.Ignore)) return;
            Teleport(hit.point + Vector3.up * 0.02f, transform.eulerAngles.y);
        }

        void TickScripted(Vector3 v, float dt)
        {
            _planar = new Vector3(v.x, 0f, v.z);
            Grounded = _cc.isGrounded || ProbeGround(0.15f);
            _vertical = Grounded && v.y <= 0f ? -2f : _vertical + gravity * dt;
            if (v.y > 0f) _vertical = v.y;
            Move(_planar + Vector3.up * _vertical, dt);
            if (_planar.sqrMagnitude > 0.0004f)
            {
                var face = Quaternion.LookRotation(_planar.normalized, Vector3.up);
                transform.rotation = Quaternion.Slerp(transform.rotation, face, 1f - Mathf.Exp(-6f * dt));
            }
        }

        void Move(Vector3 v, float dt)
        {
            _cc.Move(v * dt);
            Velocity = _cc.velocity;
            if (_cc.isGrounded && _vertical < 0f && !Flying) _vertical = Mathf.Max(_vertical, -2f);
        }

        bool ProbeGround(float dist)
        {
            var origin = transform.position + Vector3.up * (radius + 0.05f);
            return Physics.SphereCast(origin, radius * 0.9f, Vector3.down, out _, dist + 0.05f, ~0, QueryTriggerInteraction.Ignore);
        }

        public void Teleport(Vector3 position, float yaw)
        {
            _cc.enabled = false;
            transform.SetPositionAndRotation(position, Quaternion.Euler(0f, yaw, 0f));
            Physics.SyncTransforms();
            _cc.enabled = true;
            _planar = Vector3.zero; _vertical = 0f; Flying = false;
        }

        public void Stop() { _planar = Vector3.zero; if (!Flying) _vertical = Mathf.Min(_vertical, 0f); }
    }
}
