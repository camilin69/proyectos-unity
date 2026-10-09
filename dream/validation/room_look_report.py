"""Compare matching material classes, not raw pixels or an invented fidelity score."""
from pathlib import Path
import argparse, json, hashlib
import numpy as np
from PIL import Image

root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--phase',default='current');args=parser.parse_args()
paths={'reference':'referencias/estetica/evidencias/video-35/11s.png','opengl':'validation/room-opengl.png','blender':'validation/room-blender.png'}
report={'phase':args.phase,'scope':'Color diagnostics within corresponding wall/sky regions. Masks are color classes, not exact geometry registration. These statistics do not certify visual fidelity.','images':{}}
for name,path in paths.items():
    file=root/path;im=Image.open(file).convert('RGB');a=np.asarray(im.resize((360,640)),float)
    wall=a[90:340,180:234];r,g,b=wall.transpose(2,0,1)
    sky=a[115:240,65:151];sr,sg,sb=sky.transpose(2,0,1)
    masks={'pink_wall':(wall,(r>g*1.08)&(b>g*1.02)), 'mint_wall':(wall,(g>r*1.05)&(b>r*1.02)), 'blue_sky':(sky,(sb>sg*1.17)&(sb>sr*1.3))}
    result={}
    for feature,(pixels,mask) in masks.items():
        selected=pixels[mask];assert len(selected)>200,(name,feature,'Insufficient samples')
        maxc=selected.max(axis=1);minc=selected.min(axis=1)
        result[feature]={'mean_srgb':selected.mean(axis=0).round(2).tolist(),'std_srgb':selected.std(axis=0).round(2).tolist(),'value_p95':round(float(np.percentile(maxc,95)),2),'saturation_mean':round(float(((maxc-minc)/np.maximum(maxc,1)).mean()),4),'pixels':int(mask.sum())}
    floor=a[410:620,70:315]
    result['floor_region']={'mean_srgb':floor.mean(axis=(0,1)).round(2).tolist(),'std_srgb':floor.std(axis=(0,1)).round(2).tolist(),'pixels':int(floor.shape[0]*floor.shape[1]),'limitation':'Contains different arrangements of reflection and patches; mean color is diagnostic only.'}
    report['images'][name]={'path':path,'dimensions':list(im.size),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'materials':result}
for backend in ['blender','opengl']:
    report['images'][backend]['mean_rgb_error']={k:np.round(np.array(v['mean_srgb'])-report['images']['reference']['materials'][k]['mean_srgb'],2).tolist() for k,v in report['images'][backend]['materials'].items()}
out=root/'validation'/f'room-look-{args.phase}.json';out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v.get('mean_rgb_error') for k,v in report['images'].items() if k!='reference'}))
