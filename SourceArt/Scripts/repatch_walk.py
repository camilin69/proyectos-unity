# Reemplaza el ciclo de marcha de los tres bots sobre el .blend ya construido, sin rehornear texturas.
#
# El clip anterior tenía dos poses opuestas y nada en medio, así que el pie en vuelo cruzaba la vertical (su punto
# más bajo) y el bot arrastraba los pies: 7.3 mm de despeje medidos en el Vigía. `L.walk_cycle` genera el ciclo con
# pose de paso y `L.foot_lock` resuelve después la altura del cuerpo midiendo el pie de apoyo frame a frame.
# Los parámetros salen de L.WALK_PRESETS, los mismos que usan los constructores, para que un rebuild completo
# reproduzca exactamente esto.
import bpy, sys, os, json, importlib, traceback
sys.path.insert(0, r"C:/Users/HP/Documents/GitHub/proyectos-unity/SourceArt/Scripts")
import esn_lib as L; importlib.reload(L)
import measure_contacts as MC; importlib.reload(MC)

SRC = r"C:/Users/HP/Documents/GitHub/proyectos-unity/SourceArt/Blender"
# velocidad nominal contra la que G-04 compara: patrulla del dato (Vigía/Custodio) o aproximación del jefe.
JOBS = [("BOT-01_Vigia", "Vigia_Walk", 0.70),
        ("BOT-02_Custodio", "Custodio_Walk", 0.60),
        ("BOT-03_Archivista", "Archivista_Walk", 1.60)]
ONLY = globals().get("ONLY", None)
out = []

for asset, clip, nominal in JOBS:
    if ONLY and asset not in ONLY:
        continue
    try:
        bpy.ops.wm.open_mainfile(filepath=os.path.join(SRC, asset + ".blend"))
        arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
        objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
        ad = arm.animation_data
        ad.use_nla = False
        ad.action = None
        MC._reset_pose(arm)

        # fuera la pista y la acción viejas antes de generar la nueva con el mismo nombre
        for tr in list(ad.nla_tracks):
            if any(st.action and st.action.name == clip for st in tr.strips):
                ad.nla_tracks.remove(tr)
        old = bpy.data.actions.get(clip)
        if old:
            old.use_fake_user = False
            bpy.data.actions.remove(old)

        act = L.walk_cycle(arm, clip, **L.WALK_PRESETS[asset])
        ad.action = None
        MC._reset_pose(arm)
        L.push_nla(arm, act)

        feet = [o.name for o in objs if any(h in o.name.lower() for h in MC.FOOT_HINTS)]
        lock = L.foot_lock(arm, objs, feet, [clip])
        # un foot_lock que no corrige nada es un no-op silencioso, no un éxito: hay que verlo fallar.
        if not lock or any("SIN" in str(x) for e in lock for x in e):
            raise RuntimeError("foot_lock no corrigio el clip: %r (pies=%r)" % (lock, feet))
        MC._reset_pose(arm)

        L.export_fbx(objs, asset, armature_obj=arm)
        L.save_blend(asset)
        rep = MC.measure(asset, patrol_speed=nominal)
        w = next((c for c in rep["clips"] if c["clip"] == clip), None)
        out.append({"asset": asset, "frames": L.WALK_PRESETS[asset]["frames"], "foot_lock": lock,
                    "gates": {g["id"]: g["estado"] for g in rep["gates"]},
                    "detalle": [g["detalle"] for g in rep["gates"]],
                    "vel_clip": rep.get("clip_stride_speed_mps"), "nominal": nominal,
                    "factor": rep.get("stride_vs_patrol"),
                    "apoyo": w and w.get("contact_ratio"), "walk": w})
        print("OK", asset, out[-1]["gates"])
    except Exception:
        out.append({"asset": asset, "ERROR": traceback.format_exc()[-1500:]})
        print("ERR", asset)

print("RESULTADO " + json.dumps(out, ensure_ascii=False))
