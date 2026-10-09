"""Run inside Blender. Owns DREAM_Atrium; other scenes are preserved.

Architectural interpretation of video-52/05s: curved white/lime galleries,
clear blue water, glazed envelope, information columns and abundant foliage.
Set DREAM_BLOCKOUT to validate camera and massing before detailing.
"""
import bpy, math, random, json
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
BLOCKOUT=globals().get('DREAM_BLOCKOUT',False)
old=bpy.data.scenes.get('DREAM_Atrium')
if old:
    for o in list(old.objects): bpy.data.objects.remove(o,do_unlink=True)
    bpy.data.scenes.remove(old)
scene=bpy.data.scenes.new('DREAM_Atrium');bpy.context.window.scene=scene
scene['dream_asset']='atrium';scene['dream_reference']='video-52, 05 seconds'
scene['dream_stage']='blockout' if BLOCKOUT else 'garden-channel-v2'
scene.unit_settings.system='METRIC'
scene.render.resolution_x=960;scene.render.resolution_y=720
scene.render.resolution_percentage=70
try:scene.render.engine='BLENDER_EEVEE'
except TypeError:scene.render.engine='BLENDER_EEVEE_NEXT'
scene.eevee.taa_render_samples=32;scene.eevee.use_raytracing=True
scene.render.image_settings.file_format='PNG'
scene.view_settings.exposure=-.25
rng=random.Random(1708)
materials=[]
def mat(name,color,rough=.4,metal=0,kind=0,texture=None):
    c=[int(color[i:i+2],16)/255 for i in (0,2,4)]
    linear=lambda x:((x+.055)/1.055)**2.4 if x>.04045 else x/12.92
    m=bpy.data.materials.new('DREAM_ATRIUM_'+name);m.use_nodes=True
    p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    p.inputs['Base Color'].default_value=(*map(linear,c),1)
    p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
    m['dream_id']=len(materials);m['roughness']=rough;m['metallic']=metal;m['kind']=kind
    if kind in (4,6,9):
        p.inputs['Transmission Weight'].default_value=.48 if kind==9 else .9
        p.inputs['IOR'].default_value=1.333 if kind in (4,9) else 1.46
        if kind in (4,9):
            tex=m.node_tree.nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=9
            bump=m.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.15;bump.inputs['Distance'].default_value=.08
            m.node_tree.links.new(tex.outputs['Fac'],bump.inputs['Height']);m.node_tree.links.new(bump.outputs['Normal'],p.inputs['Normal'])
            if kind==9:
                p.inputs['Alpha'].default_value=.42;m.surface_render_method='BLENDED'
                coords=m.node_tree.nodes.new('ShaderNodeTexCoord')
                stretch=m.node_tree.nodes.new('ShaderNodeVectorMath');stretch.operation='MULTIPLY';stretch.inputs[1].default_value=(12,.35,1)
                m.node_tree.links.new(coords.outputs['UV'],stretch.inputs[0]);m.node_tree.links.new(stretch.outputs['Vector'],tex.inputs['Vector'])
    if kind==7:
        p.inputs['Emission Color'].default_value=(*map(linear,c),1);p.inputs['Emission Strength'].default_value=.7
    if texture:
        tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ROOT/f'assets/textures/{texture}.png'),check_existing=True)
        if tex.image.packed_file:tex.image.unpack(method='REMOVE')
        tex.image.reload()
        m.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color'])
    materials.append(m);return m

white=mat('porcelain','EAF1E9',.23)
floor=mat('floor','DEE9E4',.16,.08,1)
silver=mat('polished_alloy','C0D9DC',.18,.8)
lime=mat('lime_band','B7D96B',.2,0,7)
blue=mat('pool_mosaic','1685B8',.3)
water=mat('water','28B8CA',.065,0,4)
glass=mat('blue_glass','5CCCE7',.1,0,6)
column_glass=mat('column_glass','198CBC',.12,0,6);column_glass['opacity']=.36
leaf=mat('leaf','46872A',.62,0,5,'leaf_detail')
young=mat('young_leaf','78AA35',.6,0,5,'leaf_detail')
bark=mat('stem','726B3B',.83)
soil=mat('soil','303D25',.95)
screen=mat('screen','094965',.22,0,7)
typewhite=mat('type','BCECE8',.4,0,7)
globe=mat('biosphere','FFFFFF',.2,.12,8,'biosphere')
fall=mat('falling_water','C9F2F4',.12,0,9);fall['opacity']=.68

def mesh(label,verts,faces,material,uvs=None,smooth=False):
    me=bpy.data.meshes.new('DREAM_'+label);me.from_pydata(verts,[],faces);me.materials.append(material)
    ob=bpy.data.objects.new('GEO-DREAM-'+label,me);scene.collection.objects.link(ob)
    if uvs:
        uv=me.uv_layers.new()
        for poly in me.polygons:
            for li in poly.loop_indices:uv.data[li].uv=uvs[me.loops[li].vertex_index]
    if smooth:
        for p in me.polygons:p.use_smooth=True
    return ob
def box(label,pos,size,m,bevel=.02):
    bpy.ops.mesh.primitive_cube_add(size=1,location=pos);o=bpy.context.object;o.name='GEO-DREAM-'+label;o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m)
    if bevel:mod=o.modifiers.new('Edge radius','BEVEL');mod.width=bevel;mod.segments=2
    return o
def rod(label,a,b,r,m,segments=12):
    d=Vector(b)-Vector(a);bpy.ops.mesh.primitive_cylinder_add(vertices=segments,radius=r,depth=d.length,location=(Vector(a)+Vector(b))/2)
    o=bpy.context.object;o.name='GEO-DREAM-'+label;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();o.data.materials.append(m)
    for p in o.data.polygons:p.use_smooth=True
    return o
def ring(label,cx,cy,inner,outer,z,depth,m,start=0,end=math.tau,steps=96):
    vs=[];fs=[]
    for i in range(steps+1):
        a=start+(end-start)*i/steps
        for r,h in [(inner,z),(outer,z),(inner,z-depth),(outer,z-depth)]:vs.append((cx+r*math.cos(a),cy+r*math.sin(a),h))
    for i in range(steps):
        j=i*4;k=j+4
        fs.extend([(j,j+1,k+1,k),(j+2,k+2,k+3,j+3),(j,k,k+2,j+2),(j+1,j+3,k+3,k+1)])
    fs.extend([(0,2,3,1),(steps*4,steps*4+1,steps*4+3,steps*4+2)])
    return mesh(label,vs,fs,m,smooth=False)
def text(label,body,pos,size,m):
    cu=bpy.data.curves.new('DREAM_type','FONT');cu.body=body;cu.size=size;cu.align_x='CENTER';cu.extrude=.001
    ob=bpy.data.objects.new('GEO-DREAM-'+label,cu);scene.collection.objects.link(ob);ob.location=pos;ob.rotation_euler.x=math.pi/2;cu.materials.append(m)
    bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH')
    return bpy.context.object

cx,cy=-1,4
# A gently curved southern canal joins the pool. Its complete silhouette is
# shared by water, basin, coping and ground: there is no floor under the water.
# The swept discs taper toward the canal's round end. This envelope is star
# shaped about the pool centre, so radial tessellation produces no crossings.
channel=[]
for i in range(33):
    t=i/32;r=3.65+4.5*t;a=math.radians(-104+4*t*t)
    channel.append((cx+r*math.cos(a),cy+r*math.sin(a),1.08-.35*t))
channel_capsules=[[a[0],a[1],b[0],b[1],max(a[2],b[2])+.18]
                  for a,b in zip(channel[:-1],channel[1:])]
def shoreline(angle):
    dx,dy=math.cos(angle),math.sin(angle);radius=4.22
    for x,y,r in channel:
        x-=cx;y-=cy;along=x*dx+y*dy;side2=x*x+y*y-along*along
        if along>0 and side2<=r*r:radius=max(radius,along+math.sqrt(max(0,r*r-side2)))
    return radius

def shore_ring(label,inner_offset,outer_offset,z,depth,material,outer_radius=None):
    verts=[];faces=[];steps=256
    for i in range(steps+1):
        a=math.tau*i/steps;r=shoreline(a)
        for radius,h in [(r+inner_offset,z),(outer_radius or r+outer_offset,z),
                         (r+inner_offset,z-depth),(outer_radius or r+outer_offset,z-depth)]:
            verts.append((cx+radius*math.cos(a),cy+radius*math.sin(a),h))
    for i in range(steps):
        j=i*4;k=j+4
        faces.extend([(j,j+1,k+1,k),(j+2,k+2,k+3,j+3),
                      (j,k,k+2,j+2),(j+1,j+3,k+3,k+1)])
    return mesh(label,verts,faces,material)

shore_ring('ground_gallery',.10,0,.2,.25,floor,outer_radius=10.5)
shore_ring('pool_coping',-.012,.105,.245,.19,white)
shore_ring('pool_edge',.008,.057,.255,.04,lime)
shore_ring('pool_side',-.04,.018,.04,.74,blue)
# Dense water grid follows the connected pool/canal, with actual vertex waves
# supplied by the C++ shader. The basin uses the identical footprint.
verts=[(cx,cy,.055)];faces=[];uv=[(.5,.5)];n=256
for j in range(1,49):
    for i in range(n):
        a=math.tau*i/n;r=shoreline(a)*j/48;x=r*math.cos(a);y=r*math.sin(a)
        verts.append((cx+x,cy+y,.055));uv.append((x/8.44+.5,y/8.44+.5))
for i in range(n):faces.append((0,1+i,1+(i+1)%n))
for j in range(47):
    for i in range(n):
        a=1+j*n+i;b=1+j*n+(i+1)%n;faces.append((a,a+n,b+n,b))
mesh('water',verts,faces,water,uv,smooth=True)
basin=[(cx,cy,-.68)]+[(x,y,-.68) for x,y,z in verts[-n:]]
mesh('pool_basin',basin,[(0,1+i,1+(i+1)%n) for i in range(n)],blue)

# The waterfall is on the far side of the pool, visible between the information
# columns. UV.y runs from the splash to the lip; kind 9 is the shared runtime
# material contract for the descending translucent streams.
box('waterfall_supply',(.9,9.55,8.18),(1.36,5.5,.18),white,.045)
box('waterfall_lip',(.9,6.82,8.08),(1.40,.38,.16),silver,.035)
fall_vertices=[];fall_faces=[];fall_uv=[];fall_nx=20;fall_nz=56
for j in range(fall_nz+1):
    v=j/fall_nz;z=.09+7.91*v
    for i in range(fall_nx+1):
        u=i/fall_nx;width=1.24+.12*(1-v)
        x=.9+(u-.5)*width
        y=6.62+.034*math.sin(u*math.tau*7+v*4)+.07*math.sin(v*math.pi)
        fall_vertices.append((x,y,z));fall_uv.append((u,v))
for j in range(fall_nz):
    for i in range(fall_nx):
        a=j*(fall_nx+1)+i;fall_faces.append((a,a+1,a+fall_nx+2,a+fall_nx+1))
mesh('waterfall_curtain',fall_vertices,fall_faces,fall,fall_uv,smooth=True)

for z in [4.8,8.5]:
    ring('upper_gallery',cx,cy,8.2,10.5,z,.32,white)
    ring('luminous_fascia',cx,cy,8.16,8.23,z-.09,.065,lime)
    ring('gallery_handrail',cx,cy,8.18,8.22,z+1.05,.045,silver)
    for i in range(40):
        a=math.tau*i/40;x=cx+8.2*math.cos(a);y=cy+8.2*math.sin(a)
        rod('balustrade_post',(x,y,z),(x,y,z+1.02),.022,silver,8)

columns=[]
for degree in [-35,205,65,125]:
    a=math.radians(degree);x=cx+7*math.cos(a);y=cy+7*math.sin(a);columns.append((x,y))
    rod('column_core',(x,y,.2),(x,y,11.1),.42,white,24)
    rod('column_glass',(x,y,.28),(x,y,10.8),.68,column_glass,32)
    for z in [.3,3.7,7.1,10.8]:ring('column_lime',x,y,.675,.72,z,.07,lime,steps=32)
    box('information_panel',(x,y-.704,2.45),(1.07,.045,3.8),screen)
    if not BLOCKOUT:
        for title,z,size in [('D R E A M',3.9,.19),('ATRIUM',3.53,.15),('01',2.7,.5),('JARDIN',2.15,.17),('AGUA',1.65,.17),('BIOSFERA',1.15,.15)]:text('information_type',title,(x,y-.736,z),size,typewhite)

# Glazed circular envelope; separate panes can be sorted in the runtime.
for i in range(40):
    a=math.tau*i/40;b=math.tau*(i+1)/40
    p=(cx+10.3*math.cos(a),cy+10.3*math.sin(a))
    q=(cx+10.3*math.cos(b),cy+10.3*math.sin(b))
    rod('facade_mullion',(*p,.2),(*p,11.7),.055,silver,8)
    if not BLOCKOUT:mesh('facade_glass',[(*p,.2),(*q,.2),(*q,11.7),(*p,11.7)],[(0,1,2,3)],glass)
for z in [3,6.5,11.7]:ring('facade_ring',cx,cy,10.24,10.36,z,.1,white)
# Open radial roof ribs frame the sky and preserve the airy reference.
for i in range(16):
    a=math.tau*i/16
    rod('roof_rib',(cx+2*math.cos(a),cy+2*math.sin(a),12.5),(cx+10.3*math.cos(a),cy+10.3*math.sin(a),11.7),.055,white,8)
ring('oculus',cx,cy,1.97,2.06,12.5,.07,lime)

def plant(x,y,z,scale=1,wide=False):
    verts=[];faces=[];uvs=[]
    # Curved lanceolate leaves, deliberately meshed rather than opaque cards.
    for k in range(11 if wide else 17):
        angle=k*2.39996+rng.uniform(-.35,.35);length=rng.uniform(.7,1.55)*scale
        spread=rng.uniform(.58,1.12);height=rng.uniform(.45,1.25)*scale
        start=len(verts)
        for j in range(9):
            t=j/8;reach=length*t*spread
            zz=z+height*math.sin(t*1.9)+.05*scale
            for side in [-1,0,1]:
                width=math.sin(math.pi*t)**(.6 if wide else .9)*(.22 if wide else .09)*scale*side
                verts.append((x+reach*math.cos(angle)-width*math.sin(angle),y+reach*math.sin(angle)+width*math.cos(angle),zz-abs(side)*.025*scale))
                uvs.append(((side+1)/2,t))
        for j in range(8):
            a=start+j*3;faces.extend([(a,a+3,a+4,a+1),(a+1,a+4,a+5,a+2)])
    mesh('foliage',verts,faces,leaf if rng.random()>.3 else young,uvs,smooth=True)
    rod('plant_stem',(x,y,z),(x,y,z+.6*scale),.035*scale,bark,8)

def fern(x,y,z,scale=1):
    """Arched compound fronds; separate pinnae preserve the lacy silhouette."""
    verts=[];faces=[];uvs=[]
    for frond in range(9):
        angle=frond*2.39996+rng.uniform(-.2,.2)
        along=Vector((math.cos(angle),math.sin(angle),0))
        across=Vector((-along.y,along.x,0));length=rng.uniform(.75,1.2)*scale
        rib_start=len(verts)
        for j in range(12):
            t=j/11;p=Vector((x,y,z))+along*(length*t)
            p.z+=scale*(.10+.48*math.sin(t*2.3))
            for side in [-1,1]:
                verts.append(tuple(p+across*(side*.009*scale)));uvs.append((.5+side*.035,t))
        for j in range(11):
            a=rib_start+j*2;faces.append((a,a+1,a+3,a+2))
        for j in range(1,11):
            t=j/11;root=Vector((x,y,z))+along*(length*t)
            root.z+=scale*(.10+.48*math.sin(t*2.3))
            breadth=.25*scale*math.sin(math.pi*t)**.65
            for side in [-1,1]:
                # The central ridge bends each leaflet in three dimensions.
                tip=root+across*(side*breadth)+along*(.12*scale)
                tip.z-=.045*scale
                midpoint=(root+tip)*.5;half=.035*scale*(1-t*.5)
                a=len(verts)
                verts.extend([tuple(root),tuple(midpoint-along*half),
                              tuple(midpoint+Vector((0,0,.014*scale))),
                              tuple(midpoint+along*half),tuple(tip)])
                uvs.extend([(.5,0),(0,.5),(.5,.5),(1,.5),(.5,1)])
                faces.extend([(a,a+1,a+2),(a,a+2,a+3),(a+1,a+4,a+2),(a+2,a+4,a+3)])
    mesh('fern_fronds',verts,faces,young,uvs,smooth=True)

def hanging_vine(x,y,z,inward,length,phase):
    """Continuous hanging stem with alternating leaves attached to that stem."""
    tangent=Vector((-inward.y,inward.x,0));centres=[];segments=18
    for j in range(segments+1):
        t=j/segments
        point=Vector((x,y,z))+inward*(.12+.14*math.sin(t*math.pi))
        point+=tangent*(math.sin(phase+t*5)*.09)
        point.z-=length*t;centres.append(point)
    stemverts=[];stemfaces=[]
    for p in centres:
        for k in range(6):
            a=k*math.tau/6;stemverts.append(tuple(p+Vector((math.cos(a)*.009,math.sin(a)*.009,0))))
    for j in range(segments):
        for k in range(6):
            a=j*6+k;b=j*6+(k+1)%6;stemfaces.append((a,b,b+6,a+6))
    mesh('hanging_vine_stem',stemverts,stemfaces,bark,smooth=True)
    verts=[];faces=[];uvs=[]
    for j in range(1,segments):
        p=centres[j];side=-1 if j%2 else 1
        leaf_axis=(tangent*side*.72+inward*.45+Vector((0,0,-.7))).normalized()
        width_axis=(tangent*.65+Vector((0,0,side*.5))).normalized()
        leaf_length=rng.uniform(.16,.28);leaf_width=leaf_length*.45
        mid=p+leaf_axis*(leaf_length*.42);tip=p+leaf_axis*leaf_length
        a=len(verts)
        verts.extend([tuple(p),tuple(mid-width_axis*leaf_width),
                      tuple(mid+inward*.025),tuple(mid+width_axis*leaf_width),tuple(tip)])
        uvs.extend([(.5,0),(0,.45),(.5,.45),(1,.45),(.5,1)])
        faces.extend([(a,a+1,a+2),(a,a+2,a+3),(a+1,a+4,a+2),(a+2,a+4,a+3)])
    mesh('hanging_vine_leaves',verts,faces,leaf if phase<3 else young,uvs,smooth=True)

planters=[]
# Leave the whole arrival view and southern canal open. Irregular groups at
# the sides/far bank replace the former identical ring of foreground pots.
for i,degree in enumerate([16,48,87,126,160,193,225]):
    a=math.radians(degree);r=5.35+rng.uniform(-.12,.38)
    x=cx+r*math.cos(a);y=cy+r*math.sin(a);radius=rng.uniform(.60,.88)
    height=rng.uniform(.46,.70);planters.append((x,y,radius+.22))
    ring('garden_planter',x,y,radius-.08,radius,.2+height,height,white,steps=40)
    rod('plant_soil',(x,y,.12+height),(x,y,.15+height),radius-.09,soil,32)
    if not BLOCKOUT:
        plant(x-.18,y+.1,.16+height,rng.uniform(.8,1.15),wide=i%2==0)
        fern(x+.22,y-.2,.16+height,rng.uniform(.65,.95))
        if i%2==0:plant(x+.2,y+.18,.16+height,.5,wide=True)
for level,z in enumerate([4.8,8.5]):
    for i in range(12):
        a=math.tau*(i+.17*level)/12+rng.uniform(-.055,.055)
        x=cx+8.62*math.cos(a);y=cy+8.62*math.sin(a)
        ob=box('gallery_garden_bed',(x,y,z+.15),(.85,1.5+rng.random()*.65,.30),white,.06)
        ob.rotation_euler.z=a
        if not BLOCKOUT:
            tangent=Vector((-math.sin(a),math.cos(a),0));inward=Vector((-math.cos(a),-math.sin(a),0))
            plant(x,y,z+.3,rng.uniform(.72,1.05),wide=i%3==0)
            offset=tangent*.45
            fern(x+offset.x,y+offset.y,z+.3,rng.uniform(.6,.88))
            plant(x-offset.x,y-offset.y,z+.3,rng.uniform(.42,.66),wide=True)
            for j in range(3):
                start=Vector((x,y,z+.30))+inward*.48+tangent*((j-1)*.38)
                hanging_vine(*start,inward,rng.uniform(.85,1.9),rng.uniform(0,math.tau))

for x,y,z,r in [(-2,4,6.5,1.05),(-4,8,8,.6),(3,7,9,.75)]:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,radius=r,location=(x,y,z))
    ob=bpy.context.object;ob.name='GEO-DREAM-biosphere';ob.data.materials.append(globe)
    for p in ob.data.polygons:p.use_smooth=True
    ring('biosphere_equator',x,y,r*.99,r*1.035,z,.025,lime,steps=48)
    rod('suspension',(x,y,z+r),(x,y,12.2),.012,silver,8)

# Exterior silhouettes lend depth through the facade.
box('exterior_water_horizon',(cx,cy,-1.1),(180,180,.25),blue,.0)
for i in range(25):
    a=rng.uniform(0,math.tau);r=rng.uniform(19,36);height=rng.uniform(5,20)
    x=cx+r*math.cos(a);y=cy+r*math.sin(a)
    box('tower_island',(x,y,-.35),(3.4,3.4,.7),white,.08)
    box('distant_tower',(x,y,height/2),(rng.uniform(1,2),rng.uniform(1,2),height),white,.08)
    for z in range(2,int(height),2):box('tower_blue_band',(x,y-.8,z),(1.2,.05,.7),screen,.01)

world=bpy.data.worlds.new('DREAM_AtriumSky');world.use_nodes=True;scene.world=world
env=world.node_tree.nodes.new('ShaderNodeTexEnvironment');env.image=bpy.data.images.load(str(ROOT/'assets/textures/cloud_sky.png'),check_existing=True)
if env.image.packed_file:env.image.unpack(method='REMOVE')
env.image.reload();env.texture_mapping.scale=(1,-1,1)
bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');world.node_tree.links.new(env.outputs['Color'],bg.inputs['Color']);bg.inputs['Strength'].default_value=.8
data=bpy.data.lights.new('DREAM_AtriumSun','SUN');data.energy=2
sun=bpy.data.objects.new(data.name,data);scene.collection.objects.link(sun);sun.rotation_euler=(.5,-.4,-.3)
data=bpy.data.lights.new('DREAM_AtriumFill','AREA');data.energy=1600;data.size=10
light=bpy.data.objects.new(data.name,data);scene.collection.objects.link(light);light.location=(0,1,10)
cam=bpy.data.cameras.new('DREAM_AtriumCamera');co=bpy.data.objects.new(cam.name,cam);scene.collection.objects.link(co);scene.camera=co
co.location=(3.5,-3.7,1.85);direction=Vector((math.cos(2.06)*math.cos(.1),math.sin(2.06)*math.cos(.1),math.sin(.1)))
co.rotation_euler=direction.to_track_quat('-Z','Y').to_euler();cam.sensor_fit='VERTICAL';cam.sensor_height=24;cam.lens=24/(2*.82);cam.clip_end=200
scene['dream_navigation']=json.dumps({'boundary':[-1,4,10.0],
    'discs':[[-1,4,4.55]]+[[x,y,.86] for x,y in columns]+[list(p) for p in planters],
    'capsules':channel_capsules})
scene['dream_features']=json.dumps({'channel':'connected curved southern canal',
    'waterfall':{'material_kind':9,'uv':'u across, v bottom 0 to top 1','height_m':7.91},
    'foliage':['broad leaves','lanceolate leaves','compound fern fronds','continuous hanging vines']})
if BLOCKOUT:scene.view_layers[0].material_override=mat('blockout','B4B4B4',.8)
scene.render.filepath=str(ROOT/('validation/atrium-blockout.png' if BLOCKOUT else 'validation/atrium-blender.png'))
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/atrium.blend'))
print(json.dumps({'scene':scene.name,'objects':len(scene.objects),'stage':scene['dream_stage']}))
