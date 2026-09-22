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
        public IEnumerator NewGameReloadsInitialWorldInsteadOfResumingProgress()
        {
            _pc.inventory.hasPistol=true;_pc.inventory.pistolMag=7;
            var reg=WorldStateRegistry.Session;reg.SetFlag("TEST_OLD_PROGRESS");reg.MarkDocumentRead("DOC-09");reg.CompleteObjective("O09");
            Assert.IsTrue(CheckpointService.Instance.CommitNow("CP-OLD",_pc,"REG-S1",false,0,0,0));
            var previousPlayer=_pc;
            var menu=MenuController.Instance;menu.ShowTitle();yield return null;
            var newButton=System.Linq.Enumerable.Single(menu.GetComponentsInChildren<UnityEngine.UI.Button>(),b=>b.GetComponentInChildren<UnityEngine.UI.Text>().text=="Nueva partida");
            newButton.onClick.Invoke();Assert.AreEqual("ConfirmNew",menu.Current);
            var confirm=System.Linq.Enumerable.Single(menu.GetComponentsInChildren<UnityEngine.UI.Button>(),b=>b.GetComponentInChildren<UnityEngine.UI.Text>().text=="Sí, reemplazar y empezar");
            confirm.onClick.Invoke();
            float until=Time.realtimeSinceStartup+25f;
            while(Time.realtimeSinceStartup<until)
            {
                var current=Object.FindFirstObjectByType<PlayerController>();
                if(current && current!=previousPlayer && RegionStreamer.Instance && RegionStreamer.Instance.IsReady("REG-S1")){_pc=current;break;}
                yield return null;
            }
            Assert.IsTrue(previousPlayer==null,"The old player and loaded world must be destroyed");
            Assert.IsNotNull(_pc);Assert.IsFalse(_pc.inventory.hasPistol);Assert.AreEqual(0,_pc.inventory.documents.Count);
            Assert.IsFalse(WorldStateRegistry.Session.HasFlag("TEST_OLD_PROGRESS"));Assert.IsFalse(WorldStateRegistry.Session.HasObjective("O09"));
            Assert.IsFalse(WorldStateRegistry.Session.IsDocumentRead("DOC-09"));
            Assert.AreEqual("REG-S1",RegionStreamer.Instance.CurrentRegion);
            Assert.AreEqual(_dir,CheckpointService.Instance.saveDirectoryOverride);
            Assert.IsFalse(CheckpointService.Instance.Store.HasAnyCandidate,"The old save must be replaced, not continued");
            Assert.IsFalse(MenuController.Instance.IsOpen,"New game must start rather than show the title again");
            var opening=Object.FindFirstObjectByType<OpeningSequence>();Assert.IsNotNull(opening);
            opening.RequestSkip();
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
        public IEnumerator CapturedPlayerGetsEscapePromptInsteadOfDefeatMenu()
        {
            MenuController.Instance.Resume(); yield return null;
            _pc.Capture(null); yield return new WaitForSeconds(3f);
            Assert.IsTrue(_pc.IsCaptured); Assert.IsFalse(MenuController.Instance.IsOpen);
            Assert.AreEqual(GameState.Playing,GameFlowController.Instance.State);
            StringAssert.Contains("Presiona F varias veces para escapar",_pc.Prompt);
            for(int i=0;i<_pc.captureEscapePresses;i++) { _pc.input.FlashlightPressed=true; yield return null; }
            Assert.IsFalse(_pc.IsCaptured); Assert.IsFalse(MenuController.Instance.IsOpen);
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
