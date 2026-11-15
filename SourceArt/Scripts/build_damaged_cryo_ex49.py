"""EX-49 / OBJ-002: source-locked damaged variant of OBJ-001_Criocamara."""
import bpy, bmesh, importlib, json, math, os, shutil, sys
from mathutils import Vector

ROOT = r"C:/Users/HP/Documents/GitHub/proyectos-unity"
sys.path.insert(0, ROOT + "/SourceArt/Scripts")
import esn_lib as L
importlib.reload(L)

ASSET = "OBJ-002_CamaraVaciaDanada"
FOLDER = ROOT + "/SourceArt/_evidence/EX-49/" + ASSET
SOURCE = ROOT + "/SourceArt/Blender/OBJ-001_Criocamara.blend"
SCENE = None


def _activate():
    global SCENE
    if SCENE is not None and SCENE.name in bpy.data.scenes:
        bpy.context.window.scene = SCENE
        return SCENE
    found = bpy.data.scenes.get("EX49_" + ASSET)
    if found:
        SCENE = found; bpy.context.window.scene = found; return found
    raise RuntimeError("Run build() first")


def _object(name):
    scene = _activate()
    return next((o for o in scene.objects if o.name == name), None)


def _copy_mesh(o):
    o.data = o.data.copy()
    return o


def _delete_glass_wedge(o):
    _copy_mesh(o)
    bm = bmesh.new(); bm.from_mesh(o.data)
    doomed = []
    for f in bm.faces:
        c = f.calc_center_median()
        if c.x > .32 and c.y < -.08 and c.z > .66:
            doomed.append(f)
    bmesh.ops.delete(bm, geom=doomed, context='FACES')
    bm.to_mesh(o.data); bm.free(); o.data.update()


def _triangle_prism(name, points, thickness, collection, material):
    a, b, c = [Vector(p) for p in points]
    n = (b-a).cross(c-a).normalized() * (thickness * .5)
    verts = [a+n, b+n, c+n, a-n, b-n, c-n]
    faces = [(0,1,2), (5,4,3), (0,3,4,1), (1,4,5,2), (2,5,3,0)]
    mesh = bpy.data.meshes.new(name + "_mesh"); mesh.from_pydata(verts, [], faces); mesh.update()
    obj = bpy.data.objects.new(name, mesh); collection.objects.link(obj); L.assign(obj, material)
    L.uv_project(obj, .004); return obj


def build():
    global SCENE
    os.makedirs(FOLDER, exist_ok=True)
    with bpy.data.libraries.load(SOURCE, link=False) as (src, dst):
        dst.scenes = src.scenes[:1]
    SCENE = dst.scenes[0]; SCENE.name = "EX49_" + ASSET; bpy.context.window.scene = SCENE
    collection = SCENE.collection
    arm = next(o for o in SCENE.objects if o.type == 'ARMATURE')

    # Damage has one mechanical cause: the front-right lid corner was forced while latched.
    lid = _copy_mesh(_object("lid_frame"))
    for v in lid.data.vertices:
        if v.co.x > .22 and v.co.y < -.10:
            k = min(1., (v.co.x-.22)/.95) * min(1., (-v.co.y-.10)/.38)
            v.co.z += .065*k; v.co.y -= .025*k
    lid.data.update()
    base = _copy_mesh(_object("base"))
    for v in base.data.vertices:
        if .42 < v.co.x < 1.0 and v.co.y < -.46 and .18 < v.co.z < .52:
            k = (1-abs(v.co.x-.71)/.29) * (1-abs(v.co.z-.35)/.17)
            v.co.y += max(0., k) * .042
    base.data.update()

    glass = _object("lid_glass"); frost = _object("lid_frost")
    _delete_glass_wedge(glass); _delete_glass_wedge(frost)
    glass_mat = glass.data.materials[0]
    steel = next(m for m in bpy.data.materials if m.name.startswith("M_SteelBare"))
    fabric = next(m for m in bpy.data.materials if m.name.startswith("M_Fabric"))

    # Thick retained shards follow the lid; small splinters are represented by only four readable pieces.
    shards = []
    shard_specs = [
        ((.35,-.19,.745),(.61,-.24,.73),(.47,-.38,.705)),
        ((.60,-.20,.73),(.82,-.14,.69),(.76,-.35,.675)),
        ((.33,-.18,.744),(.46,-.38,.706),(.24,-.34,.72)),
        ((.80,-.15,.69),(.99,-.08,.64),(.78,-.34,.674)),
    ]
    for i, pts in enumerate(shard_specs):
        s = _triangle_prism("broken_glass_%02d" % i, pts, .006, collection, glass_mat)
        L.bind_rigid(s, arm, "lid"); shards.append(s)

    # Bent keeper and torn reinforcement expose bare metal exactly at the failed latch.
    keeper = _object("lid_keeper1")
    if keeper: keeper.rotation_euler.z += math.radians(17); keeper.location += Vector((.015,-.018,.018))
    tear = L.box("impact_torn_lip", (.34,.035,.018), (.66,-.485,.755), collection,
                 rot=(0, math.radians(-7), math.radians(8)), bevel=.002, segs=2)
    L.assign(tear, steel); L.bind_rigid(tear, arm, "lid")

    # A shallow, matte body imprint remains on the empty bed; it is geometry, not baked text.
    residue_mat = L.material("M_OBJ002_Residue", (.12,.055,.045), .92, 0.0, bump=.18, scale=22)
    imprint = L.sphere("previous_subject_imprint", 1, (.05,0,.794), collection, segs=32, rings=10,
                       scale=(.72,.19,.008))
    L.assign(imprint, residue_mat); L.uv_project(imprint, .01); L.bind_rigid(imprint, arm, "root")
    scrape = L.box("impact_scrape", (.42,.008,.075), (.70,-.556,.40), collection,
                   rot=(math.radians(4),0,math.radians(-8)), bevel=.002, segs=1)
    L.assign(scrape, steel); L.uv_project(scrape,.004); L.bind_rigid(scrape, arm,"root")

    # The failed motor makes one uneven attempt and settles at 48 degrees: the bed and failed corner stay readable.
    if arm.animation_data:
        for track in list(arm.animation_data.nla_tracks): arm.animation_data.nla_tracks.remove(track)
    Z=(0,0,0)
    poses={1:{"lid":((48,0,0),Z),"latch_L":((0,0,0),Z),"latch_R":((0,0,0),Z)},
           9:{"latch_L":((0,18,0),Z),"latch_R":((0,-6,0),Z)},
           17:{"lid":((63,0,2),Z)}, 25:{"lid":((43,0,-1),Z)},
           33:{"lid":((57,0,1),Z)}, 45:{"lid":((46,0,0),Z)},
           60:{"lid":((48,0,0),Z),"latch_L":((0,9,0),Z),"latch_R":((0,-4,0),Z)}}
    L.push_nla(arm, L.action(arm,"Cryo_Damaged_Jam",60,loop=False,poses=poses))
    L.push_nla(arm, L.action(arm,"Cryo_Damaged_Rest",2,loop=False,poses={1:{"lid":((48,0,0),Z)}}))

    for o in SCENE.objects:
        if o.type == 'MESH': L.smooth(o,40)
    bpy.context.view_layer.update()
    bpy.data.libraries.write(ROOT+"/SourceArt/Blender/"+ASSET+".blend", {SCENE}, fake_user=True)
    return geometry_report()


def geometry_report():
    scene=_activate(); objs=[o for o in scene.objects if o.type=='MESH']; points=[]; tris=0
    for o in objs:
        o.data.calc_loop_triangles(); tris += len(o.data.loop_triangles)
        points.extend(o.matrix_world @ v.co for v in o.data.vertices)
    dims=[max(p[i] for p in points)-min(p[i] for p in points) for i in range(3)]
    report={"asset":ASSET,"triangles":tris,"parts":len(objs),"dimensions_blender":dims,
            "texture_sets":1,"clips":["Cryo_Damaged_Jam","Cryo_Damaged_Rest"],
            "features":["source-locked OBJ-001 system","forced and twisted lid corner","missing glass wedge with four retained thick shards","bent keeper and exposed impact metal","empty bed with subject imprint","one failed opening attempt settling at 48 degrees"],
            "state":"En produccion"}
    with open(FOLDER+"/geometry.json","w",encoding="utf-8") as f: json.dump(report,f,indent=2)
    return report


def render():
    scene=_activate(); old=L.EVIDENCE; L.EVIDENCE=FOLDER
    try: return L.sheet(ASSET,[o for o in scene.objects if o.type=='MESH'],views=('front','side','iso'),res=900)
    finally: L.EVIDENCE=old


def bake_map(map_name):
    scene=_activate(); objs=[o for o in scene.objects if o.type=='MESH']; L.uv_project_all(objs)
    old=L.TEX_DIR; L.TEX_DIR=FOLDER
    try: maps=L.bake_pbr(objs,ASSET,size=1024,samples=24,only=[map_name],margin=4)
    finally: L.TEX_DIR=old
    for path in maps.values(): shutil.copy2(path,ROOT+"/EsneiderProtocoloLazaro/Assets/_Game/Art/Textures/"+os.path.basename(path))
    return maps


def finish():
    scene=_activate(); objs=[o for o in scene.objects if o.type=='MESH']; arm=next(o for o in scene.objects if o.type=='ARMATURE')
    bpy.data.libraries.write(ROOT+"/SourceArt/Blender/"+ASSET+".blend",{scene},fake_user=True)
    fbx,size=L.export_fbx(objs,ASSET,armature_obj=arm)
    report=geometry_report(); report.update({"blend":ROOT+"/SourceArt/Blender/"+ASSET+".blend","fbx":fbx,"fbx_bytes":size,
        "textures":{m:ROOT+"/EsneiderProtocoloLazaro/Assets/_Game/Art/Textures/"+ASSET+"_"+m+".png" for m in ("BaseColor","Roughness","Metallic","Normal")}})
    with open(FOLDER+"/delivery.json","w",encoding="utf-8") as f:json.dump(report,f,indent=2)
    return report
