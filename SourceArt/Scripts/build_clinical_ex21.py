"""Original clinical fixtures; Blender MCP build/render/finish per asset."""
import bpy,math,sys
ROOT='C:/Users/HP/Documents/GitHub/proyectos-unity'
sys.path.insert(0,ROOT+'/SourceArt/Scripts')
import esn_lib as L
from build_industrial_furniture_ex13 import Builder
from esn_delivery import Batch
ASSETS={'047':'SoporteFluidos','049':'BandejaInstrumental','051':'LavamanosIndustrial','052':'RejillaDrenaje'}
BATCH=Batch('EX-21',ASSETS)

def stand(b):
    b.features=['five-spoke stable base','rubber casters with forks','telescopic pole and clamp','two hooked sealed fictional fluid bags','tubing terminating in protected couplings']
    for i in range(5):
        a=math.tau*i/5; x,y=.265*math.cos(a),.265*math.sin(a)
        b.tube('base_spoke',[(0,0,.16),(x*.6,y*.6,.095),(x,y,.075)],.018,'steel')
        wheel=b.cyl('wheel',.035,.022,(x,y,.035),'dark','X',16);wheel.rotation_euler.z=a+math.pi/2
        b.box('caster_fork',(.036,.050,.037),(x,y,.071),'steel',.004)
        b.cyl('caster_stem',.009,.05,(x,y,.099),'steel','Z',12)
    b.cyl('base_hub',.042,.11,(0,0,.145),'steel','Z',20)
    b.cyl('lower_pole',.021,.88,(0,0,.61),'steel','Z',20)
    b.cyl('upper_pole',.014,.63,(0,0,1.345),'steel','Z',16)
    b.cyl('height_clamp',.033,.065,(0,0,1.035),'dark','Z',16)
    b.cyl('adjustment_knob',.022,.045,(.042,0,1.035),'dark','X',12)
    b.cyl('top_cap',.021,.025,(0,0,1.6725),'ivory')
    for sign in (-1,1):
        x=sign*.13
        b.tube('bag_hook',[(0,0,1.66),(x*.65,0,1.685),(x,0,1.66),(x,0,1.61),(x-sign*.018,0,1.602)],.007,'steel')
        b.box('bag_hanger_tab',(.035,.016,.07),(x,0,1.595),'ivory',.006)
        b.box('sealed_fluid_bag',(.13,.048,.24),(x,0,1.448),'ivory',.018)
        for dx in (-.061,.061):b.box('bag_seam',(.007,.051,.22),(x+dx,0,1.445),'label',.002)
        b.box('bag_label',(.081,.002,.10),(x,-.025,1.455),'label',.002)
        for j in range(4):b.box('graduation',(.025,.002,.002),(x+.028,-.027,1.39+j*.025),'paint',0)
        b.cyl('bag_outlet',.010,.035,(x,0,1.31),'ivory','Z',12)
        b.cyl('drip_chamber',.012,.075,(x,0,1.251),'ivory','Z',12)
        b.tube('protected_line',[(x,0,1.212),(x*1.25,-.015,1.05),(x*1.25,-.02,.89),(sign*.055,-.025,.82)],.004,'dark')
        b.cyl('closed_line_connector',.012,.042,(sign*.055,-.025,.805),'ivory','Z',12)
    b.box('line_clip',(.15,.038,.022),(0,-.006,.832),'paint',.003)
    b.collision=[{'center':[0,0,.075],'size':[.56,.56,.15]},{'center':[0,0,.91],'size':[.07,.07,1.55]}]

def tray(b):
    b.features=['thick rolled tray lip','recessed base','two distinct articulated tool silhouettes','curved blunt probe','localized contact marks']
    b.box('tray_base',(.49,.34,.006),(0,0,.003),'steel',.006,True)
    for x in (-.245,.245):b.box('raised_side',(.010,.35,.05),(x,0,.03),'steel',.004)
    for y in (-.17,.17):b.box('raised_end',(.49,.01,.05),(0,y,.03),'steel',.004)
    for x in (-.245,.245):b.box('rolled_edge',(.010,.35,.01),(x,0,.055),'steel',.004)
    for y in (-.17,.17):b.box('rolled_edge',(.49,.01,.01),(0,y,.055),'steel',.004)
    # Flat finger loops and crossing arms, not identical rectangular tools.
    for sign in (-1,1):
        x=-.11+sign*.022
        pts=[(x+.016*math.cos(a),-.09+.021*math.sin(a),.012) for a in [math.tau*j/16 for j in range(17)]]
        b.tube('forceps_loop',pts,.003,'steel')
        b.tube('forceps_arm',[(x,-.069,.012),(-.11-sign*.009,.008,.014),(-.11-sign*.018,.10,.012)],.003,'steel')
    b.cyl('forceps_pivot',.006,.006,(-.11,.009,.014),'steel','Z',12)
    for sign in (-1,1):
        b.tube('angled_clamp',[(.04+sign*.016,-.10,.011),(.04+sign*.013,.04,.012),(.065+sign*.006,.105,.014)],.0035,'steel')
    b.box('clamp_grip',(.035,.045,.012),(.04,-.091,.014),'dark',.004)
    b.tube('curved_probe',[(.15,-.10,.013),(.15,.03,.013),(.166,.055,.013),(.183,.061,.013)],.003,'steel')
    b.box('probe_grip',(.018,.08,.014),(.15,-.07,.013),'ivory',.003)
    for x,y in [(-.12,.01),(.05,-.09)]:b.box('contact_scuff',(.05,.025,.0005),(x,y,.0065),'dark',.003)

def rounded_ring(w,d,r,z):
    result=[]
    for cx,cy,a0 in [(w/2-r,d/2-r,0),(-w/2+r,d/2-r,math.pi/2),(-w/2+r,-d/2+r,math.pi),(w/2-r,-d/2+r,math.pi*1.5)]:
        for j in range(8):
            a=a0+j*math.pi/16
            result.append((cx+r*math.cos(a),cy+r*math.sin(a),z))
    return result

def sink(b):
    b.features=['open double-surface basin with drain aperture','rounded rim with thickness','supported frame','gooseneck faucet with aerator','trap and wall drain connection','localized mineral ring at drain']
    loops=[rounded_ring(.8,.6,.06,.76),rounded_ring(.70,.48,.07,.752),rounded_ring(.45,.27,.07,.575),
           [(.035*math.cos(j*math.tau/32),.035*math.sin(j*math.tau/32),.56) for j in range(32)],
           [(.042*math.cos(j*math.tau/32),.042*math.sin(j*math.tau/32),.548) for j in range(32)],
           rounded_ring(.47,.29,.07,.56),rounded_ring(.8,.6,.06,.748)]
    verts=[p for ring in loops for p in ring];faces=[]
    for k in range(len(loops)):
        for j in range(32):faces.append((k*32+j,k*32+(j+1)%32,((k+1)%len(loops))*32+(j+1)%32,((k+1)%len(loops))*32+j))
    me=bpy.data.meshes.new('Basin_open_drain');me.from_pydata(verts,[],faces);me.update()
    o=bpy.data.objects.new('GEO-051-basin',me);b.col.objects.link(o);L.assign(o,b.m['steel']);b.parts.append(o)
    for x in (-.36,.36):
        for y in (-.25,.25):b.foot(x,y,.725)
    for y in (-.275,.275):b.box('basin_support',(.75,.035,.035),(0,y,.725),'paint',.004)
    for x in (-.375,.375):b.box('side_support',(.035,.55,.035),(x,0,.725),'paint',.004)
    b.box('wall_splashback',(.79,.018,.11),(0,.285,.80),'steel',.008)
    b.tube('faucet_neck',[(0,.23,.76),(0,.23,.857),(0,.17,.885),(0,.07,.885),(0,.045,.85)],.015,'steel')
    b.cyl('aerator',.020,.025,(0,.045,.836),'steel','Z',16)
    for x in (-.10,.10):
        b.cyl('valve_base',.026,.018,(x,.225,.775),'steel','Z',16)
        b.box('valve_lever',(.065,.017,.013),(x,.214,.799),'ivory',.004)
    b.tube('drain_tail',[(0,0,.545),(0,0,.43),(0,.05,.37),(0,.14,.37),(0,.19,.44),(0,.19,.48),(0,.31,.48)],.031,'steel')
    b.cyl('wall_drain_flange',.062,.016,(0,.31,.48),'steel','Y',20)
    for z in (.515,.46):b.cyl('trap_union',.04,.017,(0,0,z),'ivory','Z',16)
    b.tube('mineral_drain_ring',[(.047*math.cos(j*math.tau/32),.047*math.sin(j*math.tau/32),.563) for j in range(33)],.002,'label')
    b.collision.append({'center':[0,0,.66],'size':[.8,.6,.20]})

def drain(b):
    b.features=['recessed drainage channel','raised perimeter frame','thick removable metal bars','retaining screws','continuous walking collider']
    b.box('channel_floor',(.59,.19,.009),(0,0,.0045),'dark',.003)
    for x in (-.291,.291):b.box('frame_end',(.018,.20,.035),(x,0,.0175),'steel',.001)
    for y in (-.091,.091):b.box('frame_side',(.564,.018,.035),(0,y,.0175),'steel',.001)
    for i in range(10):b.box('grate_bar',(.016,.169,.014),(-.252+i*.056,0,.028),'steel',.001)
    for x in (-.291,.291):
        b.cyl('retainer',.009,.002,(x,0,.036),'steel','Z',12)
        b.box('screw_slot',(.011,.002,.001),(x,0,.0372),'dark',0)
    b.collision=[{'center':[0,0,.0175],'size':[.6,.2,.035]}]

def build(id):
    b=Builder(id,ASSETS[id],'EX21');{'047':stand,'049':tray,'051':sink,'052':drain}[id](b)
    return BATCH.save(b)
def render(id):return BATCH.render(id)
def finish(id):return BATCH.finish(id)
