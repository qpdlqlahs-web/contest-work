#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EP09 효과음: numpy 합성 + 소인 목소리(edge-tts -> 피치 업). 외부 음원 다운로드 없음.
  python assets/sfx/make_sfx_ep09.py
생성: whistle(삑) chiik(치익) tadak(타닥) beep3(삑삑삑) roller(드르륵) roller_spin(드르륵+뱅글) thud(툭)
      hair(후룩) bounce(통통) creak(끼익) flutter(파닥) purr(골골) fusu(푸스스) baa(메에)
      gungcha(끙차, 여사) euat(으앗, 콩알이)
"""
import asyncio
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from scipy import signal
from scipy.io import wavfile

SR = 48000
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
rng = np.random.default_rng(99)


def save(name, x, peak=0.8):
    x = np.asarray(x, dtype=np.float64)
    x = x / max(1e-9, np.abs(x).max()) * peak
    wavfile.write(str(HERE / name), SR, (x * 32767).astype("<i2"))


def T(sec):
    return np.arange(int(SR * sec)) / SR


def env_ad(t, a=0.005, d=10.0):
    return np.minimum(1, t / a) * np.exp(-t * d)


def hp(x, fc):
    b, a = signal.butter(2, fc / (SR / 2), "high")
    return signal.lfilter(b, a, x)


def lp(x, fc):
    b, a = signal.butter(2, fc / (SR / 2), "low")
    return signal.lfilter(b, a, x)


def bp(x, lo, hi):
    b, a = signal.butter(2, [lo / (SR / 2), hi / (SR / 2)], "band")
    return signal.lfilter(b, a, x)


def place(total, parts):
    out = np.zeros(int(SR * total))
    for at, x in parts:
        i = int(SR * at)
        out[i:i + len(x)] += x[:len(out) - i]
    return out


def whistle():
    t = T(0.30)
    f = 3000 + 250 * np.sin(2 * np.pi * 38 * t) - 500 * t
    ph = 2 * np.pi * np.cumsum(f) / SR
    breath = bp(rng.uniform(-1, 1, len(t)), 2500, 4500) * 0.25
    return (np.sin(ph) + breath) * np.minimum(1, t / 0.008) * np.minimum(1, (0.30 - t) / 0.05)


def chiik():
    t = T(0.20)
    n = hp(rng.uniform(-1, 1, len(t)), 3500)
    return n * np.minimum(1, t / 0.015) * np.exp(-t * 11)


def tadak():
    parts = []
    for at in (0.0, 0.07):
        t = T(0.05)
        click = hp(rng.uniform(-1, 1, len(t)), 1500) * np.exp(-t * 140) + np.sin(2 * np.pi * 900 * t) * np.exp(-t * 120) * 0.5
        parts.append((at, click))
    return place(0.14, parts)


def beep3():
    parts = []
    for k in range(3):
        t = T(0.07)
        parts.append((k * 0.12, np.sin(2 * np.pi * 1300 * t) * np.minimum(1, t / 0.004) * np.minimum(1, (0.07 - t) / 0.01)))
    return place(0.34, parts)


def roller(sec=0.38):
    t = T(sec)
    rate = 46 - 12 * t / sec
    ph = np.cumsum(rate) / SR
    tick = (np.mod(ph, 1.0) < 0.12).astype(float)
    n = bp(rng.uniform(-1, 1, len(t)), 500, 3500) * tick
    low = np.sin(2 * np.pi * 130 * t) * 0.2
    return (n + low) * np.minimum(1, t / 0.02) * np.minimum(1, (sec - t) / 0.06)


def roller_spin():
    a = roller(0.28)
    t = T(0.35)
    f = 400 + 900 * np.sin(np.pi * t / 0.35)
    sw = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / 0.35) ** 2 * 0.6
    return place(0.62, [(0.0, a), (0.27, sw)])


def thud():
    t = T(0.16)
    f = 140 * np.exp(-t * 14) + 50
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * env_ad(t, 0.002, 22)
            + lp(rng.uniform(-1, 1, len(t)), 900) * np.exp(-t * 80) * 0.5)


def hair():
    parts = []
    for at in (0.0, 0.16):
        t = T(0.13)
        n = bp(rng.uniform(-1, 1, len(t)), 1200, 5000)
        parts.append((at, n * np.sin(np.pi * t / 0.13) ** 1.5))
    return place(0.3, parts)


def bounce():
    parts = []
    for k, at in enumerate((0.0, 0.14)):
        t = T(0.10)
        f = (220 + 160 * k) * (1 + 0.8 * np.exp(-t * 30))
        parts.append((at, np.sin(2 * np.pi * np.cumsum(f) / SR) * env_ad(t, 0.003, 26)))
    return place(0.26, parts)


def creak():
    t = T(0.45)
    f = 500 + 350 * np.sin(2 * np.pi * 5 * t) + 400 * t
    saw = signal.sawtooth(2 * np.pi * np.cumsum(f) / SR)
    return lp(saw, 2500) * np.minimum(1, t / 0.03) * np.minimum(1, (0.45 - t) / 0.08)


def flutter():
    parts = []
    for k in range(4):
        t = T(0.035)
        parts.append((k * 0.03, bp(rng.uniform(-1, 1, len(t)), 800, 3000) * np.sin(np.pi * t / 0.035) * (1 - 0.18 * k)))
    return place(0.16, parts)


def purr():
    t = T(0.8)
    saw = signal.sawtooth(2 * np.pi * 70 * t)
    am = 0.55 + 0.45 * np.sin(2 * np.pi * 24 * t)
    return lp(saw + 0.3 * rng.uniform(-1, 1, len(t)), 500) * am * np.minimum(1, t / 0.1) * np.minimum(1, (0.8 - t) / 0.2)


def fusu():
    t = T(0.35)
    n = bp(rng.uniform(-1, 1, len(t)), 1500, 6000)
    return n * np.minimum(1, t / 0.03) * np.exp(-t * 7)


def baa():
    t = T(0.32)
    f = 330 * (1 + 0.04 * np.sin(2 * np.pi * 32 * t)) * (1 - 0.15 * t)
    saw = signal.sawtooth(2 * np.pi * np.cumsum(f) / SR)
    x = bp(saw, 600, 1800) + 0.4 * bp(saw, 1800, 3000)
    return x * np.minimum(1, t / 0.03) * np.minimum(1, (0.32 - t) / 0.06)


# ---- 소인 목소리: 무료 TTS -> 피치/속도 업 -> 0.3초 이하
def find_ffmpeg():
    import json
    cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    for c in [cfg.get("ffmpeg"), "ffmpeg"]:
        if c:
            try:
                subprocess.run([c, "-version"], capture_output=True, check=True)
                return c
            except Exception:
                pass
    raise SystemExit("ffmpeg 없음")


async def _tts(text, voice, path):
    import edge_tts
    await edge_tts.Communicate(text, voice, rate="+20%").save(path)


def voice(text, voice_name, name, up=1.9, seconds=0.3):
    ff = find_ffmpeg()
    with tempfile.TemporaryDirectory() as td:
        mp3, wav = str(Path(td) / "v.mp3"), str(Path(td) / "v.wav")
        asyncio.run(_tts(text, voice_name, mp3))
        subprocess.run([ff, "-y", "-loglevel", "error", "-i", mp3, "-ac", "1", "-ar", str(SR), wav], check=True)
        sr, x = wavfile.read(wav)
    x = x.astype(np.float64) / 32768
    idx = np.where(np.abs(x) > 0.03)[0]
    x = x[idx[0]:idx[-1] + 1]                       # 앞뒤 무음 제거
    from fractions import Fraction
    fr = Fraction(up).limit_denominator(20)
    x = signal.resample_poly(x, fr.denominator, fr.numerator)   # 재생 속도 up배 = 피치·속도 up (손가락만 한 사람)
    x = hp(x, 400)
    x = x[:int(SR * seconds)]
    x = x * np.minimum(1, np.arange(len(x)) / (SR * 0.004)) * np.minimum(1, (len(x) - np.arange(len(x))) / (SR * 0.05))
    save(name, x, 0.85)
    print(f"  {name}: {len(x) / SR:.2f}s")


if __name__ == "__main__":
    for nm, fn, pk in [("whistle.wav", whistle, 0.7), ("chiik.wav", chiik, 0.5), ("tadak.wav", tadak, 0.6),
                       ("beep3.wav", beep3, 0.5), ("roller.wav", roller, 0.7), ("roller_spin.wav", roller_spin, 0.7),
                       ("thud.wav", thud, 0.85), ("hair.wav", hair, 0.5), ("bounce.wav", bounce, 0.7),
                       ("creak.wav", creak, 0.5), ("flutter.wav", flutter, 0.5), ("purr.wav", purr, 0.6),
                       ("fusu.wav", fusu, 0.5), ("baa.wav", baa, 0.55)]:
        save(nm, fn(), pk)
    print("합성 효과음 생성")
    try:
        voice("끙차", "ko-KR-SunHiNeural", "gungcha.wav")
        voice("으앗", "ko-KR-InJoonNeural", "euat.wav")
    except Exception as e:
        print(f"[TTS 실패] {type(e).__name__}: {e}")
        sys.exit(1)
