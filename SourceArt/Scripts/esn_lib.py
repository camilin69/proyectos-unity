# Biblioteca bpy compartida para la fabricación de assets (secciones 24, 36, 38, 40, 41, 59).
# Se ejecuta dentro de Blender vía MCP. Convenciones: metros, Z arriba en Blender; export FBX -Z forward / Y up.
import bpy, bmesh, math, os, json
from mathutils import Vector, Matrix

ROOT = r"C:/Users/HP/Documents/GitHub/proyectos-unity"
BLEND_DIR = ROOT + "/SourceArt/Blender"
TEX_DIR = ROOT + "/EsneiderProtocoloLazaro/Assets/_Game/Art/Textures"
FBX_DIR = ROOT + "/EsneiderProtocoloLazaro/Assets/_Game/Art/Models"
EVIDENCE = ROOT + "/SourceArt/_evidence/EX-04"
for d in (BLEND_DIR, TEX_DIR, FBX_DIR, EVIDENCE):
    os.makedirs(d, exist_ok=True)


def reset_scene():
    """Limpia la escena sin recargar el archivo (mantiene vivo el servidor MCP)."""
    scene = bpy.context.scene
    for o in list(scene.objects): bpy.data.objects.remove(o, do_unlink=True)
    for c in list(bpy.data.collections): bpy.data.collections.remove(c)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.armatures, bpy.data.actions, bpy.data.images, bpy.data.curves, bpy.data.cameras, bpy.data.lights):
        for d in list(coll):
            try: coll.remove(d)
            except Exception: pass
    bpy.data.orphans_purge(do_recursive=True)
    scene.unit_settings.system = 'METRIC'; scene.unit_settings.scale_length = 1.0
    scene.frame_start = 1
    return scene


def ctx(o=None, objs=None):
    """Contexto para operadores desde el socket MCP (sin área activa)."""
    win = bpy.context.window_manager.windows[0]
    area = next(a for a in win.screen.areas if a.type == 'VIEW_3D')
    region = next(r for r in area.regions if r.type == 'WINDOW')
    sel = objs if objs is not None else ([o] if o else [])
    for ob in bpy.context.scene.objects:
        try: ob.select_set(False)
        except Exception: pass
    for ob in sel: ob.select_set(True)
    if o is not None: bpy.context.view_layer.objects.active = o
    elif sel: bpy.context.view_layer.objects.active = sel[0]
    act = o or (sel[0] if sel else None)
    return bpy.context.temp_override(window=win, screen=win.screen, area=area, region=region, active_object=act, object=act, selected_objects=sel, selected_editable_objects=sel, view_layer=bpy.context.view_layer, scene=bpy.context.scene)


def _new(name, bm, col=None):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    if col: link(o, col)
    return o


def collection(name):
    col = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if col.name not in [c.name for c in bpy.context.scene.collection.children]:
        bpy.context.scene.collection.children.link(col)
    return col


def link(obj, col):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)
    return obj


# ---------- primitivas con pivote controlado (bmesh, sin operadores) ----------
def box(name, size, loc=(0, 0, 0), col=None, pivot='center', rot=(0, 0, 0), bevel=0.0, segs=2):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(size[0], size[1], size[2]), verts=bm.verts)
    if pivot == 'bottom': bmesh.ops.translate(bm, vec=(0, 0, size[2] / 2), verts=bm.verts)
    elif pivot == 'top': bmesh.ops.translate(bm, vec=(0, 0, -size[2] / 2), verts=bm.verts)
    if bevel > 0: bmesh.ops.bevel(bm, geom=bm.verts[:] + bm.edges[:], offset=min(bevel, min(size) * 0.45), segments=segs, affect='EDGES')
    o = _new(name, bm, col); o.location = loc; o.rotation_euler = rot
    return o


def cyl(name, radius, depth, loc=(0, 0, 0), col=None, axis='Z', verts=24, pivot='center', bevel=0.0):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=verts, radius1=radius, radius2=radius, depth=depth)
    if pivot == 'bottom': bmesh.ops.translate(bm, vec=(0, 0, depth / 2), verts=bm.verts)
    if bevel > 0:
        edges = [e for e in bm.edges if abs(e.verts[0].co.z - e.verts[1].co.z) < 1e-6]
        bmesh.ops.bevel(bm, geom=edges, offset=min(bevel, radius * 0.4, depth * 0.4), segments=2, affect='EDGES')
    if axis == 'X': bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, 'Y'), verts=bm.verts)
    elif axis == 'Y': bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, 'X'), verts=bm.verts)
    o = _new(name, bm, col); o.location = loc
    return o


def sphere(name, radius, loc=(0, 0, 0), col=None, segs=24, rings=16, scale=(1, 1, 1)):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=rings, radius=radius)
    bmesh.ops.scale(bm, vec=scale, verts=bm.verts)
    o = _new(name, bm, col); o.location = loc
    return o


def torus(name, major, minor, loc=(0, 0, 0), col=None, axis='Z', segs=32, rings=12):
    bm = bmesh.new()
    verts = []
    for i in range(segs):
        a = 2 * math.pi * i / segs
        ring = []
        for j in range(rings):
            b = 2 * math.pi * j / rings
            r = major + minor * math.cos(b)
            ring.append(bm.verts.new((r * math.cos(a), r * math.sin(a), minor * math.sin(b))))
        verts.append(ring)
    for i in range(segs):
        for j in range(rings):
            bm.faces.new((verts[i][j], verts[(i + 1) % segs][j], verts[(i + 1) % segs][(j + 1) % rings], verts[i][(j + 1) % rings]))
    if axis == 'X': bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, 'Y'), verts=bm.verts)
    elif axis == 'Y': bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, 'X'), verts=bm.verts)
    o = _new(name, bm, col); o.location = loc
    return o


def tube(name, points, radius, col=None, verts=10):
    """Cable/tubo a lo largo de una polilinea: anillos unidos entre puntos."""
    bm = bmesh.new()
    rings = []
    pts = [Vector(p) for p in points]
    for i, p in enumerate(pts):
        d = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        u = d.cross(Vector((0, 0, 1))); u = u.normalized() if u.length > 1e-4 else Vector((1, 0, 0))
        v = d.cross(u).normalized()
        rings.append([bm.verts.new(p + (u * math.cos(2 * math.pi * k / verts) + v * math.sin(2 * math.pi * k / verts)) * radius) for k in range(verts)])
    for i in range(len(rings) - 1):
        for k in range(verts):
            bm.faces.new((rings[i][k], rings[i + 1][k], rings[i + 1][(k + 1) % verts], rings[i][(k + 1) % verts]))
    bm.faces.new(list(reversed(rings[0]))); bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = _new(name, bm, col)
    return o


def join(objs, name):
    with ctx(objs[0], objs): bpy.ops.object.join()
    o = objs[0]; o.name = name
    return o


def apply_all(o):
    with ctx(o):
        bpy.ops.object.convert(target='MESH')
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)


def set_origin(o, point):
    saved = bpy.context.scene.cursor.location.copy()
    bpy.context.scene.cursor.location = point
    with ctx(o): bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    bpy.context.scene.cursor.location = saved


def smooth(o, angle=35):
    me = o.data
    for p in me.polygons: p.use_smooth = True
    bm = bmesh.new(); bm.from_mesh(me)
    for e in bm.edges:
        if len(e.link_faces) == 2 and e.calc_face_angle(0) > math.radians(angle): e.smooth = False
    bm.to_mesh(me); bm.free()


# ---------- materiales PBR procedurales (41.2 rangos de roughness) ----------
def _principled(mat):
    return next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')


def material(name, base=(0.5, 0.5, 0.5), rough=0.5, metal=0.0, wear=0.0, wear_color=(0.35, 0.2, 0.12), bump=0.0, scale=8.0, emission=None):
    """Material con variación de roughness/color por ruido y desgaste en bordes (Pointiness/AO no exportables: se hornea)."""
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        if n.type not in ('OUTPUT_MATERIAL', 'BSDF_PRINCIPLED'):
            nt.nodes.remove(n)
    p = _principled(mat)
    p.inputs['Base Color'].default_value = (*base, 1)
    p.inputs['Roughness'].default_value = rough
    p.inputs['Metallic'].default_value = metal
    tex = nt.nodes.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value = scale; tex.inputs['Detail'].default_value = 6
    ramp = nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].position = 0.35; ramp.color_ramp.elements[1].position = 0.65
    ramp.color_ramp.elements[0].color = (max(0, rough - 0.12),) * 3 + (1,); ramp.color_ramp.elements[1].color = (min(1, rough + 0.12),) * 3 + (1,)
    nt.links.new(tex.outputs['Fac'], ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'], p.inputs['Roughness'])
    if wear > 0:
        wtex = nt.nodes.new('ShaderNodeTexNoise'); wtex.inputs['Scale'].default_value = scale * 1.7; wtex.inputs['Detail'].default_value = 8
        wramp = nt.nodes.new('ShaderNodeValToRGB'); wramp.color_ramp.elements[0].position = 0.62 - wear * 0.25; wramp.color_ramp.elements[1].position = 0.75
        mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'
        mix.inputs[6].default_value = (*base, 1); mix.inputs[7].default_value = (*wear_color, 1)
        nt.links.new(wtex.outputs['Fac'], wramp.inputs['Fac']); nt.links.new(wramp.outputs['Color'], mix.inputs[0]); nt.links.new(mix.outputs[2], p.inputs['Base Color'])
        if metal > 0.5:
            mm = nt.nodes.new('ShaderNodeMath'); mm.operation = 'SUBTRACT'; mm.inputs[0].default_value = metal
            nt.links.new(wramp.outputs['Color'], mm.inputs[1]); nt.links.new(mm.outputs[0], p.inputs['Metallic'])
    if bump > 0:
        btex = nt.nodes.new('ShaderNodeTexNoise'); btex.inputs['Scale'].default_value = scale * 6; btex.inputs['Detail'].default_value = 10
        bn = nt.nodes.new('ShaderNodeBump'); bn.inputs['Strength'].default_value = bump; bn.inputs['Distance'].default_value = 0.01
        nt.links.new(btex.outputs['Fac'], bn.inputs['Height']); nt.links.new(bn.outputs['Normal'], p.inputs['Normal'])
    if emission:
        p.inputs['Emission Color'].default_value = (*emission[0], 1); p.inputs['Emission Strength'].default_value = emission[1]
    return mat


def assign(o, mat):
    o.data.materials.clear(); o.data.materials.append(mat)


MATS = {}
def std_mats():
    if MATS: return MATS
    MATS['steel_paint'] = material("M_SteelPaint", (0.32, 0.36, 0.34), 0.55, 0.0, wear=0.35, wear_color=(0.55, 0.55, 0.5), bump=0.15)
    MATS['steel_bare'] = material("M_SteelBare", (0.56, 0.57, 0.58), 0.35, 1.0, wear=0.3, wear_color=(0.42, 0.3, 0.2), bump=0.1)
    MATS['steel_dark'] = material("M_SteelDark", (0.2, 0.21, 0.23), 0.45, 1.0, wear=0.2, bump=0.1)
    MATS['rubber'] = material("M_Rubber", (0.05, 0.05, 0.05), 0.85, 0.0, bump=0.3, scale=30)
    MATS['polymer_ivory'] = material("M_PolymerIvory", (0.82, 0.78, 0.7), 0.5, 0.0, wear=0.25, wear_color=(0.5, 0.45, 0.38), bump=0.08)
    MATS['polymer_dark'] = material("M_PolymerDark", (0.12, 0.12, 0.13), 0.6, 0.0, bump=0.1)
    MATS['ceramic'] = material("M_Ceramic", (0.85, 0.83, 0.78), 0.25, 0.0)
    MATS['copper'] = material("M_Copper", (0.72, 0.42, 0.28), 0.4, 1.0, wear=0.3, wear_color=(0.25, 0.35, 0.3))
    MATS['glass'] = material("M_Glass", (0.85, 0.9, 0.95), 0.08, 0.0); _principled(MATS['glass']).inputs['Transmission Weight'].default_value = 0.9; MATS['glass'].blend_method = 'BLEND'
    MATS['skin'] = material("M_Skin", (0.72, 0.52, 0.42), 0.48, 0.0, bump=0.06, scale=40)
    MATS['fabric'] = material("M_Fabric", (0.3, 0.34, 0.38), 0.85, 0.0, bump=0.35, scale=60)
    MATS['emitter'] = material("M_Emitter", (0.3, 0.6, 1.0), 0.3, 0.0, emission=((0.3, 0.6, 1.0), 2.0))
    MATS['screen'] = material("M_Screen", (0.05, 0.08, 0.1), 0.2, 0.0, emission=((0.2, 0.5, 0.45), 1.2))
    MATS['pad'] = material("M_Pad", (0.18, 0.2, 0.22), 0.75, 0.0, bump=0.2, scale=25)
    MATS['concrete'] = material("M_Concrete", (0.45, 0.46, 0.43), 0.9, 0.0, bump=0.4, scale=20)
    return MATS


# ---------- UV ----------
def uv_project(o, margin=0.02):
    with ctx(o):
        bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=margin)
        bpy.ops.object.mode_set(mode='OBJECT')


def uv_project_all(objs, margin=0.004):
    """Un solo atlas por asset (40.3): desplegado multiobjeto para que las islas de todas las piezas se empaqueten juntas."""
    meshes = [o for o in objs if o.type == 'MESH']
    with ctx(meshes[0], meshes):
        bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=margin)
        bpy.ops.object.mode_set(mode='OBJECT')


# ---------- bake a texturas PBR (41.1) ----------
_bake_saved = {}


def bake_pbr(objs, asset_id, size=1024, samples=8, only=None):
    """Hornea BaseColor/Roughness/Metallic/Normal de los materiales procedurales a un atlas por asset (UV compartida por objeto)."""
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = samples; scene.cycles.use_denoising = False
    scene.cycles.device = 'CPU'
    maps = {'BaseColor': ('DIFFUSE', True), 'Roughness': ('ROUGHNESS', False), 'Metallic': ('EMIT', False), 'Normal': ('NORMAL', False)}
    out = {}
    mats = set()
    for o in objs:
        for m in o.data.materials:
            if m: mats.add(m)
    for mapname, (btype, srgb) in maps.items():
        if only and mapname not in only: continue
        img = bpy.data.images.new(f"{asset_id}_{mapname}", size, size, alpha=False, float_buffer=False)
        img.colorspace_settings.name = 'sRGB' if srgb else 'Non-Color'
        nodes = []
        for m in mats:
            nt = m.node_tree
            node = nt.nodes.new('ShaderNodeTexImage'); node.image = img; nt.nodes.active = node; nodes.append((nt, node))
            if mapname == 'Metallic':
                # metallic no tiene pase de bake: se enruta temporalmente a emisión
                p = _principled(m)
                link_src = p.inputs['Metallic'].links[0].from_socket if p.inputs['Metallic'].links else None
                val = p.inputs['Metallic'].default_value
                _bake_saved[m.name] = (val, p.inputs['Emission Strength'].default_value, tuple(p.inputs['Emission Color'].default_value))
                if link_src: nt.links.new(link_src, p.inputs['Emission Color'])
                else: p.inputs['Emission Color'].default_value = (val, val, val, 1)
                p.inputs['Emission Strength'].default_value = 1.0
        scene.render.bake.use_pass_direct = False; scene.render.bake.use_pass_indirect = False
        scene.render.bake.use_pass_color = True; scene.render.bake.margin = 8
        with ctx(objs[0], objs): bpy.ops.object.bake(type=btype, use_selected_to_active=False)
        path = f"{TEX_DIR}/{asset_id}_{mapname}.png"
        img.filepath_raw = path; img.file_format = 'PNG'; img.save()
        out[mapname] = path
        for nt, node in nodes: nt.nodes.remove(node)
        if mapname == 'Metallic':
            for m in mats:
                p = _principled(m)
                val, strength, color = _bake_saved.pop(m.name, (0.0, 0.0, (0, 0, 0, 1)))
                for l in list(p.inputs['Emission Color'].links): m.node_tree.links.remove(l)
                p.inputs['Emission Color'].default_value = color
                p.inputs['Emission Strength'].default_value = strength
    return out


# ---------- rig ----------
def armature(name, bones, col=None):
    """bones: lista de (nombre, head, tail, parent) en coordenadas de armadura."""
    arm = bpy.data.armatures.new(name)
    obj = bpy.data.objects.new(name, arm)
    bpy.context.scene.collection.objects.link(obj)
    if col: link(obj, col)
    with ctx(obj):
        bpy.ops.object.mode_set(mode='EDIT')
        eb = {}
        for bname, head, tail, parent in bones:
            b = arm.edit_bones.new(bname); b.head = head; b.tail = tail
            if parent: b.parent = eb[parent]; b.use_connect = (Vector(head) - eb[parent].tail).length < 1e-4
            eb[bname] = b
        bpy.ops.object.mode_set(mode='OBJECT')
    return obj


def bind_rigid(obj, arm_obj, bone):
    """Piezas mecánicas: cada pieza a un hueso (vertex group 100%) — deformación rígida (36.4)."""
    vg = obj.vertex_groups.new(name=bone)
    vg.add(list(range(len(obj.data.vertices))), 1.0, 'REPLACE')
    m = obj.modifiers.new("Armature", 'ARMATURE'); m.object = arm_obj
    obj.parent = arm_obj


def _fcurves(act):
    """Blender ≥4.4: acciones por capas/slots; <4.4: act.fcurves."""
    try:
        return list(act.fcurves)
    except AttributeError:
        out = []
        for layer in act.layers:
            for strip in layer.strips:
                for cb in strip.channelbags: out.extend(cb.fcurves)
        return out


def action(arm_obj, name, frames, fps=30, poses=None, loop=True):
    """poses: {frame: {bone: (rot_euler_deg xyz, loc xyz)}} en espacio local del hueso."""
    if arm_obj.animation_data is None: arm_obj.animation_data_create()
    act = bpy.data.actions.new(name)
    arm_obj.animation_data.action = act
    bpy.context.scene.render.fps = fps
    for f, bones in sorted(poses.items()):
        for bname, (rot, loc) in bones.items():
            pb = arm_obj.pose.bones[bname]
            pb.rotation_mode = 'XYZ'
            pb.rotation_euler = tuple(math.radians(a) for a in rot)
            pb.location = loc
            pb.keyframe_insert('rotation_euler', frame=f); pb.keyframe_insert('location', frame=f)
    act.frame_range = (1, frames)
    act.use_frame_range = True
    for fc in _fcurves(act):
        for kp in fc.keyframe_points: kp.interpolation = 'BEZIER'
        if loop:
            mod = fc.modifiers.new('CYCLES')
    act.use_fake_user = True
    return act


def push_nla(arm_obj, act):
    """Cada clip a una pista NLA (export FBX: 'All Actions' → clips separados con nombre)."""
    ad = arm_obj.animation_data
    tr = ad.nla_tracks.new(); tr.name = act.name
    tr.strips.new(act.name, int(act.frame_range[0]), act)
    ad.action = None


# ---------- export / evidencia ----------
def export_fbx(objs, asset_id, armature_obj=None, bake_anim=True):
    sel = list(objs) + ([armature_obj] if armature_obj else [])
    path = f"{FBX_DIR}/{asset_id}.fbx"
    with ctx(objs[0], sel): bpy.ops.export_scene.fbx(filepath=path, use_selection=True, apply_unit_scale=True, apply_scale_options='FBX_SCALE_ALL',
                             axis_forward='-Z', axis_up='Y', object_types={'MESH', 'ARMATURE'}, add_leaf_bones=False,
                             bake_space_transform=True, mesh_smooth_type='FACE', use_mesh_modifiers=True,
                             bake_anim=bake_anim and armature_obj is not None, bake_anim_use_all_actions=False, bake_anim_use_nla_strips=True,
                             bake_anim_use_all_bones=True, bake_anim_simplify_factor=0.0, path_mode='COPY', embed_textures=False)
    return path, os.path.getsize(path)


def save_blend(asset_id):
    path = f"{BLEND_DIR}/{asset_id}.blend"
    bpy.ops.wm.save_as_mainfile(filepath=path)
    return path


def sheet(asset_id, target_objs, size_hint=2.0, views=('front', 'side', 'iso'), res=640):
    """Hoja VIS de tres vistas con luz neutra (45.3 capturas de entrega)."""
    scene = bpy.context.scene
    try: scene.render.engine = 'BLENDER_EEVEE'
    except TypeError: pass
    scene.render.resolution_x = res; scene.render.resolution_y = res; scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    world = scene.world or bpy.data.worlds.new("World"); scene.world = world
    world.use_nodes = True
    bg = next(n for n in world.node_tree.nodes if n.type == 'BACKGROUND'); bg.inputs[0].default_value = (0.35, 0.35, 0.37, 1); bg.inputs[1].default_value = 1.0
    # centro/altura del asset
    mn = Vector((1e9, 1e9, 1e9)); mx = Vector((-1e9, -1e9, -1e9))
    for o in target_objs:
        for v in o.bound_box:
            w = o.matrix_world @ Vector(v)
            mn = Vector(map(min, mn, w)); mx = Vector(map(max, mx, w))
    center = (mn + mx) / 2; ext = max((mx - mn).length, 0.5)
    cam_data = bpy.data.cameras.new("CAM_sheet"); cam_data.lens = 50
    cam = bpy.data.objects.new("CAM_sheet", cam_data); scene.collection.objects.link(cam); scene.camera = cam
    key = bpy.data.lights.new("L_key", 'AREA'); key.energy = 400 * ext; key.size = 2
    ko = bpy.data.objects.new("L_key", key); scene.collection.objects.link(ko); ko.location = center + Vector((2, -2, 3)) * ext; ko.rotation_euler = (math.radians(40), 0, math.radians(45))
    fill = bpy.data.lights.new("L_fill", 'AREA'); fill.energy = 150 * ext; fill.size = 3
    fo = bpy.data.objects.new("L_fill", fill); scene.collection.objects.link(fo); fo.location = center + Vector((-2.5, -1.5, 2)) * ext; fo.rotation_euler = (math.radians(55), 0, math.radians(-55))
    paths = []
    dist = ext * 1.9
    for v in views:
        if v == 'front': pos = center + Vector((0, -dist, 0)); rot = (math.radians(90), 0, 0)
        elif v == 'side': pos = center + Vector((dist, 0, 0)); rot = (math.radians(90), 0, math.radians(90))
        elif v == 'back': pos = center + Vector((0, dist, 0)); rot = (math.radians(90), 0, math.radians(180))
        else: pos = center + Vector((dist * 0.7, -dist * 0.7, dist * 0.45)); rot = (math.radians(65), 0, math.radians(45))
        cam.location = pos; cam.rotation_euler = rot
        scene.render.filepath = f"{EVIDENCE}/{asset_id}_{v}.png"
        bpy.ops.render.render(write_still=True)
        paths.append(scene.render.filepath)
    for o in (cam, ko, fo): bpy.data.objects.remove(o)
    return paths


def report(asset_id, objs, extra=None):
    tris = 0
    for o in objs:
        o.data.calc_loop_triangles(); tris += len(o.data.loop_triangles)
    mn = Vector((1e9, 1e9, 1e9)); mx = Vector((-1e9, -1e9, -1e9))
    for o in objs:
        for v in o.bound_box:
            w = o.matrix_world @ Vector(v); mn = Vector(map(min, mn, w)); mx = Vector(map(max, mx, w))
    r = {"asset": asset_id, "tris": tris, "parts": len(objs), "dims_m": [round(x, 3) for x in (mx - mn)], "materials": sorted({m.name for o in objs for m in o.data.materials if m})}
    if extra: r.update(extra)
    with open(f"{EVIDENCE}/{asset_id}_report.json", "w", encoding="utf-8") as f: json.dump(r, f, indent=2)
    return r
