# CHR-01 brazos de Esneider (35: falanges, nudillos, tendones, pliegue de muñeca, manga con puño y pulsera) + armas Tier A (38):
# varilla con doblez y agarre descubierto, pistola con corredera/cargador/gatillo/guardamonte, escopeta con bombeo/culata/puerto,
# linterna con lente/reflector/switch, jeringa y ración. Cada arma es un asset propio con pivote en el punto de agarre.
import bpy, math, importlib, sys
sys.path.insert(0, r"C:/Users/HP/Documents/GitHub/proyectos-unity/SourceArt/Scripts")
import esn_lib as L; importlib.reload(L)
from mathutils import Vector

WHICH = globals().get("WHICH", "arms")
L.reset_scene()
M = L.std_mats()
M['skin'] = L.material("M_Skin", (0.72, 0.52, 0.42), 0.48, 0.0, bump=0.06, scale=40)
M['nail'] = L.material("M_Nail", (0.8, 0.66, 0.6), 0.3, 0.0)
M['sleeve'] = L.material("M_Sleeve", (0.3, 0.34, 0.38), 0.85, 0.0, wear=0.2, wear_color=(0.22, 0.24, 0.26), bump=0.35, scale=60)
M['band'] = L.material("M_Band", (0.85, 0.85, 0.82), 0.55, 0.0)
M['wood'] = L.material("M_Wood", (0.36, 0.24, 0.14), 0.7, 0.0, bump=0.25, scale=14)
M['grip'] = L.material("M_Grip", (0.1, 0.1, 0.1), 0.8, 0.0, bump=0.4, scale=50)
M['brass'] = L.material("M_Brass", (0.8, 0.62, 0.3), 0.35, 1.0)
M['plastic_red'] = L.material("M_PlasticRed", (0.6, 0.12, 0.1), 0.45, 0.0, bump=0.05)
M['liquid'] = L.material("M_Liquid", (0.35, 0.75, 0.6), 0.1, 0.0, emission=((0.2, 0.5, 0.4), 0.3))
M['foil'] = L.material("M_Foil", (0.5, 0.55, 0.45), 0.4, 0.6, bump=0.5, scale=45)


def finger(col, name, base, dirv, lengths, radius, curl=0.0, mats=None):
    """Falanges con nudillos y uña con espesor; curl en grados por articulación."""
    parts = []
    p = Vector(base); d = Vector(dirv).normalized()
    up = Vector((0, 0, 1))
    for i, ln in enumerate(lengths):
        r = radius * (1 - 0.12 * i)
        seg = L.cyl(f"{name}_ph{i}", r, ln, (0, 0, 0), col, verts=12, bevel=r * 0.3)
        seg.data.transform(L.Matrix.Translation((0, 0, ln / 2)))
        seg.location = p; seg.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
        L.assign(seg, M['skin']); parts.append(seg)
        kn = L.sphere(f"{name}_kn{i}", r * 1.08, p, col, segs=12, rings=8, scale=(1, 1.15, 0.9)); L.assign(kn, M['skin']); parts.append(kn)
        p = p + d * ln
        d = (L.Matrix.Rotation(math.radians(-curl), 3, d.cross(up).normalized() if d.cross(up).length > 1e-3 else Vector((1, 0, 0))) @ d).normalized()
    tip = L.sphere(f"{name}_tip", radius * 0.75, p, col, segs=12, rings=8); L.assign(tip, M['skin']); parts.append(tip)
    nail = L.box(f"{name}_nail", (radius * 1.1, radius * 1.2, radius * 0.25), p + Vector((0, 0, radius * 0.55)), col, bevel=radius * 0.06); L.assign(nail, M['nail']); parts.append(nail)
    return parts


def build_arm(col, side, sx):
    parts = []
    # antebrazo con manga (uniforme), puño con ribete, pliegue de muñeca, palma, pulgar y cuatro dedos
    fore = L.cyl(f"forearm_{side}", 0.045, 0.27, (sx * 0.2, -0.3, 0.0), col, axis='Y', verts=20, bevel=0.01); L.assign(fore, M['sleeve']); parts.append(fore)
    cuff = L.torus(f"cuff_{side}", 0.048, 0.008, (sx * 0.2, -0.43, 0.0), col, axis='Y'); L.assign(cuff, M['sleeve']); parts.append(cuff)
    band = L.torus(f"wristband_{side}", 0.042, 0.005, (sx * 0.2, -0.47, 0.0), col, axis='Y'); L.assign(band, M['band']); parts.append(band)
    wrist = L.cyl(f"wrist_{side}", 0.036, 0.06, (sx * 0.2, -0.47, 0.0), col, axis='Y', verts=16, bevel=0.008); L.assign(wrist, M['skin']); parts.append(wrist)
    palm = L.box(f"palm_{side}", (0.085, 0.1, 0.03), (sx * 0.2, -0.55, 0.0), col, bevel=0.012, segs=3); L.assign(palm, M['skin']); parts.append(palm)
    tendons = [L.cyl(f"tendon_{side}{i}", 0.004, 0.07, (sx * 0.2 + (i - 1.5) * 0.017, -0.545, 0.016), col, axis='Y', verts=8) for i in range(4)]
    for t in tendons: L.assign(t, M['skin'])
    parts.append(L.join(tendons, f"tendons_{side}"))
    for i in range(4):
        x = sx * 0.2 + (i - 1.5) * 0.02
        ln = [0.045, 0.028, 0.022] if i in (1, 2) else [0.04, 0.025, 0.02]
        parts += finger(col, f"finger_{side}{i}", (x, -0.6, 0.0), (0, -1, 0), ln, 0.009, curl=12)
    parts += finger(col, f"thumb_{side}", (sx * 0.2 + sx * 0.045, -0.53, -0.005), (sx * 0.7, -0.7, 0), [0.04, 0.03], 0.011, curl=15)
    return parts


if WHICH == "arms":
    ASSET = "CHR-01_Arms"; col = L.collection(ASSET); P = []
    P += build_arm(col, "L", -1); P += build_arm(col, "R", 1)
    for o in P: L.apply_all(o); L.smooth(o, 45); L.uv_project(o, 0.01)
    bones = [("root", (0, 0, 0), (0, -0.1, 0), None)]
    for side, sx in (("L", -1), ("R", 1)):
        bones += [(f"forearm_{side}", (sx * 0.2, -0.16, 0), (sx * 0.2, -0.47, 0), "root"), (f"hand_{side}", (sx * 0.2, -0.47, 0), (sx * 0.2, -0.6, 0), f"forearm_{side}")]
        for i in range(4): bones.append((f"finger_{side}{i}", (sx * 0.2 + (i - 1.5) * 0.02, -0.6, 0), (sx * 0.2 + (i - 1.5) * 0.02, -0.69, 0), f"hand_{side}"))
        bones.append((f"thumb_{side}", (sx * 0.245, -0.53, 0), (sx * 0.29, -0.58, 0), f"hand_{side}"))
    arm = L.armature("Armature_Arms", bones, col)
    for o in P:
        n = o.name; side = 'L' if '_L' in n else 'R'
        if n.startswith("finger_") or n.startswith("thumb_"):
            key = n.split("_ph")[0].split("_kn")[0].split("_tip")[0].split("_nail")[0]
            bone = key if key in arm.data.bones else f"hand_{side}"
        elif n.startswith(("forearm", "cuff")): bone = f"forearm_{side}"
        else: bone = f"hand_{side}"
        L.bind_rigid(o, arm, bone)
    Z = (0, 0, 0)
    fingers_all = {f"finger_{s}{i}": ((0, 0, 0), Z) for s in "LR" for i in range(4)}
    grip = {f"finger_{s}{i}": ((-70, 0, 0), Z) for s in "LR" for i in range(4)}
    L.push_nla(arm, L.action(arm, "Arms_Idle", 90, poses={1: {"root": ((0, 0, 0), Z)}, 45: {"root": ((1, 0, 0), (0, 0, -0.004))}, 90: {"root": ((0, 0, 0), Z)}}))
    L.push_nla(arm, L.action(arm, "Arms_Grip", 10, loop=False, poses={1: fingers_all, 10: grip}))
    L.push_nla(arm, L.action(arm, "Arms_CrowbarSwing", 26, loop=False, poses={1: {"forearm_R": ((0, 0, 0), Z)}, 6: {"forearm_R": ((-35, 0, 15), (0, 0.05, 0.05))}, 11: {"forearm_R": ((30, 0, -25), (0, -0.08, -0.05))}, 26: {"forearm_R": ((0, 0, 0), Z)}}))
    L.push_nla(arm, L.action(arm, "Arms_PistolReload", 57, loop=False, poses={1: {"forearm_L": ((0, 0, 0), Z), "forearm_R": ((0, 0, 0), Z)}, 11: {"forearm_L": ((-20, 0, 30), (0.08, 0.05, -0.02))}, 21: {"forearm_L": ((-30, 0, 40), (0.1, 0.1, -0.08))}, 41: {"forearm_L": ((-10, 0, 20), (0.06, 0.04, -0.02)), "forearm_R": ((-8, 0, 0), Z)}, 57: {"forearm_L": ((0, 0, 0), Z), "forearm_R": ((0, 0, 0), Z)}}))
    L.push_nla(arm, L.action(arm, "Arms_Syringe", 48, loop=False, poses={1: {"forearm_R": ((0, 0, 0), Z), "forearm_L": ((0, 0, 0), Z)}, 20: {"forearm_R": ((-25, 0, -30), (-0.1, 0.05, 0.05)), "forearm_L": ((-40, 0, 20), (0.05, 0.1, 0.05))}, 33: {"forearm_R": ((-30, 0, -35), (-0.12, 0.04, 0.03))}, 48: {"forearm_R": ((0, 0, 0), Z), "forearm_L": ((0, 0, 0), Z)}}))
    L.save_blend(ASSET); print("built arms", len(P))

elif WHICH == "crowbar":
    ASSET = "WPN-01_Crowbar"; col = L.collection(ASSET); P = []
    shaft = L.cyl("shaft", 0.011, 0.62, (0, 0, 0), col, axis='Y', verts=8, bevel=0.002); L.assign(shaft, M['steel_paint']); P.append(shaft)
    grip = L.cyl("grip_worn", 0.0115, 0.16, (0, -0.2, 0), col, axis='Y', verts=8); L.assign(grip, M['steel_bare']); P.append(grip)
    bend = L.tube("bend", [(0, 0.31, 0), (0, 0.36, 0.02), (0, 0.4, 0.06), (0, 0.41, 0.1)], 0.011, col); L.assign(bend, M['steel_paint']); P.append(bend)
    tip = L.box("tip_flat", (0.03, 0.012, 0.05), (0, 0.41, 0.125), col, bevel=0.003); L.assign(tip, M['steel_bare']); P.append(tip)
    heel = L.box("heel_flat", (0.028, 0.03, 0.01), (0, -0.315, 0.004), col, rot=(math.radians(15), 0, 0), bevel=0.002); L.assign(heel, M['steel_bare']); P.append(heel)
    for o in P: L.apply_all(o); L.smooth(o, 40); L.uv_project(o, 0.01)
    L.save_blend(ASSET); print("built crowbar")

elif WHICH == "pistol":
    ASSET = "WPN-02_Pistol"; col = L.collection(ASSET); P = []
    frame = L.box("frame", (0.03, 0.14, 0.03), (0, 0.02, 0.0), col, bevel=0.004); L.assign(frame, M['polymer_dark']); P.append(frame)
    slide = L.box("slide", (0.03, 0.18, 0.028), (0, 0.03, 0.03), col, bevel=0.004); L.assign(slide, M['steel_dark']); P.append(slide)
    barrel = L.cyl("barrel", 0.006, 0.05, (0, 0.135, 0.032), col, axis='Y', verts=12); L.assign(barrel, M['steel_bare']); P.append(barrel)
    serr = [L.box(f"serr{i}", (0.032, 0.002, 0.01), (0, -0.045 + i * 0.006, 0.038), col) for i in range(6)]
    for s in serr: L.assign(s, M['steel_bare'])
    P.append(L.join(serr, "serrations"))
    gripb = L.box("grip", (0.03, 0.04, 0.1), (0, -0.04, -0.06), col, rot=(math.radians(-15), 0, 0), bevel=0.006); L.assign(gripb, M['grip']); P.append(gripb)
    mag = L.box("magazine", (0.022, 0.03, 0.11), (0, -0.042, -0.07), col, rot=(math.radians(-15), 0, 0), bevel=0.002); L.assign(mag, M['steel_dark']); P.append(mag)
    guard = L.torus("trigger_guard", 0.02, 0.003, (0, 0.02, -0.03), col, axis='X', segs=20, rings=8); L.assign(guard, M['polymer_dark']); P.append(guard)
    trig = L.box("trigger", (0.006, 0.005, 0.02), (0, 0.02, -0.025), col, rot=(math.radians(10), 0, 0)); L.assign(trig, M['steel_bare']); P.append(trig)
    hammer = L.box("hammer", (0.01, 0.012, 0.02), (0, -0.07, 0.03), col, rot=(math.radians(-25), 0, 0), bevel=0.002); L.assign(hammer, M['steel_bare']); P.append(hammer)
    screws = [L.cyl(f"screw{i}", 0.003, 0.002, (0.016, -0.03 + i * 0.05, 0.0), col, axis='X', verts=8) for i in range(3)]
    for s in screws: L.assign(s, M['steel_bare'])
    P.append(L.join(screws, "screws"))
    for o in P: L.apply_all(o); L.smooth(o, 40); L.uv_project(o, 0.01)
    L.save_blend(ASSET); print("built pistol")

elif WHICH == "shotgun":
    ASSET = "WPN-03_Shotgun"; col = L.collection(ASSET); P = []
    receiver = L.box("receiver", (0.04, 0.2, 0.06), (0, 0.0, 0.0), col, bevel=0.005); L.assign(receiver, M['steel_dark']); P.append(receiver)
    barrel = L.cyl("barrel", 0.011, 0.5, (0, 0.35, 0.02), col, axis='Y', verts=16); L.assign(barrel, M['steel_dark']); P.append(barrel)
    tube = L.cyl("mag_tube", 0.012, 0.42, (0, 0.31, -0.012), col, axis='Y', verts=16); L.assign(tube, M['steel_dark']); P.append(tube)
    pump = L.cyl("pump", 0.02, 0.14, (0, 0.28, -0.012), col, axis='Y', verts=16, bevel=0.004); L.assign(pump, M['wood']); P.append(pump)
    ridges = [L.torus(f"ridge{i}", 0.021, 0.0015, (0, 0.23 + i * 0.02, -0.012), col, axis='Y', segs=16, rings=6) for i in range(5)]
    for r in ridges: L.assign(r, M['wood'])
    P.append(L.join(ridges, "pump_ridges"))
    port = L.box("eject_port", (0.005, 0.05, 0.02), (0.021, 0.03, 0.01), col); L.assign(port, M['steel_bare']); P.append(port)
    loadport = L.box("load_port", (0.02, 0.05, 0.004), (0, -0.02, -0.031), col); L.assign(loadport, M['steel_bare']); P.append(loadport)
    stock = L.box("stock", (0.035, 0.24, 0.07), (0, -0.22, -0.02), col, rot=(math.radians(8), 0, 0), bevel=0.01, segs=3); L.assign(stock, M['wood']); P.append(stock)
    gripb = L.box("pistol_grip", (0.03, 0.05, 0.09), (0, -0.09, -0.06), col, rot=(math.radians(-20), 0, 0), bevel=0.006); L.assign(gripb, M['wood']); P.append(gripb)
    guard = L.torus("trigger_guard", 0.022, 0.003, (0, -0.03, -0.035), col, axis='X', segs=20, rings=8); L.assign(guard, M['steel_dark']); P.append(guard)
    trig = L.box("trigger", (0.006, 0.005, 0.022), (0, -0.03, -0.03), col); L.assign(trig, M['steel_bare']); P.append(trig)
    sight = L.box("front_sight", (0.004, 0.01, 0.01), (0, 0.58, 0.035), col); L.assign(sight, M['brass']); P.append(sight)
    for o in P: L.apply_all(o); L.smooth(o, 40); L.uv_project(o, 0.01)
    L.save_blend(ASSET); print("built shotgun")

elif WHICH == "flashlight":
    ASSET = "WPN-04_Flashlight"; col = L.collection(ASSET); P = []
    body = L.cyl("body", 0.018, 0.16, (0, 0.0, 0), col, axis='Y', verts=20, bevel=0.003); L.assign(body, M['steel_paint']); P.append(body)
    head = L.cyl("head", 0.026, 0.05, (0, 0.1, 0), col, axis='Y', verts=20, bevel=0.004); L.assign(head, M['steel_dark']); P.append(head)
    reflector = L.cyl("reflector", 0.022, 0.01, (0, 0.122, 0), col, axis='Y', verts=20); L.assign(reflector, M['steel_bare']); P.append(reflector)
    lens = L.cyl("lens", 0.0225, 0.004, (0, 0.128, 0), col, axis='Y', verts=20); L.assign(lens, M['glass']); P.append(lens)
    gasket = L.torus("gasket", 0.024, 0.0025, (0, 0.125, 0), col, axis='Y', segs=20, rings=6); L.assign(gasket, M['rubber']); P.append(gasket)
    switch = L.box("switch", (0.012, 0.018, 0.006), (0, -0.02, 0.019), col, bevel=0.002); L.assign(switch, M['rubber']); P.append(switch)
    knurl = [L.torus(f"knurl{i}", 0.0185, 0.001, (0, -0.06 + i * 0.008, 0), col, axis='Y', segs=20, rings=6) for i in range(5)]
    for k in knurl: L.assign(k, M['rubber'])
    P.append(L.join(knurl, "knurling"))
    for o in P: L.apply_all(o); L.smooth(o, 40); L.uv_project(o, 0.01)
    L.save_blend(ASSET); print("built flashlight")

elif WHICH == "syringe":
    ASSET = "PRP-Syringe"; col = L.collection(ASSET); P = []
    body = L.cyl("body", 0.009, 0.09, (0, 0, 0), col, axis='Y', verts=16); L.assign(body, M['glass']); P.append(body)
    liquid = L.cyl("liquid", 0.0075, 0.05, (0, -0.015, 0), col, axis='Y', verts=16); L.assign(liquid, M['liquid']); P.append(liquid)
    plunger = L.cyl("plunger", 0.004, 0.09, (0, -0.06, 0), col, axis='Y', verts=10); L.assign(plunger, M['polymer_ivory']); P.append(plunger)
    thumb = L.cyl("plunger_head", 0.012, 0.004, (0, -0.105, 0), col, axis='Y', verts=16); L.assign(thumb, M['polymer_ivory']); P.append(thumb)
    flange = L.box("flange", (0.03, 0.003, 0.012), (0, -0.045, 0), col); L.assign(flange, M['polymer_ivory']); P.append(flange)
    cap = L.cyl("cap", 0.006, 0.03, (0, 0.06, 0), col, axis='Y', verts=12); L.assign(cap, M['plastic_red']); P.append(cap)
    for o in P: L.apply_all(o); L.smooth(o, 40); L.uv_project(o, 0.01)
    L.save_blend(ASSET); print("built syringe")

elif WHICH == "ration":
    ASSET = "PRP-Ration"; col = L.collection(ASSET); P = []
    pack = L.box("pack", (0.12, 0.2, 0.04), (0, 0, 0), col, bevel=0.012, segs=3); L.assign(pack, M['foil']); P.append(pack)
    seal = L.box("seal", (0.12, 0.02, 0.002), (0, 0.105, 0), col); L.assign(seal, M['foil']); P.append(seal)
    label = L.box("label", (0.08, 0.1, 0.001), (0, 0.0, 0.021), col); L.assign(label, M['band']); P.append(label)
    for o in P: L.apply_all(o); L.smooth(o, 40); L.uv_project(o, 0.01)
    L.save_blend(ASSET); print("built ration")
