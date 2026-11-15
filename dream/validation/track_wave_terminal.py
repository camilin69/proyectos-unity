"""Track explicitly labeled terminal rail corners backwards in source frames."""
from pathlib import Path
import json
import cv2
import numpy as np
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'validation/wave-terminal'
SOURCE=ROOT/'referencias/estetica/originales/WhatsApp Video 2026-10-08 at 6.27.42 PM.mp4'
seeds={'left_near_top':[151,327],'left_far_top':[164,334],
       'left_near_foot':[151,413],'left_far_foot':[169,424],
       'right_near_top':[318,334],'right_far_top':[308,341],
       'right_near_foot':[317,420],'right_far_foot':[301,432]}
cap=cv2.VideoCapture(str(SOURCE));fps=cap.get(cv2.CAP_PROP_FPS)
cap.set(cv2.CAP_PROP_POS_FRAMES,round(14*fps));frames={}
for i in range(round(14*fps),round(17*fps)+1):
    ok,frame=cap.read();assert ok
    frames[i]=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
cap.release()
rows=[]
for name,xy in seeds.items():
    point=np.array([[xy]],dtype=np.float32);samples=[[17,*map(float,xy)]];errors=[]
    for i in range(round(17*fps),round(14*fps),-1):
        q,st,_=cv2.calcOpticalFlowPyrLK(frames[i],frames[i-1],point,None,winSize=(15,15),maxLevel=3,
               criteria=(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,40,.001))
        back,bst,_=cv2.calcOpticalFlowPyrLK(frames[i-1],frames[i],q,None,winSize=(15,15),maxLevel=3)
        err=float(np.linalg.norm(back-point));errors.append(err)
        if not st[0,0] or not bst[0,0] or err>1.:break
        point=q;samples.append([(i-1)/fps,*map(float,q[0,0])])
    rows.append({'id':name,'manual_seed_17s_px':xy,'max_step_forward_backward_error_px':max(errors),
                 'complete':len(samples)==91,'samples':list(reversed(samples))})
sheet=Image.new('RGB',(3*478,884),'#17191e');d=ImageDraw.Draw(sheet)
for j,t in enumerate([14,15.5,17]):
    im=Image.open(ROOT/f'validation/wave-motion/{t:g}s.png');sheet.paste(im,(j*478,34))
    d.text((j*478+6,8),f'SOURCE {t:g}s / rail seeds and tracks',fill='white')
    for i,r in enumerate(rows):
        if not any(abs(s[0]-t)<.001 for s in r['samples']):continue
        s=min(r['samples'],key=lambda s:abs(s[0]-t));x,y=s[1]+j*478,s[2]+34
        color=['#ffee00','#ff9922','#88ff22','#33ffee','#ff22bb','#ff4444','#7788ff','#ffffff'][i]
        d.ellipse((x-3,y-3,x+3,y+3),outline=color,width=1);d.text((x+4,y-8),str(i),fill=color)
sheet.save(OUT/'rail-tracks.png')
report={'schema':'dream.wave_terminal_tracks.v1','source':'Original video-42 @14..17s; no source images changed.',
        'landmark_policy':'Approximate corners of the two short tall terminal frames. Foot points may be occluded by low trim.',
        'method':'Backward pyramidal LK; per-step forward/backward error <=1 px. Completeness does not prove correspondence.',
        'tracks':rows}
(OUT/'rail-tracks.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps([{k:r[k] for k in ('id','complete','max_step_forward_backward_error_px')} | {'sample_14s':r['samples'][0]} for r in rows]))
