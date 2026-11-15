"""Check whether manual aperture labels actually refer to the same source points."""
from pathlib import Path
import json
import cv2
import numpy as np
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'validation/wave-aperture';OUT.mkdir(exist_ok=True)
SOURCE=ROOT/'referencias/estetica/originales/WhatsApp Video 2026-10-08 at 6.27.42 PM.mp4'
cap=cv2.VideoCapture(str(SOURCE));fps=cap.get(cv2.CAP_PROP_FPS)
cap.set(cv2.CAP_PROP_POS_FRAMES,round(14*fps));frames={}
for i in range(round(14*fps),round(17*fps)+1):
    ok,frame=cap.read();assert ok;frames[i]=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
cap.release()
seeds=[('L14',14,[171,183]),('R14',14,[295,182]),('L17',17,[148,189]),('R17',17,[334,182]),
       ('left_wall_corner',17,[128,82]),('right_wall_corner',17,[344,145])]
results=[]
for name,time,xy in seeds:
    direction=1 if time==14 else -1;end=17 if direction==1 else 14
    for window in [11,21,31]:
        p=np.array([[xy]],dtype=np.float32);rows=[[time,*map(float,xy)]];errors=[]
        for i in range(round(time*fps),round(end*fps),direction):
            q,status,_=cv2.calcOpticalFlowPyrLK(frames[i],frames[i+direction],p,None,winSize=(window,window),maxLevel=3,
                criteria=(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,40,.001))
            back,reverse,_=cv2.calcOpticalFlowPyrLK(frames[i+direction],frames[i],q,None,winSize=(window,window),maxLevel=3)
            error=float(np.linalg.norm(back-p));errors.append(error)
            if not status[0,0] or not reverse[0,0] or error>1.:break
            p=q;rows.append([(i+direction)/fps,*map(float,q[0,0])])
        results.append({'id':name,'window_px':window,'complete':len(rows)==91,'max_step_fb_error_px':max(errors),
                        'samples':sorted(rows),'end_xy':rows[-1][1:]})
sheet=Image.new('RGB',(478*3,884),'#17191e');draw=ImageDraw.Draw(sheet)
colors={'L14':'#33ff77','R14':'#33ddff','L17':'#ffaa33','R17':'#ff55ee',
        'left_wall_corner':'#ffffff','right_wall_corner':'#ffff33'}
for j,t in enumerate([14,15.5,17]):
    sheet.paste(Image.open(ROOT/f'validation/wave-motion/{t:g}s.png'),(478*j,34))
    draw.text((478*j+8,8),f'SOURCE {t:g}s / 14s seeds: green, blue; 17s seeds: orange, pink',fill='white')
    for r in results:
        sample=next((s for s in r['samples'] if abs(s[0]-t)<1e-6),None)
        if sample is None:continue
        x,y=sample[1]+478*j,sample[2]+34
        draw.ellipse((x-3,y-3,x+3,y+3),outline=colors[r['id']],width=2)
        if r['window_px']==21:draw.text((x+5,y-9),r['id'],fill=colors[r['id']])
sheet.save(OUT/'correspondence.png')
report={'schema':'dream.wave_aperture_tracks.v1','accepted':False,'method':'Bidirectional per-step LK in three window sizes; not proof of corner identity.',
        'tracks':results}
(OUT/'tracks.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps([{k:v for k,v in r.items() if k!='samples'} for r in results]))
