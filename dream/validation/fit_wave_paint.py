"""Fit a repeating paint placement to manually interpreted source regions.

This diagnoses placement on provisional geometry; it cannot validate geometry,
physical material values, or fidelity beyond the labeled foreground samples.
"""
import json
from pathlib import Path
import numpy as np
from scipy.optimize import differential_evolution

ROOT = Path(__file__).resolve().parent
data = json.loads((ROOT/'wave-floor-colour-landmarks.json').read_text())
rows = [r for r in data['landmarks'] if r['pixel'][1] >= 490 and r['hit'].endswith('floor')]
xy = np.array([r['metric_uv'] for r in rows])
labels = [r['colour_label_estimate'] for r in rows]
bands = {'teal': [(-100, -1.08), (.71, 100)], 'ochre': [(-1.01, -.85), (-.15, .19)],
         'pink': [(-.79, -.54)], 'coral': [(-.48, -.21)], 'lavender': [(.25, .64)]}


def residuals(p):
    px, py, phase, offset = p
    x = ((xy[:, 0]/px+.5+offset) % 1)*6.6-3.3
    angle = 2*np.pi*(xy[:, 1]/py+phase)
    centre = 1.26*np.sin(angle+.35)+.20*np.sin(2*angle-.75)
    width = 1+.14*np.sin(angle-.5)+.05*np.cos(2*angle)
    q = (x-centre)/width
    return np.array([min(max(lo-v, 0, v-hi) for lo, hi in bands[label])
                     for v, label in zip(q, labels)])


baseline = [6.6, 5.5, 0, 0]
fit = differential_evolution(lambda p: np.mean(residuals(p)**2)+.00001*((p[0]-6.6)**2+(p[1]-5.5)**2),
                             [(3, 12), (3, 12), (0, 1), (-.25, .25)], seed=420014,
                             tol=1e-8, maxiter=400, popsize=20)
report = {'schema': 'dream.wave_paint_fit.v1', 'accepted': False,
          'status': 'candidate_needs_render_and_secondary_view',
          'parameters': dict(zip(['period_x_m', 'period_s_m', 'phase', 'offset_u'], fit.x.tolist())),
          'baseline': baseline, 'source': 'wave-reference-14s.png',
          'sample_count': len(rows), 'manual_samples': rows,
          'baseline_interval_rms': float(np.sqrt(np.mean(residuals(baseline)**2))),
          'candidate_interval_rms': float(np.sqrt(np.mean(residuals(fit.x)**2))),
          'candidate_interval_errors': residuals(fit.x).tolist(),
          'limitations': ['Manual colour labels may be ambiguous under light/reflections.',
                         'Only foreground points used; distant geometry already mismatches the reference.',
                         'This is a fit diagnostic, not a fidelity score or validation set.']}
(ROOT/'wave-paint-fit.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ('manual_samples','limitations')}))
