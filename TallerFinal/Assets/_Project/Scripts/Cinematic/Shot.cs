using System;
using UnityEngine;
using UnityEngine.Events;

namespace Dream.Cinematic
{
    // Un plano: la camara va de 'from' a 'to' (o gira alrededor de orbitCenter), mira a lookAt o a la cabeza del
    // sonador, con una focal real; el sonador puede caminar hasta un punto, moverse con una velocidad, recibir un
    // trigger del Animator y girar la cabeza hacia algo. Cada plano puede fundir desde y hacia un color.
    [Serializable]
    public class Shot
    {
        public string note;
        public float duration = 3f;
        [Header("Camara")]
        public Transform from;
        public Transform to;
        public Transform orbitCenter;
        public float orbitDegrees;
        public Transform lookAt;
        public bool lookAtActorHead;
        public float focalLength = 35f, focalLengthEnd = -1f;
        public bool cut = true;
        [Header("Sonador")]
        public Transform actorTeleport;
        public Transform actorWalkTo;
        public float actorSpeed = 1.25f;
        public Vector3 actorVelocity;
        public string actorTrigger;
        public Transform headLookAt;
        public bool hideActor;
        [Header("Fundidos y hora")]
        public Color fadeColor = Color.black;
        public float fadeInSeconds, fadeOutSeconds;
        public float setHour = -1f, hourSeconds;
        public UnityEvent onStart, onEnd;
    }
}
