using System.Collections.Generic;
using UnityEngine;

namespace Esneider.World
{
    public class DarknessVolume : MonoBehaviour
    {
        public Vector3 size;
        static readonly HashSet<DarknessVolume> Active = new HashSet<DarknessVolume>();
        void OnEnable() => Active.Add(this);
        void OnDisable() => Active.Remove(this);
        public static bool Contains(Vector3 position)
        {
            foreach (var volume in Active)
                if (volume && new Bounds(Vector3.zero,volume.size).Contains(volume.transform.InverseTransformPoint(position))) return true;
            return false;
        }
    }
}
