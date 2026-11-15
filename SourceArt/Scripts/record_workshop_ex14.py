"""Record verified EX14 delivery without equating integration to artistic acceptance."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
status_path = root / 'docs/produccion/MODELOS_ESTADO_EX12.json'
statuses = json.loads(status_path.read_text(encoding='utf-8'))
placements = {
    '019': ('TaladroFijo', 'EX14_Drill'),
    '023': ('BandejaPiezas', 'EX14_PartsTray'),
    '031': ('BombaIndustrial', 'EX14_ServicePump'),
    '032': ('GeneradorLocal', 'EX14_Generator'),
    '034': ('ValvulaBridada', 'EX14_SpareValve'),
    '035': ('Extintor', 'EX14_WallExtinguisher'),
    '036': ('SoldadorCarrito', 'EX14_Welder'),
    '037': ('Herramientas', 'EX14_ToolSet'),
}
for number, (name, instance) in placements.items():
    asset = f'OBJ-{number}_{name}'
    evidence = f'SourceArt/_evidence/EX-14/{asset}'
    geometry = json.loads((root / evidence / 'geometry.json').read_text(encoding='utf-8'))
    remaining = ['desgaste localizado y variantes segun ficha', 'revision artistica con iluminacion final']
    if number in ('031', '032'):
        remaining += ['estado operativo, vibracion y audio segun ficha; conexiones exteriores de servicio']
    statuses[f'OBJ-{number}'] = {
        'state': 'Integrado', 'acceptance_proven': False,
        'evidence': evidence, 'remaining': remaining,
        'prefab': f'EsneiderProtocoloLazaro/Assets/_Game/Prefabs/Environment/{asset}.prefab',
        'instances': [f'REG-S2/{instance}'],
        'triangles': geometry['triangles'], 'texture_sets': 1,
    }
status_path.write_text(json.dumps(statuses, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('Recorded eight integrated workshop models; artistic acceptance remains false.')
