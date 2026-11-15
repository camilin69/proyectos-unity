"""Fit a nonuniform ribbon trajectory; reserve the 16s colour samples."""
from pathlib import Path
import json
import numpy as np
from scipy.interpolate import CubicSpline
from scipy.optimize import least_squares
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'validation/wave-perspective'
source=json.loads((OUT/'paint-fit.json').read_text())
rows=source['samples']
# The two-view experiment failed at 17s; keep its report before using that
# view for training and introduce a genuinely unused paint view at 16s.
old_path=OUT/'paint-spline-fit.json'
if old_path.exists() and not (OUT/'paint-spline-two-view-fit.json').exists():
    (OUT/'paint-spline-two-view-fit.json').write_bytes(old_path.read_bytes())
p=ROOT/'validation/fit_wave_paint_multiview.py'
ns={'__file__':str(p),'__name__':'paint_ray_helpers'}
code=p.read_text(encoding='utf-8').split('rows=[];excluded=[]')[0]
exec(compile(code,str(p),'exec'),ns)
samples16=[(20,800,'pink'),(105,800,'coral'),(175,800,'ochre'),(340,770,'lavender'),(450,800,'teal'),
           (200,550,'teal'),(320,550,'pink'),(280,515,'lavender'),(295,623,'ochre'),(420,735,'teal')]
im=Image.open(ROOT/'validation/wave-motion/16s.png').convert('RGB');raw=np.array(im);draw=ImageDraw.Draw(im)
for x,y,label in samples16:
    result=ns['hit'](x,y,ns['cams'][16]);assert result is not None,(x,y)
    _,point,uv=result
    rows.append({'time_s':16,'pixel':[x,y],'label':label,'metric_uv':uv,'point_m':point,
                 'source_rgb_diagnostic':np.median(raw[y-2:y+3,x-2:x+3].reshape(-1,3),axis=0).tolist()})
    draw.ellipse((x-4,y-4,x+4,y+4),outline='yellow',width=2);draw.text((x+5,y-6),label[:2],fill='yellow',stroke_width=1,stroke_fill='black')
im.save(OUT/'paint-labels-16s.png')
xy=np.array([r['metric_uv'] for r in rows]);train=np.array([r['time_s']!=16 for r in rows])
bands={'teal':[(-100,-1.08),(.71,100)],'ochre':[(-1.01,-.85),(-.15,.19)],
       'pink':[(-.79,-.54)],'coral':[(-.48,-.21)],'lavender':[(.25,.64)]}
knots=np.arange(2.,11.51,.5)
basis=CubicSpline(knots,np.eye(len(knots)),bc_type='natural')(xy[:,1])
def errors(v):
    q=(xy[:,0]-basis@v[:-1])/v[-1]
    return np.array([min(max(lo-qv,0,qv-hi) for lo,hi in bands[r['label']]) for qv,r in zip(q,rows)])
def residual(v):
    return np.r_[errors(v)[train],.025*np.diff(v[:-1],n=2),.035*(v[-1]-1)]
best=None
for phase in np.linspace(0,2*np.pi,12,endpoint=False):
    start=np.r_[1.2*np.sin(knots*2*np.pi/5+phase),1.]
    fit=least_squares(residual,start,bounds=(np.r_[np.full(len(knots),-3.),.45],np.r_[np.full(len(knots),3.),2.]),max_nfev=500)
    score=float(np.sum(residual(fit.x)**2))
    if best is None or score<best[0]:best=(score,fit.x)
v=best[1]
e=errors(v)
metrics={name:{'samples':int(mask.sum()),'interval_rms':float(np.sqrt(np.mean(e[mask]**2))),
               'inside_label_band_fraction':float(np.mean(e[mask]<.025))} for name,mask in [('training',train),('heldout_16s',~train)]}
# Produce only reconstructed palette regions; no source lighting/pixels.
palette={'teal':[110,161,158],'lavender':[147,145,184],'pink':[208,150,165],
         'coral':[217,133,119],'ochre':[213,181,120]}
w,h=1024,2048;x=np.linspace(-5,5,w)[None,:];s=np.linspace(32,0,h)[:,None]
clipped=np.clip(s,knots[0],knots[-1])
center=CubicSpline(knots,v[:-1],bc_type='natural')(clipped)
# Unseen region stays an explicitly provisional smooth continuation.
before=s<knots[0];after=s>knots[-1]
center=np.where(before,v[0]+.25*np.sin((s-knots[0])*.8),center)
center=np.where(after,v[-2]+.7*np.sin((s-knots[-1])*.8),center)
q=(x-center)/v[-1]
rgb=np.broadcast_to(np.array(palette['teal'],float),(h,w,3)).copy()
for lo,hi,key in [(-1.04,-.82,'ochre'),(-.82,-.51,'pink'),(-.51,-.18,'coral'),(-.18,.22,'ochre'),(.22,.67,'lavender')]:
    a=np.clip((q-lo+.008)/.016,0,1);b=np.clip((hi-q+.008)/.016,0,1)
    mask=(a*a*(3-2*a)*b*b*(3-2*b))[...,None]
    rgb=rgb*(1-mask)+np.array(palette[key])*mask
Image.fromarray(np.rint(rgb).astype('uint8')).save(OUT/'rejected-paint-albedo.png')
report={'schema':'dream.wave_paint_spline.v1','accepted':False,'runtime_promoted':False,
        'knots_s_m':knots.tolist(),'center_x_m':v[:-1].tolist(),'width_scale_m':float(v[-1]),
        'metrics':metrics,'source_labels':'validation/wave-perspective/paint-fit.json',
        'samples':rows,'training_times_s':[14,15.5,17],'heldout_time_s':16,
        'texture':'validation/wave-perspective/rejected-paint-albedo.png',
        'decision':'Do not apply: held-out 16s sample coverage remains poor despite low training residual.',
        'uv_domain_m':{'x':[-5,5],'s':[0,32]},'palette_srgb':palette,'source_rgb_baked':False,
        'limitations':['Only labelled portions of the floor constrain the spline.',
                       'Outside s=2..11.5 m, continuation is provisional and must not be called reference-matched.',
                       'The two-view experiment failed at 17s and is preserved. This revision uses 17s for training and withholds 16s instead; no whole-image fidelity score is implied.',
                       'The source/camera floor interpretation is still provisional.']}
(OUT/'paint-spline-fit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='samples'}))
