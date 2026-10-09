"""Validate the exported mesh contract and embedded GLB, without Blender."""
from pathlib import Path
import json
import math
import struct

root = Path(__file__).resolve().parents[1]
metadata = json.loads((root / 'assets/pastel_room.json').read_text(encoding='utf-8'))
data = (root / 'assets/pastel_room.dreammesh').read_bytes()
assert data[:8] == b'DREAMM02'
materials, count = struct.unpack_from('<II', data, 8)
assert 0 < materials <= 32 and count % 3 == 0
assert len(data) == 16 + materials * 32 + count * 40
assert len(metadata['materials']) == materials
assert metadata['vertices'] == count
assert metadata['triangles'] * 3 == count
for corner in struct.iter_unpack('<10f', data[16 + materials * 32:]):
    assert all(math.isfinite(v) for v in corner)
    assert abs(sum(n * n for n in corner[3:6]) - 1) < 0.002
    assert corner[8] == int(corner[8]) and 0 <= corner[8] < materials
    assert 0 <= corner[9] <= 1
assert sum(o['vertex_count'] for o in metadata['objects']) == count
assert all(o['name'].startswith('GEO-DREAM-') for o in metadata['objects'])

glb = (root / 'assets/pastel_room.glb').read_bytes()
magic, version, size, json_size, chunk_type = struct.unpack_from('<5I', glb)
assert magic == 0x46546C67 and version == 2 and size == len(glb)
assert chunk_type == 0x4E4F534A
doc = json.loads(glb[20:20 + json_size])
assert len(doc['scenes']) == 1, 'Export includes another Blender scene'
assert not any(n.get('name') == 'Cube' for n in doc['nodes'])
assert all('bufferView' in im for im in doc.get('images', []))
assert len(glb) < 15 * 1024 * 1024
for texture in ['cloud_sky', 'curtain_plaid', 'ceramic_normal', 'ceramic_roughness']:
    assert (root / f'assets/textures/{texture}.png').is_file()
    assert (root / f'assets/textures/{texture}.bmp').is_file()
print(json.dumps({'result': 'PASS', 'materials': materials, 'vertices': count,
                  'triangles': count // 3, 'glb_bytes': len(glb),
                  'embedded_glb_images': len(doc.get('images', []))}))
