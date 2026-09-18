# Medidor de contactos de animación (49.7 revisión de clips, 49.8 QA, 63 fichas de contacto, PIL-14).
#
# "Contacto verificado" no es una captura ni una opinión: es un número medido frame a frame contra un umbral
# escrito de antemano. Este script recorre cada clip del asset que está EN LA ESCENA (después de construirlo)
# y mide, sobre la malla evaluada por el depsgraph:
#
#   G-01 penetración de suelo : ningún vértice por debajo de z = -2 mm en ningún frame de ningún clip.
#   G-02 pie plantado         : los ciclos son IN-PLACE (el agente traslada al bot), así que durante el apoyo el pie
#                               debe retroceder — eso no es un defecto. Lo que 49.8 llama "pies deslizándose" es que
#                               ese retroceso NO sea uniforme: si el pie acelera y frena mientras toca el suelo, patina.
#                               Se mide la dispersión de la velocidad horizontal del pie durante el apoyo: <= 35 %.
#   G-03 flotación            : en un ciclo de marcha, al menos un pie debe estar apoyado (min z <= 20 mm)
#                               en >= 85 % de los frames; si no, el bot camina flotando.
#   G-04 zancada              : velocidad implícita del clip = recorrido del pie apoyado / duración del apoyo.
#                               77.1 dice que las velocidades del dato son "valores iniciales por verificar con
#                               clips y escala", así que se compara contra patrolSpeed y se emite el factor.
#   G-05 rigidez de bisagra   : en clips de apertura (tapa, puerta, jaula) la distancia de cada vértice móvil al
#                               eje declarado debe mantenerse constante (giro real, no estiramiento).
#   G-06 despeje del pie      : cada pie debe levantarse >= 30 mm del suelo una vez por ciclo. Sin este número, un
#                               ciclo que interpola entre dos poses opuestas pasa el resto de gates arrastrando los
#                               pies: el pie en vuelo cruza la vertical, que es donde queda MÁS BAJO. Medido antes
#                               de corregirlo: 7.3 mm en el Vigía y 7.9 mm en el Custodio.
#
# Cuidado con el recorrido: en un ciclo in-place el último frame vuelve al primero, así que la distancia del primer
# al último frame del apoyo es CERO y no mide nada. El recorrido real es la separación máxima entre dos muestras.
#
# Salida: SourceArt/_evidence/EX-08/contacts_<ASSET>.json  + una línea por gate con PASA/FALLA.
import bpy, json, os, math
from mathutils import Vector

ROOT = r"C:/Users/HP/Documents/GitHub/proyectos-unity"
OUT_DIR = ROOT + "/SourceArt/_evidence/EX-08"
os.makedirs(OUT_DIR, exist_ok=True)

GROUND_TOL = -0.002        # 2 mm de penetración tolerada
PLANT_Z = 0.020            # un pie por debajo de 2 cm cuenta como apoyado
SLIDE_TOL = 0.020          # 2 cm de deslizamiento máximo durante el apoyo
CONTACT_RATIO = 0.85       # fracción mínima de frames del ciclo con algún pie apoyado
FOOT_CLEARANCE = 0.030     # el pie en vuelo tiene que levantar al menos 3 cm una vez por ciclo
FOOT_HINTS = ("foot", "boot", "sole", "pie", "toe", "pad_")
MOVING_HINTS = ("lid", "leaf", "door", "gate", "hatch", "tapa", "hoja")


def _meshes():
    return [o for o in bpy.context.scene.objects if o.type == 'MESH']


def _arm():
    for o in bpy.context.scene.objects:
        if o.type == 'ARMATURE':
            return o
    return None


def _world_verts(o, dg):
    ev = o.evaluated_get(dg)
    me = ev.to_mesh()
    mw = ev.matrix_world
    pts = [mw @ v.co for v in me.vertices]
    ev.to_mesh_clear()
    return pts


def _reset_pose(arm):
    for pb in arm.pose.bones:
        pb.location = (0.0, 0.0, 0.0)
        pb.rotation_euler = (0.0, 0.0, 0.0)
        pb.rotation_quaternion = (1.0, 0.0, 0.0, 0.0)
        pb.scale = (1.0, 1.0, 1.0)
    bpy.context.view_layer.update()


def _clips(arm):
    """(nombre, accion, frame_ini, frame_fin) por pista NLA."""
    out = []
    ad = arm.animation_data if arm else None
    if not ad:
        return out
    for tr in ad.nla_tracks:
        for st in tr.strips:
            if st.action:
                out.append((st.action.name, st.action, int(st.frame_start), int(st.frame_end)))
    return out


def measure(asset_id, patrol_speed=None, fps=30):
    arm = _arm()
    meshes = _meshes()
    clips = _clips(arm)
    rep = {"asset": asset_id, "fps": fps, "clips": [], "gates": [], "thresholds": {
        "ground_tol_m": GROUND_TOL, "plant_z_m": PLANT_Z, "slide_tol_m": SLIDE_TOL,
        "contact_ratio": CONTACT_RATIO, "foot_clearance_m": FOOT_CLEARANCE}}
    if not clips:
        rep["gates"].append({"id": "G-00", "estado": "N/A", "detalle": "el asset no tiene clips"})
        _save(asset_id, rep)
        return rep

    feet = [o for o in meshes if any(h in o.name.lower() for h in FOOT_HINTS)]
    movers = [o for o in meshes if any(h in o.name.lower() for h in MOVING_HINTS)]
    rep["foot_objects"] = [o.name for o in feet]
    rep["moving_objects"] = [o.name for o in movers]

    saved = arm.animation_data.action if arm.animation_data else None
    # Con NLA activo, las pistas de TODOS los clips se evalúan encima de la acción asignada y la pose medida es la
    # suma de los cinco. Hay que desactivar el stack para medir un clip aislado.
    saved_nla = arm.animation_data.use_nla if arm.animation_data else False
    if arm.animation_data: arm.animation_data.use_nla = False
    # Referencia de reposo: si ya en REST la malla está bajo z=0, el problema es de construcción, no de animación.
    arm.data.pose_position = 'REST'
    bpy.context.view_layer.update()
    dg0 = bpy.context.evaluated_depsgraph_get()
    rest_min = 1e9
    for o in meshes:
        pts = _world_verts(o, dg0)
        if pts: rest_min = min(rest_min, min(p.z for p in pts))
    rep["rest_min_z_m"] = round(rest_min, 5)
    arm.data.pose_position = 'POSE'
    worst_ground = {"z": 1e9, "clip": "", "frame": 0, "obj": ""}

    for name, act, f0, f1 in clips:
        # Blender conserva la pose de los huesos que la nueva acción NO keyea: sin este reseteo se mide la
        # postura heredada del clip anterior y se reportan defectos falsos.
        _reset_pose(arm)
        arm.animation_data.action = act
        n = max(2, f1 - f0 + 1)
        per_foot = {o.name: [] for o in feet}
        min_z_frames = []
        for fi in range(f0, f1 + 1):
            bpy.context.scene.frame_set(fi)
            dg = bpy.context.evaluated_depsgraph_get()
            zmin_all = 1e9; who = ""
            for o in meshes:
                pts = _world_verts(o, dg)
                if not pts:
                    continue
                z = min(p.z for p in pts)
                if z < zmin_all:
                    zmin_all = z; who = o.name
                if o.name in per_foot:
                    # El deslizamiento se mide sobre el CENTROIDE, no sobre "el vértice más bajo": ese salta de
                    # esquina en cuanto el pie bascula y produce falsos 50 cm de patinaje.
                    cx = sum(p.x for p in pts) / len(pts); cy = sum(p.y for p in pts) / len(pts)
                    per_foot[o.name].append((z, Vector((cx, cy, 0.0))))
            min_z_frames.append(zmin_all)
            if zmin_all < worst_ground["z"]:
                worst_ground = {"z": round(zmin_all, 5), "clip": name, "frame": fi, "obj": who}

        c = {"clip": name, "frames": n, "seconds": round(n / fps, 3),
             "min_z_m": round(min(min_z_frames), 5), "feet": {}}

        # --- apoyo, deslizamiento y zancada por pie ---
        # El pie de APOYO es el que soporta el peso, es decir el más bajo de los dos. No basta con "está a menos de
        # 2 cm del suelo": el pie en vuelo cruza esa banda al despegar y al aterrizar, y esos frames, en los que
        # avanza en vez de retroceder, entran en la misma tirada y disparan la dispersión de velocidad a más del
        # 100 % aunque el retroceso real sea uniforme. La fracción de contacto (G-03) sí usa el umbral, porque ahí
        # la pregunta es otra: si el bot toca el suelo.
        planted_any = 0
        lowest_of = []
        for i in range(n):
            zs = [s[i][0] for s in per_foot.values() if i < len(s)]
            lowest_of.append(min(zs) if zs else 0.0)
        for fname, samples in per_foot.items():
            planted = [i for i, (z, _) in enumerate(samples) if z <= PLANT_Z]
            # El ciclo es cerrado: el último frame repite el primero. Sin tratarlo como circular, el apoyo que cruza
            # el cierre del bucle se parte en dos tiradas, la corta mide un retroceso ridículo y la dispersión sale
            # por encima del 100 % aunque el pie avance de forma perfectamente uniforme.
            loops = len(samples) > 3 and (samples[0][1] - samples[-1][1]).length < 1e-4
            seq = samples[:-1] if loops else samples
            m = len(seq)
            stance = [i for i in range(m) if seq[i][0] <= PLANT_Z and seq[i][0] <= lowest_of[i] + 0.001]
            stance_set = set(stance)
            runs, cur = [], []
            for i in range(m):
                if i in stance_set:
                    cur.append(i)
                elif cur:
                    runs.append(cur); cur = []
            if cur: runs.append(cur)
            if loops and len(runs) > 1 and runs[0][0] == 0 and runs[-1][-1] == m - 1:
                runs[0] = runs.pop() + runs[0]        # la tirada del final y la del principio son el mismo apoyo
            lateral = 0.0; stride = 0.0; stance_s = 0.0; jitter = 0.0; bob = 0.0
            for run in runs:
                pts = [seq[i][1] for i in run]
                zs = [seq[i][0] for i in run]
                if len(pts) < 3:
                    continue
                # recorrido = separación máxima entre dos muestras del apoyo. NO (último - primero): el ciclo cierra.
                p0, p1 = max(((p, q) for p in pts for q in pts), key=lambda pq: (pq[0] - pq[1]).length)
                span = (p0 - p1).length
                stride = max(stride, span)
                if span > 1e-5:
                    d = (p0 - p1) / span
                    lateral = max(lateral, max(((p - p1) - d * (p - p1).dot(d)).length for p in pts))
                stance_s = max(stance_s, len(run) / fps)
                bob = max(bob, max(zs) - min(zs))
                # uniformidad del retroceso: desviación relativa de la velocidad horizontal entre frames del apoyo
                step = [(pts[i + 1] - pts[i]).length for i in range(len(pts) - 1)]
                mean = sum(step) / len(step)
                if mean > 1e-5:
                    jitter = max(jitter, max(abs(s - mean) for s in step) / mean)
            clearance = max((z for z, _ in samples), default=0.0)
            c["feet"][fname] = {"planted_frames": len(planted), "stance_frames": len(stance),
                                "lateral_slip_m": round(lateral, 4),
                                "stride_m": round(stride, 4), "stance_s": round(stance_s, 3),
                                "speed_jitter": round(jitter, 3), "bob_while_planted_m": round(bob, 4),
                                "clearance_m": round(clearance, 4)}
        if feet:
            for i in range(n):
                if any(i < len(s) and s[i][0] <= PLANT_Z for s in per_foot.values()):
                    planted_any += 1
            c["contact_ratio"] = round(planted_any / n, 3)

        # --- rigidez de bisagra: la distancia entre vértices de la pieza móvil no debe cambiar ---
        if movers and ("open" in name.lower() or "close" in name.lower()):
            devs = []
            for o in movers:
                ref = None
                for fi in range(f0, f1 + 1, max(1, (f1 - f0) // 6)):
                    bpy.context.scene.frame_set(fi)
                    dg = bpy.context.evaluated_depsgraph_get()
                    pts = _world_verts(o, dg)
                    if len(pts) < 4:
                        continue
                    d = [(pts[0] - pts[k]).length for k in range(1, min(len(pts), 40))]
                    if ref is None:
                        ref = d
                    else:
                        devs.append(max(abs(a - b) for a, b in zip(ref, d)))
            if devs:
                c["hinge_rigidity_max_dev_m"] = round(max(devs), 5)
        rep["clips"].append(c)

    if arm.animation_data:
        arm.animation_data.action = saved
        arm.animation_data.use_nla = saved_nla
    _reset_pose(arm)
    bpy.context.scene.frame_set(1)

    # ---------- gates ----------
    def gate(gid, ok, detalle):
        rep["gates"].append({"id": gid, "estado": "PASA" if ok else "FALLA", "detalle": detalle})

    gate("G-01", worst_ground["z"] >= GROUND_TOL,
         f"penetración máxima {worst_ground['z']*1000:.1f} mm en {worst_ground['clip']} f{worst_ground['frame']} ({worst_ground['obj']}); tolerancia {GROUND_TOL*1000:.0f} mm")

    loco = [c for c in rep["clips"] if "walk" in c["clip"].lower() or "run" in c["clip"].lower()]
    if feet and loco:
        worst_jit = max((max((f.get("speed_jitter", 0.0) for f in c["feet"].values()), default=0.0) for c in loco), default=0.0)
        worst_bob = max((max((f.get("bob_while_planted_m", 0.0) for f in c["feet"].values()), default=0.0) for c in loco), default=0.0)
        gate("G-02", worst_jit <= 0.35 and worst_bob <= 0.02,
             f"retroceso del pie apoyado: dispersión de velocidad {worst_jit*100:.0f} % (máx 35 %), rebote vertical {worst_bob*1000:.1f} mm (máx 20 mm)")
        worst_ratio = min((c.get("contact_ratio", 0.0) for c in loco), default=0.0)
        gate("G-03", worst_ratio >= CONTACT_RATIO, f"fracción de frames con algún pie apoyado {worst_ratio:.2f}; mínimo {CONTACT_RATIO:.2f}")
        speeds = []
        for c in loco:
            for f in c["feet"].values():
                if f["stance_s"] > 0.05 and f["stride_m"] > 0.01:
                    speeds.append(f["stride_m"] / f["stance_s"])
        if speeds:
            v = sum(speeds) / len(speeds)
            rep["clip_stride_speed_mps"] = round(v, 3)
            if patrol_speed:
                ratio = v / patrol_speed
                rep["stride_vs_patrol"] = round(ratio, 3)
                gate("G-04", 0.75 <= ratio <= 1.35,
                     f"velocidad implícita del clip {v:.2f} m/s contra patrulla {patrol_speed:.2f} m/s (factor {ratio:.2f}); "
                     f"fuera de 0.75-1.35 el pie patina salvo que EnemyAnimator escale la reproducción")
            else:
                gate("G-04", True, f"velocidad implícita del clip {v:.2f} m/s (sin velocidad de dato para comparar)")
        # G-06: cada pie tiene que despegar una vez por ciclo, o el bot arrastra los pies aunque los demás gates pasen
        per_foot_clear = {}
        for c in loco:
            for fname, f in c["feet"].items():
                per_foot_clear[fname] = max(per_foot_clear.get(fname, 0.0), f.get("clearance_m", 0.0))
        if per_foot_clear:
            worst_name = min(per_foot_clear, key=per_foot_clear.get)
            worst_clear = per_foot_clear[worst_name]
            rep["foot_clearance_m"] = {k: round(v, 4) for k, v in per_foot_clear.items()}
            gate("G-06", worst_clear >= FOOT_CLEARANCE,
                 f"despeje mínimo del pie en vuelo {worst_clear*1000:.1f} mm ({worst_name}); mínimo "
                 f"{FOOT_CLEARANCE*1000:.0f} mm — por debajo el pie roza el suelo en toda la pasada")
    elif not feet:
        rep["gates"].append({"id": "G-02", "estado": "N/A", "detalle": "el asset no tiene piezas de pie identificables"})

    hinge = [c.get("hinge_rigidity_max_dev_m") for c in rep["clips"] if c.get("hinge_rigidity_max_dev_m") is not None]
    if hinge:
        gate("G-05", max(hinge) <= 0.002, f"deformación máxima de pieza móvil {max(hinge)*1000:.2f} mm; debe girar rígida (<= 2 mm)")

    _save(asset_id, rep)
    return rep


def _save(asset_id, rep):
    p = f"{OUT_DIR}/contacts_{asset_id}.json"
    with open(p, "w", encoding="utf-8") as f:
        json.dump(rep, f, indent=1, ensure_ascii=False)
    rep["path"] = p
    for g in rep.get("gates", []):
        print(f"  [{g['id']}] {g['estado']}: {g['detalle']}")
    return p
