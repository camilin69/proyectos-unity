using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Playables;
using UnityEngine.Animations;

namespace Esneider.AI
{
    // 86.1/86.5: el Animator representa la decisión de la FSM. Sin Animator Controller: mezcla por Playables con crossfade 0.15–0.2 s.
    // El telegraph no se acorta al resolver el crossfade: el clip de anticipación dura lo que dura la preparación.
    public class EnemyAnimator : MonoBehaviour
    {
        public EnemyBrain brain;
        public Animator animator;
        public float blend = 0.2f;
        public string prefix = "Vigia";
        PlayableGraph _graph; AnimationMixerPlayable _mixer;
        readonly Dictionary<string, int> _slots = new Dictionary<string, int>();
        readonly List<AnimationClipPlayable> _clips = new List<AnimationClipPlayable>();
        int _current = -1; float _blendT; int _previous = -1;
        EnemyState _lastState;

        void Start()
        {
            if (brain == null) brain = GetComponentInParent<EnemyBrain>(); if (animator == null) animator = GetComponentInChildren<Animator>();
            if (animator == null) { enabled = false; return; }
            _graph = PlayableGraph.Create(name + "_anim"); _graph.SetTimeUpdateMode(DirectorUpdateMode.GameTime);
            var clips = animator.runtimeAnimatorController != null ? animator.runtimeAnimatorController.animationClips : CollectClips();
            _mixer = AnimationMixerPlayable.Create(_graph, clips.Length);
            for (int i = 0; i < clips.Length; i++)
            {
                var p = AnimationClipPlayable.Create(_graph, clips[i]); _graph.Connect(p, 0, _mixer, i); _clips.Add(p);
                _slots[clips[i].name] = i; _mixer.SetInputWeight(i, 0f);
            }
            var output = AnimationPlayableOutput.Create(_graph, "out", animator); output.SetSourcePlayable(_mixer);
            _graph.Play();
            Play(prefix + "_Idle", true);
        }

        AnimationClip[] CollectClips()
        {
            // clips del FBX referenciados por el componente (asignados por el integrador)
            return clipsFromFbx ?? new AnimationClip[0];
        }
        public AnimationClip[] clipsFromFbx;

        void OnDestroy() { if (_graph.IsValid()) _graph.Destroy(); }

        void Update()
        {
            if (brain == null || !_graph.IsValid()) return;
            if (brain.State != _lastState)
            {
                _lastState = brain.State;
                switch (brain.State)
                {
                    case EnemyState.Patrol: case EnemyState.Chase: case EnemyState.Search: case EnemyState.Return: case EnemyState.Investigate: case EnemyState.Executing: Play(prefix + "_Walk", true); break;
                    case EnemyState.Prepare: Play(prefix + "_Anticipation", false); break;
                    case EnemyState.Attack: case EnemyState.Recover: Play(prefix == "Vigia" ? "Vigia_Net" : prefix + "_Bolt", false); break;
                    case EnemyState.Staggered: Play(prefix + "_Stagger", false); break;
                    case EnemyState.Dead: Play(prefix + "_Death", false); break;
                    default: Play(prefix + "_Idle", true); break;
                }
            }
            // parado dentro de estados de locomoción → idle
            if ((_lastState == EnemyState.Patrol || _lastState == EnemyState.Search || _lastState == EnemyState.Return) && brain.TryGetComponent<UnityEngine.AI.NavMeshAgent>(out var ag) && ag.enabled && ag.isOnNavMesh)
            {
                bool moving = ag.velocity.sqrMagnitude > 0.01f;
                string want = moving ? prefix + "_Walk" : prefix + "_Idle";
                if (_slots.TryGetValue(want, out var idx) && idx != _current) Play(want, true);
            }
            if (_blendT < 1f)
            {
                _blendT = Mathf.Min(1f, _blendT + Time.deltaTime / Mathf.Max(0.01f, blend));
                if (_current >= 0) _mixer.SetInputWeight(_current, _blendT);
                if (_previous >= 0 && _previous != _current) _mixer.SetInputWeight(_previous, 1f - _blendT);
            }
        }

        public void Play(string clip, bool loop)
        {
            if (!_slots.TryGetValue(clip, out var idx)) { if (_slots.TryGetValue(prefix + "_Idle", out idx) == false) return; }
            if (idx == _current) return;
            for (int i = 0; i < _clips.Count; i++) if (i != _current) _mixer.SetInputWeight(i, 0f);
            _previous = _current; _current = idx; _blendT = 0f;
            var p = _clips[idx]; p.SetTime(0); p.SetSpeed(1); p.SetDuration(loop ? double.MaxValue : p.GetAnimationClip().length);
        }
    }
}
