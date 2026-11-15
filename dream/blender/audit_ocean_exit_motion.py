"""Inspect actual evaluated animation and saved native resources in live Blender."""
from pathlib import Path
from collections import Counter
import json,hashlib,math
import bpy
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'validation/ocean-exit-motion'
s=bpy.data.scenes['DREAM_OceanExitWater']
def ob(part):return s.objects['GEO-DREAM-oceanwater-'+part]
meshes=[]
for obj in s.objects:
    if obj.type!='MESH':continue
    edges=Counter()
    for p in obj.data.polygons:
        v=list(p.vertices)
        for a,b in zip(v,v[1:]+v[:1]):edges[tuple(sorted((a,b)))]+=1
    water=obj in [ob('interior_water'),ob('ocean')]
    assert max(edges.values())==2
    if not water:assert min(edges.values())==2,obj.name
    assert all(math.isfinite(c) for v in obj.data.vertices for c in v.co)
    meshes.append({'name':obj.name,'vertices':len(obj.data.vertices),'closed':not water,'boundary_edges':sum(n==1 for n in edges.values())})
samples={}
for frame in [1,16,31,61,91,136,181]:
    s.frame_set(frame);deps=bpy.context.evaluated_depsgraph_get();rows={};seam={}
    for part in ['interior_water','ocean']:
        obj=ob(part);eo=obj.evaluated_get(deps);me=eo.to_mesh()
        zs=[v.co.z for v in me.vertices]
        seam[part]=sorted((float(v.co.x),float(v.co.z)) for v in me.vertices if abs(v.co.y-5.3)<1e-5)
        rows[part]={'min_z':min(zs),'max_z':max(zs),'sample_z':[zs[k] for k in [0,len(zs)//3,len(zs)//2,len(zs)-1]],
                    'valid_drivers':all(f.driver.is_valid for f in obj.data.shape_keys.animation_data.drivers)}
        eo.to_mesh_clear()
    # Interpolate the denser doorway samples against the ocean threshold row.
    errors=[];outer=seam['ocean']
    for x,z in seam['interior_water']:
        for (a,za),(b,zb) in zip(outer,outer[1:]):
            if a<=x<=b:
                errors.append(abs(z-(za+(zb-za)*(x-a)/(b-a))));break
    mat=ob('interior_water').data.materials[0]
    mapping=next(n for n in mat.node_tree.nodes if n.type=='MAPPING')
    rows['foam_uv_offset_y']=float(mapping.inputs['Location'].default_value.y)
    rows['max_threshold_seam_error_m']=max(errors)
    samples[str(frame)]=rows
s.frame_set(1)
assert samples['1']['foam_uv_offset_y']==0
assert abs(samples['181']['foam_uv_offset_y']-.2)<1e-6
assert all(r['max_threshold_seam_error_m']<.003 for r in samples.values())
assert all(r[p]['valid_drivers'] for r in samples.values() for p in ['interior_water','ocean'])
for part in ['interior_water','ocean']:
    assert max(abs(a-b) for a,b in zip(samples['1'][part]['sample_z'],samples['181'][part]['sample_z']))<1e-6
images=set()
for mat in {m for obj in s.objects if obj.type=='MESH' for m in obj.data.materials}:
    images.update(n.image for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image)
images.update(n.image for n in s.world.node_tree.nodes if n.type=='TEX_ENVIRONMENT')
packed={im.name:hashlib.sha256(bytes(im.packed_file.data)).hexdigest() for im in images}
with bpy.data.libraries.load(str(ROOT/'blender/ocean_exit_water.blend'),link=False) as (src,dst):
    saved={'scenes':list(src.scenes),'images':list(src.images),'actions':list(src.actions)}
assert saved['scenes']==['DREAM_OceanExitWater']
report={'schema':'dream.ocean_exit_motion_audit.v1','objects':len(s.objects),'meshes':meshes,'samples':samples,
        'packed_images':packed,'saved_file':saved,'live_shape_key_counts':{p:len(ob(p).data.shape_keys.key_blocks) for p in ['interior_water','ocean']},
        'render_engine':s.render.engine,'native_render_samples':s.cycles.samples,
        'wave_loop_6s_verified':True,'foam_loop_claimed':False,'runtime_promoted':False,'accepted':False,
        'limitations':['These checks establish motion and a continuous doorway surface; they do not establish visual fidelity.',
                       'Frame 181 matches displacement only: foam UVs continue moving and do not loop at six seconds.']}
(OUT/'final-native-audit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
print(json.dumps({'objects':len(s.objects),'meshes':len(meshes),'packed_images':len(packed),
                  'max_seam_error_m':max(r['max_threshold_seam_error_m'] for r in samples.values()),
                  'wave_loop_verified':True,'foam_motion_verified':True}))
