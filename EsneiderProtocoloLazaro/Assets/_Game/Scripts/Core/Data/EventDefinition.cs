using UnityEngine;

namespace Esneider.Core.Data
{
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
}
