"""Compare aligned and staggered wall ends using continuously tracked corners."""
from pathlib import Path
import copy
import json
import numpy as np
from scipy.optimize import least_squares

ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
ns={'__file__':str(ROOT/'validation/fit_wave_geometry.py'),'__name__':'aperture_fit_helpers'}
exec(compile(Path(ns['__file__']).read_text(encoding='utf-8'),ns['__file__'],'exec'),ns)
project=ns['projected'];old=read('validation/wave-terminal/geometry-candidate.json');cfg=old['plan']['constructor']
tracks=read('validation/wave-aperture/tracks.json')['tracks'];cams=cfg['all_source_cameras']
fit_times=[14,15.5,17];heldout=[14.5,15,16,16.5]
observed=[];spread=[]
for c in cams:
    row=[];uncertainty=[]
    for name in ['left_wall_corner','right_wall_corner']:
        variants=[min(r['samples'],key=lambda s:abs(s[0]-c['time_s']))[1:] for r in tracks if r['id']==name and r['complete']]
        row.append(np.median(variants,axis=0));uncertainty.append(float(np.max(np.linalg.norm(np.array(variants)-row[-1],axis=1))))
    observed.append(row);spread.append(uncertainty)
observed=np.array(observed)
def residual(v,staggered,training_only=True):
    yl,yr,z=v if staggered else [v[0],v[0],v[1]]
    pts={'left':[-1.1,yl,z],'right':[1.1,yr,z]};out=[]
    for c,obs in zip(cams,observed):
        if training_only and c['time_s'] not in fit_times:continue
        pp=project(pts,c)
        for side,xy in zip(['left','right'],obs):out.extend(np.array(pp[side])-xy)
    return np.array(out)
results={}
for staggered in [False,True]:
    start=[cfg['corridor']['wall_end_y_m']]* (2 if staggered else 1)+[cfg['corridor']['ceiling_z_m']]
    lo=[6.]*(2 if staggered else 1)+[1.8];hi=[12.]*(2 if staggered else 1)+[3.0]
    fit=least_squares(lambda v:residual(v,staggered),start,bounds=(lo,hi),loss='soft_l1',f_scale=4)
    yl,yr,z=fit.x if staggered else [fit.x[0],fit.x[0],fit.x[1]]
    distances=np.linalg.norm(residual(fit.x,staggered,False).reshape((-1,2,2)),axis=2)
    results['staggered' if staggered else 'aligned']={'left_end_y_m':float(yl),'right_end_y_m':float(yr),'ceiling_z_m':float(z),
        'training_point_rms_px':float(np.sqrt(np.mean(distances[[c['time_s'] in fit_times for c in cams]]**2))),
        'heldout_point_rms_px':float(np.sqrt(np.mean(distances[[c['time_s'] in heldout for c in cams]]**2))),
        'per_view':[{'time_s':c['time_s'],'left_error_px':float(d[0]),'right_error_px':float(d[1])} for c,d in zip(cams,distances)]}
best=results['staggered'];plan=copy.deepcopy(old['plan']);c=plan['constructor']
c['corridor'].update(left_wall_end_y_m=best['left_end_y_m'],right_wall_end_y_m=best['right_end_y_m'],
    wall_end_y_m=min(best['left_end_y_m'],best['right_end_y_m']),ceiling_z_m=best['ceiling_z_m'])
c['destination_hall']['ceiling_z_m']=best['ceiling_z_m']
c['ceiling_lights']['mount_drop_m']+=best['ceiling_z_m']-cfg['corridor']['ceiling_z_m']
c['rails']['end_y_by_side_m']={'-1':best['left_end_y_m']-.05,'1':best['right_end_y_m']-.05}
c['ownership_token']='-DREAM-waveaperture-'
plan.update(scene_name='DREAM_WaveApertureCandidate',asset_id='wave_aperture_candidate',collection_name='DREAM_WaveApertureCandidate',
            stage='staggered_entrance_gray_candidate_unaccepted')
report={'schema':'dream.wave_aperture_fit.v1','accepted':False,'runtime_promoted':False,
        'hypotheses':results,'training_times_s':fit_times,'heldout_times_s':heldout,
        'observations':[{'time_s':c['time_s'],'left_px':list(xy[0]),'right_px':list(xy[1]),'window_spread_px':spr}
                        for c,xy,spr in zip(cams,observed,spread)],'plan':plan,
        'limitations':['Tracked corners are manually seeded; source glow and occlusion still limit subpixel claims.',
                       'Held-out corner samples did not enter this wall-end fit, but their camera poses were estimated earlier from other source tracks.',
                       'Automatic color-mask corners are rejected: floor reflections and the fixed half-image split contaminate their estimates.',
                       'Former aperture labels marked different source details; old error figures cannot be compared directly to this corrected landmark set.']}
(ROOT/'validation/wave-aperture/fit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(results))
