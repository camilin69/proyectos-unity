"""Reconstruct terminal rail observations against the existing seven cameras."""
from pathlib import Path
import json
import numpy as np
from scipy.optimize import least_squares

ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
ns={'__file__':str(ROOT/'validation/fit_wave_geometry.py'),'__name__':'terminal_projection'}
exec(compile(Path(ns['__file__']).read_text(encoding='utf-8'),ns['__file__'],'exec'),ns)
project=ns['projected']
motion=read('validation/wave-motion/geometry-candidate.json')
cfg=motion['plan']['constructor'];cams=cfg['all_source_cameras']
tracks=read('validation/wave-terminal/rail-tracks.json')['tracks']
observed=np.array([[min(r['samples'],key=lambda s:abs(s[0]-c['time_s']))[1:] for r in tracks] for c in cams])
def error(points):
    out=[]
    for c,obs in zip(cams,observed):
        pp=project(dict(enumerate(points)),c)
        for i,xy in enumerate(obs):out.extend(np.array(pp.get(i,[1e5,1e5]))-xy)
    return np.array(out)
initial=np.array([[-1,9.,.2],[-1,10.,-.1],[-1,9.,-.8],[-1,10.,-1.1],
                  [1,9.,.2],[1,10.,-.1],[1,9.,-.8],[1,10.,-1.1]])
free=least_squares(lambda v:error(v.reshape((-1,3))),initial.ravel(),max_nfev=1000,loss='soft_l1',f_scale=3)
freepts=free.x.reshape((-1,3));free_err=error(freepts).reshape((7,8,2))
# Shared Y/Z cross-sections and separate X positions produce two physical
# matching frames rather than an arbitrary eight-point skew polyhedron.
def points(v):
    xl,xr,yn,length,zn,height,drop=v; yf=yn+length;zf=zn-drop
    return np.array([[x,y,z] for x in [xl,xr] for y,z in [(yn,zn+height),(yf,zf+height),(yn,zn),(yf,zf)]])
def residual(v):
    return np.r_[error(points(v)),.3*(v-np.array([-1,1,9,1,-.8,.9,.3]))/np.array([.2,.2,2.,.5,.5,.25,.2])]
fit=least_squares(residual,[-1,1,9,1,-.8,.9,.3],bounds=([-1.3,.6,5,.3,-2.,.5,-.1],[-.6,1.3,16,3,1.5,1.6,.8]),
                  loss='soft_l1',f_scale=3,max_nfev=1000)
pts=points(fit.x);errors=error(pts).reshape((7,8,2))
rows=[{'id':r['id'],'free_xyz_m':freepts[i].tolist(),'constrained_xyz_m':pts[i].tolist(),
       'free_max_point_error_px':float(np.max(np.linalg.norm(free_err[:,i],axis=1))),
       'constrained_max_point_error_px':float(np.max(np.linalg.norm(errors[:,i],axis=1)))} for i,r in enumerate(tracks)]
report={'schema':'dream.wave_terminal_fit.v1','accepted':False,'points':rows,
        'parameters':dict(zip(['left_x','right_x','near_y','length','near_floor_z','height','descent'],map(float,fit.x))),
        'point_distance_rms_px':float(np.sqrt(np.mean(np.sum(errors**2,axis=2)))),
        'free_point_distance_rms_px':float(np.sqrt(np.mean(np.sum(free_err**2,axis=2)))),
        'limitations':['Camera reconstruction and tracked metal edges remain uncertain; fitted coordinates are not surveyed dimensions.',
                       'Occluded foot positions may lie on trim instead of the walkable floor.',
                       'The constrained pair must be checked against the actual stair mesh before building.']}
(ROOT/'validation/wave-terminal/fit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report))
