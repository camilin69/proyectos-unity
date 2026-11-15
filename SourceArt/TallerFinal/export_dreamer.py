# Exporta el sonador a FBX con un take por clip (tiras NLA). El stack NLA tiene que estar ACTIVO: si no, el
# exportador saca cada take con la pose de reposo repetida (leccion de Esneider, clips planos en Unity).
import bpy, os
OUT_DIR = r"C:/Users/HP/Documents/GitHub/proyectos-unity/TallerFinal/Assets/_Project/Art/Models/Character"
os.makedirs(OUT_DIR, exist_ok=True)
OUT = OUT_DIR + "/SN-01_Sonador.fbx"
bpy.context.scene.render.fps = 30          # los clips se calibraron a 30 fps; Blender exporta a 24 por defecto
bpy.context.scene.render.fps_base = 1.0
arm = bpy.data.objects["SN_Armature"]
ad = arm.animation_data
ad.action = None
ad.use_nla = True
for tr in ad.nla_tracks:
    tr.mute = False
for pb in arm.pose.bones:
    pb.location = (0, 0, 0)
    pb.rotation_quaternion = (1, 0, 0, 0)
objs = [o for o in bpy.data.objects if o.type in ("MESH", "ARMATURE") and (o == arm or o.parent == arm)]
win = bpy.context.window_manager.windows[0]
area = next(a for a in win.screen.areas if a.type == "VIEW_3D")
region = next(r for r in area.regions if r.type == "WINDOW")
for o in bpy.context.scene.objects:
    o.select_set(o in objs)
bpy.context.view_layer.objects.active = arm
with bpy.context.temp_override(window=win, screen=win.screen, area=area, region=region,
                               active_object=arm, selected_objects=objs, selected_editable_objects=objs):
    bpy.ops.export_scene.fbx(filepath=OUT, use_selection=True, object_types={"ARMATURE", "MESH"},
                             apply_unit_scale=True, apply_scale_options="FBX_SCALE_ALL",
                             axis_forward="-Z", axis_up="Y", add_leaf_bones=False,
                             bake_anim=True, bake_anim_use_nla_strips=True, bake_anim_use_all_actions=False,
                             bake_anim_force_startend_keying=True, bake_anim_simplify_factor=0.0,
                             mesh_smooth_type="FACE", use_mesh_modifiers=True, path_mode="AUTO")
EXPORTED = (OUT, os.path.getsize(OUT))
