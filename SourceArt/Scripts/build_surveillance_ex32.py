"""Surveillance cameras with separate mounting/head meshes and an explicit swivel pivot.
Run inside Blender MCP. No perception, rotation or audio is enabled by this asset.
"""
import bpy,sys,os,json,math,shutil
from mathutils import Vector,Matrix
ROOT='C:/Users/HP/Documents/GitHub/proyectos-unity'
sys.path.insert(0,ROOT+'/SourceArt/Scripts')
import esn_lib as L
from build_clinic_fixtures_ex23 import FixtureBuilder
ASSETS={'061':'CamaraVigilancia','061B':'CamaraVigilanciaDanada'}
SCENES={}
PIVOT=Vector((0,.055,.09))
def asset(id):return 'OBJ-'+id+'_'+ASSETS[id]
def folder(id):return ROOT+'/SourceArt/_evidence/EX-32/'+asset(id)

def build(id):
    b=FixtureBuilder(id,ASSETS[id],'EX32');groups=[];damaged=id.endswith('B')
    b.m['lens']=L.material(b.asset+'_coated_lens',(.025,.09,.105),.12,.65)
    b.m['board']=L.material(b.asset+'_circuit_board',(.045,.075,.035),.72,0)
    def freeze(name,pivot):
        obj=L.join(b.parts,'GEO-'+id+'-'+name);L.apply_all(obj)
        obj.data.transform(obj.matrix_world);obj.matrix_world=Matrix.Identity(4)
        obj.data.transform(Matrix.Translation(-Vector(pivot)));obj.location=pivot
        L.smooth(obj,40);groups.append(obj);b.parts=[];return obj
    # Wall plate: back plane Y=.15; base Z=0. The same attachment contract for both variants.
    b.box('wall_plate',(.12,.012,.11),(0,.144,.055),'steel',.001)
    for x in (-.045,.045):
        for z in (.017,.093):b.cyl('anchor',.006,.005,(x,.135,z),'steel','Y',8)
    b.box('load_arm',(.032,.11,.024),(0,.09,.035),'steel',.001)
    b.cyl('swivel_shaft',.025,.052,(0,.055,.066),'dark','Z',16)
    b.cyl('bearing_flange',.038,.010,(0,.055,.088),'steel','Z',20)
    b.tube('fixed_supply',[(.043,.137,.05),(.046,.107,.029),(.040,.065,.028),(.028,.054,.060)],.004,'dark')
    b.box('cable_clip',(.019,.01,.012),(.044,.118,.043),'ivory',0)
    freeze('Mount',(0,0,0))
    b.cyl('swivel_head',.026,.020,(0,.055,.099),'paint','Z',16)
    # Hollow folded shell, with an absent rear cover in the damaged variant.
    for x in (-.071,.071):b.box('housing_side',(.008,.20,.08),(x,-.030,.15),'paint',.001)
    for z in (.114,.186):b.box('housing_cap',(.134,.20,.008),(0,-.030,z),'paint',.001)
    if not damaged:b.box('rear_cover',(.134,.008,.064),(0,.066,.15),'ivory',.001)
    else:
        b.box('exposed_board',(.11,.005,.047),(0,.057,.15),'board',0)
        for x in (-.035,0,.035):
            b.box('chip',(.015,.006,.015),(x,.062,.15),'dark',0)
            b.box('circuit_trace',(.005,.001,.033),(x+.011,.060,.15),'copper',0)
    b.box('front_gasket',(.135,.008,.061),(0,-.128,.15),'dark',.001)
    b.cyl('lens_ring',.026,.020,(-.017,-.139,.15),'steel','Y',24)
    b.cyl('lens_inner',.022,.006,(-.017,-.150,.15),'dark','Y',24)
    if not damaged:
        b.cyl('lens_glass',.018,.002,(-.017,-.154,.15),'lens','Y',24)
        b.cyl('optical_aperture',.010,.001,(-.017,-.1555,.15),'dark','Y',20)
        b.cyl('inner_coating',.0065,.001,(-.017,-.1565,.15),'lens','Y',20)
    else:
        # Remaining glass shards surround a black sensor cavity. No decal-only damage.
        verts=[(-.017,-.155,.15),(-.035,-.155,.15),(-.030,-.155,.164),(-.017,-.155,.168),(-.004,-.155,.164),(.001,-.155,.15),(-.004,-.155,.137)]
        mesh=bpy.data.meshes.new('fractured optical coating');mesh.from_pydata(verts,[],[(1,2,3),(4,5,6)]);mesh.update()
        obj=bpy.data.objects.new('GEO-'+id+'-shattered_glass',mesh);b.col.objects.link(obj);L.assign(obj,b.m['lens']);b.parts.append(obj)
        b.tube('crack',[( -.032,-.1555,.161),(-.025,-.1555,.157),(-.019,-.1555,.165)],.0006,'dark')
    b.cyl('status_window',.004,.002,(.043,-.134,.147),'dark','Y',10)
    visor=b.box('sun_hood',(.17,.224,.009),(0,-.039,.1955),'ivory',.001)
    for x in (-.081,.081):b.box('hood_return',(.008,.222,.018),(x,-.039,.184),'ivory',.001)
    for x in (-.059,.059):b.cyl('front_screw',.003,.003,(x,-.133,.170),'steel','Y',8)
    b.box('serial_plate',(.030,.001,.009),(.042,-.1335,.126),'label',0)
    for i in range(6):b.box('serial_bar',(.001,.0005,.006),(.031+i*.004,-.13425,.126),'dark',0)
    if damaged:
        visor.rotation_euler.y=.10
        b.tube('severed_head_lead',[(.041,.065,.13),(.057,.075,.11),(.066,.073,.102)],.0035,'dark')
        b.tube('exposed_copper',[(.066,.073,.102),(.071,.072,.10)],.0016,'copper')
    else:
        b.tube('service_loop',[(.041,.065,.13),(.052,.09,.115),(.040,.1,.091),(.020,.07,.10)],.0035,'dark')
        b.box('maintenance_tape',(.027,.010,.020),(.043,.090,.105),'ivory',0)
    head=freeze('Head',PIVOT)
    if damaged:
        # Freeze a drooped head into geometry but retain the nominal swivel origin for repair.
        head.data.transform(Matrix.Rotation(.28,4,'X') @ Matrix.Rotation(-.16,4,'Z'))
    L.uv_project_all(groups);tris=0
    for obj in groups:obj.data.calc_loop_triangles();tris+=len(obj.data.loop_triangles)
    points=[o.matrix_world@v.co for o in groups for v in o.data.vertices]
    size=[max(v[i] for v in points)-min(v[i] for v in points) for i in range(3)]
    report={'asset':b.asset,'triangles':tris,'mesh_count':2,'texture_sets':1,'dimensions_blender':size,'pivots_blender':{'Head':list(PIVOT)},'collision_boxes_blender':[],
        'features':['wall plate and four anchors','swivel bearing','hollow housing and hood','recessed coated optics','service cable' if not damaged else 'severed cable, fractured lens, exposed rear board and drooped head'],'state':'En produccion'}
    os.makedirs(folder(id),exist_ok=True)
    with open(folder(id)+'/geometry.json','w') as f:json.dump(report,f,indent=2)
    SCENES[id]=b.scene;bpy.data.libraries.write(ROOT+'/SourceArt/Blender/'+b.asset+'.blend',{b.scene},fake_user=True)
    return report

def activate(id):
    if id not in SCENES:
        with bpy.data.libraries.load(ROOT+'/SourceArt/Blender/'+asset(id)+'.blend',link=False) as (src,dst):dst.scenes=src.scenes
        SCENES[id]=dst.scenes[0]
    bpy.context.window.scene=SCENES[id];return SCENES[id]
def render(id):
    s=activate(id);old=L.EVIDENCE;L.EVIDENCE=folder(id)
    try:return L.sheet(asset(id),[o for o in s.objects if o.type=='MESH'],views=('iso',),res=640)
    finally:L.EVIDENCE=old
def finish(id):
    s=activate(id);objs=[o for o in s.objects if o.type=='MESH'];name=asset(id)
    # Small parts made the generic pointiness wear wash out entire painted faces.
    # Keep it subtle; the damaged model expresses failure through its actual parts.
    for mat in {m for o in objs for m in o.data.materials}:
        for node in mat.node_tree.nodes:
            if node.type=='MATH' and node.operation=='MULTIPLY' and node.inputs[0].is_linked:
                ramp=node.inputs[0].links[0].from_node
                if ramp.type=='VALTORGB' and ramp.inputs['Fac'].is_linked and ramp.inputs['Fac'].links[0].from_node.type=='NEW_GEOMETRY':
                    node.inputs[1].default_value=0 if '_lens' in mat.name or '_board' in mat.name else .04
    samples=[dict(zip(('x','y','z'),o.matrix_world@v.co)) for o in objs for v in list(o.data.vertices)[::max(1,len(o.data.vertices)//32)]]
    with open(folder(id)+'/source_coordinates.json','w') as f:json.dump({'vertices':samples},f)
    old=L.TEX_DIR;L.TEX_DIR=folder(id)
    try:maps=L.bake_pbr(objs,name,size=512,samples=24)
    finally:L.TEX_DIR=old
    for suffix,path in maps.items():
        img=bpy.data.images.load(path,check_existing=False);img.pack()
        node=objs[0].data.materials[0].node_tree.nodes.new('ShaderNodeTexImage');node.image=img;node.label='Runtime baked '+suffix
        shutil.copy2(path,ROOT+'/EsneiderProtocoloLazaro/Assets/_Game/Art/Textures/'+os.path.basename(path))
    bpy.data.libraries.write(ROOT+'/SourceArt/Blender/'+name+'.blend',{s},fake_user=True)
    backups=[(o,o.data) for o in objs];mat=objs[0].data.materials[0]
    try:
        for o,mesh in backups:
            o.data=mesh.copy();o.data.materials.clear();o.data.materials.append(mat)
            for face in o.data.polygons:face.material_index=0
        with L.ctx(objs[0],objs):bpy.ops.export_scene.fbx(filepath=ROOT+'/EsneiderProtocoloLazaro/Assets/_Game/Art/Models/'+name+'.fbx',use_selection=True,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Z',axis_up='Y',object_types={'MESH'},bake_space_transform=True,mesh_smooth_type='FACE',use_mesh_modifiers=True,bake_anim=False,path_mode='STRIP',embed_textures=False)
    finally:
        for o,mesh in backups:o.data=mesh
    with open(folder(id)+'/bake.json','w') as f:json.dump(maps,f,indent=2)
    return maps
