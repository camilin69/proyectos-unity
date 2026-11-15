"""Build the staggered entrance through Blender MCP, preserving older drafts."""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def build():
    path=ROOT/'blender/build_wave_terminal_candidate.py'
    ns={'__file__':str(path),'__name__':'aperture_build_helpers'}
    exec(compile(path.read_text(encoding='utf-8'),str(path),'exec'),ns)
    ns['build'](report_path='validation/wave-aperture/fit.json',
                output_path='blender/wave_corridor_aperture_candidate.blend',
                audit_path='validation/wave-aperture/native-audit.json')

if __name__=='__main__':build()
