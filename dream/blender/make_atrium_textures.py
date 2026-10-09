"""Authored leaf detail and decorative biosphere texture, not a geographic map."""
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
root=Path(__file__).resolve().parents[1]/'assets/textures'
root.mkdir(exist_ok=True,parents=True)
x,y=np.meshgrid(np.linspace(0,1,256),np.linspace(0,1,512))
vein=np.exp(-abs(x-.5)*180)*.18
vein+=np.exp(-abs(np.sin(y*80+abs(x-.5)*33))*30)*.07
light=.68+.25*np.sin(x*np.pi)+vein
leaf=np.stack([light*80,light*147,light*43],axis=-1)
im=Image.fromarray(np.uint8(np.clip(leaf,0,255)))
im.save(root/'leaf_detail.png');im.save(root/'leaf_detail.bmp')
w,h=1024,512
x,y=np.meshgrid(np.linspace(0,1,w),np.linspace(0,1,h))
ocean=np.stack([25+25*np.cos(y*5)**2,112+48*np.sin(y*np.pi),192+43*np.sin(y*np.pi)],axis=-1)
land=(np.sin(x*19+y*7)+np.sin(x*31-y*17)*.5+np.cos(y*23+x*9)*.6)>.72
land&=(y>.13)&(y<.88)
ocean[land]=np.stack([65+35*np.sin(y*7)**2,143+50*np.cos(y*3)**2,48+33*np.sin(x*8)**2],axis=-1)[land]
cloud=np.clip((np.sin(x*39+y*27)+np.sin(y*51-x*11)-1.25)*.7,0,.6)
ocean=ocean*(1-cloud[:,:,None])+np.array([235,249,250])*cloud[:,:,None]
im=Image.fromarray(np.uint8(ocean)).filter(ImageFilter.GaussianBlur(.7))
im.save(root/'biosphere.png');im.save(root/'biosphere.bmp')
print('Saved leaf_detail and decorative biosphere maps.')
