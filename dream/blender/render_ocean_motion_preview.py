"""Render a bounded chunk of the motion preview through live Blender MCP."""
from pathlib import Path
import json
import bpy
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'validation/ocean-exit-motion/preview';OUT.mkdir(exist_ok=True)
s=bpy.data.scenes['DREAM_OceanExitWater']
s.camera=s.objects['CAM-DREAM-oceanwater-7s']
s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True
s.render.resolution_percentage=50
rendered=[]
for index in range(PREVIEW_START,PREVIEW_START+PREVIEW_COUNT):
    assert 0<=index<24
    frame=1+index*3;s.frame_set(frame)
    s.render.filepath=str(OUT/f'frame-{index+1:04d}.png')
    bpy.ops.render.render(write_still=True,scene=s.name)
    rendered.append({'image':f'frame-{index+1:04d}.png','scene_frame':frame,'time_s':index*.1})
s.render.resolution_percentage=100;s.cycles.samples=64;s.frame_set(1)
print(json.dumps({'rendered':rendered}))
