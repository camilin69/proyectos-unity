using Esneider.Core.Persistence;
using Esneider.World;
using NUnit.Framework;
using UnityEngine;

namespace Esneider.Tests
{
    public class RubbleExtractionTests
    {
        GameObject _root;
        RubbleExtraction _rubble;
        EntityState _state;
        string _guid;
        [SetUp] public void SetUp()
        {
            _root = new GameObject("Rubble test"); _root.transform.position = Vector3.up * 1000;
            var chips = new Transform[2];
            for (int i = 0; i < 2; i++) { chips[i] = new GameObject("chip" + i).transform; chips[i].SetParent(_root.transform, false); chips[i].localPosition = new Vector3(i * .3f, .45f, 1.28f); }
            _rubble = _root.AddComponent<RubbleExtraction>(); _rubble.chips = chips;
            _guid = System.Guid.NewGuid().ToString(); _rubble.pickupGuid = _guid;
            _state = WorldStateRegistry.Session.GetOrCreate(_guid, "test", "test", EntityKind.Pickup);
            _rubble.Hydrate();
        }
        [TearDown] public void TearDown() { Object.DestroyImmediate(_root); }
        void Take(bool taken) => WorldStateRegistry.Session.Apply(WorldEventKind.PickupTaken, _guid, s => s.taken = taken);

        [Test] public void ActualPickupEventReleasesOnlyOnceAndPauseFreezesMotion()
        {
            Take(false); Assert.IsFalse(_rubble.Released);
            Take(true); Assert.IsTrue(_rubble.Released);
            var start = _rubble.chips[0].localPosition; _rubble.Advance(0);
            Assert.That(_rubble.chips[0].localPosition, Is.EqualTo(start));
            _rubble.Advance(.2f);
            Assert.That(_rubble.chips[0].localPosition.y, Is.EqualTo(start.y).Within(.001f), "Must clear support before falling");
            _rubble.Advance(1); Assert.That(_rubble.ImpactsPlayed, Is.EqualTo(2));
            Take(true); _rubble.Advance(2); Assert.That(_rubble.ImpactsPlayed, Is.EqualTo(2));
            Assert.That(_rubble.chips[0].localPosition.y, Is.EqualTo(0));
        }
        [Test] public void RestoreSnapsBothStatesWithoutReplayingImpacts()
        {
            _state.taken = true; _rubble.Hydrate(); _rubble.Advance(2);
            Assert.That(_rubble.ImpactsPlayed, Is.Zero); Assert.That(_rubble.chips[1].localPosition.y, Is.Zero);
            _state.taken = false; _rubble.Hydrate();
            Assert.IsFalse(_rubble.Released); Assert.That(_rubble.chips[1].localPosition.y, Is.EqualTo(.45f));
            Take(true); _rubble.Advance(2); Assert.That(_rubble.ImpactsPlayed, Is.EqualTo(2));
        }
        [Test] public void UnrelatedPickupCannotMoveTheRubble()
        {
            WorldStateRegistry.Session.Apply(WorldEventKind.PickupTaken, System.Guid.NewGuid().ToString(), null);
            _rubble.Advance(2); Assert.IsFalse(_rubble.Released); Assert.That(_rubble.ImpactsPlayed, Is.Zero);
        }
    }
}
