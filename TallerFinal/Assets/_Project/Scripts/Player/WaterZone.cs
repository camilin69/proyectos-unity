using UnityEngine;

namespace Dream
{
    // Volumen de agua: el motor nada si se hunde mas que swimDepth bajo SurfaceY. La superficie es la cara
    // superior del BoxCollider (trigger), de modo que el volumen y el agua visible coinciden.
    [RequireComponent(typeof(BoxCollider))]
    public class WaterZone : MonoBehaviour
    {
        public SurfaceType shallowSurface = SurfaceType.ShallowWater;
        BoxCollider _box;

        public float SurfaceY => _box.bounds.max.y;

        void Awake() { _box = GetComponent<BoxCollider>(); _box.isTrigger = true; }

        void OnTriggerEnter(Collider other) { var m = other.GetComponent<PlayerMotor>(); if (m) m.EnterWater(this); }
        void OnTriggerExit(Collider other) { var m = other.GetComponent<PlayerMotor>(); if (m) m.ExitWater(this); }
    }
}
