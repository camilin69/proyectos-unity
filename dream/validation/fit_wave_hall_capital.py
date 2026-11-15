"""Fit visible capital/shaft color boundaries; never treat paint as floor contact."""
from pathlib import Path
import json
import copy
import cv2
import numpy as np
from scipy.optimize import least_squares
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'validation/wave-hall-structure'
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
ns={'__file__':str(ROOT/'validation/fit_wave_geometry.py'),'__name__':'hall_capital_helpers'}
exec(compile(Path(ns['__file__']).read_text(encoding='utf-8'),ns['__file__'],'exec'),ns)
source=ROOT/'referencias/estetica/originales/WhatsApp Video 2026-10-08 at 6.27.42 PM.mp4'
cap=cv2.VideoCapture(str(source));fps=cap.get(cv2.CAP_PROP_FPS);cap.set(cv2.CAP_PROP_POS_FRAMES,round(14*fps));frames={}
for i in range(round(14*fps),round(17*fps)+1):
    ok,frame=cap.read();assert ok;frames[i]=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
cap.release()
seeds={'capital_left':[268,178],'capital_right':[299,182],
       'shoulder_left':[256,218],'shoulder_right':[274,218],
       'paint_lower_left':[248,272],'paint_lower_right':[266,275],
       'left_form_top_left':[164,191],'left_form_top_right':[182,194],
       'left_form_bottom_left':[162,263],'left_form_bottom_right':[178,267]}
tracks=[]
for name,xy in seeds.items():
    points=np.array([[xy]],dtype=np.float32);samples=[[17,*map(float,xy)]];errors=[]
    for i in range(round(17*fps),round(14*fps),-1):
        q,st,_=cv2.calcOpticalFlowPyrLK(frames[i],frames[i-1],points,None,winSize=(17,17),maxLevel=3,
            criteria=(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,40,.001))
        back,bst,_=cv2.calcOpticalFlowPyrLK(frames[i-1],frames[i],q,None,winSize=(17,17),maxLevel=3)
        err=float(np.linalg.norm(back-points));errors.append(err)
        if not st[0,0] or not bst[0,0] or err>1:break
        points=q;samples.append([(i-1)/fps,*map(float,q[0,0])])
    tracks.append({'id':name,'complete':len(samples)==91,'max_fb_error_px':max(errors),'samples':sorted(samples)})
assert all(t['complete'] for t in tracks)
aperture=read('validation/wave-aperture/fit.json');cfg=aperture['plan']['constructor'];cams=cfg['all_source_cameras']
obs=np.array([[min(t['samples'],key=lambda s:abs(s[0]-c['time_s']))[1:] for t in tracks] for c in cams])
ceiling=cfg['corridor']['ceiling_z_m'];floor=-sum(f['riser_count']*f['riser_m'] for f in cfg['floor']['flights'])
# Capital center may overhang the shaft; the lower paint boundary is a
# material landmark only. The shaft itself always continues to the floor.
names=['shaft_x','front_y','shaft_width','capital_width','capital_height','capital_offset_x','paint_lower_z']
def points(v):
    x,y,w,cw,ch,offset,zpaint=v
    return np.array([[x+offset-cw/2,y,ceiling],[x+offset+cw/2,y,ceiling],
                     [x-w/2,y,ceiling-ch],[x+w/2,y,ceiling-ch],
                     [x-w/2,y,zpaint],[x+w/2,y,zpaint]])
def errors(v):
    p=points(v);out=[]
    for c,xy in zip(cams,obs):
        pp=ns['projected'](dict(enumerate(p)),c)
        for i,target in enumerate(xy[:6]):out.extend(np.array(pp[i])-target)
    return np.array(out)
initial=np.array([.5,18.,.55,1.3,.8,.15,.6])
def residual(v):
    return np.r_[errors(v)/5.,.1*(v-initial)/[.8,10.,.4,1.,.6,.5,.8],20*max(0,v[6]+.2-(ceiling-v[4]))]
fit=least_squares(residual,initial,bounds=([-1.,10.,.15,.4,.2,-1.,floor],[3.,50.,1.5,3.,1.8,1.5,1.7]),
                  loss='soft_l1',f_scale=2.,max_nfev=1000)
p=points(fit.x);err=errors(fit.x).reshape((7,6,2));floor_checks=[]
def left_points(v):
    x,y,w,z=v
    return np.array([[x-w/2,y,ceiling],[x+w/2,y,ceiling],[x-w/2,y,z],[x+w/2,y,z]])
def left_error(v):
    out=[]
    for cam,xy in zip(cams,obs[:,6:]):
        pp=ns['projected'](dict(enumerate(left_points(v))),cam)
        for i,target in enumerate(xy):out.extend(np.array(pp[i])-target)
    return np.array(out)
left_fit=least_squares(left_error,[-1.4,17,.3,1.0],bounds=([-4.,10.,.1,floor],[-.5,40.,1.0,1.7]),loss='soft_l1',f_scale=5)
left_result={'parameters':dict(zip(['center_x','front_y','width','visible_bottom_z'],map(float,left_fit.x))),
             'point_distance_rms_px':float(np.sqrt(np.mean(np.sum(left_error(left_fit.x).reshape((7,4,2))**2,axis=2))))}
for c in cams:
    pp=ns['projected']({'base':[fit.x[0],fit.x[1],floor]},c)
    floor_checks.append({'time_s':c['time_s'],'physical_shaft_floor_projection_px':pp['base'],
                         'paint_boundary_is_not_base':True})
overlay=Image.new('RGB',(478*3,884),'#17191e');d=ImageDraw.Draw(overlay)
for j,time in enumerate([14,15.5,17]):
    overlay.paste(Image.open(ROOT/f'validation/wave-motion/{time:g}s.png'),(478*j,34));d.text((478*j+5,8),f'SOURCE {time:g}s / circles: tracked / crosses: fit',fill='white')
    index=next(i for i,c in enumerate(cams) if c['time_s']==time);pp=ns['projected'](dict(enumerate(p)),cams[index])
    for i,xy in enumerate(obs[index,:6]):
        x,y=xy+[478*j,34];color='#ffb544' if i>=4 else '#55ffee'
        d.ellipse((x-3,y-3,x+3,y+3),outline=color,width=1)
        x,y=np.array(pp[i])+[478*j,34];d.line((x-4,y,x+4,y),fill='#ffffff');d.line((x,y-4,x,y+4),fill='#ffffff')
overlay.save(OUT/'capital-projection.png')
report={'schema':'dream.wave_hall_capital.v1','accepted':False,'parameters':dict(zip(names,map(float,fit.x))),
        'floor_z_m':floor,'ceiling_z_m':ceiling,'point_distance_rms_px':float(np.sqrt(np.mean(np.sum(err**2,axis=2)))),
        'max_point_error_px':float(np.max(np.linalg.norm(err,axis=2))),
        'tracks':tracks,'physical_base_diagnostics':floor_checks,'left_visible_form':left_result,
        'classification':'Visible support has a flared upper capital and narrower shaft. Lower cyan/pale color boundary is not asserted to be floor contact.',
        'limitations':['Capital overhang and material boundary heights are inferred from compressed source frames.',
                       'The shaft extends to the continuous hall floor; that floor contact remains visibly unverified.',
                       'No geometry acceptance or export follows automatically from these fitted color landmarks.']}
(OUT/'capital-fit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='tracks'}))
