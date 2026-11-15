"""Test whether the visible post end is submerged, retaining fixed lens cameras."""
from pathlib import Path
import math,json
import numpy as np
from scipy.optimize import least_squares
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'validation/ocean-exit'
p=json.loads((ROOT/'blender/ocean_exit_plan.json').read_text(encoding='utf8'))
first=p['primary_camera'];mid=json.loads((OUT/'post-multiview-fit.json').read_text(encoding='utf8'))['camera_9s']
last=json.loads((OUT/'secondary-camera-fit.json').read_text(encoding='utf8'))['secondary_camera']
def project(c,pts):
    yaw,pitch,roll=[c[k] for k in ['yaw_rad','pitch_rad','roll_rad']]
    f=np.array([math.cos(yaw)*math.cos(pitch),math.sin(yaw)*math.cos(pitch),math.sin(pitch)])
    r=np.cross(f,[0,0,1]);r/=np.linalg.norm(r);u=np.cross(r,f)
    rr=r*math.cos(roll)+u*math.sin(roll);uu=u*math.cos(roll)-r*math.sin(roll)
    d=np.asarray(pts)-c['position_m'];focal=850/(2*c['tan_half_vertical_fov'])
    return np.array([239+(d@rr)/(d@f)*focal,c['principal_y_px']-(d@uu)/(d@f)*focal]).T
cameras=[first,mid,last];ends=np.array([[359,425],[397,489],[472,532]])
def res(v):
    x,y,z,h=v
    rows=[(project(c,[[x,y,z]])[0]-o)/8 for c,o in zip(cameras,ends)]
    rows.append((project(first,[[x-.072,y,h]])[0]-[347,276])/3)
    return np.concatenate(rows)
fit=least_squares(res,[.9,3.5,-.4,.6],bounds=([.3,2,-.75,.2],[1.5,4.9,.1,1.4]))
x,y,z,h=fit.x
rows=[{'time_s':c['time_s'],'visible_end_px':o.tolist(),'projected_end_px':project(c,[[x,y,z]])[0].tolist(),
       'end_error_px':float(np.linalg.norm(project(c,[[x,y,z]])[0]-o)),
       'projected_head_px':project(c,[[x-.072,y,h]])[0].tolist()} for c,o in zip(cameras,ends)]
report={'schema':'dream.ocean_submerged_post.v1','post_x_y_bottom_top_m':fit.x.tolist(),
        'cameras':cameras,'views':rows,'fixed_effective_fov':True,
        'previous_endpoint_interpretation_rejected':'Visible post endpoint was assumed at water z=0. Video water can obscure a submerged endpoint; that assumption was not observed evidence.',
        'limitations':['Visible end is approximate and partially occluded by water.','All three post views used for fit; no held-out claim.','Refraction not modeled in this straight-ray fit.'],
        'accepted':False,'decision':'pending_native_render'}
(OUT/'submerged-post-fit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
print(json.dumps(report,indent=2))
