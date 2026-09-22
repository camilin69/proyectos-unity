using System;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using Object=UnityEngine.Object;

namespace Esneider.EditorTools
{
    public static class MedicalPlacement
    {
        public static string Apply(Transform root)
        {
            var tank=AssetDatabase.LoadAssetAtPath<GameObject>(FurnitureReview.Prefab("OBJ-005_DepositoCriogenico"));
            var cart=AssetDatabase.LoadAssetAtPath<GameObject>(FurnitureReview.Prefab("OBJ-006_CarroSanitario"));
            if(!tank || !cart) return "EX15 waiting for medical prefabs";
            var all=root.GetComponentsInChildren<Transform>(true);
            var old=all.FirstOrDefault(t=>t.name=="M003_deposito" || t.name=="M003_EX15");
            var support=all.FirstOrDefault(t=>t.name=="Support_PICK-F01" || t.name=="Support_PICK-F01_EX15");
            var pickup=all.FirstOrDefault(t=>t.name=="Pickup_PICK-F01");
            if(!old || !support || !pickup) throw new InvalidOperationException("Missing S1 medical anchors");
            var floor=old.position.y-(old.name=="M003_deposito" ? 1.4f : 0);
            var cluster=new GameObject("M003_EX15").transform;cluster.SetParent(old.parent);
            cluster.position=new Vector3(old.position.x,floor,old.position.z);
            foreach(var legacy in all.Where(t=>t.name=="S1_CoolantTank" && t.parent && t.parent.name=="EX10_Visual" && Vector3.Distance(t.position,cluster.position)<.1f))
                Object.DestroyImmediate(legacy.gameObject);
            foreach(var offset in new[]{new Vector3(-.37f,0,-.37f),new Vector3(.37f,0,-.37f),new Vector3(0,0,.37f)})
            {
                var instance=(GameObject)PrefabUtility.InstantiatePrefab(tank,cluster);
                instance.transform.localPosition=offset;
            }
            Object.DestroyImmediate(old.gameObject);
            var placed=(GameObject)PrefabUtility.InstantiatePrefab(cart,support.parent);
            placed.name="Support_PICK-F01_EX15";
            placed.transform.position=new Vector3(support.position.x,floor,support.position.z);
            // PICK-F01 belongs beside the initial spawn, inside Esneider's chamber.
            var relocation=new Vector3(12f,placed.transform.position.y,12f)-placed.transform.position;
            placed.transform.position+=relocation;
            pickup.position+=relocation;
            Object.DestroyImmediate(support.gameObject);
            // Move the complete pickup, keeping its identity, trigger and real mesh together.
            var visible=pickup.GetComponentsInChildren<Renderer>().Where(r=>r.enabled).ToArray();
            if(visible.Length==0) throw new InvalidOperationException("Flashlight has no visible renderer");
            float bottom=visible.Min(r=>r.bounds.min.y);
            pickup.position+=Vector3.up*(floor+.799f-bottom);
            return "M003: three cryogenic vessels; PICK-F01: sanitary cart, flashlight bottom="+(floor+.799f);
        }
        public static string ApplyExisting()
        {
            var scene=SceneManager.GetSceneByPath("Assets/_Game/Scenes/Regions/REG-S1.unity");
            if(!scene.IsValid() || !scene.isLoaded) throw new InvalidOperationException("Open S1 first");
            if(scene.isDirty) throw new InvalidOperationException("Preserve unsaved S1 changes before placement");
            var root=scene.GetRootGameObjects().Single(g=>g.GetComponentsInChildren<Transform>(true).Any(t=>t.name=="Pickup_PICK-F01"));
            var result=Apply(root.transform);EditorSceneManager.SaveScene(scene);
            System.IO.File.WriteAllText("../SourceArt/_evidence/EX-15/placements.txt",result);return result;
        }
    }
}
