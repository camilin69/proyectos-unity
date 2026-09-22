using System;
using System.Collections.Generic;
using UnityEngine;

namespace Esneider.Core.Persistence
{
    // Sección 19/89.1: payload del checkpoint. Solo IDs estables; nada de referencias Unity, proyectiles ni velocidades.
    [Serializable]
    public class SaveData
    {
        public const int CurrentSchemaVersion = 1;

        public int schemaVersion = CurrentSchemaVersion;
        public string contentVersion = "";
        public string buildId = "";
        public string campaignId = "";
        public long saveSequence;
        public string checkpointId = "";
        public string regionId = "";
        public Vector3 playerPosition;
        public float playerYaw;
        public float health;
        public float stamina;
        public bool hasFlashlight, hasCrowbar, hasPistol, hasShotgun;
        public string activeWeapon = "";
        public string[] hotbarOrder;
        public int selectedSlot;
        public int pistolMag, pistolReserve, shotgunMag, shotgunReserve;
        public int syringeCount, rationCount;
        public bool flashlightOn;
        public RegistrySnapshot world = new RegistrySnapshot();
        public bool finalCabinetCommitted;
        public bool campaignWon, endingViewed, bossDefeated;
        public float elapsedPlaySeconds;
        public int shotsFired, kills, collisionImpacts;
    }

    // 89.1: envelope con checksum SHA-256 del payload exacto.
    [Serializable]
    public class SaveEnvelope
    {
        public int schemaVersion;
        public string contentVersion;
        public string buildId;
        public string campaignId;
        public long saveSequence;
        public string checkpointId;
        public string createdUtc;
        public int payloadLength;
        public string payloadChecksum;
        public string payload;
    }
}
