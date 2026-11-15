"""Exporta una escena de dream/blender a Unity: FBX + texturas + manifiesto de materiales y luces.

Se ejecuta DENTRO de Blender (por ejemplo con runpy desde el MCP), con dos globales:
    BLEND = ruta del .blend de dream/blender
    NAME  = nombre de carpeta destino (TallerFinal/Assets/_Project/Art/Models/Dream/<NAME>/)

Escribe:
    <NAME>.fbx              mallas con modificadores aplicados; cada luz y cada camara viaja como un empty
                            ("LUZ_<n>", "CAM_<n>") para que Unity sepa donde estan, en sus mismos ejes
    tex/*.png               las imagenes que usan los materiales
    manifest.json           por material: color base, imagenes de color/normal/rugosidad/emision/alfa y valores;
                            por luz: tipo, color, potencia (W), tamano y angulo de cono
"""
import json
import math
import os

import bpy

BLEND = globals().get("BLEND")
NAME = globals().get("NAME")
OUT = os.path.join("C:/Users/HP/Documents/GitHub/proyectos-unity/TallerFinal/Assets/_Project/Art/Models/Dream", NAME)
os.makedirs(os.path.join(OUT, "tex"), exist_ok=True)

bpy.ops.wm.open_mainfile(filepath=BLEND)
scene = bpy.context.scene


def image_from(socket, depth=0):
    """Sigue un socket hacia atras hasta la primera imagen (atraviesa normal map, mezclas, rampas)."""
    if depth > 6 or not socket.is_linked:
        return None
    node = socket.links[0].from_node
    if node.type == 'TEX_IMAGE' and node.image:
        return node.image
    for inp in node.inputs:
        if inp.is_linked:
            img = image_from(inp, depth + 1)
            if img:
                return img
    return None


saved = {}


def save_image(img):
    if img.name in saved:
        return saved[img.name]
    base = os.path.splitext(img.name)[0].replace(".", "_").replace(" ", "_") + ".png"
    path = os.path.join(OUT, "tex", base)
    copy = img.copy()
    copy.filepath_raw = path
    copy.file_format = 'PNG'
    try:
        copy.save()
    except Exception:
        copy.save_render(path)
    bpy.data.images.remove(copy)
    saved[img.name] = "tex/" + base
    return saved[img.name]


materials = {}
for m in bpy.data.materials:
    if not m.users or not m.use_nodes:
        continue
    bsdf = next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if not bsdf:
        continue
    entry = {}

    def val(name):
        s = bsdf.inputs.get(name)
        if s is None:
            return None
        v = s.default_value
        return list(v) if hasattr(v, "__len__") else v

    entry["base_color"] = val("Base Color")
    entry["roughness"] = val("Roughness")
    entry["metallic"] = val("Metallic")
    entry["emission_color"] = val("Emission Color")
    entry["emission_strength"] = val("Emission Strength")
    entry["alpha"] = val("Alpha")
    for key, sock in (("albedo", "Base Color"), ("normal", "Normal"), ("roughness_map", "Roughness"),
                      ("emission", "Emission Color"), ("alpha_map", "Alpha"), ("metallic_map", "Metallic")):
        s = bsdf.inputs.get(sock)
        img = image_from(s) if s is not None else None
        if img:
            entry[key] = save_image(img)
    # canal UV de la textura de color: los materiales de dream/ eligen su mapa con un nodo UVMap (no siempre el primero)
    entry["uv_index"] = 0
    uvnode = next((n for n in m.node_tree.nodes if n.type == 'UVMAP' and n.uv_map), None)
    if uvnode:
        users = [o for o in scene.objects if o.type == 'MESH' and any(s.material == m for s in o.material_slots)]
        if users:
            keys = users[0].data.uv_layers.keys()
            if uvnode.uv_map in keys:
                entry["uv_index"] = keys.index(uvnode.uv_map)
    materials[m.name] = entry

# luces y camaras -> empties con el mismo nombre en el manifiesto
lights = {}
cams = {}
for i, o in enumerate([o for o in scene.objects if o.type == 'LIGHT']):
    name = f"LUZ_{i:02d}"
    e = bpy.data.objects.new(name, None)
    scene.collection.objects.link(e)
    e.matrix_world = o.matrix_world.copy()
    d = o.data
    lights[name] = {"type": d.type, "color": list(d.color), "energy": d.energy,
                    "size": getattr(d, "size", 0.0), "size_y": getattr(d, "size_y", 0.0), "shape": getattr(d, "shape", ""),
                    "spot_deg": math.degrees(getattr(d, "spot_size", 0.0)), "blender_name": o.name}
for i, o in enumerate([o for o in scene.objects if o.type == 'CAMERA']):
    name = f"CAM_{i:02d}"
    e = bpy.data.objects.new(name, None)
    scene.collection.objects.link(e)
    e.matrix_world = o.matrix_world.copy()
    cams[name] = {"lens_mm": o.data.lens, "sensor_mm": o.data.sensor_height, "blender_name": o.name}
# marcadores de ejes para verificar la conversion en Unity
for axis, v in (("EJE_X", (1, 0, 0)), ("EJE_Y", (0, 1, 0)), ("EJE_Z", (0, 0, 1))):
    e = bpy.data.objects.new(axis, None)
    scene.collection.objects.link(e)
    e.location = v

# sin seleccion (desde el MCP no hay contexto de ventana): el filtro de tipos deja solo mallas y empties
bpy.ops.export_scene.fbx(filepath=os.path.join(OUT, NAME + ".fbx"), use_selection=False,
                         object_types={'MESH', 'EMPTY'}, use_mesh_modifiers=True, apply_scale_options='FBX_SCALE_ALL',
                         axis_forward='-Z', axis_up='Y', bake_space_transform=True, path_mode='STRIP', mesh_smooth_type='FACE')

mesh_mats = {}
for o in scene.objects:
    if o.type == 'MESH':
        mesh_mats[o.name] = [s.material.name for s in o.material_slots if s.material]
with open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8") as f:
    json.dump({"source": os.path.basename(BLEND), "materials": materials, "lights": lights, "cameras": cams,
               "objects": mesh_mats}, f, indent=1)
print("exportado", NAME, len(materials), "materiales", len(lights), "luces", len(cams), "camaras")
