"""Authored thin-film-like floor finish shared by Blender, GLB and OpenGL.

Colors are blended in linear light and saved as sRGB albedo maps. They are
artistic interference patterns, not maps recovered from the reference video.
UVs cover the whole room, so the pattern continues over tile joints.
"""
from pathlib import Path
import json
import numpy as np
from scipy.ndimage import gaussian_filter, zoom
from PIL import Image

root=Path(__file__).resolve().parents[1]/'assets/textures'
root.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(1431);h,w=1536,1024
y,x=np.meshgrid(np.linspace(0,5.4,h),np.linspace(0,2.85,w),indexing='ij')
field=np.zeros((h,w))
for cells,weight in [(5,.60),(12,.25),(30,.1),(72,.05)]:
    small=rng.random((cells*2,cells))
    field+=zoom(small,(h/small.shape[0],w/small.shape[1]),order=3)[:h,:w]*weight
phase=field*16+np.sin(x*3+y)*.5
rainbow=.5+.5*np.cos(phase[:,:,None]+np.array([0,2.09,4.19]))
film=.16+.78*rainbow
mask=np.clip((field-.36)*3.2,0,1)
mask=gaussian_filter(mask,2)
# Pools of interference, with neutral regions remaining readable.
mask*=np.clip(.7+.3*np.sin(x*2.1-y*.9),0,1)
strength=.48*mask
linear=lambda c:np.where(c>.04045,((c+.055)/1.055)**2.4,c/12.92)
srgb=lambda c:np.where(c>.0031308,1.055*np.maximum(c,0)**(1/2.4)-.055,c*12.92)
def save(name,rgb):
    im=Image.fromarray(np.uint8(np.clip(rgb*255,0,255)))
    im.save(root/f'{name}.png');im.save(root/f'{name}.bmp')

base_colors={'pink':'BCA6B8','mint':'92B6AA'}
for name,hexcolor in base_colors.items():
    color=np.array([int(hexcolor[i:i+2],16)/255 for i in (0,2,4)])
    blend=linear(color)*(1-strength[:,:,None])+linear(film)*strength[:,:,None]
    save(f'floor_{name}_albedo',srgb(blend))
dy,dx=np.gradient(gaussian_filter(field,1),5.4/h,2.85/w)
nx=np.clip(-dx*.055,-.4,.4);ny=np.clip(dy*.055,-.4,.4)
save('floor_flow',np.stack([nx*.5+.5,ny*.5+.5,mask],axis=-1))
save('floor_normal',np.stack([nx*.5+.5,ny*.5+.5,np.sqrt(np.maximum(1-nx*nx-ny*ny,0))*.5+.5],axis=-1))
manifest={'source':'authored domain-warped interference finish','base_colors_srgb':base_colors,'color_space':'albedo sRGB; flow and normal linear','blend':'linear-light RGB','room_uv_extent_m':[2.85,5.4],'seed':1431,'limitation':'Artistic approximation with fixed albedo colors. Reflections respond to view angle; this is not a physical thin-film simulation.'}
(root/'floor_finish.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print('Saved continuous floor albedo, normal and reflection-flow maps.')
