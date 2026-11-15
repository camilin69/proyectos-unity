"""Own kitchen textures only; standalone Python, numpy/scipy/Pillow.

Creates original procedural maps, never edits the supplied reference crops.
Maps are look-development candidates until checked in the real kitchen scene.
PNG/BMP pixels agree; color maps are sRGB and normal maps are linear data.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import sys

sys.dont_write_bytecode = True

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import gaussian_filter, map_coordinates

ROOT = Path(__file__).resolve().parents[1]
GRASS_PERIOD_M = 4.0
GRASS_NORMAL_STRENGTH = 0.24


def periodic_noise(size, sigma, rng):
    a = gaussian_filter(rng.normal(size=(size, size)), sigma, mode='wrap')
    return a / max(a.std(), 1e-12)


def grass_maps(size=1024, seed=42021):
    rng = np.random.default_rng(seed)
    broad = periodic_noise(size, size/18, rng)
    medium = periodic_noise(size, size/75, rng)
    small = periodic_noise(size, size/300, rng)
    # Short irregular strokes suggest tangled blades; no directional lawn rows.
    strokes = Image.new('L', (size, size), 128)
    draw = ImageDraw.Draw(strokes)
    for _ in range(round(62000*(size/1024)**2)):
        x, y = rng.uniform(0, size, 2)
        angle = rng.uniform(0, math.tau)
        length = rng.uniform(3, 14)*size/1024
        dx, dy = math.cos(angle)*length, math.sin(angle)*length
        value = int(rng.uniform(82, 183))
        for ox in (-size, 0, size):
            for oy in (-size, 0, size):
                if -length < x+ox < size+length and -length < y+oy < size+length:
                    draw.line((x+ox, y+oy, x+dx+ox, y+dy+oy), fill=value,
                              width=max(1, round(size/1024)))
    blade = gaussian_filter(np.asarray(strokes, dtype=float), .55, mode='wrap')-128
    color = (np.array([112., 140., 95.]) + broad[..., None]*np.array([7., 8., 4.])
             + medium[..., None]*np.array([6., 7., 4.])
             + small[..., None]*np.array([2.5, 3., 2.])
             + blade[..., None]*np.array([.32, .30, .23]))
    color = np.uint8(np.clip(np.rint(color), 0, 255))
    # Actual height field in metres; this is separate from any lighting/AO.
    height = broad*.0015 + medium*.0008 + small*.00035 + blade*.000035
    spacing = GRASS_PERIOD_M/size
    dx = (np.roll(height, -1, 1)-np.roll(height, 1, 1))/(2*spacing)
    dy_row = (np.roll(height, -1, 0)-np.roll(height, 1, 0))/(2*spacing)
    normal = np.dstack((-dx, dy_row, np.ones_like(height)))
    normal /= np.linalg.norm(normal, axis=-1, keepdims=True)
    encoded = np.uint8(np.clip(np.rint((normal*.5+.5)*255), 0, 255))
    for a in (color, encoded):
        a[-1] = a[0]
        a[:, -1] = a[:, 0]
    return color, encoded


def sky_map(width=2048, height=1024):
    # Reuse only the pure volume integrator, not the room's active sky/layout.
    from make_cloud_sky import cloud_volume
    elevation = np.linspace(90, -90, height)[:, None]
    lower = np.array([135., 157., 231.])
    cyan = np.array([91., 201., 233.])
    zenith = np.array([74., 164., 217.])
    t = np.clip(elevation/16, 0, 1)[..., None]
    rgb = lower*(1-t)+cyan*t
    high = np.clip((elevation-20)/70, 0, 1)[..., None]
    rgb = rgb*(1-high)+zenith*high
    rgb = np.repeat(rgb, width, axis=1)
    haze = np.exp(-((elevation-1.3)/4.0)**2)[..., None]*.38
    rgb = rgb*(1-haze)+np.array([139., 145., 216.])*haze
    panorama = Image.fromarray(np.uint8(rgb), 'RGB').convert('RGBA')
    stamps = []
    for seed in (42041, 42043, 42047, 42049):
        cloud = cloud_volume(seed, (48, 64, 112)).astype(float)
        lighting = np.clip((cloud[..., 0]-151)/102, 0, 1)[..., None]
        cloud[..., :3] = np.array([127., 132., 210.])*(1-lighting)+np.array([229., 190., 236.])*lighting
        cloud[..., 3] *= .90
        stamps.append(Image.fromarray(np.uint8(cloud), 'RGBA'))
    # Low overlapping bank encircles the meadow, with a clear cyan upper sky.
    # Its angular silhouette reaches approximately 8-10 degrees above horizon.
    rng = np.random.default_rng(42053)
    for i in range(18):
        u = (i+.3)/18
        elevation_center = 2.7+rng.uniform(-.6, .6)
        angular_width = rng.uniform(30, 39)
        angular_height = rng.uniform(10, 13)
        size = (round(width*angular_width/360), round(height*angular_height/180))
        stamp = stamps[i % len(stamps)].resize(size, Image.Resampling.LANCZOS)
        if i % 2:
            stamp = stamp.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        stamp = stamp.filter(ImageFilter.GaussianBlur(.4))
        x = round(u*width-size[0]/2)
        y = round((.5-elevation_center/180)*height-size[1]/2)
        for offset in (-width, 0, width):
            if x+offset < width and x+offset+size[0] > 0:
                panorama.alpha_composite(stamp, (x+offset, y))
    out = np.asarray(panorama.convert('RGB')).copy()
    out[:, -1] = out[:, 0]
    out[0] = out[0].mean(axis=0)
    out[-1] = out[-1].mean(axis=0)
    return out


def perspective(sky, yaw=1.53, pitch=-.12, tan_half_fov=.65, size=(478, 850)):
    w, h = size
    forward = np.array([math.cos(yaw)*math.cos(pitch), math.sin(yaw)*math.cos(pitch), math.sin(pitch)])
    right = np.cross(forward, [0, 0, 1]);right /= np.linalg.norm(right)
    up = np.cross(right, forward)
    x, y = np.meshgrid((np.arange(w)+.5)/w*2-1, 1-(np.arange(h)+.5)/h*2)
    d = forward+x[..., None]*right*(w/h)*tan_half_fov+y[..., None]*up*tan_half_fov
    d /= np.linalg.norm(d, axis=-1, keepdims=True)
    u = (np.arctan2(d[..., 1], d[..., 0])/(2*np.pi)+.5)*(sky.shape[1]-1)
    v = (.5-np.arcsin(d[..., 2])/np.pi)*(sky.shape[0]-1)
    return np.uint8(np.stack([map_coordinates(sky[..., c], [v, u], order=1, mode='nearest') for c in range(3)], axis=-1))


def generate(output_dir, validation_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    validation_dir.mkdir(parents=True, exist_ok=True)
    albedo, normal = grass_maps()
    sky = sky_map()
    white=np.full((4,4,3),255,dtype=np.uint8)
    flat=np.zeros((4,4,3),dtype=np.uint8);flat[:]=[128,128,255]
    maps = {'kitchen_grass_albedo':albedo, 'kitchen_grass_normal':normal, 'kitchen_sky':sky,
            'kitchen_neutral_white':white, 'kitchen_neutral_normal':flat}
    report = {'version':1, 'status':'procedural_candidates_not_scene_validated',
              'source':'dream/blender/make_kitchen_textures.py', 'maps':{},
              'contract':{'grass_kind':11, 'grass_ground_variant':0, 'grass_blade_variant':1,
                          'color_sampler_slot':'floorSurface', 'normal_sampler_slot':'floorFlow',
                          'grass_uv':'world X/4, world Y/4, continuous across interior/meadow',
                          'normal_strength':GRASS_NORMAL_STRENGTH, 'roughness':.90,
                          'sky_runtime_uv':'u=atan2(Y,X)/(2pi)+.5; v=asin(Z)/pi+.5; BMP loader flips rows',
                          'sky_png_rows':'+Z at top, -Z at bottom',
                          'blender_environment_mapping_scale':[1,-1,1]},
              'limitations':['No scene render or final material acceptance yet.',
                             'Sky is an original LDR procedural approximation, not recovered HDRI.',
                             'Grass map period is 4 m; geometry and mipmaps are needed for close/far continuity.',
                             'Reference crops retain their original illumination and are not used as albedo.']}
    for name, pixels in maps.items():
        image = Image.fromarray(pixels, 'RGB')
        for suffix in ('png', 'bmp'):
            image.save(output_dir/f'{name}.{suffix}')
        png = np.asarray(Image.open(output_dir/f'{name}.png'))
        bmp = np.asarray(Image.open(output_dir/f'{name}.bmp'))
        assert np.array_equal(png, bmp)
        report['maps'][name] = {'size_px':list(image.size), 'png_bmp_pixels_equal':True,
            'color_space':'Non-Color' if name.endswith('normal') else 'sRGB',
            'horizontal_seam_pixels_equal':bool(np.array_equal(png[:, 0], png[:, -1])),
            'sha256':{s:hashlib.sha256((output_dir/f'{name}.{s}').read_bytes()).hexdigest() for s in ('png','bmp')}}
    report['grass_vertical_seam_pixels_equal'] = bool(np.array_equal(albedo[0], albedo[-1]) and np.array_equal(normal[0], normal[-1]))
    report['source_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (validation_dir/'texture-kitchen-validation.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    # This contact is an inspection artifact, never a runtime material map.
    canvas = Image.new('RGB', (1064, 648), (28, 31, 36));draw = ImageDraw.Draw(canvas)
    source = Image.open(ROOT/'referencias/estetica/texturas/video-42/cesped_interior.png').convert('RGB')
    samples = [('SOURCE GRASS (lit crop)', source), ('PROCEDURAL ALBEDO', Image.fromarray(albedo)),
               ('NORMAL DATA', Image.fromarray(normal)), ('SKY ANGULAR VIEW / NO GEOMETRY', Image.fromarray(perspective(sky)).crop((225,160,478,355)))]
    for i,(label,img) in enumerate(samples):
        x = 12+i*264
        draw.text((x,12), label, fill=(235,235,235))
        canvas.paste(img.resize((248,248), Image.Resampling.LANCZOS), (x,36))
    draw.text((12,304),'KITCHEN SKY PANORAMA - low lavender cloud bank, clear cyan upper sky',fill=(235,235,235))
    canvas.paste(Image.fromarray(sky).resize((1040,300), Image.Resampling.LANCZOS),(12,328))
    canvas.save(validation_dir/'texture-kitchen-contact.png')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=ROOT/'assets/textures')
    parser.add_argument('--validation-dir', type=Path, default=ROOT/'validation')
    args = parser.parse_args()
    result = generate(args.output_dir, args.validation_dir)
    print(json.dumps({'status':result['status'], 'maps':list(result['maps'])}))
