"""Reference-informed wall details; dimensions remain reconstruction estimates.

14s fixes signs/button positions on the fitted wall planes. The 12.5s/17s
views expose the dark strip's layered section and the two utility panels.
This does not resolve the hallway topology, door thresholds or step heights.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'GEO-DREAM-wavecorridor-detail_'
REVISION = 2
SIGN_SIZE = (.40, .16)


def apply_geometry(scene):
    import bpy
    import bmesh
    p = ROOT/'blender/build_wave_corridor.py'
    helper = {'__file__': str(p), '__name__': 'wave_pure_helpers'}
    exec(compile(p.read_text(encoding='utf-8'), str(p), 'exec'), helper)
    config = helper['load_plan']()['constructor']
    collection = bpy.data.collections['DREAM_WaveCorridor_Blockout']
    created = []

    def mesh(label, vertices, faces, role):
        name = PREFIX+label
        obj = bpy.data.objects.get(name)
        if obj is not None and obj.get('dream_detail_revision') == REVISION:
            return obj
        data = bpy.data.meshes.new(name+'_mesh')
        data.from_pydata(vertices, [], faces)
        data.update()
        bm = bmesh.new()
        bm.from_mesh(data)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        assert all(e.is_manifold for e in bm.edges), name
        bm.to_mesh(data)
        bm.free()
        if obj is None:
            obj = bpy.data.objects.new(name, data)
            collection.objects.link(obj)
        else:
            old = obj.data
            obj.data = data
            if old.users == 0:
                bpy.data.meshes.remove(old)
        obj['dream_surface_role'] = role
        obj['dream_detail_revision'] = REVISION
        obj['dream_owner'] = scene.name
        obj['dream_detail_source'] = 'video-42 @12.5,14,17s; dimensions inferred'
        created.append(name)
        return obj

    def box(label, center, size, role='door_trim'):
        vertices = [(center[0]+x*size[0]/2, center[1]+y*size[1]/2, center[2]+z*size[2]/2)
                    for x in (-1,1) for y in (-1,1) for z in (-1,1)]
        faces = [(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
        return mesh(label, vertices, faces, role)

    # Full section behind the existing rounded upper lip. The back overlaps
    # the wall by 6 mm, avoiding a floating pipe and coplanar wall faces.
    section = [(-.006,.042),(.034,.042),(.068,.031),(.068,-.034),
               (.052,-.040),(.052,-.070),(-.006,-.070)]
    for side in (-1,1):
        path = helper['rail_path'](side, config)
        half = config['corridor']['half_width_m']
        n = len(section)
        vertices = [(side*(half-depth), y, z+height) for _,y,z in path for depth,height in section]
        faces = []
        for i in range(len(path)-1):
            for j in range(n):
                k = (j+1)%n
                faces.append((i*n+j,i*n+k,(i+1)*n+k,(i+1)*n+j))
        faces += [tuple(reversed(range(n))), tuple((len(path)-1)*n+j for j in range(n))]
        mesh(f'trim_backing_{side}', vertices, faces, 'rail')
        lower = [(side*(half-.065), y, z-.065) for _,y,z in path]
        swept = helper['sweep_tube'](lower, .012, 10)
        bead = mesh(f'trim_lower_bead_{side}', swept['vertices'], swept['faces'], 'rail')
        smooth = set(swept['smooth_faces'])
        for poly in bead.data.polygons:
            poly.use_smooth = poly.index in smooth

    for side,y,z in [(-1,3.0467813,2.1874495),(1,3.0212083,2.2431388)]:
        sign = box(f'exit_{side}', (side*1.092,y,z), (.028,*SIGN_SIZE))
        sign['dream_sign_side'] = side
        sign['dream_sign_center_y'] = y
        sign['dream_sign_center_z'] = z
        sign['dream_sign_text_inferred'] = 'EXIT; red lettering visible but compressed'
    box('button_plate', (-1.088,3.87,1.16), (.03,.075,.115))
    box('button_lens', (-1.064,3.87,1.17), (.023,.034,.04), 'diffuser')
    for i,y in enumerate((6.73,7.07)):
        box(f'utility_panel_frame_{i}', (-1.087,y,.12), (.032,.29,.48))
        box(f'utility_panel_inset_{i}', (-1.065,y,.12), (.014,.25,.43))
    corridor = config['corridor']
    bottom,top = corridor['solid_bottom_z_m'],corridor['ceiling_z_m']
    closure = box('entry_closure_inferred', (0,corridor['start_y_m']-.08,(bottom+top)/2),
                  (2*corridor['half_width_m']+.36,.16,top-bottom), 'wall')
    closure['dream_detail_source'] = 'Unseen back boundary inferred for a closed traversable prototype; not an observed doorway.'
    return {'new_or_replaced': created, 'detail_objects': sum(o.name.startswith(PREFIX) for o in scene.objects),
            'reference_positions_inferred': True, 'strict_acceptance': False}


def apply_sign_materials(scene):
    import bpy
    def linear(rgb):
        return tuple(v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in rgb)+(1,)
    def principled(name, colour, emission=0):
        mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
        mat.use_nodes = True
        nt = mat.node_tree
        nt.nodes.clear()
        bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
        out = nt.nodes.new('ShaderNodeOutputMaterial')
        nt.links.new(bsdf.outputs['BSDF'],out.inputs['Surface'])
        bsdf.inputs['Base Color'].default_value = linear(colour)
        bsdf.inputs['Roughness'].default_value = .35
        bsdf.inputs['Emission Color'].default_value = linear(colour)
        bsdf.inputs['Emission Strength'].default_value = emission
        mat['runtime_material_mapping_pending'] = True
        return mat, nt, bsdf
    mat,nt,bsdf = principled('DREAM_WAVE_LOOK_exit', (1,1,1))
    uv = nt.nodes.new('ShaderNodeUVMap')
    uv.uv_map = 'WaveDecal'
    for stem,socket,data in [('wave_exit_albedo_dark','Base Color',False),
                             ('wave_exit_emission_dark','Emission Strength',True)]:
        tex = nt.nodes.new('ShaderNodeTexImage')
        tex.image = bpy.data.images.load(str(ROOT/'assets/textures/wave_candidate'/f'{stem}.png'),check_existing=True)
        tex.image.colorspace_settings.name = 'Non-Color' if data else 'sRGB'
        tex.image.pack()
        tex.extension = 'EXTEND'
        nt.links.new(uv.outputs['UV'],tex.inputs['Vector'])
        if data:
            strength = nt.nodes.new('ShaderNodeMath')
            strength.operation = 'MULTIPLY'
            strength.inputs[1].default_value = 6
            nt.links.new(tex.outputs['Color'],strength.inputs[0])
            nt.links.new(strength.outputs[0],bsdf.inputs[socket])
        else:
            nt.links.new(tex.outputs['Color'],bsdf.inputs[socket])
            nt.links.new(tex.outputs['Color'],bsdf.inputs['Emission Color'])
    coat = bpy.data.materials['DREAM_WAVE_LOOK_door_trim']
    for obj in scene.objects:
        if not obj.name.startswith(PREFIX+'exit_'):
            continue
        mesh = obj.data
        layer = mesh.uv_layers.get('WaveDecal') or mesh.uv_layers.new(name='WaveDecal')
        side,y,z = obj['dream_sign_side'],obj['dream_sign_center_y'],obj['dream_sign_center_z']
        mesh.materials.clear()
        mesh.materials.append(coat)
        mesh.materials.append(mat)
        for face in mesh.polygons:
            front = face.normal.x*side < -.5
            face.material_index = int(front)
            for li in face.loop_indices:
                co = mesh.vertices[mesh.loops[li].vertex_index].co
                if abs(face.normal.x) > .5:
                    layer.data[li].uv = (.5-side*(co.y-y)/SIGN_SIZE[0],.5+(co.z-z)/SIGN_SIZE[1])
                else:
                    # Non-textured side coating still has nondegenerate UVs.
                    layer.data[li].uv = (co.x,co.z if abs(face.normal.y) > .5 else co.y)
        mesh.uv_layers.active = layer
        layer.active_render = True
    red,_,_ = principled('DREAM_WAVE_LOOK_button_red', (.68,.16,.10), 1.2)
    obj = bpy.data.objects[PREFIX+'button_lens']
    obj.data.materials.clear()
    obj.data.materials.append(red)
    return {'signs':2,'image_maps':2,'sign_front_only':True,'side_and_back_coated':True,
            'text_confidence':'medium, inferred from compressed red signs'}
