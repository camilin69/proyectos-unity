"""Procedure table, authored neutral support pose; execute in Blender MCP."""
import sys, math
ROOT='C:/Users/HP/Documents/GitHub/proyectos-unity'
sys.path.insert(0,ROOT+'/SourceArt/Scripts')
import esn_lib as L
from build_clinic_fixtures_ex23 import FixtureBuilder
from esn_delivery import Batch
BATCH=Batch('EX-24',{'044':'MesaProcedimientos'})

def build():
    b=FixtureBuilder('044','MesaProcedimientos','EX24')
    b.m['upholstery']=L.material(b.asset+'_upholstery',(.075,.13,.12),.78,0,bump=.025,scale=140)
    b.features=['weighted pedestal with four leveling feet','telescopic lift column with bellows','tilt trunnion and visible actuator','four separate support pads with edge seams','accessory rails and stowed control pedal','neutral static pose without patient restraints']
    b.box('weighted_base',(1.12,.62,.095),(0,0,.095),'paint',.035,True)
    for x in (-.48,.48):
        for y in (-.24,.24):
            b.cyl('leveling_pad',.05,.025,(x,y,.0125),'dark','Z',16)
            b.cyl('leveling_screw',.016,.055,(x,y,.049),'steel','Z',12)
    b.box('lift_casing',(.42,.36,.31),(0,0,.293),'ivory',.025,True)
    b.box('telescopic_column',(.29,.24,.24),(0,0,.555),'steel',.01,True)
    for z in (.456,.481,.506,.531):
        b.box('bellows_fold',(.33,.28,.018),(0,0,z),'dark',.003)
    b.cyl('tilt_axis',.07,.43,(0,0,.687),'steel','Y',24)
    for y in (-.225,.225):
        b.cyl('trunnion_cover',.085,.025,(0,y,.687),'paint','Y',24)
        b.cyl('axis_cap',.031,.029,(0,y,.687),'steel','Y',16)
    b.box('upper_spine',(1.80,.21,.065),(0,0,.739),'steel',.013,True)
    b.tube('actuator_body',[(-.38,0,.29),(-.50,0,.50)],.044,'paint')
    b.tube('actuator_rod',[(-.50,0,.50),(-.64,0,.70)],.020,'steel')
    for x,z in ((-.38,.29),(-.64,.70)):
        b.cyl('actuator_pin',.028,.12,(x,0,z),'steel','Y',16)
    # Pads sum to the 2.1 m support length, with real hinge gaps between sections.
    for name,x,length in [('head',-.8625,.375),('back',-.365,.59),('pelvis',.205,.52),('legs',.77,.56)]:
        width=.61 if name=='head' else .70
        b.box(name+'_tray',(length,width+.025,.037),(x,0,.79),'ivory',.009)
        b.box(name+'_edge_seam',(length-.004,width,.010),(x,0,.814),'dark',.008)
        b.box(name+'_cushion',(length-.016,width-.018,.078),(x,0,.861),'upholstery',.024)
        b.collision.append({'center':[x,0,.8355],'size':[length,width+.025,.129]})
    for x in (-.665,-.055,.48):
        b.cyl('support_hinge',.026,.65,(x,0,.789),'steel','Y',16)
    for y in (-.386,.386):
        for x in (-.52,.52):b.box('rail_standoff',(.06,.05,.045),(x,y*.91,.753),'steel',.003)
        b.box('accessory_rail',(1.52,.027,.034),(0,y,.759),'steel',.003)
        b.box('sliding_clamp',(.13,.035,.060),(.24,y,.755),'paint',.004)
        b.cyl('rail_lock',.018,.025,(.24,y*1.032,.741),'dark','Y',12)
    b.box('pedal_housing',(.22,.13,.043),(.31,-.24,.167),'dark',.008)
    b.box('stowed_pedal',(.16,.085,.014),(.31,-.24,.195),'steel',.004)
    b.tube('control_cable',[(.31,-.23,.169),(.20,-.24,.15),(-.07,-.21,.16),(-.12,-.19,.28)],.007,'dark')
    b.serial(.0,-.184,.34,.18)
    return BATCH.save(b)
def render():return BATCH.render('044')
def finish():return BATCH.finish('044')
