"""Read-only texture audit: flag nearly black albedo in fully metallic texels.
This is a diagnostic, not artistic acceptance. Run with the image-analysis Python.
"""
import json
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from PIL import Image

root=Path(__file__).resolve().parents[2]
textures=root/'EsneiderProtocoloLazaro/Assets/_Game/Art/Textures'
rows=[]
for metallic in sorted(textures.glob('*_Metallic.png')):
    asset=metallic.stem.removesuffix('_Metallic')
    base=metallic.with_name(asset+'_BaseColor.png')
    if not base.exists():
        rows.append({'asset':asset,'status':'missing BaseColor'});continue
    m=np.asarray(Image.open(metallic).convert('L'))
    c=np.asarray(Image.open(base).convert('RGB'))
    if m.shape!=c.shape[:2]:
        rows.append({'asset':asset,'status':'map dimensions differ'});continue
    mask=m>242;count=int(mask.sum())
    black=int(((c.max(axis=2)<8)&mask).sum())
    ratio=black/count if count else None
    rows.append({'asset':asset,'metal_texels':count,'black_metal_texels':black,'black_fraction':ratio,
                 'status':'review metallic albedo' if count>100 and ratio>.1 else 'no broad black-metal issue detected'})
report={'generated_utc':datetime.now(timezone.utc).isoformat(),
        'criterion':'Metallic > 242/255 and max(BaseColor RGB) < 8/255; flag >10% of at least 100 metallic texels. Not an acceptance test.',
        'assets':rows}
destination=root/'docs/produccion/METAL_ALBEDO_AUDIT.json'
destination.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'assets':len(rows),'flagged':[r['asset'] for r in rows if r['status']=='review metallic albedo'],'output':str(destination)}))
