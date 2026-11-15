using UnityEngine;

namespace Dream
{
    // El sol visible en el cielo: un disco que brilla, siempre en la direccion de donde viene la luz del sol. Los cielos
    // de nubes (panoramas) no traen sol propio; con esto siempre se ve de donde viene la luz. Vive lejisimos (3 km), asi
    // que paredes y techos lo tapan como al sol de verdad.
    public class SunDisc : MonoBehaviour
    {
        public Renderer disc;
        public float distance = 3000f, angularSizeDeg = 2.6f;

        void LateUpdate()
        {
            var tod = TimeOfDay.Instance;
            var cam = Camera.main;
            if (!tod || !tod.sun || !cam || !disc) return;
            bool up = tod.sun.enabled && tod.sun.transform.forward.y < 0.02f;
            disc.enabled = up;
            if (!up) return;
            var dir = -tod.sun.transform.forward;
            disc.transform.position = cam.transform.position + dir * distance;
            disc.transform.rotation = Quaternion.LookRotation(-dir, Vector3.up);
            float s = 2f * distance * Mathf.Tan(angularSizeDeg * 0.5f * Mathf.Deg2Rad);
            disc.transform.localScale = new Vector3(s, s, 1f);
        }
    }
}
