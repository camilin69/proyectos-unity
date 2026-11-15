"""Check wave-specific exported camera, UVs, support geometry and map channels."""
from pathlib import Path
import hashlib
import json
import math
import struct
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
meta = json.loads((ROOT/'assets/wave_corridor.json').read_text(encoding='utf-8'))
plan = json.loads((ROOT/'blender/wave_corridor_plan.json').read_text(encoding='utf-8'))
data = (ROOT/'assets/wave_corridor.dreammesh').read_bytes()
material_count, count = struct.unpack_from('<II', data, 8)
materials = np.frombuffer(data, '<f4', material_count*8, 16).reshape(-1, 8)
corners = np.frombuffer(data, '<f4', count*10, 16+material_count*32).reshape(-1, 10)
kinds = materials[corners[:, 8].astype(int), 5].astype(int)
config = {}
for line in (ROOT/'assets/wave_corridor.scene').read_text().splitlines():
    row = line.split()
    config.setdefault(row[0], []).append(list(map(float, row[1:])))
assert config['environment'] == [[4]] and len(config['light']) == 7
floor = corners[kinds == 13].astype(float)
expected_uv = np.column_stack((floor[:, 0], floor[:, 1]-plan['constructor']['corridor']['start_y_m']-floor[:, 2]))
uv_error = float(np.abs(floor[:, 6:8]-expected_uv).max())
assert uv_error < 3e-6, 'Paint discontinuity over a tread, riser or hall seam'
sign = corners[kinds == 16]
assert len(sign) == 12 and np.all(sign[:, 6:8] >= -1e-6) and np.all(sign[:, 6:8] <= 1+1e-6)
sign_objects = [o for o in meta['objects'] if 16 in o['material_kinds']]
assert len(sign_objects) == 2 and all(o['material_kinds'] == [0, 16] for o in sign_objects)

# Check the support footprint against real upward-facing exported triangles,
# not just another copy of the navigation settings.
triangles = corners.reshape(-1, 3, 10)
top = triangles[(kinds.reshape(-1, 3) == 13).all(axis=1) & (triangles[:, :, 5] > .999).all(axis=1)]
samples = 0
for x0, y0, x1, y1, z in config['surface']:
    for x in (x0+.01, (x0+x1)/2, x1-.01):
        for y in (y0+.01, (y0+y1)/2, y1-.01):
            covered = False
            for triangle in top:
                if np.max(np.abs(triangle[:, 2]-z)) > 2e-6:
                    continue
                a, b, c = triangle[:, :2].astype(float)
                matrix = np.column_stack((b-a, c-a))
                if abs(np.linalg.det(matrix)) < 1e-12:
                    continue
                u, v = np.linalg.solve(matrix, np.array([x, y])-a)
                if u >= -1e-6 and v >= -1e-6 and u+v <= 1+1e-6:
                    covered = True
                    break
            assert covered, f'Support extends beyond rendered floor: {x,y,z}'
            samples += 1

pose = config['camera'][0]
yaw, pitch = pose[3:]
roll = config['camera_roll'][0][0]
forward = np.array([math.cos(yaw)*math.cos(pitch), math.sin(yaw)*math.cos(pitch), math.sin(pitch)])
right = np.cross(forward, [0, 0, 1]); right /= np.linalg.norm(right)
up = np.cross(right, forward)*math.cos(roll)-right*math.sin(roll)
camera_error = float(max(np.max(np.abs(forward-meta['camera']['forward'])),
                         np.max(np.abs(up-meta['camera']['up'])),
                         np.max(np.abs(np.array(pose[:3])-meta['camera']['position']))))
assert camera_error < 1e-6, 'Runtime basis differs from Blender quaternion camera'
assert abs(math.degrees(2*math.atan(config['fov'][0][0]))-meta['camera']['vertical_fov_degrees']) < 1e-5

textures = ROOT/'assets/textures'
packed = np.asarray(Image.open(textures/'wave_surface_data.png'))
for channel, name in enumerate(('wall_roughness', 'ceiling_roughness')):
    original = np.asarray(Image.open(textures/f'wave_candidate/wave_{name}.png'))
    assert np.array_equal(packed[:, :, channel], original[:, :, 0]), f'Lost {name} channel'
assert np.array_equal(packed, np.asarray(Image.open(textures/'wave_surface_data.bmp')))
source_map = Image.open(textures/'wave_candidate/wave_exit_emission_dark.png').convert('RGB').resize((512,512), Image.Resampling.BILINEAR)
assert np.array_equal(packed[:, :, 2], np.asarray(source_map)[:, :, 0]), 'Lost sign emission mask'

glb = (ROOT/'assets/wave_corridor.glb').read_bytes()
gltf = json.loads(glb[20:20+struct.unpack_from('<I', glb, 12)[0]])
for mesh in gltf['meshes']:
    for primitive in mesh['primitives']:
        material = gltf['materials'][primitive['material']]
        def verify_texture_sets(value):
            if isinstance(value, dict):
                for key, child in value.items():
                    if key.endswith('Texture') and isinstance(child, dict):
                        assert f"TEXCOORD_{child.get('texCoord', 0)}" in primitive['attributes'], 'GLB texture uses absent UV set'
                    verify_texture_sets(child)
        verify_texture_sets(material)

paths = ['assets/wave_corridor.dreammesh', 'assets/wave_corridor.scene', 'assets/wave_corridor.json',
         'assets/wave_corridor.glb', 'assets/textures/wave_surface_data.png']
report = {'status':'PASS', 'floor_metric_uv_max_error':uv_error, 'painted_floor_corners':len(floor),
          'sign_front_corners':len(sign), 'support_geometry_samples':samples,
          'camera_basis_max_error':camera_error, 'packed_data_channels':'wall roughness / ceiling roughness / sign emission',
          'glb_texture_uv_sets_present':True, 'strict_fidelity_accepted':False,
          'sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}}
(ROOT/'validation/wave-export-validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report))
