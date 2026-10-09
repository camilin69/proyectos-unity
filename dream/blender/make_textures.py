"""Generate plaid and ceramic maps; explicitly reuse or regenerate the sky.

Python + NumPy + Pillow. Sky regeneration also needs SciPy and takes about
two minutes. Default --sky reuse preserves the active volumetric environment.
"""
from pathlib import Path
import argparse
import subprocess
import sys

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1] / 'assets' / 'textures'


def save(name, rgb):
    image = Image.fromarray(np.uint8(np.clip(rgb, 0, 255)), 'RGB')
    image.save(ROOT / (name + '.png'))
    image.save(ROOT / (name + '.bmp'))


def noise(w, h, rng):
    result = np.zeros((h, w), np.float32)
    for cells, weight in [(8, .48), (16, .25), (32, .14), (64, .08), (128, .05)]:
        small = Image.fromarray(rng.integers(0, 255, (max(2,cells//2), cells), dtype=np.uint8))
        result += np.asarray(small.resize((w,h), Image.Resampling.BICUBIC), dtype=np.float32) / 255 * weight
    return result


def ceramic_rng():
    # Freeze the published ceramic stream independently of the retired sky
    # generator. This state reproduces its existing pixels byte for byte.
    rng = np.random.default_rng()
    rng.bit_generator.state = {
        'bit_generator': 'PCG64',
        'state': {'state': 149926810638657734079119730020961581637,
                  'inc': 166495920544866116219014896541133093073},
        'has_uint32': 1, 'uinteger': 2814701155,
    }
    return rng


def generate_material_maps():
    w=h=512
    x,y=np.meshgrid(np.arange(w),np.arange(h))
    # Plaid textile generated from thread bands rather than photographed lighting.
    cloth=np.full((h,w,3),[192.,188.,159.])
    for axis in [x,y]:
        band=axis%128
        for low,high,c,alpha in [(0,30,[84,134,122],.6),(36,57,[229,148,159],.65),(66,73,[234,197,127],.75),(94,98,[85,117,115],.7)]:
            mask=(band>=low)&(band<high);cloth[mask]=cloth[mask]*(1-alpha)+np.array(c)*alpha
    weave=((x%3==0).astype(float)+(y%3==0).astype(float))*4-4
    save('curtain_plaid',cloth+weave[:,:,None])

    grain=noise(w,h,ceramic_rng())
    normal=np.zeros((h,w,3));normal[:]=[128,128,255]
    normal[:,:,0]+=np.gradient(grain,axis=1)*250
    normal[:,:,1]+=np.gradient(grain,axis=0)*250
    save('ceramic_normal',normal)
    save('ceramic_roughness',np.repeat((58+grain*22)[:,:,None],3,axis=2))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sky', choices=['reuse','regenerate','skip'], default='reuse',
                        help='reuse requires existing cloud_sky PNG/BMP; regenerate calls the volumetric generator; skip only makes material maps.')
    args=parser.parse_args()
    ROOT.mkdir(parents=True,exist_ok=True)
    if args.sky=='reuse':
        missing=[str(ROOT/('cloud_sky.'+ext)) for ext in ['png','bmp'] if not (ROOT/('cloud_sky.'+ext)).is_file()]
        if missing:
            parser.error('Sky files missing. Run with --sky regenerate: '+', '.join(missing))
        print('Reusing active cloud_sky.png and cloud_sky.bmp without modifying them.')
    elif args.sky=='regenerate':
        subprocess.run([sys.executable,str(Path(__file__).with_name('make_cloud_sky.py'))],check=True)
    generate_material_maps()
    print('Generated plaid, ceramic normal and roughness in', ROOT)


if __name__=='__main__':
    main()
