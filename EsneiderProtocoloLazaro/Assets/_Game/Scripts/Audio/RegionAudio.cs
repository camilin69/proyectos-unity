using Esneider.Core;
using UnityEngine;

namespace Esneider.Audio
{
    // 50.1/88.4: ambiente estable por región con blend de 1–2 s al cruzar; zona de reverberación propia (50.3).
    public class RegionAudio : MonoBehaviour
    {
        public string regionId;
        public string ambienceBank;
        public float volume = 0.5f;
        public float fadeSeconds = 1.5f;
        public AudioReverbPreset reverb = AudioReverbPreset.Hangar;
        AudioSource _src; float _target; bool _active;
        bool _aftermath;

        void Start()
        {
            if (AudioService.Instance == null) return;
            _src = AudioService.Instance.Loop(gameObject, ambienceBank, 0f, AudioService.Instance.ambient, 5f, 400f);
            if (_src != null) { _src.spatialBlend = 0f; _src.volume = 0f; }
            var zone = gameObject.GetOrAdd<AudioReverbZone>();
            var bc = GetComponent<BoxCollider>(); float r = bc != null ? Mathf.Max(bc.size.x, bc.size.z) / 2f : 20f;
            zone.reverbPreset = reverb; zone.minDistance = r * 0.8f; zone.maxDistance = r * 1.2f;
        }

        void Update()
        {
            if (_src == null) return;
            bool aftermath = ObjectiveService.Has(ObjectiveService.BossDefeated);
            if (aftermath != _aftermath)
            {
                _aftermath = aftermath;
                _src.clip = AudioService.Instance.BankClip(aftermath ? "SND-AMBI-S1" : ambienceBank);
                _src.Play();
            }
            var st = World.RegionStreamer.Instance;
            _active = st != null && st.CurrentRegion == regionId;
            _target = _active ? volume : 0f;
            _src.volume = Mathf.MoveTowards(_src.volume, _target, Time.deltaTime / Mathf.Max(0.1f, fadeSeconds) * volume);
        }
    }
}
