using UnityEngine;

namespace Dream
{
    // Puente para que las cinematicas de una escena disparen sonidos del Boot (que vive en otra escena).
    public class SfxCue : MonoBehaviour
    {
        public AudioClip clip;
        [Range(0f, 1f)] public float volume = 1f;

        public void PlayClip() => Audio.SfxPlayer.Instance?.Play(clip, volume);
        public void LightHum() => Audio.SfxPlayer.Instance?.LightHum();
        public void Silence() => Audio.MusicPlayer.Instance?.Duck(1f, 3.5f);
        public void Duck() => Audio.MusicPlayer.Instance?.Duck(0.5f, 4f);
    }
}
