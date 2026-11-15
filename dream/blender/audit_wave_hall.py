"""Inspect the editable hall draft in Blender; never grant visual acceptance."""
import bpy
import bmesh
import hashlib
import json
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
scene=bpy.data.scenes['DREAM_WaveCorridor']
results=[]
for obj in scene.objects:
    if obj.type!='MESH' or not obj.get('dream_hall_candidate'):
        continue
    bm=bmesh.new();bm.from_mesh(obj.data)
    closed=all(edge.is_manifold for edge in bm.edges)
    volume=bm.calc_volume(signed=True);bm.free()
    assert closed and volume>0, obj.name
    assert all(obj.data.uv_layers.get(name) for name in ('WaveMetres','WaveSurface','WaveMicro')),obj.name
    results.append({'object':obj.name,'closed':closed,'positive_volume':True,
                    'role':obj['dream_surface_role'],'vertices':len(obj.data.vertices),'faces':len(obj.data.polygons)})
column=bpy.data.objects['GEO-DREAM-wavecorridor-hall_column_1']
projections=[]
for name,time,observed in [('CAM-DREAM-wavecorridor-reference14s_seed',14,[232,189,260,256]),
                           ('CAM-DREAM-wavecorridor-secondary_inspection',15.5,[340,238,374,318])]:
    camera=bpy.data.objects[name]
    points=[world_to_camera_view(scene,camera,column.matrix_world@Vector(p)) for p in column.bound_box]
    pixel=[(p.x*478,(1-p.y)*850) for p in points]
    bounds=[min(x for x,y in pixel),min(y for x,y in pixel),max(x for x,y in pixel),max(y for x,y in pixel)]
    projections.append({'time_s':time,'projected_full_column_bounds_px':bounds,
        'source_pale_support_bounds_approx_px':observed,'manual_uncertainty_px':8,
        'bottom_edge_difference_px':bounds[3]-observed[3],
        'interpretation':'Diagnostic only. Source head can be occluded by the corridor; no physical dimension or fit acceptance is inferred.'})
path=ROOT/'blender/wave_corridor_hall_candidate.blend'
with bpy.data.libraries.load(str(path),link=False) as (source,destination):
    inventory={'scenes':list(source.scenes),'objects':len(source.objects),'images':list(source.images)}
assert inventory['scenes']==['DREAM_WaveCorridor'] and len(inventory['images'])==10
report={'schema':'dream.wave_hall_audit.v1','scene_objects':len(scene.objects),
        'mesh_objects':sum(o.type=='MESH' for o in scene.objects),'hall_meshes':results,
        'native_inventory':inventory,'column_projection_diagnostics':projections,
        'candidate_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'runtime_promoted':False,'strict_fidelity_accepted':False}
(ROOT/'validation/wave-hall-audit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'closed_hall_meshes':len(results),'inventory':inventory,'column_projection_diagnostics':projections}))
