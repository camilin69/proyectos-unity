# Seis props hero del entorno (59): OBJ-001 criocámara, OBJ-041 jaula, OBJ-070 puerta corrediza, OBJ-059 terminal,
# OBJ-043 camilla, OBJ-029 carro.
#
# Paso de blockout+ a prop FABRICADO (33.2 / 41.3). Lo que cambia respecto a la versión anterior NO es "más ruido":
# es que cada pieza que antes se insinuaba con una caja ahora existe con su función.
#   · Ninguna arista queda viva: carcasas y chapas llevan chaflán real (L.chamfer / bevel), que es lo que se hornea.
#   · Tornillos donde algo se atornilla: registros de servicio, anclajes de jaula, bridas del manifold, carcasa del motor,
#     placa de serie, horquillas de rueda. No hay un solo tornillo decorativo suelto.
#   · Juntas donde dos piezas se encuentran: costura de carcasa, junta central de las hojas, costura del colchón.
#   · Rejillas donde algo respira: base térmica de la criocámara, bahía del motor de la puerta, ventilación del terminal.
#   · Nervios donde hay carga: testeros de la criocámara, hoja de puerta de 3.45 m, bajo la plataforma del carro.
#   · Desgaste donde hay roce: lo resuelve el material (Pointiness/AO de L.material), no geometría.
#
# COSTE (43): el detalle se agrupa por función con L.join, así que el número de OBJETOS baja respecto a la versión
# anterior aunque la geometría suba: menos renderers en Unity y mucha más lectura cercana.
#   OBJ-001 3.210 → ~8.7k (presupuesto criocámara 5–12k) · resto 680–2.816 → ~2.2–2.9k (prop común 0.3–3k)
# Escala de coste usada al dimensionar (medida contra los report.json de EX-04, exacta en jaula/puerta/carro):
#   caja lisa 12 · caja bisel 1 seg 28 · carcasa con chaflán 2 seg 60 · caja bisel 3 seg 92 · 4 seg 124
#   cilindro n lados 4n-4 · tubo de p puntos 2n(p-1)+2(n-2) · toro 2·segs·rings · tornillo hex 32
#   vent(slats=k) 60(k+1) · rib_row(count=c) 60c · recess 300 · panel_seam 60
#
# CONTRATOS QUE NO SE TOCAN (los usa Unity o el rig):
#   · IDs de asset, estructura `if WHICH`, nombres de hueso, clips Cryo_Open/Cryo_Closed/Cage_Open/Door_Open.
#   · OBJ-070: HeroDressing.cs busca por nombre los hijos "leaf_0" y "leaf_1" y les cuelga un BoxCollider
#     center (0, 1.72, 0) size (1.5, 3.45, 0.14) → el origen de cada hoja sigue en su base (±0.75, 0, 0.02) y la hoja
#     sigue midiendo 1.5 × 0.12 × 3.45. Por eso la caja de la hoja va SIEMPRE primera en L.join (join conserva el
#     origen del primer objeto) y el nervio más saliente se queda dentro de los 0.14 del collider.
#   · OBJ-029: CartFactory.cs usa BoxCollider size (1.0, 0.9, 0.6) center (0, 0.45, 0) → el carro no crece de 1.06 × 0.6 × 0.92.
import bpy, math, importlib, sys
sys.path.insert(0, r"C:/Users/HP/Documents/GitHub/proyectos-unity/SourceArt/Scripts")
import esn_lib as L; importlib.reload(L)
from mathutils import Vector, Euler

WHICH = globals().get("WHICH", "cryo")
L.reset_scene()
M = L.std_mats()
M['paint_med'] = L.material("M_PaintMedical", (0.78, 0.8, 0.78), 0.45, 0.0, wear=0.3, wear_color=(0.5, 0.5, 0.48), bump=0.12)
M['paint_ind'] = L.material("M_PaintIndustrial", (0.55, 0.5, 0.2), 0.55, 0.0, wear=0.4, wear_color=(0.45, 0.35, 0.25), bump=0.15)
M['foam'] = L.material("M_Foam", (0.16, 0.18, 0.2), 0.8, 0.0, bump=0.25, scale=18)
M['mattress'] = L.material("M_Mattress", (0.55, 0.6, 0.62), 0.8, 0.0, bump=0.2, scale=25)
M['blanket'] = L.material("M_Blanket", (0.45, 0.5, 0.42), 0.9, 0.0, bump=0.4, scale=40)
M['wire'] = L.material("M_Wire", (0.3, 0.3, 0.32), 0.5, 1.0, wear=0.3, wear_color=(0.4, 0.28, 0.2))
# escarcha bajo la tapa (59.1 "condensación"): capa rugosa y clara sobre el vidrio, no un vidrio sucio
M['frost'] = L.material("M_Frost", (0.86, 0.9, 0.93), 0.72, 0.0, bump=0.45, scale=70, edge_wear=0.0, ao=0.5)
# rojo de seguridad: freno de camilla, tiradores de emergencia (poca superficie, mucha lectura)
M['plastic_red'] = L.material("M_PlasticRed", (0.42, 0.06, 0.05), 0.45, 0.0, wear=0.35, wear_color=(0.3, 0.2, 0.16), bump=0.1)
# placa corporativa NÉMESIS manchada: serial nuevo encima del nombre antiguo (59.2)
M['label'] = L.material("M_PropLabel", (0.74, 0.71, 0.63), 0.6, 0.0, wear=0.45, wear_color=(0.42, 0.36, 0.3), bump=0.12, scale=18)
# amarillo de borde de carga/hoja: la pintura que se come el roce (41.3)
M['hazard'] = L.material("M_Hazard", (0.6, 0.48, 0.08), 0.6, 0.0, wear=0.55, wear_color=(0.3, 0.28, 0.25), bump=0.15)
P = []
RAD = math.radians
# orientaciones de rejilla: L.vent abre hacia -Y, así que la rotación decide a qué cara respira
FRONT, BACK, LEFT, RIGHT, UP = (0, 0, 0), (0, 0, math.pi), (0, 0, -math.pi / 2), (0, 0, math.pi / 2), (-math.pi / 2, 0, 0)


def add(o, m=None):
    if m is not None: L.assign(o, m)
    P.append(o); return o


def shell(name, size, loc, mat, rot=(0, 0, 0), pivot='center', cham=0.004, segs=2):
    """Carcasa/superficie grande: caja + chaflán por ángulo (60 tris). Ninguna arista viva (33.2)."""
    o = L.box(name, size, loc, col, pivot=pivot, rot=rot)
    L.assign(o, mat); L.chamfer(o, cham, segs, 50)
    return o


def plate(name, size, loc, mat, rot=(0, 0, 0), pivot='center', bev=0.003):
    """Chapa/pieza mediana: chaflán de un segmento (28 tris). Barato y sigue sin arista viva."""
    o = L.box(name, size, loc, col, pivot=pivot, rot=rot, bevel=bev, segs=1)
    L.assign(o, mat); return o


def slab(name, size, loc, mat, rot=(0, 0, 0), pivot='center'):
    """Pieza pequeña sin bisel (12 tris): a esa escala el Bevel node del material ya redondea el sombreado."""
    o = L.box(name, size, loc, col, pivot=pivot, rot=rot)
    L.assign(o, mat); return o


def rod(name, r, d, loc, mat, axis='Z', verts=8, pivot='center', bevel=0.0):
    o = L.cyl(name, r, d, loc, col, axis=axis, verts=verts, pivot=pivot, bevel=bevel)
    L.assign(o, mat); return o


def screw(name, r, loc, mat, axis='Z'):
    o = L.bolt(name, r, loc, col, axis=axis)
    L.assign(o, mat); return o


def grp(objs, name):
    """Une piezas ya materializadas en un solo renderer. El PRIMER objeto fija el origen del grupo."""
    return add(L.join(objs, name))


def ribs(name, length, size, center, mat, count=3, axis='Y', rot=(0, 0, 0)):
    """L.rib_row ancla el origen en el PRIMER nervio; aquí se pasa el centro de la tirada y se compensa."""
    d = length * (count - 1) / (2.0 * count)
    off = Vector({'X': (d, 0, 0), 'Y': (0, d, 0), 'Z': (0, 0, d)}[axis])
    off.rotate(Euler(rot, 'XYZ'))
    return L.rib_row(name, length, size, (center[0] - off.x, center[1] - off.y, center[2] - off.z), col,
                     count=count, axis=axis, rot=rot, mat=mat)


def sunk(name, size, center, mat, depth=None, rot=(0, 0, 0), border=None):
    """L.recess ancla el origen en el listón superior; aquí se pasa el centro real del panel y se compensa."""
    b = border if border is not None else min(size[0], size[2]) * 0.08
    off = Vector((0, 0, (size[2] - b) / 2.0))
    off.rotate(Euler(rot, 'XYZ'))
    return L.recess(name, size, (center[0] + off.x, center[1] + off.y, center[2] + off.z), col,
                    depth=depth, rot=rot, mat=mat, border=b)


def seam(name, length, loc, mat, axis='Y', width=0.006, depth=0.005, rot=None):
    o = L.panel_seam(name, length, loc, col, axis=axis, width=width, depth=depth, mat=mat)
    if rot: o.rotation_euler = rot
    return o


if WHICH == "cryo":
    ASSET = "OBJ-001_Criocamara"; col = L.collection(ASSET)
    # Envolvente 2.4 × 1.1 × 1 m (59.1). Es el objeto que el jugador mira de cerca durante toda la apertura: aquí va
    # la mayor parte del presupuesto (5–12k). Base con registros reales, lecho con hendidura y bordes, tapa de marco +
    # vidrio con escarcha, bisagras de nudillo y pasador, seguros con gancho, manifold térmico con bridas y panel de control.

    # ---------------------------------------------------------------- base: carcasa, registros, nervios, placa
    b_shell = L.box("base", (2.4, 1.1, 0.5), (0, 0, 0.12), col, pivot='bottom', bevel=0.06, segs=4)
    L.assign(b_shell, M['paint_med'])
    # nervios en los testeros: por ahí baja la carga del lecho y de la tapa abierta
    rib_l = ribs("base_rib_L", 0.9, (0.03, 0.045, 0.34), (-1.198, 0, 0.35), M['steel_paint'], count=3, axis='Y')
    rib_r = ribs("base_rib_R", 0.9, (0.03, 0.045, 0.34), (1.198, 0, 0.35), M['steel_paint'], count=3, axis='Y')
    # junta de la chapa superior contra la carcasa, en las dos caras largas
    sm_f = seam("base_seam_f", 2.3, (0, -0.552, 0.555), M['steel_bare'], axis='X')
    sm_b = seam("base_seam_b", 2.3, (0, 0.552, 0.555), M['steel_bare'], axis='X')
    # registros de servicio: panel hundido con reborde (el AO lo ensombrece) y su tornillería en las cuatro esquinas
    reg_a = sunk("base_reg_a", (0.5, 0.05, 0.26), (-0.72, -0.535, 0.30), M['steel_paint'], depth=0.03, border=0.02)
    reg_b = sunk("base_reg_b", (0.5, 0.05, 0.26), (0.72, -0.535, 0.30), M['steel_paint'], depth=0.03, border=0.02)
    bolts = []
    for i, bx in enumerate((-0.72, 0.72)):
        bolts.append(L.bolt_row(f"base_reg_bolt_lo{i}", 0.006, (bx - 0.22, -0.558, 0.19), (0.44, 0, 0), 2, col, axis='Y', mat=M['steel_bare']))
        bolts.append(L.bolt_row(f"base_reg_bolt_hi{i}", 0.006, (bx - 0.22, -0.558, 0.41), (0.44, 0, 0), 2, col, axis='Y', mat=M['steel_bare']))
    # base térmica: respira por delante y por detrás (59.1 "sistema recibe energía de núcleo sellado")
    vn_f = L.vent("base_vent_f", (0.34, 0.035, 0.22), (0, -0.545, 0.30), col, slats=3, rot=FRONT, mat_frame=M['steel_dark'], mat_slat=M['steel_dark'])
    vn_b = L.vent("base_vent_b", (0.34, 0.035, 0.22), (0, 0.545, 0.30), col, slats=3, rot=BACK, mat_frame=M['steel_dark'], mat_slat=M['steel_dark'])
    # placa de serie atornillada con dígitos en relieve
    nplate = plate("base_plate", (0.3, 0.012, 0.075), (0, -0.553, 0.50), M['label'], bev=0.002)
    ndig = ribs("base_plate_digits", 0.16, (0.022, 0.008, 0.03), (0, -0.559, 0.50), M['steel_dark'], count=3, axis='X')
    # cantoneras de esquina: la carcasa se golpea ahí al mover la cámara
    corners = [shell(f"base_corner{i}", (0.08, 0.08, 0.16), (sx * 1.175, sy * 0.522, 0.20), M['steel_bare'], cham=0.004)
               for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1)))]
    # forro interior: sólo la parte que se ve al abrir (59.1 "partes interiores solo donde se ven al abrir").
    # Se queda por dentro del hueco de la tapa (2.1 × 0.8) para no chocar con el marco al cerrarse.
    liner = [shell("base_liner_f", (2.08, 0.02, 0.12), (0, -0.388, 0.66), M['polymer_ivory'], cham=0.003),
             shell("base_liner_b", (2.08, 0.02, 0.12), (0, 0.388, 0.66), M['polymer_ivory'], cham=0.003),
             shell("base_liner_L", (0.02, 0.776, 0.12), (-1.035, 0, 0.66), M['polymer_ivory'], cham=0.003),
             shell("base_liner_R", (0.02, 0.776, 0.12), (1.035, 0, 0.66), M['polymer_ivory'], cham=0.003)]
    grp([b_shell, rib_l, rib_r, sm_f, sm_b, reg_a, reg_b] + bolts + [vn_f, vn_b, nplate, ndig] + corners + liner, "base")

    # ---------------------------------------------------------------- patas con amortiguador
    feet = []
    for i, (x, y) in enumerate(((-1.05, -0.45), (1.05, -0.45), (-1.05, 0.45), (1.05, 0.45))):
        feet.append(slab(f"foot_pad{i}", (0.16, 0.12, 0.05), (x, y, 0.0), M['rubber'], pivot='bottom'))
        feet.append(rod(f"foot_damper{i}", 0.035, 0.07, (x, y, 0.05), M['steel_bare'], verts=10, pivot='bottom'))
        feet.append(rod(f"foot_rod{i}", 0.018, 0.045, (x, y, 0.115), M['steel_bare'], verts=8))
        feet.append(slab(f"foot_flange{i}", (0.14, 0.10, 0.02), (x, y, 0.11), M['steel_dark']))
        feet.append(screw(f"foot_bolt{i}", 0.006, (x, y, 0.125), M['steel_bare']))
    grp(feet, "feet")

    # ---------------------------------------------------------------- lecho: bastidor, acolchado con hendidura, almohada
    bf = L.box("bed_frame", (2.2, 0.9, 0.06), (0, 0, 0.62), col, pivot='bottom', bevel=0.01, segs=2); L.assign(bf, M['steel_bare'])
    bcross = [plate(f"bed_cross{i}", (0.04, 0.86, 0.03), (x, 0, 0.605), M['steel_bare'], pivot='bottom') for i, x in enumerate((-0.6, 0.6))]
    grp([bf] + bcross, "bed_frame")

    bed = L.box("bed_pad", (2.05, 0.75, 0.12), (0, 0, 0.68), col, pivot='bottom', bevel=0.04, segs=4)
    L.assign(bed, M['foam'])
    cut = L.box("body_cut", (1.7, 0.45, 0.06), (0.05, 0, 0.77), col)
    m = bed.modifiers.new("Body", 'BOOLEAN'); m.operation = 'DIFFERENCE'; m.object = cut; L.apply_all(bed); bpy.data.objects.remove(cut)
    bolster = [plate(f"bed_bolster{i}", (2.0, 0.06, 0.05), (0, sy * 0.345, 0.79), M['foam']) for i, sy in enumerate((-1, 1))]
    bseam = [seam(f"bed_seam{i}", 1.95, (0, sy * 0.30, 0.797), M['fabric'], axis='X', width=0.008, depth=0.006) for i, sy in enumerate((-1, 1))]
    grp([bed] + bolster + bseam, "bed_pad")

    pil = L.box("pillow", (0.4, 0.5, 0.08), (0.85, 0, 0.8), col, pivot='bottom', bevel=0.03, segs=3); L.assign(pil, M['foam'])
    pseam = seam("pillow_seam", 0.46, (0.85, 0, 0.878), M['fabric'], axis='Y', width=0.007, depth=0.005)
    grp([pil, pseam], "pillow")

    add(L.box("gasket", (2.3, 1.0, 0.03), (0, 0, 0.62), col, pivot='bottom', bevel=0.01, segs=2), M['rubber'])

    # ---------------------------------------------------------------- tapa: marco con hueco, juntas, cantoneras, tirador
    lid = L.box("lid_frame", (2.3, 1.0, 0.08), (0, 0, 0.65), col, pivot='bottom', bevel=0.02, segs=3)
    hole = L.box("lid_hole", (2.1, 0.8, 0.2), (0, 0, 0.6), col)
    m = lid.modifiers.new("Hole", 'BOOLEAN'); m.operation = 'DIFFERENCE'; m.object = hole; L.apply_all(lid); bpy.data.objects.remove(hole)
    L.assign(lid, M['paint_med'])
    lseam = [seam(f"lid_seam{i}", 2.26, (0, sy * 0.46, 0.729), M['steel_bare'], axis='X') for i, sy in enumerate((-1, 1))]
    lgus = [shell(f"lid_gusset{i}", (0.10, 0.10, 0.05), (sx * 1.10, sy * 0.45, 0.70), M['steel_paint'], cham=0.004)
            for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1)))]
    # cajas de cierre: donde muerde el gancho del seguro
    keep = [shell(f"lid_keeper{i}", (0.08, 0.06, 0.05), (sx * 0.7, -0.47, 0.705), M['steel_dark'], cham=0.003) for i, sx in enumerate((-1, 1))]
    # tirador: la mano que deja huella (59.1 "evento de contacto de mano")
    lbar = rod("lid_bar", 0.014, 0.4, (0, -0.488, 0.755), M['steel_bare'], axis='X', verts=10)
    lpost = [slab(f"lid_bar_post{i}", (0.03, 0.05, 0.03), (sx * 0.19, -0.475, 0.74), M['steel_bare']) for i, sx in enumerate((-1, 1))]
    grp([lid] + lseam + lgus + keep + [lbar] + lpost, "lid_frame")

    # vidrio curvo y, por dentro, la capa de escarcha: dos mallas, no diez capas de vidrio superpuesto (59.1)
    glass = L.sphere("lid_glass", 1.0, (0, 0, 0.66), col, segs=48, rings=24, scale=(1.08, 0.42, 0.34))
    frost = L.sphere("lid_frost", 1.0, (0, 0, 0.66), col, segs=28, rings=12, scale=(1.062, 0.408, 0.328))
    cutb = L.box("glass_cut", (3, 2, 1.0), (0, 0, 0.15), col)
    for o in (glass, frost):
        m = o.modifiers.new("Half", 'BOOLEAN'); m.operation = 'DIFFERENCE'; m.object = cutb; L.apply_all(o)
    bpy.data.objects.remove(cutb)
    add(glass, M['glass']); add(frost, M['frost'])

    # bisagras de verdad: nudillo + eje + pasador en la tapa, pletina atornillada en la base
    hbase = []
    for i, x in enumerate((-0.8, 0.8)):
        kn = shell(f"hinge{i}_knuckle", (0.14, 0.06, 0.06), (x, 0.5, 0.67), M['steel_dark'], cham=0.003)
        br = rod(f"hinge{i}_barrel", 0.03, 0.16, (x, 0.5, 0.67), M['steel_bare'], axis='X', verts=12)
        pn = rod(f"hinge{i}_pin", 0.012, 0.21, (x, 0.5, 0.67), M['steel_bare'], axis='X', verts=8)
        # pletina de la tapa: apoya SOBRE el marco (z 0.65–0.73), no dentro de su espesor
        lf = plate(f"hinge{i}_leaf", (0.16, 0.10, 0.02), (x, 0.455, 0.74), M['steel_bare'], bev=0.002)
        grp([kn, br, pn, lf], f"hinge{i}")
        # pletina de la base: atornillada por FUERA de la pared trasera, que es donde hay material al que morder
        hbase.append(plate(f"hinge_base_leaf{i}", (0.16, 0.02, 0.14), (x, 0.556, 0.56), M['steel_bare'], bev=0.002))
        hbase.append(L.bolt_row(f"hinge_base_bolt{i}", 0.006, (x - 0.05, 0.566, 0.52), (0.10, 0, 0), 2, col, axis='Y', mat=M['steel_bare']))
    grp(hbase, "hinge_base")

    # seguros: cuerpo, gancho y maneta. El clip los gira sobre su eje vertical antes de mover la tapa
    lmount = []
    for i, x in enumerate((-0.7, 0.7)):
        bd = shell(f"latch{i}_body", (0.09, 0.06, 0.07), (x, -0.5, 0.66), M['steel_dark'], cham=0.003)
        hk = plate(f"latch{i}_hook", (0.05, 0.05, 0.03), (x, -0.5, 0.70), M['steel_bare'], bev=0.002)
        hd = rod(f"latch{i}_handle", 0.012, 0.07, (x, -0.528, 0.655), M['steel_bare'], axis='Y', verts=8)
        grp([bd, hk, hd], f"latch{i}")
        lmount.append(plate(f"latch_mount{i}", (0.12, 0.07, 0.02), (x, -0.5, 0.625), M['steel_bare'], bev=0.002))
        lmount.append(L.bolt_row(f"latch_mount_bolt{i}", 0.005, (x - 0.04, -0.5, 0.638), (0.08, 0, 0), 2, col, axis='Z', mat=M['steel_bare']))
    grp(lmount, "latch_mount")

    # ---------------------------------------------------------------- panel de control: bisel hundido, botones, dial, pilotos
    pm = shell("screen_mount", (0.06, 0.08, 0.35), (1.2, -0.3, 0.6), M['steel_dark'], pivot='bottom', cham=0.003)
    ph = shell("screen_housing", (0.05, 0.3, 0.2), (1.235, -0.3, 0.98), M['polymer_dark'], cham=0.004)
    pb = sunk("screen_bezel", (0.3, 0.05, 0.2), (1.24, -0.3, 0.98), M['polymer_dark'], depth=0.03, rot=RIGHT, border=0.018)
    btn_plate = plate("button_plate", (0.03, 0.26, 0.06), (1.25, -0.3, 0.86), M['polymer_dark'], bev=0.002)
    btns = [rod(f"button{i}", 0.013, 0.012, (1.268, -0.40 + i * 0.05, 0.86), M['rubber'], axis='X', verts=10) for i in range(5)]
    # el dial se apoya en el poste del montaje (x 1.17–1.23); si se adelanta más, flota
    dial = rod("dial", 0.022, 0.018, (1.238, -0.3, 0.775), M['polymer_ivory'], axis='X', verts=12)
    dpt = slab("dial_mark", (0.006, 0.006, 0.02), (1.2495, -0.3, 0.787), M['steel_dark'])
    leds = [slab(f"led{i}", (0.006, 0.014, 0.014), (1.2665, -0.40 + i * 0.04, 0.837), M['emitter']) for i in range(3)]
    grp([pm, ph, pb, btn_plate] + btns + [dial, dpt] + leds, "control_panel")
    # la pantalla va DENTRO del bisel hundido (x 1.215–1.265), no enrasada con su cara exterior
    add(L.box("screen", (0.006, 0.26, 0.16), (1.250, -0.3, 0.98), col), M['screen'])
    cab = L.tube("screen_cable", [(1.22, -0.3, 0.80), (1.18, -0.34, 0.68), (1.12, -0.40, 0.52), (1.06, -0.42, 0.38)], 0.008, col, verts=10)
    add(cab, M['rubber'])

    # ---------------------------------------------------------------- térmico: manifold con bridas y válvula, tubos con aislante
    mf = shell("manifold", (0.3, 0.16, 0.14), (-1.15, 0.3, 0.3), M['steel_dark'], cham=0.004)
    mfl = [plate(f"manifold_flange{i}", (0.035, 0.19, 0.17), (x, 0.3, 0.3), M['steel_bare'], bev=0.003) for i, x in enumerate((-1.30, -1.00))]
    mbolt = [L.bolt_row(f"manifold_bolt{i}", 0.006, (x, 0.22, 0.30), (0, 0.16, 0), 2, col, axis='X', mat=M['steel_bare']) for i, x in enumerate((-1.318, -0.982))]
    # el vástago arranca en la tapa del manifold (z 0.37), no en el aire
    valve = rod("manifold_valve", 0.022, 0.07, (-1.15, 0.3, 0.36), M['copper'], verts=10, pivot='bottom')
    wheel = L.torus("manifold_wheel", 0.045, 0.008, (-1.15, 0.3, 0.435), col, axis='Z', segs=10, rings=4); L.assign(wheel, M['steel_bare'])
    grp([mf] + mfl + mbolt + [valve, wheel], "manifold")

    pipes = []
    for i in range(3):
        y = 0.24 + i * 0.06   # los tres salen por la cara del manifold (y 0.22–0.38), no por su borde
        tb = L.tube(f"pipe{i}", [(-1.31, y, 0.3), (-1.42, y, 0.3), (-1.48, y, 0.22), (-1.48, y, 0.08), (-1.46, y, 0.0)], 0.02, col, verts=10)
        L.assign(tb, M['rubber']); pipes.append(tb)
        pipes.append(rod(f"pipe_conn{i}", 0.028, 0.03, (-1.318, y, 0.3), M['copper'], axis='X', verts=12))
        pipes.append(rod(f"pipe_sleeve{i}", 0.032, 0.09, (-1.48, y, 0.15), M['polymer_ivory'], verts=10))
        pipes.append(rod(f"pipe_clamp{i}", 0.026, 0.012, (-1.42, y, 0.3), M['steel_dark'], axis='X', verts=8))
    grp(pipes, "pipes")

    for o in P: L.apply_all(o); L.smooth(o, 40); L.uv_project(o, 0.006)
    # rig: tapa sobre bisagra trasera (eje X en y=0.5, z=0.67), seguros
    arm = L.armature("Armature_Cryo", [("root", (0, 0, 0), (0, 0, 0.2), None), ("lid", (0, 0.5, 0.67), (0, -0.5, 0.67), "root"), ("latch_L", (-0.7, -0.5, 0.66), (-0.7, -0.5, 0.72), "root"), ("latch_R", (0.7, -0.5, 0.66), (0.7, -0.5, 0.72), "root")], col)
    LID = ("lid_frame", "lid_glass", "lid_frost", "hinge0", "hinge1")
    for o in P:
        bone = "lid" if o.name in LID else "latch_L" if o.name == "latch0" else "latch_R" if o.name == "latch1" else "root"
        L.bind_rigid(o, arm, bone)
    Z = (0, 0, 0)
    # OBJ-001: seguro libera → junta despega → tapa abre (2.4 s)
    L.push_nla(arm, L.action(arm, "Cryo_Open", 72, loop=False, poses={1: {"lid": ((0, 0, 0), Z), "latch_L": ((0, 0, 0), Z), "latch_R": ((0, 0, 0), Z)}, 12: {"latch_L": ((0, 60, 0), Z), "latch_R": ((0, -60, 0), Z)}, 22: {"lid": ((-4, 0, 0), Z)}, 72: {"lid": ((-70, 0, 0), Z)}}))
    L.push_nla(arm, L.action(arm, "Cryo_Closed", 2, loop=False, poses={1: {"lid": ((0, 0, 0), Z)}}))
    L.save_blend(ASSET); print("built cryo", len(P))

elif WHICH == "cage":
    ASSET = "OBJ-041_Jaula"; col = L.collection(ASSET)
    W, D, H = 2.2, 1.5, 2.4
    # Módulo 2.2 × 1.5 × 2.4 (59.2). Marco soldado y anclado al suelo, barras separadas para leer al sujeto sin moiré,
    # puerta con espesor y bisagra de nudillo, cierre independiente, placa de número sobre el nombre antiguo.

    # ---------------------------------------------------------------- piso y drenaje
    fl = shell("floor_grate", (W, D, 0.05), (0, 0, 0.05), M['steel_bare'], pivot='bottom', cham=0.004)
    fs = seam("floor_seam", W - 0.1, (0, 0, 0.101), M['steel_dark'], axis='X', width=0.008, depth=0.004)
    grp([fl, fs], "floor_grate")
    # el drenaje respira hacia arriba: lamas reales, el líquido tiene a dónde ir (59.2 "sangre con dirección hacia drenaje")
    add(L.vent("drain", (0.28, 0.05, 0.28), (0.6, 0.4, 0.093), col, slats=2, rot=UP, mat_frame=M['steel_dark'], mat_slat=M['steel_dark']))

    # ---------------------------------------------------------------- postes y anclajes al concreto
    posts, anchors = [], []
    for x in (-W / 2, W / 2):
        for y in (-D / 2, D / 2):
            posts.append(shell(f"post_{x:.1f}_{y:.1f}", (0.06, 0.06, H), (x, y, 0.0), M['steel_paint'], pivot='bottom', cham=0.004))
            anchors.append(plate(f"anchor_{x:.1f}_{y:.1f}", (0.16, 0.16, 0.025), (x, y, 0.0), M['steel_dark'], pivot='bottom', bev=0.003))
            anchors.append(screw(f"anchor_bolt_{x:.1f}_{y:.1f}", 0.008, (x + 0.05, y + 0.05, 0.026), M['steel_bare']))
    grp(posts, "posts")
    grp(anchors, "anchors")

    # ---------------------------------------------------------------- travesaños, cordón de soldadura y cartelas
    rails = []
    for z in (0.35, H - 0.05):
        rails.append(plate(f"rail_front_{z:.1f}", (W, 0.05, 0.05), (0, -D / 2, z), M['steel_paint']))
        rails.append(plate(f"rail_back_{z:.1f}", (W, 0.05, 0.05), (0, D / 2, z), M['steel_paint']))
        rails.append(plate(f"rail_L_{z:.1f}", (0.05, D, 0.05), (-W / 2, 0, z), M['steel_paint']))
        rails.append(plate(f"rail_R_{z:.1f}", (0.05, D, 0.05), (W / 2, 0, z), M['steel_paint']))
    # cordón de soldadura donde el travesaño alto muere contra el poste: ahí es donde se suelda, y sólo ahí
    for i, (x, y) in enumerate(((-W / 2, -D / 2), (W / 2, -D / 2), (-W / 2, D / 2), (W / 2, D / 2))):
        rails.append(rod(f"weld_{i}", 0.036, 0.03, (x, y, H - 0.05), M['steel_bare'], verts=6))
    # cartelas en las dos esquinas frontales altas: la puerta cuelga de ese lado
    for i, sx in enumerate((-1, 1)):
        rails.append(slab(f"gusset{i}", (0.12, 0.012, 0.12), (sx * (W / 2 - 0.07), -D / 2, H - 0.13), M['steel_paint'], rot=(0, RAD(45), 0)))
    grp(rails, "rails")

    # ---------------------------------------------------------------- barras: menos y más gruesas, separación ≥ 18 cm (59.2)
    # El hueco de la puerta (x -1.05 … -0.25) NO lleva barras: lo cierra la propia puerta con sus barrotes.
    bars = []
    for i in range(7):
        bars.append(L.cyl(f"bar_f{i + 1}", 0.016, H - 0.45, (-0.2 + i * 0.2, -D / 2, 0.4), col, pivot='bottom', verts=8))
    for i in range(1, 8):
        bars.append(L.cyl(f"bar_l{i}", 0.016, H - 0.45, (-W / 2, -D / 2 + i * D / 8, 0.4), col, pivot='bottom', verts=8))
        bars.append(L.cyl(f"bar_r{i}", 0.016, H - 0.45, (W / 2, -D / 2 + i * D / 8, 0.4), col, pivot='bottom', verts=8))
    for b in bars: L.assign(b, M['steel_paint'])
    grp(bars, "bars")

    # paño sólido trasero con nervios: el collider de este lado es macizo, no barrotes (59.2)
    bp = shell("back_panel", (W - 0.1, 0.03, H - 0.45), (0, D / 2, 0.4), M['steel_paint'], pivot='bottom', cham=0.004)
    bpr = ribs("back_rib", 1.6, (0.025, 0.02, 1.85), (0, D / 2 + 0.024, 1.375), M['steel_paint'], count=2, axis='X')
    grp([bp, bpr], "back_panel")

    # ---------------------------------------------------------------- puerta con espesor, barrotes, cruceta y tirador
    door = shell("door_frame", (0.8, 0.05, H - 0.5), (-W / 2 + 0.45, -D / 2 - 0.05, 0.42), M['steel_paint'], pivot='bottom', cham=0.004)
    dparts = [door]
    for i in range(1, 6):
        dparts.append(rod(f"dbar{i}", 0.014, H - 0.6, (-W / 2 + 0.1 + i * 0.13, -D / 2 - 0.05, 0.46), M['steel_paint'], verts=8, pivot='bottom'))
    dparts.append(rod("door_handle", 0.016, 0.16, (-W / 2 + 0.78, -D / 2 - 0.08, 1.1), M['steel_bare'], verts=8))
    grp(dparts, "door")
    # el nudillo gira CON la puerta; la pletina atornillada al poste se queda quieta, así que son dos objetos
    hg, hm = [], []
    for i, z in enumerate((0.7, 1.9)):
        hg.append(rod(f"door_hinge{i}_barrel", 0.025, 0.1, (-W / 2 + 0.06, -D / 2 - 0.05, z), M['steel_bare'], verts=10))
        hm.append(plate(f"hinge_mount{i}_leaf", (0.10, 0.02, 0.07), (-W / 2 + 0.02, -D / 2 - 0.05, z), M['steel_bare'], bev=0.002))
        hm.append(L.bolt_row(f"hinge_mount{i}_bolt", 0.005, (-W / 2 - 0.01, -D / 2 - 0.062, z - 0.02), (0, 0, 0.04), 2, col, axis='Y', mat=M['steel_bare']))
    grp(hg, "cage_hinge")
    grp(hm, "hinge_mount")

    # ---------------------------------------------------------------- cierre independiente de la puerta
    lk = shell("lock_box", (0.3, 0.15, 0.2), (-W / 2 + 0.95, -D / 2 - 0.09, 1.1), M['steel_dark'], cham=0.004)
    lkf = plate("lock_face", (0.24, 0.02, 0.15), (-W / 2 + 0.95, -D / 2 - 0.17, 1.1), M['steel_paint'], bev=0.002)
    lkb = L.bolt_row("lock_bolt_row", 0.005, (-W / 2 + 0.85, -D / 2 - 0.182, 1.04), (0.2, 0, 0), 2, col, axis='Y', mat=M['steel_bare'])
    lkl = slab("lock_light", (0.02, 0.01, 0.02), (-W / 2 + 0.95, -D / 2 - 0.181, 1.15), M['emitter'])
    grp([lk, lkf, lkb, lkl], "lock_box")
    add(L.box("lock_bolt", (0.12, 0.03, 0.03), (-W / 2 + 0.82, -D / 2 - 0.02, 1.1), col), M['steel_bare'])

    # placa de número montada FÍSICAMENTE (59.2): pletina soldada entre dos barras + placa antigua + serial nuevo encima.
    # Sin la pletina las placas flotarían delante de las barras, que es justo lo que la ficha prohíbe.
    pl_bk = plate("plate_bracket", (0.26, 0.014, 0.14), (0.5, -D / 2, 1.6), M['steel_paint'], bev=0.003)
    pl_old = plate("plate_old", (0.22, 0.01, 0.1), (0.5, -D / 2 - 0.012, 1.6), M['ceramic'], bev=0.002)
    pl_new = plate("plate_new", (0.14, 0.01, 0.06), (0.55, -D / 2 - 0.02, 1.58), M['label'], bev=0.002)
    pl_b = L.bolt_row("plate_bolt", 0.004, (0.49, -D / 2 - 0.026, 1.58), (0.12, 0, 0), 2, col, axis='Y', mat=M['steel_bare'])
    grp([pl_bk, pl_old, pl_new, pl_b], "plate")

    # tubos por pasacables, no a través de una barra (59.2)
    ft = L.tube("feed_tube", [(0.9, D / 2, 1.2), (1.1, D / 2 + 0.14, 1.28), (1.3, D / 2 + 0.26, 1.18), (1.4, D / 2 + 0.3, 1.0)], 0.015, col, verts=10)
    L.assign(ft, M['rubber'])
    gl = rod("feed_gland", 0.032, 0.05, (0.9, D / 2 + 0.01, 1.2), M['steel_dark'], axis='Y', verts=8)
    grp([ft, gl], "feed_tube")

    for o in P: L.apply_all(o); L.smooth(o, 40); L.uv_project(o, 0.006)
    arm = L.armature("Armature_Cage", [("root", (0, 0, 0), (0, 0, 0.2), None), ("door", (-W / 2 + 0.06, -D / 2 - 0.05, 0.4), (-W / 2 + 0.06, -D / 2 - 0.05, 2.3), "root"), ("bolt", (-W / 2 + 0.82, -D / 2 - 0.02, 1.1), (-W / 2 + 0.82, -D / 2 - 0.02, 1.2), "root")], col)
    for o in P: L.bind_rigid(o, arm, "door" if o.name in ("door", "cage_hinge") else "bolt" if o.name == "lock_bolt" else "root")
    Z = (0, 0, 0)
    L.push_nla(arm, L.action(arm, "Cage_Open", 60, loop=False, poses={1: {"bolt": ((0, 0, 0), Z), "door": ((0, 0, 0), Z)}, 15: {"bolt": ((0, 0, 0), (0.1, 0, 0))}, 60: {"door": ((0, 0, -95), Z)}}))
    L.save_blend(ASSET); print("built cage", len(P))

elif WHICH == "door":
    ASSET = "OBJ-070_PuertaCorrediza"; col = L.collection(ASSET)
    # Paso 3 × 3.5, marco fuera del paso (59.3). Hojas con chapa, nervios, junta central y zócalo de contacto; riel
    # superior con carros de dos ruedas y cubierta de servicio que respira; motor, sensor y control con su cableado.
    #
    # OJO (contrato Unity): "leaf_0"/"leaf_1" conservan nombre, origen en su base (±0.75, 0, 0.02) y 1.5 × 0.12 × 3.45.
    # La pieza más saliente de la hoja llega a y = ∓0.070 → cabe en el BoxCollider de 0.14 de HeroDressing.cs.

    ft = shell("frame_top", (3.6, 0.5, 0.3), (0, 0, 3.5), M['steel_paint'], pivot='bottom', cham=0.005)
    fts = seam("frame_top_seam", 3.5, (0, -0.252, 3.62), M['steel_bare'], axis='X')
    ftb = L.bolt_row("frame_top_bolt", 0.008, (-1.2, -0.258, 3.56), (1.2, 0, 0), 3, col, axis='Y', mat=M['steel_bare'])
    grp([ft, fts, ftb], "frame_top")
    for i, x in enumerate((-1.65, 1.65)):
        fp = shell(f"frame_post_{x:+.1f}", (0.3, 0.5, 3.5), (x, 0, 0), M['steel_paint'], pivot='bottom', cham=0.005)
        fpb = L.bolt_row(f"frame_post_bolt{i}", 0.008, (x, -0.258, 0.6), (0, 0, 1.6), 2, col, axis='Y', mat=M['steel_bare'])
        grp([fp, fpb], f"frame_post_{x:+.1f}")

    # cubierta del riel: registro para servicio y rejilla por donde respira la bahía del motor (59.3)
    rc = shell("rail_cover", (3.6, 0.2, 0.15), (0, 0, 3.8), M['steel_dark'], pivot='bottom', cham=0.004)
    rcv = L.vent("rail_vent", (0.5, 0.06, 0.1), (1.2, -0.102, 3.875), col, slats=2, rot=FRONT, mat_frame=M['steel_dark'], mat_slat=M['steel_dark'])
    rcb = L.bolt_row("rail_cover_bolt", 0.006, (-1.0, -0.104, 3.87), (1.0, 0, 0), 3, col, axis='Y', mat=M['steel_bare'])
    # el riel asoma por el intradós del dintel: es lo que se ve desde abajo con la puerta abierta
    rail = plate("rail", (3.5, 0.10, 0.04), (0, 0, 3.49), M['steel_bare'], bev=0.004)
    stops = [slab(f"rail_stop{i}", (0.04, 0.10, 0.06), (sx * 1.72, 0, 3.52), M['steel_dark']) for i, sx in enumerate((-1, 1))]
    grp([rc, rcv, rcb, rail] + stops, "rail_cover")

    for i, sx in enumerate((-1, 1)):
        # la caja de la hoja va PRIMERA: L.join conserva su origen, que es el que usa el BoxCollider de Unity
        leaf = L.box(f"leaf_{i}", (1.5, 0.12, 3.45), (sx * 0.75, 0, 0.02), col, pivot='bottom', bevel=0.006, segs=2)
        L.assign(leaf, M['paint_ind'])
        # el relieve de la hoja se queda dentro de los 0.14 de espesor del BoxCollider: nada pasa de y = ∓0.070
        lribs = ribs(f"leaf{i}_rib", 2.6, (1.4, 0.012, 0.06), (sx * 0.75, -0.0645, 1.75), M['steel_paint'], count=3, axis='Z')
        lseam = seam(f"leaf{i}_seam", 3.3, (sx * 0.75, -0.0615, 1.75), M['steel_bare'], axis='Z')
        kick = plate(f"leaf{i}_kick", (1.44, 0.012, 0.35), (sx * 0.75, -0.0645, 0.22), M['hazard'], bev=0.003)
        kbolt = L.bolt_row(f"leaf{i}_kick_bolt", 0.006, (sx * 0.75 - 0.6, -0.0685, 0.22), (0.6, 0, 0), 3, col, axis='Y', mat=M['steel_bare'])
        grp([leaf, lribs, lseam, kick, kbolt], f"leaf_{i}")
        # junta central de goma: el borde que se come el roce (59.3 "desgaste en borde de contacto")
        add(L.box(f"edge_seal_{i}", (0.03, 0.14, 3.4), (sx * 0.015, 0, 0.05), col, pivot='bottom', bevel=0.003, segs=1), M['rubber'])
        # carro de dos ruedas sobre el riel: el eje va en Y porque el riel corre en X
        car = plate(f"wheels_{i}", (1.3, 0.08, 0.1), (sx * 0.75, 0, 3.47), M['steel_bare'], pivot='bottom', bev=0.004)
        w0 = rod(f"wheel_{i}a", 0.05, 0.04, (sx * 0.75 - 0.45, 0, 3.55), M['steel_dark'], axis='Y', verts=8)
        w1 = rod(f"wheel_{i}b", 0.05, 0.04, (sx * 0.75 + 0.45, 0, 3.55), M['steel_dark'], axis='Y', verts=8)
        ax = rod(f"wheel_axle_{i}", 0.012, 0.98, (sx * 0.75, 0, 3.55), M['steel_bare'], axis='X', verts=6)
        grp([car, w0, w1, ax], f"wheels_{i}")

    mt = shell("motor", (0.4, 0.3, 0.25), (1.3, 0.35, 3.55), M['steel_dark'], pivot='bottom', cham=0.004)
    # la rejilla va en el testero del motor (+X): por la cara -Y respiraría contra el dintel, y por +Y se saldría del bulto
    mtv = L.vent("motor_vent", (0.20, 0.06, 0.16), (1.502, 0.35, 3.68), col, slats=2, rot=RIGHT, mat_frame=M['steel_dark'], mat_slat=M['steel_dark'])
    mtb = L.bolt_row("motor_bolt", 0.006, (1.15, 0.502, 3.57), (0.15, 0, 0), 3, col, axis='Y', mat=M['steel_bare'])
    sh = rod("motor_shaft", 0.018, 0.12, (1.1, 0.35, 3.67), M['steel_bare'], axis='X', verts=8)
    pu = rod("motor_pulley", 0.05, 0.03, (1.03, 0.35, 3.67), M['steel_dark'], axis='X', verts=10)
    grp([mt, mtv, mtb, sh, pu], "motor")

    # sensor de obstrucción en la jamba izquierda, mirando de lado a lado del paso: montado en material, no flotando
    # en mitad del hueco, y fuera del recorrido de la hoja abierta (leaf_0 llega a x = -1.5).
    sn = plate("sensor", (0.05, 0.08, 0.14), (-1.475, -0.20, 1.2), M['polymer_dark'], bev=0.002)
    sl = slab("sensor_led", (0.005, 0.02, 0.02), (-1.448, -0.20, 1.25), M['emitter'])
    sc = rod("sensor_lens", 0.015, 0.012, (-1.445, -0.20, 1.16), M['glass'], axis='X', verts=6)
    grp([sn, sl, sc], "sensor")

    cp = shell("control_panel", (0.25, 0.08, 0.35), (1.9, -0.28, 1.2), M['polymer_dark'], pivot='bottom', cham=0.004)
    cs = slab("control_screen", (0.16, 0.006, 0.1), (1.9, -0.322, 1.45), M['screen'])
    cb = [rod(f"control_btn{i}", 0.016, 0.012, (1.84 + i * 0.06, -0.322, 1.3), M['rubber'], axis='Y', verts=6) for i in range(3)]
    cbb = L.bolt_row("control_bolt", 0.005, (1.9, -0.322, 1.24), (0, 0, 0.28), 2, col, axis='Y', mat=M['steel_bare'])
    grp([cp, cs] + cb + [cbb], "control_panel")

    mc = L.tube("motor_cable", [(1.5, 0.35, 3.6), (1.8, 0.32, 3.5), (1.95, 0.2, 2.6), (1.95, -0.1, 1.7)], 0.012, col, verts=8)
    L.assign(mc, M['wire'])
    cd = rod("cable_conduit", 0.022, 0.5, (1.95, -0.1, 1.45), M['steel_dark'], verts=8)
    cc = L.tube("control_cable", [(1.95, -0.15, 1.45), (1.93, -0.24, 1.3), (1.9, -0.26, 1.2)], 0.008, col, verts=8)
    L.assign(cc, M['wire'])
    grp([mc, cd, cc], "cables")

    for o in P: L.apply_all(o); L.smooth(o, 40); L.uv_project(o, 0.008)
    arm = L.armature("Armature_Door", [("root", (0, 0, 0), (0, 0, 0.2), None), ("leaf_0", (-0.75, 0, 0), (-0.75, 0, 1), "root"), ("leaf_1", (0.75, 0, 0), (0.75, 0, 1), "root")], col)
    for o in P: L.bind_rigid(o, arm, "leaf_0" if o.name in ("leaf_0", "edge_seal_0", "wheels_0") else "leaf_1" if o.name in ("leaf_1", "edge_seal_1", "wheels_1") else "root")
    Z = (0, 0, 0)
    # 2.0 s con aceleración/freno: cada hoja se desplaza 1.5 m hacia su cavidad lateral
    L.push_nla(arm, L.action(arm, "Door_Open", 60, loop=False, poses={1: {"leaf_0": ((0, 0, 0), Z), "leaf_1": ((0, 0, 0), Z)}, 60: {"leaf_0": ((0, 0, 0), (-1.5, 0, 0)), "leaf_1": ((0, 0, 0), (1.5, 0, 0))}}))
    L.save_blend(ASSET); print("built door", len(P))

elif WHICH == "terminal":
    ASSET = "OBJ-059_Terminal"; col = L.collection(ASSET)
    # Envolvente 0.6 × 0.45 × 1.2 (59.4). Base, pedestal con nervios, carcasa con juntas, bisel hundido, panel posterior
    # atornillado con rejilla, bandeja de teclas con volumen y UN control principal. La carcasa va inclinada -12°.
    TILT = (RAD(-12), 0, 0)
    CAS, BCK, SCR = (0, 0, 0.76), (0, 0.22, 0.8), (0, -0.235, 0.85)   # pivotes de carcasa / panel posterior / pantalla

    def tilt_at(origin, local):
        """Punto sobre una pieza inclinada -12°: `local` en el marco de la pieza, `origin` su pivote.
        Sin esto, el bisel, la tornillería y la rejilla se colocarían en el plano del mundo y flotarían fuera de la carcasa."""
        p = Vector(local); p.rotate(Euler(TILT, 'XYZ'))
        return (origin[0] + p.x, origin[1] + p.y, origin[2] + p.z)

    bs = shell("base", (0.5, 0.4, 0.06), (0, 0, 0), M['steel_dark'], pivot='bottom', cham=0.004)
    bfeet = [slab(f"base_foot{i}", (0.05, 0.05, 0.012), (sx * 0.2, sy * 0.15, 0.0), M['rubber'], pivot='bottom')
             for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1)))]
    grp([bs] + bfeet, "base")

    pd = shell("pedestal", (0.2, 0.2, 0.7), (0, 0.05, 0.06), M['steel_paint'], pivot='bottom', cham=0.004)
    pdr = ribs("pedestal_rib", 0.5, (0.025, 0.02, 0.6), (0, -0.052, 0.41), M['steel_paint'], count=2, axis='X')
    pdb = L.bolt_row("pedestal_bolt", 0.006, (-0.06, -0.052, 0.1), (0.12, 0, 0), 2, col, axis='Y', mat=M['steel_bare'])
    grp([pd, pdr, pdb], "pedestal")

    cs = L.box("casing", (0.6, 0.45, 0.45), (0, 0, 0.76), col, pivot='bottom', rot=TILT, bevel=0.02, segs=3)
    L.assign(cs, M['polymer_dark'])
    csm = [seam(f"casing_seam{i}", 0.42, tilt_at(CAS, (sx * 0.2975, 0, 0.225)), M['steel_dark'], axis='Y', rot=TILT) for i, sx in enumerate((-1, 1))]
    # la tapa superior es desmontable: junta a lo ancho y su tornillería (59.4 "carcasa con panel posterior... y tornillos")
    cst = seam("casing_top_seam", 0.5, tilt_at(CAS, (0, 0.0, 0.448)), M['steel_dark'], axis='X', rot=TILT)
    cstb = L.bolt_row("casing_top_bolt", 0.005, tilt_at(CAS, (-0.2, 0.10, 0.452)), (0.2, 0, 0), 3, col, axis='Z', mat=M['steel_bare'])
    grp([cs] + csm + [cst, cstb], "casing")

    # bisel hundido alrededor de la pantalla: el reborde da la sombra, el vidrio no tapa el texto (59.4)
    add(sunk("bezel", (0.52, 0.03, 0.36), tilt_at(SCR, (0, -0.005, 0.15)), M['polymer_dark'], depth=0.018, rot=TILT, border=0.018))
    add(L.box("screen", (0.46, 0.006, 0.3), SCR, col, pivot='bottom', rot=TILT), M['screen'])
    add(L.box("screen_glass", (0.47, 0.003, 0.31), (0, -0.245, 0.85), col, pivot='bottom', rot=TILT), M['glass'])

    bp = shell("back_panel", (0.5, 0.02, 0.36), BCK, M['steel_paint'], pivot='bottom', rot=TILT, cham=0.003)
    bpb = L.bolt_row("back_bolt", 0.005, tilt_at(BCK, (-0.22, 0.013, 0.05)), (0.22, 0, 0), 3, col, axis='Y', mat=M['steel_bare'])
    bps = seam("back_seam", 0.46, tilt_at(BCK, (0, 0.013, 0.31)), M['steel_dark'], axis='X', rot=TILT)
    grp([bp, bpb, bps], "back_panel")
    # por aquí respira: la ventilación cercana es parte de la firma sonora del terminal (59.4).
    # rot (+12°, 0, 180°) deja la rejilla mirando exactamente a la normal del panel inclinado.
    add(L.vent("vents", (0.22, 0.05, 0.16), tilt_at(BCK, (0.12, 0.012, 0.19)), col, slats=3, rot=(RAD(12), 0, math.pi), mat_frame=M['steel_dark'], mat_slat=M['steel_dark']))

    kt = shell("key_tray", (0.5, 0.22, 0.04), (0, -0.28, 0.72), M['polymer_dark'], pivot='bottom', cham=0.003)
    ktl = plate("key_lip", (0.5, 0.03, 0.03), (0, -0.383, 0.745), M['polymer_dark'], bev=0.002)
    grp([kt, ktl], "key_tray")
    # teclas con volumen y bisel de un segmento: se ven usadas de cerca sin pagar una carcasa por tecla
    # 3 × 10: la columna que queda libre a la derecha es la del control principal, que así no pisa ninguna tecla
    keys = [L.box(f"key{i}", (0.03, 0.03, 0.014), (-0.2 + (i % 10) * 0.035, -0.32 + (i // 10) * 0.04, 0.762), col, bevel=0.0018, segs=1) for i in range(30)]
    for k in keys: L.assign(k, M['polymer_ivory'])
    grp(keys, "keys")
    # UN control principal activa el documento; no veinte controles engañosos (59.4)
    mc = rod("main_control", 0.03, 0.02, (0.2, -0.28, 0.766), M['emitter'], verts=12)
    mcr = rod("main_control_ring", 0.042, 0.008, (0.2, -0.28, 0.762), M['steel_dark'], verts=10)
    grp([mc, mcr], "main_control")

    # tornillos del bisel: en las cuatro esquinas del marco, que es donde la carcasa se cierra contra el frente
    screws = [screw(f"screw{i}", 0.005, tilt_at(CAS, (-0.28 + (i % 2) * 0.56, -0.232, 0.05 + (i // 2) * 0.28)), M['steel_bare'], axis='Y') for i in range(4)]
    grp(screws, "screws")

    pc = L.tube("power_cable", [(0.05, 0.15, 0.1), (0.15, 0.26, 0.06), (0.28, 0.35, 0.02), (0.35, 0.4, 0.0)], 0.01, col, verts=8)
    L.assign(pc, M['wire'])
    pcr = rod("cable_relief", 0.02, 0.04, (0.05, 0.14, 0.11), M['rubber'], verts=8)
    rk = L.tube("rack_cable", [(-0.05, 0.16, 0.1), (-0.2, 0.3, 0.04), (-0.32, 0.38, 0.0)], 0.008, col, verts=8)
    L.assign(rk, M['wire'])
    grp([pc, pcr, rk], "cables")

    # franja sobre el bisel: placa NÉMESIS y pilotos de estado. Diferencian "antiguo apagado" de "activo EVA" sin
    # subir la emisión global de la pantalla (59.4).
    lb = plate("label", (0.14, 0.01, 0.04), tilt_at(CAS, (-0.18, -0.232, 0.41)), M['label'], rot=TILT, bev=0.002)
    leds = [slab(f"status_led{i}", (0.012, 0.006, 0.012), tilt_at(CAS, (0.18 + i * 0.03, -0.233, 0.41)), M['emitter'], rot=TILT) for i in range(3)]
    grp([lb] + leds, "label")

    for o in P: L.apply_all(o); L.smooth(o, 40); L.uv_project(o, 0.006)
    L.save_blend(ASSET); print("built terminal", len(P))

elif WHICH == "gurney":
    ASSET = "OBJ-043_Camilla"; col = L.collection(ASSET)
    # Envolvente 2 × 0.75 × 0.8 (59.5). Cuatro ruedas con HORQUILLA y pivote de giro, freno con pedal y varilla,
    # bastidor con nervios, colchón con hendidura, bordes y costuras, barandas con collarines y pestillo.
    castors = []
    for i, (x, y) in enumerate(((-0.85, -0.3), (0.85, -0.3), (-0.85, 0.3), (0.85, 0.3))):
        castors.append(rod(f"leg{i}", 0.02, 0.5, (x, y, 0.16), M['paint_med'], verts=10, pivot='bottom'))
        castors.append(rod(f"swivel{i}", 0.028, 0.05, (x, y, 0.135), M['steel_bare'], verts=8))
        castors.append(plate(f"fork{i}", (0.07, 0.035, 0.09), (x, y, 0.06), M['steel_bare'], pivot='bottom'))
        castors.append(slab(f"fork_cheek_a{i}", (0.012, 0.03, 0.07), (x - 0.033, y, 0.065), M['steel_bare']))
        castors.append(slab(f"fork_cheek_b{i}", (0.012, 0.03, 0.07), (x + 0.033, y, 0.065), M['steel_bare']))
        castors.append(rod(f"wheel{i}", 0.06, 0.035, (x, y, 0.06), M['rubber'], axis='X', verts=12))
        castors.append(rod(f"axle{i}", 0.008, 0.055, (x, y, 0.06), M['steel_bare'], axis='X', verts=6))
    # freno de pie: pedal rojo y varilla hasta la rueda que bloquea (59.5 "freno/metal por evento")
    # la varilla llega HASTA la rueda que bloquea (x = ±0.85); un pedal que no conecta con nada no es un freno
    for i, x in enumerate((0.72, -0.72)):
        castors.append(plate(f"brake_pedal{i}", (0.12, 0.06, 0.02), (x, -0.35, 0.1), M['plastic_red'], rot=(RAD(20), 0, 0)))
        castors.append(rod(f"brake_link{i}", 0.008, 0.28, (x, -0.33, 0.1), M['steel_bare'], axis='X', verts=6))
    grp(castors, "castors")

    fr = shell("frame", (2.0, 0.7, 0.05), (0, 0, 0.66), M['paint_med'], pivot='bottom', cham=0.004)
    frc = [plate(f"cross_{x:+.1f}", (0.04, 0.66, 0.04), (x, 0, 0.62), M['paint_med'], pivot='bottom') for x in (-0.5, 0.5)]
    frr = ribs("frame_rib", 1.4, (0.03, 0.6, 0.035), (0, 0, 0.645), M['paint_med'], count=2, axis='X')
    grp([fr] + frc + [frr], "frame")

    mat = L.box("mattress", (1.95, 0.68, 0.1), (0, 0, 0.71), col, pivot='bottom', bevel=0.03, segs=3); L.assign(mat, M['mattress'])
    cut = L.box("press_cut", (1.4, 0.4, 0.05), (0.1, 0, 0.79), col)
    m = mat.modifiers.new("Press", 'BOOLEAN'); m.operation = 'DIFFERENCE'; m.object = cut; L.apply_all(mat); bpy.data.objects.remove(cut)
    medge = [plate(f"mattress_edge{i}", (1.9, 0.05, 0.05), (0, sy * 0.32, 0.78), M['mattress']) for i, sy in enumerate((-1, 1))]
    mseam = [seam(f"mattress_seam{i}", 1.9, (0, sy * 0.28, 0.807), M['fabric'], axis='X', width=0.008, depth=0.006) for i, sy in enumerate((-1, 1))]
    grp([mat] + medge + mseam, "mattress")

    bl = L.box("blanket", (1.2, 0.72, 0.06), (-0.15, 0, 0.79), col, pivot='bottom', bevel=0.025, segs=3); L.assign(bl, M['blanket'])
    blf = ribs("blanket_fold", 0.5, (0.05, 0.7, 0.03), (-0.15, 0, 0.845), M['blanket'], count=2, axis='X')
    grp([bl, blf], "blanket")

    for sx in (-1, 1):
        rail = [rod(f"rail_{sx}_{k}", 0.012, 1.2, (0, sx * 0.36, 0.95 + k * 0.1), M['paint_med'], axis='X', verts=8) for k in range(3)]
        rail += [rod(f"railpost_{sx}_{k}", 0.012, 0.50, (-0.5 + k * 1.0, sx * 0.36, 0.66), M['paint_med'], verts=8, pivot='bottom') for k in range(2)]
        rail += [rod(f"railcollar_{sx}_{k}", 0.02, 0.03, (-0.5 + k * 1.0, sx * 0.36, 0.70), M['steel_bare'], verts=6) for k in range(2)]
        rail.append(slab(f"raillatch_{sx}", (0.05, 0.03, 0.03), (0.55, sx * 0.36, 1.0), M['steel_bare']))
        grp(rail, f"siderail_{sx}")

    iv = [rod("iv_pole", 0.012, 1.0, (-0.95, 0.3, 0.66), M['steel_bare'], verts=10, pivot='bottom'),
          slab("iv_hook", (0.06, 0.02, 0.02), (-0.92, 0.3, 1.64), M['steel_bare']),
          rod("iv_clamp", 0.022, 0.04, (-0.95, 0.3, 0.72), M['steel_dark'], verts=6),
          plate("iv_bag", (0.02, 0.1, 0.16), (-0.9, 0.3, 1.55), M['glass'], bev=0.004)]
    iv.append(L.tube("iv_tube", [(-0.9, 0.3, 1.47), (-0.78, 0.24, 1.2), (-0.56, 0.16, 0.95), (-0.4, 0.1, 0.85)], 0.004, col, verts=8))
    L.assign(iv[-1], M['glass'])
    grp(iv, "iv_stand")

    # topes de esquina (el bastidor golpea puertas y camas) y asas de empuje pulidas por la mano
    extra = [rod(f"bumper{i}", 0.03, 0.05, (sx * 0.975, sy * 0.33, 0.685), M['rubber'], axis='X', verts=8)
             for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1)))]
    extra += [rod(f"push_handle{i}", 0.016, 0.22, (sx * 0.98, 0, 0.72), M['rubber'], axis='Y', verts=8) for i, sx in enumerate((-1, 1))]
    # balda bajo el bastidor: la botella se APOYA en ella y la correa la sujeta (59.5 "equipo añadido no atraviesa cama")
    extra.append(plate("shelf", (0.5, 0.4, 0.02), (-0.3, 0, 0.42), M['steel_paint']))
    extra += [slab(f"shelf_bracket{i}", (0.03, 0.03, 0.24), (-0.3 + sx * 0.22, 0, 0.54), M['steel_bare']) for i, sx in enumerate((-1, 1))]
    extra += [rod("o2_bottle", 0.055, 0.34, (-0.42, -0.14, 0.43), M['steel_paint'], verts=12, pivot='bottom'),
              rod("o2_neck", 0.022, 0.06, (-0.42, -0.14, 0.78), M['steel_bare'], verts=8),
              slab("o2_strap", (0.13, 0.02, 0.04), (-0.42, -0.14, 0.62), M['fabric'])]
    extra.append(plate("gurney_label", (0.12, 0.01, 0.04), (0.6, -0.352, 0.69), M['label'], bev=0.002))
    grp(extra, "fittings")

    for o in P: L.apply_all(o); L.smooth(o, 40); L.uv_project(o, 0.008)
    L.save_blend(ASSET); print("built gurney", len(P))

elif WHICH == "cart":
    ASSET = "OBJ-029_Carro"; col = L.collection(ASSET)
    # Envolvente 1 × 0.6 × 0.9 (59.6). Se EMPUJA físicamente (CartFactory: BoxCollider 1.0 × 0.9 × 0.6), así que la
    # rueda tiene que leerse como rueda que gira: neumático, buje, tapacubos, radios, tuerca de eje y horquilla con pivote.
    # El asset no crece de 1.06 × 0.6 × 0.92 para no desbordar ese collider.
    pf = L.box("platform", (1.0, 0.6, 0.04), (0, 0, 0.16), col, pivot='bottom', bevel=0.006, segs=2); L.assign(pf, M['steel_bare'])
    pfp = slab("platform_paint", (0.96, 0.56, 0.005), (0, 0, 0.2), M['paint_ind'], pivot='bottom')
    pfr = ribs("platform_rib", 0.8, (0.04, 0.5, 0.03), (0, 0, 0.145), M['steel_dark'], count=3, axis='X')
    pfs = [plate(f"side_rail_{x:+.1f}", (0.05, 0.6, 0.05), (x, 0, 0.12), M['steel_dark'], pivot='bottom') for x in (-0.44, 0.44)]
    grp([pf, pfp, pfr] + pfs, "platform")

    # Rueda de radio 0.072 centrada en z = 0.072: apoya en el suelo y deja 0.016 libres hasta la plataforma (z = 0.16)
    # para que la pletina de la horquilla quepa ENCIMA del neumático en vez de atravesarlo. Las mejillas van por fuera
    # del ancho del neumático (y ± 0.032 contra 0.025 de media anchura), así que tampoco lo cortan.
    wheels = []
    for x in (-0.45, 0.45):
        for y in (-0.25, 0.25):
            tag = f"{x:+.2f}_{y:+.2f}"
            wheels.append(rod(f"tyre_{tag}", 0.072, 0.05, (x, y, 0.072), M['rubber'], axis='Y', verts=16))
            wheels.append(rod(f"hub_{tag}", 0.032, 0.056, (x, y, 0.072), M['steel_bare'], axis='Y', verts=10))
            wheels.append(rod(f"hubcap_{tag}", 0.016, 0.062, (x, y, 0.072), M['steel_dark'], axis='Y', verts=8))
            # tres radios en el plano de la rueda: es lo que delata que gira cuando el carro rueda
            for k in range(3):
                wheels.append(slab(f"spoke_{tag}_{k}", (0.012, 0.03, 0.115), (x, y, 0.072), M['steel_bare'], rot=(0, RAD(60 * k), 0)))
            wheels.append(screw(f"axle_nut_{tag}", 0.012, (x, y + 0.035, 0.072), M['steel_bare'], axis='Y'))
            wheels.append(plate(f"fork_top_{tag}", (0.08, 0.10, 0.035), (x, y, 0.163), M['steel_dark']))
            for k, sy in enumerate((-1, 1)):
                wheels.append(slab(f"fork_cheek_{tag}_{k}", (0.05, 0.012, 0.08), (x, y + sy * 0.032, 0.11), M['steel_dark']))
            wheels.append(rod(f"swivel_{tag}", 0.024, 0.04, (x, y, 0.185), M['steel_bare'], verts=8))
    grp(wheels, "wheels")

    chassis = [plate(f"chassis_{x:+.1f}", (0.06, 0.56, 0.05), (x, 0, 0.125), M['steel_dark']) for x in (-0.4, 0.4)]
    chassis += [plate(f"chassis_cross_{y:+.2f}", (0.86, 0.05, 0.04), (0, y, 0.125), M['steel_dark']) for y in (-0.22, 0.22)]
    grp(chassis, "chassis")

    handle = []
    for sx in (-1, 1):
        handle.append(rod(f"handle_post_{sx}", 0.015, 0.7, (-0.46, sx * 0.25, 0.2), M['steel_paint'], verts=10, pivot='bottom'))
        handle.append(slab(f"handle_gusset_{sx}", (0.05, 0.03, 0.09), (-0.44, sx * 0.25, 0.24), M['steel_paint']))
        # el asa se atornilla a la plataforma: es la unión que aguanta todo el empuje del jugador
        handle.append(L.bolt_row(f"handle_bolt_{sx}", 0.005, (-0.49, sx * 0.25, 0.205), (0.06, 0, 0), 2, col, axis='Z', mat=M['steel_bare']))
    handle.append(rod("handle_bar", 0.016, 0.54, (-0.46, 0, 0.9), M['steel_bare'], axis='Y', verts=12))
    # el agarre es donde la pintura se pule: el material lo resuelve, aquí basta con que la pieza exista
    handle.append(rod("handle_grip", 0.019, 0.3, (-0.46, 0, 0.9), M['rubber'], axis='Y', verts=12))
    handle += [rod(f"grip_cap_{i}", 0.021, 0.014, (-0.46, sx * 0.157, 0.9), M['rubber'], axis='Y', verts=8) for i, sx in enumerate((-1, 1))]
    grp(handle, "handle")

    cr = shell("crate_load", (0.5, 0.4, 0.4), (0.15, 0, 0.2), M['steel_paint'], pivot='bottom', cham=0.004)
    crr = ribs("crate_rib", 0.3, (0.03, 0.42, 0.28), (0.15, 0, 0.4), M['steel_paint'], count=2, axis='X')
    crl = plate("crate_lid", (0.48, 0.38, 0.02), (0.15, 0, 0.6), M['steel_dark'])
    crc = [slab(f"crate_clasp{i}", (0.04, 0.02, 0.06), (0.15 + sx * 0.18, -0.2, 0.58), M['steel_bare']) for i, sx in enumerate((-1, 1))]
    grp([cr, crr, crl] + crc, "crate_load")

    st = slab("strap", (0.52, 0.03, 0.42), (0.15, 0, 0.19), M['fabric'], pivot='bottom')
    stb = plate("strap_buckle", (0.06, 0.05, 0.04), (0.15, -0.21, 0.4), M['steel_bare'], bev=0.003)
    grp([st, stb], "strap")

    fit = [rod(f"cart_bumper{i}", 0.028, 0.04, (sx * 0.5, sy * 0.26, 0.17), M['rubber'], axis='X', verts=8)
           for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1)))]
    fit += [rod(f"tie_ring{i}", 0.022, 0.012, (sx * 0.42, 0, 0.205), M['steel_bare'], verts=8) for i, sx in enumerate((-1, 1))]
    # la placa va en el flanco de la carga, dentro de los 0.6 de ancho que admite el collider del carro
    fit.append(plate("cart_label", (0.1, 0.01, 0.035), (0.15, -0.204, 0.35), M['label'], bev=0.002))
    grp(fit, "fittings")

    for o in P: L.apply_all(o); L.smooth(o, 40); L.uv_project(o, 0.006)
    L.save_blend(ASSET); print("built cart", len(P))
