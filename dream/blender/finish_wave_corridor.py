"""Apply inspectable UV and material candidates to the fitted wave corridor.

Run apply(checker=True), inspect its render, then apply() inside Blender MCP.
No geometry, camera, runtime export or acceptance is implied by this helper.
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKEN = '-DREAM-wavecorridor-'
# Foreground registration from validation/wave-paint-fit.json; not a final fit.
FLOOR_PERIOD = (5.54369250671431, 4.46519794285846)
FLOOR_PHASE = 0.6863645501164858
FLOOR_OFFSET_U = -0.11085074134954703


def linear(rgb):
    def component(c):
        c /= 255.0
        return c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4
    return (*map(component, rgb), 1.0)


def apply(checker=False):
    import bpy
    plan = json.loads((ROOT/'blender/wave_corridor_plan.json').read_text(encoding='utf-8'))
    material_plan = json.loads((ROOT/'blender/wave_material_plan.json').read_text(encoding='utf-8'))
    config = plan['constructor']
    scene = bpy.data.scenes[plan['scene_name']]
    owned_collection = bpy.data.collections['DREAM_WaveCorridor_Blockout']
    bpy.context.window.scene = scene
    detail_path = ROOT/'blender/wave_corridor_details.py'
    details = {'__file__': str(detail_path), '__name__': 'wave_details'}
    exec(compile(detail_path.read_text(encoding='utf-8'), str(detail_path), 'exec'), details)
    detail_geometry = details['apply_geometry'](scene)
    builder_path = ROOT/'blender/build_wave_corridor.py'
    builder = {'__file__': str(builder_path), '__name__': 'wave_helpers'}
    exec(compile(builder_path.read_text(encoding='utf-8'), str(builder_path), 'exec'), builder)
    profile, _ = builder['floor_profile'](config)
    top_faces = len(profile)-1
    descent = profile[0][1]-profile[-1][1]
    role_map = {'floor': 'floor', 'wall': 'wall', 'ceiling': 'ceiling',
                'door': 'door_trim', 'trim': 'door_trim', 'rail': 'rail',
                'diffuser': 'diffuser', 'rear_panel': 'rear_panel'}
    objects = [o for o in scene.objects if o.type == 'MESH' and TOKEN in o.name]
    roles = {}
    for obj in objects:
        role = obj.get('dream_surface_role')
        if role is None:
            old = obj.data.materials[0].name.removeprefix('DREAM_WAVECORRIDOR_BLOCKOUT_')
            if old not in role_map:
                raise ValueError('Unmapped surface: '+obj.name+' / '+old)
            role = role_map[old]
        roles[obj.name] = role

    def material(role, settings, diagnostic=False):
        name = 'DREAM_WAVE_LOOK_'+role
        mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
        mat.use_nodes = True
        nt = mat.node_tree
        nt.nodes.clear()
        bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
        out = nt.nodes.new('ShaderNodeOutputMaterial')
        nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
        bsdf.inputs['Base Color'].default_value = linear(settings.get('base_color_srgb_255', [128, 128, 128]))
        for key, socket, default in [('roughness', 'Roughness', .6), ('metallic', 'Metallic', 0),
                                      ('ior', 'IOR', 1.47), ('coat_weight', 'Coat Weight', 0),
                                      ('coat_roughness', 'Coat Roughness', .2)]:
            bsdf.inputs[socket].default_value = settings.get(key, default)
        mat['runtime_material_mapping_pending'] = True
        mat['fidelity_accepted'] = False
        if diagnostic:
            uv = nt.nodes.new('ShaderNodeUVMap')
            uv.uv_map = 'WaveMetres'
            check = nt.nodes.new('ShaderNodeTexChecker')
            check.inputs['Scale'].default_value = 4
            check.inputs['Color1'].default_value = (.07, .12, .18, 1)
            check.inputs['Color2'].default_value = (.75, .75, .75, 1)
            nt.links.new(uv.outputs['UV'], check.inputs['Vector'])
            nt.links.new(check.outputs['Color'], bsdf.inputs['Base Color'])
            return mat

        def texture(map_name, uv_name, data=False):
            uv = nt.nodes.new('ShaderNodeUVMap')
            uv.uv_map = uv_name
            tex = nt.nodes.new('ShaderNodeTexImage')
            path = ROOT/'assets/textures/wave_candidate'/f'{map_name}.png'
            tex.image = bpy.data.images.load(str(path), check_existing=True)
            tex.image.colorspace_settings.name = 'Non-Color' if data else 'sRGB'
            tex.image.pack()
            tex.extension = 'REPEAT'
            nt.links.new(uv.outputs['UV'], tex.inputs['Vector'])
            return tex

        if settings.get('base_color_map'):
            tex = texture(settings['base_color_map'], 'WaveSurface' if role == 'floor' else 'WaveMicro')
            nt.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
        if settings.get('roughness_map'):
            tex = texture(settings['roughness_map'], 'WaveSurface' if role == 'floor' else 'WaveMicro', True)
            nt.links.new(tex.outputs['Color'], bsdf.inputs['Roughness'])
        if settings.get('normal_map'):
            tex = texture(settings['normal_map'], 'WaveMicro', True)
            normal = nt.nodes.new('ShaderNodeNormalMap')
            normal.space, normal.uv_map = 'TANGENT', 'WaveMicro'
            normal.inputs['Strength'].default_value = 1.6 if role == 'floor' else settings.get('normal_strength', 1)
            nt.links.new(tex.outputs['Color'], normal.inputs['Color'])
            nt.links.new(normal.outputs['Normal'], bsdf.inputs['Normal'])
            if role == 'floor':
                nt.links.new(normal.outputs['Normal'], bsdf.inputs['Coat Normal'])
        if settings.get('emission_seed'):
            bsdf.inputs['Emission Color'].default_value = linear(settings['base_color_srgb_255'])
            bsdf.inputs['Emission Strength'].default_value = settings['emission_seed']
        return mat

    materials = {}
    if checker:
        diagnostic = material('CHECKER', {}, True)
    else:
        for role in set(roles.values()):
            settings = dict(material_plan['materials'][role])
            if role == 'rear_panel':
                settings = {'base_color_srgb_255': [70, 75, 73], 'roughness': .7}
            if role == 'diffuser':
                settings['emission_seed'] = 5
            materials[role] = material(role, settings)
        materials['floor_caps'] = material('floor_caps', {'base_color_srgb_255': [110, 161, 158], 'roughness': .5})

    coverage, bad = [], []
    for obj in objects:
        mesh, role = obj.data, roles[obj.name]
        obj['dream_surface_role'] = role
        label = obj.name.split(TOKEN, 1)[1]
        original = mesh.uv_layers.get('ContinuousMetres')
        # Creating layers can invalidate RNA wrappers; acquire each afterward.
        for name in ('WaveMetres', 'WaveSurface', 'WaveMicro'):
            if mesh.uv_layers.get(name) is None:
                mesh.uv_layers.new(name=name)
        metre, surface, micro = [mesh.uv_layers[n] for n in ('WaveMetres', 'WaveSurface', 'WaveMicro')]
        original = mesh.uv_layers.get('ContinuousMetres')
        mesh.materials.clear()
        mesh.materials.append(diagnostic if checker else materials[role])
        if role == 'floor' and not checker:
            mesh.materials.append(materials['floor_caps'])
        normal_matrix = obj.matrix_world.to_3x3().inverted().transposed()
        hidden_faces = 0
        for face in mesh.polygons:
            normal = (normal_matrix @ face.normal).normalized()
            axis = max(range(3), key=lambda i: abs(normal[i]))
            is_floor_top = ((label == 'continuous_stepped_floor' and face.index < top_faces) or
                            (label == 'hall_floor' and normal.z > .5))
            face.material_index = 0
            if role == 'floor' and not is_floor_top:
                hidden_faces += 1
                if not checker:
                    face.material_index = 1
            coordinates = []
            for li in face.loop_indices:
                world = obj.matrix_world @ mesh.vertices[mesh.loops[li].vertex_index].co
                if original is not None and (label == 'continuous_stepped_floor' or label.startswith('handrail_')):
                    x, s = original.data[li].uv
                elif label == 'hall_floor' and is_floor_top:
                    x, s = world.x, world.y-config['corridor']['start_y_m']+descent
                else:
                    x, s = ((world.y, world.z), (world.x, world.z), (world.x, world.y))[axis]
                metre.data[li].uv = (x, s)
                surface.data[li].uv = (x/FLOOR_PERIOD[0]+.5+FLOOR_OFFSET_U, s/FLOOR_PERIOD[1]+FLOOR_PHASE)
                micro.data[li].uv = (x/.5, s/.5)
                coordinates.append((x, s))
            area = abs(sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(coordinates, coordinates[1:]+coordinates[:1])))/2
            if not math.isfinite(area) or area <= 1e-12:
                bad.append([obj.name, face.index, area])
        mesh.uv_layers.active = surface
        surface.active_render = True
        coverage.append({'object': obj.name, 'role': role, 'faces': len(mesh.polygons),
                         'loops': len(mesh.loops), 'neutral_cap_faces': hidden_faces})
    if bad:
        raise ValueError('Degenerate UV faces: '+str(bad[:10]))

    # Exact shared boundary in the same metric parameterization.
    floor = next(o for o in objects if o.name.endswith('continuous_stepped_floor'))
    hall = next(o for o in objects if o.name.endswith('hall_floor'))
    seam_y, seam_z = profile[-1]
    seam_values = []
    for obj in (floor, hall):
        values = []
        for face in obj.data.polygons:
            for li in face.loop_indices:
                co = obj.matrix_world @ obj.data.vertices[obj.data.loops[li].vertex_index].co
                if abs(co.y-seam_y) < 1e-5 and abs(co.z-seam_z) < 1e-5:
                    if (obj == floor and face.index == top_faces-1) or (obj == hall and face.normal.z > .5):
                        values.append(tuple(obj.data.uv_layers['WaveMetres'].data[li].uv))
        seam_values.append(values)
    # Hall is wider than the passage; compare the interpolated edge, not its
    # distant corners. A narrower entrance must match points inside that edge.
    hall_edge = sorted(set(seam_values[1]))
    if len(hall_edge) < 2:
        raise ValueError('Hall must expose a top boundary edge')
    ha, hb = hall_edge[0], hall_edge[-1]
    direction = (hb[0]-ha[0], hb[1]-ha[1])
    length_squared = sum(v*v for v in direction)
    for uv in hall_edge:
        t = sum((uv[i]-ha[i])*direction[i] for i in range(2))/length_squared
        if math.dist(uv, tuple(ha[i]+t*direction[i] for i in range(2))) > 1e-5:
            raise ValueError('Tessellated hall UV boundary is not straight')
    seam_errors = []
    for a in seam_values[0]:
        t = sum((a[i]-ha[i])*direction[i] for i in range(2))/length_squared
        if not 0 <= t <= 1:
            raise ValueError('Hall UV edge does not cover the passage')
        seam_errors.append(math.dist(a, tuple(ha[i]+t*direction[i] for i in range(2))))
    if len(seam_errors) != 2 or max(seam_errors) > 1e-5:
        raise ValueError('Floor/hall UV discontinuity: '+str(seam_values))

    if not checker:
        ceiling = config['corridor']['ceiling_z_m']
        for obj in list(scene.objects):
            if obj.type != 'LIGHT' or TOKEN not in obj.name or 'gray_light_' not in obj.name:
                continue
            obj.data.energy, obj.data.size = 40, .55
            obj.data.color = (1, .93, .84)
            obj.location.z = ceiling-.48
            name = obj.name.replace('gray_light_', 'bounce_light_')
            bounce = bpy.data.objects.get(name)
            if bounce is None:
                bounce = bpy.data.objects.new(name, bpy.data.lights.new(name+'_data', 'POINT'))
                obj.users_collection[0].objects.link(bounce)
            bounce.location = (obj.location.x, obj.location.y, ceiling-.40)
            bounce.data.energy, bounce.data.shadow_soft_size = 30, .18
            bounce.data.color = (1, .93, .84)
            bounce.data.specular_factor = 0
        # Light from the corridor continuing behind the reference camera.
        # The source's foreground illumination is visible; this emitter's
        # position and energy are inferred and remain a calibration candidate.
        name = 'LGT'+TOKEN+'entrance_fill'
        fill = bpy.data.objects.get(name)
        if fill is None:
            fill = bpy.data.objects.new(name, bpy.data.lights.new(name+'_data', 'AREA'))
            owned_collection.objects.link(fill)
        fill.location = (0, -.8, ceiling-.3)
        fill.data.energy, fill.data.size = 280, 1.4
        fill.data.color = (1, .93, .84)
        # Surface-restricted returns approximate the unmodelled indirect room
        # bounce. They remain explicit inferred lights, never baked highlights.
        def receivers(emitter, suffix, role):
            name = 'DREAM_Wave_Return_'+suffix
            group = bpy.data.collections.get(name) or bpy.data.collections.new(name)
            for old in list(group.objects):
                group.objects.unlink(old)
            for obj in objects:
                if roles[obj.name] == role:
                    group.objects.link(obj)
            emitter.light_linking.receiver_collection = group
        receivers(fill, 'Floor', 'floor')
        name = 'LGT'+TOKEN+'ceiling_return'
        up = bpy.data.objects.get(name)
        if up is None:
            up = bpy.data.objects.new(name, bpy.data.lights.new(name+'_data', 'AREA'))
            owned_collection.objects.link(up)
        # Receiver collections need not belong to the scene tree. Never use
        # users_collection[0] as the owner once light-linking sets exist.
        if up.name not in owned_collection.objects:
            owned_collection.objects.link(up)
        for collection in list(up.users_collection):
            if collection != owned_collection:
                collection.objects.unlink(up)
        up.location, up.rotation_euler = (0, 2, .9), (math.pi, 0, 0)
        up.data.energy, up.data.size = 30, 3.5
        up.data.color = (1, .96, .95)
        receivers(up, 'Ceiling', 'ceiling')
        scene.eevee.use_raytracing = True
    scene['dream_stage'] = 'uv_checker' if checker else 'material_candidate_geometry_and_look_unaccepted'
    scene['dream_material_candidate'] = 'blender/wave_material_plan.json'
    signs = None if checker else details['apply_sign_materials'](scene)
    report = {'schema': 'dream.wave_uv_coverage.v1', 'checker': checker,
              'details': detail_geometry, 'signs': signs,
              'mesh_objects': len(objects), 'coverage': coverage, 'degenerate_uv_faces': bad,
              'floor_hall_max_uv_error_m': max(seam_errors), 'floor_period_m': FLOOR_PERIOD,
              'floor_phase': FLOOR_PHASE, 'floor_offset_u': FLOOR_OFFSET_U,
              'all_closed_faces_assigned': True,
              'geometry_fidelity_accepted': False, 'visual_material_acceptance': False,
              'runtime_exported': False}
    return report


if __name__ == '__main__':
    print(json.dumps(apply()))
