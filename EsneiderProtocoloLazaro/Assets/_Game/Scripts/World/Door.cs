using Esneider.Core;
using UnityEngine;

namespace Esneider.World
{
    // Puerta cinemática mínima: estado abierto/cerrado con colisión coherente y comprobación de obstrucción (20.2).
    public class Door : MonoBehaviour, IInteractable
    {
        public string doorId;
        public bool isOpen;
        public bool locked;
        public float openSeconds = 1.5f;
        public Transform leaf;
        public Vector3 openOffset = new Vector3(0, 0, 2.8f);
        Vector3 _closedPos; float _t; bool _moving;

        public string Prompt => locked ? "Bloqueada" : isOpen ? "Cerrar" : "Abrir";
        public bool CanInteract(GameObject who) => !locked && !_moving;

        void Awake() { if (leaf == null) leaf = transform; _closedPos = leaf.localPosition; if (isOpen) leaf.localPosition = _closedPos + openOffset; }

        public void Interact(GameObject who) { if (!locked) SetOpen(!isOpen); }

        public void SetOpen(bool open)
        {
            if (open == isOpen || _moving) return;
            isOpen = open; _moving = true; _t = 0f;
            NoiseSystem.Emit(transform.position, 10f, gameObject, "door");
        }

        void Update()
        {
            if (!_moving) return;
            _t += Time.deltaTime / openSeconds;
            float k = Mathf.SmoothStep(0, 1, Mathf.Clamp01(_t));
            var target = _closedPos + openOffset;
            var next = isOpen ? Vector3.Lerp(_closedPos, target, k) : Vector3.Lerp(target, _closedPos, k);
            if (!isOpen && Physics.CheckBox(leaf.position, leaf.lossyScale * 0.5f, leaf.rotation, GameLayers.Mask(GameLayers.Player, GameLayers.Enemy, GameLayers.DynamicProp)))
            { isOpen = true; _t = 1f - _t; return; }
            leaf.localPosition = next;
            if (_t >= 1f) _moving = false;
        }
    }
}
