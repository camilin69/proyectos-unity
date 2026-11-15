"""Original fictional identities, explicitly recorded for future subject assets."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
ROOT=Path(__file__).resolve().parents[2]
people=[('062','M041','INÉS RIVAS','4042',90),('062B','M042','TOMÁS LEAL','4043',270),('062C','M046','LUCÍA SOLER','4044',90),('062D','M047','RAÚL MENA','4045',270),('062E','M048','ANA VIDAL','4046',90)]
records=[]
for id,cage,name,year,yaw in people:
    serial='81-'+cage[1:];asset='OBJ-'+id+'_PlacaSujeto'
    im=Image.new('RGB',(1024,512),(197,194,165));d=ImageDraw.Draw(im)
    def text(x,y,s,size,color=(30,41,39)):
        d.text((x,y),s,font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',size),fill=color)
    d.rectangle((0,0,1024,92),fill=(46,63,60));text(52,20,'NÉMESIS / REGISTRO PERSONAL',42,(226,224,197))
    text(53,110,name,70);text(53,355,'INGRESO '+year+' / SERIE 81',38)
    text(53,430,'ARCHIVO DE ADAPTACIÓN / S3',30)
    # Local rubbed corners and old screw halos; information area kept legible.
    for x,y in [(12,12),(1012,12),(12,500),(1012,500)]:d.ellipse((x-27,y-27,x+27,y+27),outline=(138,135,112),width=5)
    im.save(ROOT/'SourceArt/Textures'/('OBJ-'+id+'_Name_EX36.png'))
    overlay=Image.new('RGB',(768,144),(48,66,60));od=ImageDraw.Draw(overlay)
    od.text((25,18),'EVA / UNIDAD '+serial,font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',69),fill=(228,226,204))
    od.text((28,113),'CONSERVACIÓN / REGISTRO VIGENTE',font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',28),fill=(208,213,190))
    overlay.save(ROOT/'SourceArt/Textures'/('OBJ-'+id+'_Serial_EX36.png'))
    records.append(dict(id=id,asset=asset,cage=cage,name=name,serial=serial,admission_year=year,yaw=yaw,document='DOC-08',authorship='EX-36 original fictional identity; DOC-08 specifies Series 81, not these individual names'))
path=ROOT/'EsneiderProtocoloLazaro/Assets/_Game/Data/LevelPlan/subject_plates_ex36.json'
path.write_text(json.dumps({'subjects':records},ensure_ascii=False,indent=2),encoding='utf-8')
print('Prepared five identities and ten original images')
