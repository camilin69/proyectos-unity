import sys
from PIL import Image
tag = sys.argv[1]
base = "C:/Users/HP/Documents/GitHub/proyectos-unity/SourceArt/TallerFinal/_evidence/"
ims = [Image.open(base + "_%s_%s.png" % (tag, n)).convert("RGB") for n in ("frente", "lado", "espalda34")]
w, h = ims[0].size
s = Image.new("RGB", (w * 3, h), (30, 30, 34))
for i, im in enumerate(ims):
    s.paste(im, (i * w, 0))
s.save(base + "sonador_%s.png" % tag)
print(base + "sonador_%s.png" % tag)
