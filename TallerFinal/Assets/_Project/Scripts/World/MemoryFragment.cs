using System.Collections;
using UnityEngine;
using UnityEngine.Events;

namespace Dream
{
    // El recuerdo escondido de cada escenario. Flota y respira; con E a menos de 'radius' se recoge: suma al
    // puntaje, el sonador hace el gesto de recoger, suena la campanilla y se abre la transicion.
    public class MemoryFragment : MonoBehaviour
    {
        [TextArea] public string memoryText = "Un olor a pan tostado. Alguien canta en la cocina.";
        public float radius = 1.9f;
        public Transform visual;
        public Light glow;
        public bool unlocksFlight;
        [Tooltip("Si se asigna, al tomar el recuerdo arranca sola la cinematica de ese paso (el jugador no tiene que buscarlo)")]
        public TransitionGate autoGate;
        public UnityEvent onCollected;

        public bool Collected { get; private set; }
        Vector3 _base, _scale = Vector3.one;
        bool _inRange;

        void Start() { if (visual) { _base = visual.localPosition; _scale = visual.localScale; } }

        void Update()
        {
            if (visual && !Collected)
            {
                float t = Time.time;
                visual.localPosition = _base + Vector3.up * Mathf.Sin(t * 1.3f) * 0.08f;
                visual.localRotation = Quaternion.Euler(0f, t * 25f, Mathf.Sin(t * 0.7f) * 8f);
                float s = 1f + Mathf.Sin(t * 2.1f) * 0.04f;
                visual.localScale = _scale * s;
            }
            if (Collected) return;
            var rig = PlayerRig.Instance;
            bool playing = GameFlow.Instance == null || GameFlow.Instance.State == GameState.Playing;
            bool near = rig && playing && Vector3.Distance(rig.transform.position + Vector3.up, transform.position) < radius;
            if (near != _inRange) { _inRange = near; UI.HudView.Instance?.SetPrompt(near ? "E  ·  recordar" : null); }
            if (near && DreamInput.Instance != null && DreamInput.Instance.ConsumeInteract()) Collect();
        }

        public void Collect()
        {
            if (Collected) return;
            Collected = true;
            _inRange = false;
            UI.HudView.Instance?.SetPrompt(null);
            int gained = ScoreSystem.Instance ? ScoreSystem.Instance.AddMemory() : 0;
            var rig = PlayerRig.Instance;
            if (rig && rig.Anim) rig.Anim.PlayPickup();
            if (unlocksFlight && rig) rig.Motor.SetFlightAllowed(true);
            Audio.SfxPlayer.Instance?.Chime(transform.position);
            JourneyManager.Instance?.OnMemoryCollected();
            UI.HudView.Instance?.ShowMemory(memoryText, gained, unlocksFlight);
            onCollected?.Invoke();
            StartCoroutine(Dissolve());
        }

        IEnumerator Dissolve()
        {
            float g0 = glow ? glow.intensity : 0f;
            for (float t = 0f; t < 1.4f; t += Time.deltaTime)
            {
                float k = t / 1.4f;
                if (visual) visual.localScale = _scale * Mathf.Lerp(1f, 0f, k * k) * (1f + Mathf.Sin(k * Mathf.PI) * 0.6f);
                if (glow) glow.intensity = g0 * (1f + 4f * Mathf.Sin(k * Mathf.PI)) * (1f - k);
                yield return null;
            }
            if (visual) visual.gameObject.SetActive(false);
            if (glow) glow.enabled = false;
            if (autoGate)
            {
                yield return new WaitForSeconds(0.8f);              // un momento para leer el recuerdo
                autoGate.Trigger();
            }
        }
    }
}
