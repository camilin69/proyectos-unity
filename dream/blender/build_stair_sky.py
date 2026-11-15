"""Editable gray stair/sky blockout. Execute inside Blender through its MCP.

Owns only *-DREAM-stair-* objects in DREAM_StairSky. Reads stair_sky_plan.json.
Does not save, render, export, bake, change the runtime or claim final fidelity.
The flat world is diagnostic; foreground banks/rails/steps are actual volumes.
"""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
PLAN = json.loads((ROOT / 'blender/stair_sky_plan.json').read_text(encoding='utf-8'))
CONFIG = PLAN['constructor']
STAIR = CONFIG['stair']
FRAME = CONFIG['frame']
BANKS = CONFIG['banks']
RAILS = CONFIG['rails']
LANDING = CONFIG['landing']
CAMERA = CONFIG['camera_seed']
NAV = PLAN['navigation_contract']
NAME = PLAN['scene_name']
TOKEN = '-DREAM-stair-'


def smooth01(value):
    value = max(0.0, min(1.0, value))
    return value * value * (3.0 - 2.0 * value)


def support_height(y, stair):
    """Exact top of the authored horizontal tread, not a visual ramp."""
    local = y - stair['front_y_m']
    if local < 0:
        return stair['base_z_m']
    index = min(stair['count'], int(math.floor(local / stair['tread_m'])) + 1)
    return stair['base_z_m'] + index * stair['riser_m']


def navigation_data(stair, landing, nav):
    half = stair['pink_width_m'] / 2
    surfaces = [{'id': 'approach', 'xyxy_m': [-half, -5.2, half, stair['front_y_m']],
                 'support_z_m': stair['base_z_m']}]
    for index in range(stair['count']):
        y0 = stair['front_y_m'] + index * stair['tread_m']
        surfaces.append({'id': f'tread_{index + 1:02d}',
                         'xyxy_m': [-half, y0, half, y0 + stair['tread_m']],
                         'support_z_m': stair['base_z_m'] + (index + 1) * stair['riser_m']})
    surfaces.append({'id': 'upper_landing',
                     'xyxy_m': [-half, landing['start_y_m'], half, landing['end_y_m']],
                     'support_z_m': landing['top_z_m']})
    clearance = half - nav['agent_radius_m'] - 0.03
    return {'schema_version': 1, 'kind': 'stair_support_surfaces',
            'status': 'authored_support_metadata_requires_export_validation',
            'eye_height_m': nav['eye_height_m'], 'agent_radius_m': nav['agent_radius_m'],
            'max_step_up_m': nav['max_step_up_m'], 'max_step_down_m': nav['max_step_down_m'],
            'center_corridor_xyxy_m': [-clearance, -5.2, clearance, landing['end_y_m'] - 0.2],
            'support_surfaces': surfaces,
            'boundary_convention': 'Use y_min <= y < y_max, taking the following tread at a shared edge.',
            'outside_corridor': 'Blocked until additional traversable terrain is explicitly authored.',
            'top_end': 'Stop before landing edge; onward scene transition is not implemented.',
            'runtime_note': 'SceneSettings supports rectangular height surfaces; finish_stair_sky.py serializes these into the runtime configuration.'}


def bank_geometry(side, stair, bank):
    """Closed grid solid with outward winding. Pure math, independently checkable."""
    nx, ny = bank['x_segments'], bank['y_segments']
    inner = stair['pink_width_m'] / 2 + stair['side_band_width_m'] - 0.025
    vertices = []
    for j in range(ny + 1):
        y = bank['start_y_m'] + (bank['end_y_m'] - bank['start_y_m']) * j / ny
        progress = max(0.0, min(stair['count'], (y - stair['front_y_m']) / stair['tread_m'] + 0.3))
        inner_z = stair['base_z_m'] + progress * stair['riser_m']
        taper = smooth01((y - bank['start_y_m']) / 1.6)
        for i in range(nx + 1):
            t = i / nx
            x = side * (inner + (bank['outer_x_m'] - inner) * t)
            bulge = bank['outer_rise_m'] * (t ** 0.78) * taper
            z = inner_z + bulge * (0.96 + 0.04 * math.sin(y * 1.1))
            vertices.append((x, y, z))
    top_count = len(vertices)
    vertices += [(x, y, bank['bottom_z_m']) for x, y, _ in vertices]
    faces = []
    for j in range(ny):
        for i in range(nx):
            a = j * (nx + 1) + i
            quad = (a, a + 1, a + nx + 2, a + nx + 1)
            faces.append(quad if side > 0 else tuple(reversed(quad)))
    top_faces = list(faces)
    faces += [tuple(index + top_count for index in reversed(face)) for face in top_faces]
    edge = list(range(nx + 1))
    edge += [j * (nx + 1) + nx for j in range(1, ny + 1)]
    edge += [ny * (nx + 1) + i for i in range(nx - 1, -1, -1)]
    edge += [j * (nx + 1) for j in range(ny - 1, 0, -1)]
    if side < 0:
        edge.reverse()
    for a, b in zip(edge, edge[1:] + edge[:1]):
        faces.append((a, a + top_count, b + top_count, b))
    return vertices, faces, len(top_faces)


# Reject invalid dimensions before touching any existing scene objects.
assert STAIR['count'] >= 1 and STAIR['tread_m'] > 0 and STAIR['riser_m'] > 0
assert STAIR['riser_m'] <= NAV['max_step_up_m']
assert STAIR['riser_m'] <= NAV['max_step_down_m']
assert STAIR['pink_width_m'] > NAV['agent_radius_m'] * 2 + 0.06
assert abs(LANDING['start_y_m'] - (STAIR['front_y_m'] + STAIR['count'] * STAIR['tread_m'])) < 1e-6
assert abs(LANDING['top_z_m'] - (STAIR['base_z_m'] + STAIR['count'] * STAIR['riser_m'])) < 1e-6
assert abs(FRAME['opening_bottom_z_m'] - LANDING['top_z_m']) < 1e-6
assert FRAME['opening_top_z_m'] - FRAME['opening_bottom_z_m'] > NAV['eye_height_m'] + 0.2
assert BANKS['outer_x_m'] > STAIR['pink_width_m'] / 2 + STAIR['side_band_width_m']

scene = bpy.data.scenes.get(NAME) or bpy.data.scenes.new(NAME)
for old in list(scene.objects):
    if TOKEN in old.name:
        bpy.data.objects.remove(old, do_unlink=True)
bpy.context.window.scene = scene
scene.unit_settings.system = 'METRIC'
collection_name = 'DREAM_StairSky_Blockout'
collection = bpy.data.collections.get(collection_name) or bpy.data.collections.new(collection_name)
if collection.name not in scene.collection.children:
    scene.collection.children.link(collection)
scene['dream_asset'] = PLAN['asset_id']
scene['dream_stage'] = 'geometry_blockout_unvalidated'
scene['dream_reference'] = CONFIG['primary_reference']
scene['dream_source_plan'] = 'blender/stair_sky_plan.json'
scene['dream_navigation'] = json.dumps(navigation_data(STAIR, LANDING, NAV))
scene['dream_blockout_colors'] = 'Neutral gray values only; no final pink, grass, metallic reflection or sky calibration.'
scene['dream_cloud_policy'] = 'Uniform diagnostic world. No camera-facing cloud cards or reference-image planes.'
scene.render.resolution_x, scene.render.resolution_y = CAMERA['render_px']
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = False
try:
    scene.render.engine = 'BLENDER_EEVEE'
except TypeError:
    scene.render.engine = 'BLENDER_EEVEE_NEXT'
scene.eevee.taa_render_samples = 64
scene.view_settings.view_transform = 'Standard'
scene.view_settings.exposure = 0
scene.view_layers[0].material_override = None
materials = []


def material(label, value, roughness=0.8):
    name = 'DREAM_STAIR_BLOCKOUT_' + label
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    shader = next(node for node in mat.node_tree.nodes if node.type == 'BSDF_PRINCIPLED')
    shader.inputs['Base Color'].default_value = (value, value, value, 1)
    shader.inputs['Roughness'].default_value = roughness
    shader.inputs['Metallic'].default_value = 0
    shader.inputs['Emission Strength'].default_value = 0
    mat['dream_id'] = len(materials)
    mat['kind'] = 0
    mat['roughness'] = roughness
    mat['metallic'] = 0.0
    mat['diagnostic_only'] = True
    materials.append(mat)
    return mat


steps_gray = material('future_pink_fibers', 0.64)
vegetation_gray = material('future_grass', 0.27, 0.95)
surround_gray = material('future_mint_surround', 0.46)
frame_gray = material('future_pink_frame', 0.59)
rail_gray = material('future_metal_rails', 0.72, 0.5)


def own(obj, label, prefix='GEO'):
    obj.name = prefix + TOKEN + label
    if collection not in obj.users_collection:
        collection.objects.link(obj)
    for previous in list(obj.users_collection):
        if previous != collection:
            previous.objects.unlink(obj)
    obj['dream_owner'] = NAME
    return obj


def box(label, center, dimensions, mat, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    obj = own(bpy.context.object, label)
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        modifier = obj.modifiers.new('Gray edge radius', 'BEVEL')
        modifier.width = bevel
        modifier.segments = 2
    return obj


def tube(label, start, end, radius):
    start, end = Vector(start), Vector(end)
    direction = end - start
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=radius, depth=direction.length,
                                       end_fill_type='NGON', location=(start + end) / 2)
    obj = own(bpy.context.object, label)
    obj.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()
    obj.data.materials.append(rail_gray)
    for face in obj.data.polygons:
        face.use_smooth = len(face.vertices) == 4  # Keep end caps flat.
    return obj


def joint(label, point, radius):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=radius, location=point)
    obj = own(bpy.context.object, label)
    obj.data.materials.append(rail_gray)
    for face in obj.data.polygons:
        face.use_smooth = True


half = STAIR['pink_width_m'] / 2
for index in range(STAIR['count']):
    y0 = STAIR['front_y_m'] + index * STAIR['tread_m']
    top = STAIR['base_z_m'] + (index + 1) * STAIR['riser_m']
    bottom = STAIR['base_z_m'] - 0.035
    center_y = y0 + (STAIR['tread_m'] - STAIR['nosing_m']) / 2
    center_z = (bottom + top) / 2
    step = box(f'tread_{index + 1:02d}', (0, center_y, center_z),
               (STAIR['pink_width_m'], STAIR['tread_m'] + STAIR['nosing_m'], top - bottom),
               steps_gray, STAIR['edge_bevel_m'])
    step['support_z_m'] = top
    step['support_y_min_m'] = y0
    step['support_y_max_m'] = y0 + STAIR['tread_m']
    for side, label in [(-1, 'left'), (1, 'right')]:
        x = side * (half + STAIR['side_band_width_m'] / 2)
        box(f'{label}_green_tread_{index + 1:02d}', (x, center_y, center_z),
            (STAIR['side_band_width_m'] + 0.006, STAIR['tread_m'] + STAIR['nosing_m'], top - bottom),
            vegetation_gray, 0.008)

approach = CONFIG['approach']
box('approach_ground', ((approach['x_min_m'] + approach['x_max_m']) / 2,
                       (approach['y_min_m'] + approach['y_max_m']) / 2, -0.08),
    (approach['x_max_m'] - approach['x_min_m'], approach['y_max_m'] - approach['y_min_m'], 0.16),
    vegetation_gray)
box('upper_landing', (0, (LANDING['start_y_m'] + LANDING['end_y_m']) / 2,
                     (LANDING['top_z_m'] - 0.035) / 2),
    (LANDING['width_m'], LANDING['end_y_m'] - LANDING['start_y_m'] + 0.006,
     LANDING['top_z_m'] + 0.035), vegetation_gray, 0.006)

for side, label in [(-1, 'left'), (1, 'right')]:
    vertices, faces, top_faces = bank_geometry(side, STAIR, BANKS)
    mesh = bpy.data.meshes.new('DREAM_STAIR_' + label + '_bank')
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    mesh.materials.append(vegetation_gray)
    uv = mesh.uv_layers.new(name='WorldMetres')
    for face in mesh.polygons:
        face.use_smooth = face.index < top_faces
        for loop in face.loop_indices:
            vertex = vertices[mesh.loops[loop].vertex_index]
            uv.data[loop].uv = (vertex[0], vertex[1])
    obj = bpy.data.objects.new('GEO' + TOKEN + label + '_bank', mesh)
    collection.objects.link(obj)
    obj['dream_owner'] = NAME
    obj['closed_volume'] = True

fy, fw = FRAME['wall_y_m'], FRAME['opening_width_m'] / 2
low, high = FRAME['opening_bottom_z_m'], FRAME['opening_top_z_m']
wall_half = FRAME['wall_width_m'] / 2
for label, a, b in [('left', -wall_half, -fw), ('right', fw, wall_half)]:
    box('surround_' + label, ((a + b) / 2, fy, FRAME['wall_height_m'] / 2),
        (b - a, FRAME['wall_thickness_m'], FRAME['wall_height_m']), surround_gray)
box('surround_above', (0, fy, (high + FRAME['wall_height_m']) / 2),
    (2 * fw, FRAME['wall_thickness_m'], FRAME['wall_height_m'] - high), surround_gray)
box('surround_below', (0, fy, low / 2), (2 * fw, FRAME['wall_thickness_m'], low), surround_gray)
# The previous body front lay on the mint wall plane (Y=3.81), leaving only
# thin mouldings visible. Use one solid profile with front/back wall clearance.
frame_helper_path = ROOT / 'blender/stair_frame.py'
frame_namespace = {'__file__': str(frame_helper_path), '__name__': 'dream_stair_frame_helper'}
exec(compile(frame_helper_path.read_text(encoding='utf-8'), str(frame_helper_path), 'exec'), frame_namespace)
frame_build = frame_namespace['apply_stair_frame'](scene, FRAME, frame_gray)

for side, label in [(-1, 'left'), (1, 'right')]:
    x = side * RAILS['x_offset_m']
    start = (x, RAILS['main_start_y_m'], RAILS['main_start_z_m'])
    end = (x, RAILS['main_end_y_m'], RAILS['main_end_z_m'])
    lower = (x, start[1] - RAILS['lower_extension_m'], start[2])
    upper = (x, end[1] + RAILS['upper_return_m'], end[2] - 0.10)
    tube(label + '_lower_return', lower, start, RAILS['radius_m'])
    tube(label + '_inclined_rail', start, end, RAILS['radius_m'])
    tube(label + '_upper_return', end, upper, RAILS['radius_m'])
    for suffix, point in [('lower', start), ('upper', end)]:
        joint(label + '_' + suffix + '_elbow', point, RAILS['radius_m'] * 1.02)
    for index, y in enumerate(RAILS['post_y_m']):
        fraction = max(0.0, min(1.0, (y - start[1]) / (end[1] - start[1])))
        z = start[2] + fraction * (end[2] - start[2])
        base = support_height(y, STAIR)
        tube(f'{label}_post_{index}', (x, y, base - 0.015), (x, y, z + 0.005), RAILS['post_radius_m'])

world = bpy.data.worlds.get('DREAM_StairSky_Blockout_World') or bpy.data.worlds.new('DREAM_StairSky_Blockout_World')
world.use_nodes = True
background = next(node for node in world.node_tree.nodes if node.type == 'BACKGROUND')
background.inputs['Color'].default_value = (0.22, 0.22, 0.22, 1)
background.inputs['Strength'].default_value = 0.65
scene.world = world


def area(label, position, target, energy, size):
    name = 'DREAM_STAIR_BLOCKOUT_' + label
    data = bpy.data.lights.get(name) or bpy.data.lights.new(name, 'AREA')
    data.energy, data.shape, data.size = energy, 'DISK', size
    obj = bpy.data.objects.new('LGT' + TOKEN + label, data)
    collection.objects.link(obj)
    obj['dream_owner'] = NAME
    obj.location = position
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()


area('broad_shape_key', (-3.5, -0.5, 7.5), (0, 1.6, 1.2), 800, 6)
area('broad_shape_fill', (3.5, -3.5, 4.5), (0, 1.6, 1.3), 220, 5)


def camera(label, config):
    name = 'DREAM_STAIR_BLOCKOUT_' + label
    data = bpy.data.cameras.get(name) or bpy.data.cameras.new(name)
    obj = bpy.data.objects.new('CAM' + TOKEN + label, data)
    collection.objects.link(obj)
    obj['dream_owner'] = NAME
    obj.location = config['position_m']
    yaw, pitch = config['yaw_rad'], config['pitch_rad']
    forward = Vector((math.cos(yaw) * math.cos(pitch), math.sin(yaw) * math.cos(pitch), math.sin(pitch)))
    obj.rotation_euler = forward.to_track_quat('-Z', 'Y').to_euler()
    data.sensor_fit = 'VERTICAL'
    data.sensor_height = 24
    data.lens = data.sensor_height / (2 * config['tan_half_vertical_fov'])
    data.clip_start, data.clip_end = 0.04, 200
    return obj


scene.camera = camera('reference_09s', CAMERA)
camera('left_bank_inspection', CONFIG['secondary_camera_seed'])
bpy.context.view_layer.update()
print(json.dumps({'scene': scene.name, 'asset': scene['dream_asset'],
                  'stage': scene['dream_stage'], 'objects': len(scene.objects),
                  'mesh_objects': sum(obj.type == 'MESH' for obj in scene.objects),
                  'step_count': STAIR['count'], 'total_rise_m': STAIR['count'] * STAIR['riser_m'],
                  'navigation_surfaces': len(navigation_data(STAIR, LANDING, NAV)['support_surfaces']),
                  'runtime_navigation_evidence': 'validation/stair-navigation-validation.json (separate exported-scene test)',
                  'camera_seed': CAMERA, 'saved': False, 'rendered': False, 'exported': False,
                  'material_calibration': False}))
