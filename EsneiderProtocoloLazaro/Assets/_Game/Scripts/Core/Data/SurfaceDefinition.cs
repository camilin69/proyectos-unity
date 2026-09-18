using UnityEngine;

namespace Esneider.Core.Data
{
    [CreateAssetMenu(menuName = "Esneider/Data/Surface", fileName = "SurfaceDefinition")]
    public class SurfaceDefinition : GameDefinition
    {
        [Header("96.1")] public float staticFriction = 0.65f, dynamicFriction = 0.55f;
        public float footstepNoiseMultiplier = 1f;
        public string footstepBank, impactBank;
        public string visualReaction;
    }
}
