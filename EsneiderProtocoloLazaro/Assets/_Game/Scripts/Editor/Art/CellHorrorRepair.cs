using System;
using System.Collections.Generic;
using System.Linq;
using Esneider.Core;
using Esneider.World;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Esneider.EditorTools
{
    public static class CellHorrorRepair
    {
        const string Dir = "Assets/_Game/Art/CellInjuries";
        static void EnsureFolder() { if (!AssetDatabase.IsValidFolder(Dir)) AssetDatabase.CreateFolder("Assets/_Game/Art", "CellInjuries"); }
        static Material Material(string name, Color color, float smooth)
        {
            string path=Dir+"/"+name+".mat"; var m=AssetDatabase.LoadAssetAtPath<Material>(path);
            if (!m) { m=new Material(Shader.Find("Universal Render Pipeline/Lit")); AssetDatabase.CreateAsset(m,path); }
            m.SetColor("_BaseColor",color); m.SetFloat("_Smoothness",smooth); EditorUtility.SetDirty(m); return m;
        }
        static float Injury(Vector3 p)
        {
            float Ellipse(float x,float y,float rx,float ry) => Mathf.Pow((p.x-x)/rx,2)+Mathf.Pow((p.y-y)/ry,2);
            return Mathf.Min(Ellipse(-.075f,1.23f,.095f,.18f),Mathf.Min(Ellipse(.11f,.58f,.064f,.18f),Ellipse(.055f,1.6f,.052f,.058f)));
        }
        static void AddWounds(Component subject, Material blood, Material tissue)
        {
            if(subject.transform.Find("Injuries_EX51"))return;
            var marker=new GameObject("Injuries_EX51"); marker.transform.SetParent(subject.transform,false);
            foreach(var skin in subject.GetComponentsInChildren<SkinnedMeshRenderer>().ToArray())
            {
                if(!skin.name.Contains("Skin")&&!skin.name.Contains("Cloth"))continue;
                var source=skin.sharedMesh; var vertices=source.vertices; var normals=source.normals;
                for(int layer=0;layer<2;layer++)
                {
                    string key=source.name.Replace("/","_")+"_"+layer;
                    string path=Dir+"/"+key+".asset";var mesh=AssetDatabase.LoadAssetAtPath<Mesh>(path);
                    if(!mesh)
                    {
                        var triangles=new List<int>(); var original=source.triangles;
                        for(int i=0;i<original.Length;i+=3)
                        {
                            int a=original[i],b=original[i+1],c=original[i+2];var p=(vertices[a]+vertices[b]+vertices[c])/3f;
                            var normal=(normals[a]+normals[b]+normals[c]).normalized;
                            float ragged=1f+.18f*Mathf.Sin(p.y*125+p.x*73);
                            if(Mathf.Abs(normal.z)<.45f || Injury(p)>(layer==0?1f:.25f)*ragged)continue;
                            triangles.Add(a);triangles.Add(b);triangles.Add(c);
                        }
                        if(triangles.Count==0)continue;
                        mesh=UnityEngine.Object.Instantiate(source);mesh.name=key;
                        mesh.vertices=vertices.Select((v,i)=>v+normals[i]*(layer==0?.0015f:.0028f)).ToArray();
                        mesh.subMeshCount=1;mesh.SetTriangles(triangles,0);mesh.RecalculateBounds();AssetDatabase.CreateAsset(mesh,path);
                    }
                    var go=new GameObject("Wound_"+layer+"_"+skin.name);go.transform.SetParent(skin.transform.parent,false);
                    go.transform.localPosition=skin.transform.localPosition;go.transform.localRotation=skin.transform.localRotation;go.transform.localScale=skin.transform.localScale;
                    go.layer=GameLayers.Corpse;
                    var overlay=go.AddComponent<SkinnedMeshRenderer>();overlay.sharedMesh=mesh;overlay.bones=skin.bones;overlay.rootBone=skin.rootBone;
                    overlay.localBounds=skin.localBounds;overlay.sharedMaterial=layer==0?blood:tissue;overlay.updateWhenOffscreen=false;
                    overlay.shadowCastingMode=UnityEngine.Rendering.ShadowCastingMode.Off;
                }
            }
        }
        static Mesh PoolMesh()
        {
            var mesh=AssetDatabase.LoadAssetAtPath<Mesh>(Dir+"/BloodPool.asset");if(mesh)return mesh;
            var vertices=new Vector3[49];var indices=new int[48*3];
            for(int i=0;i<48;i++)
            {
                float angle=i*Mathf.PI*2/48;float radius=.7f+.12f*Mathf.Sin(angle*7)+.06f*Mathf.Cos(angle*13);
                vertices[i+1]=new Vector3(Mathf.Cos(angle)*radius,0,Mathf.Sin(angle)*radius*.58f);
                indices[i*3]=0;indices[i*3+1]=(i+1)%48+1;indices[i*3+2]=i+1;
            }
            mesh=new Mesh{name="Irregular blood pool"};mesh.vertices=vertices;mesh.triangles=indices;mesh.RecalculateNormals();mesh.RecalculateBounds();AssetDatabase.CreateAsset(mesh,Dir+"/BloodPool.asset");return mesh;
        }
        public static string Apply(Transform root,string region)
        {
            if(region!="REG-S3")return "";EnsureFolder();
            var blood=Material("DriedBlood",new Color(.12f,.005f,.009f),.43f);
            var tissue=Material("ExposedTissue",new Color(.31f,.025f,.042f),.72f);
            string[] assemblies={SleepingAdultReview.Assembly,GraftedAdultReview.Assembly,DeterioratedAdultReview.Assembly};
            int count=0;
            foreach(var cage in root.GetComponentsInChildren<Transform>(true).Where(t=>t.name.EndsWith("_jaula")).ToArray())
            {
                var placeholder=cage.GetComponentsInChildren<Transform>(true).FirstOrDefault(t=>t.name.StartsWith("Sujeto_placeholder"));
                if(placeholder&&placeholder.gameObject.activeSelf)
                {
                    var prefab=AssetDatabase.LoadAssetAtPath<GameObject>(assemblies[count%3]);
                    if(!prefab)throw new InvalidOperationException("Missing adult assembly");
                    var go=(GameObject)PrefabUtility.InstantiatePrefab(prefab,cage);go.name="AdultSubject_EX51";go.transform.localPosition=new Vector3(0,0,.6f);
                    placeholder.gameObject.SetActive(false);count++;
                }
                foreach(var subject in cage.GetComponentsInChildren<PreservedSubject>())AddWounds(subject,blood,tissue);
                foreach(var subject in cage.GetComponentsInChildren<SleepingSubject>())AddWounds(subject,blood,tissue);
                if((cage.GetComponentInChildren<PreservedSubject>()||cage.GetComponentInChildren<SleepingSubject>())&&!cage.Find("BloodPool_EX51"))
                {
                    var go=new GameObject("BloodPool_EX51",typeof(MeshFilter),typeof(MeshRenderer));go.transform.SetParent(cage,false);go.transform.localPosition=new Vector3(.28f,.012f,.5f);
                    go.GetComponent<MeshFilter>().sharedMesh=PoolMesh();go.GetComponent<MeshRenderer>().sharedMaterial=blood;
                    go.GetComponent<MeshRenderer>().shadowCastingMode=UnityEngine.Rendering.ShadowCastingMode.Off;
                }
            }
            AssetDatabase.SaveAssets();return count+" adult subjects added, with skinned wounds and blood pools";
        }
        public static string ApplyExisting()
        {
            string path="Assets/_Game/Scenes/Regions/REG-S3.unity";var s=SceneManager.GetSceneByPath(path);bool opened=!s.IsValid()||!s.isLoaded;
            if(opened)s=EditorSceneManager.OpenScene(path,OpenSceneMode.Additive);
            if(s.isDirty)throw new InvalidOperationException("Unsaved REG-S3");
            var result=Apply(s.GetRootGameObjects().Single(g=>g.name=="REG-S3").transform,"REG-S3");EditorSceneManager.SaveScene(s);if(opened)EditorSceneManager.CloseScene(s,true);return result;
        }
    }
}
