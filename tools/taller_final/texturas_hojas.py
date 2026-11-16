"""Texturas de follaje que Poly Haven no tiene: seto podado, hoja de palmera y nenufar.

Uso: python tools/taller_final/texturas_hojas.py
Escribe en TallerFinal/Assets/_Project/Art/Textures/Generadas/:
  T_Seto_albedo.png / T_Seto_normal.png    seto podado: miles de hojitas superpuestas, repetible sin costura
  T_Palmera_albedo.png                     hoja de palmera (RGBA): nervio central y foliolos que caen, alfa recortable
  T_Nenufar_albedo.png                     nenufar (RGBA): disco con muesca, nervaduras radiales y borde mas claro
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "TallerFinal", "Assets", "_Project", "Art", "Textures", "Generadas")
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(7)


def hedge(n=1024):
    """Hojitas elipticas al azar, cada una con su tono y una altura (para la normal); se dibuja con envoltura."""
    col = Image.new("RGB", (n, n), (22, 40, 20))
    hgt = Image.new("L", (n, n), 0)
    dc, dh = ImageDraw.Draw(col), ImageDraw.Draw(hgt)
    for _ in range(26000):
        x, y = rng.random() * n, rng.random() * n
        L, W = 10 + rng.random() * 14, 5 + rng.random() * 6
        a = rng.random() * math.pi
        depth = rng.random()
        g = 0.55 + 0.45 * depth
        c = (int((38 + rng.random() * 30) * g), int((78 + rng.random() * 50) * g), int((30 + rng.random() * 22) * g))
        pts = [(math.cos(t) * L, math.sin(t) * W) for t in np.linspace(0, 2 * math.pi, 10)]
        for ox in (-n, 0, n):
            for oy in (-n, 0, n):
                if not (-30 < x + ox < n + 30 and -30 < y + oy < n + 30):
                    continue
                poly = [(x + ox + px * math.cos(a) - py * math.sin(a), y + oy + px * math.sin(a) + py * math.cos(a)) for px, py in pts]
                dc.polygon(poly, fill=c)
                dh.polygon(poly, fill=int(60 + 195 * depth))
    hgt = hgt.filter(ImageFilter.GaussianBlur(1.2))
    h = np.asarray(hgt, dtype=np.float32) / 255.0
    dx = np.roll(h, -1, 1) - np.roll(h, 1, 1)
    dy = np.roll(h, -1, 0) - np.roll(h, 1, 0)
    nrm = np.dstack((-dx * 3.0, dy * 3.0, np.ones_like(h)))
    nrm /= np.linalg.norm(nrm, axis=2, keepdims=True)
    col.save(os.path.join(OUT, "T_Seto_albedo.png"))
    Image.fromarray(((nrm * 0.5 + 0.5) * 255).astype(np.uint8)).save(os.path.join(OUT, "T_Seto_normal.png"))


def palm(w=512, h=2048):
    """Hoja de palmera a lo largo de V: nervio en el centro, foliolos que salen en diagonal y se afinan."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = w / 2
    for i in range(110):
        t = i / 110.0
        y = h * (0.02 + 0.96 * t)
        length = (w * 0.48) * math.sin(math.pi * min(1.0, t * 1.05)) ** 0.6
        for s in (-1, 1):
            tip = (cx + s * length, y + h * 0.05)
            wid = 9 * (1 - 0.6 * t)
            g = 0.75 + 0.25 * rng.random()
            c = (int(44 * g), int(98 * g), int(40 * g), 255)
            d.polygon([(cx, y - wid), (tip[0], tip[1]), (cx, y + wid)], fill=c)
            d.line([(cx, y), tip], fill=(int(70 * g), int(130 * g), int(60 * g), 255), width=1)
    d.line([(cx, 0), (cx, h)], fill=(120, 140, 70, 255), width=6)
    img.save(os.path.join(OUT, "T_Palmera_albedo.png"))


def lily(n=1024):
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c, r = n / 2, n * 0.47
    d.ellipse([c - r, c - r, c + r, c + r], fill=(52, 104, 52, 255))
    d.ellipse([c - r * 0.93, c - r * 0.93, c + r * 0.93, c + r * 0.93], fill=(64, 122, 58, 255))
    for k in range(28):                                       # nervaduras radiales
        a = 2 * math.pi * k / 28
        d.line([(c, c), (c + math.cos(a) * r * 0.95, c + math.sin(a) * r * 0.95)], fill=(88, 150, 76, 255), width=3)
    d.polygon([(c, c), (c + r * 1.1 * math.cos(-0.18), c + r * 1.1 * math.sin(-0.18)),
               (c + r * 1.1 * math.cos(0.18), c + r * 1.1 * math.sin(0.18))], fill=(0, 0, 0, 0))   # la muesca
    arr = np.asarray(img).astype(np.float32)
    noise = rng.random((n, n)) * 18 - 9
    arr[..., :3] = np.clip(arr[..., :3] + noise[..., None], 0, 255)
    Image.fromarray(arr.astype(np.uint8)).save(os.path.join(OUT, "T_Nenufar_albedo.png"))


def foam(n=1024, cells=150):
    """Espuma densa para las nubes de algodon: burbujas apretadas de varios tamanos (distancia a la celda mas
    cercana, repetible sin costura). Blanco con grietas grises suaves y su mapa de normales (domos)."""
    pts = rng.random((cells, 2)) * n
    rad = 0.6 + rng.random(cells) * 0.8
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    best = np.full((n, n), 1e9, np.float32)
    second = np.full((n, n), 1e9, np.float32)
    for (px, py), r in zip(pts, rad):
        for ox in (-n, 0, n):
            for oy in (-n, 0, n):
                d = np.hypot(xx - px - ox, yy - py - oy) / r
                m = d < best
                second = np.where(m, best, np.minimum(second, d))
                best = np.where(m, d, best)
    dome = np.clip((second - best) / (second + best + 1e-3), 0, 1) ** 0.45   # domo redondo, 0 en el borde entre burbujas
    small = np.asarray(Image.fromarray((rng.random((256, 256)) * 255).astype(np.uint8)).resize((n, n), Image.BICUBIC), np.float32) / 255
    h = dome * 0.85 + small * 0.15
    alb = 0.84 + 0.16 * dome
    Image.fromarray((np.dstack((alb, alb, alb)) * 255).astype(np.uint8)).save(os.path.join(OUT, "T_Espuma_albedo.png"))
    dx = np.roll(h, -1, 1) - np.roll(h, 1, 1)
    dy = np.roll(h, -1, 0) - np.roll(h, 1, 0)
    nrm = np.dstack((-dx * 6.0, dy * 6.0, np.ones_like(h)))
    nrm /= np.linalg.norm(nrm, axis=2, keepdims=True)
    Image.fromarray(((nrm * 0.5 + 0.5) * 255).astype(np.uint8)).save(os.path.join(OUT, "T_Espuma_normal.png"))


import sys
if "--espuma" in sys.argv:
    foam(cells=340)
    print("ok espuma", OUT)
    sys.exit(0)
hedge()
palm()
lily()
foam(cells=340)
print("ok", OUT)
