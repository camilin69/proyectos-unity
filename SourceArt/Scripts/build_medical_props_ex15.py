"""Sanitary assets built in Blender through MCP, metric Z-up sources."""
import bpy, math, bmesh
import esn_lib as L
from build_industrial_furniture_ex13 import Builder
from esn_delivery import Batch

ASSETS={'005':'DepositoCriogenico','006':'CarroSanitario','014':'CortinaSanitaria'}
batch=Batch('EX-15',ASSETS)

class Medical(Builder):
    def __init__(self,id):
        super().__init__(id,ASSETS[id],'EX15')
        self.m['paint']=L.material(self.asset+'_medical_enamel',(.43,.49,.43),.64,0,bump=.025,scale=65)
        self.m['cloth']=L.material(self.asset+'_aged_cloth',(.26,.34,.29),.94,0,bump=.09,scale=180)
        self.m['hem']=L.material(self.asset+'_damp_hem',(.12,.16,.13),.91,0,bump=.09,scale=180)
    def cart(self):
        self.features=['four caster forks and axles','two folded trays','open frame','polished push handle','tray scratches','used rubber wheels']
        for x in (-.34,.34):
            for y in (-.20,.20):
                self.cyl('wheel_tread',.065,.037,(x,y,.065),'dark','X',24)
                self.cyl('wheel_hub',.034,.044,(x,y,.065),'steel','X',16)
                self.cyl('axle',.011,.068,(x,y,.065),'steel','X',10)
                for dx in (-.025,.025):self.box('caster_fork',(.009,.055,.073),(x+dx,y,.10),'steel',.003)
                self.cyl('swivel_bearing',.041,.017,(x,y,.145),'steel')
                self.cyl('frame_upright',.016,.67,(x,y,.487),'paint')
                self.collision.append({'center':[x,y,.48],'size':[.038,.038,.67]})
        for z in (.24,.79):
            self.box('tray_floor',(.81,.49,.017),(0,0,z),'steel',.005,True)
            for y in (-.252,.252):self.box('tray_long_lip',(.84,.018,.045),(0,y,z+.016),'paint',.005)
            for x in (-.411,.411):self.box('tray_end_lip',(.018,.49,.045),(x,0,z+.016),'paint',.005)
            for y in (-.22,.22):self.box('under_tray_rail',(.71,.027,.036),(0,y,z-.023),'paint',.004)
        for y in (-.20,.20):
            self.tube('handle_riser',[(.34,y,.77),(.434,y,.83),(.434,y,.884)],.016,'steel')
        self.tube('polished_push_bar',[(.434,-.20,.884),(.434,0,.884),(.434,.20,.884)],.016,'steel')
        for i in range(9):
            x=-.24+i*.048; y=.03+math.sin(i*2.1)*.08
            self.box('tray_contact_scratch',(.06+i%3*.02,.0012,.0004),(x,y,.7987),'dark',0,rot=(0,0,.3+i*.15))
        self.serial(-.18,-.262,.792,.09)
        self.collision.append({'center':[.43,0,.85],'size':[.04,.44,.10]})
    def tank(self):
        self.features=['vessel with domed shoulders','three load-bearing legs','service valve with stem','pressure gauge and needle','flanged service port','age streaks below seam']
        # Vessel profile is revolved; unlike intersecting cylinders it has no cap seam.
        rings=[(.0,.235),(.16,.235),(.27,.28),(.325,.36),(.325,1.20),(.30,1.28),(.23,1.34),(.09,1.38),(.0,1.38)]
        verts=[];faces=[];n=40
        for r,z in rings:
            for i in range(n):
                a=2*math.pi*i/n;verts.append((r*math.cos(a),r*math.sin(a),z))
        for j in range(len(rings)-1):
            for i in range(n):a=j*n+i;b=j*n+(i+1)%n;faces.append((a,b,b+n,a+n))
        mesh=bpy.data.meshes.new('VesselProfile');mesh.from_pydata(verts,[],faces);mesh.update()
        bm=bmesh.new();bm.from_mesh(mesh)
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001)
        bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.000001)
        bm.to_mesh(mesh);bm.free();mesh.update()
        obj=bpy.data.objects.new('GEO-005-vessel',mesh);self.col.objects.link(obj);L.assign(obj,self.m['paint']);self.parts.append(obj)
        for i in range(3):
            a=math.pi/6+i*2*math.pi/3;x=.235*math.cos(a);y=.235*math.sin(a)
            self.box('leg',(.06,.06,.32),(x,y,.16),'steel',.004,True)
            self.box('anchor_plate',(.105,.105,.014),(x,y,.007),'steel',.003)
        self.cyl('valve_neck',.037,.11,(0,0,1.425),'steel')
        self.box('valve_body',(.105,.062,.055),(0,0,1.48),'copper',.009)
        self.cyl('stem',.011,.072,(0,0,1.54),'steel')
        self.cyl('handwheel',.069,.017,(0,0,1.5915),'dark','Z',24)
        self.cyl('gauge_stalk',.013,.08,(.035,-.055,1.485),'steel','Y')
        self.cyl('gauge_bezel',.048,.028,(.035,-.108,1.485),'steel','Y',24)
        self.cyl('gauge_face',.041,.002,(.035,-.124,1.485),'label','Y',24)
        self.box('needle',(.002,.001,.031),(.044,-.126,1.493),'dark',0,rot=(0,-.55,0))
        self.cyl('service_port',.024,.11,(.082,0,1.478),'copper','X')
        self.cyl('port_flange',.038,.016,(.142,0,1.478),'steel','X',16)
        self.cyl('shipping_cap',.029,.005,(.153,0,1.478),'dark','X')
        # Curved label and drips conform to the shell instead of floating flat decals.
        def patch(name,angle,width,z0,z1,mat):
            v=[];f=[];steps=16
            for z in (z0,z1):
                for i in range(steps+1):
                    a=angle+width*(i/steps-.5);v.append((.3256*math.sin(a),-.3256*math.cos(a),z))
            for i in range(steps):f.append((i,i+1,i+steps+2,i+steps+1))
            me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.update()
            ob=bpy.data.objects.new('GEO-005-'+name,me);self.col.objects.link(ob);L.assign(ob,self.m[mat]);self.parts.append(ob)
        patch('aged_service_label',0,.48,.79,.97,'label')
        for i in range(5):patch('label_rule',0,.32,.815+i*.028,.818+i*.028,'dark')
        for i in range(7):patch('seam_drip',-.65+i*.23,.009+(i%3)*.003,1.10-(i%4)*.041,1.20,'hem')
        self.collision.append({'center':[0,0,.8],'size':[.63,.63,1.18]})
    def curtain(self):
        self.features=['folds vary under hanging points','double-sided cloth thickness','damp bottom strip','thirteen hangers','rail and ceiling mounts']
        nx,nz=120,26;verts=[];faces=[]
        for j in range(nz+1):
            t=j/nz;z=.045+t*2.02
            for i in range(nx+1):
                u=i/nx;x=-.96+1.92*u
                y=(.042+.027*(1-t))*math.cos(u*math.pi*24)+.013*(1-t)*math.sin(u*math.pi*7)
                sag=.013*(1-math.cos(u*math.pi*24))*(t**5)
                verts.append((x,y,z-sag))
        for j in range(nz):
            for i in range(nx):
                a=j*(nx+1)+i;faces.append((a,a+1,a+nx+2,a+nx+1))
        mesh=bpy.data.meshes.new('CurtainFoldSurface');mesh.from_pydata(verts,[],faces);mesh.update()
        obj=bpy.data.objects.new('GEO-014-folded_cloth',mesh);self.col.objects.link(obj)
        obj.data.materials.append(self.m['cloth']);obj.data.materials.append(self.m['hem'])
        for p in mesh.polygons:p.material_index=1 if p.center.z<.13 else 0
        # Polygon centers require mesh update above; bottom strip gets localized damp material.
        mod=obj.modifiers.new('WovenThickness','SOLIDIFY');mod.thickness=.0018
        self.parts.append(obj)
        self.cyl('rail',.014,2,(0,0,2.15),'steel','X',16)
        for x in (-.83,.83):
            self.cyl('ceiling_drop',.009,.05,(x,0,2.175),'steel')
            self.box('ceiling_plate',(.075,.055,.008),(x,0,2.2),'steel',.002)
        for i in range(13):
            x=-.96+i*.16
            self.tube('hanging_hook',[(x,.035,2.06),(x,.035,2.14),(x,0,2.17),(x,-.024,2.14),(x,-.024,2.10)],.0035,'steel')
        self.collision.append({'center':[0,0,2.15],'size':[2,.033,.033]})

def build(id):
    b=Medical(id);{'005':b.tank,'006':b.cart,'014':b.curtain}[id]();return batch.save(b)
def render(id):return batch.render(id)
def finish(id):return batch.finish(id)
