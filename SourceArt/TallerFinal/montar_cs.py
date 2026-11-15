import sys, glob, os
from PIL import Image, ImageDraw
base = "C:/Users/HP/Documents/GitHub/proyectos-unity/SourceArt/TallerFinal/_evidence/anim/"
rows = []
for clip in sys.argv[2:]:
    fs = sorted(glob.glob(base + "_%s_*.png" % clip))
    ims = [Image.open(f).convert("RGB") for f in fs]
    w, h = ims[0].size
    r = Image.new("RGB", (w * len(ims), h + 24), (24, 24, 28))
    ImageDraw.Draw(r).text((8, 4), clip, fill=(235, 235, 235))
    for i, im in enumerate(ims):
        r.paste(im, (i * w, 24))
    rows.append(r)
    for f in fs:
        os.remove(f)
W = max(r.width for r in rows)
s = Image.new("RGB", (W, sum(r.height for r in rows)), (24, 24, 28))
y = 0
for r in rows:
    s.paste(r, (0, y)); y += r.height
out = base + sys.argv[1] + ".png"
s.save(out)
print(out)
