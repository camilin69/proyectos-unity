using UnityEngine;

namespace Dream
{
    // Los arboles lejanos son tarjetas con la imagen del arbol real (impostores renderizados en Blender): giran sobre
    // su eje vertical para mirar siempre a la camara. Asi un bosque entero cuesta lo que unas cientos de quads.
    public class Billboards : MonoBehaviour
    {
        Transform[] _cards;

        void Awake()
        {
            _cards = new Transform[transform.childCount];
            for (int i = 0; i < _cards.Length; i++) _cards[i] = transform.GetChild(i);
        }

        void LateUpdate()
        {
            var cam = Camera.main;
            if (!cam) return;
            var cp = cam.transform.position;
            foreach (var c in _cards)
            {
                var d = c.position - cp; d.y = 0f;
                if (d.sqrMagnitude > 1e-4f) c.rotation = Quaternion.LookRotation(d.normalized, Vector3.up);
            }
        }
    }
}
