"""Containment wall monitor with physical rear mount; Blender MCP only."""
import sys,bpy
ROOT='C:/Users/HP/Documents/GitHub/proyectos-unity'
sys.path.insert(0,ROOT+'/SourceArt/Scripts')
import esn_lib as L
from esn_delivery import Batch
from build_clinic_fixtures_ex23 import FixtureBuilder
ASSETS={'074':'MonitorMural'};BATCH=Batch('EX-43',ASSETS)
def build():
    b=FixtureBuilder('074',ASSETS['074'],'EX43')
    b.m['screen']=L.material(b.asset+'_display',(.006,.014,.016),.3,0,edge_wear=0,ao=0)
    b.features=['sealed display housing','recessed display and continuous gasket','rear mounting plate and four fasteners','spaced mounting rails','rear service hatch','lower ventilation slots','recessed power and data sockets','short protected service cable']
    b.box('housing',(1.2,.068,.7),(0,-.016,.35),'paint',.014)
    b.box('display_gasket',(1.112,.005,.598),(0,-.052,.36),'dark',.005)
    b.box('display_surface',(1.08,.002,.566),(0,-.056,.36),'screen',.004)
    b.box('lower_service_strip',(.32,.002,.021),(0,-.052,.032),'ivory',.001)
    for x in (-.12,-.07):b.box('status_window',(.026,.003,.011),(x,-.054,.032),'screen',.001)
    b.box('service_button',(.036,.005,.014),(.12,-.054,.032),'dark',.002)
    b.box('rear_cover',(.76,.006,.40),(0,.021,.37),'ivory',.004)
    for x in (-.34,.34):
        for z in (.20,.54):b.cyl('cover_screw',.007,.004,(x,.026,z),'steel','Y',8)
    for x in (-.23,.23):b.box('mounting_rail',(.044,.024,.44),(x,.033,.36),'steel',.002)
    b.box('wall_plate',(.64,.006,.50),(0,.047,.36),'steel',.003)
    for x in (-.29,.29):
        for z in (.14,.58):b.cyl('wall_anchor',.012,.008,(x,.038,z),'steel','Y',10)
    for i in range(10):b.box('vent',(.028,.002,.009),(-.19+i*.042,.021,.10),'dark',0)
    for x in (-.11,.01):
        b.box('socket_recess',(.065,.003,.027),(x,.021,.057),'dark',.002)
        b.box('sealed_plug',(.042,.017,.018),(x,.027,.057),'steel',.002)
    b.tube('protected_lead',[(-.11,.034,.057),(-.11,.041,.081),(-.07,.04,.10),(-.04,.039,.125)],.006,'dark')
    for o in b.parts:
        for m in o.modifiers:
            if m.type=='BEVEL':m.segments=1
    b.collision=[{'center':[0,0,.35],'size':[1.2,.10,.7]}]
    bpy.context.view_layer.update();return BATCH.save(b)
def render():return BATCH.render('074')
def finish():return BATCH.finish('074',size=1024,margin=2)
