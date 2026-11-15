"""Five metre structural service column with accessible registers and lamp hardpoint."""
import sys
ROOT='C:/Users/HP/Documents/GitHub/proyectos-unity'
sys.path.insert(0,ROOT+'/SourceArt/Scripts')
import esn_lib as L
from build_clinic_fixtures_ex23 import FixtureBuilder
from esn_delivery import Batch
BATCH=Batch('EX-25',{'076':'ColumnaServicios'})

def build():
    b=FixtureBuilder('076','ColumnaServicios','EX25')
    b.m['concrete']=L.material(b.asset+'_concrete',(.23,.25,.24),.94,0,bump=.08,scale=24)
    b.features=['five metre structural core and bearing capitals','protected vertical service conduit','two recessed maintenance registers with fasteners','floor plinth and damp base band','reinforced clinical lamp hardpoint on positive X face']
    b.box('structural_core',(.84,.84,4.76),(0,0,2.5),'concrete',.009,True)
    b.box('floor_plinth',(1,1,.12),(0,0,.06),'concrete',.008,True)
    b.box('ceiling_capital',(1,1,.12),(0,0,4.94),'concrete',.008,True)
    b.box('base_protection',(.866,.866,.22),(0,0,.23),'paint',.006)
    for x in (-.32,.32):
        b.box('service_channel',(.075,.065,4.45),(x,-.433,2.51),'steel',.004)
    for z in (1.05,3.25):
        b.box('register_gasket',(.52,.032,.64),(0,-.427,z),'dark',.006)
        b.box('register_cover',(.49,.025,.60),(0,-.451,z),'ivory',.006)
        for x in (-.216,.216):
            for dz in (-.26,.26):b.cyl('quarter_turn_fastener',.010,.004,(x,-.466,z+dz),'steel','Y',8)
        b.box('recessed_latch',(.035,.012,.07),(.16,-.467,z),'dark',.004)
        b.serial(-.08,-.466,z+.17,.12)
    for z in (.45,1.7,2.65,4.5):
        b.box('channel_bridge',(.75,.034,.033),(0,-.48,z),'paint',.003)
    b.box('lamp_load_spreader',(.016,.31,.43),(.423,0,2.45),'steel',.003)
    for y in (-.12,.12):
        for z in (2.28,2.62):b.cyl('load_plate_bolt',.013,.01,(.436,y,z),'steel','X',12)
    # The two channels and register covers extend past the concrete core.
    b.collision.append({'center':[0,-.455,2.5],'size':[.75,.085,4.5]})
    return BATCH.save(b)
def render():return BATCH.render('076')
def finish():return BATCH.finish('076')
