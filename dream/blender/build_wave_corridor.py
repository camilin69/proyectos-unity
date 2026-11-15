"""Gray, editable source-based wave-corridor seed; not a validated replica.

Only build_scene() imports bpy and mutates Blender. Importing this file under a
module name permits pure mesh/navigation checks with ordinary Python. Execute
build_scene() through Blender MCP; never use a standalone bpy installation.
No save, render, export, runtime change or borrowed image surface is performed.
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / 'blender/wave_corridor_plan.json'
TOKEN = '-DREAM-wavecorridor-'


def load_plan():
    return json.loads(PLAN_PATH.read_text(encoding='utf-8'))


def floor_profile(config):
    """Return a monotone-Y stepped top boundary and exact flat support spans."""
    corridor, floor = config['corridor'], config['floor']
    y, z = corridor['start_y_m'], floor['base_z_m']
    points = [(y, z)]
    spans = []

    def horizontal(end):
        nonlocal y
        if end < y - 1e-9:
            raise ValueError('Descending flights overlap in Y')
        if end > y + 1e-9:
            spans.append((y, end, z))
            if len(points) > 1 and abs(points[-2][1] - z) < 1e-9:
                points[-1] = (end, z)  # merge collinear top edges, not risers
            else:
                points.append((end, z))
            y = end

    for flight in floor['flights']:
        if flight['riser_count'] < 1 or flight['riser_m'] <= 0 or flight['tread_m'] <= 0:
            raise ValueError('Invalid stair flight dimensions')
        horizontal(flight['start_y_m'])
        for i in range(flight['riser_count']):
            z -= flight['riser_m']
            points.append((y, z))
            horizontal(flight['start_y_m'] + (i + 1) * flight['tread_m'])
    horizontal(corridor['end_y_m'])
    return points, spans


def floor_height(y, config):
    """Lower tread wins exactly at a descending riser; shape query only."""
    z = config['floor']['base_z_m']
    for flight in config['floor']['flights']:
        if y < flight['start_y_m']:
            break
        index = min(flight['riser_count'], int(math.floor(
            (y - flight['start_y_m']) / flight['tread_m'] + 1e-9)) + 1)
        z -= index * flight['riser_m']
    return z


def rail_height(y, config):
    """Rail follows the broad grade of each flight, not individual stair teeth."""
    z = config['floor']['base_z_m']
    for flight in config['floor']['flights']:
        length = flight['riser_count'] * flight['tread_m']
        fraction = max(0.0, min(1.0, (y - flight['start_y_m']) / length))
        z -= fraction * flight['riser_count'] * flight['riser_m']
    return z + config['rails']['height_above_floor_m']


def door_openings(config):
    """Rectangular openings with optional explicit, uncertain sill elevations.

    An occluded door sill must not force the visible corridor into a flat
    landing. Explicit thresholds permit a closed opening above a descending
    section; the surrounding wall below it remains a real solid. This is a
    geometry hypothesis requiring a render, not proof of source architecture.
    Legacy plans without thresholds retain their flat-floor safety check.
    """
    doors, corridor = config['doors'], config['corridor']
    centres = doors['centres_y_m']
    thresholds = doors.get('thresholds_z_m')
    if thresholds is not None and len(thresholds) != len(centres):
        raise ValueError('Explicit threshold count must match door count')
    values = list(centres) + [doors['width_m'], doors['height_m'], doors['leaf_base_clearance_m']]
    if thresholds is not None:
        values += thresholds
    if not all(math.isfinite(v) for v in values) or min(doors['width_m'], doors['height_m']) <= 0:
        raise ValueError('Door dimensions/coordinates must be finite and positive')
    result, previous_end = [], corridor['start_y_m']
    for i, y in enumerate(centres):
        y0, y1 = y - doors['width_m'] / 2, y + doors['width_m'] / 2
        if y0 < previous_end or y1 > corridor.get('left_wall_end_y_m', corridor.get('wall_end_y_m', corridor['end_y_m'])):
            raise ValueError('Door intervals overlap or leave the corridor wall')
        if thresholds is None:
            if abs(floor_height(y0, config) - floor_height(y1, config)) > 1e-8:
                raise ValueError('A door across a flight needs an explicit inferred threshold')
            threshold = floor_height(y, config)
        else:
            threshold = thresholds[i]
        head = threshold + doors['height_m'] + doors['leaf_base_clearance_m']
        if threshold <= corridor['solid_bottom_z_m'] or head >= corridor['ceiling_z_m']:
            raise ValueError('Door opening leaves the solid wall envelope')
        result.append({'centre_y_m': y, 'y0_m': y0, 'y1_m': y1,
                       'threshold_z_m': threshold, 'head_z_m': head})
        previous_end = y1
    return result


def cross2(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def triangulate_polygon(points):
    """Ear-clip one simple Y/Z section; retain its input winding."""
    area = sum(a[0] * b[1] - b[0] * a[1]
               for a, b in zip(points, points[1:] + points[:1]))
    if abs(area) < 1e-10:
        raise ValueError('Degenerate profile polygon')
    indices = list(range(len(points)))
    if area < 0:
        indices.reverse()
    triangles = []
    while len(indices) > 3:
        found = False
        for k, b in enumerate(indices):
            a, c = indices[k - 1], indices[(k + 1) % len(indices)]
            if cross2(points[a], points[b], points[c]) <= 1e-12:
                continue
            inside = False
            for p in indices:
                if p in (a, b, c):
                    continue
                if (cross2(points[a], points[b], points[p]) >= -1e-12 and
                    cross2(points[b], points[c], points[p]) >= -1e-12 and
                    cross2(points[c], points[a], points[p]) >= -1e-12):
                    inside = True
                    break
            if inside:
                continue
            triangles.append((a, b, c))
            indices.pop(k)
            found = True
            break
        if not found:
            raise ValueError('Profile is not a simple nondegenerate polygon')
    triangles.append(tuple(indices))
    return [tuple(reversed(t)) for t in triangles] if area < 0 else triangles


def floor_geometry(config):
    """Closed extruded section. Treads and risers are real faces, not a map."""
    top, spans = floor_profile(config)
    half = config['corridor']['half_width_m']
    bottom = config['corridor']['solid_bottom_z_m']
    if half <= 0 or bottom >= min(z for _, z in top):
        raise ValueError('Floor needs positive width and solid thickness')
    section = top + [(top[-1][0], bottom), (top[0][0], bottom)]
    n = len(section)
    vertices = [(x, y, z) for x in (-half, half) for y, z in section]
    faces, uv_faces = [], []
    arc = [0.0]
    for a, b in zip(section, section[1:]):
        arc.append(arc[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, i + n, j + n, j))
        end_arc = arc[j] if j else arc[-1] + math.dist(section[-1], section[0])
        uv_faces.append([(-half, arc[i]), (half, arc[i]), (half, end_arc), (-half, end_arc)])
    for triangle in triangulate_polygon(section):
        faces.append(triangle)
        uv_faces.append([section[i] for i in triangle])
        right = tuple(i + n for i in reversed(triangle))
        faces.append(right)
        uv_faces.append([section[i - n] for i in right])
    return {'vertices': vertices, 'faces': faces, 'uv_faces': uv_faces,
            'top_profile_yz': top, 'support_spans_y0_y1_z': spans,
            'smooth_faces': [], 'kind': 'closed_stepped_solid'}


def rail_path(side, config):
    rail, corridor = config['rails'], config['corridor']
    start = corridor['start_y_m'] + .10
    end = rail.get('end_y_by_side_m', {}).get(str(side), rail.get('end_y_m', corridor['end_y_m'] - .10))
    count = int(math.ceil((end - start) / rail['sample_spacing_m']))
    values = [start + (end - start) * i / count for i in range(count + 1)]
    for flight in config['floor']['flights']:
        values += [flight['start_y_m'], flight['start_y_m'] + flight['riser_count'] * flight['tread_m']]
    values = sorted(set(round(y, 9) for y in values if start <= y <= end))
    x = side * (corridor['half_width_m'] - rail['offset_from_wall_m'])
    return [(x, y, rail_height(y, config)) for y in values]


def sweep_tube(points, radius, sides=12):
    """Closed constant-X tube sweep; pure geometry, with metre-based loop UVs."""
    if len(points) < 2 or radius <= 0 or sides < 3:
        raise ValueError('Invalid tube')
    vertices, arc = [], [0.0]
    for a, b in zip(points, points[1:]):
        arc.append(arc[-1] + math.dist(a, b))
    for i, p in enumerate(points):
        before, after = points[max(0, i - 1)], points[min(len(points) - 1, i + 1)]
        dy, dz = after[1] - before[1], after[2] - before[2]
        length = math.hypot(dy, dz)
        if length <= 1e-10:
            raise ValueError('Repeated/invalid rail control point')
        ty, tz = dy / length, dz / length
        for k in range(sides):
            angle = 2 * math.pi * k / sides
            # U axis +X; V axis tangent cross +X. Cross(U,V) = tangent.
            vertices.append((p[0] + radius * math.cos(angle),
                             p[1] + radius * tz * math.sin(angle),
                             p[2] - radius * ty * math.sin(angle)))
    faces, uv_faces = [], []
    for i in range(len(points) - 1):
        for k in range(sides):
            j = (k + 1) % sides
            faces.append((i * sides + k, i * sides + j, (i + 1) * sides + j, (i + 1) * sides + k))
            u0, u1 = 2 * math.pi * radius * k / sides, 2 * math.pi * radius * (k + 1) / sides
            uv_faces.append([(u0, arc[i]), (u1, arc[i]), (u1, arc[i + 1]), (u0, arc[i + 1])])
    smooth_faces = list(range(len(faces)))
    for end in (0, len(points) - 1):
        centre = len(vertices)
        vertices.append(tuple(points[end]))
        for k in range(sides):
            j = (k + 1) % sides
            triangle = (centre, end * sides + j, end * sides + k) if end == 0 else (centre, end * sides + k, end * sides + j)
            faces.append(triangle)
            uv_faces.append([(vertices[v][0], vertices[v][2]) for v in triangle])
    return {'vertices': vertices, 'faces': faces, 'uv_faces': uv_faces,
            'smooth_faces': smooth_faces, 'kind': 'closed_rail_sweep'}


def navigation_proposal(config, nav):
    """Authored candidates only. No runtime file/profile is emitted."""
    _, spans = floor_profile(config)
    width = config['corridor']['half_width_m']
    surfaces = [{'id': f'flat_{i:02d}', 'xyxy_m': [-width, y0, width, y1], 'support_z_m': z}
                for i, (y0, y1, z) in enumerate(spans)]
    hall = config['destination_hall']
    surfaces.append({'id': 'destination_hall',
                     'xyxy_m': [-hall['half_width_m'], config['corridor']['end_y_m'], hall['half_width_m'], hall['end_y_m']],
                     'support_z_m': spans[-1][2]})
    wall_end = config['corridor'].get('wall_end_y_m', config['corridor']['end_y_m'])
    if wall_end < config['corridor']['end_y_m']:
        for side in (-1, 1):
            x0, x1 = sorted((side * width, side * hall['half_width_m']))
            surfaces.append({'id': f'hall_entrance_wing_{side}',
                             'xyxy_m': [x0, wall_end, x1, config['corridor']['end_y_m']],
                             'support_z_m': spans[-1][2]})
    return {'schema_version': 1, 'kind': 'candidate_step_support_partition',
            'status': 'geometry_unvalidated_not_exported', 'requires_shape_confirmation': True,
            'eye_height_m': nav['eye_height_m'], 'max_step_up_m': nav['max_step_up_m'],
            'max_step_down_m': nav['max_step_down_m'],
            'center_corridor_xyxy_m': [-nav['x_center_limit_m'], nav['start_y_limit_m'], nav['x_center_limit_m'], nav['end_y_limit_m']],
            'support_surfaces': surfaces,
            'continuous_ramps_supported': False,
            'continuous_ramp_note': nav['continuous_ramp_state']}


def build_scene(plan_override=None):
    """Run this function inside Blender only; preserves other DREAM scenes."""
    import bpy
    from mathutils import Quaternion, Vector

    plan = load_plan() if plan_override is None else plan_override
    config, nav = plan['constructor'], plan['navigation_proposal']
    TOKEN = config.get('ownership_token', '-DREAM-wavecorridor-')
    corridor, doors, hall = config['corridor'], config['doors'], config['destination_hall']
    left_wall_end = corridor.get('left_wall_end_y_m', corridor.get('wall_end_y_m', corridor['end_y_m']))
    right_wall_end = corridor.get('right_wall_end_y_m', corridor.get('wall_end_y_m', corridor['end_y_m']))
    wall_end = min(left_wall_end, right_wall_end)
    if not all(corridor['start_y_m'] < end <= corridor['end_y_m'] for end in [left_wall_end, right_wall_end]):
        raise ValueError('Wall end must lie within the corridor floor extent')
    if wall_end < corridor['end_y_m'] and hall['half_width_m'] <= corridor['half_width_m']:
        raise ValueError('An open terminal flight needs a wider destination hall')
    geometry = floor_geometry(config)  # validate before mutating Blender
    rail_geometry = [sweep_tube(rail_path(side, config), config['rails']['radius_m'], config['rails']['tube_sides']) for side in (-1, 1)]
    openings = door_openings(config)
    scene = bpy.data.scenes.get(plan['scene_name']) or bpy.data.scenes.new(plan['scene_name'])
    for obj in list(scene.objects):
        if TOKEN in obj.name:
            bpy.data.objects.remove(obj, do_unlink=True)
    collection_name = plan.get('collection_name', 'DREAM_WaveCorridor_Blockout')
    collection = bpy.data.collections.get(collection_name) or bpy.data.collections.new(collection_name)
    if collection.name not in scene.collection.children:
        scene.collection.children.link(collection)
    if bpy.context.window:
        bpy.context.window.scene = scene
    scene.unit_settings.system = 'METRIC'
    scene['dream_asset'] = plan['asset_id']
    scene['dream_stage'] = 'gray_geometry_unvalidated'
    scene['dream_reference'] = 'video-42 original @14s; archived13s as secondary'
    scene['dream_source_plan'] = 'blender/wave_corridor_plan.json'
    scene['dream_navigation'] = json.dumps(navigation_proposal(config, nav))
    scene['dream_no_reference_texture'] = True
    scene['dream_destination_ambiguity'] = 'Hall aperture prototype; mirror/window interpretation unresolved.'
    materials = []

    def gray(label, value, rough=.8):
        name = 'DREAM_WAVECORRIDOR_BLOCKOUT_' + label
        mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
        mat.use_nodes = True
        shader = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
        shader.inputs['Base Color'].default_value = (value, value, value, 1)
        shader.inputs['Roughness'].default_value = rough
        shader.inputs['Metallic'].default_value = 0
        shader.inputs['Emission Strength'].default_value = 0
        mat['dream_id'], mat['kind'] = len(materials), 0
        mat['roughness'], mat['metallic'], mat['diagnostic_only'] = rough, 0.0, True
        materials.append(mat)
        return mat

    floor_mat, wall_mat = gray('floor', .43), gray('wall', .54)
    ceiling_mat, door_mat = gray('ceiling', .34), gray('door', .67)
    trim_mat, rail_mat = gray('trim', .72), gray('rail', .12)
    lamp_mat, rear_mat = gray('diffuser', .85), gray('rear_panel', .20)

    def own(obj, label, prefix='GEO'):
        obj.name = prefix + TOKEN + label
        if collection not in obj.users_collection:
            collection.objects.link(obj)
        for previous in list(obj.users_collection):
            if previous != collection:
                previous.objects.unlink(obj)
        obj['dream_owner'] = plan['scene_name']
        return obj

    def box(label, centre, dimensions, mat, bevel=0):
        if min(dimensions) <= 0:
            raise ValueError('Nonpositive box: ' + label)
        bpy.ops.mesh.primitive_cube_add(size=1, location=centre)
        obj = own(bpy.context.object, label)
        obj.dimensions = dimensions
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        obj.data.materials.append(mat)
        if bevel:
            modifier = obj.modifiers.new('Diagnostic edge radius', 'BEVEL')
            modifier.width, modifier.segments = bevel, 2
        return obj

    def mesh_object(label, data, mat):
        mesh = bpy.data.meshes.new('MESH' + TOKEN + label)
        mesh.from_pydata(data['vertices'], [], data['faces'])
        mesh.update()
        obj = bpy.data.objects.new('GEO' + TOKEN + label, mesh)
        collection.objects.link(obj)
        own(obj, label)
        mesh.materials.append(mat)
        uv = mesh.uv_layers.new(name='ContinuousMetres')
        smooth = set(data['smooth_faces'])
        for polygon, coordinates in zip(mesh.polygons, data['uv_faces']):
            polygon.use_smooth = polygon.index in smooth
            for index, value in zip(polygon.loop_indices, coordinates):
                uv.data[index].uv = value
        return obj

    def sphere(label, centre, scale, mat):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=config['ceiling_lights']['segments'], ring_count=10, radius=1, location=centre)
        obj = own(bpy.context.object, label)
        obj.scale = scale
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        obj.data.materials.append(mat)
        for polygon in obj.data.polygons:
            polygon.use_smooth = True
        return obj

    def cylinder_between(label, a, b, radius, mat):
        a, b = Vector(a), Vector(b)
        direction = b - a
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=radius, depth=direction.length,
                                           end_fill_type='NGON', location=(a + b) / 2)
        obj = own(bpy.context.object, label)
        obj.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()
        obj.data.materials.append(mat)
        for polygon in obj.data.polygons:
            polygon.use_smooth = len(polygon.vertices) == 4
        return obj

    mesh_object('continuous_stepped_floor', geometry, floor_mat)
    bottom, ceiling = corridor['solid_bottom_z_m'], corridor['ceiling_z_m']
    wall_x = corridor['half_width_m'] + corridor['wall_thickness_m'] / 2

    def wall_piece(side, y0, y1, z0, z1, label):
        if y1 - y0 > 1e-8 and z1 - z0 > 1e-8:
            return box(label, (side * wall_x, (y0 + y1) / 2, (z0 + z1) / 2),
                       (corridor['wall_thickness_m'], y1 - y0, z1 - z0), wall_mat)

    wall_piece(1, corridor['start_y_m'], right_wall_end, bottom, ceiling, 'right_wall')
    cursor = corridor['start_y_m']
    for i, opening in enumerate(openings):
        y, y0, y1 = opening['centre_y_m'], opening['y0_m'], opening['y1_m']
        threshold, head = opening['threshold_z_m'], opening['head_z_m']
        wall_piece(-1, cursor, y0, bottom, ceiling, f'left_wall_before_door_{i}')
        wall_piece(-1, y0, y1, bottom, threshold, f'left_wall_below_door_{i}')
        wall_piece(-1, y0, y1, head, ceiling, f'left_wall_above_door_{i}')
        recess_x = -corridor['half_width_m'] - doors['recess_m']
        box(f'door_{i}_leaf', (recess_x, y, (threshold + doors['leaf_base_clearance_m'] + head) / 2),
            (doors['leaf_thickness_m'], doors['width_m'] - .018, doors['height_m']), door_mat, .004)
        frame_x = -corridor['half_width_m'] - doors['recess_m'] / 2 + doors['frame_projection_m']
        fw = doors['frame_width_m']
        depth = doors['recess_m'] + doors['frame_projection_m'] * 2
        for end, label in ((y0, 'near'), (y1, 'far')):
            box(f'door_{i}_{label}_reveal', (frame_x, end, (threshold + head) / 2),
                (depth, fw, head - threshold + fw), trim_mat, doors['frame_bevel_m'])
        box(f'door_{i}_head_reveal', (frame_x, y, head),
            (depth, doors['width_m'] + fw, fw), trim_mat, doors['frame_bevel_m'])
        sphere(f'door_{i}_round_fitting', (recess_x + .03, y + .24, threshold + 1.0), (.018, .035, .035), rail_mat)
        cursor = y1
    wall_piece(-1, cursor, left_wall_end, bottom, ceiling, 'left_wall_after_doors')
    box('ceiling', (0, (corridor['start_y_m'] + wall_end) / 2,
                    ceiling + corridor['ceiling_thickness_m'] / 2),
        (corridor['half_width_m'] * 2 + .36, wall_end - corridor['start_y_m'],
         corridor['ceiling_thickness_m']), ceiling_mat)

    for side, data in zip((-1, 1), rail_geometry):
        mesh_object(f'handrail_{side}', data, rail_mat)
        y = corridor['start_y_m'] + .30
        side_wall_end = left_wall_end if side < 0 else right_wall_end
        while config['rails'].get('wall_brackets', True) and y < side_wall_end - .15:
            z = rail_height(y, config) - .015
            cylinder_between(f'rail_bracket_{side}_{y:.2f}',
                             (side * corridor['half_width_m'], y, z),
                             (side * (corridor['half_width_m'] - config['rails']['offset_from_wall_m']), y, z),
                             config['rails']['bracket_radius_m'], rail_mat)
            y += config['rails']['bracket_spacing_m']

    low = geometry['top_profile_yz'][-1][1]
    hall_y0, hall_y1 = wall_end, hall['end_y_m']
    floor_end = corridor['end_y_m']
    box('hall_floor', (0, (floor_end + hall_y1) / 2, (low + bottom) / 2),
        (hall['half_width_m'] * 2, hall_y1 - floor_end, low - bottom), floor_mat)
    if hall_y0 < floor_end:
        for side in (-1, 1):
            box(f'hall_entrance_wing_{side}',
                (side * (hall['half_width_m'] + corridor['half_width_m']) / 2,
                 (hall_y0 + floor_end) / 2, (low + bottom) / 2),
                (hall['half_width_m'] - corridor['half_width_m'], floor_end - hall_y0, low - bottom), floor_mat)
    for side in (-1, 1):
        box(f'hall_side_{side}', (side * (hall['half_width_m'] + .09), (hall_y0 + hall_y1) / 2, (bottom + ceiling) / 2),
            (.18, hall_y1 - hall_y0, ceiling - bottom), wall_mat)
    box('hall_ceiling', (0, (hall_y0 + hall_y1) / 2, ceiling + .08),
        (hall['half_width_m'] * 2 + .36, hall_y1 - hall_y0, .16), ceiling_mat)
    box('hall_back_wall', (0, hall_y1 + .09, (bottom + ceiling) / 2),
        (hall['half_width_m'] * 2 + .36, .18, ceiling - bottom), wall_mat)
    for i, x in enumerate(hall['column_x_m']):
        box(f'hall_column_{i}', (x, hall['column_y_m'], (low + ceiling) / 2),
            (hall['column_size_m'], hall['column_size_m'], ceiling - low), trim_mat)
    panel_half = hall['half_width_m'] - hall['back_panel_margin_m']
    panel_z0, panel_z1 = low + .18, ceiling - .18
    box('hall_unresolved_rear_panel', (0, hall_y1 - .02, (panel_z0 + panel_z1) / 2),
        (panel_half * 2, .025, panel_z1 - panel_z0), rear_mat)
    for i in range(hall['back_grid_columns'] + 1):
        x = -panel_half + 2 * panel_half * i / hall['back_grid_columns']
        box(f'hall_rear_mullion_{i}', (x, hall_y1 - .038, (panel_z0 + panel_z1) / 2),
            (.025, .020, panel_z1 - panel_z0), trim_mat)
    for i in range(1, hall['back_grid_rows']):
        z = panel_z0 + (panel_z1 - panel_z0) * i / hall['back_grid_rows']
        box(f'hall_rear_transom_{i}', (0, hall_y1 - .038, z), (panel_half * 2, .020, .025), trim_mat)

    lamp = config['ceiling_lights']
    for i, y in enumerate(lamp['centres_y_m'] + lamp.get('hall_centres_y_m', [12.4, 15.1])):
        body_z = ceiling - lamp.get('mount_drop_m', lamp['body_depth_m'] / 2)
        sphere(f'ceiling_fixture_{i}', (0, y, body_z),
               (lamp['body_radius_m'], lamp['body_radius_m'], lamp['body_depth_m']), lamp_mat)
        sphere(f'ceiling_fixture_base_{i}', (0, y, ceiling - lamp['base_depth_m'] / 2),
               (lamp['base_radius_m'], lamp['base_radius_m'], lamp['base_depth_m'] / 2), trim_mat)
        body_top, base_bottom = body_z + lamp['body_depth_m'], ceiling - lamp['base_depth_m']
        if body_top < base_bottom:
            cylinder_between(f'ceiling_fixture_stem_{i}', (0, y, body_top - .008),
                             (0, y, base_bottom + .008), min(.018, lamp['base_radius_m'] * .3), trim_mat)
        data = bpy.data.lights.new('DATA' + TOKEN + f'gray_light_{i}', 'AREA')
        data.energy, data.shape, data.size = config['diagnostic_render'].get('light_energy_w', 100), 'DISK', 1.4
        obj = bpy.data.objects.new('LGT' + TOKEN + f'gray_light_{i}', data)
        collection.objects.link(obj)
        light_z = min(ceiling - .18, body_z - lamp['body_depth_m'] - .025) if 'mount_drop_m' in lamp else ceiling - .18
        obj.location = (0, y, light_z)
        own(obj, f'gray_light_{i}', 'LGT')

    def camera(label, seed):
        data = bpy.data.cameras.new('DATA' + TOKEN + label)
        obj = bpy.data.objects.new('CAM' + TOKEN + label, data)
        collection.objects.link(obj)
        own(obj, label, 'CAM')
        obj.location = seed['position_m']
        yaw, pitch = seed['yaw_rad'], seed['pitch_rad']
        direction = Vector((math.cos(yaw) * math.cos(pitch), math.sin(yaw) * math.cos(pitch), math.sin(pitch)))
        obj.rotation_mode = 'QUATERNION'
        obj.rotation_quaternion = direction.to_track_quat('-Z', 'Y') @ Quaternion((0, 0, 1), seed['roll_rad'])
        width, height = config['camera_seed']['render_px']
        data.sensor_fit, data.sensor_width = 'HORIZONTAL', 36
        data.lens = 36 / (2 * seed['tan_half_vertical_fov'] * width / height)
        data.clip_start, data.clip_end = .03, 80
        return obj

    scene.camera = camera('reference14s_seed', config['camera_seed'])
    camera('secondary_inspection', config['secondary_camera_seed'])
    world_name = 'WORLD'+TOKEN+'gray'
    world = bpy.data.worlds.get(world_name) or bpy.data.worlds.new(world_name)
    world.use_nodes = True
    world.node_tree.nodes.clear()
    background = world.node_tree.nodes.new('ShaderNodeBackground')
    background.inputs['Color'].default_value = (.22, .22, .22, 1)
    background.inputs['Strength'].default_value = .45
    output = world.node_tree.nodes.new('ShaderNodeOutputWorld')
    world.node_tree.links.new(background.outputs['Background'], output.inputs['Surface'])
    scene.world = world
    scene.render.engine = 'BLENDER_EEVEE'
    scene.eevee.taa_render_samples = config['diagnostic_render']['samples']
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.exposure = config['diagnostic_render'].get('exposure', 0)
    scene.view_layers[0].material_override = None
    scene.render.film_transparent = False
    scene.render.resolution_x, scene.render.resolution_y = config['camera_seed']['render_px']
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    print(json.dumps({'scene': scene.name, 'stage': scene['dream_stage'],
                      'owned_objects': sum(TOKEN in obj.name for obj in scene.objects),
                      'floor_vertices': len(geometry['vertices']), 'rail_runs': 2,
                      'door_count': len(doors['centres_y_m']),
                      'saved': False, 'rendered': False, 'exported': False}))
    return scene


if __name__ == '__main__':
    build_scene()
