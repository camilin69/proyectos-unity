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
scene.render.resolution_x=720
scene.render.resolution_y=1280
scene.render.resolution_percentage=100
try: scene.render.engine='BLENDER_EEVEE'
except TypeError: scene.render.engine='BLENDER_EEVEE_NEXT'
scene.eevee.taa_render_samples=256
scene.eevee.use_raytracing=True
scene.eevee.ray_tracing_options.resolution_scale='1'
scene.eevee.ray_tracing_options.screen_trace_quality=1
scene.render.image_settings.file_format='PNG'
scene.view_settings.view_transform='Standard'
scene.view_settings.exposure=.10

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
    if kind==1:
        p.inputs['Coat Weight'].default_value=1
        p.inputs['Specular IOR Level'].default_value=1
    m['dream_id']=len(materials);m['base_srgb']=color;m['roughness']=rough;m['metallic']=metal;m['kind']=kind
    if texture:
        node=m.node_tree.nodes.new('ShaderNodeTexImage')
        node.image=image_asset(texture)
        m.node_tree.links.new(node.outputs['Color'],p.inputs['Base Color'])
    if kind in (1,3):
        normal=m.node_tree.nodes.new('ShaderNodeTexImage');normal.image=image_asset('floor_normal' if kind==1 else 'ceramic_normal',True)
        nm=m.node_tree.nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.18 if kind==3 else .65
        m.node_tree.links.new(normal.outputs['Color'],nm.inputs['Color'])
        m.node_tree.links.new(nm.outputs['Normal'],p.inputs['Normal'])
        if kind==1:m.node_tree.links.new(nm.outputs['Normal'],p.inputs['Coat Normal'])
        tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=image_asset('ceramic_roughness',True)
        scale=m.node_tree.nodes.new('ShaderNodeMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=rough/.27
        m.node_tree.links.new(tex.outputs['Color'],scale.inputs[0]);m.node_tree.links.new(scale.outputs[0],p.inputs['Roughness'])
    materials.append(m)
    return m

pink=material('pink_glaze','DCA3B7',.32,0,3)
mint=material('mint_glaze','9AC3BA',.32,0,3)
ivory=material('ivory_paint','D6CCBB',.48)
grout=material('grout','E1DFD3',.8)
chrome=material('chrome','C4C8C9',.18,1)
gold=material('door_handle','C8AA65',.25,1)
floorfinish=material('floor_finish','A8B1A8',.13,0,1,'floor_surface_albedo');floorfinish['albedo_variant']=2
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
    # Cap normals must not bend the side of a straight tube. A smooth cap had
    # introduced a +/-0.65 axial component along the whole radiator, breaking
    # reflections into horizontal bands in both renderers.
    for p in o.data.polygons:p.use_smooth=len(p.vertices)==4
    for e in o.data.edges:
        e.use_edge_sharp=abs(o.data.vertices[e.vertices[0]].co.z-o.data.vertices[e.vertices[1]].co.z)<1e-6
    return o

def tile_face(label,center,width,height,mat,front=True):
    # The closed mortar wall provides thickness; its glaze is a flat face.
    # Subpixel side faces create dark dashed joints in a distant raster view.
    if front:verts=[(-width/2,0,-height/2),(width/2,0,-height/2),(width/2,0,height/2),(-width/2,0,height/2)]
    else:verts=[(0,-width/2,-height/2),(0,-width/2,height/2),(0,width/2,height/2),(0,width/2,-height/2)]
    me=bpy.data.meshes.new('DREAM_glazed_tile');me.from_pydata(verts,[],[(0,1,2,3)]);me.materials.append(mat)
    uv=me.uv_layers.new()
    for i,point in enumerate([(0,0),(1,0),(1,1),(0,1)]):uv.data[i].uv=point
    o=bpy.data.objects.new('GEO-DREAM-'+label,me);scene.collection.objects.link(o);o.location=center
    return o

# The doorway is a real hole, never a dark painted rectangle.
# Continuous wet coating over the checkerboard. The top is subdivided to retain
# local contact AO while avoiding hundreds of visible bevel edges in reflection.
nx,ny=20,36
verts=[(-2.4+2.85*i/nx,-2.7+5.4*j/ny,.016) for j in range(ny+1) for i in range(nx+1)]
faces=[]
for j in range(ny):
    for i in range(nx):
        a=j*(nx+1)+i;faces.append((a,a+1,a+nx+2,a+nx+1))
perimeter=list(range(nx+1))+[j*(nx+1)+nx for j in range(1,ny+1)]+[ny*(nx+1)+i for i in range(nx-1,-1,-1)]+[j*(nx+1) for j in range(ny-1,0,-1)]
bottom_start=len(verts)
verts.extend((verts[i][0],verts[i][1],-.1) for i in perimeter)
bottom_center=len(verts);verts.append((-.975,0,-.1))
for k,top in enumerate(perimeter):
    next_k=(k+1)%len(perimeter)
    faces.append((perimeter[next_k],top,bottom_start+k,bottom_start+next_k))
    faces.append((bottom_center,bottom_start+next_k,bottom_start+k))
floor_mesh=bpy.data.meshes.new('DREAM_continuous_floor');floor_mesh.from_pydata(verts,[],faces);floor_mesh.materials.append(floorfinish)
layer=floor_mesh.uv_layers.new()
for loop in floor_mesh.loops:
    p=floor_mesh.vertices[loop.vertex_index].co;layer.data[loop.index].uv=((p.x+2.4)/2.85,(p.y+2.7)/5.4)
o=bpy.data.objects.new('GEO-DREAM-floor_surface',floor_mesh);scene.collection.objects.link(o)
o.hide_probe_plane=True  # A planar probe must not capture the slab's underside.
box('ceiling',(-.975,0,3.3),(3.05,5.6,.2),ceiling)
# Continuous mortar behind the tiles closes joints without sealing openings.
wall_top=3.22;door_top=2.65
wy0,wy1,wz0,wz1=.7,1.65,1.4,2.5
wc=(wy0+wy1)/2
box('front_grout_left',(-2.125,2.78,wall_top/2),(.55,.04,wall_top),grout)
box('front_grout_right',(.05,2.78,wall_top/2),(.8,.04,wall_top),grout)
box('front_grout_top',(-1.1,2.78,(wall_top+door_top)/2),(1.5,.04,wall_top-door_top),grout)
for label,ya,yb,za,zb in [('back',-2.7,wy0,0,wall_top),('front',wy1,2.7,0,wall_top),('below',wy0,wy1,0,wz0),('above',wy0,wy1,wz1,wall_top)]:
    box('right_grout_'+label,(2.48,(ya+yb)/2,(za+zb)/2),(.04,yb-ya,zb-za),grout)
def subdivisions(lo,hi,extra=()):
    return sorted(set([lo,hi,*extra]+[round(lo+i*.2,4) for i in range(1,math.ceil((hi-lo)/.2)) if lo+i*.2<hi]))
def wall_color(z,along,front=False):
    if z>3.08:return mint
    if z>2.55:return pink
    if front:return pink if (.40<z<.95 or 1.50<z<2.05) and along<.29 else mint
    return pink if (int((z+.1)/.55)+int((along+2.7)/.8))%3!=1 else mint
# Explicitly include aperture boundaries so no tile seals either opening.
xs=subdivisions(-2.4,.45,(-1.85,-.35));zs=subdivisions(0,wall_top,(door_top,))
for left,right in zip(xs,xs[1:]):
    for bottom,top in zip(zs,zs[1:]):
        x=(left+right)/2;z=(bottom+top)/2
        if -1.85<x<-.35 and z<door_top:continue
        tile_face('front_tile',(x,2.695,z),right-left-.007,top-bottom-.007,wall_color(z,x,True))
ys=subdivisions(-2.7,2.7,(wy0,wy1));zs=subdivisions(0,wall_top,(wz0,wz1))
for near,far in zip(ys,ys[1:]):
    for bottom,top in zip(zs,zs[1:]):
        y=(near+far)/2;z=(bottom+top)/2
        if wy0<y<wy1 and wz0<z<wz1:continue
        tile_face('right_tile',(2.395,y,z),far-near-.007,top-bottom-.007,wall_color(z,y),False)
# Other walls ensure the camera can turn freely.
box('left_wall',(-2.46,0,wall_top/2),(.1,5.4,wall_top),mint)
box('back_wall',(-.975,-2.76,wall_top/2),(3.05,.1,wall_top),pink)
for x in [-1.9,-.3]:box('door_casing',(x,2.64,1.335),(.14,.16,2.71),ivory,.014)
box('door_lintel',(-1.1,2.64,2.7),(1.74,.16,.15),ivory,.014)
box('threshold',(-1.1,2.73,.025),(1.6,.36,.05),ivory,.01)
# Door opens inward from left hinge. Decorative panels share its transform.
hinge=bpy.data.objects.new('DREAM_DoorHinge',None);scene.collection.objects.link(hinge)
hinge.location=(-1.82,2.6,0);hinge.rotation_euler.z=math.radians(-77)
door=box('door_leaf',(.73,0,1.275),(1.46,.055,2.55),ivory,.018);door.parent=hinge
for side in [-1,1]:
    for z in [.65,1.86]:
        for x in [.38,1.08]:
            p=box('door_panel',(x,side*.04,z),(.57,.035,1.0),ivory,.028);p.parent=hinge
handle=rod('handle',(1.21,-.11,1.3),(1.38,-.11,1.3),.022,gold);handle.parent=hinge
for y in [wy0-.04,wy1+.04]:box('window_casing',(2.36,y,(wz0+wz1)/2),(.16,.1,wz1-wz0+.20),ivory,.012)
for z in [wz0-.04,wz1+.04]:box('window_casing',(2.36,wc,z),(.16,wy1-wy0+.2,.12),ivory,.012)
box('window_mullion',(2.34,wc,2.16),(.13,wy1-wy0,.055),ivory,.012)
box('window_sill',(2.25,wc,wz0-.09),(.42,wy1-wy0+.3,.07),ivory,.015)
rod('curtain_rail',(2.17,wy0-.24,2.7),(2.17,wy1+.24,2.7),.018,chrome)
curtain_ns={}
exec((ROOT/'blender/curtain_mesh.py').read_text(encoding='utf-8'),curtain_ns)
for index,data in enumerate(curtain_ns['make_room_curtains'](wy0,wy1)):
    mesh=bpy.data.meshes.new(f'DREAM_curtain_{index}');mesh.from_pydata(data['vertices'],[],data['faces']);mesh.materials.append(cloth)
    layer=mesh.uv_layers.new()
    for poly,uvs,smooth in zip(mesh.polygons,data['face_uvs'],data['smooth_faces']):
        poly.use_smooth=smooth
        for li,uv in zip(poly.loop_indices,uvs):layer.data[li].uv=uv
    sharp={tuple(sorted(e)) for e in data['sharp_edges']}
    for edge in mesh.edges:edge.use_edge_sharp=tuple(sorted(edge.vertices)) in sharp
    mesh.update()
    o=bpy.data.objects.new(f'GEO-DREAM-curtain-{index}',mesh);scene.collection.objects.link(o)
for i in range(24):
    y=.12+i*(1.055-.12)/23
    rod('radiator_fin',(2.19,y,.18),(2.19,y,.93),.016,chrome)
for z in [.22,.88]:rod('radiator_pipe',(2.23,.08,z),(2.23,1.10,z),.024,chrome)
box('skirting_left',(-2.38,0,.06),(.08,5.4,.12),ivory,.008)
box('skirting_right',(2.37,0,.06),(.08,5.4,.12),ivory,.008)
# The reference places the window wall close to the doorway (0.75 m return).
for obj in list(scene.objects):
    if any(obj.name.startswith('GEO-DREAM-'+part) for part in ['right_','window_','curtain','radiator_','skirting_right']):obj.location.x-=1.95
    if obj.name.startswith('GEO-DREAM-front_grout'):obj.location.y-=.06
    if obj.name.startswith('GEO-DREAM-right_grout'):obj.location.x-=.06

world=bpy.data.worlds.new('DREAM_Sky');world.use_nodes=True;scene.world=world
nodes=world.node_tree.nodes;bg=next(n for n in nodes if n.type=='BACKGROUND')
env=nodes.new('ShaderNodeTexEnvironment');env.image=image_asset('cloud_sky')
# Match runtime longitude (+atan2) to Blender's reversed environment longitude.
env.texture_mapping.scale=(1,-1,1)
world.node_tree.links.new(env.outputs['Color'],bg.inputs['Color']);bg.inputs['Strength'].default_value=1

# Local reflections retain the room's colors when screen-space rays miss.
probe=bpy.data.lightprobes.new('DREAM_room_reflection','SPHERE')
probe.influence_type='BOX';probe.influence_distance=1;probe.falloff=.2
probe.clip_start=.05;probe.clip_end=20;probe.use_custom_parallax=True
probe.parallax_type='BOX';probe.parallax_distance=1
obj=bpy.data.objects.new(probe.name,probe);scene.collection.objects.link(obj)
obj.location=(-.85,.3,1.45);obj.scale=(1.42,2.7,1.6)
plane=bpy.data.lightprobes.new('DREAM_floor_reflection','PLANE')
plane.influence_distance=.1;plane.clip_start=.005
obj=bpy.data.objects.new(plane.name,plane);scene.collection.objects.link(obj)
obj.location=(-.975,0,.026);obj.scale=(1.425,2.7,1)

def area(label,loc,target,energy,color,size):
    data=bpy.data.lights.new('DREAM_'+label,'AREA');data.energy=energy;data.color=color;data.size=size;data.specular_factor=0
    obj=bpy.data.objects.new(data.name,data);scene.collection.objects.link(obj);obj.location=loc
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
    return obj
area('door_softbox',(-1.1,3.6,2),(0,0,1),105,(1,.83,.60),3)
area('window_softbox',(1.35,.9,2.2),(-.975,0,1),121,(1,.83,.60),2.2)
area('ceiling_fill',(-.975,-.5,3.10),(-.975,.5,0),25,(1,.83,.60),3.5)
reference_fill=area('reference_fill',(-.7,1.2,1.5),(-.7,2.7,1.5),27,(.70,.48,.39),2.2)
area('bounce_fill',(-1.65,-1.8,1.65),(-.85,1.2,1.5),40,(.8,.76,.70),3)
# Art-directed indirect returns. Receiver links keep the sky fill on the
# front mint wall and the bright floor's specular return on the radiator.
def link_receivers(light,label,receivers):
    collection=bpy.data.collections.get(label) or bpy.data.collections.new(label)
    for obj in receivers:
        if obj.name not in collection.objects:collection.objects.link(obj)
    light.light_linking.receiver_collection=collection
soft_receivers=[o for o in scene.objects if o.type=='MESH' and (o.active_material==ivory or o.name.startswith('GEO-DREAM-right_'))]
link_receivers(reference_fill,'DREAM_reference_full_receivers',
               [o for o in scene.objects if o.type=='MESH' and o not in soft_receivers])
soft_fill=area('reference_soft_fill',(-.7,1.2,1.5),(-.7,2.7,1.5),13.5,(.70,.48,.39),2.2)
link_receivers(soft_fill,'DREAM_reference_soft_receivers',soft_receivers)
mint_fill=area('mint_sky_fill',(-1,.9,2.5),(-.8,2.7,2.4),14,(.70,.83,1),2.2)
link_receivers(mint_fill,'DREAM_mint_sky_fill_receivers',
               [o for o in scene.objects if o.name.startswith('GEO-DREAM-front_tile') and o.active_material==mint and o.location.z>2.05])
chrome_return=area('chrome_strip',(-1.2,-.7,.05),(-1.2,-.7,1.05),12,(.90,.96,1),1)
chrome_return.data.shape='RECTANGLE';chrome_return.data.size_y=3
chrome_return.data.diffuse_factor=0;chrome_return.data.specular_factor=1
link_receivers(chrome_return,'DREAM_chrome_strip_receivers',
               [o for o in scene.objects if o.name.startswith('GEO-DREAM-radiator')])
# Local warm wall return offsets the blue sky cast on the inward door face.
# Keep its receivers on the hinged paint/handle, preserving frame calibration.
door_return=area('door_color_return',(-2.15,.3,1.5),(-1.65,1.85,1.3),14,(1,.03,.06),2)
link_receivers(door_return,'DREAM_door_color_receivers',
               [o for o in scene.objects if o.type=='MESH' and o.parent==hinge])
cam=bpy.data.cameras.new('DREAM_Camera');co=bpy.data.objects.new('DREAM_Camera',cam);scene.collection.objects.link(co);scene.camera=co
co.location=(-1.5,-2.0,1.4);target=co.location+Vector((math.cos(1.29)*math.cos(-.21),math.sin(1.29)*math.cos(-.21),math.sin(-.21)))*4
co.rotation_euler=(target-co.location).to_track_quat('-Z','Y').to_euler();cam.sensor_fit='VERTICAL';cam.sensor_height=24;cam.lens=24/(2*.7);cam.clip_end=250
scene['dream_reference']='video-35, 11 seconds'
scene['dream_stage']='blockout' if BLOCKOUT else 'reference-finish-v7'
scene['dream_asset']='pastel_room'
if BLOCKOUT:
    grey=material('blockout','C2C2C2',.7)
    scene.view_layers[0].material_override=grey
scene.render.filepath=str(ROOT/'validation'/('room-blockout.png' if BLOCKOUT else 'room-blender.png'))
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/pastel_room.blend'))
print(json.dumps({'scene':scene.name,'objects':len(scene.objects),'stage':scene['dream_stage'],'blend':bpy.data.filepath,'render':scene.render.filepath}))
