"""Authored repeatable maps for the sky stair; source crops remain untouched.

Color seeds and cloud placements are inferred from video-35/09s, not recovered
PBR maps. Grass tiles over 4 m; plush over .28 m. Sky is a distant panorama.
"""
from pathlib import Path
import hashlib, json, math
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter, zoom
from make_cloud_sky import cloud_volume

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'assets/textures'
RNG = np.random.default_rng(3509)

def noise(size, cells):
    raw = RNG.random((cells, cells), dtype=np.float32)
    return zoom(raw, size/cells, order=1, mode='wrap')[:size,:size]

def save(name, data):
    image = Image.fromarray(np.uint8(np.clip(data,0,255)), 'RGB')
    image.save(OUT/(name+'.png'))
    image.save(OUT/(name+'.bmp'))

def normal(height, strength):
    dx=(np.roll(height,-1,1)-np.roll(height,1,1))*strength
    dy=(np.roll(height,1,0)-np.roll(height,-1,0))*strength
    vector=np.stack([-dx,-dy,np.ones_like(dx)],axis=-1)
    vector/=np.linalg.norm(vector,axis=-1,keepdims=True)
    return (vector*.5+.5)*255

def materials():
    size=1024
    coarse=noise(size,16); fine=noise(size,128)
    pile=Image.new('L',(size,size),90); draw=ImageDraw.Draw(pile)
    for _ in range(28000):
        x,y=RNG.uniform(0,size,2); a=RNG.uniform(0,2*math.pi)
        length=RNG.uniform(4,20); curl=RNG.uniform(-1.4,1.4)
        points=[(x+math.cos(a+t*curl)*length*t,y+math.sin(a+t*curl)*length*t) for t in (0,.33,.66,1)]
        for ox,oy in ((0,0),(-size,0),(size,0),(0,-size),(0,size)):
            draw.line([(px+ox,py+oy) for px,py in points],fill=int(RNG.integers(125,250)),width=1)
    h=gaussian_filter(np.asarray(pile,dtype=float)/255,.45,mode='wrap')
    shade=.85+.15*coarse+.09*fine+.13*(h-h.mean())
    save('stair_plush_albedo',shade[...,None]*[247,166,158])
    save('stair_plush_normal',normal(h,1.5))
    grass=Image.new('L',(size,size),110); draw=ImageDraw.Draw(grass)
    for _ in range(55000):
        x,y=RNG.uniform(0,size,2); dx,dy=RNG.normal(0,3,2)
        draw.line((x,y,x+dx,y+dy),fill=int(RNG.integers(45,230)),width=1)
    g=gaussian_filter(np.asarray(grass,dtype=float)/255,.5,mode='wrap')
    broad=noise(size,8); middle=noise(size,64)
    shade=.62+.36*broad+.24*middle+.17*(g-g.mean())
    save('stair_grass_albedo',shade[...,None]*[76,119,45])
    save('stair_grass_normal',normal(g,1.4))
    save('stair_neutral_white',np.full((4,4,3),255))
    save('stair_neutral_normal',np.tile([128,128,255],(4,4,1)))

def panorama():
    width,height=2048,1024
    v=np.linspace(0,1,height)[:,None,None]
    sky=np.broadcast_to(np.array([35,112,147])[None,None,:]*(1-v)+np.array([105,165,188])[None,None,:]*v,(height,width,3)).copy()
    result=Image.fromarray(np.uint8(sky),'RGB').convert('RGBA')
    yaw,pitch,tan=1.51996,.001732,.597352
    f=np.array([math.cos(yaw)*math.cos(pitch),math.sin(yaw)*math.cos(pitch),math.sin(pitch)])
    right=np.cross(f,[0,0,1]);right/=np.linalg.norm(right);up=np.cross(right,f)
    def ray_uv(x,y):
        d=f+right*(x*2-1)*(720/1280)*tan+up*(1-y*2)*tan;d/=np.linalg.norm(d)
        return math.atan2(d[1],d[0])/(2*math.pi)+.5,.5-math.asin(d[2])/math.pi
    placements=[]
    for x,y,w,ratio,seed in [( .39,.285,.082,.31,359),(.45,.405,.067,.28,367),(.39,.11,.09,.33,373)]:
        placements.append((*ray_uv(x,y),w,ratio,seed))
    placements += [(.10,.44,.06,.32,379),(.30,.39,.07,.35,383),(.48,.51,.065,.3,389),(.92,.46,.065,.32,397)]
    for i,(u,v,w,ratio,seed) in enumerate(placements):
        cloud=cloud_volume(seed,(48,72,120)).astype(float)
        # Shift the shared optical cloud recipe from lavender to warm pink.
        cloud[:,:,:3]=np.clip(cloud[:,:,:3]*[1.04,.93,.80]+[5,10,13],0,255)
        image=Image.fromarray(np.uint8(cloud),'RGBA')
        iw=round(w*width);ih=round(iw*ratio)
        image=image.resize((iw,ih),Image.Resampling.LANCZOS)
        x=round(u*width-iw/2);y=round(v*height-ih/2)
        for ox in (-width,0,width):
            if x+ox<width and x+ox+iw>0: result.alpha_composite(image,(x+ox,y))
        print('stair cloud',i+1,len(placements),flush=True)
    save('stair_sky',np.asarray(result.convert('RGB')))

if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    materials();panorama()
    paths=sorted(p for p in OUT.glob('stair_*.png') if not p.name.startswith('stair_checker_'))
    report={'schema':'dream.stair_textures.v1','source':'referencias/estetica/evidencias/video-35/09s.png','maps_are_recreations':True,'source_crops_modified':False,'period_m':{'grass':4,'plush':.28},'maps':[]}
    for p in paths:
        pair=p.with_suffix('.bmp');a=np.asarray(Image.open(p));b=np.asarray(Image.open(pair))
        assert np.array_equal(a,b)
        report['maps'].append({'path':str(p.relative_to(ROOT)),'dimensions':list(Image.open(p).size),'png_bmp_pixels_equal':True,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    (ROOT/'validation/stair-textures.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('7 map pairs verified')
