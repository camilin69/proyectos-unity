using UnityEngine;
using UnityEngine.Animations;
using UnityEngine.Playables;

namespace Esneider.World
{
    // OBJ-070 (59.3): dos hojas animadas por clip Door_Open (2.0 s con aceleración/freno). El collider acompaña a la hoja;
    // obstrucción comprobada antes de cerrar; estado persistente vía Door/PersistentEntity.
    public class DoorAnimated : MonoBehaviour
    {
        public Door door;
        public Animator animator;
        public AnimationClip openClip;
        public Collider[] leafColliders;
        PlayableGraph _graph; AnimationClipPlayable _clip; float _t; bool _wasOpen; bool _ready;

        void Start()
        {
            if (door == null) door = GetComponentInParent<Door>(); if (animator == null) animator = GetComponentInChildren<Animator>();
            if (animator == null || openClip == null) { enabled = false; return; }
            animator.cullingMode = AnimatorCullingMode.AlwaysAnimate;
            _graph = PlayableGraph.Create(name + "_door"); _clip = AnimationClipPlayable.Create(_graph, openClip); _clip.SetDuration(double.MaxValue);
            var o = AnimationPlayableOutput.Create(_graph, "door", animator); o.SetSourcePlayable(_clip);
            _clip.SetSpeed(0); _graph.Play();
            _wasOpen = door != null && door.isOpen; _t = _wasOpen ? openClip.length : 0f; _clip.SetTime(_t); _clip.SetDone(false); _graph.Evaluate(0f); _ready = true;
        }

        void OnDestroy() { if (_graph.IsValid()) _graph.Destroy(); }

        void Update()
        {
            if (!_ready || door == null) return;
            var obstacle=GetComponent<UnityEngine.AI.NavMeshObstacle>(); if(obstacle!=null) obstacle.enabled=!door.isOpen || door.IsMoving;
            float target = door.isOpen ? openClip.length : 0f;
            if (Mathf.Abs(_t - target) < 0.001f) return;
            _t = Mathf.MoveTowards(_t, target, Time.deltaTime * (openClip.length / Mathf.Max(0.1f, door.openSeconds)));
            _clip.SetTime(_t); _clip.SetDone(false); _graph.Evaluate(0f);
            // la hoja es el collider: al moverse la geometría, los colliders (hijos de los huesos) acompañan automáticamente
            if (leafColliders != null) foreach (var c in leafColliders) if (c != null) c.enabled = true;
        }
    }
}
