"""Original workshop equipment from OBJ catalogue sheets; execute via Blender MCP."""
import bpy,math,importlib
from mathutils import Vector
import esn_lib as L
import build_industrial_furniture_ex13 as furniture
importlib.reload(furniture)
from esn_delivery import Batch
ASSETS={'019':'TaladroFijo','023':'BandejaPiezas','031':'BombaIndustrial','032':'GeneradorLocal','034':'ValvulaBridada','035':'Extintor','036':'SoldadorCarrito','037':'Herramientas'}
batch=Batch('EX-14',ASSETS)

class Builder(furniture.Builder):
    def __init__(self,id):
        super().__init__(id,ASSETS[id],'EX14')
        self.m['red']=L.material(self.asset+'_red',(.32,.032,.016),.57,0,edge_wear=.04,bump=.015)
        self.m['yellow']=L.material(self.asset+'_yellow',(.45,.30,.045),.65,0,edge_wear=.04)
        self.m['oil']=L.material(self.asset+'_oil',(.014,.009,.007),.24,0,edge_wear=0,ao=0,bevel=0)
    def ring(self,n,r,minor,pos,mat='steel',axis='Z',segments=24):
        o=L.torus('GEO-'+self.id+'-'+n,r,minor,pos,self.col,axis=axis,segs=segments,rings=6)
        L.assign(o,self.m[mat]);self.parts.append(o);return o
    def bar(self,n,a,b,width,mat='steel'):
        a=Vector(a);b=Vector(b);o=self.box(n,(width,width,(b-a).length),(a+b)/2,mat,min(.002,width*.12))
        o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
    def outline(self,n,points,thickness,pos,mat='steel'):
        count=len(points);verts=[(x+pos[0],y+pos[1],pos[2]+z) for z in (0,thickness) for x,y in points]
        faces=[tuple(reversed(range(count))),tuple(range(count,2*count))]
        faces += [(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)]
        mesh=bpy.data.meshes.new(n);mesh.from_pydata(verts,[],faces);mesh.update()
        obj=bpy.data.objects.new('GEO-'+self.id+'-'+n,mesh);self.col.objects.link(obj);L.assign(obj,self.m[mat]);self.parts.append(obj)
        L.chamfer(obj,.0008,1);return obj
    def flange(self,x,y,z,r=.10,axis='X'):
        self.cyl('flange',r,.028,(x,y,z),'steel',axis,24)
        for i in range(6):
            a=i*math.pi/3;u=r*.76*math.cos(a);v=r*.76*math.sin(a)
            p=(x,y+u,z+v) if axis=='X' else (x+u,y,z+v) if axis=='Y' else (x+u,y+v,z)
            self.cyl('flange_bolt',.009,.04,p,'steel',axis,6)
    def drill(self):
        self.features=['cast base with mounting holes','column collar','adjustable slotted table','belt cover','motor','chuck and bit clear of table','feed handle','power switch']
        self.box('cast_base',(.60,.50,.065),(0,0,.0325),'paint',.023,True)
        for x in (-.22,.22):
            for y in (-.18,.18):self.cyl('base_anchor',.017,.006,(x,y,.068),'steel','Z',6)
        self.cyl('column_socket',.078,.12,(0,.15,.12),'paint')
        self.cyl('column',.040,1.29,(0,.15,.79),'steel')
        self.box('table_support',(.14,.24,.095),(0,.065,.71),'paint',.007,True)
        self.box('work_table',(.41,.35,.038),(0,-.06,.775),'steel',.012,True)
        for x in (-.14,-.07,.07,.14):self.box('table_slot',(.009,.23,.001),(x,-.075,.7945),'dark',.001)
        self.cyl('quill',.046,.25,(0,-.115,1.13),'steel')
        self.cyl('chuck',.036,.07,(0,-.115,.98),'dark')
        self.cyl('bit',.007,.087,(0,-.115,.904),'steel','Z',10)
        self.box('head_casting',(.23,.39,.20),(0,.005,1.34),'paint',.025,True)
        self.box('belt_neck',(.16,.28,.065),(0,.035,1.46),'paint',.007)
        self.box('belt_cover',(.27,.46,.12),(0,.005,1.54),'paint',.026,True)
        self.cyl('rear_motor',.072,.20,(0,.17,1.28),'dark')
        self.cyl('feed_hub',.032,.05,(.14,-.07,1.29),'steel','X')
        for a in (0,2.094,4.188):
            end=(.17,-.07+.12*math.sin(a),1.29+.12*math.cos(a))
            self.bar('feed_spoke',(.17,-.07,1.29),end,.008)
            self.cyl('feed_grip',.018,.026,end,'dark','X',12)
        self.box('switch_housing',(.06,.022,.078),(-.075,-.2,1.335),'dark',.006)
        self.box('stop_button',(.037,.015,.024),(-.075,-.22,1.345),'red',.004)
        self.serial(.04,-.197,1.36,.07)
        self.tube('motor_cable',[(.065,.17,1.34),(.082,.205,.96),(.075,.20,.20),(.19,.15,.07)],.005)
        self.collision.append({'center':[0,.15,.78],'size':[.095,.095,1.30]})
    def tray(self):
        self.features=['folded tray with raised lips','three separated groups: washers pins seals','localized oil pool','worn tray edge']
        self.box('tray_floor',(.45,.30,.007),(0,0,.0035),'steel',.005,True)
        for x in (-.219,.219):self.box('tray_end',(.012,.30,.063),(x,0,.0385),'paint',.003)
        for y in (-.144,.144):self.box('tray_lip',(.45,.012,.063),(0,y,.0385),'paint',.003)
        self.cyl('oil_pool',.052,.0006,(-.11,.035,.0075),'oil','Z',20)
        for x,y in [(-.14,-.05),(-.105,.045),(-.075,-.04)]:
            for z in (.012,.020):self.ring('washer',.020,.004,(x,y,z),segments=16)
        for x in (-.012,.010,.032):
            self.cyl('hinge_pin',.007,.12,(x,0,.015),'steel','Y',10)
            self.cyl('pin_head',.011,.007,(x,-.06,.015),'steel','Y',10)
        for x,y in [(.105,.055),(.145,-.04)]:self.ring('seal',.024,.005,(x,y,.014),'dark',segments=20)
        self.box('separator',(.006,.24,.03),(.065,0,.022),'paint',.001)
    def pump(self):
        self.features=['anchored skid','ribbed motor','terminal box','guarded coupling','pump housing','bolted inlet outlet flanges','oil at shaft union']
        self.box('skid',(1.5,.8,.075),(0,0,.0375),'paint',.012,True)
        for x in (-.63,.63):
            for y in (-.31,.31):self.cyl('anchor',.018,.015,(x,y,.08),'steel','Z',6)
        for x in (-.58,-.15,.43):self.box('mount',(.12,.44,.18),(x,0,.165),'paint',.008,True)
        self.cyl('motor_body',.22,.68,(-.33,0,.46),'paint','X',24)
        for i in range(12):
            a=2*math.pi*i/12;y=.219*math.sin(a);z=.46+.219*math.cos(a)
            self.box('cooling_fin',(.57,.018,.034),(-.33,y,z),'paint',.001,rot=(a,0,0))
        self.cyl('fan_cap',.226,.065,(-.697,0,.46),'dark','X',24)
        for z in (.35,.405,.46,.515,.57):self.box('fan_guard',(.012,.28,.012),(-.734,0,z),'steel',.001)
        self.box('terminal_box',(.23,.22,.10),(-.33,0,.73),'paint',.014,True)
        self.cyl('coupling_guard',.125,.23,(.12,0,.46),'yellow','X',20)
        for x in (.06,.12,.18):self.ring('guard_band',.127,.008,(x,0,.46),'dark','X',20)
        self.cyl('pump_housing',.245,.28,(.405,0,.46),'paint','X',24)
        self.flange(.265,0,.46,.25)
        self.cyl('inlet',.075,.21,(.63,0,.46),'steel','X',20);self.flange(.735,0,.46,.12)
        self.cyl('outlet',.075,.34,(.43,0,.80),'steel','Z',20);self.flange(.43,0,.984,.12,'Z')
        self.cyl('port_cap',.065,.001,(.7505,0,.46),'dark','X',20)
        self.cyl('port_cap',.065,.001,(.43,0,.999),'dark','Z',20)
        self.cyl('oil_at_union',.075,.0005,(.18,0,.076),'oil','Z',16)
        self.collision.append({'center':[-.28,0,.45],'size':[.93,.48,.62]})
        self.collision.append({'center':[.48,0,.57],'size':[.54,.50,.86]})
        self.serial(-.32,-.227,.48,.13)
    def generator(self):
        self.features=['anchored skid','engine and four cylinder heads','alternator','guarded radiator','exhaust and muffler','fuel tank','service panel','protected feed cables']
        self.box('skid',(3,1.5,.12),(0,0,.06),'paint',.016,True)
        for x in (-1.34,1.34):
            for y in (-.61,.61):self.cyl('skid_anchor',.027,.018,(x,y,.128),'steel','Z',6)
        for x in (-.85,0,.8):self.box('isolator',(.18,1.08,.12),(x,0,.18),'dark',.014)
        for x in (-.85,0):
            for y in (-.29,.29):self.box('engine_mount',(.18,.18,.16),(x,y,.29),'steel',.006)
        for y in (-.45,.45):self.box('radiator_foot',(.18,.18,.12),(1.17,y,.18),'steel',.006)
        self.box('engine_block',(1.08,.82,.75),(-.25,0,.70),'paint',.025,True)
        for x in (-.65,-.37,-.09,.19):
            self.box('cylinder_head',(.23,.84,.21),(x,0,1.14),'steel',.022)
            for y in (-.33,.33):self.cyl('head_bolt',.015,.014,(x,y,1.25),'steel','Z',6)
        self.cyl('alternator',.40,.75,(-1.02,0,.70),'paint','X',24)
        self.collision.append({'center':[-1.02,0,.70],'size':[.75,.80,.80]})
        for x in (-1.37,-1.25,-1.13,-1.01,-.89,-.77):self.ring('alternator_rib',.401,.012,(x,0,.70),'steel','X',24)
        self.box('radiator_frame',(.40,1.28,1.32),(1.17,0,.90),'paint',.02,True)
        self.box('radiator_core',(.025,1.10,1.13),(1.383,0,.90),'dark',.004)
        for z in [ .39+i*.043 for i in range(25)]:self.box('radiator_fin',(.016,1.10,.009),(1.401,0,z),'steel',.0008)
        self.cyl('fan_cage',.41,.055,(.929,0,.90),'dark','X',24)
        self.ring('fan_guard',.415,.015,(.895,0,.90),'steel','X',24)
        for a in (0,math.pi/3,2*math.pi/3):self.bar('fan_guard_cross',(.88,-.40*math.sin(a),.9-.40*math.cos(a)),(.88,.40*math.sin(a),.9+.40*math.cos(a)),.016)
        self.box('fuel_tank',(.58,1.10,.25),(.39,0,1.35),'paint',.03,True)
        self.cyl('fuel_cap',.05,.024,(.39,.2,1.486),'dark')
        self.tube('exhaust_manifold',[(-.7,-.43,1.19),(-.4,-.44,1.22),(.05,-.44,1.22),(.27,-.38,1.3)],.036,'steel')
        self.tube('exhaust_riser',[(.27,-.38,1.3),(.40,-.40,1.65),(.15,-.40,1.70)],.038,'steel')
        self.cyl('muffler',.085,.62,(-.17,-.40,1.715),'dark','X',20)
        self.tube('exhaust_tip',[(-.48,-.40,1.715),(-.62,-.40,1.715),(-.68,-.40,1.63)],.035,'steel')
        self.box('service_panel',(.60,.065,.43),(-.20,-.46,.70),'ivory',.009)
        self.serial(-.20,-.495,.84,.18)
        for x in (-.38,-.21):
            self.cyl('control_knob',.029,.025,(x,-.51,.67),'dark','Y',16)
        self.box('emergency_stop',(.06,.023,.06),(.0,-.51,.67),'red',.005)
        self.tube('fuel_feed',[(.48,.53,1.45),(.48,.58,.83),(.22,.51,.55)],.014,'dark')
        self.tube('power_loom',[(-.92,.28,.90),(-.74,.48,.90),(-.45,.49,.76),(-.2,.48,.58),(.74,.54,.22)],.030,'dark')
    def valve(self):
        self.features=['flanged pipe spool','valve body','bonnet stem','accessible handwheel','wheel spokes','mount saddle','corrosion at joint']
        self.cyl('pipe_spool',.125,.72,(0,0,.21),'steel','X',24)
        for x in (-.345,.345):self.flange(x,0,.21,.17)
        for x in (-.361,.361):self.cyl('closed_service_cap',.111,.001,(x,0,.21),'dark','X',20)
        self.cyl('body',.19,.19,(0,0,.25),'paint','Z',24)
        self.cyl('bonnet',.085,.17,(0,0,.42),'paint')
        self.cyl('stem',.021,.18,(0,0,.575),'steel')
        self.ring('handwheel',.21,.015,(0,0,.68),'red',segments=32)
        self.cyl('wheel_hub',.035,.045,(0,0,.68),'steel')
        for a in (0,2.094,4.188):self.bar('wheel_spoke',(0,0,.68),(.207*math.cos(a),.207*math.sin(a),.68),.017,'red')
        for x in (-.23,.23):self.box('pipe_saddle',(.09,.27,.09),(x,0,.045),'paint',.006,True)
        self.collision.append({'center':[0,0,.21],'size':[.75,.34,.34]})
    def extinguisher(self):
        self.features=['rounded pressure vessel','neck valve','lever handles','gauge','hose and nozzle','wall bracket','aged label']
        self.cyl('vessel',.09,.365,(0,0,.215),'red','Z',24)
        for z in (.032,.397):
            o=L.sphere('GEO-'+self.id+'-shoulder',.09,(0,0,z),self.col,segs=24,rings=8,scale=(1,1,.355));L.assign(o,self.m['red']);self.parts.append(o)
        self.cyl('foot_ring',.085,.012,(0,0,.006),'dark','Z',24)
        self.cyl('valve_neck',.024,.07,(0,0,.45),'steel')
        self.box('lower_handle',(.13,.032,.014),(.022,0,.495),'dark',.007)
        self.box('upper_lever',(.14,.027,.011),(.016,0,.527),'red',.004,rot=(0,.14,0))
        self.cyl('lever_hinge',.018,.037,(-.04,0,.517),'steel','Y',16)
        self.cyl('gauge_rim',.021,.017,(0,-.035,.469),'steel','Y',20)
        self.cyl('gauge_face',.017,.001,(0,-.044,.469),'ivory','Y',20)
        self.box('needle',(.002,.002,.024),(0,-.046,.47),'dark',.0003,rot=(0,.3,0))
        self.tube('hose',[(.025,.015,.465),(.095,.015,.45),(.115,0,.31),(.115,-.015,.16),(.095,-.05,.13)],.009)
        self.cyl('nozzle',.013,.055,(.095,-.05,.117),'dark','Z',12)
        self.box('wall_bracket',(.10,.025,.27),(0,.093,.22),'paint',.004)
        self.box('lower_cradle',(.16,.11,.022),(0,.05,.025),'paint',.005)
        angles=[-.64+i*1.28/8 for i in range(9)]
        vertices=[(.091*math.sin(a),-.091*math.cos(a),z) for z in (.195,.315) for a in angles]
        mesh=bpy.data.meshes.new('curved_label');mesh.from_pydata(vertices,[],[(i,i+1,i+10,i+9) for i in range(8)]);mesh.update()
        label=bpy.data.objects.new('GEO-'+self.id+'-curved_label',mesh);self.col.objects.link(label);L.assign(label,self.m['label']);self.parts.append(label)
        for z in (.222,.242,.262,.282):self.tube('label_line',[(x,-math.sqrt(.092**2-x*x),z) for x in (-.035,-.023,-.012,0,.012,.023,.035)],.0007,'dark')
        self.collision=[]
    def welder(self):
        self.features=['wheeled chassis','repaired sheet-metal enclosure','wire spool','torch holster','return clamp','coiled cables','handle','controls and cooling slots']
        self.box('chassis',(.87,.46,.035),(0,0,.17),'paint',.008,True)
        for x in (-.34,.30):
            self.cyl('axle',.014,.49,(x,0,.095),'steel','Y',12)
            for y in (-.225,.225):self.cyl('wheel',.095,.05,(x,y,.095),'dark','Y',20)
        self.box('body',(.66,.40,.44),(-.04,0,.405),'paint',.02,True)
        self.box('front_panel',(.023,.35,.35),(-.383,0,.42),'ivory',.007)
        for y in (-.10,.03):self.cyl('control_knob',.027,.023,(-.403,y,.51),'dark','X',16)
        for z in (.31,.335,.36):self.box('cooling_slot',(.004,.22,.007),(-.397,0,z),'dark',.001)
        self.cyl('wire_spool',.10,.055,(.36,0,.40),'copper','X',24)
        for x in (.328,.392):self.cyl('spool_cheek',.115,.009,(x,0,.40),'dark','X',24)
        for x in (.305,.40):self.box('spool_support',(.015,.11,.17),(x,0,.25),'paint',.003)
        for y in (-.15,.15):self.bar('handle_upright',(.22,y,.58),(.34,y,.76),.022,'paint')
        self.bar('handle_grip',(.34,-.15,.775),(.34,.15,.775),.027,'dark')
        self.box('repair_patch',(.18,.009,.15),(.08,-.208,.47),'steel',.003)
        for x in (.013,.147):
            for z in (.415,.525):self.cyl('patch_rivet',.005,.01,(x,-.216,z),'steel','Y',8)
        for y in (-.211,-.225,-.239):self.ring('cable_coil',.12,.007,(-.13,y,.41),'dark','Y',segments=28)
        self.box('coil_hook',(.032,.055,.027),(-.13,-.221,.534),'steel',.003)
        self.tube('torch_cable',[(-.40,-.10,.38),(-.41,-.23,.31),(-.15,-.238,.29),(.23,-.236,.29),(.24,-.235,.56)],.006)
        self.box('torch_holster',(.030,.04,.04),(.24,-.212,.552),'steel',.003)
        self.box('torch_grip',(.07,.024,.028),(.24,-.234,.57),'dark',.005)
        self.cyl('torch_neck',.008,.065,(.205,-.234,.598),'copper','Z',12)
        self.tube('earth_lead',[(-.40,.08,.38),(-.41,.23,.24),(.03,.23,.19),(.13,.23,.22)],.006)
        self.box('return_clamp',(.065,.028,.026),(.15,.232,.21),'steel',.003)
    def tools(self):
        self.features=['open-ended wrench','pivoted pliers with insulated grips','slotted screwdriver','partially ordered bench layout','distinct tool scales']
        # Open jaws are concave outlines, not disks posing as spanners.
        wrench=[(-.016,-.105),(.016,-.105),(.012,.045),(.032,.066),(.030,.102),(.016,.117),(.014,.083),(-.014,.083),(-.016,.117),(-.03,.102),(-.032,.066),(-.012,.045)]
        self.outline('open_wrench',wrench,.009,(-.105,0,0))
        self.ring('wrench_hanging_eye',.014,.005,(-.105,-.115,.0045),'steel',segments=16)
        for side in (-1,1):
            points=[(side*.006,-.083),(side*.027,-.087),(side*.017,.007),(side*.024,.028),(side*.009,.073),(side*.003,.071),(side*.008,.027),(side*-.004,.002)]
            self.outline('plier_half',points,.009,(.015,0,.002))
            self.bar('insulated_grip',(.015+side*.017,-.077,.010),(.015+side*.008,-.012,.010),.012,'red')
        self.cyl('plier_pivot',.010,.018,(.015,.0,.009),'steel','Z',12)
        self.cyl('screwdriver_handle',.016,.088,(.12,-.052,.016),'yellow','Y',12)
        self.cyl('screwdriver_shaft',.004,.14,(.12,.057,.016),'steel','Y',10)
        self.box('driver_tip',(.008,.014,.002),(.12,.133,.016),'steel',.0005)
        self.collision=[]

def build(id):
    b=Builder(id)
    {'019':b.drill,'023':b.tray,'031':b.pump,'032':b.generator,'034':b.valve,'035':b.extinguisher,'036':b.welder,'037':b.tools}[id]()
    return batch.save(b)
def render(id):return batch.render(id)
def finish(id):return batch.finish(id)
def export(id):return batch.export(id)
