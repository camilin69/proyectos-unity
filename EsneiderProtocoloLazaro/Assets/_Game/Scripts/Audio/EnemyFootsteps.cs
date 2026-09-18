using Esneider.AI;
using Esneider.Core.Data;
using UnityEngine;
using UnityEngine.AI;

namespace Esneider.Audio
{
    // 50.2: locomoción de robots por distancia recorrida (servo/apoyo), no por temporizador que suena quieto.
    public class EnemyFootsteps : MonoBehaviour
    {
        public float stride = 0.9f;
        NavMeshAgent _agent; EnemyBrain _brain; float _acc; Vector3 _last;
        void Start() { _agent = GetComponent<NavMeshAgent>(); _brain = GetComponent<EnemyBrain>(); _last = transform.position; if (_brain != null && _brain.definition != null && _brain.definition.kind == EnemyKind.Custodio) stride = 1.3f; }
        void Update()
        {
            if (AudioService.Instance == null || _brain == null || _brain.IsDead) return;
            float d = Vector3.Distance(transform.position, _last); _last = transform.position;
            if (_agent == null || !_agent.enabled || _agent.velocity.sqrMagnitude < 0.01f) { _acc = 0f; return; }
            _acc += d;
            if (_acc >= stride)
            {
                _acc = 0f;
                bool vig = _brain.definition.kind == EnemyKind.Vigia;
                AudioService.Instance.Play(vig ? "SND-VIG-Step" : "SND-KUS-Step", transform.position, vig ? 0.6f : 0.9f, 128, 0.15f, AudioService.Instance.enemies);
            }
        }
    }
}
