using UnityEngine;

namespace Dream
{
    // Primera persona con vaiven de boya: un Perlin lento (0,15-0,25 Hz) en cabeceo, alabeo y altura, de unos 0,6 grados
    // y 1,5 cm, mas un balanceo acoplado al paso. La opcion del menu lo escala (Completo, Suave, Apagado).
    // El raton gira el cuerpo (yaw) y la cabeza (pitch); el movimiento siempre es relativo a esta mirada,
    // tambien cuando se mira por una camara de cine.
    public class FirstPersonLook : MonoBehaviour
    {
        public Transform pivot;
        public float eyeHeight = 1.58f;
        public float minPitch = -80f, maxPitch = 82f, smoothing = 22f;
        [Header("Vaiven de boya")]
        public float swayPitchDeg = 0.6f, swayRollDeg = 0.7f, swayHeight = 0.015f;
        public float swayFreqPitch = 0.19f, swayFreqRoll = 0.23f, swayFreqHeight = 0.15f;
        [Header("Paso")] public float bobWalk = 0.009f, bobJog = 0.02f, bobRollDeg = 0.25f;
        [Header("Quieto: olas")] public float wavePeriod = 7.5f, waveRollDeg = 1.5f, wavePitchDeg = 0.9f, waveHeight = 0.028f;

        PlayerMotor _motor;
        float _yaw, _pitch, _yawT, _pitchT, _bobPhase, _bobAmp, _still, _idle;

        public float Pitch => _pitch;

        void Awake()
        {
            _motor = GetComponent<PlayerMotor>();
            _yaw = _yawT = transform.eulerAngles.y;
            if (_motor) _motor.view = pivot;
        }

        public void ResetPitch(float pitch)
        {
            _pitch = _pitchT = pitch;
            _yaw = _yawT = transform.eulerAngles.y;
        }

        void Update()
        {
            var input = DreamInput.Instance;
            var flow = GameFlow.Instance;
            bool scripted = _motor && _motor.scriptedVelocity.HasValue;
            if (input != null && flow != null && flow.State == GameState.Playing && !scripted)
            {
                float s = DreamSettings.MouseSensitivity;
                _yawT += input.Look.x * s;
                _pitchT = Mathf.Clamp(_pitchT - input.Look.y * s, minPitch, maxPitch);
            }
            if (scripted || (flow != null && flow.State == GameState.Cinematic))
            {
                // en cinematica manda el cuerpo; al volver, la mirada arranca desde donde quedo
                _yaw = _yawT = transform.eulerAngles.y;
            }
            float k = 1f - Mathf.Exp(-smoothing * Time.unscaledDeltaTime);
            _yaw = Mathf.LerpAngle(_yaw, _yawT, k);
            _pitch = Mathf.Lerp(_pitch, _pitchT, k);
            if (!scripted && (flow == null || flow.State != GameState.Cinematic))
                transform.rotation = Quaternion.Euler(0f, _yaw, 0f);
        }

        void LateUpdate()
        {
            if (!pivot) return;
            float scale = DreamSettings.SwayScale;
            float t = Time.time;
            float sp = (Mathf.PerlinNoise(t * swayFreqPitch, 1.3f) - 0.5f) * 2f * swayPitchDeg * scale;
            float sr = (Mathf.PerlinNoise(t * swayFreqRoll, 7.1f) - 0.5f) * 2f * swayRollDeg * scale;
            float sh = (Mathf.PerlinNoise(t * swayFreqHeight, 3.7f) - 0.5f) * 2f * swayHeight * scale;

            // balanceo del paso: dos golpes por zancada, mas fuerte al trotar
            float speed = _motor ? _motor.PlanarSpeed : 0f;
            bool onFoot = _motor && _motor.Grounded && !_motor.Flying && !_motor.Swimming;
            float targetAmp = onFoot ? Mathf.Lerp(0f, speed > 1.6f ? bobJog : bobWalk, Mathf.Clamp01(speed / 1.2f)) : 0f;
            _bobAmp = Mathf.Lerp(_bobAmp, targetAmp, 1f - Mathf.Exp(-6f * Time.deltaTime));
            float stepLen = speed > 1.6f ? 1.0f : 0.62f;
            _bobPhase += speed / stepLen * Mathf.PI * Time.deltaTime;
            float bob = -Mathf.Abs(Mathf.Sin(_bobPhase)) * _bobAmp * (0.4f + 0.6f * scale);
            float bobRoll = Mathf.Sin(_bobPhase) * bobRollDeg * (_bobAmp / Mathf.Max(bobJog, 1e-4f)) * scale;

            float swimDip = _motor && _motor.Swimming ? Mathf.Sin(t * 1.1f) * 0.03f : 0f;

            // quieto mas de un segundo: la camara se mece como sobre las olas del mar (rolido largo, cabeceo desfasado)
            _still = speed < 0.08f ? _still + Time.deltaTime : 0f;
            _idle = Mathf.MoveTowards(_idle, _still > 1f ? 1f : 0f, Time.deltaTime * (_still > 1f ? 0.35f : 1.5f));
            float w = 2f * Mathf.PI * t / wavePeriod;
            float wRoll = (Mathf.Sin(w) + 0.35f * Mathf.Sin(w * 2.3f + 1.1f)) * waveRollDeg * _idle * scale;
            float wPitch = Mathf.Sin(w * 0.8f + 1.7f) * wavePitchDeg * _idle * scale;
            float wHeight = Mathf.Sin(w + 0.6f) * waveHeight * _idle * scale;

            pivot.localPosition = new Vector3(0f, eyeHeight + sh + bob + swimDip + wHeight, 0.08f);
            pivot.localRotation = Quaternion.Euler(_pitch + sp + wPitch, 0f, sr + bobRoll + wRoll);
        }
    }
}
