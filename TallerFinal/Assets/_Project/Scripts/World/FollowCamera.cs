using UnityEngine;

namespace Dream
{
    // Va pegado a la camara (solo la posicion): una cupula de estrellas que titilan siempre alrededor del que mira.
    public class FollowCamera : MonoBehaviour
    {
        void LateUpdate()
        {
            var cam = Camera.main;
            if (cam) transform.position = cam.transform.position;
        }
    }
}
