"""Measure visible pink-wall/teal-ceiling boundaries; keep fitted labels provisional."""
from pathlib import Path
import json
import cv2
import numpy as np
from scipy.optimize import least_squares
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'validation/wave-aperture'
times=[14,14.5,15,15.5,16,16.5,17];reports=[]
sheet=Image.new('RGB',(478*4,390*2),'#17191e');draw=ImageDraw.Draw(sheet)
for j,t in enumerate(times):
    im=np.asarray(Image.open(ROOT/f'validation/wave-motion/{t:g}s.png').convert('RGB'));rgb=im.astype(float)
    pink=((rgb[:,:,0]-rgb[:,:,1]>18)&(rgb[:,:,0]-rgb[:,:,2]>8)).astype('uint8')
    mask=pink[:350];side_reports=[];overlay=Image.fromarray(im[:350]);d=ImageDraw.Draw(overlay)
    for side,(x0,x1) in [('left',(0,239)),('right',(239,478))]:
        part=mask[:,x0:x1];n,labels,stats,_=cv2.connectedComponentsWithStats(part,8)
        idx=1+np.argmax(stats[1:,cv2.CC_STAT_AREA]);component=labels==idx
        samples=[]
        for y in range(10,310,2):
            xs=np.where(component[y])[0]
            if len(xs)<8:continue
            x=(xs[-1] if side=='left' else xs[0])+x0
            samples.append([int(y),int(x)]);d.point((x,y),fill='#ffff22')
        data=np.array(samples,dtype=float)
        # A continuous broken line estimates where the ceiling edge meets the
        # almost vertical hall return. Data are color boundaries, not depth.
        def model(v,y):
            cy,cx,a,b=v
            return cx+np.where(y<cy,a*(y-cy),b*(y-cy))
        guess=[180 if t<16 else 170,170 if side=='left' else 300,.8 if side=='left' else -.8,0]
        fit=least_squares(lambda v:model(v,data[:,0])-data[:,1],guess,
            bounds=([70,0,-3,-.5],[270,478,3,.5]),loss='soft_l1',f_scale=3,max_nfev=800)
        cy,cx,a,b=fit.x;errors=model(fit.x,data[:,0])-data[:,1]
        for y in range(10,310):
            x=model(fit.x,y)
            if 0<=x<478:d.point((x,y),fill='#44ffff')
        d.ellipse((cx-4,cy-4,cx+4,cy+4),outline='#ff5577',width=2)
        side_reports.append({'side':side,'corner_px':[float(cx),float(cy)],'ceiling_dx_dy':float(a),
                             'wall_end_dx_dy':float(b),'median_abs_error_px':float(np.median(abs(errors))),
                             'samples_yx':samples})
    x,y=(j%4)*478,(j//4)*390;sheet.paste(overlay,(x,y+30));draw.text((x+6,y+8),f'SOURCE {t}s / yellow: mask, cyan: segmented fit',fill='white')
    reports.append({'time_s':t,'sides':side_reports})
sheet.save(OUT/'ceiling-edges.png')
out={'schema':'dream.wave_ceiling_edges.v1','accepted':False,'method':'Connected pink-color boundary and robust two-segment line; glow and fittings can bias the corner.',
     'frames':reports}
(OUT/'ceiling-edges.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps([{'time':r['time_s'],'sides':[{k:v for k,v in s.items() if k!='samples_yx'} for s in r['sides']]} for r in reports]))
