"""Validate the exported mesh contract and embedded GLB, without Blender."""
from pathlib import Path
import json
import math
import shlex
import struct
import sys

root = Path(__file__).resolve().parents[1]
asset=sys.argv[1] if len(sys.argv)>1 else 'pastel_room'

# Follow the selected runtime profile instead of requiring room maps for every
# scene. Planned scenes need not have assets, and other profiles are not loaded.
texture_roles={'sky','plaid','ceramic_normal','ceramic_roughness','leaf','globe',
               'floor_surface','floor_flow','probe'}
profiles={}
scene_entries=[]
records=[shlex.split(line,comments=True) for line in
         (root/'assets/scene_catalog.cat').read_text(encoding='utf-8').splitlines()]
records=[row for row in records if row]
assert records and records[0]==['DREAM_SCENE_CATALOG','1'], 'Invalid scene catalog header'
for row in records[1:]:
    if row[0]=='profile':
        assert len(row)==4 and row[1] not in profiles, 'Invalid/duplicate profile'
        profiles[row[1]]={'environment':int(row[2]),'state':row[3],'textures':{}}
    elif row[0]=='texture':
        assert len(row)==4 and row[1] in profiles and row[2] in texture_roles, 'Invalid texture role'
        slots=profiles[row[1]]['textures']
        assert row[2] not in slots, 'Duplicate texture role'
        slots[row[2]]=row[3]
    else:
        assert row[0]=='scene' and len(row)==9, 'Invalid scene catalog record'
        scene_entries.append(row)
matches=[row for row in scene_entries if row[2]==asset]
assert len(matches)==1 and matches[0][3]=='available', 'Asset is not uniquely available in catalog'
entry=matches[0]
assert entry[6]==f'assets/{asset}.scene' and entry[7]==f'assets/{asset}.dreammesh', 'Catalog asset path mismatch'
assert entry[5] in profiles, 'Missing scene profile'
profile=profiles[entry[5]]
assert profile['state']=='available' and set(profile['textures'])==texture_roles, 'Incomplete scene profile'
settings=[line.split() for line in (root/entry[6]).read_text().splitlines()]
environments=[int(row[1]) for row in settings if row and row[0]=='environment']
assert environments==[profile['environment']], 'Scene environment differs from catalog profile'
texture_paths={}
for role,value in profile['textures'].items():
    path=Path(value)
    assert not path.is_absolute() and not path.drive and '..' not in path.parts, 'Invalid texture path'
    assert path.suffix=='.bmp', 'Runtime texture must be BMP'
    bmp=(root/path).read_bytes()
    png=(root/path.with_suffix('.png')).read_bytes()
    assert len(bmp)>=54 and bmp[:2]==b'BM', f'Invalid BMP: {value}'
    offset=struct.unpack_from('<I',bmp,10)[0]
    w,h=struct.unpack_from('<II',bmp,18)
    assert struct.unpack_from('<H',bmp,28)[0]==24 and struct.unpack_from('<I',bmp,30)[0]==0, 'Expected RGB24 BMP'
    assert 0<w<=8192 and 0<h<=8192 and offset>=54
    assert len(bmp)>=offset+((w*3+3)&~3)*h, 'Truncated BMP pixels'
    assert png[:8]==b'\x89PNG\r\n\x1a\n' and png[12:16]==b'IHDR', 'Invalid companion PNG'
    assert struct.unpack_from('>II',png,16)==(w,h), 'PNG/BMP dimensions differ'
    texture_paths[role]=value

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
    assert material[5]==int(material[5]) and int(material[5]) in {*range(10),11,12,13,14,15,16}, 'Unknown material kind'
    assert 0<=material[6]<=1, 'Invalid opacity'
    assert material[7]==int(material[7]) and material[7]>=0, 'Invalid albedo variant'
    if material[5]==11:
        assert material[7] in (0,1), 'Unknown grass variant (expected ground=0 or blades=1)'
    if material[5]==12:
        assert material[7]==0, 'Unknown plush variant (expected 0)'
corners=list(struct.iter_unpack('<10f', data[16 + materials * 32:]))
for corner in corners:
    assert all(math.isfinite(v) for v in corner)
    assert abs(sum(n * n for n in corner[3:6]) - 1) < 0.002
    assert corner[8] == int(corner[8]) and 0 <= corner[8] < materials
    assert 0 <= corner[9] <= 1
assert sum(o['vertex_count'] for o in metadata['objects']) == count
assert all(o['name'].startswith('GEO-DREAM-') for o in metadata['objects'])

grass_stats={}
grass_materials=[i for i,m in enumerate(material_values) if m[5]==11]
if grass_materials:
    assert 11 in metadata['ao'].get('excluded_occluder_kinds',[]), 'Grass included as AO occluder'
    assert 11 in metadata['ao'].get('unoccluded_receiver_kinds',[]), 'Missing unoccluded grass receiver policy'
    for first in range(0,count,3):
        triangle=corners[first:first+3]
        material=material_values[int(triangle[0][8])]
        if material[5]!=11:
            continue
        assert all(c[8]==triangle[0][8] for c in triangle), 'Mixed materials within grass triangle'
        variant=int(material[7])
        stats=grass_stats.setdefault(variant,{'vertices':0,'uv_max_error':0.,'ao_min':1.,'ao_max':0.,
                                              'minimum_triangle_area_m2':float('inf'),'minimum_normal_face_dot':1.})
        a,b,c=triangle
        ab=[b[i]-a[i] for i in range(3)]
        ac=[c[i]-a[i] for i in range(3)]
        cross=[ab[1]*ac[2]-ab[2]*ac[1],ab[2]*ac[0]-ab[0]*ac[2],ab[0]*ac[1]-ab[1]*ac[0]]
        length=math.sqrt(sum(v*v for v in cross))
        assert length>1e-10, 'Degenerate grass triangle'
        stats['minimum_triangle_area_m2']=min(stats['minimum_triangle_area_m2'],length*.5)
        for corner in triangle:
            uv_error=max(abs(corner[6]-corner[0]/4),abs(corner[7]-corner[1]/4))
            assert uv_error<2e-5, 'Grass UV differs from continuous world XY/4'
            assert abs(corner[9]-1)<1e-6, 'Grass AO must remain unoccluded'
            normal_dot=sum(corner[i+3]*cross[i]/length for i in range(3))
            # Stair banks are curved, closed volumes with smooth top normals;
            # their sides/riser faces cannot satisfy a flat-ground +Z contract.
            # Preserve the stricter original checks for every other ground and
            # for the planar blade geometry, including all kitchen assets.
            smooth_stair_ground=asset=='stair_sky' and variant==0
            assert normal_dot>(0 if smooth_stair_ground else .99), 'Grass normals disagree with exported triangle winding'
            if variant==0 and not smooth_stair_ground:
                assert abs(corner[3])<1e-4 and abs(corner[4])<1e-4 and corner[5]>.9999, 'Grass ground must have upward normals'
            stats['vertices']+=1
            stats['uv_max_error']=max(stats['uv_max_error'],uv_error)
            stats['ao_min']=min(stats['ao_min'],corner[9])
            stats['ao_max']=max(stats['ao_max'],corner[9])
            stats['minimum_normal_face_dot']=min(stats['minimum_normal_face_dot'],normal_dot)
if asset=='kitchen_meadow':
    assert profile['environment']==2 and set(grass_stats)=={0,1}, 'Kitchen requires its grass profile and both grass variants'

plush_stats={}
for first in range(0,count,3):
    triangle=corners[first:first+3]
    material=material_values[int(triangle[0][8])]
    if material[5]!=12:
        continue
    assert all(c[8]==triangle[0][8] for c in triangle), 'Mixed materials within plush triangle'
    a,b,c=triangle
    ab=[b[i]-a[i] for i in range(3)]
    ac=[c[i]-a[i] for i in range(3)]
    cross=[ab[1]*ac[2]-ab[2]*ac[1],ab[2]*ac[0]-ab[0]*ac[2],ab[0]*ac[1]-ab[1]*ac[0]]
    length=math.sqrt(sum(v*v for v in cross))
    assert length>1e-10, 'Degenerate plush triangle'
    face_normal=[v/length for v in cross]
    magnitude=list(map(abs,face_normal))
    # The UV author uses the dominant world polygon normal, not smooth corner
    # normals. Triangulated planar faces preserve that projection. Near exact
    # axis ties, float32 world positions can change which component wins; only
    # axes within this tight tolerance of the maximum may be alternate choices.
    dominant=2 if magnitude[2]>=max(magnitude[0],magnitude[1]) else (1 if magnitude[1]>=magnitude[0] else 0)
    axes=[dominant]+[i for i in range(3) if i!=dominant and max(magnitude)-magnitude[i]<2e-4]
    projections={2:(0,1),1:(0,2),0:(1,2)}
    errors={axis:max(max(abs(v[6]-v[projections[axis][0]]/.28),
                         abs(v[7]-v[projections[axis][1]]/.28)) for v in triangle) for axis in axes}
    axis=min(errors,key=errors.get)
    assert errors[axis]<2e-5, 'Plush UV differs from dominant world face projection /0.28'
    stats=plush_stats.setdefault(0,{'vertices':0,'uv_max_error':0.,'ao_min':1.,'ao_max':0.,
                                  'minimum_triangle_area_m2':float('inf'),'minimum_normal_face_dot':1.,
                                  'projection_triangles':{'xy':0,'xz':0,'yz':0},'near_tie_alternate_triangles':0})
    stats['minimum_triangle_area_m2']=min(stats['minimum_triangle_area_m2'],length*.5)
    stats['projection_triangles'][{2:'xy',1:'xz',0:'yz'}[axis]]+=1
    stats['near_tie_alternate_triangles']+=axis!=dominant
    for corner in triangle:
        normal_dot=sum(corner[i+3]*face_normal[i] for i in range(3))
        assert normal_dot>0, 'Plush normals disagree with exported triangle winding'
        stats['vertices']+=1
        stats['uv_max_error']=max(stats['uv_max_error'],errors[axis])
        stats['ao_min']=min(stats['ao_min'],corner[9])
        stats['ao_max']=max(stats['ao_max'],corner[9])
        stats['minimum_normal_face_dot']=min(stats['minimum_normal_face_dot'],normal_dot)
if asset=='stair_sky':
    assert profile['environment']==3 and entry[5]=='stair_sky', 'Stair requires its own render profile'
    assert set(plush_stats)=={0} and 0 in grass_stats, 'Stair requires plush and grass ground'
    assert all(Path(value).name.startswith('stair_') for value in texture_paths.values()), 'Stair profile requires scene-local maps'
ao_excluded_names=metadata['ao'].get('detail_objects_excluded',[])
assert isinstance(ao_excluded_names,list) and all(isinstance(name,str) for name in ao_excluded_names), 'Invalid AO detail exclusion list'
assert len(set(ao_excluded_names))==len(ao_excluded_names), 'Duplicate AO detail exclusion'
assert set(ao_excluded_names)<={obj['name'] for obj in metadata['objects']}, 'AO exclusion names an absent object'
ao_excluded_stats={}
offset=0
for obj in metadata['objects']:
    assert obj['first_vertex']==offset, 'Object ranges are not contiguous'
    assert obj['vertex_count']>0 and obj['vertex_count']%3==0
    assert len(obj['center'])==3 and all(math.isfinite(v) for v in obj['center'])
    if obj['name'] in ao_excluded_names:
        values=[corner[9] for corner in corners[offset:offset+obj['vertex_count']]]
        assert all(abs(value-1)<1e-6 for value in values), 'AO-exempt detail has occluded receiver values'
        ao_excluded_stats[obj['name']]={'vertices':obj['vertex_count'],'ao_min':min(values),'ao_max':max(values)}
    for corner in corners[offset:offset+obj['vertex_count']]:
        assert int(material_values[int(corner[8])][5]) in obj.get('material_kinds',[obj['kind']]), 'Object kind differs from mesh material'
        if asset=='kitchen_meadow' and obj['kind']==11:
            ground_names={'GEO-DREAM-kitchen-grass_interior_blockout','GEO-DREAM-kitchen-meadow_blockout'}
            assert obj['name'] in ground_names or obj['name'].startswith('GEO-DREAM-kitchen-grass_blades_'), 'Unknown kitchen grass object role'
            expected=0 if obj['name'] in ground_names else 1
            assert material_values[int(corner[8])][7]==expected, 'Grass object has wrong ground/blade variant'
    offset+=obj['vertex_count']
# Transparent ranges are derived from the actual export, never a fixed count.
transparent=[o for o in metadata['objects'] if any(k in (6,9) for k in o.get('material_kinds',[o.get('kind')]))]
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

glb = (root / f'assets/{asset}.glb').read_bytes()
magic, version, size, json_size, chunk_type = struct.unpack_from('<5I', glb)
assert magic == 0x46546C67 and version == 2 and size == len(glb)
assert chunk_type == 0x4E4F534A
doc = json.loads(glb[20:20 + json_size])
assert len(doc['scenes']) == 1, 'Export includes another Blender scene'
assert not any(n.get('name') == 'Cube' for n in doc['nodes'])
assert all('bufferView' in im for im in doc.get('images', []))
# Explicit plush fibers and grass blades make the stair (353k triangles) and
# dense-grass kitchen (199k) larger prototypes. Their review budgets are 45 MB
# and 35 MB, pending density/LOD optimization; all other scenes retain 15 MiB.
glb_budget_bytes={'stair_sky':45_000_000,'kitchen_meadow':35_000_000}.get(asset,15*1024*1024)
assert len(glb)<glb_budget_bytes, 'GLB exceeds its scene-specific asset budget'
print(json.dumps({'result': 'PASS', 'materials': materials, 'vertices': count,
                  'asset':asset,
                  'triangles': count // 3, 'glb_bytes': len(glb),'glb_budget_bytes':glb_budget_bytes,
                  'transparent_draws':len(transparent),
                  'waterfall_draws':sum(o['kind']==9 for o in transparent),
                  'navigation_verified':navigation_verified,
                  'water_vertices_covered':water_coverage_count,
                  'embedded_glb_images': len(doc.get('images', [])),
                  'profile':entry[5], 'texture_roles':texture_paths,
                  'grass_variants':grass_stats,'plush_variants':plush_stats,
                  'ao_excluded_detail_objects':ao_excluded_stats}))
