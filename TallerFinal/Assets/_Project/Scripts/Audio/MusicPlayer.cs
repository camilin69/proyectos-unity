using UnityEngine;

namespace Dream.Audio
{
    // La cancion de fondo en bucle sin costura (el WAV ya viene preparado por tools/audio_loop.py). Cada escenario
    // la tine: paso bajo y reverb en el cuarto, el jardin de noche y la piscina; abierta en la pradera y el cielo.
    // Baja un poco cuando suena un evento (Duck).
    public class MusicPlayer : MonoBehaviour
    {
        public static MusicPlayer Instance { get; private set; }

        public AudioSource music, ambience;
        public AudioLowPassFilter lowPass;
        public AudioReverbFilter reverb;
        public float transitionSeconds = 3f;

        float _vol = 0.8f, _cut = 22000f, _rev, _ambVol;
        float _duck = 1f, _duckUntil;

        void Awake()
        {
            Instance = this;
            if (music && music.clip) { music.loop = true; music.volume = 0f; music.Play(); }
            if (reverb) reverb.reverbPreset = AudioReverbPreset.User;
        }

        void OnDestroy() { if (Instance == this) Instance = null; }

        public void ApplyScene(SceneAnchor a)
        {
            if (!a) return;
            _vol = a.musicVolume; _cut = a.musicLowPass; _rev = a.musicReverb; _ambVol = a.ambienceVolume;
            if (ambience)
            {
                if (ambience.clip != a.ambience) { ambience.clip = a.ambience; ambience.volume = 0f; if (a.ambience) ambience.Play(); }
                ambience.loop = true;
            }
        }

        public void Duck(float amount, float seconds) { _duck = 1f - amount; _duckUntil = Time.unscaledTime + seconds; }

        void Update()
        {
            float k = 1f - Mathf.Exp(-Time.unscaledDeltaTime * 3f / transitionSeconds);
            float duck = Time.unscaledTime < _duckUntil ? _duck : 1f;
            bool paused = GameFlow.Instance && GameFlow.Instance.State == GameState.Paused;
            if (music) music.volume = Mathf.Lerp(music.volume, _vol * duck * (paused ? 0.4f : 1f), k);
            if (lowPass) lowPass.cutoffFrequency = Mathf.Lerp(lowPass.cutoffFrequency, paused ? 900f : _cut, k);
            if (reverb)
            {
                reverb.dryLevel = 0f;
                reverb.room = Mathf.Lerp(reverb.room, Mathf.Lerp(-10000f, -600f, _rev), k);
                reverb.decayTime = Mathf.Lerp(1.2f, 6.5f, _rev);
                reverb.reverbLevel = Mathf.Lerp(-2000f, 200f, _rev);
            }
            if (ambience) ambience.volume = Mathf.Lerp(ambience.volume, _ambVol, k);
        }
    }
}
