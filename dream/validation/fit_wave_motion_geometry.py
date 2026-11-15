"""Geometry proposal conditioned on seven source-tracked camera poses."""
from pathlib import Path
import copy
import json
import numpy as np
from scipy.optimize import least_squares

ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
def module(p):
    p=ROOT/p;ns={'__file__':str(p),'__name__':'motion_geometry_helpers'}
    exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),ns);return ns
base=module('validation/fit_wave_geometry.py');builder=module('blender/build_wave_corridor.py')
motion=read('validation/wave-motion/wall-fit.json')
plan=read('blender/wave_corridor_plan.json');seed=plan['constructor']
old=read('validation/wave-geometry-fit-candidate.json')
second=read('validation/wave-secondary-camera-fit.json')
cams=motion['cameras'];bytime={c['time_s']:c for c in cams}
keys=base['NAMES'][6:]+['far_start','far_length','far_drop','lamp_drop']
start=np.array([old['parameters'][k] for k in base['NAMES'][6:]]+[7.2,.84,.3,.16])
lower=np.array([1.8,6., .6,2.5,.7,1.8,-1.5,.1,1.1,2.3,.7,.2,.06,1.7,3.,4.]+[5.3,.5,.15,.05])
upper=np.array([3.4,14.,3.3,6.,1.4,2.6,.1,1.2,3.1,6.,3.,1.2,.55,6.,9.,13.]+[11.,1.8,.9,.5])
scale=np.r_[base['SCALES'][6:],[2.,.5,.4,.2]]
primary=[copy.deepcopy(r) for r in old['landmarks'] if r['use']=='fit']
# Review of the source sequence: former far-lamp annotation touched its lower edge.
for r in primary:
    if r['id']=='far_lamp_center':r['reference_px']=[233,170];r['uncertainty_px']=7
rows={14:[(r['id'],r['reference_px'],r['uncertainty_px']) for r in primary],
      15.5:[(r['id'],r['pixel_xy'],r['uncertainty_px']) for r in second['landmarks'] if r['use']=='fit'],
      17:[('far_lamp_center',[245,110],7),('aperture_top_left',[148,189],12),
          ('aperture_top_right',[334,182],12),('middle_trim_end_left',[74,497],10),
          ('middle_trim_end_right',[405,554],12)]}
def config(v):
    a=cams[0]
    vec=np.r_[a['position_m'][0],a['position_m'][2],a['yaw_rad'],a['pitch_rad'],a['roll_rad'],a['tan_half_vertical_fov'],v[:16]]
    cfg=base['candidate_config'](vec,seed)
    cfg['camera_seed']=copy.deepcopy(cams[0]);cfg['secondary_camera_seed']=copy.deepcopy(bytime[15.5])
    cfg['floor']['flights'][2].update(start_y_m=float(v[16]),tread_m=float(v[17]/3),riser_m=float(v[18]/3))
    cfg['corridor']['solid_bottom_z_m']=-sum(f['riser_count']*f['riser_m'] for f in cfg['floor']['flights'])-.3
    cfg['ceiling_lights']['mount_drop_m']=float(v[19])
    return cfg
def points(cfg):
    p=base['geometry'](cfg,builder)
    for name in ['nearest_full_lamp_center','next_lamp_center','far_lamp_center']:
        p[name][2]=cfg['corridor']['ceiling_z_m']-cfg['ceiling_lights']['mount_drop_m']
    return p
def obs(v):
    cfg=config(v);p=points(cfg);out=[]
    for time,rr in rows.items():
        pp=base['projected'](p,bytime[time])
        for name,xy,sigma in rr:out.extend((np.array(pp.get(name,[1e5,1e5]))-xy)/sigma)
    return np.array(out)
def residual(v):
    cfg=config(v);out=list(obs(v));out.extend(.12*(v-start)/scale)
    p=base['unpack'](np.r_[np.zeros(6),v[:16]])
    out.extend([30*max(0,p['near_end']+.2-p['mid_start']),
                30*max(0,p['mid_start']+p['mid_len']+.2-v[16]),
                30*max(0,v[16]+v[17]+.2-p['end']),
                30*max(0,p['door_first_y']+p['door_w']+.18-p['door_y']),
                30*max(0,p['door_z']+p['door_h']+.08-p['ceiling']),
                30*max(0,p['lamp_c']+.2-p['end'])])
    # Walking camera may bob; use a continuous flight grade, not a quantized
    # stair-height function, as a soft motion constraint during optimization.
    for cam in cams[1:]:
        grade=builder['rail_height'](cam['position_m'][1],cfg)-cfg['rails']['height_above_floor_m']
        out.append((cam['position_m'][2]-grade-1.55)/.16)
    return np.array(out)
first=least_squares(residual,np.clip(start,lower+1e-6,upper-1e-6),bounds=(lower,upper),max_nfev=2500)
# Wall-only reconstruction has an unconstrained global rotation about X.
# Fit the architecture and tracked cameras together to resolve that gauge.
all_tracks=read('validation/wave-motion/tracks.json')['survivors']
selected=[p for p in motion['points'] if p['max_error_px']<8]
track_ids=[p['track_id'] for p in selected]
track_xyz=np.array([p['position_m'] for p in selected])
track_obs=np.array([[min(next(r for r in all_tracks if r['id']==i)['samples'],key=lambda s:abs(s[0]-c['time_s']))[1:]
                     for i in track_ids] for c in cams])
pose_initial=np.array([c['position_m']+[c[k] for k in ['yaw_rad','pitch_rad','roll_rad']] for c in cams])
pose_indices=[i for i in range(pose_initial.size) if i not in (1,2)]
npose=len(pose_indices);npoints=len(selected)
joint_initial=np.r_[first.x,motion['tan_half_vertical_fov'],pose_initial.ravel()[pose_indices],track_xyz[:,1:].ravel()]
joint_lower=np.r_[lower,.5,np.tile([-.8,-.3,-1.,1.1,-.8,-.2],len(cams))[pose_indices],np.tile([.1,-3.],npoints)]
joint_upper=np.r_[upper,1.5,np.tile([.8,8.,2.,2.1,0.,.2],len(cams))[pose_indices],np.tile([25.,5.],npoints)]
def joint_unpack(v):
    p=pose_initial.copy().ravel();p[pose_indices]=v[21:21+npose];p=p.reshape((-1,6))
    for c,pose in zip(cams,p):
        c.update(position_m=list(pose[:3]),yaw_rad=pose[3],pitch_rad=pose[4],roll_rad=pose[5],tan_half_vertical_fov=v[20])
    return p,np.c_[track_xyz[:,0],v[21+npose:].reshape((-1,2))]
def joint_residual(v):
    poses,pts=joint_unpack(v);out=list(residual(v[:20]))
    for c,source in zip(cams,track_obs):
        pp=base['projected'](dict(enumerate(pts)),c)
        for i,xy in enumerate(source):out.extend((np.array(pp.get(i,[1e5,1e5]))-xy)/3.)
    # Weak priors preserve a plausible lens and camera motion, while allowing
    # scene geometry to determine global pitch and ceiling height.
    out.extend(.02*(v[20:]-joint_initial[20:])/np.r_[.25,np.tile([.4,2.,.5,.15,.2,.1],len(cams))[pose_indices],np.tile([3.,1.],npoints)])
    out.extend(10*np.maximum(0,poses[:-1,1]+.02-poses[1:,1]))
    return np.array(out)
result=least_squares(joint_residual,np.clip(joint_initial,joint_lower+1e-6,joint_upper-1e-6),
    bounds=(joint_lower,joint_upper),max_nfev=1000,loss='soft_l1',f_scale=2.,ftol=1e-8,xtol=1e-8,gtol=1e-8)
_,final_points=joint_unpack(result.x)
cfg=config(result.x[:20]);cfg['ownership_token']='-DREAM-wavemotion-'
cfg['all_source_cameras']=copy.deepcopy(cams)
cfg['destination_hall']['end_y_m']=max(cfg['corridor']['end_y_m']+10.,seed['destination_hall']['end_y_m'])
builder['door_openings'](cfg)
checks={'floor':base['mesh_check'](builder['floor_geometry'](cfg)),
        'rails':[base['mesh_check'](builder['sweep_tube'](builder['rail_path'](s,cfg),cfg['rails']['radius_m'],cfg['rails']['tube_sides'])) for s in (-1,1)]}
candidate=copy.deepcopy(plan);candidate.update(scene_name='DREAM_WaveMotionCandidate',asset_id='wave_motion_candidate',
    collection_name='DREAM_WaveMotionCandidate',constructor=cfg,stage='source_motion_gray_candidate_unaccepted')
details=[];ppoints=points(cfg)
for time,rr in rows.items():
    pp=base['projected'](ppoints,bytime[time])
    for name,xy,sigma in rr:
        details.append(dict(time_s=time,id=name,source_px=xy,projected_px=pp[name],error_px=float(np.linalg.norm(np.array(pp[name])-xy))))
report=dict(schema='dream.wave_motion_geometry.v1',accepted=False,solver_converged=bool(result.success),
    weighted_observation_rms=float(np.sqrt(np.mean(obs(result.x[:20])**2))),parameters=dict(zip(keys,map(float,result.x[:20]))),
    motion_track_ids=track_ids,excluded_motion_track_ids=[p['track_id'] for p in motion['points'] if p['max_error_px']>=8],
    motion_point_positions=final_points.tolist(),
    mesh_checks=checks,landmarks=details,plan=candidate,
    limitations=['Camera poses come from a robust wall-track fit with remaining outliers; they are estimates.',
                 'Hall geometry is retained as an unresolved draft; no hall silhouette acceptance is claimed.',
                 'Geometry requires actual multi-camera gray renders; no textures or runtime exports changed.'])
(ROOT/'validation/wave-motion/geometry-candidate.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:report[k] for k in ['weighted_observation_rms','parameters','landmarks']}))
