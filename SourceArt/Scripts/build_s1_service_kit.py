"""EX-10: original metric service kit. Run through the Blender MCP.
Non-destructive: owns a separate scene; never edits the currently loaded rig.
Unity convention: X width, Y up, Z depth (FBX -Z forward/Y up).
"""
import bpy, math, os, json
from mathutils import Vector

ROOT = 'C:/Users/HP/Documents/GitHub/proyectos-unity'
previous = bpy.data.scenes.get('EX10_ServiceKit')
if previous:
    for o in list(previous.objects): bpy.data.objects.remove(o,do_unlink=True)
    bpy.data.scenes.remove(previous)
scene = bpy.data.scenes.new('EX10_ServiceKit')
bpy.context.window.scene = scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1
collection = bpy.data.collections.new('EXPORT_S1_SERVICE')
scene.collection.children.link(collection)

def mat(name, color, metal=0, rough=.5):
    m = bpy.data.materials.new(name); m.diffuse_color = (*color,1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Metallic'].default_value=metal
    p.inputs['Roughness'].default_value=rough
    return m

paint=mat('S1_Ceramic',(0.43,.52,.5),0,.65)
steel=mat('S1_Steel',(.15,.19,.21),.8,.35)
dark=mat('S1_Gasket',(.025,.038,.042),0,.8)
light=mat('S1_Light',(.65,.9,.85),0,.25)
amber=mat('S1_Amber',(.8,.35,.06),0,.4)
parts=[]

def box(name, pos, size, material, bevel=.01):
    bpy.ops.mesh.primitive_cube_add(size=1,location=pos)
    o=bpy.context.object; o.name=name; o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(material)
    if bevel:
        mod=o.modifiers.new('Manufactured edges','BEVEL'); mod.width=bevel; mod.segments=2
        bpy.ops.object.modifier_apply(modifier=mod.name)
    parts.append(o); return o

def cyl(name,pos,r,depth,material,axis='Z'):
    bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=r,depth=depth,location=pos)
    o=bpy.context.object; o.name=name
    if axis=='X': o.rotation_euler[1]=math.pi/2
    if axis=='Y': o.rotation_euler[0]=math.pi/2
    o.data.materials.append(material); parts.append(o); return o

def finish(name):
    bpy.ops.object.select_all(action='DESELECT')
    for o in parts:o.select_set(True)
    bpy.context.view_layer.objects.active=parts[0]
    bpy.ops.object.join(); o=bpy.context.object; o.name=name
    scene.cursor.location=(0,0,0); bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(island_margin=.025)
    bpy.ops.object.mode_set(mode='OBJECT')
    for c in list(o.users_collection): c.objects.unlink(o)
    collection.objects.link(o); parts.clear(); return o

# Panel front faces -Y. Each panel is two metres wide, 2.8m tall.
box('service backing',(0,.025,1.4),(1.98,.1,2.8),dark)
box('ceramic panel',(0,-.035,1.48),(1.88,.10,2.56),paint,.025)
box('kick plate',(0,-.10,.20),(1.88,.08,.35),steel)
box('joint upper',(0,-.095,2.35),(1.84,.02,.025),dark,.002)
for x in [-.87,.87]:
    for z in [.43,2.58]: cyl('captive fastener',(x,-.1,z),.023,.027,steel,'Y')
for x in [-.64,-.48,-.32,-.16,0,.16,.32,.48,.64]:
    box('vent slit',(x,-.094,.58),(.075,.023,.17),dark,.005)
finish('S1_WallPanel')

# Exposed pair of insulated service pipes with flange and wall saddle.
for x in [-.16,.16]:
    cyl('pipe',(x,0,1.5),.075,3,steel)
    for z in [.3,1.5,2.7]:
        cyl('flange',(x,0,z),.11,.065,steel)
        box('support saddle',(x,.13,z),(.25,.10,.12),dark)
    cyl('service band',(x,0,.95),.078,.12,amber)
finish('S1_PipePair')

box('lamp body',(0,0,0),(1.7,.32,.15),steel,.025)
box('lamp gasket',(0,0,-.085),(1.6,.27,.045),dark)
box('lamp diffuser',(0,0,-.112),(1.48,.21,.028),light,.009)
for x in [-.78,.78]:box('protective end',(x,0,-.095),(.075,.34,.13),steel)
finish('S1_Luminaire')

# Cryochamber service manifold; placed beside wall, away from the player route.
box('cabinet',(0,0,.65),(.8,.3,1.3),steel,.03)
box('service door',(0,-.17,.69),(.72,.06,1.12),paint,.015)
for x in [-.22,.22]:
    cyl('gauge rim',(x,-.225,.98),.105,.06,steel,'Y')
    cyl('gauge face',(x,-.26,.98),.086,.01,light,'Y')
    box('gauge needle',(x,-.27,.99),(.008,.005,.10),dark,.001)
    cyl('valve',(x,-.22,.39),.095,.06,amber,'Y')
    cyl('feed',(x,0,1.55),.035,.55,steel)
finish('S1_Manifold')

# Pressure vessel sized to the existing M003 footprint (1.6 x 1.6 x 2.8m).
cyl('pressure vessel',(0,0,1.4),.64,2.28,paint)
for z in [.32,2.48]:
    cyl('reinforced collar',(0,0,z),.70,.14,steel)
for x in [-.45,.45]:
    for y in [-.45,.45]:box('anchored foot',(x,y,.17),(.19,.19,.34),steel)
cyl('pressure head',(0,0,2.63),.26,.20,steel)
cyl('valve stem',(0,0,2.77),.06,.10,steel)
cyl('handwheel',(0,0,2.82),.19,.045,amber)
for z in [.7,1.1,1.5,1.9]:box('capacity tick',(.63,-.15,z),(.015,.15,.027),amber,.002)
finish('S1_CoolantTank')

os.makedirs(ROOT+'/SourceArt/Blender',exist_ok=True)
os.makedirs(ROOT+'/EsneiderProtocoloLazaro/Assets/_Game/Art/Models',exist_ok=True)
# Save only this scene and dependencies: preserve live source scene in memory.
bpy.data.libraries.write(ROOT+'/SourceArt/Blender/S1_ServiceKit.blend',{scene},fake_user=True)
bpy.ops.object.select_all(action='DESELECT')
for o in collection.objects:o.select_set(True)
bpy.context.view_layer.objects.active=next(iter(collection.objects))
bpy.ops.export_scene.fbx(filepath=ROOT+'/EsneiderProtocoloLazaro/Assets/_Game/Art/Models/S1_ServiceKit.fbx',use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_anim=False,add_leaf_bones=False)
report=[]
for o in collection.objects:
    o.data.calc_loop_triangles()
    report.append({'name':o.name,'triangles':len(o.data.loop_triangles),'size':list(o.dimensions),'uv':len(o.data.uv_layers)})
os.makedirs(ROOT+'/SourceArt/_evidence/EX-10',exist_ok=True)
with open(ROOT+'/SourceArt/_evidence/EX-10/kit_report.json','w') as f:json.dump(report,f,indent=2)
print(json.dumps(report))
