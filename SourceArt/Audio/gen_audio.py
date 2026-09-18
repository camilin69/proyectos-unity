# Banco de audio ORIGINAL sintetizado (secciones 17, 50.2, 72.2). Generado procedimentalmente con numpy/scipy: sin muestras externas.
# Todo archivo queda identificado como "generado" en el manifiesto (72.4). WAV 48 kHz / 24 bit mono (beds estéreo).
import numpy as np, os, json, math
from scipy import signal
from scipy.io import wavfile

SR = 48000
ROOT = r"C:/Users/HP/Documents/GitHub/proyectos-unity"
OUT = ROOT + "/EsneiderProtocoloLazaro/Assets/_Game/Audio"
manifest = []
rng = np.random.default_rng(2038)


def save(rel, y, stereo=False):
    y = np.asarray(y, dtype=np.float64)
    if y.ndim == 1 and stereo: y = np.stack([y, y], axis=1)
    peak = np.max(np.abs(y)) or 1.0
    y = y / peak * 0.85
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = (y * (2 ** 23 - 1)).astype(np.int32) << 8  # 24 bit en contenedor 32
    wavfile.write(path, SR, data)
    manifest.append({"id": os.path.splitext(os.path.basename(rel))[0], "file": rel, "seconds": round(len(y) / SR, 3), "channels": 2 if y.ndim == 2 else 1, "sample_rate": SR, "origin": "generado (numpy/scipy, gen_audio.py)", "license": "original del proyecto"})
    return path


def env(n, a=0.01, d=0.1, s=0.6, r=0.2, hold=None):
    t = np.arange(n) / SR
    T = n / SR
    e = np.ones(n)
    a_n, d_n, r_n = int(a * SR), int(d * SR), int(r * SR)
    e[:a_n] = np.linspace(0, 1, max(a_n, 1))
    e[a_n:a_n + d_n] = np.linspace(1, s, max(d_n, 1))[:max(0, min(d_n, n - a_n))]
    e[a_n + d_n:n - r_n] = s
    if r_n > 0: e[n - r_n:] = np.linspace(s, 0, r_n)
    return e


def noise(n, color='white'):
    w = rng.standard_normal(n)
    if color == 'pink':
        b, a = signal.butter(1, 0.02); w = signal.lfilter(b, a, w) * 6
    elif color == 'brown':
        w = np.cumsum(w); w -= np.linspace(w[0], w[-1], n); w /= (np.max(np.abs(w)) or 1)
    return w


def bp(y, lo, hi, order=4):
    b, a = signal.butter(order, [lo / (SR / 2), hi / (SR / 2)], btype='band'); return signal.lfilter(b, a, y)


def lp(y, f, order=4):
    b, a = signal.butter(order, f / (SR / 2)); return signal.lfilter(b, a, y)


def hp(y, f, order=2):
    b, a = signal.butter(order, f / (SR / 2), btype='high'); return signal.lfilter(b, a, y)


def tone(n, f, kind='sine', drift=0.0):
    t = np.arange(n) / SR
    ph = 2 * np.pi * np.cumsum(f * (1 + drift * np.sin(2 * np.pi * 0.7 * t))) / SR if drift else 2 * np.pi * f * t
    if kind == 'saw': return 2 * ((ph / (2 * np.pi)) % 1) - 1
    if kind == 'square': return np.sign(np.sin(ph))
    return np.sin(ph)


def reverb(y, decay=1.2, mix=0.3, predelay=0.02):
    n = len(y); ir_n = int(decay * SR)
    ir = noise(ir_n) * np.exp(-np.arange(ir_n) / (decay * SR / 6.0))
    ir = lp(ir, 3500); ir[:int(predelay * SR)] = 0
    wet = signal.fftconvolve(y, ir)[:n]
    wet /= (np.max(np.abs(wet)) or 1)
    return (1 - mix) * y + mix * wet * (np.max(np.abs(y)) or 1)


def loopable(y, fade=0.5):
    n = int(fade * SR); w = np.linspace(0, 1, n)
    y = y.copy(); y[:n] = y[:n] * w + y[-n:] * (1 - w); return y[:-n]


# ---------- Vigía (12.1/72.2) ----------
def servo(dur, f0, f1):
    n = int(dur * SR); t = np.arange(n) / SR
    f = np.linspace(f0, f1, n)
    y = tone(n, f, 'saw') * 0.5 + tone(n, f * 2.01, 'sine') * 0.3
    y = bp(y, 400, 5000) * env(n, 0.005, 0.05, 0.5, 0.08)
    y += bp(noise(n), 2000, 7000) * env(n, 0.002, 0.02, 0.1, 0.05) * 0.3
    return y


for i, (d, f0, f1) in enumerate(((0.3, 380, 520), (0.42, 300, 700), (0.36, 450, 410))):
    y = servo(d, f0, f1)
    n = len(y); click = bp(noise(n), 800, 3000) * env(n, 0.001, 0.01, 0.0, 0.02) * 0.6
    y = y + click + lp(noise(n), 200) * env(n, 0.002, 0.05, 0.0, 0.05) * 0.5  # apoyo pequeño
    save(f"Enemies/SND-VIG-Step-{'ABC'[i]}.wav", y)

for name, dur in (("SND-VIG-NetCharge", 1.1), ("SND-VIG-NetCharge-Tutorial", 1.2)):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 120 * (2 ** (t / dur * 4.2))  # ascenso eléctrico
    y = tone(n, f, 'saw') * 0.4 + tone(n, f * 1.5, 'square') * 0.15
    y = bp(y, 150, 6000) * (0.3 + 0.7 * t / dur)
    y += bp(noise(n), 3000, 12000) * (t / dur) ** 2 * 0.35  # arco
    latch = np.zeros(n); k = int(0.92 * n); latch[k:k + int(0.05 * SR)] = bp(noise(int(0.05 * SR)), 1500, 4000) * env(int(0.05 * SR), 0.001, 0.02, 0.2, 0.02)
    save(f"Enemies/{name}.wav", y * env(n, 0.02, 0.1, 1.0, 0.02) + latch * 0.9)

n = int(0.35 * SR); y = bp(noise(n), 200, 1500) * env(n, 0.001, 0.05, 0.2, 0.15) + tone(n, np.linspace(900, 200, n)) * env(n, 0.001, 0.08, 0.0, 0.05) * 0.6
save("Enemies/SND-VIG-NetRelease.wav", y)
n = int(0.6 * SR); y = bp(noise(n), 1500, 9000) * (0.5 + 0.5 * np.sign(tone(n, 60, 'square'))) * env(n, 0.005, 0.1, 0.6, 0.3)
save("Enemies/SND-VIG-NetImpact.wav", y)

# ---------- Custodio (13/72.2) ----------
for i, (d, f0) in enumerate(((0.55, 70), (0.7, 55), (0.62, 62))):
    n = int(d * SR)
    y = lp(noise(n), 160) * env(n, 0.002, 0.08, 0.2, 0.3) * 1.2 + tone(n, f0) * env(n, 0.001, 0.15, 0.0, 0.1) * 0.8  # metal pesado + goma
    s = servo(d * 0.5, 180, 260); y[:len(s)] += s * 0.25
    y += bp(noise(n), 700, 2500) * env(n, 0.001, 0.02, 0.05, 0.15) * 0.4
    save(f"Enemies/SND-KUS-Step-{'ABC'[i]}.wav", y)
n = int(1.0 * SR); t = np.arange(n) / SR
f = 55 + 40 * t; y = tone(n, f) * 0.5 + tone(n, 50 * 2 ** (t * 2.5), 'square') * 0.12 * t
y = lp(y, 2500) + bp(noise(n), 4000, 14000) * (t ** 3) * 0.5  # condensador + emisor
save("Enemies/SND-KUS-RayCharge.wav", y * env(n, 0.02, 0.1, 1.0, 0.02))
n = int(0.5 * SR); y = bp(noise(n), 300, 12000) * env(n, 0.001, 0.05, 0.3, 0.3) + tone(n, 90) * env(n, 0.001, 0.1, 0.0, 0.2)
save("Enemies/SND-KUS-RayRelease.wav", y)
n = int(0.7 * SR); y = bp(noise(n), 100, 8000) * env(n, 0.001, 0.1, 0.4, 0.4) * (0.6 + 0.4 * np.sign(tone(n, 50, 'square')))
save("Enemies/SND-KUS-RayImpact.wav", y)

# ---------- Archivista: cuatro firmas (60.4/72.2) ----------
sig = {"Ray": (1.2, lambda n, t: tone(n, 40 + 60 * t) * 0.5 + bp(noise(n), 5000, 15000) * t ** 3 * 0.5),
       "Sweep": (1.4, lambda n, t: servo(1.4, 120, 60)[:n] * 0.7 + lp(noise(n), 300) * t * 0.5),
       "Charge": (1.5, lambda n, t: lp(noise(n), 120) * (t ** 1.5) * 1.2 + tone(n, 30 + 30 * t) * 0.5),
       "Pulse": (1.8, lambda n, t: tone(n, 35) * (0.5 + 0.5 * np.sin(2 * np.pi * 6 * t * (1 + t))) * 0.8 + bp(noise(n), 200, 900) * t * 0.4)}
for k, (d, fn) in sig.items():
    n = int(d * SR); t = np.arange(n) / SR / d
    save(f"Enemies/SND-BOSS-{k}.wav", fn(n, t) * env(n, 0.03, 0.1, 1.0, 0.02))
for i in range(4):
    n = int(0.9 * SR); y = lp(noise(n), 110) * env(n, 0.002, 0.1, 0.2, 0.5) * 1.5 + tone(n, 38 + i * 3) * env(n, 0.001, 0.2, 0.0, 0.2)
    save(f"Enemies/SND-BOSS-Step-{'ABCD'[i]}.wav", y)

# ---------- Esneider: pasos por superficie, respiración (50.2/96.2) ----------
surf = {"CON": (600, 3000, 'white', 0.05), "MET": (300, 6000, 'white', 0.18), "GRT": (250, 4000, 'white', 0.25), "WET": (500, 5000, 'white', 0.09), "RUB": (100, 600, 'pink', 0.06)}
for sid, (lo, hi, col, tail) in surf.items():
    for i in range(4):
        n = int((0.18 + tail) * SR); y = bp(noise(n, col), lo * (0.9 + 0.2 * rng.random()), hi, 2) * env(n, 0.001, 0.03, 0.15, tail)
        if sid in ("MET", "GRT"): y += tone(n, 800 + 300 * rng.random()) * env(n, 0.001, 0.02, 0.0, tail) * 0.25
        if sid == "WET": y += bp(noise(n), 3000, 9000) * env(n, 0.005, 0.05, 0.0, 0.05) * 0.3
        save(f"Player/SND-STEP-{sid}-{i + 1}.wav", y)
for i in range(5):
    n = int((1.1 + 0.3 * i) * SR); t = np.arange(n) / SR
    y = bp(noise(n, 'pink'), 200, 2500) * (0.5 + 0.5 * np.sin(np.pi * t / (n / SR))) ** 2
    save(f"Player/SND-BREATH-{i + 1}.wav", y)
n = int(0.4 * SR); save("Player/SND-HURT.wav", bp(noise(n), 150, 1500) * env(n, 0.001, 0.05, 0.3, 0.2) + tone(n, np.linspace(220, 140, n)) * env(n, 0.001, 0.1, 0.0, 0.1) * 0.4)

# ---------- Armas (38/50.2) ----------
for i in range(3):
    n = int(0.4 * SR); y = tone(n, 1200 * (0.9 + 0.2 * rng.random())) * env(n, 0.0005, 0.03, 0.0, 0.25) * 0.5 + bp(noise(n), 400, 5000) * env(n, 0.0005, 0.02, 0.1, 0.1)
    save(f"Weapons/SND-CROWBAR-Swing-{i + 1}.wav", bp(noise(int(0.25 * SR)), 100, 900) * env(int(0.25 * SR), 0.02, 0.1, 0.3, 0.05))
    save(f"Weapons/SND-CROWBAR-ImpactMetal-{i + 1}.wav", y)
    save(f"Weapons/SND-CROWBAR-ImpactConcrete-{i + 1}.wav", bp(noise(n), 200, 2500) * env(n, 0.0005, 0.04, 0.1, 0.12))
for i in range(3):
    n = int(0.45 * SR); y = bp(noise(n), 60, 9000, 2) * env(n, 0.0005, 0.02, 0.15, 0.3) * 1.2 + tone(n, 110) * env(n, 0.0005, 0.06, 0.0, 0.1) * 0.6
    save(f"Weapons/SND-PISTOL-Shot-{i + 1}.wav", hp(y, 40))
    n = int(0.7 * SR); y = bp(noise(n), 40, 6000, 2) * env(n, 0.0005, 0.05, 0.25, 0.5) * 1.4 + tone(n, 70) * env(n, 0.0005, 0.12, 0.0, 0.2)
    save(f"Weapons/SND-SHOTGUN-Shot-{i + 1}.wav", hp(y, 30))
def click(dur, f):
    n = int(dur * SR); return bp(noise(n), f, f * 4) * env(n, 0.0005, 0.01, 0.1, 0.03)
save("Weapons/SND-PISTOL-MagOut.wav", click(0.12, 700)); save("Weapons/SND-PISTOL-MagIn.wav", click(0.15, 500) + click(0.15, 1500) * 0.5); save("Weapons/SND-PISTOL-Slide.wav", click(0.18, 900))
save("Weapons/SND-SHOTGUN-ShellIn.wav", click(0.14, 600)); save("Weapons/SND-SHOTGUN-Pump.wav", np.concatenate([click(0.12, 500), np.zeros(int(0.08 * SR)), click(0.1, 800)]))
save("Weapons/SND-EMPTY-Click.wav", click(0.08, 1200))
save("Weapons/SND-FLASHLIGHT-Switch.wav", click(0.06, 2000))
n = int(0.5 * SR); _c = click(0.05, 1500); _h = bp(noise(n - len(_c)), 2000, 6000) * env(n - len(_c), 0.05, 0.2, 0.3, 0.1) * 0.3
save("Weapons/SND-SYRINGE-Use.wav", np.concatenate([_c, _h]))
save("Weapons/SND-RATION-Open.wav", bp(noise(int(0.6 * SR)), 1500, 9000) * (0.5 + 0.5 * np.sin(2 * np.pi * 9 * np.arange(int(0.6 * SR)) / SR)) * env(int(0.6 * SR), 0.01, 0.1, 0.5, 0.2))

# ---------- Ambientes por espacio (50.1) ----------
def bed(dur, layers):
    n = int(dur * SR); y = np.zeros(n)
    for kind, lo, hi, gain in layers:
        if kind == 'air': y += bp(noise(n, 'pink'), lo, hi, 2) * gain
        elif kind == 'hum': y += (tone(n, lo, drift=0.002) + tone(n, lo * 2, drift=0.002) * 0.4) * gain
        elif kind == 'drip':
            for _ in range(int(dur / 4)):
                k = int(rng.random() * (n - SR)); d = int(0.12 * SR)
                y[k:k + d] += tone(d, 1800 + 600 * rng.random()) * env(d, 0.001, 0.03, 0.0, 0.05) * gain
        elif kind == 'pump':
            per = int(lo * SR)
            for k in range(0, n - int(0.4 * SR), per):
                d = int(0.4 * SR); y[k:k + d] += lp(noise(d), 200) * env(d, 0.05, 0.1, 0.3, 0.2) * gain
    return loopable(y, 1.0)
save("Ambience/SND-AMBI-S1.wav", bed(45, [('air', 80, 400, 0.4), ('hum', 48, 0, 0.12), ('drip', 0, 0, 0.5)]), stereo=True)
save("Ambience/SND-AMBI-C1.wav", bed(40, [('air', 60, 250, 0.5), ('hum', 40, 0, 0.1)]), stereo=True)
save("Ambience/SND-AMBI-S2.wav", bed(45, [('air', 100, 500, 0.35), ('hum', 60, 0, 0.3), ('hum', 91, 0, 0.1)]), stereo=True)
save("Ambience/SND-AMBI-C2.wav", bed(40, [('air', 50, 300, 0.5), ('drip', 0, 0, 0.7)]), stereo=True)
save("Ambience/SND-AMBI-S3.wav", bed(45, [('air', 120, 700, 0.3), ('pump', 3.2, 0, 0.6), ('hum', 55, 0, 0.08)]), stereo=True)
save("Ambience/SND-AMBI-C3.wav", bed(40, [('air', 40, 200, 0.6)]), stereo=True)
save("Ambience/SND-AMBI-S4.wav", bed(45, [('air', 150, 900, 0.3), ('hum', 35, 0, 0.25)]), stereo=True)
save("Ambience/SND-EXIT-Air.wav", bed(30, [('air', 200, 3000, 0.6)]), stereo=True)
n = int(0.8 * SR); save("Ambience/SND-PIPE-Hit.wav", tone(n, 240) * env(n, 0.001, 0.2, 0.0, 0.5) + bp(noise(n), 300, 2000) * env(n, 0.001, 0.05, 0.0, 0.2))
n = int(3.0 * SR); save("Ambience/SND-LIGHT-Hum.wav", loopable(tone(n, 120) * 0.3 + tone(n, 240) * 0.15 + bp(noise(n), 3000, 8000) * 0.05, 0.3))

# ---------- Puertas / mecanismos (72.2) ----------
n = int(0.4 * SR); save("World/SND-DOOR-Slide-Start.wav", lp(noise(n), 400) * env(n, 0.05, 0.1, 0.6, 0.1) + tone(n, 55) * env(n, 0.02, 0.2, 0.5, 0.1) * 0.5)
n = int(1.0 * SR); save("World/SND-DOOR-Slide-Loop.wav", loopable(lp(noise(n), 500) * 0.5 + tone(n, 60, drift=0.01) * 0.3 + bp(noise(n), 800, 2500) * 0.15, 0.2))
n = int(0.5 * SR); _end = lp(noise(n), 300) * env(n, 0.001, 0.1, 0.2, 0.3); _lt = click(0.12, 500); _end[int(0.2 * SR):int(0.2 * SR) + len(_lt)] += _lt
save("World/SND-DOOR-Slide-End.wav", _end)
save("World/SND-LEVER.wav", np.concatenate([click(0.15, 300), np.zeros(int(0.2 * SR)), click(0.1, 900), lp(noise(int(0.6 * SR)), 250) * env(int(0.6 * SR), 0.01, 0.1, 0.4, 0.3) * 0.5]))
_r = click(0.09, 1100); _r2 = click(0.06, 1800); _r[int(0.03 * SR):int(0.03 * SR) + len(_r2)] += _r2
save("World/SND-RELAY.wav", _r)
n = int(1.8 * SR); t = np.arange(n) / SR
alert = (tone(n, 880) * 0.5 + tone(n, 1320) * 0.2) * ((t % 0.9) < 0.35) * env(n, 0.005, 0.1, 1.0, 0.1)
save("Voice/SND-Alert-Short.wav", lp(alert, 4000))
save("World/SND-CHECKPOINT.wav", (tone(int(0.35 * SR), 660) + tone(int(0.35 * SR), 990) * 0.5) * env(int(0.35 * SR), 0.01, 0.1, 0.5, 0.2) * 0.4)
n = int(0.6 * SR); save("World/SND-PROP-Impact.wav", lp(noise(n), 250) * env(n, 0.001, 0.08, 0.2, 0.4) + tone(n, 140) * env(n, 0.001, 0.1, 0.0, 0.2) * 0.5)
n = int(0.3 * SR); save("World/SND-PICKUP.wav", bp(noise(n), 600, 3000) * env(n, 0.001, 0.05, 0.2, 0.15))

# ---------- Megafonía: toma seca SAPI → receta 72.3 ----------
dry = OUT + "/Voice/SND-PA-Detection_dry.wav"
if os.path.exists(dry):
    sr0, v = wavfile.read(dry)
    v = v.astype(np.float64); v = v if v.ndim == 1 else v.mean(axis=1)
    v /= (np.max(np.abs(v)) or 1)
    if sr0 != SR: v = signal.resample(v, int(len(v) * SR / sr0))
    v = hp(v, 300, 2); v = lp(v, 5000, 4)                          # pasaaltos ~300 Hz, corte agudos ~5 kHz
    v = np.tanh(v * 2.2) / np.tanh(2.2)                            # compresión/saturación baja
    v = reverb(v, decay=2.0, mix=0.35, predelay=0.04)              # reverb de corredor, cola ~2 s
    tail = np.zeros(int(1.5 * SR)); v = np.concatenate([v, tail])
    save("Voice/SND-PA-Detection.wav", v)
    manifest[-1]["origin"] = "voz sintética local (Windows SAPI 'Microsoft Sabina Desktop', guion original 5.2) + procesado 72.3 (gen_audio.py)"
    manifest[-1]["subtitle"] = "Atención. Se ha detectado presencia humana no registrada en las instalaciones. Unidades de contención: procedan con cautela. Recuperación prioritaria."
else:
    manifest.append({"id": "SND-PA-Detection", "file": "Voice/SND-PA-Detection.wav", "origin": "PENDIENTE: toma seca SAPI no encontrada", "license": "n/a"})

json.dump({"generated": manifest, "note": "Banco placeholder ORIGINAL identificado como generado (50.2/72.4). Sustituible por grabaciones/diseño sonoro final sin cambiar IDs."}, open(ROOT + "/docs/produccion/AUDIO_MANIFEST.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(manifest), "archivos")
