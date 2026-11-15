"""Create compact deterministic PBR atlases for EX-50; generated output is intentionally simple."""
from pathlib import Path
from PIL import Image, ImageDraw

ROOT=Path(r"C:/Users/HP/Documents/GitHub/proyectos-unity/EsneiderProtocoloLazaro/Assets/_Game/Art/Textures")
COLORS={
"OBJ-015_PulseraLazaro":(42,51,54), "OBJ-042_CierreContencion":(73,83,85),
"OBJ-071_EsclusaPresion":(60,70,72), "OBJ-073_ConsolaPrincipal":(50,61,65),
"OBJ-075_BarandaPasarela":(66,72,70), "OBJ-077_PanelEscape":(83,63,55),
"OBJ-078_CompuertaMonumental":(57,64,65), "OBJ-080_ArchivoFisico":(122,106,78),
"ENV-EXIT_ExteriorEscape":(54,57,54)}
for asset,color in COLORS.items():
    for kind,fill in (("BaseColor",color),("Roughness",(190,190,190)),("Metallic",(145,145,145)),("Normal",(128,128,255))):
        im=Image.new("RGB",(256,256),fill); d=ImageDraw.Draw(im)
        if kind=="BaseColor":
            for y in range(0,256,16): d.line((0,y,255,y),fill=tuple(max(0,c-8-(y%32)//4) for c in color),width=1)
            d.rectangle((8,8,247,247),outline=tuple(min(255,c+18) for c in color),width=2)
        im.save(ROOT/f"{asset}_{kind}.png",optimize=True)
