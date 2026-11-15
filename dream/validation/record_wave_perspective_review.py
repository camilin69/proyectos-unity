"""Record perspective/paint failures and the verified wall-panel addition."""
from pathlib import Path
from datetime import datetime,timezone
import json
import hashlib
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];OUT='validation/wave-perspective/'
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
previous=read('validation/wave-hall-structure/review.json')
for p in [previous['native'],previous['material_native']]:assert sha(p)==previous['sha256'][p],p
native=read(OUT+'native-wall-audit.json');actual=read(OUT+'actual-native-checks.json')
panels=read(OUT+'wall-panels-fit.json');perspective=read(OUT+'floor-contact-hypothesis.json')
paint=read(OUT+'paint-fit.json');spline=read(OUT+'paint-spline-fit.json')
assert len(native['meshes'])==95 and all(m['closed'] and m['volume_m3']>0 for m in native['meshes'])
assert len(native['panel_parts'])==12 and all(m['minimum_uv_face_area_m2']>1e-12 for m in native['panel_parts'])
assert len(actual['packed_original_maps'])==8
canvas=Image.new('RGB',(956,3*884),'#17191e');draw=ImageDraw.Draw(canvas)
for row,t in enumerate(['14','15.5','17']):
    y=row*884
    for x,p,label in [(0,f'validation/wave-motion/{t}s.png',f'SOURCE {t}s'),
                      (478,OUT+f'wall-{t}s.png','BLENDER / fitted wall panels / draft')]:
        im=Image.open(ROOT/p).convert('RGB');assert im.size==(478,850)
        canvas.paste(im,(x,y+34));draw.text((x+8,y+10),label,fill='white')
canvas.save(ROOT/(OUT+'wall-comparison.png'))
detail=Image.new('RGB',(960,780),'#17191e');draw=ImageDraw.Draw(detail)
for x,p,label in [(0,'validation/wave-motion/17s.png','SOURCE 17s / wall panels'),
                  (480,OUT+'wall-17s.png','BLENDER / wall panels')]:
    crop=Image.open(ROOT/p).convert('RGB').crop((40,190,136,340)).resize((480,750))
    detail.paste(crop,(x,30));draw.text((x+8,8),label,fill='white')
detail.save(ROOT/(OUT+'wall-panel-detail.png'))
files=[str(p.relative_to(ROOT)).replace('\\','/') for p in (ROOT/OUT).iterdir() if p.is_file() and p.name!='review.json']
files+=['validation/fit_wave_hall_perspective.py','validation/fit_wave_paint_multiview.py','validation/fit_wave_paint_spline.py',
        'validation/fit_wave_wall_panels.py','validation/record_wave_perspective_review.py',
        'blender/build_wave_wall_detail_candidate.py','blender/wave_corridor_wall_detail_candidate.blend']
now=datetime.now(timezone.utc).isoformat()
report={'schema':'dream.wave_perspective_and_wall_review.v1','recorded_at_utc':now,
        'accepted':False,'runtime_promoted':False,'goal_complete':False,'native':native['native'],
        'comparison':OUT+'wall-comparison.png','detail':OUT+'wall-panel-detail.png',
        'objects':actual['objects'],'meshes':len(native['meshes']),'cameras':actual['cameras'],'lights':actual['lights'],
        'implemented_change':'Added two wall utility panels with separate closed backs, recessed inserts and four rim segments per panel, fitted to tracked source corners.',
        'panel_fit':{k:panels[k] for k in ['parameters','training_times_s','heldout_times_s','training_rms_px','heldout_rms_px','valid_corner_samples_per_view','limitations']},
        'native_checks':actual,
        'rejected_experiments':{
            'floor_contact':{'report':OUT+'floor-contact-hypothesis.json','applied':False,
                'hall_clear_height_m':perspective['hall_clear_height_m'],'parameters':perspective['hall_parameters'],
                'reason':'Joint fitting needs distant oversized hall supports and reaches the left lateral bound. Sparse residuals do not substantiate those physical dimensions or establish that the colour boundary touches the floor.'},
            'repeating_paint':{'report':OUT+'paint-fit.json','applied':False,'metrics':paint['candidate'],
                'reason':'Lower interval distance does not increase held-out label coverage enough to justify replacement.'},
            'spline_paint':{'report':OUT+'paint-spline-fit.json','applied':False,'metrics':spline['metrics'],
                'reason':'Fits 31 of 38 training labels within tolerance but only 2 of 10 held-out 16s labels. Do not bake an overfit trajectory into the scene.',
                'history':'The earlier two-view fit failed at 17s; its parameters/results are retained separately. The three-view fit uses 17s as training and 16s as the new held-out view.'},
            'floor_tracks':{'report':OUT+'floor-track-candidates.json','applied':False,
                'reason':'Many candidates follow white highlights or trim rather than identifiable painted floor points. Their triangulated depths are not used as floor geometry.'}},
        'runtime_files_unchanged':preserved,'binary_unchanged_sha256':runtime['render']['binary_sha256'],
        'original_reference_files_verified':len(runtime['references_verified_unchanged']),
        'previous_native_hashes':{p:sha(p) for p in [previous['native'],previous['material_native']]},
        'limitations':['Panel corners are blurred; approximately 5 px held-out error is not exact geometric recovery. The 17s detail render still differs in top-edge inclination, inset tone and frame thickness.',
                       'The support-floor mismatch, repeated paint trajectory, reflections, lamp forms and omitted wall details remain unresolved.',
                       'All 13 scenarios remain in scope: five runtime prototypes, eight without runtime, zero strict visual acceptance.'],
        'next_action':'Check directional constraints from ceiling edges and panel edges to distinguish camera error from panel shape; use painted-boundary correspondences across short source intervals for floor depth, excluding highlights.',
        'sha256':{p:sha(p) for p in sorted(files)}}
write(OUT+'review.json',report)
inventory=read('validation/all-scenes-plan.json');wave=next(s for s in inventory['scenes'] if s['scene_id']=='video-42/pasillo_ondulado')
entry={k:report[k] for k in ['native','comparison','detail','runtime_promoted','next_action']};entry.update(report=OUT+'review.json',accepted=False)
wave['separate_wall_detail_candidate']=entry;inventory['updated_at_utc']=now
assert inventory['inventory']['implemented_prototypes']==5 and inventory['inventory']['not_implemented']==8 and inventory['inventory']['strictly_accepted_scenes']==0
write('validation/all-scenes-plan.json',inventory)
status=read('validation/status.json');status['wave_progress']['separate_wall_detail_candidate']=entry
status['current_validation_reports']['wave_perspective_and_wall_candidate']=OUT+'review.json'
status['expanded_scope']['inventory_sha256']=sha('validation/all-scenes-plan.json')
for p in ['validation/all-scenes-plan.json',OUT+'review.json']:status['current_report_hashes'][p]=sha(p)
write('validation/status.json',status)
print(json.dumps({'native':report['native'],'panel_parts':12,'closed_meshes':95,'original_packed_maps':8,
                  'panel_heldout_rms_px':panels['heldout_rms_px'],'runtime_preserved':True,'accepted':False}))
