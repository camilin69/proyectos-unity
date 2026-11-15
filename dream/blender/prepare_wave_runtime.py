"""Assign explicit runtime material/UV/light/navigation contracts in Blender.

Run after finish_wave_corridor.apply() and before export_runtime.py. This
prepares a traversable prototype, without granting visual acceptance.
"""
import bpy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
scene = bpy.data.scenes['DREAM_WaveCorridor']
if scene.get('dream_hall_runtime_pending', False):
    raise ValueError('Hall candidate requires its own collision/light configuration before runtime export. Use the verified wave_corridor.blend for the existing runtime.')
bpy.context.window.scene = scene
plan = json.loads((ROOT/'blender/wave_corridor_plan.json').read_text(encoding='utf-8'))
config = plan['constructor']
path = ROOT/'blender/build_wave_corridor.py'
helper = {'__file__':str(path),'__name__':'wave_pure_helpers'}
exec(compile(path.read_text(encoding='utf-8'),str(path),'exec'),helper)
profile,spans = helper['floor_profile'](config)
roles = {'floor':(13,.19,0), 'floor_caps':(0,.5,0), 'wall':(14,.57,0),
         'ceiling':(15,.79,0), 'door_trim':(0,.35,0), 'rail':(0,.27,0),
         'rear_panel':(0,.7,0), 'diffuser':(7,.3,5), 'exit':(16,.35,0),
         'button_red':(7,.35,1)}
materials = {m.name:m for o in scene.objects if o.type=='MESH' and o.name.startswith('GEO-DREAM-wavecorridor-') for m in o.data.materials}
for index,(name,mat) in enumerate(sorted(materials.items())):
    role = name.removeprefix('DREAM_WAVE_LOOK_')
    if role not in roles:
        raise ValueError('Unknown wave material: '+name)
    kind,rough,variant = roles[role]
    mat['dream_id'],mat['kind'],mat['roughness'],mat['metallic'] = index,kind,rough,0.
    mat['albedo_variant'],mat['opacity'] = variant,0.
    mat['runtime_uv_layer'] = 'WaveDecal' if kind==16 else 'WaveMetres'
    mat['runtime_material_mapping_pending'] = False

camera = config['camera_seed']
corridor,hall = config['corridor'],config['destination_hall']
eye_height = camera['position_m'][2]-helper['floor_height'](camera['position_m'][1],config)
lines = ['camera '+' '.join(map(str,[*camera['position_m'],camera['yaw_rad'],camera['pitch_rad']])),
         f"camera_roll {camera['roll_rad']}", f"fov {camera['tan_half_vertical_fov']}",
         'environment 4','far_clip 80','exposure -1.2',f'eye_height {eye_height}',
         'step_limits 0.18 0.18',f"bounds {-hall['half_width_m']+.20} {hall['half_width_m']-.20} {corridor['start_y_m']+.20} {hall['end_y_m']-.22}"]
for y0,y1,z in spans:
    lines.append(f"surface {-corridor['half_width_m']+.20} {y0} {corridor['half_width_m']-.20} {y1} {z}")
lines.append(f"surface {-hall['half_width_m']+.20} {corridor['end_y_m']} {hall['half_width_m']-.20} {hall['end_y_m']-.22} {profile[-1][1]}")
# Doors are reference geometry and remain closed. Corridor supports end at the
# wall clearance; the hall's two columns use their actual footprints + radius.
for x in hall['column_x_m']:
    y,size = hall['column_y_m'],hall['column_size_m']
    lines.append(f'capsule {x} {y-size/2} {x} {y+size/2} {size/2+.20}')
lights = []
for y in config['ceiling_lights']['centres_y_m']+config['ceiling_lights']['hall_centres_y_m']:
    lights.append([0,y,corridor['ceiling_z_m']-.35,12,11.16,10.08,.16,0])
lights += [[0,-.8,corridor['ceiling_z_m']-.3,28,26.04,23.52,.7,1],
           [0,2,.9,4,3.84,3.8,1.75,2]]
for values in lights:
    lines.append('light '+' '.join(map(str,values)))
scene['dream_runtime_config'] = json.dumps(lines)
scene['dream_navigation'] = json.dumps({'kind':'rectangular_stepped_supports','surfaces':len(spans)+1,
    'riser_count':sum(f['riser_count'] for f in config['floor']['flights']),
    'total_descent_m':profile[0][1]-profile[-1][1],'eye_height_m':eye_height,
    'doors':'closed reference objects','hall_columns':'capsule obstacles',
    'runtime_validation':'pending','strict_fidelity_accepted':False})
print(json.dumps({'materials':len(materials),'surfaces':len(spans)+1,'lights':len(lights),'environment':4,'fidelity_accepted':False}))
