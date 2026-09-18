using UnityEngine;

namespace Esneider.World
{
    // 11.1/68.8: recogida parcial; nunca destruir munición que no cabe.
    public class Pickup : MonoBehaviour, IInteractable
    {
        public PickupKind kind;
        public int amount = 1;
        public string stableId;
        public string documentId;
        public string guid;

        public string Prompt => kind switch
        {
            PickupKind.Flashlight => "Recoger linterna",
            PickupKind.Crowbar => "Extraer varilla",
            PickupKind.Pistol => "Tomar pistola",
            PickupKind.Shotgun => "Tomar escopeta",
            PickupKind.PistolAmmo => $"Recoger balas ({amount})",
            PickupKind.ShotgunAmmo => $"Recoger cartuchos ({amount})",
            PickupKind.Syringe => "Recoger jeringa",
            PickupKind.Ration => "Recoger ración",
            PickupKind.Document => "Leer documento",
            _ => "Recoger"
        };

        public bool CanInteract(GameObject who) => amount > 0 && who.GetComponentInParent<Player.Inventory>() != null;

        public void Interact(GameObject who)
        {
            var inv = who.GetComponentInParent<Player.Inventory>();
            if (inv == null) return;
            int accepted = inv.TryPickup(this);
            if (accepted <= 0) { inv.Notify("No cabe más"); return; }
            amount -= accepted;
            GetComponent<PersistentEntity>()?.NotifyPickupTaken(amount);
            // EVT-02/04/09/17 (93): recogida = evento I con compromiso de objetivo (70.1)
            if (kind == PickupKind.Crowbar) Core.ObjectiveService.Complete("O02");
            else if (kind == PickupKind.Pistol) Core.ObjectiveService.Complete("O04");
            else if (kind == PickupKind.Shotgun) Core.ObjectiveService.Complete("O07");
            else if (kind == PickupKind.Document && !string.IsNullOrEmpty(documentId)) Core.Persistence.WorldStateRegistry.Session.MarkDocumentRead(documentId);
            if (amount <= 0) gameObject.SetActive(false);
        }
    }
}
