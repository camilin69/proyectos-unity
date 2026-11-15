"""Apply the kitchen's next look candidate to its already fitted geometry.

Execute inside Blender after inspecting the gray comparison. Keeps this stage
separate from build_kitchen.py so geometry can still be checked without color.
Does not render, export or save; the caller inspects each resulting artifact.
"""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector

# Baseline tied to kitchen-blender.png SHA256 3041377641ca643ee2cc5ad15df7ee9ce
# 089916e929bb01bfd9e6449e652a149 and this script's previous SHA256
# 34cd126c9af4e4a555ac553ac80d85b45806c33226d8dc176b5b2ac1b32e23fe.
# Kept as data, not applied automatically. The original capture/ROI report
# remains the source of measured results; this candidate has not been rendered.
BASELINE_LIGHTING_V2 = {
    'exterior_fill': {'energy': 120, 'color': [1., .97, .85], 'size': 5.0},
    'ceiling_fill': {'energy': 55, 'color': [1., .72, .66], 'size': 2.2},
    'daylight': {'energy': 1.8, 'color': [.94, 1., .88], 'angle': .6},
    'exposure': 0,
}
LIGHTING = {
    'exterior_fill': {'energy': 90, 'color': [1., .96, .82], 'size': 5.0},
    'ceiling_fill': {'energy': 65, 'color': [1., .67, .48], 'size': 2.8},
    'daylight': {'energy': 1.8, 'color': [1., .99, .84], 'angle': .6},
    # Soft upward return fills the dark soffit/pink wall. Keeping it below the
    # ceiling and aiming upward avoids bleaching the already bright grass.
    'warm_return': {'energy': 48, 'color': [1., .63, .39], 'size': 2.4,
                    'position': [.45, -.65, 1.20], 'target': [-.2, .50, 2.55]},
    'exposure': 0,
}

ROOT = Path(__file__).resolve().parents[1]
scene = bpy.data.scenes['DREAM_MeadowKitchen']
bpy.context.window.scene = scene
plan = json.loads((ROOT/'blender/kitchen_plan.json').read_text(encoding='utf-8'))
seed = plan['constructor_data_proposal']['layout_seed']
camera = plan['constructor_data_proposal']['camera_seed']
helper_path = ROOT/'blender/kitchen_materials.py'
helper = {'__file__':str(helper_path), '__name__':'kitchen_materials'}
exec(compile(helper_path.read_text(encoding='utf-8'),str(helper_path),'exec'),helper)
grass = helper['add_grass_detail'](scene)
materials = helper['apply_kitchen_materials'](scene)
if materials['unknown_labels_left_unchanged']:
    raise ValueError(materials['unknown_labels_left_unchanged'])

# Light position/size is authored in world space and remains consistent when
# walking. Runtime environment 2 must be compared independently after export;
# these Blender lights do not automatically become OpenGL light sources.
exterior = bpy.data.objects['LGT-DREAM-kitchen-exterior_fill'].data
ceiling = bpy.data.objects['LGT-DREAM-kitchen-ceiling_fill'].data
for light, settings in [(exterior, LIGHTING['exterior_fill']),
                        (ceiling, LIGHTING['ceiling_fill'])]:
    light.energy = settings['energy']
    light.color = settings['color']
    light.size = settings['size']
sun_name='LGT-DREAM-kitchen-daylight'
sun_obj=bpy.data.objects.get(sun_name)
if sun_obj is None:
    sun_data=bpy.data.lights.new('DREAM_KitchenDaylight','SUN')
    sun_obj=bpy.data.objects.new(sun_name,sun_data)
    scene.collection.objects.link(sun_obj)
sun_obj.data.energy=LIGHTING['daylight']['energy']
sun_obj.data.angle=LIGHTING['daylight']['angle']
sun_obj.data.color=LIGHTING['daylight']['color']
sun_obj.rotation_euler=Vector((-2,-4,-6)).to_track_quat('-Z','Y').to_euler()

fill_name = 'LGT-DREAM-kitchen-warm_return'
fill = bpy.data.objects.get(fill_name)
if fill is None:
    fill = bpy.data.objects.new(fill_name, bpy.data.lights.new('DREAM_KitchenWarmReturn', 'AREA'))
    scene.collection.objects.link(fill)
settings = LIGHTING['warm_return']
fill.data.shape = 'DISK'
fill.data.energy, fill.data.size = settings['energy'], settings['size']
fill.data.color = settings['color']
fill.location = settings['position']
fill.rotation_euler = (Vector(settings['target'])-fill.location).to_track_quat('-Z', 'Y').to_euler()

# The broad wall return should not bleach the cabinet fronts. Receiver sets
# keep this authored diffuse fill on its intended surfaces; all scene geometry
# still blocks the sunlight. This approximates missing indirect bounce.
for collection_name, emitter, roles in [
    ('DREAM_Kitchen_WallReturn_Receivers', fill, {'wall','ceiling_frame','trim'}),
    ('DREAM_Kitchen_Daylight_Receivers', sun_obj, {'grass_ground','grass_blades','paving'}),
]:
    receivers=bpy.data.collections.get(collection_name) or bpy.data.collections.new(collection_name)
    for old in list(receivers.objects): receivers.objects.unlink(old)
    for obj in scene.objects:
        if obj.type=='MESH' and obj.name.startswith('GEO-DREAM-kitchen-'):
            if helper['role_for_label'](obj.name.removeprefix('GEO-DREAM-kitchen-')) in roles:
                receivers.objects.link(obj)
    emitter.light_linking.receiver_collection=receivers
scene['dream_light_linking_policy']='Wall bounce targets walls/ceiling/trim; sunlight targets grass/paving; ordinary area lights remain shared. Material identity unchanged.'
scene.view_settings.exposure = LIGHTING['exposure']
scene['dream_look_baseline_v2'] = json.dumps({'lighting':BASELINE_LIGHTING_V2,
    'material_settings':helper['BASELINE_MATERIALS_V2'], 'grass':helper['BASELINE_V2']})
scene['dream_look_candidate'] = json.dumps({'status':'requires_render_comparison',
    'lighting':LIGHTING, 'grass_settings':helper['GRASS_SETTINGS'],
    'reference':'referencias/estetica/evidencias/video-42/02s.png',
    'runtime_lighting':'Independent environment-2 implementation; not exported by this helper.'})
scene['dream_stage'] = 'material_prototype_requires_visual_comparison'

# Explicit traversable surfaces prevent walking around the shell into the
# unmodelled area below the floor. Camera Z is support + eye height.
floor_z = 0.006
eye_height = camera['position_m'][2]-floor_z
config = ['camera '+' '.join(map(str,[*camera['position_m'],camera['yaw_rad'],camera['pitch_rad']])),
          f"fov {camera['tan_half_vertical_fov']}", 'environment 2', 'far_clip 1000',
          'exposure 0', 'reflection 0.006', 'bounds -16 16 -3.2 20',
          f'eye_height {eye_height}', 'step_limits 0.22 0.22',
          'surface -1.65 -3.4 1.85 1.8 0.006',
          'surface -16 1.8 16 20 0.006']
capsules = []

def capsule(a,b,radius):
    values = [a[0],a[1],b[0],b[1],radius]
    config.append('capsule '+' '.join(map(str,values)))
    capsules.append(values)

for obj in scene.objects:
    if obj.type!='MESH' or not obj.name.startswith('GEO-DREAM-kitchen-'):
        continue
    label=obj.name.removeprefix('GEO-DREAM-kitchen-')
    if label in ('left_wall','right_wall') or label.startswith(('exterior_wall_','entry_wall_')):
        axis=0 if obj.dimensions.x>obj.dimensions.y else 1
        a=obj.location.copy();b=obj.location.copy()
        a[axis]-=obj.dimensions[axis]/2;b[axis]+=obj.dimensions[axis]/2
        capsule(a,b,min(obj.dimensions.x,obj.dimensions.y)/2+.16)

entry=seed['foreground_entry'];angle=math.radians(entry['leaf_open_outward_deg'])
hinge=(entry['x_max_m'],entry['wall_y_m'])
capsule(hinge,(hinge[0]+math.sin(angle)*.78,hinge[1]+math.cos(angle)*.78),.18)
counter=seed['left_counter_run'];ry=seed['range']['center_y_m']
fit=seed['cabinet_run_transform'];angle=math.radians(fit['rotation_z_deg'])
pivot=Vector((counter['front_x_m'],ry))
def fitted(x,y):
    p=Vector((x,y))-pivot
    return (pivot.x+math.cos(angle)*p.x-math.sin(angle)*p.y+fit['offset_x_m'],
            pivot.y+math.sin(angle)*p.x+math.cos(angle)*p.y+fit['offset_y_m'])
front=[fitted(counter['front_x_m']+.04,y) for y in (counter['y_min_m'],counter['y_max_m'])]
capsule(*front,.19)
for y in (counter['y_min_m'],counter['y_max_m']):
    capsule(fitted(counter['wall_x_m'],y),fitted(counter['front_x_m'],y),.18)
scene['dream_runtime_config']=json.dumps(config)
scene['dream_navigation']=json.dumps({'kind':'ground_support_with_capsules',
    'eye_height_m':eye_height,'capsules':capsules,'surface_count':2,
    'runtime_validation':'pending actual walk/collision checks'})
scene['dream_material_apply_report']=json.dumps({'grass':grass,'materials':materials})
scene.render.resolution_x,scene.render.resolution_y=camera['primary_render_px']
scene.render.resolution_percentage=100
scene.eevee.taa_render_samples=128
scene.render.filepath=str(ROOT/'validation/kitchen-blender.png')
print(json.dumps({'scene':scene.name,'stage':scene['dream_stage'],
                  'objects':len(scene.objects),'grass':grass,'material_count':14,
                  'navigation_lines':len(config),'exported':False}))
