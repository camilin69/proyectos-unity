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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*")
    args = ap.parse_args()
    rows = []
    for tid, (res, use) in TEXTURES.items():
        if args.only and tid not in args.only:
            continue
        name, authors = fetch(tid, res)
        rows.append(f"{tid}\t{name}\t{authors}\tCC0\t{res}\t{use}\thttps://polyhaven.com/a/{tid}")
        print("ok", tid, res, authors)
    with open(CREDITS, "w", encoding="utf-8", newline="\n") as f:
        f.write("id\tnombre\tautores\tlicencia\tresolucion\tuso\tfuente\n" + "\n".join(rows) + "\n")


if __name__ == "__main__":
    main()
