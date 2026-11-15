"""Three rigid meshes with source pivots; motion is authored by Unity ClinicalArmMotion."""
import bpy,sys,os,json,shutil,math
from mathutils import Vector,Matrix
ROOT='C:/Users/HP/Documents/GitHub/proyectos-unity'
sys.path.insert(0,ROOT+'/SourceArt/Scripts')
import esn_lib as L
from build_clinic_fixtures_ex23 import FixtureBuilder
ASSET='OBJ-050_BrazoClinico'
FOLDER=ROOT+'/SourceArt/_evidence/EX-26/'+ASSET
SCENE=None

def build():
    global SCENE
    b=FixtureBuilder('050','BrazoClinico','EX26');groups=[]
    def freeze(name,pivot):
        obj=L.join(b.parts,'GEO-050-'+name);L.apply_all(obj)
        obj.data.transform(obj.matrix_world);obj.matrix_world=Matrix.Identity(4)
        obj.data.transform(Matrix.Translation(-Vector(pivot)));obj.location=pivot
        L.smooth(obj,40);groups.append(obj);b.parts=[];return obj
    b.box('mount_plate',(.06,.27,.40),(0,0,1.35),'paint',.008)
    for y in (-.10,.10):
        for z in (1.2,1.5):b.cyl('anchor',.014,.012,(.036,y,z),'steel','X',12)
    b.box('base_bracket',(.18,.15,.10),(.105,0,1.275),'steel',.008)
    b.cyl('yaw_bearing',.075,.13,(.12,0,1.35),'ivory','Z',24)
    freeze('Base',(0,0,0))
    b.cyl('shoulder_cap',.081,.022,(.12,0,1.424),'paint','Z',24)
    b.tube('upper_load_link',[(.12,0,1.37),(.72,0,1.75)],.062,'ivory')
    b.tube('upper_cover_seam',[(.21,-.057,1.42),(.63,-.057,1.69)],.008,'paint')
    b.tube('upper_cable',[(.12,.06,1.37),(.16,.10,1.51),(.65,.10,1.79),(.72,.08,1.77)],.009,'dark')
    b.cyl('elbow_motor',.095,.17,(.72,0,1.75),'paint','Y',24)
    for y in (-.096,.096):b.cyl('elbow_cover',.078,.018,(.72,y,1.75),'ivory','Y',24)
    freeze('Upper',(.12,0,1.35))
    b.cyl('elbow_inner_axis',.043,.19,(.72,0,1.75),'steel','Y',20)
    b.tube('forearm',[(.72,0,1.75),(1.30,0,1.60)],.046,'ivory')
    b.tube('forearm_cable',[(.75,.07,1.76),(.87,.10,1.80),(1.23,.08,1.68),(1.30,.05,1.61)],.008,'dark')
    b.cyl('wrist',.068,.12,(1.30,0,1.60),'paint','Z',24)
    b.box('tool_housing',(.19,.105,.095),(1.355,0,1.515),'ivory',.019)
    b.box('sensor_window',(.13,.075,.006),(1.355,0,1.464),'dark',.005)
    for x in (1.32,1.38):b.cyl('rounded_probe',.014,.035,(x,0,1.449),'steel','Z',12)
    b.box('sealed_tool_label',(.055,.002,.024),(1.355,-.054,1.515),'label',.001)
    freeze('Forearm',(.72,0,1.75))
    L.uv_project_all(groups);tris=0
    for obj in groups:obj.data.calc_loop_triangles();tris+=len(obj.data.loop_triangles)
    os.makedirs(FOLDER,exist_ok=True)
    report={'asset':ASSET,'triangles':tris,'mesh_count':3,'texture_sets':1,'pivots_blender':{'Upper':[.12,0,1.35],'Forearm':[.72,0,1.75]},'collision_boxes_blender':[{'center':[0,0,1.35],'size':[.06,.27,.4]}],'state':'En produccion'}
    with open(FOLDER+'/geometry.json','w') as f:json.dump(report,f,indent=2)
    SCENE=b.scene;bpy.data.libraries.write(ROOT+'/SourceArt/Blender/'+ASSET+'.blend',{SCENE},fake_user=True)
    return report
def activate():
    global SCENE
    if SCENE is None:
        with bpy.data.libraries.load(ROOT+'/SourceArt/Blender/'+ASSET+'.blend',link=False) as (src,dst):dst.scenes=src.scenes
        SCENE=dst.scenes[0]
    bpy.context.window.scene=SCENE;return SCENE
def render():
    scene=activate();old=L.EVIDENCE;L.EVIDENCE=FOLDER
    try:return L.sheet(ASSET,[o for o in scene.objects if o.type=='MESH'],views=('iso',),res=640)
    finally:L.EVIDENCE=old
def finish():
    scene=activate();objs=[o for o in scene.objects if o.type=='MESH']
    samples=[dict(zip(('x','y','z'),o.matrix_world@v.co)) for o in objs for v in list(o.data.vertices)[::max(1,len(o.data.vertices)//32)]]
    with open(FOLDER+'/source_coordinates.json','w') as f:json.dump({'vertices':samples},f)
    old=L.TEX_DIR;L.TEX_DIR=FOLDER
    try:maps=L.bake_pbr(objs,ASSET,size=1024,samples=24)
    finally:L.TEX_DIR=old
    for suffix,path in maps.items():
        img=bpy.data.images.load(path,check_existing=False);img.pack()
        node=objs[0].data.materials[0].node_tree.nodes.new('ShaderNodeTexImage');node.image=img;node.label='Runtime baked '+suffix
        shutil.copy2(path,ROOT+'/EsneiderProtocoloLazaro/Assets/_Game/Art/Textures/'+os.path.basename(path))
    bpy.data.libraries.write(ROOT+'/SourceArt/Blender/'+ASSET+'.blend',{scene},fake_user=True)
    backups=[(o,o.data) for o in objs];mat=objs[0].data.materials[0]
    try:
        for o,mesh in backups:
            o.data=mesh.copy();o.data.materials.clear();o.data.materials.append(mat)
            for face in o.data.polygons:face.material_index=0
        with L.ctx(objs[0],objs):bpy.ops.export_scene.fbx(filepath=ROOT+'/EsneiderProtocoloLazaro/Assets/_Game/Art/Models/'+ASSET+'.fbx',use_selection=True,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Z',axis_up='Y',object_types={'MESH'},bake_space_transform=True,mesh_smooth_type='FACE',use_mesh_modifiers=True,bake_anim=False,path_mode='STRIP',embed_textures=False)
    finally:
        for o,mesh in backups:o.data=mesh
    with open(FOLDER+'/bake.json','w') as f:json.dump(maps,f,indent=2)
    return maps
