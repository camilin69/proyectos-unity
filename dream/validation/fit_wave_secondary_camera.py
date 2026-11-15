"""Register the 15.5 s inspection camera with v2 geometry and FOV fixed.

Only --apply edits secondary_camera_seed and validation metadata in the plan.
No bpy. The output is an imperfect diagnostic pose, not a geometry pass.
"""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares

ROOT=Path(__file__).resolve().parents[1]
PLAN=ROOT/'blender/wave_corridor_plan.json'
REPORT=ROOT/'validation/wave-secondary-camera-fit.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable_hash(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def pure_module(path):
    namespace={'__name__':'wave_offline_helper','__file__':str(path)}
    exec(compile(path.read_text(encoding='utf8'),str(path),'exec'),namespace)
    return namespace


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--apply',action='store_true');args=parser.parse_args()
    plan=json.loads(PLAN.read_text(encoding='utf8'));cfg=copy.deepcopy(plan['constructor'])
    primary=pure_module(ROOT/'validation/fit_wave_geometry.py')
    builder=pure_module(ROOT/'blender/build_wave_corridor.py')
    points=primary['geometry'](cfg,builder);door=builder['door_openings'](cfg)[1]
    fw=cfg['doors']['frame_width_m']/2;x=-cfg['corridor']['half_width_m']+2*cfg['doors']['frame_projection_m']
    for side,y in [('near',door['y0_m']-fw),('far',door['y1_m']+fw)]:
        points[side+'_jamb_direction_point']=[x,y,0]
    anchors={
        'second_door_outer_top_near':dict(pixel_xy=[111,145],uncertainty_px=6),
        'second_door_outer_top_far':dict(pixel_xy=[200,195],uncertainty_px=7),
        'aperture_top_left':dict(pixel_xy=[269,240],uncertainty_px=9),
        'nearest_full_lamp_center':dict(pixel_xy=[358,54],uncertainty_px=7),
        'next_lamp_center':dict(pixel_xy=[350,160],uncertainty_px=6),
        'far_lamp_center':dict(pixel_xy=[345,215],uncertainty_px=7),
    }
    jambs={
        'near':dict(pixel_xy=[122,325],uncertainty_px=8),
        'far':dict(pixel_xy=[206,325],uncertainty_px=6),
    }
    # The interior right edge is not sufficiently isolated from ceiling/wall
    # occlusion; do not force it to match the same aperture plane.
    excluded={'aperture_top_right':dict(pixel_xy=[419,241],uncertainty_px=16,
        reason='Right hall edge is partly occluded/ambiguous; observation only.'),
        'second_door_bottom_far':dict(pixel_xy=[212,495],uncertainty_px=18,
        reason='Dark edge masks the lower jamb; not a measured threshold.')}
    fov=cfg['camera_seed']['tan_half_vertical_fov'];size=cfg['camera_seed']['render_px']
    initial=np.array([0.,1.4,1.25,1.75,-.23,0.])
    lower=np.array([-.82,-.1,.65,1.3,-.6,-.15]);upper=np.array([.82,3.5,1.85,2.05,.03,.15])
    scales=np.array([.4,1.3,.4,.2,.2,.07])
    def camera(v):
        return dict(position_m=list(map(float,v[:3])),yaw_rad=float(v[3]),pitch_rad=float(v[4]),
            roll_rad=float(v[5]),tan_half_vertical_fov=fov,render_px=size)
    def residual(v,regularize=True):
        pp=primary['projected'](points,camera(v));out=[]
        for key,a in anchors.items():
            if key not in pp:return np.ones(20 if regularize else 14)*1e4
            out.extend((np.asarray(pp[key])-a['pixel_xy'])/a['uncertainty_px'])
        for side,a in jambs.items():
            top=np.asarray(pp['second_door_outer_top_'+side]);bottom=np.asarray(pp[side+'_jamb_direction_point'])
            d=bottom-top;q=np.asarray(a['pixel_xy'])-top
            out.append((d[0]*q[1]-d[1]*q[0])/np.linalg.norm(d)/a['uncertainty_px'])
        if regularize:out.extend(.08*(v-initial)/scales)
        return np.asarray(out)
    fit=least_squares(residual,initial,bounds=(lower,upper),max_nfev=2500,ftol=1e-12,xtol=1e-12,gtol=1e-12)
    pose=fit.x;cam=camera(pose);pp=primary['projected'](points,cam)
    rows=[]
    for key,a in anchors.items():
        delta=np.asarray(pp[key])-a['pixel_xy'];rows.append(dict(id=key,**a,projected_px=pp[key],
            delta_px=delta.tolist(),distance_px=float(np.linalg.norm(delta)),use='fit'))
    for key,a in excluded.items():
        rows.append(dict(id=key,**a,projected_px=pp[key],use='excluded'))
    line_rows=[]
    for side,a in jambs.items():
        top=np.asarray(pp['second_door_outer_top_'+side]);bottom=np.asarray(pp[side+'_jamb_direction_point'])
        d=bottom-top;q=np.asarray(a['pixel_xy'])-top
        line_rows.append(dict(side=side,**a,perpendicular_error_px=float((d[0]*q[1]-d[1]*q[0])/np.linalg.norm(d)),
            note='Point-to-line constraint on a visible jamb segment; its height is not assigned to a 3D sill.'))

    # A diagnostic comparison only: hold primary eye-height above each exact
    # flat support interval, fitting the other five camera parameters. Separate
    # fits avoid optimizing across discontinuous stair-height evaluations.
    primary_cam=cfg['camera_seed'];primary_eye=primary_cam['position_m'][2]-builder['floor_height'](primary_cam['position_m'][1],cfg)
    trials=[]
    _,spans=builder['floor_profile'](cfg)
    for y0,y1,z in spans:
        y0,y1=max(-.1,y0+1e-6),min(3.5,y1-1e-6)
        if y1-y0<1e-5:continue
        low=lower[[0,1,3,4,5]].copy();high=upper[[0,1,3,4,5]].copy();low[1],high[1]=y0,y1
        start=np.clip(pose[[0,1,3,4,5]],low+1e-8,high-1e-8)
        def expand(v):return np.array([v[0],v[1],primary_eye+z,v[2],v[3],v[4]])
        result=least_squares(lambda v:residual(expand(v)),start,bounds=(low,high),max_nfev=1500)
        trial=expand(result.x);errors=residual(trial,False)
        trials.append(dict(camera=camera(trial),support_z_m=z,weighted_rms=float(np.sqrt(np.mean(errors**2)))))
    constant_eye=min(trials,key=lambda a:a['weighted_rms'])
    support=builder['floor_height'](pose[1],cfg);eye=float(pose[2]-support)
    geometry_hash_input=copy.deepcopy(cfg);geometry_hash_input.pop('secondary_camera_seed',None)
    report=dict(schema_version=1,status='secondary_pose_applied_pending_real_render' if args.apply else 'secondary_pose_candidate_not_applied',
        accepted=False,source='dream/validation/wave-reference-15p5s.png',source_sha256=sha(ROOT/'validation/wave-reference-15p5s.png'),
        time_s=15.5,camera=cam,fixed_geometry_and_primary_camera_hash=stable_hash(geometry_hash_input),
        fov_fixed_to_primary=True,geometry_modified=False,landmarks=rows,visible_jamb_checks=line_rows,
        weighted_rms=float(np.sqrt(np.mean(residual(pose,False)**2))),solver_success=bool(fit.success),
        eye_height_diagnostic=dict(primary_eye_height_m=primary_eye,candidate_floor_z_m=support,candidate_eye_height_m=eye,
            difference_m=eye-primary_eye,constant_eye_height_fit=constant_eye,
            interpretation='A lower fitted eye height may indicate a too-shallow first flight, handheld camera motion, or remaining shape/intrinsic mismatch. It does not recover physical step heights.'),
        primary_render_review=dict(path='dream/validation/wave-gray-v2.png',sha256=sha(ROOT/'validation/wave-gray-v2.png'),
            root_reported_objects=56,observed_improvements=['Both left doors now occupy the correct depth order and rough upper silhouettes.','The spurious near ceiling fixtures are gone; the first full lamp is near the measured height.','Gray surfaces no longer clip strongly, making the step/trim geometry inspectable.'],
            remaining=['The far hall still reads as a shallow gridded recess rather than the more open source.','The first flight is very shallow; its five ~3 cm risers remain unvalidated.','Dark edge shape/height and door-bottom occlusion remain approximate.','Door lower proportions and lamp apparent sizes need real multi-view review.']),
        limitations=['Six camera degrees of freedom only; v2 scene dimensions, door openings, floor, trim and FOV were held fixed.',
            'Manual source pixels have stated uncertainty; diffuser glow and reveal thickness make exact corners/centroids ambiguous.',
            'Aperture right edge and lower door are excluded from pose constraints.',
            'Visible jamb directions are included without assigning a hidden floor/sill height.',
            'Residuals are not a fidelity percentage and do not constitute a geometry pass.',
            'No new Blender render or scene mutation occurred in this script.'],
        script_sha256=sha(Path(__file__)))
    if args.apply:
        cam.update(status='Approximate fixed-geometry/FOV 15.5 s pose; residuals reported, not accepted.',reference_time_s=15.5)
        plan['constructor']['secondary_camera_seed']=cam
        protected=copy.deepcopy(plan['constructor']);protected.pop('secondary_camera_seed',None)
        assert stable_hash(protected)==report['fixed_geometry_and_primary_camera_hash']
        plan['stage']='gray_v2_primary_rendered_secondary_pose_pending_render'
        plan['geometry_fit']['secondary']=dict(report='dream/validation/wave-secondary-camera-fit.json',status=report['status'],accepted=False)
        plan['validation']['geometry_gate']='Primary v2 gray reviewed; fixed-geometry secondary camera pending real render and comparison. Geometry remains unaccepted.'
        PLAN.write_text(json.dumps(plan,indent=2)+'\n',encoding='utf8')
    report['projection_proof']=proof(cam,cfg,builder,primary,rows,line_rows)
    report['plan_sha256_after']=sha(PLAN)
    REPORT.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(camera=cam,weighted_rms=report['weighted_rms'],eye_height_diagnostic=report['eye_height_diagnostic'],
        landmarks=rows,visible_jamb_checks=line_rows),indent=2))


def proof(cam,cfg,builder,primary,rows,line_rows):
    from PIL import Image,ImageDraw,ImageFont
    ref=Image.open(ROOT/'validation/wave-reference-15p5s.png').convert('RGB');overlay=ref.copy();draw=ImageDraw.Draw(overlay)
    def line(points,colour):
        pp=primary['projected']({str(i):p for i,p in enumerate(points)},cam)
        for i in range(len(points)-1):
            if str(i) in pp and str(i+1) in pp:draw.line([tuple(pp[str(i)]),tuple(pp[str(i+1)])],fill=colour,width=2)
    c=cfg['corridor'];d=cfg['doors'];fw=d['frame_width_m']/2
    for opening in builder['door_openings'](cfg):
        x=-c['half_width_m']+2*d['frame_projection_m'];y0=opening['y0_m']-fw;y1=opening['y1_m']+fw
        top=opening['head_z_m']+fw;bottom=opening['threshold_z_m']
        line([(x,y0,bottom),(x,y0,top),(x,y1,top),(x,y1,bottom)],(255,205,55))
    for side in (-1,1):line(builder['rail_path'](side,cfg),(255,65,180))
    line([(-c['half_width_m'],c['end_y_m'],c['ceiling_z_m']),(c['half_width_m'],c['end_y_m'],c['ceiling_z_m'])],(60,225,255))
    for row in rows:
        if row['use']!='fit':continue
        x,y=row['pixel_xy'];draw.ellipse((x-4,y-4,x+4,y+4),outline=(50,255,80),width=1)
        x,y=row['projected_px'];draw.line((x-4,y,x+4,y),fill=(255,215,55));draw.line((x,y-4,x,y+4),fill=(255,215,55))
    for row in line_rows:
        x,y=row['pixel_xy'];draw.rectangle((x-3,y-3,x+3,y+3),outline=(50,255,80))
    canvas=Image.new('RGB',(956,915),(23,25,29));out=ImageDraw.Draw(canvas)
    try:font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
    except OSError:font=ImageFont.load_default()
    canvas.paste(ref,(0,35));canvas.paste(overlay,(478,35))
    out.text((8,8),'REFERENCE 15.5 s',font=font,fill='white');out.text((486,8),'FIXED-GEOMETRY CAMERA - OFFLINE WIRES',font=font,fill='white')
    out.text((8,887),'Not a render or visibility test. Geometry/FOV fixed. Remaining residuals are intentional evidence.',font=font,fill='white')
    path=ROOT/'validation/wave-secondary-projection.png';canvas.save(path)
    return str(path.relative_to(ROOT.parent)).replace('\\','/')


if __name__=='__main__':
    main()
