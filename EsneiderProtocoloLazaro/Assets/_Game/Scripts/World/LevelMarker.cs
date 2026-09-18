using UnityEngine;

namespace Esneider.World
{
    public enum MarkerKind { Spawn, Pickup, Document, Checkpoint, Mechanism, Door, Victory, Stairs }

    // Marcador de plano con identidad estable (68/88.6). La posición es la del GDD; la instancia runtime la consulta por GUID.
    public class LevelMarker : MonoBehaviour
    {
        public MarkerKind kind;
        public string stableId;
        public string guid;
        public string regionId;
        public string spaceId;
        public string subKind;
        public float yaw;
        public int amount;
        [TextArea] public string note;

        void OnDrawGizmos()
        {
            Gizmos.color = kind switch
            {
                MarkerKind.Spawn => subKind == "Boss" ? Color.magenta : subKind == "Custodio" ? new Color(1f, 0.4f, 0f) : Color.red,
                MarkerKind.Pickup => Color.yellow,
                MarkerKind.Document => Color.cyan,
                MarkerKind.Checkpoint => Color.green,
                MarkerKind.Mechanism => Color.blue,
                MarkerKind.Victory => Color.white,
                _ => Color.gray
            };
            Gizmos.DrawWireSphere(transform.position, 0.35f);
            Gizmos.DrawRay(transform.position, Quaternion.Euler(0, yaw, 0) * Vector3.forward * 1.2f);
        }
    }
}
