# CHR-01 brazos de Esneider (35: falanges, nudillos, tendones, pliegue de muñeca, manga con puño y pulsera) + armas Tier A (38):
# varilla con doblez y agarre descubierto, pistola con corredera/cargador/gatillo/guardamonte, escopeta con bombeo/culata/puerto,
# linterna con lente/reflector/switch, jeringa y ración. Cada arma es un asset propio con pivote en el punto de agarre.
#
# 38/43: todo lo de este archivo se ve A CENTÍMETROS de la cámara. El presupuesto es de viewmodel, no de prop lejano, y el
# detalle se modela como pieza fabricada (33.2 jerarquía de detalle, 41.3 desgaste por causa): tornillos donde algo se
# atornilla, juntas donde dos piezas se encuentran, rejillas donde algo respira, refuerzos donde hay carga y metal desnudo
# donde la mano roza. Nada de grunge decorativo.
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


def ring_boxes(col, name, count, center, radius, size, mat, axis='Y', phase=0.0, bevel=0.0, segs=1):
    """Anillo de piezas pequeñas repetidas alrededor de un eje, unidas en un solo objeto.

    Es la pieza que falta en la biblioteca para el moleteado de la linterna, las estrías del bombeo y el
    pespunte del puño: detalle REAL (cambia la silueta y el bake) sin el coste de rib_row en cada elemento.
    `size` se da en el marco local de cada pieza: (radial, axial, tangencial). Ejes soportados: 'Y' y 'Z'.
    """
    cx, cy, cz = center
    parts = []
    for i in range(count):
        a = 2 * math.pi * i / count + phase
        if axis == 'Y':
            p = (cx + radius * math.cos(a), cy, cz + radius * math.sin(a)); rot = (0, -a, 0)
        else:
            p = (cx + radius * math.cos(a), cy + radius * math.sin(a), cz); rot = (0, 0, a)
        b = L.box(f"{name}_r{i}", size, p, col, rot=rot, bevel=bevel, segs=segs)
        L.assign(b, mat); parts.append(b)
    return L.join(parts, name)


FINGER_JOINTS = {}   # nombre del dedo -> puntos de articulación, para construir el rig sobre la misma geometría


def phalanx_bone(name, index):
    """Nombre del hueso de la falange `index` del dedo `name`: el primero conserva el nombre del dedo."""
    return name if index == 0 else name + chr(ord('a') + index)


def finger(col, name, base, dirv, lengths, radius, curl=0.0):
    """Dedo con UNA PIEZA POR FALANGE y un hueso por falange (35.1 + 36.4).

    Antes el dedo se unía en una sola pieza atada a un único hueso, y eso hace imposible el agarre: por mucho que
    se cierre, el dedo gira rígido alrededor del nudillo y la punta describe un arco que pasa de largo del mango.
    Medido sobre el modelo importado, con el puño cerrado a -70° las puntas quedaban a 80-126 mm de la empuñadura.
    Con tres falanges encadenadas la punta sí llega a la palma.

    Devuelve (piezas, articulaciones); las articulaciones son las cabezas de cada falange más la punta, y el rig se
    construye con esos mismos puntos para que hueso y geometría no puedan desalinearse.
    """
    groups = [[] for _ in lengths]
    joints = []
    p = Vector(base); d = Vector(dirv).normalized()
    up = Vector((0, 0, 1))
    for i, ln in enumerate(lengths):
        joints.append(p.copy())
        r = radius * (1 - 0.12 * i)
        rot = d.to_track_quat('Z', 'Y').to_euler()
        seg = L.cyl(f"{name}_ph{i}", r, ln, (0, 0, 0), col, verts=12, bevel=r * 0.3)
        seg.data.transform(L.Matrix.Translation((0, 0, ln / 2)))
        seg.location = p; seg.rotation_euler = rot
        L.assign(seg, M['skin']); groups[i].append(seg)
        # cabeza articular: más ancha que la falange, es lo que da el perfil de nudillo al cerrar la mano
        kn = L.sphere(f"{name}_kn{i}", r * 1.1, p, col, segs=12, rings=6, scale=(1.05, 1.15, 0.9))
        L.assign(kn, M['skin']); groups[i].append(kn)
        # pliegue palmar: la piel se arruga SOLO en la cara que se comprime al doblar (41.3 causa)
        if i > 0:
            cr = L.box(f"{name}_ph{i}f", (r * 1.9, r * 0.55, r * 0.32), p - Vector((0, 0, r * 0.8)), col, rot=rot, bevel=r * 0.09, segs=1)
            L.assign(cr, M['skin']); groups[i].append(cr)
        p = p + d * ln
        d = (L.Matrix.Rotation(math.radians(-curl), 3, d.cross(up).normalized() if d.cross(up).length > 1e-3 else Vector((1, 0, 0))) @ d).normalized()
    joints.append(p.copy())
    last = groups[-1]
    tip = L.sphere(f"{name}_tip", radius * 0.78, p, col, segs=12, rings=8, scale=(1, 1.1, 0.85))
    L.assign(tip, M['skin']); last.append(tip)
    # pulpejo: almohadilla palmar de la falange distal, la que aplasta contra el grip
    pad = L.sphere(f"{name}_tipp", radius * 0.72, p + Vector((0, radius * 0.3, -radius * 0.42)), col, segs=10, rings=5, scale=(1.15, 1.35, 0.55))
    L.assign(pad, M['skin']); last.append(pad)
    # lecho ungueal: la uña se APOYA en una cama de piel con paredes laterales y eponiquio, no flota
    bed = L.box(f"{name}_nailbed", (radius * 1.45, radius * 1.7, radius * 0.42), p + Vector((0, radius * 0.6, radius * 0.4)), col, bevel=radius * 0.13, segs=2)
    L.assign(bed, M['skin']); last.append(bed)
    plate = L.box(f"{name}_nail", (radius * 1.12, radius * 1.4, radius * 0.22), p + Vector((0, radius * 0.6, radius * 0.6)), col, bevel=radius * 0.07, segs=2)
    L.assign(plate, M['nail']); last.append(plate)
    epo = L.box(f"{name}_nailc", (radius * 1.45, radius * 0.3, radius * 0.3), p + Vector((0, radius * 1.25, radius * 0.56)), col, bevel=radius * 0.08, segs=1)
    L.assign(epo, M['skin']); last.append(epo)
    for k, sxn in ((0, -1), (1, 1)):
        wall = L.box(f"{name}_nailw{k}", (radius * 0.26, radius * 1.45, radius * 0.28), p + Vector((sxn * radius * 0.6, radius * 0.6, radius * 0.56)), col, bevel=radius * 0.07, segs=1)
        L.assign(wall, M['skin']); last.append(wall)
    FINGER_JOINTS[name] = joints
    return [L.join(g, phalanx_bone(name, i)) for i, g in enumerate(groups)], joints


def build_arm(col, side, sx):
    """Un brazo = 11 piezas agrupadas por hueso. Mantiene exactamente los anclajes del rig anterior:
    antebrazo en y=-0.30, puño -0.43, muñeca -0.47, palma -0.55, dedos desde -0.60."""
    cx = sx * 0.2
    out = []

    # ---- manga: tubo, costuras del paño y pliegues donde el tejido se acumula (35.1) ----
    g = []
    fore = L.cyl(f"forearm_{side}", 0.045, 0.27, (cx, -0.3, 0.0), col, axis='Y', verts=20, bevel=0.008)
    L.assign(fore, M['sleeve']); g.append(fore)
    for k, ox in enumerate((0.0452, -0.0452)):
        g.append(L.panel_seam(f"forearm_seam{k}_{side}", 0.25, (cx + ox, -0.3, 0), col, axis='Y', width=0.005, depth=0.005, mat=M['sleeve']))
    for k, y in enumerate((-0.205, -0.315, -0.395)):
        pl = L.torus(f"forearm_pleat{k}_{side}", 0.0452, 0.004, (cx, y, 0), col, axis='Y', segs=18, rings=6)
        L.assign(pl, M['sleeve']); g.append(pl)
    out.append(L.join(g, f"forearm_{side}"))

    # ---- puño: ribete con espesor y pespunte real (el borde que más se desgasta) ----
    g = []
    cuff = L.torus(f"cuff_{side}", 0.048, 0.008, (cx, -0.43, 0), col, axis='Y', segs=20, rings=8)
    L.assign(cuff, M['sleeve']); g.append(cuff)
    hem = L.cyl(f"cuff_hem_{side}", 0.0503, 0.018, (cx, -0.4265, 0), col, axis='Y', verts=20, bevel=0.003)
    L.assign(hem, M['sleeve']); g.append(hem)
    g.append(ring_boxes(col, f"cuff_stitch_{side}", 16, (cx, -0.4405, 0), 0.0492, (0.0012, 0.0016, 0.0032), M['sleeve'], axis='Y'))
    out.append(L.join(g, f"cuff_{side}"))

    # ---- pulsera identificadora (35.1: legible al levantar un documento o usar la jeringa) ----
    g = []
    band = L.torus(f"wristband_{side}", 0.042, 0.005, (cx, -0.47, 0), col, axis='Y', segs=20, rings=8)
    L.assign(band, M['band']); g.append(band)
    plate = L.box(f"wristband_tag_{side}", (0.022, 0.016, 0.005), (cx, -0.47, 0.0425), col, bevel=0.0012, segs=2)
    L.assign(plate, M['screen']); g.append(plate)
    out.append(L.join(g, f"wristband_{side}"))

    # ---- muñeca con sus dos pliegues ----
    g = []
    wr = L.cyl(f"wrist_{side}", 0.036, 0.06, (cx, -0.47, 0), col, axis='Y', verts=16, bevel=0.006)
    L.assign(wr, M['skin']); g.append(wr)
    for k, y in enumerate((-0.486, -0.495)):
        fo = L.torus(f"wrist_fold{k}_{side}", 0.0355, 0.0035, (cx, y, 0), col, axis='Y', segs=16, rings=5)
        L.assign(fo, M['skin']); g.append(fo)
    out.append(L.join(g, f"wrist_{side}"))

    # ---- palma: eminencias tenar/hipotenar, almohadillas metacarpianas y tendones extensores ----
    g = []
    palm = L.box(f"palm_{side}", (0.085, 0.1, 0.03), (cx, -0.55, 0.0), col, bevel=0.012, segs=3)
    L.assign(palm, M['skin']); g.append(palm)
    L.chamfer(palm, 0.0012, 2, 55)
    for k, (ox, sc) in enumerate(((sx * 0.027, (1.0, 1.5, 0.62)), (-sx * 0.029, (0.85, 1.35, 0.55)))):
        m = L.sphere(f"palm_heel{k}_{side}", 0.019, (cx + ox, -0.545, -0.0135), col, segs=12, rings=6, scale=sc)
        L.assign(m, M['skin']); g.append(m)
    for i in range(4):
        pd = L.sphere(f"palm_pad{i}_{side}", 0.0105, (cx + (i - 1.5) * 0.02, -0.588, -0.013), col, segs=10, rings=5, scale=(1.0, 0.85, 0.45))
        L.assign(pd, M['skin']); g.append(pd)
    for i in range(4):
        t = L.cyl(f"palm_tendon{i}_{side}", 0.004, 0.075, (cx + (i - 1.5) * 0.017, -0.545, 0.0155), col, axis='Y', verts=8)
        L.assign(t, M['skin']); g.append(t)
    out.append(L.join(g, f"palm_{side}"))

    # ---- membranas interdigitales: sin ellas los dedos parecen cuatro tubos pegados (35.1) ----
    g = []
    for i in range(3):
        w = L.sphere(f"web_{side}{i}", 0.009, (cx + (i - 1.0) * 0.02, -0.599, -0.004), col, segs=10, rings=5, scale=(1.5, 0.9, 0.38))
        L.assign(w, M['skin']); g.append(w)
    tw = L.sphere(f"web_{side}t", 0.012, (cx + sx * 0.031, -0.567, -0.008), col, segs=10, rings=5, scale=(1.2, 1.2, 0.4))
    L.assign(tw, M['skin']); g.append(tw)
    out.append(L.join(g, f"web_{side}"))

    # ---- dedos: mismas bases y longitudes que antes, así el rig y el agarre no se mueven ----
    for i in range(4):
        x = cx + (i - 1.5) * 0.02
        ln = [0.045, 0.028, 0.022] if i in (1, 2) else [0.04, 0.025, 0.02]
        out += finger(col, f"finger_{side}{i}", (x, -0.6, 0.0), (0, -1, 0), ln, 0.009, curl=12)[0]
    out += finger(col, f"thumb_{side}", (cx + sx * 0.045, -0.53, -0.005), (sx * 0.7, -0.7, 0), [0.04, 0.03], 0.011, curl=15)[0]
    return out


if WHICH == "arms":
    ASSET = "CHR-01_Arms"; col = L.collection(ASSET); P = []
    P += build_arm(col, "L", -1); P += build_arm(col, "R", 1)
    for o in P: L.apply_all(o); L.smooth(o, 45); L.uv_project(o, 0.01)
    bones = [("root", (0, 0, 0), (0, -0.1, 0), None)]
    for side, sx in (("L", -1), ("R", 1)):
        bones += [(f"forearm_{side}", (sx * 0.2, -0.16, 0), (sx * 0.2, -0.47, 0), "root"), (f"hand_{side}", (sx * 0.2, -0.47, 0), (sx * 0.2, -0.6, 0), f"forearm_{side}")]
        # Una cadena de huesos por dedo, con las articulaciones que devolvió el constructor de la geometría. El
        # rodillo se fija igual en toda la cadena (Z local hacia el dorso): si se deja al criterio de Blender, dos
        # falanges casi paralelas salen con los ejes girados 180° y sus flexiones se cancelan entre sí.
        for nombre in [f"finger_{side}{i}" for i in range(4)] + [f"thumb_{side}"]:
            js = FINGER_JOINTS[nombre]; padre = f"hand_{side}"
            for k in range(len(js) - 1):
                bn = phalanx_bone(nombre, k)
                bones.append((bn, tuple(js[k]), tuple(js[k + 1]), padre, (0, 0, 1)))
                padre = bn
    arm = L.armature("Armature_Arms", bones, col)
    for o in P:
        n = o.name; side = 'L' if '_L' in n else 'R'
        if n in arm.data.bones: bone = n                      # cada falange se ata a su propio hueso
        elif n.startswith(("forearm", "cuff")): bone = f"forearm_{side}"
        else: bone = f"hand_{side}"
        L.bind_rigid(o, arm, bone)
    Z = (0, 0, 0)
    # Agarre 64: el cierre se reparte entre las tres falanges. Con un solo hueso por dedo no hay ángulo que valga,
    # porque el dedo rígido pasa de largo del mango en vez de envolverlo.
    dedos = [phalanx_bone(f"finger_{s}{i}", k) for s in "LR" for i in range(4) for k in range(3)]
    dedos += [phalanx_bone(f"thumb_{s}", k) for s in "LR" for k in range(2)]
    fingers_all = {b: ((0, 0, 0), Z) for b in dedos}
    # Ángulos medidos sobre el modelo importado, no estimados: con estos la yema media queda a 26 mm de la palma y a
    # 4 mm de la superficie del mango. El pulgar necesita ADUCCIÓN (giro en Z) además de flexión, porque flexionando
    # solo se queda 63 mm de lado en vez de oponerse; el signo se invierte en la mano izquierda, que va espejada.
    curl = (-75, -90, -60)          # metacarpofalángica, interfalángica proximal, distal
    grip = {phalanx_bone(f"finger_{s}{i}", k): ((curl[k], 0, 0), Z) for s in "LR" for i in range(4) for k in range(3)}
    for s, sm in (("L", -1), ("R", 1)):
        grip[phalanx_bone(f"thumb_{s}", 0)] = ((-10, -40 * sm, -65 * sm), Z)
        grip[phalanx_bone(f"thumb_{s}", 1)] = ((-30, 0, 0), Z)
    L.push_nla(arm, L.action(arm, "Arms_Idle", 90, poses={1: {"root": ((0, 0, 0), Z)}, 45: {"root": ((1, 0, 0), (0, 0, -0.004))}, 90: {"root": ((0, 0, 0), Z)}}))
    L.push_nla(arm, L.action(arm, "Arms_Grip", 10, loop=False, poses={1: fingers_all, 10: grip}))
    L.push_nla(arm, L.action(arm, "Arms_CrowbarSwing", 26, loop=False, poses={1: {"forearm_R": ((0, 0, 0), Z)}, 6: {"forearm_R": ((-35, 0, 15), (0, 0.05, 0.05))}, 11: {"forearm_R": ((30, 0, -25), (0, -0.08, -0.05))}, 26: {"forearm_R": ((0, 0, 0), Z)}}))
    L.push_nla(arm, L.action(arm, "Arms_PistolReload", 57, loop=False, poses={1: {"forearm_L": ((0, 0, 0), Z), "forearm_R": ((0, 0, 0), Z)}, 11: {"forearm_L": ((-20, 0, 30), (0.08, 0.05, -0.02))}, 21: {"forearm_L": ((-30, 0, 40), (0.1, 0.1, -0.08))}, 41: {"forearm_L": ((-10, 0, 20), (0.06, 0.04, -0.02)), "forearm_R": ((-8, 0, 0), Z)}, 57: {"forearm_L": ((0, 0, 0), Z), "forearm_R": ((0, 0, 0), Z)}}))
    L.push_nla(arm, L.action(arm, "Arms_Syringe", 48, loop=False, poses={1: {"forearm_R": ((0, 0, 0), Z), "forearm_L": ((0, 0, 0), Z)}, 20: {"forearm_R": ((-25, 0, -30), (-0.1, 0.05, 0.05)), "forearm_L": ((-40, 0, 20), (0.05, 0.1, 0.05))}, 33: {"forearm_R": ((-30, 0, -35), (-0.12, 0.04, 0.03))}, 48: {"forearm_R": ((0, 0, 0), Z), "forearm_L": ((0, 0, 0), Z)}}))
    L.save_blend(ASSET); print("built arms", len(P), sum(len(o.data.polygons) for o in P))

elif WHICH == "crowbar":
    # 38: "no cilindro uniforme ni textura estirada". Es el arma de inicio y se inspecciona constantemente,
    # así que la barra tiene sección hexagonal REAL (6 caras forjadas), el doblez tiene espesor y nervio de
    # refuerzo donde se hace palanca, y la uña está bifurcada con ranura de extracción.
    ASSET = "WPN-01_Crowbar"; col = L.collection(ASSET); P = []

    # --- barra hexagonal: el chaflán de L.chamfer mata las 6 aristas vivas del prisma (33.2) ---
    shaft = L.cyl("shaft", 0.0122, 0.60, (0, 0.0, 0), col, axis='Y', verts=6, bevel=0.0015); L.assign(shaft, M['steel_paint']); P.append(shaft)
    L.chamfer(shaft, 0.0008, 2, 40)
    step = L.cyl("shaft_step", 0.0134, 0.055, (0, 0.272, 0), col, axis='Y', verts=6, bevel=0.0018); L.assign(step, M['steel_paint']); P.append(step)
    L.chamfer(step, 0.0008, 2, 40)

    # --- agarre: metal descubierto donde la mano roza (41.3 desgaste con causa) + cinta de mantenimiento ---
    grip = L.cyl("grip_worn", 0.0126, 0.17, (0, -0.19, 0), col, axis='Y', verts=6, bevel=0.0012); L.assign(grip, M['steel_bare']); P.append(grip)
    L.chamfer(grip, 0.0008, 2, 40)
    for k, y in ((0, -0.108), (1, -0.272)):
        t = L.torus(f"grip_tape{k}", 0.0132, 0.0018, (0, y, 0), col, axis='Y', segs=12, rings=5); L.assign(t, M['rubber']); P.append(t)
    # tope forjado: marca dónde acaba la zona de agarre, y es el límite exacto donde termina la pintura
    collar = L.torus("grip_stop", 0.0129, 0.0018, (0, -0.096, 0), col, axis='Y', segs=12, rings=5); L.assign(collar, M['steel_dark']); P.append(collar)

    # --- placa de inventario del búnker (34: las armas llevan inventario local), remachada ---
    tag = L.box("inv_tag", (0.006, 0.026, 0.014), (0.0128, 0.06, 0), col, bevel=0.0012, segs=2); L.assign(tag, M['steel_paint']); P.append(tag)
    P.append(L.bolt_row("inv_rivets", 0.002, (0.0158, 0.052, 0), (0, 0.016, 0), 2, col, axis='X', mat=M['steel_bare']))

    # --- talón: pata plana con bisel de uso y nervio ---
    heel = L.box("heel", (0.028, 0.05, 0.014), (0, -0.308, 0.004), col, rot=(math.radians(16), 0, 0), bevel=0.0025, segs=2); L.assign(heel, M['steel_bare']); P.append(heel)
    hedge = L.box("heel_edge", (0.028, 0.014, 0.005), (0, -0.331, 0.0), col, rot=(math.radians(28), 0, 0), bevel=0.0012, segs=2); L.assign(hedge, M['steel_bare']); P.append(hedge)
    hrib = L.box("heel_rib", (0.008, 0.032, 0.016), (0, -0.296, 0.012), col, rot=(math.radians(16), 0, 0), bevel=0.0015, segs=2); L.assign(hrib, M['steel_paint']); P.append(hrib)

    # --- doblez con espesor + nervio en la cara de carga ---
    bend = L.tube("bend", [(0, 0.298, 0), (0, 0.336, 0.004), (0, 0.366, 0.019), (0, 0.389, 0.042), (0, 0.402, 0.07), (0, 0.406, 0.095)], 0.0118, col, verts=8); L.assign(bend, M['steel_paint']); P.append(bend)
    # nervio en la cara interior del doblez: es donde se concentra la carga al hacer palanca (refuerzo con causa)
    brib = L.box("bend_rib", (0.010, 0.05, 0.006), (0, 0.369, 0.0385), col, rot=(math.radians(45), 0, 0), bevel=0.0015, segs=2); L.assign(brib, M['steel_paint']); P.append(brib)
    # cara forjada exterior: al curvar la barra la sección se aplasta y ahí se pela la pintura antes que en ningún sitio
    bflat = L.box("bend_flat", (0.020, 0.052, 0.005), (0, 0.386, 0.0235), col, rot=(math.radians(45), 0, 0), bevel=0.0015, segs=2); L.assign(bflat, M['steel_bare']); P.append(bflat)

    # --- uña bifurcada: dos puntas afiladas y ranura de extracción entre ellas ---
    neck = L.box("claw_neck", (0.026, 0.016, 0.03), (0, 0.406, 0.106), col, rot=(math.radians(-6), 0, 0), bevel=0.002, segs=2); L.assign(neck, M['steel_bare']); P.append(neck)
    for k, sxx in ((0, -1), (1, 1)):
        pr = L.box(f"claw{k}", (0.0105, 0.014, 0.034), (sxx * 0.0093, 0.407, 0.13), col, rot=(math.radians(-4), 0, 0), bevel=0.0018, segs=2); L.assign(pr, M['steel_bare']); P.append(pr)
        pt = L.box(f"claw{k}_edge", (0.0105, 0.010, 0.010), (sxx * 0.0093, 0.4075, 0.149), col, rot=(math.radians(-22), 0, 0), bevel=0.0012, segs=2); L.assign(pt, M['steel_bare']); P.append(pt)
    slot = L.box("claw_slot", (0.007, 0.0145, 0.016), (0, 0.407, 0.12), col, bevel=0.0012, segs=2); L.assign(slot, M['steel_dark']); P.append(slot)

    for o in P: L.apply_all(o); L.smooth(o, 40); L.uv_project(o, 0.01)
    L.save_blend(ASSET); print("built crowbar", len(P), sum(len(o.data.polygons) for o in P))

elif WHICH == "pistol":
    # 38/43: arma de viewmodel a centímetros de la cámara → el presupuesto es 5–15k tris, no 800.
    # Se modela como pieza fabricada: chasis con raíl y pin de desmontaje, corredera con estrías y ventana de
    # expulsión hundida, cañón con boca rebajada, miras, gatillo con guardamonte de sección real, cachas con
    # paneles antideslizantes y cargador con orificios testigo.
    ASSET = "WPN-02_Pistol"; col = L.collection(ASSET); P = []

    # --- chasis (polímero) ---
    frame = L.box("frame", (0.028, 0.15, 0.028), (0, 0.02, 0.0), col, bevel=0.003, segs=3); L.assign(frame, M['polymer_dark']); P.append(frame)
    L.chamfer(frame, 0.0012, 2, 50)
    dust = L.box("dustcover", (0.024, 0.075, 0.018), (0, 0.095, -0.004), col, bevel=0.003, segs=3); L.assign(dust, M['polymer_dark']); P.append(dust)
    # raíl de accesorios bajo el cañón: tres travesaños
    rail = L.rib_row("rail", 0.05, (0.022, 0.005, 0.005), (0, 0.095, -0.016), col, count=3, axis='Y', mat=M['polymer_dark']); P.append(rail)
    beaver = L.box("beavertail", (0.026, 0.03, 0.01), (0, -0.055, 0.012), col, rot=(math.radians(-18), 0, 0), bevel=0.004, segs=3); L.assign(beaver, M['polymer_dark']); P.append(beaver)

    # --- corredera (acero) ---
    slide = L.box("slide", (0.029, 0.175, 0.027), (0, 0.032, 0.031), col, bevel=0.0035, segs=3); L.assign(slide, M['steel_dark']); P.append(slide)
    L.chamfer(slide, 0.0012, 2, 50)
    # estrías traseras y delanteras: geometría real, no una tira plana
    rear = L.rib_row("serr_rear", 0.042, (0.0305, 0.0022, 0.02), (0, -0.032, 0.033), col, count=8, axis='Y', mat=M['steel_bare']); P.append(rear)
    front = L.rib_row("serr_front", 0.022, (0.0305, 0.0022, 0.018), (0, 0.093, 0.033), col, count=4, axis='Y', mat=M['steel_bare']); P.append(front)
    # ventana de expulsión hundida (el AO la ensombrece) + uñeta extractora
    port = L.recess("eject_port", (0.05, 0.012, 0.018), (0.0138, 0.052, 0.036), col, depth=0.008, rot=(0, 0, math.radians(90)), mat=M['steel_bare'], border=0.0025); P.append(port)
    extr = L.box("extractor", (0.004, 0.022, 0.007), (0.0135, 0.028, 0.036), col, bevel=0.0012); L.assign(extr, M['steel_bare']); P.append(extr)

    # --- cañón y boca ---
    barrel = L.cyl("barrel", 0.0062, 0.055, (0, 0.138, 0.032), col, axis='Y', verts=20, bevel=0.0012); L.assign(barrel, M['steel_bare']); P.append(barrel)
    crown = L.torus("crown", 0.0062, 0.0011, (0, 0.1645, 0.032), col, axis='Y', segs=20, rings=8); L.assign(crown, M['steel_bare']); P.append(crown)
    bore = L.cyl("bore", 0.0042, 0.012, (0, 0.162, 0.032), col, axis='Y', verts=20); L.assign(bore, M['steel_dark']); P.append(bore)

    # --- miras ---
    fs = L.box("front_sight", (0.0035, 0.007, 0.008), (0, 0.108, 0.048), col, bevel=0.0008); L.assign(fs, M['steel_bare']); P.append(fs)
    fsd = L.cyl("front_dot", 0.0013, 0.001, (0, 0.1045, 0.049), col, axis='Y', verts=10); L.assign(fsd, M['band']); P.append(fsd)
    for i, sx in ((0, -1), (1, 1)):
        rs = L.box(f"rear_sight{i}", (0.006, 0.008, 0.008), (sx * 0.008, -0.048, 0.048), col, bevel=0.0008); L.assign(rs, M['steel_bare']); P.append(rs)

    # --- gatillo, guardamonte, mandos ---
    guard_o = L.torus("trigger_guard", 0.0205, 0.0032, (0, 0.022, -0.031), col, axis='X', segs=28, rings=10); L.assign(guard_o, M['polymer_dark']); P.append(guard_o)
    trig = L.box("trigger", (0.0055, 0.006, 0.021), (0, 0.021, -0.026), col, rot=(math.radians(10), 0, 0), bevel=0.0015, segs=2); L.assign(trig, M['steel_dark']); P.append(trig)
    trig_face = L.rib_row("trigger_face", 0.016, (0.0056, 0.0012, 0.0016), (0, 0.0245, -0.026), col, count=5, axis='Z', mat=M['steel_dark']); P.append(trig_face)
    stop = L.box("slide_stop", (0.004, 0.028, 0.006), (-0.0155, 0.01, 0.006), col, bevel=0.0012); L.assign(stop, M['steel_bare']); P.append(stop)
    safety = L.box("safety", (0.004, 0.016, 0.005), (-0.0155, -0.042, 0.016), col, rot=(math.radians(-12), 0, 0), bevel=0.001); L.assign(safety, M['steel_bare']); P.append(safety)
    relb = L.box("mag_release", (0.005, 0.009, 0.009), (0.0145, -0.012, -0.018), col, bevel=0.0015); L.assign(relb, M['steel_dark']); P.append(relb)
    pin = L.bolt("takedown_pin", 0.0035, (-0.0145, 0.052, -0.004), col, axis='X', kind='round'); L.assign(pin, M['steel_bare']); P.append(pin)

    # --- cachas: paneles antideslizantes en ambas caras ---
    gripb = L.box("grip", (0.029, 0.042, 0.1), (0, -0.042, -0.062), col, rot=(math.radians(-15), 0, 0), bevel=0.005, segs=3); L.assign(gripb, M['grip']); P.append(gripb)
    L.chamfer(gripb, 0.0012, 2, 50)
    for sx in (-1, 1):
        panel = L.rib_row(f"grip_tex{'L' if sx < 0 else 'R'}", 0.062, (0.0025, 0.0032, 0.0032), (sx * 0.0148, -0.044, -0.062), col, count=9, axis='Z', rot=(math.radians(-15), 0, 0), mat=M['grip'])
        P.append(panel)
    front_strap = L.rib_row("front_strap", 0.058, (0.02, 0.0028, 0.0028), (0, -0.0215, -0.062), col, count=8, axis='Z', rot=(math.radians(-15), 0, 0), mat=M['grip']); P.append(front_strap)

    # --- cargador con orificios testigo y talón ---
    mag = L.box("magazine", (0.021, 0.029, 0.108), (0, -0.0435, -0.072), col, rot=(math.radians(-15), 0, 0), bevel=0.0018, segs=2); L.assign(mag, M['steel_dark']); P.append(mag)
    base = L.box("mag_base", (0.026, 0.034, 0.008), (0, -0.0565, -0.1235), col, rot=(math.radians(-15), 0, 0), bevel=0.0018, segs=2); L.assign(base, M['polymer_dark']); P.append(base)
    holes = L.bolt_row("witness", 0.0025, (0.0108, -0.032, -0.045), (0, -0.0045, -0.017), 4, col, axis='X', mat=M['steel_bare']); P.append(holes)

    hammer = L.box("hammer", (0.009, 0.013, 0.019), (0, -0.072, 0.03), col, rot=(math.radians(-25), 0, 0), bevel=0.002, segs=2); L.assign(hammer, M['steel_bare']); P.append(hammer)
    screws = L.bolt_row("screws", 0.0028, (0.0145, -0.03, 0.0), (0, 0.05, 0.0), 3, col, axis='X', mat=M['steel_bare']); P.append(screws)

    for o in P: L.apply_all(o); L.smooth(o, 40)
    L.save_blend(ASSET); print("built pistol", len(P), sum(len(o.data.polygons) for o in P))

elif WHICH == "shotgun":
    # 38: "Bombeo, culata, puerto, inserción, superficies de agarre" y 64: "Bombeo e inserción por cartucho".
    # El arma de seguridad industrial del búnker: cajón mecanizado con puertos HUNDIDOS (no cajas pegadas),
    # bombeo con estrías longitudinales reales, guardamanos térmico perforado, abrazaderas atornilladas
    # cañón/tubo y culata con cantonera, tornillos y cuadriculado de agarre.
    ASSET = "WPN-03_Shotgun"; col = L.collection(ASSET); P = []

    # --- cajón de mecanismos ---
    recv = L.box("receiver", (0.04, 0.2, 0.06), (0, 0.0, 0.0), col, bevel=0.005, segs=3); L.assign(recv, M['steel_dark']); P.append(recv)
    L.chamfer(recv, 0.0012, 2, 50)
    rib = L.box("receiver_rib", (0.014, 0.19, 0.006), (0, 0.0, 0.032), col, bevel=0.0015, segs=2); L.assign(rib, M['steel_dark']); P.append(rib)
    # puerto de expulsión y puerto de carga: rebajes con reborde, el AO hace el resto (41.3)
    port = L.recess("eject_port", (0.072, 0.014, 0.028), (0.0205, 0.035, 0.008), col, depth=0.009, rot=(0, 0, math.radians(90)), mat=M['steel_bare'], border=0.003); P.append(port)
    lport = L.recess("load_port", (0.06, 0.012, 0.03), (0, 0.035, -0.0255), col, depth=0.007, rot=(math.radians(90), 0, math.radians(90)), mat=M['steel_bare'], border=0.003); P.append(lport)
    # elevador con un cartucho a la vista, justo bajo el puerto de expulsión: la inserción de 64 tiene una pieza que la sostiene
    carrier = L.box("carrier", (0.026, 0.05, 0.005), (0, 0.033, -0.0215), col, rot=(math.radians(-8), 0, 0), bevel=0.0015, segs=2); L.assign(carrier, M['steel_bare']); P.append(carrier)
    shell = L.cyl("shell_loaded", 0.0092, 0.02, (0, 0.035, -0.0135), col, axis='Y', verts=12, bevel=0.0015); L.assign(shell, M['plastic_red']); P.append(shell)
    rim = L.cyl("shell_rim", 0.0098, 0.005, (0, 0.0235, -0.0135), col, axis='Y', verts=12); L.assign(rim, M['brass']); P.append(rim)
    extr = L.box("extractor", (0.005, 0.02, 0.008), (0.0198, 0.02, 0.012), col, bevel=0.0012, segs=2); L.assign(extr, M['steel_bare']); P.append(extr)
    # pasadores del mecanismo: van donde de verdad se desmonta el arma
    P.append(L.bolt_row("action_pins_l", 0.0038, (-0.0205, -0.045, -0.012), (0, 0.045, 0), 2, col, axis='X', mat=M['steel_bare']))
    P.append(L.bolt_row("action_pins_r", 0.0038, (0.0205, -0.045, -0.012), (0, 0.045, 0), 2, col, axis='X', mat=M['steel_bare']))
    for k, ox in ((0, -0.0201), (1, 0.0201)):
        P.append(L.panel_seam(f"receiver_seam{k}", 0.19, (ox, 0.0, 0.0245), col, axis='Y', width=0.0045, depth=0.004, mat=M['steel_bare']))
    P.append(L.bolt_row("cover_bolts", 0.0024, (0.012, -0.07, 0.0305), (0, 0.07, 0), 3, col, axis='Z', mat=M['steel_bare']))
    plate = L.box("inv_plate", (0.004, 0.036, 0.016), (-0.0205, 0.05, 0.006), col, bevel=0.001, segs=2); L.assign(plate, M['steel_paint']); P.append(plate)
    P.append(L.bolt_row("inv_rivets", 0.0022, (-0.0218, 0.038, 0.006), (0, 0.024, 0), 2, col, axis='X', mat=M['steel_bare']))
    hous = L.box("trigger_housing", (0.032, 0.072, 0.016), (0, -0.032, -0.026), col, bevel=0.003, segs=2); L.assign(hous, M['polymer_dark']); P.append(hous)
    P.append(L.bolt_row("housing_pins", 0.003, (-0.0165, -0.056, -0.026), (0, 0.048, 0), 2, col, axis='X', mat=M['steel_bare']))

    # --- cañón, recámara y tubo cargador ---
    barrel = L.cyl("barrel", 0.011, 0.5, (0, 0.35, 0.02), col, axis='Y', verts=20, bevel=0.0015); L.assign(barrel, M['steel_dark']); P.append(barrel)
    chamber = L.cyl("chamber", 0.0148, 0.075, (0, 0.135, 0.02), col, axis='Y', verts=20, bevel=0.002); L.assign(chamber, M['steel_dark']); P.append(chamber)
    crown = L.torus("muzzle_crown", 0.011, 0.0015, (0, 0.598, 0.02), col, axis='Y', segs=20, rings=8); L.assign(crown, M['steel_bare']); P.append(crown)
    bore = L.cyl("bore", 0.0082, 0.02, (0, 0.594, 0.02), col, axis='Y', verts=20); L.assign(bore, M['steel_dark']); P.append(bore)
    tube = L.cyl("mag_tube", 0.012, 0.42, (0, 0.31, -0.012), col, axis='Y', verts=16, bevel=0.0015); L.assign(tube, M['steel_dark']); P.append(tube)
    tcap = L.cyl("tube_cap", 0.0138, 0.02, (0, 0.53, -0.012), col, axis='Y', verts=16, bevel=0.002); L.assign(tcap, M['steel_bare']); P.append(tcap)
    P.append(ring_boxes(col, "tube_cap_knurl", 12, (0, 0.53, -0.012), 0.0136, (0.0012, 0.016, 0.0022), M['steel_bare'], axis='Y'))
    for k, y in ((0, 0.16), (1, 0.44)):
        r = L.torus(f"tube_ring{k}", 0.0124, 0.0022, (0, y, -0.012), col, axis='Y', segs=16, rings=5); L.assign(r, M['steel_bare']); P.append(r)
    # abrazaderas: donde dos piezas se sujetan hay tornillos, no una fusión mágica (33.2)
    for k, y in ((0, 0.20), (1, 0.50)):
        cl = L.box(f"clamp{k}", (0.03, 0.016, 0.046), (0, y, 0.004), col, bevel=0.0025, segs=2); L.assign(cl, M['steel_bare']); P.append(cl)
        P.append(L.bolt_row(f"clamp{k}_bolts", 0.0026, (0.0152, y, 0.004), (-0.0304, 0, 0), 2, col, axis='X', mat=M['steel_bare']))
    sling = L.torus("sling_loop", 0.008, 0.0022, (0, 0.20, -0.032), col, axis='X', segs=14, rings=6); L.assign(sling, M['steel_bare']); P.append(sling)
    # guardamanos térmico: el cañón calienta y la mano va encima → rejilla con lamas reales
    hs = L.vent("heat_shield", (0.032, 0.02, 0.11), (0, 0.415, 0.038), col, slats=6, rot=(math.radians(90), 0, 0), depth=0.008, mat_frame=M['steel_paint'], mat_slat=M['steel_bare']); P.append(hs)
    for k, y in ((0, 0.365), (1, 0.465)):
        sc = L.box(f"shield_clamp{k}", (0.026, 0.008, 0.03), (0, y, 0.03), col, bevel=0.0015, segs=2); L.assign(sc, M['steel_paint']); P.append(sc)

    # --- bombeo: estrías longitudinales reales, collares mecanizados y barras de acción ---
    pump = L.cyl("pump", 0.0205, 0.15, (0, 0.28, -0.012), col, axis='Y', verts=20, bevel=0.004); L.assign(pump, M['wood']); P.append(pump)
    L.chamfer(pump, 0.0012, 2, 55)
    P.append(ring_boxes(col, "pump_flutes", 10, (0, 0.28, -0.012), 0.0202, (0.0034, 0.104, 0.0052), M['wood'], axis='Y', bevel=0.0009, segs=2))
    for k, y in ((0, 0.213), (1, 0.347)):
        b = L.torus(f"pump_band{k}", 0.0207, 0.0026, (0, y, -0.012), col, axis='Y', segs=20, rings=6); L.assign(b, M['steel_bare']); P.append(b)
    pcap = L.cyl("pump_cap", 0.0165, 0.016, (0, 0.358, -0.012), col, axis='Y', verts=16, bevel=0.002); L.assign(pcap, M['steel_bare']); P.append(pcap)
    for k, sxx in ((0, -1), (1, 1)):
        ab = L.box(f"action_bar{k}", (0.005, 0.13, 0.011), (sxx * 0.0155, 0.19, -0.014), col, bevel=0.0012, segs=2); L.assign(ab, M['steel_bare']); P.append(ab)

    # --- culata: cantonera con nervios, tornillos pasantes, cuadriculado y portafusil ---
    stock = L.box("stock", (0.035, 0.24, 0.07), (0, -0.22, -0.02), col, rot=(math.radians(8), 0, 0), bevel=0.01, segs=3); L.assign(stock, M['wood']); P.append(stock)
    L.chamfer(stock, 0.0015, 2, 55)
    comb = L.box("stock_comb", (0.03, 0.14, 0.016), (0, -0.2, 0.014), col, rot=(math.radians(8), 0, 0), bevel=0.005, segs=2); L.assign(comb, M['wood']); P.append(comb)
    pad = L.box("butt_pad", (0.038, 0.014, 0.076), (0, -0.341, -0.036), col, rot=(math.radians(8), 0, 0), bevel=0.004, segs=2); L.assign(pad, M['rubber']); P.append(pad)
    P.append(L.rib_row("butt_pad_ribs", 0.036, (0.036, 0.004, 0.006), (0, -0.348, -0.036), col, count=3, axis='Z', rot=(math.radians(8), 0, 0), mat=M['rubber']))
    P.append(L.bolt_row("butt_screws", 0.003, (0, -0.348, -0.012), (0, 0.004, -0.05), 2, col, axis='Y', mat=M['steel_bare']))
    P.append(L.panel_seam("stock_seam", 0.064, (0, -0.101, -0.02), col, axis='X', width=0.005, depth=0.006, mat=M['steel_dark']))
    tang = L.bolt("stock_bolt", 0.004, (0, -0.125, 0.026), col, axis='Z', kind='round'); L.assign(tang, M['steel_bare']); P.append(tang)
    swiv = L.torus("stock_swivel", 0.007, 0.002, (0, -0.30, -0.055), col, axis='X', segs=12, rings=5); L.assign(swiv, M['steel_bare']); P.append(swiv)
    P.append(L.rib_row("stock_check", 0.05, (0.028, 0.0032, 0.0032), (0, -0.155, -0.046), col, count=5, axis='Y', rot=(math.radians(8), 0, 0), mat=M['wood']))
    gripb = L.box("pistol_grip", (0.03, 0.05, 0.09), (0, -0.09, -0.06), col, rot=(math.radians(-20), 0, 0), bevel=0.006, segs=3); L.assign(gripb, M['wood']); P.append(gripb)
    L.chamfer(gripb, 0.0012, 2, 55)
    for sxx in (-1, 1):
        P.append(L.rib_row(f"grip_check{'L' if sxx < 0 else 'R'}", 0.056, (0.0026, 0.0034, 0.0034), (sxx * 0.0152, -0.088, -0.062), col, count=7, axis='Z', rot=(math.radians(-20), 0, 0), mat=M['wood']))

    # --- gatillo y seguro ---
    guard = L.torus("trigger_guard", 0.022, 0.0032, (0, -0.03, -0.035), col, axis='X', segs=24, rings=8); L.assign(guard, M['steel_dark']); P.append(guard)
    trig = L.box("trigger", (0.006, 0.007, 0.024), (0, -0.031, -0.03), col, rot=(math.radians(10), 0, 0), bevel=0.0015, segs=2); L.assign(trig, M['steel_bare']); P.append(trig)
    P.append(L.rib_row("trigger_face", 0.017, (0.0062, 0.0013, 0.0017), (0, -0.0278, -0.03), col, count=4, axis='Z', mat=M['steel_bare']))
    saf = L.bolt("safety", 0.005, (0, -0.046, -0.024), col, axis='X', head=0.042, kind='round'); L.assign(saf, M['steel_bare']); P.append(saf)

    # --- miras: punto de latón y aro fantasma ---
    fs = L.box("front_sight", (0.005, 0.012, 0.012), (0, 0.575, 0.036), col, bevel=0.0012, segs=2); L.assign(fs, M['steel_dark']); P.append(fs)
    bead = L.sphere("front_bead", 0.0022, (0, 0.575, 0.0425), col, segs=10, rings=6); L.assign(bead, M['brass']); P.append(bead)
    ghost = L.torus("rear_ghost", 0.008, 0.0022, (0, 0.06, 0.045), col, axis='Y', segs=14, rings=5); L.assign(ghost, M['steel_bare']); P.append(ghost)
    gpost = L.box("rear_post", (0.006, 0.01, 0.014), (0, 0.06, 0.036), col, bevel=0.0012, segs=2); L.assign(gpost, M['steel_bare']); P.append(gpost)

    for o in P: L.apply_all(o); L.smooth(o, 40); L.uv_project(o, 0.01)
    L.save_blend(ASSET); print("built shotgun", len(P), sum(len(o.data.polygons) for o in P))

elif WHICH == "flashlight":
    # 38/64.1: "Lente, reflector, junta, switch y carcasa" + clip visible de equipo para el montaje al arnés.
    # Herramienta industrial (34): moleteado REAL donde agarra la mano, tapa de batería sellada con junta,
    # bisel con corona y reflector escalonado con el emisor en su foco (65: la luz sale del punto correcto).
    ASSET = "WPN-04_Flashlight"; col = L.collection(ASSET); P = []

    # --- carcasa ---
    body = L.cyl("body", 0.018, 0.16, (0, 0.0, 0), col, axis='Y', verts=18, bevel=0.003); L.assign(body, M['steel_paint']); P.append(body)
    L.chamfer(body, 0.001, 2, 55)
    P.append(ring_boxes(col, "knurl", 12, (0, -0.03, 0), 0.0178, (0.0022, 0.044, 0.0034), M['steel_paint'], axis='Y', bevel=0.0006, segs=1))
    for k, y in ((0, -0.004), (1, -0.056)):
        c = L.torus(f"collar{k}", 0.0184, 0.0022, (0, y, 0), col, axis='Y', segs=14, rings=4); L.assign(c, M['steel_dark']); P.append(c)

    # --- tapa de batería sellada: rosca, junta y moleteado de apertura (causa: se abre con la mano) ---
    tail = L.cyl("tail_cap", 0.0186, 0.024, (0, -0.092, 0), col, axis='Y', verts=16, bevel=0.0025); L.assign(tail, M['steel_dark']); P.append(tail)
    tg = L.torus("tail_gasket", 0.0179, 0.0022, (0, -0.0785, 0), col, axis='Y', segs=16, rings=5); L.assign(tg, M['rubber']); P.append(tg)
    P.append(ring_boxes(col, "tail_knurl", 6, (0, -0.092, 0), 0.0184, (0.0018, 0.018, 0.003), M['steel_dark'], axis='Y', bevel=0.0005, segs=1))

    # --- cabeza: junta, bisel con corona, reflector escalonado, emisor y lente ---
    head = L.cyl("head", 0.026, 0.05, (0, 0.1, 0), col, axis='Y', verts=18, bevel=0.004); L.assign(head, M['steel_dark']); P.append(head)
    L.chamfer(head, 0.0012, 2, 55)
    gask = L.torus("gasket", 0.0242, 0.0026, (0, 0.077, 0), col, axis='Y', segs=16, rings=5); L.assign(gask, M['rubber']); P.append(gask)
    bez = L.cyl("bezel", 0.0268, 0.009, (0, 0.126, 0), col, axis='Y', verts=16, bevel=0.002); L.assign(bez, M['steel_bare']); P.append(bez)
    P.append(ring_boxes(col, "bezel_crown", 4, (0, 0.1315, 0), 0.0255, (0.0022, 0.006, 0.006), M['steel_bare'], axis='Y', bevel=0.0006, segs=1))
    refl = L.cyl("reflector", 0.0225, 0.014, (0, 0.118, 0), col, axis='Y', verts=16); L.assign(refl, M['steel_bare']); P.append(refl)
    rthr = L.cyl("reflector_throat", 0.013, 0.012, (0, 0.107, 0), col, axis='Y', verts=16); L.assign(rthr, M['steel_bare']); P.append(rthr)
    rstep = L.torus("reflector_step", 0.0178, 0.0035, (0, 0.112, 0), col, axis='Y', segs=14, rings=4); L.assign(rstep, M['steel_bare']); P.append(rstep)
    emit = L.cyl("emitter", 0.006, 0.004, (0, 0.1, 0), col, axis='Y', verts=10, bevel=0.0008); L.assign(emit, M['emitter']); P.append(emit)
    lens = L.cyl("lens", 0.0228, 0.004, (0, 0.128, 0), col, axis='Y', verts=20); L.assign(lens, M['glass']); P.append(lens)

    # --- switch en su alojamiento atornillado, en la zona lisa del cuerpo (no encima del moleteado) ---
    swp = L.box("switch_plate", (0.024, 0.03, 0.006), (0, 0.035, 0.0165), col, bevel=0.0015, segs=2); L.assign(swp, M['steel_dark']); P.append(swp)
    sw = L.cyl("switch", 0.0075, 0.006, (0, 0.035, 0.019), col, axis='Z', verts=12, bevel=0.0012); L.assign(sw, M['rubber']); P.append(sw)
    P.append(L.bolt_row("switch_screws", 0.0018, (0, 0.022, 0.018), (0, 0.026, 0), 2, col, axis='Z', mat=M['steel_bare']))

    # --- clip de bolsillo/arnés atornillado (64.1) ---
    cb = L.box("clip_base", (0.016, 0.02, 0.005), (0, -0.062, 0.017), col, bevel=0.0012, segs=2); L.assign(cb, M['steel_bare']); P.append(cb)
    cl = L.box("clip_leaf", (0.014, 0.05, 0.0025), (0, -0.038, 0.0235), col, rot=(math.radians(-6), 0, 0), bevel=0.0008, segs=2); L.assign(cl, M['steel_bare']); P.append(cl)
    P.append(L.bolt_row("clip_screws", 0.0018, (0, -0.067, 0.0195), (0, 0.009, 0), 2, col, axis='Z', mat=M['steel_bare']))
    ip = L.box("inv_plate", (0.012, 0.022, 0.0025), (0, 0.035, -0.0176), col, bevel=0.0008, segs=2); L.assign(ip, M['band']); P.append(ip)

    for o in P: L.apply_all(o); L.smooth(o, 40); L.uv_project(o, 0.01)
    L.save_blend(ASSET); print("built flashlight", len(P), sum(len(o.data.polygons) for o in P))

elif WHICH == "syringe":
    # OBJ-056: "Cuerpo, émbolo, tapa y líquido" + envase ACTUAL, no instrumento oxidado.
    # Se ve en la mano durante la curación: el tapón de goma dentro del cilindro, la varilla en cruz,
    # el cono luer con su collarín y las estrías de la tapa son lo que lo vuelve un objeto y no un tubo.
    ASSET = "PRP-Syringe"; col = L.collection(ASSET); P = []
    body = L.cyl("body", 0.009, 0.09, (0, 0, 0), col, axis='Y', verts=12, bevel=0.0012); L.assign(body, M['glass']); P.append(body)
    liquid = L.cyl("liquid", 0.0076, 0.05, (0, -0.015, 0), col, axis='Y', verts=14); L.assign(liquid, M['liquid']); P.append(liquid)
    # tapón de goma: se ve a través del cilindro y marca el nivel real de la dosis
    stop = L.cyl("stopper", 0.0079, 0.008, (0, -0.041, 0), col, axis='Y', verts=10, bevel=0.0012); L.assign(stop, M['rubber']); P.append(stop)
    plung = L.cyl("plunger", 0.0035, 0.085, (0, -0.0625, 0), col, axis='Y', verts=10); L.assign(plung, M['polymer_ivory']); P.append(plung)
    rib = L.box("plunger_rib", (0.0095, 0.082, 0.0016), (0, -0.0625, 0), col, bevel=0.0004, segs=1); L.assign(rib, M['polymer_ivory']); P.append(rib)
    thumb = L.cyl("plunger_head", 0.013, 0.004, (0, -0.104, 0), col, axis='Y', verts=12, bevel=0.0012); L.assign(thumb, M['polymer_ivory']); P.append(thumb)
    flange = L.box("flange", (0.032, 0.0035, 0.013), (0, -0.0455, 0), col, bevel=0.001, segs=1); L.assign(flange, M['polymer_ivory']); P.append(flange)
    luer = L.cyl("luer", 0.0046, 0.013, (0, 0.0505, 0), col, axis='Y', verts=10, bevel=0.0008); L.assign(luer, M['polymer_ivory']); P.append(luer)
    coll = L.torus("luer_collar", 0.0052, 0.0012, (0, 0.0455, 0), col, axis='Y', segs=10, rings=4); L.assign(coll, M['polymer_ivory']); P.append(coll)
    ndl = L.cyl("needle", 0.0011, 0.024, (0, 0.063, 0), col, axis='Y', verts=6); L.assign(ndl, M['steel_bare']); P.append(ndl)
    cap = L.cyl("cap", 0.006, 0.03, (0, 0.06, 0), col, axis='Y', verts=12, bevel=0.0012); L.assign(cap, M['plastic_red']); P.append(cap)
    P.append(ring_boxes(col, "cap_ribs", 5, (0, 0.06, 0), 0.0058, (0.0008, 0.024, 0.0014), M['plastic_red'], axis='Y'))
    for o in P: L.apply_all(o); L.smooth(o, 40); L.uv_project(o, 0.01)
    L.save_blend(ASSET); print("built syringe", len(P), sum(len(o.data.polygons) for o in P))

elif WHICH == "ration":
    # OBJ-057: "Envoltura, costura y etiqueta reciente" + "Pliegues de transporte, lote actual".
    # La prueba es que la fecha explique el alimento conservado: sello térmico dentado, fuelle inferior,
    # pliegues de transporte y muesca de apertura. Nada de ladrillo amarillo de color.
    ASSET = "PRP-Ration"; col = L.collection(ASSET); P = []
    pack = L.box("pack", (0.115, 0.185, 0.038), (0, 0, 0), col, bevel=0.012, segs=3); L.assign(pack, M['foil']); P.append(pack)
    L.chamfer(pack, 0.0015, 2, 55)
    st = L.box("seal_top", (0.12, 0.016, 0.004), (0, 0.1, 0), col, bevel=0.001, segs=2); L.assign(st, M['foil']); P.append(st)
    sb = L.box("seal_bottom", (0.12, 0.014, 0.004), (0, -0.0985, 0), col, bevel=0.001, segs=2); L.assign(sb, M['foil']); P.append(sb)
    # dentado de la selladora: huella de máquina repetida, no ruido procedural
    crimp = [L.box(f"crimp{i}", (0.0055, 0.014, 0.0056), (-0.0455 + i * 0.0182, 0.1, 0), col) for i in range(6)]
    for c in crimp: L.assign(c, M['foil'])
    P.append(L.join(crimp, "seal_crimp"))
    gus = L.box("gusset", (0.108, 0.012, 0.03), (0, -0.088, -0.006), col, rot=(math.radians(-14), 0, 0), bevel=0.002, segs=1); L.assign(gus, M['foil']); P.append(gus)
    folds = []
    for i, (y, ang) in enumerate(((0.045, 4), (-0.01, -3), (-0.055, 5))):
        folds.append(L.box(f"fold{i}", (0.112, 0.006, 0.0045), (0, y, 0.0185), col, rot=(0, 0, math.radians(ang)), bevel=0.0012, segs=1))
    for f in folds: L.assign(f, M['foil'])
    P.append(L.join(folds, "transport_folds"))
    label = L.box("label", (0.082, 0.1, 0.0012), (0, 0.005, 0.0202), col, bevel=0.0003, segs=1); L.assign(label, M['band']); P.append(label)
    lot = L.box("lot_strip", (0.05, 0.012, 0.0014), (0, -0.062, 0.0203), col, bevel=0.0003, segs=1); L.assign(lot, M['band']); P.append(lot)
    notch = L.box("tear_notch", (0.004, 0.01, 0.006), (0.056, 0.092, 0), col); L.assign(notch, M['foil']); P.append(notch)
    for o in P: L.apply_all(o); L.smooth(o, 40); L.uv_project(o, 0.01)
    L.save_blend(ASSET); print("built ration", len(P), sum(len(o.data.polygons) for o in P))
