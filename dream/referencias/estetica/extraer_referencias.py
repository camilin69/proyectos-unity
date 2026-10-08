"""Extrae evidencia visual sin reinterpretar ni generar texturas nuevas.

Uso: python extraer_referencias.py [carpeta_con_originales]
Requiere ffmpeg y ffprobe en PATH; solo usa la biblioteca estandar de Python.
"""
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'originales'
SAMPLES = {'35': [1, 5, 9, 11, 15, 19, 21, 27], '42': [2, 7, 13, 20], '51': [1, 5, 9], '52': [1, 5, 9, 13]}
CROPS = {
    '35': [('agua_espuma', 1, [180, 250, 450, 420]), ('peluche_rosa', 9, [155, 945, 355, 180]), ('cesped', 9, [578, 560, 132, 300]), ('azulejos_pastel', 11, [356, 234, 88, 440]), ('tela_cuadros', 11, [464, 172, 60, 290]), ('pavimento_mojado', 5, [230, 830, 175, 355]), ('suelo_iridiscente', 11, [155, 857, 380, 330])],
    '42': [('cesped_interior', 2, [122, 577, 276, 218]), ('azulejo_rosa', 7, [22, 82, 89, 118]), ('agua_turquesa', 7, [133, 545, 210, 235]), ('suelo_ondas_pintadas', 13, [62, 578, 348, 251]), ('techo_texturado', 13, [12, 8, 160, 82]), ('pasarela_ceramica', 20, [116, 605, 262, 235]), ('agua_oscura', 20, [4, 357, 78, 163])],
    '51': [('corteza', 1, [93, 127, 67, 111]), ('follaje', 1, [195, 45, 145, 55]), ('hierba', 1, [17, 276, 150, 45]), ('cielo', 1, [380, 310, 100, 30])],
    '52': [('asiento_azul', 1, [6, 427, 97, 220]), ('cojin_lima', 1, [65, 533, 54, 30]), ('suelo_pulido', 1, [164, 562, 163, 280]), ('plantas_colgantes', 1, [405, 45, 45, 130]), ('agua_causticas', 5, [17, 610, 170, 200]), ('vidrio_metal', 9, [54, 340, 94, 290]), ('mapa_globo', 13, [189, 258, 183, 181])]
}

def run(*args):
    return subprocess.check_output(args, text=True, encoding='utf-8')

def main():
    records = {}
    for ident, times in SAMPLES.items():
        name = f'WhatsApp Video 2026-10-08 at 6.27.{ident} PM.mp4'
        src = SOURCE / name
        target = ROOT / 'originales' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if src.resolve() != target.resolve():
            shutil.copy2(src, target)
        probe = json.loads(run('ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(target)))
        video = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        records[ident] = {'archivo': name, 'sha256': hashlib.sha256(target.read_bytes()).hexdigest(), 'bytes': target.stat().st_size, 'duracion_s': float(probe['format']['duration']), 'ancho_px': video['width'], 'alto_px': video['height'], 'fps': video['r_frame_rate'], 'codec': video['codec_name'], 'contiene_audio': any(s['codec_type'] == 'audio' for s in probe['streams'])}
        output = ROOT / 'evidencias' / f'video-{ident}'
        output.mkdir(parents=True, exist_ok=True)
        for t in times:
            run('ffmpeg', '-hide_banner', '-loglevel', 'error', '-ss', str(t), '-i', str(target), '-frames:v', '1', '-y', str(output / f'{t:02d}s.png'))
        textures = ROOT / 'texturas' / f'video-{ident}'
        textures.mkdir(parents=True, exist_ok=True)
        for label, t, (x, y, w, h) in CROPS[ident]:
            run('ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', str(output / f'{t:02d}s.png'), '-vf', f'crop={w}:{h}:{x}:{y}', '-frames:v', '1', '-y', str(textures / f'{label}.png'))
    (ROOT / 'metadatos.json').write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

if __name__ == '__main__':
    main()
