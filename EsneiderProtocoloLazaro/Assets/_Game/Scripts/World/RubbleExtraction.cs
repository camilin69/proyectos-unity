using Esneider.Audio;
using Esneider.Core;
using Esneider.Core.Persistence;
using UnityEngine;

namespace Esneider.World
{
    // Cosmetic chips never obstruct the player. The pickup remains the source of truth for saving.
    public class RubbleExtraction : MonoBehaviour
    {
        public string pickupGuid;
        public Transform[] chips;
        public float fallSeconds = .6f;
        Vector3[] _start;
        Quaternion[] _rotation;
        bool[] _landed;
        WorldStateRegistry _registry;
        CheckpointService _checkpoint;
        bool _released, _moving;
        float _elapsed;
        public bool Released => _released;
        public int ImpactsPlayed { get; private set; }

        void Init()
        {
            if (_start != null || chips == null || chips.Length == 0) return;
            _start = new Vector3[chips.Length]; _rotation = new Quaternion[chips.Length]; _landed = new bool[chips.Length];
            for (int i = 0; i < chips.Length; i++) { _start[i] = chips[i].localPosition; _rotation[i] = chips[i].localRotation; }
        }
        void OnEnable() { Bind(); }
        void Start() { Init(); Hydrate(); }
        void OnDisable()
        {
            if (_registry != null) _registry.EventApplied -= OnEvent;
            if (_checkpoint) _checkpoint.Restored -= OnRestore;
            _registry = null; _checkpoint = null;
        }
        void Bind()
        {
            if (_registry != WorldStateRegistry.Session)
            {
                if (_registry != null) _registry.EventApplied -= OnEvent;
                _registry = WorldStateRegistry.Session; _registry.EventApplied += OnEvent;
            }
            if (_checkpoint != CheckpointService.Instance)
            {
                if (_checkpoint) _checkpoint.Restored -= OnRestore;
                _checkpoint = CheckpointService.Instance;
                if (_checkpoint) _checkpoint.Restored += OnRestore;
            }
        }
        bool Taken() => !string.IsNullOrEmpty(pickupGuid) && WorldStateRegistry.Session.TryGet(pickupGuid, out var state) && state.taken;
        void OnRestore(SaveData data) { Hydrate(); }
        void OnEvent(WorldEvent e)
        {
            if (e.kind == WorldEventKind.PickupTaken && e.entityGuid == pickupGuid && Taken()) Release();
        }
        public void Hydrate()
        {
            Bind(); Init(); if (_start == null) return;
            _released = Taken(); _moving = false; _elapsed = 0;
            for (int i = 0; i < chips.Length; i++) { _landed[i] = _released; Pose(i, _released ? 1 : 0); }
        }
        public void Release()
        {
            Init(); if (_start == null || _released) return;
            _released = true; _moving = true; _elapsed = 0;
        }
        void Pose(int i, float t)
        {
            var start = _start[i];
            var end = new Vector3(start.x + (i == 0 ? -.13f : .13f), 0, start.z + .46f);
            // Slide clear of the supporting slab before dropping, rather than intersecting it.
            float slide = Mathf.Clamp01(t / .4f), fall = Mathf.Clamp01((t - .4f) / .6f);
            var p = Vector3.Lerp(start, end, slide); p.y = Mathf.Lerp(start.y, 0, fall * fall);
            chips[i].localPosition = t >= 1 ? end : p;
            chips[i].localRotation = Quaternion.Slerp(_rotation[i], Quaternion.Euler(0, i == 0 ? -27 : 34, 0) * _rotation[i], t);
        }
        void Update()
        {
            bool changed = _registry != WorldStateRegistry.Session; Bind();
            if (changed || (!_moving && Taken() != _released)) Hydrate();
            Advance(Time.deltaTime);
        }
        public void Advance(float seconds)
        {
            if (!_moving || seconds <= 0) return;
            _elapsed += seconds; bool done = true;
            for (int i = 0; i < chips.Length; i++)
            {
                float t = Mathf.Clamp01((_elapsed - i * .12f) / Mathf.Max(.1f, fallSeconds)); Pose(i, t);
                if (t < 1) { done = false; continue; }
                if (_landed[i]) continue;
                _landed[i] = true; ImpactsPlayed++;
                NoiseSystem.Emit(chips[i].position, 2f, gameObject, "rubble-impact");
                var audio = AudioService.Instance;
                if (audio) audio.Play("SND-PROP-Impact", chips[i].position, i == 0 ? .35f : .28f, 150, 0, audio.ambient);
            }
            if (done) _moving = false;
        }
    }
}
