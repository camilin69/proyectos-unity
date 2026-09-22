using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;

namespace Esneider.EditorTools
{
    public static class IndustrialFanReview
    {
        public const string Asset="OBJ-079_VentiladorIndustrial";
        public static string Integrate()
        {
            var report=AssetIntegrator.Integrate(Asset,"Environment",false,"none");
            if(report.tris>4000||report.submeshes!=2||report.warnings.Count>0)throw new InvalidOperationException("Unexpected fan import");
            FurnitureReview.VerifyAxes(Asset);
            var root=PrefabUtility.LoadPrefabContents(FurnitureReview.Prefab(Asset));
            try
            {
                if(PrefabUtility.IsAnyPrefabInstanceRoot(root))PrefabUtility.UnpackPrefabInstance(root,PrefabUnpackMode.Completely,InteractionMode.AutomatedAction);
                var rotor=root.GetComponentsInChildren<MeshFilter>().Single(m=>m.name.Contains("-Rotor"));
                var pivot=new GameObject("RotorPivot");pivot.transform.SetParent(root.transform,false);pivot.transform.localPosition=new Vector3(0,.85f,0);
                rotor.transform.SetParent(pivot.transform,true);
                var fan=root.AddComponent<Esneider.World.IndustrialFan>();fan.rotor=pivot.transform;fan.rotorRenderer=rotor.GetComponent<Renderer>();
                fan.rotorRenderer.shadowCastingMode=UnityEngine.Rendering.ShadowCastingMode.Off;
                foreach(var t in root.GetComponentsInChildren<Transform>()){t.gameObject.layer=Esneider.Core.GameLayers.WorldStatic;t.gameObject.isStatic=false;}
                // Segment the fixed ring; the front safety grid stops passage without a damage volume.
                for(int i=0;i<12;i++)
                {
                    float angle=i*30*Mathf.Deg2Rad;
                    var go=new GameObject("HousingCollider");go.transform.SetParent(root.transform,false);go.transform.localPosition=new Vector3(.75f*Mathf.Cos(angle),.85f+.75f*Mathf.Sin(angle),0);go.transform.localRotation=Quaternion.Euler(0,0,i*30+90);
                    go.layer=Esneider.Core.GameLayers.WorldStatic;go.AddComponent<BoxCollider>().size=new Vector3(.40f,.10f,.33f);
                }
                foreach(float x in new[]{-.48f,-.32f,-.16f,0f,.16f,.32f,.48f})
                {
                    var box=root.AddComponent<BoxCollider>();box.center=new Vector3(x,.85f,-.192f);box.size=new Vector3(.009f,2*Mathf.Sqrt(.665f*.665f-x*x),.010f);
                }
                PrefabUtility.SaveAsPrefabAsset(root,FurnitureReview.Prefab(Asset));
            }
            finally{PrefabUtility.UnloadPrefabContents(root);}
            File.WriteAllText(Path.Combine(FurnitureReview.Evidence(Asset),"unity_import.json"),JsonUtility.ToJson(report,true));AssetDatabase.SaveAssets();return report.tris+" triangles, independent rotor";
        }
    }
}
