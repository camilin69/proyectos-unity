"""Original fractured concrete assembly with two independently movable chips. Blender MCP only."""
import bpy,bmesh,math,random,json,os,shutil,sys
from mathutils import Vector,Matrix
ROOT='C:/Users/HP/Documents/GitHub/proyectos-unity'
sys.path.insert(0,ROOT+'/SourceArt/Scripts')
import esn_lib as L
from build_industrial_furniture_ex13 import Builder
ASSET='OBJ-012_EscombrosConcreto'
OUT=ROOT+'/SourceArt/_evidence/EX-20/'+ASSET
SCENE=None

def chunk(b,name,size,pos,seed,old_top=True):
    rng=random.Random(seed);sx,sy,sz=size
    verts=[];count=6;angle=rng.uniform(-.55,.55)
    for z in (0,sz):
        for i in range(count):
            a=i*math.tau/count+angle
            x=math.cos(a)*sx*.56*rng.uniform(.68,1)
            y=math.sin(a)*sy*.56*rng.uniform(.68,1)
            verts.append((x,y,z if z==0 else z*rng.uniform(.65,1)))
    # Convex hull gives closed fracture faces and a stable flat lower contact.
    bm=bmesh.new();vs=[bm.verts.new(v) for v in verts];bmesh.ops.convex_hull(bm,input=vs)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    me=bpy.data.meshes.new(name);bm.to_mesh(me);bm.free()
    o=bpy.data.objects.new('GEO-012-'+name,me);b.col.objects.link(o);o.location=pos
    o.data.materials.append(b.m['concrete']);o.data.materials.append(b.m['fracture'])
    for p in me.polygons:p.material_index=0 if old_top and p.normal.z>.6 else 1
    bevel=o.modifiers.new('fracture_edge_microbevel','BEVEL');bevel.width=.002;bevel.segments=1
    b.parts.append(o);return o

def freeze(b,name,pivot=(0,0,0)):
    o=L.join(b.parts,'GEO-012-'+name);L.apply_all(o)
    o.data.transform(o.matrix_world);o.matrix_world=Matrix.Identity(4)
    o.data.transform(Matrix.Translation(-Vector(pivot)));o.location=pivot
    b.parts=[];return o

def build():
    global SCENE
    b=Builder('012','EscombrosConcreto','EX20')
    b.m['concrete']=L.material(ASSET+'_aged_surface',(.20,.205,.19),.94,0,bump=.16,scale=22)
    b.m['fracture']=L.material(ASSET+'_fresh_fracture',(.38,.36,.31),.97,0,bump=.23,scale=48)
    b.m['rebar']=L.material(ASSET+'_rebar',(.16,.09,.045),.83,.65,bump=.08,scale=65)
    # Deliberate pile layout: larger wall fragments form the core; chips sit at its foot.
    layout=[(-1.35,-.6,.75,.67,.27),(-.63,-.9,.75,.65,.33),(.15,-.8,.78,.7,.34),(.95,-.45,.75,.65,.26),
            (-1.15,.12,.8,.72,.34),(-.35,-.06,.79,.72,.46),(.45,.04,.75,.75,.40),(1.18,.27,.72,.68,.30),
            (-.65,.65,.75,.67,.25),(.15,.75,.73,.66,.32),(.9,.9,.78,.66,.38),
            (-1.7,.17,.28,.23,.14),(-1.45,.79,.32,.31,.15),(-.90,1.10,.25,.24,.12),
            (.05,-1.28,.27,.22,.11),(.78,-1.15,.35,.30,.13),(1.6,.62,.23,.20,.11),(1.4,1.3,.31,.28,.18)]
    for i,(x,y,w,d,h) in enumerate(layout):
        chunk(b,'slab_%02d'%i,(w,d,h),(x,y,0),1200+i)
        if w>.4:b.collision.append({'center':[x,y,h*.44],'size':[w*.86,d*.86,h*.88]})
    # Stacked mass has a real lower slab beneath it; exposed bars emerge from the fresh face.
    for i,(x,y,z,w,d,h) in enumerate([(-.40,-.05,.31,.78,.65,.29),(.38,.12,.31,.71,.65,.26),(-.42,-.02,.54,.65,.49,.22)]):
        chunk(b,'stacked_fracture_%d'%i,(w,d,h),(x,y,z),1300+i)
        b.collision.append({'center':[x,y,z+h*.44],'size':[w*.86,d*.86,h*.88]})
    for i,x in enumerate((-.55,-.31)):
        b.tube('exposed_rebar_%d'%i,[(x,-.18,.62),(x,-.43,.68),(x+.10,-.74,.64),(x+.18,-.95,.55)],.010,'rebar')
        for j in range(6):b.cyl('bar_rib',.012,.007,(x,-.21-j*.034,.63+j*.008),'rebar','Y',10)
    # A fragment below the removable crowbar and two chips displaced by extraction.
    support=chunk(b,'crowbar_support',(.72,.59,.52),(1.12,1.33,0),1400)
    b.collision.append({'center':[1.12,1.33,.225],'size':[.60,.48,.45]})
    starts=[]
    for x,y in ((.92,1.28),(1.29,1.28)):
        ok,hit,normal,face=support.ray_cast(Vector((x,y,2))-support.location,Vector((0,0,-1)))
        if not ok:raise RuntimeError('Chip support ray missed')
        starts.append((x,y,hit.z+support.location.z+.003))
    groups=[freeze(b,'Main')];loose=[]
    for i,(x,y,z) in enumerate(starts):
        chunk(b,'loose_chip_'+str(i),(.17,.15,.10),(x,y,z),1500+i,False)
        o=freeze(b,'Loose'+str(i),(x,y,z));groups.append(o)
        loose.append({'name':o.name,'pivot_blender':[x,y,z],'size':[.17,.15,.10]})
    L.uv_project_all(groups);tris=0
    for o in groups:o.data.calc_loop_triangles();tris+=len(o.data.loop_triangles)
    os.makedirs(OUT,exist_ok=True)
    report={'asset':ASSET,'triangles':tris,'mesh_count':3,'texture_sets':1,'collision_boxes_blender':b.collision,'loose':loose,
            'features':['closed fractured slabs with thickness','aged exterior versus fresh fracture','exposed ribbed reinforcing bars','stacked structural mass','two separate extraction chips'],'state':'En produccion'}
    json.dump(report,open(OUT+'/geometry.json','w'),indent=2)
    SCENE=b.scene;bpy.data.libraries.write(ROOT+'/SourceArt/Blender/'+ASSET+'.blend',{SCENE},fake_user=True)
    return report

def activate():
    global SCENE
    if not SCENE:
        with bpy.data.libraries.load(ROOT+'/SourceArt/Blender/'+ASSET+'.blend',link=False) as (src,dst):dst.scenes=src.scenes
        SCENE=dst.scenes[0]
    bpy.context.window.scene=SCENE;return SCENE

def render():
    s=activate();old=L.EVIDENCE;L.EVIDENCE=OUT
    try:return L.sheet(ASSET,[o for o in s.objects if o.type=='MESH'],views=('iso','top'),res=640)
    finally:L.EVIDENCE=old

def finish():
    s=activate();objs=[o for o in s.objects if o.type=='MESH']
    samples=[dict(zip(('x','y','z'),o.matrix_world@v.co)) for o in objs for v in list(o.data.vertices)[::max(1,len(o.data.vertices)//64)]]
    json.dump({'vertices':samples},open(OUT+'/source_coordinates.json','w'))
    old=L.TEX_DIR;L.TEX_DIR=OUT
    try:maps=L.bake_pbr(objs,ASSET,size=1024,samples=24)
    finally:L.TEX_DIR=old
    for key,path in maps.items():
        img=bpy.data.images.load(path,check_existing=False);img.pack();n=objs[0].data.materials[0].node_tree.nodes.new('ShaderNodeTexImage');n.image=img;n.label='Runtime baked '+key
        shutil.copy2(path,ROOT+'/EsneiderProtocoloLazaro/Assets/_Game/Art/Textures/'+os.path.basename(path))
    bpy.data.libraries.write(ROOT+'/SourceArt/Blender/'+ASSET+'.blend',{s},fake_user=True)
    backup=[(o,o.data) for o in objs];mat=objs[0].data.materials[0]
    try:
        for o,me in backup:
            o.data=me.copy();o.data.materials.clear();o.data.materials.append(mat)
            for p in o.data.polygons:p.material_index=0
        with L.ctx(objs[0],objs):bpy.ops.export_scene.fbx(filepath=ROOT+'/EsneiderProtocoloLazaro/Assets/_Game/Art/Models/'+ASSET+'.fbx',use_selection=True,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Z',axis_up='Y',object_types={'MESH'},bake_space_transform=True,mesh_smooth_type='FACE',use_mesh_modifiers=True,bake_anim=False,path_mode='STRIP',embed_textures=False)
    finally:
        for o,me in backup:o.data=me
    json.dump(maps,open(OUT+'/bake.json','w'),indent=2);return maps
