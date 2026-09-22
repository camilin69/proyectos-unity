using System;
using System.IO;
using System.Linq;
using Esneider.Core.Data;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using Object = UnityEngine.Object;

namespace Esneider.EditorTools
{
    /// <summary>EX-10: repeatable cosmetic dressing. Existing colliders, IDs and navigation stay authoritative.</summary>
    public static class S1VisualPass
    {
        const string Dir = "Assets/_Game/Art/S1";
        const string Model = "Assets/_Game/Art/Models/S1_ServiceKit.fbx";
        const string ScenePath = "Assets/_Game/Scenes/Regions/REG-S1.unity";
        static Material ceramic, steel, gasket, diffuser, amber, floor, wall, trim;
        static GameObject kit;

        [MenuItem("Esneider/Art/Apply S1 visual pass")]
        public static void ApplyCurrent()
        {
            var scene = UnityEngine.SceneManagement.SceneManager.GetActiveScene();
            if (scene.path != ScenePath) throw new InvalidOperationException("Open REG-S1 before applying the visual pass.");
            Setup();
            var region = scene.GetRootGameObjects().First(x => x.name == "REG-S1").transform;
            Apply(region);
            EditorSceneManager.MarkSceneDirty(scene);
            EditorSceneManager.SaveScene(scene);
            AssetDatabase.SaveAssets();
        }

        public static void Apply(Transform region)
        {
            if (region.name != "REG-S1") return;
            Setup();
            var old = region.Find("EX10_Visual");
            if (old != null) Object.DestroyImmediate(old.gameObject);
            var root = new GameObject("EX10_Visual").transform; root.SetParent(region,false);
            var plan = LevelPlan.FromJson(File.ReadAllText(LevelPlan.DefaultAssetPath));
            foreach (var r in plan.rooms.Where(x => x.floor == "P01"))
            {
                float y = plan.Floor(r.floor).origin.y;
                var room = new GameObject(r.id).transform; room.SetParent(root,false);
                room.position = new Vector3(r.x,y,r.z);
                // A separate UV-mapped floor skin uses physical metres, avoiding stretched cube UVs.
                Floor(room,r.w,r.d);
                for (float x=1; x<r.w; x+=2)
                {
                    Place(room,"S1_WallPanel",new Vector3(x,.05f,.15f),180);
                    Place(room,"S1_WallPanel",new Vector3(x,.05f,r.d-.15f),0);
                }
                for (float z=1; z<r.d; z+=2)
                {
                    foreach (int side in new[]{0,1})
                    {
                        float wx=r.x+(side==0 ? 0:r.w), wz=r.z+z;
                        bool doorway=plan.doors.Any(d=>d.floor==r.floor && Mathf.Abs(d.x-wx)<.3f && Mathf.Abs(d.z-wz)<d.width*.5f+1f);
                    if (!doorway) Place(room,"S1_WallPanel",new Vector3(side==0?.15f:r.w-.15f,.05f,z),side==0?270:90);
                    }
                }
                for(float z=2;z<r.d;z+=4)
                {
                    Place(room,"S1_PipePair",new Vector3(.32f,1.15f,z),90);
                    Box(room,"Ceiling rib",new Vector3(r.w*.5f,4.30f,z),new Vector3(r.w,.18f,.16f),steel);
                }
                for(float z=3;z<r.d;z+=6)
                {
                    Place(room,"S1_Luminaire",new Vector3(r.w*.32f,4.12f,z),0);
                    Place(room,"S1_Luminaire",new Vector3(r.w*.68f,4.12f,z),0);
                    Lamp(room,new Vector3(r.w*.32f,3.9f,z),new Color(.56f,.82f,.79f),2.6f,9);
                    Lamp(room,new Vector3(r.w*.68f,3.9f,z),new Color(.66f,.79f,.9f),2.0f,9);
                }
                // Long cable trunk under ceiling; service lines connect the repeated stations.
                Box(room,"Service trunk",new Vector3(.22f,3.4f,r.d*.5f),new Vector3(.25f,.24f,r.d-.4f),steel);
                Box(room,"Sector stripe",new Vector3(r.w*.5f,3.03f,.07f),new Vector3(r.w-.2f,.13f,.06f),trim);
                Box(room,"Sector stripe",new Vector3(r.w*.5f,3.03f,r.d-.07f),new Vector3(r.w-.2f,.13f,.06f),trim);
            }
            // Original room lights have no physical housing and flatten the new composition.
            foreach(var l in region.GetComponentsInChildren<Light>())
                if(!l.transform.IsChildOf(root) && l.name.StartsWith("Lum_S1-R0") && (l.name.Contains("R01")||l.name.Contains("R02")||l.name.Contains("R05")))
                    l.enabled=false;
            foreach(var f in plan.furniture.Where(f=>f.family=="crio" && f.space=="P01"))
            {
                Place(root,"S1_Manifold",new Vector3(f.x-1.6f,-24,f.z+.7f),180);
                // Clearly painted service footprint; thin strips do not add collision or obstruct pickups.
                foreach(float dx in new[]{-1.3f,1.3f}) Box(root,"Cryo safety line",new Vector3(f.x+dx,-23.98f,f.z),new Vector3(.06f,.014f,3.7f),amber);
                Label(root,"LAZARO / "+f.id,new Vector3(f.x,-23.965f,f.z-2.1f),Quaternion.Euler(90,0,0),.095f);
            }
            Label(root,"N E M E S I S\nPRESERVACION  /  B-4",new Vector3(8,-20.65f,2.18f),Quaternion.Euler(0,180,0),.38f);
            Label(root,"01   /   LAZARO",new Vector3(13.79f,-20.15f,9),Quaternion.Euler(0,90,0),.16f);
            Label(root,"05   /   ARCHIVO BIOLOGICO",new Vector3(20.21f,-20.15f,13),Quaternion.Euler(0,-90,0),.11f);
            // Highlight the first exit, using warm/cool contrast as a navigation cue.
            Lamp(root,new Vector3(13.2f,-21.5f,9),new Color(1,.52f,.19f),1.4f,5);
            var tank=region.GetComponentsInChildren<MeshRenderer>().FirstOrDefault(r=>r.name=="M003_deposito");
            if(tank!=null)
            {
                tank.enabled=false;
                Place(root,"S1_CoolantTank",new Vector3(tank.bounds.center.x,-24,tank.bounds.center.z),0);
            }
            foreach(var r in region.GetComponentsInChildren<MeshRenderer>())
            {
                if(r.transform.IsChildOf(root))continue;
                if(r.name=="Solid" || r.name=="Ceiling")r.sharedMaterial=wall;
                if(r.name.StartsWith("Lintel"))r.sharedMaterial=steel;
            }
            foreach(var r in root.GetComponentsInChildren<MeshRenderer>())
                GameObjectUtility.SetStaticEditorFlags(r.gameObject,StaticEditorFlags.BatchingStatic);
            // Recover the glass/metal separation lost by the single opaque atlas material.
            var glass=Mat("CryoGlass",new Color(.25f,.52f,.54f,.23f),.05f,.86f);
            glass.SetFloat("_Surface",1);glass.SetFloat("_SrcBlend",(float)BlendMode.SrcAlpha);
            glass.SetFloat("_DstBlend",(float)BlendMode.OneMinusSrcAlpha);glass.SetFloat("_ZWrite",0);
            glass.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");glass.renderQueue=3000;
            glass.SetOverrideTag("RenderType","Transparent");
            var frost=Mat("CryoFrost",new Color(.48f,.69f,.7f,.16f),0,.18f);
            frost.SetFloat("_Surface",1);frost.SetFloat("_SrcBlend",(float)BlendMode.SrcAlpha);
            frost.SetFloat("_DstBlend",(float)BlendMode.OneMinusSrcAlpha);frost.SetFloat("_ZWrite",0);
            frost.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");frost.renderQueue=2999;frost.SetOverrideTag("RenderType","Transparent");
            foreach(var r in region.GetComponentsInChildren<Renderer>())
            {
                if(r.name=="lid_glass")r.sharedMaterials=Enumerable.Repeat(glass,r.sharedMaterials.Length).ToArray();
                if(r.name=="lid_frost")r.sharedMaterials=Enumerable.Repeat(frost,r.sharedMaterials.Length).ToArray();
            }
        }

        static void Setup()
        {
            Directory.CreateDirectory(Dir);
            AssetDatabase.Refresh();
            var importer=AssetImporter.GetAtPath(Model) as ModelImporter;
            if(importer==null)throw new InvalidOperationException("Export S1_ServiceKit.fbx through Blender first.");
            if(!importer.bakeAxisConversion || importer.importAnimation)
            {
                importer.bakeAxisConversion=true; importer.importAnimation=false;
                importer.materialImportMode=ModelImporterMaterialImportMode.ImportStandard;
                importer.SaveAndReimport();
            }
            kit=AssetDatabase.LoadAssetAtPath<GameObject>(Model);
            ceramic=Mat("Ceramic",new Color(.39f,.47f,.44f),0,.28f);
            steel=Mat("Steel",new Color(.16f,.20f,.22f),.75f,.38f);
            gasket=Mat("Gasket",new Color(.025f,.034f,.038f),0,.13f);
            amber=Mat("Amber",new Color(.66f,.37f,.10f),0,.22f);
            trim=Mat("Trim",new Color(.05f,.24f,.24f),.1f,.35f);
            diffuser=Mat("Light",new Color(.65f,.87f,.83f),0,.4f);
            diffuser.EnableKeyword("_EMISSION"); diffuser.SetColor("_EmissionColor",new Color(.35f,.8f,.72f)*2.2f);
            wall=Mat("Concrete",new Color(.23f,.27f,.27f),0,.1f);
            floor=Mat("Floor",Color.white,.15f,.27f);
            var tex=AssetDatabase.LoadAssetAtPath<Texture2D>(Dir+"/Floor.png");
            if(tex==null)
            {
                tex=new Texture2D(512,512,TextureFormat.RGB24,false);
                var pixels=new Color[512*512];
                for(int y=0;y<512;y++)for(int x=0;x<512;x++)
                {
                    float n=Mathf.PerlinNoise(x*.05f,y*.05f)*.025f+Mathf.PerlinNoise(x*.31f,y*.31f)*.018f;
                    float v=.22f+n;
                    if(x<3||y<3||x>508||y>508)v*=.48f;
                    if(x==5||y==5)v+=.09f;
                    float stain=Mathf.PerlinNoise(x*.013f+17,y*.013f+43);
                    v*=Mathf.Lerp(.78f,1,stain);
                    pixels[y*512+x]=new Color(v*.88f,v,v*.97f);
                }
                tex.SetPixels(pixels);tex.Apply();File.WriteAllBytes(Dir+"/Floor.png",tex.EncodeToPNG());Object.DestroyImmediate(tex);
                AssetDatabase.ImportAsset(Dir+"/Floor.png");tex=AssetDatabase.LoadAssetAtPath<Texture2D>(Dir+"/Floor.png");
            }
            floor.SetTexture("_BaseMap",tex);
        }

        static Material Mat(string name,Color color,float metal,float smooth)
        {
            string path=Dir+"/"+name+".mat";
            var m=AssetDatabase.LoadAssetAtPath<Material>(path);
            if(m==null){m=new Material(Shader.Find("Universal Render Pipeline/Lit"));AssetDatabase.CreateAsset(m,path);}
            m.SetColor("_BaseColor",color);m.SetFloat("_Metallic",metal);m.SetFloat("_Smoothness",smooth);EditorUtility.SetDirty(m);return m;
        }
        static void Place(Transform parent,string name,Vector3 p,float yaw)
        {
            var source=kit.GetComponentsInChildren<Transform>().First(t=>t.name==name);
            var go=Object.Instantiate(source.gameObject,parent);go.name=name;go.transform.localPosition=p;
            go.transform.localRotation=Quaternion.Euler(0,yaw,0)*source.localRotation;go.transform.localScale=source.localScale;
            foreach(var r in go.GetComponentsInChildren<Renderer>())
                r.sharedMaterials=r.sharedMaterials.Select(m=>m==null?steel:m.name.Contains("Ceramic")?ceramic:m.name.Contains("Gasket")?gasket:m.name.Contains("Light")?diffuser:m.name.Contains("Amber")?amber:steel).ToArray();
        }
        static void Box(Transform parent,string name,Vector3 pos,Vector3 size,Material mat)
        {
            var go=GameObject.CreatePrimitive(PrimitiveType.Cube);go.name=name;go.transform.SetParent(parent,false);
            go.transform.localPosition=pos;go.transform.localScale=size;Object.DestroyImmediate(go.GetComponent<Collider>());go.GetComponent<Renderer>().sharedMaterial=mat;
        }
        static void Lamp(Transform parent,Vector3 pos,Color color,float intensity,float range)
        {
            var go=new GameObject("Service light");go.transform.SetParent(parent,false);go.transform.localPosition=pos;
            var l=go.AddComponent<Light>();l.type=LightType.Point;l.color=color;l.intensity=intensity;l.range=range;l.shadows=LightShadows.None;
        }
        static void Label(Transform parent,string text,Vector3 pos,Quaternion rot,float size)
        {
            var go=new GameObject("Sign "+text.Replace('\n',' '));go.transform.SetParent(parent,false);go.transform.localPosition=pos;go.transform.localRotation=rot;
            var t=go.AddComponent<TextMesh>();t.text=text;t.fontSize=64;t.characterSize=size*.15f;t.anchor=TextAnchor.MiddleCenter;t.alignment=TextAlignment.Center;t.color=new Color(.76f,.85f,.79f);
            var font=Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");t.font=font;
            string path=Dir+"/WorldSign.mat";
            var mat=AssetDatabase.LoadAssetAtPath<Material>(path);
            if(mat==null){mat=new Material(Shader.Find("Esneider/WorldSign"));AssetDatabase.CreateAsset(mat,path);}
            mat.mainTexture=font.material.mainTexture;EditorUtility.SetDirty(mat);go.GetComponent<MeshRenderer>().sharedMaterial=mat;
        }
        static void Floor(Transform parent,float w,float d)
        {
            var mesh=new Mesh();mesh.name="S1 floor "+parent.name;
            mesh.vertices=new[]{new Vector3(0,.012f,0),new Vector3(0,.012f,d),new Vector3(w,.012f,d),new Vector3(w,.012f,0)};
            mesh.uv=new[]{Vector2.zero,new Vector2(0,d/2),new Vector2(w/2,d/2),new Vector2(w/2,0)};
            mesh.triangles=new[]{0,1,2,0,2,3};mesh.RecalculateNormals();mesh.RecalculateBounds();
            string path=Dir+"/Floor_"+parent.name+".asset";
            var stored=AssetDatabase.LoadAssetAtPath<Mesh>(path);
            if(stored!=null){EditorUtility.CopySerialized(mesh,stored);Object.DestroyImmediate(mesh);mesh=stored;}
            else AssetDatabase.CreateAsset(mesh,path);
            var go=new GameObject("Tiled floor");go.transform.SetParent(parent,false);go.AddComponent<MeshFilter>().sharedMesh=mesh;go.AddComponent<MeshRenderer>().sharedMaterial=floor;
        }
        public static string Capture(string name,Vector3 pos,Vector3 target)
        {
            var go=new GameObject("EX10 evidence camera");var c=go.AddComponent<Camera>();c.transform.position=pos;c.transform.LookAt(target);
            c.fieldOfView=70;c.nearClipPlane=.05f;c.farClipPlane=100;c.clearFlags=CameraClearFlags.SolidColor;c.backgroundColor=Color.black;
            var rt=new RenderTexture(1280,720,24);var previous=RenderTexture.active;
            string path=Path.GetFullPath(Path.Combine(Application.dataPath,"../../SourceArt/_evidence/EX-10/"+name+".png"));
            try{c.targetTexture=rt;c.Render();RenderTexture.active=rt;var t=new Texture2D(1280,720,TextureFormat.RGB24,false);t.ReadPixels(new Rect(0,0,1280,720),0,0);t.Apply();Directory.CreateDirectory(Path.GetDirectoryName(path));File.WriteAllBytes(path,t.EncodeToPNG());Object.DestroyImmediate(t);}
            finally{c.targetTexture=null;RenderTexture.active=previous;rt.Release();Object.DestroyImmediate(rt);Object.DestroyImmediate(go);}
            return path;
        }
    }
}
