# Hoja de contactos lateral de un clip: 8 fotogramas. Globales: CLIP, VIEW ("lado" o "tres").
import bpy, os
from mathutils import Vector
OUT = r"C:/Users/HP/Documents/GitHub/proyectos-unity/SourceArt/TallerFinal/_evidence/anim"
os.makedirs(OUT, exist_ok=True)
CLIP = globals().get("CLIP", "Walk")
VIEW = globals().get("VIEW", "lado")
sc = bpy.context.scene
arm = bpy.data.objects["SN_Armature"]
ad = arm.animation_data
ad.use_nla = False
act = bpy.data.actions[CLIP]
ad.action = act
sc.render.engine = "BLENDER_WORKBENCH"
sc.display.shading.light = "STUDIO"
sc.display.shading.show_shadows = True
sc.display.shading.color_type = "MATERIAL"
sc.render.resolution_x = 360
sc.render.resolution_y = 560
cam = bpy.data.objects.new("CAM_cs", bpy.data.cameras.new("CAM_cs"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.type = "ORTHO"
cam.data.ortho_scale = 2.1
target = Vector((0, 0, 0.9))
d = Vector((1, 0, 0.04)) if VIEW == "lado" else Vector((0.75, -0.6, 0.15))
cam.location = target + d.normalized() * 5
cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
n = int(act.frame_range[1])
frames = [1 + round(k * (n - 1) / 8.0) for k in range(8)]
paths = []
for f in frames:
    sc.frame_set(f)
    p = "%s/_%s_%02d.png" % (OUT, CLIP, f)
    sc.render.filepath = p
    bpy.ops.render.render(write_still=True)
    paths.append(p)
bpy.data.objects.remove(cam, do_unlink=True)
ad.action = None
ad.use_nla = True
sc.frame_set(1)
CS = paths
