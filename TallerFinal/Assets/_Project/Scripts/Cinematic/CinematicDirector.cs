using System.Collections;
using Unity.Cinemachine;
using UnityEngine;
using UnityEngine.Events;

namespace Dream.Cinematic
{
    // Orquesta cada transicion: quita el control, pone las bandas, corre la cinematica de salida, carga el
    // escenario siguiente detras del fundido, corre la de llegada y devuelve todo en orden inverso.
    public class CinematicDirector : MonoBehaviour
    {
        public static CinematicDirector Instance { get; private set; }

        public CinemachineCamera shotCamera;
        public bool Playing { get; private set; }
        // Para las pruebas automaticas: todas las cinematicas se saltan como si se pulsara Tab.
        public static bool AutoSkip;

        CinematicContext _ctx;

        void Awake() => Instance = this;
        void OnDestroy() { if (Instance == this) Instance = null; }

        void Update()
        {
            if (Playing && DreamInput.Instance != null && DreamInput.Instance.ConsumeSkip()) _ctx.Skipping = true;
        }

        CinematicContext Begin()
        {
            Playing = true;
            _ctx = new CinematicContext { camera = shotCamera, rig = PlayerRig.Instance, fader = ScreenFader.Instance, Skipping = AutoSkip };
            GameFlow.Instance?.SetState(GameState.Cinematic);
            if (_ctx.rig) { _ctx.rig.Motor.controlEnabled = false; _ctx.rig.Motor.Stop(); }
            // la camara de rodaje arranca donde estaba la del jugador, para que el primer plano entre suave
            var brainCam = Camera.main;
            if (brainCam && shotCamera) shotCamera.transform.SetPositionAndRotation(brainCam.transform.position, brainCam.transform.rotation);
            CameraModeController.Instance?.EnterCinematic();
            return _ctx;
        }

        IEnumerator End()
        {
            var rig = _ctx.rig;
            if (rig)
            {
                rig.Motor.scriptedVelocity = null;
                rig.Motor.controlEnabled = true;
                if (rig.HeadLook) rig.HeadLook.target = null;
                foreach (var r in rig.bodyRenderers) if (r) r.enabled = true;
                if (rig.Look) rig.Look.ResetPitch(0f);
            }
            CameraModeController.Instance?.ExitCinematic();
            DreamInput.Instance?.ClearPresses();
            Playing = false;
            if (GameFlow.Instance && GameFlow.Instance.State == GameState.Cinematic) GameFlow.Instance.SetState(GameState.Playing);
            if (_ctx.fader && _ctx.fader.Alpha > 0.01f) yield return _ctx.fader.Fade(_ctx.fader.image.color, 0f, 0.8f);
        }

        public IEnumerator PlayArrival(CinematicSequence seq)
        {
            var ctx = Begin();
            if (seq) yield return seq.Run(ctx);
            yield return End();
        }

        public IEnumerator PlayDeparture(CinematicSequence departure, bool advanceScene, UnityEvent onComplete)
        {
            var ctx = Begin();
            if (departure) yield return departure.Run(ctx);
            if (advanceScene && JourneyManager.Instance)
            {
                var journey = JourneyManager.Instance;
                bool finale = journey.NextIsFinale;
                // detras de un fundido: nunca se ve la carga
                if (ctx.fader && ctx.fader.Alpha < 0.99f) yield return ctx.fader.Fade(finale ? Color.white : Color.black, 1f, 0.5f);
                yield return journey.LoadNext();
                ctx.Skipping = AutoSkip;
                var anchor = journey.Anchor;
                var arrival = anchor ? (finale ? anchor.finaleArrival : anchor.arrival) : null;
                if (arrival) yield return arrival.Run(ctx);
                onComplete?.Invoke();
                if (finale)
                {
                    yield return End();
                    journey.FinishJourney();
                    yield break;
                }
            }
            else onComplete?.Invoke();
            yield return End();
        }
    }
}
