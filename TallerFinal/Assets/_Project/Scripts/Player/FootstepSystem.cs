using UnityEngine;

namespace Dream
{
    // Pasos en el contacto real del pie. No hay temporizador: se mira la altura de cada tobillo respecto a la raiz
    // y se dispara el paso cuando baja hasta su altura de apoyo (con histeresis para no repetir). Asi el sonido cae
    // justo cuando el pie toca, en Walk, en Jog y en las cinematicas. La superficie sale de un rayo bajo el pie:
    // SurfaceTag, la capa del Terrain o el agua poco profunda.
    public class FootstepSystem : MonoBehaviour
    {
        public Animator animator;
        public PlayerMotor motor;
        public FootstepBank[] banks;
        public FootstepBank landBank;
        public AudioSource source;
        public float plantMargin = 0.022f, liftMargin = 0.05f;

        Transform _l, _r;
        float _rest;
        bool _upL, _upR;
        float _lastStep;

        void Start()
        {
            if (!animator) animator = GetComponentInChildren<Animator>();
            if (!motor) motor = GetComponent<PlayerMotor>();
            if (!source) source = GetComponent<AudioSource>();
            _l = animator ? animator.GetBoneTransform(HumanBodyBones.LeftFoot) : null;
            _r = animator ? animator.GetBoneTransform(HumanBodyBones.RightFoot) : null;
            // altura del tobillo de pie: alrededor de 8 cm sobre la planta
            float l = _l ? _l.position.y - transform.position.y : 0.08f, r = _r ? _r.position.y - transform.position.y : 0.08f;
            _rest = Mathf.Clamp(Mathf.Min(l, r), 0.04f, 0.11f);
            if (motor) motor.Landed += OnLand;
        }

        void OnDestroy() { if (motor) motor.Landed -= OnLand; }

        void LateUpdate()
        {
            if (!_l || !_r || motor == null) return;
            bool active = (motor.Grounded || motor.scriptedVelocity.HasValue) && !motor.Flying && !motor.Swimming && motor.PlanarSpeed > 0.25f;
            Check(_l, ref _upL, active);
            Check(_r, ref _upR, active);
        }

        void Check(Transform foot, ref bool up, bool active)
        {
            float h = foot.position.y - transform.position.y;
            if (h > _rest + liftMargin) { up = true; return; }
            if (up && h < _rest + plantMargin)
            {
                up = false;
                if (active && Time.time - _lastStep > 0.18f) { _lastStep = Time.time; Play(foot.position, 1f, null); }
            }
        }

        void OnLand() { if (_l) Play(_l.position, 1.25f, landBank); }

        public static SurfaceType SurfaceAt(Vector3 footPos)
        {
            if (Physics.Raycast(footPos + Vector3.up * 0.3f, Vector3.down, out var hit, 0.9f, ~0, QueryTriggerInteraction.Collide))
            {
                var water = hit.collider.GetComponent<WaterZone>();
                if (water) return water.shallowSurface;
                var tag = hit.collider.GetComponentInParent<SurfaceTag>();
                if (tag) return tag.type;
                var ts = hit.collider.GetComponent<TerrainSurfaces>();
                if (ts) return ts.At(hit.point);
            }
            return SurfaceType.Stone;
        }

        void Play(Vector3 at, float gain, FootstepBank forced)
        {
            if (!source) return;
            var surface = SurfaceAt(at);
            var bank = forced;
            if (bank == null && banks != null)
                foreach (var b in banks) if (b && b.surface == surface) { bank = b; break; }
            if (bank == null) return;
            var clip = bank.Pick();
            if (!clip) return;
            source.pitch = Random.Range(bank.pitch.x, bank.pitch.y) * (motor.Running ? 1.04f : 1f);
            source.PlayOneShot(clip, bank.volume * gain * Random.Range(bank.volumeJitter.x, bank.volumeJitter.y) * (motor.Running ? 1.15f : 1f));
        }
    }
}
