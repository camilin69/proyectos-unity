using UnityEngine;

namespace Dream
{
    // El pasillo que no lleva a ningun lado: quien entra por aqui vuelve a aparecer arriba de la escalera, mirando
    // hacia abajo otra vez, sin corte ni fundido (como en los sueños, uno no nota cuando el lugar se repite).
    [RequireComponent(typeof(BoxCollider))]
    public class LoopBack : MonoBehaviour
    {
        public Transform target;

        void Reset() => GetComponent<BoxCollider>().isTrigger = true;

        void OnTriggerEnter(Collider other)
        {
            if (!target || !other.GetComponent<PlayerMotor>()) return;
            var rig = PlayerRig.Instance;
            if (rig == null) return;
            rig.Motor.Teleport(target.position, target.eulerAngles.y);
        }
    }
}
