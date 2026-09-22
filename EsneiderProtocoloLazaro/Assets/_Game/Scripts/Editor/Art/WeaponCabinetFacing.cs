using System.Linq;
using Esneider.World;
using UnityEngine;

namespace Esneider.EditorTools
{
    public static class WeaponCabinetFacing
    {
        public static void Apply(Transform root, string region)
        {
            if (region != "REG-S3") return;
            var cabinet = root.GetComponentsInChildren<HingedCabinet>(true).Single(c => c.name.Contains("PICK-W03"));
            var pickup = root.GetComponentsInChildren<Pickup>(true).Single(p => p.stableId == "PICK-W03");
            var facing = Quaternion.Euler(0, 180, 0);
            if (Quaternion.Angle(cabinet.transform.rotation, facing) < .01f) return;
            // S3-R05 is entered from the north. Keep the independent persistent pickup
            // seated inside the cabinet while turning its labelled face toward the entrance.
            var localPosition = cabinet.transform.InverseTransformPoint(pickup.transform.position);
            var localRotation = Quaternion.Inverse(cabinet.transform.rotation) * pickup.transform.rotation;
            cabinet.transform.rotation = facing;
            pickup.transform.SetPositionAndRotation(cabinet.transform.TransformPoint(localPosition), facing * localRotation);
        }
    }
}
