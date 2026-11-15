"""Offline single-frame gray proposal, not recovered physical architecture.

Use --apply to update the plan. No bpy, scene mutation, render or export.
The initial constructor remains in the report for repeatable comparisons.
"""
import argparse
import ast
import copy
import hashlib
import json
import math
from collections import Counter
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT/'blender/wave_corridor_plan.json'
REPORT = ROOT/'validation/wave-geometry-fit-candidate.json'
BUILDER = ROOT/'blender/build_wave_corridor.py'
NAMES = ['cx','cz','yaw','pitch','roll','tan','ceiling','end',
         'door_first_y','door_y','door_w','door_h','door_z','near_drop','near_end',
         'mid_start','mid_len','mid_drop','rail_h','lamp_a','lamp_b','lamp_c']
INITIAL = np.array([-.02,1.55,1.565,-.305,0,.72,2.5,10.8,
                    2.5,4.6,.92,2.16,-.4,.3,2.,4.1,1.12,.4,.25,4.9,7.2,9.5])
LOWER = [-.35,1.25,1.42,-.60,-.07,.58,2.2,8.7,1.,3.2,.8,1.95,-.85,.1,1.4,2.8,.85,.2,.08,3.,5.,7.5]
UPPER = [.35,1.8,1.73,-.18,.07,1.05,3.1,13.,3.5,6.3,1.35,2.4,.05,.65,2.8,5.5,2.4,.72,.5,6.,9.,12.8]
SCALES = np.array([.15,.2,.07,.15,.035,.2,.4,2.5,.8,1.2,.22,.16,.25,.25,.5,1.2,.5,.2,.2,1.5,2.,3.])


def unpack(v):
    return dict(zip(NAMES,map(float,v)))


def projected(points,camera):
    yaw,pitch,roll = (camera[k] for k in ('yaw_rad','pitch_rad','roll_rad'))
    f=np.array([math.cos(yaw)*math.cos(pitch),math.sin(yaw)*math.cos(pitch),math.sin(pitch)])
    r=np.cross(f,[0,0,1]);r/=np.linalg.norm(r);u=np.cross(r,f)
    rr,uu=r*math.cos(roll)+u*math.sin(roll),u*math.cos(roll)-r*math.sin(roll)
    w,h=camera['render_px'];focal=h/(2*camera['tan_half_vertical_fov']);result={}
    for key,point in points.items():
        d=np.asarray(point)-camera['position_m'];depth=float(d@f)
        if depth<=.01:continue  # historical first door was behind the camera
        result[key]=[w/2+float(d@rr)/depth*focal,h/2-float(d@uu)/depth*focal]
    return result


def candidate_config(v,seed):
    p,cfg=unpack(v),copy.deepcopy(seed)
    cfg['camera_seed'].update(position_m=[p['cx'],-.3,p['cz']],yaw_rad=p['yaw'],pitch_rad=p['pitch'],
        roll_rad=p['roll'],tan_half_vertical_fov=p['tan'],status='Offline candidate; pending real gray render and secondary view.')
    c,d,fs=cfg['corridor'],cfg['doors'],cfg['floor']['flights']
    c.update(end_y_m=p['end'],ceiling_z_m=p['ceiling'])
    fs[0].update(riser_m=p['near_drop']/fs[0]['riser_count'],tread_m=(p['near_end']-fs[0]['start_y_m'])/fs[0]['riser_count'])
    fs[1].update(start_y_m=p['mid_start'],riser_m=p['mid_drop']/fs[1]['riser_count'],tread_m=p['mid_len']/fs[1]['riser_count'])
    drop=sum(f['riser_count']*f['riser_m'] for f in fs)
    c['solid_bottom_z_m']=min(seed['corridor']['solid_bottom_z_m'],-drop-.26)
    d.update(centres_y_m=[p['door_first_y'],p['door_y']],width_m=p['door_w'],height_m=p['door_h'],thresholds_z_m=[p['door_z']]*2)
    d['note']='Explicit inferred thresholds: the lower jamb is occluded. Do not infer a flat corridor platform or measured sill. Door openings may face a descending section.'
    cfg['rails'].update(height_above_floor_m=p['rail_h'],wall_brackets=False)
    cfg['rails']['note']='Two continuous dark edge trims; provisionally low guard/skirting, not a confirmed 0.83 m handrail. Height and section remain unresolved.'
    cfg['ceiling_lights']['centres_y_m']=[p['lamp_a'],p['lamp_b'],p['lamp_c']]
    cfg['ceiling_lights']['hall_centres_y_m']=[max(p['end']+.7,12.4),15.1]
    cfg['destination_hall']['ceiling_z_m']=p['ceiling']
    cfg['floor']['fit_note']='Three straight flights and provisional 5/4/3 counts retained. Rises/lengths are regularized variables, not recovered dimensions.'
    return cfg


def geometry(cfg,pure):
    c,d,fs=cfg['corridor'],cfg['doors'],cfg['floor']['flights']
    w,fw=c['half_width_m'],d['frame_width_m'];front_x=-w+2*d['frame_projection_m']
    dy,dw=d['centres_y_m'][1],d['width_m']
    threshold=d.get('thresholds_z_m',[pure['floor_height'](y,cfg) for y in d['centres_y_m']])
    head=threshold[1]+d['height_m']+d['leaf_base_clearance_m']+fw/2
    first_head=threshold[0]+d['height_m']+d['leaf_base_clearance_m']+fw/2
    xrail=w-cfg['rails']['offset_from_wall_m']
    mid=fs[1]['start_y_m'];end=mid+fs[1]['riser_count']*fs[1]['tread_m']
    near_end=fs[0]['start_y_m']+fs[0]['riser_count']*fs[0]['tread_m']
    pts={
        'aperture_top_left':[-w,c['end_y_m'],c['ceiling_z_m']],
        'aperture_top_right':[w,c['end_y_m'],c['ceiling_z_m']],
        'aperture_floor_left':[-w,c['end_y_m'],pure['floor_height'](c['end_y_m'],cfg)],
        'aperture_floor_right':[w,c['end_y_m'],pure['floor_height'](c['end_y_m'],cfg)],
        'first_door_outer_top_far':[front_x,d['centres_y_m'][0]+dw/2+fw/2,first_head],
        'second_door_outer_top_near':[front_x,dy-dw/2-fw/2,head],
        'second_door_outer_top_far':[front_x,dy+dw/2+fw/2,head],
        'second_door_bottom_far':[front_x,dy+dw/2,threshold[1]],
        'near_flight_end_right':[xrail,near_end,pure['rail_height'](near_end,cfg)],
    }
    for side,name in [(-1,'left'),(1,'right')]:
        pts['first_near_rail_corner_'+name]=[side*xrail,mid,pure['rail_height'](mid,cfg)]
        pts['middle_trim_end_'+name]=[side*xrail,end,pure['rail_height'](end,cfg)]
    for y,name in zip(cfg['ceiling_lights']['centres_y_m'],['nearest_full_lamp_center','next_lamp_center','far_lamp_center']):
        pts[name]=[0,y,c['ceiling_z_m']-cfg['ceiling_lights']['body_depth_m']/2]
    return pts


def mesh_check(data):
    v=np.asarray(data['vertices']);edges,oriented=Counter(),Counter();volume=0.;minimum=math.inf
    for face,uv in zip(data['faces'],data['uv_faces']):
        assert len(face)==len(uv) and np.isfinite(uv).all()
        for a,b in zip(face,face[1:]+face[:1]):edges[tuple(sorted((a,b)))]+=1;oriented[(a,b)]+=1
        for i in range(1,len(face)-1):
            a,b,c=v[[face[0],face[i],face[i+1]]];area=np.linalg.norm(np.cross(b-a,c-a))/2
            minimum=min(minimum,float(area));volume+=float(a@np.cross(b,c))/6
    assert np.isfinite(v).all() and min(edges.values())==max(edges.values())==2
    assert all(n==oriented[(b,a)] for (a,b),n in oriented.items()) and volume>0 and minimum>1e-12
    return dict(vertices=len(v),faces=len(data['faces']),triangles=sum(len(f)-2 for f in data['faces']),closed=True,
        opposite_edge_winding=True,euler_characteristic=len(v)-len(edges)+len(data['faces']),signed_volume_m3=volume,
        min_triangle_area_m2=minimum,finite_complete_uv=True)


def projection_proof(cfg, pure, rows):
    """Sparse geometric overlay, explicitly not a visibility-tested render."""
    from PIL import Image, ImageDraw, ImageFont
    reference=Image.open(ROOT/'validation/wave-reference-14s.png').convert('RGB')
    initial=Image.open(ROOT/'validation/wave-gray-initial.png').convert('RGB')
    overlay=reference.copy();draw=ImageDraw.Draw(overlay)
    camera=cfg['camera_seed']
    def line(points,colour,width=2):
        pp=projected({str(i):p for i,p in enumerate(points)},camera)
        for i in range(len(points)-1):
            if str(i) in pp and str(i+1) in pp:
                draw.line([tuple(pp[str(i)]),tuple(pp[str(i+1)])],fill=colour,width=width)
    for opening in pure['door_openings'](cfg):
        x=-cfg['corridor']['half_width_m']+2*cfg['doors']['frame_projection_m']
        fw=cfg['doors']['frame_width_m']/2
        y0,y1,z0,z1=opening['y0_m']-fw,opening['y1_m']+fw,opening['threshold_z_m'],opening['head_z_m']+fw
        line([(x,y0,z0),(x,y0,z1),(x,y1,z1),(x,y1,z0)],(255,205,50))
        # No solid sill line: its source position is excluded, not measured.
    for side in (-1,1):line(pure['rail_path'](side,cfg),(255,70,180))
    c=cfg['corridor'];line([(-c['half_width_m'],c['end_y_m'],c['ceiling_z_m']),
        (c['half_width_m'],c['end_y_m'],c['ceiling_z_m'])],(70,225,255))
    for row in rows:
        if row['use']!='fit':continue
        x,y=row['reference_px'];draw.ellipse((x-3,y-3,x+3,y+3),outline=(70,255,110),width=1)
        x,y=row['candidate_px'];draw.line((x-4,y,x+4,y),fill=(255,225,70));draw.line((x,y-4,x,y+4),fill=(255,225,70))
    canvas=Image.new('RGB',(478*3,910),(23,25,29));out=ImageDraw.Draw(canvas)
    try:font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',19)
    except OSError:font=ImageFont.load_default()
    for i,(img,title) in enumerate([(reference,'REFERENCE 14 s'),(initial,'INITIAL GRAY - ACTUAL RENDER'),(overlay,'V2 OFFLINE WIRES - NOT A RENDER')]):
        canvas.paste(img,(i*478,36));out.text((i*478+9,8),title,font=font,fill='white')
    out.text((9,887),'Green: measured anchors. Yellow: candidate door/points. Pink: uncertain low trim. No occlusion solve.',font=font,fill='white')
    path=ROOT/'validation/wave-geometry-v2-projection.png';canvas.save(path)
    return str(path.relative_to(ROOT.parent)).replace('\\','/')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--apply',action='store_true');args=parser.parse_args()
    plan=json.loads(PLAN.read_text(encoding='utf8'))
    previous=json.loads(REPORT.read_text(encoding='utf8')) if REPORT.exists() else {}
    seed=previous.get('seed_constructor',copy.deepcopy(plan['constructor']))
    pure={'__file__':str(BUILDER),'__name__':'wave_geometry_helpers'}
    code=BUILDER.read_text(encoding='utf8');ast.parse(code);exec(compile(code,str(BUILDER),'exec'),pure)
    anchors={a['id']:copy.deepcopy(a) for a in plan['landmarks_primary_14s']}
    anchors.update({
        'first_door_outer_top_far':dict(pixel_xy=[45,143],uncertainty_px=9),
        'middle_trim_end_left':dict(pixel_xy=[146,417],uncertainty_px=10),
        'middle_trim_end_right':dict(pixel_xy=[309,416],uncertainty_px=10),
        'near_flight_end_right':dict(pixel_xy=[445,533],uncertainty_px=15)})
    excluded={'second_door_bottom_far':'Dark edge occludes leaf/jamb: 146,410 is not a measured sill.',
        'aperture_floor_left':'Apparent boundary may be far stair/trim bend rather than hall floor seam.',
        'aperture_floor_right':'Apparent boundary may be far stair/trim bend rather than hall floor seam.'}
    active={k:a for k,a in anchors.items() if k not in excluded}
    def residual(v,regularize=True):
        cfg=candidate_config(v,seed);pp=projected(geometry(cfg,pure),cfg['camera_seed']);out=[]
        for k,a in active.items():out.extend((np.array(pp[k])-a['pixel_xy'])/a['uncertainty_px'])
        if regularize:
            out.extend(.55*(v-INITIAL)/SCALES);p=unpack(v)
            out.extend([8*max(0,p['near_end']+.18-p['mid_start']),
                8*max(0,p['mid_start']+p['mid_len']+.18-seed['floor']['flights'][2]['start_y_m']),
                8*max(0,p['door_first_y']+p['door_w']+.15-p['door_y'])])
        return np.asarray(out)
    fit=least_squares(residual,INITIAL,bounds=(LOWER,UPPER),max_nfev=4000,ftol=1e-11,xtol=1e-11,gtol=1e-11)
    cfg=candidate_config(fit.x,seed);after=projected(geometry(cfg,pure),cfg['camera_seed'])
    pure['door_openings'](cfg)  # same pre-mutation validation as the builder
    seed_cfg=copy.deepcopy(seed);seed_cfg['ceiling_lights']['centres_y_m']=[4.9,7.2,9.5]
    before=projected(geometry(seed_cfg,pure),seed['camera_seed'])
    rows=[dict(id=k,reference_px=a['pixel_xy'],uncertainty_px=a['uncertainty_px'],use='excluded' if k in excluded else 'fit',
        exclusion_reason=excluded.get(k),seed_px=before.get(k),candidate_px=after[k],
        candidate_error_px=float(np.linalg.norm(np.array(after[k])-a['pixel_xy']))) for k,a in anchors.items()]
    mesh={'floor':mesh_check(pure['floor_geometry'](cfg)),
        'trims':[mesh_check(pure['sweep_tube'](pure['rail_path'](s,cfg),cfg['rails']['radius_m'],cfg['rails']['tube_sides'])) for s in (-1,1)]}
    door_checks=[]
    for y,z in zip(cfg['doors']['centres_y_m'],cfg['doors']['thresholds_z_m']):
        h=cfg['doors']['width_m']/2;levels=[pure['floor_height'](yy,cfg) for yy in (y-h,y,y+h)]
        door_checks.append(dict(centre_y_m=y,threshold_z_m=z,adjacent_floor_near_mid_far_z_m=levels,
            corridor_floor_flat_across_door=max(levels)-min(levels)<1e-8,occlusion_requires_render=True))
    report=dict(schema_version=2,status='candidate_applied_to_plan_pending_real_render' if args.apply else 'candidate_not_applied',
        accepted=False,seed_constructor=seed,parameters=unpack(fit.x),solver_success=bool(fit.success),
        weighted_candidate_rms=float(np.sqrt(np.mean(residual(fit.x,False)**2))),landmarks=rows,mesh_checks=mesh,
        navigation_candidate=pure['navigation_proposal'](cfg,plan['navigation_proposal']),door_checks=door_checks,
        bounds_reached=[NAMES[i] for i in range(len(NAMES)) if min(abs(fit.x[i]-LOWER[i]),abs(fit.x[i]-UPPER[i]))<1e-4],
        limitations=['One-frame regularized candidate: no lens, metric scale, threshold or exact stair count recovered.',
            'Low guard/skirting is a hypothesis. Secondary frames do not unambiguously resolve trim height.',
            'Sill and apparent hall floor seam excluded from fit: occluded/ambiguous assignments.',
            'Independent closed door openings do not force a flat floor beneath. Next render must check unsupported sill and occlusion.',
            'Secondary frames reviewed for structure only; no multi-view camera solve or visibility check.',
            'No Blender mutation/render/export, material or decorative addition in this offline pass.'],
        historical_initial_render=dict(path='dream/validation/wave-gray-initial.png',
            sha256=hashlib.sha256((ROOT/'validation/wave-gray-initial.png').read_bytes()).hexdigest(),
            root_reported_scene_objects=82,blend='dream/blender/wave_corridor.blend',preserved=True),
        source_hashes={str(p.relative_to(ROOT.parent)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in [BUILDER,Path(__file__),ROOT/'validation/wave-reference-14s.png']})
    report['projection_proof']=projection_proof(cfg,pure,rows)
    if args.apply:
        plan['constructor']=cfg;plan['stage']='gray_geometry_candidate_v2_pending_render'
        plan['measurement_policy']='Approximate visible anchors with explicit excluded occlusions; all dimensions and camera values remain inferred regularized gray candidates.'
        plan['reference_manifest']['primary_frame_state']='Native frames preserved in dream/validation/wave-reference-{12p5s,14s,15p5s,17s}.png; original unchanged.'
        plan['reference_manifest']['expected_primary_parts']['main_ceiling_lights_seed']=3
        for a in plan['landmarks_primary_14s']:
            a['fit_use']='excluded' if a['id'] in excluded else 'fit'
            if a['id'] in excluded:a['assignment_warning']=excluded[a['id']]
        plan['geometry_fit']=dict(report='dream/validation/wave-geometry-fit-candidate.json',status=report['status'],accepted=False,
            applied_by='offline fit_wave_geometry.py --apply',supersedes='Initial constructor retained in report.seed_constructor; original PNG and blend preserved.')
        plan['validation']['geometry_gate']='v2 candidate pending real Blender gray render, source comparison and secondary-view review.'
        plan['execution_evidence']['scope']='Historical initial seed only. Original mesh/profile/navigation checks below do not describe v2.'
        plan['execution_evidence']['root_initial_execution']=report['historical_initial_render']
        PLAN.write_text(json.dumps(plan,indent=2)+'\n',encoding='utf8')
    REPORT.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:report[k] for k in ['status','parameters','weighted_candidate_rms','bounds_reached','door_checks']},indent=2))
    print(json.dumps([{k:r[k] for k in ['id','use','candidate_px','candidate_error_px']} for r in rows],indent=2))


if __name__=='__main__':
    main()
