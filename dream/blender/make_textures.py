"""Original procedural textures. Run with Python + NumPy + Pillow."""
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter, ImageDraw

ROOT = Path(__file__).resolve().parents[1] / 'assets' / 'textures'
ROOT.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(718)

def save(name, rgb):
    image = Image.fromarray(np.uint8(np.clip(rgb, 0, 255)), 'RGB')
    image.save(ROOT / (name + '.png'))
    image.save(ROOT / (name + '.bmp'))

def noise(w, h):
    result = np.zeros((h, w), np.float32)
    for cells, weight in [(8, .48), (16, .25), (32, .14), (64, .08), (128, .05)]:
        small = Image.fromarray(rng.integers(0, 255, (max(2,cells//2), cells), dtype=np.uint8))
        result += np.asarray(small.resize((w,h), Image.Resampling.BICUBIC), dtype=np.float32) / 255 * weight
    return result

w,h=2048,1024
xx,yy=np.meshgrid(np.arange(w),np.arange(h))
v=yy/h
detail=noise(w,h)
sky=np.stack([125+v*30,169+v*13,232-v*1],axis=-1)
# Shaded overlapping lobes, with small-scale density variation. This is an
# authored sky texture, not a recovered HDR environment from the reference.
for row,number,scale in [(380,12,.45),(500,10,.7),(640,11,.95),(850,10,1.5)]:
    for group in range(number):
        cx=(group+.3+rng.uniform(-.15,.15))*w/number
        cy=row+rng.uniform(-30,30)
        depth=np.zeros((h,w),np.float32)
        for lobe in range(16):
            px=cx+rng.normal(0,32)*scale;py=cy+rng.normal(0,10)*scale
            radius=rng.uniform(10,26)*scale
            dx=((xx-px+w/2)%w-w/2)/(radius*1.2)
            dy=(yy-py)/radius
            field=1-dx*dx-dy*dy+(detail-.5)*.25
            depth=np.maximum(depth,np.sqrt(np.clip(field,0,1))*radius)
        dx,dy=np.gradient(depth)
        lit=np.clip(.62-dx*.2-dy*.13+depth/(45*scale),0,1)
        col=np.stack([197+lit*54,178+lit*67,221+lit*32],axis=-1)
        alpha=np.asarray(Image.fromarray(np.uint8(np.clip(depth,0,2)*127)).filter(ImageFilter.GaussianBlur(.8)),dtype=float)/255
        sky=sky*(1-alpha[:,:,None])+col*alpha[:,:,None]
save('cloud_sky',sky)

w=h=512
x,y=np.meshgrid(np.arange(w),np.arange(h))
# Plaid textile generated from thread bands rather than photographed lighting.
cloth=np.full((h,w,3),[192.,188.,159.])
for axis in [x,y]:
    band=axis%128
    for low,high,c,alpha in [(0,30,[84,134,122],.6),(36,57,[229,148,159],.65),(66,73,[234,197,127],.75),(94,98,[85,117,115],.7)]:
        mask=(band>=low)&(band<high);cloth[mask]=cloth[mask]*(1-alpha)+np.array(c)*alpha
weave=((x%3==0).astype(float)+(y%3==0).astype(float))*4-4
save('curtain_plaid',cloth+weave[:,:,None])
grain=noise(w,h)
normal=np.zeros((h,w,3));normal[:]=[128,128,255]
normal[:,:,0]+=np.gradient(grain,axis=1)*250
normal[:,:,1]+=np.gradient(grain,axis=0)*250
save('ceramic_normal',normal)
save('ceramic_roughness',np.repeat((58+grain*22)[:,:,None],3,axis=2))
print('Generated cloud sky, plaid, ceramic normal and roughness in', ROOT)
