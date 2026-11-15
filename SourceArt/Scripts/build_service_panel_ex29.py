"""Service cabinet with separately pivoted door and lever. Run via Blender MCP."""
import bpy,sys,os,json,shutil,math
from mathutils import Vector,Matrix
ROOT='C:/Users/HP/Documents/GitHub/proyectos-unity'
sys.path.insert(0,ROOT+'/SourceArt/Scripts')
import esn_lib as L
from build_clinic_fixtures_ex23 import FixtureBuilder
ASSET='OBJ-009_TableroAntiguo'
FOLDER=ROOT+'/SourceArt/_evidence/EX-29/'+ASSET
SCENE=None

def build():
    global SCENE
    b=FixtureBuilder('009','TableroAntiguo','EX29');groups=[]
    def freeze(name,pivot):
        obj=L.join(b.parts,'GEO-009-'+name);L.apply_all(obj)
        obj.data.transform(obj.matrix_world);obj.matrix_world=Matrix.Identity(4)
        obj.data.transform(Matrix.Translation(-Vector(pivot)));obj.location=pivot
        L.smooth(obj,40);groups.append(obj);b.parts=[];return obj
    b.box('back',(.8,.014,1.1),(0,.093,.55),'paint',.001,True)
    for x in (-.392,.392):b.box('side',(.016,.196,1.1),(x,-.005,.55),'paint',.001,True)
    for z in (.008,1.092):b.box('return',(.768,.196,.016),(0,-.005,z),'paint',.001,True)
    b.box('isolated_backplate',(.67,.016,.93),(0,.07,.55),'ivory',.001)
    for z in (.69,.86):b.box('module_rail',(.39,.018,.025),(-.13,.04,z),'steel',0)
    for x in (-.25,-.13):
        for z in (.68,.82):b.box('fuse_contact_socket',(.042,.018,.02),(x,.014,z),'copper',.001)
    b.box('switch_base',(.17,.09,.24),(.18,.015,.47),'dark',.002)
    b.cyl('switch_axis',.028,.07,(.18,-.05,.43),'steel','Y',16)
    for x in (-.25,-.13):
        b.tube('protected_feed',[(x,.045,.89),(x,.045,.96),(.30,.045,.96),(.30,.045,.50)],.008,'dark')
    b.tube('network_return',[(.18,.035,.38),(.29,.035,.30),(.29,.035,.09),(.15,.035,.05)],.008,'copper')
    b.box('mara_patch',(.07,.032,.056),(.29,.031,.27),'dark',.001)
    for z in (.25,.27,.29):b.box('repair_tape',(.076,.033,.008),(.29,.031,z),'ivory',0)
    b.box('note_paper',(.24,.002,.30),(-.18,.049,.30),'label',0)
    note_texture(b.m['label'])
    # Authored panel labels use world-space projection, independent of export UVs.
    b.m['titles']=L.material(ASSET+'_titles',(.6,.6,.5),.8,0)
    b.box('status_plate',(.29,.003,.12),(.17,-.035,.81),'titles',0)
    mat=b.m['titles'];nodes=mat.node_tree.nodes;links=mat.node_tree.links
    tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(ROOT+'/SourceArt/Textures/EX29_PanelLabels.png',check_existing=True);tex.image.pack()
    geo=nodes.new('ShaderNodeNewGeometry');sep=nodes.new('ShaderNodeSeparateXYZ');links.new(geo.outputs['Position'],sep.inputs[0]);combine=nodes.new('ShaderNodeCombineXYZ')
    for coord,low,high,out in [('X',.025,.315,'X'),('Z',.75,.87,'Y')]:
        remap=nodes.new('ShaderNodeMapRange');remap.inputs['From Min'].default_value=low;remap.inputs['From Max'].default_value=high
        links.new(sep.outputs[coord],remap.inputs['Value']);links.new(remap.outputs[0],combine.inputs[out])
    links.new(combine.outputs[0],tex.inputs['Vector']);shader=next(n for n in nodes if n.type=='BSDF_PRINCIPLED');links.new(tex.outputs['Color'],shader.inputs['Base Color'])
    for x in (.075,.25):b.cyl('indicator_bezel',.020,.015,(x,-.050,.72),'steel','Y',16)
    freeze('Body',(0,0,0))
    b.box('door',(.75,.012,1.06),(-.007,-.113,.55),'paint',.003)
    for z in (.18,.55,.92):b.cyl('hinge',.012,.075,(-.382,-.110,z),'steel','Z',12)
    for z in (.45,.65):b.box('handle_mount',(.026,.019,.024),(.30,-.124,z),'steel',.001)
    b.box('handle',(.025,.023,.222),(.30,-.1385,.55),'dark',.001)
    b.box('door_label',(.24,.002,.10),(0,-.120,.86),'label',0)
    # An engraved power symbol constructed as geometry reads even without a decal.
    for z in (.85,.87):b.box('warning_bar',(.15,.001,.007),(0,-.1215,z),'dark',0)
    freeze('Door',(-.382,-.110,.55))
    b.box('lever_stem',(.024,.024,.135),(.18,-.075,.4975),'steel',.001)
    b.cyl('lever_grip',.022,.104,(.18,-.075,.565),'dark','X',16)
    freeze('Lever',(.18,-.075,.43))
    L.uv_project_all(groups);tris=0
    for obj in groups:obj.data.calc_loop_triangles();tris+=len(obj.data.loop_triangles)
    os.makedirs(FOLDER,exist_ok=True)
    report={'asset':ASSET,'triangles':tris,'mesh_count':3,'texture_sets':1,'pivots_blender':{'Door':[-.382,-.110,.55],'Lever':[.18,-.075,.43]},'collision_boxes_blender':b.collision,'state':'En produccion'}
    with open(FOLDER+'/geometry.json','w') as f:json.dump(report,f,indent=2)
    SCENE=b.scene;bpy.data.libraries.write(ROOT+'/SourceArt/Blender/'+ASSET+'.blend',{SCENE},fake_user=True)
    return report

def activate():
    global SCENE
    if SCENE is None:
        with bpy.data.libraries.load(ROOT+'/SourceArt/Blender/'+ASSET+'.blend',link=False) as (src,dst):dst.scenes=src.scenes
        SCENE=dst.scenes[0]
    bpy.context.window.scene=SCENE;return SCENE

def note_texture(mat):
    nodes=mat.node_tree.nodes;links=mat.node_tree.links
    tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(ROOT+'/SourceArt/Textures/EX29_MaraNote.png',check_existing=True);tex.image.pack()
    geo=nodes.new('ShaderNodeNewGeometry');sep=nodes.new('ShaderNodeSeparateXYZ');links.new(geo.outputs['Position'],sep.inputs[0]);combine=nodes.new('ShaderNodeCombineXYZ')
    for coord,low,high,out in [('X',-.30,-.06,'X'),('Z',.15,.45,'Y')]:
        remap=nodes.new('ShaderNodeMapRange');remap.inputs['From Min'].default_value=low;remap.inputs['From Max'].default_value=high;remap.clamp=True
        links.new(sep.outputs[coord],remap.inputs['Value']);links.new(remap.outputs[0],combine.inputs[out])
    links.new(combine.outputs[0],tex.inputs['Vector']);shader=next(n for n in nodes if n.type=='BSDF_PRINCIPLED');links.new(tex.outputs['Color'],shader.inputs['Base Color'])

def render():
    scene=activate();old=L.EVIDENCE;L.EVIDENCE=FOLDER
    door=next(o for o in scene.objects if '009-Door' in o.name);door.rotation_euler.z=math.radians(-108)
    try:return L.sheet(ASSET,[o for o in scene.objects if o.type=='MESH'],views=('iso',),res=640)
    finally:L.EVIDENCE=old;door.rotation_euler.z=0

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
