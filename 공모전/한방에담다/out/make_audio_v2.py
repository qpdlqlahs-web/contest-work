# -*- coding: utf-8 -*-
"""음악 구간 추출 + 합성 효과음 믹스 + -14 LUFS 정규화. 효과음은 전부 numpy 합성(외부 소스 없음)."""
import numpy as np, soundfile as sf, subprocess, json, sys
from pathlib import Path
from timeline_v2 import *

SR = 48000
OUT = ROOT / "out"
WORK = OUT / "_work"
WORK.mkdir(exist_ok=True)
rng = np.random.default_rng(7)


def env(n, a=0.002, d=0.1, curve=4.0):
    t = np.arange(n) / SR
    e = np.minimum(t / a, 1.0) * np.exp(-t * curve / d)
    return e


def lp(x, fc):
    # 1-pole low-pass
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.zeros_like(x)
    s = 0.0
    for i, v in enumerate(x):
        s = (1 - a) * v + a * s
        y[i] = s
    return y


def sfx_tak():  # 서랍 '탁'
    n = int(0.22 * SR); t = np.arange(n) / SR
    click = rng.standard_normal(n) * np.exp(-t * 260)
    click = click - lp(click, 600)                       # 고역 클릭
    body = np.sin(2 * np.pi * (180 * np.exp(-t * 18) + 90) * t) * np.exp(-t * 40)
    return 0.55 * click + 0.7 * body


def sfx_pop():  # 빼꼼 팝
    n = int(0.16 * SR); t = np.arange(n) / SR
    f = 380 + 760 * (1 - np.exp(-t * 55))
    ph = 2 * np.pi * np.cumsum(f) / SR
    return 0.8 * np.sin(ph) * np.minimum(t / 0.004, 1) * np.exp(-t * 28)


def sfx_thud():  # 쿵
    n = int(0.55 * SR); t = np.arange(n) / SR
    f = 52 + 70 * np.exp(-t * 14)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t * 7.5)
    nz = lp(rng.standard_normal(n), 900) * np.exp(-t * 38)
    return 1.0 * body + 0.8 * nz


def sfx_splash():  # 퐁 + 촤악
    n = int(1.1 * SR); t = np.arange(n) / SR
    f = 260 + 900 * (1 - np.exp(-t * 38))
    ph = 2 * np.pi * np.cumsum(f) / SR
    plop = np.sin(ph) * np.minimum(t / 0.003, 1) * np.exp(-t * 22)
    nz = rng.standard_normal(n)
    nz = nz - lp(nz, 1500)                                # 고역 위주 물소리
    sh = nz * np.minimum(t / 0.01, 1) * np.exp(-t * 6.0)
    drips = np.zeros(n)
    for dt, g in [(0.42, .5), (0.55, .4), (0.68, .45), (0.8, .3)]:
        i = int(dt * SR); m = int(0.08 * SR); tt = np.arange(m) / SR
        drips[i:i + m] += g * np.sin(2 * np.pi * (500 + 900 * (1 - np.exp(-tt * 60))) * tt) * np.exp(-tt * 45)
    return 0.8 * plop + 0.5 * sh + 0.5 * drips


GEN = {"tak": sfx_tak, "pop": sfx_pop, "thud": sfx_thud, "splash": sfx_splash}
GAIN = {"tak": 0.35, "pop": 0.30, "thud": 0.55, "splash": 0.45}   # 음악 대비 (믹스 전, 음악 피크 ~0.9)

# 1) 곡 구간
y, sr = sf.read(ROOT / "audio" / "yakbang_t2.wav")
assert sr == SR
a = int(round(SONG_START * SR)); b = a + int(round(DUR * SR))
seg = y[a:b].copy()
# 시작 클릭 방지 20ms 페이드인, 끝 0.8s 페이드아웃(코사인)
fi = int(0.02 * SR); seg[:fi] *= np.linspace(0, 1, fi)[:, None]
fo = int(0.9 * SR); seg[-fo:] *= (0.5 + 0.5 * np.cos(np.linspace(0, np.pi, fo)))[:, None]

# 2) 효과음 얹기
mix = seg.copy()
for name, t0, g in SFX:
    s = GEN[name]()
    s = s / (np.abs(s).max() + 1e-9) * GAIN[name] * g
    i = int(round(t0 * SR))
    j = min(i + len(s), len(mix))
    mix[i:j] += s[: j - i, None]
sf.write(WORK / "mix_pre_v2.wav", mix, SR, subtype="FLOAT")

# 3) loudnorm 2-pass (-14 LUFS, TP -1.5)
def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    return p.stderr

f = lambda p: str(p)
err = run(["ffmpeg", "-hide_banner", "-i", f(WORK / "mix_pre_v2.wav"), "-af",
           "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"])
js = json.loads(err[err.rfind("{"):err.rfind("}") + 1])
print(js)
af = ("loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=%s:measured_TP=%s:measured_LRA=%s:measured_thresh=%s:offset=%s:linear=true"
      % (js["input_i"], js["input_tp"], js["input_lra"], js["input_thresh"], js["target_offset"]))
run(["ffmpeg", "-y", "-hide_banner", "-i", f(WORK / "mix_pre_v2.wav"), "-af", af + ",aresample=48000",
     "-c:a", "pcm_s24le", f(WORK / "mix_final_v2.wav")])
err = run(["ffmpeg", "-hide_banner", "-i", f(WORK / "mix_final_v2.wav"), "-af",
           "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"])
print(err[err.rfind("{"):err.rfind("}") + 1])
