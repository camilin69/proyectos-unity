# BOT-01 VIGÍA-03 (36.1): 1.25 m, cabeza grande, cuello estrecho, torso encogido, antebrazos largos, lanzador de red integrado,
# rostro sin boca con cuencas profundas como geometría. Piezas rígidas con pivote en eje de rotación; rig por hueso; clips 49.2.
import bpy, math, importlib, sys
sys.path.insert(0, r"C:/Users/HP/Documents/GitHub/proyectos-unity/SourceArt/Scripts")
import esn_lib as L; importlib.reload(L)
from mathutils import Vector

ASSET = "BOT-01_Vigia"
L.reset_scene()
col = L.collection(ASSET)
M = L.std_mats()
parts = {}

H = 1.25
# pies con goma (rodillas desfasadas: pierna izquierda 2 cm más adelantada)
for side, sx in (("L", -1), ("R", 1)):
    foot = L.box(f"foot_{side}", (0.12, 0.2, 0.05), (sx * 0.1, 0.02, 0.0), col, pivot='bottom', bevel=0.01); L.assign(foot, M['rubber'])
    shin = L.cyl(f"shin_{side}", 0.035, 0.32, (sx * 0.1, 0.0, 0.05), col, pivot='bottom', bevel=0.006); L.assign(shin, M['steel_dark'])
    knee = L.sphere(f"knee_{side}", 0.05, (sx * 0.1, 0.01 * sx, 0.37), col); L.assign(knee, M['steel_bare'])
    thigh = L.cyl(f"thigh_{side}", 0.04, 0.25, (sx * 0.1, 0.0, 0.37), col, pivot='bottom', bevel=0.006); L.assign(thigh, M['polymer_dark'])
    parts[f"foot_{side}"] = foot; parts[f"shin_{side}"] = shin; parts[f"knee_{side}"] = knee; parts[f"thigh_{side}"] = thigh
# pelvis y torso encogido (cubierta frontal sanitaria + panel posterior + rendijas)
pelvis = L.box("pelvis", (0.26, 0.16, 0.1), (0, 0, 0.62), col, pivot='bottom', bevel=0.02); L.assign(pelvis, M['steel_dark']); parts['pelvis'] = pelvis
torso = L.box("torso", (0.3, 0.2, 0.28), (0, 0, 0.72), col, pivot='bottom', bevel=0.03, segs=3); L.assign(torso, M['polymer_ivory']); parts['torso'] = torso
front = L.box("torso_cover", (0.24, 0.03, 0.2), (0, -0.105, 0.76), col, pivot='bottom', bevel=0.01); L.assign(front, M['polymer_ivory']); parts['torso_cover'] = front
back = L.box("torso_panel", (0.22, 0.02, 0.18), (0, 0.105, 0.77), col, pivot='bottom', bevel=0.005); L.assign(back, M['steel_paint']); parts['torso_panel'] = back
vents = [L.box(f"vent_{i}", (0.12, 0.004, 0.006), (0.05, -0.122, 0.79 + i * 0.02), col) for i in range(4)]
for v in vents: L.assign(v, M['steel_dark'])
vent = L.join(vents, "vents"); parts['vents'] = vent
# cuello estrecho articulado
neck_base = L.cyl("neck_base", 0.05, 0.03, (0, 0, 1.0), col, pivot='bottom'); L.assign(neck_base, M['steel_bare']); parts['neck_base'] = neck_base
neck = L.cyl("neck", 0.025, 0.06, (0, 0, 1.03), col, pivot='bottom', bevel=0.004); L.assign(neck, M['rubber']); parts['neck'] = neck
# cabeza grande con asimetría leve; cuencas como cavidades geométricas (booleano) y piezas internas oscuras
head = L.sphere("head", 0.11, (0, 0, 1.17), col, segs=32, rings=20, scale=(1.0, 1.08, 1.12)); L.assign(head, M['polymer_ivory'])
for side, sx in (("L", -1), ("R", 1)):
    cut = L.sphere(f"cut_{side}", 0.032, (sx * 0.042 + (0.004 if side == 'L' else 0), -0.095, 1.19), col, segs=16, rings=10)
    m = head.modifiers.new(f"Socket_{side}", 'BOOLEAN'); m.operation = 'DIFFERENCE'; m.object = cut
    inner = L.sphere(f"eye_inner_{side}", 0.02, (sx * 0.042, -0.075, 1.19), col, segs=12, rings=8); L.assign(inner, M['polymer_dark']); parts[f"eye_inner_{side}"] = inner
L.apply_all(head)
for side in ("L", "R"): bpy.data.objects.remove(bpy.data.objects[f"cut_{side}"])
# placas temporales y línea de unión (sin boca)
for side, sx in (("L", -1), ("R", 1)):
    plate = L.box(f"temple_{side}", (0.02, 0.07, 0.06), (sx * 0.105, 0.0, 1.18), col, bevel=0.005); L.assign(plate, M['steel_paint']); parts[f"temple_{side}"] = plate
parts['head'] = head
# brazos: hombro con junta, brazo, codo mecánico, antebrazo largo, mano de tres dedos; lanzador en antebrazo derecho
for side, sx in (("L", -1), ("R", 1)):
    sh = L.sphere(f"shoulder_{side}", 0.045, (sx * 0.17, 0, 0.95), col); L.assign(sh, M['steel_bare']); parts[f"shoulder_{side}"] = sh
    up = L.cyl(f"upperarm_{side}", 0.03, 0.22, (sx * 0.17, 0, 0.95), col, pivot='bottom', bevel=0.004); up.rotation_euler = (math.radians(180), 0, 0); L.assign(up, M['polymer_dark']); parts[f"upperarm_{side}"] = up
    el = L.sphere(f"elbow_{side}", 0.035, (sx * 0.17, 0, 0.73), col); L.assign(el, M['steel_bare']); parts[f"elbow_{side}"] = el
    fa = L.cyl(f"forearm_{side}", 0.028, 0.3, (sx * 0.17, 0, 0.73), col, pivot='bottom', bevel=0.004); fa.rotation_euler = (math.radians(180), 0, 0); L.assign(fa, M['polymer_ivory']); parts[f"forearm_{side}"] = fa
    palm = L.box(f"palm_{side}", (0.05, 0.03, 0.06), (sx * 0.17, 0, 0.43), col, pivot='top', bevel=0.006); L.assign(palm, M['polymer_dark']); parts[f"palm_{side}"] = palm
    fingers = []
    for i in range(3):
        f = L.cyl(f"finger_{side}{i}", 0.006, 0.09, (sx * 0.17 + (i - 1) * 0.015, -0.005, 0.37), col, pivot='bottom'); f.rotation_euler = (math.radians(180), 0, 0); L.assign(f, M['steel_bare']); fingers.append(f)
    fj = L.join(fingers, f"fingers_{side}"); parts[f"fingers_{side}"] = fj
# lanzador de red (antebrazo derecho): módulo, bobina, guía y cable
launcher = L.box("launcher", (0.06, 0.09, 0.14), (0.205, -0.02, 0.55), col, bevel=0.008); L.assign(launcher, M['steel_paint']); parts['launcher'] = launcher
coil = L.cyl("launcher_coil", 0.025, 0.05, (0.205, -0.02, 0.62), col, axis='Y'); L.assign(coil, M['copper']); parts['launcher_coil'] = coil
guide = L.cyl("launcher_guide", 0.018, 0.08, (0.205, -0.08, 0.55), col, axis='Y'); L.assign(guide, M['steel_dark']); parts['launcher_guide'] = guide
cable = L.tube("launcher_cable", [(0.2, 0.03, 0.63), (0.22, 0.06, 0.75), (0.19, 0.07, 0.9), (0.12, 0.09, 0.98)], 0.006, col); L.assign(cable, M['rubber']); parts['launcher_cable'] = cable

# UV por pieza y suavizado
for o in parts.values():
    L.apply_all(o); L.smooth(o, 40); L.uv_project(o)

# rig: hueso por pieza (36.4), pivote en eje de rotación
bones = [
    ("root", (0, 0, 0), (0, 0, 0.1), None),
    ("pelvis", (0, 0, 0.62), (0, 0, 0.72), "root"),
    ("spine", (0, 0, 0.72), (0, 0, 1.0), "pelvis"),
    ("neck", (0, 0, 1.0), (0, 0, 1.09), "spine"),
    ("head", (0, 0, 1.09), (0, 0, 1.28), "neck"),
    ("thigh_L", (-0.1, 0, 0.62), (-0.1, 0, 0.37), "pelvis"), ("shin_L", (-0.1, 0, 0.37), (-0.1, 0, 0.05), "thigh_L"), ("foot_L", (-0.1, 0, 0.05), (-0.1, -0.12, 0.0), "shin_L"),
    ("thigh_R", (0.1, 0, 0.62), (0.1, 0, 0.37), "pelvis"), ("shin_R", (0.1, 0, 0.37), (0.1, 0, 0.05), "thigh_R"), ("foot_R", (0.1, 0, 0.05), (0.1, -0.12, 0.0), "shin_R"),
    ("upperarm_L", (-0.17, 0, 0.95), (-0.17, 0, 0.73), "spine"), ("forearm_L", (-0.17, 0, 0.73), (-0.17, 0, 0.43), "upperarm_L"), ("hand_L", (-0.17, 0, 0.43), (-0.17, 0, 0.28), "forearm_L"),
    ("upperarm_R", (0.17, 0, 0.95), (0.17, 0, 0.73), "spine"), ("forearm_R", (0.17, 0, 0.73), (0.17, 0, 0.43), "upperarm_R"), ("hand_R", (0.17, 0, 0.43), (0.17, 0, 0.28), "forearm_R"),
]
arm = L.armature("Armature_Vigia", bones, col)
binding = {
    "pelvis": ["pelvis"], "spine": ["torso", "torso_cover", "torso_panel", "vents", "shoulder_L", "shoulder_R"], "neck": ["neck_base", "neck"],
    "head": ["head", "eye_inner_L", "eye_inner_R", "temple_L", "temple_R"],
    "thigh_L": ["thigh_L", "knee_L"], "shin_L": ["shin_L"], "foot_L": ["foot_L"], "thigh_R": ["thigh_R", "knee_R"], "shin_R": ["shin_R"], "foot_R": ["foot_R"],
    "upperarm_L": ["upperarm_L", "elbow_L"], "forearm_L": ["forearm_L"], "hand_L": ["palm_L", "fingers_L"],
    "upperarm_R": ["upperarm_R", "elbow_R"], "forearm_R": ["forearm_R", "launcher", "launcher_coil", "launcher_guide", "launcher_cable"], "hand_R": ["palm_R", "fingers_R"],
}
for bone, names in binding.items():
    for n in names: L.bind_rigid(parts[n], arm, bone)

# clips 49.2 / 60.2 (30 fps): idle (quietud casi humana), walk (marcha irregular, cabeza termina el giro después), anticipation (1.1 s, antebrazo levantado), net, death
Z = (0, 0, 0)
idle = L.action(arm, "Vigia_Idle", 90, poses={1: {"head": ((0, 0, 0), Z), "spine": ((0, 0, 0), Z)}, 45: {"head": ((-4, 0, 6), Z), "spine": ((2, 0, 0), Z), "hand_L": ((8, 0, 0), Z)}, 90: {"head": ((0, 0, 0), Z), "spine": ((0, 0, 0), Z), "hand_L": ((0, 0, 0), Z)}})
L.push_nla(arm, idle)
walk = L.action(arm, "Vigia_Walk", 40, poses={
    1: {"thigh_L": ((-25, 0, 0), Z), "thigh_R": ((25, 0, 0), Z), "shin_L": ((30, 0, 0), Z), "shin_R": ((0, 0, 0), Z), "spine": ((6, 0, -4), Z), "head": ((-4, 0, 6), Z), "upperarm_L": ((15, 0, 0), Z), "upperarm_R": ((-15, 0, 0), Z)},
    20: {"thigh_L": ((25, 0, 0), Z), "thigh_R": ((-25, 0, 0), Z), "shin_L": ((0, 0, 0), Z), "shin_R": ((30, 0, 0), Z), "spine": ((6, 0, 4), Z), "head": ((-4, 0, -2), Z), "upperarm_L": ((-15, 0, 0), Z), "upperarm_R": ((15, 0, 0), Z)},
    40: {"thigh_L": ((-25, 0, 0), Z), "thigh_R": ((25, 0, 0), Z), "shin_L": ((30, 0, 0), Z), "shin_R": ((0, 0, 0), Z), "spine": ((6, 0, -4), Z), "head": ((-4, 0, 6), Z), "upperarm_L": ((15, 0, 0), Z), "upperarm_R": ((-15, 0, 0), Z)}})
L.push_nla(arm, walk)
antic = L.action(arm, "Vigia_Anticipation", 33, loop=False, poses={1: {"upperarm_R": ((0, 0, 0), Z), "forearm_R": ((0, 0, 0), Z), "spine": ((0, 0, 0), Z)}, 12: {"upperarm_R": ((-70, 0, -20), Z), "forearm_R": ((-40, 0, 0), Z), "spine": ((-6, 0, 0), Z), "head": ((6, 0, 0), Z)}, 33: {"upperarm_R": ((-95, 0, -25), Z), "forearm_R": ((-30, 0, 0), Z), "spine": ((-8, 0, 0), Z), "head": ((8, 0, 0), Z)}})
L.push_nla(arm, antic)
net = L.action(arm, "Vigia_Net", 42, loop=False, poses={1: {"upperarm_R": ((-95, 0, -25), Z), "forearm_R": ((-30, 0, 0), Z), "spine": ((-8, 0, 0), Z)}, 4: {"upperarm_R": ((-100, 0, -20), Z), "forearm_R": ((-5, 0, 0), Z), "spine": ((4, 0, 0), Z)}, 42: {"upperarm_R": ((0, 0, 0), Z), "forearm_R": ((0, 0, 0), Z), "spine": ((0, 0, 0), Z), "head": ((0, 0, 0), Z)}})
L.push_nla(arm, net)
death = L.action(arm, "Vigia_Death", 36, loop=False, poses={1: {"root": ((0, 0, 0), Z)}, 14: {"spine": ((25, 0, 10), Z), "thigh_L": ((30, 0, 0), Z), "thigh_R": ((-10, 0, 0), Z), "root": ((0, 0, 0), (0, 0, -0.15))}, 36: {"root": ((80, 0, 15), (0, -0.2, -0.55)), "spine": ((10, 0, 20), Z), "head": ((-20, 0, 25), Z), "upperarm_L": ((40, 0, 30), Z)}})
L.push_nla(arm, death)

objs = list(parts.values())
tex = L.bake_pbr(objs, ASSET, size=1024, samples=6)
blend = L.save_blend(ASSET)
fbx, size = L.export_fbx(objs, ASSET, armature_obj=arm)
sheets = L.sheet(ASSET, objs, views=('front', 'side', 'iso'))
rep = L.report(ASSET, objs, {"blend": blend, "fbx": fbx, "fbx_bytes": size, "textures": tex, "clips": ["Vigia_Idle", "Vigia_Walk", "Vigia_Anticipation", "Vigia_Net", "Vigia_Death"], "height_target_m": H, "sheets": sheets})
print(rep)
