using Esneider.AI;
using Esneider.Player;
using UnityEngine;

namespace Esneider.World
{
    public class ArmedEncounter : MonoBehaviour
    {
        EnemyBrain brain; Inventory inventory;
        void Update()
        {
            if (!brain) brain = GetComponent<EnemyBrain>();
            if (!inventory) inventory = FindFirstObjectByType<Inventory>();
            if (inventory && inventory.hasCrowbar && brain && brain.State == EnemyState.Inactive) brain.Activate();
        }
    }
}
