# Hoja de tres vistas del personaje (Workbench). Variable global TAG = sufijo de la hoja.
import bpy, os
from mathutils import Vector
OUT = r"C:/Users/HP/Documents/GitHub/proyectos-unity/SourceArt/TallerFinal/_evidence"
os.makedirs(OUT, exist_ok=True)
TAG = globals().get("TAG", "x")
sc = bpy.context.scene
sc.render.engine = "BLENDER_WORKBENCH"
sc.display.shading.light = "STUDIO"
sc.display.shading.show_shadows = True
sc.display.shading.show_cavity = True
sc.display.shading.color_type = "MATERIAL"
sc.render.resolution_x = 600
sc.render.resolution_y = 900
cam = bpy.data.objects.new("CAM_sheet", bpy.data.cameras.new("CAM_sheet"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.type = "ORTHO"
cam.data.ortho_scale = 1.95
target = Vector((0, 0, 0.88))
paths = []
for name, d in (("frente", Vector((0, -1, 0.05))), ("lado", Vector((1, 0, 0.05))), ("espalda34", Vector((-0.7, 0.7, 0.18)))):
    cam.location = target + d.normalized() * 5
    cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
    path = "%s/_%s_%s.png" % (OUT, TAG, name)
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    paths.append(path)
bpy.data.objects.remove(cam, do_unlink=True)
SHEET = paths
