"""Create original, tileable runtime maps for the monumental-tree scene.

The small source crops are preserved as visual evidence. These larger maps
reconstruct clean material response instead of repeating baked phone pixels.
This script uses only Python's standard library; Blender remains the scene
authoring tool.
"""
from __future__ import annotations

import math
import random
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "textures" / "monumental_tree"
SIZE = 512


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def hash2(x: int, y: int) -> float:
    n = (x * 374761393 + y * 668265263) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    n ^= n >> 16
    return n / 4294967295.0


def value_noise(x: float, y: float, period: int) -> float:
    x *= period
    y *= period
    x0, y0 = math.floor(x), math.floor(y)
    fx, fy = x - x0, y - y0
    fx = fx * fx * (3 - 2 * fx)
    fy = fy * fy * (3 - 2 * fy)
    # Wrap the lattice itself so every authored map tiles cleanly. A smooth
    # blend of unrelated edge values becomes a visible checker seam in a lawn.
    x0w, y0w = x0 % period, y0 % period
    a = hash2(x0w, y0w)
    b = hash2((x0w + 1) % period, y0w)
    c = hash2(x0w, (y0w + 1) % period)
    d = hash2((x0w + 1) % period, (y0w + 1) % period)
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


def write_bmp(path: Path, pixels: list[tuple[int, int, int]], width: int, height: int) -> None:
    stride = (width * 3 + 3) & ~3
    rows = bytearray()
    for y in range(height):
        row = bytearray()
        for x in range(width):
            r, g, b = pixels[y * width + x]
            row.extend((b, g, r))
        row.extend(b"\0" * (stride - width * 3))
        rows.extend(row)
    header = struct.pack("<2sIHHI", b"BM", 54 + len(rows), 0, 0, 54)
    info = struct.pack("<IiiHHIIiiII", 40, width, height, 1, 24, 0, len(rows), 2835, 2835, 0, 0)
    path.write_bytes(header + info + rows)


def rgb8(r: float, g: float, b: float) -> tuple[int, int, int]:
    return tuple(round(clamp(v) * 255) for v in (r, g, b))


def generate() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rng = random.Random(5102026)
    bark_height: list[float] = []
    bark: list[tuple[int, int, int]] = []
    bark_rough: list[tuple[int, int, int]] = []
    grass: list[tuple[int, int, int]] = []
    grass_height: list[float] = []
    grass_rough: list[tuple[int, int, int]] = []
    leaf: list[tuple[int, int, int]] = []

    for y in range(SIZE):
        v = y / SIZE
        for x in range(SIZE):
            u = x / SIZE
            broad = value_noise(u, v, 8)
            mid = value_noise(u, v, 27)
            fine = value_noise(u, v, 97)
            warp = value_noise(u, v, 7) - .5
            phase = u * 4.0 + .12 * math.sin(2.0 * math.pi * (v + u)) + warp * .16
            groove = math.sin(2 * math.pi * phase)
            ridge = max(0.0, groove) ** 1.8
            fissure = max(0.0, -groove - 0.46)
            height = clamp(0.46 + ridge * 0.18 + broad * 0.10 + mid * 0.06 + fine * 0.035 - fissure * 0.10)
            bark_height.append(height)
            value = clamp(0.58 + ridge * 0.12 + broad * 0.08 + mid * 0.065 + fine * 0.04 - fissure * 0.12)
            # Gray-brown limestone bark with the bright, sunlit ridges visible
            # in the reference rather than a flat silver material.
            bark.append(rgb8(value * 0.95, value * 0.94, value * 0.90))
            bark_rough.append(rgb8(0.78 + mid * 0.17 + fine * 0.05, 0.78 + mid * 0.17 + fine * 0.05, 0.78 + mid * 0.17 + fine * 0.05))

            g_broad = value_noise(u, v, 6)
            g_mid = value_noise(u, v, 34)
            g_fine = value_noise(u, v, 126)
            blades = math.sin((u * 19.0 + math.sin(v * 11.0) * 0.04) * 2.0 * math.pi) * 0.008
            gh = clamp(0.48 + (g_broad - 0.5) * 0.30 + (g_mid - 0.5) * 0.16 + (g_fine - 0.5) * 0.09 + blades)
            grass_height.append(gh)
            green = clamp(0.30 + g_broad * 0.15 + g_mid * 0.08 + g_fine * 0.045)
            grass.append(rgb8(green * 0.72, green * 1.12, green * 0.39))
            grass_rough.append(rgb8(0.89 + g_mid * 0.08 + g_fine * 0.03, 0.89 + g_mid * 0.08 + g_fine * 0.03, 0.89 + g_mid * 0.08 + g_fine * 0.03))

            l_broad = value_noise(u, v, 11)
            l_mid = value_noise(u, v, 52)
            l_fine = value_noise(u, v, 177)
            l = clamp(0.40 + l_broad * 0.34 + l_mid * 0.14 + l_fine * 0.10)
            # Keep the canopy deep and cool, with restrained olive highlights.
            leaf.append(rgb8(l * 0.55, l * 0.90, l * 0.36))

    def normal_from_height(values: list[float], scale: float, strength: float) -> list[tuple[int, int, int]]:
        out = []
        for y in range(SIZE):
            yp, yn = (y + 1) % SIZE, (y - 1) % SIZE
            for x in range(SIZE):
                xp, xn = (x + 1) % SIZE, (x - 1) % SIZE
                dx = (values[y * SIZE + xp] - values[y * SIZE + xn]) * scale * strength
                dy = (values[yp * SIZE + x] - values[yn * SIZE + x]) * scale * strength
                length = math.sqrt(dx * dx + dy * dy + 1)
                out.append(rgb8(0.5 - dx / length * 0.5, 0.5 - dy / length * 0.5, 0.5 + 0.5 / length))
        return out

    write_bmp(OUT / "bark_albedo.bmp", bark, SIZE, SIZE)
    write_bmp(OUT / "bark_normal.bmp", normal_from_height(bark_height, 3.0, 0.55), SIZE, SIZE)
    write_bmp(OUT / "bark_roughness.bmp", bark_rough, SIZE, SIZE)
    write_bmp(OUT / "foliage_albedo.bmp", leaf, SIZE, SIZE)
    write_bmp(OUT / "grass_albedo.bmp", grass, SIZE, SIZE)
    write_bmp(OUT / "grass_normal.bmp", normal_from_height(grass_height, 7.0, 0.6), SIZE, SIZE)
    write_bmp(OUT / "grass_roughness.bmp", grass_rough, SIZE, SIZE)

    sky = []
    for y in range(SIZE):
        elevation = y / (SIZE - 1)
        for x in range(SIZE):
            # A high-saturation, cloudless blue gradient matching the frame.
            if elevation < 0.38:
                t = elevation / 0.38
                a, b = (0.12, 0.30, 0.65), (0.09, 0.39, 0.83)
            else:
                t = (elevation - 0.38) / 0.62
                a, b = (0.09, 0.39, 0.83), (0.035, 0.20, 0.57)
            sky.append(rgb8(*(a[i] * (1 - t) + b[i] * t for i in range(3))))
    write_bmp(OUT / "clear_blue_sky.bmp", sky, SIZE, SIZE)
    write_bmp(OUT / "sky_linear_probe.bmp", sky, SIZE, SIZE)
    write_bmp(OUT / "foliage_mask.bmp", [(c[1], c[1], c[1]) for c in leaf], SIZE, SIZE)
    write_bmp(OUT / "neutral_aux.bmp", [(180, 180, 180)] * (SIZE * SIZE), SIZE, SIZE)

    print(f"Wrote original 512x512 tree maps to {OUT}")


if __name__ == "__main__":
    generate()
