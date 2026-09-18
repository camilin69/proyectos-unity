using System;
using System.Collections.Generic;
using System.Security.Cryptography;
using System.Text;
using UnityEngine;

namespace Esneider.Core.Data
{
    [Serializable] public class PlanVec3 { public float x, y, z; public Vector3 ToVector3() => new Vector3(x, y, z); }
    [Serializable] public class PlanPoint { public float x, z; }
    [Serializable] public class PlanRect { public float x, z, w, d; public bool Contains(float px, float pz) => px >= x && px <= x + w && pz >= z && pz <= z + d; }

    [Serializable] public class PlanFloor { public string id, sector, name, region; public PlanVec3 origin; public float w, d, height; }
    [Serializable] public class PlanRoom : PlanRect { public string id, floor, name, scn; }
    [Serializable] public class PlanCirculation : PlanRect { public string id, floor, name; }
    [Serializable] public class PlanStairs : PlanRect { public string id, lowerFloor, upperFloor, axis; public float landingX, landingZ, rise; public int flights, startDir; }
    [Serializable] public class PlanDoor { public string id, floor, room, edge, state, owner; public float x, z, width, height; }
    [Serializable] public class PlanConnector { public string id, region, fromDoor, toDoor; public PlanVec3 origin; public float width, height, length; public List<PlanPoint> points; public List<PlanRect> alcoves; }
    [Serializable] public class PlanSpawn { public string id, kind, space, note; public float x, z, yaw; }
    [Serializable] public class PlanPickup { public string id, kind, space, support; public float x, z, height; public int amount; }
    [Serializable] public class PlanDocument { public string id, space, support, condition; public float x, z; }
    [Serializable] public class PlanCheckpoint { public string id, space, activation, protection; public float x, z; }
    [Serializable] public class PlanMechanism { public string id, kind, space, opens; public float x, z; }
    [Serializable] public class PlanPillar { public string id, space; public float x, z, size; }
    [Serializable] public class PlanExterior { public string space; public float x, z, w, d, victoryX, victoryZ; }
    [Serializable] public class PlanRegion { public string id, contents, limit; }

    [Serializable]
    public class LevelPlan
    {
        public string version, notes;
        public float wallThickness = 0.2f, envelopeWallThickness = 0.4f;
        public List<PlanFloor> floors;
        public List<PlanRoom> rooms;
        public List<PlanCirculation> circulation;
        public List<PlanStairs> stairs;
        public List<PlanDoor> doors;
        public List<PlanConnector> connectors;
        public List<PlanSpawn> spawns;
        public List<PlanPickup> pickups;
        public List<PlanDocument> documents;
        public List<PlanCheckpoint> checkpoints;
        public List<PlanMechanism> mechanisms;
        public List<PlanPillar> pillars;
        public PlanExterior exterior;
        public List<PlanRegion> regions;

        public const string DefaultAssetPath = "Assets/_Game/Data/LevelPlan/bunker_plan.json";

        public static LevelPlan FromJson(string json) => JsonUtility.FromJson<LevelPlan>(json);

        public PlanFloor Floor(string id) => floors.Find(f => f.id == id);
        public PlanRoom Room(string id) => rooms.Find(r => r.id == id);
        public PlanDoor Door(string id) => doors.Find(d => d.id == id);
        public PlanConnector Connector(string id) => connectors.Find(c => c.id == id);

        // Resolves a local (x,z) inside a floor or connector to world space at floor level.
        public bool TryToWorld(string space, float x, float z, out Vector3 world)
        {
            var f = Floor(space);
            if (f != null) { world = f.origin.ToVector3() + new Vector3(x, 0, z); return true; }
            var c = Connector(space);
            if (c != null) { world = c.origin.ToVector3() + new Vector3(x, 0, z); return true; }
            world = Vector3.zero; return false;
        }

        // Deterministic GUID from a stable catalogue ID (88.6: identity never comes from instanceID).
        public static Guid StableGuid(string stableId)
        {
            using (var md5 = MD5.Create())
            {
                var hash = md5.ComputeHash(Encoding.UTF8.GetBytes("ESNEIDER:" + stableId));
                return new Guid(hash);
            }
        }
    }
}
