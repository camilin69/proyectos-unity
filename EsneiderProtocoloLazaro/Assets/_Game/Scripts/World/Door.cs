using Esneider.Core;
using UnityEngine;

namespace Esneider.World
{
    // Puerta cinemática: estado abierto/cerrado con colisión coherente, obstrucción, permisos de frontera (68.4) y persistencia.
    public class Door : MonoBehaviour, IInteractable
    {
        public string doorId;
        public bool isOpen;
        public bool locked;
        public bool requiresPermission; // D06/D14/D22/D28/D29 según ObjectiveService
        public float openSeconds = 1.5f;
        public Transform leaf;
        public Vector3 openOffset = new Vector3(0, 0, 2.8f);
        Vector3 _closedPos; float _t; bool _moving; bool _init;
        PersistentEntity _persistent;

        public bool IsMoving => _moving;
        public bool Allowed => !locked && (!requiresPermission || ObjectiveService.DoorAllowed(doorId));
        public string Prompt => !Allowed ? "Bloqueada" : isOpen ? "Cerrar" : "Abrir";
        public bool CanInteract(GameObject who) => Allowed && !_moving;

        void Awake() { Init(); _persistent = GetComponent<PersistentEntity>(); }

        void Init()
        {
            if (_init) return; _init = true;
            if (leaf == null) leaf = transform; _closedPos = leaf.localPosition;
            if (isOpen) leaf.localPosition = _closedPos + openOffset;
        }

        public void Interact(GameObject who) { if (Allowed) SetOpen(!isOpen); }

        public void SetOpen(bool open)
        {
            if (open == isOpen || _moving) return;
            isOpen = open; _moving = true; _t = 0f;
            NoiseSystem.Emit(transform.position, 10f, gameObject, "door");
            Core.Persistence.WorldStateRegistry.Session.DiscoverDoor(doorId); // 87.3: puerta vista/usada en el mapa
            _persistent?.NotifyDoor(isOpen, !locked);
        }

        // Hidratación: estado inmediato sin animación ni ruido.
        public void SnapOpen(bool open)
        {
            Init(); isOpen = open; _moving = false; _t = 0f;
            leaf.localPosition = open ? _closedPos + openOffset : _closedPos;
        }

        void Update()
        {
            if (!_moving) return;
            _t += Time.deltaTime / openSeconds;
            float k = Mathf.SmoothStep(0, 1, Mathf.Clamp01(_t));
            var target = _closedPos + openOffset;
            var next = isOpen ? Vector3.Lerp(_closedPos, target, k) : Vector3.Lerp(target, _closedPos, k);
            if (!isOpen && Physics.CheckBox(leaf.position, leaf.lossyScale * 0.5f, leaf.rotation, GameLayers.Mask(GameLayers.Player, GameLayers.Enemy)))
            { isOpen = true; _t = 1f - _t; _persistent?.NotifyDoor(true, !locked); return; }
            leaf.localPosition = next;
            if (_t >= 1f) _moving = false;
        }
    }
}
