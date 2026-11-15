# SUENO LUCIDO - el sonador: figura blanca sin rostro, de tela, con esqueleto Humanoid de Unity.
#
# El cuerpo sale de un grafo de articulaciones con Skin modifier + Subdivision: da una figura organica con
# anillos de aristas en cada articulacion, que es lo que necesita una malla para deformarse sin pellizcarse.
# El esqueleto se construye con las MISMAS articulaciones, asi que hueso y malla no pueden desalinearse.
# Convencion: Z arriba, el personaje mira a -Y, su izquierda es +X, pose A (brazos a 40 grados), 1.70 m.
import bpy, bmesh, math
from mathutils import Vector

OUT_BLEND = r"C:/Users/HP/Documents/GitHub/proyectos-unity/SourceArt/TallerFinal/SN-01_Sonador.blend"

J = {
    "Hips": (0, 0.0, 0.95), "Spine": (0, 0.005, 1.06), "Chest": (0, 0.01, 1.22), "UpperChest": (0, 0.01, 1.33),
    "Neck": (0, 0.0, 1.45), "Head": (0, -0.005, 1.53), "HeadTop": (0, 0.0, 1.71),
}
for side, sx in (("Left", 1), ("Right", -1)):
    J.update({
        side + "Shoulder": (sx * 0.035, 0.0, 1.405), side + "UpperArm": (sx * 0.17, 0.0, 1.40),
        # pose A: brazos 40 grados abajo. La tela se simula y se pesa en esta pose; asi el velo cae sobre los
        # hombros y no queda apoyado en unos brazos en T que luego bajan y lo dejan flotando.
        side + "LowerArm": (sx * (0.17 + 0.2107), 0.0, 1.40 - 0.1768),
        side + "Hand": (sx * (0.17 + 0.4060), 0.0, 1.40 - 0.3407),
        side + "HandEnd": (sx * (0.17 + 0.5286), 0.0, 1.40 - 0.4436),
        side + "UpperLeg": (sx * 0.095, 0.0, 0.92), side + "LowerLeg": (sx * 0.10, 0.0, 0.50),
        side + "Foot": (sx * 0.10, 0.025, 0.085), side + "Toes": (sx * 0.10, -0.115, 0.022),
        side + "ToeEnd": (sx * 0.10, -0.20, 0.02),
    })

# radios (x, y) por articulacion: figura esbelta, hombros suaves, sin rasgos marcados
R = {"Hips": (0.16, 0.11), "Spine": (0.13, 0.095), "Chest": (0.158, 0.108), "UpperChest": (0.17, 0.10),
     "Neck": (0.048, 0.05), "Head": (0.068, 0.075), "HeadTop": (0.042, 0.046)}
for side in ("Left", "Right"):
    R.update({side + "Shoulder": (0.062, 0.062), side + "UpperArm": (0.055, 0.056), side + "LowerArm": (0.036, 0.038),
              side + "Hand": (0.024, 0.032), side + "HandEnd": (0.012, 0.026),
              side + "UpperLeg": (0.092, 0.095), side + "LowerLeg": (0.05, 0.052), side + "Foot": (0.033, 0.036),
              side + "Toes": (0.04, 0.026), side + "ToeEnd": (0.028, 0.016)})

J["HeadMid"] = (0, -0.012, 1.615); R["HeadMid"] = (0.084, 0.096)
# (Se probaron nariz, barbilla y ceja bajo el velo: la tela se engancha en ellas y se amontona en un volante.
#  El rostro adivinado se sugiere con el mapa de normales de la tela, no con geometria.)
for side, sx in (("Left", 1), ("Right", -1)):
    J[side + "Heel"] = (sx * 0.10, 0.06, 0.035); R[side + "Heel"] = (0.032, 0.03)
    J[side + "Thumb"] = (sx * 0.60, -0.045, 1.035); R[side + "Thumb"] = (0.013, 0.013)
EDGES = [("Hips", "Spine"), ("Spine", "Chest"), ("Chest", "UpperChest"), ("UpperChest", "Neck"), ("Neck", "Head"),
         ("Head", "HeadMid"), ("HeadMid", "HeadTop")]
for s in ("Left", "Right"):
    EDGES += [("UpperChest", s + "Shoulder"), (s + "Shoulder", s + "UpperArm"), (s + "UpperArm", s + "LowerArm"),
              (s + "LowerArm", s + "Hand"), (s + "Hand", s + "HandEnd"),
              ("Hips", s + "UpperLeg"), (s + "UpperLeg", s + "LowerLeg"), (s + "LowerLeg", s + "Foot"),
              (s + "Foot", s + "Toes"), (s + "Toes", s + "ToeEnd"), (s + "Foot", s + "Heel"), (s + "Hand", s + "Thumb")]

LONG = {"UpperArm", "LowerArm", "UpperLeg", "LowerLeg"}

# Nodos de forma entre articulaciones: dan anatomia (muslo, rodilla, gemelo, tobillo, codo, antebrazo,
# muneca) sin crear huesos nuevos. Cada entrada: (t a lo largo del segmento, (rx, ry), desplazamiento).
SHAPE = {
    "UpperLeg": [(0.35, (0.083, 0.088), (0, -0.006, 0)), (0.75, (0.064, 0.066), (0, 0.0, 0)), (0.95, (0.052, 0.054), (0, -0.008, 0))],
    "LowerLeg": [(0.25, (0.058, 0.062), (0, 0.012, 0)), (0.55, (0.046, 0.05), (0, 0.006, 0)), (0.88, (0.031, 0.033), (0, 0.0, 0))],
    "UpperArm": [(0.3, (0.05, 0.052), (0, 0, 0)), (0.85, (0.037, 0.04), (0, 0, 0))],
    "LowerArm": [(0.25, (0.041, 0.043), (0, 0, 0)), (0.85, (0.027, 0.03), (0, 0, 0))],
    "Hand":     [(0.45, (0.022, 0.044), (0, 0, 0))],
}


def ctx(o=None, objs=None):
    """Contexto de ventana para operadores llamados por el socket MCP, que no tiene area activa."""
    win = bpy.context.window_manager.windows[0]
    area = next(a for a in win.screen.areas if a.type == 'VIEW_3D') if any(a.type == 'VIEW_3D' for a in win.screen.areas) else win.screen.areas[0]
    if area.type != 'VIEW_3D':
        area.type = 'VIEW_3D'
    region = next(r for r in area.regions if r.type == 'WINDOW')
    sel = objs if objs is not None else ([o] if o else [])
    for ob in bpy.context.scene.objects:
        ob.select_set(False)
    for ob in sel:
        ob.select_set(True)
    act = o or (sel[0] if sel else None)
    if act is not None:
        bpy.context.view_layer.objects.active = act
    return bpy.context.temp_override(window=win, screen=win.screen, area=area, region=region,
                                     active_object=act, object=act, selected_objects=sel,
                                     selected_editable_objects=sel, view_layer=bpy.context.view_layer,
                                     scene=bpy.context.scene)


def lerp(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def build_body():
    me = bpy.data.meshes.new("Body")
    ob = bpy.data.objects.new("SN_Body", me)
    bpy.context.scene.collection.objects.link(ob)
    bm = bmesh.new()
    names = list(J.keys())
    idx = {n: bm.verts.new(Vector(J[n])) for n in names}
    extra = []
    for a, b in EDGES:
        seg = a.replace("Left", "").replace("Right", "")
        nodes = SHAPE.get(seg) if b.replace("Left", "").replace("Right", "") not in ("Thumb", "Heel") else None
        if nodes:
            prev = idx[a]
            for tt, rr, off in nodes:
                p = Vector(lerp(J[a], J[b], tt)) + Vector(off)
                mv = bm.verts.new(p)
                extra.append(rr)
                bm.edges.new((prev, mv)); prev = mv
            bm.edges.new((prev, idx[b]))
        else:
            bm.edges.new((idx[a], idx[b]))
    bm.to_mesh(me); bm.free()
    mod = ob.modifiers.new("Skin", 'SKIN')
    mod.use_smooth_shade = True
    sk = me.skin_vertices[0].data
    for i, n in enumerate(names):
        sk[i].radius = R[n]
    for k, r in enumerate(extra):
        sk[len(names) + k].radius = r
    sk[names.index("Hips")].use_root = True
    sub = ob.modifiers.new("Subsurf", 'SUBSURF'); sub.levels = 2; sub.render_levels = 2
    with ctx(ob):
        bpy.ops.object.modifier_apply(modifier="Skin")
        bpy.ops.object.modifier_apply(modifier="Subsurf")
        bpy.ops.object.shade_smooth()
    return ob


def grid_object(name, size_x, size_y, nx, ny):
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=nx, y_segments=ny, size=0.5)
    for v in bm.verts:
        v.co.x *= size_x; v.co.y *= size_y
    bm.to_mesh(me); bm.free()
    return ob


def simulate(cloth_objs, collider, frames):
    """Deja caer la tela sobre el cuerpo y congela el ultimo frame: los pliegues salen de la fisica."""
    col = collider.modifiers.new("Collision", 'COLLISION')
    collider.collision.thickness_outer = 0.004
    collider.collision.cloth_friction = 12.0
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 1, frames
    for o in cloth_objs:
        m = o.modifiers.new("Cloth", 'CLOTH')
        s = m.settings
        s.quality = 8; s.mass = 0.18; s.air_damping = 2.0
        s.tension_stiffness = 12; s.compression_stiffness = 12; s.shear_stiffness = 6; s.bending_stiffness = 0.25
        s.vertex_group_mass = "pin"
        m.collision_settings.use_self_collision = True
        m.collision_settings.self_distance_min = 0.003
        m.collision_settings.distance_min = 0.004
        m.point_cache.frame_start, m.point_cache.frame_end = 1, frames
    for f in range(1, frames + 1):
        sc.frame_set(f)
    for o in cloth_objs:
        with ctx(o):
            bpy.ops.object.modifier_apply(modifier="Cloth")
    collider.modifiers.remove(col)
    sc.frame_set(1)


def pin(ob, test):
    g = ob.vertex_groups.new(name="pin")
    ids = [v.index for v in ob.data.vertices if test(ob.matrix_world @ v.co)]
    g.add(ids, 1.0, 'REPLACE')
    return len(ids)


def build_cloth(body):
    """Velo sobre la cabeza (Magritte, Los amantes) y capa fruncida en los hombros, simulados sobre el cuerpo."""
    # Velo: disco polar de quads (anillos concentricos). Un cuadrado deja dos esquinas colgando como lenguas y
    # un borde en escalera; un disco cae parejo alrededor de la cabeza, como un sudario.
    veil = bpy.data.objects.new("SN_Veil", bpy.data.meshes.new("Veil"))
    bpy.context.scene.collection.objects.link(veil)
    bm = bmesh.new()
    segs, rings, radius = 96, 34, 0.50
    centre = bm.verts.new((0, 0, 0))
    rows = []
    for r in range(1, rings + 1):
        rr = radius * (r / rings)
        rows.append([bm.verts.new((rr * math.cos(2 * math.pi * k / segs), rr * math.sin(2 * math.pi * k / segs), 0))
                     for k in range(segs)])
    for k in range(segs):
        bm.faces.new((centre, rows[0][k], rows[0][(k + 1) % segs]))
    for r in range(rings - 1):
        for k in range(segs):
            bm.faces.new((rows[r][k], rows[r + 1][k], rows[r + 1][(k + 1) % segs], rows[r][(k + 1) % segs]))
    bm.to_mesh(veil.data); bm.free()
    veil.location = (0, -0.008, J["HeadTop"][2] + 0.012)
    bpy.context.view_layer.update()
    pin(veil, lambda w: ((w.x) ** 2 + (w.y + 0.008) ** 2) ** 0.5 < 0.05)

    # Tunica: tubo de tela fruncido bajo las axilas, que cae hasta la rodilla y se pliega sobre las caderas.
    # Un panel vertical no tiene sobre que plegarse; un tubo mas ancho que el cuerpo, si.
    cape = bpy.data.objects.new("SN_Tunic", bpy.data.meshes.new("Tunic"))
    bpy.context.scene.collection.objects.link(cape)
    bm = bmesh.new()
    seg, rings = 72, 44
    z_top, z_bot = 1.325, 0.47
    rows = []
    for r in range(rings + 1):
        f = r / rings
        z = z_top + (z_bot - z_top) * f
        rx = 0.165 + 0.17 * f ** 0.8
        ry = 0.112 + 0.15 * f ** 0.8
        ring = []
        for k in range(seg):
            ang = 2 * math.pi * k / seg
            ring.append(bm.verts.new((rx * math.cos(ang), 0.01 + ry * math.sin(ang), z)))
        rows.append(ring)
    for r in range(rings):
        for k in range(seg):
            bm.faces.new((rows[r][k], rows[r][(k + 1) % seg], rows[r + 1][(k + 1) % seg], rows[r + 1][k]))
    bm.to_mesh(cape.data); bm.free()
    bpy.context.view_layer.update()
    pin(cape, lambda w: w.z > z_top - 0.03)

    simulate([veil, cape], body, 46)
    for p in (veil, cape):
        so = p.modifiers.new("Solidify", 'SOLIDIFY'); so.thickness = 0.004; so.offset = 1.0
        with ctx(p):
            bpy.ops.object.modifier_apply(modifier="Solidify")
            bpy.ops.object.shade_smooth()
        g = p.vertex_groups.get("pin")
        if g:
            p.vertex_groups.remove(g)
    return veil, cape


def build_armature():
    arm_data = bpy.data.armatures.new("SN_Armature")
    arm = bpy.data.objects.new("SN_Armature", arm_data)
    bpy.context.scene.collection.objects.link(arm)
    _c = ctx(arm); _c.__enter__()
    bpy.ops.object.mode_set(mode='EDIT')
    eb = arm_data.edit_bones

    def bone(name, head, tail, parent=None, roll_axis=(0, -1, 0)):
        b = eb.new(name); b.head = Vector(head); b.tail = Vector(tail)
        if parent:
            b.parent = eb[parent]
            b.use_connect = (Vector(head) - eb[parent].tail).length < 1e-4
        b.align_roll(Vector(roll_axis))
        return b

    bone("Hips", J["Hips"], J["Spine"])
    bone("Spine", J["Spine"], J["Chest"], "Hips")
    bone("Chest", J["Chest"], J["UpperChest"], "Spine")
    bone("UpperChest", J["UpperChest"], J["Neck"], "Chest")
    bone("Neck", J["Neck"], J["Head"], "UpperChest")
    bone("Head", J["Head"], J["HeadTop"], "Neck")
    for s in ("Left", "Right"):
        # rodillo fijado igual en toda la cadena para que las flexiones no se cancelen (leccion de los dedos)
        bone(s + "Shoulder", J[s + "Shoulder"], J[s + "UpperArm"], "UpperChest", (0, 0, 1))
        bone(s + "UpperArm", J[s + "UpperArm"], J[s + "LowerArm"], s + "Shoulder", (0, 0, 1))
        bone(s + "LowerArm", J[s + "LowerArm"], J[s + "Hand"], s + "UpperArm", (0, 0, 1))
        bone(s + "Hand", J[s + "Hand"], J[s + "HandEnd"], s + "LowerArm", (0, 0, 1))
        bone(s + "UpperLeg", J[s + "UpperLeg"], J[s + "LowerLeg"], "Hips", (0, -1, 0))
        bone(s + "LowerLeg", J[s + "LowerLeg"], J[s + "Foot"], s + "UpperLeg", (0, -1, 0))
        bone(s + "Foot", J[s + "Foot"], J[s + "Toes"], s + "LowerLeg", (0, 0, 1))
        bone(s + "Toes", J[s + "Toes"], J[s + "ToeEnd"], s + "Foot", (0, 0, 1))
    bpy.ops.object.mode_set(mode='OBJECT')
    _c.__exit__(None, None, None)
    return arm


def material():
    m = bpy.data.materials.new("M_SN_Cloth")
    m.use_nodes = True
    bsdf = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs["Base Color"].default_value = (0.86, 0.85, 0.82, 1)
    bsdf.inputs["Roughness"].default_value = 0.78
    if "Sheen Weight" in bsdf.inputs:
        bsdf.inputs["Sheen Weight"].default_value = 0.6
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.08
    return m


def main():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for coll in (bpy.data.meshes, bpy.data.armatures, bpy.data.materials):
        for d in list(coll):
            coll.remove(d)
    body = build_body()
    hood, mantle = build_cloth(body)
    m = material()
    for o in (body, hood, mantle):
        o.data.materials.clear()
        o.data.materials.append(m)
    arm = build_armature()
    with ctx(arm, [body, hood, mantle, arm]):
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    # capucha y manto solo siguen cabeza, cuello y torso; nunca brazos ni piernas
    keep = {"SN_Veil": ("Head", "Neck"), "SN_Tunic": ("Chest", "UpperChest", "Spine", "Hips", "LeftUpperLeg", "RightUpperLeg")}
    for o in (hood, mantle):
        for vg in list(o.vertex_groups):
            if vg.name not in keep[o.name]:
                o.vertex_groups.remove(vg)
        first = o.vertex_groups.get(keep[o.name][0]) or o.vertex_groups.new(name=keep[o.name][0])
        orphan = [v.index for v in o.data.vertices if sum(g.weight for g in v.groups) < 1e-4]
        if orphan:
            first.add(orphan, 1.0, 'REPLACE')
    sin_peso = sum(1 for v in body.data.vertices if sum(g.weight for g in v.groups) < 1e-4)
    tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in (body, hood, mantle))
    bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
    return {"triangulos": tris, "huesos": len(arm.data.bones), "vertices_cuerpo_sin_peso": sin_peso,
            "blend": OUT_BLEND}


RESULT = main()
print("SONADOR", RESULT)
