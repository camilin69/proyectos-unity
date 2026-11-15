"""Export evaluated Blender geometry and material parameters to the C++ viewer.

DREAMM02: 8-byte magic, uint32 material count, uint32 vertex count;
materials: 8 float32 (linear RGB, roughness, metallic, shader kind, opacity,
albedo_variant; 0=default, legacy 1=mint, 2=continuous pastel floor);
vertices: 10 float32 (world XYZ, world normal XYZ, UV, material index, AO).
Little-endian, triangles, Z-up metres. GLB is also exported for interoperability.
"""
import bpy, json, struct, math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]
scene=bpy.context.scene
asset=scene.get('dream_asset','pastel_room')
scene.view_layers[0].material_override=None
deps=bpy.context.evaluated_depsgraph_get()
objects=[o for o in scene.objects if o.type=='MESH' and o.name.startswith('GEO-DREAM-')]
materials={m.name:m for o in objects for m in o.data.materials}
ordered=sorted(materials.values(),key=lambda m:m['dream_id'])
ids={m.name:i for i,m in enumerate(ordered)}
vertices=[];ranges=[];skip_ao=[]
for obj in objects:
    eo=obj.evaluated_get(deps);mesh=eo.to_mesh();mesh.calc_loop_triangles()
    normalmat=eo.matrix_world.to_3x3().inverted().transposed()
    uv=mesh.uv_layers.active
    start=len(vertices)//9
    for tri in mesh.loop_triangles:
        mat=ids[mesh.materials[tri.material_index].name]
        for li in tri.loops:
            vi=mesh.loops[li].vertex_index
            p=eo.matrix_world@mesh.vertices[vi].co
            n=(normalmat@mesh.corner_normals[li].vector).normalized()
            # Runtime texture coordinates can differ from Blender's active
            # layer when a material combines metric tiling and decal UVs.
            runtime_uv=ordered[mat].get('runtime_uv_layer')
            layer=mesh.uv_layers.get(runtime_uv) if runtime_uv else uv
            if runtime_uv and layer is None:
                raise ValueError(f'{obj.name}: missing runtime UV layer {runtime_uv}')
            tex=layer.data[li].uv if layer else (0,0)
            vertices.extend((*p,*n,*tex,float(mat)))
    center=obj.matrix_world@Vector((0,0,0))
    if len(mesh.vertices):center=sum((obj.matrix_world@v.co for v in mesh.vertices),Vector())/len(mesh.vertices)
    # Evaluated material proxies need not expose custom ID properties.
    kinds=sorted({int(ordered[ids[m.name]]['kind']) for m in mesh.materials})
    ranges.append({'name':obj.name,'first_vertex':start,'vertex_count':len(vertices)//9-start,'kind':int(obj.data.materials[0]['kind']),'material_kinds':kinds,'center':list(center)})
    skip_ao.extend([bool(obj.get('dream_skip_ao',False))]*(len(vertices)//9-start))
    eo.to_mesh_clear()
# Bake local geometric occlusion into corners. Cache repeated corners rather
# than casting the same rays for both triangles of every quad.
positions=[Vector(vertices[i:i+3]) for i in range(0,len(vertices),9)]
bvh=BVHTree.FromPolygons(positions,[(i,i+1,i+2) for i in range(0,len(positions),3) if not skip_ao[i] and ordered[int(vertices[i*9+8])]['kind'] not in (4,6,9,11)],all_triangles=True)
cache={};baked=[]
for i in range(0,len(vertices),9):
    p=Vector(vertices[i:i+3]);n=Vector(vertices[i+3:i+6]);key=tuple(round(v,4) for v in (*p,*n))
    if skip_ao[i//9] or ordered[int(vertices[i+8])]['kind']==11:
        # Grass uses its own diffuse/transmission model. Baking each tiny blade
        # as an opaque AO occluder produces black spikes and huge bake costs.
        cache[key]=1.0
    elif key not in cache:
        tangent=n.cross(Vector((0,0,1)) if abs(n.z)<.9 else Vector((0,1,0))).normalized()
        bitangent=n.cross(tangent);occ=0
        for j in range(8):
            a=j*2.39996323;r=math.sqrt((j+.5)/8)*.85
            d=(tangent*(r*math.cos(a))+bitangent*(r*math.sin(a))+n*math.sqrt(1-r*r)).normalized()
            hit,_,_,distance=bvh.ray_cast(p+n*.012,d,.65)
            if hit is not None:occ+=max(0,1-distance/.65)
        cache[key]=max(.35,1-occ/8*.8)
    baked.extend(vertices[i:i+9]);baked.append(cache[key])
out=ROOT/f'assets/{asset}.dreammesh'
with out.open('wb') as f:
    f.write(b'DREAMM02');f.write(struct.pack('<II',len(ordered),len(vertices)//9))
    for mat in ordered:
        p=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
        f.write(struct.pack('<8f',*p.inputs['Base Color'].default_value[:3],mat['roughness'],mat['metallic'],mat['kind'],mat.get('opacity',0),mat.get('albedo_variant',0)))
    f.write(struct.pack('<%df'%len(baked),*baked))
frame=scene.camera.data.view_frame(scene=scene)
tan_half_fov=max(abs(v.y/v.z) for v in frame)
camera_rotation=scene.camera.matrix_world.to_quaternion()
meta={'format':'DREAMM02','axes':'Z-up, right handed, metres','materials':[m.name for m in ordered],'vertices':len(vertices)//9,'triangles':len(vertices)//27,'objects':ranges,'camera':{'position':list(scene.camera.matrix_world.translation),'vertical_fov_degrees':math.degrees(2*math.atan(tan_half_fov)),'forward':list(camera_rotation@Vector((0,0,-1))),'up':list(camera_rotation@Vector((0,1,0)))},'source':f'blender/{asset}.blend','ao':{'method':'8 cosine hemisphere rays, 0.65 m radius','minimum':min(cache.values()),'corners':len(cache)}}
meta['ao']['excluded_occluder_kinds']=[4,6,9,11]
meta['ao']['unoccluded_receiver_kinds']=[11]
meta['ao']['detail_objects_excluded']=[o.name for o in objects if o.get('dream_skip_ao',False)]
if 'dream_navigation' in scene:
    nav=json.loads(scene['dream_navigation'])
    meta['navigation']=nav
(ROOT/f'assets/{asset}.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
(ROOT/f'assets/{asset}.draws').write_text('\n'.join(f"{r['first_vertex']} {r['vertex_count']} "+' '.join(str(v) for v in r['center']) for r in ranges if any(k in (6,9) for k in r['material_kinds']))+'\n',encoding='utf-8')
if asset=='atrium':
    config=['camera 3.5 -3.7 1.85 2.06 0.1','fov 0.82','reflection 0.055','environment 1','boundary '+' '.join(map(str,nav['boundary']))]
    config+=['disc '+' '.join(map(str,d)) for d in nav['discs']]
    config+=['capsule '+' '.join(map(str,c)) for c in nav.get('capsules',[])]
    (ROOT/'assets/atrium.scene').write_text('\n'.join(config)+'\n',encoding='utf-8')
elif 'dream_runtime_config' in scene:
    # Additional scenes own an explicit configuration; never inherit the room
    # or atrium profile merely because their asset ID is different.
    config=json.loads(scene['dream_runtime_config'])
    if not isinstance(config,list) or not all(isinstance(line,str) for line in config):
        raise ValueError('dream_runtime_config must contain scene setting lines')
    (ROOT/f'assets/{asset}.scene').write_text('\n'.join(config)+'\n',encoding='utf-8')
bpy.ops.object.select_all(action='DESELECT')
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=objects[0]
bpy.ops.export_scene.gltf(filepath=str(ROOT/f'assets/{asset}.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_apply=True,export_animations=False)
for mat in ordered:
    for node in mat.node_tree.nodes:
        if node.type=='TEX_IMAGE' and node.image and not node.image.packed_file:
            node.image.pack()
# Save the selected source scene and its dependencies, excluding unrelated
# live scenes and inspection cameras. Do not change the user's current file.
bpy.data.libraries.write(str(ROOT/f'blender/{asset}.blend'),{scene},path_remap='RELATIVE_ALL',fake_user=True,compress=True)
print(json.dumps({'mesh_bytes':out.stat().st_size,'triangles':len(vertices)//27,'glb_bytes':(ROOT/f'assets/{asset}.glb').stat().st_size}))
