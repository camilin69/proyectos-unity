using System.Linq;
using Esneider.Core;
using Esneider.Core.Persistence;
using Esneider.World;
using NUnit.Framework;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Esneider.Tests
{
    public class DistributionPanelTests
    {
        [Test] public void AuthorizationButtonIsReachableAndRestoresItsRealPermission()
        {
            const string path="Assets/_Game/Scenes/Regions/REG-S2.unity";
            var previous=SceneManager.GetActiveScene();var scene=SceneManager.GetSceneByPath(path);bool opened=!scene.IsValid()||!scene.isLoaded;
            if(opened)scene=EditorSceneManager.OpenScene(path,OpenSceneMode.Additive);
            var registry=WorldStateRegistry.Session;var saved=registry.Snapshot();var actor=new GameObject("Panel operator");ServicePanelVisual visual=null;
            try
            {
                visual=scene.GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<ServicePanelVisual>(true)).Single();
                var mech=visual.mechanism;Assert.AreEqual("MECH-PANEL-A",mech.mechanismId);Assert.AreEqual(ObjectiveService.PermisoA,mech.grantsFlag);Assert.AreEqual("REG-C2",mech.preloadRegion);
                Assert.That(mech.transform.position.y-visual.transform.position.y,Is.EqualTo(1.14f).Within(.001f));
                Physics.SyncTransforms();var target=mech.GetComponent<Collider>().bounds.center;var origin=target-visual.transform.forward*1.2f+Vector3.up*.42f;RaycastHit hit;
                Assert.IsTrue(Physics.Raycast(origin,(target-origin).normalized,out hit,1.5f,GameLayers.Mask(GameLayers.Interactable,GameLayers.WorldStatic),QueryTriggerInteraction.Collide));
                Assert.AreSame(mech,hit.collider.GetComponentInParent<IInteractable>(),"Control must be in front of the housing collider");
                Assert.IsNotNull(visual.GetComponent<UnityEngine.AI.NavMeshObstacle>());
                registry.Restore(new RegistrySnapshot());visual.SnapToState();var block=new MaterialPropertyBlock();visual.networkLamp.GetPropertyBlock(block);var before=block.GetColor("_BaseColor");
                // Avoid streaming into the editor; verify the preserved target above.
                string preload=mech.preloadRegion;mech.preloadRegion="";
                try{mech.Interact(actor);}finally{mech.preloadRegion=preload;}
                Assert.IsTrue(ObjectiveService.DoorAllowed("D14"));Assert.IsTrue(registry.HasObjective("O05"));
                visual.Advance(.1f);visual.networkLamp.GetPropertyBlock(block);Assert.AreNotEqual(before,block.GetColor("_BaseColor"));
                var snapshot=registry.Snapshot();long sequence=registry.Sequence;mech.Interact(actor);Assert.AreEqual(sequence,registry.Sequence);
                registry.Restore(new RegistrySnapshot());visual.SnapToState();Assert.IsFalse(mech.Used);
                registry.Restore(snapshot);visual.SnapToState();Assert.IsTrue(mech.Used);Assert.IsTrue(ObjectiveService.DoorAllowed("D14"));Assert.AreEqual(sequence,registry.Sequence);
            }
            finally
            {
                registry.Restore(saved);if(visual)visual.SnapToState();Object.DestroyImmediate(actor);
                if(opened)EditorSceneManager.CloseScene(scene,true);if(previous.IsValid()&&previous.isLoaded)SceneManager.SetActiveScene(previous);
            }
        }
    }
}
