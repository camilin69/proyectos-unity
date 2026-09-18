# BOT-02 CUSTODIO-06 (36.2): 2.15 m, tórax ancho con estructura, hombro del arma más voluminoso, placa de reparación al otro lado,
# cuencas estrechas, emisor de rayo con aislantes cerámicos/núcleo/anillos, rodillas que se bloquean, pistones.
import bpy, math, importlib, sys
sys.path.insert(0, r"C:/Users/HP/Documents/GitHub/proyectos-unity/SourceArt/Scripts")
import esn_lib as L; importlib.reload(L)

ASSET = "BOT-02_Custodio"
L.reset_scene()
col = L.collection(ASSET)
M = L.std_mats()
P = {}

# piernas casi humanas, más pesadas; tobillos y rodillas con stops
for side, sx in (("L", -1), ("R", 1)):
    foot = L.box(f"foot_{side}", (0.18, 0.32, 0.07), (sx * 0.19, 0.04, 0.0), col, pivot='bottom', bevel=0.015); L.assign(foot, M['rubber']); P[f"foot_{side}"] = foot
    ankle = L.cyl(f"ankle_{side}", 0.06, 0.12, (sx * 0.19, 0.0, 0.07), col, axis='X'); L.assign(ankle, M['steel_bare']); P[f"ankle_{side}"] = ankle
    shin = L.box(f"shin_{side}", (0.12, 0.14, 0.42), (sx * 0.19, 0.0, 0.1), col, pivot='bottom', bevel=0.02); L.assign(shin, M['steel_paint']); P[f"shin_{side}"] = shin
    piston = L.cyl(f"piston_{side}", 0.018, 0.36, (sx * 0.19 + sx * 0.06, 0.07, 0.12), col, pivot='bottom'); L.assign(piston, M['steel_bare']); P[f"piston_{side}"] = piston
    knee = L.cyl(f"knee_{side}", 0.075, 0.16, (sx * 0.19, 0.0, 0.55), col, axis='X'); L.assign(knee, M['steel_dark']); P[f"knee_{side}"] = knee
    thigh = L.box(f"thigh_{side}", (0.15, 0.18, 0.5), (sx * 0.19, 0.0, 0.55), col, pivot='bottom', bevel=0.025); L.assign(thigh, M['polymer_dark']); P[f"thigh_{side}"] = thigh
# pelvis y tórax con estructura (placas frontales, costillas laterales, panel posterior)
pelvis = L.box("pelvis", (0.44, 0.28, 0.18), (0, 0, 1.05), col, pivot='bottom', bevel=0.03); L.assign(pelvis, M['steel_dark']); P['pelvis'] = pelvis
spine = L.cyl("spine_col", 0.07, 0.16, (0, 0.04, 1.23), col, pivot='bottom'); L.assign(spine, M['rubber']); P['spine_col'] = spine
torso = L.box("torso", (0.62, 0.36, 0.5), (0, 0, 1.36), col, pivot='bottom', bevel=0.04, segs=3); L.assign(torso, M['steel_paint']); P['torso'] = torso
chest = L.box("chest_plate", (0.5, 0.05, 0.36), (0, -0.19, 1.42), col, pivot='bottom', bevel=0.015); L.assign(chest, M['steel_paint']); P['chest_plate'] = chest
repair = L.box("repair_plate", (0.22, 0.03, 0.2), (-0.16, -0.215, 1.48), col, pivot='bottom', bevel=0.006); L.assign(repair, M['steel_bare']); P['repair_plate'] = repair
backp = L.box("back_panel", (0.46, 0.04, 0.4), (0, 0.19, 1.4), col, pivot='bottom', bevel=0.01); L.assign(backp, M['polymer_dark']); P['back_panel'] = backp
ribs = [L.box(f"rib_{i}", (0.03, 0.34, 0.03), (0.325 * (1 if i % 2 == 0 else -1), 0, 1.42 + (i // 2) * 0.1), col) for i in range(6)]
for rb in ribs: L.assign(rb, M['steel_bare'])
P['ribs'] = L.join(ribs, "ribs")
# hombros asimétricos: derecho (arma) voluminoso
shR = L.sphere("shoulder_R", 0.13, (0.4, 0, 1.8), col, scale=(1, 1.1, 0.9)); L.assign(shR, M['steel_paint']); P['shoulder_R'] = shR
shL = L.sphere("shoulder_L", 0.09, (-0.37, 0, 1.8), col); L.assign(shL, M['steel_bare']); P['shoulder_L'] = shL
for side, sx in (("L", -1), ("R", 1)):
    up = L.cyl(f"upperarm_{side}", 0.055 if side == 'L' else 0.07, 0.36, (sx * (0.37 if side == 'L' else 0.4), 0, 1.8), col, pivot='bottom', bevel=0.008); up.rotation_euler = (math.radians(180), 0, 0); L.assign(up, M['polymer_dark']); P[f"upperarm_{side}"] = up
    el = L.cyl(f"elbow_{side}", 0.06, 0.14, (sx * (0.37 if side == 'L' else 0.4), 0, 1.44), col, axis='X'); L.assign(el, M['steel_dark']); P[f"elbow_{side}"] = el
    fa = L.cyl(f"forearm_{side}", 0.05, 0.38, (sx * (0.37 if side == 'L' else 0.4), 0, 1.44), col, pivot='bottom', bevel=0.006); fa.rotation_euler = (math.radians(180), 0, 0); L.assign(fa, M['steel_paint']); P[f"forearm_{side}"] = fa
    hand = L.box(f"hand_{side}", (0.09, 0.05, 0.12), (sx * (0.37 if side == 'L' else 0.4), 0, 1.06), col, pivot='top', bevel=0.01); L.assign(hand, M['polymer_dark']); P[f"hand_{side}"] = hand
    fingers = [L.cyl(f"f_{side}{i}", 0.011, 0.1, (sx * (0.37 if side == 'L' else 0.4) + (i - 1.5) * 0.022, -0.01, 0.94), col, pivot='bottom') for i in range(4)]
    for f in fingers: f.rotation_euler = (math.radians(180), 0, 0); L.assign(f, M['steel_bare'])
    P[f"fingers_{side}"] = L.join(fingers, f"fingers_{side}")
# emisor de rayo en antebrazo derecho: aislantes cerámicos, núcleo, anillos, cables
emitter_base = L.cyl("emitter_base", 0.075, 0.2, (0.4, -0.09, 1.28), col, axis='Y'); L.assign(emitter_base, M['steel_dark']); P['emitter_base'] = emitter_base
for i in range(3):
    ring = L.torus(f"emitter_ring{i}", 0.085, 0.012, (0.4, -0.16 - i * 0.05, 1.28), col, axis='Y'); L.assign(ring, M['ceramic']); P[f"emitter_ring{i}"] = ring
core = L.cyl("emitter_core", 0.03, 0.22, (0.4, -0.2, 1.28), col, axis='Y'); L.assign(core, M['emitter']); P['emitter_core'] = core
ecable = L.tube("emitter_cable", [(0.42, 0.02, 1.32), (0.5, 0.1, 1.5), (0.45, 0.14, 1.7), (0.3, 0.16, 1.82)], 0.009, col); L.assign(ecable, M['rubber']); P['emitter_cable'] = ecable
# cuello y cabeza: placa facial lisa, cuencas estrechas y profundas, línea de unión sin boca
neck = L.cyl("neck", 0.06, 0.1, (0, 0.02, 1.86), col, pivot='bottom'); L.assign(neck, M['rubber']); P['neck'] = neck
head = L.box("head", (0.2, 0.24, 0.26), (0, 0.0, 1.96), col, pivot='bottom', bevel=0.05, segs=4); L.assign(head, M['polymer_ivory'])
for side, sx in (("L", -1), ("R", 1)):
    cut = L.box(f"cut_{side}", (0.03, 0.08, 0.05), (sx * 0.05, -0.11, 2.11), col)
    m = head.modifiers.new(f"Socket_{side}", 'BOOLEAN'); m.operation = 'DIFFERENCE'; m.object = cut
    inner = L.box(f"eye_inner_{side}", (0.026, 0.02, 0.045), (sx * 0.05, -0.085, 2.11), col); L.assign(inner, M['polymer_dark']); P[f"eye_inner_{side}"] = inner
L.apply_all(head)
for side in ("L", "R"): bpy.data.objects.remove(bpy.data.objects[f"cut_{side}"])
seam = L.box("face_seam", (0.16, 0.004, 0.004), (0, -0.121, 2.0), col); L.assign(seam, M['steel_dark']); P['face_seam'] = seam
P['head'] = head

for o in P.values():
    L.apply_all(o); L.smooth(o, 40); L.uv_project(o)

bones = [
    ("root", (0, 0, 0), (0, 0, 0.15), None),
    ("pelvis", (0, 0, 1.05), (0, 0, 1.23), "root"), ("spine", (0, 0, 1.23), (0, 0, 1.86), "pelvis"), ("neck", (0, 0, 1.86), (0, 0, 1.96), "spine"), ("head", (0, 0, 1.96), (0, 0, 2.22), "neck"),
    ("thigh_L", (-0.19, 0, 1.05), (-0.19, 0, 0.55), "pelvis"), ("shin_L", (-0.19, 0, 0.55), (-0.19, 0, 0.07), "thigh_L"), ("foot_L", (-0.19, 0, 0.07), (-0.19, -0.18, 0), "shin_L"),
    ("thigh_R", (0.19, 0, 1.05), (0.19, 0, 0.55), "pelvis"), ("shin_R", (0.19, 0, 0.55), (0.19, 0, 0.07), "thigh_R"), ("foot_R", (0.19, 0, 0.07), (0.19, -0.18, 0), "shin_R"),
    ("upperarm_L", (-0.37, 0, 1.8), (-0.37, 0, 1.44), "spine"), ("forearm_L", (-0.37, 0, 1.44), (-0.37, 0, 1.06), "upperarm_L"), ("hand_L", (-0.37, 0, 1.06), (-0.37, 0, 0.9), "forearm_L"),
    ("upperarm_R", (0.4, 0, 1.8), (0.4, 0, 1.44), "spine"), ("forearm_R", (0.4, 0, 1.44), (0.4, 0, 1.06), "upperarm_R"), ("hand_R", (0.4, 0, 1.06), (0.4, 0, 0.9), "forearm_R"),
]
arm = L.armature("Armature_Custodio", bones, col)
binding = {
    "pelvis": ["pelvis", "spine_col"], "spine": ["torso", "chest_plate", "repair_plate", "back_panel", "ribs", "shoulder_R", "shoulder_L"], "neck": ["neck"],
    "head": ["head", "eye_inner_L", "eye_inner_R", "face_seam"],
    "thigh_L": ["thigh_L", "knee_L", "piston_L"], "shin_L": ["shin_L", "ankle_L"], "foot_L": ["foot_L"], "thigh_R": ["thigh_R", "knee_R", "piston_R"], "shin_R": ["shin_R", "ankle_R"], "foot_R": ["foot_R"],
    "upperarm_L": ["upperarm_L", "elbow_L"], "forearm_L": ["forearm_L"], "hand_L": ["hand_L", "fingers_L"],
    "upperarm_R": ["upperarm_R", "elbow_R"], "forearm_R": ["forearm_R", "emitter_base", "emitter_ring0", "emitter_ring1", "emitter_ring2", "emitter_core", "emitter_cable"], "hand_R": ["hand_R", "fingers_R"],
}
for bone, names in binding.items():
    for n in names: L.bind_rigid(P[n], arm, bone)

Z = (0, 0, 0)
L.push_nla(arm, L.action(arm, "Custodio_Idle", 100, poses={1: {"head": ((0, 0, 0), Z), "spine": ((0, 0, 0), Z)}, 50: {"head": ((3, 0, -5), Z), "spine": ((1.5, 0, 0), Z), "hand_R": ((6, 0, 0), Z)}, 100: {"head": ((0, 0, 0), Z), "spine": ((0, 0, 0), Z), "hand_R": ((0, 0, 0), Z)}}))
L.push_nla(arm, L.action(arm, "Custodio_Walk", 48, poses={
    1: {"thigh_L": ((-22, 0, 0), Z), "thigh_R": ((22, 0, 0), Z), "shin_L": ((28, 0, 0), Z), "shin_R": ((0, 0, 0), Z), "spine": ((4, 0, -3), Z), "head": ((-2, 0, 4), Z), "upperarm_L": ((12, 0, 0), Z), "upperarm_R": ((-12, 0, 0), Z), "root": ((0, 0, 0), (0, 0, 0))},
    12: {"root": ((0, 0, 0), (0, 0, 0.02))},
    24: {"thigh_L": ((22, 0, 0), Z), "thigh_R": ((-22, 0, 0), Z), "shin_L": ((0, 0, 0), Z), "shin_R": ((28, 0, 0), Z), "spine": ((4, 0, 3), Z), "head": ((-2, 0, -3), Z), "upperarm_L": ((-12, 0, 0), Z), "upperarm_R": ((12, 0, 0), Z), "root": ((0, 0, 0), (0, 0, 0))},
    36: {"root": ((0, 0, 0), (0, 0, 0.02))},
    48: {"thigh_L": ((-22, 0, 0), Z), "thigh_R": ((22, 0, 0), Z), "shin_L": ((28, 0, 0), Z), "shin_R": ((0, 0, 0), Z), "spine": ((4, 0, -3), Z), "head": ((-2, 0, 4), Z), "upperarm_L": ((12, 0, 0), Z), "upperarm_R": ((-12, 0, 0), Z), "root": ((0, 0, 0), (0, 0, 0))}}))
# aviso de rayo 1.0 s (60.3): brazo levantado, chispas breves, sin deslizar
L.push_nla(arm, L.action(arm, "Custodio_Anticipation", 30, loop=False, poses={1: {"upperarm_R": ((0, 0, 0), Z), "forearm_R": ((0, 0, 0), Z), "spine": ((0, 0, 0), Z)}, 10: {"upperarm_R": ((-60, 0, -15), Z), "forearm_R": ((-35, 0, 0), Z), "spine": ((-4, 0, -6), Z)}, 30: {"upperarm_R": ((-90, 0, -10), Z), "forearm_R": ((-10, 0, 0), Z), "spine": ((-6, 0, -8), Z), "head": ((4, 0, 0), Z)}}))
L.push_nla(arm, L.action(arm, "Custodio_Bolt", 48, loop=False, poses={1: {"upperarm_R": ((-90, 0, -10), Z), "forearm_R": ((-10, 0, 0), Z), "spine": ((-6, 0, -8), Z)}, 4: {"upperarm_R": ((-80, 0, -6), Z), "spine": ((3, 0, -4), Z)}, 48: {"upperarm_R": ((0, 0, 0), Z), "forearm_R": ((0, 0, 0), Z), "spine": ((0, 0, 0), Z), "head": ((0, 0, 0), Z)}}))
L.push_nla(arm, L.action(arm, "Custodio_Stagger", 9, loop=False, poses={1: {"spine": ((0, 0, 0), Z)}, 4: {"spine": ((12, 0, 6), Z), "head": ((10, 0, 0), Z)}, 9: {"spine": ((0, 0, 0), Z), "head": ((0, 0, 0), Z)}}))
L.push_nla(arm, L.action(arm, "Custodio_Death", 45, loop=False, poses={1: {"root": ((0, 0, 0), Z)}, 18: {"thigh_L": ((35, 0, 0), Z), "shin_L": ((60, 0, 0), Z), "spine": ((20, 0, 8), Z), "root": ((0, 0, 0), (0, 0, -0.3))}, 45: {"root": ((85, 0, 10), (0, -0.4, -1.0)), "spine": ((5, 0, 15), Z), "head": ((-15, 0, 20), Z), "upperarm_R": ((30, 0, 40), Z)}}))

objs = list(P.values())
blend = L.save_blend(ASSET)
print("built", len(objs))
