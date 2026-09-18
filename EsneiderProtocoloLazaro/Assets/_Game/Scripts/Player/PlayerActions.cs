using System.Collections.Generic;
using Esneider.Core;
using Esneider.Core.Data;
using UnityEngine;

namespace Esneider.Player
{
    public enum ActionKind { None, Equip, Attack, ReloadPistol, ReloadShotgun, Heal }

    // Sección 86: PlayerActionController + WeaponController. Decide acciones con transacciones ActionID; el Animator solo representa.
    public class PlayerActions : MonoBehaviour
    {
        public Inventory inventory;
        public PlayerLook look;
        public Health health;
        public PlayerMotor motor;
        public Transform muzzle;

        public WeaponKind? ActiveWeapon { get; private set; }
        public ActionKind CurrentKind { get; private set; } = ActionKind.None;
        public ActionTransaction Current { get; private set; }
        public bool actionsEnabled = true;
        public int shotSeed;
        public string LastEvent { get; private set; } = "";

        float _nextAttackTime;
        WeaponKind? _pendingEquip;
        bool _shotgunStopAfterCycle;
        int _shotgunCyclesPlanned;
        float _shotgunCycleStart, _shotgunExitStart;
        int _shotgunCycleIndex;
        bool _shotgunCycleCommitted;
        readonly Dictionary<Health, float> _pelletDamage = new Dictionary<Health, float>();

        WeaponDefinition Def(WeaponKind k) => k == WeaponKind.Melee ? inventory.crowbar : k == WeaponKind.Pistol ? inventory.pistol : inventory.shotgun;
        public WeaponDefinition ActiveDef => ActiveWeapon.HasValue ? Def(ActiveWeapon.Value) : null;
        public bool Busy => Current != null && Current.IsRunning;

        void Update()
        {
            if (Current != null && Current.IsRunning)
            {
                if (CurrentKind == ActionKind.ReloadShotgun) TickShotgunReload(Time.deltaTime);
                else if (Current.Tick(Time.deltaTime)) Finish();
            }
        }

        void Finish()
        {
            if (CurrentKind == ActionKind.Equip && Current.Phase == ActionPhase.Completed && _pendingEquip.HasValue) { ActiveWeapon = _pendingEquip; LastEvent = "equip:" + ActiveWeapon; }
            _pendingEquip = null;
            Current = null; CurrentKind = ActionKind.None; motor.SpeedFactor = 1f;
        }

        // ---------- equipar (86.2/86.6) ----------
        public bool RequestEquip(WeaponKind kind)
        {
            if (!actionsEnabled || !inventory.HasWeapon(kind)) return false;
            if (ActiveWeapon == kind && !(Busy && CurrentKind == ActionKind.Equip)) return false; // arma ya activa: no reanimar
            if (Busy)
            {
                if (CurrentKind == ActionKind.Attack) return false;
                CancelCurrent("equip"); if (Busy) return false;
            }
            float dur = kind == WeaponKind.Melee ? 0.55f : kind == WeaponKind.Pistol ? 0.65f : 0.85f;
            _pendingEquip = kind;
            Begin(ActionKind.Equip, new ActionTransaction("Equip", dur));
            return true;
        }

        // ---------- atacar (11/60/86) ----------
        public bool RequestAttack()
        {
            if (!actionsEnabled || !ActiveWeapon.HasValue || Time.time < _nextAttackTime) return false;
            if (Busy)
            {
                if (CurrentKind == ActionKind.ReloadShotgun) { _shotgunStopAfterCycle = true; return false; }
                if (CurrentKind == ActionKind.Heal || CurrentKind == ActionKind.Equip) return false;
                if (CurrentKind == ActionKind.ReloadPistol) { if (!Current.AnyCommitDone) CancelCurrent("attack"); else return false; }
                if (Busy) return false;
            }
            var def = ActiveDef;
            switch (ActiveWeapon.Value)
            {
                case WeaponKind.Melee:
                    {
                        int attackId = AttackIds.Next();
                        var t = new ActionTransaction("Attack", def.attackCycle).AddCommit(def.activeStart, () => MeleeHit(def, attackId));
                        Begin(ActionKind.Attack, t);
                        _nextAttackTime = Time.time + def.attackCycle;
                        return true;
                    }
                case WeaponKind.Pistol:
                    if (!inventory.ConsumeRound(AmmoType.Pistol)) { LastEvent = "click"; _nextAttackTime = Time.time + 0.25f; return false; }
                    FireHitscan(def, 1, 0f, def.range, def.range);
                    _nextAttackTime = Time.time + def.attackCycle;
                    look?.AddRecoil(1.2f);
                    return true;
                case WeaponKind.Shotgun:
                    if (!inventory.ConsumeRound(AmmoType.Shotgun)) { LastEvent = "click"; _nextAttackTime = Time.time + 0.4f; return false; }
                    FireHitscan(def, def.pellets, 4f, 6f, def.range);
                    _nextAttackTime = Time.time + def.attackCycle; // incluye bombeo 0.65 s
                    look?.AddRecoil(3f);
                    return true;
            }
            return false;
        }

        void MeleeHit(WeaponDefinition def, int attackId)
        {
            NoiseSystem.Emit(transform.position, def.noiseRadius, gameObject, "crowbar");
            var aim = look.AimRay;
            var ray = new Ray(aim.origin - Vector3.up * 0.35f, aim.direction); // arco a la altura del pecho
            var hits = Physics.SphereCastAll(ray, 0.45f, def.range, GameLayers.PlayerAttackMask, QueryTriggerInteraction.Ignore);
            var damaged = new HashSet<Health>();
            foreach (var h in hits)
            {
                var hp = h.collider.GetComponentInParent<Health>();
                if (hp == null || hp.gameObject == gameObject || damaged.Contains(hp)) continue;
                // no golpear a través de pared
                var toHit = h.point - ray.origin; float d = toHit.magnitude;
                if (d > 0.05f && Physics.Raycast(ray.origin, toHit / d, d - 0.05f, GameLayers.CoverMask, QueryTriggerInteraction.Ignore)) continue;
                if (hp.ApplyDamage(new DamageInfo { amount = def.damage, attackId = attackId, source = gameObject, point = h.point, direction = ray.direction, kind = "Crowbar" }))
                    damaged.Add(hp);
            }
            LastEvent = "melee:" + damaged.Count;
        }

        // Hitscan desde cámara para intención; comprobación desde la boca del arma contra cobertura cercana (11).
        void FireHitscan(WeaponDefinition def, int rays, float spreadDeg, float fullDamageRange, float maxRange)
        {
            if (GameFlowController.Instance != null) GameFlowController.Instance.shotsFired++;
            NoiseSystem.Emit(transform.position, def.noiseRadius, gameObject, def.kind.ToString());
            int attackId = AttackIds.Next();
            var rng = new System.Random(++shotSeed);
            var ray = look.AimRay;
            var muzzlePos = muzzle != null ? muzzle.position : ray.origin + ray.direction * 0.4f;
            _pelletDamage.Clear();
            int hitsCount = 0;
            for (int i = 0; i < rays; i++)
            {
                var dir = ray.direction;
                if (spreadDeg > 0f)
                {
                    float a = (float)rng.NextDouble() * 360f, r = (float)rng.NextDouble() * spreadDeg;
                    dir = Quaternion.AngleAxis(a, ray.direction) * Quaternion.AngleAxis(r, Vector3.Cross(ray.direction, Vector3.up).normalized) * ray.direction;
                }
                if (!Physics.Raycast(ray.origin, dir, out var hit, maxRange, GameLayers.PlayerAttackMask, QueryTriggerInteraction.Ignore)) continue;
                // desde la boca: si hay cobertura entre boca y punto de impacto, el disparo pega en la cobertura
                var seg = hit.point - muzzlePos; float segLen = seg.magnitude;
                if (segLen > 0.05f && Physics.Raycast(muzzlePos, seg / segLen, out var block, segLen - 0.02f, GameLayers.CoverMask, QueryTriggerInteraction.Ignore))
                { hitsCount++; continue; }
                hitsCount++;
                var hp = hit.collider.GetComponentInParent<Health>();
                if (hp == null || hp.gameObject == gameObject) continue;
                float falloff = hit.distance <= fullDamageRange ? 1f : Mathf.Clamp01(1f - (hit.distance - fullDamageRange) / Mathf.Max(0.01f, maxRange - fullDamageRange));
                float dmg = def.damage * falloff;
                _pelletDamage[hp] = (_pelletDamage.TryGetValue(hp, out var acc) ? acc : 0f) + dmg;
            }
            foreach (var kv in _pelletDamage)
                kv.Key.ApplyDamage(new DamageInfo { amount = kv.Value, attackId = attackId, source = gameObject, point = kv.Key.transform.position, direction = ray.direction, kind = def.kind.ToString() });
            LastEvent = def.kind + ":hits=" + hitsCount + ":targets=" + _pelletDamage.Count;
        }

        // ---------- recargar (86.3/86.4) ----------
        public bool RequestReload()
        {
            if (!actionsEnabled || !ActiveWeapon.HasValue || Busy) return false;
            var def = ActiveDef;
            if (ActiveWeapon == WeaponKind.Pistol)
            {
                if (inventory.pistolMag >= inventory.MagCapacity(AmmoType.Pistol) || inventory.pistolReserve <= 0) return false;
                var t = new ActionTransaction("ReloadPistol", def.reloadDuration).AddCommit(def.reloadCommit, () => { int n = inventory.CommitPistolReload(); LastEvent = "reload:" + n; });
                Begin(ActionKind.ReloadPistol, t); motor.SpeedFactor = 0.8f; return true;
            }
            if (ActiveWeapon == WeaponKind.Shotgun)
            {
                int n = Mathf.Min(inventory.MagCapacity(AmmoType.Shotgun) - inventory.shotgunMag, inventory.shotgunReserve);
                if (n <= 0) return false;
                _shotgunCyclesPlanned = n; _shotgunCycleIndex = 0; _shotgunStopAfterCycle = false; _shotgunCycleCommitted = false;
                _shotgunCycleStart = def.shellEnter; _shotgunExitStart = -1f;
                float total = def.shellEnter + def.shellInsert * n + def.shellExit;
                Begin(ActionKind.ReloadShotgun, new ActionTransaction("ReloadShotgun", total)); motor.SpeedFactor = 0.8f; return true;
            }
            return false;
        }

        void TickShotgunReload(float dt)
        {
            var def = inventory.shotgun; var t = Current;
            // avanzar reloj manualmente (la transacción no tiene commits fijos porque la salida puede adelantarse)
            t.Advance(dt);
            float e = t.Elapsed;
            if (_shotgunExitStart >= 0f)
            {
                if (e >= _shotgunExitStart + def.shellExit) { t.Complete(); Finish(); }
                return;
            }
            if (e < _shotgunCycleStart) return; // entrada
            float inCycle = e - _shotgunCycleStart;
            if (!_shotgunCycleCommitted && inCycle >= def.shellInsertCommit)
            {
                _shotgunCycleCommitted = true;
                if (inventory.CommitShotgunShell()) LastEvent = "shell:" + inventory.shotgunMag;
            }
            if (inCycle >= def.shellInsert)
            {
                _shotgunCycleIndex++;
                bool more = _shotgunCycleIndex < _shotgunCyclesPlanned && !_shotgunStopAfterCycle && inventory.shotgunReserve > 0 && inventory.shotgunMag < inventory.MagCapacity(AmmoType.Shotgun);
                if (more) { _shotgunCycleStart = e; _shotgunCycleCommitted = false; }
                else _shotgunExitStart = e;
            }
        }

        // ---------- curar (10/86.2) ----------
        public bool RequestHeal()
        {
            if (!actionsEnabled || Busy || health == null || health.Current >= health.maxHp) return false;
            var p = inventory.player;
            if (inventory.syringes > 0)
            {
                float dur = p != null ? p.syringeDuration : 1.6f, commit = p != null ? p.syringeCommit : 1.1f; int heal = p != null ? p.syringeHeal : 45;
                Begin(ActionKind.Heal, new ActionTransaction("Syringe", dur).AddCommit(commit, () => { if (inventory.ConsumeSyringe()) { health.Heal(heal); LastEvent = "heal:syringe"; } }));
                motor.SpeedFactor = 0.6f; return true;
            }
            if (inventory.rations > 0)
            {
                float dur = p != null ? p.rationDuration : 2.0f, commit = p != null ? p.rationCommit : 1.4f; int heal = p != null ? p.rationHeal : 20;
                Begin(ActionKind.Heal, new ActionTransaction("Ration", dur).AddCommit(commit, () => { if (inventory.ConsumeRation()) { health.Heal(heal); LastEvent = "heal:ration"; } }));
                motor.SpeedFactor = 0.6f; return true;
            }
            return false;
        }

        // ---------- cancelación común (86.6) ----------
        public void CancelCurrent(string reason)
        {
            if (Current == null || !Current.IsRunning) return;
            if (CurrentKind == ActionKind.Attack) return; // el golpe no se cancela salvo captura/muerte (11)
            if (CurrentKind == ActionKind.ReloadShotgun)
            {
                // dentro de un ciclo ya comprometido: esperar fin de inserción y salida
                if (_shotgunCycleCommitted && _shotgunExitStart < 0f) { _shotgunStopAfterCycle = true; return; }
            }
            Current.Cancel(reason); LastEvent = "cancel:" + CurrentKind + ":" + reason;
            Finish();
        }

        public void ForceCancelAll(string reason)
        {
            if (Current != null && Current.IsRunning) { Current.Cancel(reason); LastEvent = "cancel:" + CurrentKind + ":" + reason; }
            _pendingEquip = null; Current = null; CurrentKind = ActionKind.None; motor.SpeedFactor = 1f;
        }

        void Begin(ActionKind kind, ActionTransaction t) { Current = t; CurrentKind = kind; t.Begin(); }

        // Carga de snapshot (19): arma activa sin animar ni reiniciar cooldown.
        public void RestoreActiveWeapon(string kindName)
        {
            ForceCancelAll("restore");
            if (string.IsNullOrEmpty(kindName) || !System.Enum.TryParse<WeaponKind>(kindName, out var k) || !inventory.HasWeapon(k)) { ActiveWeapon = null; return; }
            ActiveWeapon = k; _nextAttackTime = 0f;
        }
    }
}
