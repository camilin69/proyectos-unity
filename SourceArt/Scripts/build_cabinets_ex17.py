"""Articulated cabinet sources. Execute through Blender MCP only."""
import bpy,math,json,os,shutil
from mathutils import Vector,Matrix
import esn_lib as L
from build_industrial_furniture_ex13 import Builder
ROOT='C:/Users/HP/Documents/GitHub/proyectos-unity'
ASSETS={'007':('ArmarioPreparacion',1,.5,1.9),'024':('LockerSeguridad',1,.55,1.9),'025':('ArmarioEscopeta',1.2,.55,1.9),'026':('GabineteSuministros',1,.5,1.8)}
SCENES={}

class Cabinet(Builder):
    def __init__(self,id):
        name,self.w,self.d,self.h=ASSETS[id];super().__init__(id,name,'EX17')
        self.groups=[];self.doors=[]
        self.m['fabric']=L.material(self.asset+'_folded_fabric',(.16,.20,.18),.91,0,bump=.05,scale=110)
    def freeze(self,name,pivot=(0,0,0)):
        o=L.join(self.parts,'GEO-'+self.id+'-'+name);L.apply_all(o)
        world=o.matrix_world.copy();o.data.transform(world);o.matrix_world=Matrix.Identity(4)
        o.data.transform(Matrix.Translation(-Vector(pivot)));o.location=pivot
        L.smooth(o,40);self.groups.append(o);self.parts=[];return o
    def body(self):
        w,d,h=self.w,self.d,self.h
        self.features=['folded sheet enclosure','open interior','separate thick hinged leaves','three hinge barrels per leaf','shelf supports','latch and worn handles']
        for x in (-w*.41,w*.41):
            for y in (-d*.33,d*.33):self.foot(x,y,.12)
        self.box('bottom',(w,d,.035),(0,0,.1375),'paint',.004,True)
        self.box('top',(w,d,.035),(0,0,h-.0175),'paint',.004,True)
        for x in (-w/2+.015,w/2-.015):self.box('side',(.03,d,h-.17),(x,0,(h+.10)/2),'paint',.004,True)
        self.box('back',(w-.06,.021,h-.17),(0,d/2-.0105,(h+.10)/2),'paint',.003,True)
        levels=[.55,1.02,1.47] if self.id in ('007','026') else [.53,1.46] if self.id=='024' else [.28,1.50]
        for z in levels:
            if z>h-.1:continue
            self.box('shelf',(w-.08,d-.065,.018),(0,.005,z),'ivory',.002,True)
            for x in (-w/2+.045,w/2-.045):
                self.box('shelf_angle',(.022,d-.08,.024),(x,.005,z-.019),'steel',.002)
        if self.id=='007':
            for x,z in [(-.23,.568),(.20,1.038)]:
                for j in range(3):self.box('folded_garment',(.30,.29,.042),(x,.028,z+.021+j*.044),'fabric',.015)
                self.box('cloth_binding',(.024,.295,.132),(x,.028,z+.066),'label',.003)
            for i in range(4):self.box('archive_folder',(.045,.28,.27),(-.24+i*.055,.03,1.615),'label',.005)
        elif self.id=='024':
            # A shallow display cradle sized for the existing pistol, leaving the pickup independent.
            for x in (-.22,.22):self.box('pistol_cradle',(.055,.21,.055),(x,-.04,.5665),'dark',.012)
            for x in (-.27,-.15,.0):self.box('magazine_spare',(.045,.035,.16),(x,.14,1.549),'dark',.006)
        elif self.id=='025':
            for x in (-.26,.26):
                self.box('butt_cup',(.11,.16,.038),(x,.07,.308),'dark',.01)
                self.box('barrel_rest',(.10,.15,.045),(x,.12,1.12),'dark',.01)
                self.box('barrel_rest_bracket',(.06,.085,.04),(x,.2325,1.12),'steel',.003)
            for i in range(6):self.cyl('shell_spare',.011,.065,(-.30+i*.065,0,1.5425),'copper','Z',12)
        else:
            for x,z in [(-.23,.568),(.22,.568),(-.23,1.038),(.22,1.038)]:
                self.box('sealed_supply_case',(.29,.29,.18),(x,.02,z+.09),'ivory',.014)
                self.box('case_lid',(.298,.298,.017),(x,.02,z+.179),'paint',.004)
                self.serial(x,-.128,z+.09,.12)
            self.box('reserve_bin',(.65,.32,.16),(0,0,1.559),'paint',.008)
        self.freeze('Body')
    def leaves(self):
        w,d,h=self.w,self.d,self.h;th=.028;z0=.155;leafh=h-z0-.04;leafw=(w-.064)/2
        for sign in (-1,1):
            x=sign*(leafw/2+.006);y=-d/2-.003;z=z0+leafh/2
            self.box('door_panel',(leafw,th,leafh),(x,y,z),'paint',.003)
            for zz in (z0+.13,z0+leafh-.13):self.box('door_inner_stiffener',(leafw-.055,.025,.034),(x,y+.018,zz),'steel',.003)
            # Raised frame flanges give the inner face physical depth.
            for xx in (x-leafw/2+.012,x+leafw/2-.012):self.box('folded_return',(.018,.025,leafh-.05),(xx,y+.018,z),'paint',.002)
            pivot=(sign*(w/2-.03),y,z0)
            for zz in (z0+.18,z,z0+leafh-.18):
                self.cyl('hinge_barrel',.015,.09,(pivot[0],y,zz),'steel','Z',16)
                self.cyl('hinge_pin',.006,.103,(pivot[0],y,zz),'steel','Z',10)
            hx=sign*.062
            for zz in (z-.075,z+.075):self.box('handle_mount',(.028,.027,.020),(hx,y-.025,zz),'steel',.003)
            self.box('handle_grip',(.019,.022,.17),(hx,y-.045,z),'steel',.008)
            self.box('handle_polished_patch',(.058,.001,.24),(hx,y-.0146,z),'ivory',.008)
            if sign==1:
                self.cyl('lock_bezel',.017,.008,(hx,y-.022,z-.19),'steel','Y',16)
                self.box('key_slot',(.002,.002,.012),(hx,y-.027,z-.19),'dark',0)
            if self.id in ('024','025'):
                for zz in (z0+.17,z0+.21,z0+.25):self.box('vent_slot',(leafw*.64,.0015,.012),(x,y-.015,zz),'dark',.002)
            self.serial(x,y-.016,h-.22,.16)
            o=self.freeze('DoorL' if sign<0 else 'DoorR',pivot)
            self.doors.append({'name':o.name,'pivot_blender':list(pivot),'open_degrees_blender':sign*108,'center_local':[x-pivot[0],0,z-pivot[2]],'size':[leafw,th+.027,leafh]})

def folder(id):return ROOT+'/SourceArt/_evidence/EX-17/OBJ-'+id+'_'+ASSETS[id][0]
def asset(id):return 'OBJ-'+id+'_'+ASSETS[id][0]
def activate(id):
    if id not in SCENES:
        with bpy.data.libraries.load(ROOT+'/SourceArt/Blender/'+asset(id)+'.blend',link=False) as (src,dst):dst.scenes=src.scenes
        SCENES[id]=dst.scenes[0]
    bpy.context.window.scene=SCENES[id];return SCENES[id]
def build(id):
    b=Cabinet(id);b.body();b.leaves();L.uv_project_all(b.groups)
    tris=0
    for o in b.groups:o.data.calc_loop_triangles();tris+=len(o.data.loop_triangles)
    os.makedirs(folder(id),exist_ok=True)
    report={'asset':b.asset,'triangles':tris,'mesh_count':3,'texture_sets':1,'dimensions_target':[b.w,b.d,b.h],
        'collision_boxes_blender':b.collision,'doors':b.doors,'features':b.features,'state':'En produccion'}
    with open(folder(id)+'/geometry.json','w') as f:json.dump(report,f,indent=2)
    SCENES[id]=b.scene;bpy.data.libraries.write(ROOT+'/SourceArt/Blender/'+asset(id)+'.blend',{b.scene},fake_user=True);return report
def render(id,opened=False):
    s=activate(id);objs=[o for o in s.objects if o.type=='MESH'];old=L.EVIDENCE;L.EVIDENCE=folder(id)
    states=[(o,o.rotation_euler.copy()) for o in objs]
    try:
        if opened:
            for o in objs:
                if 'DoorL' in o.name:o.rotation_euler.z=-math.radians(108)
                if 'DoorR' in o.name:o.rotation_euler.z=math.radians(108)
        bpy.context.view_layer.update();return L.sheet(asset(id)+('_open' if opened else '_closed'),objs,views=('iso',),res=640)
    finally:
        for o,rot in states:o.rotation_euler=rot
        bpy.context.view_layer.update();L.EVIDENCE=old
def finish(id):
    s=activate(id);objs=[o for o in s.objects if o.type=='MESH'];name=asset(id)
    samples=[dict(zip(('x','y','z'),o.matrix_world @ v.co)) for o in objs for v in list(o.data.vertices)[::max(1,len(o.data.vertices)//32)]]
    with open(folder(id)+'/source_coordinates.json','w') as f:json.dump({'vertices':samples},f)
    for m in {m for o in objs for m in o.data.materials if m}:
        for n in m.node_tree.nodes:
            if n.type=='MATH' and n.operation=='MULTIPLY' and n.inputs[0].is_linked:
                r=n.inputs[0].links[0].from_node
                if r.type=='VALTORGB' and r.inputs['Fac'].is_linked and r.inputs['Fac'].links[0].from_node.type=='NEW_GEOMETRY':n.inputs[1].default_value=.06
    old=L.TEX_DIR;L.TEX_DIR=folder(id)
    try:maps=L.bake_pbr(objs,name,size=1024,samples=24)
    finally:L.TEX_DIR=old
    for suffix,path in maps.items():
        img=bpy.data.images.load(path,check_existing=False);img.pack();n=objs[0].data.materials[0].node_tree.nodes.new('ShaderNodeTexImage');n.image=img;n.label='Runtime baked '+suffix
        shutil.copy2(path,ROOT+'/EsneiderProtocoloLazaro/Assets/_Game/Art/Textures/'+os.path.basename(path))
    bpy.data.libraries.write(ROOT+'/SourceArt/Blender/'+name+'.blend',{s},fake_user=True)
    # Collapse material slots on temporary mesh copies only; retain three articulated objects.
    backup=[(o,o.data) for o in objs];mat=objs[0].data.materials[0]
    try:
        for o,me in backup:
            o.data=me.copy();o.data.materials.clear();o.data.materials.append(mat)
            for p in o.data.polygons:p.material_index=0
        with L.ctx(objs[0],objs):bpy.ops.export_scene.fbx(filepath=ROOT+'/EsneiderProtocoloLazaro/Assets/_Game/Art/Models/'+name+'.fbx',use_selection=True,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Z',axis_up='Y',object_types={'MESH'},bake_space_transform=True,mesh_smooth_type='FACE',use_mesh_modifiers=True,bake_anim=False,path_mode='STRIP',embed_textures=False)
    finally:
        for o,me in backup:o.data=me
    with open(folder(id)+'/bake.json','w') as f:json.dump(maps,f,indent=2)
    return maps
