"""Preservation console with a tilted, standing-height readout. Blender MCP only."""
import bpy,sys,math
from mathutils import Vector,Matrix
ROOT='C:/Users/HP/Documents/GitHub/proyectos-unity'
sys.path.insert(0,ROOT+'/SourceArt/Scripts')
import esn_lib as L
from esn_delivery import Batch
from build_clinic_fixtures_ex23 import FixtureBuilder
ASSETS={'003':'ConsolaPreservacion'};BATCH=Batch('EX-42',ASSETS)
def build():
    b=FixtureBuilder('003',ASSETS['003'],'EX42')
    b.m['screen']=L.material(b.asset+'_screen',(.008,.021,.024),.3,0,edge_wear=0,ao=0)
    b.features=['stable floor plinth and rubber pads','sanitary pedestal','twenty degree tilted screen housing','recessed glass display','one confirmation key and three status lamps','rear service hatch and screw heads','vent grille and capped maintenance connector']
    b.box('plinth',(.65,.45,.055),(0,0,.0275),'steel',.008)
    for x in (-.26,.26):
        for y in (-.17,.17):b.box('rubber_pad',(.07,.065,.012),(x,y,.006),'dark',.002)
    b.box('pedestal',(.30,.25,.70),(0,.04,.395),'ivory',.016)
    b.box('base_collar',(.33,.28,.065),(0,.04,.088),'paint',.004)
    b.box('neck',(.23,.19,.12),(0,.04,.75),'steel',.006)
    angle=math.radians(-20);rot=Matrix.Rotation(angle,4,'X');center=Vector((0,0,.958))
    def face(n,size,local,mat,bevel=.003):return b.box(n,size,center+rot@Vector(local),mat,bevel,rot=(angle,0,0))
    face('head_shell',(.7,.18,.45),(0,0,0),'ivory',.014)
    face('screen_seal',(.586,.008,.305),(0,-.093,.035),'dark',.006)
    face('display',(.562,.003,.281),(0,-.099,.035),'screen',.002)
    face('control_recess',(.58,.004,.05),(0,-.094,-.168),'paint',.003)
    face('confirmation_key',(.11,.015,.032),(.207,-.104,-.168),'dark',.004)
    for x in (-.24,-.19,-.14):face('status_lens',(.020,.005,.014),(x,-.100,-.168),'screen',.003)
    face('rear_hatch',(.55,.014,.32),(0,.096,0),'paint',.006)
    for x in (-.235,.235):
        for z in (-.13,.13):
            o=b.cyl('service_screw',.008,.008,center+rot@Vector((x,.108,z)),'steel','Y',8)
            # Cylinder axis is already Y; compose the housing tilt.
            o.rotation_euler=(rot.to_3x3()@o.rotation_euler.to_matrix()).to_euler()
    for i in range(7):face('vent_slot',(.20,.002,.008),(-.09,.105,-.085+i*.023),'dark',0)
    b.box('pedestal_access',(.19,.008,.34),(0,.168,.38),'paint',.004)
    for x in (-.074,.074):
        for z in (.24,.52):b.cyl('access_screw',.006,.006,(x,.174,z),'steel','Y',8)
    b.cyl('service_socket',.026,.033,(.065,.178,.19),'steel','Y',16)
    b.cyl('socket_cap',.022,.009,(.065,.197,.19),'dark','Y',16)
    b.tube('cap_tether',[(.085,.193,.19),(.111,.196,.16),(.10,.18,.135),(.076,.17,.14)],.003,'dark')
    b.collision=[{'center':[0,0,.395],'size':[.34,.29,.79]},{'center':[0,0,.97],'size':[.70,.34,.46]}]
    bpy.context.view_layer.update();return BATCH.save(b)
def render():return BATCH.render('003')
def finish():return BATCH.finish('003',size=1024,margin=2)
