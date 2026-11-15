"""Record the terminal guards, real renders and actual mesh attachment checks."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import numpy as np
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def write(p,r):(ROOT/p).write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def module(p):
    path=ROOT/p;ns={'__file__':str(path),'__name__':'terminal_review_helpers'}
    exec(compile(path.read_text(encoding='utf-8'),str(path),'exec'),ns);return ns
baseline=read('validation/wave-runtime-integration.json')
preserved={}
for p,h in baseline['sha256'].items():
    if p.startswith(('assets/','runtime/')) or p=='blender/wave_corridor.blend':
        assert sha(p)==h,p;preserved[p]=h
assert sha('runtime/build/dream.exe')==baseline['render']['binary_sha256']
for p,h in baseline['references_verified_unchanged'].items():
    assert hashlib.sha256((ROOT.parent/p).read_bytes()).hexdigest()==h,p
previous=read('validation/wave-motion/review.json')
assert sha(previous['native'])==previous['sha256'][previous['native']]
builder=module('blender/build_wave_corridor.py');base=module('validation/fit_wave_geometry.py')
canonical=read('blender/wave_corridor_plan.json');c=canonical['constructor']
values={'floor':builder['floor_geometry'](c),'left_rail':builder['rail_path'](-1,c),'right_rail':builder['rail_path'](1,c),
        'doors':builder['door_openings'](c),'navigation':builder['navigation_proposal'](c,canonical['navigation_proposal'])}
hashes={k:hashlib.sha256(json.dumps(v,sort_keys=True).encode()).hexdigest() for k,v in values.items()}
assert hashes==read('validation/wave-terminal/default-builder-before.json')
fit=read('validation/wave-terminal/geometry-candidate.json');cfg=fit['plan']['constructor']
native=read('validation/wave-terminal/native-audit.json');actual=read('validation/wave-terminal/mesh-attachments.json')
assert actual['passed'] and actual['checked_rays']==8
assert all(x['closed'] and x['volume_m3']>0 for x in native['meshes'])
assert all(x['all_faces_explicit_uv'] and x['min_uv_face_area_m2']>1e-12 for x in native['guard_uv'])
old=read('validation/wave-motion/geometry-candidate.json')
points=base['geometry'](cfg,builder)
for key in ['aperture_top_left','aperture_top_right']:points[key][1]=cfg['corridor']['wall_end_y_m']
cams={cam['time_s']:cam for cam in cfg['all_source_cameras']}
diagnostics=[]
for row in old['landmarks']:
    if not any(k in row['id'] for k in ['rail_corner','trim_end','flight_end','aperture_top']):continue
    projected=base['projected'](points,cams[row['time_s']])[row['id']]
    diagnostics.append({'id':row['id'],'time_s':row['time_s'],'source_px':row['source_px'],
                        'before_error_px':row['error_px'],'after_error_px':float(np.linalg.norm(np.array(projected)-row['source_px'])),
                        'after_projected_px':projected})
sheet=Image.new('RGB',(956,3*884),'#17191e');draw=ImageDraw.Draw(sheet)
for i,t in enumerate(['14','15.5','17']):
    y=i*884;draw.text((10,y+10),f'SOURCE {t}s',fill='white');draw.text((488,y+10),'BLENDER / terminal guards / NOT ACCEPTED',fill='white')
    for x,p in [(0,f'validation/wave-motion/{t}s.png'),(478,f'validation/wave-terminal/gray-{t}s.png')]:
        im=Image.open(ROOT/p).convert('RGB');assert im.size==(478,850);sheet.paste(im,(x,y+34))
sheet.save(ROOT/'validation/wave-terminal/comparison.png')
files=['blender/build_wave_corridor.py','blender/build_wave_terminal_candidate.py','blender/wave_corridor_terminal_candidate.blend',
       'validation/track_wave_terminal.py','validation/fit_wave_terminal.py','validation/fit_wave_terminal_geometry.py',
       'validation/record_wave_terminal_review.py']
files += [str(p.relative_to(ROOT)).replace('\\','/') for p in (ROOT/'validation/wave-terminal').iterdir() if p.is_file() and p.name!='review.json']
now=datetime.now(timezone.utc).isoformat()
report={'schema':'dream.wave_terminal_review.v1','recorded_at_utc':now,'strict_fidelity_accepted':False,
        'runtime_promoted':False,'goal_complete':False,'native':native['saved'],
        'comparison':'validation/wave-terminal/comparison.png','reverse_view':'validation/wave-terminal/gray-reverse.png',
        'scene_objects':native['objects'],'closed_meshes':len(native['meshes']),'cameras':native['cameras'],
        'changes':['Added two tall terminal guard frames with rounded bends, explicit tube and cap UVs.',
                   'Separated the end of the corridor walls from the end of the continuous stair floor.',
                   'Moved the final flight into the hall entrance and added closed side landing strips.',
                   'Adjusted the middle and final descents against continuously tracked terminal frame corners.'],
        'reference_fit':{'sampled_views':7,'point_distance_rms_px':fit['point_distance_rms_px'],
                         'max_point_distance_px':fit['max_point_distance_px'],
                         'scope':'Fitted approximate terminal corner tracks only; not full-scene fidelity or independent validation.'},
        'existing_landmark_diagnostics':diagnostics,
        'actual_mesh_checks':actual,'guard_uv_checks':native['guard_uv'],
        'default_builder_pure_outputs_unchanged':hashes,
        'canonical_runtime_files_unchanged':preserved,
        'binary_unchanged_sha256':baseline['render']['binary_sha256'],
        'original_reference_files_verified':len(baseline['references_verified_unchanged']),
        'previous_motion_blend_unchanged_sha256':sha(previous['native']),
        'history_policy':'wave-motion/review.json describes the previous snapshot. Its builder hash predates the optional open-terminal support; its saved .blend and renders remain unchanged.',
        'limitations':['The source foot locations are partially occluded, and the two guards still differ by up to 13 pixels in the sampled views.',
                       'The 17s opening-top observations regress: left error increases from 38 to 59 px and right from 17 to 44 px. Do not promote this geometry as an overall fidelity improvement.',
                       'Opening height, low trim cross-section, background supports and the dark rear grid are unresolved.',
                       'Panel infill, final guard metal finish, texture alignment and lighting have not been accepted.',
                       'This is a separate Blender reconstruction; there is no new OpenGL export or tested runtime navigation for this variant.'],
        'next_action':'Resolve the conflicting 17s ceiling/opening-top observations against the continuous source before changing ceiling geometry or promoting the new floor. Then refine hall supports using full surfaces, separating pale paint, turquoise cladding and floor contact.',
        'sha256':{p:sha(p) for p in sorted(files)}}
write('validation/wave-terminal/review.json',report)
plan=read('validation/all-scenes-plan.json');wave=next(s for s in plan['scenes'] if s['scene_id']=='video-42/pasillo_ondulado')
wave['separate_terminal_candidate']={k:report[k] for k in ['native','comparison','runtime_promoted','next_action']}
wave['separate_terminal_candidate'].update(report='validation/wave-terminal/review.json',accepted=False)
plan['updated_at_utc']=now;write('validation/all-scenes-plan.json',plan)
status=read('validation/status.json');status['wave_progress']['separate_terminal_candidate']=wave['separate_terminal_candidate']
status['current_validation_reports']['wave_terminal_candidate']='validation/wave-terminal/review.json'
status['expanded_scope']['inventory_sha256']=sha('validation/all-scenes-plan.json')
assert status['expanded_scope']['implemented_prototypes']==5 and status['expanded_scope']['strictly_accepted_scenes']==0
for p in ['validation/all-scenes-plan.json','validation/wave-terminal/review.json']:status['current_report_hashes'][p]=sha(p)
write('validation/status.json',status)
print(json.dumps({'native':report['native'],'closed_meshes':report['closed_meshes'],'cameras':report['cameras'],
                  'reference_fit':report['reference_fit'],'mesh_checks_passed':True,'runtime_preserved':True,
                  'existing_landmarks':diagnostics,'accepted':False}))
