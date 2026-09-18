using System;
using System.Collections.Generic;
using Esneider.Core.Data;
using Esneider.World;
using UnityEngine;

namespace Esneider.Player
{
    public enum AmmoType { Pistol, Shotgun }

    // Sección 18/11.1: tres ranuras de arma, munición por tipo, curas, documentos. Sin peso ni cuadrícula.
    public class Inventory : MonoBehaviour
    {
        public WeaponDefinition crowbar, pistol, shotgun;
        public PlayerDefinition player;

        public bool hasFlashlight, hasCrowbar, hasPistol, hasShotgun;
        public int pistolMag, pistolReserve, shotgunMag, shotgunReserve;
        public int syringes, rations;
        public readonly HashSet<string> documents = new HashSet<string>();

        public event Action Changed;
        public event Action<string> Message;

        public int MaxSyringes => player != null ? player.maxSyringes : 3;
        public int MaxRations => player != null ? player.maxRations : 2;

        public int MagCapacity(AmmoType t) => t == AmmoType.Pistol ? (pistol != null ? pistol.magazineSize : 12) : (shotgun != null ? shotgun.magazineSize : 6);
        public int ReserveMax(AmmoType t) => t == AmmoType.Pistol ? (pistol != null ? pistol.reserveMax : 80) : (shotgun != null ? shotgun.reserveMax : 36);
        public int Mag(AmmoType t) => t == AmmoType.Pistol ? pistolMag : shotgunMag;
        public int Reserve(AmmoType t) => t == AmmoType.Pistol ? pistolReserve : shotgunReserve;

        public void Notify(string msg) => Message?.Invoke(msg);
        void Raise() => Changed?.Invoke();

        // Devuelve cuántas unidades se aceptaron (recogida parcial 11.1).
        public int TryPickup(Pickup p)
        {
            switch (p.kind)
            {
                case PickupKind.Flashlight: if (hasFlashlight) return 0; hasFlashlight = true; Notify("Linterna recogida"); Raise(); return 1;
                case PickupKind.Crowbar: if (hasCrowbar) return 0; hasCrowbar = true; Notify("Varilla recogida"); Raise(); return 1;
                case PickupKind.Pistol:
                    if (hasPistol) return 0; hasPistol = true;
                    pistolMag = pistol != null ? pistol.pickupLoaded : 10; pistolReserve = pistol != null ? pistol.pickupReserve : 10;
                    Notify("Pistola encontrada"); Raise(); return 1;
                case PickupKind.Shotgun:
                    if (hasShotgun) return 0; hasShotgun = true;
                    shotgunMag = shotgun != null ? shotgun.pickupLoaded : 5; shotgunReserve = shotgun != null ? shotgun.pickupReserve : 5;
                    Notify("Escopeta encontrada"); Raise(); return 1;
                case PickupKind.PistolAmmo: { int n = AddAmmo(AmmoType.Pistol, p.amount); if (n > 0) Notify($"+{n} balas"); return n; }
                case PickupKind.ShotgunAmmo: { int n = AddAmmo(AmmoType.Shotgun, p.amount); if (n > 0) Notify($"+{n} cartuchos"); return n; }
                case PickupKind.Syringe: if (syringes >= MaxSyringes) return 0; syringes++; Notify("Jeringa recogida"); Raise(); return 1;
                case PickupKind.Ration: if (rations >= MaxRations) return 0; rations++; Notify("Ración recogida"); Raise(); return 1;
                case PickupKind.Document: documents.Add(p.documentId ?? p.stableId); Notify("Documento leído"); Raise(); return 1;
            }
            return 0;
        }

        // Munición de arma no encontrada puede recogerse hasta capacidad (68.8); solo entra a la reserva.
        public int AddAmmo(AmmoType t, int amount)
        {
            int room = ReserveMax(t) - Reserve(t);
            int n = Mathf.Clamp(amount, 0, room);
            if (n <= 0) return 0;
            if (t == AmmoType.Pistol) pistolReserve += n; else shotgunReserve += n;
            Raise(); return n;
        }

        // 86.3: transferencia única n = min(capacidad - cargador, reserva).
        public int CommitPistolReload()
        {
            int n = Mathf.Min(MagCapacity(AmmoType.Pistol) - pistolMag, pistolReserve);
            if (n <= 0) return 0;
            pistolReserve -= n; pistolMag += n; Raise(); return n;
        }

        // 86.4: un cartucho por commit.
        public bool CommitShotgunShell()
        {
            if (shotgunMag >= MagCapacity(AmmoType.Shotgun) || shotgunReserve <= 0) return false;
            shotgunReserve--; shotgunMag++; Raise(); return true;
        }

        public bool ConsumeRound(AmmoType t)
        {
            if (Mag(t) <= 0) return false;
            if (t == AmmoType.Pistol) pistolMag--; else shotgunMag--;
            Raise(); return true;
        }

        public bool ConsumeSyringe() { if (syringes <= 0) return false; syringes--; Raise(); return true; }
        public bool ConsumeRation() { if (rations <= 0) return false; rations--; Raise(); return true; }

        public bool HasWeapon(WeaponKind k) => k == WeaponKind.Melee ? hasCrowbar : k == WeaponKind.Pistol ? hasPistol : hasShotgun;
    }
}
