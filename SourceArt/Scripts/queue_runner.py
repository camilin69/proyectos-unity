# Cola de fabricación autónoma (100.5 ciclo por asset): build → bake → blend → FBX → hoja → informe, un asset tras otro.
# Progreso en SourceArt/_evidence/EX-04/queue_progress.json. Se ejecuta con bpy.app.timers para no bloquear el socket MCP.
import bpy, runpy, json, os, sys, time, traceback
S = r"C:/Users/HP/Documents/GitHub/proyectos-unity/SourceArt/Scripts"
if S not in sys.path: sys.path.insert(0, S)
EV = r"C:/Users/HP/Documents/GitHub/proyectos-unity/SourceArt/_evidence/EX-04"
QUEUE = globals().get("QUEUE", [])
PROG = EV + "/queue_progress.json"
state = {"done": [], "failed": [], "current": "", "started": time.strftime("%H:%M:%S")}


def save():
    json.dump(state, open(PROG, "w"), indent=1)


def run_item(item):
    state["current"] = item["asset"]; save()
    g = {"WHICH": item.get("which", "")}
    runpy.run_path(S + "/" + item["script"], init_globals=g, run_name="__main__")
    fin = {"ASSET": item["asset"], "ARM_NAME": item.get("arm", ""), "CLIPS": item.get("clips", []), "HEIGHT": item.get("height", 0), "DO_BAKE": True, "MAPS": item.get("maps", ["BaseColor", "Roughness", "Metallic", "Normal"]), "SIZE": item.get("size", 1024), "SAMPLES": item.get("samples", 32)}
    runpy.run_path(S + "/finish_asset.py", init_globals=fin, run_name="__main__")
    # 49.7/49.8 y PIL-14: medir los contactos del asset recién construido, con el rig todavía en escena
    try:
        import importlib, measure_contacts as MC
        importlib.reload(MC)
        MC.measure(item["asset"], patrol_speed=item.get("patrol_speed"))
    except Exception:
        state.setdefault("measure_errors", []).append({"asset": item["asset"], "error": traceback.format_exc()[-800:]})


def step():
    if not QUEUE:
        state["current"] = ""; state["finished"] = time.strftime("%H:%M:%S"); save(); return None
    item = QUEUE.pop(0)
    try:
        run_item(item); state["done"].append(item["asset"])
    except Exception:
        state["failed"].append({"asset": item["asset"], "error": traceback.format_exc()[-1500:]})
    save()
    return 0.5  # siguiente asset en el próximo tick


save()
bpy.app.timers.register(step, first_interval=0.5)
