using System;
using System.IO;
using System.Linq;
using NUnit.Framework;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Esneider.Tests
{
    public class SubjectPlateTests
    {
        [Serializable] class Entry { public string cage,asset,serial; public float yaw; }
        [Serializable] class Registry { public Entry[] subjects; }
        [Test]
        public void FiveUniqueSubjectsHaveReadableScaleAndPhysicalCageSupport()
        {
            var entries=JsonUtility.FromJson<Registry>(File.ReadAllText("Assets/_Game/Data/LevelPlan/subject_plates_ex36.json")).subjects;
            Assert.AreEqual(5,entries.Length);Assert.AreEqual(5,entries.Select(e=>e.serial).Distinct().Count());
            const string path="Assets/_Game/Scenes/Regions/REG-S3.unity";var previous=SceneManager.GetActiveScene();var scene=SceneManager.GetSceneByPath(path);
            bool opened=!scene.IsValid()||!scene.isLoaded;if(opened)scene=EditorSceneManager.OpenScene(path,OpenSceneMode.Additive);
            try
            {
                var all=scene.GetRootGameObjects().SelectMany(r=>r.GetComponentsInChildren<Transform>(true)).ToArray();Physics.SyncTransforms();
                foreach(var e in entries)
                {
                    var cage=all.Single(t=>t.name==e.cage+"_jaula");var plate=cage.Find("SubjectPlate_EX36");Assert.IsNotNull(plate,e.cage);
                    Assert.That(plate.position.y-cage.position.y,Is.EqualTo(1.45f).Within(.001f));Assert.That(Quaternion.Angle(plate.rotation,Quaternion.Euler(0,e.yaw,0)),Is.LessThan(.01f));
                    Assert.AreEqual(0,plate.GetComponentsInChildren<Collider>().Length);Assert.AreEqual(0,plate.GetComponentsInChildren<AudioSource>().Length);
                    var mesh=plate.GetComponentInChildren<MeshFilter>().sharedMesh;Assert.AreEqual(316,mesh.triangles.Length/3);Assert.AreEqual(1,mesh.subMeshCount);
                    var material=plate.GetComponentInChildren<Renderer>().sharedMaterial;Assert.AreEqual(1024,material.GetTexture("_BaseMap").width);
                    // Source rear pads end at local Z=+0.010; they meet the selected bar.
                    foreach(float y in new[]{.022f,.078f})
                    {
                        var pad=plate.TransformPoint(new Vector3(0,y,.010f));var direction=plate.forward;
                        RaycastHit hit;Assert.IsTrue(Physics.Raycast(pad,direction,out hit,.005f,Esneider.Core.GameLayers.Mask(Esneider.Core.GameLayers.WorldStatic)),e.cage);
                        Assert.AreEqual("bar",hit.collider.name);Assert.IsTrue(hit.transform.IsChildOf(cage));Assert.That(hit.distance,Is.EqualTo(.0005f).Within(.0003f));
                    }
                }
            }
            finally{if(opened)EditorSceneManager.CloseScene(scene,true);if(previous.IsValid()&&previous.isLoaded)SceneManager.SetActiveScene(previous);}
        }
    }
}
