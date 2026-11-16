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
        [Tooltip("Sigue a la luna en vez del sol (la luna llena grande, como un planeta)")] public bool moon;

        void LateUpdate()
        {
            var tod = TimeOfDay.Instance;
            var cam = Camera.main;
            var body = tod ? (moon ? tod.moon : tod.sun) : null;
            if (!body || !cam || !disc) return;
            bool up = body.enabled && body.transform.forward.y < 0.02f;
            disc.enabled = up;
            if (!up) return;
            var dir = -body.transform.forward;
            disc.transform.position = cam.transform.position + dir * distance;
            disc.transform.rotation = Quaternion.LookRotation(dir, Vector3.up);   // la cara visible del quad (-Z) mira a la camara
            float s = 2f * distance * Mathf.Tan(angularSizeDeg * 0.5f * Mathf.Deg2Rad);
            disc.transform.localScale = new Vector3(s, s, 1f);
        }
    }
}
