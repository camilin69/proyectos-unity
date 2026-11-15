"""Record actual motion evidence without rewriting the initial study's reports."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,ast,subprocess
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'validation/ocean-exit-motion'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,obj):p.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
previous=read(ROOT/'validation/ocean-exit/review.json')
for path,expected in previous['reference_files_preserved'].items():assert sha(ROOT.parent/path)==expected,path
for path,expected in previous['prior_runtime_and_wave_assets_preserved'].items():assert sha(ROOT/path)==expected,path
assert sha(ROOT/'blender/ocean_exit.blend')==previous['sha256']['blender/ocean_exit.blend']
native=read(OUT/'final-native-audit.json')
initial=read(ROOT/'validation/ocean-exit/native-audit.json')
assert sorted(native['packed_images'].values())==sorted(initial['packed_images'].values())
scripts=['blender/animate_ocean_exit.py','blender/render_ocean_motion_preview.py','blender/audit_ocean_exit_motion.py',
         'validation/fit_ocean_post_multiview.py','validation/fit_ocean_camera_post_joint.py','validation/fit_ocean_submerged_post.py',
         'validation/record_ocean_exit_motion.py']
for p in scripts:ast.parse((ROOT/p).read_text(encoding='utf8'),filename=p)
video=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries',
    'stream=width,height,nb_frames,avg_frame_rate,duration','-of','json',str(OUT/'water-preview.mp4')],text=True))['streams'][0]
assert video['nb_frames']=='24' and video['avg_frame_rate']=='10/1'
decisions={
 'post-multiview-fit.json':'rejected: assuming the visible post end is at water z=0 leaves a 151.6 px endpoint error in the reserved view.',
 'camera-post-joint-fit.json':'not_applied: variable effective FOV can fit endpoints but does not independently verify lens/zoom and conflicts with the foreground-border progression.',
 'submerged-post-fit.json':'applied_to_separate_motion_candidate: post geometry now stays in final view, but submerged visible length still differs. All three endpoint observations used for fit; no held-out claim.'}
for filename,decision in decisions.items():
    path=ROOT/'validation/ocean-exit'/filename;data=read(path);data['decision']=decision;write(path,data)
remaining=[
 'Post is visible at 11.5s, but the visible submerged length, bent head and width still differ from the source. Refraction was not included in the geometric fit.',
 'Foam is too smooth and uniform; it does not yet reproduce turbulent fronts, breakup around borders, or the source motion.',
 'Exterior ocean waves repeat in regular bands; the source has irregular multi-scale waves.',
 'Magenta reflection distribution, surface detail, tile gloss, sky streaks, horizon silhouette, service door and small wall fixtures remain unmatched.',
 'Fixed-lens door fits still have 3.58px RMS at 9s and 5.74px at 11.5s; source labels and camera model need further refinement.',
 'OpenGL ocean profile, shifted projection, animated shader/wave equivalence, navigation and collisions are not implemented.'
]
artifacts=scripts+['blender/ocean_exit_water.blend']
artifacts += [p.relative_to(ROOT).as_posix() for p in OUT.rglob('*') if p.is_file() and p.name!='review.json']
artifacts += ['validation/ocean-exit/'+p for p in decisions]
diff=read(OUT/'frame-differences.json')
report={'schema':'dream.ocean_exit_motion_review.v1','recorded_at_utc':datetime.now(timezone.utc).isoformat(),
 'previous_goal_turn_classification':'progress: initial native ocean scene, eight packed maps and two-view comparison created and verified.',
 'status':'blender_animated_prototype_fidelity_pending','accepted':False,'runtime_promoted':False,'goal_complete':False,
 'native':'blender/ocean_exit_water.blend','previous_native_preserved':'blender/ocean_exit.blend',
 'preview':{'path':'validation/ocean-exit-motion/water-preview.mp4','metadata':video,
            'render':'24 Cycles frames, 16 samples, 239x425; MP4 padded to 240x426; 10fps diagnostic preview, not final-quality motion.',
            'contact_sheet':'validation/ocean-exit-motion/contact-sheet.png',
            'max_adjacent_mean_rgb_difference_0_255':max(r['mean_rgb_diff'] for r in diff['frame_diff'])},
 'visual_review':{'contact_sheet_inspected':True,'three_view_comparison_inspected':True,
                 'comparison':'validation/ocean-exit-motion/comparison.png','remaining':remaining},
 'motion_checks':{'evaluated_frames':[1,16,31,61,91,136,181],'four_wave_shape_keys_per_water_mesh':True,
                 'wave_displacement_6s_loop':True,'foam_uv_advection':True,'foam_seamless_loop':False,
                 'max_threshold_gap_m':max(r['max_threshold_seam_error_m'] for r in native['samples'].values()),
                 'limitation':'Continuity and geometry checks do not prove fluid realism or fidelity; material animation requires separate runtime implementation.'},
 'animation_quality_gate':{'subject_and_architecture_stability':'pass in inspected frames',
                          'large_frame_jumps':'none in 24-frame preview',
                          'texture_motion':'continuous translation, but foam formation/dissipation absent',
                          'motion_design':'needs irregularity and source-speed calibration',
                          'source_fidelity':'not accepted','runtime_export_equivalence':'not implemented'},
 'diagnostics':decisions,
 'eevee_note':'Raytraced transmission and explicit thin-surface Thickness were tested. Cycles produces the current comparison/preview. No parity between both renderers claimed.',
 'technical_reference':'https://developer.blender.org/docs/release_notes/4.2/eevee_migration/',
 'preservation':{'original_reference_files':len(previous['reference_files_preserved']),
                 'prior_runtime_and_wave_assets':len(previous['prior_runtime_and_wave_assets_preserved']),
                 'original_ocean_native_sha256':sha(ROOT/'blender/ocean_exit.blend'),'packed_map_payloads_identical':8},
 'python_parse_pass':scripts,'sha256':{p:sha(ROOT/p) for p in sorted(set(artifacts))},
 'next_action':'Develop irregular, depth-aware foam breakup and ocean wave directions, retain the post/camera diagnostic, then implement an explicit ocean OpenGL profile with matching motion and camera shift.'}
write(OUT/'review.json',report)
planpath=ROOT/'validation/all-scenes-plan.json';plan=read(planpath)
entry=next(e for e in plan['scenes'] if e['scene_id']=='video-42/salida_oceano')
entry['status']=report['status'];entry['strict_acceptance']=False
entry['native_prototype']={'file':'dream/blender/ocean_exit_water.blend','report':'dream/validation/ocean-exit-motion/review.json',
 'comparison':'dream/validation/ocean-exit-motion/comparison.png','preview':'dream/validation/ocean-exit-motion/water-preview.mp4',
 'initial_native_preserved':'dream/blender/ocean_exit.blend','initial_report':'dream/validation/ocean-exit/review.json',
 'runtime_available':False,'remaining':remaining}
plan['updated_at_utc']=report['recorded_at_utc'];write(planpath,plan)
statuspath=ROOT/'validation/status.json';status=read(statuspath)
status['ocean_exit_progress']={'status':report['status'],'native':report['native'],'report':'validation/ocean-exit-motion/review.json',
 'comparison':report['visual_review']['comparison'],'preview':report['preview']['path'],
 'initial_report':'validation/ocean-exit/review.json','runtime_promoted':False,'accepted':False,'remaining':remaining}
status['expanded_scope']['inventory_sha256']=sha(planpath)
for path in ['validation/all-scenes-plan.json','validation/ocean-exit-motion/review.json']:
    status['current_report_hashes'][path]=sha(ROOT/path)
write(statuspath,status)
print(json.dumps({'artifacts_hashed':len(report['sha256']),'preservation':report['preservation'],
                  'max_frame_difference':report['preview']['max_adjacent_mean_rgb_difference_0_255'],
                  'runtime_prototypes':5,'blender_only_scenes':1,'accepted_scenes':0}))
