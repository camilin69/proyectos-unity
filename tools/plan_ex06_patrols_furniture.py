"""EX-06: transcribe las tablas 77.1 (patrullas) y 76.2 (mobiliario) del GDD al plano JSON.
Idempotente: reemplaza las claves `patrols` y `furniture`. Coordenadas locales a planta/conector (76.1)."""
import json, sys, io
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "EsneiderProtocoloLazaro/Assets/_Game/Data/LevelPlan/bunker_plan.json"

def P(route, unit, space, pts, mode="pingpong", delay=0.0):
    return {"id": route, "unit": unit, "space": space, "mode": mode, "delay": delay,
            "points": [{"x": x, "z": z} for x, z in pts]}

PATROLS = [
    P("PAT-01", "V01", "C-01", [(14, 1), (16, 0), (8, 0)]),
    P("PAT-02", "K01", "P03", [(16, 18), (16, 26), (14, 26)]),
    P("PAT-03", "V02", "P03", [(40, 12), (45, 14), (45, 19), (35, 19)], "loop"),
    P("PAT-04", "V03", "P03", [(10, 22), (14, 22), (14, 15)]),
    P("PAT-04", "K02", "P03", [(20, 9), (22, 13), (18, 13)], delay=8),
    P("PAT-05", "V04", "P04", [(10, 10), (12, 10), (12, 18)]),
    P("PAT-05", "K04", "P04", [(15, 18), (15, 20), (7, 20)]),
    P("PAT-06", "V05", "P04", [(50, 8), (50, 11), (53, 12)]),
    P("PAT-07", "V06", "P04", [(34, 12), (36, 12), (36, 20)]),
    P("PAT-07", "K03", "P04", [(38, 18), (40, 18), (40, 12)], delay=6),
    P("PAT-08", "V07", "C-02", [(12, 1), (18, 0), (6, 0)]),
    P("PAT-08", "K05", "C-02", [(24, 10), (24, 14), (24, 5)]),
    P("PAT-09", "V08", "C-02", [(36, 16), (44, 16), (32, 16)]),
    P("PAT-10", "V09", "P05", [(10, 10), (11, 10), (11, 15)]),
    P("PAT-10", "V10", "P05", [(16, 20), (19, 24), (12, 24)]),
    P("PAT-10", "K06", "P05", [(18, 14), (20, 14), (20, 24)]),
    P("PAT-11", "V11", "P05", [(32, 8), (35, 8), (35, 13)]),
    P("PAT-11", "V12", "P05", [(35, 20), (35, 24), (28, 24)]),
    P("PAT-11", "K07", "P05", [(38, 16), (35, 16), (35, 13)]),
    P("PAT-12", "V13", "P05", [(12, 44), (10, 44), (10, 49)]),
    P("PAT-13", "V14", "P05", [(30, 42), (29, 42), (29, 48)]),
    P("PAT-13", "K08", "P05", [(26, 48), (26, 51), (29, 51)]),
    P("PAT-14", "V15", "P05", [(50, 40), (50, 45), (48, 45)]),
    P("PAT-15", "V16", "P05", [(56, 8), (56, 5), (58, 5)]),
    P("PAT-15", "K09", "P05", [(58, 12), (60, 12), (60, 9)]),
    P("PAT-16", "K10", "P05", [(46, 28), (54, 28), (60, 28)]),
    P("PAT-17", "V17", "C-03", [(12, 1), (16, 0), (7, 0)]),
    P("PAT-17", "K11", "C-03", [(20, 7), (20, 3), (20, 9)]),
    P("PAT-18", "V18", "C-03", [(30, 10), (36, 10), (26, 10)]),
    P("PAT-19", "V22", "P06", [(44, 32), (36, 32), (28, 32)]),
    # PAT-19-01: (60,28) del GDD cae fuera de la galería P06-GAL (z 30–34) → (60,31); intención (extremo este) conservada
    P("PAT-19", "K14", "P06", [(54, 32), (60, 32), (60, 31)]),
    P("PAT-20", "V19", "P06", [(10, 12), (10, 8), (14, 8)]),
    P("PAT-20", "V20", "P06", [(18, 22), (14, 22), (10, 22)]),
    P("PAT-20", "V23", "P06", [(6, 20), (6, 17), (8, 17)]),
    P("PAT-20", "K12", "P06", [(17, 8), (17, 12), (17, 20)]),
    P("PAT-21", "V21", "P06", [(20, 42), (23, 42), (23, 39)]),
    P("PAT-21", "K13", "P06", [(24, 46), (25, 46), (25, 43)]),
]

def M(mid, floor, room, family, x, z, w, d, h, yaw=0, **kw):
    e = {"id": mid, "space": floor, "room": room, "family": family, "x": x, "z": z, "w": w, "d": d, "h": h, "yaw": yaw,
         "yOff": 0.0, "physics": False, "doorSide": "", "doorAt": 0.0}
    e.update(kw)
    return e

FURNITURE = [
    # P01
    M("M001", "P01", "S1-R01", "crio", 7, 7, 2.4, 4, 2.4), M("M002", "P01", "S1-R01", "consola", 4, 12, 1.4, 0.7, 1.1),
    M("M003", "P01", "S1-R01", "deposito", 11, 4, 1.6, 1.6, 2.8), M("M004", "P01", "S1-R01", "bandeja", 4, 4, 1.8, 0.8, 0.9),
    M("M005", "P01", "S1-R02", "banco", 5, 21, 2.4, 0.65, 0.5), M("M006", "P01", "S1-R02", "taquillas", 3, 26, 0.7, 3, 2.1),
    M("M007", "P01", "S1-R02", "carro", 8, 27, 1.2, 0.7, 0.95),
    M("M008", "P01", "S1-R05", "crio", 24, 6, 2.4, 4, 2.4), M("M009", "P01", "S1-R05", "crio", 32, 6, 2.4, 4, 2.4),
    M("M010", "P01", "S1-R05", "crio", 24, 18, 2.4, 4, 2.4), M("M011", "P01", "S1-R05", "crio", 32, 18, 2.4, 4, 2.4),
    M("M012", "P01", "S1-R05", "tuberia", 36, 12, 0.6, 12, 0.6, yOff=2.6),
    # P02
    M("M013", "P02", "S1-R03", "cascote", 6, 6, 5, 4, 1.1), M("M014", "P02", "S1-R03", "viga", 7, 13, 5, 0.5, 0.7),
    M("M015", "P02", "S1-R03", "carro", 12, 6, 1.4, 0.8, 1.0),
    M("M016", "P02", "S1-R04", "panel", 26, 4, 2.2, 0.4, 2), M("M017", "P02", "S1-R04", "mesa", 30, 7, 2, 0.8, 0.9),
    M("M018", "P02", "S1-R04", "tablero", 32, 10, 0.4, 2, 2.4),
    # P03
    M("M019", "P03", "S2-R01", "prensa", 7, 8, 6, 6, 5), M("M020", "P03", "S2-R01", "torno", 20, 7, 4, 3, 2),
    M("M021", "P03", "S2-R01", "mesa", 9, 19, 4, 2, 1.25), M("M022", "P03", "S2-R01", "contenedor", 20, 24, 3, 2, 1.4),
    M("M023", "P03", "S2-R06", "banco", 34, 5, 6, 1.2, 0.95), M("M024", "P03", "S2-R06", "robot", 47, 8, 2, 2, 2.3),
    M("M025", "P03", "S2-R06", "estanteria", 52, 16, 1, 8, 2.6), M("M026", "P03", "S2-R06", "carro", 39, 18, 2, 1, 1.25, physics=True),
    M("M027", "P03", "S2-R03", "escritorio", 35, 27, 3, 1.4, 0.85), M("M028", "P03", "S2-R03", "archivador", 38, 33, 1, 3, 1.8),
    M("M029", "P03", "S2-R03", "silla", 35, 29, 0.7, 0.7, 1.1),
    # P04
    M("M030", "P04", "S2-R02", "estante", 4, 10, 1.2, 12, 3), M("M031", "P04", "S2-R02", "estante", 16, 10, 1.2, 12, 3),
    M("M032", "P04", "S2-R02", "palet", 8, 13, 2, 2, 1.25), M("M033", "P04", "S2-R02", "locker", 7, 5, 2, 0.7, 2),
    M("M034", "P04", "S2-R04", "generador", 28, 7, 5, 4, 2.6), M("M035", "P04", "S2-R04", "carro", 31, 16, 2, 1.2, 1.25, physics=True),
    M("M036", "P04", "S2-R04", "bobina", 41, 7, 2.5, 2.5, 2),
    M("M037", "P04", "S2-R05", "bandeja", 48, 5, 1, 4, 1.3), M("M038", "P04", "S2-R05", "mesa", 53, 5, 3, 1.2, 0.9),
    M("M039", "P04", "S2-R05", "contenedor", 55, 10, 2, 2, 1.25),
    # P05
    M("M040", "P05", "S3-R02A", "jaula", 6, 7, 5, 6, 3, doorSide="E", doorAt=9), M("M041", "P05", "S3-R02A", "jaula", 16, 7, 5, 6, 3),
    M("M042", "P05", "S3-R02A", "jaula", 6, 19, 5, 6, 3), M("M043", "P05", "S3-R02A", "jaula", 16, 19, 5, 6, 3, doorSide="N", doorAt=16),
    M("M044", "P05", "S3-R02A", "biomonitor", 20, 12, 0.7, 1, 1.6),
    M("M045", "P05", "S3-R02B", "jaula", 30, 7, 5, 6, 3, doorSide="E", doorAt=8), M("M046", "P05", "S3-R02B", "jaula", 40, 7, 5, 6, 3),
    M("M047", "P05", "S3-R02B", "jaula", 30, 20, 5, 6, 3), M("M048", "P05", "S3-R02B", "jaula", 40, 20, 5, 6, 3),
    M("M049", "P05", "S3-R02B", "deposito", 44, 13, 1, 2, 2.2),
    M("M050", "P05", "S3-R05", "locker", 52, 5, 2, 0.8, 2), M("M051", "P05", "S3-R05", "barrera", 53, 11, 2, 1, 1.25),
    M("M052", "P05", "S3-R05", "consola", 60, 5, 1, 2, 1.1),
    M("M053", "P05", "S3-R01", "mostrador", 5, 39, 1.2, 8, 1.25), M("M054", "P05", "S3-R01", "sillas", 15, 46, 1, 6, 1.1),
    M("M055", "P05", "S3-R01", "dispensador", 5, 48, 1, 1, 2),
    M("M056", "P05", "S3-R03", "mesaq", 26, 37, 2, 3, 0.9), M("M057", "P05", "S3-R03", "mesaq", 35, 48, 2, 3, 0.9),
    M("M058", "P05", "S3-R03", "mampara", 33, 40, 0.2, 5, 1.8), M("M059", "P05", "S3-R03", "instrumental", 38, 36, 1, 2, 1.2),
    # FUR-M060-01: (50,33) invadía CP-04B (46,34; 1.5 m) y el vano de D21 → (51.5, 34.2); sigue separando observación y clínica
    M("M060", "P05", "S3-R04", "vidrio", 51.5, 34.2, 8, 0.15, 2.5), M("M061", "P05", "S3-R04", "consola", 46, 45, 2, 1, 1.1),
    M("M062", "P05", "S3-R04", "asiento", 53, 43, 1, 2, 1),
    # P06
    M("M063", "P06", "S4-R05", "rack", 5, 8, 1, 6, 2.5), M("M064", "P06", "S4-R05", "rack", 19, 15, 1, 6, 2.5),
    M("M065", "P06", "S4-R05", "consola", 12, 16, 4, 2, 1.25), M("M066", "P06", "S4-R05", "mapa", 12, 3, 5, 0.15, 2.2),
    M("M067", "P06", "S4-R02", "gabinete", 4, 45, 1.4, 0.6, 1.8), M("M068", "P06", "S4-R02", "banco", 9, 44, 2, 0.6, 0.5),
    M("M069", "P06", "S4-R02", "terminal", 4, 39, 1, 0.6, 1.2),
    M("M070", "P06", "S4-R01", "locker", 18, 39, 2, 0.7, 2), M("M071", "P06", "S4-R01", "barrera", 20, 46, 3, 1, 1.25),
    M("M072", "P06", "S4-R01", "mesa", 26, 39, 1, 3, 0.9),
    # M073–M076 pilares: ya existen en el blockout (plan.pillars)
    M("M077", "P06", "S4-R03", "archivos", 30, 15, 1, 5, 1.2), M("M078", "P06", "S4-R03", "archivos", 50, 6, 1, 4, 1.2),
    M("M079", "P06", "S4-R04", "asiento", 58, 5, 4, 0.7, 0.5), M("M080", "P06", "S4-R04", "panel", 66, 7, 0.4, 1.5, 1.6),
    M("M081", "P06", "S4-R04", "rejilla", 60, 19, 4, 0.2, 0.1),
]

def main():
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    plan["patrols"] = PATROLS
    plan["furniture"] = FURNITURE
    units = {s["id"] for s in plan["spawns"]}
    missing = [p["unit"] for p in PATROLS if p["unit"] not in units]
    assert not missing, f"unidades sin spawn: {missing}"
    PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"patrols={len(PATROLS)} furniture={len(FURNITURE)} -> {PLAN}")

if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    main()
