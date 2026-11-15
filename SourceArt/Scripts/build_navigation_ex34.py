"""Original double-sided wayfinding panels and the D06 isolation plate; Blender MCP."""
import bpy,sys,json
ROOT='C:/Users/HP/Documents/GitHub/proyectos-unity'
sys.path.insert(0,ROOT+'/SourceArt/Scripts')
import esn_lib as L
from esn_delivery import Batch
from build_clinic_fixtures_ex23 import FixtureBuilder
ASSETS={f'NAV-{i:02d}':f'NAV-{i:02d}_Orientacion' for i in range(1,8)}
ASSETS['016']='OBJ-016_PlacaEmergencia'
class SignBatch(Batch):
    def asset(self,id):return ASSETS[id]
BATCH=SignBatch('EX-34',ASSETS)
def printed(b,key,file,w,h,z,back=False):
    mat=L.material(b.asset+'_'+key,(.5,.5,.4),.75,0,edge_wear=0,ao=0)
    n=mat.node_tree.nodes;l=mat.node_tree.links
    tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(ROOT+'/SourceArt/Textures/'+file,check_existing=True);tex.image.pack()
    geo=n.new('ShaderNodeNewGeometry');sep=n.new('ShaderNodeSeparateXYZ');l.new(geo.outputs['Position'],sep.inputs[0]);comb=n.new('ShaderNodeCombineXYZ')
    for axis,lo,hi,out in [('X',w/2 if back else -w/2,-w/2 if back else w/2,'X'),('Z',z-h/2,z+h/2,'Y')]:
        remap=n.new('ShaderNodeMapRange');remap.inputs['From Min'].default_value=lo;remap.inputs['From Max'].default_value=hi
        l.new(sep.outputs[axis],remap.inputs['Value']);l.new(remap.outputs[0],comb.inputs[out])
    l.new(comb.outputs[0],tex.inputs['Vector']);l.new(tex.outputs['Color'],next(x for x in n if x.type=='BSDF_PRINCIPLED').inputs['Base Color']);b.m[key]=mat
def build(id):
    b=FixtureBuilder(id,ASSETS[id],'EX34');b.asset=ASSETS[id]
    small=id=='016';w,h=(.45,.30) if small else (2,.60)
    b.features=['thick painted metal backing','four face screws','original printed NEMESIS signage','EVA maintenance overlay' if small else 'different directional arrows on front and back','wall mounting pads' if small else 'two suspension lugs']
    b.box('backing',(w,.024,h),(0,0,h/2),'paint',.001)
    label_w,label_h=(.418,.278) if small else (1.94,.54)
    printed(b,'face_front','OBJ-016_Front_EX34.png' if small else id+'_Front_EX34.png',label_w,label_h,h/2)
    b.box('printed_front',(label_w,.001,label_h),(0,-.0127,h/2),'face_front',0)
    if not small:
        printed(b,'face_back',id+'_Back_EX34.png',label_w,label_h,h/2,True)
        b.box('printed_back',(label_w,.001,label_h),(0,.0127,h/2),'face_back',0)
    for x in (-w/2+.012,w/2-.012):
        for z in (.014,h-.014):
            b.cyl('face_screw',.0045,.003,(x,-.014,z),'steel','Y',8)
            if not small:b.cyl('rear_screw',.0045,.003,(x,.014,z),'steel','Y',8)
    if small:
        for x in (-.15,.15):b.box('wall_pad',(.055,.008,.20),(x,.016,.15),'steel',0)
        printed(b,'eva_overlay','OBJ-016_Overlay_EX34.png',.30,.056,.032)
        b.box('applied_eva_plate',(.30,.003,.056),(0,-.015,.032),'eva_overlay',0)
    else:
        for x in (-.70,.70):b.box('suspension_lug',(.028,.034,.06),(x,0,h+.022),'steel',.001)
    b.collision=[];report=BATCH.save(b);obj=next(o for o in b.scene.objects if o.type=='MESH')
    # Dedicated text islands, with the unprinted hardware in a separate atlas area.
    uv=obj.data.uv_layers.active.data
    for loop in uv:loop.uv=(loop.uv.x*.96+.02,loop.uv.y*.30+.68)
    for face in obj.data.polygons:
        name=obj.data.materials[face.material_index].name
        if '_face_front' in name and face.normal.y<-.99:rect=(.02,.02,.96,.64 if small else .267);fw,fh,z=label_w,label_h,h/2
        elif '_face_back' in name and face.normal.y>.99:rect=(.02,.34,.96,.267);fw,fh,z=label_w,label_h,h/2
        elif '_eva_overlay' in name and face.normal.y<-.99:rect=(.04,.68,.60,.112);fw,fh,z=.30,.056,.032
        else:continue
        u,v,du,dv=rect
        for li in face.loop_indices:
            co=obj.matrix_world@obj.data.vertices[obj.data.loops[li].vertex_index].co
            uv[li].uv=(u+(co.x/fw+.5)*du,v+((co.z-z)/fh+.5)*dv)
    if small:
        # Move nontext UVs clear of the added EVA strip.
        for face in obj.data.polygons:
            name=obj.data.materials[face.material_index].name
            if ('_face_front' in name or '_eva_overlay' in name) and face.normal.y<-.99:continue
            for li in face.loop_indices:
                old=uv[li].uv.copy();uv[li].uv=(old.x, .83+(old.y-.68)*.5)
    bpy.data.libraries.write(ROOT+'/SourceArt/Blender/'+b.asset+'.blend',{b.scene},fake_user=True)
    return report
def render(id):return BATCH.render(id)
def finish(id,only=None):return BATCH.finish(id,only=only,size=1024,margin=2)
