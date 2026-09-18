using System;
using System.Collections.Generic;
using Esneider.Combat;
using Esneider.Player;
using Esneider.World;
using UnityEngine;

namespace Esneider.Core.Persistence
{
    // 19/89: captura coherente al final del frame, escritura transaccional, restauración con pipeline de carga.
    public class CheckpointService : MonoBehaviour
    {
        public static CheckpointService Instance { get; private set; }
        public string contentVersion = "0.1.0";
        public string campaignId = "campaign-1";
        [SerializeField] string _saveDirectoryOverride = "";
        SaveFileStore _store;
        // Pruebas: carpeta aislada. Cambiarla reinicia el almacén.
        public string saveDirectoryOverride { get => _saveDirectoryOverride; set { _saveDirectoryOverride = value; _store = null; } }
        public SaveFileStore Store => _store ??= new SaveFileStore(string.IsNullOrEmpty(_saveDirectoryOverride) ? System.IO.Path.Combine(Application.persistentDataPath, "saves", campaignId) : _saveDirectoryOverride);
        public SaveData LastConfirmed { get; private set; }
        public string LastNotice { get; private set; } = "";
        public event Action<SaveData> Committed;
        public event Action<SaveData> Restored;
        long _sequence;
        bool _busy;

        void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(this); return; }
            Instance = this;
        }

        void OnDestroy() { if (Instance == this) Instance = null; }

        // 89.2 paso 1: condiciones seguras. No mover el punto de reintento al solicitar.
        public bool CanCheckpoint(PlayerController pc, out string why)
        {
            why = "";
            var flow = GameFlowController.Instance;
            if (pc == null || pc.health == null || pc.health.IsDead) { why = "jugador muerto"; return false; }
            if (pc.IsCaptured) { why = "capturado"; return false; }
            if (flow != null && flow.State != GameState.Playing) { why = "estado " + flow.State; return false; }
            if (pc.actions != null && pc.actions.Busy) { why = "acción en curso"; return false; }
            if (_busy) { why = "escritura en curso"; return false; }
            return true;
        }

        public bool RequestCheckpoint(string checkpointId, PlayerController pc, string regionId, bool isShelter = false, int guaranteeHp = 0, int guaranteePistolTotal = 0, int guaranteeShotgunTotal = 0)
        {
            if (!CanCheckpoint(pc, out var why)) { LastNotice = "Checkpoint no guardado: " + why; return false; }
            StartCoroutine(CommitAtEndOfFrame(checkpointId, pc, regionId, isShelter, guaranteeHp, guaranteePistolTotal, guaranteeShotgunTotal));
            return true;
        }

        System.Collections.IEnumerator CommitAtEndOfFrame(string cp, PlayerController pc, string regionId, bool shelter, int gHp, int gPistol, int gShotgun)
        {
            _busy = true;
            yield return new WaitForEndOfFrame();
            bool ok = CommitNow(cp, pc, regionId, shelter, gHp, gPistol, gShotgun);
            _busy = false;
            if (ok) pc.inventory.Notify("Checkpoint guardado"); else pc.inventory.Notify("No se pudo guardar: " + Store.LastError);
        }

        // Síncrono (pruebas y refugio): consolidar → CP-06 → validar → escribir → confirmar.
        public bool CommitNow(string cp, PlayerController pc, string regionId, bool shelter, int gHp, int gPistol, int gShotgun)
        {
            foreach (var pe in FindObjectsByType<PersistentEntity>(FindObjectsInactive.Include, FindObjectsSortMode.None)) pe.CaptureStable();
            // 80.2/89.2 paso 3: garantía del refugio aplicada a la copia y al jugador, idempotente, sin sumar
            if (shelter)
            {
                var inv = pc.inventory;
                if (gHp > 0 && pc.health.Current < gHp) pc.health.Heal(gHp - pc.health.Current);
                if (inv.hasPistol && gPistol > 0 && inv.pistolMag + inv.pistolReserve < gPistol) inv.pistolReserve = Mathf.Min(inv.ReserveMax(AmmoType.Pistol), gPistol - inv.pistolMag);
                if (inv.hasShotgun && gShotgun > 0 && inv.shotgunMag + inv.shotgunReserve < gShotgun) inv.shotgunReserve = Mathf.Min(inv.ReserveMax(AmmoType.Shotgun), gShotgun - inv.shotgunMag);
                WorldStateRegistry.Session.SetFlag(ObjectiveService.FinalCabinet);
            }
            var data = Capture(cp, pc, regionId);
            if (!Store.Commit(data)) { LastNotice = Store.LastError; return false; }
            LastConfirmed = data; LastNotice = "Checkpoint guardado " + cp;
            WorldStateRegistry.Session.Apply(WorldEventKind.CheckpointCommitted, "", null, cp);
            Committed?.Invoke(data);
            return true;
        }

        public SaveData Capture(string cp, PlayerController pc, string regionId)
        {
            var inv = pc.inventory; var flow = GameFlowController.Instance; var reg = WorldStateRegistry.Session;
            return new SaveData
            {
                contentVersion = contentVersion, buildId = Application.version, campaignId = campaignId, saveSequence = ++_sequence, checkpointId = cp, regionId = regionId,
                playerPosition = pc.transform.position, playerYaw = pc.transform.eulerAngles.y, health = pc.health.Current, stamina = pc.motor.stamina,
                hasFlashlight = inv.hasFlashlight, hasCrowbar = inv.hasCrowbar, hasPistol = inv.hasPistol, hasShotgun = inv.hasShotgun,
                activeWeapon = pc.actions.ActiveWeapon.HasValue ? pc.actions.ActiveWeapon.Value.ToString() : "",
                pistolMag = inv.pistolMag, pistolReserve = inv.pistolReserve, shotgunMag = inv.shotgunMag, shotgunReserve = inv.shotgunReserve,
                syringeCount = inv.syringes, rationCount = inv.rations, flashlightOn = pc.flashlight != null && pc.flashlight.enabled,
                world = reg.Snapshot(), finalCabinetCommitted = reg.HasFlag(ObjectiveService.FinalCabinet),
                bossDefeated = reg.HasFlag(ObjectiveService.BossDefeated), campaignWon = flow != null && flow.State == GameState.Won,
                elapsedPlaySeconds = flow != null ? flow.attemptTime : 0, shotsFired = flow != null ? flow.shotsFired : 0, kills = flow != null ? flow.enemiesKilled : 0, collisionImpacts = flow != null ? flow.physicsImpacts : 0
            };
        }

        // 19/89.4: pausar → liberar proyectiles → restaurar registro y mundo → jugador → inventario → habilitar.
        public bool RestoreInto(SaveData data, PlayerController pc)
        {
            if (data == null || pc == null) return false;
            var flow = GameFlowController.Instance;
            flow?.SetState(GameState.Loading);
            foreach (var p in FindObjectsByType<Projectile>(FindObjectsSortMode.None)) p.Despawn();
            WorldStateRegistry.Session.Restore(data.world);
            foreach (var pe in FindObjectsByType<PersistentEntity>(FindObjectsInactive.Include, FindObjectsSortMode.None))
                if (WorldStateRegistry.Session.TryGet(pe.guid, out var s)) { pe.gameObject.SetActive(true); pe.Hydrate(s); }
            pc.ResetForRestore();
            pc.motor.Teleport(data.playerPosition, data.playerYaw);
            pc.health.ResetTo(data.health); pc.motor.stamina = data.stamina;
            var inv = pc.inventory;
            inv.hasFlashlight = data.hasFlashlight; inv.hasCrowbar = data.hasCrowbar; inv.hasPistol = data.hasPistol; inv.hasShotgun = data.hasShotgun;
            inv.pistolMag = data.pistolMag; inv.pistolReserve = data.pistolReserve; inv.shotgunMag = data.shotgunMag; inv.shotgunReserve = data.shotgunReserve;
            inv.syringes = data.syringeCount; inv.rations = data.rationCount;
            if (pc.flashlight != null) pc.flashlight.enabled = data.flashlightOn;
            pc.actions.RestoreActiveWeapon(data.activeWeapon);
            if (flow != null) { flow.attemptTime = data.elapsedPlaySeconds; flow.shotsFired = data.shotsFired; flow.enemiesKilled = data.kills; flow.physicsImpacts = data.collisionImpacts; flow.ResumeAttempt(); }
            LastConfirmed = data;
            Restored?.Invoke(data);
            return true;
        }

        public SaveData LoadFromDisk(out string source) { var d = Store.LoadBest(out source); if (!string.IsNullOrEmpty(Store.LastRecoveryNotice)) LastNotice = Store.LastRecoveryNotice; return d; }
    }
}
