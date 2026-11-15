"""Joint pose/effective-FOV study; 7s camera held fixed, post shared across views."""
from pathlib import Path
import json,math
import numpy as np
from scipy.optimize import least_squares
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'validation/ocean-exit'
plan=json.loads((ROOT/'blender/ocean_exit_plan.json').read_text(encoding='utf8'))
primary=plan['primary_camera']
old=json.loads((OUT/'post-multiview-fit.json').read_text(encoding='utf8'))
secondary=json.loads((OUT/'secondary-camera-fit.json').read_text(encoding='utf8'))['secondary_camera']
def vector(c):return np.r_[c['position_m'],c['yaw_rad'],c['pitch_rad'],c['roll_rad'],c['tan_half_vertical_fov']]
def project(v,pts):
    x,y,z,yaw,pitch,roll,tan=v
    f=np.array([math.cos(yaw)*math.cos(pitch),math.sin(yaw)*math.cos(pitch),math.sin(pitch)])
    r=np.cross(f,[0,0,1]);r/=np.linalg.norm(r);u=np.cross(r,f)
    rr=r*math.cos(roll)+u*math.sin(roll);uu=u*math.cos(roll)-r*math.sin(roll)
    d=np.asarray(pts)-[x,y,z];depth=d@f;focal=850/(2*tan)
    return np.array([239+(d@rr)/depth*focal,primary['principal_y_px']-(d@uu)/depth*focal]).T
door=np.array([[-.85,5.3,2.4],[.85,5.3,2.4],[.85,5.3,0],[-.85,5.3,0],[0,10000,0]])
doorobs=[np.array(plan['primary_door_observations_px']),np.array([[129,96],[319,97],[318,358],[134,360]]),np.array([[125,64],[350,66],[350,380],[133,383]])]
bases=np.array([[359,425],[397,489],[472,532]])
def unpack(v):return [vector(primary),v[:7],v[7:14]],v[14:]
def res(v):
    cameras,p=unpack(v);x,y,h=p;rows=[]
    for i,c in enumerate(cameras):
        dp=project(c,door)
        rows.extend(((dp[:4]-doorobs[i])/2).ravel())
        rows.append((dp[4,1]-[249,269,280][i])/3)
        rows.extend(((project(c,[[x,y,0]])[0]-bases[i])/8).ravel())
    # Only the primary bent head is unoccluded enough to constrain its height.
    rows.extend((project(cameras[0],[[x-.072,y,h]])[0]-[347,276])/3)
    rows.extend([(c[6]-.85)/.3 for c in cameras[1:]])
    return rows
seed=np.r_[vector(old['camera_9s']),vector(secondary),.585,2.547,.65]
lo=[-.8,-1,.35,1.2,-.3,-.15,.45]*2+[.3,1.9,.35]
hi=[.8,3,1.5,1.9,.35,.15,1.4]*2+[1.2,4.7,1.3]
fit=least_squares(res,seed,bounds=(lo,hi),max_nfev=3000)
cameras,p=unpack(fit.x);result=[]
for i,v in enumerate(cameras):
    c=dict(primary);c.update(position_m=v[:3].tolist(),yaw_rad=float(v[3]),pitch_rad=float(v[4]),roll_rad=float(v[5]),tan_half_vertical_fov=float(v[6]),time_s=[7,9,11.5][i])
    dp=project(v,door);bp=project(v,[[p[0],p[1],0]])[0]
    result.append({'camera':c,'door_rms_px':float(np.sqrt(np.mean(np.sum((dp[:4]-doorobs[i])**2,axis=1)))),
                   'post_base_observed_px':bases[i].tolist(),'post_base_projected_px':bp.tolist(),
                   'post_base_error_px':float(np.linalg.norm(bp-bases[i])),
                   'horizon_error_px':float(dp[4,1]-[249,269,280][i])})
report={'schema':'dream.ocean_camera_post_joint.v1','views':result,'post_xyz_height':p.tolist(),
        'effective_fov_is_fit':True,'principal_shift_shared':True,'accepted':False,
        'limitation':'Effective FOV may represent crop/zoom or reconstruction error. This is not recovered lens metadata. All three views are training observations, not held-out validation.',
        'decision':'pending_native_render'}
(OUT/'camera-post-joint-fit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
print(json.dumps(report,indent=2))
