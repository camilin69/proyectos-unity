"""Build the isolated terminal staircase and guards through Blender MCP."""
from pathlib import Path
import json
import math

ROOT=Path(__file__).resolve().parents[1]

def rounded_polyline(points,radius=.045,steps=5):
    from mathutils import Vector
    result=[tuple(points[0])]
    for i in range(1,len(points)-1):
        a,b,c=map(Vector,points[i-1:i+2])
        r=min(radius,(a-b).length*.2,(c-b).length*.2)
        enter=b+(a-b).normalized()*r;leave=b+(c-b).normalized()*r
        for j in range(steps+1):
            t=j/steps;result.append(tuple((1-t)**2*enter+2*t*(1-t)*b+t*t*leave))
    result.append(tuple(points[-1]));return result

def build(report_path='validation/wave-terminal/geometry-candidate.json',
          output_path='blender/wave_corridor_terminal_candidate.blend',
          audit_path='validation/wave-terminal/native-audit.json'):
    import bpy
    import bmesh
    from mathutils import Vector,Quaternion
    report=json.loads((ROOT/report_path).read_text(encoding='utf-8'))
    plan=report['plan'];cfg=plan['constructor'];token=cfg['ownership_token']
    p=ROOT/'blender/build_wave_corridor.py';ns={'__file__':str(p),'__name__':'terminal_build_helpers'}
    exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),ns)
    scene=ns['build_scene'](plan);collection=bpy.data.collections[plan['collection_name']]
    scene['dream_source_plan']=report_path
    scene['dream_stage']=plan['stage'];scene['dream_hall_runtime_pending']=True
    for obj in list(scene.objects):
        if obj.type=='CAMERA' and token in obj.name:bpy.data.objects.remove(obj,do_unlink=True)
    for seed in cfg['all_source_cameras']:
        name=token+f"reference_{seed['time_s']:g}s"
        data=bpy.data.cameras.new('DATA'+name);obj=bpy.data.objects.new('CAM'+name,data);collection.objects.link(obj)
        obj['dream_owner']=scene.name;obj['dream_reference_time_s']=seed['time_s'];obj.location=seed['position_m']
        yaw,pitch=seed['yaw_rad'],seed['pitch_rad']
        direction=Vector((math.cos(yaw)*math.cos(pitch),math.sin(yaw)*math.cos(pitch),math.sin(pitch)))
        obj.rotation_mode='QUATERNION'
        obj.rotation_quaternion=direction.to_track_quat('-Z','Y') @ Quaternion((0,0,1),seed['roll_rad'])
        data.sensor_fit='HORIZONTAL';data.sensor_width=36;data.lens=36/(2*seed['tan_half_vertical_fov']*478/850)
        data.clip_start=.03;data.clip_end=80
    scene.camera=bpy.data.objects['CAM'+token+'reference_14s']
    for obj in scene.objects:
        prefix='GEO'+token+'ceiling_fixture_'
        if obj.type=='MESH' and obj.name.startswith(prefix) and obj.name[len(prefix):].isdigit():
            obj.location.z=cfg['corridor']['ceiling_z_m']-cfg['ceiling_lights']['mount_drop_m']
    mat=bpy.data.materials.get('MAT'+token+'guard') or bpy.data.materials.new('MAT'+token+'guard')
    mat.use_nodes=True
    shader=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    shader.inputs['Base Color'].default_value=(.3,.3,.3,1);shader.inputs['Roughness'].default_value=.32
    shader.inputs['Metallic'].default_value=.65;shader.inputs['Emission Strength'].default_value=0
    guard=cfg['terminal_guards'];attachments=[];uv_checks=[]
    for side,x in zip(['left','right'],guard['x_m']):
        yn,yf=guard['near_y_m'],guard['far_y_m'];zn,zf=ns['floor_height'](yn,cfg),ns['floor_height'](yf,cfg)
        controls=[(x,yn,zn-.008),(x,yn,zn+guard['height_m']),(x,yf,zf+guard['height_m']),(x,yf,zf-.008)]
        path=rounded_polyline(controls)
        data=ns['sweep_tube'](path,guard['tube_radius_m'],guard['sides'])
        # Both cut ends are horizontal: use X/Y UVs for their caps. The generic
        # wall-trim sweep uses X/Z caps, which would degenerate on these posts.
        for i,face in enumerate(data['faces']):
            if i not in data['smooth_faces']:
                data['uv_faces'][i]=[(data['vertices'][v][0],data['vertices'][v][1]) for v in face]
        mesh=bpy.data.meshes.new('MESH'+token+'terminal_guard_'+side)
        mesh.from_pydata(data['vertices'],[],data['faces']);mesh.update()
        obj=bpy.data.objects.new('GEO'+token+'terminal_guard_'+side,mesh);collection.objects.link(obj)
        obj['dream_owner']=scene.name;obj['dream_role']='terminal_guard';mesh.materials.append(mat)
        uv=mesh.uv_layers.new(name='GuardMetres')
        min_area=1e9
        for poly,coords in zip(mesh.polygons,data['uv_faces']):
            poly.use_smooth=poly.index in data['smooth_faces']
            for li,value in zip(poly.loop_indices,coords):uv.data[li].uv=value
            area=abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(coords,coords[1:]+coords[:1])))*.5
            min_area=min(min_area,area)
        assert min_area>1e-12
        uv_checks.append({'object':obj.name,'min_uv_face_area_m2':min_area,'all_faces_explicit_uv':True})
        for y,z in [(yn,zn),(yf,zf)]:
            assert abs(x)+guard['tube_radius_m']<cfg['corridor']['half_width_m']
            attachments.append({'side':side,'xy_m':[x,y],'floor_z_m':z,'post_cap_z_m':z-.008,
                                'embed_m':.008,'inside_tread_width':True})
    # Reverse view exposes the tread attachments and open landing sides.
    data=bpy.data.cameras.new('DATA'+token+'reverse');obj=bpy.data.objects.new('CAM'+token+'reverse',data)
    collection.objects.link(obj);obj['dream_validation_only']=True;obj['dream_owner']=scene.name
    obj.location=(2.,12.7,1.);direction=Vector((0,9.8,-.4))-obj.location
    obj.rotation_mode='QUATERNION';obj.rotation_quaternion=direction.to_track_quat('-Z','Y');data.lens=25
    meshes=[]
    for obj in scene.objects:
        if obj.type!='MESH':continue
        bm=bmesh.new();bm.from_mesh(obj.data)
        meshes.append({'name':obj.name,'closed':all(e.is_manifold for e in bm.edges),'volume_m3':float(bm.calc_volume(signed=True))})
        bm.free()
    assert all(m['closed'] and m['volume_m3']>0 for m in meshes)
    dest=ROOT/output_path
    bpy.data.libraries.write(str(dest),{scene},path_remap='RELATIVE_ALL',fake_user=True,compress=True)
    audit={'scene':scene.name,'objects':len(scene.objects),'cameras':sum(o.type=='CAMERA' for o in scene.objects),
           'meshes':meshes,'guard_uv':uv_checks,'guard_attachments':attachments,
           'wall_end_y_m':cfg['corridor']['wall_end_y_m'],'floor_end_y_m':cfg['corridor']['end_y_m'],
           'saved':str(dest.relative_to(ROOT)).replace('\\','/'),'accepted':False,'runtime_promoted':False}
    (ROOT/audit_path).write_text(json.dumps(audit,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in audit.items() if k!='meshes'}))

if __name__=='__main__':build()
