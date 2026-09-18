# BOT-03 EL ARCHIVISTA (15 / 36.3 / 61): jefe final, 3.10 m de "casi humano estirado".
# Como jefe llena la pantalla durante todo el combate final, así que es el asset con mayor densidad de detalle
# del proyecto. Lo que cambia respecto al blockout anterior:
#   · Compartimentos de registro REALES (36.3): seis bahías abiertas con booleano —grosor y fondo, no agujeros—,
#     cada una con su marco, su cajón con tirador, cierre, chapa de código y las guías sobre las que corre.
#     Uno está sacado: se le ve el cuerpo y la corredera. Los "códigos de humanos archivados" son chapa, no textura.
#   · Blindaje segmentado: bandas de pecho que se solapan con junta, flancos con nervios, rejillas donde respira
#     y un parche de reparación con pintura distinta y cordón de soldadura (33.2 / 41.3: el detalle tiene causa).
#   · Servos visibles en cada articulación: eje, tope físico, rótula, anillo de servo y tornillería de la tapa (36.4).
#   · Manos de pinza articuladas de tres dedos con falanges y nudillos, y el emisor del pulso montado en la palma
#     con aislantes cerámicos y mordazas (el pulso de fase III nace de un sitio concreto).
#   · Cara porcelánica lisa con cuencas estrechas, profundas y CON REBORDE; una sola línea de unión, nunca una boca.
#   · Nuca demasiado larga con vértebras, columna de goma y haces de cable organizados (no spaghetti).
#   · Chaflán en toda pieza grande: ninguna arista viva (33.2), que es lo que hornea bien en el atlas.
# Presupuesto 43 (jefe, LOD0): 35–60k tris. Objetivo de este build ~42–48k.
# Altura 3.10 m intacta (colliders y escala del juego), rig, nombres de huesos, binding y los 7 clips se conservan.
import bpy, math, importlib, sys
sys.path.insert(0, r"C:/Users/HP/Documents/GitHub/proyectos-unity/SourceArt/Scripts")
import esn_lib as L; importlib.reload(L)

ASSET = "BOT-03_Archivista"
L.reset_scene()
col = L.collection(ASSET)
M = L.std_mats()
# Materiales propios: reparación, calor y registro son causas visibles, no grunge decorativo (41.3).
M['weld'] = L.material("M_Weld", (0.40, 0.38, 0.36), 0.62, 1.0, wear=0.35, wear_color=(0.30, 0.22, 0.16), bump=0.45, scale=70)
M['paint_new'] = L.material("M_PaintRepair", (0.30, 0.32, 0.38), 0.48, 0.0, wear=0.10, wear_color=(0.46, 0.46, 0.43), bump=0.12)
M['heat'] = L.material("M_HeatSteel", (0.27, 0.25, 0.29), 0.36, 1.0, wear=0.42, wear_color=(0.34, 0.26, 0.40), bump=0.12, scale=12)
# 36.3: la carcasa facial está casi intacta sobre un cuerpo remendado. Esa limpieza relativa es la amenaza.
M['porcelain'] = L.material("M_Porcelain", (0.88, 0.86, 0.82), 0.18, 0.0, wear=0.06, wear_color=(0.60, 0.56, 0.50), bump=0.03, edge_wear=0.12)
# chapas de código de los compartimentos: papel/esmalte viejo, borrado por el roce de abrir el cajón
M['label'] = L.material("M_RecordTag", (0.74, 0.70, 0.58), 0.72, 0.0, wear=0.45, wear_color=(0.42, 0.36, 0.28), bump=0.20, scale=45)
M['pulse'] = L.material("M_PulseEmitter", (0.35, 0.72, 1.0), 0.25, 0.0, emission=((0.35, 0.72, 1.0), 3.0))

P = {}
BIND = {}


def add(key, obj, bone, mat=None):
    """Registra una pieza: colección, material y hueso quedan resueltos donde se crea la pieza."""
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
# Zancada larga y pesada (15): el jefe recorre la arena. Goma donde toca el suelo, acero donde recibe el peso,
# tope físico en rodilla y tobillo para que las poses de Walk/Pulse tengan un límite que se ve (36.4).
for side, sx in (("L", -1), ("R", 1)):
    X = sx * 0.26

    # --- pie: suela de goma con tacos, empeine y puntera atornillados ---
    parts = []
    sole = L.box(f"foot_{side}", (0.24, 0.42, 0.05), (X, 0.04, 0.0), col, pivot='bottom', bevel=0.012)
    L.assign(sole, M['rubber']); parts.append(sole)
    inst = L.box(f"foot_inst_{side}", (0.20, 0.18, 0.045), (X, 0.09, 0.05), col, pivot='bottom', bevel=0.010)
    L.assign(inst, M['steel_paint']); parts.append(inst)
    toe = L.box(f"foot_toe_{side}", (0.21, 0.12, 0.04), (X, -0.11, 0.05), col, pivot='bottom', bevel=0.008)
    L.assign(toe, M['steel_bare']); parts.append(toe)
    parts.append(ribs_at(f"foot_tread_{side}", 0.30, (0.20, 0.035, 0.015), (X, 0.02, 0.008), count=2, axis='Y', mat=M['rubber']))
    parts.append(bolts(f"foot_bolt_{side}", 0.009, (X - 0.066, 0.09, 0.094), (0.044, 0, 0), 4, axis='Z', mat=M['steel_bare']))
    group(parts, f"foot_{side}", f"foot_{side}")

    # --- tobillo: eje real, pasador, fuelles de goma y horquilla que transmite el peso ---
    parts = []
    ank = L.cyl(f"ankle_{side}", 0.07, 0.17, (X, 0.0, 0.085), col, axis='X', verts=16)
    L.assign(ank, M['steel_bare']); parts.append(ank)
    for i, zz in enumerate((0.125, 0.165)):
        bel = L.torus(f"ankle_bel{i}_{side}", 0.068, 0.016, (X, 0.0, zz), col, axis='Z', segs=14, rings=6)
        L.assign(bel, M['rubber']); parts.append(bel)
    for i, gx in enumerate((-0.075, 0.075)):
        yk = L.box(f"ankle_yoke{i}_{side}", (0.035, 0.13, 0.15), (X + gx, 0.0, 0.13), col, bevel=0.008)
        L.assign(yk, M['steel_dark']); parts.append(yk)
    pin = L.bolt(f"ankle_pin_{side}", 0.016, (X + sx * 0.092, 0.0, 0.085), col, axis='X', kind='hex')
    if sx < 0: pin.rotation_euler = (0, math.radians(180), 0)
    L.assign(pin, M['steel_dark']); parts.append(pin)
    group(parts, f"ankle_{side}", f"shin_{side}")

    # --- espinilla: núcleo de polímero con placa blindada hundida y junta soldada lateral ---
    shin = L.box(f"shin_{side}", (0.17, 0.19, 0.60), (X, 0.0, 0.10), col, pivot='bottom')
    L.assign(shin, M['polymer_dark']); L.chamfer(shin, 0.004, 2, 45)
    add(f"shin_{side}", shin, f"shin_{side}")

    parts = []
    parts.append(recess_at(f"shin_plate_{side}", (0.13, 0.030, 0.34), (X, -0.084, 0.34), depth=0.015, mat=M['steel_paint'], border=0.013))
    parts.append(bolts(f"shin_bolt_a_{side}", 0.008, (X - 0.052, -0.099, 0.21), (0, 0, 0.11), 3, axis='Y', mat=M['steel_bare']))
    parts.append(bolts(f"shin_bolt_b_{side}", 0.008, (X + 0.052, -0.099, 0.21), (0, 0, 0.11), 3, axis='Y', mat=M['steel_bare']))
    parts.append(L.panel_seam(f"shin_seam_{side}", 0.56, (X + sx * 0.088, 0.0, 0.38), col, axis='Z', width=0.007, depth=0.009, mat=M['weld']))
    guard = L.box(f"shin_guard_{side}", (0.15, 0.11, 0.12), (X, -0.045, 0.62), col, bevel=0.014)
    L.assign(guard, M['steel_dark']); parts.append(guard)
    parts.append(ribs_at(f"shin_rib_{side}", 0.26, (0.030, 0.11, 0.030), (X, 0.092, 0.40), count=2, axis='Z', mat=M['steel_bare']))
    group(parts, f"shin_det_{side}", f"shin_{side}")

    # --- pistón de la espinilla: vástago, camisa, tapa, horquilla y latiguillo. Carrera con tope real ---
    parts = []
    rod = L.cyl(f"piston_{side}", 0.020, 0.32, (X + sx * 0.088, 0.075, 0.14), col, pivot='bottom', verts=12)
    L.assign(rod, M['steel_bare']); parts.append(rod)
    slv = L.cyl(f"piston_slv_{side}", 0.031, 0.18, (X + sx * 0.088, 0.075, 0.30), col, pivot='bottom', verts=12, bevel=0.006)
    L.assign(slv, M['steel_dark']); parts.append(slv)
    cap = L.cyl(f"piston_cap_{side}", 0.035, 0.024, (X + sx * 0.088, 0.075, 0.485), col, verts=12)
    L.assign(cap, M['steel_dark']); parts.append(cap)
    clv = L.box(f"piston_clv_{side}", (0.036, 0.055, 0.055), (X + sx * 0.088, 0.075, 0.14), col, bevel=0.006)
    L.assign(clv, M['steel_bare']); parts.append(clv)
    hose = L.tube(f"piston_hose_{side}", [(X + sx * 0.088, 0.104, 0.50), (X + sx * 0.072, 0.126, 0.58),
                                          (X + sx * 0.040, 0.118, 0.66), (X, 0.098, 0.72)], 0.009, col, verts=8)
    L.assign(hose, M['rubber']); parts.append(hose)
    group(parts, f"piston_{side}", f"thigh_{side}")

    # --- rodilla: eje, rótula, dos topes que explican el bloqueo, servo y anillo de holgura ---
    parts = []
    kn = L.cyl(f"knee_{side}", 0.10, 0.23, (X, 0.0, 0.72), col, axis='X', verts=16)
    L.assign(kn, M['steel_dark']); parts.append(kn)
    kc = L.box(f"knee_cap_{side}", (0.13, 0.14, 0.16), (X, -0.045, 0.72), col, bevel=0.018)
    L.assign(kc, M['steel_paint']); parts.append(kc)
    for i, (yy, zz) in enumerate(((0.070, 0.81), (-0.030, 0.62))):
        st = L.box(f"knee_stop{i}_{side}", (0.11, 0.035, 0.032), (X, yy, zz), col, bevel=0.007)
        L.assign(st, M['steel_bare']); parts.append(st)
    srv = L.box(f"knee_servo_{side}", (0.06, 0.09, 0.09), (X + sx * 0.118, 0.010, 0.72), col, bevel=0.010)
    L.assign(srv, M['steel_dark']); parts.append(srv)
    rim = L.torus(f"knee_rim_{side}", 0.105, 0.016, (X, 0.0, 0.72), col, axis='X', segs=14, rings=6)
    L.assign(rim, M['steel_bare']); parts.append(rim)
    parts.append(bolts(f"knee_bolt_{side}", 0.009, (X + sx * 0.108, -0.045, 0.665), (0, 0, 0.055), 3, axis='X', mat=M['steel_bare'], flip=(sx < 0)))
    group(parts, f"knee_{side}", f"thigh_{side}")

    # --- muslo: núcleo + dos placas que SE SOLAPAN con junta soldada, y el actuador de cadera ---
    th = L.box(f"thigh_{side}", (0.20, 0.23, 0.68), (X, 0.0, 0.72), col, pivot='bottom')
    L.assign(th, M['polymer_dark']); L.chamfer(th, 0.005, 2, 45)
    add(f"thigh_{side}", th, f"thigh_{side}")

    parts = []
    up = L.box(f"thigh_pl_up_{side}", (0.19, 0.040, 0.26), (X, -0.101, 1.22), col, bevel=0.009)
    L.assign(up, M['steel_paint']); parts.append(up)
    lo = L.box(f"thigh_pl_lo_{side}", (0.18, 0.036, 0.24), (X, -0.094, 0.94), col, bevel=0.009)
    L.assign(lo, M['steel_paint']); parts.append(lo)
    parts.append(L.panel_seam(f"thigh_seam_{side}", 0.18, (X, -0.118, 1.085), col, axis='X', width=0.010, depth=0.011, mat=M['weld']))
    parts.append(bolts(f"thigh_bolt_a_{side}", 0.0085, (X - 0.062, -0.124, 1.30), (0.062, 0, 0), 3, axis='Y', mat=M['steel_bare']))
    parts.append(bolts(f"thigh_bolt_b_{side}", 0.0085, (X - 0.058, -0.115, 0.86), (0.058, 0, 0), 3, axis='Y', mat=M['steel_bare']))
    shroud = L.box(f"hip_shroud_{side}", (0.21, 0.24, 0.14), (X, 0.0, 1.35), col, bevel=0.020)
    L.assign(shroud, M['steel_dark']); parts.append(shroud)
    group(parts, f"thigh_det_{side}", f"thigh_{side}")

    # actuador de cadera: la pierna de 3 m necesita algo que la levante, y se ve
    parts = []
    arod = L.cyl(f"hip_rod_{side}", 0.022, 0.30, (X + sx * 0.108, 0.088, 0.80), col, pivot='bottom', verts=12)
    L.assign(arod, M['steel_bare']); parts.append(arod)
    aslv = L.cyl(f"hip_slv_{side}", 0.033, 0.20, (X + sx * 0.108, 0.088, 1.06), col, pivot='bottom', verts=12, bevel=0.006)
    L.assign(aslv, M['steel_dark']); parts.append(aslv)
    acl = L.box(f"hip_clamp_{side}", (0.050, 0.050, 0.030), (X + sx * 0.108, 0.088, 1.28), col, bevel=0.006)
    L.assign(acl, M['steel_bare']); parts.append(acl)
    group(parts, f"thigh_act_{side}", f"thigh_{side}")

    # Asimetría con causa (36.2): la pierna que planta primero en la carga lleva nervios de refuerzo;
    # la contraria arrastra un parche con pintura nueva y cordón de soldadura.
    if side == "R":
        parts = [ribs_at(f"thigh_rib_{side}", 0.24, (0.028, 0.12, 0.028), (X + sx * 0.113, 0.010, 1.05), count=2, axis='Z', mat=M['steel_bare'])]
        gus = L.box(f"thigh_gusset_{side}", (0.030, 0.14, 0.13), (X + sx * 0.112, 0.010, 0.88), col, bevel=0.007)
        L.assign(gus, M['steel_bare']); parts.append(gus)
        parts.append(bolts(f"thigh_gbolt_{side}", 0.008, (X + sx * 0.128, -0.045, 0.88), (0, 0.045, 0), 2, axis='X', mat=M['steel_bare'], flip=(sx < 0)))
        group(parts, f"thigh_mark_{side}", f"thigh_{side}")
    else:
        parts = [ribs_at(f"thigh_rib_{side}", 0.24, (0.028, 0.12, 0.028), (X + sx * 0.113, 0.010, 1.05), count=2, axis='Z', mat=M['steel_bare'])]
        pat = L.box(f"thigh_patch_{side}", (0.024, 0.14, 0.19), (X + sx * 0.112, 0.010, 0.86), col, bevel=0.006)
        L.assign(pat, M['paint_new']); parts.append(pat)
        parts.append(bolts(f"thigh_pbolt_{side}", 0.008, (X + sx * 0.126, -0.052, 0.79), (0, 0.052, 0), 3, axis='X', mat=M['steel_bare'], flip=True))
        wl = L.tube(f"thigh_weld_{side}", [(X + sx * 0.112, -0.068, 0.956), (X + sx * 0.112, 0.010, 0.962), (X + sx * 0.112, 0.078, 0.956)], 0.005, col, verts=6)
        L.assign(wl, M['weld']); parts.append(wl)
        group(parts, f"thigh_mark_{side}", f"thigh_{side}")

# ================================ PELVIS Y CINTURA ================================
# Donde el peso del torso de archivo baja a las piernas. La cintura deja un hueco con fuelle visible:
# el "casi humano estirado" necesita un punto de flexión legible entre pelvis y tórax.
pelvis = L.box("pelvis", (0.64, 0.36, 0.20), (0, 0, 1.42), col, pivot='bottom')
L.assign(pelvis, M['steel_dark']); L.chamfer(pelvis, 0.006, 2, 45)
add('pelvis', pelvis, 'pelvis')

parts = []
parts.append(recess_at("pelvis_plate", (0.34, 0.038, 0.11), (0, -0.192, 1.53), depth=0.018, mat=M['steel_paint'], border=0.015))
parts.append(bolts("pelvis_bolt_a", 0.009, (-0.150, -0.203, 1.585), (0.10, 0, 0), 4, axis='Y', mat=M['steel_bare']))
parts.append(bolts("pelvis_bolt_b", 0.009, (-0.150, -0.203, 1.475), (0.10, 0, 0), 4, axis='Y', mat=M['steel_bare']))
for sxx in (-1, 1):
    sd = 'L' if sxx < 0 else 'R'
    gus = L.box(f"hip_gusset_{sd}", (0.070, 0.19, 0.16), (sxx * 0.25, 0.0, 1.48), col, bevel=0.012)
    L.assign(gus, M['steel_bare']); parts.append(gus)
    yok = L.cyl(f"hip_yoke_{sd}", 0.065, 0.10, (sxx * 0.26, 0.0, 1.44), col, axis='X', verts=14)
    L.assign(yok, M['steel_dark']); parts.append(yok)
    parts.append(L.panel_seam(f"pelvis_seam_{sd}", 0.18, (sxx * 0.322, -0.05, 1.53), col, axis='Z', width=0.007, depth=0.008, mat=M['steel_dark']))
parts.append(L.vent("pelvis_vent", (0.24, 0.032, 0.10), (0, 0.163, 1.53), col, slats=3, rot=R180, mat_frame=M['steel_dark'], mat_slat=M['steel_bare']))
group(parts, 'pelvis_det', 'pelvis')

# columna de cintura: fuelle de goma entre pelvis (1.62) y tórax (1.70)
parts = []
sp = L.cyl("spine_col", 0.095, 0.20, (0, 0.02, 1.56), col, pivot='bottom', verts=14)
L.assign(sp, M['rubber']); parts.append(sp)
for i, zz in enumerate((1.635, 1.665, 1.695)):
    rg = L.torus(f"spine_bel{i}", 0.100, 0.018, (0, 0.02, zz), col, axis='Z', segs=14, rings=6)
    L.assign(rg, M['rubber']); parts.append(rg)
srv = L.box("spine_servo", (0.10, 0.08, 0.07), (0, 0.105, 1.66), col, bevel=0.010)
L.assign(srv, M['steel_dark']); parts.append(srv)
group(parts, 'spine_col', 'pelvis')

# ================================ TÓRAX DE ARCHIVO ================================
# El torso es un mueble de registro: seis bahías abiertas en el propio casco con booleano, para que la abertura
# tenga grosor de chapa y fondo (36.3 lo pide por su nombre). El chaflán se aplica DESPUÉS del booleano,
# así el canto de cada bahía queda redondeado y no lee como agujero recortado.
torso = L.box("torso", (0.72, 0.44, 0.70), (0, 0, 1.70), col, pivot='bottom')
L.assign(torso, M['steel_paint'])

BAYS = [(i, j) for i in range(3) for j in range(2)]
DRAWER_OPEN = (1, 0)   # una bahía con el cajón sacado: se ve el cuerpo del cajón y la corredera


def bay_center(i, j):
    return (j - 0.5) * 0.31, 1.82 + i * 0.22


cuts = []
for i, j in BAYS:
    cx, cz = bay_center(i, j)
    c = L.box(f"dcut_{i}{j}", (0.235, 0.15, 0.155), (cx, -0.165, cz), col)
    m = torso.modifiers.new(f"Bay_{i}{j}", 'BOOLEAN'); m.operation = 'DIFFERENCE'; m.object = c
    cuts.append(c)
L.apply_all(torso)
for c in cuts: bpy.data.objects.remove(c)
L.chamfer(torso, 0.004, 2, 45)
add('torso', torso, 'spine')

# --- guías: la corredera sobre la que cada cajón entra y sale. Sin ellas el cajón es una tapa pintada ---
rails = []
for i, j in BAYS:
    cx, cz = bay_center(i, j)
    for k, gx in enumerate((cx - 0.104, cx + 0.104)):
        g = L.box(f"bay_rail{i}{j}_{k}", (0.013, 0.125, 0.016), (gx, -0.152, cz + 0.055), col, bevel=0.004)
        L.assign(g, M['steel_bare']); rails.append(g)
group(rails, 'bay_rails', 'spine')

# --- cajones: marco con reborde, frente hundido, tirador con su escuadra, cierre y chapa de código ---
drawers = []
for i, j in BAYS:
    cx, cz = bay_center(i, j)
    openq = (i, j) == DRAWER_OPEN
    # el cajón entreabierto se saca solo 5.5 cm: suficiente para leer la corredera y el cuerpo del cajón
    # sin engordar la caja envolvente del asset, que el juego usa para escala y colliders
    dy = -0.055 if openq else 0.0
    drawers.append(recess_at(f"drawer_face_{i}{j}", (0.225, 0.042, 0.145), (cx, -0.190 + dy, cz),
                             depth=0.024, mat=M['steel_paint'], border=0.014))
    br = L.box(f"drawer_br_{i}{j}", (0.105, 0.020, 0.018), (cx, -0.214 + dy, cz - 0.042), col, bevel=0.004)
    L.assign(br, M['steel_dark']); drawers.append(br)
    pull = L.box(f"drawer_pull_{i}{j}", (0.085, 0.032, 0.024), (cx, -0.232 + dy, cz - 0.042), col, bevel=0.006)
    L.assign(pull, M['steel_bare']); drawers.append(pull)
    lat = L.box(f"drawer_latch_{i}{j}", (0.030, 0.028, 0.048), (cx + 0.082, -0.218 + dy, cz + 0.032), col, bevel=0.005)
    L.assign(lat, M['steel_dark']); drawers.append(lat)
    tag = L.box(f"drawer_tag_{i}{j}", (0.072, 0.005, 0.026), (cx - 0.052, -0.213 + dy, cz + 0.042), col)
    L.assign(tag, M['label']); drawers.append(tag)
    drawers.append(bolts(f"drawer_tagbolt_{i}{j}", 0.005, (cx - 0.090, -0.216 + dy, cz + 0.042), (0.076, 0, 0), 2, axis='Y', mat=M['steel_bare']))
    if openq:
        # cuerpo del cajón: dos costados, fondo y trasera. Es un cajón, no una placa desplazada.
        for k, (bs, bl) in enumerate((((0.014, 0.120, 0.132), (cx - 0.104, -0.185, cz)),
                                      ((0.014, 0.120, 0.132), (cx + 0.104, -0.185, cz)),
                                      ((0.222, 0.120, 0.014), (cx, -0.185, cz - 0.066)),
                                      ((0.222, 0.012, 0.132), (cx, -0.122, cz)))):
            b = L.box(f"drawer_body{i}{j}_{k}", bs, bl, col, bevel=0.004)
            L.assign(b, M['polymer_dark']); drawers.append(b)
group(drawers, 'drawers', 'spine')

# --- blindaje segmentado del frente: bandas que se solapan, junta entre ellas y montante central ---
parts = []
for i, (bz, bh) in enumerate(((1.955, 0.045), (2.175, 0.045), (2.365, 0.060))):
    bd = L.box(f"chest_band{i}", (0.60, 0.036, bh), (0, -0.230, bz), col, bevel=0.009)
    L.assign(bd, M['steel_paint']); parts.append(bd)
post = L.box("chest_post", (0.060, 0.036, 0.62), (0, -0.230, 2.03), col, bevel=0.008)
L.assign(post, M['steel_bare']); parts.append(post)
for i, sz in enumerate((1.9325, 2.1525)):
    parts.append(L.panel_seam(f"chest_seam{i}", 0.60, (0, -0.250, sz), col, axis='X', width=0.009, depth=0.010, mat=M['weld']))
plate_n = L.box("unit_plate", (0.11, 0.012, 0.050), (0.235, -0.254, 2.365), col)
L.assign(plate_n, M['steel_bare']); parts.append(plate_n)
parts.append(bolts("unit_bolt", 0.006, (0.190, -0.262, 2.365), (0.090, 0, 0), 2, axis='Y', mat=M['steel_bare']))
group(parts, 'chest_bands', 'spine')

# --- flancos: placa, nervios de refuerzo donde el brazo largo hace palanca, rejilla y línea de fundición ---
for sd, sxx in (("L", -1), ("R", 1)):
    parts = []
    fl = L.box(f"flank_{sd}", (0.050, 0.36, 0.44), (sxx * 0.362, -0.020, 2.06), col, bevel=0.012)
    L.assign(fl, M['steel_paint']); parts.append(fl)
    parts.append(ribs_at(f"flank_rib_{sd}", 0.22, (0.032, 0.30, 0.032), (sxx * 0.392, 0.0, 2.12), count=2, axis='Z', mat=M['steel_bare']))
    # la rejilla gira 90 grados sobre Z para mirar al flanco; el signo la orienta hacia fuera en cada lado
    parts.append(L.vent(f"flank_vent_{sd}", (0.16, 0.032, 0.14), (sxx * 0.388, 0.060, 1.92), col, slats=3,
                        rot=(0, 0, math.radians(90 * sxx)), mat_frame=M['steel_dark'], mat_slat=M['heat']))
    parts.append(L.panel_seam(f"cast_seam_{sd}", 0.44, (sxx * 0.390, -0.185, 2.06), col, axis='Z', width=0.008, depth=0.009, mat=M['steel_dark']))
    group(parts, f"flank_{sd}", 'spine')

# --- collar y cartelas de hombro: los brazos de 1.3 m cuelgan de aquí, el refuerzo tiene causa ---
parts = []
collar = L.torus("collar", 0.130, 0.026, (0, 0.02, 2.40), col, axis='Z', segs=20, rings=8)
L.assign(collar, M['steel_dark']); parts.append(collar)
group(parts, 'collar', 'spine')

for sd, sxx in (("L", -1), ("R", 1)):
    parts = []
    for i, (bx, bz) in enumerate(((0.28, 2.36), (0.35, 2.31))):
        br = L.box(f"brace_{sd}{i}", (0.10, 0.16, 0.11), (sxx * bx, 0.0, bz), col, rot=(0, math.radians(-16 * sxx), 0), bevel=0.013)
        L.assign(br, M['steel_bare']); parts.append(br)
    parts.append(bolts(f"brace_bolt_{sd}", 0.009, (sxx * 0.32, -0.070, 2.40), (0, 0.070, 0), 3, axis='Z', mat=M['steel_bare']))
    group(parts, f"brace_{sd}", 'spine')

# --- parche de reparación del flanco: 2000 años de mantenimiento autónomo dejan pintura nueva sobre chapa vieja ---
parts = []
pat = L.box("torso_patch", (0.024, 0.16, 0.20), (-0.374, 0.070, 2.20), col, bevel=0.006)
L.assign(pat, M['paint_new']); parts.append(pat)
parts.append(bolts("torso_patch_bolt", 0.008, (-0.388, 0.0, 2.20), (0, 0.070, 0), 3, axis='X', mat=M['steel_bare'], flip=True))
# cordón en L: un recorrido cerrado con dos vueltas de 90 grados haría girar los anillos del tubo sobre sí mismos
pw = L.tube("torso_patch_weld", [(-0.374, -0.012, 2.302), (-0.374, 0.152, 2.302), (-0.374, 0.152, 2.098)], 0.005, col, verts=6)
L.assign(pw, M['weld']); parts.append(pw)
group(parts, 'torso_patch', 'spine')

# --- espalda: panel de mantenimiento hundido y atornillado, con su rejilla de evacuación ---
parts = []
bp = L.box("back_panel", (0.58, 0.060, 0.62), (0, 0.230, 1.74), col, pivot='bottom')
L.assign(bp, M['polymer_dark']); L.chamfer(bp, 0.005, 2, 45); parts.append(bp)
parts.append(recess_at("back_recess", (0.36, 0.040, 0.26), (0, 0.2365, 2.10), depth=0.018, rot=R180, mat=M['steel_paint'], border=0.015))
parts.append(bolts("back_bolt_l", 0.009, (-0.215, 0.2465, 1.98), (0, 0, 0.12), 3, axis='Y', mat=M['steel_bare'], flip=True))
parts.append(bolts("back_bolt_r", 0.009, (0.215, 0.2465, 1.98), (0, 0, 0.12), 3, axis='Y', mat=M['steel_bare'], flip=True))
parts.append(L.vent("back_vent", (0.28, 0.034, 0.12), (0, 0.234, 1.83), col, slats=4, rot=R180, mat_frame=M['steel_dark'], mat_slat=M['heat']))
parts.append(ribs_at("back_rib", 0.26, (0.50, 0.030, 0.030), (0, 0.250, 2.30), count=2, axis='Z', mat=M['steel_bare']))
group(parts, 'back_panel', 'spine')

# --- cableado en HACES, no spaghetti (36.3): tronco principal, dos ramales y abrazaderas que lo fijan.
#     Termina en la base del cuello: un cable no cruza dos huesos (36.4).
parts = []
# los haces suben con avance lateral constante: si el tramo final quedara vertical, los anillos del tubo
# pierden referencia (el marco se calcula contra Z) y el haz aparece retorcido en el bake.
hr = L.tube("cable_harness", [(-0.22, 0.262, 1.80), (-0.16, 0.278, 2.00), (-0.05, 0.292, 2.20), (0.02, 0.284, 2.34), (0.06, 0.276, 2.42)], 0.026, col, verts=10)
L.assign(hr, M['rubber']); parts.append(hr)
for k, pts in enumerate((
        [(0.20, 0.258, 1.84), (0.16, 0.276, 2.02), (0.08, 0.288, 2.20), (0.04, 0.280, 2.36)],
        [(-0.12, 0.254, 1.92), (-0.06, 0.272, 2.10), (0.00, 0.282, 2.26), (0.03, 0.276, 2.38)])):
    br2 = L.tube(f"cable_branch{k}", pts, 0.014, col, verts=8)
    L.assign(br2, M['rubber']); parts.append(br2)
for k, (cy, cz) in enumerate(((0.286, 1.98), (0.298, 2.18), (0.286, 2.34))):
    cl = L.box(f"cable_clamp{k}", (0.11, 0.024, 0.030), (0.0, cy, cz), col, bevel=0.005)
    L.assign(cl, M['steel_bare']); parts.append(cl)
jb = L.box("cable_junction", (0.14, 0.060, 0.10), (-0.20, 0.268, 1.80), col, bevel=0.010)
L.assign(jb, M['polymer_dark']); parts.append(jb)
group(parts, 'cable_harness', 'spine')

# --- luces de fase (36.3): la fase se lee en el cuerpo, no en una transformación ---
parts = []
for i in range(5):
    lx = -0.24 + i * 0.12
    lg = L.box(f"light_{i}", (0.026, 0.012, 0.026), (lx, -0.248, 2.365), col)
    L.assign(lg, M['emitter']); parts.append(lg)
    bz2 = L.torus(f"light_bezel{i}", 0.022, 0.006, (lx, -0.244, 2.365), col, axis='Y', segs=10, rings=4)
    L.assign(bz2, M['steel_dark']); parts.append(bz2)
group(parts, 'phase_lights', 'spine')

# ================================ HOMBROS ================================
# Rótula real con hombrera de dos placas solapadas, reborde y el servo que mueve un brazo demasiado largo.
for sd, sxx in (("L", -1), ("R", 1)):
    parts = []
    # radio 0.145: la rótula es el punto más ancho del bot, y con la hombrera encima mantiene el ancho original
    sh = L.sphere(f"shoulder_{sd}", 0.145, (sxx * 0.45, 0, 2.32), col, segs=20, rings=14, scale=(1.0, 1.1, 0.95))
    L.assign(sh, M['steel_bare']); parts.append(sh)
    pa = L.box(f"pauldron_{sd}0", (0.060, 0.28, 0.14), (sxx * 0.478, 0.0, 2.36), col, rot=(0, math.radians(-12 * sxx), 0), bevel=0.015)
    L.assign(pa, M['steel_paint']); parts.append(pa)
    pb2 = L.box(f"pauldron_{sd}1", (0.055, 0.24, 0.12), (sxx * 0.498, 0.0, 2.24), col, rot=(0, math.radians(-8 * sxx), 0), bevel=0.013)
    L.assign(pb2, M['steel_paint']); parts.append(pb2)
    rim2 = L.torus(f"pauldron_rim_{sd}", 0.135, 0.018, (sxx * 0.45, 0.0, 2.32), col, axis='X', segs=18, rings=6)
    L.assign(rim2, M['steel_dark']); parts.append(rim2)
    srv2 = L.box(f"shoulder_servo_{sd}", (0.070, 0.10, 0.10), (sxx * 0.45, 0.095, 2.32), col, bevel=0.010)
    L.assign(srv2, M['steel_dark']); parts.append(srv2)
    parts.append(bolts(f"pauldron_bolt_{sd}", 0.009, (sxx * 0.506, -0.095, 2.375), (0, 0.095, 0), 3, axis='X', mat=M['steel_bare'], flip=(sxx < 0)))
    group(parts, f"shoulder_{sd}", 'spine')

# ================================ BRAZOS EXCESIVAMENTE LARGOS ================================
# 0.62 m de brazo + 0.66 m de antebrazo con articulaciones plausibles: carenado atornillado, nervios,
# anillo de servo en cada eje y conducto de alimentación que muere dentro de su propio hueso (36.4).
for side, sx in (("L", -1), ("R", 1)):
    AX = sx * 0.45

    parts = []
    up2 = L.cyl(f"upperarm_{side}", 0.082, 0.62, (AX, 0, 2.32), col, pivot='bottom', verts=16, bevel=0.010)
    up2.rotation_euler = (math.radians(180), 0, 0)
    L.assign(up2, M['polymer_dark']); parts.append(up2)
    for i, yy in enumerate((-0.064, 0.060)):
        shr = L.box(f"ua_shroud{i}_{side}", (0.14, 0.035, 0.24), (AX, yy, 2.05), col, bevel=0.009)
        L.assign(shr, M['steel_paint']); parts.append(shr)
    parts.append(bolts(f"ua_bolt_{side}", 0.008, (AX - 0.042, -0.082, 2.12), (0.042, 0, 0), 3, axis='Y', mat=M['steel_bare']))
    parts.append(ribs_at(f"ua_rib_{side}", 0.22, (0.026, 0.10, 0.026), (AX + sx * 0.090, 0.0, 2.05), count=2, axis='Z', mat=M['steel_bare']))
    band = L.torus(f"ua_servo_{side}", 0.095, 0.016, (AX, 0.0, 2.24), col, axis='Z', segs=16, rings=6)
    L.assign(band, M['steel_dark']); parts.append(band)
    cnd = L.tube(f"ua_conduit_{side}", [(AX + sx * 0.078, 0.050, 2.26), (AX + sx * 0.084, 0.058, 2.02), (AX + sx * 0.078, 0.064, 1.78)], 0.012, col, verts=8)
    L.assign(cnd, M['polymer_dark']); parts.append(cnd)
    group(parts, f"upperarm_{side}", f"upperarm_{side}")

    # --- codo: eje, tapa, tope físico y reborde de holgura ---
    parts = []
    el = L.cyl(f"elbow_{side}", 0.090, 0.20, (AX, 0, 1.70), col, axis='X', verts=16)
    L.assign(el, M['steel_dark']); parts.append(el)
    ec = L.box(f"elbow_cap_{side}", (0.11, 0.12, 0.13), (AX, -0.040, 1.70), col, bevel=0.014)
    L.assign(ec, M['steel_paint']); parts.append(ec)
    es = L.box(f"elbow_stop_{side}", (0.090, 0.032, 0.030), (AX, 0.062, 1.76), col, bevel=0.006)
    L.assign(es, M['steel_bare']); parts.append(es)
    er = L.torus(f"elbow_rim_{side}", 0.095, 0.015, (AX, 0.0, 1.70), col, axis='X', segs=14, rings=6)
    L.assign(er, M['steel_bare']); parts.append(er)
    parts.append(bolts(f"elbow_bolt_{side}", 0.008, (AX + sx * 0.096, -0.040, 1.665), (0, 0, 0.036), 3, axis='X', mat=M['steel_bare'], flip=(sx < 0)))
    group(parts, f"elbow_{side}", f"upperarm_{side}")

    # --- antebrazo: el marfil "limpio" del Archivista sobre placa blindada hundida ---
    parts = []
    fa = L.cyl(f"forearm_{side}", 0.072, 0.66, (AX, 0, 1.70), col, pivot='bottom', verts=16, bevel=0.008)
    fa.rotation_euler = (math.radians(180), 0, 0)
    L.assign(fa, M['polymer_ivory']); parts.append(fa)
    parts.append(recess_at(f"fa_plate_{side}", (0.105, 0.028, 0.30), (AX, -0.082, 1.37), depth=0.014, mat=M['steel_paint'], border=0.012))
    parts.append(bolts(f"fa_bolt_a_{side}", 0.0075, (AX - 0.046, -0.094, 1.24), (0, 0, 0.10), 3, axis='Y', mat=M['steel_bare']))
    parts.append(bolts(f"fa_bolt_b_{side}", 0.0075, (AX + 0.046, -0.094, 1.24), (0, 0, 0.10), 3, axis='Y', mat=M['steel_bare']))
    parts.append(L.panel_seam(f"fa_seam_{side}", 0.56, (AX + sx * 0.076, 0.0, 1.38), col, axis='Z', width=0.007, depth=0.008, mat=M['steel_dark']))
    parts.append(ribs_at(f"fa_rib_{side}", 0.22, (0.026, 0.090, 0.026), (AX, 0.074, 1.30), count=2, axis='Z', mat=M['steel_bare']))
    fr = L.torus(f"fa_servo_{side}", 0.085, 0.015, (AX, 0.0, 1.60), col, axis='Z', segs=16, rings=6)
    L.assign(fr, M['steel_dark']); parts.append(fr)
    fc = L.tube(f"fa_conduit_{side}", [(AX + sx * 0.070, 0.048, 1.64), (AX + sx * 0.074, 0.054, 1.36), (AX + sx * 0.068, 0.058, 1.10)], 0.011, col, verts=8)
    L.assign(fc, M['polymer_dark']); parts.append(fc)
    group(parts, f"forearm_{side}", f"forearm_{side}")

    # --- muñeca: rótula y collar de holgura ---
    parts = []
    wr = L.sphere(f"wrist_{side}", 0.078, (AX, 0, 1.04), col, segs=16, rings=10)
    L.assign(wr, M['steel_bare']); parts.append(wr)
    wc = L.torus(f"wrist_collar_{side}", 0.082, 0.016, (AX, 0.0, 1.075), col, axis='Z', segs=16, rings=6)
    L.assign(wc, M['steel_dark']); parts.append(wc)
    group(parts, f"wrist_{side}", f"forearm_{side}")

# ================================ MANOS DE PINZA ================================
# Tres dedos con nudillo, falange, eje y falange distal: volumen suficiente para leer el barrido y la carga (36.3).
# En la palma, el emisor del pulso de fase III con sus aislantes cerámicos y tres mordazas.
for side, sx in (("L", -1), ("R", 1)):
    AX = sx * 0.45

    parts = []
    pl3 = L.box(f"hand_{side}", (0.14, 0.090, 0.14), (AX, 0, 1.04), col, pivot='top', bevel=0.012)
    L.assign(pl3, M['polymer_dark']); parts.append(pl3)
    hs = L.box(f"hand_servo_{side}", (0.090, 0.070, 0.060), (AX, 0.058, 1.00), col, bevel=0.009)
    L.assign(hs, M['steel_dark']); parts.append(hs)
    kr = L.torus(f"knuckle_ring_{side}", 0.075, 0.016, (AX, -0.010, 0.918), col, axis='Z', segs=16, rings=6)
    L.assign(kr, M['steel_bare']); parts.append(kr)
    parts.append(bolts(f"hand_bolt_{side}", 0.008, (AX - 0.042, 0.048, 1.075), (0.042, 0, 0), 3, axis='Z', mat=M['steel_bare']))
    group(parts, f"hand_{side}", f"hand_{side}")

    claws = []
    for k in range(3):
        a = math.radians(120 * k + 90)
        px = AX + 0.055 * math.cos(a)
        py = -0.010 + 0.055 * math.sin(a)
        kn2 = L.sphere(f"claw_kn_{side}{k}", 0.024, (px, py, 0.905), col, segs=10, rings=6)
        L.assign(kn2, M['steel_dark']); claws.append(kn2)
        p1 = L.box(f"claw_p1_{side}{k}", (0.045, 0.060, 0.13), (px, py, 0.900), col, pivot='top', bevel=0.008)
        L.assign(p1, M['steel_bare']); claws.append(p1)
        jt = L.cyl(f"claw_jt_{side}{k}", 0.020, 0.050, (px, py, 0.772), col, axis='X', verts=10)
        L.assign(jt, M['steel_dark']); claws.append(jt)
        p2 = L.box(f"claw_p2_{side}{k}", (0.038, 0.050, 0.11), (px, py - 0.008, 0.772), col, pivot='top', bevel=0.007)
        L.assign(p2, M['steel_dark']); claws.append(p2)
    group(claws, f"claw_{side}", f"hand_{side}")

    # emisor del pulso: carcasa, dos aislantes cerámicos, núcleo y tres mordazas radiales sobre el eje del cañón
    parts = []
    eh = L.cyl(f"pulse_house_{side}", 0.050, 0.050, (AX, -0.048, 0.985), col, axis='Y', verts=14)
    L.assign(eh, M['steel_dark']); parts.append(eh)
    for k, yy in enumerate((-0.058, -0.074)):
        rg2 = L.torus(f"pulse_ring{k}_{side}", 0.055, 0.012, (AX, yy, 0.985), col, axis='Y', segs=14, rings=6)
        L.assign(rg2, M['ceramic']); parts.append(rg2)
    cr = L.cyl(f"pulse_core_{side}", 0.028, 0.060, (AX, -0.078, 0.985), col, axis='Y', verts=12)
    L.assign(cr, M['pulse']); parts.append(cr)
    for k in range(3):
        a = math.radians(90 + k * 120)
        pt = L.box(f"pulse_petal{k}_{side}", (0.022, 0.048, 0.042), (AX + math.cos(a) * 0.046, -0.100, 0.985 + math.sin(a) * 0.046),
                   col, rot=(0, -a, 0), bevel=0.005)
        L.assign(pt, M['heat']); parts.append(pt)
    group(parts, f"pulse_emitter_{side}", f"hand_{side}")

# ================================ NUCA DEMASIADO LARGA ================================
# Cuatro vértebras con su anillo, columna de goma y tres cables que ATRAVIESAN la nuca (15).
parts = []
for i in range(4):
    r = 0.075 - i * 0.005
    z = 2.44 + i * 0.09
    v = L.cyl(f"vert_{i}", r, 0.070, (0, 0.020 * i, z), col, verts=14)
    L.assign(v, M['steel_bare']); parts.append(v)
    vr = L.torus(f"vert_rim_{i}", r, 0.014, (0, 0.020 * i, z), col, axis='Z', segs=14, rings=6)
    L.assign(vr, M['rubber']); parts.append(vr)
ncol = L.cyl("neck_col", 0.038, 0.36, (0, 0.030, 2.40), col, pivot='bottom', verts=12)
L.assign(ncol, M['rubber']); parts.append(ncol)
nsrv = L.box("neck_servo", (0.10, 0.080, 0.060), (0, 0.108, 2.46), col, bevel=0.010)
L.assign(nsrv, M['steel_dark']); parts.append(nsrv)
group(parts, 'neck_vert', 'neck')

parts = []
for k, ox in enumerate((-0.042, 0.0, 0.042)):
    nc = L.tube(f"nape_cable{k}", [(ox, 0.098, 2.42), (ox * 1.1, 0.120, 2.53), (ox * 1.1, 0.134, 2.65), (ox * 0.8, 0.142, 2.75)], 0.011, col, verts=8)
    L.assign(nc, M['rubber']); parts.append(nc)
for k, cz2 in enumerate((2.505, 2.680)):
    cl2 = L.box(f"nape_clamp{k}", (0.12, 0.024, 0.026), (0, 0.126, cz2), col, bevel=0.005)
    L.assign(cl2, M['steel_bare']); parts.append(cl2)
group(parts, 'nape_cables', 'neck')

# ================================ CARA PORCELÁNICA ================================
# Carcasa casi intacta sobre cuerpo remendado (36.3). Cuencas estrechas y PROFUNDAS abiertas con booleano,
# achaflanadas después para que el canto tenga espesor, y con reborde: no son agujeros al vacío de la malla.
head = L.sphere("head", 0.16, (0, 0.06, 2.92), col, segs=28, rings=18, scale=(0.85, 1.0, 1.15))
L.assign(head, M['porcelain'])
eyecuts = []
for sd, sxx in (("L", -1), ("R", 1)):
    c = L.sphere(f"eyecut_{sd}", 0.045, (sxx * 0.055, -0.070, 2.960), col, segs=16, rings=10, scale=(1.0, 1.25, 0.72))
    m = head.modifiers.new(f"Socket_{sd}", 'BOOLEAN'); m.operation = 'DIFFERENCE'; m.object = c
    eyecuts.append(c)
    inner = L.sphere(f"eye_inner_{sd}", 0.026, (sxx * 0.055, -0.042, 2.960), col, segs=12, rings=8)
    add(f"eye_inner_{sd}", inner, 'head', M['polymer_dark'])
L.apply_all(head)
for c in eyecuts: bpy.data.objects.remove(c)
L.chamfer(head, 0.0018, 2, 55)
add('head', head, 'head')

# una sola línea de unión; nunca una boca legible (36.2)
seam_f = L.box("face_seam", (0.18, 0.006, 0.006), (0, -0.098, 2.880), col)
add('face_seam', seam_f, 'head', M['steel_dark'])

parts = []
for sd, sxx in (("L", -1), ("R", 1)):
    rim3 = L.torus(f"socket_rim_{sd}", 0.046, 0.008, (sxx * 0.055, -0.074, 2.960), col, axis='Y', segs=14, rings=6)
    L.assign(rim3, M['porcelain']); parts.append(rim3)
    sp3 = L.box(f"skull_plate_{sd}", (0.026, 0.17, 0.17), (sxx * 0.118, 0.060, 2.930), col, bevel=0.007)
    L.assign(sp3, M['porcelain']); parts.append(sp3)
    parts.append(bolts(f"skull_bolt_{sd}", 0.007, (sxx * 0.128, 0.020, 2.880), (0, 0.080, 0), 2, axis='X', mat=M['steel_bare'], flip=(sxx < 0)))
jaw = L.box("jaw_plate", (0.17, 0.050, 0.055), (0, -0.075, 2.800), col, bevel=0.008)
L.assign(jaw, M['porcelain']); parts.append(jaw)
parts.append(L.vent("head_vent", (0.14, 0.030, 0.075), (0, 0.188, 2.880), col, slats=2, rot=R180, mat_frame=M['steel_dark'], mat_slat=M['steel_bare']))
pod = L.cyl("sensor_pod", 0.026, 0.035, (0, -0.098, 2.850), col, axis='Y', verts=12)
L.assign(pod, M['steel_dark']); parts.append(pod)
lens = L.bolt("sensor_lens", 0.011, (0, -0.116, 2.850), col, axis='Y', kind='hex')
L.assign(lens, M['glass']); parts.append(lens)
crown = L.torus("crown_rim", 0.100, 0.014, (0, 0.060, 3.040), col, axis='Z', segs=20, rings=6)
L.assign(crown, M['steel_dark']); parts.append(crown)
group(parts, 'head_det', 'head')

# ================================ ACABADO ================================
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
# binding se construye en el mismo punto donde nace cada pieza (add/group), con los mismos huesos de siempre.
binding = BIND
missing = [b for b in binding if b not in arm.data.bones]
if missing: raise RuntimeError("huesos inexistentes en el binding: %s" % missing)
for bone, names in binding.items():
    for n in names: L.bind_rigid(P[n], arm, bone)

Z = (0, 0, 0)
L.push_nla(arm, L.walk_cycle(arm, "Archivista_Walk", **L.WALK_PRESETS[ASSET]))
# cuatro firmas distintas (60.4): rayo 1.2 s, barrido 1.4 s, carga 1.5 s, pulso 1.8 s
L.push_nla(arm, L.action(arm, "Archivista_Ray", 36 + 60, loop=False, poses={1: {"upperarm_R": ((0, 0, 0), Z)}, 36: {"upperarm_R": ((-95, 0, -10), Z), "forearm_R": ((-10, 0, 0), Z), "spine": ((-6, 0, -6), Z)}, 40: {"upperarm_R": ((-85, 0, -5), Z)}, 96: {"upperarm_R": ((0, 0, 0), Z), "forearm_R": ((0, 0, 0), Z), "spine": ((0, 0, 0), Z)}}))
L.push_nla(arm, L.action(arm, "Archivista_Sweep", 42 + 66, loop=False, poses={1: {"upperarm_L": ((0, 0, 0), Z), "spine": ((0, 0, 0), Z)}, 42: {"upperarm_L": ((-80, 0, 60), Z), "spine": ((0, 0, 25), Z)}, 50: {"upperarm_L": ((-80, 0, -70), Z), "spine": ((0, 0, -30), Z)}, 108: {"upperarm_L": ((0, 0, 0), Z), "spine": ((0, 0, 0), Z)}}))
L.push_nla(arm, L.action(arm, "Archivista_Charge", 45 + 72, loop=False, poses={1: {"spine": ((0, 0, 0), Z)}, 45: {"spine": ((25, 0, 0), Z), "head": ((-20, 0, 0), Z), "upperarm_L": ((-40, 0, 20), Z), "upperarm_R": ((-40, 0, -20), Z)}, 60: {"spine": ((20, 0, 0), Z)}, 117: {"spine": ((0, 0, 0), Z), "head": ((0, 0, 0), Z), "upperarm_L": ((0, 0, 0), Z), "upperarm_R": ((0, 0, 0), Z)}}))
L.push_nla(arm, L.action(arm, "Archivista_Pulse", 54 + 72, loop=False, poses={1: {"root": ((0, 0, 0), Z)}, 54: {"thigh_L": ((40, 0, 0), Z), "thigh_R": ((40, 0, 0), Z), "shin_L": ((70, 0, 0), Z), "shin_R": ((70, 0, 0), Z), "root": ((0, 0, 0), (0, 0, -0.45)), "upperarm_L": ((-120, 0, 0), Z), "upperarm_R": ((-120, 0, 0), Z)}, 60: {"upperarm_L": ((20, 0, 0), Z), "upperarm_R": ((20, 0, 0), Z)}, 126: {"thigh_L": ((0, 0, 0), Z), "thigh_R": ((0, 0, 0), Z), "shin_L": ((0, 0, 0), Z), "shin_R": ((0, 0, 0), Z), "root": ((0, 0, 0), Z), "upperarm_L": ((0, 0, 0), Z), "upperarm_R": ((0, 0, 0), Z)}}))
L.push_nla(arm, L.action(arm, "Archivista_Death", 60, loop=False, poses={1: {"root": ((0, 0, 0), Z)}, 25: {"thigh_L": ((40, 0, 0), Z), "shin_L": ((70, 0, 0), Z), "spine": ((25, 0, 10), Z), "root": ((0, 0, 0), (0, 0, -0.5))}, 60: {"root": ((88, 0, 8), (0, -0.6, -1.4)), "spine": ((0, 0, 20), Z), "neck": ((-30, 0, 15), Z), "upperarm_L": ((40, 0, 50), Z)}}))

objs = list(P.values())
tris = 0
for o in objs:
    o.data.calc_loop_triangles(); tris += len(o.data.loop_triangles)
blend = L.save_blend(ASSET)
print("built", len(objs), "piezas", tris, "tris")
