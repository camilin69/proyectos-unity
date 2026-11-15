"""Initial GRAY kitchen/meadow blockout; execute inside Blender through MCP.

Owns only DREAM_MeadowKitchen objects prefixed *-DREAM-kitchen-. No texture
generation, export, file save, final materials or reference-fidelity claim.
The blue world is a diagnostic backdrop, not the final reference sky.
Dimensions/camera come from kitchen_plan.json and are inferred fit seeds.
"""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
PLAN = json.loads((ROOT / 'blender/kitchen_plan.json').read_text(encoding='utf-8'))
SEED = PLAN['constructor_data_proposal']['layout_seed']
CAMERA = PLAN['constructor_data_proposal']['camera_seed']
NAME = 'DREAM_MeadowKitchen'
scene = bpy.data.scenes.get(NAME) or bpy.data.scenes.new(NAME)
for obj in list(scene.objects):
    if '-DREAM-kitchen-' in obj.name:
        bpy.data.objects.remove(obj, do_unlink=True)
bpy.context.window.scene = scene
scene.unit_settings.system = 'METRIC'
scene['dream_asset'] = 'kitchen_meadow'
scene['dream_stage'] = 'geometry_blockout_unvalidated'
scene['dream_reference'] = 'referencias/estetica/evidencias/video-42/02s.png'
scene['dream_blockout_background'] = 'Flat diagnostic blue; no old pastel cloud sky or final kitchen sky.'
scene['dream_source_plan'] = 'blender/kitchen_plan.json'
scene['dream_blockout_colors'] = 'Neutral gray part values only; no material/color calibration.'
scene.render.resolution_x, scene.render.resolution_y = CAMERA['primary_render_px']
scene.render.resolution_percentage = 100
try:
    scene.render.engine = 'BLENDER_EEVEE'
except TypeError:
    scene.render.engine = 'BLENDER_EEVEE_NEXT'
scene.eevee.taa_render_samples = 64
scene.render.image_settings.file_format = 'PNG'
scene.view_settings.view_transform = 'Standard'
scene.view_settings.exposure = 0
scene.view_layers[0].material_override = None
materials = []


def material(label, value, emission=0):
    name = 'DREAM_KITCHEN_BLOCKOUT_' + label
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    shader = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    shader.inputs['Base Color'].default_value = (value, value, value, 1)
    shader.inputs['Roughness'].default_value = 0.8
    shader.inputs['Metallic'].default_value = 0
    shader.inputs['Emission Color'].default_value = (1, 1, 1, 1)
    shader.inputs['Emission Strength'].default_value = emission
    mat['diagnostic_only'] = True
    mat['dream_id'] = len(materials)
    mat['roughness'] = 0.8
    mat['metallic'] = 0.0
    mat['kind'] = 7 if emission else 0
    materials.append(mat)
    return mat


gray = material('structure', 0.5)
light = material('appliances', 0.7)
dark = material('dark_parts', 0.12)
ground = material('grass_footprint', 0.36)
paving = material('paving', 0.6)
diffuser = material('ceiling_diffuser', 0.8, 0.5)


def box(label, center, dimensions, mat=gray, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    obj = bpy.context.object
    obj.name = 'GEO-DREAM-kitchen-' + label
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Blockout edge radius', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
    return obj


def cylinder(label, center, radius, depth, mat=dark, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=radius, depth=depth,
                                     location=center, rotation=rotation)
    obj = bpy.context.object
    obj.name = 'GEO-DREAM-kitchen-' + label
    obj.data.materials.append(mat)
    return obj


def polygon(label, vertices, mat):
    mesh = bpy.data.meshes.new('DREAM_KITCHEN_' + label)
    mesh.from_pydata(vertices, [], [tuple(range(len(vertices)))])
    mesh.materials.append(mat)
    obj = bpy.data.objects.new('GEO-DREAM-kitchen-' + label, mesh)
    scene.collection.objects.link(obj)
    return obj


# The original never reveals a full floor plan. These are editable fit seeds,
# with actual open apertures, rather than a reference image painted on a plane.
x0, x1, y0, y1 = SEED['room_bounds_xy_m']
height = SEED['ceiling_z_m']
thick = SEED['wall_thickness_m']
opening = SEED['exterior_opening']
ox0, ox1, oz1 = opening['x_min_m'], opening['x_max_m'], opening['top_z_m']
entry = SEED['foreground_entry']
ey, ex0, ex1, ez1 = entry['wall_y_m'], entry['x_min_m'], entry['x_max_m'], entry['top_z_m']
box('floor_support', ((x0+x1)/2, (y1-3.4)/2, -0.04), (x1-x0, y1+3.4, 0.08), paving)
box('left_wall', (x0-thick/2, (ey+y1)/2, height/2), (thick, y1-ey, height))
box('right_wall', (x1+thick/2, (ey+y1)/2, height/2), (thick, y1-ey, height))
box('ceiling', ((x0+x1)/2, (ey+y1)/2, height+0.04), (x1-x0+2*thick, y1-ey+thick, 0.08))
for label, lo, hi in [('left', x0, ox0), ('right', ox1, x1)]:
    box('exterior_wall_' + label, ((lo+hi)/2, y1, height/2), (hi-lo, thick, height))
box('exterior_header', ((ox0+ox1)/2, y1, (oz1+height)/2), (ox1-ox0, thick, height-oz1))
for label, lo, hi in [('left', x0, ex0), ('right', ex1, x1)]:
    box('entry_wall_' + label, ((lo+hi)/2, ey, height/2), (hi-lo, thick, height))
box('entry_header', ((ex0+ex1)/2, ey, (ez1+height)/2), (ex1-ex0, thick, height-ez1))
for label, x in [('left', ox0), ('right', ox1)]:
    box('exterior_jamb_' + label, (x, y1-0.05, oz1/2), (0.065, 0.17, oz1), light)
box('exterior_lintel', ((ox0+ox1)/2, y1-0.05, oz1+0.025), (ox1-ox0+0.10, 0.17, 0.07), light)
for label, x in [('left', ex0), ('right', ex1)]:
    box('entry_jamb_' + label, (x, ey-0.015, ez1/2), (0.085, 0.19, ez1), light)
# Rotate the open leaf about its real hinge; the far edge must not mask the exit.
leaf_angle = math.radians(entry.get('leaf_open_outward_deg', 30))
leaf_direction = Vector((math.sin(leaf_angle), math.cos(leaf_angle), 0))
leaf_center = Vector((ex1, ey, ez1/2)) + leaf_direction*0.39
leaf = box('entry_leaf', leaf_center, (0.04, 0.78, ez1), light, 0.006)
leaf.rotation_euler.z = -leaf_angle
knob_center = Vector((ex1, ey, entry.get('knob_z_m', 1.04))) + leaf_direction*entry.get('knob_along_leaf_m', 0.69)
cylinder('entry_knob', knob_center, 0.013, 0.04, light, (0, math.pi/2, -leaf_angle))

counter = SEED['left_counter_run']
wall_x, front_x = counter['wall_x_m'], counter['front_x_m']
ry, rw = SEED['range']['center_y_m'], SEED['range']['width_along_y_m']
counter_z = counter['countertop_z_m']
range_z = SEED['range']['height_m']
for label, lo, hi in [('near', counter['y_min_m'], ry-rw/2),
                      ('far', ry+rw/2, counter['y_max_m'])]:
    if hi <= lo:
        continue
    box('base_cabinet_' + label, ((wall_x+front_x)/2, (lo+hi)/2, (counter_z-0.05)/2),
        (front_x-wall_x-0.02, hi-lo, counter_z-0.05), light, 0.005)
    box('counter_' + label, ((wall_x+front_x)/2, (lo+hi)/2, counter_z-0.01),
        (front_x-wall_x+0.035, hi-lo+0.012, 0.045), light, 0.006)
    box('base_front_' + label, (front_x+0.008, (lo+hi)/2, (counter_z-0.2)/2+0.12),
        (0.022, hi-lo-0.03, counter_z-0.2), light, 0.003)
    box('base_toe_' + label, (front_x-0.035, (lo+hi)/2, 0.045),
        (0.025, hi-lo, 0.08), dark)

box('range_body', ((wall_x+front_x)/2, ry, (range_z-0.03)/2), (0.62, rw-0.015, range_z-0.03), light, 0.012)
box('range_top', ((wall_x+front_x)/2, ry, range_z-0.013), (0.63, rw, 0.025), light, 0.005)
for ix, x in enumerate([wall_x+0.16, front_x-0.16]):
    for iy, y in enumerate([ry-rw*0.24, ry+rw*0.24]):
        cylinder(f'hob_{ix}_{iy}', (x, y, range_z+0.005), 0.09, 0.012)
box('range_back_controls', (wall_x+0.036, ry, range_z+0.1), (0.065, rw, 0.21), light, 0.006)
box('oven_door', (front_x+0.008, ry, range_z*0.478), (0.025, rw-0.04, range_z*0.722), light, 0.008)
box('oven_window', (front_x+0.023, ry, range_z*0.70), (0.008, rw*0.54, range_z*0.22), dark, 0.005)
box('oven_handle', (front_x+0.048, ry, range_z-0.12), (0.025, rw*0.8, 0.024), light, 0.005)
box('oven_lower_panel', (front_x+0.025, ry, 0.095), (0.03, rw-0.025, 0.15), light, 0.005)
for i in range(4):
    cylinder(f'oven_control_{i}', (front_x+0.03, ry+(i-1.5)*rw*0.18, range_z-0.055),
             0.018, 0.018, light, (0, math.pi/2, 0))

mw = SEED['microwave']
mw_front = front_x-0.015+mw.get('front_offset_x_m', 0)
mw_z = mw['base_z_m']+mw['height_m']/2
box('microwave', (mw_front-mw['depth_along_x_m']/2, mw['center_y_m'], mw_z),
    (mw['depth_along_x_m'], mw['width_along_y_m'], mw['height_m']), light, 0.009)
box('microwave_window', (mw_front+0.003, mw['center_y_m']-0.04, mw_z),
    (0.008, mw['width_along_y_m']*0.66, mw['height_m']*0.68), dark, 0.005)
box('microwave_controls', (mw_front+0.004, mw['center_y_m']+mw['width_along_y_m']*0.39, mw_z),
    (0.009, 0.044, mw['height_m']*0.77), gray)
upper = SEED['upper_units']
upper_y = ry+upper.get('center_y_offset_m', 0.12)
box('upper_cabinet', (wall_x+upper['depth_m']/2, upper_y, (upper['bottom_z_m']+upper['top_z_m'])/2),
    (upper['depth_m'], upper.get('width_m', 1.3), upper['top_z_m']-upper['bottom_z_m']), light, 0.006)
hood_depth = upper.get('hood_depth_m', 0.45)
hood_width = upper.get('hood_width_m', rw+0.13)
box('hood', (wall_x+hood_depth/2, ry, upper['bottom_z_m']-0.035), (hood_depth, hood_width, 0.08), light, 0.006)
box('hood_lower_lip', (wall_x+hood_depth-0.015, ry, upper['bottom_z_m']-0.06), (0.055, hood_width, 0.035), gray)
box('hood_back_cover', (wall_x+0.08, ry, upper['bottom_z_m']-0.17),
    (0.16, hood_width-.05, 0.26), gray, 0.006)

# This oblique fitted run is inferred from the visible appliance fronts.
# Keep it a single coherent group, including its architectural backing.
box('cabinet_run_backing', (wall_x-0.025, (counter['y_min_m']+counter['y_max_m'])/2, height/2),
    (0.05, counter['y_max_m']-counter['y_min_m'], height), gray)
fit = SEED.get('cabinet_run_transform', {})
angle = math.radians(fit.get('rotation_z_deg', 0))
pivot = Vector((front_x, ry, 0))
offset = Vector((fit.get('offset_x_m', 0), fit.get('offset_y_m', 0), 0))
for part in list(scene.objects):
    label = part.name.removeprefix('GEO-DREAM-kitchen-')
    if label.startswith(('base_', 'counter_', 'range_', 'hob_', 'oven_', 'microwave', 'upper_', 'hood', 'cabinet_run_')):
        p = part.location-pivot
        part.location = pivot+Vector((math.cos(angle)*p.x-math.sin(angle)*p.y,
                                      math.sin(angle)*p.x+math.cos(angle)*p.y, p.z))+offset
        part.rotation_euler.z += angle

# Top-side panel grid: geometric framing only, grayscale radiance for blockout.
panel_x0, panel_x1, panel_y0, panel_y1 = SEED.get('ceiling_panel_bounds_xy_m', [-1.35, 1.25, -1.35, 0.65])
box('ceiling_panel_frame', ((panel_x0+panel_x1)/2, (panel_y0+panel_y1)/2, height-0.035),
    (panel_x1-panel_x0, panel_y1-panel_y0, 0.07), gray)
for i in range(2):
    for j in range(2):
        x = panel_x0+(i+0.5)*(panel_x1-panel_x0)/2
        y = panel_y0+(j+0.5)*(panel_y1-panel_y0)/2
        box(f'ceiling_diffuser_{i}_{j}', (x, y, height-0.078),
            ((panel_x1-panel_x0)/2-0.045, (panel_y1-panel_y0)/2-0.045, 0.015), diffuser)
        bar_offset = (panel_x1-panel_x0)*0.12
        for k, offset in enumerate([-bar_offset, bar_offset]):
            box(f'ceiling_bar_{i}_{j}_{k}', (x+offset, y, height-0.087),
                (0.04, (panel_y1-panel_y0)*0.30, 0.008), diffuser)
grid = SEED.get('ceiling_grid_transform', {})
angle = math.radians(grid.get('rotation_z_deg', 0))
cx,cy=grid.get('pivot_xy_m', [(panel_x0+panel_x1)/2,(panel_y0+panel_y1)/2])
for part in list(scene.objects):
    label=part.name.removeprefix('GEO-DREAM-kitchen-')
    if label.startswith(('ceiling_panel_', 'ceiling_diffuser_', 'ceiling_bar_')):
        dx,dy=part.location.x-cx,part.location.y-cy
        part.location.x=cx+math.cos(angle)*dx-math.sin(angle)*dy
        part.location.y=cy+math.sin(angle)*dx+math.cos(angle)*dy
        part.rotation_euler.z+=angle

# One continuous footprint through the real opening; detail/grass blades wait
# for the geometry gate. All coordinates are world-space, not camera painted.
left_edge = []
boundary = SEED['grass'].get('boundary_xy_m')
for i in range(25):
    y = -3.4+(y1+3.4)*i/24
    if boundary:
        a,b=next(((a,b) for a,b in zip(boundary,boundary[1:]) if a[1] <= y <= b[1]), (boundary[-2],boundary[-1]))
        t=max(0,min(1,(y-a[1])/(b[1]-a[1])))
        x=a[0]+t*(b[0]-a[0])+0.013*math.sin(y*9)
    else:
        x = front_x+0.31+0.065*math.sin(y*3.7)+0.032*math.sin(y*7.4+0.6)
    left_edge.append((x, y, 0.006))
scene['dream_grass_boundary']=json.dumps(left_edge)
polygon('grass_interior_blockout', [left_edge[0], (x1, -3.4, 0.006),
        (x1, y1, 0.006), *reversed(left_edge[1:])], ground)
extent = SEED['grass']['exterior_extent_initial_m']
polygon('meadow_blockout', [(-extent, y1, 0.006), (extent, y1, 0.006),
        (extent, extent, 0.006), (-extent, extent, 0.006)], ground)

world = bpy.data.worlds.get('DREAM_KitchenBlockoutWorld') or bpy.data.worlds.new('DREAM_KitchenBlockoutWorld')
world.use_nodes = True
bg = next(n for n in world.node_tree.nodes if n.type == 'BACKGROUND')
bg.inputs['Color'].default_value = (0.19, 0.32, 0.47, 1)
bg.inputs['Strength'].default_value = 0.65
scene.world = world


def area(label, location, target, energy, size):
    data = bpy.data.lights.new('DREAM_KITCHEN_BLOCKOUT_' + label, 'AREA')
    data.energy = energy
    data.shape = 'DISK'
    data.size = size
    obj = bpy.data.objects.new('LGT-DREAM-kitchen-' + label, data)
    scene.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat('-Z', 'Y').to_euler()


area('exterior_fill', (0.6, 5, 4), (0, -0.2, 0.8), 650, 5)
area('ceiling_fill', (-0.2, -0.2, height-0.12), (-0.2, -0.2, 0), 100, 2.2)
camera = bpy.data.cameras.new('DREAM_KITCHEN_BLOCKOUT_Camera')
obj = bpy.data.objects.new('CAM-DREAM-kitchen-reference', camera)
scene.collection.objects.link(obj)
scene.camera = obj
obj.location = CAMERA['position_m']
yaw, pitch = CAMERA['yaw_rad'], CAMERA['pitch_rad']
forward = Vector((math.cos(yaw)*math.cos(pitch), math.sin(yaw)*math.cos(pitch), math.sin(pitch)))
obj.rotation_euler = forward.to_track_quat('-Z', 'Y').to_euler()
camera.sensor_fit = 'VERTICAL'
camera.sensor_height = 24
camera.lens = camera.sensor_height/(2*CAMERA['tan_half_vertical_fov'])
camera.clip_start = 0.05
camera.clip_end = 1000
bpy.context.view_layer.update()
print(json.dumps({'scene': scene.name, 'stage': scene['dream_stage'],
                  'mesh_objects': sum(o.type == 'MESH' for o in scene.objects),
                  'reference': scene['dream_reference'],
                  'camera_seed': CAMERA, 'material_calibration': False,
                  'note': 'Inspect gray shapes before any final look/material work.'}))
