"""Fit only a 17 s camera against fixed joint-flat geometry; no source edits."""
from pathlib import Path
import copy
import hashlib
import json
import math
import numpy as np
from scipy.optimize import least_squares

ROOT=Path(__file__).resolve().parents[1]
def module(name):
    p=ROOT/name;ns={'__file__':str(p),'__name__':'third_view_helpers'}
    exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),ns);return ns
fit=module('validation/fit_wave_geometry.py')
builder=module('blender/build_wave_corridor.py')
report=json.loads((ROOT/'validation/wave-joint-flat-candidate.json').read_text(encoding='utf-8'))
cfg=report['plan']['constructor'];points=fit['geometry'](cfg,builder)
for i,y in enumerate(cfg['ceiling_lights']['hall_centres_y_m']):
    points['hall_lamp_'+str(i)]=[0,y,cfg['corridor']['ceiling_z_m']-.0525]
observed={}
fixed_eye=cfg['camera_seed']['position_m'][2]
def camera(v):
    return {'position_m':list(map(float,v[:3])),'yaw_rad':float(v[3]),'pitch_rad':float(v[4]),
            'roll_rad':float(v[5]),'tan_half_vertical_fov':cfg['camera_seed']['tan_half_vertical_fov'],
            'render_px':[478,850]}
def residual(v,prior=True):
    pp=fit['projected'](points,camera(v));out=[]
    for name,(xy,uncertainty) in observed.items():
        if name not in pp:return np.ones(2*len(observed)+(6 if prior else 0))*1e4
        out.extend((np.array(pp[name])-xy)/uncertainty)
    if prior:out.extend(.03*(v-np.array([0,2.5,1.2,1.57,-.4,0]))/np.array([.3,1.,.3,.1,.1,.05]))
    return np.array(out)

trials=[]
hypotheses=[['next_lamp_center','far_lamp_center','hall_lamp_0'],
            ['far_lamp_center','hall_lamp_0','hall_lamp_1']]
for lamps in hypotheses:
    observed=dict(zip(lamps,[([245,111],7),([244,151],7),([243,175],7)]))
    observed.update(aperture_top_left=([148,189],9),aperture_top_right=([334,182],12))
    for y0,y1,z in builder['floor_profile'](cfg)[1]:
        lo=max(y0+1e-5,cfg['secondary_camera_seed']['position_m'][1]+.1)
        hi=min(y1-1e-5,points[lamps[0]][1]-.2,cfg['corridor']['end_y_m']-1)
        if hi-lo<1e-4:continue
        def expand(v):return np.r_[v[:2],z+fixed_eye,v[2:]]
        lower=np.array([-.65,lo,1.3,-.7,-.15]);upper=np.array([.65,hi,1.9,-.12,.15])
        start=np.clip([0,(lo+hi)/2,1.57,-.4,0],lower+1e-7,upper-1e-7)
        result=least_squares(lambda v:residual(expand(v)),start,bounds=(lower,upper),max_nfev=2000)
        pose=expand(result.x)
        trials.append({'camera':camera(pose),'support_z_m':z,'lamp_correspondence':lamps,
                       'observed':copy.deepcopy(observed),'weighted_rms':float(np.sqrt(np.mean(residual(pose,False)**2)))})
best=min(trials,key=lambda row:row['weighted_rms']);observed=best['observed']
pp=fit['projected'](points,best['camera'])
rows=[{'id':name,'source_px':xy,'uncertainty_px':uncertainty,'projected_px':pp[name],
       'distance_px':float(np.linalg.norm(np.array(pp[name])-xy))} for name,(xy,uncertainty) in observed.items()]
# Independent visual observations: uncertain correspondence, excluded from fit.
x=cfg['corridor']['half_width_m']-cfg['rails']['offset_from_wall_m']
y=cfg['corridor']['end_y_m']-.1;z=builder['rail_height'](y,cfg)
heldout=fit['projected']({'left':[-x,y,z],'right':[x,y,z]},best['camera'])
checks=[{'side':side,'projected_rail_end_px':heldout[side],'source_possible_rail_end_px':xy,
         'distance_px':float(np.linalg.norm(np.array(heldout[side])-xy)),
         'use':'excluded diagnostic: upright handrail may differ from low edge-trim termination'}
        for side,xy in [('left',[148,329]),('right',[322,335])]]
output={'schema':'dream.wave_third_view.v1','accepted':False,'geometry_modified':False,'time_s':17,
        'hypothesis':'Two lamp correspondence hypotheses compared; best retained without changing geometry.',
        'fixed_eye_height_m':fixed_eye,'best':best,'trials':trials,'landmarks':rows,'held_out':checks,
        'limitations':['Only the camera is fitted; the full original video trajectory is not recovered.',
                       'Lamp correspondence and the hall aperture corners remain manually assigned and approximate.',
                       'The possible rail endpoints are not fit inputs; their mismatches must not be hidden.'],
        'geometry_source_sha256':hashlib.sha256((ROOT/'validation/wave-joint-flat-candidate.json').read_bytes()).hexdigest()}
(ROOT/'validation/wave-joint-third-view.json').write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'best':best,'landmarks':rows,'held_out':checks}))
