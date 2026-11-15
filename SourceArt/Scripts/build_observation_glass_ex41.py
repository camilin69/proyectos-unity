"""Four-metre observation glazing module; preserve all other Blender scenes."""
import bpy,sys,os,json,shutil
from mathutils import Matrix
ROOT='C:/Users/HP/Documents/GitHub/proyectos-unity'
sys.path.insert(0,ROOT+'/SourceArt/Scripts')
import esn_lib as L
from build_clinic_fixtures_ex23 import FixtureBuilder
ASSET='OBJ-060_VidrioObservacion';FOLDER=ROOT+'/SourceArt/_evidence/EX-41/'+ASSET
SCENE=None

def build():
    global SCENE
    b=FixtureBuilder('060','VidrioObservacion','EX41')
    # Structural jambs enclose a 3.84 by 2.34 metre clear opening.
    for x in (-1.96,1.96):b.box('jamb',(.08,.15,2.5),(x,0,1.25),'paint',.002)
    for z in (.04,2.46):b.box('sill_header',(3.84,.15,.08),(0,0,z),'paint',.002)
    for y in (-.022,.022):
        for x in (-1.911,1.911):b.box('vertical_seal',(.018,.020,2.34),(x,y,1.25),'dark',0)
        for z in (.089,2.411):b.box('horizontal_seal',(3.804,.020,.018),(0,y,z),'dark',0)
    for y in (-.043,.043):
        for x in (-1.929,1.929):b.box('retaining_strip',(.022,.020,2.38),(x,y,1.25),'steel',.001)
        for z in (.065,2.435):b.box('retaining_strip',(3.836,.020,.022),(0,y,z),'steel',.001)
        for x in (-1.96,1.96):
            for z in (.18,2.32):b.cyl('retainer_fastener',.014,.008,(x,(-.079 if y<0 else .079),z),'steel','Y',8)
    for o in b.parts:
        for m in o.modifiers:
            if m.type=='BEVEL':m.segments=1
    bpy.context.view_layer.update()
    frame=L.join(b.parts,'GEO-060-Frame');L.apply_all(frame);frame.data.transform(frame.matrix_world);frame.matrix_world=Matrix.Identity(4);L.smooth(frame,35);L.uv_project(frame)
    b.parts=[]
    glass=bpy.data.materials.new(ASSET+'_glass');glass.use_nodes=True
    shader=glass.node_tree.nodes.get('Principled BSDF');shader.inputs['Base Color'].default_value=(.78,.89,.88,1);shader.inputs['Roughness'].default_value=.12;shader.inputs['Transmission Weight'].default_value=1;shader.inputs['IOR'].default_value=1.5
    b.m['glass']=glass
    pane=b.box('Pane',(3.84,.024,2.34),(0,0,1.25),'glass',0);pane.name='GEO-060-Pane';L.apply_all(pane)
    pane.data.transform(pane.matrix_world);pane.matrix_world=Matrix.Identity(4)
    uv=pane.data.uv_layers.active or pane.data.uv_layers.new(name='Glazing')
    for poly in pane.data.polygons:
        for li in poly.loop_indices:
            co=pane.data.vertices[pane.data.loops[li].vertex_index].co;uv.data[li].uv=((co.x+1.92)/3.84,(co.z-.08)/2.34)
    os.makedirs(FOLDER,exist_ok=True);SCENE=b.scene
    objs=[frame,pane];tris=0
    for o in objs:o.data.calc_loop_triangles();tris+=len(o.data.loop_triangles)
    report={'asset':ASSET,'triangles':tris,'mesh_count':2,'texture_sets':2,'texture_notes':'512 frame PBR atlas plus 512 glazing RGBA mask; frame atlas not yet shared with other assets','dimensions_blender':[4,.166,2.5],'collision_boxes_blender':[{'center':[0,0,1.25],'size':[4,.15,2.5]}],'features':['structural frame and retaining strips','front and rear continuous gaskets','24 mm thick pane','recessed clear opening','eight accessible fasteners'],'state':'En produccion'}
    open(FOLDER+'/geometry.json','w').write(json.dumps(report,indent=2));bpy.data.libraries.write(ROOT+'/SourceArt/Blender/'+ASSET+'.blend',{SCENE},fake_user=True);return report

def render():
    old=L.EVIDENCE;L.EVIDENCE=FOLDER
    try:return L.sheet(ASSET,[o for o in SCENE.objects if o.type=='MESH'],views=('iso',),res=640)
    finally:L.EVIDENCE=old

def finish():
    bpy.context.window.scene=SCENE;objs=[o for o in SCENE.objects if o.type=='MESH'];frame=next(o for o in objs if 'Frame' in o.name)
    samples=[dict(zip(('x','y','z'),o.matrix_world@v.co)) for o in objs for v in list(o.data.vertices)[::max(1,len(o.data.vertices)//48)]]
    open(FOLDER+'/source_coordinates.json','w').write(json.dumps({'vertices':samples}))
    old=L.TEX_DIR;L.TEX_DIR=FOLDER
    try:maps=L.bake_pbr([frame],ASSET,size=512,samples=24,margin=2)
    finally:L.TEX_DIR=old
    for suffix,path in maps.items():
        img=bpy.data.images.load(path,check_existing=False);img.pack();n=frame.data.materials[0].node_tree.nodes.new('ShaderNodeTexImage');n.image=img;n.label='Runtime baked '+suffix
        shutil.copy2(path,ROOT+'/EsneiderProtocoloLazaro/Assets/_Game/Art/Textures/'+os.path.basename(path))
    mask=ROOT+'/EsneiderProtocoloLazaro/Assets/_Game/Art/Textures/'+ASSET+'_Glazing.png'
    if os.path.isfile(mask):
        pane=next(o for o in objs if 'Pane' in o.name);img=bpy.data.images.load(mask,check_existing=True);img.pack()
        node=pane.data.materials[0].node_tree.nodes.new('ShaderNodeTexImage');node.image=img;node.label='Runtime condensation and contact alpha mask'
    bpy.data.libraries.write(ROOT+'/SourceArt/Blender/'+ASSET+'.blend',{SCENE},fake_user=True)
    oldmesh=frame.data;frame.data=oldmesh.copy();mat=oldmesh.materials[0];frame.data.materials.clear();frame.data.materials.append(mat)
    for face in frame.data.polygons:face.material_index=0
    try:
        with L.ctx(frame,objs):bpy.ops.export_scene.fbx(filepath=ROOT+'/EsneiderProtocoloLazaro/Assets/_Game/Art/Models/'+ASSET+'.fbx',use_selection=True,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Z',axis_up='Y',object_types={'MESH'},bake_space_transform=True,mesh_smooth_type='FACE',use_mesh_modifiers=True,bake_anim=False,path_mode='STRIP',embed_textures=False)
    finally:frame.data=oldmesh
    open(FOLDER+'/bake.json','w').write(json.dumps(maps,indent=2));return maps
