"""EX-45: second adult base with a localized left-arm graft and cervical brace.

The anatomical topology and 30-bone contract intentionally derive from HUM-01, but
the proportions, removed limb geometry, implant, restraint details, materials and
ambient clip are authored as a distinct source asset.
"""
import bpy, bmesh, json, math, os, shutil, sys
from mathutils import Vector

ROOT = 'C:/Users/HP/Documents/GitHub/proyectos-unity'
sys.path.insert(0, ROOT + '/SourceArt/Scripts')
import esn_lib as L
import build_sleeping_adult_ex44 as H

ASSET = 'HUM-02_AdultoInjertos'
FOLDER = ROOT + '/SourceArt/_evidence/EX-45/' + ASSET


def remap(point):
    """Broader upper body, shorter legs and deeper torso than HUM-01."""
    p = Vector(point)
    upper = max(0.0, min(1.0, (p.z - .72) / .78))
    p.x *= .94 + .14 * upper
    p.y *= 1.055
    p.z = .025 + p.z * .972
    return p


def _rig():
    return next(o for o in H.SCENE.objects if o.type == 'ARMATURE')


def _mesh(atlas):
    return next(o for o in H.SCENE.objects if o.type == 'MESH' and o.get('atlas') == atlas)


def _tag(obj, atlas):
    obj['atlas'] = atlas
    return obj


def graft_tube(name, points, radii, material, bone, sides=12, atlas='implant'):
    o = H.tube(name, [tuple(remap(p)) for p in points], radii, material, bone, sides)
    return _tag(o, atlas)


def graft_sphere(name, point, scale, material, bone, segs=16, rings=10, atlas='implant'):
    p = remap(point)
    upper = max(0.0, min(1.0, (point[2] - .72) / .78))
    s = (.94 + .14 * upper, 1.055, .972)
    o = H.sphere(name, tuple(p), tuple(scale[i] * s[i] for i in range(3)), material, bone, segs, rings)
    return _tag(o, atlas)


def remove_biological_left_arm(skin):
    bm = bmesh.new(); bm.from_mesh(skin.data)
    doomed = []
    for f in bm.faces:
        c = f.calc_center_median()
        if c.x < -.215 and .77 < c.z < 1.32:
            doomed.append(f)
    bmesh.ops.delete(bm, geom=doomed, context='FACES')
    loose = [v for v in bm.verts if not v.link_faces]
    if loose: bmesh.ops.delete(bm, geom=loose, context='VERTS')
    bm.to_mesh(skin.data); bm.free(); skin.data.update()


def compress_cloth_under_brace(cloth):
    for v in cloth.data.vertices:
        # The gown is pressed inward only under the collar and two restraint pads.
        if 1.34 < v.co.z < 1.46 and v.co.y < -.025:
            weight = max(0.0, 1.0 - abs(v.co.x) / .19)
            v.co.y += .0045 * weight


def merge_atlases():
    rig = _rig()
    for atlas in ('skin', 'cloth', 'implant'):
        objects = [o for o in H.SCENE.objects if o.type == 'MESH' and o.get('atlas') == atlas]
        if len(objects) > 1:
            existing = [o for o in objects if o.modifiers.get('Subject rig')]
            if existing:
                objects.remove(existing[0]); objects.insert(0, existing[0])
            merged = L.join(objects, 'GEO-HUM02-' + atlas.title())
        else:
            merged = objects[0]; merged.name = 'GEO-HUM02-' + atlas.title()
        merged['atlas'] = atlas
        L.uv_project(merged, margin=.008)
        if not any(m.type == 'ARMATURE' for m in merged.modifiers):
            merged.parent = rig
            mod = merged.modifiers.new('Subject rig', 'ARMATURE'); mod.object = rig


def add_implant():
    H.M.update({
        'implant': L.material(ASSET + '_implant', (.19, .22, .225), .34, 1.0,
                              wear=.16, edge_color=(.10, .11, .115), bump=.008, scale=150, ao=.7),
        'polymer': L.material(ASSET + '_polymer', (.10, .13, .125), .72, 0.0,
                              wear=.04, bump=.012, scale=190, ao=.65),
        'scar': L.material(ASSET + '_scar', (.285, .105, .075), .68, 0.0,
                           bump=.01, scale=220, edge_wear=0, ao=0),
        'pad': L.material(ASSET + '_brace_pad', (.13, .16, .15), .92, 0.0,
                          bump=.018, scale=210, edge_wear=0, ao=.5),
    })
    # Localized scar and compression ring: it bridges tissue and the mechanical cuff.
    graft_tube('scar_transition_L', [(-.246, .012, 1.323), (-.263, .013, 1.286)],
               [(.064, .061), (.061, .058)], 'scar', 'upperarm_L', 24, 'skin')
    graft_tube('graft_cuff_L', [(-.259, .012, 1.304), (-.278, .014, 1.248)],
               [(.071, .067), (.065, .061)], 'polymer', 'upperarm_L', 24)
    # Load-bearing upper link, elbow joint, forearm shell and visible service cable.
    graft_tube('upper_link_L', [(-.272, .014, 1.266), (-.298, .015, 1.154)],
               [(.045, .041), (.041, .039)], 'implant', 'upperarm_L', 14)
    graft_sphere('elbow_joint_L', (-.298, .015, 1.15), (.058, .052, .056), 'implant', 'forearm_L', 20, 12)
    graft_tube('forearm_shell_L', [(-.299, .012, 1.136), (-.307, -.006, 1.065), (-.302, -.028, .987), (-.300, -.043, .925)],
               [(.049, .045), (.047, .043), (.041, .037), (.034, .031)], 'polymer', 'forearm_L', 18)
    graft_tube('forearm_rail_outer_L', [(-.335, .025, 1.135), (-.343, .001, 1.045), (-.331, -.032, .944)],
               [.010, .009, .008], 'implant', 'forearm_L', 10)
    graft_tube('forearm_rail_inner_L', [(-.263, .022, 1.135), (-.267, -.001, 1.045), (-.272, -.037, .944)],
               [.010, .009, .008], 'implant', 'forearm_L', 10)
    graft_tube('service_cable_L', [(-.246, .044, 1.278), (-.253, .061, 1.19), (-.279, .050, 1.08), (-.282, .005, .969)],
               [.006, .006, .0055, .0045], 'polymer', 'forearm_L', 10)
    graft_sphere('wrist_socket_L', (-.300, -.047, .916), (.041, .035, .040), 'implant', 'hand_L', 18, 10)
    graft_tube('palm_frame_L', [(-.300, -.052, .917), (-.300, -.055, .842)],
               [(.039, .022), (.034, .019)], 'polymer', 'hand_L', 16)
    for i, x in enumerate((-.329, -.311, -.293, -.275)):
        bone = 'finger%d_L' % i
        length = (.066, .077, .071, .055)[i]
        graft_tube('digit_L%d' % i, [(x, -.055, .858), (x - .002, -.064, .825), (x - .003, -.074, .858 - length)],
                   [.0085, .0075, .0055], 'implant', bone, 8)
    graft_tube('thumb_L', [(-.267, -.054, .888), (-.248, -.064, .861), (-.240, -.074, .836)],
               [.012, .010, .005], 'implant', 'thumb_L', 9)

    # Open-front cervical brace and sternum pads; no tube passes through the body.
    arc = []
    for i in range(22):
        a = math.radians(38 + i * (284 / 21))
        arc.append((.072 * math.sin(a), .018 + .061 * math.cos(a), 1.505 + .005 * math.cos(a)))
    graft_tube('cervical_brace', arc, [.012] * len(arc), 'polymer', 'neck', 10)
    for side in (-1, 1):
        graft_tube('brace_shoulder_%s' % side,
                   [(side * .055, -.047, 1.48), (side * .115, -.058, 1.43), (side * .155, -.054, 1.37)],
                   [(.026, .015), (.030, .016), (.025, .014)], 'pad', 'chest', 12)
    graft_tube('brace_sternum', [(0, -.072, 1.455), (0, -.083, 1.37), (0, -.078, 1.30)],
               [(.025, .012), (.032, .014), (.027, .012)], 'polymer', 'chest', 12)
    for z in (1.39, 1.335):
        graft_tube('pressure_band_%.3f' % z,
                   [(-.17, -.073, z), (-.09, -.096, z - .006), (0, -.103, z - .009), (.09, -.096, z - .006), (.17, -.073, z)],
                   [.010] * 5, 'pad', 'chest', 10)


def build():
    os.makedirs(FOLDER, exist_ok=True)
    H.ASSET = ASSET; H.FOLDER = FOLDER
    H.build()
    H.SCENE.name = 'EX45_' + ASSET
    rig = _rig(); rig.name = 'RIG-HUM02'
    skin = _mesh('skin'); cloth = _mesh('cloth')
    # Remap both mesh data and armature rest coordinates with the same function.
    for o in (skin, cloth):
        for v in o.data.vertices: v.co = remap(v.co)
    with L.ctx(rig):
        bpy.ops.object.mode_set(mode='EDIT')
        for bone in rig.data.edit_bones:
            bone.head = remap(bone.head); bone.tail = remap(bone.tail)
        bpy.ops.object.mode_set(mode='OBJECT')
    remove_biological_left_arm(skin)
    compress_cloth_under_brace(cloth)
    add_implant(); merge_atlases()
    report = geometry_report()
    save(); return report


def geometry_report():
    meshes = [o for o in H.SCENE.objects if o.type == 'MESH']
    tris = 0
    for o in meshes: o.data.calc_loop_triangles(); tris += len(o.data.loop_triangles)
    report = {
        'asset': ASSET, 'triangles': tris, 'bones': len(_rig().data.bones),
        'mesh_count': len(meshes), 'texture_sets': 3, 'height_m': 1.77,
        'pose': 'reclined restraint source pose pending Unity assembly',
        'features': ['distinct broad-shouldered adult base', 'left biological arm removed below graft',
                     'scar-to-polymer transition cuff', 'articulated implant with rails and service cable',
                     'four mechanical digits and thumb', 'open-front cervical brace',
                     'gown compression beneath restraint pads'],
        'state': 'En produccion'
    }
    with open(FOLDER + '/geometry.json', 'w', encoding='utf-8') as f: json.dump(report, f, indent=2, ensure_ascii=False)
    return report


def save():
    bpy.data.libraries.write(ROOT + '/SourceArt/Blender/' + ASSET + '.blend', {H.SCENE}, fake_user=True)


def render():
    old = L.EVIDENCE; L.EVIDENCE = FOLDER; bpy.context.window.scene = H.SCENE
    try: return L.sheet(ASSET, [o for o in H.SCENE.objects if o.type == 'MESH'], views=('front', 'side', 'iso'), res=900)
    finally: L.EVIDENCE = old


def bake(atlas):
    bpy.context.window.scene = H.SCENE
    rig = _rig(); rig.data.pose_position = 'REST'
    obj = _mesh(atlas)
    old = L.TEX_DIR; L.TEX_DIR = FOLDER
    try: maps = L.bake_pbr([obj], ASSET + '_' + atlas.title(), size=1024 if atlas != 'implant' else 512, samples=24, margin=3)
    finally: L.TEX_DIR = old
    for suffix, path in maps.items():
        image = bpy.data.images.load(path, check_existing=False); image.pack()
        node = obj.data.materials[0].node_tree.nodes.new('ShaderNodeTexImage'); node.image = image; node.label = 'Runtime baked ' + suffix
        shutil.copy2(path, ROOT + '/EsneiderProtocoloLazaro/Assets/_Game/Art/Textures/' + os.path.basename(path))
    save()
    with open(FOLDER + '/bake_' + atlas + '.json', 'w', encoding='utf-8') as f: json.dump(maps, f, indent=2)
    return maps


def animate():
    bpy.context.window.scene = H.SCENE; rig = _rig(); rig.data.pose_position = 'POSE'
    with L.ctx(rig):
        bpy.ops.object.mode_set(mode='EDIT')
        for name in ('chest', 'neck'): rig.data.edit_bones[name].use_connect = False
        bpy.ops.object.mode_set(mode='OBJECT')
    rig.animation_data_clear(); H.SCENE.render.fps = 30; H.SCENE.frame_start = 1; H.SCENE.frame_end = 181
    poses = {}
    for frame, breath in ((1, 0), (46, .55), (91, 1), (136, .38), (181, 0)):
        poses[frame] = {'chest': ((0, 0, 0), (0, 0, .0023 * breath)),
                        'neck': ((0, 0, 0), (0, 0, -.0023 * breath)),
                        'head': ((0, 4, 0), (0, 0, 0))}
    # A restrained mechanical adjustment, roughly 3 mm at the hand, followed by release.
    for frame, angle in ((1, 0), (68, 0), (74, .65), (82, 0), (181, 0)):
        poses.setdefault(frame, {})['forearm_L'] = ((angle, 0, 0), (0, 0, 0))
    action = L.action(rig, 'HUM02_Restrained_Breathe', 181, poses=poses)
    L.push_nla(rig, action); L.enable_nla(rig); H.SCENE.frame_set(1); save()
    return {'clip': action.name, 'seconds': 6, 'chest_travel_m': .0023, 'implant_joint_degrees': .65}


def export():
    bpy.context.window.scene = H.SCENE; H.SCENE.frame_set(1)
    rig = _rig(); rig.data.pose_position = 'POSE'; L.enable_nla(rig)
    objects = [o for o in H.SCENE.objects if o.type == 'MESH']; backups = []
    for o in objects:
        backups.append((o, o.data)); o.data = o.data.copy(); mat = o.data.materials[0]
        o.data.materials.clear(); o.data.materials.append(mat)
        for face in o.data.polygons: face.material_index = 0
    path = ROOT + '/EsneiderProtocoloLazaro/Assets/_Game/Art/Models/' + ASSET + '.fbx'
    try:
        with L.ctx(objects[0], objects + [rig]):
            bpy.ops.export_scene.fbx(filepath=path, use_selection=True, apply_unit_scale=True,
                apply_scale_options='FBX_SCALE_ALL', axis_forward='-Z', axis_up='Y',
                object_types={'MESH', 'ARMATURE'}, add_leaf_bones=False, bake_space_transform=True,
                mesh_smooth_type='FACE', use_mesh_modifiers=True, bake_anim=True,
                bake_anim_use_all_actions=False, bake_anim_use_nla_strips=True,
                bake_anim_use_all_bones=True, bake_anim_simplify_factor=0, path_mode='STRIP', embed_textures=False)
    finally:
        for o, data in backups: o.data = data
    samples = [dict(zip(('x', 'y', 'z'), o.matrix_world @ v.co)) for o in objects for v in list(o.data.vertices)[::max(1, len(o.data.vertices)//40)]]
    with open(FOLDER + '/source_coordinates.json', 'w', encoding='utf-8') as f: json.dump({'vertices': samples}, f)
    report = geometry_report()
    report['unweighted_vertices'] = sum(sum(g.weight for g in v.groups) < .999 for o in objects for v in o.data.vertices)
    report['clips'] = [strip.action.name for track in rig.animation_data.nla_tracks for strip in track.strips]
    report['pose'] = 'restrained breathing loop; reclined Unity placement pending'
    with open(FOLDER + '/geometry.json', 'w', encoding='utf-8') as f: json.dump(report, f, indent=2, ensure_ascii=False)
    save(); return report


SUPPORT_BATCH = None
def build_support():
    """Vertical restraint rack; Unity reclines the complete human/rack assembly."""
    global SUPPORT_BATCH
    from esn_delivery import Batch
    from build_clinic_fixtures_ex23 import FixtureBuilder
    name = 'HUM-02_SoporteInclinado'
    b = FixtureBuilder('SUPPORT', 'SoporteInclinado', 'EX45'); b.asset = name
    b.m['pad'] = L.material(name + '_pad', (.10, .125, .12), .91, 0,
                            bump=.018, scale=190, edge_wear=0, ao=.55)
    b.m['clean'] = L.material(name + '_maintained_metal', (.29, .32, .31), .34, 1,
                              wear=.025, edge_color=(.14, .15, .15), bump=.006, scale=90, ao=.7)
    # A structural spine and two rails support the load; the body contacts pads, not metal.
    b.box('back_spine', (.18, .10, 1.72), (0, .115, .91), 'paint', .018)
    for x in (-.34, .34):
        b.box('side_rail', (.065, .095, 1.78), (x, .105, .92), 'clean', .012)
        b.box('floor_foot', (.12, .74, .07), (x, .20, .035), 'clean', .010)
    for z in (.18, .72, 1.18, 1.70):
        b.box('crossmember', (.74, .075, .055), (0, .105, z), 'clean', .008)
    for z, w, h in ((.42, .48, .30), (.93, .58, .36), (1.34, .54, .31), (1.59, .28, .17)):
        b.box('pressure_pad', (w, .085, h), (0, .025, z), 'pad', .025)
    # Heel cups and sole plates transfer weight to the base.
    for x in (-.115, .115):
        b.box('foot_plate', (.19, .33, .045), (x, -.075, .075), 'pad', .012)
        b.box('heel_stop', (.19, .055, .12), (x, .065, .13), 'clean', .008)
    # Open cervical cradle: two pads leave airway/front unobstructed.
    for side in (-1, 1):
        b.tube('neck_cradle', [(side*.18, .08, 1.56), (side*.13, -.005, 1.61), (side*.085, -.035, 1.62)], .025, 'pad')
        b.box('shoulder_stop', (.15, .095, .07), (side*.22, -.005, 1.48), 'pad', .015)
    b.features = ['load-bearing spine and twin rails', 'four anatomical pressure pads',
                  'separate heel cups and sole plates', 'open cervical cradle',
                  'broad floor feet for a reclined installation']
    b.collision = [{'center':[0,.08,.92], 'size':[.80,.20,1.84]}]
    SUPPORT_BATCH = Batch('EX-45', {'SUPPORT':'SoporteInclinado'}); SUPPORT_BATCH.asset = lambda _: name
    return SUPPORT_BATCH.save(b)


def finish_support():
    return SUPPORT_BATCH.finish('SUPPORT', size=512, margin=3)
