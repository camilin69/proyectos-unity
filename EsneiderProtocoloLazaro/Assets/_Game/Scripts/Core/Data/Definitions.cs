using System;
using System.Collections.Generic;
using UnityEngine;

namespace Esneider.Core.Data
{
    // Sección 95.1: definiciones tipadas, inmutables en runtime. El estado mutable vive aparte.

    public abstract class GameDefinition : ScriptableObject
    {
        [Tooltip("ID estable de catálogo (GDD). Nunca cambia tras publicarse.")] public string id;
        [Tooltip("Sección del GDD que fija estos valores")] public string gddSource;
    }

    [CreateAssetMenu(menuName = "Esneider/Data/Player", fileName = "PlayerDefinition")]
    public class PlayerDefinition : GameDefinition
    {
        [Header("Salud (10/103)")] public int maxHp = 90;
        public float invulnerabilitySeconds = 0.65f;
        [Header("Cápsula y movimiento (9)")] public float capsuleHeight = 1.8f;
        public float capsuleRadius = 0.35f;
        public float crouchHeight = 1.2f;
        public float walkSpeed = 3.2f;
        public float runSpeed = 5.2f;
        public float crouchSpeed = 1.6f;
        [Header("Curación (10/86)")] public int syringeHeal = 45;
        public float syringeDuration = 1.6f, syringeCommit = 1.1f;
        public int rationHeal = 20;
        public float rationDuration = 2.0f, rationCommit = 1.4f;
        public int maxSyringes = 3, maxRations = 2;
        [Header("Cámara (9/81)")] public float fovVertical = 75f;
        public float fovMin = 70f, fovMax = 100f;
        [Header("Ruido base (14/78)")] public float noiseCrouch = 1.5f, noiseWalk = 4f, noiseRun = 10f;
    }

    public enum WeaponKind { Melee, Pistol, Shotgun }

    [CreateAssetMenu(menuName = "Esneider/Data/Weapon", fileName = "WeaponDefinition")]
    public class WeaponDefinition : GameDefinition
    {
        public WeaponKind kind;
        [Header("Daño (11/103)")] public float damage = 20f;
        [Tooltip("Pellets por disparo; 1 salvo escopeta")] public int pellets = 1;
        public float range = 2.0f;
        [Header("Capacidad")] public int magazineSize = 0;
        public int reserveMax = 0;
        public int pickupLoaded = 0, pickupReserve = 0;
        [Header("Tiempos y commit (60/86)")] public float attackCycle = 0.85f;
        public float activeStart = 0.20f, activeEnd = 0.35f;
        public float reloadDuration = 0f, reloadCommit = 0f;
        [Tooltip("Escopeta: entrada, inserción por cartucho, commit de inserción, salida, bombeo")]
        public float shellEnter = 0f, shellInsert = 0f, shellInsertCommit = 0f, shellExit = 0f, pumpDuration = 0f;
        [Header("Ruido lógico (14/78)")] public float noiseRadius = 12f;
        [Header("Presentación")] public string viewmodelSocket = "hand_R";
        public List<string> clipIds = new List<string>();
    }

    public enum EnemyKind { Vigia, Custodio }

    [CreateAssetMenu(menuName = "Esneider/Data/Enemy", fileName = "EnemyDefinition")]
    public class EnemyDefinition : GameDefinition
    {
        public EnemyKind kind;
        [Header("Vida y velocidad (12/13/77)")] public int maxHp = 60;
        public float patrolSpeed = 0.7f, chaseSpeed = 2.6f;
        [Header("Percepción (14/78): normal / alerta")] public float visionRangeLit = 12f, visionAngleLit = 90f;
        public float visionRangeAlert = 16f, visionAngleAlert = 100f;
        public float visionRangeDark = 6f, visionRangeDarkAlert = 8f;
        public float closeRange = 3f, closeReaction = 0.35f;
        public float searchSeconds = 12f, combatSearchSeconds = 18f;
        [Header("Ataque (12/13/78)")] public float attackRangeMin = 3f, attackRangeMax = 9f;
        public float telegraph = 1.1f, telegraphTutorial = 1.2f;
        public float recovery = 1.4f, cooldown = 3.5f;
        public int attackDamage = 0;
        [Tooltip("Red: duración máxima de captura hasta derrota")] public float captureSeconds = 2.5f;
        public float staggerSeconds = 0.3f;
    }

    [Serializable]
    public class BossAttackDefinition
    {
        public string id;
        public int damage;
        public float telegraph, recovery;
        public float radius;
        public int phaseFrom = 1;
    }

    [CreateAssetMenu(menuName = "Esneider/Data/Boss", fileName = "BossDefinition")]
    public class BossDefinition : GameDefinition
    {
        [Header("15/61/79/103")] public int maxHp = 1200;
        public int phase2Threshold = 800, phase3Threshold = 400;
        public float phaseTransitionSeconds = 2f;
        public float doubleSequenceGap = 0.8f, doubleSequenceRecovery = 2.5f;
        public List<BossAttackDefinition> attacks = new List<BossAttackDefinition>();
    }

    [CreateAssetMenu(menuName = "Esneider/Data/Surface", fileName = "SurfaceDefinition")]
    public class SurfaceDefinition : GameDefinition
    {
        [Header("96.1")] public float staticFriction = 0.65f, dynamicFriction = 0.55f;
        public float footstepNoiseMultiplier = 1f;
        public string footstepBank, impactBank;
        public string visualReaction;
    }

    public enum RegionKind { Sector, Connector }

    [CreateAssetMenu(menuName = "Esneider/Data/RoomRegion", fileName = "RoomRegionDefinition")]
    public class RoomRegionDefinition : GameDefinition
    {
        public RegionKind kind;
        public string regionId;
        [Tooltip("Serialized stable GUID (LevelPlan.StableGuid)")] public string guid;
        public string floorId, sectorId;
        public Vector3 worldOrigin;
        public Rect localRect;
        public float height;
        public List<string> doorIds = new List<string>();
        public List<string> ownedEntityIds = new List<string>();
    }

    public enum EventPolicy { Once, Repeatable, Ambient, Interaction }

    [CreateAssetMenu(menuName = "Esneider/Data/Event", fileName = "EventDefinition")]
    public class EventDefinition : GameDefinition
    {
        [Header("93.1")] public string roomId;
        public string guid;
        public EventPolicy policy;
        [TextArea] public string trigger, action, restore;
        public int priority = 0;
        public float cooldownSeconds = 0f;
        public string commitFlag, fallback;
    }

    [CreateAssetMenu(menuName = "Esneider/Data/Checkpoint", fileName = "CheckpointDefinition")]
    public class CheckpointDefinition : GameDefinition
    {
        [Header("19/68.9/80")] public string spaceId;
        public string guid;
        public Vector3 worldPosition;
        public float yaw;
        [TextArea] public string activation, protection;
        public bool isShelter;
        [Tooltip("Garantía CP-06: mínimos aplicados una vez, no suma")] public int guaranteeHp = 0, guaranteePistolTotal = 0, guaranteeShotgunTotal = 0;
    }

    [CreateAssetMenu(menuName = "Esneider/Data/Difficulty", fileName = "DifficultyDefinition")]
    public class DifficultyDefinition : GameDefinition
    {
        public string presetName = "Normal";
        [Header("Modificadores explícitos (80.3/95.2). Normal = 1")] public float enemyDamageMultiplier = 1f;
        public float playerDamageMultiplier = 1f;
        public float telegraphMultiplier = 1f;
        public float perceptionRangeMultiplier = 1f;
        public float ammoDropMultiplier = 1f;
    }

    // Catálogo único para consumidores y validador.
    [CreateAssetMenu(menuName = "Esneider/Data/Catalog", fileName = "GameDataCatalog")]
    public class GameDataCatalog : ScriptableObject
    {
        public string contentVersion = "0.1.0";
        public PlayerDefinition player;
        public List<WeaponDefinition> weapons = new List<WeaponDefinition>();
        public List<EnemyDefinition> enemies = new List<EnemyDefinition>();
        public BossDefinition boss;
        public List<SurfaceDefinition> surfaces = new List<SurfaceDefinition>();
        public List<RoomRegionDefinition> regions = new List<RoomRegionDefinition>();
        public List<EventDefinition> events = new List<EventDefinition>();
        public List<CheckpointDefinition> checkpoints = new List<CheckpointDefinition>();
        public List<DifficultyDefinition> difficulties = new List<DifficultyDefinition>();
        public TextAsset levelPlanJson;
    }
}
