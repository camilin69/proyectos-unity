"""Deterministic glazing mask: condensation at seals, sparse contact smears."""
from pathlib import Path
import math,random
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
ASSET='OBJ-060_VidrioObservacion'
def prepare():
    image=Image.new('RGBA',(512,512));pixels=image.load();rng=random.Random(41)
    # Contact area at approximately 1.45 m height; preserve the main viewing area.
    marks=[(.68,.60,.022,.023,.065)]
    marks += [(.657+i*.011,.626+(.020 if i in (1,2) else .010),.004,.020,.052) for i in range(5)]
    for y in range(512):
        v=1-y/511
        for x in range(512):
            u=x/511;edge=min(u,1-u,v,1-v)
            mist=.16*math.exp(-edge*42)*( .82+.18*math.sin(u*43+v*21))
            contact=sum(a*math.exp(-((u-cx)/sx)**2-((v-cy)/sy)**2) for cx,cy,sx,sy,a in marks)
            alpha=.055+mist+contact+rng.random()*.004
            pixels[x,y]=(169,195,193,round(255*alpha))
    target=ROOT/'EsneiderProtocoloLazaro/Assets/_Game/Art/Textures'/f'{ASSET}_Glazing.png'
    image.save(target)
    evidence=ROOT/'SourceArt/_evidence/EX-41'/ASSET;evidence.mkdir(parents=True,exist_ok=True)
    image.save(evidence/target.name)
    print(target)
if __name__=='__main__':prepare()
