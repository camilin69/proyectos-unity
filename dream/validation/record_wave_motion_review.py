"""Record the actual seven-pose geometry study and preserve runtime provenance."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import numpy as np
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def write(p,data):(ROOT/p).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

baseline=read('validation/wave-runtime-integration.json')
preserved={}
for p,expected in baseline['sha256'].items():
    if p.startswith(('assets/','runtime/')) or p=='blender/wave_corridor.blend':
        assert sha(p)==expected,p
        preserved[p]=expected
assert sha('runtime/build/dream.exe')==baseline['render']['binary_sha256']
for p,expected in baseline['references_verified_unchanged'].items():
    assert hashlib.sha256((ROOT.parent/p).read_bytes()).hexdigest()==expected,p
hall=read('validation/wave-hall-review.json')
assert sha('blender/wave_corridor_hall_candidate.blend')==hall['sha256']['blender/wave_corridor_hall_candidate.blend']

fit=read('validation/wave-motion/geometry-candidate.json')
track_source=read('validation/wave-motion/tracks.json')
assert sha(track_source['source'])==track_source['sha256']
native=read('validation/wave-motion/native-audit.json')
assert native['cameras']==7 and all(r['closed'] and r['volume_m3']>0 for r in native['meshes'])
ns={'__file__':str(ROOT/'validation/fit_wave_geometry.py'),'__name__':'motion_review_helpers'}
exec(compile(Path(ns['__file__']).read_text(encoding='utf-8'),ns['__file__'],'exec'),ns)
pts=fit['motion_point_positions'];cams=fit['plan']['constructor']['all_source_cameras']
distances=[]
for c in cams:
    pp=ns['projected'](dict(enumerate(pts)),c)
    for i,identity in enumerate(fit['motion_track_ids']):
        track=next(r for r in track_source['survivors'] if r['id']==identity)
        obs=min(track['samples'],key=lambda s:abs(s[0]-c['time_s']))[1:]
        distances.append(float(np.linalg.norm(np.array(pp[i])-obs)))

sheet=Image.new('RGB',(956,3*884),'#17191e');draw=ImageDraw.Draw(sheet)
for i,t in enumerate(['14','15.5','17']):
    y=i*884
    draw.text((10,y+10),f'SOURCE {t}s',fill='white')
    draw.text((488,y+10),'BLENDER / motion candidate / NOT ACCEPTED',fill='white')
    for x,p in [(0,f'validation/wave-motion/{t}s.png'),(478,f'validation/wave-motion/gray-{t}s.png')]:
        im=Image.open(ROOT/p).convert('RGB');assert im.size==(478,850);sheet.paste(im,(x,y+34))
sheet.save(ROOT/'validation/wave-motion/comparison.png')

previous=read('validation/wave-joint-third-view.json')
files=['blender/build_wave_corridor.py','blender/build_wave_motion_candidate.py',
       'blender/wave_corridor_motion_candidate.blend','validation/inspect_wave_motion.py',
       'validation/fit_wave_wall_motion.py','validation/fit_wave_motion_geometry.py',
       'validation/record_wave_motion_review.py']
files += [str(p.relative_to(ROOT)).replace('\\','/') for p in (ROOT/'validation/wave-motion').iterdir() if p.is_file() and p.name!='review.json']
now=datetime.now(timezone.utc).isoformat()
report={'schema':'dream.wave_motion_review.v1','recorded_at_utc':now,
        'strict_fidelity_accepted':False,'runtime_promoted':False,'goal_complete':False,
        'native':'blender/wave_corridor_motion_candidate.blend','comparison':'validation/wave-motion/comparison.png',
        'scene_objects':native['objects'],'closed_meshes':len(native['meshes']),'camera_count':native['cameras'],
        'source_interval_s':[12.33,17.37],
        'sequence_note':'17.5s and 18s in the contact sheet are the next scene after the cut, and were not fitted.',
        'source_tracking':{'seeds':track_source['seed_count'],'survived_14_to_17_s':len(track_source['survivors']),
                           'selected_static_tracks':fit['motion_track_ids'],'excluded_for_large_plane_fit_residual':fit['excluded_motion_track_ids'],
                           'camera_times_s':[c['time_s'] for c in cams],
                           'point_distance_rms_px':float(np.sqrt(np.mean(np.square(distances)))),
                           'max_point_distance_px':max(distances),
                           'caveat':'These are fitted source tracks, not independent validation. Reflections and distant supports were not motion constraints.'},
        'previous_joint_candidate':{'native':'blender/wave_corridor_joint_candidate.blend',
            'third_view_report':'validation/wave-joint-third-view.json','runtime_promoted':False,'accepted':False,
            'finding':'Two-view fit failed the independent 17s view: both lamp hypotheses left the second doorway in the frame.'},
        'changes':['Added a source sequence and continuous optical tracking instead of choosing unrelated lamp centers per frame.',
                   'Estimated seven camera poses and jointly fitted corridor geometry with selected wall and trim tracks.',
                   'Resolved the wall-only global-pitch ambiguity by including the door and ceiling observations.',
                   'Built and inspected actual Blender gray renders at 14, 15.5 and 17 seconds; the second doorway now leaves the last frame.'],
        'remaining':['The 17s aperture top-left remains approximately 38 pixels from the manually assigned observation.',
                     'The 17s middle trim ends remain approximately 26 and 27 pixels away; stairs and trim heights are not locked.',
                     'Hall columns, rear openness and terminal upright handrails still need reconstruction.',
                     'The gray candidate has no final surface-material pass, no updated runtime collisions, and no OpenGL export.',
                     'Three manually assigned lamp points and ambiguous ceiling corners are not exact recovered dimensions.'],
        'next_action':'Reconstruct the terminal upright handrails and hall entrance from continuous tracks; separate those supports from the low wall trim before refining the floor profile.',
        'canonical_runtime_files_unchanged':preserved,
        'binary_unchanged_sha256':baseline['render']['binary_sha256'],
        'original_reference_files_verified':len(baseline['references_verified_unchanged']),
        'original_reference_sha256':baseline['references_verified_unchanged'],
        'sha256':{p:sha(p) for p in sorted(files)}}
write('validation/wave-motion/review.json',report)
plan=read('validation/all-scenes-plan.json')
wave=next(s for s in plan['scenes'] if s['scene_id']=='video-42/pasillo_ondulado')
wave['separate_motion_candidate']={k:report[k] for k in ['native','comparison','runtime_promoted','next_action']}
wave['separate_motion_candidate'].update(report='validation/wave-motion/review.json',accepted=False,camera_count=7)
wave['separate_joint_candidate']=report['previous_joint_candidate']
plan['updated_at_utc']=now;write('validation/all-scenes-plan.json',plan)
status=read('validation/status.json')
status['wave_progress']['separate_motion_candidate']=wave['separate_motion_candidate']
status['wave_progress']['separate_joint_candidate']=wave['separate_joint_candidate']
status['current_validation_reports']['wave_motion_candidate']='validation/wave-motion/review.json'
status['expanded_scope']['inventory_sha256']=sha('validation/all-scenes-plan.json')
assert status['expanded_scope']['implemented_prototypes']==5 and status['expanded_scope']['strictly_accepted_scenes']==0
for p in ['validation/all-scenes-plan.json','validation/wave-motion/review.json']:status['current_report_hashes'][p]=sha(p)
write('validation/status.json',status)
print(json.dumps({'saved':report['native'],'closed_meshes':report['closed_meshes'],
                  'camera_count':7,'source_tracking':report['source_tracking'],
                  'runtime_preserved':True,'strict_fidelity_accepted':False}))
