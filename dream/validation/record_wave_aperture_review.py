"""Record corrected corner identities and the staggered entrance hypothesis."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib
import json
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def write(p,r):(ROOT/p).write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
runtime=read('validation/wave-runtime-integration.json');preserved={}
for p,h in runtime['sha256'].items():
    if p.startswith(('assets/','runtime/')) or p=='blender/wave_corridor.blend':
        assert sha(p)==h,p;preserved[p]=h
assert sha('runtime/build/dream.exe')==runtime['render']['binary_sha256']
for p,h in runtime['references_verified_unchanged'].items():
    assert hashlib.sha256((ROOT.parent/p).read_bytes()).hexdigest()==h,p
previous=read('validation/wave-terminal/review.json')
assert sha(previous['native'])==previous['sha256'][previous['native']]
fit=read('validation/wave-aperture/fit.json');native=read('validation/wave-aperture/native-audit.json')
actual=read('validation/wave-aperture/native-alignment.json')
assert actual['passed'] and len(actual['actual_camera_corner_projections'])==14
assert all(m['closed'] and m['volume_m3']>0 for m in native['meshes'])
assert fit['hypotheses']['staggered']['heldout_point_rms_px']<fit['hypotheses']['aligned']['heldout_point_rms_px']
# Recheck the optional constructor changes against the unchanged default plan.
p=ROOT/'blender/build_wave_corridor.py';ns={'__file__':str(p),'__name__':'aperture_review_helpers'}
exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),ns)
plan=read('blender/wave_corridor_plan.json');c=plan['constructor']
values={'floor':ns['floor_geometry'](c),'left_rail':ns['rail_path'](-1,c),'right_rail':ns['rail_path'](1,c),
        'doors':ns['door_openings'](c),'navigation':ns['navigation_proposal'](c,plan['navigation_proposal'])}
hashes={k:hashlib.sha256(json.dumps(v,sort_keys=True).encode()).hexdigest() for k,v in values.items()}
assert hashes==read('validation/wave-terminal/default-builder-before.json')
sheet=Image.new('RGB',(956,4*884),'#17191e');d=ImageDraw.Draw(sheet)
for i,t in enumerate(['14','15.5','16.5','17']):
    y=i*884;d.text((10,y+10),f'SOURCE {t}s',fill='white');d.text((488,y+10),'BLENDER / staggered entrance / draft',fill='white')
    for x,p in [(0,f'validation/wave-motion/{t}s.png'),(478,f'validation/wave-aperture/gray-{t}s.png')]:
        im=Image.open(ROOT/p).convert('RGB');assert im.size==(478,850);sheet.paste(im,(x,y+34))
sheet.save(ROOT/'validation/wave-aperture/comparison.png')
detail=Image.new('RGB',(956,420),'#17191e');d=ImageDraw.Draw(detail)
for x,p,label in [(0,'validation/wave-motion/17s.png','SOURCE 17s'),(478,'validation/wave-aperture/gray-17s.png','BLENDER / corrected wall ends')]:
    detail.paste(Image.open(ROOT/p).crop((0,0,478,385)),(x,35));d.text((x+8,10),label,fill='white')
detail.save(ROOT/'validation/wave-aperture/ceiling-detail.png')
files=['blender/build_wave_corridor.py','blender/build_wave_terminal_candidate.py','blender/build_wave_aperture_candidate.py',
       'blender/wave_corridor_aperture_candidate.blend','validation/check_wave_aperture_tracks.py','validation/measure_wave_ceiling_edges.py',
       'validation/fit_wave_aperture.py','validation/record_wave_aperture_review.py']
files += [str(p.relative_to(ROOT)).replace('\\','/') for p in (ROOT/'validation/wave-aperture').iterdir() if p.is_file() and p.name!='review.json']
now=datetime.now(timezone.utc).isoformat()
report={'schema':'dream.wave_aperture_review.v1','recorded_at_utc':now,'strict_fidelity_accepted':False,
        'runtime_promoted':False,'goal_complete':False,'native':native['saved'],
        'comparison':'validation/wave-aperture/comparison.png','detail':'validation/wave-aperture/ceiling-detail.png',
        'scene_objects':native['objects'],'closed_meshes':len(native['meshes']),'cameras':native['cameras'],
        'source_label_correction':{'old_labels':'Earlier aperture markers mixed background light/glow details with the actual wall-ceiling junction.',
            'new_labels':'Two visible wall corners manually seeded at 17s and tracked back in three LK window sizes; median positions used.',
            'automatic_mask_rejected':'Connected pink-color segmentation included reflected floor patches and clipped wall masks when the camera turned. Its low residuals at 15.5s are not valid geometry evidence.',
            'comparison_policy':'Old ceiling-error figures used different source labels and are not directly comparable. Aligned and staggered hypotheses here use the same corrected observations.'},
        'hypothesis_comparison':fit['hypotheses'],'training_times_s':fit['training_times_s'],'heldout_times_s':fit['heldout_times_s'],
        'heldout_caveat':fit['limitations'][1],
        'changes':['Added separate left/right wall endpoints and shortened each low wall trim to its own wall.',
                   'Kept a continuous flat ceiling across the widened entrance, with closed side landing strips.',
                   'Preserved diffuser world heights while adjusting ceiling height, and added small mounting stems.',
                   'Placed each diagnostic area emitter below its opaque diffuser to avoid self-occlusion; energies unchanged.'],
        'native_checks':actual,'guard_uv':native['guard_uv'],'default_builder_pure_outputs_unchanged':hashes,
        'runtime_files_unchanged':preserved,'binary_unchanged_sha256':runtime['render']['binary_sha256'],
        'original_reference_files_verified':len(runtime['references_verified_unchanged']),
        'previous_terminal_blend_preserved_sha256':sha(previous['native']),
        'history_policy':'Previous motion and terminal review JSON files describe earlier snapshots of the builder. Their saved blends and renders are preserved; this report contains the updated builder hashes.',
        'limitations':['The staggered wall-end reconstruction is supported by the sampled corner tracks, not by measured real-world dimensions.',
                       'The gray hall still has provisional columns and a dark rear grid that do not reproduce the video.',
                       'Floor patterns, low trim cross section, detailed lamp shapes and final lighting still need work.',
                       'No textured candidate export or new OpenGL navigation was produced; the existing runtime remains the earlier prototype.'],
        'next_action':'Replace the provisional hall supports and rear grid using complete source silhouettes, separating pale paint from turquoise cladding and floor contact.',
        'sha256':{p:sha(p) for p in sorted(files)}}
write('validation/wave-aperture/review.json',report)
inventory=read('validation/all-scenes-plan.json');wave=next(s for s in inventory['scenes'] if s['scene_id']=='video-42/pasillo_ondulado')
wave['separate_aperture_candidate']={k:report[k] for k in ['native','comparison','runtime_promoted','next_action']}
wave['separate_aperture_candidate'].update(report='validation/wave-aperture/review.json',accepted=False)
inventory['updated_at_utc']=now;write('validation/all-scenes-plan.json',inventory)
status=read('validation/status.json');status['wave_progress']['separate_aperture_candidate']=wave['separate_aperture_candidate']
status['current_validation_reports']['wave_aperture_candidate']='validation/wave-aperture/review.json'
status['expanded_scope']['inventory_sha256']=sha('validation/all-scenes-plan.json')
assert status['expanded_scope']['implemented_prototypes']==5 and status['expanded_scope']['strictly_accepted_scenes']==0
for p in ['validation/all-scenes-plan.json','validation/wave-aperture/review.json']:status['current_report_hashes'][p]=sha(p)
write('validation/status.json',status)
print(json.dumps({'saved':report['native'],'closed_meshes':report['closed_meshes'],
                  'heldout_rms_aligned_px':fit['hypotheses']['aligned']['heldout_point_rms_px'],
                  'heldout_rms_staggered_px':fit['hypotheses']['staggered']['heldout_point_rms_px'],
                  'runtime_preserved':True,'strict_fidelity_accepted':False}))
