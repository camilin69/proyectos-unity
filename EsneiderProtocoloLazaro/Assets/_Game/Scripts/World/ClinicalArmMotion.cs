using UnityEngine;

namespace Esneider.World
{
    // A deliberately slow equipment self-check; no combat or damage callbacks.
    public class ClinicalArmMotion : MonoBehaviour
    {
        public Transform shoulder;
        public Transform elbow;
        public AudioSource servo;
        public float PhaseSeconds { get; private set; }
        public bool Moving { get; private set; }
        void Start()
        {
            if(servo && Esneider.Audio.AudioService.Instance)
                servo.outputAudioMixerGroup=Esneider.Audio.AudioService.Instance.ambient;
        }
        void Update() { Advance(Time.deltaTime); }
        void OnDisable() { if(servo)servo.Stop(); }
        public void Advance(float seconds)
        {
            if(seconds<=0) { if(servo&&servo.isPlaying)servo.Pause();return; }
            Sample(PhaseSeconds+seconds);
            if(servo && Application.isPlaying)
            {
                if(Moving && !servo.isPlaying)servo.Play();
                else if(!Moving && servo.isPlaying)servo.Stop();
            }
        }
        public void Sample(float seconds)
        {
            PhaseSeconds=Mathf.Repeat(seconds,20f);
            Moving=PhaseSeconds>14f;
            float t=Moving?(PhaseSeconds-14f)/6f:0;
            float eased=Moving ? Mathf.Pow(Mathf.Sin(Mathf.PI*t),2) : 0;
            if(shoulder)shoulder.localRotation=Quaternion.Euler(0,6f*eased,0);
            if(elbow)elbow.localRotation=Quaternion.Euler(0,0,4f*eased);
        }
    }
}
