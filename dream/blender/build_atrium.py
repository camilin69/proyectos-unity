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
scene['dream_stage']='blockout' if BLOCKOUT else 'materials-v1'
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
    if kind in (4,6):
        p.inputs['Transmission Weight'].default_value=.9
        p.inputs['IOR'].default_value=1.333 if kind==4 else 1.46
        if kind==4:
            tex=m.node_tree.nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=9
            bump=m.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.15;bump.inputs['Distance'].default_value=.08
            m.node_tree.links.new(tex.outputs['Fac'],bump.inputs['Height']);m.node_tree.links.new(bump.outputs['Normal'],p.inputs['Normal'])
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
lime=mat('lime_band','A9DF38',.2,0,7)
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
ring('ground_gallery',cx,cy,4.3,10.5,.2,.25,floor)
ring('pool_edge',cx,cy,4.21,4.34,.25,.18,lime)
rod('pool_basin',(cx,cy,-.75),(cx,cy,-.65),4.23,blue,96)
ring('pool_side',cx,cy,4.18,4.25,.04,.74,blue)
# Dense water grid clipped to a disk, allowing real vertex waves in C++.
verts=[(cx,cy,.055)];faces=[];uv=[(.5,.5)];n=128
for j in range(1,49):
    for i in range(n):
        a=math.tau*i/n;r=4.22*j/48;x=r*math.cos(a);y=r*math.sin(a)
        verts.append((cx+x,cy+y,.055));uv.append((x/8.44+.5,y/8.44+.5))
for i in range(n):faces.append((0,1+i,1+(i+1)%n))
for j in range(47):
    for i in range(n):
        a=1+j*n+i;b=1+j*n+(i+1)%n;faces.append((a,a+n,b+n,b))
mesh('water',verts,faces,water,uv,smooth=True)

for z in [4.8,8.5]:
    ring('upper_gallery',cx,cy,8.2,10.5,z,.32,white)
    ring('luminous_fascia',cx,cy,8.15,8.26,z-.1,.14,lime)
    ring('gallery_handrail',cx,cy,8.18,8.22,z+1.05,.045,silver)
    for i in range(40):
        a=math.tau*i/40;x=cx+8.2*math.cos(a);y=cy+8.2*math.sin(a)
        rod('balustrade_post',(x,y,z),(x,y,z+1.02),.022,silver,8)

columns=[]
for degree in [-35,205,65,125]:
    a=math.radians(degree);x=cx+7*math.cos(a);y=cy+7*math.sin(a);columns.append((x,y))
    rod('column_core',(x,y,.2),(x,y,11.1),.42,white,24)
    rod('column_glass',(x,y,.28),(x,y,10.8),.68,column_glass,32)
    for z in [.3,3.7,7.1,10.8]:ring('column_lime',x,y,.65,.74,z,.12,lime,steps=32)
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
ring('oculus',cx,cy,1.9,2.1,12.5,.12,lime)

def plant(x,y,z,scale=1):
    verts=[];faces=[];uvs=[]
    # Curved lanceolate leaves, deliberately meshed rather than opaque cards.
    for k in range(18):
        angle=k*2.39996+rng.uniform(-.18,.18);length=rng.uniform(.65,1.5)*scale
        spread=rng.uniform(.45,.95);height=rng.uniform(.6,1.2)*scale
        start=len(verts)
        for j in range(9):
            t=j/8;reach=length*t*spread
            zz=z+height*math.sin(t*1.9)+.05*scale
            for side in [-1,0,1]:
                width=math.sin(math.pi*t)**.75*.10*scale*side
                verts.append((x+reach*math.cos(angle)-width*math.sin(angle),y+reach*math.sin(angle)+width*math.cos(angle),zz-abs(side)*.025*scale))
                uvs.append(((side+1)/2,t))
        for j in range(8):
            a=start+j*3;faces.extend([(a,a+3,a+4,a+1),(a+1,a+4,a+5,a+2)])
    mesh('foliage',verts,faces,leaf if rng.random()>.3 else young,uvs,smooth=True)
    rod('plant_stem',(x,y,z),(x,y,z+.6*scale),.035*scale,bark,8)

planters=[]
for i in range(14):
    a=math.tau*i/14
    x=cx+5.35*math.cos(a);y=cy+5.35*math.sin(a);planters.append((x,y))
    ring('planter',x,y,.44,.55,.65,.45,white,steps=24)
    rod('plant_soil',(x,y,.56),(x,y,.59),.44,soil,24)
    if not BLOCKOUT:plant(x,y,.6,.9)
for z in [4.8,8.5]:
    for i in range(18):
        a=math.tau*i/18;x=cx+8.6*math.cos(a);y=cy+8.6*math.sin(a)
        box('gallery_planter',(x,y,z+.15),(.7,.7,.3),white,.08)
        if not BLOCKOUT:
            plant(x,y,z+.3,.72)
            # Cascading vines add an irregular silhouette below the galleries.
            for j in range(3):plant(x-.25,y,z-.2-j*.32,.25)

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
bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');world.node_tree.links.new(env.outputs['Color'],bg.inputs['Color']);bg.inputs['Strength'].default_value=.8
data=bpy.data.lights.new('DREAM_AtriumSun','SUN');data.energy=2
sun=bpy.data.objects.new(data.name,data);scene.collection.objects.link(sun);sun.rotation_euler=(.5,-.4,-.3)
data=bpy.data.lights.new('DREAM_AtriumFill','AREA');data.energy=1600;data.size=10
light=bpy.data.objects.new(data.name,data);scene.collection.objects.link(light);light.location=(0,1,10)
cam=bpy.data.cameras.new('DREAM_AtriumCamera');co=bpy.data.objects.new(cam.name,cam);scene.collection.objects.link(co);scene.camera=co
co.location=(3.5,-3.7,1.85);direction=Vector((math.cos(2.06)*math.cos(.1),math.sin(2.06)*math.cos(.1),math.sin(.1)))
co.rotation_euler=direction.to_track_quat('-Z','Y').to_euler();cam.sensor_fit='VERTICAL';cam.sensor_height=24;cam.lens=24/(2*.82);cam.clip_end=200
scene['dream_navigation']=json.dumps({'boundary':[-1,4,10.0],'discs':[[-1,4,4.55]]+[[x,y,.86] for x,y in columns]+[[x,y,.75] for x,y in planters]})
if BLOCKOUT:scene.view_layers[0].material_override=mat('blockout','B4B4B4',.8)
scene.render.filepath=str(ROOT/('validation/atrium-blockout.png' if BLOCKOUT else 'validation/atrium-blender.png'))
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/atrium.blend'))
print(json.dumps({'scene':scene.name,'objects':len(scene.objects),'stage':scene['dream_stage']}))
