"""Fit the two visible utility panels on the existing left wall plane."""
from pathlib import Path
import json
import cv2
import numpy as np
from scipy.optimize import least_squares
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'validation/wave-perspective'
cfg=json.loads((ROOT/'validation/wave-aperture/fit.json').read_text())['plan']['constructor']
cams=cfg['all_source_cameras']
p=ROOT/'validation/fit_wave_geometry.py';ns={'__file__':str(p),'__name__':'panel_fit_helpers'}
exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),ns)
cap=cv2.VideoCapture(str(ROOT/'referencias/estetica/originales/WhatsApp Video 2026-10-08 at 6.27.42 PM.mp4'))
fps=cap.get(cv2.CAP_PROP_FPS);cap.set(cv2.CAP_PROP_POS_FRAMES,round(14*fps));frames={}
for i in range(round(14*fps),round(17*fps)+1):
    ok,frame=cap.read();assert ok;frames[i]=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
cap.release()
seeds=[[66,229],[94,225],[101,312],[77,325],[95,225],[116,224],[121,298],[101,311]]
tracks=[]
for xy in seeds:
    point=np.array([[xy]],np.float32);samples=[[17,*map(float,xy)]];errors=[]
    for i in range(round(17*fps),round(14*fps),-1):
        nxt,st,_=cv2.calcOpticalFlowPyrLK(frames[i],frames[i-1],point,None,winSize=(15,15),maxLevel=3)
        back,bst,_=cv2.calcOpticalFlowPyrLK(frames[i-1],frames[i],nxt,None,winSize=(15,15),maxLevel=3)
        error=float(np.linalg.norm(back-point));errors.append(error)
        if not st[0,0] or not bst[0,0] or error>1:break
        point=nxt;samples.append([(i-1)/fps,*map(float,point[0,0])])
    tracks.append({'seed_17s':xy,'samples':sorted(samples),'complete':len(samples)==91,'max_fb_error_px':max(errors)})
obs=np.array([[min(t['samples'],key=lambda s:abs(s[0]-c['time_s']))[1:] for t in tracks] for c in cams])
valid=np.array([[min(abs(s[0]-c['time_s']) for s in t['samples'])<.01 for t in tracks] for c in cams])
wall_x=-cfg['corridor']['half_width_m']+.035
def points(v):
    y0,y1,z,w0,w1,h=v
    rows=[]
    for y,w in [(y0,w0),(y1,w1)]:
        rows.extend([[wall_x,y-w/2,z+h/2],[wall_x,y+w/2,z+h/2],
                     [wall_x,y+w/2,z-h/2],[wall_x,y-w/2,z-h/2]])
    return rows
def error(v,indices):
    xyz=dict(enumerate(points(v)));result=[]
    for i in indices:
        pp=ns['projected'](xyz,cams[i])
        result.extend((np.array([pp[j] for j in range(8)])-obs[i])[valid[i]])
    return np.asarray(result).ravel()
train=[0,3,6];heldout=[1,2,4,5]
fit=least_squares(lambda v:error(v,train),[5.3,5.65,.65,.3,.3,.55],
                  bounds=([3,3,-.2,.1,.1,.2],[9,9,1.8,.8,.8,1.5]),loss='soft_l1',f_scale=3,max_nfev=700)
v=fit.x
report={'schema':'dream.wave_wall_panels.v1','accepted':False,'runtime_promoted':False,
        'parameters':dict(zip(['near_center_y','far_center_y','center_z','near_width','far_width','height'],map(float,v))),
        'front_x_m':wall_x,'tracks':tracks,'training_times_s':[cams[i]['time_s'] for i in train],
        'valid_corner_samples_per_view':valid.sum(axis=1).tolist(),
        'heldout_times_s':[cams[i]['time_s'] for i in heldout],
        'training_rms_px':float(np.sqrt(np.mean(np.sum(error(v,train).reshape(-1,2)**2,axis=1)))),
        'heldout_rms_px':float(np.sqrt(np.mean(np.sum(error(v,heldout).reshape(-1,2)**2,axis=1)))),
        'limitations':['Compressed/blurred panel corners are uncertain; dimensions are a fitted hypothesis.',
                       'Held-out samples were not used for panel fitting, but cameras were estimated previously.']}
(OUT/'wall-panels-fit.json').write_text(json.dumps(report,indent=2)+'\n')
sheet=Image.new('RGB',(1434,884),'#17191e');draw=ImageDraw.Draw(sheet)
for col,i in enumerate(train):
    time=cams[i]['time_s'];sheet.paste(Image.open(ROOT/f'validation/wave-motion/{time:g}s.png'),(478*col,34))
    draw.text((478*col+5,10),f'SOURCE {time:g}s / cyan track / white model',fill='white')
    pp=ns['projected'](dict(enumerate(points(v))),cams[i])
    for j,xy in enumerate(obs[i]):
        if not valid[i,j]:continue
        x,y=xy+[478*col,34];draw.ellipse((x-3,y-3,x+3,y+3),outline='cyan')
        x,y=np.array(pp[j])+[478*col,34];draw.line((x-3,y,x+3,y),fill='white');draw.line((x,y-3,x,y+3),fill='white')
sheet.save(OUT/'wall-panels-fit.png')
print(json.dumps({k:v for k,v in report.items() if k!='tracks'}))
