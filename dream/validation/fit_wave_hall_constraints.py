"""Diagnose hall elevation/depth ambiguity across two source views.

No scene/plan mutation: compare the flat-hall hypothesis to an unconstrained
vertical span. Manual bounds are approximate and may include occlusion.
"""
from pathlib import Path
import json
import math
import hashlib
import numpy as np
from scipy.optimize import least_squares

ROOT=Path(__file__).resolve().parents[1]
cfg=json.loads((ROOT/'blender/wave_corridor_plan.json').read_text(encoding='utf-8'))['constructor']
audit=json.loads((ROOT/'validation/wave-hall-audit.json').read_text(encoding='utf-8'))
observations=audit['column_projection_diagnostics']
cameras=[cfg['camera_seed'],cfg['secondary_camera_seed']]
base=-sum(f['riser_count']*f['riser_m'] for f in cfg['floor']['flights'])
ceiling=cfg['corridor']['ceiling_z_m']

def bounds(v,camera):
    x,y,width,z0,z1=v
    points=np.array([(x+dx*width/2,y+dy*.31,z) for dx in (-1,1) for dy in (-1,1) for z in (z0,z1)])
    yaw,pitch,roll=[camera[k] for k in ('yaw_rad','pitch_rad','roll_rad')]
    f=np.array([math.cos(yaw)*math.cos(pitch),math.sin(yaw)*math.cos(pitch),math.sin(pitch)])
    r=np.cross(f,[0,0,1]);r/=np.linalg.norm(r);u=np.cross(r,f)
    rr=r*math.cos(roll)+u*math.sin(roll);uu=u*math.cos(roll)-r*math.sin(roll)
    delta=points-np.array(camera['position_m']);depth=delta@f
    focal=850/(2*camera['tan_half_vertical_fov'])
    px=239+delta@rr/depth*focal;py=425-delta@uu/depth*focal
    return np.array([px.min(),py.min(),px.max(),py.max()])

def errors(v):
    return np.concatenate([(bounds(v,c)-o['source_pale_support_bounds_approx_px'])/o['manual_uncertainty_px']
                           for c,o in zip(cameras,observations)])

def fit(free_elevation):
    initial=np.array([.65,18.2,.64,base,ceiling])
    def expand(v):return v if free_elevation else np.array([*v,base,ceiling])
    seed=initial if free_elevation else initial[:3]
    lo=[-2,10.8,.25,base,ceiling] if free_elevation else [-2,10.8,.25]
    hi=[2,60,1.2,2,5] if free_elevation else [2,60,1.2]
    def residual(v):
        p=expand(v)
        # Weak plausibility prior, never a measurement or acceptance rule.
        prior=[.05*(p[1]-18.2)/15,.05*(p[2]-.64)/.3]
        if free_elevation:prior.append(.05*((p[4]-p[3])-2.5))
        return np.r_[errors(p),prior]
    result=least_squares(residual,seed,bounds=(lo,hi),max_nfev=3000)
    v=expand(result.x)
    return {'solver_converged':bool(result.success),'parameters':dict(zip(['x_m','y_m','width_m','bottom_z_m','top_z_m'],map(float,v))),
            'bottom_above_current_hall_floor_m':float(v[3]-base),'weighted_rms':float(np.sqrt(np.mean(errors(v)**2))),
            'projected_bounds_px':[bounds(v,c).tolist() for c in cameras]}

report={'schema':'dream.wave_hall_constraint_diagnostic.v1','geometry_modified':False,'accepted':False,
        'fixed_flat_hall':fit(False),'free_vertical_span':fit(True),'observations':observations,
        'interpretation':'Allowing a different vertical span tests a raised/reconfigured rear area versus errors in the existing cameras and floor. It does not prove a raised platform. Source occlusion and ambiguous support identification must be resolved before modelling steps.',
        'next_action':'Jointly fit corridor floor, camera poses and hall supports from additional views. Do not adjust lights to hide this geometric residual.',
        'input_sha256':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['blender/wave_corridor_plan.json','validation/wave-hall-audit.json']}}
(ROOT/'validation/wave-hall-constraint-diagnostic.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:report[k] for k in ('fixed_flat_hall','free_vertical_span','geometry_modified')}))
