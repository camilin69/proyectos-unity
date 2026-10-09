"""Deterministic authored cumulus environment, independent of Blender.

Ray-integrates small 3D cloud volumes with directional optical shadows. The
output is an LDR equirectangular environment, NOT a measured HDRI or a texture
recovered from the video. Run with Python, numpy, scipy and Pillow.

PNG rows go from +Z to -Z. Runtime's +Y points to u=.75, +X to u=.5.
The default output is the active cloud_sky PNG/BMP pair. Use --output-stem
cloud_sky_candidate to keep a proposed variant separate from the active scene.
"""
from pathlib import Path
import argparse
import json
import math
import re
import time

import numpy as np
from scipy.ndimage import gaussian_filter, shift, zoom
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[1]


def cloud_volume(seed, resolution=(96, 136, 224)):
    """Optically shaded RGBA, with depth first, then image Y and X."""
    rng = np.random.default_rng(seed)
    nz, ny, nx = resolution
    zz, yy, xx = np.meshgrid(
        np.linspace(-1, 1, nz, dtype=np.float32),
        np.linspace(-1, 1, ny, dtype=np.float32),
        np.linspace(-1.7, 1.7, nx, dtype=np.float32), indexing='ij')
    field = np.full(resolution, -3, np.float32)
    # A wide coherent base supports irregular upright towers. Smooth maximum
    # joins the masses so their boundaries do not look like pasted circles.
    lobes = [(-.78, .30, .08, .80, .40, .62), (.04, .31, -.07, .90, .43, .60),
             (.79, .33, .06, .68, .37, .48)]
    for center_x in [-.91, -.37, .13, .64]:
        lobes.append((center_x + rng.uniform(-.10, .10),
                      rng.uniform(-.23, .03), rng.uniform(-.17, .16),
                      rng.uniform(.35, .52), rng.uniform(.44, .67),
                      rng.uniform(.41, .62)))
    for _ in range(13):
        lobes.append((rng.uniform(-1.1, 1.12), rng.uniform(-.39, .25),
                      rng.uniform(-.44, .18), rng.uniform(.18, .34),
                      rng.uniform(.19, .34), rng.uniform(.24, .39)))
    for cx, cy, cz, rx, ry, rz in lobes:
        d = (1 - np.sqrt(((xx-cx)/rx)**2 + ((yy-cy)/ry)**2 + ((zz-cz)/rz)**2)) * min(rx, ry, rz)
        k = .07
        blend = np.clip(.5 + .5*(d-field)/k, 0, 1)
        field = field*(1-blend) + d*blend + k*blend*(1-blend)
    turbulence = np.zeros(resolution, np.float32)
    # True volumetric octaves disturb the contour and its illumination together.
    for cell, weight in [(7, .080), (14, .044), (28, .022), (48, .010), (80, .005)]:
        small = rng.random((max(3, cell//2), max(3, cell//2), cell), dtype=np.float32)
        interp = zoom(small, np.array(resolution)/np.array(small.shape), order=1)
        turbulence += (interp-.5)*weight*3.0
    density = np.clip((field+turbulence-.019)/.09, 0, 1).astype(np.float32)
    # Taper to a softer, nearly level underside, as with fair-weather cumulus.
    density *= np.clip((.78-yy)/.17, 0, 1)
    density = gaussian_filter(density, .45)

    extinction = .135 * 88/nz
    light_depth = np.zeros_like(density)
    # Sun from upper left and towards the viewer; every sample accumulates
    # density between itself and the sun. Empty volume is outside the cloud.
    for step in range(1, 29):
        light_depth += shift(density, (step*1.3*nz/88, step*1.7*ny/104, step*.60*nx/168), order=1,
                             mode='constant', cval=0, prefilter=False) * 2.2*nz/88
    direct = np.exp(-light_depth*extinction*.72)
    # Cool lavender skylight in shadow and warm pink-white in sun. These are
    # deliberately pastel display-referred values, matching the source mood.
    shadow = np.array([151., 153., 207.], dtype=np.float32)
    sunlight = np.array([253., 234., 248.], dtype=np.float32)
    light = .12 + .88*direct
    lit = shadow[None,None,None,:] + (sunlight-shadow)[None,None,None,:]*light[:,:,:,None]
    alpha = 1 - np.exp(-density*extinction)
    trans = np.exp(-np.cumsum(density, axis=0)*extinction)
    before = np.concatenate([np.ones((1,ny,nx), np.float32), trans[:-1]], axis=0)
    contribution = before*alpha
    opacity = contribution.sum(axis=0)
    rgb = (lit*contribution[:,:,:,None]).sum(axis=0)
    rgb = np.divide(rgb, np.maximum(opacity[:,:,None], 1e-5))
    return np.dstack([rgb, opacity*255]).astype(np.uint8)


def generate(width=2048, height=1024):
    v = np.linspace(0,1,height)[:,None]
    sky = np.repeat(np.stack([122+v*23, 158+v*23, 235-v*3], axis=-1), width, axis=1)
    # Horizon haze changes very gently, preserving an open blue upper sky.
    horizon = np.exp(-((v-.52)/.25)**2)
    sky = sky*(1-horizon[:,:,None]*.11) + np.array([168,183,244])*horizon[:,:,None]*.11
    result = Image.fromarray(np.uint8(sky), 'RGB').convert('RGBA')
    # Hand-placed loose cumulus field: no regular rows. Main masses face +Y
    # (door) and +X (window). Vertical locations are actual sky latitudes.
    placements = [
        (.03,.590,.170,71), (.145,.650,.186,73), (.28,.603,.170,79),
        (.40,.570,.115,83), (.535,.602,.218,89), (.695,.660,.150,97),
        (.773,.568,.192,101), (.915,.608,.183,103),
        (.09,.415,.069,107), (.235,.458,.094,109), (.37,.386,.075,113),
        (.52,.434,.075,127), (.674,.380,.063,131), (.86,.418,.068,137),
        (.01,.785,.268,139), (.25,.850,.280,149), (.51,.801,.272,151),
        (.79,.864,.295,157),
    ]
    for idx,(u,v,w,seed) in enumerate(placements):
        small = idx >= 8 and idx < 14
        image = Image.fromarray(cloud_volume(seed, (72,88,144) if small else (96,136,224)), 'RGBA')
        iw = round(w*width)
        ih = round(iw*.54)
        image = image.resize((iw,ih),Image.Resampling.LANCZOS)
        # Atmospheric perspective softens and slightly fades the distant clouds.
        if small:
            array=np.asarray(image).copy()
            array[:,:,:3] = array[:,:,:3]*.82 + np.array([150,176,239])*.18
            array[:,:,3] = array[:,:,3]*.67
            image=Image.fromarray(array,'RGBA').filter(ImageFilter.GaussianBlur(.7))
        x=round(u*width-iw/2);y=round(v*height-ih/2)
        for ox in [-width,0,width]:
            if x+ox<width and x+ox+iw>0:
                result.alpha_composite(image,(x+ox,y))
        print(f'cloud {idx+1}/{len(placements)}',flush=True)
    # Each pole must converge to a single value to avoid a pinwheel seam.
    rgb=np.asarray(result.convert('RGB'),dtype=np.float32).copy()
    pole=max(4,height//24)
    for n in range(pole):
        blend=(1-n/pole)**2
        for row in [n,height-1-n]:
            rgb[row] = rgb[row]*(1-blend)+rgb[row].mean(axis=0)*blend
    return Image.fromarray(np.uint8(rgb),'RGB')


def perspective(sky, yaw_deg, pitch_deg, fov_deg=70, size=(640,720)):
    """Reference-friendly view using exactly the runtime equirectangular axes."""
    w,h=size; yaw=math.radians(yaw_deg); pitch=math.radians(pitch_deg)
    forward=np.array([math.cos(yaw)*math.cos(pitch),math.sin(yaw)*math.cos(pitch),math.sin(pitch)])
    right=np.cross(forward,[0,0,1]);right/=np.linalg.norm(right)
    up=np.cross(right,forward)
    xx,yy=np.meshgrid(np.linspace(-1,1,w),np.linspace(1,-1,h))
    direction=forward + right*xx[:,:,None]*(w/h)*math.tan(math.radians(fov_deg/2)) + up*yy[:,:,None]*math.tan(math.radians(fov_deg/2))
    direction/=np.linalg.norm(direction,axis=-1,keepdims=True)
    u=(np.arctan2(direction[:,:,1],direction[:,:,0])/(2*np.pi)+.5)*sky.width
    v=(.5-np.arcsin(direction[:,:,2])/np.pi)*sky.height
    from scipy.ndimage import map_coordinates
    array=np.asarray(sky)
    output=np.stack([map_coordinates(array[:,:,c],(v,u),order=1,mode='wrap') for c in range(3)],axis=-1)
    return Image.fromarray(output,'RGB')


def output_stem(value):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', value):
        raise argparse.ArgumentTypeError('Use a filename stem without paths or extension.')
    return value


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--width',type=int,default=2048)
    parser.add_argument('--output-stem',type=output_stem,default='cloud_sky',
                        help='Texture filename stem; default overwrites the active cloud_sky pair.')
    args=parser.parse_args()
    if args.width < 512 or args.width > 8192 or args.width % 2:
        parser.error('--width must be an even integer between 512 and 8192.')
    started=time.time()
    environment=generate(args.width,args.width//2)
    textures=ROOT/'assets'/'textures'; textures.mkdir(exist_ok=True,parents=True)
    png_path=textures/(args.output_stem+'.png')
    bmp_path=textures/(args.output_stem+'.bmp')
    environment.save(png_path)
    environment.save(bmp_path)
    validation=ROOT/'validation';validation.mkdir(exist_ok=True)
    validation_stem='sky' if args.output_stem=='cloud_sky' else 'sky-'+args.output_stem.removeprefix('cloud_sky_').replace('_','-')
    panorama_path=validation/(validation_stem+'-panorama.jpg')
    directions_path=validation/(validation_stem+'-directions.png')
    environment.resize((1536,768)).save(panorama_path,quality=93)
    door=perspective(environment,90,-5)
    window=perspective(environment,0,0)
    proof=Image.new('RGB',(1280,720));proof.paste(door,(0,0));proof.paste(window,(640,0))
    proof.save(directions_path)
    array=np.asarray(environment,dtype=np.float32)
    report={'authored':True,'source':'procedural optical density, no external assets',
            'textures':[str(p.relative_to(ROOT)).replace('\\','/') for p in [png_path,bmp_path]],
            'proofs':[str(p.relative_to(ROOT)).replace('\\','/') for p in [panorama_path,directions_path]],
            'size':list(environment.size),'elapsed_seconds':round(time.time()-started,2),
            'mapping':'PNG top +Z; runtime +Y u=0.75; +X u=0.5; yaw offset 0 degrees',
            'seam_mean_absolute_rgb':float(np.abs(array[:,0]-array[:,-1]).mean()),
            'average_horizontal_neighbor_difference':float(np.abs(array[:,1:]-array[:,:-1]).mean()),
            'pole_top_max_rgb_spread':int((array[0].max(axis=0)-array[0].min(axis=0)).max()),
            'pole_bottom_max_rgb_spread':int((array[-1].max(axis=0)-array[-1].min(axis=0)).max()),
            'limitations':'LDR artistic environment; clouds have no walkable geometry; not an exact source recovery.'}
    (validation/(validation_stem+'.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
