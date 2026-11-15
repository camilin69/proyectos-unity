"""Original 1.6 m guarded axial fan; separate housing and balanced rotor."""
import bpy,sys,math,json,os,shutil
from mathutils import Vector,Matrix
ROOT='C:/Users/HP/Documents/GitHub/proyectos-unity'
sys.path.insert(0,ROOT+'/SourceArt/Scripts')
import esn_lib as L
from build_clinic_fixtures_ex23 import FixtureBuilder
ASSET='OBJ-079_VentiladorIndustrial';FOLDER=ROOT+'/SourceArt/_evidence/EX-37/'+ASSET
PIVOT=Vector((0,0,.85));SCENE=None
def mesh(b,name,verts,faces,mat):
    m=bpy.data.meshes.new(name);m.from_pydata(verts,[],faces);m.update();o=bpy.data.objects.new('GEO-079-'+name,m);b.col.objects.link(o);L.assign(o,b.m[mat]);b.parts.append(o);return o
def ring(b,name,ro,ri,y,depth,mat='paint',n=48):
    verts=[];faces=[]
    for radius,yy in [(ro,y-depth/2),(ro,y+depth/2),(ri,y-depth/2),(ri,y+depth/2)]:
        verts.extend((radius*math.cos(i*math.tau/n),yy,.85+radius*math.sin(i*math.tau/n)) for i in range(n))
    for i in range(n):
        j=(i+1)%n
        faces.extend([(i,j,n+j,n+i),(2*n+j,2*n+i,3*n+i,3*n+j),(j,i,2*n+i,2*n+j),(n+i,n+j,3*n+j,3*n+i)])
    return mesh(b,name,verts,faces,mat)
def build():
    global SCENE
    b=FixtureBuilder('079','VentiladorIndustrial','EX37');groups=[]
    b.m['blade']=L.material(ASSET+'_blades',(.20,.24,.22),.62,.7,wear=.03,wear_color=(.3,.29,.25),bump=.015,scale=30)
    def freeze(name,pivot):
        bpy.context.view_layer.update();o=L.join(b.parts,'GEO-079-'+name);L.apply_all(o);o.data.transform(o.matrix_world);o.matrix_world=Matrix.Identity(4);o.data.transform(Matrix.Translation(-Vector(pivot)));o.location=pivot;L.smooth(o,35);groups.append(o);b.parts=[];return o
    ring(b,'duct_shell',.75,.70,0,.30)
    for y in (-.154,.154):ring(b,'duct_flange',.80,.68,y,.020,'steel')
    for y in (-.192,.192):
        ring(b,'guard_rim',.672,.66,y,.012,'dark',40)
        for x in (-.48,-.32,-.16,0,.16,.32,.48):
            h=2*math.sqrt(.665**2-x*x)
            if y>0 and x==0:
                for sign in (-1,1):b.box('guard_vertical',(.009,.010,.485),(0,y,.85+sign*.4225),'steel',0)
            else:b.box('guard_vertical',(.009,.010,h),(x,y,.85),'steel',0)
        for z in (-.48,-.32,-.16,0,.16,.32,.48):
            w=2*math.sqrt(.665**2-z*z)
            if y>0 and z==0:
                for sign in (-1,1):b.box('guard_horizontal',(.485,.010,.009),(sign*.4225,y,.85),'steel',0)
            else:b.box('guard_horizontal',(w,.010,.009),(0,y,.85+z),'steel',0)
        if y>0:ring(b,'shaft_clearance_guard',.18,.17,y,.012,'dark',24)
    for i in range(8):
        a=i*math.tau/8;x=.765*math.cos(a);z=.85+.765*math.sin(a)
        b.cyl('flange_bolt',.016,.032,(x,-.163,z),'steel','Y',8)
    for x in (-.52,.52):
        b.box('foot',(.22,.45,.04),(x,0,.020),'steel',.001)
        b.box('upright',(.07,.16,.24),(x,0,.15),'paint',.001)
        for y in (-.17,.17):b.cyl('floor_anchor',.018,.025,(x,y,.0525),'steel','Z',8)
    b.cyl('motor_body',.14,.22,(0,.30,.85),'paint','Y',24)
    b.cyl('motor_cap',.15,.032,(0,.422,.85),'dark','Y',24)
    for i in range(3):
        a=i*math.tau/3
        b.tube('motor_brace',[(.11*math.cos(a),.30,.85+.11*math.sin(a)),(.72*math.cos(a),.154,.85+.72*math.sin(a))],.018,'steel')
    b.box('terminal_box',(.10,.12,.08),(.12,.32,.94),'dark',.001)
    b.tube('supply_lead',[(.16,.34,.94),(.24,.32,.95),(.3,.25,.91),(.38,.16,.84)],.008,'dark')
    freeze('Housing',(0,0,0))
    b.cyl('hub',.13,.14,(0,0,.85),'steel','Y',24)
    b.cyl('drive_shaft',.035,.23,(0,.145,.85),'steel','Y',12)
    b.cyl('hub_nose',.10,.035,(0,-.083,.85),'paint','Y',24)
    for blade in range(6):
        verts=[];faces=[];angle=blade*math.tau/6
        # Swept, pitched sheet blades, with a finite 6 mm edge thickness.
        for side in (-1,1):
            for k in range(4):
                r=.10+k*.175;twist=.050*(1-k/4);sweep=.22*k/3
                for edge in (-1,1):
                    a=angle+sweep+edge*(.24-.04*k/3)
                    verts.append((r*math.cos(a),edge*twist+side*.003,.85+r*math.sin(a)))
        for k in range(3):
            a=2*k;faces.extend([(a,a+2,a+3,a+1),(a+8,a+9,a+11,a+10),(a,a+8,a+10,a+2),(a+1,a+3,a+11,a+9)])
        faces.extend([(0,1,9,8),(6,14,15,7)]);mesh(b,'blade_'+str(blade),verts,faces,'blade')
    freeze('Rotor',PIVOT);L.uv_project_all(groups)
    tris=0
    for o in groups:o.data.calc_loop_triangles();tris+=len(o.data.loop_triangles)
    points=[o.matrix_world@v.co for o in groups for v in o.data.vertices]
    report={'asset':ASSET,'triangles':tris,'mesh_count':2,'texture_sets':1,'dimensions_blender':[max(v[i] for v in points)-min(v[i] for v in points) for i in range(3)],'pivots_blender':{'Rotor':list(PIVOT)},'collision_boxes_blender':[], 'features':['hollow duct housing and bolted flanges','front and rear protective grids','six pitched swept blades with thickness','independent rotor pivot','rear motor, braces and terminal cable','four floor anchors'],'state':'En produccion'}
    os.makedirs(FOLDER,exist_ok=True);open(FOLDER+'/geometry.json','w').write(json.dumps(report,indent=2));SCENE=b.scene
    bpy.data.libraries.write(ROOT+'/SourceArt/Blender/'+ASSET+'.blend',{SCENE},fake_user=True);return report
def activate():
    global SCENE
    if SCENE is None:
        with bpy.data.libraries.load(ROOT+'/SourceArt/Blender/'+ASSET+'.blend',link=False) as (src,dst):dst.scenes=src.scenes
        SCENE=dst.scenes[0]
    bpy.context.window.scene=SCENE;return SCENE
def render():
    s=activate();old=L.EVIDENCE;L.EVIDENCE=FOLDER
    try:return L.sheet(ASSET,[o for o in s.objects if o.type=='MESH'],views=('iso',),res=640)
    finally:L.EVIDENCE=old
def finish():
    s=activate();objs=[o for o in s.objects if o.type=='MESH']
    samples=[dict(zip(('x','y','z'),o.matrix_world@v.co)) for o in objs for v in list(o.data.vertices)[::max(1,len(o.data.vertices)//32)]]
    open(FOLDER+'/source_coordinates.json','w').write(json.dumps({'vertices':samples}));old=L.TEX_DIR;L.TEX_DIR=FOLDER
    try:maps=L.bake_pbr(objs,ASSET,size=1024,samples=24,margin=3)
    finally:L.TEX_DIR=old
    for suffix,path in maps.items():
        img=bpy.data.images.load(path,check_existing=False);img.pack();node=objs[0].data.materials[0].node_tree.nodes.new('ShaderNodeTexImage');node.image=img;node.label='Runtime baked '+suffix
        shutil.copy2(path,ROOT+'/EsneiderProtocoloLazaro/Assets/_Game/Art/Textures/'+os.path.basename(path))
    bpy.data.libraries.write(ROOT+'/SourceArt/Blender/'+ASSET+'.blend',{s},fake_user=True);backups=[(o,o.data) for o in objs];mat=objs[0].data.materials[0]
    try:
        for o,data in backups:
            o.data=data.copy();o.data.materials.clear();o.data.materials.append(mat)
            for f in o.data.polygons:f.material_index=0
        with L.ctx(objs[0],objs):bpy.ops.export_scene.fbx(filepath=ROOT+'/EsneiderProtocoloLazaro/Assets/_Game/Art/Models/'+ASSET+'.fbx',use_selection=True,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Z',axis_up='Y',object_types={'MESH'},bake_space_transform=True,mesh_smooth_type='FACE',use_mesh_modifiers=True,bake_anim=False,path_mode='STRIP',embed_textures=False)
    finally:
        for o,data in backups:o.data=data
    open(FOLDER+'/bake.json','w').write(json.dumps(maps,indent=2));return maps
