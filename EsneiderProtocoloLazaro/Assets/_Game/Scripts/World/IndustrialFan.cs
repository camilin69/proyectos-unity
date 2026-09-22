using UnityEngine;

namespace Esneider.World
{
    // Presentation only: no damage, triggers, power authority or audible source.
    public class IndustrialFan : MonoBehaviour
    {
        public Transform rotor;
        public Renderer rotorRenderer;
        [Range(0,15)] public float revolutionsPerMinute=12;
        public float animationDistance=25;
        Quaternion rest=Quaternion.identity;
        float angle;
        Camera viewer;
        void Awake() { if(rotor)rest=rotor.localRotation; }
        void Update()
        {
            if(!viewer)viewer=Camera.main;
            if(!rotor||!viewer||!rotorRenderer||!rotorRenderer.isVisible)return;
            if((viewer.transform.position-transform.position).sqrMagnitude>animationDistance*animationDistance)return;
            Advance(Time.deltaTime);
        }
        public void Advance(float deltaTime)
        {
            if(!rotor||deltaTime<=0)return;
            angle=Mathf.Repeat(angle+Mathf.Clamp(revolutionsPerMinute,0,15)*6*deltaTime,360);
            rotor.localRotation=rest*Quaternion.AngleAxis(angle,Vector3.forward);
        }
    }
}
