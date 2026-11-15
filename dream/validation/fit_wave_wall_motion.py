"""Fit shared wall planes to source tracks; infer cameras independently of stairs.

Fixed corridor width establishes an arbitrary metric scale. Source reflections,
lamps and distant hall supports are excluded from this motion estimate.
"""
from pathlib import Path
import copy
import json
import math
import numpy as np
from scipy.optimize import least_squares

ROOT=Path(__file__).resolve().parents[1]
def read(p): return json.loads((ROOT/p).read_text(encoding='utf-8'))
ns={'__file__':str(ROOT/'validation/fit_wave_geometry.py'),'__name__':'wall_motion_helpers'}
exec(compile(Path(ns['__file__']).read_text(encoding='utf-8'),ns['__file__'],'exec'),ns)
projected=ns['projected']
times=np.array([14,14.5,15,15.5,16,16.5,17])
all_rows=read('validation/wave-motion/tracks.json')['survivors']
# Surface assignments visually checked in the timestamped native source.
left=[110,160,170,175,198,204,245,246]
right=[64,100,107,117,137,166,229]
rows=[next(r for r in all_rows if r['id']==i) for i in left+right]
surfaces=np.array([-1.10]*len(left)+[1.02]*len(right))
observed=np.array([[min(r['samples'],key=lambda s:abs(s[0]-t))[1:] for r in rows] for t in times])
old=read('validation/wave-joint-flat-candidate.json')['plan']['constructor']
poses=[]
for t in times:
    a=old['camera_seed'];b=old['secondary_camera_seed']
    if t<=15.5:
        f=(t-14)/1.5
        p=np.array(a['position_m'])*(1-f)+np.array(b['position_m'])*f
        angle=[a[k]*(1-f)+b[k]*f for k in ['yaw_rad','pitch_rad','roll_rad']]
    else:
        f=(t-15.5)/1.5;p=np.array(b['position_m'])*(1-f)+np.array([0,3.9,1.0])*f
        angle=np.array([b[k] for k in ['yaw_rad','pitch_rad','roll_rad']])*(1-f)+np.array([1.57,-.4,0])*f
    poses.append(np.r_[p,angle])
poses=np.array(poses);poses[0,2]=1.55
tan=old['camera_seed']['tan_half_vertical_fov']
def camera(p,tan):
    return dict(position_m=list(p[:3]),yaw_rad=p[3],pitch_rad=p[4],roll_rad=p[5],
                tan_half_vertical_fov=tan,render_px=[478,850])
def ray(xy,pose,tan):
    yaw,pitch,roll=pose[3:]
    f=np.array([math.cos(yaw)*math.cos(pitch),math.sin(yaw)*math.cos(pitch),math.sin(pitch)])
    r=np.cross(f,[0,0,1]);r/=np.linalg.norm(r);u=np.cross(r,f)
    rr=r*math.cos(roll)+u*math.sin(roll);uu=u*math.cos(roll)-r*math.sin(roll)
    return f+(xy[0]-239)/425*tan*rr-(xy[1]-425)/425*tan*uu
point_seed=[]
for x,xy in zip(surfaces,observed[0]):
    d=ray(xy,poses[0],tan);p=poses[0,:3]+d*(x-poses[0,0])/d[0]
    point_seed.append(p[1:])
point_seed=np.array(point_seed)
# Fix first camera Y/Z only (gauge); no fixed eye height or floor imposed.
indices=[i for i in range(poses.size) if i not in (1,2)]
initial=np.r_[tan,poses.ravel()[indices],point_seed.ravel()]
def unpack(v):
    p=poses.copy().ravel();p[indices]=v[1:1+len(indices)];p=p.reshape((-1,6))
    yz=v[1+len(indices):].reshape((-1,2));pts=np.c_[surfaces,yz]
    return v[0],p,pts
def observations(v):
    tan,p,pts=unpack(v);out=[]
    for pose,obs in zip(p,observed):
        pp=projected(dict(enumerate(pts)),camera(pose,tan))
        for i,xy in enumerate(obs):out.extend((np.array(pp.get(i,[1e5,1e5]))-xy)/2.)
    return np.array(out)
scale=np.r_[.25,np.tile([.4,2.,.5,.15,.2,.1],len(times))[indices],np.tile([3.,1.],len(rows))]
def residual(v):
    tan,p,pts=unpack(v)
    prior=.015*(v-initial)/scale
    monotonic=10*np.maximum(0,p[:-1,1]+.02-p[1:,1])
    return np.r_[observations(v),prior,monotonic]
pose_low=np.tile([-.8,-.3,-1.,1.1,-.8,-.2],len(times))[indices]
pose_high=np.tile([.8,8.,2.,2.1,0.,.2],len(times))[indices]
lower=np.r_[.5,pose_low,np.tile([.1,-2.],len(rows))]
upper=np.r_[1.5,pose_high,np.tile([25.,5.],len(rows))]
fit=least_squares(residual,np.clip(initial,lower+1e-6,upper-1e-6),bounds=(lower,upper),
                  loss='soft_l1',f_scale=2.,max_nfev=1200,ftol=1e-9,xtol=1e-9,gtol=1e-9)
tan,p,pts=unpack(fit.x)
errors=(observations(fit.x)*2).reshape((len(times),len(rows),2))
report={'schema':'dream.wave_wall_motion.v1','accepted':False,'fixed_half_width_m':1.1,
        'solver_success':bool(fit.success),'evaluations':fit.nfev,'tan_half_vertical_fov':tan,
        'pixel_rmse':float(np.sqrt(np.mean(errors**2))),
        'max_point_error_px':float(np.max(np.linalg.norm(errors,axis=2))),
        'cameras':[dict(time_s=float(t),**camera(pose,tan)) for t,pose in zip(times,p)],
        'points':[{'track_id':r['id'],'position_m':list(pos),
                   'max_error_px':float(np.max(np.linalg.norm(errors[:,i],axis=1)))} for i,(r,pos) in enumerate(zip(rows,pts))],
        'limitations':['Track drift, compression and trim depth can violate the plane assignment.',
                       'The arbitrary 2.2 m corridor width sets scale; these are not measured dimensions.',
                       'This motion estimate does not establish floor elevations, full scene fidelity or a finished asset.']}
(ROOT/'validation/wave-motion/wall-fit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report))
