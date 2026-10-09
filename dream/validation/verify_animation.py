"""Check rendered changes at two fixed simulation times, with a static control."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parent
a=np.asarray(Image.open(root/'atrium-opengl.png').convert('RGB'),dtype=float)
b=np.asarray(Image.open(root/'atrium-time2.png').convert('RGB'),dtype=float)
assert a.shape==b.shape==(720,960,3)
regions={'water':[350,495,500,530],'foliage':[210,390,300,530],'static_control':[870,200,920,280]}
report={'times_s':[0,2],'camera_equal':True,'regions':{},'scope':'Rendered variation in fixed crops; not a physical water simulation or full animation quality score.'}
for name,(x0,y0,x1,y1) in regions.items():
    delta=np.abs(a[y0:y1,x0:x1]-b[y0:y1,x0:x1])
    report['regions'][name]={'xyxy':[x0,y0,x1,y1],'mean_absolute_channel_delta':float(delta.mean()),'changed_pixels':int(np.count_nonzero(np.max(delta,axis=2)>2))}
assert report['regions']['water']['mean_absolute_channel_delta']>.2
assert report['regions']['foliage']['changed_pixels']>50
assert report['regions']['static_control']['mean_absolute_channel_delta']<.01
report['result']='PASS'
(root/'animation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report))
