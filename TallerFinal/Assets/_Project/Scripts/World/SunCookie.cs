using UnityEngine;
using UnityEngine.Rendering.HighDefinition;

namespace Dream
{
    // Sombras de nubes que pasan por el campo: un cookie de manchas suaves en el sol, que se desliza con el viento.
    // Lo pone el escenario al entrar y lo quita al salir (el sol vive en Boot y lo comparten todos).
    public class SunCookie : MonoBehaviour
    {
        public Texture2D cookie;
        public float size = 260f, speed = 2.2f;
        Light _sun;
        HDAdditionalLightData _hd;
        Vector3 _base;

        void OnEnable()
        {
            _sun = TimeOfDay.Instance ? TimeOfDay.Instance.sun : null;
            if (!_sun) return;
            _hd = _sun.GetComponent<HDAdditionalLightData>();
            _base = _sun.transform.position;
            if (_hd && cookie) _hd.SetCookie(cookie, new Vector2(size, size));
        }

        void OnDisable()
        {
            if (_sun) _sun.cookie = null;          // SetCookie(null) de HDRP lanza una excepcion: se quita en la luz
            if (_sun) _sun.transform.position = _base;
        }

        void Update()
        {
            // en un sol direccional el cookie se proyecta desde su posicion: moverla desliza las sombras
            if (_sun) _sun.transform.position = _base + Wind.Direction * (Time.time * speed);
        }
    }
}
