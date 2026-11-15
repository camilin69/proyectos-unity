"""OBJ-008 original industrial bench, 1.4 x .45 x .45 m. Run via Blender MCP."""
import bpy,sys,os,json,math
ROOT='C:/Users/HP/Documents/GitHub/proyectos-unity'
sys.path.insert(0,ROOT+'/SourceArt/Scripts')
import esn_lib as L
from mathutils import Vector
ASSET='OBJ-008_BancoIndustrial'
scene=bpy.data.scenes.new('EX12_'+ASSET); bpy.context.window.scene=scene
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
col=bpy.data.collections.new('EXPORT_'+ASSET);scene.collection.children.link(col)
paint=L.material('EX12_Bench_PaintedSteel',(.12,.19,.18),.68,0,wear=.12,wear_color=(.28,.29,.28),bump=.06,scale=65)
wood=L.material('EX12_Bench_SealedTimber',(.22,.12,.06),.64,0,wear=.15,wear_color=(.36,.23,.12),bump=.045,scale=38)
steel=L.material('EX12_Bench_Fasteners',(.32,.34,.34),.5,1)
rubber=L.material('EX12_Bench_Feet',(.022,.026,.025),.88,0)
parts=[]
def box(name,size,loc,mat,bevel=.004):
    o=L.box('GEO-'+name,size,loc,col,bevel=bevel,segs=2);L.assign(o,mat);parts.append(o);return o
# Four protected feet, angled-load bracing, two welded end frames.
for x in (-.55,.55):
    for y in (-.16,.16):
        box('rubber_foot',(.065,.065,.018),(x,y,.009),rubber,.004)
        box('square_tube_leg',(.043,.043,.375),(x,y,.2045),paint,.002)
    box('end_frame',(.05,.40,.038),(x,0,.382),paint,.003)
    box('lower_cross_tie',(.035,.33,.027),(x,0,.10),paint,.002)
for y in (-.15,.15): box('underseat_rail',(1.22,.031,.039),(0,y,.382),paint,.002)
box('longitudinal_stretcher',(1.12,.027,.032),(0,0,.135),paint,.002)
# Three independently bevelled slats, narrow drainage gaps, inset fastener heads.
for j,y in enumerate((-.151,0,.151)):
    box('seat_slat_'+str(j),(1.4,.148,.044),(0,y,.428),wood,.007)
    for x in (-.55,.55):
        bolt=L.cyl('GEO-seat_fastener',.008,.0015,(x,y,.450),col,verts=12,bevel=.0004)
        L.assign(bolt,steel);parts.append(bolt)
        box('bolt_slot',(.007,.0012,.0005),(x,y,.4509),rubber,.0002)
# Small mounting gussets sit below each joint; geometry expresses the assembly.
for x in (-.55,.55):
    for y in (-.15,.15):
        o=box('gusset',(.11,.015,.024),(x,y,.337),paint,.002)
        o.rotation_euler[1]=math.radians(35 if x<0 else -35)
mesh=L.join(parts,'GEO-OBJ008_Bench')
L.apply_all(mesh); L.smooth(mesh,40); L.uv_project(mesh)
out=ROOT+'/SourceArt/_evidence/EX-12/bench';os.makedirs(out,exist_ok=True)
mesh.data.calc_loop_triangles()
report={'asset':ASSET,'triangles':len(mesh.data.loop_triangles),'vertices':len(mesh.data.vertices),
        'dimensions':[round(float(x),4) for x in mesh.dimensions],'uv_layers':len(mesh.data.uv_layers),
        'state':'En produccion','pending':['bake PBR','importacion Unity','capturas neutral/juego','sustitucion de bancos de bloque','colliders y revision de montaje']}
with open(out+'/geometry.json','w') as f:json.dump(report,f,indent=2)
bpy.data.libraries.write(ROOT+'/SourceArt/Blender/'+ASSET+'.blend',{scene},fake_user=True)
print(json.dumps(report))
