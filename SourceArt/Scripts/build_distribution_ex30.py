"""Distribution cabinet with modular contactors and an exposed authorization control."""
import bpy,sys
ROOT='C:/Users/HP/Documents/GitHub/proyectos-unity'
sys.path.insert(0,ROOT+'/SourceArt/Scripts')
import esn_lib as L
from build_clinic_fixtures_ex23 import FixtureBuilder
from esn_delivery import Batch
BATCH=Batch('EX-30',{'033':'CuadroDistribucion'})

def build():
    b=FixtureBuilder('033','CuadroDistribucion','EX30')
    b.features=['folded sheet housing and raised plinth','twelve recent contactor modules on three rails','protected horizontal and vertical wiring','separate closed control compartment with pull handle','human-height authorization button and two status bezels','top cable glands']
    b.box('plinth',(1.4,.28,.10),(0,.01,.05),'dark',.003)
    b.box('back',(1.4,.016,1.66),(0,.142,.93),'paint',.001)
    for x in (-.692,.692):b.box('folded_side',(.016,.27,1.66),(x,.007,.93),'paint',.001)
    b.box('top',(1.368,.27,.016),(0,.007,1.752),'paint',.001)
    b.box('bottom',(1.368,.27,.016),(0,.007,.108),'paint',.001)
    b.box('divider',(.018,.245,1.63),(.10,.015,.93),'paint',.001)
    b.box('module_backplate',(.71,.012,1.52),(-.30,.114,.94),'ivory',.001)
    for z in (.42,.87,1.32):
        b.box('DIN_rail',(.67,.03,.035),(-.30,.08,z),'steel',0)
        for x in (-.56,-.39,-.22,-.05):
            b.box('contactor',(.128,.10,.22),(x,.022,z+.045),'ivory',.001)
            b.box('actuator',(.046,.022,.075),(x,-.039,z+.05),'dark',.001)
            b.box('module_caption',(.095,.002,.027),(x,-.029,z+.115),'label',0)
            for dz in (-.081,.171):b.box('terminal',(.065,.024,.028),(x,.012,z+dz),'copper',0)
        b.box('protected_cable_duct',(.65,.046,.057),(-.30,.05,z+.25),'dark',.001)
        b.tube('feed_cable',[(-.59,.064,z+.25),(-.625,.064,z+.25),(-.625,.064,z+.03)],.010,'dark')
    b.box('vertical_trunk',(.035,.047,1.43),(-.643,.05,.91),'dark',.001)
    b.box('control_door',(.547,.014,1.60),(.393,-.108,.93),'paint',.002)
    b.box('control_plate',(.40,.003,.35),(.387,-.117,1.265),'label',0)
    # Texture carries labels, module IDs and warnings without extra geometry.
    mat=b.m['label'];nodes=mat.node_tree.nodes;links=mat.node_tree.links
    tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(ROOT+'/SourceArt/Textures/EX30_DistributionLabels.png',check_existing=True);tex.image.pack()
    geo=nodes.new('ShaderNodeNewGeometry');sep=nodes.new('ShaderNodeSeparateXYZ');links.new(geo.outputs['Position'],sep.inputs[0]);combine=nodes.new('ShaderNodeCombineXYZ')
    for coord,low,high,out in [('X',-.7,.7,'X'),('Z',0,1.8,'Y')]:
        remap=nodes.new('ShaderNodeMapRange');remap.inputs['From Min'].default_value=low;remap.inputs['From Max'].default_value=high
        links.new(sep.outputs[coord],remap.inputs['Value']);links.new(remap.outputs[0],combine.inputs[out])
    links.new(combine.outputs[0],tex.inputs['Vector']);shader=next(n for n in nodes if n.type=='BSDF_PRINCIPLED');links.new(tex.outputs['Color'],shader.inputs['Base Color'])
    for x in (.275,.50):b.cyl('lamp_bezel',.032,.02,(x,-.127,1.25),'steel','Y',16)
    b.cyl('authorize_socket',.065,.025,(.39,-.13,1.14),'dark','Y',24)
    b.cyl('authorize_button',.048,.006,(.39,-.147,1.14),'ivory','Y',24)
    for z in (.56,.83):b.box('handle_foot',(.026,.020,.032),(.586,-.126,z),'steel',.001)
    b.box('pull_handle',(.024,.018,.29),(.586,-.141,.695),'dark',.001)
    for z in (.35,.94,1.54):b.cyl('hinge_pin',.012,.08,(.665,-.11,z),'steel','Z',12)
    for x in (-.45,-.15,.35):
        b.cyl('gland',.035,.05,(x,.065,1.775),'dark','Z',10)
    # A simple block covers the closed electrical assembly; the control protrudes.
    b.collision=[{'center':[0,.015,.90],'size':[1.4,.27,1.8]}]
    report=BATCH.save(b)
    prioritize_labels(next(o for o in b.scene.objects if o.type=='MESH'))
    bpy.data.libraries.write(ROOT+'/SourceArt/Blender/'+b.asset+'.blend',{b.scene},fake_user=True)
    return report

def prioritize_labels(obj):
    """Reserve atlas islands for readable type; all other UVs remain disjoint below 0.72."""
    if obj.get('label_uv_priority'):return
    uv=obj.data.uv_layers.active.data
    for item in uv:item.uv*=.72
    for face in obj.data.polygons:
        if not obj.data.materials[face.material_index].name.startswith('OBJ-033_CuadroDistribucion_label') or face.normal.y>-.99:continue
        points=[obj.matrix_world@obj.data.vertices[i].co for i in face.vertices]
        center=sum(points,points[0]*0)/len(points)
        if center.x>0:
            left,right,bottom,top=.187,.587,1.09,1.44
            u,v,w,h=.73,.73,.26,.2275
        else:
            col=min(range(4),key=lambda j:abs(center.x-(-.56+.17*j)))
            row=min(range(3),key=lambda j:abs(center.z-(.535+.45*j)))
            left=-.56+.17*col-.0475;right=left+.095
            bottom=.535+.45*row-.0135;top=bottom+.027
            u,v,w,h=.01+col*.175,.76+row*.065,.155,.04405
        for loop_index in face.loop_indices:
            p=obj.matrix_world@obj.data.vertices[obj.data.loops[loop_index].vertex_index].co
            uv[loop_index].uv=(u+(p.x-left)/(right-left)*w,v+(p.z-bottom)/(top-bottom)*h)
    obj['label_uv_priority']=True

def render():return BATCH.render('033')
def finish():return BATCH.finish('033')
