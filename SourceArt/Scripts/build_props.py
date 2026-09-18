# Seis assets focales (59): OBJ-001 criocámara, OBJ-041 jaula, OBJ-070 puerta corrediza, OBJ-059 terminal, OBJ-043 camilla, OBJ-029 carro.
# Piezas con espesor y función, pivotes en ejes de movimiento, materiales diferenciados (metal pintado / descubierto / goma / vidrio / pantalla).
import bpy, math, importlib, sys
sys.path.insert(0, r"C:/Users/HP/Documents/GitHub/proyectos-unity/SourceArt/Scripts")
import esn_lib as L; importlib.reload(L)

WHICH = globals().get("WHICH", "cryo")
L.reset_scene()
M = L.std_mats()
M['paint_med'] = L.material("M_PaintMedical", (0.78, 0.8, 0.78), 0.45, 0.0, wear=0.3, wear_color=(0.5, 0.5, 0.48), bump=0.12)
M['paint_ind'] = L.material("M_PaintIndustrial", (0.55, 0.5, 0.2), 0.55, 0.0, wear=0.4, wear_color=(0.45, 0.35, 0.25), bump=0.15)
M['foam'] = L.material("M_Foam", (0.16, 0.18, 0.2), 0.8, 0.0, bump=0.25, scale=18)
M['mattress'] = L.material("M_Mattress", (0.55, 0.6, 0.62), 0.8, 0.0, bump=0.2, scale=25)
M['blanket'] = L.material("M_Blanket", (0.45, 0.5, 0.42), 0.9, 0.0, bump=0.4, scale=40)
M['wire'] = L.material("M_Wire", (0.3, 0.3, 0.32), 0.5, 1.0, wear=0.3, wear_color=(0.4, 0.28, 0.2))
P = []


def add(o, m):
    L.assign(o, m); P.append(o); return o


if WHICH == "cryo":
    ASSET = "OBJ-001_Criocamara"; col = L.collection(ASSET)
    # base redondeada con patas, registros y juntas; lecho acolchado con hendidura; tapa marco+vidrio con bisagras; pantalla; térmico
    base = add(L.box("base", (2.4, 1.1, 0.5), (0, 0, 0.12), col, pivot='bottom', bevel=0.06, segs=4), M['paint_med'])
    for i, (x, y) in enumerate(((-1.05, -0.45), (1.05, -0.45), (-1.05, 0.45), (1.05, 0.45))):
        add(L.box(f"foot{i}", (0.16, 0.12, 0.12), (x, y, 0.0), col, pivot='bottom', bevel=0.01), M['rubber'])
    for i in range(3):
        add(L.box(f"service_panel{i}", (0.4, 0.02, 0.22), (-0.8 + i * 0.8, -0.56, 0.22), col, pivot='bottom', bevel=0.004), M['steel_paint'])
    add(L.box("bed_frame", (2.2, 0.9, 0.06), (0, 0, 0.62), col, pivot='bottom', bevel=0.01), M['steel_bare'])
    bed = add(L.box("bed_pad", (2.05, 0.75, 0.12), (0, 0, 0.68), col, pivot='bottom', bevel=0.04, segs=4), M['foam'])
    cut = L.box("body_cut", (1.7, 0.45, 0.06), (0.05, 0, 0.77), col)
    m = bed.modifiers.new("Body", 'BOOLEAN'); m.operation = 'DIFFERENCE'; m.object = cut; L.apply_all(bed); bpy.data.objects.remove(cut)
    add(L.box("pillow", (0.4, 0.5, 0.08), (0.85, 0, 0.8), col, pivot='bottom', bevel=0.03, segs=3), M['foam'])
    add(L.box("gasket", (2.3, 1.0, 0.03), (0, 0, 0.62), col, pivot='bottom', bevel=0.01), M['rubber'])
    # tapa: marco con espesor, vidrio curvo (esfera escalada recortada), bisagras en el lado trasero (pivote en eje)
    lid = L.box("lid_frame", (2.3, 1.0, 0.08), (0, 0, 0.65), col, pivot='bottom', bevel=0.02, segs=3)
    hole = L.box("lid_hole", (2.1, 0.8, 0.2), (0, 0, 0.6), col)
    m = lid.modifiers.new("Hole", 'BOOLEAN'); m.operation = 'DIFFERENCE'; m.object = hole; L.apply_all(lid); bpy.data.objects.remove(hole)
    add(lid, M['paint_med'])
    glass = L.sphere("lid_glass", 1.0, (0, 0, 0.66), col, segs=48, rings=24, scale=(1.08, 0.42, 0.34))
    cutb = L.box("glass_cut", (3, 2, 1.0), (0, 0, 0.15), col)
    m = glass.modifiers.new("Half", 'BOOLEAN'); m.operation = 'DIFFERENCE'; m.object = cutb; L.apply_all(glass); bpy.data.objects.remove(cutb)
    add(glass, M['glass'])
    for i, x in enumerate((-0.8, 0.8)):
        add(L.cyl(f"hinge{i}", 0.03, 0.14, (x, 0.5, 0.67), col, axis='X'), M['steel_bare'])
    for i, x in enumerate((-0.7, 0.7)):
        add(L.box(f"latch{i}", (0.08, 0.05, 0.06), (x, -0.5, 0.66), col, bevel=0.006), M['steel_dark'])
    # pantalla con montaje, botones y cable; tubos con aislante al manifold
    add(L.box("screen_mount", (0.06, 0.08, 0.35), (1.2, -0.3, 0.6), col, pivot='bottom'), M['steel_dark'])
    add(L.box("screen_housing", (0.04, 0.3, 0.2), (1.24, -0.3, 0.98), col, bevel=0.01), M['polymer_dark'])
    add(L.box("screen", (0.006, 0.26, 0.16), (1.263, -0.3, 0.98), col), M['screen'])
    for i in range(3): add(L.cyl(f"button{i}", 0.012, 0.01, (1.265, -0.42 + i * 0.03, 0.86), col, axis='X', verts=12), M['rubber'])
    add(L.tube("screen_cable", [(1.22, -0.3, 0.88), (1.18, -0.35, 0.7), (1.1, -0.4, 0.5)], 0.008, col), M['rubber'])
    add(L.box("manifold", (0.3, 0.16, 0.14), (-1.15, 0.3, 0.3), col, bevel=0.01), M['steel_dark'])
    for i in range(3):
        add(L.tube(f"pipe{i}", [(-1.3, 0.2 + i * 0.08, 0.3), (-1.45, 0.2 + i * 0.08, 0.3), (-1.5, 0.2 + i * 0.08, 0.1), (-1.5, 0.2 + i * 0.08, 0.0)], 0.02, col), M['rubber'])
        add(L.cyl(f"pipe_conn{i}", 0.028, 0.03, (-1.31, 0.2 + i * 0.08, 0.3), col, axis='X', verts=12), M['copper'])
    for o in P: L.apply_all(o); L.smooth(o, 40); L.uv_project(o, 0.01)
    # rig: tapa sobre bisagra trasera (eje X en y=0.5, z=0.67), seguros
    arm = L.armature("Armature_Cryo", [("root", (0, 0, 0), (0, 0, 0.2), None), ("lid", (0, 0.5, 0.67), (0, -0.5, 0.67), "root"), ("latch_L", (-0.7, -0.5, 0.66), (-0.7, -0.5, 0.72), "root"), ("latch_R", (0.7, -0.5, 0.66), (0.7, -0.5, 0.72), "root")], col)
    for o in P:
        bone = "lid" if o.name in ("lid_frame", "lid_glass", "hinge0", "hinge1") else "latch_L" if o.name == "latch0" else "latch_R" if o.name == "latch1" else "root"
        L.bind_rigid(o, arm, bone)
    Z = (0, 0, 0)
    # OBJ-001: seguro libera → junta despega → tapa abre (2.4 s)
    L.push_nla(arm, L.action(arm, "Cryo_Open", 72, loop=False, poses={1: {"lid": ((0, 0, 0), Z), "latch_L": ((0, 0, 0), Z), "latch_R": ((0, 0, 0), Z)}, 12: {"latch_L": ((0, 60, 0), Z), "latch_R": ((0, -60, 0), Z)}, 22: {"lid": ((-4, 0, 0), Z)}, 72: {"lid": ((-70, 0, 0), Z)}}))
    L.push_nla(arm, L.action(arm, "Cryo_Closed", 2, loop=False, poses={1: {"lid": ((0, 0, 0), Z)}}))
    L.save_blend(ASSET); print("built cryo", len(P))

elif WHICH == "cage":
    ASSET = "OBJ-041_Jaula"; col = L.collection(ASSET)
    W, D, H = 2.2, 1.5, 2.4
    add(L.box("floor_grate", (W, D, 0.05), (0, 0, 0.05), col, pivot='bottom'), M['steel_bare'])
    add(L.box("drain", (0.25, 0.25, 0.02), (0.6, 0.4, 0.1), col), M['steel_dark'])
    for x in (-W / 2, W / 2):
        for y in (-D / 2, D / 2):
            add(L.box(f"post_{x:.1f}_{y:.1f}", (0.06, 0.06, H), (x, y, 0.0), col, pivot='bottom', bevel=0.006), M['steel_paint'])
            add(L.box(f"anchor_{x:.1f}_{y:.1f}", (0.14, 0.14, 0.02), (x, y, 0.0), col, pivot='bottom'), M['steel_dark'])
    for z in (0.35, H - 0.05):
        add(L.box(f"rail_front_{z:.1f}", (W, 0.05, 0.05), (0, -D / 2, z), col), M['steel_paint'])
        add(L.box(f"rail_back_{z:.1f}", (W, 0.05, 0.05), (0, D / 2, z), col), M['steel_paint'])
        add(L.box(f"rail_L_{z:.1f}", (0.05, D, 0.05), (-W / 2, 0, z), col), M['steel_paint'])
        add(L.box(f"rail_R_{z:.1f}", (0.05, D, 0.05), (W / 2, 0, z), col), M['steel_paint'])
    # barras separadas ≥ 12 cm (lectura del sujeto sin moiré); paño sólido trasero
    bars = []
    for i in range(1, 16):
        bars.append(L.cyl(f"bar_f{i}", 0.012, H - 0.45, (-W / 2 + i * W / 16, -D / 2, 0.4), col, pivot='bottom', verts=10))
    for i in range(1, 11):
        bars.append(L.cyl(f"bar_l{i}", 0.012, H - 0.45, (-W / 2, -D / 2 + i * D / 11, 0.4), col, pivot='bottom', verts=10))
        bars.append(L.cyl(f"bar_r{i}", 0.012, H - 0.45, (W / 2, -D / 2 + i * D / 11, 0.4), col, pivot='bottom', verts=10))
    for b in bars: L.assign(b, M['steel_paint'])
    P.append(L.join(bars, "bars"))
    add(L.box("back_panel", (W - 0.1, 0.03, H - 0.45), (0, D / 2, 0.4), col, pivot='bottom'), M['steel_paint'])
    # puerta con espesor sobre bisagras (pivote en poste izquierdo frontal) y cierre independiente
    door = L.box("door_frame", (0.8, 0.05, H - 0.5), (-W / 2 + 0.45, -D / 2 - 0.05, 0.42), col, pivot='bottom', bevel=0.006)
    dbars = [L.cyl(f"dbar{i}", 0.011, H - 0.6, (-W / 2 + 0.1 + i * 0.13, -D / 2 - 0.05, 0.46), col, pivot='bottom', verts=10) for i in range(1, 6)]
    for b in dbars: L.assign(b, M['steel_paint'])
    add(L.join([door] + dbars, "door"), M['steel_paint'])
    for z in (0.7, 1.9): add(L.cyl(f"hinge_{z}", 0.025, 0.1, (-W / 2 + 0.06, -D / 2 - 0.05, z), col, verts=12), M['steel_bare'])
    add(L.box("lock_box", (0.3, 0.15, 0.2), (-W / 2 + 0.95, -D / 2 - 0.09, 1.1), col, bevel=0.01), M['steel_dark'])
    add(L.box("lock_bolt", (0.12, 0.03, 0.03), (-W / 2 + 0.82, -D / 2 - 0.02, 1.1), col), M['steel_bare'])
    add(L.box("lock_light", (0.02, 0.01, 0.02), (-W / 2 + 0.95, -D / 2 - 0.17, 1.15), col), M['emitter'])
    add(L.box("plate", (0.2, 0.01, 0.1), (0.5, -D / 2 - 0.04, 1.6), col), M['ceramic'])
    add(L.tube("feed_tube", [(0.9, D / 2, 1.2), (1.2, D / 2 + 0.2, 1.3), (1.4, D / 2 + 0.3, 1.0)], 0.015, col), M['rubber'])
    for o in P: L.apply_all(o); L.smooth(o, 40); L.uv_project(o, 0.008)
    arm = L.armature("Armature_Cage", [("root", (0, 0, 0), (0, 0, 0.2), None), ("door", (-W / 2 + 0.06, -D / 2 - 0.05, 0.4), (-W / 2 + 0.06, -D / 2 - 0.05, 2.3), "root"), ("bolt", (-W / 2 + 0.82, -D / 2 - 0.02, 1.1), (-W / 2 + 0.82, -D / 2 - 0.02, 1.2), "root")], col)
    for o in P: L.bind_rigid(o, arm, "door" if o.name in ("door", "hinge_0.7", "hinge_1.9") else "bolt" if o.name == "lock_bolt" else "root")
    Z = (0, 0, 0)
    L.push_nla(arm, L.action(arm, "Cage_Open", 60, loop=False, poses={1: {"bolt": ((0, 0, 0), Z), "door": ((0, 0, 0), Z)}, 15: {"bolt": ((0, 0, 0), (0.1, 0, 0))}, 60: {"door": ((0, 0, -95), Z)}}))
    L.save_blend(ASSET); print("built cage", len(P))

elif WHICH == "door":
    ASSET = "OBJ-070_PuertaCorrediza"; col = L.collection(ASSET)
    # paso 3 × 3.5; marco fuera del paso; dos hojas con chapa, nervios, junta central; riel superior cubierto; motor/sensor/control
    add(L.box("frame_top", (3.6, 0.5, 0.3), (0, 0, 3.5), col, pivot='bottom', bevel=0.02), M['steel_paint'])
    for x in (-1.65, 1.65): add(L.box(f"frame_post_{x:+.1f}", (0.3, 0.5, 3.5), (x, 0, 0), col, pivot='bottom', bevel=0.02), M['steel_paint'])
    add(L.box("rail_cover", (3.6, 0.2, 0.15), (0, 0, 3.8), col, pivot='bottom'), M['steel_dark'])
    for i, sx in enumerate((-1, 1)):
        leaf = L.box(f"leaf_{i}", (1.5, 0.12, 3.45), (sx * 0.75, 0, 0.02), col, pivot='bottom', bevel=0.01)
        ribs = [L.box(f"leaf{i}_rib{k}", (1.4, 0.02, 0.05), (sx * 0.75, -0.07, 0.4 + k * 0.6), col) for k in range(5)]
        for r in ribs: L.assign(r, M['steel_paint'])
        add(L.join([leaf] + ribs, f"leaf_{i}"), M['paint_ind'])
        add(L.box(f"edge_seal_{i}", (0.03, 0.14, 3.4), (sx * 0.015, 0, 0.05), col, pivot='bottom'), M['rubber'])
        add(L.box(f"wheels_{i}", (1.3, 0.08, 0.1), (sx * 0.75, 0, 3.47), col, pivot='bottom'), M['steel_bare'])
    add(L.box("motor", (0.4, 0.3, 0.25), (1.3, 0.35, 3.55), col, pivot='bottom', bevel=0.01), M['steel_dark'])
    add(L.box("sensor", (0.12, 0.05, 0.06), (0, -0.27, 3.3), col), M['polymer_dark'])
    add(L.box("sensor_led", (0.02, 0.005, 0.02), (0, -0.295, 3.3), col), M['emitter'])
    add(L.box("control_panel", (0.25, 0.08, 0.35), (1.9, -0.28, 1.2), col, pivot='bottom', bevel=0.006), M['polymer_dark'])
    add(L.tube("motor_cable", [(1.5, 0.35, 3.6), (1.9, 0.3, 3.4), (1.95, 0.0, 1.6)], 0.012, col), M['rubber'])
    for o in P: L.apply_all(o); L.smooth(o, 40); L.uv_project(o, 0.01)
    arm = L.armature("Armature_Door", [("root", (0, 0, 0), (0, 0, 0.2), None), ("leaf_0", (-0.75, 0, 0), (-0.75, 0, 1), "root"), ("leaf_1", (0.75, 0, 0), (0.75, 0, 1), "root")], col)
    for o in P: L.bind_rigid(o, arm, "leaf_0" if o.name in ("leaf_0", "edge_seal_0", "wheels_0") else "leaf_1" if o.name in ("leaf_1", "edge_seal_1", "wheels_1") else "root")
    Z = (0, 0, 0)
    # 2.0 s con aceleración/freno: cada hoja se desplaza 1.5 m hacia su cavidad lateral
    L.push_nla(arm, L.action(arm, "Door_Open", 60, loop=False, poses={1: {"leaf_0": ((0, 0, 0), Z), "leaf_1": ((0, 0, 0), Z)}, 60: {"leaf_0": ((0, 0, 0), (-1.5, 0, 0)), "leaf_1": ((0, 0, 0), (1.5, 0, 0))}}))
    L.save_blend(ASSET); print("built door", len(P))

elif WHICH == "terminal":
    ASSET = "OBJ-059_Terminal"; col = L.collection(ASSET)
    add(L.box("base", (0.5, 0.4, 0.06), (0, 0, 0), col, pivot='bottom', bevel=0.01), M['steel_dark'])
    add(L.box("pedestal", (0.2, 0.2, 0.7), (0, 0.05, 0.06), col, pivot='bottom', bevel=0.01), M['steel_paint'])
    add(L.box("casing", (0.6, 0.45, 0.45), (0, 0, 0.76), col, pivot='bottom', rot=(math.radians(-12), 0, 0), bevel=0.02, segs=3), M['polymer_dark'])
    add(L.box("bezel", (0.52, 0.02, 0.36), (0, -0.23, 0.82), col, pivot='bottom', rot=(math.radians(-12), 0, 0), bevel=0.006), M['polymer_dark'])
    add(L.box("screen", (0.46, 0.006, 0.3), (0, -0.235, 0.85), col, pivot='bottom', rot=(math.radians(-12), 0, 0)), M['screen'])
    add(L.box("screen_glass", (0.47, 0.003, 0.31), (0, -0.245, 0.85), col, pivot='bottom', rot=(math.radians(-12), 0, 0)), M['glass'])
    add(L.box("back_panel", (0.5, 0.02, 0.36), (0, 0.22, 0.8), col, pivot='bottom', rot=(math.radians(-12), 0, 0)), M['steel_paint'])
    vents = [L.box(f"vent{i}", (0.2, 0.005, 0.01), (0.12, 0.23, 0.9 + i * 0.03), col) for i in range(5)]
    for v in vents: L.assign(v, M['steel_dark'])
    P.append(L.join(vents, "vents"))
    add(L.box("key_tray", (0.5, 0.22, 0.04), (0, -0.28, 0.72), col, pivot='bottom', bevel=0.006), M['polymer_dark'])
    keys = [L.box(f"key{i}", (0.03, 0.03, 0.012), (-0.2 + (i % 12) * 0.035, -0.32 + (i // 12) * 0.04, 0.76), col, bevel=0.002) for i in range(36)]
    for k in keys: L.assign(k, M['polymer_ivory'])
    P.append(L.join(keys, "keys"))
    add(L.cyl("main_control", 0.03, 0.02, (0.2, -0.33, 0.76), col, verts=16), M['emitter'])
    screws = [L.cyl(f"screw{i}", 0.005, 0.003, (-0.28 + (i % 2) * 0.56, -0.215, 0.7 + (i // 2) * 0.3), col, axis='Y', verts=8) for i in range(4)]
    for s in screws: L.assign(s, M['steel_bare'])
    P.append(L.join(screws, "screws"))
    add(L.tube("power_cable", [(0.05, 0.15, 0.1), (0.2, 0.3, 0.05), (0.35, 0.4, 0.0)], 0.01, col), M['rubber'])
    for o in P: L.apply_all(o); L.smooth(o, 40); L.uv_project(o, 0.01)
    L.save_blend(ASSET); print("built terminal", len(P))

elif WHICH == "gurney":
    ASSET = "OBJ-043_Camilla"; col = L.collection(ASSET)
    for i, (x, y) in enumerate(((-0.85, -0.3), (0.85, -0.3), (-0.85, 0.3), (0.85, 0.3))):
        add(L.cyl(f"wheel{i}", 0.06, 0.04, (x, y, 0.06), col, axis='X', verts=16), M['rubber'])
        add(L.box(f"fork{i}", (0.06, 0.03, 0.12), (x, y, 0.06), col, pivot='bottom'), M['steel_bare'])
        add(L.cyl(f"leg{i}", 0.02, 0.5, (x, y, 0.16), col, pivot='bottom', verts=12), M['paint_med'])
    add(L.box("brake_pedal", (0.12, 0.06, 0.02), (0.6, -0.36, 0.1), col, rot=(math.radians(20), 0, 0)), M['plastic_red'] if 'plastic_red' in M else M['rubber'])
    add(L.box("frame", (2.0, 0.7, 0.05), (0, 0, 0.66), col, pivot='bottom', bevel=0.008), M['paint_med'])
    for x in (-0.5, 0.5): add(L.box(f"cross_{x:+.1f}", (0.04, 0.66, 0.04), (x, 0, 0.62), col, pivot='bottom'), M['paint_med'])
    mat = add(L.box("mattress", (1.95, 0.68, 0.1), (0, 0, 0.71), col, pivot='bottom', bevel=0.03, segs=3), M['mattress'])
    cut = L.box("press_cut", (1.4, 0.4, 0.05), (0.1, 0, 0.79), col)
    m = mat.modifiers.new("Press", 'BOOLEAN'); m.operation = 'DIFFERENCE'; m.object = cut; L.apply_all(mat); bpy.data.objects.remove(cut)
    add(L.box("seam", (1.95, 0.68, 0.005), (0, 0, 0.76), col, pivot='bottom'), M['fabric'])
    add(L.box("blanket", (1.2, 0.72, 0.06), (-0.15, 0, 0.79), col, pivot='bottom', bevel=0.025, segs=3), M['blanket'])
    for sx in (-1, 1):
        rail = [L.cyl(f"rail_{sx}_{k}", 0.012, 1.2, (0, sx * 0.36, 0.95 + k * 0.1), col, axis='X', verts=10) for k in range(3)]
        rail += [L.cyl(f"railpost_{sx}_{k}", 0.012, 0.35, (-0.5 + k * 1.0, sx * 0.36, 0.66), col, pivot='bottom', verts=10) for k in range(2)]
        for r in rail: L.assign(r, M['paint_med'])
        P.append(L.join(rail, f"siderail_{sx}"))
    add(L.cyl("iv_pole", 0.012, 1.0, (-0.95, 0.3, 0.66), col, pivot='bottom', verts=10), M['steel_bare'])
    add(L.box("iv_hook", (0.06, 0.02, 0.02), (-0.92, 0.3, 1.64), col), M['steel_bare'])
    add(L.tube("iv_tube", [(-0.92, 0.3, 1.6), (-0.7, 0.2, 1.2), (-0.4, 0.1, 0.85)], 0.004, col), M['glass'])
    for o in P: L.apply_all(o); L.smooth(o, 40); L.uv_project(o, 0.01)
    L.save_blend(ASSET); print("built gurney", len(P))

elif WHICH == "cart":
    ASSET = "OBJ-029_Carro"; col = L.collection(ASSET)
    add(L.box("platform", (1.0, 0.6, 0.04), (0, 0, 0.16), col, pivot='bottom', bevel=0.006), M['steel_bare'])
    add(L.box("platform_paint", (0.96, 0.56, 0.005), (0, 0, 0.2), col, pivot='bottom'), M['paint_ind'])
    for x in (-0.45, 0.45):
        for y in (-0.25, 0.25):
            add(L.cyl(f"wheel_{x:+.2f}_{y:+.2f}", 0.08, 0.05, (x, y, 0.08), col, axis='Y', verts=16), M['rubber'])
            add(L.cyl(f"hub_{x:+.2f}_{y:+.2f}", 0.03, 0.06, (x, y, 0.08), col, axis='Y', verts=12), M['steel_bare'])
            add(L.box(f"bracket_{x:+.2f}_{y:+.2f}", (0.06, 0.08, 0.08), (x, y, 0.1), col, pivot='bottom'), M['steel_dark'])
    for x in (-0.44, 0.44): add(L.box(f"rail_{x:+.1f}", (0.05, 0.6, 0.04), (x, 0, 0.12), col, pivot='bottom'), M['steel_dark'])
    for sx in (-1, 1):
        add(L.cyl(f"handle_post_{sx}", 0.015, 0.7, (-0.46, sx * 0.25, 0.2), col, pivot='bottom', verts=12), M['steel_paint'])
    add(L.cyl("handle_bar", 0.016, 0.54, (-0.46, 0, 0.9), col, axis='Y', verts=12), M['steel_bare'])
    add(L.cyl("handle_grip", 0.019, 0.3, (-0.46, 0, 0.9), col, axis='Y', verts=12), M['rubber'])
    add(L.box("crate_load", (0.5, 0.4, 0.4), (0.15, 0, 0.2), col, pivot='bottom', bevel=0.01), M['steel_paint'])
    add(L.box("strap", (0.52, 0.03, 0.42), (0.15, 0, 0.19), col, pivot='bottom'), M['fabric'])
    for o in P: L.apply_all(o); L.smooth(o, 40); L.uv_project(o, 0.01)
    L.save_blend(ASSET); print("built cart", len(P))
