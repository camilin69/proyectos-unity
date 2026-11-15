"""Test floor-contact interpretation jointly with existing wall motion.

No scene mutation. A low residual alone cannot validate landmark semantics.
"""
from pathlib import Path
import json
import copy
import numpy as np
from scipy.optimize import least_squares

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'validation/wave-perspective'
OUT.mkdir(exist_ok=True)

def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
def helpers(p):
    p=ROOT/p;ns={'__file__':str(p),'__name__':'perspective_helpers'}
    exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),ns)
    return ns

base=helpers('validation/fit_wave_geometry.py')
builder=helpers('blender/build_wave_corridor.py')
ap=read('validation/wave-aperture/fit.json')
cfg=ap['plan']['constructor'];cams=cfg['all_source_cameras']
old=read('validation/wave-motion/geometry-candidate.json')
alltracks=read('validation/wave-motion/tracks.json')['survivors']
selected=[next(t for t in alltracks if t['id']==i) for i in old['motion_track_ids']]
hall=read('validation/wave-hall-structure/capital-fit.json')
observations=lambda tracks:np.array([[min(t['samples'],key=lambda s:abs(s[0]-c['time_s']))[1:] for t in tracks] for c in cams])
wall_obs=observations(selected);hall_obs=observations(hall['tracks'])
wall_xyz=np.array(old['motion_point_positions'])
poses=np.array([c['position_m']+[c[k] for k in ['yaw_rad','pitch_rad','roll_rad']] for c in cams])
pose_indices=[i for i in range(poses.size) if i not in (1,2)]
npose=len(pose_indices);nwall=len(selected)
floor=hall['floor_z_m']
# Fixed door/lamp coordinates and the corrected independent wall endpoints
# constrain changes to the camera while hall geometry is being investigated.
architecture=base['geometry'](cfg,builder)
for name,y in zip(['nearest_full_lamp_center','next_lamp_center','far_lamp_center'],cfg['ceiling_lights']['centres_y_m']):
    architecture[name]=[0,y,cfg['corridor']['ceiling_z_m']-cfg['ceiling_lights']['mount_drop_m']]
arch_rows=[r for r in old['landmarks'] if 'door' in r['id'] or 'lamp' in r['id']]
arch_keys=list(dict.fromkeys(r['id'] for r in arch_rows))
arch_xyz=np.array([architecture[k] for k in arch_keys])

def project(pts,p,tan):
    yaw,pitch,roll=p[:,3],p[:,4],p[:,5]
    f=np.c_[np.cos(yaw)*np.cos(pitch),np.sin(yaw)*np.cos(pitch),np.sin(pitch)]
    r=np.c_[np.sin(yaw),-np.cos(yaw),np.zeros(len(p))]
    u=np.cross(r,f)
    rr=r*np.cos(roll)[:,None]+u*np.sin(roll)[:,None]
    uu=u*np.cos(roll)[:,None]-r*np.sin(roll)[:,None]
    d=pts[None,:,:]-p[:,:3,None].transpose(0,2,1)
    depth=np.einsum('tnk,tk->tn',d,f)
    depth=np.maximum(depth,.01)
    return np.stack([239+425/tan*np.einsum('tnk,tk->tn',d,rr)/depth,
                     425-425/tan*np.einsum('tnk,tk->tn',d,uu)/depth],axis=2)

def unpack(v):
    pose=poses.ravel().copy();pose[pose_indices]=v[1:1+npose];pose=pose.reshape((-1,6))
    points=wall_xyz.copy();points[:,1:]=v[1+npose:1+npose+nwall*2].reshape((-1,2))
    return pose,points,v[1+npose+nwall*2:]

def hall_points(h):
    x,y,w,cw,ch,offset,ceil,lx,ly,lw=h
    return np.array([[x+offset-cw/2,y,ceil],[x+offset+cw/2,y,ceil],
        [x-w/2,y,ceil-ch],[x+w/2,y,ceil-ch],[x-w/2,y,floor],[x+w/2,y,floor],
        [lx-lw/2,ly,ceil],[lx+lw/2,ly,ceil],[lx-lw/2,ly,floor],[lx+lw/2,ly,floor]])

hall_seed=[.3,35,.8,1.2,.8,.4,5.,-3.,38.,.6]
initial=np.r_[cams[0]['tan_half_vertical_fov'],poses.ravel()[pose_indices],wall_xyz[:,1:].ravel(),hall_seed]
lower=np.r_[.45,np.tile([-.8,-.3,-1.,1.1,-.85,-.2],len(cams))[pose_indices],np.tile([.1,-3],nwall),
            [-2,11,.15,.3,.1,-1,2.5,-8,11,.15]]
upper=np.r_[1.5,np.tile([.8,8.,2.5,2.1,.1,.2],len(cams))[pose_indices],np.tile([30,6],nwall),
            [4,100,2,4,3,2,8,-.5,100,2]]
scales=np.r_[.25,np.tile([.3,2,.5,.12,.12,.08],len(cams))[pose_indices],np.tile([3,1],nwall),[1,25,1,1,1,1,3,2,25,1]]
arch_time_indices=[next(i for i,c in enumerate(cams) if c['time_s']==r['time_s']) for r in arch_rows]
arch_point_indices=[arch_keys.index(r['id']) for r in arch_rows]
arch_obs=np.array([r['source_px'] for r in arch_rows])

def errors(v):
    pose,points,h=unpack(v)
    return project(points,pose,v[0])-wall_obs,project(hall_points(h),pose,v[0])-hall_obs,project(arch_xyz,pose,v[0])[arch_time_indices,arch_point_indices]-arch_obs

def residual(v):
    pose,points,h=unpack(v);wall_e,hall_e,arch_e=errors(v)
    return np.r_[wall_e.ravel()/3,hall_e.ravel()/4,arch_e.ravel()/7,
                 .03*(v-initial)/scales,10*np.maximum(0,pose[:-1,1]+.02-pose[1:,1])]

result=least_squares(residual,np.clip(initial,lower+1e-6,upper-1e-6),bounds=(lower,upper),
                     loss='soft_l1',f_scale=2,max_nfev=700)
pose,pts,h=unpack(result.x)
es=errors(result.x)
report={'schema':'dream.wave_hall_floor_contact_hypothesis.v1','accepted':False,'runtime_promoted':False,
        'hypothesis':'Treat visible lower boundaries as floor contact, allow independent taller hall ceiling and jointly revise camera estimates.',
        'solver_success':bool(result.success),'evaluations':result.nfev,
        'rms_px':{k:float(np.sqrt(np.mean(np.sum(e*e,axis=-1)))) for k,e in zip(['wall_tracks','hall_tracks','door_lamp_landmarks'],es)},
        'tan_half_vertical_fov':float(result.x[0]),
        'hall_parameters':dict(zip(['right_x','right_y','shaft_width','capital_width','capital_height','capital_offset_x','ceiling_z','left_x','left_y','left_width'],map(float,h))),
        'floor_z_m':floor,'hall_clear_height_m':float(h[6]-floor),
        'camera_changes':[{'time_s':c['time_s'],'position_delta_m':(p[:3]-np.array(c['position_m'])).tolist(),
                           'angle_delta_degrees':np.degrees(p[3:]-np.array([c[k] for k in ['yaw_rad','pitch_rad','roll_rad']])).tolist()} for p,c in zip(pose,cams)],
        'cameras':[dict(c,position_m=p[:3].tolist(),yaw_rad=float(p[3]),pitch_rad=float(p[4]),roll_rad=float(p[5]),tan_half_vertical_fov=float(result.x[0])) for p,c in zip(pose,cams)],
        'hall_points_m':hall_points(h).tolist(),
        'hall_observations':hall_obs.tolist(),'hall_projections':project(hall_points(h),pose,result.x[0]).tolist(),
        'limitations':['Lower boundaries remain ambiguous; this fit tests rather than proves floor contact.',
                       'All listed observations participate in this fit, so these are not independent validation residuals.',
                       'No architectural mutation follows automatically from solver convergence.']}
(OUT/'floor-contact-hypothesis.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:report[k] for k in ['solver_success','evaluations','rms_px','tan_half_vertical_fov','hall_parameters','hall_clear_height_m','camera_changes']}))
