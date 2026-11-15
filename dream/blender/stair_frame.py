"""Solid stair opening frame: pure mesh generation plus an isolated live patch.

Only the live patch helpers import bpy. They replace named frame pieces and
subdivide the unchanged upper mint box in DREAM_StairSky; cameras, stairs,
banks, detail grass, lights and navigation stay untouched. No save, render,
export or material-node modification is performed.
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKEN = '-DREAM-stair-'


def box_grid_geometry(bounds_min, bounds_max, spacing=.24):
    """Closed axis-aligned box with shared grid vertices and unchanged extent.

    Subdivision bounds interpolation of corner-baked AO to small cells. It
    changes tessellation only: all points remain on the six original planes.
    """
    low, high = tuple(bounds_min), tuple(bounds_max)
    if len(low) != 3 or len(high) != 3 or not math.isfinite(spacing) or spacing <= 0:
        raise ValueError('Expected finite box bounds and positive grid spacing')
    if not all(math.isfinite(a) and math.isfinite(b) and a < b for a, b in zip(low, high)):
        raise ValueError('Expected a box with positive finite dimensions')
    counts = [max(1, int(math.ceil((b - a) / spacing))) for a, b in zip(low, high)]
    coordinates = [[a + (b - a) * i / count for i in range(count + 1)]
                   for a, b, count in zip(low, high, counts)]
    vertices, faces, normals, indices = [], [], [], {}

    def vertex(grid_index):
        key = tuple(grid_index)
        if key not in indices:
            indices[key] = len(vertices)
            vertices.append(tuple(coordinates[axis][key[axis]] for axis in range(3)))
        return indices[key]

    # Each (u,v) pair has cross(u,v)=positive fixed axis.
    for axis, (u, v) in enumerate(((1, 2), (2, 0), (0, 1))):
        for side in (0, 1):
            for j in range(counts[v]):
                for i in range(counts[u]):
                    face = []
                    for du, dv in ((0, 0), (1, 0), (1, 1), (0, 1)):
                        point = [0, 0, 0]
                        point[axis], point[u], point[v] = side * counts[axis], i + du, j + dv
                        face.append(vertex(point))
                    faces.append(tuple(face if side else reversed(face)))
                    n = [0, 0, 0]
                    n[axis] = 1 if side else -1
                    normals.append(tuple(n))
    return {'vertices': vertices, 'faces': faces, 'face_normals': normals,
            'bounds_min': low, 'bounds_max': high, 'grid_counts_xyz': counts,
            'maximum_spacing_m': max((b - a) / c for a, b, c in zip(low, high, counts))}


def refine_upper_surround(scene, spacing=.24):
    """Replace only the upper mint box's mesh; preserve object and material.

    No AO exemption is introduced. Reapplying an identical grid is a no-op.
    Cameras, world, lights, frame, navigation and all other geometry are left
    untouched. All six faces retain flat normals and dominant-axis metric UVs.
    """
    import bpy
    from mathutils import Vector

    if scene is None or scene.name != 'DREAM_StairSky':
        raise ValueError('Expected DREAM_StairSky for the local AO tessellation')
    obj = scene.objects.get('GEO' + TOKEN + 'surround_above')
    if obj is None or obj.type != 'MESH' or obj.modifiers:
        raise ValueError('Expected the unmodified upper mint surround mesh')
    old_mesh = obj.data
    if not old_mesh.vertices:
        raise ValueError('Upper surround mesh is empty')
    low = tuple(min(v.co[axis] for v in old_mesh.vertices) for axis in range(3))
    high = tuple(max(v.co[axis] for v in old_mesh.vertices) for axis in range(3))
    if not all(any(abs(v.co[axis] - edge) < 1e-6 for axis in range(3)
                   for edge in (low[axis], high[axis])) for v in old_mesh.vertices):
        raise ValueError('Upper surround is no longer an axis-aligned box surface')
    # The builder applies scale. Reject rather than silently change spacing in
    # an unexpectedly transformed object; the existing object matrix remains.
    basis = obj.matrix_world.to_3x3()
    if any(abs(basis[i][j] - (1 if i == j else 0)) > 1e-5 for i in range(3) for j in range(3)):
        raise ValueError('Apply the existing box transform before AO tessellation')
    data = box_grid_geometry(low, high, spacing)
    identical = (len(old_mesh.vertices) == len(data['vertices']) and
                 len(old_mesh.polygons) == len(data['faces']) and
                 all((v.co - Vector(p)).length < 1e-6 for v, p in zip(old_mesh.vertices, data['vertices'])) and
                 all(tuple(poly.vertices) == face for poly, face in zip(old_mesh.polygons, data['faces'])))
    result = {'object': obj.name, 'changed': not identical, 'shape_preserved': True,
              'materials_preserved': True, 'ao_excluded': False,
              'vertices': len(data['vertices']), 'quads': len(data['faces']),
              'triangles': len(data['faces']) * 2, 'grid_counts_xyz': data['grid_counts_xyz'],
              'maximum_spacing_m': data['maximum_spacing_m'],
              'local_bounds_min': list(low), 'local_bounds_max': list(high)}
    if identical:
        return result
    material_indices = {poly.material_index for poly in old_mesh.polygons}
    if len(material_indices) != 1:
        raise ValueError('Expected one intentionally plain mint surface material')
    material_index = next(iter(material_indices))
    mesh = bpy.data.meshes.new('DREAM_STAIR_surround_above_ao_grid')
    mesh.from_pydata(data['vertices'], [], data['faces'])
    mesh.update()
    for material in old_mesh.materials:
        mesh.materials.append(material)
    for polygon in mesh.polygons:
        polygon.use_smooth = False
        polygon.material_index = material_index
    names = [uv.name for uv in old_mesh.uv_layers] or ['StairSurfaceUV']
    active_name = old_mesh.uv_layers.active.name if old_mesh.uv_layers.active else names[0]
    render_name = next((uv.name for uv in old_mesh.uv_layers if uv.active_render), active_name)
    for name in names:
        uv = mesh.uv_layers.new(name=name)
        for polygon, normal in zip(mesh.polygons, data['face_normals']):
            axis = max(range(3), key=lambda i: abs(normal[i]))
            axes = (0, 1) if axis == 2 else ((0, 2) if axis == 1 else (1, 2))
            for loop_index in polygon.loop_indices:
                position = obj.matrix_world @ mesh.vertices[mesh.loops[loop_index].vertex_index].co
                uv.data[loop_index].uv = (position[axes[0]] / .28, position[axes[1]] / .28)
        uv.active_render = name == render_name
    mesh.uv_layers.active = mesh.uv_layers[active_name]
    obj.data = mesh
    obj['dream_ao_grid_spacing_m'] = spacing
    obj['dream_ao_grid_policy'] = 'Closed box grid; same six planes, materials and metric UV coverage; AO remains enabled.'
    if old_mesh.users == 0:
        bpy.data.meshes.remove(old_mesh)
    return result


def frame_geometry(frame):
    """Closed U-shaped solid with integral front moulding and a flat rear cap.

    The structural opening remains invariant. A 2 mm reveal lip masks the
    otherwise coplanar mint reveal; its smaller clear aperture is explicit.
    Each profile station defines the
    outward fraction of jamb/header width and its projection before the wall.
    The connected mitred front contains the full painted area between ridges;
    no disconnected rods or cosmetic image planes stand in for the body.
    """
    half = frame['opening_width_m'] / 2
    low, high = frame['opening_bottom_z_m'], frame['opening_top_z_m']
    width, height = frame['jamb_width_m'], frame['header_height_m']
    lip = frame['reveal_lip_m']
    wall_front = frame['wall_y_m'] - frame['wall_thickness_m'] / 2
    rear = frame['wall_y_m'] + frame['wall_thickness_m'] / 2 + frame['back_projection_m']
    profile = frame['solid_profile_fraction_projection_m']
    if min(half, width, height, frame['wall_thickness_m']) <= 0 or high <= low:
        raise ValueError('Invalid stair-frame dimensions')
    if lip <= 0 or lip >= min(width, height) / 10:
        raise ValueError('Reveal overlap must be a small physical edge lip')
    if len(profile) < 2 or profile[0][0] != 0 or profile[-1][0] != 1:
        raise ValueError('Frame profile must cover its complete inner/outer width')
    if any(b[0] <= a[0] for a, b in zip(profile, profile[1:])):
        raise ValueError('Frame stations must increase strictly')
    if any(offset <= .005 for _, offset in profile) or frame['back_projection_m'] <= .005:
        raise ValueError('Keep painted front and rear visibly clear of the wall planes')

    # Contour order: left foot -> left corner -> right corner -> right foot.
    # It is deliberately open underneath: no sill crosses the walkable path.
    def contour(fraction, y):
        x = half + width * fraction - lip * (1 - fraction)
        z = high + height * fraction - lip * (1 - fraction)
        return [(-x, y, low), (-x, y, z), (x, y, z), (x, y, low)]

    n = len(profile)
    vertices = []
    for fraction, projection in profile:
        vertices.extend(contour(fraction, wall_front - projection))
    back_start = len(vertices)
    for fraction, _ in profile:
        vertices.extend(contour(fraction, rear))
    faces, categories = [], []

    def face(indices, category):
        faces.append(tuple(indices))
        categories.append(category)

    for station in range(n - 1):
        for segment in range(3):
            a, b = station * 4 + segment, (station + 1) * 4 + segment
            face((a, a + 1, b + 1, b), 'front_cap')
            face((a + back_start, b + back_start, b + 1 + back_start, a + 1 + back_start), 'back_cap')
        # Closed flat ends at the left and right feet of the U.
        a, b = station * 4, (station + 1) * 4
        face((a, b, b + back_start, a + back_start), 'bottom_cap')
        a, b = station * 4 + 3, (station + 1) * 4 + 3
        face((a, a + back_start, b + back_start, b), 'bottom_cap')
    for segment in range(3):
        a = segment
        face((a, a + back_start, a + 1 + back_start, a + 1), 'inner_reveal')
        a = (n - 1) * 4 + segment
        face((a, a + 1, a + 1 + back_start, a + back_start), 'outer_sidewall')

    # Every real surface carries an explicit metric UV projection. The current
    # frame is intentionally plain paint; these loops also permit later bakes.
    uv_faces = []
    for indices in faces:
        a, b, c = (vertices[i] for i in indices[:3])
        ab, ac = [b[i] - a[i] for i in range(3)], [c[i] - a[i] for i in range(3)]
        normal = [ab[1] * ac[2] - ab[2] * ac[1],
                  ab[2] * ac[0] - ab[0] * ac[2], ab[0] * ac[1] - ab[1] * ac[0]]
        axis = max(range(3), key=lambda i: abs(normal[i]))
        axes = (0, 1) if axis == 2 else ((0, 2) if axis == 1 else (1, 2))
        uv_faces.append([(vertices[i][axes[0]] / .28, vertices[i][axes[1]] / .28) for i in indices])
    return {'vertices': vertices, 'faces': faces, 'uv_faces': uv_faces,
            'surface_categories': categories, 'wall_front_y_m': wall_front,
            'front_y_range_m': [min(vertices[i][1] for i in range(back_start)),
                                max(vertices[i][1] for i in range(back_start))],
            'rear_y_m': rear, 'structural_opening_xyz': [half * 2, low, high],
            'clear_opening_xyz': [2 * (half - lip), low, high - lip]}


def is_frame_object(obj):
    """Narrow ownership filter: excludes the mint surround and all detail."""
    prefix = 'GEO' + TOKEN
    if not obj.name.startswith(prefix):
        return False
    label = obj.name[len(prefix):].split('.')[0]
    return label in ('frame_left', 'frame_right', 'frame_header', 'frame_solid_profile') or (
        label.startswith(('header_moulding_', 'left_moulding_', 'right_moulding_')))


def apply_stair_frame(scene=None, frame_config=None, material=None):
    """Patch only frame objects via data API; safe while another scene is active."""
    import bpy

    if scene is None:
        scene = bpy.data.scenes.get('DREAM_StairSky')
    if scene is None or scene.name != 'DREAM_StairSky':
        raise ValueError('Expected the existing DREAM_StairSky scene')
    if frame_config is None:
        frame_config = json.loads((ROOT / 'blender/stair_sky_plan.json').read_text(encoding='utf-8'))['constructor']['frame']
    data = frame_geometry(frame_config)  # validate before creating/removing data
    previous = [obj for obj in scene.objects if is_frame_object(obj)]
    if material is None:
        material = bpy.data.materials.get('DREAM_STAIR_MAT_frame')
        if material is None:
            material = next((obj.data.materials[0] for obj in previous
                             if obj.type == 'MESH' and obj.data.materials), None)
    if material is None:
        raise ValueError('No existing stair frame material; pass frame_gray from the builder')
    collection = previous[0].users_collection[0] if previous and previous[0].users_collection else (
        scene.collection.children.get('DREAM_StairSky_Blockout') or scene.collection)
    mesh = bpy.data.meshes.new('DREAM_STAIR_solid_frame_profile')
    mesh.from_pydata(data['vertices'], [], data['faces'])
    mesh.update()
    mesh.materials.append(material)
    uv = mesh.uv_layers.new(name='StairSurfaceUV')
    mesh.uv_layers.active = uv
    uv.active_render = True
    for polygon, coordinates in zip(mesh.polygons, data['uv_faces']):
        polygon.use_smooth = False  # preserve broad flats and moulding shoulders
        for loop, coordinate in zip(polygon.loop_indices, coordinates):
            uv.data[loop].uv = coordinate
    obj = bpy.data.objects.new('GEO' + TOKEN + 'frame_solid_profile', mesh)
    collection.objects.link(obj)
    obj['dream_owner'], obj['dream_surface_role'] = 'DREAM_StairSky', 'frame'
    obj['dream_frame_geometry_version'] = 2
    obj['closed_volume'] = True
    obj['dream_surface_coverage'] = json.dumps({
        name: data['surface_categories'].count(name) for name in sorted(set(data['surface_categories']))})
    obj['dream_material_policy'] = 'Existing intentionally plain PBR paint covers every real face; complete metric UVs.'
    removed = [item.name for item in previous]
    for item in previous:
        bpy.data.objects.remove(item, do_unlink=True)
    # Remove a possible .001 suffix caused by an already-present target object.
    obj.name = 'GEO' + TOKEN + 'frame_solid_profile'
    upper_surround = refine_upper_surround(scene)
    return {'scene': scene.name, 'replaced_objects': removed, 'new_object': obj.name,
            'vertices': len(data['vertices']), 'faces': len(data['faces']),
            'triangles': sum(len(face) - 2 for face in data['faces']),
            'material_reused': material.name,
            'upper_surround_ao_tessellation': upper_surround,
            'camera_changed': False, 'navigation_changed': False,
            'grass_changed': False, 'save_render_export_performed': False}
