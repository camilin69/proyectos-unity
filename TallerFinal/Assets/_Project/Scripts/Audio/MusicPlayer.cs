using UnityEngine;

namespace Dream.Audio
{
    // Banda sonora con dos platos, como un DJ: en el menu suena la cancion del menu en bucle; al empezar el viaje se
    // funde con la primera pista y desde ahi cada cancion, al acercarse a su final, se funde con la siguiente
    // (fundido de igual potencia). La lista da la vuelta. Cada escenario tine la musica: paso bajo y reverb en el
    // cuarto, el jardin de noche y la piscina; abierta en la pradera y el cielo. Baja un poco cuando suena un evento.
    public class MusicPlayer : MonoBehaviour
    {
        public static MusicPlayer Instance { get; private set; }

        [Tooltip("Dos fuentes, cada una con su paso bajo y su reverb")] public AudioSource[] decks = new AudioSource[2];
        public AudioClip menu;
        public AudioClip[] playlist;
        public float crossfadeSeconds = 8f;
        public AudioSource ambience;
        public float transitionSeconds = 3f;

        public AudioSource music => decks != null && decks.Length > 0 ? decks[_active] : null;
        public int Track { get; private set; } = -1;
        public bool InMenu { get; private set; } = true;

        int _active;
        float _fade = 1f, _fadeSpeed;        // peso del plato activo (0..1); el otro recibe 1 - _fade
        float _vol = 0.8f, _cut = 22000f, _rev, _ambVol;
        float _duck = 1f, _duckUntil;
        AudioLowPassFilter[] _lp;
        AudioReverbFilter[] _rv;

        void Awake()
        {
            Instance = this;
            _lp = new AudioLowPassFilter[decks.Length];
            _rv = new AudioReverbFilter[decks.Length];
            for (int i = 0; i < decks.Length; i++)
            {
                if (!decks[i]) continue;
                decks[i].loop = false; decks[i].playOnAwake = false; decks[i].volume = 0f; decks[i].spatialBlend = 0f;
                _lp[i] = decks[i].GetComponent<AudioLowPassFilter>();
                _rv[i] = decks[i].GetComponent<AudioReverbFilter>();
                if (_rv[i]) _rv[i].reverbPreset = AudioReverbPreset.User;
            }
        }

        void Start()
        {
            if (menu) PlayOn(_active, menu, true, 0f);
            _fadeSpeed = 1f / 3f;                                   // la cancion del menu entra suave
            if (GameFlow.Instance) GameFlow.Instance.StateChanged += OnState;
        }

        void OnDestroy()
        {
            if (GameFlow.Instance) GameFlow.Instance.StateChanged -= OnState;
            if (Instance == this) Instance = null;
        }

        void OnState(GameState s)
        {
            // al dejar la intro empieza la lista
            if (InMenu && s is GameState.Playing or GameState.Cinematic) { InMenu = false; Next(); }
        }

        void PlayOn(int deck, AudioClip clip, bool loop, float startWeight)
        {
            var d = decks[deck];
            d.clip = clip; d.loop = loop; d.time = 0f; d.Play();
            _active = deck;
            _fade = startWeight;
        }

        // Pasa a la siguiente pista fundiendo los dos platos.
        public void Next()
        {
            if (playlist == null || playlist.Length == 0) return;
            Track = (Track + 1) % playlist.Length;
            int other = 1 - _active;
            PlayOn(other, playlist[Track], false, 0f);
            _fadeSpeed = 1f / Mathf.Max(0.5f, crossfadeSeconds);
        }

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

        public static float EqualPower(float w) => Mathf.Sin(Mathf.Clamp01(w) * Mathf.PI * 0.5f);

        void Update()
        {
            float dt = Time.unscaledDeltaTime;
            float k = 1f - Mathf.Exp(-dt * 3f / transitionSeconds);
            _fade = Mathf.MoveTowards(_fade, 1f, _fadeSpeed * dt);

            // la pista activa se acerca a su final: empieza el fundido con la siguiente
            var cur = decks[_active];
            if (!InMenu && cur && cur.clip && !cur.loop && _fade >= 1f && cur.time >= cur.clip.length - crossfadeSeconds) Next();

            float duck = Time.unscaledTime < _duckUntil ? _duck : 1f;
            bool paused = GameFlow.Instance && GameFlow.Instance.State == GameState.Paused;
            float master = (InMenu ? 0.85f : _vol) * duck * (paused ? 0.4f : 1f);
            for (int i = 0; i < decks.Length; i++)
            {
                var d = decks[i];
                if (!d) continue;
                float w = i == _active ? EqualPower(_fade) : EqualPower(1f - _fade);
                d.volume = master * w;
                if (i != _active && w <= 0.001f && d.isPlaying) d.Stop();
                if (_lp[i]) _lp[i].cutoffFrequency = Mathf.Lerp(_lp[i].cutoffFrequency, InMenu ? 22000f : paused ? 900f : _cut, k);
                if (_rv[i])
                {
                    float rev = InMenu ? 0f : _rev;
                    _rv[i].dryLevel = 0f;
                    _rv[i].room = Mathf.Lerp(_rv[i].room, Mathf.Lerp(-10000f, -600f, rev), k);
                    _rv[i].decayTime = Mathf.Lerp(1.2f, 6.5f, rev);
                    _rv[i].reverbLevel = Mathf.Lerp(-2000f, 200f, rev);
                }
            }
            if (ambience) ambience.volume = Mathf.Lerp(ambience.volume, _ambVol, k);
        }
    }
}
