"""Bucle sin costura para la musica de fondo de Sueno Lucido.

Uso:
    python tools/taller_final/audio_loop.py <cancion.(wav|mp3|m4a|...)> [--salida RUTA] [--fundido 3.0]

1. Convierte la cancion a WAV estereo de 48 kHz con ffmpeg.
2. Busca el mejor punto de cierre: entre el 55 % y el 97 % de la cancion, el instante cuya envolvente y
   espectro mas se parecen a los primeros segundos (correlacion de la envolvente RMS), ajustado al cruce por
   cero mas cercano para no producir clics.
3. Hace un fundido cruzado de igual potencia de N segundos entre la cola y el principio, de modo que el ultimo
   sample empalma con el primero.
4. Normaliza el pico a -6 dBFS (la mezcla del juego deja aire a los efectos).

La salida va por defecto a TallerFinal/Assets/_Project/Audio/Music/Eccochamber_loop.wav. Esa carpeta esta en
.gitignore: la cancion es comercial y no se sube al repositorio publico.
"""
import argparse
import os
import subprocess
import sys
import tempfile

import numpy as np
from scipy.io import wavfile

RATE = 48000
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DEFAULT_OUT = os.path.join(ROOT, "TallerFinal", "Assets", "_Project", "Audio", "Music", "Eccochamber_loop.wav")


def decode(path):
    tmp = os.path.join(tempfile.mkdtemp(), "decoded.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", path, "-ac", "2", "-ar", str(RATE), "-sample_fmt", "s16", tmp], check=True)
    rate, data = wavfile.read(tmp)
    return data.astype(np.float32) / 32768.0


def envelope(x, win):
    mono = x.mean(axis=1)
    n = len(mono) // win
    return np.sqrt((mono[: n * win].reshape(n, win) ** 2).mean(axis=1) + 1e-12)


def best_loop_end(x, head_seconds=6.0):
    win = RATE // 50                      # 20 ms
    env = envelope(x, win)
    head = env[: int(head_seconds * 50)]
    head = (head - head.mean()) / (head.std() + 1e-9)
    lo, hi = int(len(env) * 0.55), int(len(env) * 0.97) - len(head)
    best, best_i = -2.0, hi
    for i in range(lo, hi):
        seg = env[i: i + len(head)]
        seg = (seg - seg.mean()) / (seg.std() + 1e-9)
        c = float((seg * head).mean())
        if c > best:
            best, best_i = c, i
    return best_i * win, best


def nearest_zero_crossing(x, at, radius=2400):
    mono = x.mean(axis=1)
    a, b = max(1, at - radius), min(len(mono) - 1, at + radius)
    idx = np.where(np.sign(mono[a - 1: b - 1]) != np.sign(mono[a:b]))[0]
    if len(idx) == 0:
        return at
    return int(a + idx[np.argmin(np.abs(idx + a - at))])


def make_loop(x, end, fade_seconds):
    fade = int(fade_seconds * RATE)
    end = max(end, 2 * fade)
    body = x[:end].copy()
    t = np.linspace(0.0, np.pi / 2.0, fade)[:, None]
    tail = body[-fade:]
    head = x[:fade]
    body[-fade:] = tail * np.cos(t) + head * np.sin(t)    # igual potencia: no hay bache de volumen
    return body[fade:]                                    # el principio ya vive dentro del fundido


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada")
    ap.add_argument("--salida", default=DEFAULT_OUT)
    ap.add_argument("--fundido", type=float, default=3.0)
    args = ap.parse_args()
    x = decode(args.entrada)
    end, score = best_loop_end(x)
    end = nearest_zero_crossing(x, end)
    loop = make_loop(x, end, args.fundido)
    peak = float(np.abs(loop).max())
    loop *= (10 ** (-6 / 20)) / max(peak, 1e-6)
    os.makedirs(os.path.dirname(args.salida), exist_ok=True)
    wavfile.write(args.salida, RATE, (np.clip(loop, -1, 1) * 32767).astype(np.int16))
    # comprobacion del empalme: diferencia entre el ultimo y el primer sample
    jump = float(np.abs(loop[-1] - loop[0]).max())
    print(f"bucle de {len(loop) / RATE:.1f} s (cierre en {end / RATE:.1f} s, parecido {score:.2f}), salto en el empalme {jump:.4f}")
    print("escrito", args.salida)


if __name__ == "__main__":
    sys.exit(main())
