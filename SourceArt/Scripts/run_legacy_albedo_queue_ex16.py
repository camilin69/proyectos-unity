"""Sequential MCP calls with per-asset logs; refuses to continue after an uncertain failure."""
import json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
EVIDENCE=ROOT/'SourceArt/_evidence/EX-16'
CLIENT=ROOT/'SourceArt/Scripts/blender_mcp_client.py'
PYTHON='C:/Users/HP/AppData/Roaming/uv/tools/mcp-for-blender/Scripts/python.exe'
targets=sys.argv[1:]
if not targets:raise SystemExit('Pass exact asset IDs after inspecting source-inspection.json')
env=dict(os.environ,BLENDER_PORT='9877')
for asset in targets:
    if (EVIDENCE/asset/'repair.json').exists():
        raise SystemExit(f'{asset} already has a repair receipt; verify before rerunning')
    request=EVIDENCE/(asset+'-request.json')
    request.write_text(json.dumps({'user_prompt':'modelar todos los modelos restantes',
        'code':f'import repair_legacy_albedo_ex16 as R; print(R.repair({asset!r}))'}),encoding='utf-8')
    print('START '+asset,flush=True)
    with (EVIDENCE/(asset+'-client.log')).open('w',encoding='utf-8') as log:
        result=subprocess.run([PYTHON,str(CLIENT),'execute_blender_code',str(request)],env=env,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    if result.returncode or not (EVIDENCE/asset/'repair.json').exists():
        raise SystemExit(f'{asset}: receipt missing or MCP failure; inspect live Blender before retry')
    print('DONE '+asset,flush=True)
