"""Clamped personal nameplates with later administrative overlays; Blender MCP."""
import bpy,sys,json,shutil,os
ROOT='C:/Users/HP/Documents/GitHub/proyectos-unity'
sys.path.insert(0,ROOT+'/SourceArt/Scripts')
import esn_lib as L
from esn_delivery import Batch
from build_clinic_fixtures_ex23 import FixtureBuilder
from build_navigation_ex34 import printed
ASSETS={i:'PlacaSujeto' for i in ['062','062B','062C','062D','062E']}
BATCH=Batch('EX-36',ASSETS)
def build(id):
    b=FixtureBuilder(id,ASSETS[id],'EX36')
    b.features=['20 by 10 cm metal personal registry plate','four corner screws','physical EVA serial overlay partially covering personal name','two rear clamp pads and connecting shanks','original Series 81 identity']
    b.box('backing',(.20,.006,.10),(0,0,.05),'paint',.001)
    printed(b,'name','OBJ-'+id+'_Name_EX36.png',.186,.088,.05)
    b.box('name_skin',(.186,.0006,.088),(0,-.0034,.05),'name',0)
    # Upper portion of the person's name remains visible above the imposed serial.
    printed(b,'serial','OBJ-'+id+'_Serial_EX36.png',.16,.030,.050)
    b.box('serial_overlay',(.16,.001,.030),(0,-.0045,.050),'serial',0)
    for x in (-.09,.09):
        for z in (.008,.092):b.cyl('corner_screw',.003,.002,(x,-.0045,z),'steel','Y',8)
    for z in (.022,.078):
        b.box('clamp_pad',(.080,.004,.016),(0,.008,z),'dark',0)
        for x in (-.028,.028):b.cyl('clamp_standoff',.003,.010,(x,.004,z),'steel','Y',8)
    b.collision=[];report=BATCH.save(b);obj=next(o for o in b.scene.objects if o.type=='MESH');uv=obj.data.uv_layers.active.data
    for loop in uv:loop.uv=(.02+loop.uv.x*.96,.75+loop.uv.y*.23)
    for f in obj.data.polygons:
        m=obj.data.materials[f.material_index].name
        if '_name' in m and f.normal.y<-.99:rect=(.02,.02,.96,.454);w,h,z=.186,.088,.05
        elif '_serial' in m and f.normal.y<-.99:rect=(.02,.50,.80,.15);w,h,z=.16,.030,.050
        else:continue
        u,v,du,dv=rect
        for li in f.loop_indices:
            co=obj.matrix_world@obj.data.vertices[obj.data.loops[li].vertex_index].co;uv[li].uv=(u+(co.x/w+.5)*du,v+((co.z-z)/h+.5)*dv)
    bpy.data.libraries.write(ROOT+'/SourceArt/Blender/'+b.asset+'.blend',{b.scene},fake_user=True)
    return report
def render(id):return BATCH.render(id)
def finish(id):
    if id=='062':return BATCH.finish(id,size=1024,margin=2)
    maps=BATCH.finish(id,only=['BaseColor'],size=1024,margin=2)
    # Identical meshes, UVs and scalar materials permit reuse of these three maps.
    base=BATCH.folder('062')+'/staging/OBJ-062_PlacaSujeto_'
    for name in ('Roughness','Metallic','Normal'):
        target=BATCH.folder(id)+'/staging/'+BATCH.asset(id)+'_'+name+'.png';shutil.copy2(base+name+'.png',target)
        shutil.copy2(target,ROOT+'/EsneiderProtocoloLazaro/Assets/_Game/Art/Textures/'+os.path.basename(target));maps[name]=target
    with open(BATCH.folder(id)+'/bake.json','w') as f:json.dump(maps,f,indent=2)
    return maps
