"""Thermal maintenance, sealed reserve and damaged structural I-beam. Blender MCP only."""
import bpy, bmesh, math, sys
from mathutils import Vector
ROOT='C:/Users/HP/Documents/GitHub/proyectos-unity'
sys.path.insert(0,ROOT+'/SourceArt/Scripts')
import esn_lib as L
from build_industrial_furniture_ex13 import Builder
from esn_delivery import Batch
ASSETS={'004':'UnidadTermica','011':'NucleoSellado','013':'VigaDeformada'}
BATCH=Batch('EX-19',ASSETS)

def thermal(b):
    b.features=['exposed radiator fins with return headers','isolated compressor','insulated coolant hoses','service panel and bolted frame','hose couplings and drain tray']
    for x in (-.52,.52):
        for y in (-.25,.25):
            b.box('vibration_foot',(.13,.12,.04),(x,y,.02),'dark',.008,True)
            b.box('frame_post',(.035,.035,.91),(x,y,.495),'paint',.003,True)
    b.box('base_pan',(1.16,.61,.045),(0,0,.0625),'paint',.008,True)
    b.box('top_cover',(1.20,.65,.04),(0,0,.98),'ivory',.007,True)
    for y in (-.28,.28):b.box('frame_rail',(1.10,.035,.035),(0,y,.90),'paint',.003)
    b.box('rear_panel',(1.09,.018,.77),(0,.286,.50),'paint',.004,True)
    # Radiator assembly: plates have thickness and free air gaps, not a textured slab.
    for x in (-.45,-.11):b.cyl('radiator_header',.035,.69,(x,-.04,.52),'copper','Z',16)
    for i in range(21):b.box('radiator_fin',(.37,.38,.009),(-.28,-.055,.22+i*.03),'steel',.001)
    for x in (-.41,-.29,-.17):b.cyl('radiator_pass',.012,.64,(x,-.055,.52),'copper','Z',12)
    b.collision.append({'center':[-.28,-.055,.52],'size':[.41,.40,.70]})
    # Compressor has its own brackets and isolators, with space around the pipe connections.
    for x in (.12,.42):
        b.box('compressor_mount',(.085,.34,.025),(x,0,.11),'steel',.003)
        for y in (-.12,.12):b.cyl('isolator',.025,.06,(x,y,.153),'dark')
        b.box('compressor_saddle',(.065,.28,.035),(x,0,.197),'steel',.003)
    b.cyl('compressor_shell',.16,.36,(.28,.0,.36),'dark','X',24)
    for x in (.10,.46):b.cyl('compressor_end',.155,.025,(x,0,.36),'steel','X',24)
    b.collision.append({'center':[.28,0,.36],'size':[.40,.33,.33]})
    b.box('electrical_cover',(.18,.17,.11),(.27,-.08,.57),'ivory',.008,True)
    b.tube('insulated_return',[(.38,.02,.49),(.39,.04,.71),(.24,.06,.81),(-.10,.06,.81),(-.11,.01,.85)],.027,'dark')
    b.tube('coolant_feed',[(.11,-.1,.37),(.03,-.16,.37),(.03,-.18,.15),(-.44,-.18,.15),(-.45,-.07,.18)],.018,'copper')
    for x in (-.42,.39):
        b.cyl('external_coupling',.039,.10,(x,.295,.81),'steel','Y',12)
        b.cyl('gasket',.041,.014,(x,.286,.81),'dark','Y',16)
    b.box('service_panel',(.40,.02,.24),(.28,-.306,.77),'ivory',.003,True)
    for x in (.105,.455):
        for z in (.68,.86):b.cyl('panel_screw',.008,.004,(x,-.319,z),'steel','Y',10)
    for i in range(7):b.box('panel_vent',(.25,.004,.008),(.28,-.318,.72+i*.015),'dark',.001)
    b.serial(.28,-.32,.855,.13)
    b.box('drain_tray',(.44,.45,.025),(-.28,-.025,.099),'steel',.004)

def core(b):
    b.features=['sealed double-wall reserve housing','four insulating feet','protected connector shroud','intact wire tamper seal','steady recessed indicator','bolted inspection lid']
    for x in (-.39,.39):
        for y in (-.21,.21):
            b.box('isolated_foot',(.14,.14,.07),(x,y,.035),'dark',.008,True)
            b.box('foot_mount',(.18,.17,.025),(x,y,.0825),'steel',.005)
    b.box('reserve_housing',(.94,.54,.62),(0,0,.395),'paint',.025,True)
    b.box('lid_gasket',(.962,.562,.016),(0,0,.713),'dark',.006)
    b.box('bolted_lid',(1.0,.60,.045),(0,0,.744),'ivory',.008,True)
    for x in (-.43,0,.43):
        for y in (-.25,.25):b.cyl('lid_bolt',.015,.015,(x,y,.774),'steel','Z',6)
    for x in (-.465,.465):b.box('corner_guard',(.05,.56,.53),(x,0,.40),'steel',.006)
    b.box('recessed_connector_plate',(.33,.025,.23),(.18,-.278,.43),'dark',.006)
    for x in (.08,.28):
        b.cyl('ceramic_bushing',.044,.04,(x,-.30,.43),'ivory','Y',16)
        b.cyl('covered_terminal',.027,.024,(x,-.33,.43),'steel','Y',12)
    b.box('connector_canopy',(.40,.13,.028),(.18,-.28,.58),'paint',.004,True)
    for x in (-.035,.395):b.box('canopy_cheek',(.026,.12,.20),(x,-.285,.48),'paint',.003)
    b.box('seal_anchor',(.08,.02,.07),(-.30,-.284,.68),'steel',.003)
    b.box('intact_seal',(.035,.018,.03),(-.30,-.314,.647),'copper',.003)
    b.tube('security_wire',[(-.327,-.303,.716),(-.338,-.316,.66),(-.30,-.32,.626),(-.262,-.316,.66),(-.275,-.303,.716)],.002,'steel')
    b.box('indicator_bezel',(.054,.018,.036),(-.30,-.286,.48),'dark',.004)
    b.box('steady_indicator',(.032,.004,.013),(-.30,-.297,.48),'label',.002)
    b.serial(-.25,-.283,.31,.22)
    for x in (-.35,-.20,-.05):b.box('old_company_mark',(.025,.003,.04),(x,-.281,.20),'ivory',.001)
    for x in (-.46,.46):
        b.box('lift_mount',(.028,.15,.07),(x,0,.775),'steel',.005)

def beam(b):
    b.features=['solid I-profile with flange and web thickness','localized buckling at structural hinge','uneven torn end section','broken bolted splice','fresh steel at crease and old coating elsewhere']
    # Width .28 m, section height .32 m, web 18 mm and flanges 22 mm.
    section=[(-.14,-.16),(.14,-.16),(.14,-.138),(.009,-.138),(.009,.138),(.14,.138),(.14,.16),(-.14,.16),(-.14,.138),(-.009,.138),(-.009,-.138),(-.14,-.138)]
    stations=[(-2,.18,0),(-1.70,.18,0),(-.35,.18,0),(-.15,.20,-.08),(0,.30,-.16),(.15,.41,-.06),(.40,.48,0),(1.80,.77,0),(2,.81,0)]
    verts=[]
    for j,(x,z,twist) in enumerate(stations):
        for k,(y,h) in enumerate(section):
            torn=(.025 if k%3==0 else -.02 if k%3==1 else .009) if j==len(stations)-1 else 0
            verts.append((x+torn,y*math.cos(twist)-h*math.sin(twist),z+y*math.sin(twist)+h*math.cos(twist)))
    n=len(section);faces=[tuple(reversed(range(n)))]
    for j in range(len(stations)-1):
        for k in range(n):faces.append((j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k))
    faces.append(tuple((len(stations)-1)*n+k for k in range(n)))
    mesh=bpy.data.meshes.new('I_beam_solid_section');mesh.from_pydata(verts,[],faces);mesh.update()
    o=bpy.data.objects.new('GEO-013-buckled_I_beam',mesh);b.col.objects.link(o);b.parts.append(o)
    L.assign(o,b.m['paint']);o.data.materials.append(b.m['steel'])
    for p in o.data.polygons:
        if p.index==len(faces)-1 or 37<=p.index<=60:p.material_index=1
    bevel=o.modifiers.new('edge_thickness_highlights','BEVEL');bevel.width=.0015;bevel.segments=1
    for j in range(len(stations)-1):
        a,z0,_=stations[j];c,z1,_=stations[j+1]
        b.collision.append({'center':[(a+c)/2,0,(z0+z1)/2],'size':[c-a,.28,.32+abs(z1-z0)]})
    # Broken connection left end; plates and bolt stubs remain attached to the web.
    for y in (-.022,.022):b.box('broken_splice',(.31,.018,.22),(-1.82,y,.18),'steel',.003)
    for x in (-1.90,-1.75):
        for z in (.105,.255):
            b.cyl('splice_bolt',.015,.077,(x,0,z),'steel','Y',6)
    for x in (-1.45,-.85):
        b.box('aged_flange_scuff',(.19,.075,.001),(x,.07,.341),'steel',.0002)

def build(id):
    b=Builder(id,ASSETS[id],'EX19');{'004':thermal,'011':core,'013':beam}[id](b)
    if id=='013':
        for o in b.parts:o.location.z-=.02
        for box in b.collision:box['center'][2]-=.02
        for o in b.parts:
            L.apply_all(o)
            clean_triangles(o)
    return BATCH.save(b)
def clean_triangles(o):
    bm=bmesh.new();bm.from_mesh(o.data)
    bmesh.ops.triangulate(bm,faces=list(bm.faces))
    dead=[f for f in bm.faces if f.calc_area()<1e-12]
    bmesh.ops.delete(bm,geom=dead,context='FACES_ONLY')
    bm.to_mesh(o.data);bm.free();o.data.update()
def render(id):return BATCH.render(id)
def finish(id):return BATCH.finish(id)
