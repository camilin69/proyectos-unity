"""Render actual sign front, side, back and obliques for coverage inspection.

Run through Blender MCP. The inspection scene is separate; main scene settings
and geometry are preserved. These views test a prop, not reference fidelity.
"""
import bpy
import json
from mathutils import Vector
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
main = bpy.data.scenes['DREAM_WaveCorridor']
name = 'DREAM_WaveSignInspection'
scene = bpy.data.scenes.get(name) or bpy.data.scenes.new(name)
for old in list(scene.objects):
    if old.name.startswith('QA-WaveSign-'):
        bpy.data.objects.remove(old, do_unlink=True)
source = bpy.data.objects['GEO-DREAM-wavecorridor-detail_exit_-1']
obj = source.copy()
obj.name = 'QA-WaveSign-actual_sign'
scene.collection.objects.link(obj)
obj.location = (1.092,-source['dream_sign_center_y'],-source['dream_sign_center_z'])
scene.world = main.world
scene.render.engine = main.render.engine
scene.eevee.taa_render_samples = 32
scene.eevee.use_raytracing = False
scene.view_settings.view_transform = main.view_settings.view_transform
scene.view_settings.exposure = -1.2
scene.render.resolution_x, scene.render.resolution_y = 320, 240
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = main.render.image_settings.file_format
camera = bpy.data.objects.new('QA-WaveSign-camera',bpy.data.cameras.new('QA-WaveSign-camera_data'))
scene.collection.objects.link(camera)
camera.data.lens = 55
scene.camera = camera
for i,position in enumerate([(1,-1,1),(-1,0,1),(0,1,.5)]):
    data = bpy.data.lights.new(f'QA-WaveSign-light_data_{i}','AREA')
    data.energy, data.size = 20, 1
    light = bpy.data.objects.new(f'QA-WaveSign-light_{i}',data)
    scene.collection.objects.link(light)
    light.location = position
    light.rotation_euler = (-light.location).to_track_quat('-Z','Y').to_euler()
views = [('front',(1,0,0)),('oblique',(.75,.65,.12)),('edge',(0,1,.05)),
         ('back',(-1,0,.05)),('opposite',(.75,-.65,.12))]
out = ROOT/'validation/wave-sign-qa'
out.mkdir(exist_ok=True)
try:
    bpy.context.window.scene = scene
    for label,position in views:
        camera.location = position
        camera.rotation_euler = (-Vector(position)).to_track_quat('-Z','Y').to_euler()
        scene.render.filepath = str(out/(label+'.png'))
        bpy.ops.render.render(write_still=True)
finally:
    bpy.context.window.scene = main
(out/'views.json').write_text(json.dumps({'source_object':source.name,'views':views,
    'source_mesh_shared_without_edits':True,'reference_fidelity_evaluation':False,
    'expected':'Lettering on front only; back and all sides have plain coating.'},indent=2),encoding='utf-8')
print(json.dumps({'inspection_scene':scene.name,'views_rendered':len(views),'main_scene_restored':True}))
