"""Validate the exported mesh contract and embedded GLB, without Blender."""
from pathlib import Path
import json
import math
import struct
import sys

root = Path(__file__).resolve().parents[1]
asset=sys.argv[1] if len(sys.argv)>1 else 'pastel_room'
metadata = json.loads((root / f'assets/{asset}.json').read_text(encoding='utf-8'))
data = (root / f'assets/{asset}.dreammesh').read_bytes()
assert data[:8] == b'DREAMM02'
materials, count = struct.unpack_from('<II', data, 8)
assert 0 < materials <= 32 and count % 3 == 0
assert len(data) == 16 + materials * 32 + count * 40
assert len(metadata['materials']) == materials
assert metadata['vertices'] == count
assert metadata['triangles'] * 3 == count
material_values=list(struct.iter_unpack('<8f',data[16:16+materials*32]))
for material in material_values:
    assert all(math.isfinite(v) for v in material)
    assert all(0<=v<=1 for v in material[:5]), 'Invalid base color, roughness or metallic'
    assert material[5]==int(material[5]) and 0<=material[5]<=9, 'Unknown material kind'
    assert 0<=material[6]<=1, 'Invalid opacity'
    assert material[7]==int(material[7]) and material[7]>=0, 'Invalid albedo variant'
corners=list(struct.iter_unpack('<10f', data[16 + materials * 32:]))
for corner in corners:
    assert all(math.isfinite(v) for v in corner)
    assert abs(sum(n * n for n in corner[3:6]) - 1) < 0.002
    assert corner[8] == int(corner[8]) and 0 <= corner[8] < materials
    assert 0 <= corner[9] <= 1
assert sum(o['vertex_count'] for o in metadata['objects']) == count
assert all(o['name'].startswith('GEO-DREAM-') for o in metadata['objects'])
offset=0
for obj in metadata['objects']:
    assert obj['first_vertex']==offset, 'Object ranges are not contiguous'
    assert obj['vertex_count']>0 and obj['vertex_count']%3==0
    assert len(obj['center'])==3 and all(math.isfinite(v) for v in obj['center'])
    for corner in corners[offset:offset+obj['vertex_count']]:
        assert int(material_values[int(corner[8])][5])==obj['kind'], 'Object kind differs from mesh material'
    offset+=obj['vertex_count']
# Transparent ranges are derived from the actual export, never a fixed count.
transparent=[o for o in metadata['objects'] if o.get('kind') in (6,9)]
draws=[line for line in (root/f'assets/{asset}.draws').read_text().splitlines() if line.strip()]
assert len(draws)==len(transparent), 'Missing or extra transparent draw ranges'
for line,obj in zip(draws,transparent):
    values=line.split()
    assert len(values)==5
    assert int(values[0])==obj['first_vertex'] and int(values[1])==obj['vertex_count']
    assert all(math.isfinite(float(v)) for v in values)
    assert all(math.isclose(float(v),c,abs_tol=1e-5) for v,c in zip(values[2:],obj['center']))

navigation_verified=False
water_coverage_count=0
if asset=='atrium':
    nav=metadata.get('navigation')
    if nav is not None:
        config={'boundary':[],'disc':[],'capsule':[]}
        for line in (root/'assets/atrium.scene').read_text().splitlines():
            values=line.split()
            if values and values[0] in config:
                numbers=list(map(float,values[1:]))
                assert all(math.isfinite(v) for v in numbers)
                assert len(numbers)==(5 if values[0]=='capsule' else 3)
                assert numbers[-1]>0
                config[values[0]].append(numbers)
        assert config['boundary']==[nav['boundary']]
        assert config['disc']==nav['discs']
        assert config['capsule']==nav.get('capsules',[])
        def blocked(x,y):
            if any((x-dx)**2+(y-dy)**2<=r*r+1e-6 for dx,dy,r in nav['discs']):return True
            for ax,ay,bx,by,r in nav.get('capsules',[]):
                dx,dy=bx-ax,by-ay;length=dx*dx+dy*dy
                t=max(0,min(1,((x-ax)*dx+(y-ay)*dy)/length)) if length else 0
                if (x-ax-t*dx)**2+(y-ay-t*dy)**2<=r*r+1e-6:return True
            return False
        for corner in corners:
            if int(material_values[int(corner[8])][5])==4:
                assert blocked(corner[0],corner[1]), 'Water surface has no navigation obstacle'
                water_coverage_count+=1
        navigation_verified=True
    if any(o['kind']==9 for o in metadata['objects']):
        assert navigation_verified and nav.get('capsules'), 'Waterfall/canal export lacks navigation provenance'
        assert 9 in metadata['ao']['excluded_occluder_kinds'], 'Waterfall incorrectly included as AO occluder'
    for texture in ['leaf_detail','biosphere']:
        assert (root/f'assets/textures/{texture}.png').is_file()
        assert (root/f'assets/textures/{texture}.bmp').is_file()

glb = (root / f'assets/{asset}.glb').read_bytes()
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
                  'asset':asset,
                  'triangles': count // 3, 'glb_bytes': len(glb),
                  'transparent_draws':len(transparent),
                  'waterfall_draws':sum(o['kind']==9 for o in transparent),
                  'navigation_verified':navigation_verified,
                  'water_vertices_covered':water_coverage_count,
                  'embedded_glb_images': len(doc.get('images', []))}))
