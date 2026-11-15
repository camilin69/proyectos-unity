"""Opt-in kitchen material/grass helpers; no scene changes on import.

Root calls apply_kitchen_materials(scene) only after the geometry gate. bpy is
imported inside mutating functions; generate_grass_batches is pure Python.
Runtime contract: kind 11, variant 0=ground normal / 1=geometric blade normal;
floorSurface=kitchen_grass_albedo, floorFlow=kitchen_grass_normal. No kind-1
floor reflection or kind-5 tropical-leaf deformation is used.
"""
from pathlib import Path
import json
import math
import random

ROOT = Path(__file__).resolve().parents[1]
SCENE_NAME = 'DREAM_MeadowKitchen'
PREFIX = 'GEO-DREAM-kitchen-'
GRASS_PERIOD_M = 4.0
GRASS_NORMAL_STRENGTH = 0.24

# Recorded before this candidate; the associated render is kitchen-blender.png
# SHA256 3041377641ca643ee2cc5ad15df7ee9ce089916e929bb01bfd9e6449e652a149.
# Keep these values available for a parameter rollback / controlled comparison.
BASELINE_V2 = {
    'source_sha256': 'e5b7a75703ed9ed2798b684f9c308f010cfe5bee87da6080c62c18fd0a8b76b5',
    'grass': {'near_radius': 3.8, 'far_radius': 10.0, 'near_density': 180.0,
              'far_density': 8.0, 'cell_size': .06, 'blades_per_tuft': 6,
              'height_m': [.03, .07], 'width_m': [.008, .018],
              'lean_height_ratio': .45, 'abrupt_density_boundary_m': 3.8},
    'emission': {'light_bar': 1.2, 'diffuser': .65, 'grass_blades': .12},
}

# Artistic base-color seeds, not measured albedos recovered from the video.
BASELINE_MATERIALS_V2 = {
    'wall': ('D3A2A2', .82, 0, 0, 0),
    'appliance': ('DCDFCC', .40, 0, 0, 0),
    'cabinet': ('DAD7C7', .60, 0, 0, 0),
    'trim': ('D4CFB9', .62, 0, 0, 0),
    'paving': ('D2BEAC', .76, 0, 0, 0),
    'ceiling_frame': ('ADA98C', .78, 0, 0, 0),
    'hob': ('30372C', .65, 0, 0, 0),
    'toe': ('777563', .80, 0, 0, 0),
    'microwave_window': ('426647', .28, 0, 0, 0),
    'oven_window': ('8BA488', .29, 0, 0, 0),
    'diffuser': ('EFAFCB', .75, 0, 7, 0),
    'light_bar': ('FFE5F0', .75, 0, 7, 0),
    'grass_ground': ('FFFFFF', .90, 0, 11, 0),
    'grass_blades': ('FFFFFF', .90, 0, 11, 1),
}

# A restrained warm palette and broader rough highlights reduce blue sky
# reflection on the enamel. Lighting remains the principal calibration lever.
# No image pixels, scene-specific texture maps or runtime shader kinds change.
MATERIALS = {
    **BASELINE_MATERIALS_V2,
    'wall': ('D3A29B', .82, 0, 0, 0),
    'appliance': ('DCDFCC', .58, 0, 0, 0),
    'cabinet': ('DAD7C7', .72, 0, 0, 0),
    'trim': ('D4CFB9', .76, 0, 0, 0),
    'ceiling_frame': ('B5B08C', .82, 0, 0, 0),
    'diffuser': ('F0B4BC', .85, 0, 7, 0),
}
EMISSION_STRENGTH = {'light_bar': 1.0, 'diffuser': .72, 'grass_blades': .10}

GRASS_SETTINGS = {'near_radius': 4.5, 'far_radius': 12.0,
                  'near_density': 260.0, 'far_density': 32.0,
                  'cell_size': .05, 'blades_per_tuft': 8}


def grass_density(distance, near_radius, far_radius, near_density, far_density):
    """Continuous density across batch boundaries, with a soft distance tail."""
    def smoothstep(a, b, x):
        t = max(0.0, min(1.0, (x-a)/(b-a)))
        return t*t*(3-2*t)
    transition = smoothstep(near_radius*.68, far_radius*.72, distance)
    fade = 1-smoothstep(far_radius*.78, far_radius, distance)
    return (near_density*(1-transition)+far_density*transition)*fade


def role_for_label(label):
    """Explicit parts first, then known family labels. Unknowns stay unchanged."""
    if label.startswith('grass_blades_'):
        return 'grass_blades'
    if label.startswith(('grass_interior', 'meadow_blockout')):
        return 'grass_ground'
    if label == 'floor_support':
        return 'paving'
    if label.startswith('ceiling_diffuser_'):
        return 'diffuser'
    if label.startswith('ceiling_bar_'):
        return 'light_bar'
    if label in ('ceiling', 'ceiling_panel_frame'):
        return 'ceiling_frame'
    if label.startswith('hob_'):
        return 'hob'
    if label.startswith('base_toe_'):
        return 'toe'
    if label == 'microwave_window':
        return 'microwave_window'
    if label == 'oven_window':
        return 'oven_window'
    if label.startswith(('range_', 'oven_', 'microwave', 'hood')):
        return 'appliance'
    if label.startswith(('base_', 'counter_', 'upper_')):
        return 'cabinet'
    if label.startswith(('entry_jamb_', 'exterior_jamb_', 'exterior_lintel', 'entry_leaf', 'entry_knob')):
        return 'trim'
    if label.startswith(('left_wall', 'right_wall', 'exterior_wall_', 'entry_wall_',
                         'exterior_header', 'entry_header', 'cabinet_run_backing')):
        return 'wall'
    return None


def srgb_to_linear(value):
    return value/12.92 if value <= .04045 else ((value+.055)/1.055)**2.4


def _set_input(node, name, value):
    for socket in node.inputs:
        if socket.name == name:
            socket.default_value = value
            return
    raise KeyError(name)


def _image(bpy, name, non_color=False):
    path = ROOT/'assets/textures'/f'{name}.png'
    image = bpy.data.images.load(str(path), check_existing=True)
    if image.packed_file:
        image.unpack(method='REMOVE')
    image.reload()
    image.colorspace_settings.name = 'Non-Color' if non_color else 'sRGB'
    return image


def _world_uv(obj):
    """Identical coordinates for ground/field/blades, independent of camera."""
    mesh = obj.data
    uv = mesh.uv_layers.get('KitchenWorldXY') or mesh.uv_layers.new(name='KitchenWorldXY')
    mesh.uv_layers.active = uv
    for polygon in mesh.polygons:
        for li in polygon.loop_indices:
            point = obj.matrix_world @ mesh.vertices[mesh.loops[li].vertex_index].co
            uv.data[li].uv = (point.x/GRASS_PERIOD_M, point.y/GRASS_PERIOD_M)
    mesh.update()


def _build_material(bpy, role, index):
    color_hex, roughness, metallic, kind, variant = MATERIALS[role]
    srgb = [int(color_hex[i:i+2], 16)/255 for i in (0, 2, 4)]
    linear = [srgb_to_linear(c) for c in srgb]
    name = 'DREAM_KITCHEN_MAT_' + role
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_backface_culling = False
    mat.node_tree.nodes.clear()
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    shader = nodes.new('ShaderNodeBsdfPrincipled')
    output = nodes.new('ShaderNodeOutputMaterial')
    links.new(shader.outputs['BSDF'], output.inputs['Surface'])
    _set_input(shader, 'Base Color', (*linear, 1))
    _set_input(shader, 'Roughness', roughness)
    _set_input(shader, 'Metallic', metallic)
    if kind == 7:
        _set_input(shader, 'Emission Color', (*linear, 1))
        _set_input(shader, 'Emission Strength', EMISSION_STRENGTH[role])
    if kind == 11:
        image = nodes.new('ShaderNodeTexImage')
        image.image = _image(bpy, 'kitchen_grass_albedo')
        image.extension = 'REPEAT'
        image.interpolation = 'Linear'
        links.new(image.outputs['Color'], shader.inputs['Base Color'])
        if variant == 1:
            # A small diffuse return represents light scattered through leaves;
            # direct lighting still supplies most of the blade's appearance.
            links.new(image.outputs['Color'], shader.inputs['Emission Color'])
            _set_input(shader, 'Emission Strength', EMISSION_STRENGTH[role])
        if variant == 0:
            texture = nodes.new('ShaderNodeTexImage')
            texture.image = _image(bpy, 'kitchen_grass_normal', True)
            texture.extension = 'REPEAT'
            normal = nodes.new('ShaderNodeNormalMap')
            normal.space = 'TANGENT'
            normal.inputs['Strength'].default_value = GRASS_NORMAL_STRENGTH
            links.new(texture.outputs['Color'], normal.inputs['Color'])
            links.new(normal.outputs['Normal'], shader.inputs['Normal'])
    mat['dream_id'] = index
    mat['base_srgb'] = srgb
    mat['roughness'] = roughness
    mat['metallic'] = metallic
    mat['kind'] = kind
    mat['albedo_variant'] = variant
    mat['dream_profile'] = 'kitchen'
    mat['dream_material_role'] = role
    mat['dream_normal_strength'] = GRASS_NORMAL_STRENGTH if kind == 11 and variant == 0 else 0
    return mat


def apply_kitchen_materials(scene=None, install_world=True):
    """Explicit root call after geometry approval; never called at import time.

    Changes only kitchen object materials/UVs and the kitchen's own world.
    Does not change lights, camera, geometry, other scenes, save or export.
    """
    import bpy
    scene = scene or bpy.data.scenes.get(SCENE_NAME)
    if scene is None or scene.name != SCENE_NAME:
        raise ValueError('Expected the existing DREAM_MeadowKitchen scene')
    mats = {role:_build_material(bpy, role, index) for index, role in enumerate(MATERIALS)}
    assigned, unknown = {}, []
    for obj in scene.objects:
        if obj.type != 'MESH' or not obj.name.startswith(PREFIX):
            continue
        role = role_for_label(obj.name.removeprefix(PREFIX))
        if role is None:
            unknown.append(obj.name)
            continue
        obj.data.materials.clear()
        obj.data.materials.append(mats[role])
        if role.startswith('grass_'):
            _world_uv(obj)
        assigned[obj.name] = role
    if install_world:
        world = bpy.data.worlds.get('DREAM_KitchenWorld') or bpy.data.worlds.new('DREAM_KitchenWorld')
        world.use_nodes = True
        nodes, links = world.node_tree.nodes, world.node_tree.links
        nodes.clear()
        background = nodes.new('ShaderNodeBackground')
        background.inputs['Strength'].default_value = 1.0
        output = nodes.new('ShaderNodeOutputWorld')
        environment = nodes.new('ShaderNodeTexEnvironment')
        environment.image = _image(bpy, 'kitchen_sky')
        environment.texture_mapping.scale = (1, -1, 1)
        links.new(environment.outputs['Color'], background.inputs['Color'])
        links.new(background.outputs[0], output.inputs['Surface'])
        scene.world = world
    scene['dream_material_profile'] = 'kitchen'
    scene['dream_material_status'] = 'candidate_requires_render_validation'
    return {'assigned':assigned, 'unknown_labels_left_unchanged':unknown,
            'world_installed':install_world, 'runtime_environment':2,
            'runtime_slots':{'floorSurface':'kitchen_grass_albedo.bmp',
                             'floorFlow':'kitchen_grass_normal.bmp', 'sky':'kitchen_sky.bmp'}}


def generate_grass_batches(boundary_xyz, right_x, origin_xy, seed=42061,
                           near_radius=4.5, far_radius=12.0,
                           near_density=260.0, far_density=32.0, cell_size=.05,
                           blades_per_tuft=8):
    """Pure, deterministic short turf over the exact authored boundary.

    boundary_xyz is scene['dream_grass_boundary'], increasing Y. No curve is
    refit or randomized. Interior is to its right; beyond its last Y is meadow.
    The two static batches share a continuous density function: no visible
    population step at their split. Short curved fans overlap into clumps;
    roots are spread within each tuft instead of forming repeated V spikes.
    No alpha cards, particles, camera-space effects or Blender-only modifiers.
    Ground maps continue beyond far_radius. This is not dynamic runtime LOD.
    """
    boundary = [tuple(map(float, p)) for p in boundary_xyz]
    values = [right_x, *origin_xy, near_radius, far_radius,
              near_density, far_density, cell_size, *[v for p in boundary for v in p]]
    if any(not math.isfinite(v) for v in values):
        raise ValueError('Grass inputs must be finite')
    if len(boundary) < 2 or any(b[1] <= a[1] for a,b in zip(boundary,boundary[1:])):
        raise ValueError('Grass boundary must have at least two points with increasing Y')
    if (not 0 < near_radius < far_radius or min(near_density, far_density) < 0
            or cell_size <= 0 or any(p[0] >= right_x for p in boundary)
            or not isinstance(blades_per_tuft, int) or not 1 <= blades_per_tuft <= 16):
        raise ValueError('Invalid grass density/radius')
    if max(near_density, far_density)*cell_size**2 > 1:
        raise ValueError('Cell grid cannot represent requested density')
    result = {name:{'vertices':[], 'faces':[], 'uvs':[], 'tufts':0, 'bases':[], 'blades':0}
              for name in ('near', 'mid')}

    def terrain(x, y):
        if y < boundary[0][1]:
            return None
        if y > boundary[-1][1]:
            return boundary[-1][2]
        for a,b in zip(boundary,boundary[1:]):
            if a[1] <= y <= b[1]:
                t = (y-a[1])/(b[1]-a[1])
                left = a[0]*(1-t)+b[0]*t
                # Validate each blade vertex, not just its root. This preserves
                # the fitted paving boundary without a wide bare perimeter.
                if x < left+.001 or x > right_x-.001:
                    return None
                return a[2]*(1-t)+b[2]*t
        return None

    ox, oy = origin_xy
    for iy in range(math.floor((oy-far_radius)/cell_size), math.ceil((oy+far_radius)/cell_size)+1):
        for ix in range(math.floor((ox-far_radius)/cell_size), math.ceil((ox+far_radius)/cell_size)+1):
            rng = random.Random((seed ^ (ix*73856093) ^ (iy*19349663)) & 0xffffffff)
            x = (ix+rng.random())*cell_size
            y = (iy+rng.random())*cell_size
            distance = math.hypot(x-ox, y-oy)
            if distance > far_radius:
                continue
            zone = 'near' if distance <= near_radius else 'mid'
            density = grass_density(distance, near_radius, far_radius,
                                    near_density, far_density)
            if rng.random() >= density*cell_size**2:
                continue
            z = terrain(x, y)
            if z is None:
                continue
            batch = result[zone]
            first_blade = batch['blades']
            tuft_height = rng.uniform(.021, .043)
            for _ in range(blades_per_tuft):
                angle = rng.uniform(0, math.tau)
                side = (math.cos(angle), math.sin(angle))
                blade_height = tuft_height*rng.uniform(.72, 1.13)
                width = rng.uniform(.010, .020)
                # Positive cross(side, lean).z keeps the geometric upper face
                # upward; a broad bent tip catches light instead of a black spike.
                lean_angle = angle+rng.uniform(.95, 2.15)
                reach = rng.uniform(.024, .052)
                lean = (math.cos(lean_angle)*reach, math.sin(lean_angle)*reach)
                root_angle = rng.uniform(0, math.tau)
                root_radius = .023*math.sqrt(rng.random())
                bx, by = x+math.cos(root_angle)*root_radius, y+math.sin(root_angle)*root_radius
                points = [(bx-side[0]*width/2, by-side[1]*width/2, 0),
                          (bx+side[0]*width/2, by+side[1]*width/2, 0),
                          (bx+lean[0]*.50-side[0]*width*.32, by+lean[1]*.50-side[1]*width*.32, blade_height*.90),
                          (bx+lean[0]*.50+side[0]*width*.32, by+lean[1]*.50+side[1]*width*.32, blade_height*.90),
                          (bx+lean[0], by+lean[1], blade_height*.76)]
                ground = [terrain(p[0], p[1]) for p in points]
                if any(value is None for value in ground):
                    continue
                points = [(p[0], p[1], base+p[2]) for p,base in zip(points,ground)]
                start = len(batch['vertices'])
                batch['vertices'].extend(points)
                batch['uvs'].extend((p[0]/GRASS_PERIOD_M, p[1]/GRASS_PERIOD_M) for p in points)
                batch['faces'].extend(tuple(start+i for i in face) for face in [(0,1,3),(0,3,2),(2,3,4)])
                batch['blades'] += 1
            if batch['blades'] > first_blade:
                batch['tufts'] += 1
                batch['bases'].append((x,y,z))
    return {'batches':result, 'topology':{
        'seed':seed, 'exact_boundary_xyz':boundary, 'right_x':right_x,
        'lod_origin_xy':list(origin_xy), 'near_radius_m':near_radius, 'far_radius_m':far_radius,
        'near_density_tufts_m2':near_density, 'mid_density_tufts_m2':far_density,
        'density_transition_m':[near_radius*.68,far_radius*.72],
        'density_fade_m':[far_radius*.78,far_radius],
        'boundary_clearance_m':.001, 'boundary_check':'All five vertices of every blade',
        'blades_per_tuft_max':blades_per_tuft, 'triangles_per_blade':3,
        'tuft_height_m':[.021,.043], 'blade_width_m':[.010,.020],
        'blade_reach_m':[.024,.052], 'root_spread_radius_m':.023,
        'blades':sum(b['blades'] for b in result.values()),
        'triangles':sum(len(b['faces']) for b in result.values()),
        'vertices':sum(len(b['vertices']) for b in result.values()),
        'objects':sum(bool(b['faces']) for b in result.values()),
        'runtime_lod':'Two static authoring-distance batches; no dynamic renderer LOD implemented.'}}


def add_grass_detail(scene=None, seed=42061):
    """Root opt-in after boundary approval; creates two opaque batched meshes.

    Call this first, then apply_kitchen_materials so new blade meshes receive
    the variant-1 material. No export/save or camera/light changes are made.
    """
    import bpy
    scene = scene or bpy.data.scenes.get(SCENE_NAME)
    if scene is None or scene.name != SCENE_NAME:
        raise ValueError('Expected DREAM_MeadowKitchen')
    raw = scene.get('dream_grass_boundary')
    if raw is None:
        raise ValueError('Builder must publish dream_grass_boundary before adding detail')
    boundary = json.loads(raw) if isinstance(raw, str) else list(raw)
    source = next((o for o in scene.objects if o.name == PREFIX+'grass_interior_blockout'), None)
    if source is None:
        raise ValueError('Missing authored interior grass surface')
    right_x = max((source.matrix_world @ v.co).x for v in source.data.vertices)
    origin = tuple(scene.camera.location[:2])
    data = generate_grass_batches(boundary, right_x, origin, seed=seed, **GRASS_SETTINGS)
    for name, batch in data['batches'].items():
        label = PREFIX+'grass_blades_'+name
        old = bpy.data.objects.get(label)
        if old is not None and old.name in scene.objects:
            old_mesh = old.data
            bpy.data.objects.remove(old, do_unlink=True)
            if old_mesh.users == 0:
                bpy.data.meshes.remove(old_mesh)
        if not batch['faces']:
            continue
        mesh = bpy.data.meshes.new('DREAM_KITCHEN_grass_blades_'+name)
        mesh.from_pydata(batch['vertices'], [], batch['faces'])
        uv = mesh.uv_layers.new(name='KitchenWorldXY')
        for polygon in mesh.polygons:
            polygon.use_smooth = False
            for li in polygon.loop_indices:
                uv.data[li].uv = batch['uvs'][mesh.loops[li].vertex_index]
        obj = bpy.data.objects.new(label, mesh)
        scene.collection.objects.link(obj)
        mesh.update()
    scene['dream_grass_detail_topology'] = json.dumps(data['topology'])
    return data['topology']
