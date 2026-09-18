# BOT-03 EL ARCHIVISTA (36.3/15): 3.1 m, brazos y cuello excesivamente largos con articulaciones plausibles, compartimentos torácicos
# con códigos, cableado en haces, manos de pinza, carcasa facial casi intacta sobre cuerpo remendado, aberturas con grosor.
import bpy, math, importlib, sys
sys.path.insert(0, r"C:/Users/HP/Documents/GitHub/proyectos-unity/SourceArt/Scripts")
import esn_lib as L; importlib.reload(L)

ASSET = "BOT-03_Archivista"
L.reset_scene()
col = L.collection(ASSET)
M = L.std_mats()
P = {}

for side, sx in (("L", -1), ("R", 1)):
    foot = L.box(f"foot_{side}", (0.22, 0.4, 0.08), (sx * 0.26, 0.05, 0.0), col, pivot='bottom', bevel=0.02); L.assign(foot, M['rubber']); P[f"foot_{side}"] = foot
    shin = L.box(f"shin_{side}", (0.14, 0.16, 0.62), (sx * 0.26, 0.0, 0.08), col, pivot='bottom', bevel=0.02); L.assign(shin, M['steel_dark']); P[f"shin_{side}"] = shin
    knee = L.cyl(f"knee_{side}", 0.09, 0.2, (sx * 0.26, 0.0, 0.72), col, axis='X'); L.assign(knee, M['steel_bare']); P[f"knee_{side}"] = knee
    thigh = L.box(f"thigh_{side}", (0.17, 0.2, 0.7), (sx * 0.26, 0.0, 0.72), col, pivot='bottom', bevel=0.03); L.assign(thigh, M['steel_paint']); P[f"thigh_{side}"] = thigh
pelvis = L.box("pelvis", (0.6, 0.32, 0.22), (0, 0, 1.42), col, pivot='bottom', bevel=0.04); L.assign(pelvis, M['steel_dark']); P['pelvis'] = pelvis
torso = L.box("torso", (0.7, 0.42, 0.76), (0, 0, 1.64), col, pivot='bottom', bevel=0.05, segs=3); L.assign(torso, M['steel_paint'])
# compartimentos torácicos: cavidades con grosor y fondo
drawers = []
for i in range(3):
    for j in range(2):
        cut = L.box(f"cut_{i}{j}", (0.16, 0.12, 0.14), ((j - 0.5) * 0.24, -0.19, 1.74 + i * 0.2), col)
        m = torso.modifiers.new(f"Drawer_{i}{j}", 'BOOLEAN'); m.operation = 'DIFFERENCE'; m.object = cut
        back = L.box(f"drawer_back_{i}{j}", (0.15, 0.02, 0.13), ((j - 0.5) * 0.24, -0.135, 1.74 + i * 0.2), col); L.assign(back, M['polymer_dark']); drawers.append(back)
        tag = L.box(f"tag_{i}{j}", (0.06, 0.004, 0.02), ((j - 0.5) * 0.24, -0.215, 1.66 + i * 0.2), col); L.assign(tag, M['ceramic']); drawers.append(tag)
L.apply_all(torso)
for i in range(3):
    for j in range(2): bpy.data.objects.remove(bpy.data.objects[f"cut_{i}{j}"])
P['torso'] = torso; P['drawers'] = L.join(drawers, "drawers")
backp = L.box("back_panel", (0.56, 0.05, 0.6), (0, 0.22, 1.7), col, pivot='bottom', bevel=0.012); L.assign(backp, M['polymer_dark']); P['back_panel'] = backp
harness = L.tube("cable_harness", [(-0.25, 0.25, 1.7), (-0.2, 0.28, 2.1), (0.0, 0.3, 2.4), (0.1, 0.22, 2.7), (0.05, 0.12, 2.86)], 0.025, col); L.assign(harness, M['rubber']); P['cable_harness'] = harness
# hombros y brazos muy largos (dos segmentos por brazo + pinza)
for side, sx in (("L", -1), ("R", 1)):
    sh = L.sphere(f"shoulder_{side}", 0.14, (sx * 0.45, 0, 2.32), col); L.assign(sh, M['steel_bare']); P[f"shoulder_{side}"] = sh
    up = L.cyl(f"upperarm_{side}", 0.07, 0.62, (sx * 0.45, 0, 2.32), col, pivot='bottom', bevel=0.01); up.rotation_euler = (math.radians(180), 0, 0); L.assign(up, M['steel_paint']); P[f"upperarm_{side}"] = up
    el = L.cyl(f"elbow_{side}", 0.075, 0.18, (sx * 0.45, 0, 1.7), col, axis='X'); L.assign(el, M['steel_dark']); P[f"elbow_{side}"] = el
    fa = L.cyl(f"forearm_{side}", 0.06, 0.66, (sx * 0.45, 0, 1.7), col, pivot='bottom', bevel=0.01); fa.rotation_euler = (math.radians(180), 0, 0); L.assign(fa, M['polymer_ivory']); P[f"forearm_{side}"] = fa
    wrist = L.sphere(f"wrist_{side}", 0.07, (sx * 0.45, 0, 1.04), col); L.assign(wrist, M['steel_bare']); P[f"wrist_{side}"] = wrist
    claws = []
    for k in range(3):
        a = math.radians(120 * k)
        c = L.box(f"claw_{side}{k}", (0.035, 0.05, 0.26), (sx * 0.45 + 0.06 * math.cos(a), 0.06 * math.sin(a), 1.04), col, pivot='top', bevel=0.008); L.assign(c, M['steel_dark']); claws.append(c)
    P[f"claw_{side}"] = L.join(claws, f"claw_{side}")
# cuello largo con vértebras y cabeza porcelánica
for i in range(4):
    v = L.cyl(f"vert_{i}", 0.055 - i * 0.004, 0.09, (0, 0.02 * i, 2.4 + i * 0.1), col); L.assign(v, M['rubber' if i % 2 else 'steel_bare']); P[f"vert_{i}"] = v
head = L.sphere("head", 0.16, (0, 0.06, 2.92), col, segs=32, rings=20, scale=(0.85, 1.0, 1.15)); L.assign(head, M['ceramic'])
for side, sx in (("L", -1), ("R", 1)):
    cut = L.sphere(f"cut_{side}", 0.04, (sx * 0.055, -0.07, 2.96), col, segs=16, rings=10)
    m = head.modifiers.new(f"Socket_{side}", 'BOOLEAN'); m.operation = 'DIFFERENCE'; m.object = cut
    inner = L.sphere(f"eye_inner_{side}", 0.025, (sx * 0.055, -0.045, 2.96), col, segs=12, rings=8); L.assign(inner, M['polymer_dark']); P[f"eye_inner_{side}"] = inner
L.apply_all(head)
for side in ("L", "R"): bpy.data.objects.remove(bpy.data.objects[f"cut_{side}"])
P['head'] = head
nape = L.tube("nape_cables", [(0, 0.2, 2.86), (0.03, 0.26, 2.7), (-0.02, 0.28, 2.5)], 0.012, col); L.assign(nape, M['rubber']); P['nape_cables'] = nape
lights = [L.box(f"light_{i}", (0.02, 0.01, 0.02), (-0.28 + i * 0.14, -0.215, 2.3), col) for i in range(5)]
for lg in lights: L.assign(lg, M['emitter'])
P['phase_lights'] = L.join(lights, "phase_lights")

for o in P.values():
    L.apply_all(o); L.smooth(o, 40); L.uv_project(o)

bones = [
    ("root", (0, 0, 0), (0, 0, 0.2), None),
    ("pelvis", (0, 0, 1.42), (0, 0, 1.64), "root"), ("spine", (0, 0, 1.64), (0, 0, 2.4), "pelvis"), ("neck", (0, 0, 2.4), (0, 0.06, 2.76), "spine"), ("head", (0, 0.06, 2.76), (0, 0.06, 3.1), "neck"),
    ("thigh_L", (-0.26, 0, 1.42), (-0.26, 0, 0.72), "pelvis"), ("shin_L", (-0.26, 0, 0.72), (-0.26, 0, 0.08), "thigh_L"), ("foot_L", (-0.26, 0, 0.08), (-0.26, -0.2, 0), "shin_L"),
    ("thigh_R", (0.26, 0, 1.42), (0.26, 0, 0.72), "pelvis"), ("shin_R", (0.26, 0, 0.72), (0.26, 0, 0.08), "thigh_R"), ("foot_R", (0.26, 0, 0.08), (0.26, -0.2, 0), "shin_R"),
    ("upperarm_L", (-0.45, 0, 2.32), (-0.45, 0, 1.7), "spine"), ("forearm_L", (-0.45, 0, 1.7), (-0.45, 0, 1.04), "upperarm_L"), ("hand_L", (-0.45, 0, 1.04), (-0.45, 0, 0.78), "forearm_L"),
    ("upperarm_R", (0.45, 0, 2.32), (0.45, 0, 1.7), "spine"), ("forearm_R", (0.45, 0, 1.7), (0.45, 0, 1.04), "upperarm_R"), ("hand_R", (0.45, 0, 1.04), (0.45, 0, 0.78), "forearm_R"),
]
arm = L.armature("Armature_Archivista", bones, col)
binding = {
    "pelvis": ["pelvis"], "spine": ["torso", "drawers", "back_panel", "cable_harness", "shoulder_L", "shoulder_R", "phase_lights"], "neck": ["vert_0", "vert_1", "vert_2", "vert_3", "nape_cables"],
    "head": ["head", "eye_inner_L", "eye_inner_R"],
    "thigh_L": ["thigh_L", "knee_L"], "shin_L": ["shin_L"], "foot_L": ["foot_L"], "thigh_R": ["thigh_R", "knee_R"], "shin_R": ["shin_R"], "foot_R": ["foot_R"],
    "upperarm_L": ["upperarm_L", "elbow_L"], "forearm_L": ["forearm_L", "wrist_L"], "hand_L": ["claw_L"],
    "upperarm_R": ["upperarm_R", "elbow_R"], "forearm_R": ["forearm_R", "wrist_R"], "hand_R": ["claw_R"],
}
for bone, names in binding.items():
    for n in names: L.bind_rigid(P[n], arm, bone)

Z = (0, 0, 0)
L.push_nla(arm, L.action(arm, "Archivista_Idle", 120, poses={1: {"head": ((0, 0, 0), Z), "neck": ((0, 0, 0), Z)}, 60: {"head": ((5, 0, -8), Z), "neck": ((3, 0, 4), Z), "hand_L": ((0, 0, 10), Z)}, 120: {"head": ((0, 0, 0), Z), "neck": ((0, 0, 0), Z), "hand_L": ((0, 0, 0), Z)}}))
L.push_nla(arm, L.action(arm, "Archivista_Walk", 56, poses={
    1: {"thigh_L": ((-24, 0, 0), Z), "thigh_R": ((24, 0, 0), Z), "shin_L": ((30, 0, 0), Z), "spine": ((5, 0, -3), Z), "upperarm_L": ((10, 0, 0), Z), "upperarm_R": ((-10, 0, 0), Z)},
    28: {"thigh_L": ((24, 0, 0), Z), "thigh_R": ((-24, 0, 0), Z), "shin_L": ((0, 0, 0), Z), "shin_R": ((30, 0, 0), Z), "spine": ((5, 0, 3), Z), "upperarm_L": ((-10, 0, 0), Z), "upperarm_R": ((10, 0, 0), Z)},
    56: {"thigh_L": ((-24, 0, 0), Z), "thigh_R": ((24, 0, 0), Z), "shin_L": ((30, 0, 0), Z), "shin_R": ((0, 0, 0), Z), "spine": ((5, 0, -3), Z), "upperarm_L": ((10, 0, 0), Z), "upperarm_R": ((-10, 0, 0), Z)}}))
# cuatro firmas distintas (60.4): rayo 1.2 s, barrido 1.4 s, carga 1.5 s, pulso 1.8 s
L.push_nla(arm, L.action(arm, "Archivista_Ray", 36 + 60, loop=False, poses={1: {"upperarm_R": ((0, 0, 0), Z)}, 36: {"upperarm_R": ((-95, 0, -10), Z), "forearm_R": ((-10, 0, 0), Z), "spine": ((-6, 0, -6), Z)}, 40: {"upperarm_R": ((-85, 0, -5), Z)}, 96: {"upperarm_R": ((0, 0, 0), Z), "forearm_R": ((0, 0, 0), Z), "spine": ((0, 0, 0), Z)}}))
L.push_nla(arm, L.action(arm, "Archivista_Sweep", 42 + 66, loop=False, poses={1: {"upperarm_L": ((0, 0, 0), Z), "spine": ((0, 0, 0), Z)}, 42: {"upperarm_L": ((-80, 0, 60), Z), "spine": ((0, 0, 25), Z)}, 50: {"upperarm_L": ((-80, 0, -70), Z), "spine": ((0, 0, -30), Z)}, 108: {"upperarm_L": ((0, 0, 0), Z), "spine": ((0, 0, 0), Z)}}))
L.push_nla(arm, L.action(arm, "Archivista_Charge", 45 + 72, loop=False, poses={1: {"spine": ((0, 0, 0), Z)}, 45: {"spine": ((25, 0, 0), Z), "head": ((-20, 0, 0), Z), "upperarm_L": ((-40, 0, 20), Z), "upperarm_R": ((-40, 0, -20), Z)}, 60: {"spine": ((20, 0, 0), Z)}, 117: {"spine": ((0, 0, 0), Z), "head": ((0, 0, 0), Z), "upperarm_L": ((0, 0, 0), Z), "upperarm_R": ((0, 0, 0), Z)}}))
L.push_nla(arm, L.action(arm, "Archivista_Pulse", 54 + 72, loop=False, poses={1: {"root": ((0, 0, 0), Z)}, 54: {"thigh_L": ((40, 0, 0), Z), "thigh_R": ((40, 0, 0), Z), "shin_L": ((70, 0, 0), Z), "shin_R": ((70, 0, 0), Z), "root": ((0, 0, 0), (0, 0, -0.45)), "upperarm_L": ((-120, 0, 0), Z), "upperarm_R": ((-120, 0, 0), Z)}, 60: {"upperarm_L": ((20, 0, 0), Z), "upperarm_R": ((20, 0, 0), Z)}, 126: {"thigh_L": ((0, 0, 0), Z), "thigh_R": ((0, 0, 0), Z), "shin_L": ((0, 0, 0), Z), "shin_R": ((0, 0, 0), Z), "root": ((0, 0, 0), Z), "upperarm_L": ((0, 0, 0), Z), "upperarm_R": ((0, 0, 0), Z)}}))
L.push_nla(arm, L.action(arm, "Archivista_Death", 60, loop=False, poses={1: {"root": ((0, 0, 0), Z)}, 25: {"thigh_L": ((40, 0, 0), Z), "shin_L": ((70, 0, 0), Z), "spine": ((25, 0, 10), Z), "root": ((0, 0, 0), (0, 0, -0.5))}, 60: {"root": ((88, 0, 8), (0, -0.6, -1.4)), "spine": ((0, 0, 20), Z), "neck": ((-30, 0, 15), Z), "upperarm_L": ((40, 0, 50), Z)}}))

objs = list(P.values())
blend = L.save_blend(ASSET)
print("built", len(objs))
