using System.Collections;
using UnityEngine;

namespace Dream.Cinematic
{
    // Cinematica hecha de planos. Si se salta (Tab), cada plano deja su estado final al instante: el sonador
    // termina donde tenia que terminar y la hora queda puesta, asi saltar nunca rompe el viaje.
    public class ShotSequence : CinematicSequence
    {
        public Shot[] shots;
        static Vector3 _startPos;
        static Quaternion _startRot;

        public override IEnumerator Run(CinematicContext ctx)
        {
            foreach (var s in shots) yield return RunShot(s, ctx);
            if (ctx.rig) ctx.rig.Motor.scriptedVelocity = null;
        }

        IEnumerator RunShot(Shot s, CinematicContext ctx)
        {
            var rig = ctx.rig;
            var cam = ctx.camera;
            s.onStart?.Invoke();
            if (s.setHour >= 0f && TimeOfDay.Instance) TimeOfDay.Instance.GoTo(s.setHour, ctx.Skipping ? 0f : s.hourSeconds);
            if (rig)
            {
                if (s.actorTeleport) rig.Motor.Teleport(s.actorTeleport.position, s.actorTeleport.eulerAngles.y);
                if (!string.IsNullOrEmpty(s.actorTrigger)) rig.Anim.Animator.SetTrigger(s.actorTrigger);
                rig.HeadLook.target = s.headLookAt;
                foreach (var r in rig.bodyRenderers) if (r) r.enabled = !s.hideActor;
            }
            if (s.fadeInSeconds > 0f) ctx.fader.Set(s.fadeColor, 1f);
            if (CameraModeController.Instance) CameraModeController.Instance.SetCut(s.cut);

            _startPos = cam ? cam.transform.position : Vector3.zero;
            _startRot = cam ? cam.transform.rotation : Quaternion.identity;
            float dur = Mathf.Max(0.01f, s.duration);
            bool fadingOut = false;
            for (float t = 0f; t <= dur; t += Time.deltaTime)
            {
                if (ctx.Skipping) break;
                float k = Mathf.Clamp01(t / dur);
                PlaceCamera(s, cam, rig, k);
                DriveActor(s, rig);
                if (s.fadeInSeconds > 0f && t < s.fadeInSeconds) ctx.fader.Set(s.fadeColor, 1f - Smooth(t / s.fadeInSeconds));
                if (s.fadeOutSeconds > 0f && t >= dur - s.fadeOutSeconds)
                {
                    fadingOut = true;
                    ctx.fader.Set(s.fadeColor, Smooth((t - (dur - s.fadeOutSeconds)) / s.fadeOutSeconds));
                }
                yield return null;
            }
            // estado final del plano (tambien al saltar)
            if (rig)
            {
                rig.Motor.scriptedVelocity = null;
                if (s.actorWalkTo && (ctx.Skipping || Flat(rig.transform.position - s.actorWalkTo.position).magnitude > 0.6f))
                    rig.Motor.Teleport(s.actorWalkTo.position, s.actorWalkTo.eulerAngles.y);
            }
            PlaceCamera(s, cam, rig, 1f);
            if (s.fadeOutSeconds > 0f || fadingOut) ctx.fader.Set(s.fadeColor, 1f);
            else if (s.fadeInSeconds > 0f) ctx.fader.Set(s.fadeColor, 0f);
            if (CameraModeController.Instance) CameraModeController.Instance.SetCut(false);
            s.onEnd?.Invoke();
        }

        static float Smooth(float x) { x = Mathf.Clamp01(x); return x * x * (3f - 2f * x); }
        static Vector3 Flat(Vector3 v) => new(v.x, 0f, v.z);

        static void PlaceCamera(Shot s, Unity.Cinemachine.CinemachineCamera cam, PlayerRig rig, float k)
        {
            if (!cam) return;
            float e = Smooth(k);
            Vector3 pos = cam.transform.position;
            if (s.orbitCenter && s.from)
            {
                var off = s.from.position - s.orbitCenter.position;
                pos = s.orbitCenter.position + Quaternion.Euler(0f, s.orbitDegrees * e, 0f) * off;
            }
            else if (s.from && s.to) pos = Vector3.Lerp(s.from.position, s.to.position, e);
            else if (s.from) pos = s.from.position;
            else if (s.to) pos = Vector3.Lerp(_startPos, s.to.position, e);   // desde donde quedo la camara
            // brazo de grua: si algo se interpone entre el sonador y la camara (una escalera, una pared, el suelo),
            // la camara se acerca a el hasta verlo
            if (rig && !s.hideActor && (s.lookAtActorHead || (s.lookAt && Vector3.Distance(s.lookAt.position, rig.transform.position) < 5f)))
            {
                var head = rig.transform.position + Vector3.up * 1.45f;
                var dir = pos - head; float len = dir.magnitude;
                if (len > 0.4f && Physics.SphereCast(head, 0.18f, dir / len, out var hit, len, ~0, QueryTriggerInteraction.Ignore)
                    && !hit.collider.GetComponentInParent<PlayerRig>())
                    pos = head + dir / len * Mathf.Max(0.6f, hit.distance - 0.25f);
            }
            cam.transform.position = pos;

            Vector3? look = null;
            if (s.lookAt) look = s.lookAt.position;
            else if (s.lookAtActorHead && rig) look = rig.transform.position + Vector3.up * 1.5f;
            else if (s.orbitCenter) look = s.orbitCenter.position;
            if (look.HasValue && (look.Value - pos).sqrMagnitude > 1e-4f) cam.transform.rotation = Quaternion.LookRotation(look.Value - pos, Vector3.up);
            else if (s.from && s.to) cam.transform.rotation = Quaternion.Slerp(s.from.rotation, s.to.rotation, e);
            else if (s.from) cam.transform.rotation = s.from.rotation;
            else if (s.to) cam.transform.rotation = Quaternion.Slerp(_startRot, s.to.rotation, e);

            float f = s.focalLengthEnd > 0f ? Mathf.Lerp(s.focalLength, s.focalLengthEnd, e) : s.focalLength;
            cam.Lens.FieldOfView = CineRig.FocalToFov(Mathf.Max(8f, f));
        }

        static void DriveActor(Shot s, PlayerRig rig)
        {
            if (!rig) return;
            if (s.actorWalkTo)
            {
                var d = Flat(s.actorWalkTo.position - rig.transform.position);
                rig.Motor.scriptedVelocity = d.magnitude > 0.08f ? d.normalized * s.actorSpeed : Vector3.zero;
            }
            else if (s.actorVelocity.sqrMagnitude > 0f) rig.Motor.scriptedVelocity = s.actorVelocity;
            else rig.Motor.scriptedVelocity = null;
        }
    }
}
