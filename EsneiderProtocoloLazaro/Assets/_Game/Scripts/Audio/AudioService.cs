using Esneider.Core;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Audio;

namespace Esneider.Audio
{
    // 17/50.3: mezcla con grupos, pool de fuentes 3D, variación leve de pitch/volumen (96.2), prioridad de señales mortales,
    // sin Instantiate/Destroy por evento. Los bancos se cargan por ID desde Resources-like folders (Assets/_Game/Audio/**).
    public class AudioService : MonoBehaviour
    {
        public static AudioService Instance { get; private set; }
        public AudioMixer mixer;
        public AudioMixerGroup master, ambient, enemies, weapons, voice, ui;
        public int poolSize = 24;
        public float pitchJitter = 0.04f, volumeJitterDb = 1.5f;
        readonly List<AudioSource> _pool = new List<AudioSource>();
        readonly Dictionary<string, AudioClip[]> _banks = new Dictionary<string, AudioClip[]>();
        readonly Dictionary<string, int> _lastIndex = new Dictionary<string, int>();
        readonly Dictionary<string, float> _lastPlay = new Dictionary<string, float>();
        int _next;

        void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(this); return; }
            Instance = this;
            gameObject.GetOrAdd<ProgressionMusic>();
            for (int i = 0; i < poolSize; i++)
            {
                var go = new GameObject("SFX_" + i); go.transform.SetParent(transform);
                var s = go.AddComponent<AudioSource>(); s.playOnAwake = false; s.spatialBlend = 1f; s.rolloffMode = AudioRolloffMode.Logarithmic; s.minDistance = 1.5f; s.maxDistance = 40f; s.dopplerLevel = 0f;
                _pool.Add(s);
            }
        }
        void OnDestroy() { if (Instance == this) Instance = null; }

        public void RegisterBank(string id, AudioClip[] clips) { if (clips != null && clips.Length > 0) _banks[id] = clips; }
        public bool HasBank(string id) => _banks.ContainsKey(id);
        public AudioClip BankClip(string id) => Pick(id);

        AudioClip Pick(string id)
        {
            if (!_banks.TryGetValue(id, out var clips) || clips.Length == 0) return null;
            if (clips.Length == 1) return clips[0];
            int last = _lastIndex.TryGetValue(id, out var l) ? l : -1; int idx;
            do idx = Random.Range(0, clips.Length); while (idx == last); // evitar repetición inmediata (96.2)
            _lastIndex[id] = idx; return clips[idx];
        }

        // Fuente puntual 3D; prioridad: señales mortales (0) > voz (32) > armas (64) > locomoción (128) > ambiente (200)
        public AudioSource Play(string bankId, Vector3 position, float volume = 1f, int priority = 128, float minRepeat = 0f, AudioMixerGroup group = null, bool jitter = true)
        {
            var clip = Pick(bankId); if (clip == null) return null;
            if (minRepeat > 0f && _lastPlay.TryGetValue(bankId, out var t) && Time.time - t < minRepeat) return null;
            _lastPlay[bankId] = Time.time;
            var s = Acquire(priority); if (s == null) return null;
            s.transform.position = position; s.clip = clip; s.priority = priority; s.outputAudioMixerGroup = group ?? enemies; s.loop = false; s.spatialBlend = 1f;
            s.pitch = jitter ? 1f + Random.Range(-pitchJitter, pitchJitter) : 1f;
            s.volume = volume * (jitter ? Mathf.Pow(10f, Random.Range(-volumeJitterDb, volumeJitterDb) / 20f) : 1f);
            s.Play(); return s;
        }

        public AudioSource Play2D(string bankId, float volume = 1f, AudioMixerGroup group = null)
        {
            var clip = Pick(bankId); if (clip == null) return null;
            var s = Acquire(64); if (s == null) return null;
            s.clip = clip; s.spatialBlend = 0f; s.outputAudioMixerGroup = group ?? ui; s.pitch = 1f; s.volume = volume; s.loop = false; s.Play(); return s;
        }

        // Loops anclados a un objeto (máquinas, puertas): la fuente pertenece al emisor, no al pool.
        public AudioSource Loop(GameObject owner, string bankId, float volume, AudioMixerGroup group, float minDist = 2f, float maxDist = 25f)
        {
            var clip = Pick(bankId); if (clip == null) return null;
            var s = owner.GetOrAdd<AudioSource>();
            s.clip = clip; s.loop = true; s.spatialBlend = 1f; s.volume = volume; s.outputAudioMixerGroup = group ?? ambient; s.minDistance = minDist; s.maxDistance = maxDist; s.rolloffMode = AudioRolloffMode.Logarithmic; s.dopplerLevel = 0f; s.playOnAwake = false;
            if (!s.isPlaying) s.Play(); return s;
        }

        AudioSource Acquire(int priority)
        {
            for (int i = 0; i < _pool.Count; i++) { var s = _pool[(_next + i) % _pool.Count]; if (!s.isPlaying) { _next = (_next + i + 1) % _pool.Count; return s; } }
            // pool lleno: robar la fuente de menor prioridad (número mayor) si la nueva es más importante (50.3)
            AudioSource worst = null;
            foreach (var s in _pool) if (worst == null || s.priority > worst.priority) worst = s;
            if (worst != null && worst.priority > priority) { worst.Stop(); return worst; }
            return null;
        }

        public void SetGroupVolume(string exposedParam, float linear01) { if (mixer != null) mixer.SetFloat(exposedParam, Mathf.Log10(Mathf.Clamp(linear01, 0.0001f, 1f)) * 20f); }
    }
}
