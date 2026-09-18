using UnityEngine;

namespace Esneider.World
{
    public interface IInteractable
    {
        string Prompt { get; }
        bool CanInteract(GameObject who);
        void Interact(GameObject who);
    }

    public enum PickupKind { Flashlight, Crowbar, Pistol, Shotgun, PistolAmmo, ShotgunAmmo, Syringe, Ration, Document }
}
