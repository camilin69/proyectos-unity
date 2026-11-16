"""Luna llena detallada y los cielos de noche del final.

Uso: python tools/taller_final/cielos_noche.py
Escribe en TallerFinal/Assets/_Project/Art/Textures/PolyHaven/HDRI/:
  T_Luna_llena.png        disco de luna llena (2048): mares oscuros, crateres con borde y rayos, limbo un poco mas oscuro
  dream_noche_morada.png  equirectangular 4096x2048: morado profundo con muchisimas estrellas brillantes (la escalera)
  dream_noche_rosa.png    equirectangular 4096x2048: rosa de madrugada con estrellas suaves (el cuarto a las 3:33)
Los cielos se usan como emision del espacio del Physically Based Sky, asi la luna (cuerpo celeste) se dibuja encima.
"""
import os

import numpy as np
from PIL import Image, ImageFilter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "TallerFinal", "Assets", "_Project", "Art", "Textures", "PolyHaven", "HDRI")
rng = np.random.default_rng(33)


def fbm(n, octaves=6, seed=0):
    r = np.random.default_rng(seed)
    acc = np.zeros((n, n))
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        size = 4 * 2 ** o
        g = r.random((size, size))
        img = Image.fromarray((g * 255).astype(np.uint8)).resize((n, n), Image.BICUBIC)
        acc += np.asarray(img, dtype=np.float32) / 255.0 * amp
        tot += amp
        amp *= 0.55
    return acc / tot


def moon(n=2048):
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    cx = cy = n / 2
    r = n * 0.49
    d = np.hypot(xx - cx, yy - cy) / r
    base = 0.72 + 0.12 * (fbm(n, 7, 1) - 0.5)
    maria = np.clip((fbm(n, 4, 2) - 0.47) * 6.0, 0, 1) ** 1.1          # mares: manchas grandes y oscuras
    alb = base - 0.40 * maria
    for _ in range(260):                                                 # crateres con borde claro y fondo oscuro
        px, py = rng.random(2) * n
        cr = (rng.random() ** 4) * n * 0.05 + 2
        x0, x1 = int(max(0, px - cr * 1.7)), int(min(n, px + cr * 1.7))
        y0, y1 = int(max(0, py - cr * 1.7)), int(min(n, py + cr * 1.7))
        if x1 <= x0 or y1 <= y0:
            continue
        dd = np.hypot(xx[y0:y1, x0:x1] - px, yy[y0:y1, x0:x1] - py) / cr
        sub = alb[y0:y1, x0:x1]
        sub += np.where(dd < 1.0, -0.05 * np.sqrt(np.clip(1 - dd, 0, 1)), 0.02 * np.exp(-((dd - 1.05) / 0.25) ** 2))
    for _ in range(3):                                                   # rayos de los crateres jovenes
        px, py = rng.random(2) * n
        ang = np.arctan2(yy - py, xx - px)
        dist = np.hypot(xx - px, yy - py)
        rays = np.clip(np.cos(ang * rng.integers(9, 17) + rng.random() * 6) * 1.4 - 0.7, 0, 1) * np.exp(-dist / (n * 0.12))
        alb += 0.07 * rays
    alb = np.asarray(Image.fromarray((np.clip(alb, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2.2)), dtype=np.float32) / 255
    limb = np.clip(1 - d ** 2, 0, 1) ** 0.25                             # el borde un poco mas oscuro
    v = np.clip(alb * (0.75 + 0.25 * limb), 0, 1)
    alpha = np.clip((1 - d) * n * 0.01, 0, 1)
    img = np.dstack((v * 0.98, v * 0.97, v * 1.0, alpha))
    Image.fromarray((img * 255).astype(np.uint8), "RGBA").save(os.path.join(OUT, "T_Luna_llena.png"))


def sky(name, stops, n_stars, star_gain):
    W, H = 4096, 2048
    v = np.linspace(0, 1, H)[:, None]
    e = np.broadcast_to((0.5 - v) * 180.0, (H, W))
    img = np.zeros((H, W, 3))
    for (e0, c0), (e1, c1) in zip(stops[:-1], stops[1:]):
        m = (e <= e0) & (e >= e1)
        t = ((e0 - e) / (e0 - e1))[m]
        for k in range(3):
            img[..., k][m] = c0[k] + (c1[k] - c0[k]) * t
    neb = np.asarray(Image.fromarray((fbm(1024, 6, 9) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), dtype=np.float32) / 255
    img *= (0.85 + 0.3 * neb)[..., None]                                 # nebulosas suaves
    sy = (rng.random(n_stars) ** 1.2) * H * 0.5
    sx = rng.random(n_stars) * W
    star = np.zeros((H, W))
    b = rng.random(n_stars) ** 4 * star_gain
    star[sy.astype(int), sx.astype(int)] = b
    star = np.asarray(Image.fromarray(np.clip(star * 255, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.7)), dtype=np.float32) / 255 * 2.2
    img += star[..., None] * np.array([0.95, 0.92, 1.0])
    Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).save(os.path.join(OUT, name))


moon()
sky("dream_noche_morada.png", [(90, (0.05, 0.02, 0.14)), (40, (0.16, 0.06, 0.32)), (10, (0.36, 0.14, 0.52)), (0, (0.55, 0.25, 0.62)),
                               (-90, (0.10, 0.04, 0.18))], 26000, 1.0)
sky("dream_noche_rosa.png", [(90, (0.16, 0.06, 0.20)), (45, (0.36, 0.14, 0.34)), (12, (0.62, 0.30, 0.48)), (0, (0.85, 0.50, 0.62)),
                              (-90, (0.20, 0.08, 0.18))], 9000, 0.6)
print("ok", OUT)
