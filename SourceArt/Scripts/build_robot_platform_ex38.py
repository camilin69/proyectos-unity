"""Metric maintenance cradle, authored from OBJ-021; Blender MCP only."""
import bpy,sys
ROOT='C:/Users/HP/Documents/GitHub/proyectos-unity'
sys.path.insert(0,ROOT+'/SourceArt/Scripts')
import esn_lib as L
from esn_delivery import Batch
from build_clinic_fixtures_ex23 import FixtureBuilder
ASSETS={'021':'PlataformaRobot'};BATCH=Batch('EX-38',ASSETS)
def build():
    b=FixtureBuilder('021',ASSETS['021'],'EX38')
    b.features=['2.6 metre maintenance chassis','two longitudinal service rails','three removable deck panels','four rubber body rests','two adjustable pairs of retaining jaws','isolated service sockets and parked leads','floor anchors and recessed wheel access']
    for y in (-.60,.60):
        b.box('chassis_rail',(2.6,.14 if y<0 else .20,.15),(0,y,.185),'paint',.003)
        b.box('service_track',(2.50,.035,.018),(0,y,.269),'steel',.001)
    for x in (-1.14,0,1.14):b.box('cross_member',(.13,1.20,.12),(x,0,.15),'steel',.001)
    for x in (-1.08,1.08):
        for y in (-.56,.56):
            b.box('floor_foot',(.25,.23,.028),(x,y,.014),'dark',.001)
            b.box('leg',(.10,.11,.12),(x,y,.080),'paint',.001)
            b.cyl('anchor',.015,.030,(x+.08,y,.04),'steel','Z',8)
    for x in (-.80,0,.80):
        b.box('deck_panel',(.775,.96,.020),(x,0,.238),'ivory',.002)
        for y in (-.41,.41):
            for dx in (-.32,.32):b.cyl('deck_fastener',.009,.004,(x+dx,y,.250),'steel','Z',8)
    for x in (-.65,.55):
        for y in (-.28,.28):
            b.box('body_rest',(.35,.20,.032),(x,y,.264),'dark',.004)
    for x in (-.65,.55):
        for sign in (-1,1):
            y=sign*.60
            b.box('clamp_carriage',(.19,.14,.032),(x,y,.286),'steel',.001)
            b.box('retaining_jaw',(.13,.055,.072),(x,sign*.535,.314),'paint',.001)
            b.box('jaw_pad',(.12,.018,.058),(x,sign*.504,.315),'dark',.001)
            b.cyl('lock_screw',.012,.12,(x+.067,y,.312),'steel','Y',10)
            b.cyl('lock_knob',.026,.025,(x+.067,sign*.665,.312),'dark','Y',12)
    for x in (.82,1.02):
        b.box('service_socket_base',(.10,.025,.060),(x,-.669,.177),'dark',.001)
        b.cyl('socket_ring',.021,.016,(x,-.689,.177),'steel','Y',12)
        b.cyl('recessed_socket',.014,.001,(x,-.698,.177),'dark','Y',12)
    # Parked on the deck; connection to the final robot remains an assembly task.
    b.tube('parked_service_lead',[(.82,-.68,.22),(.97,-.49,.265),(1.10,-.25,.265),(1.15,.03,.264),(1.07,.16,.264),(.94,.10,.266)],.010,'dark')
    b.cyl('parked_connector',.024,.070,(.91,.10,.266),'steel','X',12)
    b.box('service_label',(.24,.002,.047),(-.94,-.671,.182),'label',0)
    for i in range(8):b.box('label_bar',(.009,.001,.026),(-1.03+i*.025,-.6725,.181),'dark',0)
    b.collision=[{'center':[0,0,.14],'size':[2.6,1.4,.28]}]
    return BATCH.save(b)
def render():return BATCH.render('021')
def finish():return BATCH.finish('021',size=1024,margin=3)
