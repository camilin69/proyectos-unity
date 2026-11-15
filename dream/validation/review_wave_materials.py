"""Record actual saved Blender comparisons; no acceptance from fit scores."""
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT/'validation'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact(relative):
    path = ROOT/relative
    return {'path': 'dream/'+relative, 'bytes': path.stat().st_size, 'sha256': sha(path)}


def comparison(files, labels, target):
    canvas = Image.new('RGB', (478*len(files), 884), (25, 25, 29))
    draw = ImageDraw.Draw(canvas)
    for i, (file, label) in enumerate(zip(files, labels)):
        with Image.open(HERE/file) as im:
            assert im.size == (478, 850), (file, im.size)
            canvas.paste(im.convert('RGB'), (i*478, 34))
        draw.text((i*478+12, 10), label, fill='white')
    canvas.save(HERE/target)


comparison(['wave-reference-14s.png', 'wave-material-initial.png', 'wave-material-v5.png'],
           ['SOURCE 14s', 'INITIAL MATERIAL', 'CURRENT CANDIDATE - NOT FINAL'],
           'wave-material-comparison.png')
comparison(['wave-reference-15p5s.png', 'wave-material-v5-secondary.png'],
           ['SOURCE 15.5s', 'SECOND VIEW - NOT FINAL'], 'wave-secondary-comparison.png')

rois = {'right_wall': [350, 260, 410, 390], 'ceiling': [160, 35, 210, 70],
        'foreground_teal': [140, 760, 260, 825]}
stats = {}
for name in ['wave-reference-14s.png', 'wave-material-initial.png', 'wave-material-v2.png',
             'wave-material-v3.png', 'wave-material-v4.png', 'wave-material-v5.png']:
    pixels = np.array(Image.open(HERE/name).convert('RGB'))
    stats[name] = {role: np.median(pixels[y0:y1, x0:x1].reshape(-1, 3), axis=0).tolist()
                   for role, (x0, y0, x1, y1) in rois.items()}

plan = json.loads((ROOT/'blender/wave_corridor_plan.json').read_text(encoding='utf-8'))
source_hashes = dict(plan['reference_manifest']['preserved_source_sha256'])
source_hashes[plan['reference_manifest']['original']] = plan['reference_manifest']['original_sha256']
for path, expected in source_hashes.items():
    assert sha(ROOT.parent/path) == expected, 'Changed reference: '+path

coverage = json.loads((HERE/'wave-material-coverage.json').read_text())
audit = json.loads((HERE/'wave-native-audit.json').read_text())
assert not coverage['degenerate_uv_faces'] and coverage['floor_hall_max_uv_error_m'] == 0
assert audit['native_sha256'] == sha(ROOT/'blender/wave_corridor.blend')
report = {
    'schema': 'dream.wave_material_review.v1',
    'stage': 'blender_material_prototype_with_two_rendered_views',
    'accepted': False, 'geometry_fidelity_accepted': False, 'runtime_available': False,
    'primary_reference_time_s': 14, 'secondary_reference_time_s': 15.5,
    'native_audit': audit,
    'technical_checks': {
        'checker_render_inspected': True, 'full_closed_surface_uv_coverage': True,
        'floor_hall_uv_error_m': 0, 'eight_images_packed_in_single_scene_native': True,
        'source_files_unchanged': source_hashes,
        'repeat_apply_does_not_duplicate_objects_or_change_geometry_uvs': True,
        'scope': 'These checks prove storage and UV consistency, not reproduction fidelity.'},
    'observed_improvements': [
        'Paint uses continuous floor arclength across treads/risers and into the hall.',
        'Foreground paint placement fitted to 11 manually interpreted colour regions.',
        'Ceiling, wall and floor have separate colour, roughness and normal maps.',
        'Floor coat uses the normal map, breaking up the initial smooth highlights.',
        'Limited surface-region brightness comparison improved wall/floor balance.'],
    'material_calibration': {'roi_xyxy': rois, 'median_srgb_255': stats,
                             'scope': 'Three small same-camera regions; not whole-image fidelity or recovered albedo.'},
    'lighting': {'downward_areas_w': 40, 'point_bounce_w': 30,
                 'floor_entrance_return_w': 280, 'ceiling_return_w': 30,
                 'exposure_stops': -1.2, 'engine': 'BLENDER_EEVEE', 'samples': 64,
                 'raytracing': True,
                 'inference': 'Surface-linked floor/ceiling returns approximate missing indirect bounce; light positions/powers are authored.'},
    'history': {'initial': 'initial UV phase and gray-stage exposure',
                'v2': 'foreground paint registration, coat normals, entrance fill',
                'v3': 'wall/floor light balance; ceiling return was not linked into the scene',
                'v4': 'ceiling return membership repaired; 80 W too bright in sampled region',
                'v5': 'current 30 W ceiling return; both reference views rendered'},
    'remaining': [
        'Source hall is a brighter open space; current dark grid is unresolved geometry.',
        'Step distribution and door thresholds still disagree between the views.',
        'Far-floor ribbon pattern and width do not yet match the source.',
        'Floor reflection spread, roughness scale and compression/optical softness differ.',
        'Red exit plaques, utility plates and door details are missing.',
        'No C++/OpenGL profile, export, navigation verification or animated camera match yet.'],
    'next_action': 'Refine shared geometry and paint using both views, including the far hall and door bases, before treating the scene as a faithful reference match.',
    'artifacts': [artifact(p) for p in [
        'blender/wave_corridor.blend', 'blender/finish_wave_corridor.py',
        'validation/wave-gray-v2.blend', 'validation/wave-gray-v2.png',
        'validation/wave-gray-v2-secondary.png', 'validation/wave-uv-checker.png',
        'validation/wave-uv-coverage.json', 'validation/wave-material-coverage.json',
        'validation/wave-paint-fit.json', 'validation/wave-material-initial.png',
        'validation/wave-material-v2.png', 'validation/wave-material-v2-secondary.png',
        'validation/wave-material-v3.png', 'validation/wave-material-v4.png',
        'validation/wave-material-v5.png', 'validation/wave-material-v5-secondary.png',
        'validation/wave-material-comparison.png', 'validation/wave-secondary-comparison.png',
        'validation/wave-native-audit.json']]
}
(HERE/'wave-material-review.json').write_text(json.dumps(report, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
print(json.dumps({'native_bytes': audit['native_file_bytes'], 'images_packed': 8,
                  'objects': audit['scene_objects'], 'uv_check': 'PASS', 'strict_acceptance': False,
                  'region_medians_current': stats['wave-material-v5.png']}))
