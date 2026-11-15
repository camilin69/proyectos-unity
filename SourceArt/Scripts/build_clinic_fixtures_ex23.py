"""Authored clinical lamp and privacy screen; execute through Blender MCP."""
import bpy, math, sys
ROOT='C:/Users/HP/Documents/GitHub/proyectos-unity'
sys.path.insert(0,ROOT+'/SourceArt/Scripts')
import esn_lib as L
from build_industrial_furniture_ex13 import Builder
from esn_delivery import Batch
ASSETS={'048':'LamparaClinica','053':'Biombo'}
BATCH=Batch('EX-23',ASSETS)

class FixtureBuilder(Builder):
    def cyl(self,n,r,depth,pos,mat='steel',axis='Z',verts=16):
        o=L.cyl('GEO-'+self.id+'-'+n,r,depth,pos,self.col,axis=axis,verts=verts,bevel=0)
        L.assign(o,self.m[mat]);self.parts.append(o);return o

def lamp(b):
    b.features=['wall load plate and four fasteners','two rigid articulated links','joint housings and protected cable','60 cm head with seven recessed lenses','sterile central grip']
    b.box('wall_plate',(.06,.24,.34),(0,0,2.45),'paint',.008,True)
    for y in (-.085,.085):
        for z in (2.32,2.58):b.cyl('anchor_bolt',.013,.012,(.036,y,z),'steel','X',12)
    b.cyl('wall_pivot',.075,.16,(.11,0,2.45),'ivory','Z',20)
    b.tube('proximal_link',[(.11,0,2.45),(.62,0,2.58)],.034,'ivory')
    b.cyl('elbow',.065,.10,(.62,0,2.58),'paint','Y',20)
    b.tube('distal_link',[(.62,0,2.58),(1.22,0,2.28)],.031,'ivory')
    b.tube('cable',[(.12,.043,2.46),(.56,.043,2.62),(.67,.043,2.60),(1.23,.043,2.3)],.008,'dark')
    b.cyl('head_swivel',.055,.12,(1.22,0,2.25),'steel','Z',20)
    b.cyl('head_shell',.30,.075,(1.22,0,2.155),'ivory','Z',40)
    b.cyl('lens_carrier',.28,.012,(1.22,0,2.113),'dark','Z',40)
    for i in range(7):
        a=math.tau*i/7;x=1.22+.19*math.cos(a);y=.19*math.sin(a)
        b.cyl('lens_bezel',.061,.014,(x,y,2.102),'steel','Z',16)
        b.cyl('diffuser',.049,.006,(x,y,2.092),'lens','Z',16)
    b.cyl('grip_base',.04,.027,(1.22,0,2.09),'paint','Z',16)
    b.cyl('sterile_grip',.022,.115,(1.22,0,2.025),'ivory','Z',16)
    b.cyl('grip_flange',.032,.009,(1.22,0,1.966),'ivory','Z',16)
    b.collision=[{'center':[0,0,2.45],'size':[.06,.24,.34]}]

def screen(b):
    b.features=['two uprights and top/bottom rails','four rubber casters and forks','thick pleated textile with hems','lower gap and stable transverse feet']
    for x in (-.729,.729):
        b.cyl('upright',.021,1.64,(x,0,.98),'steel','Z',12)
        b.box('transverse_foot',(.038,.43,.034),(x,0,.099),'paint',.008)
        for y in (-.205,.205):
            b.cyl('caster',.044,.032,(x,y,.044),'dark','X',12)
            b.box('wheel_fork',(.044,.032,.034),(x,y,.085),'steel',.003)
    for z in (.32,1.765):b.tube('horizontal_rail',[(-.729,0,z),(.729,0,z)],.018,'steel')
    verts=[]; faces=[];nx=36;nz=3
    for j in range(nz+1):
        z=.35+j*1.38/nz
        for i in range(nx+1):
            x=-.701+i*1.402/nx
            y=.022*math.sin(i/nx*math.tau*9)+.008*math.sin(j/nz*math.pi)*math.sin(i*.8)
            verts.append((x,y,z+.004*math.sin(i*.7)*(1-j/nz)))
    for j in range(nz):
        for i in range(nx):
            a=j*(nx+1)+i;faces.append((a,a+1,a+nx+2,a+nx+1))
    mesh=bpy.data.meshes.new('pleated textile');mesh.from_pydata(verts,[],faces);mesh.update()
    obj=bpy.data.objects.new('GEO-053-textile',mesh);b.col.objects.link(obj);L.assign(obj,b.m['fabric']);b.parts.append(obj)
    solid=obj.modifiers.new('cloth thickness','SOLIDIFY');solid.thickness=.0025
    for z in (.35,1.73):
        hem=L.tube('GEO-053-sewn_hem',[(-.701+i*1.402/nx,.022*math.sin(i/nx*math.tau*9),z) for i in range(nx+1)],.004,b.col,verts=4)
        L.assign(hem,b.m['fabric']);b.parts.append(hem)
    b.collision=[{'center':[0,0,1.04],'size':[1.50,.075,1.52]}]+[{'center':[x,0,.10],'size':[.05,.49,.20]} for x in (-.729,.729)]

def build(id):
    b=FixtureBuilder(id,ASSETS[id],'EX23')
    b.m['lens']=L.material(b.asset+'_diffuser',(.64,.73,.70),.28,0)
    b.m['fabric']=L.material(b.asset+'_fabric',(.15,.235,.215),.93,0,bump=.035,scale=180)
    {'048':lamp,'053':screen}[id](b)
    for obj in b.parts:
        for modifier in list(obj.modifiers):
            if modifier.type=='BEVEL':
                modifier.segments=1
                if id=='048' and any(s in obj.name for s in ('anchor_bolt','diffuser','lens_bezel','grip','swivel')):
                    obj.modifiers.remove(modifier)
    return BATCH.save(b)
def render(id):return BATCH.render(id)
def finish(id):return BATCH.finish(id)
