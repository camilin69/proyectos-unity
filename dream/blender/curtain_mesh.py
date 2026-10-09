"""Deterministic, closed curtain panels for the pastel room.

This module has no bpy dependency and never changes a scene. The caller creates
one mesh object per returned panel, assigns the existing plaid material, and
copies ``face_uvs`` into Blender's loop UVs. Coordinates match build_room.py
*before* its final -1.95 m shift of the window wall.

The shape is a modest static cloth approximation, not a cloth simulation or an
exact reconstruction. Its three broad pleats vary along the drop; the aperture
edge draws slightly away from the window and the hem has a different shape
from the header. UVs stay attached to the cloth coordinates, preserving the
accepted one repeat across / two repeats down plaid mapping.
"""

from __future__ import annotations

import math


def _sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def _unit(a):
    length = math.sqrt(sum(x * x for x in a))
    return tuple(x / length for x in a)


def make_curtain_mesh(center_y, *, aperture_side=1, x_plane=2.15,
                      width=0.34, bottom_z=1.25, height=1.43,
                      thickness=0.0016, segments_u=32, segments_v=16):
    """Return vertices, quads, loop UVs, smoothing flags and topology metadata.

    ``aperture_side`` is +1 when the aperture is toward increasing Y, otherwise
    -1. Defaults therefore fit the panel centered at Y=.6; the panel at Y=1.75
    uses -1. The mid-surface remains inside center_y +/- width/2. The physical
    shell extends by at most half its thickness beyond that envelope.

    Quads are outward wound. Front/back each carry the same cloth UVs; they are
    reversed in face order rather than mirroring or resetting the texture.
    Boundary quads close all four edges. ``sharp_edges`` can be marked sharp
    on the Blender mesh so its tiny flat rim does not round into the cloth.
    """
    if aperture_side not in (-1, 1):
        raise ValueError('aperture_side must be -1 or +1')
    if segments_u < 18 or segments_v < 8:
        raise ValueError('At least 18 x 8 segments are needed for soft pleats')
    if not all(math.isfinite(x) for x in
               (center_y, x_plane, width, bottom_z, height, thickness)):
        raise ValueError('Curtain dimensions must be finite')
    if min(width, height, thickness) <= 0 or thickness > 0.01 * width:
        raise ValueError('Use positive dimensions and a thin cloth shell')

    def surface(u, v):
        t = 1.0 - v  # distance down from the header
        s = u if aperture_side == 1 else 1.0 - u
        inner_inset = 0.028 * math.sin(math.pi * t) ** 1.35 + 0.012 * t
        outer_inset = 0.007 * math.sin(math.pi * t) + 0.003 * t
        lateral = ((s - 0.5) * width + outer_inset * (1.0 - s)
                   - inner_inset * s)
        y = center_y + aperture_side * lateral

        # Irregular spacing is fixed to the cloth. Slow phase changes avoid
        # uniform extruded corrugation, while keeping only three broad folds.
        phase = math.tau * (3.0 * s + 0.046 * math.sin(math.tau * s + 0.3)
                            + 0.062 * t * math.sin(math.pi * s + 0.7)
                            + 0.017 * t * t)
        amplitude = (0.027 + 0.013 * math.sin(math.pi * t) + 0.009 * t)
        amplitude *= 0.92 + 0.08 * math.cos(math.tau * s + 0.5)
        pleat = amplitude * (0.86 * math.cos(phase)
                             + 0.14 * math.cos(2.0 * phase + 0.8))
        bow = 0.017 * math.sin(math.pi * t) * (0.6 + 0.4 * s) + 0.014 * t*t
        x = x_plane + pleat - bow

        # Header stays close to the rail; the hem is independently uneven and
        # varies by less than 2 cm, rather than repeating the pleat sinusoid.
        hem = (0.018 * t**4 * (0.35 + 0.65 * s)
               + 0.004 * math.sin(math.tau * s + 0.2) * t*t)
        header_sag = 0.004 * math.sin(math.pi * s)**2 * v**10
        z = bottom_z + height * v + hem - header_sag
        return (x, y, z)

    nu, nv = segments_u, segments_v
    row = nu + 1
    mid, normals, cloth_uvs = [], [], []
    epsilon = 1e-5
    for j in range(nv + 1):
        v = j / nv
        for i in range(nu + 1):
            u = i / nu
            mid.append(surface(u, v))
            lo_u, hi_u = max(0.0, u - epsilon), min(1.0, u + epsilon)
            lo_v, hi_v = max(0.0, v - epsilon), min(1.0, v + epsilon)
            du = _sub(surface(hi_u, v), surface(lo_u, v))
            dv = _sub(surface(u, hi_v), surface(u, lo_v))
            normals.append(_unit(_cross(dv, du)))  # facing into room (-X)
            cloth_uvs.append((u, 2.0 * v))

    n = len(mid)
    half = thickness * 0.5
    vertices = [tuple(p[k] + half * normal[k] for k in range(3))
                for p, normal in zip(mid, normals)]
    vertices += [tuple(p[k] - half * normal[k] for k in range(3))
                 for p, normal in zip(mid, normals)]
    faces, face_uvs, smooth_faces = [], [], []
    boundary = {}
    for j in range(nv):
        for i in range(nu):
            a = j * row + i
            face = (a, a + row, a + row + 1, a + 1)
            faces.append(face)
            face_uvs.append(tuple(cloth_uvs[k] for k in face))
            smooth_faces.append(True)
            for first, second in zip(face, face[1:] + face[:1]):
                if (second, first) in boundary:
                    del boundary[second, first]
                else:
                    boundary[first, second] = True
    front_face_count = len(faces)
    for front in faces[:front_face_count]:
        back = tuple(k + n for k in reversed(front))
        faces.append(back)
        face_uvs.append(tuple(cloth_uvs[k - n] for k in back))
        smooth_faces.append(True)

    sharp_edges = []
    for a, b in boundary:
        faces.append((b, a, a + n, b + n))
        # Each rim takes the UV at its sewn perimeter. Its microscopic depth
        # deliberately samples that same color instead of adding an atlas seam.
        face_uvs.append((cloth_uvs[b], cloth_uvs[a], cloth_uvs[a], cloth_uvs[b]))
        smooth_faces.append(False)
        sharp_edges.extend(((a, b), (a + n, b + n)))

    bounds = {name: [min(p[axis] for p in vertices), max(p[axis] for p in vertices)]
              for axis, name in enumerate(('x', 'y', 'z'))}
    topology = {
        'version': 'curtain-static-drape-v7',
        'vertices': len(vertices), 'quads': len(faces),
        'triangles_after_triangulation': 2 * len(faces),
        'surface_quads_per_side': front_face_count, 'rim_quads': len(boundary),
        'expected_euler_characteristic': 2,
        'expected_edge_face_incidence': 2,
        'bounds_before_window_wall_shift_m': bounds,
        'parameters': {
            'center_y': center_y, 'aperture_side': aperture_side,
            'x_plane': x_plane, 'width': width, 'bottom_z': bottom_z,
            'height': height, 'thickness': thickness,
            'segments_u': nu, 'segments_v': nv, 'broad_pleats': 3,
            'uv_repeat_u': 1.0, 'uv_repeat_v': 2.0,
        },
        'construction': 'Two offset surfaces, shared closed rim; no modifiers or simulation.',
        'uv_policy': 'Fixed material coordinates per grid vertex; matching front/back, flat rim.',
    }
    return {'vertices': vertices, 'faces': faces, 'face_uvs': face_uvs,
            'smooth_faces': smooth_faces, 'sharp_edges': sharp_edges,
            'topology': topology}


def make_room_curtains(wy0=0.7, wy1=1.65):
    """The room's two panels, ready for two mesh objects (no extra objects)."""
    return [make_curtain_mesh(wy0 - 0.10, aperture_side=1),
            make_curtain_mesh(wy1 + 0.10, aperture_side=-1)]
