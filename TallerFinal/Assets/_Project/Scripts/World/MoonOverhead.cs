using UnityEngine;

namespace Dream
{
    // Mientras esta escena esta cargada, la luna llena se queda en una direccion fija: justo encima en el pasillo
    // (se ve por el vidrio del hueco), o detras del que sube en la escalera (para no tapar el meteorito). Al
    // descargarse, la luna vuelve a moverse con la hora.
    public class MoonOverhead : MonoBehaviour
    {
        [Tooltip("Hacia donde esta la luna (casi vertical = encima; la vertical exacta no tiene giro definido)")]
        public Vector3 direction = new Vector3(0.02f, 1f, 0.03f);

        Vector3 Dir => direction.normalized;

        void OnEnable() { if (TimeOfDay.Instance) TimeOfDay.Instance.moonDirection = Dir; }
        void Update() { if (TimeOfDay.Instance && TimeOfDay.Instance.moonDirection != Dir) TimeOfDay.Instance.moonDirection = Dir; }
        void OnDisable() { if (TimeOfDay.Instance && TimeOfDay.Instance.moonDirection == Dir) TimeOfDay.Instance.moonDirection = Vector3.zero; }
    }
}
