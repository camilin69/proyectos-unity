"""Create original reconstruction maps; never resample video RGB into materials."""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/textures/ocean_exit'
OUT.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(4207)

def save(name, array):
    Image.fromarray(np.uint8(np.clip(array, 0, 1) * 255)).save(OUT / name)

n = 512
y, x = np.mgrid[:n, :n] / n
edge = np.minimum.reduce([x, y, 1-x, 1-y])
glaze = np.clip((edge-.009)/.018, 0, 1)
variation = gaussian_filter(rng.normal(size=(n,n)), 12, mode='wrap')
tile = np.array([.79,.49,.64])[None,None,:] * (1+variation[...,None]*.15)
grout = np.array([.77,.68,.67])
save('pink_tile_albedo.png', grout+(tile-grout)*glaze[...,None])
save('pink_tile_height.png', glaze*.8+.1)
save('pink_tile_roughness.png', .40-.23*glaze)

n = 1024
y,x = np.mgrid[:n,:n]/n
noise = gaussian_filter(rng.normal(size=(n,n)), 28, mode='wrap')
noise /= noise.std()
detail = gaussian_filter(rng.normal(size=(n,n)), 5, mode='wrap')
detail /= detail.std()
wave = np.sin(2*np.pi*(y*5 + .33*np.sin(x*2*np.pi*3)+noise*.16))
foam = np.clip((wave+noise*.4+detail*.2-.47)*1.6,0,1)
save('foam_mask.png', foam)
save('ripple_height.png', np.clip(.5+.18*wave+.065*detail,0,1))

# Equirectangular sunset and stars, with the horizon at the equator.
h,w = 1024,2048
y,x = np.mgrid[:h,:w]
elevation = (.5-y/h)*np.pi
sky = np.zeros((h,w,3))+np.array([.055,.075,.19])
sunset = np.exp(-((elevation-.045)/.15)**2)
sky += sunset[...,None]*np.array([.51,.18,.26])
upper = np.exp(-((elevation-.35)/.4)**2)
sky += upper[...,None]*np.array([.12,.17,.29])
cloud = gaussian_filter(rng.normal(size=(h,w)), (12,35), mode='wrap')
cloud /= cloud.std()
sky += np.maximum(cloud,0)[...,None]*upper[...,None]*np.array([.017,.025,.06])
for _ in range(4200):
    sx=int(rng.integers(w)); sy=int(rng.integers(40,h//2-10))
    strength=rng.uniform(.2,.65)
    sky[sy,sx] += strength
save('sunset_stars.png',sky)

font = 'C:/Windows/Fonts/arialbd.ttf'
for name, size in [('exit_here.png',(384,512)), ('exit_lamp.png',(512,192))]:
    im=Image.new('RGB',size, '#698bba' if 'here' in name else '#673b27')
    draw=ImageDraw.Draw(im)
    if 'here' in name:
        for word, top in [('EXIT',40),('HERE',284)]:
            draw.rectangle((12,top,372,top+180), fill='#e3d69a')
            f=ImageFont.truetype(font,120)
            draw.text((192,top+90),word,font=f,fill='#292c28',anchor='mm')
        draw.rectangle((3,3,380,508),outline='#dfd1ae',width=8)
    else:
        draw.text((256,96),'EXIT',font=ImageFont.truetype(font,164),fill='#ffdb74',anchor='mm')
    im.save(OUT/name)

report={'schema':'dream.original_texture_maps.v1','source_pixels_used':False,
        'purpose':'Ocean-exit reconstruction proposal; not recovered original textures.',
        'maps':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.glob('*.png'))}}
(OUT/'manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
print(json.dumps(report,indent=2))
