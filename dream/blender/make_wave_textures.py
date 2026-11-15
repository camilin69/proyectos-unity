"""Create isolated, reference-informed wave-corridor material candidates.

Pure Python/NumPy/Pillow: no bpy, scene edits, renders, or active asset binding.
The video is evidence for appearance, not recovered PBR data. The painted
waves affect colour only; actual stair height stays in the geometric profile.
Run with the local Blender skill Python runtime, not Blender itself.
"""
from pathlib import Path
import hashlib
import json
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'dream/assets/textures/wave_candidate'
EVIDENCE = ROOT / 'dream/validation/wave-material-source'
PLAN = ROOT / 'dream/blender/wave_material_plan.json'
FLOOR_SIZE = 1024
GRAIN_SIZE = 512
FLOOR_METRES = (6.6, 5.5)
GRAIN_METRES = .5
SEED = 420014
PALETTE = {
    'teal': [110, 161, 158],
    'lavender': [147, 145, 184],
    'pink': [208, 150, 165],
    'coral': [217, 133, 119],
    'ochre': [213, 181, 120],
    'wall': [215, 163, 160],
    'ceiling': [109, 159, 163],
    'door': [220, 214, 192],
    'rail': [28, 35, 35],
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rel(path):
    return Path(path).relative_to(ROOT).as_posix()


def noise(rng, size, sigma):
    result = gaussian_filter(rng.standard_normal((size, size)), sigma, mode='wrap')
    return np.clip(result / max(float(result.std()), 1e-10), -3, 3) / 3


def seam(array):
    """The duplicated endpoint texels also protect linear-filtered tile edges."""
    result = array.copy()
    result[-1] = result[0]
    result[:, -1] = result[:, 0]
    return result


def smoothstep(lo, hi, value):
    t = np.clip((value - lo) / (hi - lo), 0, 1)
    return t * t * (3 - 2 * t)


def normal_from_height(height, width_m):
    spacing = width_m / height.shape[0]
    dx = (np.roll(height, -1, 1) - np.roll(height, 1, 1)) / (2 * spacing)
    dy_row = (np.roll(height, -1, 0) - np.roll(height, 1, 0)) / (2 * spacing)
    # OpenGL tangent +Y: raster rows run downward, opposite to texture V.
    normal = np.stack((-dx, dy_row, np.ones_like(height)), axis=-1)
    normal /= np.linalg.norm(normal, axis=-1, keepdims=True)
    return np.rint((normal * .5 + .5) * 255).clip(0, 255).astype('uint8')


def write_map(name, values, role, colour_space, period_m, tiled=True):
    array = np.asarray(values)
    if array.ndim == 2:
        array = np.repeat(array[..., None], 3, axis=2)
    array = np.rint(array).clip(0, 255).astype('uint8')
    if tiled:
        array = seam(array)
    im = Image.fromarray(array)
    png, bmp = OUT / (name + '.png'), OUT / (name + '.bmp')
    im.save(png)
    im.save(bmp)
    decoded = np.asarray(Image.open(bmp).convert(im.mode))
    assert np.array_equal(array, decoded), name + ': BMP/PNG pixel mismatch'
    record = {
        'name': name, 'role': role, 'colour_space': colour_space,
        'period_m': period_m, 'size_px': list(im.size),
        'png': {'path': rel(png), 'sha256': sha(png)},
        'bmp': {'path': rel(bmp), 'sha256': sha(bmp)},
        'pixel_ranges': [[int(array[..., i].min()), int(array[..., i].max())] for i in range(3)],
        'png_bmp_pixels_identical': True,
        'edge_texels_identical': bool(np.array_equal(array[0], array[-1]) and np.array_equal(array[:, 0], array[:, -1])) if tiled else None,
    }
    if role == 'normal':
        n = array.astype(float) / 255 * 2 - 1
        lengths = np.linalg.norm(n, axis=-1)
        assert np.isfinite(n).all() and .98 < lengths.min() <= lengths.max() < 1.02
        assert n[..., 2].min() > .90
        record['decoded_vector_length_range'] = [float(lengths.min()), float(lengths.max())]
        record['rms_tangent_slope'] = float(np.sqrt(np.mean(np.sum((n[..., :2] / n[..., 2, None]) ** 2, axis=-1))))
    return record


def make_floor(rng):
    # Coordinates here describe a whole physical tile, never screen pixels.
    u = np.linspace(-FLOOR_METRES[0] / 2, FLOOR_METRES[0] / 2, FLOOR_SIZE)
    s = np.linspace(FLOOR_METRES[1], 0, FLOOR_SIZE)
    x, distance = np.meshgrid(u, s)
    phase = 2 * math.pi * distance / FLOOR_METRES[1]
    centre = 1.26 * np.sin(phase + .35) + .20 * np.sin(2 * phase - .75)
    # Slightly changing ribbon width avoids mechanically equidistant stripes.
    width = 1 + .14 * np.sin(phase - .5) + .05 * np.cos(2 * phase)
    q = (x - centre) / width
    colours = np.broadcast_to(np.array(PALETTE['teal'], dtype=float), (FLOOR_SIZE, FLOOR_SIZE, 3)).copy()
    # Broad painted ribbons; the centre line may leave the 2.2m corridor but
    # remains continuous across its stairs and the wider destination hall.
    bands = [(-1.04, -.82, 'ochre'), (-.82, -.51, 'pink'),
             (-.51, -.18, 'coral'), (-.18, .22, 'ochre'), (.22, .67, 'lavender')]
    for lo, hi, key in bands:
        mask = smoothstep(lo - .010, lo + .010, q) * (1 - smoothstep(hi - .010, hi + .010, q))
        colours = colours * (1 - mask[..., None]) + np.array(PALETTE[key]) * mask[..., None]
    colour_noise = 1.15 * noise(rng, FLOOR_SIZE, 3) + .65 * noise(rng, FLOOR_SIZE, 19)
    colours += colour_noise[..., None]
    roughness = .19 + .024 * noise(rng, FLOOR_SIZE, 5) + .015 * noise(rng, FLOOR_SIZE, 26)
    return [
        write_map('wave_floor_albedo', colours, 'albedo', 'sRGB', FLOOR_METRES),
        write_map('wave_floor_roughness', roughness * 255, 'roughness', 'Non-Color', FLOOR_METRES),
    ]


def make_grain(rng):
    fine, medium = noise(rng, GRAIN_SIZE, .65), noise(rng, GRAIN_SIZE, 2.8)
    broad = noise(rng, GRAIN_SIZE, 12)
    floor_height = .00004 * fine + .00022 * medium + .00006 * broad
    paint_height = .00012 * fine + .00017 * medium + .000055 * broad
    floor_normal = normal_from_height(floor_height, GRAIN_METRES)
    paint_normal = normal_from_height(paint_height, GRAIN_METRES)
    result = [
        write_map('wave_floor_normal', floor_normal, 'normal', 'Non-Color', [GRAIN_METRES] * 2),
        write_map('wave_paint_normal', paint_normal, 'normal', 'Non-Color', [GRAIN_METRES] * 2),
    ]
    for key, rough, modulation in [('wall', .57, .055), ('ceiling', .79, .065)]:
        albedo = np.array(PALETTE[key])[None, None, :] + (1.7 * fine + 1.1 * medium + .8 * broad)[..., None]
        result += [
            write_map('wave_' + key + '_albedo', albedo, 'albedo', 'sRGB', [GRAIN_METRES] * 2),
            write_map('wave_' + key + '_roughness', (rough + modulation * medium + .014 * fine) * 255, 'roughness', 'Non-Color', [GRAIN_METRES] * 2),
        ]
    return result


def make_sign(style='candidate'):
    # Type and text are a candidate inferred from the small red plaques, not
    # OCR. No adjacent-scene EXIT HERE phrase or watermark is copied here.
    font_path = Path('C:/Windows/Fonts/arialbd.ttf')
    font = ImageFont.truetype(str(font_path), 77)
    if style not in ('candidate', 'dark'):
        raise ValueError('Unknown sign finish')
    im = Image.new('RGB', (256, 128), (232, 221, 205) if style == 'candidate' else (57, 43, 40))
    draw = ImageDraw.Draw(im)
    draw.rounded_rectangle((5, 5, 250, 122), radius=7,
                           outline=(186, 176, 163) if style == 'candidate' else (72, 48, 43), width=3)
    box = draw.textbbox((0, 0), 'EXIT', font=font)
    origin = ((256 - (box[2] - box[0])) / 2 - box[0], (128 - (box[3] - box[1])) / 2 - box[1])
    draw.text(origin, 'EXIT', font=font, fill=(197, 38, 33))
    rgb = np.array(im)
    # Separate emission mask; leave final intensity for the lighting pass.
    mask = ((rgb[..., 0] > rgb[..., 1] * 2) & (rgb[..., 0] > rgb[..., 2] * 2)).astype('uint8') * 255
    return [write_map('wave_exit_albedo_'+style, rgb, 'albedo', 'sRGB', None, tiled=False),
            write_map('wave_exit_emission_'+style, mask, 'emission_mask', 'Non-Color', None, tiled=False)], {
                'font': str(font_path), 'font_sha256': sha(font_path),
                'text': 'EXIT', 'text_confidence': 'medium; red plaque visible, native letters blurred',
                'active': False, 'geometry_placement': 'Pending source/geometry gate; never place on whole wall UV.',
            }


def make_contact():
    canvas = Image.new('RGB', (1320, 1090), (30, 31, 34))
    draw = ImageDraw.Draw(canvas)
    reference = Image.open(EVIDENCE / '14s.png').convert('RGB')
    canvas.paste(reference, (14, 40))
    draw.text((14, 14), 'ORIGINAL 14s / 478x850 / evidence only', fill='white')
    floor = Image.open(OUT / 'wave_floor_albedo.png')
    floor.thumbnail((780, 650))
    canvas.paste(floor, (516, 40))
    draw.text((516, 14), 'OWN MAP: 6.6 x 5.5m / colour only / UV fit pending', fill='white')
    for index, name in enumerate(['wave_floor_normal', 'wave_floor_roughness', 'wave_wall_albedo', 'wave_ceiling_albedo', 'wave_paint_normal']):
        swatch = Image.open(OUT / (name + '.png')).resize((142, 142))
        x = 516 + index * 157
        canvas.paste(swatch, (x, 717))
        draw.text((x, 867), name.replace('wave_', ''), fill='white')
    sign = Image.open(OUT / 'wave_exit_albedo_candidate.png')
    canvas.paste(sign, (516, 926))
    draw.text((794, 930), 'Sign candidate ONLY: text inferred.', fill='white')
    draw.text((794, 954), 'No source pixels in generated maps.', fill='white')
    draw.text((794, 978), 'Normal/rugosity/scale are artistic seeds.', fill='white')
    draw.text((14, 933), 'No scene assignment or final UV validation.', fill='white')
    draw.text((14, 957), 'Gloss and lamp reflections must come from 3D.', fill='white')
    path = EVIDENCE / 'material-contact.png'
    canvas.save(path)
    return {'path': rel(path), 'sha256': sha(path), 'purpose': 'Evidence/map juxtaposition, not a material render or fidelity comparison.'}


def make_plan(records, sign, contact):
    source_manifest = json.loads((EVIDENCE / 'provenance.json').read_text(encoding='utf8'))
    region_path = EVIDENCE / 'observed-regions.json'
    source_analysis = ROOT / 'dream/referencias/estetica/video-42.json'
    geometry_plan = ROOT / 'dream/blender/wave_corridor_plan.json'
    return {
        'schema_version': 1, 'asset_id': 'wave_corridor', 'canonical_scene_id': 'video-42/pasillo_ondulado',
        'stage': 'isolated_procedural_material_candidates_not_applied', 'accepted': False,
        'source_analysis': {'path': rel(source_analysis), 'sha256': sha(source_analysis)},
        'geometry_plan_read_only': {'path': rel(geometry_plan), 'sha256_at_preparation': sha(geometry_plan)},
        'source_evidence': source_manifest,
        'observed_regions': {'path': rel(region_path), 'sha256': sha(region_path), 'usage': 'Rendered/compressed sRGB values, not physical albedo or direct targets under arbitrary lighting.'},
        'provenance': {
            'generator': rel(Path(__file__)), 'generator_sha256': sha(__file__), 'seed': SEED,
            'source_pixels_used_in_maps': False, 'physical_materials_recovered': False,
            'notes': 'Own analytic colour bands and seeded noise. Scale, roughness, height, IOR and palette are editable artistic guesses from appearance. Original frames/crops remain evidence only.',
        },
        'observations': [
            {'part': 'floor', 'observed': 'Broad coral, pink, ochre, lavender and teal curves continue across landings and straight treads. Luminaires reflect as broken white highlights, strongest near camera.', 'confidence': 'high', 'inferred': 'Coated painted solid; no water animation, no wave-shaped displacement. Exact ribbon phase/scale and coating chemistry unknown.'},
            {'part': 'walls_ceiling', 'observed': 'Warm pink walls with subtle grain; teal ceiling has stronger orange-peel-like texture around fixtures. Large light/shadow gradients are visible.', 'confidence': 'high', 'inferred': 'Fine procedural relief, weaker on wall; gradients belong in lighting, not albedo.'},
            {'part': 'rails', 'observed': 'Near-black tubular rail with a narrow bright rim; brackets are dark.', 'confidence': 'high', 'inferred': 'Black painted/coated metal surface, dielectric topcoat. Do not make the whole tube mirror-bright raw chrome.'},
            {'part': 'doors_signs', 'observed': 'Cream door leaves and thick reveals, small warm utility indicators, red high-level plaques.', 'confidence': 'high for colours/forms, medium for EXIT lettering', 'inferred': 'EXIT candidate only; no EXIT HERE text imported from preceding ocean scene. No invented labels on utility plates.'},
            {'part': 'rear_hall', 'observed': 'Pastel floor continues toward a dark gridded rear boundary with repeated bright lights.', 'confidence': 'medium', 'inferred': 'Opening/mirror and rear material unresolved; no reference screenshot or painted reflection supplied.'},
        ],
        'palette_srgb_artistic_seed_255': PALETTE,
        'maps': records, 'contact': contact,
        'materials': {
            'floor': {'objects': ['continuous_stepped_floor', 'hall_floor'], 'base_color_map': 'wave_floor_albedo', 'roughness_map': 'wave_floor_roughness', 'normal_map': 'wave_floor_normal', 'normal_strength': 1, 'metallic': 0, 'ior': 1.47, 'coat_weight': .55, 'coat_roughness': .13, 'transmission': 0, 'displacement': 0, 'animated': False},
            'wall': {'objects': ['right_wall', 'left_wall_*', 'hall_side_*', 'hall_back_wall'], 'base_color_map': 'wave_wall_albedo', 'roughness_map': 'wave_wall_roughness', 'normal_map': 'wave_paint_normal', 'normal_strength': .50, 'metallic': 0, 'ior': 1.47},
            'ceiling': {'objects': ['ceiling', 'hall_ceiling'], 'base_color_map': 'wave_ceiling_albedo', 'roughness_map': 'wave_ceiling_roughness', 'normal_map': 'wave_paint_normal', 'normal_strength': 1, 'metallic': 0, 'ior': 1.47},
            'door_trim': {'objects': ['door_*_leaf', 'door_*_reveal', 'hall_column_*'], 'base_color_srgb_255': PALETTE['door'], 'roughness': .35, 'metallic': 0, 'coat_weight': .15, 'ior': 1.47},
            'rail': {'objects': ['handrail_*', 'rail_bracket_*'], 'base_color_srgb_255': PALETTE['rail'], 'roughness': .27, 'metallic': 0, 'coat_weight': .55, 'coat_roughness': .18, 'ior': 1.5, 'note': 'Black coating over metal; narrow reflected rim must be light/environment-driven.'},
            'diffuser': {'objects': ['ceiling_fixture_* except bases'], 'base_color_srgb_255': [255, 245, 232], 'roughness': .30, 'metallic': 0, 'emission_seed': 2, 'note': 'Luminous object plus separate actual lamp illumination; do not bake white blobs into floor. Emission/intensity is uncalibrated.'},
            'exit_sign_candidate': sign,
            'utility_plates': {'base_color_srgb_255': [218, 211, 196], 'roughness': .40, 'metallic': 0, 'text': None, 'geometry_state': 'Not supplied; place only after geometry gate.'},
            'rear_panel': {'state': 'unresolved', 'instruction': 'Keep diagnostic until source confirms opening, glazing or mirror. No fake image-plane material.'},
        },
        'uv_contract_pending_geometry_gate': {
            'state': 'not_applied_not_checker_validated', 'units': 'metres',
            'floor_source_uv': '(x, s), where s is accumulated YZ arclength from corridor start, including every riser; existing ContinuousMetres layer.',
            'floor_colour_and_roughness_uv': '(x / 6.6 + 0.5, s / 5.5 + phase); phase starts at 0 and remains adjustable after registered render.',
            'floor_grain_uv': '(x / 0.5, s / 0.5); preserve across each tread/riser, not one tile per step.',
            'hall': 'Current hall cube UV is NOT ready. Reproject floor top as (worldX, corridorArcEnd + worldY - corridorEndY) before normalization. Recompute corridorArcEnd from final accepted profile; do not hardcode.',
            'wall': 'Metric YZ projection with a shared world origin for all split wall pieces; 0.5m tile. Check reveals/edges separately.',
            'ceiling': 'Metric XY projection with shared world origin; 0.5m tile.',
            'sign': 'Own front-face 0..1 UV; side/back use cream material; separate emissive letter mask. No full-wall atlas mapping.',
            'coverage': 'Floor end/underside/side caps currently have a different UV convention. Explicitly assign matching coating or neutral hidden solid after closed-surface inspection, never stretch top pattern blindly over caps.',
            'normal_convention': 'Tangent OpenGL +Y; PNG top row is highest V. Unit-scale normal, no color conversion. Keep grain in a second UV set or preserve metre coordinates for shader sampling. Do not silently sample it using the large albedo period.',
            'runtime_contract': 'No environment/kind/profile assigned here. Root owns shader/export integration. Require separate spatial frequencies for large paint and fine normal, mipmaps and sRGB albedo decoding. Roughness/normal are Non-Color.',
        },
        'next_gates': [
            'Accept gray camera/real tread geometry and confirmed left door count before any map assignment.',
            'Apply metre-based UV transforms consistently to corridor and hall; render a checker in front/oblique views including risers and reveals.',
            'Calibrate palette and lamp-driven floor reflections at 14s, then inspect 12.5/15.5/17s; do not compensate for geometry with painted shadows.',
            'Keep bright lamps, soft pink wall falloff and fine ceiling relief; evaluate floor roughness under real interior reflection probes.',
            'Validate matching exported map roles, colour spaces and scale in OpenGL; motion should come from camera/parallax, not animated painted waves.',
        ],
        'execution': {'bpy_imported': False, 'blender_applied': False, 'rendered': False, 'runtime_bound': False, 'uv_fit_validated': False, 'source_intact_checked': True, 'map_checks': 'PNG/BMP pixel equality; periodic texel seams; finite near-unit normals; deterministic seeded source.'},
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    # Never proceed against a changed video without explicitly revisiting provenance.
    evidence = json.loads((EVIDENCE / 'provenance.json').read_text(encoding='utf8'))
    assert sha(ROOT / evidence['source']) == evidence['source_sha256']
    for frame in evidence['frames']:
        assert sha(ROOT / frame['path']) == frame['sha256']
    rng = np.random.default_rng(SEED)
    records = make_floor(rng) + make_grain(rng)
    signs, sign_info = make_sign()
    records += signs
    contact = make_contact()
    plan = make_plan(records, sign_info, contact)
    PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    manifest = {'schema_version': 1, 'stage': plan['stage'], 'accepted': False,
                'material_plan': {'path': rel(PLAN), 'sha256': sha(PLAN)}, 'maps': records}
    (OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf8')
    print(json.dumps({'maps': len(records), 'plan': rel(PLAN), 'contact': contact['path'],
                      'accepted': False, 'applied': False, 'seed': SEED}, indent=2))


if __name__ == '__main__':
    main()
