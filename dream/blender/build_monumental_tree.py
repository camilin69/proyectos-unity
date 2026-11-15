"""Build the editable Blender source scene for video-51's monumental tree.

All dimensions and the walkable terrain are inferred from the supplied camera
frames. The source texture crops stay untouched; this scene uses newly authored
tileable material maps alongside them.
"""
import bpy
import json
import math
import random
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
MAPS = ROOT / 'assets' / 'textures' / 'monumental_tree'
SCENE_NAME = 'DREAM_MonumentalTree'
PREFIX = 'GEO-DREAM-tree-'
GENERATED_PREFIXES = (PREFIX, 'DREAM_Tree_')
random.seed(5102026)

previous_scene = bpy.context.window.scene if bpy.context.window else None
scene = bpy.data.scenes.get(SCENE_NAME) or bpy.data.scenes.new(SCENE_NAME)
for obj in list(scene.objects):
    if obj.name.startswith(GENERATED_PREFIXES):
        bpy.data.objects.remove(obj, do_unlink=True)
# Rebuilding in the live session must not accumulate lights, cameras or stale
# material datablocks in the editable source scene.
for datablocks in (bpy.data.materials, bpy.data.meshes, bpy.data.curves):
    for datablock in list(datablocks):
        if datablock.name.startswith(('DREAM_TREE_', 'DREAM_TREE_CURVE_')) and datablock.users == 0:
            datablocks.remove(datablock)
for collection in (bpy.data.cameras, bpy.data.lights):
    for datablock in list(collection):
        if datablock.name.startswith('DREAM_Tree_') and datablock.users == 0:
            collection.remove(datablock)
if bpy.context.window:
    bpy.context.window.scene = scene

scene.unit_settings.system = 'METRIC'
scene.render.resolution_x = 992
scene.render.resolution_y = 736
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'Medium High Contrast'
scene.view_settings.exposure = 0.0
scene.view_settings.gamma = 1.0
try:
    scene.render.engine = 'BLENDER_EEVEE_NEXT'
except TypeError:
    scene.render.engine = 'BLENDER_EEVEE'
if hasattr(scene, 'eevee') and hasattr(scene.eevee, 'taa_render_samples'):
    scene.eevee.taa_render_samples = 64
scene.render.film_transparent = False
scene['dream_asset'] = 'v51_monumental_tree'
scene['dream_stage'] = 'editable_reference_reconstruction'
scene['dream_reference'] = 'referencias/estetica/evidencias/video-51/01s.png'
scene['dream_source_plan'] = 'validation/all-scenes-plan.json#video-51/arbol_monumental'
scene['dream_scale_note'] = 'Inferred: giant tree, small distant human, broad sloped lawn.'
scene['dream_source_texture_policy'] = 'Source crops preserved separately; clean runtime maps are authored reconstructions.'
scene['dream_navigation'] = json.dumps({
    'support': 'single analytic plane', 'height_at_xy': 'z=-0.30*x',
    'support_bounds': [-42, -70, 42, 36], 'eye_height_m': 1.65,
    'tree_obstacle_disc': [-7, 0, 2.8], 'collision_note': 'Player follows the same slope as the Blender lawn.'
})
scene['dream_runtime_config'] = json.dumps([
    'camera 0 -32 1.65 1.446 0.21',
    'fov 0.47',
    'far_clip 120',
    'exposure -0.08',
    'environment 6',
    'eye_height 1.65',
    'step_limits 0.32 0.32',
    'bounds -42 42 -70 36',
    'ramp -42 -70 42 36 0 -0.30 0',
    'disc -7 0 2.8'
])

world = bpy.data.worlds.get('DREAM_Tree_ClearBlue') or bpy.data.worlds.new('DREAM_Tree_ClearBlue')
world.use_nodes = True
background = next(n for n in world.node_tree.nodes if n.type == 'BACKGROUND')
background.inputs['Color'].default_value = (0.015, 0.085, 0.45, 1)
background.inputs['Strength'].default_value = 0.72
scene.world = world

material_ids = 0
image_cache = {}


def image(filename):
    path = MAPS / filename
    key = str(path)
    if key not in image_cache:
        img = bpy.data.images.load(str(path), check_existing=True)
        img.reload()
        if filename.endswith('_normal.bmp') or filename.endswith('_roughness.bmp'):
            img.colorspace_settings.name = 'Non-Color'
        image_cache[key] = img
    return image_cache[key]


def material(label, color, roughness, kind, base_map=None, normal_map=None, rough_map=None):
    global material_ids
    name = 'DREAM_TREE_' + label
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    output = nodes.new('ShaderNodeOutputMaterial')
    shader = nodes.new('ShaderNodeBsdfPrincipled')
    links.new(shader.outputs['BSDF'], output.inputs['Surface'])
    coordinates = nodes.new('ShaderNodeTexCoord')
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Roughness'].default_value = roughness
    shader.inputs['Metallic'].default_value = 0
    if base_map:
        tex = nodes.new('ShaderNodeTexImage')
        tex.image = image(base_map)
        tex.interpolation = 'Linear'
        links.new(coordinates.outputs['UV'], tex.inputs['Vector'])
        links.new(tex.outputs['Color'], shader.inputs['Base Color'])
    if normal_map:
        tex = nodes.new('ShaderNodeTexImage')
        tex.image = image(normal_map)
        tex.interpolation = 'Linear'
        links.new(coordinates.outputs['UV'], tex.inputs['Vector'])
        normal = nodes.new('ShaderNodeNormalMap')
        normal.inputs['Strength'].default_value = 0.28
        links.new(tex.outputs['Color'], normal.inputs['Color'])
        links.new(normal.outputs['Normal'], shader.inputs['Normal'])
    if rough_map:
        tex = nodes.new('ShaderNodeTexImage')
        tex.image = image(rough_map)
        tex.interpolation = 'Linear'
        links.new(coordinates.outputs['UV'], tex.inputs['Vector'])
        links.new(tex.outputs['Color'], shader.inputs['Roughness'])
    mat.diffuse_color = (*color, 1)
    mat['dream_id'] = material_ids
    mat['kind'] = kind
    mat['roughness'] = roughness
    mat['metallic'] = 0.0
    material_ids += 1
    return mat


bark = material('Bark_Limestone', (0.76, 0.74, 0.69), 0.94, 0,
                'bark_albedo.bmp', 'bark_normal.bmp', 'bark_roughness.bmp')
bark_shadow = material('Bark_DeepFissure', (0.46, 0.47, 0.45), 0.96, 0,
                       'bark_albedo.bmp', 'bark_normal.bmp', 'bark_roughness.bmp')
foliage_mats = [
    material('Canopy_DeepPine', (0.70, 0.78, 0.66), 0.92, 5, 'foliage_albedo.bmp'),
    material('Canopy_Olive', (0.78, 0.83, 0.67), 0.93, 5, 'foliage_albedo.bmp'),
    material('Canopy_Shadow', (0.55, 0.66, 0.52), 0.96, 5, 'foliage_albedo.bmp'),
]
grass = material('Hill_Grass', (1, 1, 1), 0.94, 11,
                 'grass_albedo.bmp', 'grass_normal.bmp', 'grass_roughness.bmp')
person = material('ScaleFigure_OffWhite', (0.78, 0.80, 0.75), 0.72, 18)
person_dark = material('ScaleFigure_ShadowCloth', (0.30, 0.34, 0.31), 0.88, 18)
runtime_shadow = material('RuntimeCanopyShadow', (0.055, 0.095, 0.035), 1.0, 17)


def add_mesh(label, verts, faces, mats, mat_indices=None, uv_mode='world'):
    mesh = bpy.data.meshes.new('DREAM_TREE_' + label)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    for mat in mats:
        mesh.materials.append(mat)
    if mat_indices:
        for poly, index in zip(mesh.polygons, mat_indices):
            poly.material_index = index
    uv_layer = mesh.uv_layers.new(name='UVMap')
    mesh.uv_layers.active = uv_layer
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            p = mesh.vertices[mesh.loops[li].vertex_index].co
            if uv_mode == 'bark':
                uv_layer.data[li].uv = ((p.x + p.y * 0.33) * 0.42, p.z * 0.11)
            elif uv_mode == 'foliage':
                uv_layer.data[li].uv = ((p.x + p.y * 0.27) * 0.16, (p.z + p.y * 0.16) * 0.16)
            elif uv_mode == 'grass':
                uv_layer.data[li].uv = (p.x * 0.12, p.y * 0.12)
            else:
                uv_layer.data[li].uv = (p.x * 0.4, p.z * 0.4)
    obj = bpy.data.objects.new(PREFIX + label, mesh)
    scene.collection.objects.link(obj)
    if label.startswith(('canopy', 'grass-blades')):
        obj['dream_skip_ao'] = True
    for poly in mesh.polygons:
        poly.use_smooth = True
    return obj


def hill_z(x, y=0.0):
    return -0.30 * x


# Broad, continuous lawn surface. The runtime uses the same analytic ramp for
# foot placement; its collision plane never snaps the player to a flat floor.
hill_verts = []
hill_faces = []
nx, ny = 45, 58
x0, x1, y0, y1 = -44.0, 44.0, -80.0, 35.0
for j in range(ny + 1):
    y = y0 + (y1 - y0) * j / ny
    for i in range(nx + 1):
        x = x0 + (x1 - x0) * i / nx
        hill_verts.append((x, y, hill_z(x, y)))
for j in range(ny):
    for i in range(nx):
        a = j * (nx + 1) + i
        hill_faces.append((a, a + 1, a + nx + 2, a + nx + 1))
hill = add_mesh('sloped-grass-hill', hill_verts, hill_faces, [grass], uv_mode='grass')


def catmull(points, samples=5):
    output = []
    for i in range(len(points) - 1):
        p0 = points[max(i - 1, 0)]
        p1 = points[i]
        p2 = points[i + 1]
        p3 = points[min(i + 2, len(points) - 1)]
        for step in range(samples):
            t = step / samples
            vals = []
            for k in range(4):
                vals.append(0.5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * t +
                                   (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t * t +
                                   (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t * t * t))
            output.append(vals)
    output.append(list(points[-1]))
    return output


def branch(label, points, bevel, mat=bark, resolution=10):
    data = bpy.data.curves.new('DREAM_TREE_CURVE_' + label, 'CURVE')
    data.dimensions = '3D'
    data.resolution_u = 2
    data.bevel_depth = bevel
    data.bevel_resolution = 3
    data.resolution_u = 2
    spline = data.splines.new('POLY')
    path = catmull(points)
    spline.points.add(len(path) - 1)
    for point, values in zip(spline.points, path):
        point.co = (values[0], values[1], values[2], 1.0)
        point.radius = values[3]
    obj = bpy.data.objects.new(PREFIX + label, data)
    scene.collection.objects.link(obj)
    data.materials.append(mat)
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.convert(target='MESH')
    obj = bpy.context.object
    obj.name = PREFIX + label
    for existing_uv in list(obj.data.uv_layers):
        obj.data.uv_layers.remove(existing_uv)
    uv_layer = obj.data.uv_layers.new(name='UVMap')
    obj.data.uv_layers.active = uv_layer
    for poly in obj.data.polygons:
        poly.use_smooth = True
        for li in poly.loop_indices:
            p = obj.data.vertices[obj.data.loops[li].vertex_index].co
            uv_layer.data[li].uv = ((p.x + p.y * 0.33) * 0.42, p.z * 0.11)
    obj['dream_skip_ao'] = True
    return obj


base_x = -7.0
base_z = hill_z(base_x)
trunk = [
    (base_x, 0.0, base_z + 0.20, 1.28),
    (base_x - 0.50, 0.0, base_z + 3.0, 1.00),
    (base_x - 0.35, 0.1, base_z + 7.0, 0.82),
    (base_x + 0.15, 0.18, base_z + 11.0, 0.72),
    (base_x + 0.90, 0.28, base_z + 15.5, 0.59),
    (base_x + 1.25, 0.40, base_z + 20.0, 0.46),
    (base_x + 2.20, 0.65, base_z + 24.5, 0.32),
    (base_x + 3.50, 0.85, base_z + 28.5, 0.16),
    (base_x + 4.10, 0.95, base_z + 31.0, 0.06),
]
branch('main-trunk', trunk, 1.60, bark)

branches = [
    ('primary-right-low', [(-6.8, 0.2, base_z + 13, .62), (-3, .25, base_z + 15, .52), (2, .35, base_z + 16.4, .39), (8, .55, base_z + 16.6, .29), (14, .8, base_z + 15.7, .20), (20, 1.05, base_z + 14.4, .08)], .66),
    ('primary-left-low', [(-7.0, .18, base_z + 12, .62), (-11, .18, base_z + 14.0, .49), (-16, .20, base_z + 16.1, .32), (-21, .35, base_z + 17.4, .16), (-25, .55, base_z + 17.5, .04)], .61),
    ('primary-right-high', [(-5.9, .42, base_z + 18.7, .48), (-2.2, .55, base_z + 22.0, .37), (3.0, .72, base_z + 23.4, .27), (8.5, .93, base_z + 22.8, .19), (14.5, 1.0, base_z + 21.0, .07)], .51),
    ('primary-left-high', [(-5.7, .4, base_z + 20, .46), (-9.1, .55, base_z + 23.8, .35), (-14.0, .70, base_z + 26.8, .23), (-19.0, .9, base_z + 27.4, .06)], .48),
    ('crown-center', [(-3.8, .65, base_z + 25, .34), (-1.0, .8, base_z + 29, .24), (2.8, 1.0, base_z + 31, .15), (6.2, 1.2, base_z + 30, .04)], .38),
    ('outer-right-droop', [(5.0, .8, base_z + 22, .25), (10, 1.0, base_z + 20, .18), (15, 1.3, base_z + 17.5, .12), (20, 1.6, base_z + 15.8, .035)], .29),
    ('outer-left-fork', [(-13, .55, base_z + 25, .25), (-17, .75, base_z + 29, .16), (-22, .95, base_z + 30, .08), (-25, 1.15, base_z + 29, .025)], .29),
    ('crossing-limb', [(-6.7, -.55, base_z + 16, .35), (-4, -1.2, base_z + 18, .23), (-1, -1.6, base_z + 19, .13), (3, -1.8, base_z + 18.7, .025)], .37),
]
for name, path, radius in branches:
    branch(name, path, radius * 1.75, bark if 'primary' in name else bark_shadow)

# Secondary limbs break the clean geometric arcs and carry smaller sprays into
# the crown, following the irregular branch network visible in the frame.
twig_sources = [entry[1] for entry in branches[:7]]
for index in range(26):
    source = random.choice(twig_sources)
    segment = random.randrange(len(source) - 1)
    t = random.uniform(.22, .82)
    a, b = source[segment], source[segment + 1]
    x = a[0] * (1 - t) + b[0] * t
    y = a[1] * (1 - t) + b[1] * t
    z = a[2] * (1 - t) + b[2] * t
    side = -1 if x < base_x - 1 else 1
    dx = side * random.uniform(.7, 2.6)
    dy = random.uniform(-1.5, 1.5)
    dz = random.uniform(1.3, 4.4)
    twig = [(x, y, z, .56),
            (x + dx * .48, y + dy * .52, z + dz * .53, .34),
            (x + dx, y + dy, z + dz, .015)]
    branch('secondary-twig-%02d' % index, twig, random.uniform(.14, .22), bark_shadow)

# Exposed, radial buttress roots merge the huge trunk into the sloped turf.
for index in range(9):
    angle = 2 * math.pi * index / 9 + 0.12
    dx, dy = math.cos(angle), math.sin(angle)
    end_x, end_y = base_x + dx * random.uniform(2.2, 4.0), dy * random.uniform(2.0, 3.8)
    end_z = hill_z(end_x, end_y) + 0.05
    path = [
        (base_x + dx * .32, dy * .30, base_z + 1.15, .54),
        (base_x + dx * 1.0, dy * .8, base_z + .72, .38),
        (base_x + dx * 2.1, dy * 1.6, end_z + .28, .17),
        (end_x, end_y, end_z, .025),
    ]
    branch('buttress-root-%02d' % index, path, 1.35, bark)


# Leaf clusters form a broad, asymmetric crown and leave intentional blue-sky
# windows between major limbs. Individual curved leaves replace spherical
# placeholders so the silhouette reads as foliage at both close and long range.
canopy_verts, canopy_faces, canopy_indices = [], [], []
cluster_count = 1900
for cluster in range(cluster_count):
    # Rejection-sampled elliptical crown, slightly heavier on the right.
    for _ in range(500):
        cx = random.uniform(-25.0, 21.0)
        cz = random.uniform(base_z + 10.0, base_z + 25.0)
        ellipse = ((cx + 2.0) / 25.0) ** 2 + ((cz - (base_z + 16.5)) / 8.4) ** 2
        if ellipse < random.uniform(.72, 1.12):
            break
    cy = random.uniform(-2.8, 2.5)
    size = random.uniform(.50, .90)
    mat_index = random.choices([0, 1, 2], weights=[.48, .23, .29])[0]
    for leaf_index in range(random.randint(10, 18)):
        center = Vector((cx + random.uniform(-.52, .52) * size,
                         cy + random.uniform(-.42, .42) * size,
                         cz + random.uniform(-.42, .42) * size))
        axis = Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-.65, .9))).normalized()
        normal = Vector((random.uniform(-.9, .9), random.uniform(-1.0, -.20), random.uniform(-.85, .85))).normalized()
        width_axis = axis.cross(normal)
        if width_axis.length < 0.1:
            width_axis = axis.cross(Vector((0, 0, 1)))
        width_axis.normalize()
        length = random.uniform(.48, .84) * size
        width = random.uniform(.12, .22) * size
        leaf_points = [center + normal * width * .20,
                       center - axis * length * .50,
                       center - axis * length * .19 + width_axis * width * .72,
                       center + axis * length * .08 + width_axis * width,
                       center + axis * length * .50,
                       center + axis * length * .08 - width_axis * width,
                       center - axis * length * .19 - width_axis * width * .72]
        first = len(canopy_verts)
        canopy_verts.extend(tuple(point) for point in leaf_points)
        for edge in range(1, 7):
            canopy_faces.append((first, first + edge, first + (edge % 6) + 1))
            canopy_indices.append(mat_index)
canopy = add_mesh('canopy-leaf-masses', canopy_verts, canopy_faces, foliage_mats, canopy_indices, 'foliage')
canopy['dream_cluster_count'] = cluster_count


# Sparse close-range grass blades give the lawn a readable surface without
# filling the source silhouette with tall ornamental vegetation.
blade_verts, blade_faces = [], []
for _ in range(180):
    x = random.uniform(-37, 37)
    y = random.uniform(-29, 25)
    z = hill_z(x, y) + .015
    height = random.uniform(.06, .12)
    width = random.uniform(.015, .03)
    angle = random.uniform(0, 2 * math.pi)
    dx, dy = math.cos(angle), math.sin(angle)
    sx, sy = -dy * width, dx * width
    lean = random.uniform(-.11, .11)
    i = len(blade_verts)
    blade_verts.extend([(x - sx, y - sy, z), (x + sx, y + sy, z),
                        (x + dx * lean, y + dy * lean, z + height)])
    blade_faces.append((i, i + 1, i + 2))
blades = add_mesh('grass-blades', blade_verts, blade_faces, [grass], uv_mode='grass')


def ellipsoid(label, center, scale, mat, segments=12, rings=8):
    verts, faces = [], []
    for j in range(rings + 1):
        theta = math.pi * j / rings
        for i in range(segments):
            phi = 2 * math.pi * i / segments
            verts.append((center[0] + math.sin(theta) * math.cos(phi) * scale[0],
                          center[1] + math.sin(theta) * math.sin(phi) * scale[1],
                          center[2] + math.cos(theta) * scale[2]))
    for j in range(rings):
        for i in range(segments):
            a = j * segments + i
            b = j * segments + (i + 1) % segments
            faces.append((a, b, b + segments, a + segments))
    return add_mesh(label, verts, faces, [mat], uv_mode='person')


def limb(label, a, b, radius, mat):
    direction = Vector(b) - Vector(a)
    midpoint = (Vector(a) + Vector(b)) * .5
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=radius, depth=direction.length, location=midpoint)
    obj = bpy.context.object
    obj.name = PREFIX + label
    obj.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()
    obj.data.materials.append(mat)
    obj['dream_skip_ao'] = True
    return obj


# A small pale human in the distance anchors the otherwise implausibly large tree.
human_x, human_y = 3.3, 20.0
human_z = hill_z(human_x, human_y)
human_scale = .76
ellipsoid('distant-person-head', (human_x, human_y, human_z + 1.56 * human_scale), (.105 * human_scale, .105 * human_scale, .13 * human_scale), person)
ellipsoid('distant-person-body', (human_x, human_y, human_z + 1.13 * human_scale), (.17 * human_scale, .12 * human_scale, .31 * human_scale), person)
limb('distant-person-left-leg', (human_x - .08 * human_scale, human_y, human_z + .95 * human_scale), (human_x - .11 * human_scale, human_y, human_z + .12 * human_scale), .055 * human_scale, person_dark)
limb('distant-person-right-leg', (human_x + .08 * human_scale, human_y, human_z + .95 * human_scale), (human_x + .12 * human_scale, human_y, human_z + .12 * human_scale), .055 * human_scale, person_dark)
limb('distant-person-left-arm', (human_x - .15 * human_scale, human_y, human_z + 1.34 * human_scale), (human_x - .30 * human_scale, human_y + .02 * human_scale, human_z + .75 * human_scale), .043 * human_scale, person)
limb('distant-person-right-arm', (human_x + .15 * human_scale, human_y, human_z + 1.34 * human_scale), (human_x + .27 * human_scale, human_y - .03 * human_scale, human_z + .76 * human_scale), .043 * human_scale, person)


# Runtime-only dark canopy footprint: Blender renders real directional shadows;
# the OpenGL profile uses this slightly lifted grass polygon as a soft proxy.
shadow_outline = [(-11, -1), (-8, -3), (-3, -4), (3, -3), (7, -1), (13, 1),
                  (18, 4), (20, 8), (16, 10), (10, 8), (4, 7), (-2, 6), (-8, 4), (-12, 2)]
shadow_center = (sum(x for x, _ in shadow_outline) / len(shadow_outline),
                 sum(y for _, y in shadow_outline) / len(shadow_outline))
shadow_verts = [(x, y, hill_z(x, y) + .035) for x, y in shadow_outline]
shadow_verts.append((shadow_center[0], shadow_center[1], hill_z(*shadow_center) + .035))
shadow_faces = [(len(shadow_outline), i, (i + 1) % len(shadow_outline)) for i in range(len(shadow_outline))]
shadow = add_mesh('runtime-canopy-shadow', shadow_verts, shadow_faces, [runtime_shadow], uv_mode='grass')
shadow.hide_render = True
shadow['dream_runtime_only'] = True
shadow['dream_skip_ao'] = True


# Direct sunlight and a cool sky fill reproduce the hard, high-contrast image.
sun_data = bpy.data.lights.new('DREAM_Tree_Sun', 'SUN')
sun_data.energy = 3.5
sun_data.angle = math.radians(.6)
sun = bpy.data.objects.new('DREAM_Tree_Sun', sun_data)
scene.collection.objects.link(sun)
sun.rotation_euler = Vector((.50, .62, -1.0)).to_track_quat('-Z', 'Y').to_euler()

camera_data = bpy.data.cameras.new('DREAM_Tree_ReferenceCamera')
camera = bpy.data.objects.new('DREAM_Tree_ReferenceCamera', camera_data)
scene.collection.objects.link(camera)
camera.location = (0, -32, 1.65)
camera_target = Vector((4.0, 0, 7.15))
camera_target.z = 8.50
camera.rotation_euler = (camera_target - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera_data.lens = 28
camera_data.sensor_width = 36
scene.camera = camera

scene.render.filepath = str(ROOT / 'validation' / 'tree-preview.png')
scene.render.resolution_percentage = 100

# Keep the existing OceanExitWater scene active after authoring. Save only this
# new scene, its objects, and material images into a separate editable file.
if bpy.context.window and previous_scene and previous_scene.name in bpy.data.scenes:
    bpy.context.window.scene = previous_scene
print(json.dumps({'scene': SCENE_NAME, 'objects': len(scene.objects),
                  'materials': len({m.name for o in scene.objects if o.type == 'MESH' for m in o.data.materials}),
                  'camera': list(camera.location), 'reference_target': list(camera_target)}))
