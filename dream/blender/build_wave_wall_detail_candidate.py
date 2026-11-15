"""Add source-fitted utility panels to an isolated saved material study."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]

def build():
    import bpy
    import bmesh
    token='-DREAM-wavewall-'
    name='DREAM_WaveWallDetailCandidate'
    assert bpy.data.scenes.get(name) is None,'Candidate already exists; inspect before replacing.'
    source_path=ROOT/'blender/wave_corridor_hall_look_candidate.blend'
    with bpy.data.libraries.load(str(source_path),link=False) as (source,dest):
        assert len(source.scenes)==1
        dest.scenes=list(source.scenes)
    scene=dest.scenes[0];scene.name=name
    bpy.context.window.scene=scene
    for obj in scene.objects:
        obj.name=obj.name.replace('-DREAM-wavehallform-',token)
        obj['dream_owner']=name
    group=bpy.data.collections.new('DREAM_WaveWallPanels');scene.collection.children.link(group)
    data=json.loads((ROOT/'validation/wave-perspective/wall-panels-fit.json').read_text())
    p=data['parameters'];front=data['front_x_m']
    base=next(o for o in scene.objects if o.type=='MESH' and 'door_0_leaf' in o.name).data.materials[0]
    frame_mat=base.copy();frame_mat.name='MAT'+token+'panel_frame'
    insert_mat=base.copy();insert_mat.name='MAT'+token+'panel_insert'
    shader=next(n for n in insert_mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    shader.inputs['Base Color'].default_value=(.40,.42,.36,1)
    shader.inputs['Roughness'].default_value=.65
    created=[]
    def box(label,center,size,material):
        x,y,z=center;dx,dy,dz=size
        vertices=[(x+a*dx/2,y+b*dy/2,z+c*dz/2) for a in (-1,1) for b in (-1,1) for c in (-1,1)]
        faces=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
        mesh=bpy.data.meshes.new('MESH'+token+label);mesh.from_pydata(vertices,[],faces);mesh.update()
        bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        assert all(e.is_manifold for e in bm.edges) and bm.calc_volume(signed=True)>0
        bm.to_mesh(mesh);bm.free();mesh.update()
        uv=mesh.uv_layers.new(name='PanelMetres');areas=[]
        for face in mesh.polygons:
            axis=max(range(3),key=lambda i:abs(face.normal[i]));axes=[i for i in range(3) if i!=axis];values=[]
            for li in face.loop_indices:
                co=mesh.vertices[mesh.loops[li].vertex_index].co;value=[co[i] for i in axes]
                uv.data[li].uv=value;values.append(value)
            area=abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(values,values[1:]+values[:1])))/2
            assert area>1e-12;areas.append(area)
        obj=bpy.data.objects.new('GEO'+token+label,mesh);group.objects.link(obj);mesh.materials.append(material)
        obj['dream_owner']=name;obj['dream_source_fit']='validation/wave-perspective/wall-panels-fit.json'
        created.append({'name':obj.name,'minimum_uv_face_area_m2':min(areas),'closed':True})
    gap=.012
    for label,y,w in [('near',p['near_center_y'],p['near_width']),('far',p['far_center_y'],p['far_width'])]:
        z=p['center_z'];h=p['height'];rim=.016
        box('panel_'+label+'_back',(front-.025,y,z),(.024,w,h),frame_mat)
        box('panel_'+label+'_insert',(front-.011,y,z),(.010,w-2*rim,h-2*rim),insert_mat)
        for suffix,yy in [('near',y-(w-rim)/2),('far',y+(w-rim)/2)]:
            box('panel_'+label+'_rim_'+suffix,(front-.009,yy,z),(.018,rim,h),frame_mat)
        for suffix,zz in [('top',z+(h-rim)/2),('bottom',z-(h-rim)/2)]:
            box('panel_'+label+'_rim_'+suffix,(front-.009,y,zz),(.018,w-2*rim,rim),frame_mat)
    scene.camera=next(o for o in scene.objects if o.type=='CAMERA' and o.get('dream_reference_time_s')==14)
    scene['dream_wall_detail_candidate']=True;scene['dream_hall_runtime_pending']=True
    mesh_checks=[]
    for obj in scene.objects:
        if obj.type!='MESH':continue
        bm=bmesh.new();bm.from_mesh(obj.data)
        mesh_checks.append({'name':obj.name,'closed':all(e.is_manifold for e in bm.edges),'volume_m3':bm.calc_volume(signed=True)})
        bm.free()
    assert all(m['closed'] and m['volume_m3']>0 for m in mesh_checks)
    output=ROOT/'blender/wave_corridor_wall_detail_candidate.blend'
    bpy.data.libraries.write(str(output),{scene},path_remap='RELATIVE_ALL',fake_user=True,compress=True)
    audit={'scene':scene.name,'objects':len(scene.objects),'meshes':mesh_checks,'panel_parts':created,
           'native':str(output.relative_to(ROOT)).replace('\\','/'),'accepted':False,'runtime_promoted':False,
           'source_native_preserved':'blender/wave_corridor_hall_look_candidate.blend',
           'paint_experiments_applied':False,'camera_hypothesis_applied':False}
    (ROOT/'validation/wave-perspective/native-wall-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    print(json.dumps({k:v for k,v in audit.items() if k not in ['meshes','panel_parts']}))

if __name__=='__main__':build()
