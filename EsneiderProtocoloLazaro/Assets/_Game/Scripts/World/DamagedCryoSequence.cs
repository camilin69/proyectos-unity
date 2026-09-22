using Esneider.Audio;
using Esneider.Player;
using UnityEngine;
using UnityEngine.Animations;
using UnityEngine.Playables;

namespace Esneider.World
{
    // OBJ-002: un único intento de apertura por proximidad; el clip queda fijado en su último frame.
    public class DamagedCryoSequence : MonoBehaviour
    {
        public Animator animator;
        public AnimationClip jamClip;
        public float triggerDistance = 4.5f;
        public bool Attempted { get; private set; }
        public bool Stable { get; private set; }
        public float NormalizedProgress { get; private set; }

        PlayableGraph _graph;
        AnimationClipPlayable _playable;
        Transform _player;
        float _elapsed;

        void Start()
        {
            if (!animator) animator = GetComponent<Animator>();
            if (!animator || !jamClip) { enabled = false; return; }
            animator.cullingMode = AnimatorCullingMode.AlwaysAnimate;
            _graph = PlayableGraph.Create(name + "_damaged_cryo");
            _playable = AnimationClipPlayable.Create(_graph, jamClip);
            var output = AnimationPlayableOutput.Create(_graph, "jam", animator); output.SetSourcePlayable(_playable);
            _playable.SetSpeed(0); _playable.SetTime(0); _graph.Play();
        }

        void Update()
        {
            if (!Attempted)
            {
                if (!_player) { var p = FindFirstObjectByType<PlayerController>(); if (p) _player = p.transform; }
                if (_player && Vector3.Distance(_player.position, transform.position) <= triggerDistance) TriggerNow();
                return;
            }
            if (Stable) return;
            _elapsed += Time.deltaTime; NormalizedProgress = Mathf.Clamp01(_elapsed / Mathf.Max(.01f, jamClip.length));
            if (_elapsed < jamClip.length) return;
            _playable.SetSpeed(0); _playable.SetTime(jamClip.length); Stable = true; NormalizedProgress = 1f;
            AudioService.Instance?.Play("SND-DOOR-Slide-End", transform.position, .48f, 96, .2f, AudioService.Instance.weapons, false);
        }

        public void TriggerNow()
        {
            if (Attempted || !_graph.IsValid()) return;
            Attempted = true; _elapsed = 0; _playable.SetTime(0); _playable.SetSpeed(1);
            AudioService.Instance?.Play("SND-DOOR-Slide-Start", transform.position, .42f, 96, .2f, AudioService.Instance.weapons, false);
        }

        void OnDestroy() { if (_graph.IsValid()) _graph.Destroy(); }
    }
}
