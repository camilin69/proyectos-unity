using UnityEngine;
using UnityEngine.Events;

namespace Dream
{
    // El paso al escenario siguiente. Cerrado hasta encontrar el recuerdo; al cruzarlo corre la cinematica de
    // salida y (si advanceScene) carga el siguiente escenario. Tambien sirve para cinematicas dentro del mismo
    // escenario (la llegada a la colina tras el vuelo), con advanceScene apagado.
    [RequireComponent(typeof(Collider))]
    public class TransitionGate : MonoBehaviour
    {
        public Cinematic.CinematicSequence departure;
        public bool advanceScene = true;
        public bool requireMemory = true;
        public bool revokesFlight;
        [TextArea] public string lockedHint = "Algo falta aquí. Busca el recuerdo.";
        public UnityEvent onComplete;

        bool _used;
        float _lastHint = -10f;

        void Awake() => GetComponent<Collider>().isTrigger = true;

        void OnTriggerEnter(Collider other) => TryUse(other);
        void OnTriggerStay(Collider other) => TryUse(other);

        // Abre el paso sin cruzarlo (lo usa el recuerdo con autoGate).
        public void Trigger()
        {
            if (_used) return;
            if (GameFlow.Instance && GameFlow.Instance.State != GameState.Playing) return;
            _used = true;
            if (revokesFlight) PlayerRig.Instance?.Motor.SetFlightAllowed(false);
            var director = Cinematic.CinematicDirector.Instance;
            if (director) director.StartCoroutine(director.PlayDeparture(departure, advanceScene, onComplete));
        }

        void TryUse(Collider other)
        {
            if (_used || !other.GetComponent<PlayerMotor>()) return;
            if (GameFlow.Instance && GameFlow.Instance.State != GameState.Playing) return;
            var anchor = JourneyManager.Instance ? JourneyManager.Instance.Anchor : null;
            if (requireMemory && anchor && !anchor.memoryCollected)
            {
                if (Time.time - _lastHint > 6f) { _lastHint = Time.time; UI.HudView.Instance?.ShowHint(lockedHint); }
                return;
            }
            _used = true;
            if (revokesFlight) PlayerRig.Instance?.Motor.SetFlightAllowed(false);
            var director = Cinematic.CinematicDirector.Instance;
            if (director) director.StartCoroutine(director.PlayDeparture(departure, advanceScene, onComplete));
        }
    }
}
