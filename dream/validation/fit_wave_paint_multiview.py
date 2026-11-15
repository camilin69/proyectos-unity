"""Refit existing procedural paint UV placement using multiple source views.

Labels are interpreted surface colours, not sampled RGB baked into a texture.
The 17-second view is withheld from the optimization.
"""
from pathlib import Path
import json
import math
import numpy as np
from scipy.optimize import differential_evolution
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'validation/wave-perspective'
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
cfg=read('validation/wave-hall-structure/geometry-candidate.json')['plan']['constructor']
p=ROOT/'blender/build_wave_corridor.py';ns={'__file__':str(p),'__name__':'paint_helpers'}
exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),ns)
profile,_=ns['floor_profile'](cfg)
arc=np.r_[0,np.cumsum([math.dist(a,b) for a,b in zip(profile,profile[1:])])]
cams={c['time_s']:c for c in cfg['all_source_cameras']}
manual={14:[(350,780,'teal'),(75,730,'teal'),(390,700,'ochre'),(320,670,'ochre'),
            (185,635,'teal'),(100,590,'coral'),(55,560,'ochre'),(390,575,'teal'),(280,490,'lavender')],
        15.5:[(20,800,'ochre'),(80,800,'pink'),(140,800,'coral'),(220,800,'ochre'),(330,800,'lavender'),(450,800,'teal'),
              (20,680,'ochre'),(80,680,'pink'),(140,680,'coral'),(220,680,'ochre'),(330,680,'lavender'),(450,680,'teal'),
              (175,570,'pink'),(295,545,'lavender'),(375,520,'pink'),(310,480,'lavender'),(275,500,'teal')],
        17:[(30,800,'pink'),(100,800,'pink'),(220,800,'lavender'),(400,800,'teal'),
            (100,650,'pink'),(200,650,'coral'),(300,650,'ochre'),
            (100,600,'teal'),(200,580,'teal'),(305,565,'pink'),
            (150,510,'teal'),(225,490,'lavender'),(325,510,'pink')]}

def hit(x,y,cam):
    yaw,pitch,roll=[cam[k] for k in ['yaw_rad','pitch_rad','roll_rad']]
    f=np.array([math.cos(yaw)*math.cos(pitch),math.sin(yaw)*math.cos(pitch),math.sin(pitch)])
    r=np.cross(f,[0,0,1]);r/=np.linalg.norm(r);u=np.cross(r,f)
    rr=r*math.cos(roll)+u*math.sin(roll);uu=u*math.cos(roll)-r*math.sin(roll)
    ray=f+(x-239)/425*cam['tan_half_vertical_fov']*rr-(y-425)/425*cam['tan_half_vertical_fov']*uu
    origin=np.array(cam['position_m']);hits=[]
    for i,(a,b) in enumerate(zip(profile,profile[1:])):
        axis=2 if abs(a[1]-b[1])<1e-9 else 1
        value=a[1] if axis==2 else a[0]
        if abs(ray[axis])<1e-10:continue
        t=(value-origin[axis])/ray[axis]
        point=origin+t*ray
        if t<=0 or abs(point[0])>cfg['corridor']['half_width_m']:continue
        if not (min(a[0],b[0])-1e-7<=point[1]<=max(a[0],b[0])+1e-7 and min(a[1],b[1])-1e-7<=point[2]<=max(a[1],b[1])+1e-7):continue
        distance=arc[i]+math.dist(a,(point[1],point[2]))
        hits.append((t,point.tolist(),[float(point[0]),distance]))
    return min(hits,key=lambda h:h[0]) if hits else None

rows=[];excluded=[]
colors={'teal':'#3ee0d6','ochre':'#ffd24b','pink':'#ff75c8','coral':'#ff6845','lavender':'#a194ff'}
for time,samples in manual.items():
    image=Image.open(ROOT/f'validation/wave-motion/{time:g}s.png').convert('RGB')
    draw=ImageDraw.Draw(image)
    raw=np.array(image)
    for x,y,label in samples:
        result=hit(x,y,cams[time])
        if result is None:
            excluded.append({'time_s':time,'pixel':[x,y],'label':label,'reason':'Ray misses current floor geometry; not silently reassigned to another surface.'})
            continue
        _,point,uv=result
        row={'time_s':time,'pixel':[x,y],'label':label,'metric_uv':uv,'point_m':point,'used_for_fit':time!=17,
             'source_rgb_diagnostic':np.median(raw[y-2:y+3,x-2:x+3].reshape(-1,3),axis=0).tolist()}
        rows.append(row)
        draw.ellipse((x-4,y-4,x+4,y+4),outline=colors[label],width=2)
        draw.text((x+5,y-6),label[:2],fill=colors[label],stroke_width=1,stroke_fill='black')
    image.save(OUT/f'paint-labels-{time:g}s.png')

xy=np.array([r['metric_uv'] for r in rows]);labels=[r['label'] for r in rows]
train=np.array([r['used_for_fit'] for r in rows])
bands={'teal':[(-100,-1.08),(.71,100)],'ochre':[(-1.01,-.85),(-.15,.19)],
       'pink':[(-.79,-.54)],'coral':[(-.48,-.21)],'lavender':[(.25,.64)]}

def residuals(v):
    px,py,phase,offset=v
    x=((xy[:,0]/px+.5+offset)%1)*6.6-3.3
    angle=2*np.pi*(xy[:,1]/py+phase)
    centre=1.26*np.sin(angle+.35)+.20*np.sin(2*angle-.75)
    width=1+.14*np.sin(angle-.5)+.05*np.cos(2*angle)
    q=(x-centre)/width
    return np.array([min(max(lo-v,0,v-hi) for lo,hi in bands[label]) for v,label in zip(q,labels)])

baseline=np.array([5.54369250671431,4.46519794285846,.6863645501164858,-.11085074134954703])
fit=differential_evolution(lambda v:np.mean(residuals(v)[train]**2),[(3,12),(3,16),(0,1),(-.35,.35)],
                           seed=420017,maxiter=500,popsize=24,tol=1e-9)
def metrics(v):
    e=residuals(v)
    return {name:{'samples':int(mask.sum()),'interval_rms':float(np.sqrt(np.mean(e[mask]**2))),
                  'inside_label_band_fraction':float(np.mean(e[mask]<.025))} for name,mask in [('training',train),('heldout_17s',~train)]}
report={'schema':'dream.wave_paint_multiview.v1','accepted':False,'runtime_promoted':False,
        'baseline_parameters':baseline.tolist(),'candidate_parameters':fit.x.tolist(),
        'parameter_names':['period_x_m','period_s_m','phase','offset_u'],
        'label_review':'Labels checked on current timestamped source overlays and local RGB. Two old 14s glare samples excluded, and inherited colour mislabels corrected. These labels supersede the older single-view paint sample semantics.',
        'baseline':metrics(baseline),'candidate':metrics(fit.x),'samples':rows,'excluded_samples':excluded,
        'limitations':['Sparse manually interpreted colour labels; reflections can change perceived colour.',
                       'Geometry/cameras are still provisional; paint fitting does not validate them.',
                       '17s labels are held out from the paint optimizer, but the camera itself was fitted using source evidence.']}
(OUT/'paint-fit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ['samples','limitations']}))
