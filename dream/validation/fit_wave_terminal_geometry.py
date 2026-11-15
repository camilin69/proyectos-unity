"""Fit two terminal guards with feet attached to a continuous stair flight."""
from pathlib import Path
import copy
import json
import numpy as np
from scipy.optimize import least_squares

ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
def module(p):
    p=ROOT/p;ns={'__file__':str(p),'__name__':'terminal_geometry_helpers'}
    exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),ns);return ns
base=module('validation/fit_wave_geometry.py');builder=module('blender/build_wave_corridor.py')
old=read('validation/wave-motion/geometry-candidate.json');seed=old['plan']['constructor']
tracks=read('validation/wave-terminal/rail-tracks.json')['tracks']
cams=seed['all_source_cameras'];cam_by_time={c['time_s']:c for c in cams}
observed=np.array([[min(r['samples'],key=lambda s:abs(s[0]-c['time_s']))[1:] for r in tracks] for c in cams])
independent=read('validation/wave-terminal/fit.json')['parameters']
# Variables: near Y, frame length, middle drop, last drop, guard height,
# guard X left/right, middle start/length, low-trim height.
near_drop=seed['floor']['flights'][0]['riser_count']*seed['floor']['flights'][0]['riser_m']
initial=np.array([independent['near_y'],independent['length'],-independent['near_floor_z']-near_drop,
                  independent['descent'],independent['height'],-1.035,1.035,
                  seed['floor']['flights'][1]['start_y_m'],
                  seed['floor']['flights'][1]['riser_count']*seed['floor']['flights'][1]['tread_m'],
                  seed['rails']['height_above_floor_m']])
lower=[7.5,.6,.2,.15,.7,-1.055,.8,2.5,.8,.08]
upper=[13.,1.8,1.,.6,1.4,-.8,1.055,5.5,3.,.6]
def config(v):
    c=copy.deepcopy(seed);fs=c['floor']['flights']
    fs[1].update(start_y_m=float(v[7]),tread_m=float(v[8]/fs[1]['riser_count']),riser_m=float(v[2]/fs[1]['riser_count']))
    fs[2].update(start_y_m=float(v[0]+.04),tread_m=float((v[1]-.08)/fs[2]['riser_count']),riser_m=float(v[3]/fs[2]['riser_count']))
    c['corridor'].update(wall_end_y_m=float(v[0]-.07),end_y_m=float(v[0]+v[1]+.15),solid_bottom_z_m=float(-near_drop-v[2]-v[3]-.3))
    c['rails'].update(end_y_m=float(v[0]-.09),height_above_floor_m=float(v[9]))
    c['terminal_guards']={'x_m':[float(v[5]),float(v[6])],'near_y_m':float(v[0]),'far_y_m':float(v[0]+v[1]),
                         'height_m':float(v[4]),'tube_radius_m':.022,'sides':16,
                         'classification':'Two short tall guard frames, separate from the dark low wall trim.',
                         'status':'Gray reconstruction; panel infill and exact metal finish unresolved.'}
    return c
def corners(cfg):
    g=cfg['terminal_guards'];p=[]
    for x in g['x_m']:
        yn,yf=g['near_y_m'],g['far_y_m'];zn,zf=builder['floor_height'](yn,cfg),builder['floor_height'](yf,cfg)
        p.extend([[x,yn,zn+g['height_m']],[x,yf,zf+g['height_m']],[x,yn,zn],[x,yf,zf]])
    return p
def errors(v):
    c=config(v);p=corners(c);out=[]
    for cam,obs in zip(cams,observed):
        pp=base['projected'](dict(enumerate(p)),cam)
        for i,xy in enumerate(obs):out.extend((np.array(pp[i])-xy)/5.)
    return np.array(out)
def residual(v):
    c=config(v);p=base['geometry'](c,builder)
    for name in ['aperture_top_left','aperture_top_right']:p[name][1]=c['corridor']['wall_end_y_m']
    out=list(errors(v))
    # Preserve existing door/lamp/camera work; only floor and opening landmarks
    # participate in this local terminal-structure adjustment.
    for row in old['landmarks']:
        if not any(k in row['id'] for k in ['rail_corner','trim_end','flight_end','aperture_top']):continue
        pp=base['projected'](p,cam_by_time[row['time_s']])[row['id']]
        out.extend((np.array(pp)-row['source_px'])/12.)
    out.extend(.15*(v-initial)/np.array([2.,.5,.3,.2,.3,.1,.1,1.,1.,.3]))
    out.append(30*max(0,v[7]+v[8]+.3-v[0]))
    return np.array(out)
fit=least_squares(residual,np.clip(initial,lower,upper),bounds=(lower,upper),loss='soft_l1',f_scale=2.,max_nfev=1500)
c=config(fit.x);c['ownership_token']='-DREAM-waveterminal-'
builder['door_openings'](c)
mesh=base['mesh_check'](builder['floor_geometry'](c))
plan=copy.deepcopy(old['plan']);plan.update(scene_name='DREAM_WaveTerminalCandidate',asset_id='wave_terminal_candidate',
    collection_name='DREAM_WaveTerminalCandidate',constructor=c,stage='terminal_guards_gray_candidate_unaccepted')
row_errors=errors(fit.x).reshape((7,8,2))*5
guardrows=[]
for cam,err,source in zip(cams,row_errors,observed):
    pp=base['projected'](dict(enumerate(corners(c))),cam)
    guardrows.append({'time_s':cam['time_s'],'points':[{'id':r['id'],'source_px':source[i].tolist(),'projected_px':pp[i],
                    'distance_px':float(np.linalg.norm(err[i]))} for i,r in enumerate(tracks)]})
report={'schema':'dream.wave_terminal_geometry.v1','accepted':False,'runtime_promoted':False,
        'point_distance_rms_px':float(np.sqrt(np.mean(np.sum(row_errors**2,axis=2)))),
        'max_point_distance_px':float(np.max(np.linalg.norm(row_errors,axis=2))),
        'plan':plan,'corners_m':corners(c),'guard_observations':guardrows,'floor_mesh':mesh,
        'attachment_policy':'Each post extends into its tread by 8 mm; near/far foot elevations queried from the same floor mesh profile.',
        'limitations':['The two frame feet remain partially occluded in the source; correspondences are approximate.',
                       'The wall-end/floor-end separation is a reconstruction hypothesis, not a recovered construction drawing.',
                       'Old camera and ceiling estimates remain fixed; hall supports and opening-height discrepancies are unresolved.']}
(ROOT/'validation/wave-terminal/geometry-candidate.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'rms_px':report['point_distance_rms_px'],'max_px':report['max_point_distance_px'],
                  'guards':c['terminal_guards'],'floor':c['floor']['flights'],'corridor':c['corridor']}))
