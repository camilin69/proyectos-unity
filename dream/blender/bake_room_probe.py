"""Run inside Blender. Bake six room views for the runtime's local reflection.

The timer renders one face at a time so Blender MCP can report progress between
faces. Run pack_room_probe.py with normal Python after status becomes complete.
This is an LDR artistic reflection probe, not an HDR light or a GI solution.
"""
from pathlib import Path
import bpy, json
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
scene=bpy.data.scenes['DREAM_PastelRoom']
# Scene properties survive saving/reopening a .blend, while timers do not.
# The registered callable is authoritative; the scene property is progress only.
PROBE_TIMER_KEY='dream_room_probe_bake_callback'
active_callback=bpy.app.driver_namespace.get(PROBE_TIMER_KEY)
if callable(active_callback) and bpy.app.timers.is_registered(active_callback):
    raise RuntimeError('A room probe bake is already running')
bpy.app.driver_namespace.pop(PROBE_TIMER_KEY,None)
out=ROOT/'validation/room-probe-faces';out.mkdir(parents=True,exist_ok=True)
origin=(-.85,.3,1.45)
directions=[('px',(1,0,0)),('nx',(-1,0,0)),('py',(0,1,0)),('ny',(0,-1,0)),('pz',(0,0,1)),('nz',(0,0,-1))]
saved={'camera':scene.camera,'active':bpy.context.window.scene,'x':scene.render.resolution_x,'y':scene.render.resolution_y,'percent':scene.render.resolution_percentage,'path':scene.render.filepath,'exposure':scene.view_settings.exposure,'samples':scene.eevee.taa_render_samples}
camera_data=bpy.data.cameras.new('DREAM_ProbeBakeCamera')
camera=bpy.data.objects.new('DREAM_ProbeBakeCamera',camera_data);scene.collection.objects.link(camera)
camera.location=origin;camera_data.sensor_width=32;camera_data.lens=16;camera_data.clip_start=.025;camera_data.clip_end=50
hidden=[(o,o.hide_render) for o in scene.objects if o.name.startswith('GEO-DREAM-radiator')]
for obj,_ in hidden:obj.hide_render=True
scene.camera=camera;bpy.context.window.scene=scene
scene.render.resolution_x=320;scene.render.resolution_y=320;scene.render.resolution_percentage=100
scene.eevee.taa_render_samples=64;scene.view_settings.exposure=0
manifest={'schema':1,'status':'running','origin':origin,'bounds':[[-2.4,-2.7,.016],[.45,2.7,3.2]],'color_space':'sRGB, Standard view, exposure 0; LDR','faces':[]}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
scene['dream_probe_bake_state']=json.dumps({'status':'running','face':0})

def restore():
    scene.camera=saved['camera'];bpy.context.window.scene=saved['active']
    scene.render.resolution_x=saved['x'];scene.render.resolution_y=saved['y'];scene.render.resolution_percentage=saved['percent'];scene.render.filepath=saved['path']
    scene.view_settings.exposure=saved['exposure'];scene.eevee.taa_render_samples=saved['samples']
    for obj,flag in hidden:obj.hide_render=flag
    bpy.data.objects.remove(camera,do_unlink=True);bpy.data.cameras.remove(camera_data)

def render_face():
    try:
        index=len(manifest['faces']);name,direction=directions[index]
        q=Vector(direction).to_track_quat('-Z','Y');camera.rotation_euler=q.to_euler()
        scene.render.filepath=str(out/(name+'.png'))
        bpy.ops.render.render(write_still=True)
        manifest['faces'].append({'name':name,'image':name+'.png','forward':list(q@Vector((0,0,-1))),'right':list(q@Vector((1,0,0))),'up':list(q@Vector((0,1,0)))})
        if len(manifest['faces'])<6:
            (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
            scene['dream_probe_bake_state']=json.dumps({'status':'running','face':len(manifest['faces'])})
            return .2
        manifest['status']='complete';(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
        scene['dream_probe_bake_state']=json.dumps({'status':'complete','faces':6});restore()
    except Exception as exc:
        manifest.update(status='failed',error=str(exc));(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
        scene['dream_probe_bake_state']=json.dumps({'status':'failed','error':str(exc)});restore();raise
    finally:
        if manifest.get('status')!='running' and bpy.app.driver_namespace.get(PROBE_TIMER_KEY) is render_face:
            bpy.app.driver_namespace.pop(PROBE_TIMER_KEY,None)
    return None

bpy.app.timers.register(render_face,first_interval=.5)
bpy.app.driver_namespace[PROBE_TIMER_KEY]=render_face
print('Room reflection probe scheduled: six 320px faces')
