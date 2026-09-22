using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;
using Object=UnityEngine.Object;

namespace Esneider.EditorTools
{
    public static class RobotPlatformReview
    {
        public const string Asset="OBJ-021_PlataformaRobot";
        public const string Assembly="Assets/_Game/Prefabs/Environment/RobotMaintenance_EX38.prefab";
        public static string Integrate()
        {
            var result=FurnitureReview.Integrate(Asset);
            var root=new GameObject("RobotMaintenance_EX38");
            try
            {
                PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(FurnitureReview.Prefab(Asset)),root.transform);
                // Import only the visual source, never the enemy prefab or its gameplay components.
                var robot=(GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(AssetIntegrator.ModelsDir+"/BOT-02_Custodio.fbx"),root.transform);
                robot.name="InertCustodio";robot.transform.localRotation=Quaternion.LookRotation(Vector3.up,Vector3.right);robot.transform.localScale=Vector3.one;
                var material=AssetDatabase.LoadAssetAtPath<Material>("Assets/_Game/Art/Materials/Assets/M_BOT-02_Custodio.mat");
                if(!material)throw new InvalidOperationException("Missing Custodio material");
                var renderers=robot.GetComponentsInChildren<Renderer>();var bounds=renderers[0].bounds;foreach(var r in renderers){bounds.Encapsulate(r.bounds);r.sharedMaterials=Enumerable.Repeat(material,r.sharedMaterials.Length).ToArray();}
                robot.transform.localPosition=new Vector3(-bounds.center.x,.280f-bounds.min.y,-bounds.center.z);
                if(bounds.size.x>2.60f||bounds.size.z>1.00f)throw new InvalidOperationException("Robot does not fit between retaining jaws at original scale");
                if(robot.GetComponentsInChildren<MonoBehaviour>().Length>0||robot.GetComponentsInChildren<Collider>().Length>0)throw new InvalidOperationException("Visual source includes gameplay");
                PrefabUtility.RecordPrefabInstancePropertyModifications(robot.transform);PrefabUtility.RecordPrefabInstancePropertyModifications(robot);
                foreach(var r in renderers)PrefabUtility.RecordPrefabInstancePropertyModifications(r);
                foreach(var t in root.GetComponentsInChildren<Transform>()) {t.gameObject.layer=Esneider.Core.GameLayers.WorldStatic;t.gameObject.isStatic=true;}
                PrefabUtility.SaveAsPrefabAsset(root,Assembly);
                File.WriteAllText(Path.Combine(FurnitureReview.Evidence(Asset),"robot_fit.txt"),"Original-scale robot rotated bounds: "+bounds.size+"; support baseline 0.280 m; no AI or body collider.\nExact individual pad contact and cable coupling remain pending.");
            }
            finally{Object.DestroyImmediate(root);}
            return result;
        }
    }
}
