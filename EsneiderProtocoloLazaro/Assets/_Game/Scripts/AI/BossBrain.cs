using System.Collections.Generic;
using Esneider.Core;
using Esneider.Core.Data;
using Esneider.Core.Persistence;
using UnityEngine;
using UnityEngine.AI;

namespace Esneider.AI
{
    public enum BossState { Dormant, Awakening, Engage, Prepare, Attack, Recover, Transition, Dead }

    // 15/61/79.2/103.1: EL ARCHIVISTA. Solo melee del jugador cuenta como ventana; sin redes, sin adds, sin invulnerabilidad larga.
    // Fase I (1200–801): rayo 30 (aviso 1.2 s / rec 2.0) y barrido 30 (1.4 / 2.2). Fase II (800–401): secuencia doble separada 0.8 s, rec 2.5 tras la segunda.
    // Fase III (400–1): carga 45 (1.5 / 2.4, trayectoria comprometida al terminar el aviso) y pulso 30 radio 6 m (1.8 / 2.4, centro fijado al iniciar el gesto, pilares no lo bloquean); nunca dos pulsos seguidos.
    // Cambio de fase: terminar el ataque emitido → transición 2 s sin emisión. Muerte: cancelar, pool, agente parado, colapso, BOSS_DEFEATED, O10, CP-07.
    public class BossBrain : MonoBehaviour
    {
        public BossDefinition definition;
        public string stableId = "B01";
        public Transform muzzle;
        public Vector3 arenaCenter, arenaSize; public float arenaInset = 2.5f;
        public string arenaDoorId = "D27";
        public float approachSpeed = 1.6f, chargeSpeed = 9f, chargeMaxDistance = 12f, sweepRange = 3.5f, sweepHalfAngle = 60f, rayMinRange = 4f, rayMaxRange = 18f;
        public float attackGap = 0.6f;
        public bool debugLog;
        void OnDestroy() { if (debugLog) Debug.Log($"BOSS {stableId} destroyed (scene {gameObject.scene.name}, loaded={gameObject.scene.isLoaded})\n{System.Environment.StackTrace}"); }
        void OnDisable() { if (debugLog) Debug.Log($"BOSS {stableId} disabled state={State}"); }

        public BossState State { get; private set; } = BossState.Dormant;
        public int Phase { get; private set; } = 1;
        public string CurrentAttack { get; private set; } = "";
        public readonly List<string> Emitted = new List<string>();
        public int attacksEmitted;
        public float StateTime => Time.time - _stateSince;
        public string LastTransition { get; private set; } = "";
        public bool IsDead => State == BossState.Dead;

        NavMeshAgent _agent; Health _health; Transform _player; EnemyAnimator _anim;
        float _stateSince, _nextAttackAt; int _pendingPhase; int _attackId; bool _inDouble; int _doubleStep;
        Vector3 _chargeDir, _chargeStart, _pulseCenter; bool _chargeHit; GameObject _pulseRing; string _lastAttack = "";
        static readonly System.Random _rng = new System.Random(11);
        BossAttackDefinition Def(string id) => definition.attacks.Find(a => a.id == id);

        bool _awoken;
        void Awake() => EnsureRefs();
        void EnsureRefs()
        {
            if (_awoken) return; _awoken = true;
            _agent = GetComponent<NavMeshAgent>(); _health = GetComponent<Health>(); _anim = GetComponent<EnemyAnimator>();
            if (definition != null) { _health.maxHp = definition.maxHp; _health.ResetTo(definition.maxHp); }
            _health.Damaged += OnDamaged; _health.Died += OnDied;
            _agent.speed = approachSpeed; _agent.angularSpeed = 120f; _agent.acceleration = 6f; _agent.stoppingDistance = 2.2f; _agent.autoBraking = true;
        }

        void Start()
        {
            var pc = FindFirstObjectByType<Player.PlayerController>(); if (pc != null) _player = pc.transform;
            if (!_agent.enabled) _agent.enabled = true;
            if (State != BossState.Dead) Set(BossState.Dormant);
        }

        void Set(BossState next)
        {
            if (State == BossState.Dead) return;
            LastTransition = State + "->" + next; State = next; _stateSince = Time.time;
            if (debugLog) Debug.Log($"BOSS {stableId}: {LastTransition} t={Time.time:F2} phase={Phase} hp={_health?.Current}");
            switch (next)
            {
                case BossState.Dormant: Stop(); _anim?.Play("Archivista_Idle", true); break;
                case BossState.Awakening: Stop(); _anim?.Play("Archivista_Idle", true); break;
                case BossState.Engage: Resume(); break;
                case BossState.Prepare: Stop(); break;
                case BossState.Recover: Stop(); _anim?.Play("Archivista_Idle", true); break;
                case BossState.Transition: Stop(); _anim?.Play("Archivista_Idle", true); break;
            }
        }

        void Stop() { if (_agent.enabled && _agent.isOnNavMesh) { _agent.isStopped = true; _agent.velocity = Vector3.zero; } }
        void Resume() { if (_agent.enabled && _agent.isOnNavMesh) _agent.isStopped = false; }
        bool PlayerInArena(float inset)
        {
            if (_player == null) return false; var d = _player.position - arenaCenter;
            return Mathf.Abs(d.x) <= arenaSize.x / 2f - inset && Mathf.Abs(d.z) <= arenaSize.z / 2f - inset && Mathf.Abs(d.y) <= arenaSize.y;
        }
        float Dist => _player != null ? Vector3.Distance(transform.position, _player.position) : 999f;
        bool HasLos()
        {
            if (_player == null) return false;
            var from = transform.position + Vector3.up * 2.2f; var to = _player.position + Vector3.up * 1.0f;
            return !Physics.Linecast(from, to, GameLayers.VisionBlockMask, QueryTriggerInteraction.Ignore);
        }

        void Update()
        {
            if (State == BossState.Dead || _player == null) return;
            var flow = GameFlowController.Instance;
            if (flow != null && !flow.GameplayActive) { if (debugLog && State == BossState.Awakening && Time.frameCount % 60 == 0) Debug.Log($"BOSS wait: flow {flow.State}"); return; }
            if (!_agent.enabled || !_agent.isOnNavMesh) { if (debugLog && Time.frameCount % 60 == 0) Debug.Log($"BOSS wait: agent enabled={_agent.enabled} onMesh={_agent.isOnNavMesh} pos={transform.position}"); return; }
            switch (State)
            {
                case BossState.Dormant:
                    // EVT-21: cruzar D27 y entrar con espacio útil; retirarse antes del umbral no inicia la fase (61.1)
                    if (ObjectiveService.Has(ObjectiveService.BossDefeated)) break;
                    if (PlayerInArena(arenaInset) && World.EventRunner.Instance != null && World.EventRunner.Instance.TryRunOnce("EVT-21", () => { }))
                    {
                        Set(BossState.Awakening);
                        var hud = FindFirstObjectByType<UI.HudController>(); hud?.ShowBoss("EL ARCHIVISTA"); hud?.ShowMessage("[EVA] Unidad humana no conciliada. La recuperación continúa.", 5f);
                        Audio.AudioService.Instance?.Play("SND-Alert-Short", transform.position + Vector3.up * 3f, 0.7f, 8, 0f, Audio.AudioService.Instance.voice, false);
                        foreach (var d in FindObjectsByType<World.Door>(FindObjectsSortMode.None)) if (d.doorId == arenaDoorId && d.isOpen) d.SetOpen(false); // cierre con chequeo de obstrucción (Door)
                    }
                    break;
                case BossState.Awakening:
                    Face(_player.position, 60f);
                    if (StateTime >= 2.0f) { _nextAttackAt = Time.time + 0.8f; Set(BossState.Engage); }
                    break;
                case BossState.Engage:
                    if (_pendingPhase > Phase) { Set(BossState.Transition); break; }
                    _agent.speed = approachSpeed; _anim?.Play(_agent.velocity.sqrMagnitude > 0.05f ? "Archivista_Walk" : "Archivista_Idle", true);
                    if (Time.time >= _nextAttackAt)
                    {
                        var choice = Choose();
                        if (choice != null) { Begin(choice); break; }
                    }
                    if (_agent.isOnNavMesh) _agent.SetDestination(_player.position);
                    break;
                case BossState.Prepare:
                {
                    var a = Def(CurrentAttack); float telegraph = a.telegraph * AccessibilitySettings.TelegraphScale;
                    if (CurrentAttack != "BOSS-PULSO") Face(_player.position, CurrentAttack == "BOSS-CARGA" ? 90f : 180f);
                    if (StateTime >= telegraph) { Set(BossState.Attack); Emit(a); }
                    break;
                }
                case BossState.Attack:
                    if (CurrentAttack == "BOSS-CARGA") { if (!TickCharge()) FinishAttack(); }
                    else FinishAttack();
                    break;
                case BossState.Recover:
                {
                    float rec = _inDouble && _doubleStep == 1 ? definition.doubleSequenceGap : (_inDouble ? definition.doubleSequenceRecovery : Def(CurrentAttack).recovery);
                    if (StateTime >= rec)
                    {
                        if (_inDouble && _doubleStep == 1) { _doubleStep = 2; var second = ChooseFrom(Phase1Pool(), true); if (second != null) { Begin(second, keepDouble: true); break; } }
                        _inDouble = false; _doubleStep = 0;
                        if (_pendingPhase > Phase) { Set(BossState.Transition); break; }
                        _nextAttackAt = Time.time + attackGap; Set(BossState.Engage);
                    }
                    break;
                }
                case BossState.Transition:
                    if (StateTime >= definition.phaseTransitionSeconds)
                    {
                        Phase = Mathf.Max(Phase, _pendingPhase); _pendingPhase = 0;
                        FindFirstObjectByType<UI.HudController>()?.ShowMessage(Phase == 2 ? "El torso reajusta su postura; un soporte interno hace click." : "El apoyo cambia de longitud; una luz interna marca sobrecarga.", 3f);
                        _nextAttackAt = Time.time + attackGap; Set(BossState.Engage);
                    }
                    break;
            }
        }

        // ---- selección de ataques ----
        List<string> Phase1Pool() => new List<string> { "BOSS-RAYO", "BOSS-BARRIDO" };
        string Choose()
        {
            if (Phase <= 2) { var pick = ChooseFrom(Phase1Pool(), false); if (pick != null && Phase == 2) { _inDouble = true; _doubleStep = 1; } return pick; }
            var pool = new List<string> { "BOSS-CARGA", "BOSS-PULSO", "BOSS-RAYO" };
            if (_lastAttack == "BOSS-PULSO") pool.Remove("BOSS-PULSO");
            return ChooseFrom(pool, false);
        }
        string ChooseFrom(List<string> pool, bool second)
        {
            var feasible = new List<string>();
            float d = Dist; bool los = HasLos();
            foreach (var id in pool)
            {
                switch (id)
                {
                    case "BOSS-RAYO": if (los && d >= rayMinRange && d <= rayMaxRange) feasible.Add(id); break;
                    case "BOSS-BARRIDO": if (d <= sweepRange + 0.5f) feasible.Add(id); break;
                    case "BOSS-CARGA": if (los && d >= 4f && d <= 14f) feasible.Add(id); break;
                    case "BOSS-PULSO": if (d <= 7f) feasible.Add(id); break;
                }
            }
            if (feasible.Count == 0) return second ? (los && d <= rayMaxRange ? "BOSS-RAYO" : null) : null;
            return feasible[_rng.Next(feasible.Count)];
        }

        void Begin(string id, bool keepDouble = false)
        {
            if (!keepDouble && Phase != 2) _inDouble = false;
            CurrentAttack = id; Set(BossState.Prepare);
            _anim?.Play(id == "BOSS-RAYO" ? "Archivista_Ray" : id == "BOSS-BARRIDO" ? "Archivista_Sweep" : id == "BOSS-CARGA" ? "Archivista_Charge" : "Archivista_Pulse", false);
            if (id == "BOSS-PULSO") { _pulseCenter = transform.position; ShowRing(); Audio.AudioService.Instance?.Play("SND-BOSS-Pulse", transform.position, 0.8f, 16, 0f, Audio.AudioService.Instance.enemies, false); }
            else Audio.AudioService.Instance?.Play(id == "BOSS-RAYO" ? "SND-BOSS-Ray" : id == "BOSS-BARRIDO" ? "SND-BOSS-Sweep" : "SND-BOSS-Charge", transform.position + Vector3.up * 2f, 0.8f, 16, 0f, Audio.AudioService.Instance.enemies, false);
        }

        void Emit(BossAttackDefinition a)
        {
            _attackId = AttackIds.Next(); attacksEmitted++; Emitted.Add(a.id); _lastAttack = a.id;
            var hp = _player.GetComponent<Health>();
            switch (a.id)
            {
                case "BOSS-RAYO":
                {
                    var origin = muzzle != null ? muzzle.position : transform.position + Vector3.up * 2.2f + transform.forward * 0.6f;
                    var aim = (_player.position + Vector3.up * 1.0f) - origin;
                    Combat.Projectile.Spawn(Combat.ProjectileKind.BossBolt, origin, aim, gameObject, _attackId, a.damage * AccessibilitySettings.RayDamageScale);
                    break;
                }
                case "BOSS-BARRIDO":
                {
                    var to = _player.position - transform.position; to.y = 0;
                    if (to.magnitude <= sweepRange && Vector3.Angle(transform.forward, to) <= sweepHalfAngle && HasLos())
                        hp?.ApplyDamage(new DamageInfo { amount = a.damage, attackId = _attackId, source = gameObject, point = _player.position, direction = to.normalized, kind = a.id });
                    break;
                }
                case "BOSS-CARGA":
                {
                    var to = _player.position - transform.position; to.y = 0; _chargeDir = to.normalized; _chargeStart = transform.position; _chargeHit = false;
                    transform.rotation = Quaternion.LookRotation(_chargeDir); Resume(); _agent.speed = chargeSpeed;
                    break;
                }
                case "BOSS-PULSO":
                {
                    HideRing();
                    var d = _player.position - _pulseCenter; d.y = 0;
                    if (d.magnitude <= a.radius) hp?.ApplyDamage(new DamageInfo { amount = a.damage, attackId = _attackId, source = gameObject, point = _player.position, direction = d.normalized, kind = a.id });
                    break;
                }
            }
            NoiseSystem.Emit(transform.position, 8f, gameObject, "boss");
        }

        bool TickCharge()
        {
            var a = Def("BOSS-CARGA");
            var step = _chargeDir * chargeSpeed * Time.deltaTime;
            var before = transform.position; _agent.Move(step);
            float moved = (transform.position - before).magnitude;
            if (!_chargeHit && _player != null)
            {
                var to = _player.position - transform.position; to.y = 0;
                if (to.magnitude <= 1.6f) { _chargeHit = true; _player.GetComponent<Health>()?.ApplyDamage(new DamageInfo { amount = a.damage, attackId = _attackId, source = gameObject, point = _player.position, direction = _chargeDir, kind = a.id }); }
            }
            bool blocked = moved < step.magnitude * 0.3f && StateTime > 0.15f;
            return !(blocked || Vector3.Distance(_chargeStart, transform.position) >= chargeMaxDistance || StateTime > 1.6f);
        }

        void FinishAttack() { _agent.speed = approachSpeed; Set(BossState.Recover); }

        void Face(Vector3 p, float degPerSec)
        {
            var d = p - transform.position; d.y = 0; if (d.sqrMagnitude < 0.001f) return;
            transform.rotation = Quaternion.RotateTowards(transform.rotation, Quaternion.LookRotation(d), degPerSec * Time.deltaTime);
        }

        void ShowRing()
        {
            var a = Def("BOSS-PULSO");
            if (_pulseRing == null) { _pulseRing = GameObject.CreatePrimitive(PrimitiveType.Cylinder); _pulseRing.name = "PulseRing"; Destroy(_pulseRing.GetComponent<Collider>()); _pulseRing.GetComponent<MeshRenderer>().sharedMaterial = World.SandboxFactory.Mat(new Color(0.9f, 0.3f, 0.2f)); _pulseRing.layer = GameLayers.VFX; }
            _pulseRing.transform.position = _pulseCenter + Vector3.up * 0.03f; _pulseRing.transform.localScale = new Vector3(a.radius * 2f, 0.02f, a.radius * 2f); _pulseRing.SetActive(true);
        }
        void HideRing() { if (_pulseRing != null) _pulseRing.SetActive(false); }

        void OnDamaged(DamageInfo info, float remaining)
        {
            int target = remaining <= definition.phase3Threshold ? 3 : remaining <= definition.phase2Threshold ? 2 : 1;
            if (target > Phase && target > _pendingPhase) _pendingPhase = target; // se resuelve tras el ataque ya emitido (61.2)
            if (State == BossState.Dormant && !ObjectiveService.Has(ObjectiveService.BossDefeated)) { /* no recibe daño desde fuera: Dormant solo dentro de arena */ }
        }

        void OnDied(DamageInfo info)
        {
            var prev = State; State = BossState.Dead; LastTransition = prev + "->Dead";
            HideRing(); Combat.Projectile.DespawnAllFrom(gameObject);
            if (_agent.enabled && _agent.isOnNavMesh) _agent.isStopped = true; _agent.enabled = false;
            foreach (var c in GetComponentsInChildren<Collider>()) c.gameObject.layer = GameLayers.Corpse;
            gameObject.layer = GameLayers.Corpse;
            _anim?.Play("Archivista_Death", false);
            if (GameFlowController.Instance != null) GameFlowController.Instance.enemiesKilled++;
            // 61.3: permiso de salida y CP-07 antes de cualquier menú; pantalla de control: custodio local fuera de servicio
            ObjectiveService.Grant(ObjectiveService.BossDefeated); ObjectiveService.Complete("O10");
            var hud = FindFirstObjectByType<UI.HudController>(); hud?.HideBoss(); hud?.ShowMessage("Pantalla de control: custodio local fuera de servicio.", 5f);
            var pc = FindFirstObjectByType<Player.PlayerController>();
            if (pc != null && CheckpointService.Instance != null) CheckpointService.Instance.RequestCheckpoint("CP-07", pc, "REG-S4");
            enabled = false;
        }

        // ---- persistencia (88.6) ----
        public string StableMode => State == BossState.Dead ? "Dead" : ObjectiveService.Has(ObjectiveService.BossDefeated) ? "Dead" : "Dormant";
        public void MarkDeadFromSnapshot()
        {
            EnsureRefs();
            if (State == BossState.Dead) return;
            State = BossState.Dead; LastTransition = "restore->Dead"; HideRing();
            if (_agent.enabled && _agent.isOnNavMesh) _agent.isStopped = true; _agent.enabled = false;
            foreach (var c in GetComponentsInChildren<Collider>()) c.gameObject.layer = GameLayers.Corpse; gameObject.layer = GameLayers.Corpse;
            _anim?.Play("Archivista_Death", false); enabled = false;
        }
        public void ReviveForRestore()
        {
            EnsureRefs();
            if (State != BossState.Dead) return;
            gameObject.layer = GameLayers.Enemy; foreach (var c in GetComponentsInChildren<Collider>()) c.gameObject.layer = GameLayers.Enemy;
            _agent.enabled = true; enabled = true; State = BossState.Dormant; LastTransition = "revive";
        }
        public void RestoreStable()
        {
            EnsureRefs();
            Phase = 1; _pendingPhase = 0; _inDouble = false; _doubleStep = 0; CurrentAttack = ""; HideRing();
            if (State == BossState.Dead) return;
            if (!_agent.enabled) _agent.enabled = true;
            // el registro manda: EVT-21 hecho en el snapshot = combate en curso → Engage; si no, reposo
            if (World.EventRunner.Instance != null && World.EventRunner.Instance.IsDone("EVT-21")) { _nextAttackAt = Time.time + 1f; Set(BossState.Engage); }
            else Set(BossState.Dormant);
            int target = _health.Current <= definition.phase3Threshold ? 3 : _health.Current <= definition.phase2Threshold ? 2 : 1; Phase = target;
        }
        public void WarpTo(Vector3 position, Vector3 euler)
        {
            EnsureRefs();
            if (_agent.enabled && _agent.isOnNavMesh) _agent.Warp(position); else transform.position = position;
            transform.eulerAngles = new Vector3(0f, euler.y, 0f);
        }
    }
}
