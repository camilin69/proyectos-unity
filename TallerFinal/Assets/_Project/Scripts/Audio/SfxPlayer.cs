using UnityEngine;

namespace Dream.Audio
{
    // Efectos puntuales: campanilla de recuerdo, zumbido de la puerta de luz, cualquier clip de una cinematica.
    public class SfxPlayer : MonoBehaviour
    {
        public static SfxPlayer Instance { get; private set; }
        public AudioSource source;
        public AudioClip chime;
        AudioClip _hum;

        void Awake()
        {
            Instance = this;
            if (!source) source = GetComponent<AudioSource>();
            if (!chime) chime = ProceduralAudio.Chime();
        }

        void OnDestroy() { if (Instance == this) Instance = null; }

        public void Chime(Vector3 at)
        {
            if (source && chime) source.PlayOneShot(chime, 0.9f);
            MusicPlayer.Instance?.Duck(0.45f, 2.5f);
        }

        public void LightHum()
        {
            if (!_hum) _hum = ProceduralAudio.LightHum();
            if (source) source.PlayOneShot(_hum, 0.6f);
        }

        public void Play(AudioClip clip, float volume = 1f) { if (source && clip) source.PlayOneShot(clip, volume); }
    }
}
