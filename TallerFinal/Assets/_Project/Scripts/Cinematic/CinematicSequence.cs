using System.Collections;
using UnityEngine;

namespace Dream.Cinematic
{
    // Una cinematica. La de salida vive en la escena que se deja; la de llegada en la escena a la que se llega,
    // asi cada una usa las coordenadas de su propio escenario.
    public abstract class CinematicSequence : MonoBehaviour
    {
        public abstract IEnumerator Run(CinematicContext ctx);
    }
}
