"""Fictional monitoring and sealed perfusion devices; Blender MCP only."""
import math,sys
ROOT='C:/Users/HP/Documents/GitHub/proyectos-unity'
sys.path.insert(0,ROOT+'/SourceArt/Scripts')
import esn_lib as L
from build_industrial_furniture_ex13 import Builder
from esn_delivery import Batch
ASSETS={'045':'MonitorBiometrico','046':'BombaPerfusion'}
BATCH=Batch('EX-22',ASSETS)

def monitor(b):
    b.features=['polymer housing and recessed display','stable pedestal with metal tilt bracket','rotary encoder and three buttons','rear service panel and ventilation slots','keyed capped connectors']
    b.box('housing',(.44,.112,.27),(0,0,.215),'ivory',.012)
    b.box('screen_gasket',(.345,.006,.205),(-.029,-.058,.22),'dark',.006)
    b.box('screen_surface',(.327,.002,.187),(-.029,-.062,.22),'screen',.004)
    b.box('foot',(.245,.145,.014),(0,.006,.007),'steel',.004)
    b.box('foot_pad',(.22,.125,.003),(0,.006,.0015),'dark',.002)
    b.box('pedestal',(.035,.035,.098),(0,.032,.065),'steel',.004)
    b.cyl('tilt_hub',.024,.072,(0,.03,.119),'steel','X',12)
    for z in (.16,.20,.24):b.box('button',(.024,.008,.016),(.178,-.061,z),'paint',.002)
    b.cyl('encoder',.019,.018,(.178,-.065,.106),'dark','Y',16)
    b.box('encoder_mark',(.002,.001,.008),(.178,-.075,.117),'label',0)
    b.box('rear_cover',(.29,.010,.18),(0,.06,.21),'paint',.003)
    for x in (-.12,.12):
        for z in (.14,.28):b.cyl('rear_screw',.005,.003,(x,.067,z),'steel','Y',8)
    for i in range(7):b.box('vent_slot',(.075,.002,.004),(.07,.067,.16+i*.013),'dark',0)
    for x in (-.08,-.015):
        b.cyl('sensor_socket',.012,.022,(x,.063,.115),'steel','Y',12)
        b.cyl('socket_cap',.009,.004,(x,.076,.115),'dark','Y',10)
    b.serial(-.075,.068,.26,.1)
    # Housing sits on a cart/stand; no separate collision around tiny controls.
    b.collision=[]

def pump(b):
    b.features=['compact sealed cassette housing','small recessed status screen','two top inlets aligned to fluid stand','bottom protected outlet','rear split pole clamp and knob','unit label and recessed controls']
    b.box('pump_housing',(.20,.125,.224),(0,-.01,.122),'ivory',.012)
    b.box('screen_gasket',(.132,.004,.069),(-.012,-.074,.177),'dark',.005)
    b.box('screen_surface',(.12,.002,.058),(-.012,-.077,.177),'screen',.003)
    b.box('sealed_cassette',(.135,.012,.075),(-.015,-.078,.079),'paint',.005)
    b.box('cassette_latch',(.025,.010,.051),(.065,-.080,.08),'steel',.003)
    for x in (-.053,0,.052):b.box('control_key',(.026,.006,.013),(x,-.076,.124),'dark',.002)
    for x in (-.055,.055):
        b.cyl('inlet_collar',.014,.017,(x,.040,.2315),'steel','Z',12)
        b.cyl('inlet_port',.008,.024,(x,.065,.238),'ivory','Z',12)
        b.tube('inlet_elbow',[(x,.040,.228),(x,.052,.231),(x,.065,.236)],.007,'ivory')
    b.cyl('bottom_outlet',.011,.020,(0,-.035,.01),'ivory','Z',12)
    b.box('mount_backplate',(.08,.020,.10),(0,.059,.15),'steel',.003)
    points=[(.026*math.cos(a),.090+.026*math.sin(a),.16) for a in [math.radians(-150+j*30) for j in range(11)]]
    b.tube('pole_clamp',points,.006,'steel')
    b.cyl('clamp_screw',.005,.045,(.035,.09,.16),'steel','X',10)
    b.cyl('clamp_knob',.014,.010,(.057,.09,.16),'dark','X',12)
    b.serial(-.03,-.074,.026,.074)
    b.collision=[]

def build(id):
    b=Builder(id,ASSETS[id],'EX22')
    b.m['screen']=L.material(b.asset+'_screen',(.005,.016,.012),.38,0)
    {'045':monitor,'046':pump}[id](b)
    return BATCH.save(b)
def render(id):return BATCH.render(id)
def finish(id):return BATCH.finish(id)
