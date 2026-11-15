"""Joint two-view camera/architecture diagnostic; writes separate candidates.

The original constructor and playable export are never overwritten. Compare
a continuous flat hall and a free rear elevation under identical observations.
Neither lower residuals nor solver convergence establish source reconstruction.
"""
from pathlib import Path
import copy
import hashlib
import json
import math
import numpy as np
from scipy.optimize import least_squares

ROOT=Path(__file__).resolve().parents[1]
def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8'))
def module(name):
    path=ROOT/name;namespace={'__file__':str(path),'__name__':'joint_offline_helpers'}
    exec(compile(path.read_text(encoding='utf-8'),str(path),'exec'),namespace)
    return namespace
primary=module('validation/fit_wave_geometry.py')
builder=module('blender/build_wave_corridor.py')
plan=read('blender/wave_corridor_plan.json')
old=read('validation/wave-geometry-fit-candidate.json')
secondary=read('validation/wave-secondary-camera-fit.json')
hall=read('validation/wave-hall-audit.json')
seed=copy.deepcopy(plan['constructor'])
names=primary['NAMES']+['secondary_x','secondary_y','secondary_z','secondary_yaw','secondary_pitch','secondary_roll',
                       'column_x','column_y','column_width','rear_elevation']
values=[old['parameters'][k] for k in primary['NAMES']]
cam=seed['secondary_camera_seed']
initial=np.array(values+cam['position_m']+[cam['yaw_rad'],cam['pitch_rad'],cam['roll_rad']]+[.65,18.2,.64,0.])
lower=np.array(primary['LOWER']+[-.75,.1,.6,1.3,-.65,-.15,-1.5,11.,.25,0.])
upper=np.array(primary['UPPER']+[.75,3.5,1.8,2.05,.03,.15,2.,50.,1.2,2.5])
scales=np.r_[primary['SCALES'],[.3,1.,.25,.12,.15,.06,1.,15.,.4,1.]]
primary_rows=[r for r in old['landmarks'] if r['use']=='fit']
secondary_rows=[r for r in secondary['landmarks'] if r['use']=='fit']

def construct(v):
    cfg=primary['candidate_config'](v[:22],seed)
    camera=copy.deepcopy(seed['secondary_camera_seed'])
    camera.update(position_m=list(map(float,v[22:25])),yaw_rad=float(v[25]),pitch_rad=float(v[26]),
                  roll_rad=float(v[27]),tan_half_vertical_fov=float(v[5]))
    cfg['secondary_camera_seed']=camera
    return cfg

def projected_bounds(points,camera):
    p=primary['projected']({str(i):point for i,point in enumerate(points)},camera)
    xy=np.array(list(p.values()))
    return np.r_[xy.min(axis=0),xy.max(axis=0)]

def observation_residual(v):
    cfg=construct(v);points=primary['geometry'](cfg,builder)
    projections=[primary['projected'](points,cfg[key]) for key in ('camera_seed','secondary_camera_seed')]
    out=[]
    for rows,pp,key in ((primary_rows,projections[0],'reference_px'),(secondary_rows,projections[1],'pixel_xy')):
        for row in rows:out.extend((np.array(pp[row['id']])-row[key])/row['uncertainty_px'])
    # Source jamb samples constrain a visible line without inventing a sill.
    d=cfg['doors'];x=-cfg['corridor']['half_width_m']+2*d['frame_projection_m'];fw=d['frame_width_m']/2
    for row in secondary['visible_jamb_checks']:
        side=row['side'];y=d['centres_y_m'][1]+(-1 if side=='near' else 1)*(d['width_m']/2+fw)
        p=primary['projected']({'bottom':[x,y,0]},cfg['secondary_camera_seed'])['bottom']
        top=np.array(projections[1]['second_door_outer_top_'+side]);direction=np.array(p)-top;q=np.array(row['pixel_xy'])-top
        out.append(float((direction[0]*q[1]-direction[1]*q[0])/np.linalg.norm(direction)/row['uncertainty_px']))
    floor=-sum(f['riser_count']*f['riser_m'] for f in cfg['floor']['flights'])
    z0,z1=floor+v[31],cfg['corridor']['ceiling_z_m']
    corners=[(v[28]+side*v[30]/2,v[29]+end*.31,z) for side in (-1,1) for end in (-1,1) for z in (z0,z1)]
    for observation,key in zip(hall['column_projection_diagnostics'],('camera_seed','secondary_camera_seed')):
        out.extend((projected_bounds(corners,cfg[key])-observation['source_pale_support_bounds_approx_px'])/observation['manual_uncertainty_px'])
    return np.array(out)

def residual(v):
    cfg=construct(v);out=list(observation_residual(v))
    out.extend(.20*(v-initial)/scales)
    p=primary['unpack'](v[:22]);fs=cfg['floor']['flights'];door=cfg['doors']
    out.extend([15*max(0,p['near_end']+.18-p['mid_start']),
                15*max(0,p['mid_start']+p['mid_len']+.18-fs[2]['start_y_m']),
                15*max(0,p['door_first_y']+p['door_w']+.15-p['door_y']),
                15*max(0,p['lamp_c']+.4-p['end']),
                15*max(0,p['end']+.5-v[29]),
                15*max(0,door['thresholds_z_m'][0]+door['height_m']+.06-p['ceiling'])])
    primary_height=v[1]-builder['floor_height'](-.3,cfg)
    secondary_height=v[24]-builder['floor_height'](v[23],cfg)
    out.append((secondary_height-primary_height)/.12)
    return np.array(out)

def fit(raised):
    indices=list(range(32 if raised else 31))
    def expand(v):return v if raised else np.r_[v,0.]
    start=np.clip(initial[indices],lower[indices]+1e-7,upper[indices]-1e-7)
    result=least_squares(lambda v:residual(expand(v)),start,bounds=(lower[indices],upper[indices]),
                         max_nfev=3000,ftol=1e-9,xtol=1e-9,gtol=1e-9)
    values=expand(result.x);cfg=construct(values)
    # These checks prove only a valid solid/door construction, not likeness.
    builder['door_openings'](cfg)
    primary['mesh_check'](builder['floor_geometry'](cfg))
    cfg['destination_hall'].update(half_width_m=4.3,end_y_m=float(max(values[29]+4,24)),
        column_x_m=[-1.9,float(values[28])],column_y_m=float(values[29]),column_size_m=float(values[30]),
        rear_elevation_m=float(values[31]),rear_stair_count=12)
    cfg['ownership_token']='-DREAM-wavejoint-'
    floor=-sum(f['riser_count']*f['riser_m'] for f in cfg['floor']['flights'])
    observations=observation_residual(values)
    bound_hits=[name for name,value,lo,hi in zip(names,values,lower,upper) if min(abs(value-lo),abs(value-hi))<1e-4]
    candidate=copy.deepcopy(plan)
    candidate.update(scene_name='DREAM_WaveJointCandidate',asset_id='wave_joint_candidate',
                     collection_name='DREAM_WaveJointCandidate',stage='joint_gray_candidate_unaccepted',constructor=cfg)
    candidate['validation']={'geometry_gate':'Joint offline fit only; requires real gray renders and source review.'}
    report={'hypothesis':'free rear elevation' if raised else 'continuous flat hall',
        'accepted':False,'solver_converged':bool(result.success),'evaluations':result.nfev,
        'weighted_observation_rms':float(np.sqrt(np.mean(observations**2))),
        'weighted_observation_max':float(np.max(np.abs(observations))),
        'baseline_weighted_observation_rms':float(np.sqrt(np.mean(observation_residual(initial)**2))),
        'parameters':dict(zip(names,map(float,values))),'bounds_reached':bound_hits,
        'eye_height_difference_m':float(values[24]-builder['floor_height'](values[23],cfg)-values[1]),
        'rear_support_bottom_z_m':float(floor+values[31]),'plan':candidate,
        'source_bound_limitation':'The hall support bounds are approximate, with uncertain head occlusion and possible mistaken correspondence. A raised rear fit does not prove a raised platform.'}
    return report

if __name__=='__main__':
    reports={'flat':fit(False),'raised':fit(True)}
    for key,value in reports.items():
        path=ROOT/f'validation/wave-joint-{key}-candidate.json'
        path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
    summary={key:{k:v for k,v in value.items() if k not in ('plan','parameters')} for key,value in reports.items()}
    summary['input_sha256']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in
        ['blender/wave_corridor_plan.json','validation/wave-geometry-fit-candidate.json',
         'validation/wave-secondary-camera-fit.json','validation/wave-hall-audit.json']}
    (ROOT/'validation/wave-joint-fit-diagnostic.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary))
