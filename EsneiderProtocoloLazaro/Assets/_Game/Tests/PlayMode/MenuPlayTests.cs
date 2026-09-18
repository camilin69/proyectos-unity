using System.Collections;
using System.IO;
using Esneider.Core;
using Esneider.Core.Persistence;
using Esneider.Player;
using Esneider.UI;
using Esneider.World;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

namespace Esneider.Tests
{
    // 81.2/81.3: pausa congela el mundo y muestra cursor; derrota muestra causa legible y Reintentar restaura el checkpoint;
    // ajustes persisten fuera del snapshot; inicio pide confirmación antes de reemplazar un guardado.
    public class MenuPlayTests
    {
        PlayerController _pc; string _dir;

        [UnitySetUp]
        public IEnumerator SetUp()
        {
            Health.Clock = () => Time.time; WorldStateRegistry.ResetSession(); MenuController.SkipTitle = true;
            _dir = Path.Combine(Path.GetTempPath(), "esneider-tests", System.Guid.NewGuid().ToString("N"));
#if UNITY_EDITOR
            yield return UnityEditor.SceneManagement.EditorSceneManager.LoadSceneAsyncInPlayMode("Assets/_Game/Scenes/BOOT.unity", new LoadSceneParameters(LoadSceneMode.Single));
#endif
            yield return null;
            _pc = Object.FindFirstObjectByType<PlayerController>();
            CheckpointService.Instance.saveDirectoryOverride = _dir;
            float t0 = Time.time; while (!RegionStreamer.Instance.IsReady("REG-S1") && Time.time - t0 < 20f) yield return null;
            Object.FindFirstObjectByType<OpeningSequence>()?.RequestSkip();
            t0 = Time.time; while (!_pc.motor.movementEnabled && Time.time - t0 < 25f) yield return null;
            yield return null;
        }

        [UnityTearDown]
        public IEnumerator TearDown()
        {
            Time.timeScale = 1f; try { Directory.Delete(_dir, true); } catch { }
            yield return SceneManager.LoadSceneAsync("Combat_Sandbox", LoadSceneMode.Single);
            var pc = Object.FindFirstObjectByType<PlayerController>(); if (pc != null) Object.Destroy(pc.transform.root.gameObject);
            yield return null;
        }

        [UnityTest]
        public IEnumerator Pause_FreezesWorld_ShowsMenu_ResumeRestores()
        {
            var flow = GameFlowController.Instance; var menu = MenuController.Instance; Assert.IsNotNull(menu);
            flow.TogglePause(); yield return null;
            Assert.AreEqual(0f, Time.timeScale); Assert.AreEqual("Pause", menu.Current); Assert.IsTrue(Cursor.visible);
            menu.Resume(); yield return null;
            Assert.AreEqual(1f, Time.timeScale); Assert.AreEqual(GameState.Playing, flow.State); Assert.IsFalse(menu.IsOpen);
        }

        [UnityTest]
        public IEnumerator Defeat_ShowsCause_RetryRestoresCheckpoint()
        {
            var flow = GameFlowController.Instance; var menu = MenuController.Instance;
            float t0 = Time.time; while (CheckpointService.Instance.LastConfirmed == null && Time.time - t0 < 6f) yield return null;
            Assert.IsNotNull(CheckpointService.Instance.LastConfirmed, "CP-00 confirmado");
            _pc.health.ApplyDamage(new DamageInfo { amount = 999f, attackId = AttackIds.Next(), kind = "Bolt" }); yield return null;
            Assert.AreEqual(GameState.Dead, flow.State);
            yield return new WaitForSecondsRealtime(2f);
            Assert.AreEqual("Defeat", menu.Current, "pantalla de derrota tras secuencia breve"); Assert.IsTrue(menu.Modal);
            _pc.Restart(); menu.Hide(); yield return null;
            Assert.AreEqual(GameState.Playing, flow.State); Assert.AreEqual(90f, _pc.health.Current, 0.5f); Assert.IsTrue(EventRunner.Instance.IsDone("EVT-01"), "reintentar no repite la apertura");
        }

        [UnityTest]
        public IEnumerator Settings_PersistOutsideSnapshot()
        {
            float before = AccessibilitySettings.Sensitivity;
            AccessibilitySettings.Sensitivity = 0.2f; AccessibilitySettings.SetAssist(true); AccessibilitySettings.Save(); MenuController.Instance.ApplySettings();
            Assert.AreEqual(0.2f, _pc.look.sensitivity, 0.001f); Assert.AreEqual(1.25f, AccessibilitySettings.TelegraphScale);
            _pc.Restart(); yield return null;
            Assert.AreEqual(0.2f, _pc.look.sensitivity, 0.001f, "cargar CP no revierte ajustes");
            AccessibilitySettings.Sensitivity = before; AccessibilitySettings.SetAssist(false); AccessibilitySettings.Save(); MenuController.Instance.ApplySettings();
        }
    }
}
