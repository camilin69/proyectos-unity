"""Create small, explicit RGB24 maps consumed by the native DREAM renderer.

Original PNGs remain the editable source of truth. Pillow is supplied by the
configured Blender Python runtime, but this script does not start Blender or
alter any scene.
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets/textures/ocean_exit"
OUTPUT = ROOT / "assets/textures/ocean_exit_runtime"
OUTPUT.mkdir(parents=True, exist_ok=True)


def rgb24(source: str, target: str) -> None:
    image = Image.open(SOURCE / source).convert("RGB")
    image.save(OUTPUT / target, format="BMP")


def normal_from_height(source: str, target: str, strength: float) -> None:
    height = Image.open(SOURCE / source).convert("L")
    pixels = height.load()
    width, height_px = height.size
    output = Image.new("RGB", height.size)
    normals = output.load()
    for y in range(height_px):
        ym, yp = (y - 1) % height_px, (y + 1) % height_px
        for x in range(width):
            xm, xp = (x - 1) % width, (x + 1) % width
            dx = (pixels[xp, y] - pixels[xm, y]) * (strength / 255.0)
            dy = (pixels[x, yp] - pixels[x, ym]) * (strength / 255.0)
            nx, ny, nz = -dx, -dy, 1.0
            length = (nx * nx + ny * ny + nz * nz) ** 0.5
            normals[x, y] = tuple(
                max(0, min(255, round((value / length * 0.5 + 0.5) * 255)))
                for value in (nx, ny, nz)
            )
    output.save(OUTPUT / target, format="BMP")


rgb24("sunset_stars_v2.png", "ocean_sky.bmp")
rgb24("pink_tile_albedo.png", "ocean_tile.bmp")
rgb24("pink_tile_roughness.png", "ocean_tile_roughness.bmp")
normal_from_height("pink_tile_height.png", "ocean_tile_normal.bmp", 18.0)
rgb24("foam_mask.png", "ocean_foam.bmp")
rgb24("exit_lamp.png", "ocean_exit_lamp.bmp")
rgb24("exit_here.png", "ocean_exit_here.bmp")
normal_from_height("ripple_height.png", "ocean_ripple_normal.bmp", 6.0)

for path in sorted(OUTPUT.glob("*.bmp")):
    with Image.open(path) as image:
        if image.mode != "RGB" or image.size[0] > 8192 or image.size[1] > 8192:
            raise RuntimeError(f"Unexpected runtime texture format: {path}")
        print(f"{path.relative_to(ROOT)} {image.width}x{image.height}")
