using System;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEditor;

namespace Esneider.EditorTools
{
    public static class CabinetReview
    {
        [Serializable] public class Leaf { public string name; public float[] pivot_blender,center_local,size; public float open_degrees_blender; }
        [Serializable] public class Geometry { public int triangles; public FurnitureReview.CollisionBox[] collision_boxes_blender; public Leaf[] doors; }
        public static string Integrate(string asset)
        {
            var folder=FurnitureReview.Evidence(asset);
            var geometry=JsonUtility.FromJson<Geometry>(File.ReadAllText(Path.Combine(folder,"geometry.json")));
            var report=AssetIntegrator.Integrate(asset,"Environment",false,"none");
            if(report.tris!=geometry.triangles || report.submeshes!=3 || report.warnings.Count>0) throw new InvalidOperationException("Cabinet topology/material import mismatch");
            var axis=FurnitureReview.VerifyAxes(asset);
            var root=PrefabUtility.LoadPrefabContents(FurnitureReview.Prefab(asset));
            try
            {
                foreach(var box in geometry.collision_boxes_blender)
                {
                    var c=root.AddComponent<BoxCollider>();c.center=new Vector3(axis.signX*box.center[0],box.center[2],axis.signZ*box.center[1]);c.size=new Vector3(box.size[0],box.size[2],box.size[1]);
                }
                foreach(var leaf in geometry.doors)
                {
                    string suffix=leaf.name.Contains("DoorL") ? "DoorL" : "DoorR";
                    var t=root.GetComponentsInChildren<Transform>().Single(x=>x.name.Contains(suffix));
                    Vector3 pivot=new Vector3(axis.signX*leaf.pivot_blender[0],leaf.pivot_blender[2],axis.signZ*leaf.pivot_blender[1]);
                    if(Vector3.Distance(t.position,pivot)>.001f)throw new InvalidOperationException("Imported hinge differs from source");
                    var c=t.gameObject.AddComponent<BoxCollider>();
                    // Define the closed leaf box in model coordinates, then transform to the imported pivot.
                    var center=pivot+new Vector3(axis.signX*leaf.center_local[0],leaf.center_local[2],axis.signZ*leaf.center_local[1]);
                    c.center=t.InverseTransformPoint(center);c.size=new Vector3(leaf.size[0],leaf.size[2],leaf.size[1]);
                }
                foreach(var t in root.GetComponentsInChildren<Transform>())t.gameObject.layer=Esneider.Core.GameLayers.WorldStatic;
                var tag=root.AddComponent<Esneider.World.SurfaceTag>();tag.surfaceId="SUR-MET";
                var cabinet=root.AddComponent<Esneider.World.HingedCabinet>();
                cabinet.leaves=new[]{root.GetComponentsInChildren<Transform>().Single(t=>t.name.Contains("DoorL")),root.GetComponentsInChildren<Transform>().Single(t=>t.name.Contains("DoorR"))};
                var persistent=root.AddComponent<Esneider.World.PersistentEntity>();persistent.kind=Esneider.Core.Persistence.EntityKind.Door;
                PrefabUtility.SaveAsPrefabAsset(root,FurnitureReview.Prefab(asset));
            }
            finally {PrefabUtility.UnloadPrefabContents(root);}
            File.WriteAllText(Path.Combine(folder,"unity_import.json"),JsonUtility.ToJson(report,true));return asset+": "+report.tris+" tris, two verified hinge pivots";
        }
        public static string Capture(string asset,bool opened)
        {
            return FurnitureReview.Capture(asset,null,Path.Combine(FurnitureReview.Evidence(asset),opened ? "open" : "closed"),go=>{
                if(!opened)return;
                foreach(var t in go.GetComponentsInChildren<Transform>())
                    if(t.name.Contains("DoorL") || t.name.Contains("DoorR"))t.localRotation=Quaternion.Euler(0,t.name.Contains("DoorL") ? 108 : -108,0)*t.localRotation;
            });
        }
    }
}
