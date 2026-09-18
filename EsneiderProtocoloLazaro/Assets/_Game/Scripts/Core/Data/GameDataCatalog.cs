using System.Collections.Generic;
using UnityEngine;

namespace Esneider.Core.Data
{
    // Catálogo único para consumidores y validador (95).
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
