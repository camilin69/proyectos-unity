"""EX-46: third preserved adult, visibly atrophied and posed on the left side."""
import bpy, json, math, os, shutil, sys
from mathutils import Vector

ROOT = 'C:/Users/HP/Documents/GitHub/proyectos-unity'
sys.path.insert(0, ROOT + '/SourceArt/Scripts')
import esn_lib as L
import build_sleeping_adult_ex44 as H

ASSET = 'HUM-03_AdultoDeteriorado'
FOLDER = ROOT + '/SourceArt/_evidence/EX-46/' + ASSET


def remap(point):
    p = Vector(point)
    upper = max(0.0, min(1.0, (p.z - .65) / .9))
    p.x *= .84 + .025 * upper
    p.y *= .91
    p.z = .022 + p.z * .955
    # Coherent lateral curvature through pelvis/spine rather than random vertex noise.
    if p.z > .68:
        p.x += .030 * math.sin(math.pi * min(1.0, (p.z - .68) / 1.05))
    return p


def rig(): return next(o for o in H.SCENE.objects if o.type == 'ARMATURE')


def mesh(atlas): return next(o for o in H.SCENE.objects if o.type == 'MESH' and o.get('atlas') == atlas)


def tag(obj, atlas): obj['atlas'] = atlas; return obj


def wrapped_tube(name, points, radii, material, bone, sides=12):
    return tag(H.tube(name, [tuple(remap(p)) for p in points], radii, material, bone, sides), 'cloth')


def tune_materials():
    values = {
        'skin': ((.285, .245, .215, 1), .72),
        'lip': ((.22, .13, .115, 1), .76),
        'cloth': ((.19, .205, .195, 1), .95),
        'sock': ((.225, .23, .215, 1), .96),
    }
    for key, (color, roughness) in values.items():
        bsdf = next(n for n in H.M[key].node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
        bsdf.inputs['Base Color'].default_value = color; bsdf.inputs['Roughness'].default_value = roughness
    H.M['bandage'] = L.material(ASSET + '_bandage', (.43, .405, .35), .98, 0,
                                bump=.025, scale=260, edge_wear=0, ao=.55)


def add_details():
    # Layered wraps have thickness and staggered edges; they follow the real limb bones.
    for i, z in enumerate((.155, .177, .200, .224)):
        wrapped_tube('ankle_wrap_L_%d' % i,
                     [(-.102, .022, z-.010), (-.104, .021, z+.010)],
                     [(.052, .050), (.053, .051)], 'bandage', 'shin_L', 18)
    for i, z in enumerate((.98, 1.015, 1.05, 1.083)):
        wrapped_tube('forearm_wrap_R_%d' % i,
                     [(.276, -.030, z-.014), (.280, -.025, z+.014)],
                     [(.041, .039), (.042, .040)], 'bandage', 'forearm_R', 18)


def merge_details():
    r = rig()
    for atlas in ('skin','cloth'):
        objects = [o for o in H.SCENE.objects if o.type == 'MESH' and o.get('atlas') == atlas]
        if len(objects) > 1:
            existing = [o for o in objects if o.modifiers.get('Subject rig')]
            if existing: objects.remove(existing[0]); objects.insert(0, existing[0])
            merged = L.join(objects, 'GEO-HUM03-' + atlas.title())
        else: merged = objects[0]; merged.name = 'GEO-HUM03-' + atlas.title()
        merged['atlas'] = atlas; L.uv_project(merged, margin=.008)
        if not any(m.type == 'ARMATURE' for m in merged.modifiers):
            merged.parent = r; mod = merged.modifiers.new('Subject rig','ARMATURE'); mod.object = r


def build():
    os.makedirs(FOLDER, exist_ok=True)
    H.ASSET = ASSET; H.FOLDER = FOLDER; H.build()
    H.SCENE.name = 'EX46_' + ASSET; rig().name = 'RIG-HUM03'
    tune_materials()
    for o in (mesh('skin'), mesh('cloth')):
        for v in o.data.vertices: v.co = remap(v.co)
    with L.ctx(rig()):
        bpy.ops.object.mode_set(mode='EDIT')
        for bone in rig().data.edit_bones: bone.head = remap(bone.head); bone.tail = remap(bone.tail)
        bpy.ops.object.mode_set(mode='OBJECT')
    # Subtle cheek and temple loss follows facial regions, never a global decimate.
    for v in mesh('skin').data.vertices:
        if 1.54 < v.co.z < 1.70 and abs(v.co.x) > .018:
            v.co.x *= .945
    add_details(); merge_details(); report = geometry_report(); save(); return report


def geometry_report():
    meshes=[o for o in H.SCENE.objects if o.type=='MESH']; tris=0
    for o in meshes: o.data.calc_loop_triangles(); tris += len(o.data.loop_triangles)
    report={'asset':ASSET,'triangles':tris,'bones':len(rig().data.bones),'mesh_count':len(meshes),
            'texture_sets':2,'height_m':1.737,
            'pose':'left-side assembly pose pending Unity placement',
            'features':['third slender adult base','coherent pelvis-to-spine lateral curvature',
                        'localized cheek and temple volume loss','layered ankle and forearm wraps',
                        'bald scalp with closed eyes','complete hands and feet'],
            'state':'En produccion'}
    with open(FOLDER+'/geometry.json','w',encoding='utf-8') as f:json.dump(report,f,indent=2,ensure_ascii=False)
    return report


def save(): bpy.data.libraries.write(ROOT+'/SourceArt/Blender/'+ASSET+'.blend',{H.SCENE},fake_user=True)


def render():
    old=L.EVIDENCE;L.EVIDENCE=FOLDER;bpy.context.window.scene=H.SCENE
    try:return L.sheet(ASSET,[o for o in H.SCENE.objects if o.type=='MESH'],views=('front','side','iso'),res=900)
    finally:L.EVIDENCE=old


def bake(atlas):
    bpy.context.window.scene=H.SCENE;rig().data.pose_position='REST';o=mesh(atlas)
    old=L.TEX_DIR;L.TEX_DIR=FOLDER
    try:maps=L.bake_pbr([o],ASSET+'_'+atlas.title(),size=1024,samples=24,margin=3)
    finally:L.TEX_DIR=old
    for suffix,path in maps.items():
        image=bpy.data.images.load(path,check_existing=False);image.pack()
        node=o.data.materials[0].node_tree.nodes.new('ShaderNodeTexImage');node.image=image;node.label='Runtime baked '+suffix
        shutil.copy2(path,ROOT+'/EsneiderProtocoloLazaro/Assets/_Game/Art/Textures/'+os.path.basename(path))
    save()
    with open(FOLDER+'/bake_'+atlas+'.json','w') as f:json.dump(maps,f,indent=2)
    return maps


def animate():
    bpy.context.window.scene=H.SCENE;r=rig();r.data.pose_position='POSE'
    with L.ctx(r):
        bpy.ops.object.mode_set(mode='EDIT')
        for name in ('chest','neck'):r.data.edit_bones[name].use_connect=False
        bpy.ops.object.mode_set(mode='OBJECT')
    r.animation_data_clear();H.SCENE.render.fps=30;H.SCENE.frame_start=1;H.SCENE.frame_end=211
    poses={}
    for frame,amount in ((1,0),(53,.45),(106,1),(159,.30),(211,0)):
        poses[frame]={'chest':((0,0,-3),(0,0,.0018*amount)),
                      'neck':((0,0,2),(0,0,-.0018*amount)),
                      'head':((0,7,4),(0,0,0)),
                      'spine':((0,0,5),(0,0,0))}
    # One small finger response per seven-second loop.
    for frame,angle in ((1,0),(116,0),(124,-4),(134,0),(211,0)):
        poses.setdefault(frame,{})['finger1_R']=((angle,0,0),(0,0,0))
    action=L.action(r,'HUM03_Side_Breathe',211,poses=poses);L.push_nla(r,action);L.enable_nla(r);H.SCENE.frame_set(1);save()
    return {'clip':action.name,'seconds':7,'chest_travel_m':.0018,'finger_response_degrees':4}


def export():
    bpy.context.window.scene=H.SCENE;H.SCENE.frame_set(1);r=rig();r.data.pose_position='POSE';L.enable_nla(r)
    objects=[o for o in H.SCENE.objects if o.type=='MESH'];backups=[]
    for o in objects:
        backups.append((o,o.data));o.data=o.data.copy();mat=o.data.materials[0];o.data.materials.clear();o.data.materials.append(mat)
        for face in o.data.polygons:face.material_index=0
    path=ROOT+'/EsneiderProtocoloLazaro/Assets/_Game/Art/Models/'+ASSET+'.fbx'
    try:
        with L.ctx(objects[0],objects+[r]):
            bpy.ops.export_scene.fbx(filepath=path,use_selection=True,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Z',axis_up='Y',object_types={'MESH','ARMATURE'},add_leaf_bones=False,bake_space_transform=True,mesh_smooth_type='FACE',use_mesh_modifiers=True,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=True,bake_anim_use_all_bones=True,bake_anim_simplify_factor=0,path_mode='STRIP',embed_textures=False)
    finally:
        for o,data in backups:o.data=data
    samples=[dict(zip(('x','y','z'),o.matrix_world@v.co)) for o in objects for v in list(o.data.vertices)[::max(1,len(o.data.vertices)//40)]]
    with open(FOLDER+'/source_coordinates.json','w') as f:json.dump({'vertices':samples},f)
    report=geometry_report();report['unweighted_vertices']=sum(sum(g.weight for g in v.groups)<.999 for o in objects for v in o.data.vertices)
    report['clips']=[strip.action.name for track in r.animation_data.nla_tracks for strip in track.strips]
    report['pose']='seven-second breathing loop; left-side Unity placement pending'
    with open(FOLDER+'/geometry.json','w',encoding='utf-8') as f:json.dump(report,f,indent=2,ensure_ascii=False)
    save();return report


SUPPORT_BATCH=None
def build_support():
    global SUPPORT_BATCH
    from esn_delivery import Batch
    from build_clinic_fixtures_ex23 import FixtureBuilder
    name='HUM-03_SoporteLateral';b=FixtureBuilder('SUPPORT','SoporteLateral','EX46');b.asset=name
    b.m['pad']=L.material(name+'_pad',(.16,.175,.16),.96,0,bump=.018,scale=210,edge_wear=0,ao=.55)
    b.box('base',(1.95,.75,.10),(0,0,.05),'paint',.018)
    b.box('mattress',(1.88,.69,.12),(0,0,.16),'pad',.035)
    b.box('side_body_pad',(1.02,.46,.12),(-.08,.02,.28),'pad',.035)
    b.box('head_pad',(.38,.48,.21),(-.73,.04,.325),'pad',.035)
    for x in (-.82,.82):b.box('floor_skid',(.26,.86,.055),(x,0,.028),'steel',.010)
    for x in (-.55,.02,.58):b.box('support_rib',(.055,.79,.065),(x,0,.085),'steel',.008)
    b.features=['low side-lying platform','sealed mattress with rounded edge','raised side-body cushion',
                'separate head pad','three underframe ribs','two broad floor skids']
    b.collision=[{'center':[0,0,.16],'size':[1.95,.75,.32]}]
    SUPPORT_BATCH=Batch('EX-46',{'SUPPORT':'SoporteLateral'});SUPPORT_BATCH.asset=lambda _:name
    return SUPPORT_BATCH.save(b)


def finish_support():return SUPPORT_BATCH.finish('SUPPORT',size=512,margin=3)
