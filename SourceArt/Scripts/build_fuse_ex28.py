"""Original ceramic fuse module, metre scale; execute via Blender MCP."""
import bpy,sys
ROOT='C:/Users/HP/Documents/GitHub/proyectos-unity'
sys.path.insert(0,ROOT+'/SourceArt/Scripts')
import esn_lib as L
from build_clinic_fixtures_ex23 import FixtureBuilder
from esn_delivery import Batch
BATCH=Batch('EX-28',{'010':'FusibleModulo'})

def build():
    b=FixtureBuilder('010','FusibleModulo','EX28')
    b.m['ceramic']=L.material(b.asset+'_ceramic',(.64,.62,.51),.34,0,bump=.006,scale=220)
    b.m['contact']=L.material(b.asset+'_contact',(.36,.25,.13),.4,1)
    b.features=['glazed ceramic insulated body','two opposed blade terminals','recessed contact shoulders','front serial label','rear mounting shoe']
    b.box('ceramic_body',(.08,.034,.082),(0,0,.06),'ceramic',.004)
    for z in (.015,.105):
        b.box('insulated_shoulder',(.046,.026,.012),(0,0,z),'ceramic',.001)
        b.box('contact_blade',(.036,.007,.021),(0,0,.0105 if z<.06 else .1095),'contact',.001)
        b.box('worn_contact',(.029,.0003,.009),(0,-.00365,.007 if z<.06 else .113),'steel',0)
    b.box('rear_mounting_shoe',(.044,.003,.041),(0,.0185,.06),'dark',.001)
    # Label on the front (negative Y), backed by a shallow molded recess.
    b.box('label_recess',(.063,.001,.057),(0,-.0175,.06),'dark',.001)
    b.box('serial_label',(.059,.0005,.053),(0,-.01825,.06),'label',0)
    mat=b.m['label'];nodes=mat.node_tree.nodes;links=mat.node_tree.links
    tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(ROOT+'/SourceArt/Textures/EX28_FuseSerial.png',check_existing=True);tex.image.pack()
    geo=nodes.new('ShaderNodeNewGeometry');sep=nodes.new('ShaderNodeSeparateXYZ');links.new(geo.outputs['Position'],sep.inputs[0])
    combine=nodes.new('ShaderNodeCombineXYZ')
    for coord,low,high,out in [('X',-.0295,.0295,'X'),('Z',.0335,.0865,'Y')]:
        remap=nodes.new('ShaderNodeMapRange');remap.inputs['From Min'].default_value=low;remap.inputs['From Max'].default_value=high
        links.new(sep.outputs[coord],remap.inputs['Value']);links.new(remap.outputs[0],combine.inputs[out])
    links.new(combine.outputs[0],tex.inputs['Vector']);shader=next(n for n in nodes if n.type=='BSDF_PRINCIPLED');links.new(tex.outputs['Color'],shader.inputs['Base Color'])
    b.collision=[]
    return BATCH.save(b)

def render():return BATCH.render('010')
def finish():return BATCH.finish('010',size=512)
