"""Earlier Custodio head, preserving paired optics and an ivory sanitary shell."""
import bpy,sys
ROOT='C:/Users/HP/Documents/GitHub/proyectos-unity'
sys.path.insert(0,ROOT+'/SourceArt/Scripts')
import esn_lib as L
from esn_delivery import Batch
from build_clinic_fixtures_ex23 import FixtureBuilder
ASSETS={'022':'CabezaCustodioAntigua'};BATCH=Batch('EX-39',ASSETS)
def build():
    b=FixtureBuilder('022',ASSETS['022'],'EX39')
    b.m['shell']=L.material(b.asset+'_protected_polymer',(.56,.57,.49),.5,0,wear=.025,wear_color=(.42,.43,.36),bump=.008,scale=45)
    b.m['lens']=L.material(b.asset+'_optical_coating',(.025,.075,.09),.18,.45,edge_wear=0,ao=0)
    b.features=['rounded ivory early-generation shell','paired recessed optics matching current Custodio lineage','replaceable front faceplate and screws','speaker grille and rear ventilation','neck flange, bench stand and unplugged service lead','clean protected face with worn outer shell']
    b.box('bench_stand',(.16,.14,.015),(0,0,.0075),'steel',.002)
    b.cyl('neck_flange',.067,.020,(0,0,.025),'steel','Z',24)
    b.cyl('neck_stem',.047,.072,(0,0,.066),'dark','Z',20)
    for z in (.043,.082):b.cyl('neck_ring',.052,.012,(0,0,z),'steel','Z',20)
    b.box('old_shell',(.27,.19,.255),(0,.01,.2225),'shell',.025)
    b.box('face_gasket',(.247,.009,.205),(0,-.087,.225),'dark',.020)
    b.box('replaceable_faceplate',(.235,.009,.195),(0,-.094,.225),'shell',.018)
    b.box('eye_recess',(.212,.006,.075),(0,-.100,.252),'dark',.010)
    for x in (-.061,.061):
        b.cyl('optical_bezel',.029,.014,(x,-.109,.252),'steel','Y',24)
        b.cyl('optical_gasket',.024,.005,(x,-.118,.252),'dark','Y',24)
        b.cyl('optical_glass',.020,.001,(x,-.121,.252),'lens','Y',24)
        b.cyl('aperture',.010,.0006,(x,-.122,.252),'dark','Y',16)
    b.box('speaker_backing',(.13,.003,.034),(0,-.100,.174),'dark',.002)
    for z in (.163,.174,.185):b.box('speaker_slat',(.118,.006,.004),(0,-.104,z),'steel',.0005)
    for x in (-.096,.096):
        for z in (.143,.307):b.cyl('face_screw',.004,.004,(x,-.099,z),'steel','Y',8)
    for x in (-.141,.141):b.cyl('side_service_cap',.022,.018,(x,.010,.253),'paint','X',16)
    b.box('rear_vent_backing',(.135,.007,.080),(0,.108,.236),'dark',.003)
    for z in (.210,.223,.236,.249,.262):b.box('rear_vent_slat',(.125,.006,.004),(0,.113,z),'steel',0)
    b.tube('unplugged_lead',[(.025,.042,.065),(.04,.07,.050),(.07,.09,.043),(.10,.10,.045),(.10,.115,.065)],.006,'dark')
    b.cyl('service_plug',.010,.028,(.10,.115,.077),'steel','Z',12)
    b.box('generation_plate',(.082,.0015,.018),(0,-.100,.307),'paint',.001)
    # Four inset registration marks visually distinguish the original production series.
    for x in (-.026,-.009,.009,.026):b.box('series_mark',(.006,.001,.009),(x,-.1013,.307),'ivory',0)
    b.collision=[];return BATCH.save(b)
def render():return BATCH.render('022')
def finish():return BATCH.finish('022',size=1024,margin=2)
