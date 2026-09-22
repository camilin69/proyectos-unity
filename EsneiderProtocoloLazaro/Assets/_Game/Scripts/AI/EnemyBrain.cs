using System.Collections.Generic;
using Esneider.Combat;
using Esneider.Core;
using Esneider.Core.Data;
using UnityEngine;
using UnityEngine.AI;

namespace Esneider.AI
{
    public enum EnemyState { Inactive, Patrol, Suspicious, Investigate, Alert, Chase, Prepare, Attack, Recover, Search, Return, Staggered, Executing, Dead }

    // Sección 14/78.2: FSM con transiciones explícitas. Orden por tick: muerte→derrota→interrupción→ataque→percepción→navegación.
    [RequireComponent(typeof(NavMeshAgent), typeof(Health), typeof(EnemyPerception))]
    public class EnemyBrain : MonoBehaviour
    {
        public EnemyDefinition definition;
        public string stableId;
        public bool startActive = true;
        public bool tutorialTelegraph;
        public List<Transform> waypoints = new List<Transform>();
        // 77.1: ida/vuelta (invertir en extremos) o cerrada; 1.5 s por punto, 3 s en extremos; espera inicial opcional (K02 8 s, K03 6 s)
        public bool patrolLoop;
        public float patrolDelay, pointWaitSeconds = 1.5f, endWaitSeconds = 3f;
        public Transform muzzle;
        public EnemyState State { get; private set; } = EnemyState.Inactive;
        public string LastTransition { get; private set; } = "";
        public int attacksEmitted;

        NavMeshAgent _agent; Health _health; EnemyPerception _perception; Transform _player;
        float _stateSince, _cooldownUntil, _staggerImmuneUntil, _lastCrowbarHit = -10f, _searchUntil, _waitUntil;
        int _crowbarHitsWindow, _wp, _searchPoints, _dir = 1;
        float _patrolHoldUntil;
        int _currentAttackId;
        bool _offMeshLogged;
        Vector3 _searchTarget;
        readonly List<Vector3> _searchCandidates = new List<Vector3>();
        static readonly System.Random _rng = new System.Random(7);

        public bool IsDead => State == EnemyState.Dead;
        public static event System.Action<EnemyBrain, EnemyState, EnemyState> AnyStateChanged;
        public float StateTime => Time.time - _stateSince;

        bool _awoken;
        void Awake() => EnsureRefs();

        // La hidratación (PersistentEntity.OnEnable) puede llegar antes que este Awake al cargar una región: inicializar bajo demanda.
        void EnsureRefs()
        {
            if (_awoken) return; _awoken = true;
            _agent = GetComponent<NavMeshAgent>(); _health = GetComponent<Health>(); _perception = GetComponent<EnemyPerception>();
            if (definition != null)
            {
                _health.maxHp = definition.maxHp; _health.ResetTo(definition.maxHp);
                _agent.speed = definition.patrolSpeed; _agent.angularSpeed = 240f; _agent.acceleration = 8f; _agent.stoppingDistance = 0.4f;
                _perception.definition = definition;
            }
            _health.Damaged += OnDamaged; _health.Died += OnDied;
            _agent.autoBraking = true;
        }

        void Start()
        {
            var pc = FindFirstObjectByType<Player.PlayerController>();
            if (pc != null) { _player = pc.transform; _perception.target = _player; _perception.targetFlashlight = pc.flashlight; }
            EncounterDirector.Ensure();
            if (!_agent.enabled) _agent.enabled = true; // la superficie regional ya existe en Start
            _patrolHoldUntil = Time.time + patrolDelay;
            Transition(startActive ? EnemyState.Patrol : EnemyState.Inactive);
        }

        public void Activate() { if (State == EnemyState.Inactive) { _patrolHoldUntil = Time.time + patrolDelay; Transition(EnemyState.Patrol); } }

        void AdvanceWaypoint()
        {
            int n = waypoints.Count; if (n <= 1) return;
            if (patrolLoop) { _wp = (_wp + 1) % n; return; }
            if (_wp + _dir < 0 || _wp + _dir >= n) _dir = -_dir;
            _wp += _dir;
        }

        void Transition(EnemyState next)
        {
            if (State == EnemyState.Dead) return;
            var prev = State;
            LastTransition = State + "->" + next; State = next; _stateSince = Time.time;
            _agent.updateRotation = next != EnemyState.Prepare && next != EnemyState.Attack && next != EnemyState.Recover;
            AnyStateChanged?.Invoke(this, prev, next);
            switch (next)
            {
                case EnemyState.Patrol: _agent.speed = definition.patrolSpeed; _perception.alertMode = false; GoToWaypoint(); break;
                case EnemyState.Chase: _agent.speed = definition.chaseSpeed; _perception.alertMode = true; break;
                case EnemyState.Search: _agent.speed = definition.chaseSpeed * 0.7f; _searchUntil = Time.time + (attacksEmitted > 0 ? definition.combatSearchSeconds : definition.searchSeconds); _searchPoints = 0; SafeDest(_perception.lastKnownPosition); break;
                case EnemyState.Return: _agent.speed = definition.patrolSpeed; _perception.alertMode = false; _perception.suspicion = 0f; GoToWaypoint(nearest: true); break;
                case EnemyState.Prepare: Stop(); break;
                case EnemyState.Recover: Stop(); break;
                case EnemyState.Staggered: Stop(); break;
                case EnemyState.Executing: _agent.speed = definition.chaseSpeed; _agent.isStopped = false; EncounterDirector.Instance?.Release(this); break;
            }
            if (next != EnemyState.Prepare && next != EnemyState.Attack && next != EnemyState.Recover && next != EnemyState.Chase) EncounterDirector.Instance?.Release(this);
        }

        void SafeDest(Vector3 p) { if (_agent.enabled && _agent.isOnNavMesh) _agent.SetDestination(p); }
        void Stop() { if (_agent.isOnNavMesh) { _agent.isStopped = true; _agent.velocity = Vector3.zero; } }
        void Resume() { if (_agent.isOnNavMesh) _agent.isStopped = false; }

        void Update()
        {
            if (State == EnemyState.Dead || State == EnemyState.Inactive) return;
            if (!_agent.enabled || !_agent.isOnNavMesh)
            {
                if (!_offMeshLogged) { _offMeshLogged = true; Debug.LogWarning($"{name} ({stableId}) fuera del NavMesh en {transform.position}: revisar spawn 68.7"); }
                return;
            }
            var flow = GameFlowController.Instance;
            if (flow != null && !flow.GameplayActive && flow.State != GameState.Captured) return;
            float dist = _player != null ? Vector3.Distance(transform.position, _player.position) : 999f;
            bool sees = _perception.SeesTarget;
            switch (State)
            {
                case EnemyState.Patrol:
                    if (_perception.Confirmed) { Transition(EnemyState.Alert); break; }
                    if (_perception.heardRecently) { _perception.heardRecently = false; Transition(EnemyState.Investigate); SafeDest(_perception.lastKnownPosition); Resume(); break; }
                    if (_perception.suspicion > 0.2f) { Transition(EnemyState.Suspicious); break; }
                    if (Time.time < _patrolHoldUntil) { Stop(); break; }
                    if (_agent.isStopped && _waitUntil <= 0f) Resume();
                    if (waypoints.Count > 0 && !_agent.pathPending && _agent.remainingDistance <= _agent.stoppingDistance + 0.1f)
                    {
                        bool end = !patrolLoop && (_wp == 0 || _wp == waypoints.Count - 1);
                        if (_waitUntil <= 0f) _waitUntil = Time.time + (end ? endWaitSeconds : pointWaitSeconds);
                        else if (Time.time >= _waitUntil) { _waitUntil = 0f; AdvanceWaypoint(); GoToWaypoint(); }
                    }
                    break;
                case EnemyState.Suspicious:
                    Stop(); FaceTowards(_perception.lastKnownPosition.sqrMagnitude > 0 ? _perception.lastKnownPosition : (_player != null ? _player.position : transform.position));
                    if (_perception.Confirmed) Transition(EnemyState.Alert);
                    else if (_perception.suspicion <= 0.01f) { Resume(); Transition(EnemyState.Patrol); }
                    break;
                case EnemyState.Investigate:
                    if (_perception.Confirmed) { Transition(EnemyState.Alert); break; }
                    if (_perception.heardRecently) { _perception.heardRecently = false; SafeDest(_perception.lastKnownPosition); }
                    if (!_agent.pathPending && _agent.remainingDistance <= 0.6f)
                    {
                        if (_waitUntil <= 0f) _waitUntil = Time.time + 3f;
                        else if (Time.time >= _waitUntil) { _waitUntil = 0f; Transition(EnemyState.Return); }
                    }
                    break;
                case EnemyState.Alert:
                    NoiseSystem.Emit(transform.position, 0.01f, gameObject, "acquire");
                    ShareAlert();
                    Transition(EnemyState.Chase);
                    break;
                case EnemyState.Chase:
                    Resume();
                    // Keep the face toward a visible target even while retreating. Navigation
                    // still supplies position, but must not turn the body toward the escape path.
                    _agent.updateRotation = !sees;
                    if (sees && _player != null) FaceTowards(_player.position);
                    if (!sees && Time.time - _perception.lastSeenTime > 1.5f) { Transition(EnemyState.Search); break; }
                    // la última posición conocida la fija la percepción en el instante en que ve (14: sin omnisciencia)
                    bool inRange = dist >= definition.attackRangeMin && dist <= definition.attackRangeMax;
                    if (sees && inRange && Time.time >= _cooldownUntil && EncounterDirector.Instance != null && EncounterDirector.Instance.TryAcquireSlot(this))
                    { Transition(EnemyState.Prepare); break; }
                    // 13/78.3: demasiado cerca → retroceder a posición libre, sin golpe melee
                    if (dist < definition.attackRangeMin) { var away = transform.position + (transform.position - _player.position).normalized * 3f; if (NavMesh.SamplePosition(away, out var h, 2f, NavMesh.AllAreas)) SafeDest(h.position); }
                    else SafeDest(_perception.lastKnownPosition);
                    break;
                case EnemyState.Prepare:
                    FaceTowards(_player.position);
                    EncounterDirector.Instance?.Heartbeat(this);
                    if (!sees) { Transition(EnemyState.Chase); break; } // perder visión cancela red/rayo (78.2)
                    float telegraph = (tutorialTelegraph ? definition.telegraphTutorial : definition.telegraph) * AccessibilitySettings.TelegraphScale; // 80.3 asistencia explícita
                    if (StateTime >= telegraph && FacingTarget && EncounterDirector.Instance.CanEmitNow()) Transition(EnemyState.Attack);
                    break;
                case EnemyState.Attack:
                    FaceTowards(_player.position);
                    Emit();
                    Transition(EnemyState.Recover);
                    break;
                case EnemyState.Recover:
                    FaceTowards(_player.position, 60f);
                    if (StateTime >= definition.recovery) { Resume(); Transition(EnemyState.Chase); }
                    break;
                case EnemyState.Search:
                    if (sees) { Transition(EnemyState.Chase); break; }
                    if (Time.time >= _searchUntil) { Transition(EnemyState.Return); break; }
                    if (!_agent.pathPending && _agent.remainingDistance <= 0.8f)
                    {
                        if (_searchPoints >= 3) { Transition(EnemyState.Return); break; }
                        var rnd = _perception.lastKnownPosition + new Vector3((float)_rng.NextDouble() * 12f - 6f, 0, (float)_rng.NextDouble() * 12f - 6f);
                        if (NavMesh.SamplePosition(rnd, out var hit, 3f, NavMesh.AllAreas)) { SafeDest(hit.position); _searchPoints++; }
                        else _searchPoints++;
                    }
                    break;
                case EnemyState.Return:
                    if (_perception.Confirmed) { Transition(EnemyState.Alert); break; }
                    if (_perception.heardRecently) { _perception.heardRecently = false; Transition(EnemyState.Investigate); SafeDest(_perception.lastKnownPosition); break; }
                    if (!_agent.pathPending && _agent.remainingDistance <= 0.6f) Transition(EnemyState.Patrol);
                    break;
                case EnemyState.Staggered:
                    float stagger = definition.kind == EnemyKind.Vigia ? 0.45f : 0.3f;
                    if (StateTime >= stagger) { _staggerImmuneUntil = Time.time + 1.2f; Resume(); Transition(EnemyState.Chase); }
                    break;
                case EnemyState.Executing:
                    if (_player != null) SafeDest(_player.position);
                    break;
            }
        }

        void Emit()
        {
            if (!FacingTarget) return;
            // Recheck at release: perception is sampled at 10 Hz and a door can close between samples.
            _perception.Sense(0f);
            if (!_perception.SeesTarget) return;
            var origin = muzzle != null ? muzzle.position : transform.position + Vector3.up * 1.0f + transform.forward * 0.5f;
            var aim = (_player.position + Vector3.up * 1.0f) - origin; // apuntar al punto del jugador al liberar, sin perseguirlo (12.1)
            if (Physics.Linecast(origin, origin + aim, GameLayers.VisionBlockMask, QueryTriggerInteraction.Ignore)
                || Physics.Linecast(origin + aim, origin, GameLayers.VisionBlockMask, QueryTriggerInteraction.Ignore)) return;
            _currentAttackId = AttackIds.Next(); attacksEmitted++;
            var kind = definition.kind == EnemyKind.Vigia ? ProjectileKind.Net : ProjectileKind.Bolt;
            Projectile.Spawn(kind, origin, aim, gameObject, _currentAttackId, definition.attackDamage * (kind == ProjectileKind.Bolt ? AccessibilitySettings.RayDamageScale : 1f));
            EncounterDirector.Instance?.RegisterEmission();
            _cooldownUntil = Time.time + definition.cooldown;
            NoiseSystem.Emit(origin, 6f, gameObject, "attack");
        }

        void ShareAlert()
        {
            foreach (var other in FindObjectsByType<EnemyBrain>(FindObjectsSortMode.None))
            {
                if (other == this || other.IsDead || Vector3.Distance(other.transform.position, transform.position) > 12f) continue;
                if (Physics.Linecast(transform.position + Vector3.up, other.transform.position + Vector3.up, GameLayers.VisionBlockMask)) continue;
                other._perception.lastKnownPosition = _perception.lastKnownPosition; other._perception.lastKnownTime = Time.time; other._perception.heardRecently = true;
            }
        }

        void GoToWaypoint(bool nearest = false)
        {
            if (waypoints.Count == 0) { Stop(); return; }
            if (nearest)
            {
                float best = float.MaxValue;
                for (int i = 0; i < waypoints.Count; i++) { float d = Vector3.Distance(transform.position, waypoints[i].position); if (d < best) { best = d; _wp = i; } }
            }
            Resume(); SafeDest(waypoints[_wp].position); _waitUntil = 0f;
        }

        void FaceTowards(Vector3 p, float degPerSec = 360f)
        {
            var d = p - transform.position; d.y = 0;
            if (d.sqrMagnitude < 0.001f) return;
            transform.rotation = Quaternion.RotateTowards(transform.rotation, Quaternion.LookRotation(d), degPerSec * Time.deltaTime);
        }

        public bool FacingTarget
        {
            get
            {
                if (_player == null) return false;
                var direction = _player.position - transform.position; direction.y = 0;
                return direction.sqrMagnitude < .001f || Vector3.Dot(transform.forward, direction.normalized) >= .966f;
            }
        }

        void OnDamaged(DamageInfo info, float remaining)
        {
            _perception.OnDamaged(info);
            if (State == EnemyState.Patrol || State == EnemyState.Suspicious || State == EnemyState.Investigate || State == EnemyState.Return || State == EnemyState.Search)
            { Transition(EnemyState.Alert); }
            // 78.3: stagger por varilla
            if (info.kind == "Crowbar" && Time.time >= _staggerImmuneUntil && State != EnemyState.Staggered && State != EnemyState.Executing)
            {
                bool trigger;
                if (definition.kind == EnemyKind.Vigia) trigger = true;
                else { if (Time.time - _lastCrowbarHit <= 2f) _crowbarHitsWindow++; else _crowbarHitsWindow = 1; _lastCrowbarHit = Time.time; trigger = _crowbarHitsWindow >= 2; if (trigger) _crowbarHitsWindow = 0; }
                if (trigger) Transition(EnemyState.Staggered);
            }
        }

        void OnDied(DamageInfo info)
        {
            var prev = State; State = EnemyState.Dead; LastTransition = "->Dead"; AnyStateChanged?.Invoke(this, prev, EnemyState.Dead);
            EncounterDirector.Instance?.Release(this);
            Projectile.DespawnAllFrom(gameObject);
            if (_agent.isOnNavMesh) _agent.isStopped = true; _agent.enabled = false;
            foreach (var c in GetComponentsInChildren<Collider>()) { c.gameObject.layer = GameLayers.Corpse; }
            gameObject.layer = GameLayers.Corpse;
            gameObject.GetOrAdd<RobotDestruction>().Explode(false);
            if (GameFlowController.Instance != null) GameFlowController.Instance.enemiesKilled++;
            enabled = false;
        }

        public void OnNetCaptured(Player.PlayerController player) { if (State != EnemyState.Dead && player.IsCaptured && player.CaptureSource==gameObject) Transition(EnemyState.Executing); }
        public void OnCaptureEscaped() { if (State==EnemyState.Executing) Transition(EnemyState.Staggered); }

        // ---- persistencia (19/88.6): solo estados estables ----
        public string StableMode => State == EnemyState.Dead ? "Dead" : State == EnemyState.Inactive ? "Inactive" : "Patrol";
        public int CurrentWaypoint => _wp;

        public void RestoreStable(string mode, int waypoint)
        {
            EnsureRefs();
            _wp = waypoints.Count > 0 ? Mathf.Clamp(waypoint, 0, waypoints.Count - 1) : 0;
            _perception.suspicion = 0f; _perception.heardRecently = false; _cooldownUntil = 0f;
            if (State == EnemyState.Dead) return;
            if (!_agent.enabled) _agent.enabled = true;
            if (mode == "Inactive") { State = EnemyState.Inactive; LastTransition = "restore->Inactive"; Stop(); }
            else if (_agent.isOnNavMesh) Transition(EnemyState.Patrol);
            else { State = EnemyState.Patrol; LastTransition = "restore->Patrol(pending navmesh)"; }
        }

        public void MarkDeadFromSnapshot()
        {
            EnsureRefs();
            if (State == EnemyState.Dead) return;
            State = EnemyState.Dead; LastTransition = "restore->Dead";
            EncounterDirector.Instance?.Release(this);
            if (_agent.enabled && _agent.isOnNavMesh) _agent.isStopped = true; _agent.enabled = false;
            foreach (var c in GetComponentsInChildren<Collider>()) c.gameObject.layer = GameLayers.Corpse;
            gameObject.layer = GameLayers.Corpse;
            gameObject.GetOrAdd<RobotDestruction>().HideForSnapshot();
            enabled = false;
        }

        public void WarpTo(Vector3 position, Vector3 euler)
        {
            EnsureRefs();
            if (_agent.enabled && _agent.isOnNavMesh) _agent.Warp(position); else transform.position = position;
            transform.eulerAngles = new Vector3(0f, euler.y, 0f);
        }

        // Revivir tras cargar un snapshot anterior a la muerte (retry): el registro manda.
        public void ReviveForRestore()
        {
            EnsureRefs();
            if (State != EnemyState.Dead) return;
            GetComponent<RobotDestruction>()?.RestoreVisuals();
            gameObject.layer = GameLayers.Enemy;
            foreach (var c in GetComponentsInChildren<Collider>()) c.gameObject.layer = GameLayers.Enemy;
            transform.rotation = Quaternion.Euler(0f, transform.eulerAngles.y, 0f);
            _agent.enabled = true; enabled = true;
            State = EnemyState.Patrol; LastTransition = "revive";
        }
    }
}
