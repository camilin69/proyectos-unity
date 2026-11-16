using UnityEngine;

namespace Dream
{
    // Mientras esta escena esta cargada, la luna llena se queda justo encima (a 90 grados): se ve por el vidrio del
    // hueco del pasillo. Al descargarse, la luna vuelve a moverse con la hora.
    public class MoonOverhead : MonoBehaviour
    {
        static readonly Vector3 Up = new Vector3(0.02f, 1f, 0.03f).normalized;   // casi vertical (vertical exacta no tiene giro definido)

        void OnEnable() { if (TimeOfDay.Instance) TimeOfDay.Instance.moonDirection = Up; }
        void Update() { if (TimeOfDay.Instance && TimeOfDay.Instance.moonDirection != Up) TimeOfDay.Instance.moonDirection = Up; }
        void OnDisable() { if (TimeOfDay.Instance && TimeOfDay.Instance.moonDirection == Up) TimeOfDay.Instance.moonDirection = Vector3.zero; }
    }
}
