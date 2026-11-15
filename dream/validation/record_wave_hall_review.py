"""Record the separate, unaccepted hall reconstruction and its diagnostics."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8-sig'))
def sha(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
def write(name,value):(ROOT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.now(timezone.utc).isoformat()
audit=read('validation/wave-hall-audit.json')
coverage=read('validation/wave-hall-uv-coverage.json')
diagnostic=read('validation/wave-hall-constraint-diagnostic.json')
baseline=read('validation/wave-runtime-integration.json')
assert sha('blender/wave_corridor_hall_candidate.blend')==audit['candidate_sha256']
assert not coverage['degenerate_uv_faces'] and coverage['floor_hall_max_uv_error_m']<1e-5
preserved={}
for path,expected in baseline['sha256'].items():
    if path.startswith('assets/') or path in ('blender/wave_corridor.blend','runtime/shaders/scene.frag'):
        assert sha(path)==expected,path
        preserved[path]=expected
assert sha('runtime/build/dream.exe')==baseline['render']['binary_sha256']
for path,expected in baseline['references_verified_unchanged'].items():
    assert hashlib.sha256((ROOT.parent/path).read_bytes()).hexdigest()==expected,path

rows=[('validation/wave-reference-14s.png','validation/wave-hall-candidate-v11.png','14 s'),
      ('validation/wave-reference-15p5s.png','validation/wave-hall-candidate-v11-secondary.png','15.5 s')]
sheet=Image.new('RGB',(956,1768),'#19191b');draw=ImageDraw.Draw(sheet)
for i,(reference,candidate,label) in enumerate(rows):
    y=i*884
    draw.text((10,y+10),'VIDEO '+label,fill='white')
    draw.text((488,y+10),'HALL CANDIDATE / geometry not accepted',fill='white')
    for x,path in ((0,reference),(478,candidate)):
        image=Image.open(ROOT/path).convert('RGB');assert image.size==(478,850)
        sheet.paste(image,(x,y+34))
sheet.save(ROOT/'validation/wave-hall-comparison.png')
files=['blender/wave_corridor_hall_candidate.blend','blender/wave_hall_plan.json',
       'blender/refine_wave_hall.py','blender/audit_wave_hall.py','blender/finish_wave_corridor.py',
       'blender/wave_material_plan.json','blender/prepare_wave_runtime.py',
       'validation/wave-hall-audit.json','validation/wave-hall-uv-coverage.json',
       'validation/wave-hall-checker-audit.json','validation/wave-hall-checker-secondary.png',
       'validation/wave-hall-constraint-diagnostic.json','validation/fit_wave_hall_constraints.py',
       'validation/wave-hall-candidate-v10.png','validation/wave-hall-candidate-v11.png',
       'validation/wave-hall-candidate-v11-secondary.png','validation/wave-hall-comparison.png',
       'validation/wave-hall-reference-17s.png','validation/wave-hall-reference-pair.png']
report={'schema':'dream.wave_hall_review.v1','recorded_at_utc':now,
        'stage':'editable_hall_candidate_geometry_rejected_for_runtime_promotion',
        'strict_fidelity_accepted':False,'runtime_promoted':False,'goal_complete':False,
        'native':'blender/wave_corridor_hall_candidate.blend','scene_objects':122,'mesh_objects':92,
        'closed_hall_meshes':47,'packed_images':10,
        'changes':['Replaced the short, full-width dark grid with a deeper hall enclosure.',
                   'Added broad pale supports, a turquoise accent and horizontal members.',
                   'Added two side rows of four ceiling fixtures and their real light contribution.',
                   'Added entrance return walls and metric UVs on all new closed surfaces.'],
        'uv_checker':'Secondary checker render inspected; all closed faces have explicit UVs, with no degenerate faces and a continuous floor/hall boundary.',
        'floor_hall_uv_error_m':coverage['floor_hall_max_uv_error_m'],
        'comparison':'validation/wave-hall-comparison.png',
        'geometry_findings':audit['column_projection_diagnostics'],
        'constraint_comparison':{'fixed_floor_weighted_rms':diagnostic['fixed_flat_hall']['weighted_rms'],
                                 'free_vertical_span_weighted_rms':diagnostic['free_vertical_span']['weighted_rms'],
                                 'interpretation':diagnostic['interpretation']},
        'limitations':['The main support extends too far down in both source views; do not accept this candidate as a matched hall.',
                       'Rear horizontal members are represented as rails provisionally; stairs or reflected structures have not been ruled out.',
                       'New hall depth, width, columns and rails do not yet have matching runtime collisions.',
                       'No new runtime export, GLB, animation or source-camera trajectory was produced.'],
        'next_action':diagnostic['next_action'],
        'verified_runtime_files_unchanged':preserved,
        'original_reference_files_unchanged':len(baseline['references_verified_unchanged']),
        'source_guard':'prepare_wave_runtime.py now refuses the live hall candidate before mutation. The verified canonical .blend is unchanged.',
        'history_policy':'wave-runtime-integration.json remains the preceding export snapshot; its prepare_wave_runtime.py hash predates the new guard.',
        'sha256':{path:sha(path) for path in files}}
write('validation/wave-hall-review.json',report)
plan=read('validation/all-scenes-plan.json')
wave=next(x for x in plan['scenes'] if x['scene_id']=='video-42/pasillo_ondulado')
wave['separate_hall_candidate']={'native':report['native'],'report':'validation/wave-hall-review.json',
    'runtime_promoted':False,'accepted':False,'next_action':report['next_action']}
plan['updated_at_utc']=now
write('validation/all-scenes-plan.json',plan)
status=read('validation/status.json')
status['wave_progress']['separate_hall_candidate']=wave['separate_hall_candidate']
status['current_validation_reports']['wave_hall_candidate']='validation/wave-hall-review.json'
status['expanded_scope']['inventory_sha256']=sha('validation/all-scenes-plan.json')
for path in ('validation/all-scenes-plan.json','validation/wave-hall-review.json'):
    status['current_report_hashes'][path]=sha(path)
write('validation/status.json',status)
print(json.dumps({'saved':report['native'],'closed_hall_meshes':47,'packed_images':10,
                  'runtime_preserved':True,'accepted':False,'next_action':report['next_action']}))
