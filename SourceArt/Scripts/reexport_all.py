# Reexporta todos los FBX con el stack NLA activo.
#
# Defecto encontrado midiendo los clips YA IMPORTADOS en Unity: cada take salía con el nombre y la duración
# correctos y con la pose de reposo repetida en todos los frames (36 claves por curva, cero curvas que cambien de
# valor). Causa: `export_scene.fbx` con `bake_anim_use_nla_strips=True` evalúa las tiras a través del stack NLA, y
# el stack quedaba apagado porque el medidor de contactos, `ground_clamp` y `foot_lock` lo desactivan para poder
# leer un clip aislado y lo restauran al valor que encontraron, que ya era False.
#
# No hace falta rehornear nada: se reabre cada .blend, se reactiva el stack y se reexporta.
import bpy, sys, os, json, importlib, traceback
sys.path.insert(0, r"C:/Users/HP/Documents/GitHub/proyectos-unity/SourceArt/Scripts")
import esn_lib as L; importlib.reload(L)
import measure_contacts as MC; importlib.reload(MC)

SRC = r"C:/Users/HP/Documents/GitHub/proyectos-unity/SourceArt/Blender"
out = []
for fn in sorted(os.listdir(SRC)):
    if not fn.endswith(".blend"):
        continue
    asset = fn[:-6]
    try:
        bpy.ops.wm.open_mainfile(filepath=os.path.join(SRC, fn))
        arm = next((o for o in bpy.data.objects if o.type == 'ARMATURE'), None)
        objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
        if not objs:
            out.append({"asset": asset, "estado": "sin mallas"}); continue
        pistas = 0
        if arm is not None:
            MC._reset_pose(arm)
            L.enable_nla(arm)
            pistas = len(arm.animation_data.nla_tracks) if arm.animation_data else 0
        _, size = L.export_fbx(objs, asset, armature_obj=arm)
        L.save_blend(asset)
        out.append({"asset": asset, "pistas_nla": pistas, "bytes": size})
        print("ok", asset, "pistas", pistas)
    except Exception:
        out.append({"asset": asset, "ERROR": traceback.format_exc()[-800:]})
        print("ERR", asset)
print("RESULTADO " + json.dumps(out, ensure_ascii=False))
