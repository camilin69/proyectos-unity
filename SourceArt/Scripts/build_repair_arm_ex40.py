"""Four rigid assemblies of the workshop repair arm. Blender MCP only."""
import bpy,sys,math,json,os,importlib.util
from mathutils import Vector,Matrix
ROOT='C:/Users/HP/Documents/GitHub/proyectos-unity'
sys.path.insert(0,ROOT+'/SourceArt/Scripts')
import esn_lib as L
from build_clinic_fixtures_ex23 import FixtureBuilder
ASSET='OBJ-020_BrazoReparacion';FOLDER=ROOT+'/SourceArt/_evidence/EX-40/'+ASSET
SCENE=None
PIVOTS={'Upper':(0,0,.56),'Forearm':(.72,0,1.22),'Tool':(1.42,0,.95)}
def build():
    global SCENE
    b=FixtureBuilder('020','BrazoReparacion','EX40');groups=[]
    b.m['new_joint']=L.material(ASSET+'_maintained_joint',(.25,.28,.27),.42,.8,wear=.02,wear_color=(.32,.33,.31),bump=.01,scale=55)
    def freeze(name,pivot):
        bpy.context.view_layer.update();o=L.join(b.parts,'GEO-020-'+name);L.apply_all(o);o.data.transform(o.matrix_world);o.matrix_world=Matrix.Identity(4);o.data.transform(Matrix.Translation(-Vector(pivot)));o.location=pivot;L.smooth(o,35);groups.append(o);b.parts=[]
    b.box('anchor_plate',(.48,.48,.06),(0,0,.03),'steel',.003)
    for x in (-.18,.18):
        for y in (-.18,.18):b.cyl('anchor_bolt',.025,.035,(x,y,.0775),'steel','Z',12)
    b.cyl('pedestal',.16,.37,(0,0,.245),'paint','Z',32)
    b.cyl('yaw_ring',.18,.07,(0,0,.445),'new_joint','Z',32)
    b.box('shoulder_yoke',(.20,.25,.20),(0,0,.53),'paint',.015)
    b.box('supply_box',(.13,.10,.15),(-.145,.03,.24),'dark',.008)
    b.tube('base_supply',[(-.18,.04,.23),(-.21,.03,.14),(-.20,-.10,.10),(-.14,-.16,.09)],.015,'dark')
    freeze('Base',(0,0,0))
    b.cyl('shoulder_axis',.13,.30,(0,0,.56),'new_joint','Y',32)
    for y in (-.16,.16):b.cyl('shoulder_cover',.115,.024,(0,y,.56),'ivory','Y',24)
    for y in (-.087,.087):b.tube('upper_spar',[(.02,y,.59),(.70,y,1.21)],.057,'paint')
    b.tube('upper_actuator_body',[(.13,-.16,.63),(.46,-.16,.97)],.034,'dark')
    b.tube('upper_actuator_rod',[(.42,-.16,.93),(.65,-.16,1.16)],.018,'steel')
    b.tube('upper_cable',[(.0,.14,.59),(.10,.17,.76),(.42,.17,1.02),(.63,.16,1.25),(.72,.13,1.24)],.013,'dark')
    b.cyl('elbow_housing',.135,.23,(.72,0,1.22),'paint','Y',28)
    for y in (-.129,.129):b.cyl('elbow_service_cover',.105,.025,(.72,y,1.22),'new_joint','Y',24)
    freeze('Upper',PIVOTS['Upper'])
    b.cyl('elbow_shaft',.065,.29,(.72,0,1.22),'steel','Y',24)
    for y in (-.061,.061):b.tube('forearm_spar',[(.74,y,1.22),(1.41,y,.95)],.045,'ivory')
    b.tube('forearm_drive',[(.88,-.115,1.15),(1.18,-.115,1.04)],.030,'dark')
    b.tube('forearm_pushrod',[(1.13,-.115,1.06),(1.38,-.115,.965)],.015,'steel')
    b.tube('forearm_cable',[(.76,.12,1.23),(.88,.17,1.25),(1.26,.15,1.11),(1.42,.10,1.0)],.011,'dark')
    b.cyl('wrist_housing',.085,.17,(1.42,0,.95),'new_joint','Y',24)
    freeze('Forearm',PIVOTS['Forearm'])
    b.cyl('wrist_axis',.050,.20,(1.42,0,.95),'steel','Y',20)
    b.box('tool_adapter',(.16,.13,.08),(1.47,0,.885),'paint',.010)
    b.box('gripper_body',(.14,.18,.115),(1.50,0,.795),'new_joint',.009)
    for sign in (-1,1):
        b.box('jaw_slider',(.095,.054,.025),(1.51,sign*.065,.726),'dark',.001)
        b.box('gripper_finger',(.040,.025,.11),(1.548,sign*.066,.679),'steel',.002)
        b.box('contact_tip',(.075,.036,.018),(1.535,sign*.055,.631),'dark',.001)
    b.cyl('tool_connector',.022,.045,(1.48,.105,.81),'dark','Y',12)
    b.box('tool_service_label',(.072,.001,.025),(1.49,-.091,.807),'label',0)
    freeze('Tool',PIVOTS['Tool'])
    L.uv_project_all(groups);points=[o.matrix_world@v.co for o in groups for v in o.data.vertices];tris=0
    for o in groups:o.data.calc_loop_triangles();tris+=len(o.data.loop_triangles)
    report={'asset':ASSET,'triangles':tris,'mesh_count':4,'texture_sets':1,'dimensions_blender':[max(v[i] for v in points)-min(v[i] for v in points) for i in range(3)],'pivots_blender':PIVOTS,'collision_boxes_blender':[{'center':[0,0,.315],'size':[.48,.48,.63]}],'features':['anchored pedestal and yaw bearing','separate shoulder elbow and wrist assemblies','paired structural spars','linear drive bodies and exposed rods','service cables per rigid link','two padded gripper fingers','maintained joint against older painted links'],'state':'En produccion'}
    os.makedirs(FOLDER,exist_ok=True);open(FOLDER+'/geometry.json','w').write(json.dumps(report,indent=2));SCENE=b.scene;bpy.data.libraries.write(ROOT+'/SourceArt/Blender/'+ASSET+'.blend',{SCENE},fake_user=True);return report
def delivery():
    # Reuse the existing multi-rigid bake/export functions in an isolated module namespace.
    # That module only defines recipes at import time; its build() is never invoked here.
    spec=importlib.util.spec_from_file_location('ex40_rigid_delivery',ROOT+'/SourceArt/Scripts/build_clinical_arm_ex26.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.ASSET=ASSET;module.FOLDER=FOLDER;module.SCENE=SCENE;return module
def render():return delivery().render()
def finish():return delivery().finish()
