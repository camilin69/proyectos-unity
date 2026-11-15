"""Record the inspected wave runtime iteration and reconcile current inventory.

Run after the render, export, navigation and regression checks. Historical
reports remain snapshots; this does not promote visual fidelity acceptance.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
def read(name):
    return json.loads((ROOT/name).read_text(encoding='utf-8-sig'))
def write(name, value):
    (ROOT/name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def sha(name):
    return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
now = datetime.now(timezone.utc).isoformat()
plan = read('validation/all-scenes-plan.json')
status = read('validation/status.json')
native = read('validation/wave-native-runtime-audit.json')
export = read('validation/wave-export-validation.json')
navigation = read('validation/wave-navigation-result.json')
regression = read('validation/wave-runtime-regression.json')
assert export['status'] == navigation['status'] == 'PASS'
assert all(x['changed_pixels'] == 0 and x['gl_error'] == 0 for x in regression['results'])
assert sha('runtime/shaders/scene.frag') == regression['shader_sha256']
assert sha('runtime/build/dream.exe') == regression['binary_sha256']
assert sha('blender/wave_corridor.blend') == native['sha256']
for path, expected in export['sha256'].items():
    assert sha(path) == expected, path
references = {}
for path, item in plan['artifact_registry'].items():
    if path.startswith('dream/referencias/'):
        actual = hashlib.sha256((REPO/path).read_bytes()).hexdigest()
        assert actual == item['sha256'], f'Reference changed: {path}'
        references[path] = actual

captures = ['validation/wave-reference-14s.png',
            'validation/wave-blender-runtime-v8.png', 'validation/wave-opengl-v9.png']
labels = ['VIDEO 14 s', 'BLENDER / current prototype', 'OPENGL / current prototype']
sheet = Image.new('RGB', (478*3, 884), '#19191b')
draw = ImageDraw.Draw(sheet)
for i,(path,label) in enumerate(zip(captures,labels)):
    image = Image.open(ROOT/path).convert('RGB')
    assert image.size == (478,850)
    sheet.paste(image, (478*i,34));draw.text((478*i+10,10),label,fill='white')
sheet.save(ROOT/'validation/wave-runtime-comparison.png')

remaining = [
    'The source hall is bright and open; the current dark grid is unresolved geometry.',
    'Nonuniform stair heights and door thresholds still disagree across source views.',
    'Far-floor ribbon placement, widths and optical softness remain approximate.',
    'OpenGL has emitter reflections, but no architectural reflections or equivalent local shadows yet.',
    'OpenGL floor brightness and wall shading still differ from the current Blender render and the source.',
    'Sign proportions/glow, fittings and trim cross section remain approximate.',
    'Animated source-camera trajectory is not reconstructed; free walking is functional only.'
]
artifacts = [
    'blender/wave_corridor.blend', 'blender/prepare_wave_runtime.py', 'blender/export_runtime.py',
    'blender/wave_corridor_details.py', 'blender/pack_wave_runtime_maps.py',
    'assets/wave_corridor.dreammesh', 'assets/wave_corridor.glb', 'assets/wave_corridor.json',
    'assets/wave_corridor.scene', 'assets/wave_corridor.draws', 'assets/scene_catalog.cat',
    'runtime/src/main.cpp', 'runtime/src/scene.hpp', 'runtime/src/scene_catalog.hpp',
    'runtime/src/render_support.hpp', 'runtime/shaders/scene.frag',
    'validation/wave-export-validation.json', 'validation/wave-navigation-result.json',
    'validation/wave-native-runtime-audit.json', 'validation/wave-runtime-textures.json',
    'validation/wave-runtime-regression.json', 'validation/wave-cycle-smoke.log',
    'validation/wave-navigation.cpp', 'validation/verify_wave_runtime.py',
    'validation/wave-runtime-comparison.png', *captures]
artifacts += [str(p.relative_to(ROOT)).replace('\\','/') for p in (ROOT/'assets/textures').glob('wave_*.bmp')]
artifacts += [str(p.relative_to(ROOT)).replace('\\','/') for p in (ROOT/'assets/textures/wave_candidate').glob('*') if p.suffix in ('.png','.bmp')]
report = {
    'schema':'dream.wave_runtime_integration.v1', 'recorded_at_utc':now,
    'status':'functional_prototype_verified_fidelity_pending', 'runtime_available':True,
    'strict_fidelity_accepted':False, 'goal_complete':False,
    'native':{'scene_objects':native['scene_objects'],'mesh_objects':native['mesh_objects'],
              'packed_images':len(native['images']),'scenes_in_saved_file':native['native_inventory']['scenes']},
    'export':{'triangles':24960,'vertices':74880,'materials':10,'embedded_glb_images':9,
              'single_scene_native':True,'different_material_uv_sets_verified':True},
    'navigation':navigation,
    'camera':{'position_forward_up_and_fov_match_export':True,
              'basis_max_error':export['camera_basis_max_error'],
              'trajectory_reconstructed':False},
    'render':{'capture':'validation/wave-opengl-v9.png','framebuffer_px':[478,850],
              'frames':8,'time':0,'samples':4,'gl_error':0,'gpu':'Intel HD Graphics 630',
              'shader_sha256':regression['shader_sha256'],
              'binary_sha256':regression['binary_sha256'],
              'floor_specular':'Finite emitter disk approximation filtered by roughness and pixel footprint at each tread height. No architectural reflections or local visibility/shadow solution.',
              'visual_review':'Source, current native render and OpenGL capture inspected; differences remain.'},
    'regression':regression['results'],
    'cycle_smoke':{'frames':481,'sequence':['wave_corridor','atrium','wave_corridor'],
                   'gl_error':0,'mouse_and_resize_exercised':True},
    'inferred_geometry':['Unseen entrance back wall closes the area behind spawn; not claimed as a source detail.'],
    'references_verified_unchanged':references,'remaining':remaining,
    'sha256':{path:sha(path) for path in dict.fromkeys(artifacts)}
}
write('validation/wave-runtime-integration.json',report)
plan['historical_inventory_snapshots'].append({'recorded_before_runtime_integration':now,'inventory':plan['inventory'].copy()})
plan['inventory'].update(implemented_prototypes=5,not_implemented=8,blender_only_prototypes=0,
    counting_rule='Five available runtime prototypes, eight without runtime. No strict visual acceptance is implied.')
wave = next(x for x in plan['scenes'] if x['scene_id']=='video-42/pasillo_ondulado')
wave.update(status='implemented_prototype_reference_fidelity_pending',runtime_implemented=True,runtime_alias='wave_corridor')
wave['target_deliverables'].update(asset_stem='wave_corridor',runtime_mesh='dream/assets/wave_corridor.dreammesh',
    runtime_metadata='dream/assets/wave_corridor.scene',interchange='dream/assets/wave_corridor.glb',
    scene_resource_profile='wave_corridor / environment 4',navigation='17 rectangular supports, 12 risers and 2 column capsules; production controller tests passed')
wave['existing_artifacts_verified'] = list(dict.fromkeys(wave['existing_artifacts_verified']+['dream/'+p for p in artifacts]))
wave['native_progress'].update(scene_objects=76,mesh_objects=62,detail_meshes=13,
    review='dream/validation/wave-runtime-integration.json',runtime_mapping='Explicit material kinds 13-16, metric floor UV and front-only sign UV; seven local lights.')
wave['runtime_validation'] = 'dream/validation/wave-runtime-integration.json'
wave['remaining'] = remaining
snapshot = plan['current_runtime_snapshot']
snapshot['recorded_at_utc'] = now
snapshot['catalog_sha256'] = sha('assets/scene_catalog.cat')
snapshot['profiles']['wave_corridor'] = 4
snapshot['available'] = ['stair_sky','pastel_room','kitchen_meadow','wave_corridor','atrium']
snapshot['cpu_validation'] = '--validate-scenes PASS for all five profiles; wave export/nav checks passed.'
snapshot['gpu_validation'] = 'Wave capture and 481-frame scene cycle passed. Four previous scene captures are pixel-identical.'
snapshot['report'] = 'dream/validation/wave-runtime-integration.json'
plan['completion_gate']['global_completion'] = 'false until all 13 environments have strict reference acceptance; five working prototypes do not complete the four videos.'
plan['updated_at_utc'] = now
write('validation/all-scenes-plan.json',plan)

status['expanded_scope'].update(implemented_prototypes=5,without_runtime_implementation=8,
    implemented_runtime_scenes=['pastel_room','atrium','kitchen_meadow','stair_sky','wave_corridor'],
    inventory_sha256=sha('validation/all-scenes-plan.json'))
status['current_runtime_inventory'].update(available_prototypes=5,planned_without_runtime=8,
    profiles=snapshot['profiles'],verified_at_utc=now,
    validation='Wave export, supported navigation, actual GL capture and scene cycle verified; prior four captures pixel-identical.',
    historical_evidence_policy='Historical reports retain their source versions and timestamps; wave-runtime-integration.json describes the current fifth runtime prototype.')
status['wave_progress'].update(stage=wave['status'],review='validation/wave-runtime-integration.json',
    scene_objects=76,mesh_objects=62,runtime_available=True,remaining=remaining)
status['current_validation_reports']['wave_runtime'] = 'validation/wave-runtime-integration.json'
for row in status['requirement_review']:
    if row['id']==2:
        row['limitation']='Five scenes with explicit profiles. Supported stairs use rectangular surfaces; continuous ramps and moving platforms remain unimplemented. No fullscreen FPS guarantee.'
    if row['id']==4:
        row['limitation']='13 distinct scenes / 20 temporal entries: five runtime prototypes, eight without runtime and zero strict fidelity acceptances. All-scene construction and reference validation remain incomplete.'
for path in ['validation/all-scenes-plan.json','assets/scene_catalog.cat','validation/wave-runtime-integration.json']:
    status['current_report_hashes'][path] = sha(path)
status['wave_runtime_reconciliation'] = {'recorded_at_utc':now,'report':'validation/wave-runtime-integration.json','references_modified':False}
write('validation/status.json',status)
print(json.dumps({'recorded':report['status'],'available':5,'without_runtime':8,'strictly_accepted':0,'reference_files_verified':len(references)}))
