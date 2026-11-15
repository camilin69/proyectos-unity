"""Original EVA ration packaging artwork; fictional project dates."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
out=ROOT/'SourceArt/Textures';out.mkdir(exist_ok=True)
im=Image.new('RGB',(1024,614),(155,164,144));d=ImageDraw.Draw(im)
def text(x,y,s,size,color=(26,43,41)):
    d.text((x,y),s,font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',size),fill=color)
d.rounded_rectangle((94,78,930,532),radius=24,fill=(212,216,192),outline=(43,65,59),width=5)
d.rectangle((95,79,929,159),fill=(39,65,59))
text(130,92,'EVA / CONTINUIDAD',48,(231,231,209))
text(132,185,'RACIÓN SELLADA',65)
text(135,274,'RESERVA DE MANTENIMIENTO',31)
d.line((135,331,887,331),fill=(65,84,69),width=3)
text(135,356,'PRODUCIDO: 4046-09',35)
text(135,405,'CONSUMIR ANTES: 4047-09',31)
text(135,468,'LOTE EVA-R046-09  /  1 UNIDAD',27)
# Heat-seal printing and opening instruction stay outside the main label.
text(86,26,'ABRIR POR LA MUESCA',25)
for x in (22,37,52,970,985,1000):d.line((x,35,x,579),fill=(105,123,109),width=3)
for i in range(29):
    x=720+i*5;d.rectangle((x,349,x+1+(i%3==0),416),fill=(26,43,41))
im.save(out/'OBJ-057_Front_EX35.png')
back=Image.new('RGB',(1024,614),(148,158,139));bd=ImageDraw.Draw(back)
bd.rounded_rectangle((240,165,784,449),radius=16,fill=(206,212,189),outline=(43,65,59),width=4)
for y,s,size in [(192,'EVA / SUMINISTROS',38),(253,'ENVASE HERMÉTICO',35),(315,'CONSERVAR EL SELLO',28),(369,'EVA-R046-09',32)]:
    bd.text((276,y),s,font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',size),fill=(26,43,41))
back.save(out/'OBJ-057_Back_EX35.png')
print('Prepared two original package faces')
