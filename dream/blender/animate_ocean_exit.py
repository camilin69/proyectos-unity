"""Build separate animated water/post candidate using the live Blender MCP."""
from pathlib import Path
import json,math,hashlib
import bpy
from mathutils import Vector,Quaternion
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'validation/ocean-exit-motion';OUT.mkdir(exist_ok=True)
assert bpy.data.scenes.get('DREAM_OceanExitWater') is None, 'Inspect existing candidate before replacing.'
with bpy.data.libraries.load(str(ROOT/'blender/ocean_exit.blend'),link=False) as (src,dst):
    dst.scenes=['DREAM_OceanExit']
s=dst.scenes[0];s.name='DREAM_OceanExitWater';bpy.context.window.scene=s
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=64;s.cycles.use_denoising=True
for ob in s.objects:
    ob.name=ob.name.replace('DREAM-ocean-','DREAM-oceanwater-').removesuffix('.001')
    if ob.data:ob.data.name=ob.data.name.replace('DREAM-ocean-','DREAM-oceanwater-').removesuffix('.001')
materials={m for ob in s.objects if ob.type=='MESH' for m in ob.data.materials}
for m in materials:m.name=m.name.replace('DREAM-ocean-','DREAM-oceanwater-').removesuffix('.001')
bed=s.objects['GEO-DREAM-oceanwater-bed'].data.materials[0]
next(n for n in bed.node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Base Color'].default_value=(.10,.55,.45,1)
s.objects['LIGHT-DREAM-oceanwater-magenta_exit'].data.energy=30
cfg=json.loads((ROOT/'validation/ocean-exit/submerged-post-fit.json').read_text(encoding='utf8'))
s.frame_start=1;s.frame_end=181;s.render.fps=30
def name(part):return 'GEO-DREAM-oceanwater-'+part
def assign_uv(me,period=4):
    uv=me.uv_layers.active or me.uv_layers.new(name='SurfaceMetres')
    for p in me.polygons:
        axis=max(range(3),key=lambda k:abs(p.normal[k]));axes=[k for k in range(3) if k!=axis]
        for li in p.loop_indices:
            v=me.vertices[me.loops[li].vertex_index].co
            uv.data[li].uv=(v[axes[0]]/period,v[axes[1]]/period)
def replace_mesh(ob,verts,faces):
    old=ob.data;me=bpy.data.meshes.new(old.name+'-motion');me.from_pydata(verts,[],faces);me.update()
    for m in old.materials:me.materials.append(m)
    ob.data=me
    for p in me.polygons:p.use_smooth=True
    assign_uv(me)

# The visible lower endpoint can lie under water; the solid post continues into the bed.
x,y,visible_bottom,h=cfg['post_x_y_bottom_top_m']
points=[(x,y,-.8),(x,y,h-.17),(x-.005,y,h-.09),(x-.03,y,h-.025),(x-.072,y,h)]
verts=[];segments=24;radius=.045
for k,p in enumerate(points):
    tangent=(Vector(points[min(k+1,len(points)-1)])-Vector(points[max(0,k-1)])).normalized()
    a=Vector((0,1,0));b=tangent.cross(a).normalized()
    verts += [tuple(Vector(p)+radius*(a*math.cos(2*math.pi*i/segments)+b*math.sin(2*math.pi*i/segments))) for i in range(segments)]
faces=[tuple(reversed(range(segments)))]
for k in range(len(points)-1):
    faces += [(k*segments+i,k*segments+(i+1)%segments,(k+1)*segments+(i+1)%segments,(k+1)*segments+i) for i in range(segments)]
faces.append(tuple((len(points)-1)*segments+i for i in range(segments)))
replace_mesh(s.objects[name('bent_access_post')],verts,faces)

# More samples near the ocean threshold avoid the old 3 m-wide wave facets.
xs=[-150,-40,-10]+[-8+i*.125 for i in range(129)]+[10,40,150]
ys=[5.3+i*.15 for i in range(132)]+[25.1+(.5*i)**1.65 for i in range(1,81)]
nx=len(xs);ny=len(ys)
verts=[(xx,yy,0) for yy in ys for xx in xs]
faces=[(j*nx+i,j*nx+i+1,(j+1)*nx+i+1,(j+1)*nx+i) for j in range(ny-1) for i in range(nx-1)]
replace_mesh(s.objects[name('ocean')],verts,faces)

for part in ['interior_water','ocean']:
    ob=s.objects[name(part)]
    assert ob.data.shape_keys is None
    for v in ob.data.vertices:v.co.z=0
    ob.shape_key_add(name='Basis')
    for idx,(amp,kx,ky,period) in enumerate([(.028,0,3,6),(.013,3,8,3)]):
        for component in ['sin','cos']:
            key=ob.shape_key_add(name=f'Wave{idx}_{component}');key.slider_min=-1;key.slider_max=1
            for v,target in zip(ob.data.vertices,key.data):
                xx,yy=v.co.x,v.co.y
                phase=kx*xx+ky*yy+.3*math.sin(xx*2)
                fade=1 if part=='interior_water' else min(1,12/max(12,yy-5.3))
                target.co.z=amp*fade*(math.sin(phase) if component=='sin' else math.cos(phase))
            fc=key.driver_add('value');fc.driver.type='SCRIPTED'
            # sin(a-t)=sin(a)*cos(t)-cos(a)*sin(t).
            trig='cos' if component=='sin' else '-sin'
            fc.driver.expression=f'{trig}((frame-1)*{2*math.pi/(30*period):.15f})'
    mat=ob.data.materials[0];nodes=mat.node_tree.nodes;links=mat.node_tree.links
    bsdf=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
    uv=nodes.new('ShaderNodeTexCoord');mapping=nodes.new('ShaderNodeMapping')
    mapping.label='Foam and ripples travel toward the room'
    links.new(uv.outputs['UV'],mapping.inputs['Vector'])
    for n in list(nodes):
        if n.type=='TEX_IMAGE':links.new(mapping.outputs['Vector'],n.inputs['Vector'])
    loc=mapping.inputs['Location']
    for frame,value in [(1,0),(181,.20)]:
        loc.default_value[1]=value;loc.keyframe_insert('default_value',index=1,frame=frame)
    action=mat.node_tree.animation_data.action
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    for point in curve.keyframe_points:point.interpolation='LINEAR'
    if part=='interior_water':
        mat.use_raytrace_refraction=True
        mat.thickness_mode='SLAB'
        mat.refraction_depth=.25
        output=next(n for n in nodes if n.type=='OUTPUT_MATERIAL')
        thickness=nodes.new('ShaderNodeValue');thickness.outputs[0].default_value=.01
        links.new(thickness.outputs[0],output.inputs['Thickness'])
        foam=next(n for n in nodes if n.type=='TEX_IMAGE' and 'foam_mask' in n.image.name)
        mul=nodes.new('ShaderNodeMath');mul.operation='MULTIPLY_ADD';mul.inputs[1].default_value=-.35;mul.inputs[2].default_value=.92
        links.new(foam.outputs['Color'],mul.inputs[0]);links.new(mul.outputs[0],bsdf.inputs['Transmission Weight'])
        ramp=next(n for n in nodes if n.type=='VALTORGB')
        ramp.color_ramp.elements[0].color=(.68,.90,.85,1);ramp.color_ramp.elements[1].color=(.45,.66,.6,1)
        bsdf.inputs['Roughness'].default_value=.14
    next(n for n in nodes if n.type=='BUMP').inputs['Distance'].default_value=.005

camcfg=cfg['cameras'][1]
camdata=s.camera.data.copy();camdata.name='CAM-DREAM-oceanwater-9s'
cam=bpy.data.objects.new(camdata.name,camdata);s.collection.objects.link(cam)
cam.location=camcfg['position_m'];cam.rotation_mode='QUATERNION'
yaw,pitch=camcfg['yaw_rad'],camcfg['pitch_rad']
direction=Vector((math.cos(yaw)*math.cos(pitch),math.sin(yaw)*math.cos(pitch),math.sin(pitch)))
cam.rotation_quaternion=direction.to_track_quat('-Z','Y') @ Quaternion((0,0,1),camcfg['roll_rad'])
s.frame_set(1);bpy.context.view_layer.update()
samples={}
for frame in [1,16,31,91,181]:
    s.frame_set(frame);deps=bpy.context.evaluated_depsgraph_get();row={}
    for part in ['interior_water','ocean']:
        ob=s.objects[name(part)];eo=ob.evaluated_get(deps);me=eo.to_mesh()
        z=[v.co.z for v in me.vertices]
        row[part]={'min_z':min(z),'max_z':max(z),'sample_z':[z[i] for i in [0,len(z)//3,len(z)//2,len(z)-1]],
                   'drivers_valid':all(f.driver.is_valid for f in ob.data.shape_keys.animation_data.drivers)}
        eo.to_mesh_clear()
    samples[str(frame)]=row
s.frame_set(1);s.camera=s.objects['CAM-DREAM-oceanwater-7s']
report={'schema':'dream.ocean_exit_animation_native.v1','scene':s.name,'objects':len(s.objects),
        'source_native_sha256':hashlib.sha256((ROOT/'blender/ocean_exit.blend').read_bytes()).hexdigest(),
        'post_fit':cfg['post_x_y_bottom_top_m'],'post_actual_bottom_m':-.8,
        'waves':'Two analytic travelling harmonics, four shape keys per water mesh; 6-second displacement loop.',
        'foam':'UV advection .1333 m/s toward room; not a fluid simulation or seamless six-second texture loop.',
        'samples':samples,'accepted':False,'runtime_promoted':False,
        'export_limitations':'Shape-key drivers and shader mapping animation require explicit C++ implementation; no GLB/runtime motion equivalence claimed.'}
assert all(d['drivers_valid'] for r in samples.values() for d in r.values())
assert samples['1']['interior_water']['sample_z']!=samples['31']['interior_water']['sample_z']
bpy.data.libraries.write(str(ROOT/'blender/ocean_exit_water.blend'),{s},path_remap='RELATIVE_ALL',fake_user=True,compress=True)
(OUT/'native-animation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
print(json.dumps(report))
