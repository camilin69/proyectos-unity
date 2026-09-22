using Esneider.Core.Data;
using Esneider.Player;
using UnityEngine;
using UnityEngine.UI;

namespace Esneider.UI
{
    public class InventoryHotbar : MonoBehaviour
    {
        public PlayerController player;
        readonly Image[] backgrounds = new Image[Inventory.SlotCount];
        readonly Text[] labels = new Text[Inventory.SlotCount];
        readonly Outline[] borders = new Outline[Inventory.SlotCount];
        Text selection;
        public int SelectedSlot { get; private set; } = -1;
        public string SlotText(int index) => labels[index] != null ? labels[index].text : "";

        void Start()
        {
            var font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            for (int i = 0; i < Inventory.SlotCount; i++)
            {
                var cell = new GameObject("Slot_" + i, typeof(RectTransform), typeof(Image));
                cell.transform.SetParent(transform, false);
                var rect = cell.GetComponent<RectTransform>();
                rect.anchorMin = rect.anchorMax = new Vector2(.5f, 0);
                rect.pivot = new Vector2(.5f, 0); rect.sizeDelta = new Vector2(82, 66);
                rect.anchoredPosition = new Vector2((i - 4f) * 88, 22);
                backgrounds[i] = cell.GetComponent<Image>(); backgrounds[i].raycastTarget = false;
                borders[i] = cell.AddComponent<Outline>(); borders[i].effectDistance = new Vector2(3,3); borders[i].effectColor = new Color(1,.85f,.35f);
                var caption = new GameObject("Label", typeof(RectTransform), typeof(Text));
                caption.transform.SetParent(cell.transform, false);
                var text = caption.GetComponent<Text>(); text.font = font; text.fontSize = 13;
                text.alignment = TextAnchor.MiddleCenter; text.raycastTarget = false;
                text.rectTransform.anchorMin = Vector2.zero; text.rectTransform.anchorMax = Vector2.one;
                text.rectTransform.offsetMin = new Vector2(3, 3); text.rectTransform.offsetMax = new Vector2(-3, -3);
                labels[i] = text;
            }
            var heading = new GameObject("SelectedItem", typeof(RectTransform), typeof(Text)); heading.transform.SetParent(transform,false);
            selection = heading.GetComponent<Text>(); selection.font=font; selection.fontSize=16; selection.alignment=TextAnchor.MiddleCenter; selection.raycastTarget=false;
            selection.rectTransform.anchorMin=selection.rectTransform.anchorMax=new Vector2(.5f,0); selection.rectTransform.pivot=new Vector2(.5f,0);
            selection.rectTransform.sizeDelta=new Vector2(790,30); selection.rectTransform.anchoredPosition=new Vector2(0,94);
        }

        void Update()
        {
            if (!player || !player.inventory || !player.actions) return;
            var inv = player.inventory;
            inv.EnsureHotbar(); SelectedSlot = inv.selectedSlot;
            for (int i=0; i<Inventory.SlotCount; i++)
            {
                var item=inv.ItemAt(i); string caption=(i+1)+"\n—";
                if(item.HasValue)
                {
                    caption=(i+1)+"\n"+Inventory.ItemName(item.Value);
                    if(item==World.PickupKind.Flashlight) caption+="\nMANO IZQ.";
                    else if(item==World.PickupKind.Pistol) caption+="\n"+inv.AmmoLabel(AmmoType.Pistol);
                    else if(item==World.PickupKind.Shotgun) caption+="\n"+inv.AmmoLabel(AmmoType.Shotgun);
                    else if(item==World.PickupKind.PistolAmmo || item==World.PickupKind.ShotgunAmmo) caption+="\nTOTAL ×"+inv.Count(item.Value);
                    else if(!Inventory.WeaponFor(item).HasValue) caption+=" ×"+inv.Count(item.Value);
                }
                Set(i,item.HasValue && inv.HasItem(item.Value),caption,SelectedSlot==i);
            }
            var selected=inv.SelectedItem;
            selection.text=(SelectedSlot+1)+" · "+(selected.HasValue ? Inventory.ItemName(selected.Value) : "MANO DERECHA VACÍA")+(inv.hasFlashlight ? "     |     Clic derecho: linterna" : "");
        }

        void Set(int i, bool owned, string caption, bool selected)
        {
            backgrounds[i].color = selected ? new Color(.20f, .43f, .45f, .95f) : new Color(.025f, .035f, .04f, .90f);
            borders[i].enabled = selected;
            labels[i].text = caption;
            labels[i].color = owned ? Color.white : new Color(.4f, .44f, .46f);
        }
    }
}
