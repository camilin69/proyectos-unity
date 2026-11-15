using System.Collections.Generic;
using UnityEngine;

namespace Dream
{
    // Lo que cada escenario le dice al viaje: donde aparece el sonador, a que hora, si puede volar, como
    // suena la musica alli y que cinematica de llegada tiene. Hay uno por escena aditiva.
    public class SceneAnchor : MonoBehaviour
    {
        static readonly List<SceneAnchor> All = new();

        public int index;
        public string title = "Cuarto";
        public Transform spawn;
        [Tooltip("Solo el cuarto: donde se despierta al volver al final del viaje")] public Transform finaleSpawn;
        public float startHour = 7f, endHour = 8.5f, minutesToEndHour = 4f;
        public bool allowFlight, startFlying;
        [TextArea] public string arrivalHint;
        public Cinematic.CinematicSequence arrival;
        [Tooltip("Solo el cuarto: la cinematica del regreso")] public Cinematic.CinematicSequence finaleArrival;
        [Header("Musica en este escenario")]
        [Range(200f, 22000f)] public float musicLowPass = 22000f;
        [Range(0f, 1f)] public float musicVolume = 0.8f;
        [Range(0f, 1f)] public float musicReverb = 0f;
        public AudioClip ambience;
        [Range(0f, 1f)] public float ambienceVolume = 0.6f;
        public float respawnBelowY = -60f;

        [System.NonSerialized] public bool memoryCollected;

        void OnEnable() => All.Add(this);
        void OnDisable() => All.Remove(this);

        public static SceneAnchor Find(int i) => All.Find(a => a.index == i);
    }
}
