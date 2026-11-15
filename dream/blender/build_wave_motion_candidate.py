"""Build only the isolated source-motion study, through live Blender MCP."""
from pathlib import Path
import json
import math

ROOT=Path(__file__).resolve().parents[1]

def build():
    import bpy
    import bmesh
    from mathutils import Vector, Quaternion
    report=json.loads((ROOT/'validation/wave-motion/geometry-candidate.json').read_text(encoding='utf-8'))
    plan=report['plan'];cfg=plan['constructor'];token=cfg['ownership_token']
    path=ROOT/'blender/build_wave_corridor.py'
    ns={'__file__':str(path),'__name__':'wave_motion_build_helpers'}
    exec(compile(path.read_text(encoding='utf-8'),str(path),'exec'),ns)
    scene=ns['build_scene'](plan)
    scene['dream_source_plan']='validation/wave-motion/geometry-candidate.json'
    scene['dream_stage']='source_motion_gray_candidate_unaccepted'
    scene['dream_hall_runtime_pending']=True
    collection=bpy.data.collections[plan['collection_name']]
    for obj in list(scene.objects):
        if obj.type=='CAMERA' and token in obj.name:bpy.data.objects.remove(obj,do_unlink=True)
    for seed in cfg['all_source_cameras']:
        label=f"reference_{seed['time_s']:g}s"
        data=bpy.data.cameras.new('DATA'+token+label)
        obj=bpy.data.objects.new('CAM'+token+label,data);collection.objects.link(obj)
        obj['dream_owner']=scene.name;obj['dream_reference_time_s']=seed['time_s']
        obj.location=seed['position_m'];yaw,pitch=seed['yaw_rad'],seed['pitch_rad']
        direction=Vector((math.cos(yaw)*math.cos(pitch),math.sin(yaw)*math.cos(pitch),math.sin(pitch)))
        obj.rotation_mode='QUATERNION'
        obj.rotation_quaternion=direction.to_track_quat('-Z','Y') @ Quaternion((0,0,1),seed['roll_rad'])
        data.sensor_fit='HORIZONTAL';data.sensor_width=36
        data.lens=36/(2*seed['tan_half_vertical_fov']*478/850)
        data.clip_start=.03;data.clip_end=80
    scene.camera=bpy.data.objects['CAM'+token+'reference_14s']
    # Match the optimizer's lamp-center interpretation exactly, without altering
    # the canonical builder or the textured runtime model.
    for obj in scene.objects:
        if obj.type=='MESH' and obj.name.startswith('GEO'+token+'ceiling_fixture_') and 'base' not in obj.name:
            obj.location.z=cfg['corridor']['ceiling_z_m']-cfg['ceiling_lights']['mount_drop_m']
    meshes=[]
    for obj in scene.objects:
        if obj.type!='MESH':continue
        bm=bmesh.new();bm.from_mesh(obj.data)
        meshes.append({'name':obj.name,'closed':all(e.is_manifold for e in bm.edges),
                       'volume_m3':float(bm.calc_volume(signed=True))})
        bm.free()
    assert all(m['closed'] and m['volume_m3']>0 for m in meshes)
    dest=ROOT/'blender/wave_corridor_motion_candidate.blend'
    bpy.data.libraries.write(str(dest),{scene},path_remap='RELATIVE_ALL',fake_user=True,compress=True)
    audit={'scene':scene.name,'objects':len(scene.objects),'cameras':sum(o.type=='CAMERA' for o in scene.objects),
           'meshes':meshes,'saved':str(dest.relative_to(ROOT)),
           'materials':'Neutral geometry-study materials only; source maps and textured exports are preserved separately.',
           'accepted':False,'runtime_promoted':False}
    (ROOT/'validation/wave-motion/native-audit.json').write_text(json.dumps(audit,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in audit.items() if k!='meshes'}))
    return scene

if __name__=='__main__':build()
