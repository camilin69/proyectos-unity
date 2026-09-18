# BOT-01 VIGÍA-03 (12 / 36.1): 1.25 m, cabeza grande, cuello estrecho, torso encogido, antebrazos largos, lanzador de red
# integrado, rostro sin boca con cuencas profundas como geometría. Piezas rígidas con pivote en eje de rotación; rig por
# hueso; clips 49.2.
#
# Paso a unidad de contención FABRICADA (33.2 / 41.3): cada pieza grande es una carcasa con chaflán (ninguna arista viva),
# las juntas existen donde dos piezas se encuentran, los tornillos están donde algo se atornilla (suela/carcasa, cubierta
# sanitaria, panel de mantenimiento, placas temporales, módulo del lanzador), las rejillas están donde algo respira
# (pecho, espalda alta, nuca), los nervios están donde hay carga (flancos del torso bajo los hombros), los pistones y
# cables están en las articulaciones que se mueven, y la placa de serie NÉMESIS va en relieve sobre la cubierta.
#
# COSTE: el detalle se agrupa por hueso con L.join, así que el número de OBJETOS (37) se mantiene prácticamente igual que
# antes (36) aunque la geometría se duplique: mismo número de renderers en Unity, silueta y lectura cercana muy superiores.
import bpy, math, importlib, sys
sys.path.insert(0, r"C:/Users/HP/Documents/GitHub/proyectos-unity/SourceArt/Scripts")
import esn_lib as L; importlib.reload(L)
from mathutils import Vector

ASSET = "BOT-01_Vigia"
L.reset_scene()
col = L.collection(ASSET)
M = L.std_mats()
# etiqueta corporativa manchada (12: "pequeñas etiquetas corporativas") y cableado de instrumentación
M['label'] = L.material("M_VigiaLabel", (0.74, 0.71, 0.63), 0.6, 0.0, wear=0.45, wear_color=(0.42, 0.36, 0.3), bump=0.12, scale=18)
M['wire'] = L.material("M_VigiaWire", (0.07, 0.07, 0.08), 0.7, 0.0, bump=0.3, scale=45)
parts = {}

H = 1.25
RAD = math.radians


def shell(name, size, loc, mat, rot=(0, 0, 0), pivot='center', cham=0.004):
    """Carcasa: caja con material y chaflán por ángulo. Ninguna arista queda viva (33.2)."""
    o = L.box(name, size, loc, col, pivot=pivot, rot=rot)
    L.assign(o, mat)
    L.chamfer(o, cham, 2, 50)
    return o


def cable(name, pts, radius=0.005, mat=None):
    """Cable de instrumentación con holgura para el rango de la articulación (36.4)."""
    o = L.tube(name, pts, radius, col, verts=8)
    L.assign(o, mat or M['wire'])
    return o


# ---------------------------------------------------------------- piernas
# Pies estables con goma, rodillas desfasadas (pierna izquierda 2 cm más adelantada), pistón de tobillo visible.
for side, sx in (("L", -1), ("R", 1)):
    x = sx * 0.1
    # pie: suela de goma + carcasa de acero atornillada a la suela + puntera de refuerzo
    fsh = shell(f"foot_shell_{side}", (0.118, 0.196, 0.034), (x, 0.02, 0.033), M['steel_dark'])
    sole = shell(f"sole_{side}", (0.12, 0.2, 0.018), (x, 0.02, 0.0), M['rubber'], pivot='bottom', cham=0.003)
    toe = shell(f"toe_{side}", (0.105, 0.07, 0.016), (x, -0.04, 0.052), M['steel_bare'], cham=0.003)
    fbolt = L.bolt_row(f"foot_bolt_{side}", 0.004, (sx * 0.1595, -0.04, 0.026), (0, 0.06, 0), 3, col, axis='X', mat=M['steel_bare'])
    parts[f"foot_{side}"] = L.join([fsh, sole, toe, fbolt], f"foot_{side}")

    # espinilla: tubo + rótula de tobillo con collar, placa frontal atornillada y pistón de accionamiento
    shin = L.cyl(f"shin_{side}", 0.035, 0.32, (x, 0.0, 0.05), col, pivot='bottom', verts=16, bevel=0.006); L.assign(shin, M['steel_dark'])
    ankle = L.sphere(f"ankle_{side}", 0.045, (x, 0.005, 0.058), col, segs=12, rings=8); L.assign(ankle, M['steel_bare'])
    acol = L.torus(f"ankle_ring_{side}", 0.042, 0.006, (x, 0.005, 0.058), col, axis='Z', segs=14, rings=6); L.assign(acol, M['rubber'])
    splate = shell(f"shin_plate_{side}", (0.055, 0.03, 0.2), (x, -0.038, 0.2), M['polymer_ivory'], cham=0.003)
    sbolt = L.bolt_row(f"shin_bolt_{side}", 0.004, (x, -0.054, 0.12), (0, 0, 0.08), 3, col, axis='Y', mat=M['steel_bare'])
    pcyl = L.cyl(f"piston_{side}", 0.012, 0.1, (sx * 0.142, 0.032, 0.26), col, verts=10); L.assign(pcyl, M['steel_bare'])
    prod = L.cyl(f"piston_rod_{side}", 0.006, 0.09, (sx * 0.142, 0.032, 0.165), col, verts=8); L.assign(prod, M['steel_bare'])
    pfoot = shell(f"piston_foot_{side}", (0.024, 0.024, 0.018), (sx * 0.142, 0.032, 0.115), M['steel_dark'], cham=0.002)
    parts[f"shin_{side}"] = L.join([shin, ankle, acol, splate, sbolt, pcyl, prod, pfoot], f"shin_{side}")

    # rodilla: rótula + rotula cubierta por una cazoleta atornillada (36.4 holgura entre carcasa y joint)
    knee = L.sphere(f"knee_{side}", 0.05, (x, 0.01 * sx, 0.37), col, segs=14, rings=9); L.assign(knee, M['steel_bare'])
    kcap = shell(f"knee_cap_{side}", (0.07, 0.05, 0.06), (x, -0.038, 0.375), M['polymer_ivory'], cham=0.004)
    kbolt = L.bolt_row(f"knee_bolt_{side}", 0.0038, (x - 0.022, -0.058, 0.375), (0.044, 0, 0), 2, col, axis='Y', mat=M['steel_bare'])
    parts[f"knee_{side}"] = L.join([knee, kcap, kbolt], f"knee_{side}")

    # muslo: tubo + carcasa exterior + rótula de cadera + mazo de cables que baja por detrás con holgura
    thigh = L.cyl(f"thigh_{side}", 0.04, 0.25, (x, 0.0, 0.37), col, pivot='bottom', verts=16, bevel=0.006); L.assign(thigh, M['polymer_dark'])
    tshell = shell(f"thigh_shell_{side}", (0.09, 0.075, 0.16), (x, 0.0, 0.5), M['polymer_ivory'], cham=0.004)
    hip = L.sphere(f"hip_{side}", 0.05, (x, 0.0, 0.62), col, segs=12, rings=8); L.assign(hip, M['steel_bare'])
    lcab = cable(f"leg_cable_{side}", [(sx * 0.14, 0.05, 0.6), (sx * 0.148, 0.055, 0.54), (sx * 0.145, 0.05, 0.47), (sx * 0.13, 0.045, 0.41)], 0.006)
    parts[f"thigh_{side}"] = L.join([thigh, tshell, hip, lcab], f"thigh_{side}")

# ---------------------------------------------------------------- pelvis y torso encogido
# Pelvis con faldón que tapa los actuadores de cadera, junta de cintura por delante y por detrás y tornillería de servicio.
pelvis = shell("pelvis", (0.26, 0.16, 0.1), (0, 0, 0.62), M['steel_dark'], pivot='bottom', cham=0.005)
skirt = shell("pelvis_skirt", (0.28, 0.17, 0.04), (0, 0, 0.605), M['steel_paint'], cham=0.004)
pb_a = L.bolt_row("pelvis_bolt_a", 0.0042, (-0.09, -0.082, 0.645), (0.09, 0, 0), 3, col, axis='Y', mat=M['steel_bare'])
pb_b = L.bolt_row("pelvis_bolt_b", 0.0042, (-0.09, -0.082, 0.7), (0.09, 0, 0), 3, col, axis='Y', mat=M['steel_bare'])
ps_f = L.panel_seam("pelvis_seam_f", 0.25, (0, -0.0805, 0.665), col, axis='X', width=0.006, depth=0.005, mat=M['steel_bare'])
ps_b = L.panel_seam("pelvis_seam_b", 0.25, (0, 0.0805, 0.665), col, axis='X', width=0.006, depth=0.005, mat=M['steel_bare'])
parts['pelvis'] = L.join([pelvis, skirt, pb_a, pb_b, ps_f, ps_b], "pelvis")

# Torso: caja encogida + nervios de refuerzo en los flancos (la carga de los brazos baja por ahí) + travesaño de hombros.
torso = shell("torso", (0.3, 0.2, 0.28), (0, 0, 0.72), M['polymer_ivory'], pivot='bottom', cham=0.005)
rib_l = L.rib_row("torso_rib_L", 0.16, (0.008, 0.1, 0.014), (-0.152, 0, 0.86), col, count=2, axis='Z', mat=M['steel_paint'])
rib_r = L.rib_row("torso_rib_R", 0.16, (0.008, 0.1, 0.014), (0.152, 0, 0.86), col, count=2, axis='Z', mat=M['steel_paint'])
clav = shell("clavicle", (0.34, 0.07, 0.035), (0, 0, 0.965), M['steel_dark'], cham=0.004)
parts['torso'] = L.join([torso, rib_l, rib_r, clav], "torso")

# Cubierta frontal sanitaria: atornillada arriba y abajo, con juntas verticales y placa de serie NÉMESIS en relieve.
cover = shell("torso_cover", (0.24, 0.03, 0.2), (0, -0.105, 0.76), M['polymer_ivory'], pivot='bottom', cham=0.004)
cb_a = L.bolt_row("cover_bolt_a", 0.0042, (-0.09, -0.1225, 0.775), (0.06, 0, 0), 4, col, axis='Y', mat=M['steel_bare'])
cb_b = L.bolt_row("cover_bolt_b", 0.0042, (-0.09, -0.1225, 0.945), (0.06, 0, 0), 4, col, axis='Y', mat=M['steel_bare'])
cs_l = L.panel_seam("cover_seam_L", 0.19, (-0.115, -0.1185, 0.86), col, axis='Z', width=0.005, depth=0.006, mat=M['steel_dark'])
cs_r = L.panel_seam("cover_seam_R", 0.19, (0.115, -0.1185, 0.86), col, axis='Z', width=0.005, depth=0.006, mat=M['steel_dark'])
serial = shell("serial_plate", (0.08, 0.005, 0.028), (0.055, -0.1195, 0.905), M['label'], cham=0.0015)
sdig = L.rib_row("serial_digits", 0.058, (0.007, 0.003, 0.016), (0.055, -0.1235, 0.905), col, count=4, axis='X', mat=M['steel_dark'])
parts['torso_cover'] = L.join([cover, cb_a, cb_b, cs_l, cs_r, serial, sdig], "torso_cover")

# Rendijas de refrigeración: dos rejillas con lamas reales sobre la cubierta (las lamas entran hacia el cuerpo).
v_a = L.vent("vent_a", (0.08, 0.022, 0.085), (-0.055, -0.1205, 0.815), col, slats=3, rot=(0, 0, RAD(180)), mat_frame=M['steel_dark'], mat_slat=M['steel_dark'])
v_b = L.vent("vent_b", (0.08, 0.022, 0.085), (0.055, -0.1205, 0.815), col, slats=3, rot=(0, 0, RAD(180)), mat_frame=M['steel_dark'], mat_slat=M['steel_dark'])
parts['vents'] = L.join([v_a, v_b], "vents")

# Panel posterior de mantenimiento: hundido con reborde (el AO lo ensombrece), atornillado, y rejilla de extracción arriba.
panel = L.recess("torso_panel", (0.22, 0.035, 0.18), (0, 0.0975, 0.845), col, depth=0.018, rot=(0, 0, RAD(180)), mat=M['steel_paint'], border=0.012)
nb_a = L.bolt_row("panel_bolt_a", 0.0042, (-0.095, 0.114, 0.762), (0.095, 0, 0), 3, col, axis='Y', mat=M['steel_bare'])
nb_b = L.bolt_row("panel_bolt_b", 0.0042, (-0.095, 0.114, 0.928), (0.095, 0, 0), 3, col, axis='Y', mat=M['steel_bare'])
bvent = L.vent("back_vent", (0.12, 0.028, 0.055), (0, 0.0985, 0.965), col, slats=3, mat_frame=M['steel_dark'], mat_slat=M['steel_dark'])
parts['torso_panel'] = L.join([panel, nb_a, nb_b, bvent], "torso_panel")

# Hombros: rótula + cazoleta atornillada al travesaño (la junta es visible, no una esfera flotando).
for side, sx in (("L", -1), ("R", 1)):
    sh = L.sphere(f"shoulder_{side}", 0.045, (sx * 0.17, 0, 0.95), col, segs=14, rings=9); L.assign(sh, M['steel_bare'])
    scap = shell(f"shoulder_cap_{side}", (0.085, 0.08, 0.055), (sx * 0.1725, 0, 0.962), M['polymer_ivory'], cham=0.004)
    sbo = L.bolt_row(f"shoulder_bolt_{side}", 0.004, (sx * 0.214, -0.025, 0.962), (0, 0.025, 0), 3, col, axis='X', mat=M['steel_bare'])
    parts[f"shoulder_{side}"] = L.join([sh, scap, sbo], f"shoulder_{side}")

# ---------------------------------------------------------------- cuello estrecho articulado
nbase = L.cyl("neck_base", 0.05, 0.03, (0, 0, 1.0), col, verts=20, pivot='bottom', bevel=0.005); L.assign(nbase, M['steel_bare'])
nbolt = L.bolt_row("neck_bolt", 0.0035, (-0.028, -0.03, 1.028), (0.028, 0, 0), 3, col, axis='Z', mat=M['steel_bare'])
parts['neck_base'] = L.join([nbase, nbolt], "neck_base")
# fuelle: sólo z 1.03–1.05 queda a la vista bajo la cabeza, los anillos van ahí y no dentro del cráneo
ncore = L.cyl("neck", 0.022, 0.06, (0, 0, 1.03), col, verts=12, pivot='bottom'); L.assign(ncore, M['rubber'])
bell = []
for i, z in enumerate((1.036, 1.046)):
    b = L.torus(f"neck_bellow{i}", 0.027, 0.005, (0, 0, z), col, axis='Z', segs=14, rings=6); L.assign(b, M['rubber']); bell.append(b)
parts['neck'] = L.join([ncore] + bell, "neck")

# ---------------------------------------------------------------- cabeza grande, sin boca, con cuencas geométricas
head = L.sphere("head", 0.11, (0, 0, 1.17), col, segs=28, rings=18, scale=(1.0, 1.08, 1.12)); L.assign(head, M['polymer_ivory'])
for side, sx in (("L", -1), ("R", 1)):
    cut = L.sphere(f"cut_{side}", 0.032, (sx * 0.042 + (0.004 if side == 'L' else 0), -0.095, 1.19), col, segs=16, rings=10)
    m = head.modifiers.new(f"Socket_{side}", 'BOOLEAN'); m.operation = 'DIFFERENCE'; m.object = cut
L.apply_all(head)
for side in ("L", "R"): bpy.data.objects.remove(bpy.data.objects[f"cut_{side}"])
L.chamfer(head, 0.0012, 1, 60)  # el borde de la cuenca deja de ser un corte infinitamente fino
brow = shell("brow", (0.13, 0.035, 0.018), (0, -0.093, 1.228), M['polymer_ivory'], rot=(RAD(-12), 0, 0), cham=0.002)
jaw = shell("jaw_plate", (0.09, 0.05, 0.03), (0, -0.086, 1.122), M['polymer_ivory'], rot=(RAD(15), 0, 0), cham=0.003)
hvent = L.vent("head_vent", (0.075, 0.026, 0.05), (0, 0.1105, 1.185), col, slats=3, mat_frame=M['steel_dark'], mat_slat=M['steel_dark'])
parts['head'] = L.join([head, brow, jaw, hvent], "head")

# cuencas: pieza interna oscura + aro de espesor en el borde (sin ojos luminosos permanentes, 12)
for side, sx in (("L", -1), ("R", 1)):
    inner = L.sphere(f"eye_core_{side}", 0.02, (sx * 0.042, -0.075, 1.19), col, segs=12, rings=8); L.assign(inner, M['polymer_dark'])
    rim = L.torus(f"eye_rim_{side}", 0.031, 0.0045, (sx * 0.042, -0.1, 1.19), col, axis='Y', segs=16, rings=6); L.assign(rim, M['steel_dark'])
    parts[f"eye_inner_{side}"] = L.join([inner, rim], f"eye_inner_{side}")

# placas temporales atornilladas (sugieren rostro humano sin reproducirlo, 36)
for side, sx in (("L", -1), ("R", 1)):
    plate = shell(f"temple_{side}", (0.02, 0.07, 0.06), (sx * 0.105, 0.0, 1.18), M['steel_paint'], cham=0.003)
    tb = L.bolt_row(f"temple_bolt_{side}", 0.0035, (sx * 0.1155, -0.022, 1.18), (0, 0.022, 0), 3, col, axis='X', mat=M['steel_bare'])
    parts[f"temple_{side}"] = L.join([plate, tb], f"temple_{side}")

# óptica frontal: carcasa, tubo, junta de goma y lente. No emite: la amenaza sobrevive sin luz roja (36).
oh = shell("optic_housing", (0.042, 0.03, 0.034), (0, -0.088, 1.252), M['steel_dark'], cham=0.002)
ob = L.cyl("optic_barrel", 0.013, 0.024, (0, -0.1, 1.252), col, axis='Y', verts=16, bevel=0.002); L.assign(ob, M['steel_bare'])
og = L.torus("optic_gasket", 0.0145, 0.0035, (0, -0.1065, 1.252), col, axis='Y', segs=16, rings=6); L.assign(og, M['rubber'])
ol = L.cyl("optic_lens", 0.011, 0.004, (0, -0.11, 1.252), col, axis='Y', verts=16); L.assign(ol, M['glass'])
parts['optic'] = L.join([oh, ob, og, ol], "optic")

# ---------------------------------------------------------------- brazos con antebrazos largos
for side, sx in (("L", -1), ("R", 1)):
    x = sx * 0.17
    up = L.cyl(f"upperarm_{side}", 0.03, 0.22, (x, 0, 0.95), col, pivot='bottom', verts=16, bevel=0.004)
    up.rotation_euler = (RAD(180), 0, 0); L.assign(up, M['polymer_dark'])
    useam = L.panel_seam(f"ua_seam_{side}", 0.18, (x, -0.031, 0.84), col, axis='Z', width=0.005, depth=0.005, mat=M['steel_dark'])
    acab = cable(f"arm_cable_{side}", [(sx * 0.196, 0.018, 0.945), (sx * 0.204, 0.024, 0.88), (sx * 0.198, 0.022, 0.8), (sx * 0.184, 0.018, 0.745)], 0.005)
    parts[f"upperarm_{side}"] = L.join([up, useam, acab], f"upperarm_{side}")

    el = L.sphere(f"elbow_{side}", 0.035, (x, 0, 0.73), col, segs=14, rings=9); L.assign(el, M['steel_bare'])
    ering = L.torus(f"elbow_ring_{side}", 0.033, 0.006, (x, 0, 0.73), col, axis='Z', segs=14, rings=6); L.assign(ering, M['rubber'])
    parts[f"elbow_{side}"] = L.join([el, ering], f"elbow_{side}")

    fa = L.cyl(f"forearm_{side}", 0.028, 0.3, (x, 0, 0.73), col, pivot='bottom', verts=16, bevel=0.004)
    fa.rotation_euler = (RAD(180), 0, 0); L.assign(fa, M['polymer_ivory'])
    fplate = shell(f"forearm_plate_{side}", (0.05, 0.028, 0.18), (x, -0.032, 0.585), M['steel_paint'], cham=0.003)
    fbo = L.bolt_row(f"forearm_bolt_{side}", 0.0038, (x, -0.0475, 0.52), (0, 0, 0.065), 3, col, axis='Y', mat=M['steel_bare'])
    wrist = L.cyl(f"wrist_{side}", 0.026, 0.035, (x, 0, 0.445), col, verts=12, bevel=0.004); L.assign(wrist, M['steel_bare'])
    parts[f"forearm_{side}"] = L.join([fa, fplate, fbo, wrist], f"forearm_{side}")

    palm = shell(f"palm_{side}", (0.05, 0.03, 0.06), (x, 0, 0.43), M['polymer_dark'], pivot='top', cham=0.004)
    pad = shell(f"palm_pad_{side}", (0.04, 0.006, 0.045), (x, -0.017, 0.4), M['rubber'], cham=0.002)
    parts[f"palm_{side}"] = L.join([palm, pad], f"palm_{side}")

    # manos finas con dedos demasiado largos: dos falanges, nudillos y yema (pulidos por roce en el material)
    fingers = []
    for i in range(3):
        fx = x + (i - 1) * 0.018
        p0 = L.cyl(f"finger_{side}{i}a", 0.007, 0.055, (fx, -0.005, 0.37), col, verts=8, pivot='bottom'); p0.rotation_euler = (RAD(180), 0, 0); L.assign(p0, M['polymer_ivory'])
        k0 = L.sphere(f"knuckle_{side}{i}a", 0.0085, (fx, -0.005, 0.37), col, segs=8, rings=4); L.assign(k0, M['steel_bare'])
        p1 = L.cyl(f"finger_{side}{i}b", 0.006, 0.045, (fx, -0.005, 0.315), col, verts=8, pivot='bottom'); p1.rotation_euler = (RAD(180), 0, 0); L.assign(p1, M['polymer_ivory'])
        k1 = L.sphere(f"knuckle_{side}{i}b", 0.0075, (fx, -0.005, 0.315), col, segs=8, rings=4); L.assign(k1, M['steel_bare'])
        tip = L.sphere(f"fingertip_{side}{i}", 0.0065, (fx, -0.005, 0.272), col, segs=8, rings=4); L.assign(tip, M['steel_bare'])
        fingers += [p0, k0, p1, k1, tip]
    parts[f"fingers_{side}"] = L.join(fingers, f"fingers_{side}")

# ---------------------------------------------------------------- lanzador de red (antebrazo derecho)
# Módulo atornillado al antebrazo por dos abrazaderas, tapa de apertura con su tornillería, bobina con devanado visible,
# guía con boca y cable de alimentación que queda DENTRO del antebrazo (antes cruzaba codo y hombro y se despegaba al
# levantar el brazo en Anticipation/Net).
launcher = shell("launcher", (0.06, 0.09, 0.14), (0.205, -0.02, 0.55), M['steel_paint'], cham=0.004)
hatch = shell("launcher_hatch", (0.007, 0.07, 0.1), (0.2315, -0.025, 0.55), M['steel_dark'], cham=0.002)
hbolt = L.bolt_row("launcher_bolt", 0.0038, (0.234, -0.025, 0.505), (0, 0, 0.03), 4, col, axis='X', mat=M['steel_bare'])
brk = []
for i, z in enumerate((0.5, 0.605)):
    b = L.torus(f"launcher_bracket{i}", 0.032, 0.006, (0.17, 0, z), col, axis='Z', segs=14, rings=6); L.assign(b, M['steel_dark']); brk.append(b)
parts['launcher'] = L.join([launcher, hatch, hbolt] + brk, "launcher")

coil = L.cyl("launcher_coil", 0.025, 0.05, (0.205, -0.02, 0.62), col, axis='Y', verts=20, bevel=0.003); L.assign(coil, M['copper'])
wind = []
for i, y in enumerate((-0.032, -0.008)):
    w = L.torus(f"coil_wind{i}", 0.027, 0.005, (0.205, y, 0.62), col, axis='Y', segs=14, rings=6); L.assign(w, M['copper']); wind.append(w)
parts['launcher_coil'] = L.join([coil] + wind, "launcher_coil")

guide = L.cyl("launcher_guide", 0.018, 0.08, (0.205, -0.08, 0.55), col, axis='Y', verts=16, bevel=0.003); L.assign(guide, M['steel_dark'])
muzzle = L.torus("launcher_muzzle", 0.019, 0.004, (0.205, -0.118, 0.55), col, axis='Y', segs=14, rings=6); L.assign(muzzle, M['steel_bare'])
parts['launcher_guide'] = L.join([guide, muzzle], "launcher_guide")

parts['launcher_cable'] = cable("launcher_cable", [(0.203, -0.005, 0.645), (0.213, 0.015, 0.675), (0.198, 0.028, 0.705), (0.178, 0.026, 0.723)], 0.005)

# UV por pieza y suavizado (finish_asset.py rehace el atlas compartido del asset, 40.3)
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
    "head": ["head", "eye_inner_L", "eye_inner_R", "temple_L", "temple_R", "optic"],
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
walk = L.walk_cycle(arm, "Vigia_Walk", **L.WALK_PRESETS[ASSET])
L.push_nla(arm, walk)
antic = L.action(arm, "Vigia_Anticipation", 33, loop=False, poses={1: {"upperarm_R": ((0, 0, 0), Z), "forearm_R": ((0, 0, 0), Z), "spine": ((0, 0, 0), Z)}, 12: {"upperarm_R": ((-70, 0, -20), Z), "forearm_R": ((-40, 0, 0), Z), "spine": ((-6, 0, 0), Z), "head": ((6, 0, 0), Z)}, 33: {"upperarm_R": ((-95, 0, -25), Z), "forearm_R": ((-30, 0, 0), Z), "spine": ((-8, 0, 0), Z), "head": ((8, 0, 0), Z)}})
L.push_nla(arm, antic)
net = L.action(arm, "Vigia_Net", 42, loop=False, poses={1: {"upperarm_R": ((-95, 0, -25), Z), "forearm_R": ((-30, 0, 0), Z), "spine": ((-8, 0, 0), Z)}, 4: {"upperarm_R": ((-100, 0, -20), Z), "forearm_R": ((-5, 0, 0), Z), "spine": ((4, 0, 0), Z)}, 42: {"upperarm_R": ((0, 0, 0), Z), "forearm_R": ((0, 0, 0), Z), "spine": ((0, 0, 0), Z), "head": ((0, 0, 0), Z)}})
L.push_nla(arm, net)
death = L.action(arm, "Vigia_Death", 36, loop=False, poses={1: {"root": ((0, 0, 0), Z)}, 14: {"spine": ((25, 0, 10), Z), "thigh_L": ((30, 0, 0), Z), "thigh_R": ((-10, 0, 0), Z), "root": ((0, 0, 0), (0, 0, -0.15))}, 36: {"root": ((80, 0, 15), (0, -0.2, -0.55)), "spine": ((10, 0, 20), Z), "head": ((-20, 0, 25), Z), "upperarm_L": ((40, 0, 30), Z)}})
L.push_nla(arm, death)

objs = list(parts.values())
tris = 0
for o in objs:
    o.data.calc_loop_triangles(); tris += len(o.data.loop_triangles)
blend = L.save_blend(ASSET)
print("built vigia", len(objs), "piezas", tris, "tris")
