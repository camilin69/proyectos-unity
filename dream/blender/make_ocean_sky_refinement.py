"""Original sky texture revision; preserve initial map and every video source."""
from pathlib import Path
import json, hashlib
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'assets/textures/ocean_exit/sunset_stars_v2.png'
h,w=2048,4096
y,x=np.mgrid[:h,:w].astype(np.float32)
elevation=(.5-y/h)*np.pi
rng=np.random.default_rng(4272)
sky=np.zeros((h,w,3),np.float32)+[.26,.37,.56]
sky*=np.clip(1-elevation[...,None]*.5,.3,1)
sunset=np.exp(-((elevation-.024)/.075)**2)
sky+=sunset[...,None]*np.array([.32,.035,-.065],np.float32)
cloud=gaussian_filter(rng.normal(size=(h,w)).astype(np.float32),(9,28),mode='wrap')
cloud/=cloud.std()
sky+=cloud[...,None]*np.exp(-((elevation-.1)/.15)**2)[...,None]*np.array([.032,.016,.022],np.float32)
for _ in range(18000):
    sx=int(rng.integers(w));sy=int(rng.integers(30,h//2-20))
    sky[sy,sx]+=rng.uniform(.12,.5)
# Soft elongated celestial streaks distributed over azimuth; artistic reconstruction.
for u in [.12,.37,.62,.87]:
    dx=(x/w-u)*2*np.pi;dy=elevation-.18
    streak=np.exp(-((dx-dy*.24)/.004)**2)*np.exp(-((dy-.018)/.05)**2)
    sky+=streak[...,None]*np.array([.18,.18,.22],np.float32)
Image.fromarray(np.uint8(np.clip(sky,0,1)*255)).save(out)
report={'source_pixels_used':False,'map':str(out.relative_to(ROOT)),
        'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'size_px':[w,h],
        'status':'Original sky proposal; nebula arrangement remains unmatched.'}
(ROOT/'validation/ocean-exit/sky-map-v2.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
print(json.dumps(report))
