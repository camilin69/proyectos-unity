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
        public const int SlotCount = 9;
        public List<PickupKind> hotbarOrder = new List<PickupKind>();
        public int selectedSlot;
        public PickupKind? SelectedItem => ItemAt(selectedSlot);
        public PickupKind? ItemAt(int slot) => slot >= 0 && slot < hotbarOrder.Count ? hotbarOrder[slot] : (PickupKind?)null;
        public bool HasItem(PickupKind kind) => kind switch
        {
            PickupKind.Flashlight => hasFlashlight, PickupKind.Crowbar => hasCrowbar,
            PickupKind.Pistol => hasPistol, PickupKind.Shotgun => hasShotgun,
            PickupKind.PistolAmmo => false, PickupKind.ShotgunAmmo => false,
            PickupKind.Syringe => syringes > 0, PickupKind.Ration => rations > 0, _ => false
        };
        public static WeaponKind? WeaponFor(PickupKind? kind) => kind == PickupKind.Crowbar ? WeaponKind.Melee : kind == PickupKind.Pistol ? WeaponKind.Pistol : kind == PickupKind.Shotgun ? WeaponKind.Shotgun : (WeaponKind?)null;
        public static PickupKind ItemFor(WeaponKind kind) => kind == WeaponKind.Melee ? PickupKind.Crowbar : kind == WeaponKind.Pistol ? PickupKind.Pistol : PickupKind.Shotgun;
        public static string ItemName(PickupKind kind) => kind switch
        {
            PickupKind.Flashlight => "LINTERNA", PickupKind.Crowbar => "VARILLA", PickupKind.Pistol => "PISTOLA", PickupKind.Shotgun => "ESCOPETA",
            PickupKind.PistolAmmo => "BALAS", PickupKind.ShotgunAmmo => "CARTUCHOS", PickupKind.Syringe => "JERINGA", PickupKind.Ration => "RACIÓN", _ => ""
        };
        public int Count(PickupKind kind) => kind == PickupKind.Syringe ? syringes : kind == PickupKind.Ration ? rations : kind == PickupKind.PistolAmmo ? TotalAmmo(AmmoType.Pistol) : kind == PickupKind.ShotgunAmmo ? TotalAmmo(AmmoType.Shotgun) : HasItem(kind) ? 1 : 0;

        // New types append once; depleted stacks keep their number for the next pickup.
        public void EnsureHotbar()
        {
            var selected = SelectedItem;
            int removed = hotbarOrder.RemoveAll(k => k == PickupKind.PistolAmmo || k == PickupKind.ShotgunAmmo);
            if (removed > 0 && selected.HasValue)
            {
                int migrated = hotbarOrder.IndexOf(selected.Value);
                selectedSlot = migrated >= 0 ? migrated : 0;
            }
            foreach (PickupKind kind in Enum.GetValues(typeof(PickupKind)))
                if (HasItem(kind) && !hotbarOrder.Contains(kind) && hotbarOrder.Count < SlotCount) hotbarOrder.Add(kind);
            selectedSlot = Mathf.Clamp(selectedSlot, 0, SlotCount - 1);
        }
        public void Select(int slot) { EnsureHotbar(); selectedSlot = Mathf.Clamp(slot, 0, SlotCount - 1); Changed?.Invoke(); }
        public string[] CaptureHotbar() { EnsureHotbar(); return hotbarOrder.ConvertAll(k => k.ToString()).ToArray(); }
        public void RestoreHotbar(string[] order, int slot)
        {
            hotbarOrder.Clear();
            if (order != null) foreach (var name in order)
                if (Enum.TryParse<PickupKind>(name, out var kind) && kind != PickupKind.Document && Enum.IsDefined(typeof(PickupKind), kind) && !hotbarOrder.Contains(kind) && hotbarOrder.Count < SlotCount) hotbarOrder.Add(kind);
            selectedSlot = slot; EnsureHotbar(); Changed?.Invoke();
        }

        public event Action Changed;
        public event Action<string> Message;

        public int MaxSyringes => player != null ? player.maxSyringes : 3;
        public int MaxRations => player != null ? player.maxRations : 2;

        public int MagCapacity(AmmoType t) => t == AmmoType.Pistol ? (pistol != null ? pistol.magazineSize : 12) : (shotgun != null ? shotgun.magazineSize : 6);
        public int ReserveMax(AmmoType t) => t == AmmoType.Pistol ? (pistol != null ? pistol.reserveMax : 80) : (shotgun != null ? shotgun.reserveMax : 36);
        public int Mag(AmmoType t) => t == AmmoType.Pistol ? pistolMag : shotgunMag;
        public int Reserve(AmmoType t) => t == AmmoType.Pistol ? pistolReserve : shotgunReserve;
        // Legacy save fields remain compatible; gameplay spends their combined total directly.
        public int TotalAmmo(AmmoType t) => Mag(t) + Reserve(t);
        public string AmmoLabel(AmmoType t) => t == AmmoType.Pistol ? $"{TotalAmmo(t)} balas" : $"{TotalAmmo(t)} cartuchos";

        public void Notify(string msg) => Message?.Invoke(msg);
        void Raise() { EnsureHotbar(); Changed?.Invoke(); }

        // Devuelve cuántas unidades se aceptaron (recogida parcial 11.1).
        public int TryPickup(Pickup p)
        {
            switch (p.kind)
            {
                case PickupKind.Flashlight: if (hasFlashlight) return 0; hasFlashlight = true; Notify("Linterna recogida"); Raise(); return 1;
                case PickupKind.Crowbar: if (hasCrowbar) return 0; hasCrowbar = true; Notify("Varilla recogida"); Raise(); return 1;
                case PickupKind.Pistol:
                    if (hasPistol) return 0; hasPistol = true;
                    pistolMag = Mathf.Clamp(pistol != null ? pistol.pickupLoaded : 10, 0, MagCapacity(AmmoType.Pistol));
                    pistolReserve = Mathf.Clamp(pistolReserve + (pistol != null ? pistol.pickupReserve : 10), 0, ReserveMax(AmmoType.Pistol));
                    Notify("Pistola encontrada"); Raise(); return 1;
                case PickupKind.Shotgun:
                    if (hasShotgun) return 0; hasShotgun = true;
                    shotgunMag = Mathf.Clamp(shotgun != null ? shotgun.pickupLoaded : 5, 0, MagCapacity(AmmoType.Shotgun));
                    shotgunReserve = Mathf.Clamp(shotgunReserve + (shotgun != null ? shotgun.pickupReserve : 5), 0, ReserveMax(AmmoType.Shotgun));
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
            if (TotalAmmo(t) <= 0) return false;
            if (t == AmmoType.Pistol) { if (pistolMag > 0) pistolMag--; else pistolReserve--; }
            else { if (shotgunMag > 0) shotgunMag--; else shotgunReserve--; }
            Raise(); return true;
        }

        public bool ConsumeSyringe() { if (syringes <= 0) return false; syringes--; Raise(); return true; }
        public bool ConsumeRation() { if (rations <= 0) return false; rations--; Raise(); return true; }

        public bool HasWeapon(WeaponKind k) => k == WeaponKind.Melee ? hasCrowbar : k == WeaponKind.Pistol ? hasPistol : hasShotgun;
    }
}
