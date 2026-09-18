using System;
using UnityEngine;

namespace Esneider.Core.Persistence
{
    public enum EntityKind { Pickup, Enemy, Door, Movable, Breakable, Corpse, Mechanism, Boss }

    // 88.6: registro lógico por entidad. Estado tipado plano y serializable con JsonUtility (sin Dictionary).
    [Serializable]
    public class EntityState
    {
        public string guid;
        public string prefabId;
        public string regionId;
        public EntityKind kind;
        public int stateVersion;
        public long lastEventSequence;

        // Pickup
        public int amount = -1;        // -1: intacto (usar valor del prefab)
        public bool taken;
        // Enemy / Boss
        public float hp = -1f;
        public bool dead;
        public string mode = "";       // Patrol/Inactive/Dead estable
        public int waypoint;
        // Door
        public bool isOpen;
        public bool unlocked;
        // Movable / Corpse
        public bool hasTransform;
        public Vector3 position;
        public Vector3 eulerAngles;
        // Breakable
        public string variant = "";

        public EntityState Clone() => (EntityState)MemberwiseClone();
    }

    public enum WorldEventKind { PickupTaken, EnemyDamaged, EnemyDied, DoorChanged, PropMoved, PropBroken, RoomDiscovered, CheckpointCommitted, FlagSet, MechanismUsed }

    // Evento idempotente: (entidad, secuencia) única; aplicar dos veces no suma.
    [Serializable]
    public struct WorldEvent
    {
        public long sequence;
        public WorldEventKind kind;
        public string entityGuid;
        public string data;
        public float time;
    }
}
