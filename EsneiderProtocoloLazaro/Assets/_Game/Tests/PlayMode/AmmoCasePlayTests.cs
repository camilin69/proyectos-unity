using System.Collections;
using Esneider.Player;
using Esneider.World;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;

namespace Esneider.Tests
{
    public class AmmoCasePlayTests
    {
        [UnityTest] public IEnumerator EmptyPresentationUpdatesAfterPickupChildDisablesItself()
        {
            var box=new GameObject("Persistent empty shell");var who=new GameObject("Collector");
            try
            {
                var contents=new GameObject("Contents");contents.transform.SetParent(box.transform,false);
                var entity=new GameObject("Pickup");entity.transform.SetParent(box.transform,false);
                var p=entity.AddComponent<Pickup>();p.kind=PickupKind.PistolAmmo;p.amount=10;
                var inv=who.AddComponent<Inventory>();inv.pistolReserve=inv.ReserveMax(AmmoType.Pistol)-2;
                var view=box.AddComponent<AmmoCaseVisual>();view.pickup=p;view.contents=contents;
                p.Interact(who);yield return null;yield return null;
                Assert.AreEqual(8,p.amount);Assert.IsTrue(contents.activeInHierarchy);Assert.IsTrue(entity.activeInHierarchy);
                inv.pistolReserve=0;p.Interact(who);yield return null;yield return null;
                Assert.IsFalse(entity.activeSelf);Assert.IsFalse(contents.activeSelf);Assert.IsTrue(box.activeInHierarchy);
                // A restored nonempty pickup also refreshes the already living presentation root.
                p.amount=3;entity.SetActive(true);yield return null;yield return null;
                Assert.IsTrue(contents.activeInHierarchy);Assert.AreEqual(3,p.amount);
            }
            finally { Object.DestroyImmediate(box);Object.DestroyImmediate(who); }
        }
    }
}
