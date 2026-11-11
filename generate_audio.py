# -*- coding: utf-8 -*-
"""Генерация атмосферного аудио для лонгрида (OGG Vorbis)."""

import os
import wave
import struct
import math
import numpy as np
import subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(BASE, "assets", "audio")
os.makedirs(OUTDIR, exist_ok=True)
SR = 44100
DUR = 48.0
N = int(SR * DUR)
t = np.arange(N) / SR
rng = np.random.default_rng(7)

# --- низкий дрон ------------------------------------------------------
drone = (0.12 * np.sin(2 * np.pi * 55.0 * t)
         + 0.05 * np.sin(2 * np.pi * 55.4 * t + 0.6)
         + 0.025 * np.sin(2 * np.pi * 110.0 * t + 1.2))
drone *= 0.75 + 0.25 * np.sin(2 * np.pi * 0.035 * t)

# --- медленный аккорд -------------------------------------------------
chord = np.zeros_like(t)
for f, a, ph in [(110.0, 0.055, 0.0),
                 (164.81, 0.045, 0.7),
                 (220.0, 0.035, 1.1),
                 (261.63, 0.022, 2.0),
                 (329.63, 0.014, 0.3)]:
    lfo = 0.55 + 0.45 * np.sin(2 * np.pi * 0.018 * t + ph)
    chord += a * lfo * np.sin(2 * np.pi * f * t + ph)
chord *= 1.0 + 0.15 * np.sin(2 * np.pi * 0.011 * t)

# --- шумовой «воздух» -------------------------------------------------
noise = rng.normal(0, 1, N)
# простой однополюсный низкочастотный фильтр
alpha = 0.015
lp = np.empty_like(noise)
acc = 0.0
for i in range(N):
    acc += alpha * (noise[i] - acc)
    lp[i] = acc
air = lp * 1.8
air *= 0.6 + 0.4 * np.sin(2 * np.pi * 0.02 * t + 1.5)

# --- редкие «цифровые» импульсы --------------------------------------
blips = np.zeros_like(t)
for start in [4.5, 10.2, 16.8, 23.4, 31.0, 38.5, 44.0]:
    idx = int(start * SR)
    length = int(0.45 * SR)
    tt = np.arange(length) / SR
    env = np.exp(-tt * 9.0)
    freq = 1180 + 240 * math.sin(start)
    sig = 0.05 * env * np.sin(2 * np.pi * freq * tt)
    blips[idx:idx + length] += sig

# --- мягкая пульсация -------------------------------------------------
pulse = 0.018 * np.sin(2 * np.pi * 0.5 * t) * np.exp(-((np.mod(t, 2.0) - 0.15) ** 2) / 0.01)

mix = drone + chord + air + blips + pulse
# лёгкое стерео-расширение через задержку
delay = int(0.013 * SR)
right = np.copy(mix)
right[delay:] = 0.82 * right[delay:] + 0.18 * mix[:-delay]
left = mix
stereo = np.column_stack([left, right])

# фейды
fade = int(2.5 * SR)
stereo[:fade] *= np.linspace(0, 1, fade)[:, None]
stereo[-fade:] *= np.linspace(1, 0, fade)[:, None]
# нормализация
peak = np.max(np.abs(stereo))
stereo = stereo / peak * 0.82
pcm = (stereo * 32767).astype(np.int16)

wav_path = os.path.join(OUTDIR, "ambient.wav")
with wave.open(wav_path, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())

ogg_path = os.path.join(OUTDIR, "ambient.ogg")
cmd = (f'gst-launch-1.0 -e filesrc location="{wav_path}" ! wavparse '
       f'! audioconvert ! vorbisenc quality=0.55 ! oggmux '
       f'! filesink location="{ogg_path}"')
subprocess.run(cmd, shell=True, check=True)

mp3_path = os.path.join(OUTDIR, "ambient.mp3")
cmd = (f'gst-launch-1.0 -e filesrc location="{wav_path}" ! wavparse '
       f'! audioconvert ! lamemp3enc target=bitrate bitrate=128 cbr=true '
       f'! filesink location="{mp3_path}"')
subprocess.run(cmd, shell=True, check=True)

os.remove(wav_path)
print("saved", ogg_path, os.path.getsize(ogg_path) // 1024, "KB")
print("saved", mp3_path, os.path.getsize(mp3_path) // 1024, "KB")
