using UnityEngine;

namespace Dream
{
    // Si el sonador cae fuera del sueno, reaparece en el ultimo de estos que piso.
    [RequireComponent(typeof(Collider))]
    public class Checkpoint : MonoBehaviour
    {
        void Awake() => GetComponent<Collider>().isTrigger = true;

        void OnTriggerEnter(Collider other)
        {
            if (other.GetComponent<PlayerMotor>()) PlayerRig.Instance?.SetCheckpoint(transform.position, transform.eulerAngles.y);
        }
    }
}
