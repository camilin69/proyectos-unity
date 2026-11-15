"""Original catalogue furniture. Execute build(id), render(id), finish(id) in Blender MCP.
Each recipe encodes the assembly and collision volumes of its own object sheet.
Existing scenes are preserved; bakes are material-to-atlas, not high/low sculpt bakes.
"""
import bpy,sys,os,json,math,shutil
from mathutils import Vector,Matrix
ROOT='C:/Users/HP/Documents/GitHub/proyectos-unity'
sys.path.insert(0,ROOT+'/SourceArt/Scripts')
import esn_lib as L
ASSETS={'017':'BancoTrabajo','018':'Mordaza','028':'EstanteriaIndustrial','030':'ContenedorTecnico','038':'MesaOficina','039':'SillaUsada','072':'RackControl'}
SCENES={}

class Builder:
    def __init__(self,id,asset_name=None,series='EX13'):
        self.id=id; self.asset='OBJ-'+id+'_'+(asset_name or ASSETS[id])
        self.scene=bpy.data.scenes.new(series+'_'+self.asset);bpy.context.window.scene=self.scene
        self.scene.unit_settings.system='METRIC';self.scene.unit_settings.scale_length=1
        self.col=bpy.data.collections.new('EXPORT_'+self.asset);self.scene.collection.children.link(self.col)
        self.parts=[];self.collision=[];self.features=[]
        self.m={
            'paint':L.material(self.asset+'_enamel',(.11,.18,.18),.64,0,wear=.15,wear_color=(.24,.25,.23),bump=.055,scale=60),
            'steel':L.material(self.asset+'_steel',(.32,.34,.36),.5,1,bump=.025,scale=90),
            'dark':L.material(self.asset+'_rubber',(.018,.022,.023),.84,0,bump=.06,scale=100),
            'wood':L.material(self.asset+'_timber',(.23,.135,.075),.65,0,wear=.14,wear_color=(.34,.23,.12),bump=.04,scale=35),
            'ivory':L.material(self.asset+'_laminate',(.43,.44,.39),.68,0,wear=.08,wear_color=(.28,.28,.25),bump=.025,scale=65),
            'copper':L.material(self.asset+'_copper',(.30,.14,.07),.58,1),
            'label':L.material(self.asset+'_label',(.59,.57,.45),.81,0),
        }
    def box(self,n,size,pos,mat='paint',bevel=.004,collision=False,rot=None):
        o=L.box('GEO-'+self.id+'-'+n,size,pos,self.col,bevel=bevel,segs=1 if bevel<=.001 else 2)
        L.assign(o,self.m[mat]);self.parts.append(o)
        if rot:o.rotation_euler=rot
        if collision:self.collision.append({'center':list(pos),'size':list(size)})
        return o
    def cyl(self,n,r,depth,pos,mat='steel',axis='Z',verts=16):
        o=L.cyl('GEO-'+self.id+'-'+n,r,depth,pos,self.col,axis=axis,verts=min(verts,10) if r<=.009 else verts,bevel=0 if r<=.009 else min(.002,r*.1));L.assign(o,self.m[mat]);self.parts.append(o);return o
    def tube(self,n,points,r=.006,mat='dark'):
        o=L.tube('GEO-'+self.id+'-'+n,points,r,self.col,verts=8);L.assign(o,self.m[mat]);self.parts.append(o);return o
    def handle(self,x,y,z,length=.15):
        for dx in (-length/2,length/2):self.box('handle_mount',(.018,.025,.035),(x+dx,y,z),'steel',.003)
        self.box('handle_grip',(length,.023,.019),(x,y-.021,z),'steel',.007)
    def serial(self,x,y,z,w=.1):
        self.box('serial_plate',(w,.003,.035),(x,y,z),'label',.001)
        for i in range(7):self.box('serial_bar',(.002+(i%3)*.001,.001,.019),(x-w*.36+i*w*.11,y-.002,z),'dark',.0002)
    def foot(self,x,y,height):
        self.box('foot_pad',(.073,.073,.016),(x,y,.008),'dark',.003)
        self.box('square_tube',(.049,.049,height-.016),(x,y,(height+.016)/2),collision=True,bevel=.002)
    def vise(self,pos=(0,0,0)):
        x,y,z=pos
        self.box('vise_base',(.24,.18,.035),(x,y,z+.0175),'paint',.008,True)
        self.cyl('swivel',.08,.035,(x,y,z+.05))
        self.box('fixed_jaw_body',(.20,.055,.11),(x,y+.06,z+.118),'paint',.008,True)
        self.box('moving_jaw',(.20,.045,.10),(x,y-.04,z+.115),'paint',.007,True)
        for jy in (.031,-.015):self.box('jaw_insert',(.18,.009,.045),(x,y+jy,z+.15),'steel',.0015)
        self.cyl('lead_screw',.014,.235,(x,y-.035,z+.082),'steel','Y')
        for i in range(8):self.cyl('thread',.016,.002,(x,y-.105+i*.011,z+.082),'steel','Y',12)
        self.cyl('handle_hub',.025,.028,(x,y-.17,z+.082),'paint','Y')
        self.cyl('sliding_handle',.007,.19,(x,y-.19,z+.082),'steel','X',12)
        for sx in (-1,1):self.cyl('handle_stop',.011,.016,(x+sx*.10,y-.19,z+.082),'steel','X',12)
    def workbench(self):
        self.features=['load-bearing frame','thick worktop','vice with screw and handle','three drawers','lower shelf']
        for x in (-.87,.87):
            for y in (-.28,.28):self.foot(x,y,.85)
        self.box('thick_worktop',(2,.75,.055),(0,0,.8725),'wood',.01,True)
        for y in (-.30,.30):self.box('apron',(1.80,.035,.10),(0,y,.79),collision=True)
        self.box('lower_shelf',(1.75,.59,.025),(0,0,.17),collision=True)
        self.box('drawer_carcase',(.58,.57,.42),(.53,0,.60),'paint',.008,True)
        for z in (.46,.59,.72):
            self.box('drawer_front',(.55,.035,.12),(.53,-.307,z),'ivory',.003)
            self.handle(.53,-.331,z)
        self.serial(.53,-.33,.805,.12)
        self.vise((-.59,-.22,.90))
        for x in (-.87,.87):
            for y in (-.29,.29):self.cyl('top_bolt',.009,.0015,(x,y,.901),'steel','Z',12)
    def shelving(self):
        self.features=['four angle uprights','bolted shelf beams','cross braces','four supported loads','floor anchor plates']
        for x in (-1.20,1.20):
            for y in (-.255,.255):
                self.box('upright_flange',(.047,.017,2.78),(x,y,1.41),collision=True,bevel=.0015)
                self.box('upright_return',(.017,.047,2.78),(x-.015,y+.015,1.41),collision=True,bevel=.0015)
                self.box('floor_anchor',(.1,.10,.015),(x,y,.0075),'steel',.003,True)
                for z in (.28,.98,1.68,2.38):self.cyl('fixing',.007,.005,(x,y-.014,z),'steel','Y',12)
        for z in (.25,.95,1.65,2.35):
            self.box('shelf',(2.46,.58,.035),(0,0,z),collision=True)
            for y in (-.28,.28):self.box('beam',(2.46,.024,.065),(0,y,z-.045),collision=True)
        for a,b in [((-1.18,.276,.30),(1.18,.276,2.65)),((1.18,.278,.30),(-1.18,.278,2.65))]:
            mid=(Vector(a)+Vector(b))/2;length=(Vector(b)-Vector(a)).length
            o=self.box('diagonal_brace',(.023,.012,length),mid,'steel',.001)
            o.rotation_euler=(Vector(b)-Vector(a)).to_track_quat('Z','Y').to_euler()
        for x,z,w in [(-.62,.2675,.8),(.59,.9675,.9),(-.55,1.6675,.9),(.61,2.3675,.7)]:
            h=.32 if z>2 else .42
            self.box('supported_case',(w,.48,h),(x,0,z+h/2),'ivory',.009,True)
            for dx in (-w*.4,w*.4):self.box('case_band',(.025,.488,h+.005),(x+dx,0,z+h/2),'dark',.001)
            self.serial(x,-.244,z+h*.7)
    def container(self):
        self.features=['recessed transport panels','corner protectors','lid gasket','two latches','recessed handles','serial plate']
        self.box('sealed_body',(1.16,.76,.80),(0,0,.46),'paint',.014,True)
        self.box('gasket',(1.185,.785,.016),(0,0,.852),'dark',.005)
        self.box('lid',(1.20,.80,.036),(0,0,.882),'paint',.012,True)
        for x in (-.55,.55):
            for y in (-.35,.35):
                self.box('transport_foot',(.10,.10,.065),(x,y,.0325),'dark',.008,True)
                self.box('corner_guard',(.085,.085,.74),(x,y,.48),'steel',.006)
        for x in (-.48,-.24,0,.24,.48):self.box('panel_rib',(.035,.018,.60),(x,-.388,.45),'paint',.007)
        for x in (-.32,.32):
            self.box('latch_plate',(.075,.014,.16),(x,-.405,.76),'steel',.003)
            self.box('latch_toggle',(.045,.024,.095),(x,-.423,.75),'dark',.004)
        self.handle(0,-.413,.56,.23);self.serial(.23,-.412,.58,.14)
    def desk(self):
        self.features=['laminate top','edge band','steel legs','three drawers','cable grommet','modesty panel']
        self.box('edge_band',(1.6,.75,.039),(0,0,.726),'dark',.008)
        self.box('laminate_top',(1.592,.742,.03),(0,0,.735),'ivory',.007,True)
        for y in (-.28,.28):self.foot(-.67,y,.71)
        self.box('pedestal',(.43,.60,.67),(.54,0,.375),'paint',.006,True)
        self.box('plinth',(.39,.54,.035),(.54,0,.025),'dark',.005)
        for z in (.19,.39,.59):
            self.box('drawer',(.408,.024,.18),(.54,-.31,z),'ivory',.003)
            self.handle(.54,-.327,z+.015,.13)
        self.box('modesty_panel',(1.16,.022,.36),(-.08,.28,.49),'paint',.003,True)
        self.cyl('cable_grommet',.025,.0015,(-.53,.23,.751),'dark','Z',20)
        self.box('cable_slot',(.045,.005,.002),(-.53,.23,.752),'paint',.001)
        self.tube('rear_cable',[(-.53,.265,.72),(-.53,.315,.63),(-.55,.31,.20),(-.50,.29,.02)],.005)
    def chair(self):
        self.features=['five-spoke base','five castors contacting floor','gas lift','compressed seat','back shell','armrests','back supports']
        self.cyl('hub',.07,.08,(0,0,.16),'paint')
        self.cyl('gas_lift',.029,.25,(0,0,.29),'steel')
        for i in range(5):
            a=2*math.pi*i/5;x=.27*math.cos(a);y=.27*math.sin(a)
            self.box('radial_leg',(.29,.035,.026),(x*.50,y*.50,.125),'paint',.005,rot=(0,0,a))
            self.cyl('caster_axle',.012,.045,(x,y,.064),'steel','X',12)
            for dx in (-.017,.017):self.cyl('caster',.049,.016,(x+dx,y,.049),'dark','X',16)
        self.box('seat_pan',(.49,.47,.033),(0,0,.427),'paint',.013,True)
        self.box('seat_cushion',(.48,.46,.057),(0,0,.468),'dark',.019,True)
        for x in (-.16,.16):self.box('back_stay',(.025,.022,.39),(x,.207,.673),'paint',.003)
        self.box('back_shell',(.465,.032,.40),(0,.215,.80),'paint',.018,True)
        self.box('back_cushion',(.44,.052,.36),(0,.185,.8),'dark',.018)
        for x in (-.285,.285):
            self.box('arm_stay',(.02,.027,.18),(x,.08,.535),'paint',.003)
            self.box('arm_pad',(.060,.30,.035),(x,-.03,.641),'dark',.01,True)
        self.collision.append({'center':[0,0,.21],'size':[.58,.58,.40]})
    def rack(self):
        self.features=['cabinet frame','six rack modules','rack ears','fan grilles','service cable loom','serials','status lenses']
        for x in (-.365,.365):
            for y in (-.365,.365):self.box('rack_post',(.045,.045,2.12),(x,y,1.10),collision=True)
        for z in (.025,2.175):self.box('frame_cap',(.8,.8,.05),(0,0,z),collision=True)
        for x in (-.389,.389):self.box('side_skin',(.02,.73,2.08),(x,0,1.10),'paint',.004,True)
        self.box('rear_skin',(.75,.018,2.08),(0,.382,1.10),'paint',.004,True)
        for i,z in enumerate((.25,.55,.85,1.15,1.45,1.75)):
            self.box('equipment',(.65,.61,.26),(0,0,z),'dark',.006,True)
            self.box('module_face',(.70,.018,.25),(0,-.329,z),'paint' if i%2 else 'steel',.003)
            for x in (-.335,.335):
                for dz in (-.09,.09):self.cyl('rack_screw',.006,.004,(x,-.341,z+dz),'steel','Y',12)
            self.serial(-.17,-.341,z+.075,.12)
            for x in (.035,.105,.175):
                self.cyl('fan_recess',.041,.005,(x,-.341,z-.025),'dark','Y',16)
                for dz in (-.027,-.009,.009,.027):self.box('fan_guard',(.068,.004,.003),(x,-.345,z-.025+dz),'steel',.001)
            for j in range(2):self.cyl('status_lens',.006,.004,(-.25+j*.028,-.344,z-.025),'copper','Y',10)
        self.tube('service_loom',[(.29,.28,.08),(.31,.29,.3),(.30,.27,1.5),(.26,.30,2.12)],.014)
    def save(self):
        geo=L.join(self.parts,'GEO-'+self.asset);L.apply_all(geo);L.smooth(geo,40);L.uv_project(geo)
        geo.data.calc_loop_triangles();out=ROOT+'/SourceArt/_evidence/EX-13/'+self.asset;os.makedirs(out,exist_ok=True)
        report={'asset':self.asset,'features':self.features,'triangles':len(geo.data.loop_triangles),'vertices':len(geo.data.vertices),
            'dimensions_blender':list(geo.dimensions),'collision_boxes_blender':self.collision,'uv_layers':len(geo.data.uv_layers),'state':'En produccion'}
        with open(out+'/geometry.json','w') as f:json.dump(report,f,indent=2)
        bpy.data.libraries.write(ROOT+'/SourceArt/Blender/'+self.asset+'.blend',{self.scene},fake_user=True)
        SCENES[self.id]=self.scene;return report

def build(id):
    b=Builder(id)
    {'017':b.workbench,'018':b.vise,'028':b.shelving,'030':b.container,'038':b.desk,'039':b.chair,'072':b.rack}[id]()
    if id=='018':b.features=['swivel base','fixed and moving jaws','lead screw','sliding handle']
    return b.save()

def activate(id):
    s=SCENES.get(id)
    if not s:
        with bpy.data.libraries.load(ROOT+'/SourceArt/Blender/OBJ-'+id+'_'+ASSETS[id]+'.blend',link=False) as (src,dst):dst.scenes=src.scenes
        s=dst.scenes[0];SCENES[id]=s
    bpy.context.window.scene=s;return s

def render(id):
    s=activate(id);asset='OBJ-'+id+'_'+ASSETS[id];old=L.EVIDENCE;L.EVIDENCE=ROOT+'/SourceArt/_evidence/EX-13/'+asset
    try:return L.sheet(asset,[o for o in s.objects if o.type=='MESH'],views=('iso',),res=640)
    finally:L.EVIDENCE=old

def finish(id,only=None):
    s=activate(id);asset='OBJ-'+id+'_'+ASSETS[id];o=next(x for x in s.objects if x.type=='MESH')
    # Cycles Pointiness also affects large planar faces on joined beveled parts.
    # Keep its contribution subtle so the bake preserves enamel and dark rubber.
    for m in o.data.materials:
        amount=.025 if '_rubber' in m.name else .05 if '_timber' in m.name else .06
        for n in m.node_tree.nodes:
            if n.type=='MATH' and n.operation=='MULTIPLY' and n.inputs[0].is_linked:
                ramp=n.inputs[0].links[0].from_node
                if ramp.type=='VALTORGB' and ramp.inputs['Fac'].is_linked and ramp.inputs['Fac'].links[0].from_node.type=='NEW_GEOMETRY':n.inputs[1].default_value=amount
    samples=[dict(zip(('x','y','z'),o.matrix_world @ v.co)) for v in list(o.data.vertices)[::max(1,len(o.data.vertices)//64)]]
    with open(ROOT+'/SourceArt/_evidence/EX-13/'+asset+'/source_coordinates.json','w') as f:json.dump({'vertices':samples},f)
    stage=ROOT+'/SourceArt/_evidence/EX-13/'+asset+'/staging';os.makedirs(stage,exist_ok=True)
    old_dir=L.TEX_DIR;L.TEX_DIR=stage
    try:maps=L.bake_pbr([o],asset,size=1024,samples=24,only=only)
    finally:L.TEX_DIR=old_dir
    mat=o.data.materials[0]
    for n in list(mat.node_tree.nodes):
        if n.type=='TEX_IMAGE' and n.label in ['Runtime baked '+name for name in maps]:mat.node_tree.nodes.remove(n)
    for name,path in maps.items():
        img=bpy.data.images.load(path,check_existing=False);img.pack()
        n=mat.node_tree.nodes.new('ShaderNodeTexImage');n.image=img;n.label='Runtime baked '+name
        shutil.copy2(path,ROOT+'/EsneiderProtocoloLazaro/Assets/_Game/Art/Textures/'+os.path.basename(path))
    bpy.data.libraries.write(ROOT+'/SourceArt/Blender/'+asset+'.blend',{s},fake_user=True)
    export(id)
    receipt=ROOT+'/SourceArt/_evidence/EX-13/'+asset+'/bake.json';all_maps=json.load(open(receipt)) if only and os.path.isfile(receipt) else {}
    all_maps.update(maps)
    with open(receipt,'w') as f:json.dump(all_maps,f,indent=2)
    return maps

def export(id):
    s=activate(id);asset='OBJ-'+id+'_'+ASSETS[id];o=next(x for x in s.objects if x.type=='MESH')
    mat=o.data.materials[0];old=o.data;matrix=o.matrix_world.copy();o.data=old.copy()
    o.data.transform(matrix);o.matrix_world=Matrix.Identity(4)
    o.data.materials.clear();o.data.materials.append(mat)
    for p in o.data.polygons:p.material_index=0
    try:
        with L.ctx(o):bpy.ops.export_scene.fbx(filepath=ROOT+'/EsneiderProtocoloLazaro/Assets/_Game/Art/Models/'+asset+'.fbx',use_selection=True,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Z',axis_up='Y',object_types={'MESH'},bake_space_transform=True,mesh_smooth_type='FACE',use_mesh_modifiers=True,bake_anim=False,path_mode='STRIP',embed_textures=False)
    finally:o.data=old;o.matrix_world=matrix
    return asset
