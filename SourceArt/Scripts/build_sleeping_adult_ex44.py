"""Original sleeping adult. Anatomical lofts, separate fingers and closed-eye face.
Run only in Blender via MCP; preserve existing scenes. The standing coordinate
contract is X lateral, -Y anterior, Z feet-to-head; Unity places it supine.
"""
import bpy,sys,os,math,json,shutil
from mathutils import Vector,Matrix
ROOT='C:/Users/HP/Documents/GitHub/proyectos-unity'
sys.path.insert(0,ROOT+'/SourceArt/Scripts')
import esn_lib as L
ASSET='HUM-01_AdultoDormido';FOLDER=ROOT+'/SourceArt/_evidence/EX-44/'+ASSET
SCENE=None;PARTS=[];BONES=[];COL=None;M={}

def resting_arm_point(point):
    p=Vector(point);p.x*=.96
    keys=[(.72,.16),(.94,.154),(1.15,.05),(1.30,0),(1.50,0)]
    delta=keys[0][1]
    for i in range(len(keys)-1):
        a,b=keys[i],keys[i+1]
        if a[0]<=p.z<=b[0]:delta=a[1]+(b[1]-a[1])*(p.z-a[0])/(b[0]-a[0]);break
        if p.z>b[0]:delta=b[1]
    p.y+=delta;return p

def is_arm(name):return name.startswith(('clavicle_','upperarm_','forearm_','hand_','finger','thumb_'))

def mesh(name,verts,faces,mat,bone,weights=None):
    data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.update()
    o=bpy.data.objects.new('GEO-HUM01-'+name,data);COL.objects.link(o);o.data.materials.append(M[mat])
    for p in data.polygons:p.use_smooth=True
    if weights:
        groups={n:o.vertex_groups.new(name=n) for n in {n for row in weights for n in row}}
        for i,row in enumerate(weights):
            for n,w in row.items():
                if w>0:groups[n].add([i],w,'REPLACE')
    else:o.vertex_groups.new(name=bone).add(list(range(len(verts))),1,'REPLACE')
    o['atlas']='cloth' if mat in ('cloth','seam','sock') else 'skin';PARTS.append(o);return o

def sphere(name,pos,scale,mat,bone,segs=20,rings=12):
    o=L.sphere('GEO-HUM01-'+name,1,pos,COL,segs=segs,rings=rings,scale=scale);L.apply_all(o)
    o.data.transform(o.matrix_world);o.matrix_world=Matrix.Identity(4);L.assign(o,M[mat])
    for p in o.data.polygons:p.use_smooth=True
    o.vertex_groups.new(name=bone).add(list(range(len(o.data.vertices))),1,'REPLACE')
    o['atlas']='cloth' if mat in ('cloth','seam','sock') else 'skin';PARTS.append(o);return o

def tube(name,points,radii,mat,bone,sides=12):
    points=[Vector(p) for p in points];verts=[];faces=[]
    for j,p in enumerate(points):
        tangent=(points[min(j+1,len(points)-1)]-points[max(j-1,0)]).normalized()
        right=tangent.cross(Vector((0,1,0)))
        if right.length<.01:right=tangent.cross(Vector((1,0,0)))
        right.normalize();other=tangent.cross(right).normalized();r=radii[j] if isinstance(radii,list) else radii
        rx,ry=r if isinstance(r,(tuple,list)) else (r,r)
        for i in range(sides):
            a=math.tau*i/sides;verts.append(tuple(p+right*(rx*math.cos(a))+other*(ry*math.sin(a))))
    for j in range(len(points)-1):
        for i in range(sides):a=j*sides+i;b=j*sides+(i+1)%sides;faces.append((a,b,b+sides,a+sides))
    faces.extend([tuple(reversed(range(sides))),tuple((len(points)-1)*sides+i for i in range(sides))])
    return mesh(name,verts,faces,mat,bone)

def loft(name,rings,mat,bone,sides=32,breath_weights=False,folds=0):
    # Rings are (z, half-width, half-depth, center-x, center-y).
    verts=[];faces=[];weights=[]
    for j,(z,rx,ry,cx,cy) in enumerate(rings):
        for i in range(sides):
            a=math.tau*i/sides;fold=folds*(.65*math.sin(a*7+j*.9)+.35*math.sin(a*11-j*.6))
            verts.append((cx+(rx+fold)*math.sin(a),cy-(ry+fold*.5)*math.cos(a),z))
            if breath_weights:
                upper=max(0,min(1,(z-1.03)/.35));lower=max(0,min(1,(z-.83)/.24))
                weights.append({'pelvis':1-lower,'spine':lower*(1-upper),'chest':lower*upper})
    for j in range(len(rings)-1):
        for i in range(sides):a=j*sides+i;b=j*sides+(i+1)%sides;faces.append((a,b,b+sides,a+sides))
    faces.extend([tuple(reversed(range(sides))),tuple((len(rings)-1)*sides+i for i in range(sides))])
    return mesh(name,verts,faces,mat,bone,weights if breath_weights else None)

HEAD=[(1.535,.026,.031,.004),(1.55,.041,.050,-.004),(1.573,.059,.061,.0),(1.60,.071,.069,.004),
      (1.628,.081,.078,.010),(1.652,.082,.081,.013),(1.677,.079,.087,.016),(1.704,.078,.090,.018),
      (1.732,.076,.088,.020),(1.757,.067,.078,.022),(1.779,.047,.056,.022),(1.792,.017,.022,.020),(1.795,.001,.001,.020)]
def head_profile(z):
    for i in range(len(HEAD)-1):
        a,b=HEAD[i],HEAD[i+1]
        if a[0]<=z<=b[0]:
            t=(z-a[0])/(b[0]-a[0]);return tuple(a[k]*(1-t)+b[k]*t for k in (1,2,3))
    return HEAD[0][1:] if z<HEAD[0][0] else HEAD[-1][1:]
def bump(x,z):
    g=lambda cx,cz,sx,sz:math.exp(-((x-cx)/sx)**2-((z-cz)/sz)**2)
    return (.029*g(0,1.646,.018,.016)+.016*g(0,1.677,.013,.031)
            +.004*g(0,1.58,.030,.014)+.004*g(0,1.61,.025,.016)
            +sum(.009*g(s*.049,1.637,.027,.019)-.008*g(s*.032,1.669,.021,.011) for s in (-1,1)))
def face_y(x,z):
    rx,ry,cy=head_profile(z);return cy-ry*math.sqrt(max(0,1-(x/rx)**2))-bump(x,z)
def head():
    verts=[];faces=[];sides=64;levels=36
    for j in range(levels):
        z=1.535+(1.795-1.535)*j/(levels-1);rx,ry,cy=head_profile(z)
        for i in range(sides):
            a=math.tau*i/sides;x=rx*math.sin(a);y=cy-ry*math.cos(a)
            if math.cos(a)>0:y-=bump(x,z)*max(0,math.cos(a))**3
            verts.append((x,y,z))
    for j in range(levels-1):
        for i in range(sides):a=j*sides+i;b=j*sides+(i+1)%sides;faces.append((a,b,b+sides,a+sides))
    faces.extend([tuple(reversed(range(sides))),tuple((levels-1)*sides+i for i in range(sides))]);mesh('head_surface',verts,faces,'skin','head')
    for s in (-1,1):
        # Lids follow the face surface rather than adding exposed eyeballs.
        xs=[s*.032+(-.022+i*.044/12) for i in range(13)]
        points=[(x,face_y(x,1.668)-.0012,1.668-.003*math.sin(math.pi*i/12)) for i,x in enumerate(xs)]
        tube('closed_lid_'+str(s),points,[.0004+.00045*math.sin(math.pi*i/12) for i in range(13)],'crease','head',6)
        brow=[(x,face_y(x,1.692)-.001,1.690+.004*math.sin(math.pi*i/12)) for i,x in enumerate(xs)]
        tube('brow_'+str(s),brow,[.0004+.0015*math.sin(math.pi*i/12) for i in range(13)],'hair','head',6)
        sphere('ear_'+str(s),(s*.081,.015,1.651),(.015,.021,.029),'skin','head',16,10)
        sphere('ear_concha_'+str(s),(s*.090,-.0005,1.651),(.006,.004,.014),'lip','head',12,8)
        helix=[(s*(.088+.007*math.sin(math.pi*i/12)),.013-.015*math.cos(math.tau*i/18),1.651+.023*math.sin(math.tau*i/18)) for i in range(19)]
        tube('ear_helix_'+str(s),helix,.0022,'skin','head',6)
        sphere('nostril_'+str(s),(s*.011,face_y(s*.011,1.638)-.001,1.638),(.0035,.001,.0018),'crease','head',12,6)
    for dz,name in ((.0018,'upper_lip'),(-.002,'lower_lip')):
        points=[]
        for i in range(17):
            x=-.023+i*.046/16;z=1.605+dz-.0015*math.cos(x/.023*math.pi);points.append((x,face_y(x,z)-.0012,z))
        tube(name,points,[.0003+.0015*math.sin(math.pi*i/16) for i in range(17)],'lip','head',8)
    points=[(x,face_y(x,1.605)-.0014,1.605-.0015*math.cos(x/.023*math.pi)) for x in [-.023+i*.046/16 for i in range(17)]]
    tube('mouth_rest',points,.0005,'crease','head',6)

def build():
    global SCENE,COL,PARTS,BONES,M
    SCENE=bpy.data.scenes.new('EX44_'+ASSET);bpy.context.window.scene=SCENE;SCENE.unit_settings.system='METRIC';SCENE.unit_settings.scale_length=1
    COL=bpy.data.collections.new('EXPORT_'+ASSET);SCENE.collection.children.link(COL);PARTS=[]
    M={
        'skin':L.material(ASSET+'_skin',(.34,.235,.18),.60,0,bump=.006,scale=190,edge_wear=0,ao=0),
        'lip':L.material(ASSET+'_lips',(.29,.155,.12),.65,0,edge_wear=0,ao=0),
        'crease':L.material(ASSET+'_crease',(.075,.038,.023),.8,0,edge_wear=0,ao=0),
        'hair':L.material(ASSET+'_brow',(.048,.035,.025),.85,0,edge_wear=0,ao=0),
        'nail':L.material(ASSET+'_nail',(.41,.30,.235),.45,0,edge_wear=0,ao=0),
        'cloth':L.material(ASSET+'_gown',(.20,.285,.26),.93,0,bump=.018,scale=240,edge_wear=0,ao=0),
        'seam':L.material(ASSET+'_seam',(.14,.20,.18),.94,0,bump=.01,scale=240,edge_wear=0,ao=0),
        'sock':L.material(ASSET+'_trousers',(.27,.30,.28),.95,0,bump=.015,scale=220,edge_wear=0,ao=0)}
    BONES=[('root',(0,0,0),(0,0,.15),None),('pelvis',(0,0,.86),(0,0,1.02),'root'),('spine',(0,0,1.02),(0,0,1.26),'pelvis'),('chest',(0,0,1.26),(0,0,1.46),'spine'),('neck',(0,0,1.46),(0,0,1.56),'chest'),('head',(0,0,1.56),(0,0,1.78),'neck')]
    # Neck joins beneath jaw and the gown collar with an anatomical taper.
    loft('neck',[(1.435,.056,.053,0,.016),(1.49,.047,.049,0,.012),(1.54,.043,.046,0,.009),(1.57,.045,.05,0,.008)],'skin','neck',24)
    head()
    # Hospital trousers and a loose short-sleeved gown; no naked body proxy.
    loft('gown',[(.72,.20,.112,0,.014),(.76,.198,.117,0,.012),(.84,.185,.120,0,.008),(.93,.168,.113,0,.007),(1.02,.15,.098,0,.01),(1.10,.159,.109,0,.005),(1.20,.183,.12,0,0),(1.31,.21,.123,0,0),(1.39,.224,.109,0,.0),(1.435,.208,.087,0,.008),(1.466,.128,.062,0,.008),(1.475,.062,.052,0,.01)],'cloth','spine',40,True,.003)
    for z,rx,ry in ((.729,.20,.115),(1.467,.061,.051)):
        tube('gown_hem',[(rx*math.sin(a),.01-ry*math.cos(a),z) for a in [math.tau*i/40 for i in range(41)]],.002,'seam','pelvis' if z<1 else 'chest',6)
    # Side seam follows the torso, avoiding a mechanically straight stripe.
    for s in (-1,1):
        tube('side_seam',[(s*.199,.021,.735),(s*.183,.016,.84),(s*.161,.011,1.03),(s*.177,.015,1.19),(s*.219,.012,1.38)],.0015,'seam','spine',6)
    for s,side in ((-1,'L'),(1,'R')):
        hip=(s*.10,.018,.92);knee=(s*.112,.005,.50);ankle=(s*.119,.027,.10)
        BONES.extend([(f'thigh_{side}',hip,knee,'pelvis'),(f'shin_{side}',knee,ankle,f'thigh_{side}'),(f'foot_{side}',ankle,(s*.12,-.16,.05),f'shin_{side}')])
        loft('trouser_'+side,[(.09,.045,.046,s*.119,.024),(.15,.047,.048,s*.12,.02),(.26,.062,.065,s*.12,.018),(.38,.074,.069,s*.116,.015),(.49,.067,.064,s*.112,.005),(.54,.073,.068,s*.11,.0),(.67,.080,.079,s*.095,.01),(.79,.079,.080,s*.081,.015),(.90,.071,.078,s*.079,.018)],'sock',f'thigh_{side}',28,False,.002)
        # Smoothly distribute the lower leg around the knee instead of rigid trouser deformation.
        leg=PARTS[-1];leg.vertex_groups.clear();a=leg.vertex_groups.new(name=f'thigh_{side}');b=leg.vertex_groups.new(name=f'shin_{side}')
        for v in leg.data.vertices:
            t=max(0,min(1,(v.co.z-.44)/.14));a.add([v.index],t,'REPLACE');b.add([v.index],1-t,'REPLACE')
        sphere('foot_'+side,(s*.12,-.061,.058),(.049,.119,.055),'skin',f'foot_{side}',24,14)
        for i in range(5):
            x=s*(.084+i*.018);y=-.156+.004*i;r=.012 if i==0 else .009
            sphere('toe_'+side+str(i),(x,y,.047),(r,.029-i*.002,.018),'skin',f'foot_{side}',12,8)
        shoulder=(s*.205,.007,1.40);elbow=(s*.298,.015,1.15);wrist=(s*(.30 if s<0 else .28),-.043,.927)
        BONES.extend([(f'clavicle_{side}',(0,0,1.44),shoulder,'chest'),(f'upperarm_{side}',shoulder,elbow,f'clavicle_{side}'),(f'forearm_{side}',elbow,wrist,f'upperarm_{side}'),(f'hand_{side}',wrist,(wrist[0],-.055,.842),f'forearm_{side}')])
        tube('sleeve_'+side,[(s*.135,.007,1.382),(s*.184,.008,1.387),(s*.218,.009,1.368),(s*.241,.010,1.333),(s*.260,.012,1.29),(s*.276,.013,1.254)],[.060,.074,.080,.079,.075,.07],'cloth',f'upperarm_{side}',24)
        tube('arm_'+side,[(s*.258,.012,1.30),(s*.28,.014,1.24),elbow,(s*.304,-.004,1.087),(wrist[0],-.026,1.005),wrist],[.059,.055,.043,.047,.035,.027],'skin',f'forearm_{side}',24)
        # Forearm surface blends across elbow; upper vertices follow humerus.
        arm=PARTS[-1];arm.vertex_groups.clear();ga=arm.vertex_groups.new(name=f'upperarm_{side}');gb=arm.vertex_groups.new(name=f'forearm_{side}')
        for v in arm.data.vertices:
            t=max(0,min(1,(v.co.z-1.10)/.12));ga.add([v.index],t,'REPLACE');gb.add([v.index],1-t,'REPLACE')
        palm=(wrist[0],-.051,.876)
        loft('palm_'+side,[(.837,.032,.016,palm[0],-.053),(.855,.037,.019,palm[0],-.053),(.879,.039,.022,palm[0],-.052),(.90,.034,.021,palm[0],-.049),(.925,.026,.019,palm[0],-.043),(.936,.023,.018,palm[0],-.041)],'skin',f'hand_{side}',24)
        for i in range(4):
            x=palm[0]+s*(-.027+i*.018);start=(x,-.053,.843);length=[.069,.079,.074,.058][i]
            end=(x+s*.003,-.075,.843-length)
            bone=f'finger{i}_{side}';BONES.append((bone,start,end,f'hand_{side}'))
            points=[(x,-.053,.852),(x,-.054,.841),(x+s*.001,-.058,.82),(x+s*.002,-.068,.843-length*.73),end,(end[0],end[1],end[2]-.003)]
            tube('finger_'+side+str(i),points,[.0095,.0095,.009,.008,.006,.0015],'skin',bone,10)
            sphere('nail_'+side+str(i),(end[0],end[1]-.006,end[2]+.009),(.0048,.0018,.008),'nail',bone,12,6)
        start=(palm[0]-s*.032,-.054,.888);end=(palm[0]-s*.059,-.075,.838);bone=f'thumb_{side}'
        BONES.append((bone,start,end,f'hand_{side}'))
        tube('thumb_'+side,[start,(palm[0]-s*.046,-.061,.871),(palm[0]-s*.057,-.072,.848),end],[.016,.014,.011,.005],'skin',bone,12)
    # Supine-ready rest pose: forearms and palms lie towards the support plane.
    for o in PARTS:
        if any(is_arm(g.name) for g in o.vertex_groups):
            for v in o.data.vertices:v.co=resting_arm_point(v.co)
    BONES=[(n,tuple(resting_arm_point(h)),tuple(resting_arm_point(t)),p) if is_arm(n) else (n,h,t,p) for n,h,t,p in BONES]
    # Create the 30-bone source rig and keep two atlas groups for skin and clothing.
    rig=L.armature('RIG-HUM01',[(n,h,t,p,(0,-1,0)) for n,h,t,p in BONES],COL)
    return finish_geometry(rig)

def finish_geometry(rig):
    bpy.context.view_layer.update();merged=[]
    for atlas in ('skin','cloth'):
        objects=[o for o in SCENE.objects if o.type=='MESH' and o.get('atlas')==atlas];o=L.join(objects,'GEO-HUM01-'+atlas.title());L.apply_all(o)
        o.data.transform(o.matrix_world);o.matrix_world=Matrix.Identity(4);L.uv_project(o,margin=.008)
        o.parent=rig;m=o.modifiers.new('Subject rig','ARMATURE');m.object=rig;merged.append(o)
    os.makedirs(FOLDER,exist_ok=True);tris=0
    for o in merged:o.data.calc_loop_triangles();tris+=len(o.data.loop_triangles)
    report={'asset':ASSET,'triangles':tris,'bones':len(BONES),'mesh_count':2,'texture_sets':2,'height_m':1.795,'pose':'source rest pose; supine placement pending','features':['closed-eye anatomical face','separate fingers and thumbs','bare feet and toes','loose gown with collar and hem','separate trousers','30-bone weighted source rig'],'state':'En produccion'}
    open(FOLDER+'/geometry.json','w').write(json.dumps(report,indent=2));save();return report

def save():bpy.data.libraries.write(ROOT+'/SourceArt/Blender/'+ASSET+'.blend',{SCENE},fake_user=True)
def render():
    bpy.context.window.scene=SCENE;old=L.EVIDENCE;L.EVIDENCE=FOLDER
    try:return L.sheet(ASSET,[o for o in SCENE.objects if o.type=='MESH'],views=('front','side','iso'),res=900)
    finally:L.EVIDENCE=old

def bake(atlas):
    bpy.context.window.scene=SCENE;rig=next(o for o in SCENE.objects if o.type=='ARMATURE');rig.data.pose_position='REST'
    obj=next(o for o in SCENE.objects if o.type=='MESH' and atlas.title() in o.name)
    old=L.TEX_DIR;L.TEX_DIR=FOLDER
    try:maps=L.bake_pbr([obj],ASSET+'_'+atlas.title(),size=1024,samples=24,margin=2)
    finally:L.TEX_DIR=old
    for suffix,path in maps.items():
        img=bpy.data.images.load(path,check_existing=False);img.pack();node=obj.data.materials[0].node_tree.nodes.new('ShaderNodeTexImage');node.image=img;node.label='Runtime baked '+suffix
        shutil.copy2(path,ROOT+'/EsneiderProtocoloLazaro/Assets/_Game/Art/Textures/'+os.path.basename(path))
    save();open(FOLDER+'/bake_'+atlas+'.json','w').write(json.dumps(maps,indent=2));return maps

def animate():
    bpy.context.window.scene=SCENE;rig=next(o for o in SCENE.objects if o.type=='ARMATURE');rig.data.pose_position='POSE'
    # Connected edit bones suppress pose translation; breathing needs a soft
    # skinned offset, while parenting still preserves the skeletal hierarchy.
    with L.ctx(rig):
        bpy.ops.object.mode_set(mode='EDIT')
        for name in ('chest','neck'):rig.data.edit_bones[name].use_connect=False
        bpy.ops.object.mode_set(mode='OBJECT')
    rig.animation_data_clear();SCENE.render.fps=30;SCENE.frame_start=1;SCENE.frame_end=151
    # 5-second breathing cycle. Neck counter-translation keeps the head supported.
    # Bone Z is aligned to anterior -Y by the source roll contract.
    zero=(0,0,0);poses={}
    for frame,amount in ((1,0),(31,.4),(61,1),(91,.65),(121,.15),(151,0)):
        poses[frame]={'chest':(zero,(0,0,.0028*amount)),'neck':(zero,(0,0,-.0028*amount))}
    action=L.action(rig,'HUM01_Sleep_Breathe',151,poses=poses);L.push_nla(rig,action);L.enable_nla(rig);SCENE.frame_set(1)
    save();return {'clip':action.name,'seconds':5,'anterior_chest_travel_m':.0028}

def export():
    bpy.context.window.scene=SCENE;SCENE.frame_set(1)
    rig=next(o for o in SCENE.objects if o.type=='ARMATURE');rig.data.pose_position='POSE';L.enable_nla(rig)
    objects=[o for o in SCENE.objects if o.type=='MESH'];backups=[]
    # One material slot per atlas. Preserve all source shader recipes in the blend.
    for o in objects:
        backups.append((o,o.data));o.data=o.data.copy();mat=o.data.materials[0];o.data.materials.clear();o.data.materials.append(mat)
        for face in o.data.polygons:face.material_index=0
    try:
        with L.ctx(objects[0],objects+[rig]):
            bpy.ops.export_scene.fbx(filepath=ROOT+'/EsneiderProtocoloLazaro/Assets/_Game/Art/Models/'+ASSET+'.fbx',use_selection=True,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Z',axis_up='Y',object_types={'MESH','ARMATURE'},add_leaf_bones=False,bake_space_transform=True,mesh_smooth_type='FACE',use_mesh_modifiers=True,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=True,bake_anim_use_all_bones=True,bake_anim_simplify_factor=0,path_mode='STRIP',embed_textures=False)
    finally:
        for o,meshdata in backups:o.data=meshdata
    samples=[dict(zip(('x','y','z'),o.matrix_world@v.co)) for o in objects for v in list(o.data.vertices)[::max(1,len(o.data.vertices)//48)]]
    open(FOLDER+'/source_coordinates.json','w').write(json.dumps({'vertices':samples}))
    report=json.load(open(FOLDER+'/geometry.json'));report['unweighted_vertices']=sum(sum(g.weight for g in v.groups)<.999 for o in objects for v in o.data.vertices)
    report['clips']=[strip.action.name for track in rig.animation_data.nla_tracks for strip in track.strips];report['pose']='source rest pose with subtle breathing; supine placement pending'
    open(FOLDER+'/geometry.json','w').write(json.dumps(report,indent=2));save();return report

SUPPORT_BATCH=None
def build_supports():
    """Separate camilla accessories; never export room props with the subject rig."""
    global SUPPORT_BATCH
    from esn_delivery import Batch
    from build_clinic_fixtures_ex23 import FixtureBuilder
    name='HUM-01_ApoyosCamilla';b=FixtureBuilder('SUPPORT','ApoyosCamilla','EX44');b.asset=name
    b.m['fabric']=L.material(name+'_cloth',(.31,.36,.33),.96,0,bump=.015,scale=220,edge_wear=0,ao=0)
    for label,cx,length,width,height in [('topper',0,1.87,.68,.054),('head',-.79,.36,.36,.030),('calves',.55,.32,.43,.055),('heels',.842,.23,.44,.067)]:
        nx=12;ny=10;verts=[];faces=[];count=(nx+1)*(ny+1)
        for layer in (0,1):
            for j in range(ny+1):
                v=-1+2*j/ny
                for i in range(nx+1):
                    u=-1+2*i/nx;dome=min(1,(6 if label=='topper' else 2.3)*(1-u*u)*(1-v*v))
                    base=.764 if label=='topper' else .809
                    z=base+( .004+height*dome+.0015*math.sin(u*16+v*6)*dome if layer else 0)
                    verts.append((cx+u*length*.5,v*width*.5,z))
        for layer in (0,1):
            for j in range(ny):
                for i in range(nx):
                    a=layer*count+j*(nx+1)+i;q=(a,a+1,a+nx+2,a+nx+1);faces.append(q if layer else tuple(reversed(q)))
        boundary=list(range(nx+1))+[j*(nx+1)+nx for j in range(1,ny+1)]+[ny*(nx+1)+i for i in range(nx-1,-1,-1)]+[j*(nx+1) for j in range(ny-1,0,-1)]
        for k,a in enumerate(boundary):c=boundary[(k+1)%len(boundary)];faces.append((a,c,c+count,a+count))
        data=bpy.data.meshes.new(label);data.from_pydata(verts,[],faces);data.update();o=bpy.data.objects.new('GEO-HUM01-support_'+label,data);b.col.objects.link(o);L.assign(o,b.m['fabric']);b.parts.append(o)
        for p in data.polygons:p.use_smooth=True
    b.features=['pressure mattress topper resting on actual mattress surface','separate head pad','calf support','heel support','sealed cloth sidewall'];b.collision=[]
    SUPPORT_BATCH=Batch('EX-44',{'SUPPORT':'ApoyosCamilla'});SUPPORT_BATCH.asset=lambda _:name
    return SUPPORT_BATCH.save(b)
def finish_supports():return SUPPORT_BATCH.finish('SUPPORT',size=512,margin=3)
