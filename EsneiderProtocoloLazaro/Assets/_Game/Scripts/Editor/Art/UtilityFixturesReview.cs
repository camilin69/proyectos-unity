using System;
using System.Linq;
using System.Collections.Generic;
using Esneider.Core;
using Esneider.World;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using Object=UnityEngine.Object;

namespace Esneider.EditorTools
{
    public static class UtilityFixturesReview
    {
        public const string Luminaire="OBJ-066_LuminariaTecnica",Speaker="OBJ-065_AltavozMegafonia",Emergency="OBJ-067_LamparaEmergencia";
        public static string Integrate(string asset)
        {
            var report=FurnitureReview.Integrate(asset);
            if(asset!=Luminaire&&asset!=Emergency)return report;
            string path=AssetIntegrator.TexDir+"/"+asset+"_Emission.png";
            var importer=AssetImporter.GetAtPath(path) as TextureImporter;if(!importer)throw new InvalidOperationException("Missing emission mask");
            importer.sRGBTexture=false;importer.textureType=TextureImporterType.Default;importer.SaveAndReimport();
            var root=PrefabUtility.LoadPrefabContents(FurnitureReview.Prefab(asset));
            try
            {
                var renderer=root.GetComponentInChildren<Renderer>();var material=renderer.sharedMaterial;
                material.EnableKeyword("_EMISSION");material.SetTexture("_EmissionMap",AssetDatabase.LoadAssetAtPath<Texture2D>(path));material.SetColor("_EmissionColor",asset==Emergency?new Color(1,.38f,.045f):Color.white);
                EditorUtility.SetDirty(material);
                var glow=root.AddComponent<FixtureEmission>();glow.surface=renderer;glow.previewColor=asset==Emergency?new Color(1,.38f,.045f):Color.white;glow.Refresh();
                PrefabUtility.SaveAsPrefabAsset(root,FurnitureReview.Prefab(asset));
            }
            finally{PrefabUtility.UnloadPrefabContents(root);}
            AssetDatabase.SaveAssets();return report+"; masked emission";
        }
        public static string Apply(Transform root,string region)
        {
            int count=0;var skipped=new List<string>();
            var prefab=AssetDatabase.LoadAssetAtPath<GameObject>(FurnitureReview.Prefab(Luminaire));
            if(prefab)foreach(var light in root.GetComponentsInChildren<Light>(true).ToArray())
            {
                if(!light.enabled||!(light.name.StartsWith("Lum_")||light.name.StartsWith("Circ_")))continue;
                var existing=light.GetComponentInParent<FixtureEmission>();
                if(existing){if(existing.source!=light){existing.source=light;PrefabUtility.RecordPrefabInstancePropertyModifications(existing);count++;}continue;}
                RaycastHit hit;if(!Physics.Raycast(light.transform.position,Vector3.up,out hit,1,1<<GameLayers.WorldStatic)||hit.normal.y>-.9f){skipped.Add(light.name);continue;}
                bool supported=true;
                foreach(float x in new[]{-.25f,.25f})foreach(float z in new[]{-.045f,.045f})
                {RaycastHit anchor;if(!Physics.Raycast(light.transform.position+new Vector3(x,0,z),Vector3.up,out anchor,1,1<<GameLayers.WorldStatic)||Mathf.Abs(anchor.point.y-hit.point.y)>.015f)supported=false;}
                if(!supported){skipped.Add(light.name);continue;}
                var go=(GameObject)PrefabUtility.InstantiatePrefab(prefab,light.transform.parent);go.name="Fixture_EX31_"+light.name;
                go.transform.position=new Vector3(light.transform.position.x,hit.point.y-.1505f,light.transform.position.z);
                light.transform.SetParent(go.transform,true);light.transform.localPosition=new Vector3(0,-.01f,0);
                var glow=go.GetComponent<FixtureEmission>();glow.source=light;PrefabUtility.RecordPrefabInstancePropertyModifications(glow);count++;
            }
            if(region=="REG-C1")
            {
                var speaker=root.GetComponentInChildren<AnnouncementSpeaker>(true);
                var model=AssetDatabase.LoadAssetAtPath<GameObject>(FurnitureReview.Prefab(Speaker));
                if(speaker&&model&&!speaker.transform.Find("SpeakerVisual_EX31"))
                {
                    RaycastHit wall;if(!Physics.Raycast(speaker.transform.position,Vector3.back,out wall,1,1<<GameLayers.WorldStatic))throw new InvalidOperationException("Speaker wall missing");
                    speaker.transform.localScale=Vector3.one;speaker.transform.rotation=Quaternion.Euler(0,180,0);
                    speaker.transform.position=new Vector3(speaker.transform.position.x,speaker.transform.position.y,wall.point.z+.1505f);
                    speaker.GetComponent<MeshRenderer>().enabled=false;foreach(var collider in speaker.GetComponents<Collider>())Object.DestroyImmediate(collider);
                    var visual=(GameObject)PrefabUtility.InstantiatePrefab(model,speaker.transform);visual.name="SpeakerVisual_EX31";visual.transform.localPosition=Vector3.down*.125f;count++;
                }
            }
            return count>0?region+": "+count+" fixtures; no ceiling at "+string.Join(",",skipped):"";
        }
        public static string ApplyExisting()
        {
            var previous=SceneManager.GetActiveScene();var results=new List<string>();
            foreach(string region in new[]{"REG-S1","REG-S2","REG-S3","REG-S4","REG-C1","REG-C2","REG-C3"})
            {
                string path="Assets/_Game/Scenes/Regions/"+region+".unity";var scene=SceneManager.GetSceneByPath(path);bool opened=!scene.IsValid()||!scene.isLoaded;
                if(opened)scene=EditorSceneManager.OpenScene(path,OpenSceneMode.Additive);else if(scene.isDirty)throw new InvalidOperationException("Unsaved "+region);
                try{var result=Apply(scene.GetRootGameObjects().Single(g=>g.name==region).transform,region);if(result!=""){EditorSceneManager.SaveScene(scene);results.Add(result);}}
                finally{if(opened)EditorSceneManager.CloseScene(scene,true);}
            }
            if(previous.IsValid()&&previous.isLoaded)SceneManager.SetActiveScene(previous);return string.Join("\n",results);
        }
    }
}
