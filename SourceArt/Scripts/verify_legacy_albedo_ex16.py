"""Read-only checks of repaired runtime maps and protected files, plus a QA contact sheet."""
import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
E=ROOT/'SourceArt/_evidence/EX-16'
before=json.loads((E/'audit-before.json').read_text())
assets=[a['asset'] for a in before['assets'] if a['status']=='review metallic albedo']
rows=[]
for asset in assets:
    receipt=json.loads((E/asset/'repair.json').read_text())
    checks={p:hashlib.sha256(Path(p).read_bytes()).hexdigest()==digest for p,digest in receipt['unchanged_runtime_files_sha256'].items()}
    assert all(checks.values()),asset+' protected file changed'
    assert receipt['fingerprint_before']==receipt['fingerprint_after'],asset+' source changed'
    source=E/asset/(asset+'_BaseColor.png')
    target=ROOT/'EsneiderProtocoloLazaro/Assets/_Game/Art/Textures'/(asset+'_BaseColor.png')
    assert source.read_bytes()==target.read_bytes(),asset+' runtime map mismatch'
    rows.append({'asset':asset,'protected_files_verified':len(checks),'source_geometry_uv_rig_preserved':True,'runtime_matches_bake':True})
(E/'protected-files-verification.json').write_text(json.dumps({'assets':rows,'passed':True},indent=2))
for start in range(0,len(assets),5):
    page=Image.new('RGB',(1600,360),(31,37,40));draw=ImageDraw.Draw(page)
    for j,asset in enumerate(assets[start:start+5]):
        path=E/asset/'after/unity_preview.png'
        if not path.exists():raise RuntimeError('Missing reviewed capture '+asset)
        img=Image.open(path).convert('RGB');img.thumbnail((320,320));page.paste(img,(j*320,0));draw.text((j*320+5,330),asset,fill='white')
    page.save(E/f'contact-sheet-{start//5+1}.png')
print(json.dumps({'assets':len(rows),'protected_files':sum(r['protected_files_verified'] for r in rows),'passed':True}))
