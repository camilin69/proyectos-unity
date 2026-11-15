"""Record the initial native ocean study, preserving historical runtime evidence."""
from pathlib import Path
from datetime import datetime, timezone
import ast, hashlib, json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'validation/ocean-exit'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,obj):p.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

baseline=read(ROOT/'validation/wave-runtime-integration.json')
references={}
for path,expected in baseline['references_verified_unchanged'].items():
    current=sha(ROOT.parent/path)
    assert current==expected,path
    references[path]=current
preserved={}
for path,expected in baseline['sha256'].items():
    if path.startswith(('assets/','runtime/')) or path=='blender/wave_corridor.blend':
        current=sha(ROOT/path)
        assert current==expected,path
        preserved[path]=current

scripts=['blender/make_ocean_exit_maps.py','blender/build_ocean_exit.py','blender/refine_ocean_exit.py',
         'blender/make_ocean_sky_refinement.py','blender/finish_ocean_exit_study.py','validation/fit_ocean_exit_camera.py',
         'validation/record_ocean_exit_study.py']
for path in scripts:ast.parse((ROOT/path).read_text(encoding='utf8'),filename=path)
native=read(OUT/'native-audit.json');saved=read(OUT/'saved-file-audit.json')
assert saved['scenes_in_saved_file']==['DREAM_OceanExit']
assert len(saved['images'])==len(native['packed_images'])==8
for name,expected in native['packed_images'].items():
    assert sha(ROOT/'assets/textures/ocean_exit'/name.removeprefix('DREAM-ocean-'))==expected,name

remaining=[
    'Water is a static reconstructed surface: broad foam fronts, shoreline interaction, finer reflections and animation still differ.',
    'The post exits the second rendered frame but remains visible at the right edge of the source; revisit joint pose and post position.',
    'Secondary door fit is 5.74 px RMS and approximate horizon misses by 6.63 px with fixed primary lens/shift; this does not verify the camera model.',
    'Sky nebula/comet arrangement and distant horizon silhouette remain unmatched.',
    'Wall and cap material response, bright magenta jamb reflection, ceiling/EXIT sign proportions, service door and missing switches/access panels need work.',
    'No C++/OpenGL export, water animation, collision/navigation, or lens-shift runtime support has been implemented for this scene.'
]
artifacts=scripts+['blender/ocean_exit_plan.json','blender/ocean_exit.blend']
artifacts += [p.relative_to(ROOT).as_posix() for p in OUT.iterdir() if p.is_file() and p.name!='review.json']
artifacts += [p.relative_to(ROOT).as_posix() for p in (ROOT/'assets/textures/ocean_exit').iterdir() if p.is_file()]
report={
 'schema':'dream.ocean_exit_study.v1','recorded_at_utc':datetime.now(timezone.utc).isoformat(),
 'status':'blender_only_prototype_fidelity_pending','accepted':False,'runtime_promoted':False,'goal_complete':False,
 'previous_goal_turn_classification':'no_progress: feasibility explanation; this turn revalidated files and created the missing native ocean scene.',
 'native':{'file':'blender/ocean_exit.blend','objects':native['objects'],'closed_meshes':27,'open_water_surfaces':2,
           'packed_maps':8,'camera_views_s':[7,11.5],'saved_scene_names':saved['scenes_in_saved_file']},
 'visual_review':{'comparison':'validation/ocean-exit/comparison-v3.png','source_and_render_pairs_inspected':True,
                  'first_revision':'validation/ocean-exit/blender-7s-v1.png',
                  'improvements':['Foreground borders now visible and closer to source positions.','Post height reduced from visibly oversized first pass.','Clipped white water highlights reduced.','Smaller stars and narrower sunset band.'],
                  'remaining':remaining},
 'geometry_validation':'All 27 solid base meshes closed; 2 intentionally open water grids; no edge with >2 faces; all base-mesh UV faces have positive area. Does not certify visual fidelity or runtime navigation.',
 'texture_validation':'Eight used image byte payloads are packed and match the original generated PNGs. Source videos, frames and texture crops remain unchanged.',
 'reference_files_preserved':references,'prior_runtime_and_wave_assets_preserved':preserved,
 'python_parse_pass':scripts,
 'sha256':{p:sha(ROOT/p) for p in sorted(set(artifacts))},
 'next_action':'Jointly validate post/border/door landmarks across 7s, 9s and 11.5s; develop moving foam and water lighting, then add explicit ocean profile and shifted projection support in OpenGL.'}
write(OUT/'review.json',report)

planpath=ROOT/'validation/all-scenes-plan.json';plan=read(planpath)
plan['inventory']['blender_only_prototypes']=1
plan['inventory']['counting_rule']='Five available runtime prototypes, eight without runtime; one of those eight now has a Blender-only prototype. No strict visual acceptance is implied.'
entry=next(e for e in plan['scenes'] if e['scene_id']=='video-42/salida_oceano')
entry['status']='blender_only_prototype_fidelity_pending'
entry['strict_acceptance']=False
entry['native_prototype']={'file':'dream/blender/ocean_exit.blend','report':'dream/validation/ocean-exit/review.json',
                           'comparison':'dream/validation/ocean-exit/comparison-v3.png','runtime_available':False,
                           'remaining':remaining}
plan['updated_at_utc']=report['recorded_at_utc'];write(planpath,plan)

statuspath=ROOT/'validation/status.json';status=read(statuspath)
status['ocean_exit_progress']={'status':report['status'],'native':'blender/ocean_exit.blend',
 'report':'validation/ocean-exit/review.json','comparison':'validation/ocean-exit/comparison-v3.png',
 'runtime_promoted':False,'accepted':False,'remaining':remaining}
status['expanded_scope']['blender_only_prototypes']=1
status['expanded_scope']['inventory_sha256']=sha(planpath)
status['current_report_hashes']['validation/all-scenes-plan.json']=sha(planpath)
status['current_report_hashes']['validation/ocean-exit/review.json']=sha(OUT/'review.json')
status['goal_complete']=False;write(statuspath,status)
print(json.dumps({'new_native_prototype':'ocean_exit','source_files_preserved':len(references),
                  'prior_asset_hashes_preserved':len(preserved),'artifact_hashes':len(report['sha256']),
                  'runtime_prototypes':5,'blender_only_prototypes':1,'without_runtime':8,'accepted':0}))
