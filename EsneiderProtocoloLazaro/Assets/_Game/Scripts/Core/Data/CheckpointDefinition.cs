using UnityEngine;

namespace Esneider.Core.Data
{
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
}
