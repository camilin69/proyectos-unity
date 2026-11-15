"""Fit a static access post using 7s/9s; reserve 11.5s for validation."""
from pathlib import Path
import json,math
import numpy as np
from scipy.optimize import least_squares

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'validation/ocean-exit'
plan=json.loads((ROOT/'blender/ocean_exit_plan.json').read_text(encoding='utf8'))
c=plan['primary_camera']
def pose(camera):return np.r_[camera['position_m'],camera['yaw_rad'],camera['pitch_rad'],camera['roll_rad']]
def project(v,points):
    x,y,z,yaw,pitch,roll=v
    f=np.array([math.cos(yaw)*math.cos(pitch),math.sin(yaw)*math.cos(pitch),math.sin(pitch)])
    r=np.cross(f,[0,0,1]);r/=np.linalg.norm(r);u=np.cross(r,f)
    rr=r*math.cos(roll)+u*math.sin(roll);uu=u*math.cos(roll)-r*math.sin(roll)
    d=np.asarray(points)-[x,y,z];depth=d@f;focal=850/(2*c['tan_half_vertical_fov'])
    return np.array([239+(d@rr)/depth*focal,c['principal_y_px']-(d@uu)/depth*focal]).T

door=np.array([[-.85,5.3,2.4],[.85,5.3,2.4],[.85,5.3,0],[-.85,5.3,0],[0,10000,0]])
observed9=np.array([[129,96],[319,97],[318,358],[134,360]])
def cres(v):
    q=project(v,door)
    return np.r_[(q[:4]-observed9).ravel(),(q[4,1]-269)/2]
seed=pose(c);seed[1]+=.55
fit=least_squares(cres,seed,bounds=([-.8,-.3,.35,1.2,-.3,-.15],[.8,3,1.4,1.9,.35,.15]),max_nfev=2000)
cam9=dict(c);v=fit.x
cam9.update(position_m=v[:3].tolist(),yaw_rad=float(v[3]),pitch_rad=float(v[4]),roll_rad=float(v[5]),time_s=9)
cam11=json.loads((OUT/'secondary-camera-fit.json').read_text(encoding='utf8'))['secondary_camera']
cams=[c,cam9,cam11]
# Approximate water intersection is occluded by foam and treated with low weight.
# Head at 9s partly overlaps the video overlay; its uncertainty is larger.
observed=[np.array([[347,276],[359,425]]),np.array([[382,282],[397,489]]),np.array([[np.nan,np.nan],[472,532]])]
def points(v):
    x,y,h=v
    return [[x-.072,y,h],[x,y,0]]
def residual(v):
    return np.concatenate([((project(pose(cam),points(v))-o)/np.array([[3],[12]])).ravel() for cam,o in zip(cams[:2],observed[:2])])
result=least_squares(residual,[.585,2.547,.676],bounds=([.25,1.8,.35],[1.1,4.7,1.3]))
old=[.585,2.547,.676];new=result.x.tolist()
rows=[]
for cam,o in zip(cams,observed):
    qold=project(pose(cam),points(old));q=project(pose(cam),points(new))
    rows.append({'time_s':cam['time_s'],'use':'fit' if cam['time_s']!=11.5 else 'held_out',
                 'observed_head_px':o[0].tolist() if np.isfinite(o[0]).all() else None,'observed_water_intersection_px':o[1].tolist(),
                 'old_projected_px':qold.tolist(),'new_projected_px':q.tolist(),
                 'water_intersection_error_px':float(np.linalg.norm(q[1]-o[1]))})
report={'schema':'dream.ocean_exit_post_multiview.v1','camera_9s':cam9,
        'door_9s_rms_px':float(np.sqrt(np.mean(np.sum((project(pose(cam9),door)[:4]-observed9)**2,axis=1)))),
        'post_old_xyz_height':old,'post_candidate_xyz_height':new,'views':rows,
        'measurement_uncertainty':'Head +/-3px or more where overlaid text intersects; foam/water intersection +/-12px. Metric scale and camera intrinsics remain assumptions.',
        'decision':'pending_native_render','accepted':False}
(OUT/'post-multiview-fit.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf8')
print(json.dumps(report,indent=2,allow_nan=False))
