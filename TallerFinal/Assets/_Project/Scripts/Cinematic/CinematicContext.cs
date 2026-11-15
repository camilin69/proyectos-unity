using System.Collections;
using Unity.Cinemachine;
using UnityEngine;

namespace Dream.Cinematic
{
    // Lo que una cinematica puede usar: la camara de rodaje, el sonador, el fundido y la marca de saltar (Tab).
    public class CinematicContext
    {
        public CinemachineCamera camera;
        public PlayerRig rig;
        public ScreenFader fader;
        public bool Skipping;

        public IEnumerator Wait(float seconds)
        {
            for (float t = 0f; t < seconds && !Skipping; t += Time.deltaTime) yield return null;
        }
    }
}
