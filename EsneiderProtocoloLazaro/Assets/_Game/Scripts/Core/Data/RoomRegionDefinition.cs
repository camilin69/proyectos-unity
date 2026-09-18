using System.Collections.Generic;
using UnityEngine;

namespace Esneider.Core.Data
{
    public enum RegionKind { Sector, Connector }

    [CreateAssetMenu(menuName = "Esneider/Data/RoomRegion", fileName = "RoomRegionDefinition")]
    public class RoomRegionDefinition : GameDefinition
    {
        public RegionKind kind;
        public string regionId;
        [Tooltip("GUID estable serializado (LevelPlan.StableGuid)")] public string guid;
        public string floorId, sectorId;
        public Vector3 worldOrigin;
        public Rect localRect;
        public float height;
        public List<string> doorIds = new List<string>();
        public List<string> ownedEntityIds = new List<string>();
    }
}
