"""Tronco nudoso del arbol monumental (sueño 3), con contrafuertes y un hueco tallado.

Se ejecuta DENTRO de Blender (por ejemplo desde el MCP). Crea la escena TRONCO_NUDOSO y exporta
TallerFinal/Assets/_Project/Art/Models/Dream/Arbol_Monumental/Tronco_Nudoso.fbx.

- Cilindro de 128 x ~170 anillos; radio con estrias retorcidas (dos familias de senos), ruido y un ensanche en la
  base que se convierte en raices de contrafuerte de largo desigual (bajo tierra se abren mas).
- El valle entre dos raices mas cercano a -Y se gira a -Y exacto: alli se talla el hueco con un booleano de un
  elipsoide. En Unity, -Y de Blender es +Z: el hueco mira a la ladera, por donde llega el sonador.
- Material 0 corteza, material 1 interior del hueco (Unity pone negro absoluto).
"""
import math

import bmesh
import bpy
from mathutils import Matrix, Vector, noise

OUT = "C:/Users/HP/Documents/GitHub/proyectos-unity/TallerFinal/Assets/_Project/Art/Models/Dream/Arbol_Monumental/Tronco_Nudoso.fbx"
SEG, H0, H1, DH = 128, -2.0, 32.0, 0.2


def flute(h, th):
    tw = 0.07 * h
    f = max(0.0, math.sin(7 * th + tw + 0.5 * math.sin(3 * th))) ** 1.6
    f += 0.6 * max(0.0, math.sin(11 * th - 0.6 * tw + 1.3)) ** 2.2
    return f


def radius(h, th):
    hp = max(h, 0.0)
    base = 1.3 + 0.35 * math.exp(-hp / 10.0) + 1.5 * math.exp(-hp / 1.6)
    reach = 0.65 + 0.7 * (0.5 + 0.5 * noise.noise(Vector((math.cos(th) * 1.3, math.sin(th) * 1.3, 3.3))))
    amp = 0.09 + 0.75 * reach * math.exp(-hp / 1.8)
    if h < 0:
        amp *= 1.0 + 0.5 * (-h)
    n = noise.noise(Vector((math.cos(th) * 1.6, math.sin(th) * 1.6, h * 0.3)))
    n2 = noise.noise(Vector((math.cos(th) * 4.0 + 7, math.sin(th) * 4.0, h * 0.9)))
    r = base * (1.0 + amp * flute(h, th)) + base * (0.10 * n + 0.04 * n2)
    if hp > 26:
        r *= 1.0 - 0.25 * (hp - 26) / 6.0
    return r


def center(h):
    return Vector((0.35 * math.sin(h * 0.11), 0.25 * math.cos(h * 0.08 + 1.0) - 0.25, 0.0))


def build():
    sc = bpy.data.scenes.get("TRONCO_NUDOSO") or bpy.data.scenes.new("TRONCO_NUDOSO")
    bpy.context.window.scene = sc
    for o in list(sc.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    best = min((flute(1.0, -math.pi / 2 + d * 0.01) + 0.002 * abs(d), -math.pi / 2 + d * 0.01) for d in range(-60, 61))[1]
    rings = int((H1 - H0) / DH) + 1
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("UVMap")
    grid = []
    for i in range(rings):
        h = H0 + i * DH
        c = center(h)
        grid.append([bm.verts.new((c.x + math.cos(th) * radius(h, th), c.y + math.sin(th) * radius(h, th), h))
                     for th in (2 * math.pi * (j % SEG) / SEG for j in range(SEG + 1))])
    for i in range(rings - 1):
        for j in range(SEG):
            f = bm.faces.new((grid[i][j], grid[i][j + 1], grid[i + 1][j + 1], grid[i + 1][j]))
            for loop, (ii, jj) in zip(f.loops, ((i, j), (i, j + 1), (i + 1, j + 1), (i + 1, j))):
                loop[uvl].uv = (jj / SEG * 6.0, (H0 + ii * DH) / 2.5)
    bm.faces.new([grid[-1][j] for j in range(SEG)][::-1])
    bm.faces.new([grid[0][j] for j in range(SEG)])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    rot = Matrix.Rotation(-math.pi / 2 - best, 4, 'Z')
    bmesh.ops.transform(bm, matrix=rot, verts=bm.verts[:])
    me = bpy.data.meshes.new("Tronco_Nudoso")
    bm.to_mesh(me)
    bm.free()
    trunk = bpy.data.objects.new("Tronco_Nudoso", me)
    sc.collection.objects.link(trunk)

    rf = radius(1.2, best)
    cy = (rot @ Vector((center(1.2).x, center(1.2).y, 0))).y
    cut = bpy.data.objects.new("Cortador", bpy.data.meshes.new("Cortador"))
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=40, v_segments=24, radius=1.0)
    bm.to_mesh(cut.data)
    bm.free()
    cut.location = (0.0, cy - rf + 0.3, 1.1)
    cut.scale = (0.72, 1.35, 1.1)
    sc.collection.objects.link(cut)
    mod = trunk.modifiers.new("Hueco", "BOOLEAN")
    mod.object, mod.operation, mod.solver = cut, "DIFFERENCE", "EXACT"
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()
    newme = bpy.data.meshes.new_from_object(trunk.evaluated_get(dg))
    trunk.modifiers.clear()
    old = trunk.data
    trunk.data = newme
    bpy.data.meshes.remove(old)
    newme.name = "Tronco_Nudoso"
    for name in ("Corteza_Nudosa", "Hueco_Interior"):
        newme.materials.append(bpy.data.materials.get(name) or bpy.data.materials.new(name))
    inv = cut.matrix_world.inverted()
    for p in newme.polygons:
        p.use_smooth = True
        if (inv @ p.center).length < 1.03:
            p.material_index = 1
    bpy.data.objects.remove(cut, do_unlink=True)
    with bpy.context.temp_override(scene=sc):
        bpy.ops.export_scene.fbx(filepath=OUT, use_selection=False, object_types={'MESH'}, use_mesh_modifiers=True,
                                 apply_scale_options='FBX_SCALE_ALL', axis_forward='-Z', axis_up='Y',
                                 bake_space_transform=True, path_mode='STRIP', mesh_smooth_type='FACE')
    print("exportado", OUT, len(newme.vertices), "vertices")


build()
