using System.Linq;
using Esneider.Core;
using Esneider.Core.Data;
using Esneider.Core.Persistence;
using Esneider.World;
using NUnit.Framework;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Esneider.Tests
{
    public class ServicePanelTests
    {
        [Test] public void ClosedDoorProtectsControlAndNoteWhileOpenDoorExposesBoth()
        {
            const string path="Assets/_Game/Scenes/Regions/REG-S1.unity";
            var previous=SceneManager.GetActiveScene();var scene=SceneManager.GetSceneByPath(path);bool opened=!scene.IsValid()||!scene.isLoaded;
            if(opened)scene=EditorSceneManager.OpenScene(path,OpenSceneMode.Additive);
            HingedCabinet cabinet=null;PersistentEntity pe=null;string stable=null,guid=null;
            try
            {
                var panel=scene.GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<ServicePanelVisual>(true)).Single();
                cabinet=panel.GetComponent<HingedCabinet>();pe=panel.GetComponent<PersistentEntity>();stable=pe.stableId;guid=pe.guid;
                Assert.AreEqual(LevelPlan.StableGuid(stable).ToString(),guid);pe.stableId=pe.guid="";
                Assert.AreEqual("MECH-LEVER-S1",panel.mechanism.mechanismId);Assert.AreEqual(ObjectiveService.PermisoServicio,panel.mechanism.grantsFlag);
                var doc=panel.GetComponentInChildren<Pickup>(true);Assert.AreEqual("DOC-02",doc.documentId);Assert.AreEqual(LevelPlan.StableGuid("DOC-02").ToString(),doc.guid);Assert.AreEqual(1,doc.amount);
                cabinet.SnapOpen(false);Physics.SyncTransforms();
                var controlRay=new Ray(panel.mechanism.transform.position-panel.transform.forward*1.2f,panel.transform.forward);
                var noteRay=new Ray(doc.transform.position-panel.transform.forward*1.2f,panel.transform.forward);
                Assert.AreSame(cabinet,First(controlRay).GetComponentInParent<IInteractable>());Assert.AreSame(cabinet,First(noteRay).GetComponentInParent<IInteractable>());
                cabinet.Interact(null);cabinet.Advance(2);Assert.IsTrue(cabinet.isOpen,cabinet.Prompt);Physics.SyncTransforms();
                Assert.AreSame(panel.mechanism,First(controlRay).GetComponentInParent<IInteractable>());
                Assert.AreSame(doc,First(noteRay).GetComponentInParent<IInteractable>());
                Assert.IsTrue(panel.lever.GetComponentInChildren<MeshFilter>());Assert.IsTrue(cabinet.leaves[0].GetComponentInChildren<MeshFilter>());
            }
            finally
            {
                if(cabinet)cabinet.SnapOpen(false);if(pe){pe.stableId=stable;pe.guid=guid;}Physics.SyncTransforms();
                if(opened)EditorSceneManager.CloseScene(scene,true);if(previous.IsValid()&&previous.isLoaded)SceneManager.SetActiveScene(previous);
            }
        }
        static Collider First(Ray ray)
        {
            RaycastHit hit;Assert.IsTrue(Physics.Raycast(ray,out hit,2,GameLayers.Mask(GameLayers.WorldStatic,GameLayers.Interactable,GameLayers.DynamicProp),QueryTriggerInteraction.Collide));return hit.collider;
        }
        [Test] public void OperatesOnceAndVisualHydratesPermissionWithoutReplayingEvents()
        {
            var registry=WorldStateRegistry.Session;var saved=registry.Snapshot();registry.Restore(new RegistrySnapshot());
            var root=new GameObject("ServicePanel test");var who=new GameObject("Operator");
            try
            {
                var mechanism=root.AddComponent<Mechanism>();mechanism.mechanismId="MECH-LEVER-S1";mechanism.grantsFlag=ObjectiveService.PermisoServicio;
                var lever=new GameObject("Lever").transform;lever.SetParent(root.transform,false);
                var visual=root.AddComponent<ServicePanelVisual>();visual.mechanism=mechanism;visual.lever=lever;visual.SnapToState();
                mechanism.Interact(who);var sequence=registry.Sequence;Assert.IsTrue(ObjectiveService.DoorAllowed("D06"));
                mechanism.Interact(who);Assert.AreEqual(sequence,registry.Sequence,"Used panel must not emit another event");
                visual.Advance(0);Assert.AreEqual(0,visual.LeverAngle,"Paused pose must not advance");visual.Advance(.25f);Assert.That(visual.LeverAngle,Is.EqualTo(-27.5f).Within(.001f));
                var checkpoint=registry.Snapshot();registry.Restore(new RegistrySnapshot());visual.SnapToState();Assert.AreEqual(0,visual.LeverAngle);
                registry.Restore(checkpoint);visual.SnapToState();Assert.AreEqual(-55,visual.LeverAngle);Assert.AreEqual(sequence,registry.Sequence,"Hydration is presentation only");
            }
            finally{Object.DestroyImmediate(root);Object.DestroyImmediate(who);registry.Restore(saved);}
        }
    }
}
