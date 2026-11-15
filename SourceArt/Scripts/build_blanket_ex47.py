"""EX-47: weighted hospital blanket for the focal HUM-01 camilla."""
import bpy, json, math, os, shutil, sys
from mathutils import Vector

ROOT='C:/Users/HP/Documents/GitHub/proyectos-unity'
sys.path.insert(0,ROOT+'/SourceArt/Scripts')
import esn_lib as L

ASSET='OBJ-054_VendajesManta';FOLDER=ROOT+'/SourceArt/_evidence/EX-47/'+ASSET
SCENE=None;COL=None;RIG=None;BLANKET=None


def build():
    global SCENE,COL,RIG,BLANKET
    SCENE=bpy.data.scenes.new('EX47_'+ASSET);bpy.context.window.scene=SCENE
    SCENE.unit_settings.system='METRIC';SCENE.unit_settings.scale_length=1
    COL=bpy.data.collections.new('EXPORT_'+ASSET);SCENE.collection.children.link(COL)
    mat=L.material(ASSET+'_fabric',(.265,.31,.285),.97,0,bump=.024,scale=260,edge_wear=0,ao=.58)
    nx,ny=24,16;verts=[];faces=[];weights=[]
    count=(nx+1)*(ny+1)
    for layer in (0,1):
        for j in range(ny+1):
            v=-1+2*j/ny;edge=max(0,1-v*v)**.55
            for i in range(nx+1):
                u=i/nx;x=-.58+1.56*u
                torso=.230*math.exp(-((x+.24)/.40)**2)
                thighs=.155*math.exp(-((x-.31)/.48)**2)
                feet=.115*math.exp(-((x-.84)/.20)**2)
                fold=.009*math.sin(u*math.tau*8+v*3.4)*edge + .005*math.sin(v*math.tau*3.5+u*4)*edge
                top=.836+edge*(torso+thighs+feet)+fold
                z=top if layer else top-.011
                verts.append((x,v*.50,z))
                chest=max(0,min(1,(.22-x)/.48))*edge
                weights.append({'blanket_root':1-chest,'blanket_chest':chest})
    for layer in (0,1):
        for j in range(ny):
            for i in range(nx):
                a=layer*count+j*(nx+1)+i;q=(a,a+1,a+nx+2,a+nx+1)
                faces.append(q if layer else tuple(reversed(q)))
    boundary=list(range(nx+1))+[j*(nx+1)+nx for j in range(1,ny+1)]+[ny*(nx+1)+i for i in range(nx-1,-1,-1)]+[j*(nx+1) for j in range(ny-1,0,-1)]
    for k,a in enumerate(boundary):
        b=boundary[(k+1)%len(boundary)];faces.append((a,b,b+count,a+count))
    data=bpy.data.meshes.new(ASSET);data.from_pydata(verts,[],faces);data.update()
    BLANKET=bpy.data.objects.new('GEO-'+ASSET,data);COL.objects.link(BLANKET);L.assign(BLANKET,mat)
    for p in data.polygons:p.use_smooth=True
    groups={n:BLANKET.vertex_groups.new(name=n) for n in ('blanket_root','blanket_chest')}
    for index,row in enumerate(weights):
        for name,weight in row.items():
            if weight>0:groups[name].add([index],weight,'REPLACE')
    RIG=L.armature('RIG-'+ASSET,[('blanket_root',(0,0,.78),(0,0,.90),None,(0,-1,0)),
                                 ('blanket_chest',(-.28,0,.84),(-.28,0,1.04),'blanket_root',(0,-1,0))],COL)
    BLANKET.parent=RIG;mod=BLANKET.modifiers.new('Blanket rig','ARMATURE');mod.object=RIG
    L.uv_project(BLANKET,margin=.008);data.calc_loop_triangles()
    report={'asset':ASSET,'triangles':len(data.loop_triangles),'vertices':len(data.vertices),'bones':2,
            'mesh_count':1,'texture_sets':1,'dimensions_blender':list(BLANKET.dimensions),
            'features':['1.56 x 1.0 m closed blanket with physical edge thickness','body-derived torso thigh and foot volume',
                        'two-frequency authored folds','weighted torso region follows breathing','draped edges reach mattress'],
            'collision_boxes_blender':[],'state':'En produccion'}
    os.makedirs(FOLDER,exist_ok=True)
    with open(FOLDER+'/geometry.json','w',encoding='utf-8') as f:json.dump(report,f,indent=2,ensure_ascii=False)
    save();return report


def save():bpy.data.libraries.write(ROOT+'/SourceArt/Blender/'+ASSET+'.blend',{SCENE},fake_user=True)


def render():
    old=L.EVIDENCE;L.EVIDENCE=FOLDER;bpy.context.window.scene=SCENE
    try:return L.sheet(ASSET,[BLANKET],views=('top','side','iso'),res=900)
    finally:L.EVIDENCE=old


def bake():
    bpy.context.window.scene=SCENE;RIG.data.pose_position='REST';old=L.TEX_DIR;L.TEX_DIR=FOLDER
    try:maps=L.bake_pbr([BLANKET],ASSET,size=1024,samples=24,margin=3)
    finally:L.TEX_DIR=old
    for suffix,path in maps.items():
        image=bpy.data.images.load(path,check_existing=False);image.pack()
        node=BLANKET.data.materials[0].node_tree.nodes.new('ShaderNodeTexImage');node.image=image;node.label='Runtime baked '+suffix
        shutil.copy2(path,ROOT+'/EsneiderProtocoloLazaro/Assets/_Game/Art/Textures/'+os.path.basename(path))
    save()
    with open(FOLDER+'/bake.json','w') as f:json.dump(maps,f,indent=2)
    return maps


def animate():
    bpy.context.window.scene=SCENE;RIG.data.pose_position='POSE'
    with L.ctx(RIG):
        bpy.ops.object.mode_set(mode='EDIT');RIG.data.edit_bones['blanket_chest'].use_connect=False;bpy.ops.object.mode_set(mode='OBJECT')
    RIG.animation_data_clear();SCENE.render.fps=30;SCENE.frame_start=1;SCENE.frame_end=151
    poses={f:{'blanket_chest':((0,0,0),(0,0,.0024*a))} for f,a in ((1,0),(31,.4),(61,1),(91,.65),(121,.15),(151,0))}
    action=L.action(RIG,'OBJ054_Blanket_Breathe',151,poses=poses);L.push_nla(RIG,action);L.enable_nla(RIG);SCENE.frame_set(1);save()
    return {'clip':action.name,'seconds':5,'travel_m':.0024}


def export():
    bpy.context.window.scene=SCENE;SCENE.frame_set(1);RIG.data.pose_position='POSE';L.enable_nla(RIG)
    old=BLANKET.data;BLANKET.data=old.copy();mat=BLANKET.data.materials[0];BLANKET.data.materials.clear();BLANKET.data.materials.append(mat)
    for face in BLANKET.data.polygons:face.material_index=0
    path=ROOT+'/EsneiderProtocoloLazaro/Assets/_Game/Art/Models/'+ASSET+'.fbx'
    try:
        with L.ctx(BLANKET,[BLANKET,RIG]):
            bpy.ops.export_scene.fbx(filepath=path,use_selection=True,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Z',axis_up='Y',object_types={'MESH','ARMATURE'},add_leaf_bones=False,bake_space_transform=True,mesh_smooth_type='FACE',use_mesh_modifiers=True,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=True,bake_anim_use_all_bones=True,bake_anim_simplify_factor=0,path_mode='STRIP',embed_textures=False)
    finally:BLANKET.data=old
    samples=[dict(zip(('x','y','z'),BLANKET.matrix_world@v.co)) for v in list(BLANKET.data.vertices)[::max(1,len(BLANKET.data.vertices)//80)]]
    with open(FOLDER+'/source_coordinates.json','w') as f:json.dump({'vertices':samples},f)
    report=json.load(open(FOLDER+'/geometry.json'));report['unweighted_vertices']=sum(sum(g.weight for g in v.groups)<.999 for v in BLANKET.data.vertices)
    report['clips']=[strip.action.name for track in RIG.animation_data.nla_tracks for strip in track.strips]
    with open(FOLDER+'/geometry.json','w') as f:json.dump(report,f,indent=2)
    save();return report
