using Esneider.Core;
using Esneider.Core.Persistence;
using UnityEngine;

namespace Esneider.World
{
    // Palancas/paneles (68.9): operar concede un permiso global (flag) y prepara la región siguiente (88.2).
    public class Mechanism : MonoBehaviour, IInteractable
    {
        public string mechanismId;
        public string grantsFlag;
        public string preloadRegion;
        public float operateSeconds = 2f;
        public bool Used => !string.IsNullOrEmpty(grantsFlag) && ObjectiveService.Has(grantsFlag);

        public string Prompt => Used ? "Operado" : "Operar";
        public bool CanInteract(GameObject who) => !Used;

        public void Interact(GameObject who)
        {
            if (Used) return;
            ObjectiveService.Grant(grantsFlag);
            WorldStateRegistry.Session.Apply(WorldEventKind.MechanismUsed, "", null, mechanismId);
            NoiseSystem.Emit(transform.position, 6f, gameObject, "mechanism");
            if (!string.IsNullOrEmpty(preloadRegion)) RegionStreamer.Instance?.Preload(preloadRegion);
            who.GetComponentInParent<Player.Inventory>()?.Notify(Message());
        }

        string Message() => grantsFlag switch
        {
            ObjectiveService.PermisoServicio => "Red de servicio reconectada",
            ObjectiveService.PermisoA => "Autorización A habilitada",
            ObjectiveService.PermisoB => "Autorización clínica habilitada",
            ObjectiveService.PanelExit => "Compuerta exterior liberada",
            _ => "Mecanismo operado"
        };
    }
}
