"""Execute inside Blender through MCP. Owns only scene DREAM_PastelRoom.

Coordinates: metres, X right, Y toward doorway, Z up. Runtime preserves them.
Set DREAM_BLOCKOUT=True in globals for a composition preview.
"""
import bpy, math, json, struct
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
BLOCKOUT=globals().get('DREAM_BLOCKOUT',False)
name='DREAM_PastelRoom'
old=bpy.data.scenes.get(name)
if old:
    for obj in list(old.objects):
        bpy.data.objects.remove(obj,do_unlink=True)
    bpy.data.scenes.remove(old)
scene=bpy.data.scenes.new(name)
bpy.context.window.scene=scene
scene.unit_settings.system='METRIC'
scene.render.resolution_x=960
scene.render.resolution_y=720
scene.render.resolution_percentage=100
try: scene.render.engine='BLENDER_EEVEE'
except TypeError: scene.render.engine='BLENDER_EEVEE_NEXT'
scene.eevee.taa_render_samples=64
scene.eevee.use_raytracing=True
scene.render.image_settings.file_format='PNG'
scene.view_settings.exposure=-.15

def linear(c):
    return ((c+.055)/1.055)**2.4 if c>.04045 else c/12.92
materials=[]
def image_asset(name,non_color=False):
    im=bpy.data.images.load(str(ROOT/'assets/textures'/f'{name}.png'),check_existing=True)
    if im.packed_file: im.unpack(method='REMOVE')
    im.reload()
    if non_color: im.colorspace_settings.name='Non-Color'
    return im

def material(label,hexcolor,rough=.4,metal=0,kind=0,texture=None):
    color=[int(hexcolor[i:i+2],16)/255 for i in (0,2,4)]
    m=bpy.data.materials.new('DREAM_MAT_'+label);m.use_nodes=True
    p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    p.inputs['Base Color'].default_value=tuple(linear(v) for v in color)+(1,)
    p.inputs['Roughness'].default_value=rough
    p.inputs['Metallic'].default_value=metal
    if kind==1: p.inputs['Coat Weight'].default_value=.5
    m['dream_id']=len(materials);m['base_srgb']=color;m['roughness']=rough;m['metallic']=metal;m['kind']=kind
    if texture:
        node=m.node_tree.nodes.new('ShaderNodeTexImage')
        node.image=image_asset(texture)
        m.node_tree.links.new(node.outputs['Color'],p.inputs['Base Color'])
    if kind in (1,3):
        normal=m.node_tree.nodes.new('ShaderNodeTexImage');normal.image=image_asset('ceramic_normal',True)
        nm=m.node_tree.nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.18
        m.node_tree.links.new(normal.outputs['Color'],nm.inputs['Color'])
        m.node_tree.links.new(nm.outputs['Normal'],p.inputs['Normal'])
        tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=image_asset('ceramic_roughness',True)
        scale=m.node_tree.nodes.new('ShaderNodeMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=rough/.27
        m.node_tree.links.new(tex.outputs['Color'],scale.inputs[0]);m.node_tree.links.new(scale.outputs[0],p.inputs['Roughness'])
    materials.append(m)
    return m

pink=material('pink_glaze','DCA3B7',.32,0,3)
mint=material('mint_glaze','9AC3BA',.32,0,3)
ivory=material('ivory_paint','E6DAD8',.38)
grout=material('grout','CBCDC7',.8)
chrome=material('chrome','BAC4CA',.2,1)
gold=material('door_handle','C8AA65',.25,1)
floorpink=material('floor_pink','C9ABC2',.16,0,1)
floormint=material('floor_mint','95BBB5',.16,0,1)
cloth=material('plaid','FFFFFF',.85,0,2,'curtain_plaid')
ceiling=material('ceiling','D4D9D3',.83)

def box(label,pos,size,mat,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=pos)
    o=bpy.context.object;o.name='GEO-DREAM-'+label;o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(mat)
    if bevel:
        mod=o.modifiers.new('Rounded edges','BEVEL');mod.width=bevel;mod.segments=2 if bevel>.02 else 1
    return o

def rod(label,a,b,r,mat):
    delta=Vector(b)-Vector(a)
    bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=r,depth=delta.length,location=(Vector(a)+Vector(b))/2)
    o=bpy.context.object;o.name='GEO-DREAM-'+label
    o.rotation_euler=delta.to_track_quat('Z','Y').to_euler();o.data.materials.append(mat)
    for p in o.data.polygons:p.use_smooth=True
    return o

# The doorway is a real hole, never a dark painted rectangle.
box('subfloor',(0,0,-.08),(4.8,5.4,.15),grout)
for ix in range(8):
    for iy in range(9):
        box('floor',(-2.1+ix*.6,-2.4+iy*.6,.005),(.597,.597,.022),floormint if (ix+iy)%2 else floorpink,.008)
box('ceiling',(0,0,3.12),(5,5.6,.2),ceiling)
# Continuous mortar behind the tiles closes joints without sealing openings.
box('front_grout_left',(-2.115,2.78,1.5),(.57,.04,3),grout)
box('front_grout_right',(1.015,2.78,1.5),(2.77,.04,3),grout)
box('front_grout_top',(-1.1,2.78,2.88),(1.46,.04,.24),grout)
box('right_grout_back',(2.48,-1.35,1.5),(.04,2.7,3),grout)
box('right_grout_front',(2.48,2.25,1.5),(.04,.9,3),grout)
box('right_grout_below',(2.48,.9,.6),(.04,1.8,1.2),grout)
box('right_grout_above',(2.48,.9,2.85),(.04,1.8,.3),grout)
# Front wall y=2.7: door x in [-1.85,-.35], z below 2.75.
for ix in range(16):
    for iz in range(10):
        x=-2.25+ix*.3;z=.15+iz*.3
        if -1.85<x<-.35 and z<2.75:continue
        mat=pink if (iz//2+ix//4)%3==0 else mint
        box('front_tile',(x,2.73,z),(.297,.07,.297),mat,.004)
# Window x=2.4 wall, y .0..1.8 and z 1.3..2.8.
for iy in range(18):
    for iz in range(10):
        y=-2.55+iy*.3;z=.15+iz*.3
        if -.02<y<1.82 and 1.32<z<2.82:continue
        mat=pink if (iz//2+iy//4)%3==0 else mint
        box('right_tile',(2.43,y,z),(.07,.297,.297),mat,.004)
# Other walls ensure the camera can turn freely.
box('left_wall',(-2.46,0,1.5),(.1,5.4,3),mint)
box('back_wall',(0,-2.76,1.5),(5,.1,3),pink)
for x in [-1.9,-.3]:box('door_casing',(x,2.64,1.4),(.14,.16,2.84),ivory,.014)
box('door_lintel',(-1.1,2.64,2.82),(1.74,.16,.15),ivory,.014)
box('threshold',(-1.1,2.73,.025),(1.6,.36,.05),ivory,.01)
# Door opens inward from left hinge. Decorative panels share its transform.
hinge=bpy.data.objects.new('DREAM_DoorHinge',None);scene.collection.objects.link(hinge)
hinge.location=(-1.82,2.6,0);hinge.rotation_euler.z=math.radians(-77)
door=box('door_leaf',(.73,0,1.35),(1.46,.055,2.7),ivory,.018);door.parent=hinge
for z in [.68,1.98]:
    for x in [.38,1.08]:
        p=box('door_panel',(x,-.04,z),(.57,.035,1.0),ivory,.028);p.parent=hinge
handle=rod('handle',(1.21,-.11,1.3),(1.38,-.11,1.3),.022,gold);handle.parent=hinge
for y in [-.06,1.86]:box('window_casing',(2.36,y,2.06),(.16,.1,1.68),ivory,.012)
for z in [1.28,2.84]:box('window_casing',(2.36,.9,z),(.16,2.02,.12),ivory,.012)
box('window_mullion',(2.34,.9,2.32),(.13,1.88,.07),ivory,.012)
box('window_sill',(2.25,.9,1.25),(.42,2.1,.09),ivory,.015)
rod('curtain_rail',(2.17,-.48,2.96),(2.17,2.18,2.96),.018,chrome)
for center in [-.22,2.02]:
    verts=[];faces=[];uv=[];nx=32;nz=8
    for j in range(nz+1):
        for i in range(nx+1):
            u=i/nx;v=j/nz
            verts.append((2.15+.055*math.cos(u*math.tau*5),center+(u-.5)*.68,1.3+v*1.6+.025*math.cos(u*math.tau*5)))
    for j in range(nz):
        for i in range(nx):
            a=j*(nx+1)+i;faces.append((a,a+1,a+nx+2,a+nx+1))
    mesh=bpy.data.meshes.new('DREAM_curtain');mesh.from_pydata(verts,[],faces);mesh.materials.append(cloth)
    layer=mesh.uv_layers.new()
    for poly in mesh.polygons:
        poly.use_smooth=True
        for li in poly.loop_indices:
            vi=mesh.loops[li].vertex_index;layer.data[li].uv=((vi%(nx+1))/nx,(vi//(nx+1))/nz*2)
    o=bpy.data.objects.new('GEO-DREAM-curtain',mesh);scene.collection.objects.link(o)
for i in range(18):
    y=.12+i*.085
    rod('radiator_fin',(2.19,y,.18),(2.19,y,.93),.026,chrome)
for z in [.22,.88]:rod('radiator_pipe',(2.23,.08,z),(2.23,1.64,z),.036,chrome)
box('skirting_left',(-2.38,0,.06),(.08,5.4,.12),ivory,.008)
box('skirting_right',(2.37,0,.06),(.08,5.4,.12),ivory,.008)

world=bpy.data.worlds.new('DREAM_Sky');world.use_nodes=True;scene.world=world
nodes=world.node_tree.nodes;bg=next(n for n in nodes if n.type=='BACKGROUND')
env=nodes.new('ShaderNodeTexEnvironment');env.image=image_asset('cloud_sky')
world.node_tree.links.new(env.outputs['Color'],bg.inputs['Color']);bg.inputs['Strength'].default_value=.7

def area(label,loc,target,energy,color,size):
    data=bpy.data.lights.new('DREAM_'+label,'AREA');data.energy=energy;data.color=color;data.size=size
    obj=bpy.data.objects.new(data.name,data);scene.collection.objects.link(obj);obj.location=loc
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
area('door_softbox',(-1.1,3.6,2),(0,0,1),180,(.83,.87,1),3)
area('window_softbox',(3.3,.9,2.2),(0,0,1),220,(1,.85,.94),2.2)
area('ceiling_fill',(0,-.5,2.9),(0,.5,0),95,(.85,1,.96),3.5)
cam=bpy.data.cameras.new('DREAM_Camera');co=bpy.data.objects.new('DREAM_Camera',cam);scene.collection.objects.link(co);scene.camera=co
co.location=(-.05,-1.35,1.6);target=co.location+Vector((math.cos(1.32)*math.cos(-.24),math.sin(1.32)*math.cos(-.24),math.sin(-.24)))*4
co.rotation_euler=(target-co.location).to_track_quat('-Z','Y').to_euler();cam.sensor_fit='VERTICAL';cam.sensor_height=24;cam.lens=24/(2*.9);cam.clip_end=250
scene['dream_reference']='video-35, 11 seconds'
scene['dream_stage']='blockout' if BLOCKOUT else 'materials-v2'
scene['dream_asset']='pastel_room'
if BLOCKOUT:
    grey=material('blockout','C2C2C2',.7)
    scene.view_layers[0].material_override=grey
scene.render.filepath=str(ROOT/'validation'/('room-blockout.png' if BLOCKOUT else 'room-blender.png'))
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/pastel_room.blend'))
print(json.dumps({'scene':scene.name,'objects':len(scene.objects),'stage':scene['dream_stage'],'blend':bpy.data.filepath,'render':scene.render.filepath}))
