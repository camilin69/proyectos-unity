"""Pack the wave profile's linear auxiliary data without altering source maps."""
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
source = ROOT/'assets/textures/wave_candidate'
out = ROOT/'assets/textures'
channels = [('wave_wall_roughness.png',0),('wave_ceiling_roughness.png',1),
            ('wave_exit_emission_dark.png',2)]
packed = np.zeros((512,512,3), dtype=np.uint8)
inputs = []
for name,channel in channels:
    path=source/name
    image=Image.open(path).convert('RGB')
    if image.size != (512,512):
        image=image.resize((512,512),Image.Resampling.BILINEAR)
    packed[...,channel]=np.array(image)[...,0]
    inputs.append({'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'channel':channel})
outputs=[]
for stem,pixels in [('wave_surface_data',packed),('wave_neutral_environment',np.full((4,8,3),32,dtype=np.uint8))]:
    image=Image.fromarray(pixels)
    for extension in ('png','bmp'):
        path=out/(stem+'.'+extension);image.save(path)
        assert np.array_equal(np.array(Image.open(path).convert('RGB')),pixels)
        outputs.append({'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
report={'schema':'dream.wave_packed_maps.v1','source_maps_preserved':True,'inputs':inputs,'outputs':outputs,
        'linear_data_channels':{'R':'wall roughness at metric UV/.5','G':'ceiling roughness at metric UV/.5','B':'sign emission mask at clamped decal UV'},
        'emission_resampling':'bilinear 256x128 to 512x512; original aspect restored by decal UV geometry',
        'environment':'Neutral dark placeholder outside the closed shell; not a source panorama.'}
(ROOT/'validation/wave-runtime-textures.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'packed_maps':2,'source_images_unchanged':True}))
