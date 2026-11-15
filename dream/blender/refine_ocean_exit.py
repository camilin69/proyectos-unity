"""Apply measured foreground corrections to the isolated initial ocean study via MCP."""
from pathlib import Path
import json, math
import bpy
from mathutils import Vector, Quaternion
from bpy_extras.object_utils import world_to_camera_view

ROOT=Path(__file__).resolve().parents[1]
s=bpy.data.scenes['DREAM_OceanExit']
assert not s.get('ocean_refinement_v2'), 'Already refined; inspect rather than apply twice.'
for side in [-1,1]:
    for part in ['low_border','pink_cap']:
        ob=s.objects[f'GEO-DREAM-ocean-{part}_{side}']
        for v in ob.data.vertices:
            # Narrow the borders around the observed inner endpoints; preserve depth.
            v.co.x=side*(.36+(abs(v.co.x)-.66)/3)
        ob.data.update()
        for poly in ob.data.polygons:
            axis=max(range(3),key=lambda k:abs(poly.normal[k]))
            axes=[k for k in range(3) if k!=axis]
            for li in poly.loop_indices:
                v=ob.data.vertices[ob.data.loops[li].vertex_index].co
                ob.data.uv_layers.active.data[li].uv=(v[axes[0]]/.16,v[axes[1]]/.16)
post=s.objects['GEO-DREAM-ocean-bent_access_post']
for v in post.data.vertices:
    v.co.x=.585+(v.co.x-.88)*.73
    v.co.y=2.547+(v.co.y-3.35)*.73
    v.co.z*=.65
post.data.update()

def bsdf(name):
    m=bpy.data.materials['MAT-DREAM-ocean-'+name]
    return m,next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
m,b=bsdf('interior_water')
r=next(n for n in m.node_tree.nodes if n.type=='VALTORGB')
r.color_ramp.elements[0].color=(.08,.25,.24,1)
r.color_ramp.elements[1].color=(.24,.40,.37,1)
b.inputs['Roughness'].default_value=.18
next(n for n in m.node_tree.nodes if n.type=='BUMP').inputs['Distance'].default_value=.009
m,b=bsdf('ocean');b.inputs['Base Color'].default_value=(.012,.035,.045,1)
b.inputs['Transmission Weight'].default_value=0;b.inputs['Roughness'].default_value=.23
for name,power in [('ceiling',180),('front_fill',90)]:
    light=s.objects['LIGHT-DREAM-ocean-'+name].data;light.energy=power;light.specular_factor=.12
light=s.objects['LIGHT-DREAM-ocean-magenta_exit'].data
light.energy=50;light.diffuse_factor=.18;light.size=1.8

# Original reference has vertically elongated ceramic tiles.
for ob in s.objects:
    if ob.type=='MESH' and ob.data.materials and ob.data.materials[0].name=='MAT-DREAM-ocean-pink_ceramic':
        for poly in ob.data.polygons:
            if abs(poly.normal.z)<.5:
                for li in poly.loop_indices: ob.data.uv_layers.active.data[li].uv.y*=.58

cfg=json.loads((ROOT/'validation/ocean-exit/secondary-camera-fit.json').read_text(encoding='utf8'))['secondary_camera']
primary=s.camera
data=primary.data.copy();data.name='CAM-DREAM-ocean-11.5s'
cam=bpy.data.objects.new(data.name,data);s.collection.objects.link(cam)
cam.location=cfg['position_m'];cam.rotation_mode='QUATERNION'
yaw,pitch=cfg['yaw_rad'],cfg['pitch_rad']
direction=Vector((math.cos(yaw)*math.cos(pitch),math.sin(yaw)*math.cos(pitch),math.sin(pitch)))
cam.rotation_quaternion=direction.to_track_quat('-Z','Y') @ Quaternion((0,0,1),cfg['roll_rad'])
s['ocean_refinement_v2']=True
bpy.context.view_layer.update()
audit={}
for camera in [primary,cam]:
    out=[]
    for p in [(-.85,5.3,2.4),(.85,5.3,2.4),(.85,5.3,0),(-.85,5.3,0)]:
        uv=world_to_camera_view(s,camera,Vector(p));out.append([uv.x*478,(1-uv.y)*850])
    audit[camera.name]=out
(ROOT/'validation/ocean-exit/refined-projection.json').write_text(json.dumps(audit,indent=2)+'\n',encoding='utf8')
bpy.data.libraries.write(str(ROOT/'blender/ocean_exit.blend'),{s},path_remap='RELATIVE_ALL',fake_user=True,compress=True)
print(json.dumps({'objects':len(s.objects),'camera_projection':audit,'saved':'blender/ocean_exit.blend'}))
