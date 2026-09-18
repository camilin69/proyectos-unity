# BOT-02 CUSTODIO-06 (13 y 36.2): 2.22 m de maquinaria de contención pesada.
# El tórax deja de ser una caja: es un casco blindado con placas atornilladas de SOLAPE REAL, juntas, soldaduras
# y líneas de fundición (36.2 las pide por su nombre). Refuerzos de carga donde hay carga —hombro del arma y caderas—,
# emisor de rayo con aislantes cerámicos, núcleo, disipador y condensadores, pistones con topes físicos en las piernas
# y cableado dentro de conductos protegidos (36.4: el cable no cruza dos huesos).
# Cada detalle tiene causa (33.2 / 41.3): tornillo donde algo se atornilla, junta donde dos chapas se encuentran,
# rejilla donde algo respira, soldadura y pintura distinta donde se reparó, goma donde roza el suelo.
# Presupuesto 43 (Custodio, perfil base LOD0): 20–35k tris. Objetivo de este build ~28k.
# Rig, nombres de huesos, binding y los 6 clips se conservan exactamente.
import bpy, math, importlib, sys
sys.path.insert(0, r"C:/Users/HP/Documents/GitHub/proyectos-unity/SourceArt/Scripts")
import esn_lib as L; importlib.reload(L)

ASSET = "BOT-02_Custodio"
L.reset_scene()
col = L.collection(ASSET)
M = L.std_mats()
# Materiales propios: la reparación y el calor son causas visibles, no grunge decorativo (41.3).
M['weld'] = L.material("M_Weld", (0.40, 0.38, 0.36), 0.62, 1.0, wear=0.35, wear_color=(0.30, 0.22, 0.16), bump=0.45, scale=70)
M['paint_new'] = L.material("M_PaintRepair", (0.29, 0.33, 0.39), 0.48, 0.0, wear=0.10, wear_color=(0.46, 0.46, 0.43), bump=0.12)
M['heat'] = L.material("M_HeatSteel", (0.27, 0.25, 0.29), 0.36, 1.0, wear=0.42, wear_color=(0.34, 0.26, 0.40), bump=0.12, scale=12)

P = {}
BIND = {}


def add(key, obj, bone, mat=None):
    """Registra una pieza: colección, material y hueso quedan resueltos en el mismo sitio donde se crea."""
    if mat is not None: L.assign(obj, mat)
    P[key] = obj
    BIND.setdefault(bone, []).append(key)
    return obj


def group(parts, key, bone):
    """Une un racimo de detalle en una sola pieza rígida del hueso que le corresponde."""
    if len(parts) == 1:
        parts[0].name = key
        return add(key, parts[0], bone)
    return add(key, L.join(parts, key), bone)


def bolts(name, r, start, step, count, axis='Z', mat=None, flip=False):
    """Fila de tornillos. L.bolt_row orienta la cabeza a +X / -Y / +Z; `flip` la gira para caras opuestas."""
    mat = mat or M['steel_bare']
    if not flip:
        return L.bolt_row(name, r, start, step, count, col, axis=axis, mat=mat)
    parts = []
    for i in range(count):
        p = (start[0] + step[0] * i, start[1] + step[1] * i, start[2] + step[2] * i)
        b = L.bolt(f"{name}{i}", r, p, col, axis=axis)
        b.rotation_euler = (0, math.radians(180), 0) if axis == 'X' else (math.radians(180), 0, 0)
        L.assign(b, mat); parts.append(b)
    return L.join(parts, name) if len(parts) > 1 else parts[0]


def recess_at(name, size, loc, depth=None, rot=(0, 0, 0), mat=None, border=None):
    """L.recess une sus cinco piezas sobre el listón superior, así que el origen del grupo queda en el borde de
    arriba y `location` desplaza la placa media altura hacia abajo. Se recoloca para que `loc` sea el centro real."""
    b = border if border is not None else min(size[0], size[2]) * 0.08
    o = L.recess(name, size, loc, col, depth=depth, rot=rot, mat=mat, border=border)
    o.location = (loc[0], loc[1], loc[2] + (size[2] - b) / 2)
    return o


def ribs_at(name, length, size, loc, count=5, axis='Y', mat=None):
    """Igual que L.rib_row, pero centrando la fila en `loc`: el origen del grupo cae en el primer nervio."""
    o = L.rib_row(name, length, size, loc, col, count=count, axis=axis, mat=mat)
    t = -length / 2 + length * 0.5 / count
    d = (0, t, 0) if axis == 'Y' else ((t, 0, 0) if axis == 'X' else (0, 0, t))
    o.location = (loc[0] + d[0], loc[1] + d[1], loc[2] + d[2])
    return o


R180 = (0, 0, math.radians(180))

# ================================ PIERNAS ================================
# Casi humanas y pesadas: suela de goma con tacos, fuelle de tobillo, espinilla blindada con placa hundida,
# pistón con camisa y horquilla, rodilla con topes que la bloquean al detenerse (13).
for side, sx in (("L", -1), ("R", 1)):
    X = sx * 0.19

    # --- pie: la goma toca el suelo, el acero recibe el peso ---
    parts = []
    sole = L.box(f"foot_{side}", (0.18, 0.32, 0.05), (X, 0.04, 0.0), col, pivot='bottom', bevel=0.012)
    L.assign(sole, M['rubber']); parts.append(sole)
    inst = L.box(f"foot_inst_{side}", (0.16, 0.14, 0.04), (X, 0.10, 0.05), col, pivot='bottom', bevel=0.01)
    L.assign(inst, M['steel_paint']); parts.append(inst)
    toe = L.box(f"foot_toe_{side}", (0.17, 0.09, 0.035), (X, -0.09, 0.05), col, pivot='bottom', bevel=0.008)
    L.assign(toe, M['steel_bare']); parts.append(toe)
    parts.append(ribs_at(f"foot_tread_{side}", 0.22, (0.155, 0.03, 0.014), (X, 0.04, 0.008), count=2, axis='Y', mat=M['rubber']))
    parts.append(bolts(f"foot_bolt_{side}", 0.009, (X - 0.055, 0.10, 0.092), (0.055, 0, 0), 3, axis='Z', mat=M['steel_bare']))
    group(parts, f"foot_{side}", f"foot_{side}")

    # --- tobillo: eje, pasador y fuelle de goma que protege la articulación ---
    parts = []
    ank = L.cyl(f"ankle_{side}", 0.06, 0.13, (X, 0.0, 0.08), col, axis='X', verts=16)
    L.assign(ank, M['steel_bare']); parts.append(ank)
    for i, zz in enumerate((0.115, 0.155)):
        bel = L.torus(f"ankle_bel{i}_{side}", 0.055, 0.014, (X, 0.0, zz), col, axis='Z', segs=14, rings=6)
        L.assign(bel, M['rubber']); parts.append(bel)
    pin = L.bolt(f"ankle_pin_{side}", 0.014, (X + sx * 0.062, 0.0, 0.08), col, axis='X', kind='round')
    if sx < 0: pin.rotation_euler = (0, math.radians(180), 0)
    L.assign(pin, M['steel_dark']); parts.append(pin)
    group(parts, f"ankle_{side}", f"shin_{side}")

    # --- espinilla: chapa pintada con chaflán en toda arista viva ---
    shin = L.box(f"shin_{side}", (0.12, 0.14, 0.42), (X, 0.0, 0.1), col, pivot='bottom')
    L.assign(shin, M['steel_paint']); L.chamfer(shin, 0.0035, 2, 45)
    add(f"shin_{side}", shin, f"shin_{side}")

    parts = []
    parts.append(recess_at(f"shin_plate_{side}", (0.10, 0.028, 0.26), (X, -0.072, 0.28), depth=0.014, mat=M['steel_paint'], border=0.012))
    parts.append(bolts(f"shin_bolt_a_{side}", 0.008, (X - 0.043, -0.087, 0.17), (0, 0, 0.075), 3, axis='Y', mat=M['steel_bare']))
    parts.append(bolts(f"shin_bolt_b_{side}", 0.008, (X + 0.043, -0.087, 0.17), (0, 0, 0.075), 3, axis='Y', mat=M['steel_bare']))
    parts.append(L.panel_seam(f"shin_seam_{side}", 0.40, (X + sx * 0.061, 0.0, 0.30), col, axis='Z', width=0.006, depth=0.008, mat=M['weld']))
    guard = L.box(f"shin_guard_{side}", (0.13, 0.10, 0.10), (X, -0.032, 0.47), col, bevel=0.012)
    L.assign(guard, M['steel_dark']); parts.append(guard)
    group(parts, f"shin_det_{side}", f"shin_{side}")

    # --- pistón: vástago, camisa, horquilla y latiguillo. Tope real en la carrera ---
    parts = []
    rod = L.cyl(f"piston_{side}", 0.018, 0.34, (X + sx * 0.068, 0.062, 0.12), col, pivot='bottom', verts=12)
    L.assign(rod, M['steel_bare']); parts.append(rod)
    slv = L.cyl(f"piston_slv_{side}", 0.028, 0.17, (X + sx * 0.068, 0.062, 0.26), col, pivot='bottom', verts=12, bevel=0.006)
    L.assign(slv, M['steel_dark']); parts.append(slv)
    cap = L.cyl(f"piston_cap_{side}", 0.032, 0.022, (X + sx * 0.068, 0.062, 0.435), col, verts=12)
    L.assign(cap, M['steel_dark']); parts.append(cap)
    clv = L.box(f"piston_clv_{side}", (0.032, 0.05, 0.05), (X + sx * 0.068, 0.062, 0.12), col, bevel=0.006)
    L.assign(clv, M['steel_bare']); parts.append(clv)
    pb = L.bolt(f"piston_bolt_{side}", 0.011, (X + sx * 0.068, 0.062, 0.12), col, axis='X', kind='round')
    if sx < 0: pb.rotation_euler = (0, math.radians(180), 0)
    L.assign(pb, M['steel_bare']); parts.append(pb)
    hose = L.tube(f"piston_hose_{side}", [(X + sx * 0.068, 0.088, 0.41), (X + sx * 0.055, 0.108, 0.50),
                                          (X + sx * 0.03, 0.10, 0.60), (X, 0.082, 0.68)], 0.008, col, verts=8)
    L.assign(hose, M['rubber']); parts.append(hose)
    group(parts, f"piston_{side}", f"thigh_{side}")

    # --- rodilla: eje, rótula y dos topes que explican por qué se bloquea ---
    parts = []
    kn = L.cyl(f"knee_{side}", 0.075, 0.17, (X, 0.0, 0.55), col, axis='X', verts=16)
    L.assign(kn, M['steel_dark']); parts.append(kn)
    kc = L.box(f"knee_cap_{side}", (0.10, 0.11, 0.13), (X, -0.036, 0.55), col, bevel=0.016)
    L.assign(kc, M['steel_paint']); parts.append(kc)
    for i, (yy, zz) in enumerate(((0.056, 0.63), (-0.02, 0.47))):
        st = L.box(f"knee_stop{i}_{side}", (0.09, 0.03, 0.028), (X, yy, zz), col, bevel=0.006)
        L.assign(st, M['steel_bare']); parts.append(st)
    parts.append(bolts(f"knee_bolt_{side}", 0.009, (X + sx * 0.079, -0.036, 0.51), (0, 0, 0.04), 3, axis='X', mat=M['steel_bare'], flip=(sx < 0)))
    group(parts, f"knee_{side}", f"thigh_{side}")

    # --- muslo: núcleo de polímero + dos placas de acero que se solapan, con junta soldada y tornillería ---
    th = L.box(f"thigh_{side}", (0.15, 0.18, 0.5), (X, 0.0, 0.55), col, pivot='bottom')
    L.assign(th, M['polymer_dark']); L.chamfer(th, 0.004, 2, 45)
    add(f"thigh_{side}", th, f"thigh_{side}")

    parts = []
    up = L.box(f"thigh_pl_up_{side}", (0.145, 0.035, 0.24), (X, -0.086, 0.92), col, bevel=0.008)
    L.assign(up, M['steel_paint']); parts.append(up)
    lo = L.box(f"thigh_pl_lo_{side}", (0.135, 0.030, 0.22), (X, -0.079, 0.70), col, bevel=0.008)
    L.assign(lo, M['steel_paint']); parts.append(lo)
    parts.append(L.panel_seam(f"thigh_seam_{side}", 0.14, (X, -0.098, 0.805), col, axis='X', width=0.009, depth=0.010, mat=M['weld']))
    parts.append(bolts(f"thigh_bolt_a_{side}", 0.0085, (X - 0.055, -0.106, 0.86), (0.055, 0, 0), 3, axis='Y', mat=M['steel_bare']))
    parts.append(bolts(f"thigh_bolt_b_{side}", 0.0085, (X - 0.05, -0.097, 0.63), (0.05, 0, 0), 3, axis='Y', mat=M['steel_bare']))
    hipg = L.box(f"hip_shroud_{side}", (0.16, 0.19, 0.12), (X, 0.0, 0.98), col, bevel=0.018)
    L.assign(hipg, M['steel_dark']); parts.append(hipg)
    group(parts, f"thigh_det_{side}", f"thigh_{side}")

    # Asimetría con causa (36.2): la pierna del lado del arma carga más y lleva nervios de refuerzo;
    # la contraria arrastra un parche de reparación con pintura distinta y cordón de soldadura.
    if side == "R":
        rib = ribs_at(f"thigh_rib_{side}", 0.28, (0.024, 0.11, 0.024), (X + sx * 0.077, 0.005, 0.82), count=3, axis='Z', mat=M['steel_bare'])
        add(f"thigh_rib_{side}", rib, f"thigh_{side}")
    else:
        parts = []
        pat = L.box(f"thigh_patch_{side}", (0.022, 0.12, 0.17), (X + sx * 0.078, 0.005, 0.82), col, bevel=0.006)
        L.assign(pat, M['paint_new']); parts.append(pat)
        parts.append(bolts(f"thigh_patch_bolt_{side}", 0.008, (X + sx * 0.090, -0.045, 0.75), (0, 0.045, 0), 3, axis='X', mat=M['steel_bare'], flip=True))
        wl = L.tube(f"thigh_patch_weld_{side}", [(X + sx * 0.078, -0.058, 0.906), (X + sx * 0.078, 0.005, 0.912), (X + sx * 0.078, 0.065, 0.906)], 0.005, col, verts=6)
        L.assign(wl, M['weld']); parts.append(wl)
        group(parts, f"thigh_patch_{side}", f"thigh_{side}")

# ================================ PELVIS ================================
# Donde el peso del tórax baja a las piernas: faja atornillada, cartelas de cadera y yugos de fémur.
pelvis = L.box("pelvis", (0.44, 0.28, 0.18), (0, 0, 1.05), col, pivot='bottom')
L.assign(pelvis, M['steel_dark']); L.chamfer(pelvis, 0.005, 2, 45)
add('pelvis', pelvis, 'pelvis')

parts = []
parts.append(recess_at("pelvis_plate", (0.30, 0.035, 0.11), (0, -0.152, 1.13), depth=0.016, mat=M['steel_paint'], border=0.014))
parts.append(bolts("pelvis_bolt_a", 0.009, (-0.135, -0.162, 1.185), (0.09, 0, 0), 4, axis='Y', mat=M['steel_bare']))
parts.append(bolts("pelvis_bolt_b", 0.009, (-0.135, -0.162, 1.075), (0.09, 0, 0), 4, axis='Y', mat=M['steel_bare']))
for sx in (-1, 1):
    sd = 'L' if sx < 0 else 'R'
    gus = L.box(f"hip_gusset_{sd}", (0.06, 0.16, 0.14), (sx * 0.19, 0.0, 1.06), col, bevel=0.01)
    L.assign(gus, M['steel_bare']); parts.append(gus)
    yok = L.cyl(f"hip_yoke_{sd}", 0.055, 0.09, (sx * 0.19, 0.0, 1.05), col, axis='X', verts=14)
    L.assign(yok, M['steel_dark']); parts.append(yok)
parts.append(L.vent("pelvis_vent", (0.20, 0.03, 0.09), (0, 0.143, 1.13), col, slats=3, rot=R180, mat_frame=M['steel_dark'], mat_slat=M['steel_bare']))
group(parts, 'pelvis_det', 'pelvis')

# columna: fuelle de goma entre pelvis y tórax
parts = []
sp = L.cyl("spine_col", 0.07, 0.16, (0, 0.04, 1.23), col, pivot='bottom', verts=14)
L.assign(sp, M['rubber']); parts.append(sp)
for i, zz in enumerate((1.27, 1.34)):
    rg = L.torus(f"spine_bel{i}", 0.073, 0.016, (0, 0.04, zz), col, axis='Z', segs=14, rings=6)
    L.assign(rg, M['rubber']); parts.append(rg)
group(parts, 'spine_col', 'pelvis')

# ================================ TÓRAX ================================
torso = L.box("torso", (0.62, 0.36, 0.5), (0, 0, 1.36), col, pivot='bottom')
L.assign(torso, M['steel_paint']); L.chamfer(torso, 0.008, 2, 42)
add('torso', torso, 'spine')

# --- pecho: placa inferior + placa superior que MONTA sobre ella, junta y cordón de soldadura ---
parts = []
chest = L.box("chest_plate", (0.50, 0.05, 0.24), (0, -0.190, 1.53), col)
L.assign(chest, M['steel_paint']); L.chamfer(chest, 0.005, 2, 42); parts.append(chest)
chup = L.box("chest_upper", (0.46, 0.05, 0.18), (0, -0.200, 1.71), col)
L.assign(chup, M['steel_paint']); L.chamfer(chup, 0.005, 2, 42); parts.append(chup)
parts.append(L.panel_seam("chest_seam", 0.46, (0, -0.228, 1.632), col, axis='X', width=0.010, depth=0.012, mat=M['weld']))
wb = L.tube("chest_weld", [(-0.23, -0.226, 1.618), (-0.08, -0.229, 1.622), (0.08, -0.229, 1.622), (0.23, -0.226, 1.618)], 0.006, col, verts=6)
L.assign(wb, M['weld']); parts.append(wb)
parts.append(recess_at("chest_recess", (0.30, 0.04, 0.14), (0, -0.222, 1.52), depth=0.018, mat=M['steel_paint'], border=0.014))
parts.append(bolts("chest_bolt_l", 0.010, (-0.215, -0.222, 1.44), (0, 0, 0.075), 3, axis='Y', mat=M['steel_bare']))
parts.append(bolts("chest_bolt_r", 0.010, (0.215, -0.222, 1.44), (0, 0, 0.075), 3, axis='Y', mat=M['steel_bare']))
parts.append(bolts("chest_bolt_up", 0.010, (-0.165, -0.232, 1.775), (0.11, 0, 0), 4, axis='Y', mat=M['steel_bare']))
# número de unidad borrado: chapa grabada, no textura suelta
plate_n = L.box("unit_plate", (0.10, 0.012, 0.05), (0.14, -0.222, 1.455), col, bevel=0.004)
L.assign(plate_n, M['steel_bare']); parts.append(plate_n)
parts.append(bolts("unit_bolt", 0.006, (0.10, -0.230, 1.455), (0.08, 0, 0), 2, axis='Y', mat=M['steel_bare']))
group(parts, 'chest_plate', 'spine')

# --- placa de reparación en el hombro opuesto al arma: pintura distinta, tornillos nuevos, cordón perimetral ---
parts = []
rep = L.box("repair_plate", (0.19, 0.03, 0.17), (-0.155, -0.222, 1.70), col, bevel=0.005)
L.assign(rep, M['paint_new']); parts.append(rep)
parts.append(bolts("repair_bolt_a", 0.008, (-0.225, -0.236, 1.765), (0.07, 0, 0), 3, axis='Y', mat=M['steel_bare']))
parts.append(bolts("repair_bolt_b", 0.008, (-0.225, -0.236, 1.635), (0.07, 0, 0), 3, axis='Y', mat=M['steel_bare']))
rw = L.tube("repair_weld", [(-0.25, -0.222, 1.616), (-0.06, -0.224, 1.616), (-0.06, -0.224, 1.786), (-0.25, -0.222, 1.786)], 0.005, col, verts=6)
L.assign(rw, M['weld']); parts.append(rw)
group(parts, 'repair_plate', 'spine')

# --- espalda: panel de mantenimiento hundido, atornillado, con su rejilla ---
parts = []
bp = L.box("back_panel", (0.46, 0.04, 0.40), (0, 0.19, 1.40), col, pivot='bottom')
L.assign(bp, M['polymer_dark']); L.chamfer(bp, 0.004, 2, 45); parts.append(bp)
parts.append(recess_at("back_recess", (0.30, 0.035, 0.20), (0, 0.1945, 1.56), depth=0.016, rot=R180, mat=M['steel_paint'], border=0.014))
parts.append(bolts("back_bolt_l", 0.009, (-0.185, 0.2035, 1.47), (0, 0, 0.09), 3, axis='Y', mat=M['steel_bare'], flip=True))
parts.append(bolts("back_bolt_r", 0.009, (0.185, 0.2035, 1.47), (0, 0, 0.09), 3, axis='Y', mat=M['steel_bare'], flip=True))
parts.append(L.vent("back_vent", (0.24, 0.032, 0.10), (0, 0.193, 1.74), col, slats=3, rot=R180, mat_frame=M['steel_dark'], mat_slat=M['heat']))
parts.append(L.panel_seam("cast_seam_back", 0.42, (0, 0.2055, 1.60), col, axis='Z', width=0.007, depth=0.008, mat=M['steel_dark']))
group(parts, 'back_panel', 'spine')

# --- costillas laterales: nervios de chapa reforzada, no seis palos sueltos ---
ribL = ribs_at("rib_L", 0.34, (0.03, 0.30, 0.03), (-0.316, 0.0, 1.58), count=2, axis='Z', mat=M['steel_bare'])
ribR = ribs_at("rib_R", 0.34, (0.03, 0.30, 0.03), (0.316, 0.0, 1.58), count=2, axis='Z', mat=M['steel_bare'])
group([ribL, ribR], 'ribs', 'spine')

# --- líneas de fundición verticales en los flancos + collar de cuello ---
parts = []
for sx in (-1, 1):
    parts.append(L.panel_seam(f"cast_seam_{'L' if sx < 0 else 'R'}", 0.46, (sx * 0.312, -0.06, 1.60), col, axis='Z', width=0.007, depth=0.008, mat=M['steel_dark']))
collar = L.torus("collar", 0.095, 0.022, (0, 0.02, 1.855), col, axis='Z', segs=20, rings=8)
L.assign(collar, M['steel_dark']); parts.append(collar)
group(parts, 'torso_seams', 'spine')

# --- refuerzos de carga en los hombros: el del arma lleva dos cartelas, el otro una ---
parts = []
for i, (bx, bz) in enumerate(((0.26, 1.80), (0.33, 1.76))):
    br = L.box(f"brace_R{i}", (0.09, 0.14, 0.10), (bx, 0.0, bz), col, rot=(0, math.radians(-16), 0), bevel=0.012)
    L.assign(br, M['steel_bare']); parts.append(br)
parts.append(bolts("brace_bolt_R", 0.009, (0.30, -0.062, 1.845), (0, 0.062, 0), 3, axis='Z', mat=M['steel_bare']))
group(parts, 'brace_R', 'spine')

parts = []
bl = L.box("brace_L0", (0.08, 0.13, 0.09), (-0.27, 0.0, 1.79), col, rot=(0, math.radians(14), 0), bevel=0.012)
L.assign(bl, M['steel_bare']); parts.append(bl)
parts.append(bolts("brace_bolt_L", 0.008, (-0.27, -0.05, 1.835), (0, 0.05, 0), 2, axis='Z', mat=M['steel_bare']))
group(parts, 'brace_L', 'spine')

# --- conducto de alimentación del tórax: el cable va protegido, dentro de su hueso ---
parts = []
cd = L.tube("torso_conduit", [(0.10, 0.192, 1.42), (0.16, 0.188, 1.55), (0.20, 0.174, 1.68), (0.235, 0.132, 1.78)], 0.016, col, verts=8)
L.assign(cd, M['polymer_dark']); parts.append(cd)
for i, (cx, cy, cz) in enumerate(((0.155, 0.19, 1.545), (0.225, 0.147, 1.765))):
    cl = L.box(f"conduit_clamp{i}", (0.045, 0.02, 0.028), (cx, cy, cz), col, bevel=0.005)
    L.assign(cl, M['steel_bare']); parts.append(cl)
group(parts, 'torso_conduit', 'spine')

# ================================ HOMBROS ================================
# Derecho (arma): hombrera de dos placas solapadas con reborde y tornillería. Izquierdo: más simple y más gastado.
parts = []
shR = L.sphere("shoulder_R", 0.13, (0.40, 0, 1.80), col, segs=18, rings=12, scale=(1, 1.1, 0.9))
L.assign(shR, M['steel_paint']); parts.append(shR)
pa = L.box("pauldron_R0", (0.055, 0.26, 0.13), (0.425, 0.0, 1.84), col, rot=(0, math.radians(-12), 0), bevel=0.014)
L.assign(pa, M['steel_paint']); parts.append(pa)
pb2 = L.box("pauldron_R1", (0.05, 0.22, 0.11), (0.445, 0.0, 1.73), col, rot=(0, math.radians(-8), 0), bevel=0.012)
L.assign(pb2, M['steel_paint']); parts.append(pb2)
rim = L.torus("pauldron_rim_R", 0.115, 0.015, (0.40, 0.0, 1.80), col, axis='X', segs=18, rings=6)
L.assign(rim, M['steel_bare']); parts.append(rim)
parts.append(bolts("pauldron_bolt_R", 0.009, (0.452, -0.09, 1.855), (0, 0.09, 0), 3, axis='X', mat=M['steel_bare']))
group(parts, 'shoulder_R', 'spine')

parts = []
shL = L.sphere("shoulder_L", 0.09, (-0.37, 0, 1.80), col, segs=16, rings=10)
L.assign(shL, M['steel_bare']); parts.append(shL)
pl = L.box("pauldron_L0", (0.045, 0.19, 0.10), (-0.392, 0.0, 1.83), col, rot=(0, math.radians(10), 0), bevel=0.012)
L.assign(pl, M['steel_bare']); parts.append(pl)
rimL = L.torus("pauldron_rim_L", 0.082, 0.012, (-0.37, 0.0, 1.80), col, axis='X', segs=14, rings=6)
L.assign(rimL, M['steel_dark']); parts.append(rimL)
parts.append(bolts("pauldron_bolt_L", 0.008, (-0.418, -0.06, 1.845), (0, 0.06, 0), 3, axis='X', mat=M['steel_bare'], flip=True))
group(parts, 'shoulder_L', 'spine')

# ================================ BRAZOS ================================
for side, sx in (("L", -1), ("R", 1)):
    AX = -0.37 if side == 'L' else 0.40
    thick = 0.055 if side == 'L' else 0.07

    # --- brazo: tubo + carenado atornillado ---
    parts = []
    up = L.cyl(f"upperarm_{side}", thick, 0.36, (AX, 0, 1.80), col, pivot='bottom', verts=16, bevel=0.008)
    up.rotation_euler = (math.radians(180), 0, 0)
    L.assign(up, M['polymer_dark']); parts.append(up)
    for i, yy in enumerate((-0.055, 0.052)):
        sh = L.box(f"ua_shroud{i}_{side}", (thick * 1.9, 0.03, 0.22), (AX, yy, 1.63), col, bevel=0.008)
        L.assign(sh, M['steel_paint']); parts.append(sh)
    parts.append(bolts(f"ua_bolt_{side}", 0.008, (AX - 0.03, -0.072, 1.70), (0.03, 0, 0), 3, axis='Y', mat=M['steel_bare']))
    group(parts, f"upperarm_{side}", f"upperarm_{side}")

    # --- codo: eje con tope y tornillos de la tapa ---
    parts = []
    el = L.cyl(f"elbow_{side}", 0.06, 0.15, (AX, 0, 1.44), col, axis='X', verts=16)
    L.assign(el, M['steel_dark']); parts.append(el)
    ec = L.box(f"elbow_cap_{side}", (0.085, 0.10, 0.10), (AX, -0.028, 1.44), col, bevel=0.012)
    L.assign(ec, M['steel_paint']); parts.append(ec)
    es = L.box(f"elbow_stop_{side}", (0.075, 0.028, 0.026), (AX, 0.05, 1.50), col, bevel=0.006)
    L.assign(es, M['steel_bare']); parts.append(es)
    parts.append(bolts(f"elbow_bolt_{side}", 0.008, (AX + sx * 0.062, -0.028, 1.41), (0, 0, 0.032), 3, axis='X', mat=M['steel_bare'], flip=(sx < 0)))
    group(parts, f"elbow_{side}", f"upperarm_{side}")

    # --- antebrazo: el derecho carga el emisor y va blindado con placa hundida; el izquierdo, dos placas solapadas ---
    parts = []
    fa = L.cyl(f"forearm_{side}", 0.05, 0.38, (AX, 0, 1.44), col, pivot='bottom', verts=16, bevel=0.006)
    fa.rotation_euler = (math.radians(180), 0, 0)
    L.assign(fa, M['steel_paint']); parts.append(fa)
    if side == 'R':
        parts.append(recess_at(f"fa_plate_{side}", (0.085, 0.025, 0.14), (AX, -0.058, 1.15), depth=0.012, mat=M['steel_paint'], border=0.011))
        parts.append(bolts(f"fa_bolt_a_{side}", 0.0075, (AX - 0.036, -0.068, 1.10), (0, 0, 0.10), 2, axis='Y', mat=M['steel_bare']))
        parts.append(bolts(f"fa_bolt_b_{side}", 0.0075, (AX + 0.036, -0.068, 1.10), (0, 0, 0.10), 2, axis='Y', mat=M['steel_bare']))
    else:
        f1 = L.box(f"fa_pl_up_{side}", (0.085, 0.025, 0.16), (AX, -0.054, 1.31), col, bevel=0.007)
        L.assign(f1, M['steel_paint']); parts.append(f1)
        f2 = L.box(f"fa_pl_lo_{side}", (0.078, 0.022, 0.13), (AX, -0.048, 1.15), col, bevel=0.007)
        L.assign(f2, M['steel_paint']); parts.append(f2)
        parts.append(bolts(f"fa_bolt_{side}", 0.0075, (AX - 0.03, -0.062, 1.25), (0.03, 0, 0), 3, axis='Y', mat=M['steel_bare']))
    cnd = L.tube(f"fa_conduit_{side}", [(AX + sx * 0.052, 0.035, 1.40), (AX + sx * 0.056, 0.042, 1.26), (AX + sx * 0.052, 0.038, 1.12)], 0.011, col, verts=8)
    L.assign(cnd, M['polymer_dark']); parts.append(cnd)
    group(parts, f"forearm_{side}", f"forearm_{side}")

    # --- mano: bloque de nudillos y almohadilla de goma en la palma (agarra y aparta, 36.5) ---
    parts = []
    hd = L.box(f"hand_{side}", (0.095, 0.055, 0.12), (AX, 0, 1.06), col, pivot='top', bevel=0.010)
    L.assign(hd, M['polymer_dark']); parts.append(hd)
    kb = L.box(f"knuckle_bar_{side}", (0.10, 0.045, 0.028), (AX, -0.004, 0.952), col, bevel=0.008)
    L.assign(kb, M['steel_dark']); parts.append(kb)
    pd = L.box(f"palm_pad_{side}", (0.07, 0.014, 0.075), (AX, -0.032, 1.00), col, bevel=0.006)
    L.assign(pd, M['rubber']); parts.append(pd)
    group(parts, f"hand_{side}", f"hand_{side}")

    # --- dedos: dos falanges y nudillo por dedo, más pulgar opuesto ---
    fg = []
    for i in range(4):
        fx = AX + (i - 1.5) * 0.024
        kn = L.sphere(f"fk_{side}{i}", 0.014, (fx, -0.010, 0.943), col, segs=8, rings=5)
        L.assign(kn, M['steel_dark']); fg.append(kn)
        p1 = L.cyl(f"f_{side}{i}", 0.011, 0.058, (fx, -0.010, 0.940), col, pivot='bottom', verts=8)
        p1.rotation_euler = (math.radians(180), 0, 0); L.assign(p1, M['steel_bare']); fg.append(p1)
        p2 = L.cyl(f"f2_{side}{i}", 0.0092, 0.05, (fx, -0.013, 0.882), col, pivot='bottom', verts=8)
        p2.rotation_euler = (math.radians(172), 0, 0); L.assign(p2, M['steel_bare']); fg.append(p2)
    tk = L.sphere(f"tk_{side}", 0.015, (AX + sx * 0.048, -0.018, 0.985), col, segs=8, rings=5)
    L.assign(tk, M['steel_dark']); fg.append(tk)
    t1 = L.cyl(f"th_{side}", 0.012, 0.05, (AX + sx * 0.048, -0.018, 0.985), col, pivot='bottom', verts=8)
    t1.rotation_euler = (math.radians(150), 0, math.radians(-18 * sx)); L.assign(t1, M['steel_bare']); fg.append(t1)
    t2 = L.cyl(f"th2_{side}", 0.010, 0.042, (AX + sx * 0.054, -0.040, 0.948), col, pivot='bottom', verts=8)
    t2.rotation_euler = (math.radians(160), 0, 0); L.assign(t2, M['steel_bare']); fg.append(t2)
    group(fg, f"fingers_{side}", f"hand_{side}")

# ================================ EMISOR DE RAYO ================================
# 36.2: aislantes cerámicos, núcleo, anillos y cables. Añadido con causa: disipador (el rayo calienta),
# condensadores (hay que acumular carga), bobina de cobre y carcasa partida atornillada sobre el antebrazo.
parts = []
eb = L.cyl("emitter_base", 0.075, 0.20, (0.40, -0.09, 1.28), col, axis='Y', verts=18, bevel=0.006)
L.assign(eb, M['steel_dark']); parts.append(eb)
for i, zz in enumerate((0.056, -0.056)):
    hs = L.box(f"emitter_shell{i}", (0.17, 0.19, 0.035), (0.40, -0.09, 1.28 + zz), col)
    L.assign(hs, M['steel_paint']); L.chamfer(hs, 0.003, 2, 45); parts.append(hs)
parts.append(bolts("emitter_bolt_a", 0.008, (0.40 + 0.086, -0.16, 1.312), (0, 0.06, 0), 3, axis='X', mat=M['steel_bare']))
parts.append(bolts("emitter_bolt_b", 0.008, (0.40 - 0.086, -0.16, 1.312), (0, 0.06, 0), 3, axis='X', mat=M['steel_bare'], flip=True))
br1 = L.box("emitter_bracket", (0.12, 0.05, 0.11), (0.40, 0.005, 1.28), col, bevel=0.008)
L.assign(br1, M['steel_bare']); parts.append(br1)
group(parts, 'emitter_base', 'forearm_R')

# aislantes cerámicos + bobina: lo que separa el núcleo del chasis
parts = []
for i in range(3):
    rg = L.torus(f"emitter_ring{i}", 0.085, 0.013, (0.40, -0.16 - i * 0.05, 1.28), col, axis='Y', segs=14, rings=6)
    L.assign(rg, M['ceramic']); parts.append(rg)
coil = L.torus("emitter_coil", 0.062, 0.010, (0.40, -0.125, 1.28), col, axis='Y', segs=18, rings=6)
L.assign(coil, M['copper']); parts.append(coil)
group(parts, 'emitter_rings', 'forearm_R')

# núcleo y boca: la señal luminosa nace aquí al cargar (13)
parts = []
cr = L.cyl("emitter_core", 0.03, 0.22, (0.40, -0.20, 1.28), col, axis='Y', verts=14)
L.assign(cr, M['emitter']); parts.append(cr)
for i in range(3):
    a = math.radians(90 + i * 120)
    # las tres mordazas miran radialmente a la boca: giro sobre el eje del cañón (Y)
    pt = L.box(f"emitter_petal{i}", (0.022, 0.05, 0.045), (0.40 + math.cos(a) * 0.045, -0.282, 1.28 + math.sin(a) * 0.045), col,
               rot=(0, -a, 0), bevel=0.005)
    L.assign(pt, M['heat']); parts.append(pt)
group(parts, 'emitter_core', 'forearm_R')

# disipador y condensadores: el calor y la carga tienen dónde ir
parts = []
parts.append(ribs_at("emitter_fins", 0.13, (0.10, 0.014, 0.05), (0.40, -0.105, 1.358), count=4, axis='Y', mat=M['heat']))
for i, cx in enumerate((0.362, 0.438)):
    cp = L.cyl(f"emitter_cap{i}", 0.022, 0.085, (cx, -0.03, 1.352), col, axis='Y', verts=12)
    L.assign(cp, M['steel_bare']); parts.append(cp)
    ct = L.cyl(f"emitter_captop{i}", 0.024, 0.012, (cx, -0.075, 1.352), col, axis='Y', verts=12)
    L.assign(ct, M['copper']); parts.append(ct)
group(parts, 'emitter_heat', 'forearm_R')

# cable de alimentación: sale del emisor y muere en el codo. No cruza dos huesos (36.4).
parts = []
ec = L.tube("emitter_cable", [(0.42, 0.018, 1.322), (0.452, 0.055, 1.36), (0.448, 0.075, 1.40), (0.425, 0.062, 1.432)], 0.010, col, verts=8)
L.assign(ec, M['rubber']); parts.append(ec)
cl = L.box("emitter_clamp", (0.04, 0.022, 0.02), (0.449, 0.070, 1.385), col, bevel=0.004)
L.assign(cl, M['steel_bare']); parts.append(cl)
group(parts, 'emitter_cable', 'forearm_R')

# ================================ CUELLO Y CABEZA ================================
parts = []
nk = L.cyl("neck", 0.06, 0.10, (0, 0.02, 1.86), col, pivot='bottom', verts=16)
L.assign(nk, M['rubber']); parts.append(nk)
for i, zz in enumerate((1.885, 1.925)):
    nb = L.torus(f"neck_bel{i}", 0.062, 0.013, (0, 0.02, zz), col, axis='Z', segs=16, rings=6)
    L.assign(nb, M['rubber']); parts.append(nb)
srv = L.box("neck_servo", (0.07, 0.06, 0.05), (0, 0.055, 1.90), col, bevel=0.008)
L.assign(srv, M['steel_dark']); parts.append(srv)
group(parts, 'neck', 'neck')

# placa facial lisa; cuencas estrechas y profundas abiertas con booleano y luego achaflanadas para que el borde
# tenga espesor (36.2). Una línea de unión, nunca una boca legible.
head = L.box("head", (0.2, 0.24, 0.26), (0, 0.0, 1.96), col, pivot='bottom', bevel=0.05, segs=3)
L.assign(head, M['polymer_ivory'])
for side, sx in (("L", -1), ("R", 1)):
    cut = L.box(f"cut_{side}", (0.03, 0.08, 0.05), (sx * 0.05, -0.11, 2.11), col)
    m = head.modifiers.new(f"Socket_{side}", 'BOOLEAN'); m.operation = 'DIFFERENCE'; m.object = cut
    inner = L.box(f"eye_inner_{side}", (0.026, 0.02, 0.045), (sx * 0.05, -0.085, 2.11), col, bevel=0.004)
    L.assign(inner, M['polymer_dark'])
    add(f"eye_inner_{side}", inner, 'head')
L.apply_all(head)
for side in ("L", "R"): bpy.data.objects.remove(bpy.data.objects[f"cut_{side}"])
L.chamfer(head, 0.0018, 2, 55)
add('head', head, 'head')

seam = L.box("face_seam", (0.16, 0.006, 0.006), (0, -0.121, 2.0), col)
add('face_seam', seam, 'head', M['steel_dark'])

# placas del cráneo atornilladas, rejilla de evacuación trasera y pod de sensor: todo dentro de 2.22 m
parts = []
for i, sx in enumerate((-1, 1)):
    sp2 = L.box(f"skull_plate{i}", (0.022, 0.16, 0.14), (sx * 0.100, 0.02, 2.09), col, bevel=0.006)
    L.assign(sp2, M['polymer_ivory']); parts.append(sp2)
parts.append(bolts("skull_bolt_l", 0.007, (-0.106, -0.03, 2.05), (0, 0.07, 0), 2, axis='X', mat=M['steel_bare'], flip=True))
parts.append(bolts("skull_bolt_r", 0.007, (0.106, -0.03, 2.05), (0, 0.07, 0), 2, axis='X', mat=M['steel_bare']))
brow = L.box("brow_plate", (0.17, 0.02, 0.035), (0, -0.118, 2.155), col, bevel=0.005)
L.assign(brow, M['polymer_ivory']); parts.append(brow)
parts.append(L.vent("head_vent", (0.12, 0.028, 0.07), (0, 0.122, 2.06), col, slats=2, rot=R180, mat_frame=M['steel_dark'], mat_slat=M['steel_bare']))
pod = L.cyl("sensor_pod", 0.022, 0.03, (0, -0.118, 2.045), col, axis='Y', verts=12)
L.assign(pod, M['steel_dark']); parts.append(pod)
pl2 = L.bolt("sensor_bolt", 0.009, (0, -0.132, 2.045), col, axis='Y', kind='round')
L.assign(pl2, M['glass']); parts.append(pl2)
group(parts, 'head_det', 'head')

# ================================ ACABADO ================================
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
# binding se construye en el mismo punto donde nace cada pieza (add/group), con los mismos huesos de siempre.
binding = BIND
missing = [b for b in binding if b not in arm.data.bones]
if missing: raise RuntimeError("huesos inexistentes en el binding: %s" % missing)
for bone, names in binding.items():
    for n in names: L.bind_rigid(P[n], arm, bone)

Z = (0, 0, 0)
L.push_nla(arm, L.walk_cycle(arm, "Custodio_Walk", **L.WALK_PRESETS[ASSET]))
# aviso de rayo 1.0 s (60.3): brazo levantado, chispas breves, sin deslizar
L.push_nla(arm, L.action(arm, "Custodio_Anticipation", 30, loop=False, poses={1: {"upperarm_R": ((0, 0, 0), Z), "forearm_R": ((0, 0, 0), Z), "spine": ((0, 0, 0), Z)}, 10: {"upperarm_R": ((-60, 0, -15), Z), "forearm_R": ((-35, 0, 0), Z), "spine": ((-4, 0, -6), Z)}, 30: {"upperarm_R": ((-90, 0, -10), Z), "forearm_R": ((-10, 0, 0), Z), "spine": ((-6, 0, -8), Z), "head": ((4, 0, 0), Z)}}))
L.push_nla(arm, L.action(arm, "Custodio_Bolt", 48, loop=False, poses={1: {"upperarm_R": ((-90, 0, -10), Z), "forearm_R": ((-10, 0, 0), Z), "spine": ((-6, 0, -8), Z)}, 4: {"upperarm_R": ((-80, 0, -6), Z), "spine": ((3, 0, -4), Z)}, 48: {"upperarm_R": ((0, 0, 0), Z), "forearm_R": ((0, 0, 0), Z), "spine": ((0, 0, 0), Z), "head": ((0, 0, 0), Z)}}))
L.push_nla(arm, L.action(arm, "Custodio_Stagger", 9, loop=False, poses={1: {"spine": ((0, 0, 0), Z)}, 4: {"spine": ((12, 0, 6), Z), "head": ((10, 0, 0), Z)}, 9: {"spine": ((0, 0, 0), Z), "head": ((0, 0, 0), Z)}}))
L.push_nla(arm, L.action(arm, "Custodio_Death", 45, loop=False, poses={1: {"root": ((0, 0, 0), Z)}, 18: {"thigh_L": ((35, 0, 0), Z), "shin_L": ((60, 0, 0), Z), "spine": ((20, 0, 8), Z), "root": ((0, 0, 0), (0, 0, -0.3))}, 45: {"root": ((85, 0, 10), (0, -0.4, -1.0)), "spine": ((5, 0, 15), Z), "head": ((-15, 0, 20), Z), "upperarm_R": ((30, 0, 40), Z)}}))

objs = list(P.values())
tris = 0
for o in objs:
    o.data.calc_loop_triangles(); tris += len(o.data.loop_triangles)
blend = L.save_blend(ASSET)
print("built", len(objs), "piezas", tris, "tris")
