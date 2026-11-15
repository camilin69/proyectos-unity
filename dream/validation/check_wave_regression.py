"""Render existing scenes with the wave-capable runtime and compare pixels."""
from pathlib import Path
import hashlib
import json
import subprocess
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'validation'
cases = {'pastel_room':'room-radiator-opengl-v9.png',
         'stair_sky':'stair-frame-opengl-v5.png',
         'kitchen_meadow':'kitchen-opengl.png',
         'atrium':'atrium-v8-current.png'}
results = []
for scene, baseline in cases.items():
    image = Image.open(OUT/baseline).convert('RGB')
    w,h = image.size
    target = OUT/f'wave-regression-{scene}.ppm'
    args = [str(ROOT/'runtime/build/dream.exe'),'--root',str(ROOT),'--scene',scene,
            '--capture',str(target),'--frames','8','--time','0','--samples','4',
            '--width',str(w),'--height',str(h),'--hidden']
    run = subprocess.run(args, capture_output=True, text=True, check=True)
    assert 'gl_error=0' in run.stdout
    (OUT/f'wave-regression-{scene}.log').write_text(run.stdout,encoding='utf-8')
    current = Image.open(target).convert('RGB')
    current.save(target.with_suffix('.png'))
    difference = np.abs(np.asarray(current).astype(int)-np.asarray(image).astype(int))
    results.append({'scene':scene,'baseline':baseline,'framebuffer':[w,h],
                    'maximum_channel_difference':int(difference.max()),
                    'mean_channel_difference':float(difference.mean()),
                    'changed_pixels':int(np.any(difference!=0,axis=2).sum()),
                    'capture':target.with_suffix('.png').name,'gl_error':0})
report = {'scope':'Four existing scene captures, 8 frames, time=0, MSAA4. Pixel comparison, not visual acceptance.',
          'results':results,'shader_sha256':hashlib.sha256((ROOT/'runtime/shaders/scene.frag').read_bytes()).hexdigest(),
          'binary_sha256':hashlib.sha256((ROOT/'runtime/build/dream.exe').read_bytes()).hexdigest()}
(OUT/'wave-runtime-regression.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report))
