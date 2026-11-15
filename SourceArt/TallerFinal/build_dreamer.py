# SUENO LUCIDO - el sonador: figura blanca sin rostro, de tela, con esqueleto Humanoid de Unity.
#
# El cuerpo sale de un grafo de articulaciones con Skin modifier + Subdivision: da una figura organica con
# anillos de aristas en cada articulacion, que es lo que necesita una malla para deformarse sin pellizcarse.
# El esqueleto se construye con las MISMAS articulaciones, asi que hueso y malla no pueden desalinearse.
# Convencion: Z arriba, el personaje mira a -Y, su izquierda es +X, pose T, 1.70 m.
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
        side + "LowerArm": (sx * 0.445, 0.0, 1.40), side + "Hand": (sx * 0.70, 0.0, 1.40),
        side + "HandEnd": (sx * 0.86, 0.0, 1.40),
        side + "UpperLeg": (sx * 0.095, 0.0, 0.92), side + "LowerLeg": (sx * 0.10, 0.0, 0.50),
        side + "Foot": (sx * 0.10, 0.025, 0.085), side + "Toes": (sx * 0.10, -0.115, 0.022),
        side + "ToeEnd": (sx * 0.10, -0.20, 0.02),
    })

# radios (x, y) por articulacion: figura esbelta, hombros suaves, sin rasgos marcados
R = {"Hips": (0.15, 0.10), "Spine": (0.13, 0.09), "Chest": (0.155, 0.10), "UpperChest": (0.16, 0.095),
     "Neck": (0.052, 0.052), "Head": (0.075, 0.085), "HeadTop": (0.04, 0.045)}
for side in ("Left", "Right"):
    R.update({side + "Shoulder": (0.07, 0.07), side + "UpperArm": (0.052, 0.052), side + "LowerArm": (0.043, 0.043),
              side + "Hand": (0.035, 0.045), side + "HandEnd": (0.014, 0.02),
              side + "UpperLeg": (0.085, 0.085), side + "LowerLeg": (0.058, 0.058), side + "Foot": (0.045, 0.05),
              side + "Toes": (0.042, 0.03), side + "ToeEnd": (0.02, 0.015)})

EDGES = [("Hips", "Spine"), ("Spine", "Chest"), ("Chest", "UpperChest"), ("UpperChest", "Neck"), ("Neck", "Head"),
         ("Head", "HeadTop")]
for s in ("Left", "Right"):
    EDGES += [("UpperChest", s + "Shoulder"), (s + "Shoulder", s + "UpperArm"), (s + "UpperArm", s + "LowerArm"),
              (s + "LowerArm", s + "Hand"), (s + "Hand", s + "HandEnd"),
              ("Hips", s + "UpperLeg"), (s + "UpperLeg", s + "LowerLeg"), (s + "LowerLeg", s + "Foot"),
              (s + "Foot", s + "Toes"), (s + "Toes", s + "ToeEnd")]

LONG = {"UpperArm", "LowerArm", "UpperLeg", "LowerLeg"}


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
        if seg in LONG:
            mv = bm.verts.new(Vector(lerp(J[a], J[b], 0.5)))
            ra, rb = R[a], R[b]
            extra.append(((ra[0] + rb[0]) / 2 * 1.02, (ra[1] + rb[1]) / 2 * 1.02))
            bm.edges.new((idx[a], mv)); bm.edges.new((mv, idx[b]))
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
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.ops.object.modifier_apply(modifier="Skin")
    bpy.ops.object.modifier_apply(modifier="Subsurf")
    bpy.ops.object.shade_smooth()
    return ob


def build_hood_and_mantle():
    """Capucha y manto: tela que cae. Capucha = esfera abierta por delante sobre la cabeza; manto = cono
    acampanado desde el cuello hasta media espalda y pecho, con pliegues verticales por desplazamiento."""
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=32, radius=0.112, location=(0, 0.012, 1.60))
    hood = bpy.context.active_object; hood.name = "SN_Hood"
    hood.scale = (1.0, 1.12, 1.18)
    bpy.ops.object.transform_apply(scale=True)
    bm = bmesh.new(); bm.from_mesh(hood.data)
    kill = [f for f in bm.faces if f.calc_center_median().y < -0.05 and -0.10 < f.calc_center_median().z < 0.07]
    bmesh.ops.delete(bm, geom=kill, context='FACES')
    bm.to_mesh(hood.data); bm.free()

    bpy.ops.mesh.primitive_cone_add(vertices=96, radius1=0.40, radius2=0.10, depth=0.62, end_fill_type='NOTHING',
                                    location=(0, 0.01, 1.17))
    mantle = bpy.context.active_object; mantle.name = "SN_Mantle"
    mantle.scale = (1.0, 0.72, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    bm = bmesh.new(); bm.from_mesh(mantle.data)
    vert_edges = [e for e in bm.edges if abs(e.verts[0].co.z - e.verts[1].co.z) > 0.05]
    bmesh.ops.subdivide_edges(bm, edges=vert_edges, cuts=10, use_grid_fill=False)
    for v in bm.verts:
        ang = math.atan2(v.co.y, v.co.x)
        t = (0.31 - v.co.z) / 0.62
        fold = 0.018 * t * (math.sin(ang * 9) + 0.5 * math.sin(ang * 17 + 1.3))
        r = Vector((v.co.x, v.co.y, 0)).length
        if r > 1e-5:
            k = (r + fold) / r
            v.co.x *= k; v.co.y *= k
        if t > 0.95:
            v.co.z += 0.03 * math.sin(ang * 3 + 0.7)
    bm.to_mesh(mantle.data); bm.free()
    for p in (hood, mantle):
        so = p.modifiers.new("Solidify", 'SOLIDIFY'); so.thickness = 0.006; so.offset = 1.0
        bpy.context.view_layer.objects.active = p
        bpy.ops.object.modifier_apply(modifier="Solidify")
        bpy.ops.object.shade_smooth()
    return hood, mantle


def build_armature():
    arm_data = bpy.data.armatures.new("SN_Armature")
    arm = bpy.data.objects.new("SN_Armature", arm_data)
    bpy.context.scene.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
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
    bpy.ops.wm.read_homefile(use_empty=True)
    body = build_body()
    hood, mantle = build_hood_and_mantle()
    m = material()
    for o in (body, hood, mantle):
        o.data.materials.clear()
        o.data.materials.append(m)
    arm = build_armature()
    bpy.ops.object.select_all(action='DESELECT')
    for o in (body, hood, mantle):
        o.select_set(True)
    arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    # capucha y manto solo siguen cabeza, cuello y torso; nunca brazos ni piernas
    keep = {"SN_Hood": ("Head", "Neck"), "SN_Mantle": ("Neck", "UpperChest", "Chest", "Head")}
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
