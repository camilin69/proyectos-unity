using UnityEngine;
using UnityEngine.Rendering;

namespace Dream
{
    // Raiz del sonador: junta el motor, la camara de primera persona, el Animator y los renderers del cuerpo.
    // En primera persona el cuerpo solo proyecta sombra; en las camaras de cine y en las cinematicas se ve entero.
    [DefaultExecutionOrder(-80)]
    public class PlayerRig : MonoBehaviour
    {
        public static PlayerRig Instance { get; private set; }

        public PlayerMotor Motor;
        public PlayerAnimatorBridge Anim;
        public FirstPersonLook Look;
        public HeadLook HeadLook;
        public Renderer[] bodyRenderers;

        Vector3 _safePos; float _safeYaw;

        void Awake()
        {
            Instance = this;
            if (!Motor) Motor = GetComponent<PlayerMotor>();
            if (!Anim) Anim = GetComponentInChildren<PlayerAnimatorBridge>();
            if (!Look) Look = GetComponent<FirstPersonLook>();
            if (!HeadLook) HeadLook = GetComponentInChildren<HeadLook>();
            if (bodyRenderers == null || bodyRenderers.Length == 0) bodyRenderers = GetComponentsInChildren<Renderer>();
        }

        void OnDestroy() { if (Instance == this) Instance = null; }

        public void SetBodyVisible(bool visible)
        {
            foreach (var r in bodyRenderers)
                if (r) r.shadowCastingMode = visible ? ShadowCastingMode.On : ShadowCastingMode.ShadowsOnly;
        }

        public void PlaceAt(Transform t)
        {
            if (!t) return;
            Motor.Teleport(t.position, t.eulerAngles.y);
            if (Look) Look.ResetPitch(0f);
            SetCheckpoint(t.position, t.eulerAngles.y);
        }

        public void SetCheckpoint(Vector3 pos, float yaw) { _safePos = pos; _safeYaw = yaw; }

        public void Respawn() => StartCoroutine(RespawnRoutine());

        System.Collections.IEnumerator RespawnRoutine()
        {
            var fader = Cinematic.ScreenFader.Instance;
            if (fader) yield return fader.Fade(Color.white, 1f, 0.6f);
            Motor.Teleport(_safePos, _safeYaw);
            if (Look) Look.ResetPitch(0f);
            if (fader) yield return fader.Fade(Color.white, 0f, 0.9f);
        }
    }
}
