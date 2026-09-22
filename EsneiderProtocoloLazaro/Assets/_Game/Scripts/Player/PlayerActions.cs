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
        public Transform PresentationMuzzle { get; set; }
        public event System.Action<WeaponKind, Vector3[]> Fired;

        public WeaponKind? ActiveWeapon { get; private set; }
        public ActionKind CurrentKind { get; private set; } = ActionKind.None;
        public ActionTransaction Current { get; private set; }
        public bool actionsEnabled = true;
        public int shotSeed;
        public string LastEvent { get; private set; } = "";
        public float LastHitTime { get; private set; } = -100f;

        float _nextAttackTime;
        WeaponKind? _pendingEquip;
        readonly Dictionary<Health, float> _pelletDamage = new Dictionary<Health, float>();

        WeaponDefinition Def(WeaponKind k) => k == WeaponKind.Melee ? inventory.crowbar : k == WeaponKind.Pistol ? inventory.pistol : inventory.shotgun;
        public WeaponDefinition ActiveDef => ActiveWeapon.HasValue ? Def(ActiveWeapon.Value) : null;
        public bool Busy => Current != null && Current.IsRunning;

        void Update()
        {
            if (Current != null && Current.IsRunning)
            {
                if (Current.Tick(Time.deltaTime)) Finish();
            }
        }

        void Finish()
        {
            if (CurrentKind == ActionKind.Equip && Current.Phase == ActionPhase.Completed && _pendingEquip.HasValue) { ActiveWeapon = _pendingEquip; inventory.EnsureHotbar(); inventory.Select(inventory.hotbarOrder.IndexOf(Inventory.ItemFor(ActiveWeapon.Value))); LastEvent = "equip:" + ActiveWeapon; }
            _pendingEquip = null;
            Current = null; CurrentKind = ActionKind.None; motor.SpeedFactor = 1f;
        }

        // ---------- equipar (86.2/86.6) ----------
        public bool RequestSelectSlot(int slot)
        {
            if (!actionsEnabled || slot < 0 || slot >= Inventory.SlotCount) return false;
            inventory.EnsureHotbar();
            var kind = Inventory.WeaponFor(inventory.ItemAt(slot));
            if (kind.HasValue && inventory.HasWeapon(kind.Value))
            {
                if (ActiveWeapon == kind && !Busy) { inventory.Select(slot); return true; }
                return RequestEquip(kind.Value);
            }
            if (Busy) { CancelCurrent("select"); if (Busy) return false; }
            ActiveWeapon = null; inventory.Select(slot); return true;
        }
        public bool RequestUseSelected()
        {
            var item = inventory.SelectedItem;
            if (!item.HasValue || !inventory.HasItem(item.Value)) return false;
            if (Inventory.WeaponFor(item).HasValue) return RequestAttack();
            if (item == World.PickupKind.Syringe || item == World.PickupKind.Ration) return RequestHeal(item);
            if (item == World.PickupKind.PistolAmmo || item == World.PickupKind.ShotgunAmmo) inventory.Notify("Selecciona el arma para usar su munición");
            return false;
        }
        public bool RequestEquip(WeaponKind kind)
        {
            if (!actionsEnabled || !inventory.HasWeapon(kind)) return false;
            if (ActiveWeapon == kind && !(Busy && CurrentKind == ActionKind.Equip)) return false; // arma ya activa: no reanimar
            if (Busy)
            {
                if (CurrentKind == ActionKind.Attack && ActiveWeapon == WeaponKind.Melee) return false;
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
                    Begin(ActionKind.Attack, new ActionTransaction("PistolFire", def.attackCycle));
                    _nextAttackTime = Time.time + def.attackCycle;
                    look?.AddRecoil(1.2f);
                    return true;
                case WeaponKind.Shotgun:
                    if (!inventory.ConsumeRound(AmmoType.Shotgun)) { LastEvent = "click"; _nextAttackTime = Time.time + 0.4f; return false; }
                    FireHitscan(def, def.pellets, 4f, 6f, def.range);
                    Begin(ActionKind.Attack, new ActionTransaction("ShotgunFire", def.attackCycle));
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
            // Follow the crosshair: lowering an already downward-facing ray misses short enemies.
            var ray = aim;
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
                { damaged.Add(hp); LastHitTime = Time.time; }
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
            var mouth = PresentationMuzzle != null ? PresentationMuzzle : muzzle;
            var muzzlePos = mouth != null ? mouth.position : ray.origin + ray.direction * 0.4f;
            var endpoints = new Vector3[rays];
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
                bool hitTarget = Physics.Raycast(ray.origin, dir, out var hit, maxRange, GameLayers.PlayerAttackMask, QueryTriggerInteraction.Ignore);
                endpoints[i] = hitTarget ? hit.point : ray.origin + dir * maxRange;
                // desde la boca: si hay cobertura entre boca y punto de impacto, el disparo pega en la cobertura
                var seg = endpoints[i] - muzzlePos; float segLen = seg.magnitude;
                if (segLen > 0.05f && Physics.Raycast(muzzlePos, seg / segLen, out var block, segLen - 0.02f, GameLayers.CoverMask, QueryTriggerInteraction.Ignore))
                { endpoints[i] = block.point; hitsCount++; continue; }
                if (!hitTarget) continue;
                hitsCount++;
                var hp = hit.collider.GetComponentInParent<Health>();
                if (hp == null || hp.gameObject == gameObject) continue;
                float falloff = hit.distance <= fullDamageRange ? 1f : Mathf.Clamp01(1f - (hit.distance - fullDamageRange) / Mathf.Max(0.01f, maxRange - fullDamageRange));
                float dmg = def.damage * falloff;
                _pelletDamage[hp] = (_pelletDamage.TryGetValue(hp, out var acc) ? acc : 0f) + dmg;
            }
            foreach (var kv in _pelletDamage)
                if (kv.Key.ApplyDamage(new DamageInfo { amount = kv.Value, attackId = attackId, source = gameObject, point = kv.Key.transform.position, direction = ray.direction, kind = def.kind.ToString() })) LastHitTime = Time.time;
            LastEvent = def.kind + ":hits=" + hitsCount + ":targets=" + _pelletDamage.Count;
            Fired?.Invoke(def.kind, endpoints);
        }

        // Compatibility entry point for the old R binding: ammunition is now one spendable total.
        public bool RequestReload() => false;

        // ---------- curar (10/86.2) ----------
        public bool RequestHeal(World.PickupKind? preferred = null)
        {
            if (!actionsEnabled || Busy || health == null || health.Current >= health.maxHp) return false;
            var p = inventory.player;
            if (inventory.syringes > 0 && (!preferred.HasValue || preferred == World.PickupKind.Syringe))
            {
                float dur = p != null ? p.syringeDuration : 1.6f, commit = p != null ? p.syringeCommit : 1.1f; int heal = p != null ? p.syringeHeal : 45;
                Begin(ActionKind.Heal, new ActionTransaction("Syringe", dur).AddCommit(commit, () => { if (inventory.ConsumeSyringe()) { health.Heal(heal); LastEvent = "heal:syringe"; } }));
                motor.SpeedFactor = 0.6f; return true;
            }
            if (inventory.rations > 0 && (!preferred.HasValue || preferred == World.PickupKind.Ration))
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
            if (CurrentKind == ActionKind.Attack && ActiveWeapon == WeaponKind.Melee) return; // no cancelar el golpe antes de su impacto
            // Firearm damage is already committed. Changing weapon may end recoil, but keeps _nextAttackTime.
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
