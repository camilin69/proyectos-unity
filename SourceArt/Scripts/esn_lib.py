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


# ---------- detalle mecánico (33.1 jerarquía de detalle, 36.4 ingeniería antes de rig, 39.2 coherencia de instalaciones) ----------
def chamfer(o, width=0.0015, segments=2, angle=45):
    """Chaflán por ángulo sobre toda la malla: ninguna arista queda viva (33.2).
    Se aplica como modificador y se consolida, así el bake y el FBX lo llevan incorporado."""
    m = o.modifiers.new("Chamfer", 'BEVEL')
    m.width = width; m.segments = segments
    m.limit_method = 'ANGLE'; m.angle_limit = math.radians(angle)
    m.miter_outer = 'MITER_ARC'
    m.use_clamp_overlap = True
    with ctx(o): bpy.ops.object.modifier_apply(modifier=m.name)
    return o


def bolt(name, radius, loc, col=None, axis='Z', head=None, kind='hex'):
    """Tornillo/remache con cabeza y ranura: la pieza pequeña que delata fabricación (39.2)."""
    h = head if head is not None else radius * 0.6
    segs = 6 if kind == 'hex' else 16
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segs, radius1=radius, radius2=radius * 0.96, depth=h)
    top = [v for v in bm.verts if v.co.z > h * 0.4]
    if top: bmesh.ops.bevel(bm, geom=top + [e for e in bm.edges if all(v in top for v in e.verts)], offset=radius * 0.18, segments=1, affect='EDGES')
    if axis == 'X': bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, 'Y'), verts=bm.verts)
    elif axis == 'Y': bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, 'X'), verts=bm.verts)
    o = _new(name, bm, col); o.location = loc
    return o


def bolt_row(name, radius, start, step, count, col=None, axis='Z', mat=None):
    """Fila de tornillos unida en una sola pieza."""
    parts = []
    for i in range(count):
        p = (start[0] + step[0] * i, start[1] + step[1] * i, start[2] + step[2] * i)
        b = bolt(f"{name}{i}", radius, p, col, axis=axis)
        if mat: assign(b, mat)
        parts.append(b)
    return join(parts, name) if len(parts) > 1 else parts[0]


def vent(name, size, loc, col=None, slats=5, rot=(0, 0, 0), depth=None, mat_frame=None, mat_slat=None):
    """Rejilla de ventilación: marco hundido + lamas inclinadas. Da sombra propia y rompe la superficie plana."""
    w, d, h = size
    dp = depth if depth is not None else d * 0.8
    parts = []
    frame = box(f"{name}_frame", (w, d * 0.35, h), (0, 0, 0), col, bevel=min(w, h) * 0.05)
    if mat_frame: assign(frame, mat_frame)
    parts.append(frame)
    step = h / (slats + 1)
    for i in range(slats):
        s = box(f"{name}_s{i}", (w * 0.86, dp, step * 0.42), (0, -d * 0.12, -h / 2 + step * (i + 1)), col, rot=(math.radians(28), 0, 0), bevel=step * 0.06)
        if mat_slat: assign(s, mat_slat)
        parts.append(s)
    g = join(parts, name)
    g.location = loc; g.rotation_euler = rot
    return g


def rib_row(name, length, size, loc, col=None, count=5, axis='Y', rot=(0, 0, 0), mat=None):
    """Nervios/refuerzos repetidos: lectura de chapa reforzada en vez de caja lisa."""
    parts = []
    for i in range(count):
        t = -length / 2 + length * (i + 0.5) / count
        off = (0, t, 0) if axis == 'Y' else ((t, 0, 0) if axis == 'X' else (0, 0, t))
        r = box(f"{name}{i}", size, off, col, bevel=min(size) * 0.3, segs=2)
        if mat: assign(r, mat)
        parts.append(r)
    g = join(parts, name); g.location = loc; g.rotation_euler = rot
    return g


def recess(name, size, loc, col=None, depth=None, rot=(0, 0, 0), mat=None, border=None):
    """Panel hundido con reborde: junta real que el AO ensombrece (41.3)."""
    w, d, h = size
    dp = depth if depth is not None else d * 0.5
    parts = []
    b = border if border is not None else min(w, h) * 0.08
    ring = []
    for dx, dz, sw, sh in ((0, (h - b) / 2, w, b), (0, -(h - b) / 2, w, b), ((w - b) / 2, 0, b, h - 2 * b), (-(w - b) / 2, 0, b, h - 2 * b)):
        ring.append(box(f"{name}_b{len(ring)}", (sw, d, sh), (dx, 0, dz), col, bevel=b * 0.25))
    inner = box(f"{name}_in", (w - 2 * b, d - dp, h - 2 * b), (0, dp / 2, 0), col, bevel=b * 0.2)
    parts = ring + [inner]
    if mat:
        for p in parts: assign(p, mat)
    g = join(parts, name); g.location = loc; g.rotation_euler = rot
    return g


def panel_seam(name, length, loc, col=None, axis='Y', width=0.004, depth=0.003, mat=None):
    """Junta entre paneles: tira fina hundida. Barata en triángulos, cara en lectura."""
    size = (width, length, depth) if axis == 'Y' else ((length, width, depth) if axis == 'X' else (width, depth, length))
    s = box(name, size, loc, col, bevel=width * 0.3)
    if mat: assign(s, mat)
    return s


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


def material(name, base=(0.5, 0.5, 0.5), rough=0.5, metal=0.0, wear=0.0, wear_color=(0.35, 0.2, 0.12), bump=0.0, scale=8.0, emission=None,
             bevel=0.0025, edge_wear=None, edge_color=None, ao=0.85, ao_dist=0.06):
    """Material PBR de acabado (40/41).

    Además del ruido de superficie, tres capas dependientes de la geometría que SÍ se hornean a los mapas:
      · Bevel node  → redondea el sombreado de toda arista viva; sin esto un objeto lee como "primitiva pintada" (33.2).
      · Pointiness  → desgaste por causa (41.3): la pintura se va en las aristas convexas y asoma el metal, no ruido uniforme.
      · AO          → oscurece cavidades y juntas; se multiplica en BaseColor para dar lectura de volumen.
    edge_wear: 0..1 intensidad del desgaste de arista (por defecto deriva de `wear`). edge_color: color bajo la pintura.
    """
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

    # --- roughness: variación por ruido (mantiene el comportamiento anterior) ---
    tex = nt.nodes.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value = scale; tex.inputs['Detail'].default_value = 6
    ramp = nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].position = 0.35; ramp.color_ramp.elements[1].position = 0.65
    ramp.color_ramp.elements[0].color = (max(0, rough - 0.12),) * 3 + (1,); ramp.color_ramp.elements[1].color = (min(1, rough + 0.12),) * 3 + (1,)
    nt.links.new(tex.outputs['Fac'], ramp.inputs['Fac'])
    rough_out = ramp.outputs['Color']

    # --- color: desgaste por ruido (manchas) ---
    color_out = None
    wear_mask = None
    if wear > 0:
        wtex = nt.nodes.new('ShaderNodeTexNoise'); wtex.inputs['Scale'].default_value = scale * 1.7; wtex.inputs['Detail'].default_value = 8
        wramp = nt.nodes.new('ShaderNodeValToRGB'); wramp.color_ramp.elements[0].position = 0.62 - wear * 0.25; wramp.color_ramp.elements[1].position = 0.75
        mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'
        mix.inputs[6].default_value = (*base, 1); mix.inputs[7].default_value = (*wear_color, 1)
        nt.links.new(wtex.outputs['Fac'], wramp.inputs['Fac']); nt.links.new(wramp.outputs['Color'], mix.inputs[0])
        color_out = mix.outputs[2]; wear_mask = wramp.outputs['Color']

    # --- 41.3 desgaste POR CAUSA: aristas convexas (Pointiness) pierden pintura ---
    ew = edge_wear if edge_wear is not None else min(1.0, 0.25 + wear)
    if ew > 0:
        geo = nt.nodes.new('ShaderNodeNewGeometry')
        pramp = nt.nodes.new('ShaderNodeValToRGB')
        # ventana estrecha justo por encima de 0.5 = solo las aristas realmente convexas
        pramp.color_ramp.elements[0].position = 0.515
        pramp.color_ramp.elements[1].position = 0.515 + max(0.02, 0.10 * (1.0 - ew))
        nt.links.new(geo.outputs['Pointiness'], pramp.inputs['Fac'])
        emix = nt.nodes.new('ShaderNodeMix'); emix.data_type = 'RGBA'
        ecol = edge_color if edge_color is not None else ((0.62, 0.60, 0.56) if metal < 0.5 else tuple(min(1, c * 1.35 + 0.08) for c in base))
        if color_out: nt.links.new(color_out, emix.inputs[6])
        else: emix.inputs[6].default_value = (*base, 1)
        emix.inputs[7].default_value = (*ecol, 1)
        fac = nt.nodes.new('ShaderNodeMath'); fac.operation = 'MULTIPLY'; fac.inputs[1].default_value = ew
        nt.links.new(pramp.outputs['Color'], fac.inputs[0]); nt.links.new(fac.outputs[0], emix.inputs[0])
        color_out = emix.outputs[2]
        # el metal desnudo de la arista es más liso que la pintura mate
        rmix = nt.nodes.new('ShaderNodeMix'); rmix.data_type = 'FLOAT'
        nt.links.new(rough_out, rmix.inputs[2]); rmix.inputs[3].default_value = max(0.05, rough - 0.28)
        nt.links.new(fac.outputs[0], rmix.inputs[0])
        rough_out = rmix.outputs[0]
        if metal > 0.5 and wear_mask is not None:
            mm = nt.nodes.new('ShaderNodeMath'); mm.operation = 'SUBTRACT'; mm.inputs[0].default_value = metal
            nt.links.new(wear_mask, mm.inputs[1]); nt.links.new(mm.outputs[0], p.inputs['Metallic'])

    # --- AO de cavidad multiplicado en el color (lectura de volumen sin luz) ---
    if ao > 0:
        aon = nt.nodes.new('ShaderNodeAmbientOcclusion'); aon.samples = 8; aon.inputs['Distance'].default_value = ao_dist
        amix = nt.nodes.new('ShaderNodeMix'); amix.data_type = 'RGBA'; amix.blend_type = 'MULTIPLY'; amix.inputs[0].default_value = ao
        if color_out: nt.links.new(color_out, amix.inputs[6])
        else: amix.inputs[6].default_value = (*base, 1)
        nt.links.new(aon.outputs['Color'], amix.inputs[7])
        color_out = amix.outputs[2]

    if color_out: nt.links.new(color_out, p.inputs['Base Color'])
    nt.links.new(rough_out, p.inputs['Roughness'])

    # --- normal: micro-relieve de material + Bevel de arista (33.2) ---
    normal_out = None
    if bump > 0:
        btex = nt.nodes.new('ShaderNodeTexNoise'); btex.inputs['Scale'].default_value = scale * 6; btex.inputs['Detail'].default_value = 10
        bn = nt.nodes.new('ShaderNodeBump'); bn.inputs['Strength'].default_value = bump; bn.inputs['Distance'].default_value = 0.01
        nt.links.new(btex.outputs['Fac'], bn.inputs['Height'])
        normal_out = bn.outputs['Normal']
    if bevel > 0:
        bev = nt.nodes.new('ShaderNodeBevel'); bev.samples = 8; bev.inputs['Radius'].default_value = bevel
        if normal_out: nt.links.new(normal_out, bev.inputs['Normal'])
        normal_out = bev.outputs['Normal']
    if normal_out: nt.links.new(normal_out, p.inputs['Normal'])

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


def bake_pbr(objs, asset_id, size=1024, samples=48, only=None):
    """Hornea BaseColor/Roughness/Metallic/Normal a un atlas por asset (UV compartida, 40.3/41.1).

    Las capas dependientes de geometría (Bevel, Pointiness, AO) se resuelven por muestreo: con pocas muestras
    el AO sale con grano. 48 muestras + denoise dan un atlas limpio sin disparar el tiempo de horneado.
    """
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = samples; scene.cycles.use_denoising = True
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


# 49.2/60.2 · ciclos de marcha con pose de paso
#
# Los ciclos originales tenían dos poses opuestas (pierna izquierda adelante / pierna derecha adelante) y nada en
# medio. Interpolar entre ellas hace pasar la pierna en vuelo por la vertical, que es exactamente donde el pie queda
# MÁS BAJO, así que el pie no despega: medido, 7.3 mm de despeje en el Vigía y 7.9 mm en el Custodio para piernas de
# 0.70 y 0.98 m. Eso no es caminar, es arrastrar los pies.
#
# Una marcha necesita como mínimo cuatro poses por pierna: contacto, apoyo medio, despegue y PASO (la rodilla doblada
# que sube el pie). Aquí se generan `keys` poses por ciclo a partir de la fase de cada pierna, con dos decisiones
# medidas sobre el rig y no supuestas:
#   · signo de rodilla: rotación X NEGATIVA en `shin` lleva el talón hacia atrás y sube el pie (comprobado: muslo -25°
#     con rodilla -45° deja el pie a +155 mm; con +45° lo deja a +19 mm, porque hiperextiende en vez de doblar).
#   · el pie se mantiene paralelo al suelo restando la suma de la cadena: los tres huesos de la pierna giran sobre X.
# Durante el APOYO el muslo se calcula por arcoseno para que el pie retroceda a velocidad uniforme: el gate G-02 mide
# justo esa dispersión, y una interpolación suave del ángulo produce un retroceso que acelera y frena (patinaje).
# `frames` fija la cadencia y con ella la velocidad implícita del clip, que G-04 compara contra la velocidad del
# dato (Vigía patrulla 0.7 m/s, Custodio 0.6, Archivista se aproxima a 1.6). Se ajusta aquí y en ningún otro sitio.
WALK_PRESETS = {
    "BOT-01_Vigia":      dict(frames=36, stride_deg=22, leg_reach=0.99, clearance=0.14,
                              arm_swing=15, spine_pitch=6, spine_sway=4, head_yaw=6, head_lag=0.18),
    "BOT-02_Custodio":   dict(frames=64, stride_deg=20, leg_reach=0.99, clearance=0.11,
                              arm_swing=12, spine_pitch=4, spine_sway=3, head_yaw=4, head_lag=0.22),
    "BOT-03_Archivista": dict(frames=42, stride_deg=26, leg_reach=0.99, clearance=0.13,
                              arm_swing=10, spine_pitch=5, spine_sway=3, head_yaw=3, head_lag=0.25),
}


def _bump(u, peak, height):
    """Campana suave: vale 0 en u=0 y u=1, y `height` en u=`peak`."""
    if u <= 0.0 or u >= 1.0 or height == 0.0:
        return 0.0
    x = u / (2.0 * peak) if u < peak else 0.5 + (u - peak) / (2.0 * (1.0 - peak))
    return height * math.sin(math.pi * x)


def walk_cycle(arm_obj, name, frames, stride_deg=22.0, leg_reach=0.99, clearance=0.12,
               arm_swing=14.0, spine_pitch=5.0, spine_sway=4.0,
               head_yaw=5.0, head_lag=0.2, keys=None, fps=30, extra=None):
    """Ciclo de marcha in-place para el rig estándar (root/pelvis/spine/head + thigh/shin/foot por lado).

    No se escriben ángulos de muslo y rodilla: se escribe la TRAYECTORIA DEL PIE y la pierna se resuelve por
    cinemática inversa de dos eslabones. Escribir los ángulos a mano falla por un motivo geométrico que no se ve
    hasta medirlo: con la rodilla a medio flexionar la tibia queda casi vertical y la pierna ALCANZA MÁS ABAJO que
    en la pose de contacto, así que el pie en vuelo toca el suelo antes de terminar el paso y se arrastra hacia
    delante hasta el contacto (medido: 216 mm de avance con el pie ya apoyado, y 169 mm después de retrasar la
    extensión de la rodilla). Con la trayectoria impuesta el problema desaparece por construcción.

    Modelo:
      · APOYO — la pierna de apoyo es un puntal rígido de longitud `leg_reach`·(muslo+tibia) que gira sobre el pie.
        El ángulo se calcula por arcoseno para que el pie retroceda a velocidad EXACTAMENTE uniforme (es lo que
        mide G-02), y el balanceo de la cadera sale solo, como consecuencia del giro del puntal.
      · VUELO — la cadera está a la altura que le impone la pierna contraria, así que la altura del pie sobre el
        suelo se puede imponer: sube `clearance` a media zancada y vuelve a cero justo en el contacto. En los dos
        extremos la trayectoria coincide con la del apoyo, así que el ciclo empalma sin salto.
    La altura absoluta del cuerpo NO se keyea aquí: la resuelve `foot_lock` midiendo el pie de apoyo.
    """
    z0 = (0.0, 0.0, 0.0)
    # Una clave por frame. Con menos claves las poses caen en frames desigualmente espaciados (36 frames en 16
    # claves dan huecos de 2 y de 3) y el muslo avanza a ritmos distintos aunque el ángulo esté bien calculado:
    # medido, hasta un 50 % de variación en la velocidad del pie apoyado por pura rejilla de claves.
    keys = keys if keys else max(2, frames - 1)
    bones = arm_obj.data.bones
    a = bones["thigh_L"].length
    b = bones["shin_L"].length
    reach = leg_reach * (a + b)          # longitud del puntal de apoyo
    lift_m = clearance * (a + b)         # despeje del pie a media zancada
    sin_s = math.sin(math.radians(stride_deg))

    def ik(y, d):
        """(muslo, tibia) en grados para poner el tobillo en (adelante=y, bajada=d) respecto de la cadera."""
        r = math.hypot(y, d)
        r = min(r, (a + b) * 0.999)
        cos_knee = max(-1.0, min(1.0, (r * r - a * a - b * b) / (2.0 * a * b)))
        shin = -math.acos(cos_knee)                       # negativa: el talón va hacia atrás (signo medido)
        leg_angle = math.atan2(y, d)
        offset = math.atan2(b * math.sin(shin), a + b * math.cos(shin))
        return math.degrees(leg_angle - offset), math.degrees(shin)

    def leg(p):
        """(muslo, tibia) en grados para la fase p de esa pierna: [0, 0.5) apoyo, [0.5, 1) vuelo."""
        p %= 1.0
        if p < 0.5:
            u = p / 0.5
            sin_a = sin_s * (1.0 - 2.0 * u)               # lineal en u => retroceso uniforme del pie
            ang = math.asin(sin_a)
            return ik(reach * sin_a, reach * math.cos(ang))
        u = (p - 0.5) / 0.5
        hip_drop = reach * math.cos(math.asin(sin_s * (1.0 - 2.0 * u)))   # altura que impone la pierna contraria
        eased = 0.5 - 0.5 * math.cos(math.pi * u)                        # llega al contacto frenando
        return ik(reach * sin_s * (-1.0 + 2.0 * eased), hip_drop - _bump(u, 0.45, lift_m))

    poses = {}
    for i in range(keys + 1):
        t = i / float(keys)
        f = 1 + int(round(t * (frames - 1)))
        th_l, sh_l = leg(t)
        th_r, sh_r = leg(t + 0.5)
        bones = {
            "thigh_L": ((th_l, 0, 0), z0), "shin_L": ((sh_l, 0, 0), z0),
            "thigh_R": ((th_r, 0, 0), z0), "shin_R": ((sh_r, 0, 0), z0),
            "foot_L": ((-(th_l + sh_l), 0, 0), z0), "foot_R": ((-(th_r + sh_r), 0, 0), z0),
            # los brazos van a contrafase de la pierna del mismo lado (t=0 es el contacto de la pierna izquierda)
            "upperarm_L": ((-arm_swing * math.cos(2 * math.pi * t), 0, 0), z0),
            "upperarm_R": ((arm_swing * math.cos(2 * math.pi * t), 0, 0), z0),
            "spine": ((spine_pitch, 0, spine_sway * math.cos(2 * math.pi * t)), z0),
        }
        if head_yaw and "head" in arm_obj.pose.bones:
            bones["head"] = ((-spine_pitch * 0.5, 0, head_yaw * math.cos(2 * math.pi * (t - head_lag))), z0)
        poses[f] = bones
    for t, extra_bones in (extra or {}).items():
        poses.setdefault(1 + int(round(t * (frames - 1))), {}).update(extra_bones)

    act = action(arm_obj, name, frames, fps=fps, poses=poses, loop=True)
    # El muslo marca el retroceso del pie apoyado. Con handles Bézier ese retroceso acelera y frena entre poses y el
    # pie patina; en el muslo la interpolación tiene que ser lineal para que G-02 mida un deslizamiento uniforme.
    for fc in _fcurves(act):
        if "thigh_" in fc.data_path and fc.data_path.endswith("rotation_euler") and fc.array_index == 0:
            for kp in fc.keyframe_points:
                kp.interpolation = 'LINEAR'
    return act


def _names(seq):
    """Acepta indistintamente objetos de Blender o sus nombres.

    `foot_lock` y `ground_clamp` filtraban por nombre y, al pasarles objetos, no encontraban nada y devolvían una
    lista vacía SIN AVISAR: el clip quedaba sin corregir y el gate posterior medía otra cosa. Un no-op silencioso en
    un paso de corrección es peor que un error, porque se reporta como hecho.
    """
    return [s if isinstance(s, str) else getattr(s, "name", str(s)) for s in (seq or [])]


def ground_clamp(arm_obj, meshes, actions=None, root_bone="root", floor=0.0, report=None):
    """49.8: ningún frame puede hundir la malla bajo el suelo.

    Los clips de muerte bajan el hueso raíz una cantidad escrita a ojo, y la silueta tumbada acaba enterrada
    (medido: Vigía −361 mm, Custodio −600 mm, Archivista −876 mm). En vez de inventar otro número, se mide la
    penetración real por frame y se sube el raíz exactamente lo necesario.

    El desplazamiento se aplica en el espacio LOCAL del hueso (que no coincide con el mundo), resolviendo qué
    vector local produce un metro de subida en Z mundial.
    """
    if arm_obj is None or arm_obj.animation_data is None: return []
    ad = arm_obj.animation_data
    saved_action, saved_nla = ad.action, ad.use_nla
    ad.use_nla = False
    pb = arm_obj.pose.bones.get(root_bone)
    if pb is None: ad.action, ad.use_nla = saved_action, saved_nla; return []
    # vector local del hueso que equivale a +Z mundial
    basis = (arm_obj.matrix_world @ pb.bone.matrix_local).to_3x3()
    try: up_local = basis.inverted() @ Vector((0.0, 0.0, 1.0))
    except ValueError: up_local = Vector((0.0, 1.0, 0.0))

    tracks = [(s.action.name, s.action) for t in ad.nla_tracks for s in t.strips if s.action]
    wanted = _names(actions)
    out = []
    for missing in [w for w in wanted if w not in [n for n, _ in tracks]]:
        out.append((missing, "SIN PISTA NLA"))
    for name, act in tracks:
        if wanted and name not in wanted: continue
        ad.action = act
        f0, f1 = int(act.frame_range[0]), int(act.frame_range[1])
        worst = 1e9
        for f in range(f0, f1 + 1):
            bpy.context.scene.frame_set(f)
            dg = bpy.context.evaluated_depsgraph_get()
            for o in meshes:
                ev = o.evaluated_get(dg); me = ev.to_mesh()
                if me.vertices:
                    mw = ev.matrix_world
                    worst = min(worst, min((mw @ v.co).z for v in me.vertices))
                ev.to_mesh_clear()
        pen = worst - floor
        if pen >= -0.002: out.append((name, 0.0)); continue
        delta = up_local * (-pen)
        for fc in _fcurves(act):
            if fc.data_path.endswith("location") and root_bone in fc.data_path:
                d = delta[fc.array_index]
                if abs(d) < 1e-9: continue
                for kp in fc.keyframe_points:
                    kp.co.y += d; kp.handle_left.y += d; kp.handle_right.y += d
        out.append((name, round(-pen, 4)))
    ad.action, ad.use_nla = saved_action, saved_nla
    bpy.context.scene.frame_set(1)
    if report is not None: report.extend(out)
    return out


def foot_lock(arm_obj, meshes, feet, actions, root_bone="root", floor=0.0, max_lift=0.25):
    """49.8: el pie de apoyo toca el suelo en todo el ciclo, en vez de flotar.

    Los ciclos procedurales mantienen la pelvis a altura constante mientras las piernas rotan, así que cuando la
    pierna se flexiona el pie se despega (medido: sólo el 52 % de los frames del Custodio tenían algún pie apoyado,
    contra el 85 % exigido). Aquí no se inventa un balanceo: para cada frame se mide cuál es el pie más bajo y se
    baja el raíz exactamente lo necesario para que toque. El bob vertical natural sale solo de esa corrección.
    """
    if arm_obj is None or arm_obj.animation_data is None: return []
    ad = arm_obj.animation_data
    saved_action, saved_nla = ad.action, ad.use_nla
    ad.use_nla = False
    pb = arm_obj.pose.bones.get(root_bone)
    if pb is None: ad.action, ad.use_nla = saved_action, saved_nla; return []
    basis = (arm_obj.matrix_world @ pb.bone.matrix_local).to_3x3()
    try: up_local = basis.inverted() @ Vector((0.0, 0.0, 1.0))
    except ValueError: up_local = Vector((0.0, 1.0, 0.0))
    feet_names = _names(feet)
    foot_objs = [o for o in meshes if o.name in feet_names]
    if not foot_objs:
        ad.action, ad.use_nla = saved_action, saved_nla
        raise ValueError("foot_lock: ninguna malla de la escena coincide con %s" % feet_names)

    def reset_pose():
        # Si un clip no keyea el raíz, `pb.location` conserva el valor que dejó el clip anterior (p. ej. el descenso
        # del clip de muerte) y se estaría midiendo una pose heredada. Hay que partir de identidad.
        for b in arm_obj.pose.bones:
            b.location = (0.0, 0.0, 0.0); b.rotation_euler = (0.0, 0.0, 0.0)
            b.rotation_quaternion = (1.0, 0.0, 0.0, 0.0); b.scale = (1.0, 1.0, 1.0)
        bpy.context.view_layer.update()

    out = []
    for name in _names(actions):
        act = bpy.data.actions.get(name)
        if act is None:
            out.append((name, "SIN ACCION"))
            continue
        # partir de cero: se elimina cualquier curva de traslación del raíz previa en este clip para no acumular
        for fc in list(_fcurves(act)):
            if fc.data_path.endswith("location") and root_bone in fc.data_path:
                try: act.fcurves.remove(fc)
                except Exception:
                    for layer in act.layers:
                        for strip in layer.strips:
                            for cb in strip.channelbags:
                                if fc in list(cb.fcurves): cb.fcurves.remove(fc)
        reset_pose()
        ad.action = act
        f0, f1 = int(act.frame_range[0]), int(act.frame_range[1])
        plan = []
        for f in range(f0, f1 + 1):
            bpy.context.scene.frame_set(f)
            dg = bpy.context.evaluated_depsgraph_get()
            lowest = 1e9
            for o in foot_objs:
                ev = o.evaluated_get(dg); me = ev.to_mesh()
                if me.vertices:
                    mw = ev.matrix_world
                    lowest = min(lowest, min((mw @ v.co).z for v in me.vertices))
                ev.to_mesh_clear()
            if lowest > 1e8: continue
            delta = floor - lowest
            if abs(delta) > max_lift:
                out.append((name, "CLAMP", round(delta, 4)))   # no callar un recorte: delataría un rig mal escalado
                delta = math.copysign(max_lift, delta)
            plan.append((f, pb.location.copy() + up_local * delta, delta))
        # segunda pasada: escribir las claves ya calculadas (escribirlas mientras se mide falsearía la medición)
        for f, loc, _ in plan:
            bpy.context.scene.frame_set(f)
            pb.location = loc
            pb.keyframe_insert("location", frame=f)
        rng = [d for _, _, d in plan]
        out.append((name, round(min(rng), 4), round(max(rng), 4)))
    ad.action, ad.use_nla = saved_action, saved_nla
    bpy.context.scene.frame_set(1)
    return out


def push_nla(arm_obj, act):
    """Cada clip a una pista NLA (export FBX: 'All Actions' → clips separados con nombre)."""
    ad = arm_obj.animation_data
    tr = ad.nla_tracks.new(); tr.name = act.name
    tr.strips.new(act.name, int(act.frame_range[0]), act)
    ad.action = None


# ---------- export / evidencia ----------
def enable_nla(armature_obj):
    """Deja el stack NLA activo y sin pistas silenciadas, que es como tiene que quedar un asset con clips."""
    ad = getattr(armature_obj, "animation_data", None)
    if ad is None:
        return False
    ad.action = None            # la acción activa se sumaría encima de cada tira al exportar
    ad.use_nla = True
    for t in ad.nla_tracks:
        t.mute = False
    return True


def export_fbx(objs, asset_id, armature_obj=None, bake_anim=True):
    sel = list(objs) + ([armature_obj] if armature_obj else [])
    path = f"{FBX_DIR}/{asset_id}.fbx"
    # El exportador saca un clip por tira NLA, pero las EVALÚA a través del stack. Si `use_nla` está apagado —y lo
    # apagan el medidor de contactos, ground_clamp y foot_lock para poder leer un clip aislado— cada take sale con
    # el nombre y la duración correctos y con la POSE DE REPOSO repetida en todos los frames. Medido en Unity:
    # 36 claves por curva y CERO curvas que cambien de valor, es decir enemigos que no animan aunque el .blend sí.
    if bake_anim and armature_obj is not None:
        enable_nla(armature_obj)
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
