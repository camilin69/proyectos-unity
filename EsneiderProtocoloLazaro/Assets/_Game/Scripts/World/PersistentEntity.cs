using Esneider.AI;
using Esneider.Core;
using Esneider.Core.Persistence;
using UnityEngine;

namespace Esneider.World
{
    // Enlaza una instancia de escena con su estado lógico en WorldStateRegistry (88.6): hidrata al activarse y publica cambios.
    public class PersistentEntity : MonoBehaviour
    {
        public string stableId;
        public string guid;
        public string regionId;
        public string prefabId;
        public EntityKind kind;
        public bool hydrated;

        Pickup _pickup; Door _door; HingedCabinet _cabinet; EnemyBrain _brain; BossBrain _boss; Health _health; Rigidbody _rb;
        Vector3 _lastPos; float _nextMoveCheck;

        void Awake()
        {
            if (string.IsNullOrEmpty(guid) && !string.IsNullOrEmpty(stableId)) guid = Core.Data.LevelPlan.StableGuid(stableId).ToString();
            _pickup = GetComponent<Pickup>(); _door = GetComponent<Door>(); _cabinet = GetComponent<HingedCabinet>(); _brain = GetComponent<EnemyBrain>(); _boss = GetComponent<BossBrain>(); _health = GetComponent<Health>(); _rb = GetComponent<Rigidbody>();
        }

        bool _subscribed;
        EntityState _initial;

        void OnEnable() { EnsureRegistered(); }
        void Start() { EnsureRegistered(); }

        // El GUID puede asignarse después de AddComponent (OnEnable ya corrió): registrar en cuanto exista.
        public void EnsureRegistered()
        {
            if (string.IsNullOrEmpty(guid) && !string.IsNullOrEmpty(stableId)) guid = Core.Data.LevelPlan.StableGuid(stableId).ToString();
            if (string.IsNullOrEmpty(guid)) return;
            if (_pickup == null) { _pickup = GetComponent<Pickup>(); _door = GetComponent<Door>(); _cabinet = GetComponent<HingedCabinet>(); _brain = GetComponent<EnemyBrain>(); _boss = GetComponent<BossBrain>(); _health = GetComponent<Health>(); _rb = GetComponent<Rigidbody>(); }
            if (_initial == null)
                _initial = new EntityState { guid=guid, prefabId=prefabId, regionId=regionId, kind=kind, stateVersion=1,
                    amount=_pickup != null ? _pickup.amount : -1, hp=_health != null ? _health.maxHp : -1,
                    hasTransform=true, position=transform.position, eulerAngles=transform.eulerAngles,
                    isOpen=_door != null ? _door.isOpen : _cabinet != null && _cabinet.isOpen,
                    unlocked=_door == null || !_door.locked, mode=_brain != null && !_brain.startActive ? "Inactive" : "Patrol" };
            if (!_subscribed && _health != null) { _health.Damaged += OnDamaged; _health.Died += OnDied; _subscribed = true; }
            if (hydrated) return;
            var s = WorldStateRegistry.Session.GetOrCreate(guid, prefabId, regionId, kind);
            Hydrate(s);
        }

        void OnDisable()
        {
            if (_subscribed && _health != null) { _health.Damaged -= OnDamaged; _health.Died -= OnDied; _subscribed = false; }
        }

        // Hidratar es leer el registro, no repetir eventos.
        public void Hydrate(EntityState s)
        {
            hydrated = true;
            switch (kind)
            {
                case EntityKind.Pickup:
                    if (_pickup == null) break;
                    if (s.taken) gameObject.SetActive(false);
                    else if (s.amount >= 0) { _pickup.amount = s.amount; if (s.amount == 0) gameObject.SetActive(false); }
                    break;
                case EntityKind.Door:
                    if (_cabinet != null) { if (s.stateVersion > 0) _cabinet.SnapOpen(s.isOpen); break; }
                    if (_door == null) break;
                    if (s.stateVersion > 0) { _door.locked = !s.unlocked; _door.SnapOpen(s.isOpen); }
                    break;
                case EntityKind.Enemy:
                case EntityKind.Boss:
                    if (_health == null) break;
                    if (s.hp >= 0f)
                    {
                        if (s.dead || s.hp <= 0f) { _health.ResetTo(0f); _brain?.MarkDeadFromSnapshot(); _boss?.MarkDeadFromSnapshot(); }
                        else { _brain?.ReviveForRestore(); _boss?.ReviveForRestore(); _health.ResetTo(s.hp); _brain?.RestoreStable(s.mode, s.waypoint); _boss?.RestoreStable(); }
                    }
                    if (s.hasTransform)
                    {
                        if (_brain != null && !s.dead) _brain.WarpTo(s.position, s.eulerAngles);
                        else if (_boss != null && !s.dead) _boss.WarpTo(s.position, s.eulerAngles);
                        else { transform.position = s.position; transform.eulerAngles = s.eulerAngles; }
                    }
                    break;
                case EntityKind.Movable:
                case EntityKind.Corpse:
                    if (s.hasTransform)
                    {
                        transform.position = s.position; transform.eulerAngles = s.eulerAngles;
                        if (_rb != null) { _rb.linearVelocity = Vector3.zero; _rb.angularVelocity = Vector3.zero; }
                    }
                    _lastPos = transform.position;
                    break;
            }
        }

        // ---- publicación de cambios ----
        public void RestoreInitial()
        {
            EnsureRegistered();
            if (_initial == null) return;
            WorldStateRegistry.Session.GetOrCreate(guid,prefabId,regionId,kind);
            gameObject.SetActive(true); Hydrate(_initial.Clone()); CaptureStable();
        }
        public void NotifyPickupTaken(int remaining)
        {
            EnsureRegistered();
            WorldStateRegistry.Session.Apply(WorldEventKind.PickupTaken, guid, s => { s.amount = remaining; s.taken = remaining <= 0; }, remaining.ToString());
        }

        public void NotifyDoor(bool open, bool unlocked)
        {
            WorldStateRegistry.Session.Apply(WorldEventKind.DoorChanged, guid, s => { s.isOpen = open; s.unlocked = unlocked; }, open ? "open" : "closed");
        }

        void OnDamaged(DamageInfo info, float remaining)
        {
            WorldStateRegistry.Session.Apply(WorldEventKind.EnemyDamaged, guid, s => { s.hp = remaining; s.dead = remaining <= 0f; }, remaining.ToString("F0"));
        }

        void OnDied(DamageInfo info)
        {
            WorldStateRegistry.Session.Apply(WorldEventKind.EnemyDied, guid, s => { s.hp = 0f; s.dead = true; s.mode = "Dead"; s.hasTransform = true; s.position = transform.position; s.eulerAngles = transform.eulerAngles; });
        }

        void Update()
        {
            if (kind != EntityKind.Movable || Time.time < _nextMoveCheck) return;
            _nextMoveCheck = Time.time + 0.5f;
            if (_rb != null && _rb.linearVelocity.sqrMagnitude > 0.01f) return; // registrar en reposo
            if ((transform.position - _lastPos).sqrMagnitude < 0.01f) return;
            _lastPos = transform.position;
            var pos = transform.position; var rot = transform.eulerAngles;
            WorldStateRegistry.Session.Apply(WorldEventKind.PropMoved, guid, s => { s.hasTransform = true; s.position = pos; s.eulerAngles = rot; });
        }

        // Captura el estado estable actual (enemigos vivos: modo/waypoint) justo antes del snapshot.
        public void CaptureStable()
        {
            EnsureRegistered();
            var reg = WorldStateRegistry.Session;
            if (!reg.TryGet(guid, out var s)) return;
            if ((kind == EntityKind.Enemy || kind == EntityKind.Boss) && _health != null && !_health.IsDead)
            {
                s.hp = _health.Current; s.dead = false; s.mode = _brain != null ? _brain.StableMode : _boss != null ? _boss.StableMode : "Patrol"; s.waypoint = _brain != null ? _brain.CurrentWaypoint : 0;
                s.hasTransform = true; s.position = transform.position; s.eulerAngles = transform.eulerAngles;
            }
            if (kind == EntityKind.Movable) { s.hasTransform = true; s.position = transform.position; s.eulerAngles = transform.eulerAngles; }
            if (kind == EntityKind.Pickup && _pickup != null) { s.amount = _pickup.amount; s.taken = !gameObject.activeSelf || _pickup.amount <= 0; }
            if (kind == EntityKind.Door && _door != null) { s.isOpen = _door.isOpen; s.unlocked = !_door.locked; s.stateVersion = Mathf.Max(1,s.stateVersion); }
            if (kind == EntityKind.Door && _cabinet != null) { s.isOpen = _cabinet.isOpen; s.stateVersion = Mathf.Max(1,s.stateVersion); }
        }
    }
}
