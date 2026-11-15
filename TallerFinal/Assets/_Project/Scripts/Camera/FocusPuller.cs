using UnityEngine;

namespace Dream
{
    // Foquista: la profundidad de campo de HDRP usa la camara fisica, asi que alguien tiene que enfocar. Cuando se ve
    // al sonador (camaras de cine y cinematicas) el foco va a su cabeza con un diafragma abierto (bokeh real);
    // en primera persona va a lo que se mira, con el diafragma cerrado para que casi todo quede nitido.
    [DefaultExecutionOrder(10000)]
    [RequireComponent(typeof(Camera))]
    public class FocusPuller : MonoBehaviour
    {
        public float cineAperture = 2.8f, firstPersonAperture = 11f, pullSpeed = 6f;
        Camera _cam;
        float _focus = 3f;

        void Awake()
        {
            _cam = GetComponent<Camera>();
            _cam.usePhysicalProperties = true;
            _cam.sensorSize = new Vector2(36f, 24f);
            _cam.gateFit = Camera.GateFitMode.Vertical;
        }

        void LateUpdate()
        {
            var cams = CameraModeController.Instance;
            var rig = PlayerRig.Instance;
            bool cine = cams != null && cams.ShowingBody;
            float target;
            if (cine && rig) target = Vector3.Distance(transform.position, rig.transform.position + Vector3.up * 1.45f);
            else if (Physics.Raycast(transform.position, transform.forward, out var hit, 200f, ~0, QueryTriggerInteraction.Ignore)) target = hit.distance;
            else target = 200f;
            _focus = Mathf.Lerp(_focus, Mathf.Max(0.2f, target), 1f - Mathf.Exp(-pullSpeed * Time.unscaledDeltaTime));
            _cam.focusDistance = _focus;
            _cam.aperture = cine ? cineAperture : firstPersonAperture;
        }
    }
}
