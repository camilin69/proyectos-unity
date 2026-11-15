using Unity.Cinemachine;
using UnityEngine;

namespace Dream
{
    // Las tres camaras de cine de la tecla F. Cada una se coloca sola alrededor del sonador:
    //  - Steadicam 35 mm: 3/4 frontal, retrocediendo delante de el (luce el trote).
    //  - Teleobjetivo 135 mm: lejos y bajo; el personaje pequeno contra el sueno.
    //  - Contrapicado 24 mm: a ras de suelo, el cielo domina el cuadro.
    // Siguen el rumbo del cuerpo con amortiguacion y no atraviesan paredes ni el suelo.
    [RequireComponent(typeof(CinemachineCamera))]
    public class CineRig : MonoBehaviour
    {
        public CineStyle style;
        public float positionDamping = 0.45f, headingDamping = 0.9f;

        CinemachineCamera _cam;
        Vector3 _vel;
        float _heading, _headingVel;
        bool _init;

        public static float FocalToFov(float mm, float sensorHeight = 24f) => 2f * Mathf.Atan(sensorHeight / (2f * mm)) * Mathf.Rad2Deg;

        public float FocalLength => style switch { CineStyle.Steadicam => 35f, CineStyle.Telephoto => 135f, _ => 24f };

        void Awake()
        {
            _cam = GetComponent<CinemachineCamera>();
            _cam.Lens.FieldOfView = FocalToFov(FocalLength);
            _cam.Lens.NearClipPlane = 0.05f;
            _cam.Lens.FarClipPlane = 6000f;
        }

        void OnEnable() => _init = false;

        void LateUpdate()
        {
            var rig = PlayerRig.Instance;
            if (!rig) return;
            var p = rig.transform.position;
            float yaw = rig.transform.eulerAngles.y;
            if (!_init) { _heading = yaw; }
            _heading = Mathf.SmoothDampAngle(_heading, yaw, ref _headingVel, headingDamping);
            var rot = Quaternion.Euler(0f, _heading, 0f);
            var fwd = rot * Vector3.forward; var right = rot * Vector3.right;

            Vector3 desired, look;
            switch (style)
            {
                case CineStyle.Steadicam:
                    desired = p + fwd * 2.7f + right * 0.95f + Vector3.up * 1.42f;
                    look = p + Vector3.up * 1.2f + fwd * 0.3f;
                    break;
                case CineStyle.Telephoto:
                    desired = p - fwd * 15f + right * 7.5f + Vector3.up * 1.1f;
                    look = p + Vector3.up * 1.05f;
                    break;
                default:
                    desired = p + fwd * 2.3f + right * 1.5f;
                    desired.y = GroundY(desired, p.y) + 0.2f;
                    look = p + Vector3.up * 1.75f - fwd * 0.6f;
                    break;
            }
            if (style != CineStyle.LowAngle) desired.y = Mathf.Max(desired.y, GroundY(desired, p.y) + 0.45f);
            desired = AvoidOcclusion(look, desired);

            if (!_init) { transform.position = desired; _vel = Vector3.zero; _init = true; }
            else transform.position = Vector3.SmoothDamp(transform.position, desired, ref _vel, positionDamping);
            transform.rotation = Quaternion.LookRotation(look - transform.position, Vector3.up);
        }

        static float GroundY(Vector3 at, float fallback)
        {
            if (Physics.Raycast(at + Vector3.up * 40f, Vector3.down, out var hit, 120f, ~0, QueryTriggerInteraction.Ignore)) return hit.point.y;
            return fallback;
        }

        static Vector3 AvoidOcclusion(Vector3 from, Vector3 to)
        {
            var d = to - from;
            float len = d.magnitude;
            if (len < 0.01f) return to;
            if (Physics.SphereCast(from, 0.18f, d / len, out var hit, len, ~0, QueryTriggerInteraction.Ignore)
                && !hit.collider.GetComponentInParent<PlayerRig>())
                return from + d / len * Mathf.Max(0.4f, hit.distance - 0.1f);
            return to;
        }
    }
}
