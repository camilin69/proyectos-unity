using System.Collections;
using Esneider.Audio;
using Esneider.Core;
using Esneider.Core.Persistence;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;

namespace Esneider.Tests
{
    public class ProgressionMusicPlayTests
    {
        [UnityTest] public IEnumerator DoorProgressCrescendosAndBossDeathStopsBothTracksIncludingAfterRestore()
        {
            var saved = WorldStateRegistry.Session.Snapshot(); WorldStateRegistry.ResetSession();
            var go = new GameObject("MusicTest");
            try
            {
                go.AddComponent<AudioService>(); yield return null;
                var music = go.GetComponent<ProgressionMusic>();
                Assert.AreEqual(-2, ProgressionMusic.ResolveStage("REG-S1"));
                WorldStateRegistry.Session.SetFlag("OPENING_DONE"); music.RefreshNow();
                Assert.AreEqual(0, music.Stage);
                foreach (var id in new[] { "D06", "D14", "D22" })
                {
                    int previous = music.Stage; ProgressionMusic.DoorOpened(id); music.RefreshNow();
                    Assert.AreEqual(previous + 1, music.Stage);
                    Assert.AreEqual("Tension" + music.Stage, music.CurrentTrackName, "Each difficulty gate must select its own denser score");
                    yield return new WaitForSeconds(.15f);
                    Assert.Greater(music.CurrentVolume, 0f, "The crescendo track must be audible after the gate opens");
                    ProgressionMusic.DoorOpened(id); music.RefreshNow(); Assert.AreEqual(previous + 1, music.Stage, "Reopening does not stack intensity");
                }
                var beforeBoss = WorldStateRegistry.Session.Snapshot();
                WorldStateRegistry.Session.MarkEventDone("EVT-21"); music.RefreshNow(); Assert.AreEqual(4, music.Stage);
                Assert.IsNotNull(Resources.Load<AudioClip>("Music/Tension4"));
                ObjectiveService.Grant(ObjectiveService.BossDefeated); music.RefreshNow();
                Assert.AreEqual(-1, music.Stage); Assert.IsTrue(music.IsSilent);
                Assert.AreEqual(-1, ProgressionMusic.ResolveStage("REG-S1"), "Backtracking after victory cannot restart the score");
                WorldStateRegistry.Session.Restore(beforeBoss); music.RefreshNow(); Assert.AreEqual(3, music.Stage);
                WorldStateRegistry.ResetSession(); music.RefreshNow(); Assert.AreEqual(-2, music.Stage); Assert.IsTrue(music.IsSilent);
            }
            finally { Object.Destroy(go); WorldStateRegistry.Session.Restore(saved); }
        }
    }
}
