"""Baja texturas CC0 de Poly Haven (api.polyhaven.com) y las deja listas para HDRP.

Uso:  python tools/taller_final/polyhaven_fetch.py [--only id1 id2]

Por cada textura escribe en TallerFinal/Assets/_Project/Art/Textures/PolyHaven/<id>/:
  <id>_albedo.jpg   color base
  <id>_normal.jpg   normal en convencion OpenGL (la de Unity)
  <id>_mask.png     mascara de HDRP: R metal, G oclusion, B detalle, A suavidad (1 - rugosidad)
y anota cada descarga en TallerFinal/Docs/CREDITOS_polyhaven.tsv.
"""
import argparse
import io
import json
import os
import urllib.request

from PIL import Image, ImageOps

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "TallerFinal", "Assets", "_Project", "Art", "Textures", "PolyHaven")
CREDITS = os.path.join(ROOT, "TallerFinal", "Docs", "CREDITOS_polyhaven.tsv")
UA = {"User-Agent": "taller-final-unity/1.0"}

# id -> (resolucion, uso)
TEXTURES = {
    "leafy_grass": ("1k", "pasto de la pradera y la colina"),
    "coast_sand_01": ("1k", "arena de la playa"),
    "forest_leaves_02": ("1k", "suelo del bosque de palmeras"),
    "long_white_tiles": ("2k", "azulejo de la piscina y del cuarto"),
    "interior_tiles": ("1k", "piso del cuarto"),
    "velour_velvet": ("1k", "moqueta de la escalera"),
    "rough_linen": ("1k", "tela del sonador"),
    "cotton_jersey": ("1k", "cobija y cama"),
    "bark_willow": ("1k", "tronco del arbol monumental"),
    "palm_bark": ("1k", "troncos de palmera"),
    "white_planks_clean": ("1k", "puertas"),
    "marble_01": ("1k", "estatuas y base de piedra"),
    "painted_plaster_wall": ("1k", "paredes, techos y molduras pintadas"),
    "clean_pebbles": ("1k", "fondo del estanque y del vestibulo"),
    "mossy_stone_wall": ("1k", "paredes del pozo del jardin"),
    "metal_plate": ("1k", "pasamanos, postes y herrajes"),
    "dark_rock": ("1k", "paredes del tunel de la playa"),
}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return r.read()


def pick(files, key, res):
    m = files.get(key)
    if not m:
        return None
    m = m.get(res) or m.get("1k")
    for fmt in ("jpg", "png"):
        if m and fmt in m:
            return m[fmt]["url"]
    return None


def fetch(tid, res):
    files = json.loads(get(f"https://api.polyhaven.com/files/{tid}"))
    info = json.loads(get(f"https://api.polyhaven.com/info/{tid}"))
    folder = os.path.join(OUT, tid)
    os.makedirs(folder, exist_ok=True)
    albedo = Image.open(io.BytesIO(get(pick(files, "Diffuse", res)))).convert("RGB")
    albedo.save(os.path.join(folder, f"{tid}_albedo.jpg"), quality=92)
    normal = Image.open(io.BytesIO(get(pick(files, "nor_gl", res)))).convert("RGB")
    normal.save(os.path.join(folder, f"{tid}_normal.jpg"), quality=95)
    size = albedo.size
    arm_url = pick(files, "arm", res)
    if arm_url:
        arm = Image.open(io.BytesIO(get(arm_url))).convert("RGB").resize(size)
        ao, rough, metal = arm.split()
    else:
        rough = Image.open(io.BytesIO(get(pick(files, "Rough", res)))).convert("L").resize(size)
        ao_url = pick(files, "AO", res)
        ao = Image.open(io.BytesIO(get(ao_url))).convert("L").resize(size) if ao_url else Image.new("L", size, 255)
        metal = Image.new("L", size, 0)
    mask = Image.merge("RGBA", (metal, ao, Image.new("L", size, 255), ImageOps.invert(rough)))
    mask.save(os.path.join(folder, f"{tid}_mask.png"))
    authors = ", ".join(info.get("authors", {}).keys())
    return info.get("name", tid), authors


MODELS_OUT = os.path.join(ROOT, "TallerFinal", "Assets", "_Project", "Art", "Models", "PolyHaven")

# modelos 3D: id -> uso
MODELS = {
    "old_bed_frame": "cama de hierro del cuarto",
    "painted_wooden_nightstand": "mesa de noche",
    "alarm_clock_01": "reloj despertador",
    "ornate_mirror_01": "espejo del cuarto",
    "potted_plant_01": "planta en maceta",
    "modern_ceiling_lamp_01": "lampara de techo",
    # pradera
    "grass_medium_01": "pasto 3D de la pradera",
    "grass_medium_02": "pasto 3D de la pradera",
    "dandelion_01": "dientes de leon de la pradera",
    "flower_gazania": "flores de la pradera",
    "flower_heliophila": "flores de la pradera",
    "flower_ursinia": "flores de la pradera",
    "shrub_01": "arbustos de la pradera",
    "shrub_02": "arbustos de la pradera",
    "boulder_01": "roca de la pradera",
    "tree_stump_01": "tocon de la pradera",
    "painted_wooden_bench": "banca en medio de la pradera",
    # playa: sotobosque de jungla y rocas grandes
    "fern_02": "helechos de la playa",
    "shrub_03": "arbustos de la playa",
    "shrub_04": "arbustos de la playa",
    "nettle_plant": "plantas bajas de la playa",
    "coast_rocks_01": "rocas grandes de la playa",
    "coast_rocks_02": "rocas grandes de la playa",
    "namaqualand_boulder_02": "pena grande de la playa",
}


def fetch_model(mid):
    """FBX + albedo, normal GL y mascara HDRP compuesta (los EXR del FBX no se conectan solos en HDRP)."""
    files = json.loads(get(f"https://api.polyhaven.com/files/{mid}"))
    info = json.loads(get(f"https://api.polyhaven.com/info/{mid}"))
    folder = os.path.join(MODELS_OUT, mid)
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, f"{mid}.fbx"), "wb") as f:
        f.write(get(files["fbx"]["1k"]["fbx"]["url"]))
    # un modelo puede tener una sola parte ("Diffuse") o varias ("pot_diff", "leaves_diff"...)
    parts = [""] if "Diffuse" in files else sorted(k[:-4] for k in files if k.endswith("_diff"))
    for part in parts:
        tag = f"{mid}_{part[:-1]}" if part else mid
        diff = pick(files, "Diffuse", "1k") if not part else pick(files, part + "diff", "1k")
        albedo = Image.open(io.BytesIO(get(diff))).convert("RGB")
        size = albedo.size
        alpha = pick(files, part + "alpha", "1k") or (pick(files, "opacity", "1k") or pick(files, "alpha", "1k") or pick(files, "Alpha", "1k") if not part else None)
        if alpha and not mid.startswith("alarm_clock"):      # hojas/pasto recortados: el alfa va dentro del albedo
            a = Image.open(io.BytesIO(get(alpha))).convert("L").resize(size)
            albedo.putalpha(a)
            albedo.save(os.path.join(folder, f"{tag}_albedo.png"))
        else:
            albedo.save(os.path.join(folder, f"{tag}_albedo.jpg"), quality=92)
        n = pick(files, part + "nor_gl", "1k")
        if n:
            Image.open(io.BytesIO(get(n))).convert("RGB").resize(size).save(os.path.join(folder, f"{tag}_normal.jpg"), quality=95)
        arm_url = pick(files, part + "arm", "1k")
        if arm_url:
            ao, rough, metal = Image.open(io.BytesIO(get(arm_url))).convert("RGB").resize(size).split()
        else:
            ru = pick(files, part + "rough", "1k"); au = pick(files, part + "ao", "1k")
            rough = Image.open(io.BytesIO(get(ru))).convert("L").resize(size) if ru else Image.new("L", size, 160)
            ao = Image.open(io.BytesIO(get(au))).convert("L").resize(size) if au else Image.new("L", size, 255)
            metal = Image.new("L", size, 0)
        Image.merge("RGBA", (metal, ao, Image.new("L", size, 255), ImageOps.invert(rough))).save(os.path.join(folder, f"{tag}_mask.png"))
    return info.get("name", mid), ", ".join(info.get("authors", {}).keys())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--models", action="store_true", help="bajar solo los modelos 3D")
    args = ap.parse_args()
    if args.models:
        rows = []
        for mid, use in MODELS.items():
            if args.only and mid not in args.only:
                continue
            name, authors = fetch_model(mid)
            rows.append(f"{mid}\t{name} (modelo)\t{authors}\tCC0\t1k\t{use}\thttps://polyhaven.com/a/{mid}")
            print("ok", mid, authors)
        with open(CREDITS, "a", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(rows) + "\n")
        return
    rows = []
    for tid, (res, use) in TEXTURES.items():
        if args.only and tid not in args.only:
            continue
        name, authors = fetch(tid, res)
        rows.append(f"{tid}\t{name}\t{authors}\tCC0\t{res}\t{use}\thttps://polyhaven.com/a/{tid}")
        print("ok", tid, res, authors)
    if args.only:                                   # solo algunas: se agregan sin borrar los creditos anteriores
        with open(CREDITS, "a", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(rows) + "\n")
        return
    with open(CREDITS, "w", encoding="utf-8", newline="\n") as f:
        f.write("id\tnombre\tautores\tlicencia\tresolucion\tuso\tfuente\n" + "\n".join(rows) + "\n")


if __name__ == "__main__":
    main()
