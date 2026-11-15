"""Inventory source evidence against all 80 object sheets; never infer acceptance from existence."""
import json,re
from pathlib import Path
root=Path(__file__).resolve().parents[2]
doc=(root/'docs/ESNEIDER_FICHAS_OBJETOS.md').read_text(encoding='utf-8-sig')
entries=[]
sources=list((root/'SourceArt/Blender').glob('*.blend'))
for match in re.finditer(r'^### (OBJ-\d+) · (.+)$',doc,re.M):
    id,name=match.groups()
    block=doc[match.end():].split('\n### ',1)[0]
    sources_for_id=[str(p.relative_to(root)).replace('\\','/') for p in sources if p.name.startswith(id+'_')]
    entries.append({'id':id,'name':name,'requirements_markdown':block.strip(),'source_files':sources_for_id,
                    'state':'Revisar' if sources_for_id else 'Pendiente','acceptance_proven':False})
for p in sources:
    if p.name.startswith(('OBJ-','NAV-','HUM-','ENV-EXIT')) or p.name=='S1_ServiceKit.blend': continue
    entries.append({'id':p.stem,'name':p.stem,'source_files':[str(p.relative_to(root)).replace('\\','/')],
                    'state':'Revisar','acceptance_proven':False})
for id,name in [('HUM-01','Adulto dormido'),('HUM-02','Adulto con injertos'),('HUM-03','Adulto deteriorado'),('ENV-EXIT','Exterior de escape')]+[(f'NAV-{i:02d}','Señalética de sector') for i in range(1,8)]:
    entries.append({'id':id,'name':name,'source_files':[],'state':'Pendiente','acceptance_proven':False})
out=root/'docs/produccion/MODELOS_PENDIENTES_EX12.json'
status_path=root/'docs/produccion/MODELOS_ESTADO_EX12.json'
if status_path.exists():
    statuses=json.loads(status_path.read_text(encoding='utf-8'))
    for entry in entries: entry.update(statuses.get(entry['id'],{}))
out.write_text(json.dumps({'scope':'80 fichas OBJ + actores/armas/consumibles existentes + HUM-01/02/03 + NAV-01..07 + ENV-EXIT; las variantes indicadas en cada ficha forman parte del alcance',
                           'objects_in_sheets':80,'entries':entries},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'entries':len(entries),'object_sheets':sum(e['id'].startswith('OBJ-') for e in entries),'output':str(out)}))
