"""Valida JSON, archivos, hashes, duraciones y procedencia de recortes."""
import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def png_size(path):
    data = path.read_bytes()[:24]
    assert data[:8] == b'\x89PNG\r\n\x1a\n', path
    return struct.unpack('>II', data[16:24])

def main():
    documents = sorted(ROOT.glob('video-*.json'))
    assert len(documents) == 4, 'Se esperan cuatro analisis'
    textures = 0
    for path in documents:
        data = json.loads(path.read_text(encoding='utf-8'))
        source = data['fuente']
        raw = (ROOT / source['original']).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == source['metadatos']['sha256']
        assert len(raw) == source['metadatos']['bytes']
        assert data['recreacion_cpp']['apis_objetivo'] == ['OpenGL', 'Vulkan']
        end = 0
        for scene in data['secuencia']:
            assert abs(scene['inicio_aprox_s'] - end) < 0.01
            assert scene['fin_aprox_s'] > scene['inicio_aprox_s']
            assert (ROOT / scene['fotograma_referencia']).is_file()
            end = scene['fin_aprox_s']
        assert abs(end - source['metadatos']['duracion_s']) < 0.01
        for texture in data['texturas']:
            reference = texture['procedencia_recorte']
            assert 0 <= reference['tiempo_s'] < end
            width, height = png_size(ROOT / reference['fotograma'])
            x, y, w, h = reference['rectangulo_px_xywh']
            assert x >= 0 and y >= 0 and w > 0 and h > 0
            assert x + w <= width and y + h <= height
            assert png_size(ROOT / texture['recorte']) == (w, h)
            textures += 1
    print(f'Correcto: {len(documents)} JSON, {textures} recortes, originales y hashes verificados.')

if __name__ == '__main__':
    main()
