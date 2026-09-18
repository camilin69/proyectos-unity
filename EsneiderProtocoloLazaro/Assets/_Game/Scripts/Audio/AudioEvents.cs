using Esneider.AI;
using Esneider.Core;
using Esneider.Core.Data;
using UnityEngine;

namespace Esneider.Audio
{
    // Puente eventos de gameplay → bancos (17/50.3/96.2). Los datos de ruido lógico no dependen del audio y viceversa.
    public class AudioEvents : MonoBehaviour
    {
        public AudioBankSet bankSet;
        public AudioService service;

        void Awake()
        {
            if (service == null) service = GetComponent<AudioService>(); if (service == null) service = AudioService.Instance;
            if (service != null && bankSet != null) bankSet.ApplyTo(service);
        }
        void OnEnable() { NoiseSystem.Emitted += OnNoise; EnemyBrain.AnyStateChanged += OnEnemyState; }
        void OnDisable() { NoiseSystem.Emitted -= OnNoise; EnemyBrain.AnyStateChanged -= OnEnemyState; }

        void OnNoise(NoiseEvent e)
        {
            if (service == null) return;
            switch (e.kind)
            {
                case "footstep":
                    {
                        var motor = e.source != null ? e.source.GetComponent<Player.PlayerMotor>() : null;
                        string surf = SurfaceUnder(e.source);
                        float vol = motor != null && motor.IsCrouched ? 0.35f : motor != null && motor.IsRunning ? 1f : 0.7f;
                        service.Play("SND-STEP-" + surf, e.position, vol, 128, 0.12f, service.weapons); break;
                    }
                case "crowbar": service.Play("SND-CROWBAR-Swing", e.position, 0.9f, 64, 0f, service.weapons); break;
                case "Pistol": service.Play("SND-PISTOL-Shot", e.position, 1f, 40, 0f, service.weapons); break;
                case "Shotgun": service.Play("SND-SHOTGUN-Shot", e.position, 1f, 40, 0f, service.weapons); break;
                case "door": service.Play("SND-DOOR-Slide-Start", e.position, 0.8f, 100, 0.3f, service.ambient); break;
                case "prop-impact": service.Play("SND-PROP-Impact", e.position, 0.9f, 100, 0.25f, service.ambient); break;
                case "mechanism": service.Play("SND-LEVER", e.position, 0.9f, 80, 0.5f, service.ambient); break;
            }
        }

        static string SurfaceUnder(GameObject who)
        {
            if (who == null) return "CON";
            if (Physics.Raycast(who.transform.position + Vector3.up * 0.3f, Vector3.down, out var hit, 1.2f, GameLayers.Mask(GameLayers.WorldStatic, GameLayers.DynamicProp), QueryTriggerInteraction.Ignore))
            {
                var tag = hit.collider.GetComponent<World.SurfaceTag>();
                if (tag != null) return tag.surfaceId.Replace("SUR-", "");
                var pm = hit.collider.sharedMaterial; if (pm != null && pm.name.StartsWith("SUR-")) return pm.name.Substring(4);
            }
            return "CON";
        }

        void OnEnemyState(EnemyBrain b, EnemyState from, EnemyState to)
        {
            if (service == null || b == null || b.definition == null) return;
            bool vig = b.definition.kind == EnemyKind.Vigia; var p = b.transform.position + Vector3.up;
            switch (to)
            {
                case EnemyState.Prepare: service.Play(vig ? (b.tutorialTelegraph ? "SND-VIG-NetCharge-Tutorial" : "SND-VIG-NetCharge") : "SND-KUS-RayCharge", p, 1f, 0, 0f, service.enemies, false); break; // señal mortal: prioridad máxima, sin jitter
                case EnemyState.Attack: service.Play(vig ? "SND-VIG-NetRelease" : "SND-KUS-RayRelease", p, 1f, 0, 0f, service.enemies); break;
                case EnemyState.Alert: service.Play("SND-RELAY", p, 0.6f, 32, 0.5f, service.enemies); break;
                case EnemyState.Dead: service.Play(vig ? "SND-VIG-Step" : "SND-KUS-Step", p, 1f, 32, 0f, service.enemies); service.Play("SND-PROP-Impact", p, 0.8f, 32, 0f, service.enemies); break;
                case EnemyState.Staggered: service.Play("SND-CROWBAR-ImpactMetal", p, 0.9f, 48, 0f, service.weapons); break;
            }
        }
    }
}
