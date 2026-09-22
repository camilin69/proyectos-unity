using UnityEngine;

namespace Esneider.World
{
    // Presentation follows the existing permission; it never grants it or replays audio.
    public class ServicePanelVisual : MonoBehaviour
    {
        public Mechanism mechanism;
        public Transform lever;
        public Renderer powerLamp, networkLamp;
        float angle;
        MaterialPropertyBlock block;
        public float LeverAngle => angle;
        void OnEnable() { SnapToState(); }
        void Update() { Advance(Time.deltaTime); }
        public void SnapToState()
        {
            angle = mechanism && mechanism.Used ? -55f : 0f;
            Apply();
        }
        public void Advance(float seconds)
        {
            if(seconds<=0) return;
            angle=Mathf.MoveTowards(angle,mechanism && mechanism.Used ? -55f : 0f,110f*seconds);
            Apply();
        }
        void Apply()
        {
            if(lever)lever.localRotation=Quaternion.Euler(angle,0,0);
            SetLamp(powerLamp,new Color(.15f,.75f,.35f));
            SetLamp(networkLamp,mechanism && mechanism.Used ? new Color(.15f,.75f,.35f) : new Color(.8f,.16f,.035f));
        }
        void SetLamp(Renderer lamp,Color color)
        {
            if(!lamp)return;
            if(block==null)block=new MaterialPropertyBlock();
            block.Clear();block.SetColor("_BaseColor",color);block.SetColor("_EmissionColor",color*.6f);lamp.SetPropertyBlock(block);
        }
    }
}
