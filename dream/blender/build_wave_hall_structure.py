"""Hall form study: observed upper contours plus explicit inferred continuations."""
from pathlib import Path
import copy
import json

ROOT=Path(__file__).resolve().parents[1]

def build():
    import bpy
    import bmesh
    source=json.loads((ROOT/'validation/wave-aperture/fit.json').read_text(encoding='utf-8'))
    fit=json.loads((ROOT/'validation/wave-hall-structure/capital-fit.json').read_text(encoding='utf-8'))
    plan=copy.deepcopy(source['plan']);c=plan['constructor'];token='-DREAM-wavehallform-'
    c['ownership_token']=token;c['destination_hall'].update(half_width_m=4.3,end_y_m=24.,column_x_m=[],back_grid_columns=12)
    plan.update(scene_name='DREAM_WaveHallFormCandidate',asset_id='wave_hall_form_candidate',collection_name='DREAM_WaveHallFormCandidate',stage='hall_visible_forms_and_inferred_bases_unaccepted')
    candidate={'plan':plan,'accepted':False,'runtime_promoted':False,'source_fit':'validation/wave-hall-structure/capital-fit.json'}
    (ROOT/'validation/wave-hall-structure/geometry-candidate.json').write_text(json.dumps(candidate,indent=2)+'\n',encoding='utf-8')
    path=ROOT/'blender/build_wave_terminal_candidate.py';ns={'__file__':str(path),'__name__':'hall_structure_helpers'}
    exec(compile(path.read_text(encoding='utf-8'),str(path),'exec'),ns)
    ns['build'](report_path='validation/wave-hall-structure/geometry-candidate.json',
                output_path='blender/wave_corridor_hall_structure_candidate.blend',audit_path='validation/wave-hall-structure/base-native-audit.json')
    scene=bpy.data.scenes[plan['scene_name']];collection=bpy.data.collections[plan['collection_name']]
    material=bpy.data.materials['DREAM_WAVECORRIDOR_BLOCKOUT_trim']
    panel_mat=bpy.data.materials.get('MAT'+token+'panel') or bpy.data.materials.new('MAT'+token+'panel')
    panel_mat.use_nodes=True;shader=next(n for n in panel_mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    shader.inputs['Base Color'].default_value=(.26,.26,.26,1);shader.inputs['Roughness'].default_value=.5
    shader.inputs['Metallic'].default_value=0
    created=[]
    def solid(label,polygon,y,depth,mat=material,inferred=False):
        n=len(polygon);vertices=[(x,yy,z) for yy in (y,y+depth) for x,z in polygon]
        faces=[tuple(range(n)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
        data=bpy.data.meshes.new('MESH'+token+label);data.from_pydata(vertices,[],faces);data.update()
        bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        assert all(e.is_manifold for e in bm.edges) and bm.calc_volume(signed=True)>0
        bm.to_mesh(data);bm.free();data.update()
        obj=bpy.data.objects.new('GEO'+token+label,data);collection.objects.link(obj);obj['dream_owner']=scene.name
        obj['dream_hall_inferred_lower_continuation']=inferred;obj.data.materials.append(mat)
        uv=data.uv_layers.new(name='HallMetres');areas=[]
        for face in data.polygons:
            normal=face.normal;axis=max(range(3),key=lambda i:abs(normal[i]));indices=[i for i in range(3) if i!=axis]
            coords=[]
            for li in face.loop_indices:
                point=data.vertices[data.loops[li].vertex_index].co;value=(point[indices[0]],point[indices[1]])
                uv.data[li].uv=value;coords.append(value)
            area=abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(coords,coords[1:]+coords[:1])))*.5;assert area>1e-12;areas.append(area)
        created.append({'name':obj.name,'inferred_lower_continuation':inferred,'min_uv_face_area_m2':min(areas)})
        return obj
    def rectangle(label,x,y,z0,z1,width,depth,mat=material,inferred=False):
        return solid(label,[(x-width/2,z0),(x+width/2,z0),(x+width/2,z1),(x-width/2,z1)],y,depth,mat,inferred)
    p=fit['parameters'];floor,ceiling=fit['floor_z_m'],fit['ceiling_z_m']
    x,y,w,cw,ch,offset,z=(p[k] for k in ['shaft_x','front_y','shaft_width','capital_width','capital_height','capital_offset_x','paint_lower_z'])
    polygon=[(x-w/2,z),(x+w/2,z),(x+w/2,ceiling-ch),(x+offset+cw/2,ceiling),
             (x+offset-cw/2,ceiling),(x-w/2,ceiling-ch)]
    solid('hall_right_visible_form',polygon,y,.45)
    rectangle('hall_right_lower_inferred',x,y,floor,z,w,.45,inferred=True)
    rectangle('hall_right_panel_region',x-.02,y-.012,z+.02,ceiling-ch-.05,w*.65,.015,panel_mat)
    p=fit['left_visible_form']['parameters']
    rectangle('hall_left_visible_form',p['center_x'],p['front_y'],p['visible_bottom_z'],ceiling,p['width'],.4)
    rectangle('hall_left_lower_inferred',p['center_x'],p['front_y'],floor,p['visible_bottom_z'],p['width'],.4,inferred=True)
    fixtures=[]
    for side,x,start in [('left',-1.6,13.8),('right',1.6,12.8)]:
        for i in range(4):
            y=start+2.7*i;z=ceiling-c['ceiling_lights']['mount_drop_m']
            for label,zz,scale in [('shade',z,(.15,.15,.1)),('mount',ceiling-.018,(.16,.16,.018))]:
                bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=1,location=(x,y,zz))
                obj=bpy.context.object;obj.name='GEO'+token+f'hall_lamp_{side}_{i}_{label}';obj.scale=scale
                bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
                for old in list(obj.users_collection):old.objects.unlink(obj)
                collection.objects.link(obj);obj.data.materials.append(bpy.data.materials['DREAM_WAVECORRIDOR_BLOCKOUT_diffuser'])
                obj['dream_owner']=scene.name
                for face in obj.data.polygons:face.use_smooth=True
            data=bpy.data.lights.new('DATA'+token+f'hall_light_{side}_{i}','AREA');data.energy=40;data.shape='DISK';data.size=.7
            obj=bpy.data.objects.new('LGT'+token+f'hall_light_{side}_{i}',data);collection.objects.link(obj);obj.location=(x,y,z-.125)
            fixtures.append({'side':side,'xy_m':[x,y],'placement':'Source-inspired row spacing, not fitted lamp-by-lamp.'})
    scene['dream_hall_lower_continuation_unresolved']=True
    scene['dream_hall_structure_fit']='validation/wave-hall-structure/capital-fit.json'
    checks=[]
    for obj in scene.objects:
        if obj.type!='MESH':continue
        bm=bmesh.new();bm.from_mesh(obj.data);checks.append({'name':obj.name,'closed':all(e.is_manifold for e in bm.edges),'volume':bm.calc_volume(signed=True)});bm.free()
    assert all(r['closed'] and r['volume']>0 for r in checks)
    destination=ROOT/'blender/wave_corridor_hall_structure_candidate.blend'
    bpy.data.libraries.write(str(destination),{scene},path_remap='RELATIVE_ALL',fake_user=True,compress=True)
    audit={'scene':scene.name,'objects':len(scene.objects),'mesh_checks':checks,'new_forms':created,'side_fixtures':fixtures,
           'native':str(destination.relative_to(ROOT)).replace('\\','/'),'accepted':False,'runtime_promoted':False,
           'inferred_bases_visible_by_default':True,'note':'Full-height supports remain the physical hypothesis. The visible paint boundary is not their lower end.'}
    (ROOT/'validation/wave-hall-structure/native-audit.json').write_text(json.dumps(audit,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in audit.items() if k not in ['mesh_checks','new_forms','side_fixtures']}))

if __name__=='__main__':build()
