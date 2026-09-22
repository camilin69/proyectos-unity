using Esneider.Core;
using Esneider.Core.Persistence;
using Esneider.World;
using NUnit.Framework;
using UnityEngine;

namespace Esneider.Tests
{
    public class HingedCabinetTests
    {
        GameObject _root,_block;
        HingedCabinet Make()
        {
            _root=new GameObject("CabinetTest");_root.transform.position=Vector3.up*1000;
            var leaf=new GameObject("Leaf");leaf.transform.SetParent(_root.transform,false);
            var box=leaf.AddComponent<BoxCollider>();box.center=new Vector3(.25f,.5f,0);box.size=new Vector3(.5f,1,.03f);
            var cabinet=_root.AddComponent<HingedCabinet>();cabinet.leaves=new[]{leaf.transform};cabinet.openAngles=new[]{108f};return cabinet;
        }
        [TearDown] public void Cleanup(){if(_root)Object.DestroyImmediate(_root);if(_block)Object.DestroyImmediate(_block);}
        [Test] public void PausedAdvanceDoesNotMoveAndOpeningCommitsOnlyAtEnd()
        {
            var c=Make();c.Interact(null);c.Advance(0);
            Assert.That(c.leaves[0].localEulerAngles.y,Is.EqualTo(0));Assert.That(c.isOpen,Is.False);
            c.Advance(.4f);Assert.That(c.isOpen,Is.False);Assert.That(c.IsMoving,Is.True);
            c.Advance(2);Assert.That(c.isOpen,Is.True);Assert.That(c.IsMoving,Is.False);
            Assert.That(Quaternion.Angle(c.leaves[0].localRotation,Quaternion.Euler(0,108,0)),Is.LessThan(.001f));
        }
        [Test] public void ObstacleStopsLeafAndRemovalAllowsRetry()
        {
            var c=Make();_block=GameObject.CreatePrimitive(PrimitiveType.Cube);_block.layer=GameLayers.DynamicProp;
            _block.transform.position=new Vector3(.25f,1000.5f,-.20f);_block.transform.localScale=new Vector3(.12f,.4f,.12f);
            Physics.SyncTransforms();c.Interact(null);c.Advance(3);
            Assert.That(c.isOpen,Is.False);Assert.That(c.IsMoving,Is.False);Assert.That(c.Prompt,Is.EqualTo("Despeja la puerta"));
            _block.transform.position=Vector3.one*2000;Physics.SyncTransforms();c.Interact(null);c.Advance(3);
            Assert.That(c.isOpen,Is.True);
        }
        [Test] public void PersistentDoorStateHydratesBothClosedAndOpenWithoutAnimation()
        {
            var c=Make();var p=_root.AddComponent<PersistentEntity>();p.kind=EntityKind.Door;
            p.guid=System.Guid.NewGuid().ToString();p.regionId="CABINET_TEST";p.EnsureRegistered();
            p.Hydrate(new EntityState{stateVersion=1,isOpen=true});
            Assert.That(c.isOpen,Is.True);Assert.That(c.IsMoving,Is.False);
            p.Hydrate(new EntityState{stateVersion=2,isOpen=false});Assert.That(c.isOpen,Is.False);
            c.Interact(null);c.Advance(3);
            Assert.That(WorldStateRegistry.Session.GetOrCreate(p.guid,"",p.regionId,EntityKind.Door).isOpen,Is.True);
        }
    }
}
