"""Record generated EX-50 artifacts in the machine-readable production inventory."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PENDING=ROOT/"docs/produccion/MODELOS_PENDIENTES_EX12.json"
STATE=ROOT/"docs/produccion/MODELOS_ESTADO_EX12.json"
MAP={
"OBJ-015":"OBJ-015_PulseraLazaro", "OBJ-042":"OBJ-042_CierreContencion",
"OBJ-071":"OBJ-071_EsclusaPresion", "OBJ-073":"OBJ-073_ConsolaPrincipal",
"OBJ-075":"OBJ-075_BarandaPasarela", "OBJ-077":"OBJ-077_PanelEscape",
"OBJ-078":"OBJ-078_CompuertaMonumental", "OBJ-080":"OBJ-080_ArchivoFisico",
"ENV-EXIT":"ENV-EXIT_ExteriorEscape"}

p=json.loads(PENDING.read_text(encoding="utf-8-sig")); s=json.loads(STATE.read_text(encoding="utf-8-sig"))
for entry in p["entries"]:
    if entry["id"] not in MAP: continue
    asset=MAP[entry["id"]]; evidence=f"SourceArt/_evidence/EX-50/{asset}"
    report=json.loads((ROOT/evidence/"delivery.json").read_text(encoding="utf-8"))
    entry.update({"source_files":[f"SourceArt/Blender/{asset}.blend"],"state":"Prefab validado",
        "acceptance_proven":False,"prefab":f"EsneiderProtocoloLazaro/Assets/_Game/Prefabs/Environment/{asset}.prefab",
        "evidence":evidence,"triangles":report["tris"],"texture_sets":1,
        "remaining":["montaje definitivo en escena y conexión de interacción", "validación artística con iluminación final"]})
    s[entry["id"]]={"state":"Prefab validado","acceptance_proven":False,"series":"EX-50",
        "source":f"SourceArt/Blender/{asset}.blend","fbx":f"EsneiderProtocoloLazaro/Assets/_Game/Art/Models/{asset}.fbx",
        "prefab":f"EsneiderProtocoloLazaro/Assets/_Game/Prefabs/Environment/{asset}.prefab",
        "triangles":report["tris"],"texture_sets":1,"dimensions_m":report["dims_m"],"evidence":evidence,
        "remaining":["montaje definitivo en escena y conexión de interacción", "validación artística con iluminación final"]}
PENDING.write_text(json.dumps(p,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
STATE.write_text(json.dumps(s,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
