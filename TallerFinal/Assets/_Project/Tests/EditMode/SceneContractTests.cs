using System.Linq;
using Dream.Cinematic;
using NUnit.Framework;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

namespace Dream.Tests
{
    // Contrato de cada escenario: lo que el viaje necesita para no romperse, y lo que pide la rubrica.
    public class SceneContractTests
    {
        const string Dir = "Assets/_Project/Scenes";

        static T[] InScene<T>() where T : Object => Object.FindObjectsByType<T>(FindObjectsInactive.Include);

        [TestCaseSource(nameof(Indices))]
        public void CadaEscenarioTieneRecuerdoPasoYAmbiente(int i)
        {
            string name = JourneyManager.Scenes[i];
            EditorSceneManager.OpenScene($"{Dir}/{name}.unity");
            var anchors = InScene<SceneAnchor>();
            Assert.AreEqual(1, anchors.Length, $"{name}: un SceneAnchor");
            var a = anchors[0];
            Assert.AreEqual(i, a.index, $"{name}: indice del anchor");
            Assert.IsNotNull(a.spawn, $"{name}: punto de aparicion");
            Assert.IsNotNull(a.arrival, $"{name}: cinematica de llegada");
            Assert.Less(a.startHour, a.endHour, $"{name}: la hora avanza");
            Assert.AreEqual(1, InScene<MemoryFragment>().Length, $"{name}: un recuerdo escondido");
            var gates = InScene<TransitionGate>();
            Assert.IsTrue(gates.Any(g => g.advanceScene && g.requireMemory && g.departure), $"{name}: un paso que exige el recuerdo");
            Assert.IsTrue(InScene<Volume>().Any(v => v.sharedProfile != null), $"{name}: volumen de ambiente (niebla)");
            foreach (var seq in InScene<ShotSequence>())
                Assert.IsTrue(seq.shots != null && seq.shots.Length > 0, $"{name}: {seq.name} sin planos");
            foreach (var go in InScene<GameObject>())
                foreach (var c in go.GetComponents<Component>())
                    Assert.IsNotNull(c, $"{name}: script faltante en {go.name}");
        }

        static int[] Indices() => Enumerable.Range(0, JourneyManager.Scenes.Length).ToArray();

        [Test]
        public void ElCuartoTieneRegresoParaElFinal()
        {
            EditorSceneManager.OpenScene($"{Dir}/S1_Cuarto.unity");
            var a = InScene<SceneAnchor>()[0];
            Assert.IsNotNull(a.finaleSpawn);
            Assert.IsNotNull(a.finaleArrival);
        }

        [Test]
        public void SoloElCieloDejaVolar()
        {
            for (int i = 0; i < JourneyManager.Scenes.Length; i++)
            {
                EditorSceneManager.OpenScene($"{Dir}/{JourneyManager.Scenes[i]}.unity");
                var a = InScene<SceneAnchor>()[0];
                Assert.AreEqual(i == 2, a.allowFlight, $"{JourneyManager.Scenes[i]}: vuelo");
            }
        }

        [TestCase("S2_Pradera")]
        [TestCase("S3_Colina")]
        [TestCase("S6_Playa")]
        public void LosTerrenosTienenCapasYSuperficies(string scene)
        {
            EditorSceneManager.OpenScene($"{Dir}/{scene}.unity");
            var t = InScene<Terrain>();
            Assert.AreEqual(1, t.Length);
            Assert.GreaterOrEqual(t[0].terrainData.terrainLayers.Length, 2, "capas pintadas");
            Assert.IsNotNull(t[0].GetComponent<TerrainSurfaces>(), "pasos sobre el terreno");
        }

        [Test]
        public void BootTieneTodoLoQueViveElViaje()
        {
            EditorSceneManager.OpenScene($"{Dir}/Boot.unity");
            Assert.AreEqual(1, InScene<GameFlow>().Length);
            Assert.AreEqual(1, InScene<JourneyManager>().Length);
            Assert.AreEqual(1, InScene<ScoreSystem>().Length);
            Assert.AreEqual(1, InScene<CinematicDirector>().Length);
            Assert.AreEqual(1, InScene<TimeOfDay>().Length);
            var rig = InScene<PlayerRig>().Single();
            var anim = rig.GetComponentInChildren<Animator>();
            Assert.IsTrue(anim.avatar != null && anim.avatar.isHuman, "sonador Humanoid");
            Assert.IsNotNull(anim.runtimeAnimatorController, "Animator con controller");
            var modes = InScene<CameraModeController>().Single();
            Assert.AreEqual(3, modes.cine.Count(c => c != null), "tres camaras de cine");
            var steps = rig.GetComponent<FootstepSystem>();
            var surfaces = (SurfaceType[])System.Enum.GetValues(typeof(SurfaceType));
            foreach (var s in surfaces) Assert.IsTrue(steps.banks.Any(b => b && b.surface == s), $"banco de pasos para {s}");
        }

        [Test]
        public void LasEscenasEstanEnBuildEnOrden()
        {
            var names = EditorBuildSettings.scenes.Where(s => s.enabled).Select(s => System.IO.Path.GetFileNameWithoutExtension(s.path)).ToArray();
            CollectionAssert.AreEqual(new[] { "Boot" }.Concat(JourneyManager.Scenes).ToArray(), names);
        }
    }
}
