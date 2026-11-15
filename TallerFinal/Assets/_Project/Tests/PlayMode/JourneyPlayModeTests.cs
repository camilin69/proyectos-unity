using System.Collections;
using System.Linq;
using Dream.Cinematic;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

namespace Dream.Tests
{
    // El viaje de verdad, en Play: Boot + escenarios aditivos, recuerdos, pasos, cinematicas (saltadas), reloj y final.
    public class JourneyPlayModeTests
    {
        [UnitySetUp]
        public IEnumerator CargarBoot()
        {
            CinematicDirector.AutoSkip = true;
            SceneManager.LoadScene("Boot", LoadSceneMode.Single);
            yield return null;
            yield return null;
            Assert.IsNotNull(GameFlow.Instance, "Boot no cargo");
        }

        [UnityTearDown]
        public IEnumerator Limpiar()
        {
            CinematicDirector.AutoSkip = false;
            Time.timeScale = 1f;
            yield return null;
        }

        static IEnumerator Until(System.Func<bool> cond, float timeout, string what)
        {
            float t = 0f;
            while (!cond() && t < timeout) { t += Time.unscaledDeltaTime; yield return null; }
            Assert.IsTrue(cond(), "tiempo agotado esperando: " + what);
        }

        static bool Playing => GameFlow.Instance.State == GameState.Playing && !JourneyManager.Instance.Busy;

        static MemoryFragment CurrentMemory() =>
            Object.FindObjectsByType<MemoryFragment>().FirstOrDefault(m => m.gameObject.scene == SceneManager.GetActiveScene());

        static TransitionGate NextGate(bool advance) =>
            Object.FindObjectsByType<TransitionGate>().FirstOrDefault(g => g.gameObject.scene == SceneManager.GetActiveScene() && g.advanceScene == advance);

        static void StepInto(TransitionGate g)
        {
            var box = g.GetComponent<BoxCollider>();
            var p = g.transform.position;
            PlayerRig.Instance.Motor.Teleport(new Vector3(p.x, p.y - box.size.y / 2f + 0.05f, p.z), 0f);
        }

        [UnityTest]
        public IEnumerator SinElRecuerdoLaPuertaNoAbre()
        {
            GameFlow.Instance.StartJourney();
            yield return Until(() => Playing && JourneyManager.Instance.Current == 0, 20f, "el cuarto");
            StepInto(NextGate(true));
            yield return new WaitForSeconds(1.5f);
            Assert.AreEqual(0, JourneyManager.Instance.Current, "la puerta se abrio sin recuerdo");
            Assert.AreEqual(GameState.Playing, GameFlow.Instance.State);
            Assert.IsFalse(PlayerRig.Instance.Motor.FlightAllowed, "en el cuarto no se vuela");
        }

        [UnityTest]
        public IEnumerator AlCaminarSuenanPasosEnElAzulejo()
        {
            GameFlow.Instance.StartJourney();
            yield return Until(() => Playing && JourneyManager.Instance.Current == 0, 20f, "el cuarto");
            var rig = PlayerRig.Instance;
            var steps = rig.GetComponent<FootstepSystem>();
            rig.Motor.Teleport(new Vector3(-1.5f, 0.05f, -1.8f), 90f);
            yield return new WaitForSeconds(0.5f);
            int before = steps.StepCount;
            rig.Motor.scriptedVelocity = new Vector3(1.25f, 0f, 0f);
            yield return new WaitForSeconds(3f);
            rig.Motor.scriptedVelocity = null;
            int n = steps.StepCount - before;
            // Walk: 0,45 s por paso -> unos 6-7 pasos en 3 s
            Assert.GreaterOrEqual(n, 4, "pocos pasos: el contacto del pie no se detecta");
            Assert.LessOrEqual(n, 10, "demasiados pasos: la histeresis no funciona");
            Assert.AreEqual(SurfaceType.WetTile, steps.LastSurface, "el piso del cuarto es azulejo mojado");
        }

        [UnityTest]
        public IEnumerator LaTeclaFRecorreCuatroModos()
        {
            GameFlow.Instance.StartJourney();
            yield return Until(() => Playing, 20f, "control");
            var modes = CameraModeController.Instance;
            Assert.AreEqual(0, modes.Mode);
            Assert.IsFalse(modes.ShowingBody);
            for (int i = 1; i <= 4; i++)
            {
                var f = typeof(CameraModeController).GetProperty("Mode");
                f.SetValue(modes, i % 4);
                modes.Apply();
                yield return null;
                Assert.AreEqual(i % 4 != 0, modes.ShowingBody, $"modo {i % 4}");
                Assert.AreEqual(i % 4 == 0, modes.firstPerson.gameObject.activeSelf);
            }
        }

        [UnityTest]
        public IEnumerator ElViajeCompletoTerminaEnElCuartoAMedianoche()
        {
            float[] hours = { 7f, 9f, 12f, 20f, 21.33f, 22.67f, 23.5f };
            GameFlow.Instance.StartJourney();
            for (int i = 0; i < JourneyManager.Scenes.Length; i++)
            {
                yield return Until(() => Playing && JourneyManager.Instance.Current == i, 30f, "escenario " + i);
                Assert.AreEqual(hours[i], TimeOfDay.Instance.hour, 0.3f, $"hora al llegar al escenario {i + 1}");
                Assert.AreEqual(i == 2, PlayerRig.Instance.Motor.FlightAllowed, $"vuelo en el escenario {i + 1}");
                CurrentMemory().Collect();
                yield return null;
                var landing = NextGate(false);
                if (landing)
                {
                    StepInto(landing);
                    yield return Until(() => Playing && !PlayerRig.Instance.Motor.FlightAllowed, 30f, "aterrizar en la colina");
                    Assert.AreEqual(12f, TimeOfDay.Instance.hour, 1f);
                }
                StepInto(NextGate(true));
                yield return new WaitForSeconds(0.2f);
            }
            yield return Until(() => GameFlow.Instance.State == GameState.Ended, 40f, "el final");
            Assert.AreEqual(0, JourneyManager.Instance.Current, "vuelve al cuarto");
            Assert.IsTrue(JourneyManager.Instance.InFinale);
            Assert.AreEqual(7, ScoreSystem.Instance.Memories);
            Assert.IsTrue(ScoreSystem.Instance.Locked);
            Assert.AreEqual("00:00", TimeOfDay.Format(TimeOfDay.Instance.hour));
            int score = ScoreSystem.Instance.Score;
            Assert.AreEqual(0, ScoreSystem.Instance.AddMemory(), "despues del final nada suma");
            Assert.AreEqual(score, ScoreSystem.Instance.Score);
        }
    }
}
