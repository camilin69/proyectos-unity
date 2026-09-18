using UnityEngine;

namespace Esneider.Player
{
    // Sección 9: yaw en el cuerpo, pitch en el pivote de cámara con límite; FOV vertical; retroceso pequeño sin quitar control.
    public class PlayerLook : MonoBehaviour
    {
        public Transform cameraPivot;
        public Camera playerCamera;
        public float sensitivity = 0.12f;
        public float pitchMin = -85f, pitchMax = 85f;
        public float fovVertical = 75f;
        public bool lookEnabled = true;
        float _pitch, _recoil;

        void Start() { if (playerCamera != null) playerCamera.fieldOfView = fovVertical; }

        public void Tick(Vector2 look)
        {
            if (lookEnabled)
            {
                transform.Rotate(0f, look.x * sensitivity, 0f, Space.Self);
                _pitch = Mathf.Clamp(_pitch - look.y * sensitivity, pitchMin, pitchMax);
            }
            _recoil = Mathf.MoveTowards(_recoil, 0f, 12f * Time.deltaTime);
            if (cameraPivot != null) cameraPivot.localRotation = Quaternion.Euler(_pitch - _recoil, 0f, 0f);
        }

        public void AddRecoil(float degrees) => _recoil = Mathf.Min(_recoil + degrees, 6f);
        public void SetFov(float fov) { fovVertical = Mathf.Clamp(fov, 70f, 100f); if (playerCamera != null) playerCamera.fieldOfView = fovVertical; }
        public Ray AimRay => playerCamera != null ? new Ray(playerCamera.transform.position, playerCamera.transform.forward) : new Ray(transform.position, transform.forward);
    }
}
