# Continuación genérica: hornea (opcional), guarda, exporta y renderiza la hoja de un asset ya construido en la escena.
# Parámetros por variables globales inyectadas: ASSET, ARM_NAME, CLIPS, HEIGHT, DO_BAKE, MAPS
import bpy, sys, importlib, traceback, json, os
sys.path.insert(0, r"C:/Users/HP/Documents/GitHub/proyectos-unity/SourceArt/Scripts")
import esn_lib as L; importlib.reload(L)

ASSET = globals().get("ASSET", "BOT-01_Vigia")
ARM_NAME = globals().get("ARM_NAME", "Armature_Vigia")
CLIPS = globals().get("CLIPS", [])
HEIGHT = globals().get("HEIGHT", 0)
DO_BAKE = globals().get("DO_BAKE", True)
MAPS = globals().get("MAPS", ["BaseColor", "Roughness", "Metallic", "Normal"])
SIZE = globals().get("SIZE", 1024)
# Bevel/Pointiness/AO se resuelven por muestreo: con 6 muestras el AO sale granulado (41.1 exige mapas limpios).
SAMPLES = globals().get("SAMPLES", 48)
log = []
arm = bpy.data.objects.get(ARM_NAME)
objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
tex = {}
if DO_BAKE:
    try:
        L.uv_project_all(objs); log.append("uv atlas compartido ok")
    except Exception:
        log.append("uv atlas ERR " + traceback.format_exc()[-800:])
    for m in MAPS:
        try:
            tex.update(L.bake_pbr(objs, ASSET, size=SIZE, samples=SAMPLES, only=[m]))
            log.append("bake %s ok" % m)
        except Exception:
            log.append("bake %s ERR %s" % (m, traceback.format_exc()[-1200:]))
for m in ("BaseColor", "Roughness", "Metallic", "Normal"):
    p = f"{L.TEX_DIR}/{ASSET}_{m}.png"
    if os.path.exists(p): tex[m] = p
# 49.8/PIL-14: los contactos con el suelo se resuelven sobre la geometría ya construida y ANTES de exportar, para que
# el FBX que ve Unity sea el mismo que mide el gate. `foot_lock` baja/sube el raíz hasta que el pie de apoyo toca en
# cada frame del ciclo; `ground_clamp` sube los clips que entierran el cuerpo (muerte, caída).
try:
    import measure_contacts as MC; importlib.reload(MC)
    if arm is not None and arm.animation_data:
        acts = [st.action for tr in arm.animation_data.nla_tracks for st in tr.strips if st.action]
        feet = [o for o in objs if any(h in o.name.lower() for h in MC.FOOT_HINTS)]
        loco = [a for a in acts if "walk" in a.name.lower() or "run" in a.name.lower()]
        if feet and loco:
            log.append("foot_lock %s" % L.foot_lock(arm, objs, feet, loco))
        resto = [a for a in acts if a not in loco]
        if resto:
            log.append("ground_clamp %s" % [r for r in L.ground_clamp(arm, objs, resto) if r[1]])
        MC._reset_pose(arm)   # sin esto el FBX hornea los huesos no keyeados con la pose del último clip medido
        L.enable_nla(arm)     # y sin esto el .blend se guarda con el stack apagado y el siguiente export sale plano
except Exception:
    log.append("contactos ERR " + traceback.format_exc()[-900:])
try:
    blend = L.save_blend(ASSET); log.append("blend ok")
except Exception:
    blend = ""; log.append("blend ERR " + traceback.format_exc()[-600:])
try:
    fbx, size = L.export_fbx(objs, ASSET, armature_obj=arm); log.append("fbx ok %d" % size)
except Exception:
    fbx, size = "", 0; log.append("fbx ERR " + traceback.format_exc()[-800:])
try:
    if arm is not None: arm.data.pose_position = 'REST'  # hoja en pose de reposo, no en un frame de clip
    bpy.context.view_layer.update()
    sheets = L.sheet(ASSET, objs); log.append("sheet ok")
    if arm is not None: arm.data.pose_position = 'POSE'
except Exception:
    sheets = []; log.append("sheet ERR " + traceback.format_exc()[-800:])
rep = L.report(ASSET, objs, {"blend": blend, "fbx": fbx, "fbx_bytes": size, "textures": tex, "clips": CLIPS, "height_target_m": HEIGHT, "sheets": sheets, "log": log})
print(json.dumps(rep, indent=1)[-1500:])
