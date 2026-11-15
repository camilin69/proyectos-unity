"""Original synthesized score and robot explosion; no external samples. EX58."""
from pathlib import Path
import wave
import numpy as np

SR = 32000
OUT = Path(__file__).resolve().parents[2] / 'EsneiderProtocoloLazaro/Assets/_Game/Resources/Music'
OUT.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(2058)

def save(name, sound):
    peak = max(float(np.max(np.abs(sound))), .001)
    sound = np.clip(sound / peak * .78, -1, 1)
    if sound.ndim == 1:
        sound = np.stack([sound, sound], axis=1)
    with wave.open(str(OUT / (name + '.wav')), 'wb') as f:
        f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR)
        f.writeframes((sound * 32767).astype('<i2').tobytes())
    print(name, 'seconds', round(len(sound) / SR, 2), 'peak', round(float(np.max(np.abs(sound))), 3))

for stage, bpm in enumerate([64, 80, 96, 112, 128]):
    beat = 60 / bpm; duration = beat * 32
    t = np.arange(round(SR * duration)) / SR
    left = np.zeros(len(t)); right = np.zeros(len(t))
    for degree, amplitude in [(0, .16), (7, .065), (10, .035 + stage * .01), (13, stage * .009)]:
        freq = round(73.416 * 2 ** (degree / 12) * duration) / duration
        swell = .7 + .3 * np.sin(2 * np.pi * t / duration - np.pi / 2)
        left += amplitude * swell * np.sin(2 * np.pi * freq * t + .15 * np.sin(2 * np.pi * t / duration))
        right += amplitude * swell * np.sin(2 * np.pi * freq * t + .15 * np.cos(2 * np.pi * t / duration))
    subdivision = 1 if stage < 2 else 2 if stage < 4 else 4
    motif = [0, 7, 10, 7, 0, 6, 10, 3]
    for step in range(32 * subdivision):
        start = int(step * beat / subdivision * SR)
        count = min(int(beat * .72 * SR), len(t) - start)
        x = np.arange(count) / SR
        if stage > 0:
            freq = 146.832 * 2 ** (motif[step % 8] / 12)
            note = .1 * np.sin(2 * np.pi * freq * x) * (1 - np.exp(-x * 100)) * np.exp(-x * 9)
            pan = .25 if step % 2 else .75
            left[start:start+count] += note * pan; right[start:start+count] += note * (1-pan)
        if step % subdivision == 0 and stage >= 1:
            kick = (.10 + stage * .025) * np.sin(2 * np.pi * (44 * x + .8 * (1 - np.exp(-x * 35)))) * np.exp(-x * 16)
            left[start:start+count] += kick; right[start:start+count] += kick
        if stage >= 2:
            tick = rng.uniform(-1, 1, count) * np.exp(-x * 85) * (.025 + stage * .01)
            left[start:start+count] += tick; right[start:start+count] += tick * .8
    fade = np.minimum(1, np.minimum(t, duration-t) / .04)
    save('Tension' + str(stage), np.stack([left * fade, right * fade], axis=1))

t = np.arange(int(SR * 1.7)) / SR
noise = rng.uniform(-1, 1, len(t))
blast = .55 * noise * np.exp(-t * 8) + .55 * np.sin(2 * np.pi * (36*t + 1.2*(1-np.exp(-t*40)))) * np.exp(-t*5)
for when in [.08, .17, .29, .43, .61]:
    x = np.maximum(0, t-when)
    blast += (t>=when) * .09 * np.sin(2*np.pi*(1300*x+200*x*x)) * np.exp(-x*35)
blast *= np.minimum(1, t/.003)
save('RobotExplosion', blast)
