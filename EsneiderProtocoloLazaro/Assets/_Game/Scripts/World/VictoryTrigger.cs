using Esneider.Core;
using Esneider.Core.Persistence;
using UnityEngine;

namespace Esneider.World
{
    // 97/EVT-EXIT: se gana cruzando el exterior seguro con el jefe derrotado, una sola vez.
    [RequireComponent(typeof(BoxCollider))]
    public class VictoryTrigger : MonoBehaviour
    {
        bool _fired;
        void Awake() { var c = GetComponent<BoxCollider>(); c.isTrigger = true; gameObject.layer = GameLayers.Trigger; }

        void OnTriggerEnter(Collider other)
        {
            if (_fired) return;
            var pc = other.GetComponent<Player.PlayerController>();
            if (pc == null || !ObjectiveService.Has(ObjectiveService.BossDefeated)) return;
            _fired = true;
            WorldStateRegistry.Session.SetFlag("CAMPAIGN_WON");
            pc.Win();
        }
    }
}
