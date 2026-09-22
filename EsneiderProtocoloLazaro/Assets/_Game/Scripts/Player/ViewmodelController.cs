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
        public GameObject crowbarPrefab, pistolPrefab, shotgunPrefab, flashlightPrefab, syringePrefab;
        public GameObject rationPrefab, pistolAmmoPrefab, shotgunAmmoPrefab;
        public AnimationClip[] armClips;
        public Vector3 armsOffset = new Vector3(0f, -0.27f, -0.08f);
        public Vector3 weaponOffset = new Vector3(0.2f, -0.27f, 0.52f);
        public Vector3 flashlightOffset = new Vector3(-0.22f, -0.25f, 0.35f);

        // 63/64 y PIL-14: el arma va SUJETA a la mano, no colgada de la cámara. Si cuelga de la cámara, al animar el
        // brazo la mano se separa del mango y el contrato "palma, pulgar y dedos sostienen el grip" es imposible.
        [Header("Agarre (64: el arma sigue a la mano)")]
        public string rightSocket = "hand_R", leftSocket = "hand_L";
        public bool attachToHand = true;
        // Punto de agarre de cada arma en su espacio local (Unity). Sirven de reserva: el punto real se LEE de la
        // geometría del arma (las piezas cuyo nombre declara que son el mango). Escribirlo a mano ya falló una vez:
        // los tres valores tenían el signo de Z invertido respecto del eje de exportación del FBX (-Z forward), así
        // que el arma quedaba sujeta por el extremo contrario. Medido: la varilla a 375 mm de la palma, la escopeta
        // a 173 y la pistola a 83, con las puntas de los dedos entre 160 y 466 mm del mango.
        public Vector3 crowbarGrip = new Vector3(0f, 0f, -0.175f);
        public Vector3 pistolGrip = new Vector3(0f, -0.041f, -0.038f);
        public Vector3 shotgunGrip = new Vector3(0f, -0.045f, -0.082f);
        public Vector3 flashlightGrip = new Vector3(0f, 0f, 0f);
        public Vector3 syringeGrip = Vector3.zero;
        public Vector3 syringeEuler = new Vector3(18f, -12f, 78f);
        public bool deriveGripFromGeometry = true;
        // Desplazamiento de la palma respecto al origen del hueso de la mano. Reserva: el punto real se lee de la
        // pieza `palm_L`/`palm_R` del modelo. Escrito a mano apuntaba a la muñeca y no a la palma, 80 mm más allá,
        // así que el mango caía por detrás de donde cierran los dedos.
        public Vector3 palmOffset = new Vector3(0f, -0.01f, 0.035f);
        public bool derivePalmFromGeometry = true;
        // Dónde se asienta el eje del mango respecto al centro de la pieza de la palma, en el espacio del hueso de
        // la mano: entre la superficie palmar y las yemas del puño cerrado. Medido sobre el modelo, no estimado, y
        // `GripContactTests` falla si deja de ser cierto.
        public Vector3 gripSeat = new Vector3(0f, 0.021f, 0.032f);
        public float bobAmplitude = 0.008f; // head bob leve y desactivable (9)
        public bool bobEnabled = true;

        GameObject _arms, _weapon, _flash, _syringe;
        Transform _syringeCap, _syringeCapRibs, _syringeStopper, _syringePlunger, _syringePlungerRib, _syringePlungerHead;
        Vector3 _capStart, _capRibsStart, _stopperStart, _plungerStart, _plungerRibStart, _plungerHeadStart;
        Animator _animator; PlayableGraph _graph; AnimationMixerPlayable _mixer;
        readonly Dictionary<string, int> _slots = new Dictionary<string, int>();
        readonly List<AnimationClipPlayable> _clips = new List<AnimationClipPlayable>();
        int _current = -1, _previous = -1; float _blendT = 1f;
        WeaponKind? _shownWeapon; ActionKind _lastKind = ActionKind.None; int _lastActionId = -1;
        World.PickupKind? _shownItem;
        PlayerMotor _motor; float _bobT;
        Transform _leftForearm, _rightForearm;
        float _leftForearmX, _rightForearmX;

        // Expuestos para la validación de integración: permiten comprobar que el prop aparece y que el
        // émbolo avanza durante la misma transacción que consume la jeringa.
        public GameObject ActiveSyringeModel => _syringe;
        public float SyringePress01 { get; private set; }

        void Start()
        {
            if (actions == null) actions = GetComponentInParent<PlayerActions>();
            _motor = GetComponentInParent<PlayerMotor>();
            if (cameraPivot == null) cameraPivot = transform;
            if (armsPrefab != null)
            {
                _arms = Instantiate(armsPrefab, cameraPivot); _arms.name = "Arms"; _arms.transform.localPosition = armsOffset; _arms.transform.localRotation = Quaternion.Euler(0, 180, 0);
                foreach (var c in _arms.GetComponentsInChildren<Collider>()) Destroy(c);
                _animator = _arms.GetOrAdd<Animator>();
                // The imported rig faces -Z. Turning it toward the camera's +Z also
                // exchanges screen sides; translate each complete arm back to its side.
                foreach (var bone in _animator.GetComponentsInChildren<Transform>())
                {
                    if (bone.name == "forearm_L" && bone.GetComponent<Renderer>() == null) { _leftForearm = bone; _leftForearmX = bone.localPosition.x; }
                    if (bone.name == "forearm_R" && bone.GetComponent<Renderer>() == null) { _rightForearm = bone; _rightForearmX = bone.localPosition.x; }
                }
                _animator.cullingMode = AnimatorCullingMode.AlwaysAnimate;
                foreach (var skin in _arms.GetComponentsInChildren<SkinnedMeshRenderer>()) skin.updateWhenOffscreen = true;
                PreparePresentation(_arms);
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
                if (lsock != null) Place(_flash.transform, flashlightGrip, Quaternion.Euler(-90f, 0f, 0f));
                else { _flash.transform.localPosition = flashlightOffset; _flash.transform.localRotation = Quaternion.identity; }
                foreach (var c in _flash.GetComponentsInChildren<Collider>()) Destroy(c);
                PreparePresentation(_flash);
                _flash.SetActive(false);
            }
            var fillObject = new GameObject("ViewmodelFill"); fillObject.transform.SetParent(cameraPivot,false);
            fillObject.transform.localPosition = new Vector3(0,.15f,.35f);
            var fill = fillObject.AddComponent<Light>(); fill.type=LightType.Point; fill.intensity=.2f; fill.range=1.5f;
            fillObject.AddComponent<UnityEngine.Rendering.Universal.UniversalAdditionalLightData>().renderingLayers=2;
        }

        static void PreparePresentation(GameObject model)
        {
            foreach(var renderer in model.GetComponentsInChildren<Renderer>(true))
            {
                renderer.renderingLayerMask=2;
                renderer.shadowCastingMode=UnityEngine.Rendering.ShadowCastingMode.Off;
                renderer.receiveShadows=false;
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
            t.localPosition = PalmPoint(t.parent) + gripSeat - (rot * GripPoint(t.gameObject, gripLocal, deriveGripFromGeometry));
        }

        // La palma también es una pieza del modelo. Leerla evita repetir el error de los puntos de agarre: un número
        // escrito a mano que nadie vuelve a comprobar cuando el asset se refabrica.
        public Vector3 PalmPoint(Transform socket)
        {
            if (!derivePalmFromGeometry || _arms == null || socket == null) return palmOffset;
            string quiero = socket.name.EndsWith("_L") ? "palm_L" : "palm_R";
            foreach (var r in _arms.GetComponentsInChildren<Renderer>(true))
                if (r.name == quiero) return socket.InverseTransformPoint(r.bounds.center);
            return palmOffset;
        }

        // El mango es una pieza del modelo y se declara en su nombre, así que el punto de agarre se mide en vez de
        // escribirse: sobrevive a una refabricación del arma y no depende de recordar el eje de exportación.
        public static Vector3 GripPoint(GameObject weapon, Vector3 fallback, bool derive = true)
        {
            if (!derive || weapon == null) return fallback;
            bool any = false; var box = new Bounds();
            foreach (var mf in weapon.GetComponentsInChildren<MeshFilter>(true))
            {
                if (mf.sharedMesh == null || mf.name.IndexOf("grip", System.StringComparison.OrdinalIgnoreCase) < 0) continue;
                var b = mf.sharedMesh.bounds;
                var c = weapon.transform.InverseTransformPoint(mf.transform.TransformPoint(b.center));
                var e = weapon.transform.InverseTransformVector(mf.transform.TransformVector(b.extents));
                var local = new Bounds(c, new Vector3(Mathf.Abs(e.x), Mathf.Abs(e.y), Mathf.Abs(e.z)) * 2f);
                if (!any) { box = local; any = true; } else box.Encapsulate(local);
            }
            return any ? box.center : fallback;
        }

        void OnDestroy() { if (_graph.IsValid()) _graph.Destroy(); }

        void LateUpdate()
        {
            // Absolute coordinates avoid accumulating offsets when a clip omits translation.
            // Apply after animation so idle, grip and attack all retain anatomical handedness.
            if (_leftForearm != null) { var p = _leftForearm.localPosition; p.x = -_leftForearmX; _leftForearm.localPosition = p; }
            if (_rightForearm != null) { var p = _rightForearm.localPosition; p.x = -_rightForearmX; _rightForearm.localPosition = p; }
        }

        void Update()
        {
            if (actions == null) return;
            // arma visible = arma activa (86.6: cambia solo al commit de equipar)
            var inv = actions.inventory;
            var desired = actions.ActiveWeapon.HasValue ? Inventory.ItemFor(actions.ActiveWeapon.Value) : inv != null && inv.SelectedItem.HasValue && inv.HasItem(inv.SelectedItem.Value) && inv.SelectedItem != World.PickupKind.Flashlight ? inv.SelectedItem : null;
            if (_shownItem != desired || _shownWeapon != actions.ActiveWeapon)
            {
                _shownItem=desired; _shownWeapon=actions.ActiveWeapon;
                if (_shownWeapon.HasValue) ShowWeapon(_shownWeapon); else ShowHeldItem(desired);
            }
            if (_flash != null) _flash.SetActive(inv != null && inv.hasFlashlight);
            // clip por acción en curso
            int id = actions.Current != null ? actions.Current.Id : -1;
            if (actions.Busy && id != _lastActionId)
            {
                _lastActionId = id; _lastKind = actions.CurrentKind;
                switch (actions.CurrentKind)
                {
                    case ActionKind.Attack:
                        if (actions.ActiveWeapon == WeaponKind.Melee) Play("Arms_CrowbarSwing", false);
                        break;
                    case ActionKind.ReloadPistol: case ActionKind.ReloadShotgun: Play("Arms_PistolReload", false); break;
                    case ActionKind.Heal:
                        Play("Arms_Syringe", false);
                        if (actions.Current != null && actions.Current.Type == "Syringe") BeginSyringeVisual();
                        break;
                    case ActionKind.Equip: Play("Arms_Grip", false); break;
                }
            }
            else if (!actions.Busy && _lastKind != ActionKind.None)
            {
                _lastKind = ActionKind.None; _lastActionId = -1;
                if(actions.ActiveWeapon.HasValue && _slots.TryGetValue("Arms_Grip",out var gripSlot))
                {
                    Play("Arms_Grip",false);
                    var pose=_clips[gripSlot];pose.SetTime(pose.GetAnimationClip().length);pose.SetDuration(double.MaxValue);pose.SetDone(false);pose.SetSpeed(0);
                }
                else Play("Arms_Idle",true);
            }
            bool usingSyringe = actions.Busy && actions.CurrentKind == ActionKind.Heal && actions.Current != null && actions.Current.Type == "Syringe";
            if (usingSyringe) UpdateSyringeVisual(); else EndSyringeVisual();
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
                float recoil = actions.Busy && actions.CurrentKind == ActionKind.Attack && actions.ActiveWeapon != WeaponKind.Melee
                    ? Mathf.Sin(Mathf.Clamp01(actions.Current.Elapsed / actions.Current.Duration) * Mathf.PI) : 0f;
                _arms.transform.localRotation = Quaternion.Euler(-recoil * (actions.ActiveWeapon == WeaponKind.Shotgun ? 14f : 7f), 180, 0);
                _arms.transform.localPosition += Vector3.back * (recoil * .018f);
            }
        }

        void BeginSyringeVisual()
        {
            if (_syringe != null || syringePrefab == null) return;
            var socket = FindSocket(rightSocket);
            _syringe = Instantiate(syringePrefab, socket != null ? socket : cameraPivot);
            _syringe.name = "SyringeModel";
            if (socket != null) Place(_syringe.transform, syringeGrip, Quaternion.Euler(syringeEuler));
            else { _syringe.transform.localPosition = new Vector3(-0.12f, -0.18f, 0.46f); _syringe.transform.localRotation = Quaternion.Euler(syringeEuler); }
            foreach (var c in _syringe.GetComponentsInChildren<Collider>()) Destroy(c);
            PreparePresentation(_syringe);
            foreach (var t in _syringe.GetComponentsInChildren<Transform>(true)) t.gameObject.layer = gameObject.layer;

            _syringeCap = FindChild(_syringe.transform, "cap");
            _syringeCapRibs = FindChild(_syringe.transform, "cap_ribs");
            _syringeStopper = FindChild(_syringe.transform, "stopper");
            _syringePlunger = FindChild(_syringe.transform, "plunger");
            _syringePlungerRib = FindChild(_syringe.transform, "plunger_rib");
            _syringePlungerHead = FindChild(_syringe.transform, "plunger_head");
            Remember(_syringeCap, out _capStart); Remember(_syringeCapRibs, out _capRibsStart);
            Remember(_syringeStopper, out _stopperStart); Remember(_syringePlunger, out _plungerStart);
            Remember(_syringePlungerRib, out _plungerRibStart); Remember(_syringePlungerHead, out _plungerHeadStart);
            if (_weapon != null) _weapon.SetActive(false);
            SyringePress01 = 0f;
            Audio.AudioService.Instance?.Play2D("SND-SYRINGE-Use", 0.72f, Audio.AudioService.Instance.weapons);
        }

        void UpdateSyringeVisual()
        {
            if (_syringe == null) { BeginSyringeVisual(); if (_syringe == null) return; }
            float duration = Mathf.Max(0.01f, actions.Current.Duration);
            float p = Mathf.Clamp01(actions.Current.Elapsed / duration);
            float commit = actions.inventory != null && actions.inventory.player != null
                ? Mathf.Clamp01(actions.inventory.player.syringeCommit / duration) : 0.6875f;

            // La tapa sale primero. El émbolo sólo llega al fondo en el commit que consume la unidad y cura.
            float uncap = Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(0.02f, 0.20f, p));
            Move(_syringeCap, _capStart + Vector3.back * (0.035f * uncap));
            Move(_syringeCapRibs, _capRibsStart + Vector3.back * (0.035f * uncap));
            bool capVisible = p < 0.22f;
            if (_syringeCap != null) _syringeCap.gameObject.SetActive(capVisible);
            if (_syringeCapRibs != null) _syringeCapRibs.gameObject.SetActive(capVisible);

            SyringePress01 = Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(0.34f, commit, p));
            Vector3 press = Vector3.back * (0.028f * SyringePress01);
            Move(_syringeStopper, _stopperStart + press);
            Move(_syringePlunger, _plungerStart + press);
            Move(_syringePlungerRib, _plungerRibStart + press);
            Move(_syringePlungerHead, _plungerHeadStart + press);
        }

        void EndSyringeVisual()
        {
            if (_syringe == null) return;
            Destroy(_syringe); _syringe = null;
            _syringeCap = _syringeCapRibs = _syringeStopper = _syringePlunger = _syringePlungerRib = _syringePlungerHead = null;
            SyringePress01 = 0f;
            if (_weapon != null) _weapon.SetActive(true);
        }

        static Transform FindChild(Transform root, string childName)
        {
            foreach (var t in root.GetComponentsInChildren<Transform>(true)) if (t.name == childName) return t;
            return null;
        }

        static void Remember(Transform t, out Vector3 value) => value = t != null ? t.localPosition : Vector3.zero;
        static void Move(Transform t, Vector3 value) { if (t != null) t.localPosition = value; }

        void ShowWeapon(WeaponKind? kind)
        {
            actions.PresentationMuzzle = null;
            if (_weapon != null) Destroy(_weapon);
            _weapon = null;
            var prefab = kind == WeaponKind.Melee ? crowbarPrefab : kind == WeaponKind.Pistol ? pistolPrefab : kind == WeaponKind.Shotgun ? shotgunPrefab : null;
            if (prefab == null) return;
            var socket = FindSocket(rightSocket);
            _weapon = Instantiate(prefab, socket != null ? socket : cameraPivot); _weapon.name = "Weapon_" + kind;
            var rot = kind == WeaponKind.Melee ? Quaternion.Euler(-60f, 10f, 0f) : Quaternion.Euler(-90f,0f,0f);
            if (socket != null)
            {
                var grip = kind == WeaponKind.Melee ? crowbarGrip : kind == WeaponKind.Pistol ? pistolGrip : shotgunGrip;
                Place(_weapon.transform, grip, rot);
            }
            else { _weapon.transform.localPosition = weaponOffset; _weapon.transform.localRotation = rot; }
            foreach (var c in _weapon.GetComponentsInChildren<Collider>()) Destroy(c);
            PreparePresentation(_weapon);
            foreach (var t in _weapon.GetComponentsInChildren<Transform>()) t.gameObject.layer = gameObject.layer;
            if (kind == WeaponKind.Pistol || kind == WeaponKind.Shotgun)
                _weapon.AddComponent<WeaponFireVisual>().Initialize(actions, kind.Value);
            if (_syringe != null) _weapon.SetActive(false);
        }

        void ShowHeldItem(World.PickupKind? kind)
        {
            actions.PresentationMuzzle = null;
            if (_weapon != null) Destroy(_weapon);
            _weapon=null;
            var prefab=kind==World.PickupKind.Syringe ? syringePrefab : kind==World.PickupKind.Ration ? rationPrefab : kind==World.PickupKind.PistolAmmo ? pistolAmmoPrefab : kind==World.PickupKind.ShotgunAmmo ? shotgunAmmoPrefab : null;
            if (prefab==null) return;
            var socket=FindSocket(rightSocket);
            _weapon=Instantiate(prefab,socket!=null ? socket : cameraPivot); _weapon.name="Held_"+kind;
            if(kind==World.PickupKind.PistolAmmo || kind==World.PickupKind.ShotgunAmmo) _weapon.transform.localScale*=.5f;
            if(socket!=null)
            {
                var grip=kind==World.PickupKind.Ration ? new Vector3(0,0,.075f) : Vector3.zero;
                var rotation=kind==World.PickupKind.Syringe ? Quaternion.Euler(syringeEuler) : kind==World.PickupKind.Ration ? Quaternion.Euler(0,0,180) : Quaternion.Euler(-90,0,0);
                Place(_weapon.transform,grip,rotation);
            }
            else _weapon.transform.localPosition=weaponOffset;
            foreach(var c in _weapon.GetComponentsInChildren<Collider>()) Destroy(c);
            PreparePresentation(_weapon);
            if(_syringe!=null) _weapon.SetActive(false);
        }

        void Play(string clip, bool loop)
        {
            if (!_graph.IsValid() || !_slots.TryGetValue(clip, out var idx)) return;
            if (idx == _current) { if (!loop) { _clips[idx].SetTime(0); _clips[idx].SetDone(false); _clips[idx].SetSpeed(actions != null && actions.Current != null ? _clips[idx].GetAnimationClip().length / Mathf.Max(.01f,actions.Current.Duration) : 1f); } return; }
            for (int i = 0; i < _clips.Count; i++) if (i != _current) _mixer.SetInputWeight(i, 0f);
            _previous = _current; _current = idx; _blendT = 0f;
            var p = _clips[idx]; p.SetTime(0); p.SetDuration(loop ? double.MaxValue : p.GetAnimationClip().length);
            p.SetDone(false);
            p.SetSpeed(!loop && actions != null && actions.Current != null ? p.GetAnimationClip().length / Mathf.Max(.01f, actions.Current.Duration) : 1f);
        }
    }
}
