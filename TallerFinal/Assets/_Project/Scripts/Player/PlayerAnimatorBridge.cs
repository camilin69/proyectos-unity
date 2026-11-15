using UnityEngine;

namespace Dream
{
    // Pasa el estado del motor a los 7 parametros del Animator (los de PlayerAnimatorSpec.json).
    [RequireComponent(typeof(Animator))]
    public class PlayerAnimatorBridge : MonoBehaviour
    {
        public PlayerMotor motor;
        static readonly int Speed = Animator.StringToHash("Speed"), Grounded = Animator.StringToHash("Grounded"),
            VerticalSpeed = Animator.StringToHash("VerticalSpeed"), Flying = Animator.StringToHash("Flying"),
            Swimming = Animator.StringToHash("Swimming"), Jump = Animator.StringToHash("Jump"), Pickup = Animator.StringToHash("Pickup");

        public Animator Animator { get; private set; }

        void Awake()
        {
            Animator = GetComponent<Animator>();
            Animator.cullingMode = AnimatorCullingMode.AlwaysAnimate;   // en primera persona el cuerpo solo da sombra
            Animator.applyRootMotion = false;
            if (!motor) motor = GetComponentInParent<PlayerMotor>();
        }

        void OnEnable() { if (motor) motor.Jumped += OnJump; }
        void OnDisable() { if (motor) motor.Jumped -= OnJump; }
        void OnJump() => Animator.SetTrigger(Jump);

        public void PlayPickup() => Animator.SetTrigger(Pickup);

        void Update()
        {
            if (!motor) return;
            float dt = Time.deltaTime;
            Animator.SetFloat(Speed, motor.PlanarSpeed, 0.12f, dt);
            Animator.SetBool(Grounded, motor.Grounded || motor.Swimming);
            Animator.SetFloat(VerticalSpeed, motor.Velocity.y);
            Animator.SetBool(Flying, motor.Flying);
            Animator.SetBool(Swimming, motor.Swimming);
        }
    }
}
