using Esneider.Core;
using System.Collections.Generic;
using Esneider.Core.Data;
using UnityEngine;
using UnityEngine.Animations;
using UnityEngine.Playables;

namespace Esneider.Player
{
    // 35/38/86.1: brazos y arma en espacio de presentación bajo la cámara; el arma no equipada no se renderiza;
    // los clips representan la acción decidida por PlayerActions (equipar, golpe, recarga, jeringa).
    public class ViewmodelController : MonoBehaviour
    {
        public PlayerActions actions;
        public Transform cameraPivot;
        public GameObject armsPrefab;
        public GameObject crowbarPrefab, pistolPrefab, shotgunPrefab, flashlightPrefab;
        public AnimationClip[] armClips;
        public Vector3 armsOffset = new Vector3(0f, -0.32f, 0.28f);
        public Vector3 weaponOffset = new Vector3(0.2f, -0.27f, 0.52f);
        public Vector3 flashlightOffset = new Vector3(-0.22f, -0.25f, 0.35f);

        // 63/64 y PIL-14: el arma va SUJETA a la mano, no colgada de la cámara. Si cuelga de la cámara, al animar el
        // brazo la mano se separa del mango y el contrato "palma, pulgar y dedos sostienen el grip" es imposible.
        [Header("Agarre (64: el arma sigue a la mano)")]
        public string rightSocket = "hand_R", leftSocket = "hand_L";
        public bool attachToHand = true;
        // Punto de agarre de cada arma en su espacio local (Unity), derivado del modelo de Blender.
        public Vector3 crowbarGrip = new Vector3(0f, 0f, 0.20f);
        public Vector3 pistolGrip = new Vector3(0f, -0.062f, 0.042f);
        public Vector3 shotgunGrip = new Vector3(0f, -0.06f, 0.09f);
        public Vector3 flashlightGrip = new Vector3(0f, 0f, 0f);
        // Desplazamiento de la palma respecto al origen del hueso de la mano.
        public Vector3 palmOffset = new Vector3(0f, -0.01f, 0.035f);
        public float bobAmplitude = 0.008f; // head bob leve y desactivable (9)
        public bool bobEnabled = true;

        GameObject _arms, _weapon, _flash;
        Animator _animator; PlayableGraph _graph; AnimationMixerPlayable _mixer;
        readonly Dictionary<string, int> _slots = new Dictionary<string, int>();
        readonly List<AnimationClipPlayable> _clips = new List<AnimationClipPlayable>();
        int _current = -1, _previous = -1; float _blendT = 1f;
        WeaponKind? _shownWeapon; ActionKind _lastKind = ActionKind.None; int _lastActionId = -1;
        PlayerMotor _motor; float _bobT;

        void Start()
        {
            if (actions == null) actions = GetComponentInParent<PlayerActions>();
            _motor = GetComponentInParent<PlayerMotor>();
            if (cameraPivot == null) cameraPivot = transform;
            if (armsPrefab != null)
            {
                _arms = Instantiate(armsPrefab, cameraPivot); _arms.name = "Arms"; _arms.transform.localPosition = armsOffset; _arms.transform.localRotation = Quaternion.identity;
                foreach (var c in _arms.GetComponentsInChildren<Collider>()) Destroy(c);
                _animator = _arms.GetOrAdd<Animator>();
                if (armClips != null && armClips.Length > 0)
                {
                    _graph = PlayableGraph.Create("viewmodel"); _mixer = AnimationMixerPlayable.Create(_graph, armClips.Length);
                    for (int i = 0; i < armClips.Length; i++) { var p = AnimationClipPlayable.Create(_graph, armClips[i]); _graph.Connect(p, 0, _mixer, i); _clips.Add(p); _slots[armClips[i].name] = i; _mixer.SetInputWeight(i, 0f); }
                    var o = AnimationPlayableOutput.Create(_graph, "vm", _animator); o.SetSourcePlayable(_mixer); _graph.Play(); Play("Arms_Idle", true);
                }
            }
            if (flashlightPrefab != null)
            {
                var lsock = FindSocket(leftSocket);
                _flash = Instantiate(flashlightPrefab, lsock != null ? lsock : cameraPivot); _flash.name = "FlashlightModel";
                if (lsock != null) Place(_flash.transform, flashlightGrip, Quaternion.Euler(0f, 0f, 0f));
                else { _flash.transform.localPosition = flashlightOffset; _flash.transform.localRotation = Quaternion.identity; }
                foreach (var c in _flash.GetComponentsInChildren<Collider>()) Destroy(c);
                _flash.SetActive(false);
            }
        }

        // Busca el hueso del rig de los brazos por nombre (el FBX conserva los nombres de la armadura de Blender).
        Transform FindSocket(string bone)
        {
            if (!attachToHand || _arms == null || string.IsNullOrEmpty(bone)) return null;
            foreach (var t in _arms.GetComponentsInChildren<Transform>(true)) if (t.name == bone) return t;
            return null;
        }

        // Coloca el objeto de modo que su punto de agarre caiga en la palma del hueso.
        void Place(Transform t, Vector3 gripLocal, Quaternion rot)
        {
            t.localRotation = rot;
            t.localPosition = palmOffset - (rot * gripLocal);
        }

        void OnDestroy() { if (_graph.IsValid()) _graph.Destroy(); }

        void Update()
        {
            if (actions == null) return;
            // arma visible = arma activa (86.6: cambia solo al commit de equipar)
            if (_shownWeapon != actions.ActiveWeapon) { _shownWeapon = actions.ActiveWeapon; ShowWeapon(_shownWeapon); }
            var inv = actions.inventory; if (_flash != null) _flash.SetActive(inv != null && inv.hasFlashlight);
            // clip por acción en curso
            int id = actions.Current != null ? actions.Current.Id : -1;
            if (actions.Busy && id != _lastActionId)
            {
                _lastActionId = id; _lastKind = actions.CurrentKind;
                switch (actions.CurrentKind)
                {
                    case ActionKind.Attack: Play("Arms_CrowbarSwing", false); break;
                    case ActionKind.ReloadPistol: case ActionKind.ReloadShotgun: Play("Arms_PistolReload", false); break;
                    case ActionKind.Heal: Play("Arms_Syringe", false); break;
                    case ActionKind.Equip: Play("Arms_Grip", false); break;
                }
            }
            else if (!actions.Busy && _lastKind != ActionKind.None) { _lastKind = ActionKind.None; _lastActionId = -1; Play("Arms_Idle", true); }
            if (_blendT < 1f && _graph.IsValid())
            {
                _blendT = Mathf.Min(1f, _blendT + Time.deltaTime / 0.12f);
                if (_current >= 0) _mixer.SetInputWeight(_current, _blendT);
                if (_previous >= 0 && _previous != _current) _mixer.SetInputWeight(_previous, 1f - _blendT);
            }
            // head bob leve
            if (_arms != null)
            {
                float speed = _motor != null ? new Vector3(_motor.Velocity.x, 0, _motor.Velocity.z).magnitude : 0f;
                _bobT += Time.deltaTime * (speed > 0.1f ? speed * 2.2f : 0f);
                var bob = bobEnabled && speed > 0.1f ? new Vector3(Mathf.Sin(_bobT) * bobAmplitude, Mathf.Abs(Mathf.Cos(_bobT)) * bobAmplitude, 0) : Vector3.zero;
                _arms.transform.localPosition = Vector3.Lerp(_arms.transform.localPosition, armsOffset + bob, 10f * Time.deltaTime);
            }
        }

        void ShowWeapon(WeaponKind? kind)
        {
            if (_weapon != null) Destroy(_weapon);
            _weapon = null;
            var prefab = kind == WeaponKind.Melee ? crowbarPrefab : kind == WeaponKind.Pistol ? pistolPrefab : kind == WeaponKind.Shotgun ? shotgunPrefab : null;
            if (prefab == null) return;
            var socket = FindSocket(rightSocket);
            _weapon = Instantiate(prefab, socket != null ? socket : cameraPivot); _weapon.name = "Weapon_" + kind;
            var rot = kind == WeaponKind.Melee ? Quaternion.Euler(-60f, 10f, 0f) : Quaternion.identity;
            if (socket != null)
            {
                var grip = kind == WeaponKind.Melee ? crowbarGrip : kind == WeaponKind.Pistol ? pistolGrip : shotgunGrip;
                Place(_weapon.transform, grip, rot);
            }
            else { _weapon.transform.localPosition = weaponOffset; _weapon.transform.localRotation = rot; }
            foreach (var c in _weapon.GetComponentsInChildren<Collider>()) Destroy(c);
            foreach (var t in _weapon.GetComponentsInChildren<Transform>()) t.gameObject.layer = gameObject.layer;
        }

        void Play(string clip, bool loop)
        {
            if (!_graph.IsValid() || !_slots.TryGetValue(clip, out var idx) || idx == _current) return;
            for (int i = 0; i < _clips.Count; i++) if (i != _current) _mixer.SetInputWeight(i, 0f);
            _previous = _current; _current = idx; _blendT = 0f;
            var p = _clips[idx]; p.SetTime(0); p.SetDuration(loop ? double.MaxValue : p.GetAnimationClip().length);
        }
    }
}
