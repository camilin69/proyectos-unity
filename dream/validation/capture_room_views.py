"""Capture material checks from two walkable positions; restore camera config."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
from PIL import Image

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--revision', default='v7', choices=['v6', 'v7'])
revision = parser.parse_args().revision
config = root / 'assets/pastel_room.scene'
original = config.read_bytes()
original_hash = hashlib.sha256(original).hexdigest()
views = [
    (f'room-view-radiator-{revision}', [-1.2, -.9, 1.4, .79, -.32]),
    (f'room-view-right-{revision}', [-.65, -1.8, 1.4, 1.60, -.21]),
]
records = []
try:
    for name, camera in views:
        lines = original.decode('utf-8').splitlines()
        lines = ['camera ' + ' '.join(map(str, camera)) if line.startswith('camera ') else line for line in lines]
        config.write_text('\n'.join(lines) + '\n', encoding='utf-8')
        capture = root / 'validation' / (name + '.ppm')
        args = [str(root / 'runtime/build/dream.exe'), '--hidden', '--frames', '8',
                '--samples', '4', '--width', '960', '--height', '720', '--time', '0',
                '--capture', str(capture)]
        run = subprocess.run(args, capture_output=True, text=True)
        if run.returncode or not re.search(r'gl_error=0\b', run.stdout):
            raise RuntimeError(run.stdout + run.stderr)
        output = capture.with_suffix('.png')
        Image.open(capture).save(output)
        records.append({'camera': camera, 'image': output.name,
                        'image_sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
                        'output': run.stdout.strip()})
finally:
    config.write_bytes(original)

assert hashlib.sha256(config.read_bytes()).hexdigest() == original_hash
report = {'result': 'PASS', 'revision': revision, 'scope': 'Two fixed, walkable-position material captures; visual review is separate.',
          'size': [960, 720], 'opaque_samples': 4, 'frames_each': 8, 'fixed_time_s': 0,
          'configuration_restored_sha256': original_hash, 'captures': records,
          'performance_claim': False, 'performance_context': 'Other GPU workload was not isolated or measured.'}
(root / 'validation' / f'room-views-{revision}.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(json.dumps(report))
