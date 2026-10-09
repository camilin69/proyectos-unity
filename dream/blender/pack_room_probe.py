"""Reproject rendered cubemap faces into the runtime's equirectangular layout."""
from pathlib import Path
import hashlib, json
import numpy as np
from scipy.ndimage import map_coordinates
from PIL import Image

root=Path(__file__).resolve().parents[1]
folder=root/'validation/room-probe-faces'
meta=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
assert meta['status']=='complete' and len(meta['faces'])==6
w,h=1024,512
longitude=((np.arange(w)+.5)/w-.5)*2*np.pi
latitude=(.5-(np.arange(h)+.5)/h)*np.pi
lon,lat=np.meshgrid(longitude,latitude)
d=np.stack((np.cos(lat)*np.cos(lon),np.cos(lat)*np.sin(lon),np.sin(lat)),axis=-1)
forward=np.array([face['forward'] for face in meta['faces']])
projection=np.einsum('hwc,fc->hwf',d,forward)
choice=projection.argmax(axis=-1)
result=np.zeros((h,w,3),dtype=np.float32)
for i,face in enumerate(meta['faces']):
    image=np.asarray(Image.open(folder/face['image']).convert('RGB'),dtype=np.float32)
    rays=d[choice==i];depth=rays@forward[i]
    u=.5+.5*(rays@np.array(face['right']))/depth
    v=.5-.5*(rays@np.array(face['up']))/depth
    coords=np.stack((v*image.shape[0]-.5,u*image.shape[1]-.5))
    result[choice==i]=np.stack([map_coordinates(image[:,:,ch],coords,order=1,mode='nearest') for ch in range(3)],axis=-1)
im=Image.fromarray(np.clip(np.rint(result),0,255).astype('uint8'))
dest=root/'assets/textures/room_probe'
for suffix in ['.png','.bmp']:im.save(dest.with_suffix(suffix))
meta.update({'output':'room_probe','resolution':[w,h],'mapping':'longitude=atan2(y,x)/(2*pi)+0.5; latitude=asin(z)/pi+0.5, BMP bottom-up','png_sha256':hashlib.sha256(dest.with_suffix('.png').read_bytes()).hexdigest(),'scope':'Static LDR interior reflection; box projected at runtime. Does not encode dynamic objects or HDR radiance.'})
dest.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'output':str(dest),'size':im.size,'faces':len(meta['faces'])}))
