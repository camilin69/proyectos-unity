"""Record the observed-form study and its material transfer without acceptance."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = 'validation/wave-hall-structure/'


def read(p): return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def write(p,r): (ROOT/p).write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


runtime = read('validation/wave-runtime-integration.json')
preserved = {}
for p,h in runtime['sha256'].items():
    if p.startswith(('assets/','runtime/')) or p=='blender/wave_corridor.blend':
        assert sha(p)==h,p
        preserved[p]=h
assert sha('runtime/build/dream.exe')==runtime['render']['binary_sha256']
for p,h in runtime['references_verified_unchanged'].items():
    assert hashlib.sha256((ROOT.parent/p).read_bytes()).hexdigest()==h,p
previous = read('validation/wave-aperture/review.json')
assert sha(previous['native'])==previous['sha256'][previous['native']]
native = read(OUT+'native-audit.json')
fit = read(OUT+'capital-fit.json')
look = read(OUT+'look-audit.json')
actual = read(OUT+'actual-look-audit.json')
assert all(m['closed'] and m['volume_m3']>0 for m in actual['meshes'])
assert len(actual['meshes'])==len(look['coverage'])==83
assert all(m['minimum_uv_area_m2']>1e-12 for m in look['coverage'])
assert actual['adjacent_floor_faces_uv_max_error_m']<1e-6
assert actual['inferred_lower_supports_visible']
assert len(actual['packed_images'])==8
assert all(i['source_identical'] for i in actual['packed_images'].values())
times = ['14','15.5','17']
sheet = Image.new('RGB',(1434,884*3),'#17191e')
draw = ImageDraw.Draw(sheet)
for row,t in enumerate(times):
    for col,(p,label) in enumerate([
        (f'validation/wave-motion/{t}s.png',f'SOURCE {t}s'),
        (OUT+f'gray-{t}s.png','BLENDER / geometry study'),
        (OUT+f'look-{t}s.png','BLENDER / preserved maps / unaccepted')]):
        im = Image.open(ROOT/p).convert('RGB')
        assert im.size==(478,850)
        x,y = col*478,row*884
        draw.text((x+8,y+10),label,fill='white')
        sheet.paste(im,(x,y+34))
sheet.save(ROOT/(OUT+'comparison.png'))
detail = Image.new('RGB',(956,884),'#17191e')
draw = ImageDraw.Draw(detail)
for x,p,label in [(0,'validation/wave-motion/17s.png','SOURCE 17s'),
                  (478,OUT+'look-17s.png','BLENDER / material study / not accepted')]:
    draw.text((x+8,10),label,fill='white')
    detail.paste(Image.open(ROOT/p).convert('RGB'),(x,34))
detail.save(ROOT/(OUT+'look-comparison-17s.png'))
now = datetime.now(timezone.utc).isoformat()
files = [str(p.relative_to(ROOT)).replace('\\','/') for p in (ROOT/OUT).iterdir() if p.is_file() and p.name!='review.json']
files += ['blender/build_wave_hall_structure.py','blender/finish_wave_hall_structure.py',
          'blender/build_wave_corridor.py','blender/build_wave_terminal_candidate.py',
          'blender/wave_corridor_hall_structure_candidate.blend','blender/wave_corridor_hall_look_candidate.blend',
          'validation/fit_wave_hall_capital.py','validation/record_wave_hall_structure_review.py']
report = {
    'schema':'dream.wave_hall_structure_review.v1','recorded_at_utc':now,
    'strict_fidelity_accepted':False,'runtime_promoted':False,'goal_complete':False,
    'native':native['native'],'material_native':look['native'],
    'comparison':OUT+'comparison.png','material_comparison':OUT+'look-comparison-17s.png',
    'gray_objects':native['objects'],'material_objects':actual['objects'],
    'closed_meshes':len(actual['meshes']),'cameras':actual['cameras'],'material_lights':actual['lights'],
    'changes':[
        'Replaced two arbitrary straight supports with the fitted upper contour of the right form and a separate left visible form.',
        'Kept full-height lower continuations visible and explicitly marked as inferred; did not hide them to match a silhouette.',
        'Widened the isolated hall and added eight side fixtures; spacing is provisional, not recovered lamp positions.',
        'Applied saved native material maps through explicit metric UV layers, with a checker render and all-face area checks.',
        'Added five explicit diffuse-return approximations; area emitters retain direct-light shadows.'],
    'fit_scope':{
        'right_visible_landmark_rms_px':fit['point_distance_rms_px'],
        'right_visible_landmark_max_px':fit['max_point_error_px'],
        'left_visible_landmark_rms_px':fit['left_visible_form']['point_distance_rms_px'],
        'note':'These are residuals on fitted visible contour/color tracks. They do not verify pillar floor contact, camera accuracy, or whole-scene fidelity.',
        'free_point_diagnostic':OUT+'free-point-diagnostic.json',
        'free_point_limit':'Lower residuals for independently triangulated points do not establish a rigid architectural model.'},
    'actual_native_checks':actual,
    'texture_preservation':{
        'packed_maps_used_by_this_study':8,
        'packed_bytes_match_original_png':True,
        'unused_sign_maps':'The two sign maps remain in the canonical native and on disk. This isolated study has no sign geometry yet.',
        'source_images_used_as_geometry_or_render_backdrop':False},
    'runtime_files_unchanged':preserved,
    'binary_unchanged_sha256':runtime['render']['binary_sha256'],
    'original_reference_files_verified':len(runtime['references_verified_unchanged']),
    'previous_aperture_native_preserved_sha256':sha(previous['native']),
    'limitations':[
        'Full-height supports project conspicuously below the visible source forms. The floor height, camera trajectory and support interpretation require joint re-evaluation.',
        'The visible lower color boundary is not proven floor contact; a raised hall or suspended structure is not established by this study.',
        'The dark rear grid and side fixture spacing remain provisional; source details and support depth are incomplete.',
        'Floor bands repeat too frequently in depth and differ in registration from the source. Reflection appearance is still much weaker and smoother than the video.',
        'Diffuse-return lights are an artistic approximation, not measured illumination. Shape and mounting of the lamps still need refinement.',
        'This candidate omits the canonical wall utility/sign details; it is not ready to replace the runtime scene.',
        'Earlier review hashes remain historical snapshots. The executable and previous native candidates have not been regenerated.'],
    'next_action':'Revisit source floor-contact evidence and camera/floor constraints together before exporting the hall; then refit floor pattern coordinates and architectural reflections.',
    'sha256':{p:sha(p) for p in sorted(files)}
}
write(OUT+'review.json',report)
inventory = read('validation/all-scenes-plan.json')
wave = next(s for s in inventory['scenes'] if s['scene_id']=='video-42/pasillo_ondulado')
entry = {k:report[k] for k in ['native','material_native','comparison','material_comparison','runtime_promoted','next_action']}
entry.update(report=OUT+'review.json',accepted=False)
wave['separate_hall_structure_candidate'] = entry
inventory['updated_at_utc'] = now
assert inventory['inventory']['implemented_prototypes']==5
assert inventory['inventory']['not_implemented']==8
assert inventory['inventory']['strictly_accepted_scenes']==0
write('validation/all-scenes-plan.json',inventory)
status = read('validation/status.json')
status['wave_progress']['separate_hall_structure_candidate'] = entry
status['current_validation_reports']['wave_hall_structure_candidate'] = OUT+'review.json'
status['expanded_scope']['inventory_sha256'] = sha('validation/all-scenes-plan.json')
for p in ['validation/all-scenes-plan.json',OUT+'review.json']:
    status['current_report_hashes'][p] = sha(p)
write('validation/status.json',status)
print(json.dumps({'review':OUT+'review.json','closed_meshes':83,'packed_maps':8,
                  'references_preserved':len(runtime['references_verified_unchanged']),
                  'runtime_preserved':True,'strict_fidelity_accepted':False}))
