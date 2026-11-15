"""Extract a timestamped source sequence and track features, without altering source."""
from pathlib import Path
import hashlib
import json
import cv2
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'referencias/estetica/originales/WhatsApp Video 2026-10-08 at 6.27.42 PM.mp4'
OUT = ROOT/'validation/wave-motion'
OUT.mkdir(exist_ok=True)
cap = cv2.VideoCapture(str(SOURCE))
fps = cap.get(cv2.CAP_PROP_FPS)
frames = {}
cap.set(cv2.CAP_PROP_POS_FRAMES, round(12.5*fps))
for index in range(round(12.5*fps), round(18*fps)+1):
    ok, frame = cap.read()
    if not ok: break
    frames[index] = frame
cap.release()
times = [12.5, 13, 13.5, 14, 14.5, 15, 15.5, 16, 16.5, 17, 17.5, 18]
sheet = Image.new('RGB', (239*6, 455*2), '#17191e')
draw = ImageDraw.Draw(sheet)
for i, time in enumerate(times):
    im = Image.fromarray(cv2.cvtColor(frames[round(time*fps)], cv2.COLOR_BGR2RGB))
    im.save(OUT/f'{time:g}s.png')
    x, y = (i%6)*239, (i//6)*455
    sheet.paste(im.resize((239,425)), (x,y+25))
    draw.text((x+7,y+5), f'SOURCE {time:g} s', fill='white')
sheet.save(OUT/'sequence.png')
start = round(14*fps)
gray = cv2.cvtColor(frames[start],cv2.COLOR_BGR2GRAY)
# Exclude the changing floor reflections and social overlays from feature seeds.
mask=np.zeros_like(gray); mask[20:425,:]=255
points=cv2.goodFeaturesToTrack(gray,maxCorners=250,qualityLevel=.008,minDistance=7,mask=mask)
rows=[{'id':i,'samples':[[14,float(p[0]),float(p[1])]]} for i,p in enumerate(points[:,0])]
ids=np.arange(len(rows))
for index in range(start+1,round(17*fps)+1):
    nxt=cv2.cvtColor(frames[index],cv2.COLOR_BGR2GRAY)
    new,found,err=cv2.calcOpticalFlowPyrLK(gray,nxt,points,None,winSize=(21,21),maxLevel=3,
        criteria=(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,40,.001))
    back,reverse,_=cv2.calcOpticalFlowPyrLK(nxt,gray,new,None,winSize=(21,21),maxLevel=3)
    valid=(found[:,0]>0)&(reverse[:,0]>0)&(np.linalg.norm(back-points,axis=2)[:,0]<1.)
    valid&=(new[:,0,0]>=0)&(new[:,0,0]<478)&(new[:,0,1]>=0)&(new[:,0,1]<850)
    for identity,p in zip(ids[valid],new[valid,0]):rows[int(identity)]['samples'].append([index/fps,float(p[0]),float(p[1])])
    ids=ids[valid];points=new[valid];gray=nxt
survivors=[r for r in rows if len(r['samples'])==round(3*fps)+1]
out={'source':str(SOURCE.relative_to(ROOT)),'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
     'fps':fps,'method':'Sequential pyramidal LK, forward-backward error < 1 px each step; visual review required.',
     'not_proof_of_rigidity':True,'survivors':survivors,'seed_count':len(rows)}
(OUT/'tracks.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
overlay=Image.new('RGB',(478*3,880),'#17191e');od=ImageDraw.Draw(overlay)
for i,t in enumerate([14,15.5,17]):
    overlay.paste(Image.open(OUT/f'{t:g}s.png'),(478*i,30));od.text((478*i+5,8),f'SOURCE {t}s; tracked source IDs',fill='white')
    for row in survivors:
        p=min(row['samples'],key=lambda x:abs(x[0]-t));x,y=p[1]+478*i,p[2]+30
        color=tuple(int(c) for c in np.random.default_rng(row['id']).integers(100,256,3))
        od.ellipse((x-2,y-2,x+2,y+2),fill=color);od.text((x+3,y),str(row['id']),fill=color)
overlay.save(OUT/'tracked-source.png')
print(json.dumps({'seed_count':len(rows),'survivor_count':len(survivors),'sheet':str(OUT/'sequence.png')}))
