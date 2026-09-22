using System.Collections;
using System.Collections.Generic;
using Esneider.Core;
using Esneider.Core.Persistence;
using UnityEngine;

namespace Esneider.World
{
    // 93.1: evento de sala genérico. Política U (una vez por campaña, EventRunner) o A (ambiente con cooldown).
    // Disparo: entrada o salida del jugador en el volumen, o lectura de un documento. Condiciones: flag requerido/prohibido,
    // unidad viva, ausencia de combate (aplaza hasta ventana segura, no reinicia cada frame). Acciones: sonido, mensaje HUD,
    // objetivo, flag, activación de unidades. Sin clip → fallback legible (93.3).
    [RequireComponent(typeof(BoxCollider))]
    public class RoomEvent : MonoBehaviour
    {
        public string eventId;
        public bool once = true;              // U; false = A (repetible con cooldown)
        public float cooldown = 30f;
        public bool onExit;                   // disparar al salir en vez de al entrar
        public string watchDocument = "";     // dispara cuando el jugador lee este documento (estando o no en el volumen)
        public string requiredFlag = "", forbiddenFlag = "", requiredDocument = "";
        public string requiresAliveUnit = "";
        public bool deferWhileCombat;
        public float delay;
        public string sound = ""; public Vector3 soundOffset; public float soundVolume = 0.8f;
        public string message = ""; public float messageSeconds = 4f;
        public string objectiveId = "", setFlag = "";
        public List<string> activateUnits = new List<string>();
        public int fired;
        bool _inside, _pending, _init;
        BoxCollider _box; Transform _player;

        void Awake() { _box = GetComponent<BoxCollider>(); _box.isTrigger = true; gameObject.layer = GameLayers.Trigger; }
        public void ResetForCheckpoint() { StopAllCoroutines(); _inside=false; _pending=false; _init=false; fired=0; }

        // Presencia por volumen (entidad principal del jugador, 93.1), muestreada cada frame: robusta ante teletransportes y cargas,
        // donde OnTriggerEnter/Exit del CharacterController no son fiables.
        void Update()
        {
            if(GameFlowController.Instance != null && !GameFlowController.Instance.GameplayActive) return;
            if (_player == null) { var pc = FindFirstObjectByType<Player.PlayerController>(); if (pc == null) return; _player = pc.transform; }
            bool inside = _box.bounds.Contains(_player.position + Vector3.up * 0.5f);
            if (!_init) { _init = true; _inside = inside; if (inside && !onExit && string.IsNullOrEmpty(watchDocument)) _pending = true; }
            else if (inside != _inside)
            {
                _inside = inside;
                if (inside && !onExit && string.IsNullOrEmpty(watchDocument)) _pending = true;
                if (!inside && onExit) _pending = true;
            }
            if (!string.IsNullOrEmpty(watchDocument) && !_pending && WorldStateRegistry.Session.IsDocumentRead(watchDocument)) _pending = true;
            if (!_pending) return;
            if (!Conditions()) { if (!deferWhileCombat) _pending = false; return; }
            _pending = false;
            if (EventRunner.Instance == null) return;
            if (once) EventRunner.Instance.TryRunOnce(eventId, () => StartCoroutine(Fire()));
            else EventRunner.Instance.TryRunRepeatable(eventId, cooldown, () => StartCoroutine(Fire()));
        }

        bool Conditions()
        {
            var reg = WorldStateRegistry.Session;
            if (!string.IsNullOrEmpty(requiredFlag) && !reg.HasFlag(requiredFlag)) return false;
            if (!string.IsNullOrEmpty(forbiddenFlag) && reg.HasFlag(forbiddenFlag)) return false;
            if (!string.IsNullOrEmpty(requiredDocument) && !reg.IsDocumentRead(requiredDocument)) return false;
            if (!string.IsNullOrEmpty(requiresAliveUnit)) { var b = FindUnit(requiresAliveUnit); if (b == null || b.IsDead) return false; }
            if (deferWhileCombat && AI.EncounterDirector.Instance != null && AI.EncounterDirector.Instance.AnyEngaged) return false;
            return true;
        }

        IEnumerator Fire()
        {
            fired++;
            if (delay > 0) yield return new WaitForSeconds(delay);
            var svc = Audio.AudioService.Instance;
            if (svc != null && !string.IsNullOrEmpty(sound))
            {
                if (svc.HasBank(sound)) svc.Play(sound, transform.position + soundOffset, soundVolume, 100, 0f, svc.ambient, false);
                else Debug.LogWarning($"EVT {eventId}: banco de audio '{sound}' ausente; fallback sin sonido (93.3)");
            }
            if (!string.IsNullOrEmpty(message)) Object.FindFirstObjectByType<UI.HudController>()?.ShowMessage(message, messageSeconds);
            if (!string.IsNullOrEmpty(setFlag)) WorldStateRegistry.Session.SetFlag(setFlag);
            if (!string.IsNullOrEmpty(objectiveId)) ObjectiveService.Complete(objectiveId);
            foreach (var id in activateUnits) { var b = FindUnit(id); if (b != null && !b.IsDead) b.Activate(); }
        }

        static AI.EnemyBrain FindUnit(string id)
        {
            foreach (var b in Object.FindObjectsByType<AI.EnemyBrain>(FindObjectsInactive.Include, FindObjectsSortMode.None)) if (b.stableId == id) return b;
            return null;
        }
    }
}
