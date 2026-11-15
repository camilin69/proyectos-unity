"""Apply preserved native wave materials to the isolated hall study via MCP.

This does not export, hide disputed supports, or change the canonical runtime.
The gray native remains available for geometry-only inspection.
"""
from pathlib import Path
import json
import math

ROOT = Path(__file__).resolve().parents[1]
TOKEN = '-DREAM-wavehallform-'


def apply(checker=False):
    import bpy
    scene = bpy.data.scenes['DREAM_WaveHallFormCandidate']
    plan = json.loads((ROOT/'validation/wave-hall-structure/geometry-candidate.json').read_text())['plan']
    cfg = plan['constructor']
    p = ROOT/'blender/build_wave_corridor.py'
    helpers = {'__file__': str(p), '__name__': 'hall_look_helpers'}
    exec(compile(p.read_text(encoding='utf-8'), str(p), 'exec'), helpers)
    profile, _ = helpers['floor_profile'](cfg)
    top_faces = len(profile)-1
    descent = profile[0][1]-profile[-1][1]
    role_map = {'floor':'floor', 'wall':'wall', 'ceiling':'ceiling',
                'door':'door_trim', 'trim':'door_trim', 'rail':'rail',
                'diffuser':'diffuser', 'rear_panel':'rear_panel'}
    objects = [o for o in scene.objects if o.type == 'MESH']
    roles = {}
    for obj in objects:
        role = obj.get('dream_hall_material_role')
        if role is None:
            name = obj.data.materials[0].name
            if name.startswith('DREAM_WAVECORRIDOR_BLOCKOUT_'):
                role = role_map[name.removeprefix('DREAM_WAVECORRIDOR_BLOCKOUT_')]
            elif obj.name.endswith('panel_region'):
                role = 'hall_accent'
            elif 'terminal_guard_' in obj.name:
                role = 'hall_metal'
            else:
                raise ValueError('Unmapped material: '+obj.name)
        roles[obj.name] = role
        obj['dream_hall_material_role'] = role
    materials = {}
    if checker:
        mat = bpy.data.materials.get('MAT'+TOKEN+'checker') or bpy.data.materials.new('MAT'+TOKEN+'checker')
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        nodes.clear()
        shader = nodes.new('ShaderNodeBsdfPrincipled')
        out = nodes.new('ShaderNodeOutputMaterial')
        uv = nodes.new('ShaderNodeUVMap'); uv.uv_map = 'WaveMetres'
        check = nodes.new('ShaderNodeTexChecker')
        check.inputs['Scale'].default_value = 4
        check.inputs['Color1'].default_value = (.04,.08,.12,1)
        check.inputs['Color2'].default_value = (.7,.7,.7,1)
        for a,b in [(uv.outputs['UV'],check.inputs['Vector']),
                    (check.outputs['Color'],shader.inputs['Base Color']),
                    (shader.outputs['BSDF'],out.inputs['Surface'])]:
            mat.node_tree.links.new(a,b)
        materials = {r:mat for r in set(roles.values())|{'floor_caps'}}
    else:
        # Load exact saved materials, rather than trusting other live studies.
        required = sorted(set(roles.values())|{'floor_caps'})
        with bpy.data.libraries.load(str(ROOT/'blender/wave_corridor.blend'), link=False) as (source,dest):
            requested = ['DREAM_WAVE_LOOK_'+r for r in required]
            # Hall-only finishes belong to this study, not the runtime baseline.
            requested = [n for n in requested if n in source.materials]
            dest.materials = list(requested)
        loaded = dict(zip(requested,dest.materials))
        for role in required:
            base = loaded.get('DREAM_WAVE_LOOK_'+role)
            if base is not None:
                mat = base.copy()
            else:
                assert role in ['hall_accent','hall_metal'], role
                mat = bpy.data.materials.new('MAT'+TOKEN+role)
                mat.use_nodes = True
                shader = next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
                shader.inputs['Base Color'].default_value = (.16,.38,.37,1) if role=='hall_accent' else (.55,.55,.55,1)
                shader.inputs['Roughness'].default_value = .35 if role=='hall_accent' else .23
                shader.inputs['Metallic'].default_value = 0 if role=='hall_accent' else 1
            mat.name = 'MAT'+TOKEN+'look_'+role
            mat['dream_fidelity_accepted'] = False
            materials[role] = mat
    coverage = []
    for obj in objects:
        mesh, role = obj.data, roles[obj.name]
        label = obj.name.split(TOKEN,1)[1]
        for name in ['WaveMetres','WaveSurface','WaveMicro']:
            if mesh.uv_layers.get(name) is None: mesh.uv_layers.new(name=name)
        metre,surface,micro = [mesh.uv_layers[n] for n in ['WaveMetres','WaveSurface','WaveMicro']]
        original = mesh.uv_layers.get('ContinuousMetres')
        mesh.materials.clear(); mesh.materials.append(materials[role])
        if role=='floor': mesh.materials.append(materials['floor_caps'])
        normal_matrix = obj.matrix_world.to_3x3().inverted().transposed()
        minimum = math.inf
        for face in mesh.polygons:
            normal = (normal_matrix@face.normal).normalized()
            axis = max(range(3),key=lambda k:abs(normal[k]))
            patterned = role=='floor' and ((label=='continuous_stepped_floor' and face.index<top_faces) or normal.z>.5)
            face.material_index = 1 if role=='floor' and not patterned else 0
            coords = []
            for li in face.loop_indices:
                world = obj.matrix_world@mesh.vertices[mesh.loops[li].vertex_index].co
                if original and (label=='continuous_stepped_floor' or label.startswith('handrail_')):
                    x,s = original.data[li].uv
                elif role=='floor' and normal.z>.5:
                    x,s = world.x, world.y-cfg['corridor']['start_y_m']+descent
                    # The short wings follow the terminal step's current level.
                    if 'wing' in label: s = world.y-cfg['corridor']['start_y_m']-world.z
                else:
                    x,s = ((world.y,world.z),(world.x,world.z),(world.x,world.y))[axis]
                metre.data[li].uv = (x,s)
                surface.data[li].uv = (x/5.54369250671431+.5-.11085074134954703,s/4.46519794285846+.6863645501164858)
                micro.data[li].uv = (x/.5,s/.5)
                coords.append((x,s))
            area = abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(coords,coords[1:]+coords[:1])))*.5
            assert math.isfinite(area) and area>1e-12,(obj.name,face.index,area)
            minimum = min(minimum,area)
        mesh.uv_layers.active = surface; surface.active_render = True
        coverage.append({'object':obj.name,'role':role,'faces':len(mesh.polygons),'minimum_uv_area_m2':minimum})
    images = {}
    for mat in set(materials.values()):
        for node in mat.node_tree.nodes:
            if node.type=='TEX_IMAGE' and node.image:
                image = node.image
                assert image.packed_file is not None, image.name
                images[image.name] = {'filepath':image.filepath,'packed':True,'color_space':image.colorspace_settings.name}
    scene.eevee.use_raytracing = not checker
    bounce_lights = []
    if not checker:
        # Explicit provisional indirect-light approximation, shared in purpose
        # with the earlier material study; no baked source highlights.
        collection = bpy.data.collections[plan['collection_name']]
        for emitter in list(scene.objects):
            if emitter.type!='LIGHT' or 'gray_light_' not in emitter.name: continue
            name = emitter.name.replace('gray_light_', 'look_bounce_')
            bounce = bpy.data.objects.get(name)
            if bounce is None:
                data = bpy.data.lights.new(name+'_data','POINT')
                bounce = bpy.data.objects.new(name,data)
                collection.objects.link(bounce)
            bounce.location = emitter.location
            bounce.location.z -= .06
            bounce.data.energy = 30
            bounce.data.color = (1,.93,.84)
            bounce.data.shadow_soft_size = .015
            # This represents diffuse return, not another direct point source.
            # Direct area emitters retain their physical occlusion shadows.
            bounce.data.use_shadow = False
            bounce.data.specular_factor = 0
            bounce['dream_owner'] = scene.name
            bounce_lights.append(name)
    scene['dream_hall_material_study'] = True
    scene['dream_hall_runtime_pending'] = True
    report = {'accepted':False,'runtime_promoted':False,'checker':checker,'objects':len(scene.objects),
              'coverage':coverage,'packed_images':images,'provisional_bounce_lights':bounce_lights,
              'inferred_supports_visible':all(not o.hide_render for o in objects if o.get('dream_hall_inferred_lower_continuation')),
              'note':'Preserved material maps on revised geometry; pattern registration and physical floor levels remain unaccepted.'}
    if not checker:
        scene.camera = bpy.data.objects['CAM'+TOKEN+'reference_14s']
        dest = ROOT/'blender/wave_corridor_hall_look_candidate.blend'
        bpy.data.libraries.write(str(dest),{scene},path_remap='RELATIVE_ALL',fake_user=True,compress=True)
        report['native'] = str(dest.relative_to(ROOT)).replace('\\','/')
    (ROOT/'validation/wave-hall-structure'/('checker-audit.json' if checker else 'look-audit.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'checker':checker,'meshes':len(coverage),'packed_images':len(images),'saved':report.get('native')}))
    return report


if __name__=='__main__': apply()
