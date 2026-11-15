"""Cielo de atardecer morado con cometa (video 42 de dream/, 6-12 s), como panorama equirectangular 4096x2048.

Uso: python tools/taller_final/cielo_atardecer_cometa.py
Escribe TallerFinal/Assets/_Project/Art/Textures/PolyHaven/HDRI/dream_atardecer_cometa.png.

Arriba violeta profundo lleno de estrellas; hacia el horizonte lila, magenta y una franja rosa-durazno; debajo del
horizonte, el mar casi negro. El cometa (nucleo blanco y una cola larga y suave que se abre) esta en u=0.5, unos
22 grados sobre el horizonte; en Unity se gira el cielo para que quede frente a la puerta del vestibulo.
"""
import os

import numpy as np
from PIL import Image

W, H = 4096, 2048
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "TallerFinal", "Assets", "_Project", "Art", "Textures", "PolyHaven", "HDRI", "dream_atardecer_cometa.png")

v = np.linspace(0.0, 1.0, H)[:, None]            # 0 arriba, 1 abajo
u = np.linspace(0.0, 1.0, W)[None, :]
e = np.broadcast_to((0.5 - v) * 180.0, (H, W))   # grados sobre el horizonte

stops = [  # elevacion, color (0-1)
    (90, (0.07, 0.06, 0.20)),
    (55, (0.16, 0.12, 0.38)),
    (30, (0.34, 0.22, 0.55)),
    (14, (0.58, 0.32, 0.66)),
    (6, (0.86, 0.42, 0.66)),
    (2, (0.98, 0.62, 0.62)),
    (0, (1.00, 0.78, 0.62)),
    (-1, (0.20, 0.16, 0.30)),
    (-90, (0.02, 0.03, 0.06)),
]
img = np.zeros((H, W, 3))
for (e0, c0), (e1, c1) in zip(stops[:-1], stops[1:]):
    m = (e <= e0) & (e >= e1)
    t = ((e0 - e) / (e0 - e1))[m]
    for k in range(3):
        img[..., k][m] = c0[k] + (c1[k] - c0[k]) * t

# el resplandor del atardecer es mas fuerte hacia donde se fue el sol (u ~ 0.5, detras del cometa)
glow = np.exp(-((u - 0.5) ** 2) / (2 * 0.12 ** 2)) * np.exp(-np.clip(e, 0, None) / 10.0) * (e > -1)
img += glow[..., None] * np.array([0.35, 0.12, 0.2])

# estrellas: mas densas y brillantes arriba, se apagan en el resplandor
rng = np.random.default_rng(42)
n = 9000
sy = (rng.random(n) ** 1.4) * (H * 0.47)
sx = rng.random(n) * W
for x, y in zip(sx.astype(int), sy.astype(int)):
    el = (0.5 - y / H) * 180
    b = rng.random() ** 3 * 0.9 * min(1.0, (el - 4) / 25.0)
    if b <= 0:
        continue
    r = 1 if rng.random() < 0.85 else 2
    img[max(0, y - r + 1):y + r, max(0, x - r + 1):x + r] += b * np.array([0.95, 0.92, 1.0])

# el cometa: nucleo a 22 grados en u=0.5; cola curva hacia arriba a la izquierda que se abre y se desvanece
cx, cy = 0.5 * W, (0.5 - 22 / 180) * H
yy, xx = np.mgrid[0:H, 0:W]
d_core = np.hypot(xx - cx, yy - cy)
img += (np.exp(-(d_core / 3.0) ** 2) * 3.0 + np.exp(-(d_core / 14.0) ** 2) * 0.5)[..., None] * np.array([1.0, 0.98, 1.0])
for i in range(1, 260):
    t = i / 260.0
    px = cx - t * 330.0
    py = cy - t * 150.0 - 40.0 * t * t
    width = 2.0 + 24.0 * t
    a = (1.0 - t) ** 1.6 * 0.07
    sub = (slice(int(max(0, py - width * 3)), int(min(H, py + width * 3))), slice(int(max(0, px - width * 3)), int(min(W, px + width * 3))))
    d = np.hypot(xx[sub] - px, yy[sub] - py)
    img[sub] += (np.exp(-(d / width) ** 2) * a)[..., None] * np.array([0.85, 0.9, 1.0])

img = np.clip(img, 0.0, 1.0) ** (1 / 1.05)
Image.fromarray((img * 255).astype(np.uint8)).save(OUT)
print("ok", OUT)
