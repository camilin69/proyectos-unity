"""Fit a second pose with fixed lens/shift; no source pixel baking or bpy."""
from pathlib import Path
import json
import math
import numpy as np
from scipy.optimize import least_squares

ROOT=Path(__file__).resolve().parents[1]
plan=json.loads((ROOT/'blender/ocean_exit_plan.json').read_text(encoding='utf8'))
c=plan['primary_camera']
points=np.array([[-.85,5.3,2.4],[.85,5.3,2.4],[.85,5.3,0],[-.85,5.3,0],[0,10000,0]])
observed=np.array([[125,64],[350,66],[350,380],[133,383],[239,280]])

def project(pose,points):
    x,y,z,yaw,pitch,roll=pose
    f=np.array([math.cos(yaw)*math.cos(pitch),math.sin(yaw)*math.cos(pitch),math.sin(pitch)])
    r=np.cross(f,[0,0,1]);r/=np.linalg.norm(r);u=np.cross(r,f)
    rr=r*math.cos(roll)+u*math.sin(roll);uu=u*math.cos(roll)-r*math.sin(roll)
    d=points-[x,y,z];depth=d@f;focal=850/(2*c['tan_half_vertical_fov'])
    return np.array([239+(d@rr)/depth*focal,c['principal_y_px']-(d@uu)/depth*focal]).T

def residual(v):
    pred=project(v,points)
    return np.r_[(pred[:4]-observed[:4]).ravel(),(pred[4,1]-280)/2]

seed=np.r_[c['position_m'],c['yaw_rad'],c['pitch_rad'],c['roll_rad']]
seed[1]+=1
fit=least_squares(residual,seed,bounds=([-.8,-.3,.35,1.2,-.3,-.15],[.8,3,1.4,1.9,.35,.15]),max_nfev=2000)
pose=fit.x
secondary=dict(c)
secondary.update(position_m=pose[:3].tolist(),yaw_rad=float(pose[3]),pitch_rad=float(pose[4]),roll_rad=float(pose[5]),time_s=11.5)
report={'schema':'dream.ocean_exit_camera_fit.v1','secondary_camera':secondary,
        'observed_door_px':observed[:4].tolist(),'projected_door_px':project(pose,points)[:4].tolist(),
        'door_corner_rms_px':float(np.sqrt(np.mean(np.sum((project(pose,points)[:4]-observed[:4])**2,axis=1)))),
        'horizon_reference_y_px':280,'horizon_projected_y_px':float(project(pose,points)[4,1]),
        'fixed_intrinsics':['tan_half_vertical_fov','principal_y_px','shift_y'],
        'limitation':'Four manual door corners and approximate horizon fit only. Other scene landmarks and rendered appearance remain validation evidence, not this training residual.'}
(ROOT/'validation/ocean-exit/secondary-camera-fit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
print(json.dumps(report,indent=2))
