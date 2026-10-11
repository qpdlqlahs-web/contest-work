#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""「새벽3시CCTV」 배경음악: 살금살금 도둑 느낌의 피치카토(직접 합성, 저작권 걱정 없음).
  python assets/sfx/make_bgm.py  ->  assets/sfx/bgm_sneaky.wav (약 48초, 끝과 처음이 이어짐)
"""
from pathlib import Path
import wave

import numpy as np

SR = 48000
BPM = 104
BEAT = 60 / BPM
HERE = Path(__file__).resolve().parent


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def pluck(freq, dur, vol=0.5, bright=0.55):
    """카르플루스-스트롱 현 뜯는 소리 (피치카토)."""
    n = int(SR * dur)
    period = max(2, int(SR / freq))
    buf = np.random.uniform(-1, 1, period)
    out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % period]
        buf[i % period] = bright * buf[i % period] + (1 - bright) * buf[(i + 1) % period]
    env = np.exp(-np.linspace(0, 6, n))
    return out * env * vol


def tone(freq, dur, vol=0.18):
    """부드러운 클라리넷 비슷한 음 (홀수 배음)."""
    t = np.arange(int(SR * dur)) / SR
    w = sum(np.sin(2 * np.pi * freq * k * t) / k for k in (1, 3, 5))
    att = np.minimum(1, t / 0.04)
    rel = np.minimum(1, (dur - t) / 0.08)
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.5 * t)
    return w * att * rel * vol * vib


def place(track, clip, at):
    i = int(at * SR)
    j = min(len(track), i + len(clip))
    track[i:j] += clip[: j - i]


def main():
    bars = 20                       # 4/4, 104bpm → 약 46초
    total = bars * 4 * BEAT
    track = np.zeros(int(SR * (total + 1)))
    # D 단조 살금살금 베이스 (스타카토 2박 + 쉼표)
    bass_pat = [38, None, 45, None, 41, None, 45, 44]       # D A F A G#
    alt_pat = [36, None, 43, None, 40, None, 43, 42]
    for b in range(bars):
        pat = bass_pat if (b // 2) % 2 == 0 else alt_pat
        for k, n in enumerate(pat):
            if n is not None:
                place(track, pluck(midi(n), 0.4, 0.55, 0.5), b * 4 * BEAT + k * BEAT / 2)
    # 손가락 튕기기(스냅) 2·4박
    for b in range(bars):
        for beat in (1, 3):
            click = np.random.uniform(-1, 1, int(SR * 0.03)) * np.exp(-np.linspace(0, 12, int(SR * 0.03))) * 0.25
            place(track, click, b * 4 * BEAT + beat * BEAT)
    # 멜로디: 살금살금 → 들킨 듯 반음 상승 (4마디 단위)
    mel = [(62, 0.5), (None, 0.5), (65, 0.5), (66, 0.5), (67, 1.0), (None, 1.0),
           (69, 0.5), (68, 0.5), (67, 0.5), (65, 0.5), (62, 1.5), (None, 0.5),
           (62, 0.5), (None, 0.5), (65, 0.5), (66, 0.5), (67, 1.0), (70, 1.0),
           (69, 0.75), (67, 0.25), (65, 0.5), (64, 0.5), (62, 2.0)]
    for start_bar in (4, 12):
        t = start_bar * 4 * BEAT
        for n, d in mel:
            if n is not None:
                place(track, tone(midi(n), d * BEAT * 0.85), t)
                place(track, pluck(midi(n + 12), 0.25, 0.12, 0.6), t)
            t += d * BEAT
    track = track[: int(SR * total)]
    # 앞뒤 0.3초 크로스페이드로 반복 재생 이음새 없애기
    f = int(SR * 0.3)
    track[:f] = track[:f] * np.linspace(0, 1, f) + track[-f:] * np.linspace(1, 0, f)
    track = track[:-f]
    track = track / np.max(np.abs(track)) * 0.8
    pcm = (np.stack([track, track], 1) * 32767).astype(np.int16)
    with wave.open(str(HERE / "bgm_sneaky.wav"), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print(HERE / "bgm_sneaky.wav", round(len(track) / SR, 1), "s")


if __name__ == "__main__":
    main()
