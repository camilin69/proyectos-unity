using UnityEngine;

namespace Esneider.World
{
    // The persistent pickup owns quantity. Its sibling case remains after the pickup is depleted.
    public class AmmoCaseVisual : MonoBehaviour
    {
        public Pickup pickup;
        public GameObject contents;
        void OnEnable() => Refresh();
        void LateUpdate() => Refresh();
        public void Refresh()
        {
            if (!contents || !pickup) return; // Unbound prefab previews show their contents.
            bool stocked = pickup.amount > 0 && pickup.gameObject.activeSelf;
            if (contents.activeSelf != stocked) contents.SetActive(stocked);
        }
    }
}
