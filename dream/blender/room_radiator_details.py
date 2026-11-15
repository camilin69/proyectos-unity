"""Add the six lower radiator connection pieces to DREAM_PastelRoom.

Shared by build_room.py and an incremental Blender MCP call. This module does
not run, save, render or export on import. The pure specification function can
be inspected without Blender; apply_radiator_returns requires live bpy.
"""
import math


PREFIX = 'GEO-DREAM-radiator_return_'


def radiator_return_specs(wall_shift_x=-1.95):
    """World-metre seeds inferred from video-35 at 11s and 24s, not recovered CAD.

    Reuse the existing lower collector's x/z and its end y coordinates. Small
    external stubs connect to drops penetrating the floor coating (.016) by
    one centimetre, so no artificial gap remains at the pipe entry.
    Neither the 24 fins nor the window, radiator body or camera move.
    """
    x = 2.23 + wall_shift_x
    specs = []
    for side, collector_y, drop_y in [('near', .08, .045), ('far', 1.10, 1.135)]:
        specs.extend([
            {'name': PREFIX + side + '_stub', 'a': (x, collector_y, .22),
             'b': (x, drop_y, .22), 'radius': .014},
            {'name': PREFIX + side + '_drop', 'a': (x, drop_y, .22),
             'b': (x, drop_y, .006), 'radius': .012},
            {'name': PREFIX + side + '_collar', 'a': (x, drop_y, .201),
             'b': (x, drop_y, .239), 'radius': .022},
        ])
    return specs


def apply_radiator_returns(scene=None, material=None):
    """Idempotent data-only update, safe while another scene is active.

    Only PREFIX objects in DREAM_PastelRoom are replaced. Existing collections,
    geometry/UVs, lights, camera and scene selection are preserved. New pieces
    join the existing radiator/full receiver collections if those exist, which
    gives the incremental update the same light linking as a full room build.
    """
    import bpy
    from mathutils import Vector

    scene = scene or bpy.data.scenes.get('DREAM_PastelRoom')
    if scene is None or scene.name != 'DREAM_PastelRoom':
        raise ValueError('Expected existing DREAM_PastelRoom scene')
    fins = [o for o in scene.objects if o.name.startswith('GEO-DREAM-radiator_fin')]
    if not fins:
        raise ValueError('Existing radiator fins are required')
    material = material or fins[0].active_material
    if material is None or material.get('metallic') != 1 or material.get('kind') != 0:
        raise ValueError('Expected the existing room chrome material')

    specs = radiator_return_specs()
    owned = [o for o in scene.objects if o.name.startswith(PREFIX)]
    if any(other != scene for obj in owned for other in obj.users_scene):
        raise ValueError('Radiator detail object is shared with another scene')
    for spec in specs:
        existing = bpy.data.objects.get(spec['name'])
        if existing is not None and existing not in owned:
            raise ValueError('Radiator detail name belongs to another scene: ' + spec['name'])
    for obj in owned:
        mesh = obj.data if obj.type == 'MESH' else None
        bpy.data.objects.remove(obj, do_unlink=True)
        if mesh is not None and mesh.users == 0:
            bpy.data.meshes.remove(mesh)

    created = []
    segments = 12  # Same tube tessellation as the existing radiator.
    for spec in specs:
        a, b = Vector(spec['a']), Vector(spec['b'])
        delta = b - a
        radius = spec['radius']
        vertices = [(radius * math.cos(i * 2 * math.pi / segments),
                     radius * math.sin(i * 2 * math.pi / segments), z)
                    for z in (-delta.length / 2, delta.length / 2)
                    for i in range(segments)]
        faces = [(i, (i + 1) % segments, (i + 1) % segments + segments, i + segments)
                 for i in range(segments)]
        faces += [tuple(reversed(range(segments))), tuple(range(segments, 2 * segments))]
        mesh = bpy.data.meshes.new(spec['name'] + '_mesh')
        mesh.from_pydata(vertices, [], faces)
        mesh.materials.append(material)
        mesh.update()
        uv = mesh.uv_layers.new(name='CylinderSurface')
        for poly in mesh.polygons:
            poly.use_smooth = len(poly.vertices) == 4
            if poly.index < segments:
                i = poly.index
                coords = [(i / segments, 0), ((i + 1) / segments, 0),
                          ((i + 1) / segments, 1), (i / segments, 1)]
            else:
                coords = [(vertices[v][0] / (2 * radius) + .5,
                           vertices[v][1] / (2 * radius) + .5) for v in poly.vertices]
            for loop, coord in zip(poly.loop_indices, coords):
                uv.data[loop].uv = coord
        for edge in mesh.edges:
            edge.use_edge_sharp = abs(vertices[edge.vertices[0]][2] - vertices[edge.vertices[1]][2]) < 1e-6
        obj = bpy.data.objects.new(spec['name'], mesh)
        scene.collection.objects.link(obj)
        obj.location = (a + b) / 2
        obj.rotation_euler = delta.to_track_quat('Z', 'Y').to_euler()
        for name in ['DREAM_chrome_strip_receivers', 'DREAM_reference_full_receivers']:
            collection = bpy.data.collections.get(name)
            if collection is not None:
                collection.objects.link(obj)
        created.append(obj.name)
    return {'scene': scene.name, 'objects_added': created, 'count': len(created),
            'specification': specs, 'saved': False, 'rendered': False, 'exported': False}
