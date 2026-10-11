#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""「새벽3시CCTV」 효과음 직접 합성 (numpy, 외부 다운로드 없음 -> 저작권 걱정 없음).
  python assets/sfx/make_sfx.py  ->  pop.wav('뿅') / chijik.wav(무전 '치직') / bang.wav(결재 도장 '쾅')
"""
from pathlib import Path
import wave

import numpy as np

SR = 48000
HERE = Path(__file__).resolve().parent
rng = np.random.default_rng(9)


def save(name: str, x: np.ndarray, peak: float = 0.8) -> None:
    x = x / max(1e-9, np.abs(x).max()) * peak
    pcm = (x * 32767).astype("<i2")
    with wave.open(str(HERE / name), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def pop() -> np.ndarray:
    """뿅: 낮은 음에서 높은 음으로 튀어 오르는 코믹 버블 (0.22초)."""
    n = int(SR * 0.22)
    t = np.arange(n) / SR
    f = 260 + 900 * (1 - np.exp(-t * 22))
    ph = 2 * np.pi * np.cumsum(f) / SR
    env = np.minimum(1, t / 0.006) * np.exp(-t * 14)
    return (np.sin(ph) + 0.3 * np.sin(2 * ph)) * env


def chijik() -> np.ndarray:
    """치직: 무전기 스퀠치 잡음. 3번 끊기는 대역 잡음 (0.14초)."""
    n = int(SR * 0.14)
    t = np.arange(n) / SR
    noise = rng.uniform(-1, 1, n)
    hp = noise - np.convolve(noise, np.ones(8) / 8, mode="same")  # 고음만 남김
    gate = (np.sin(2 * np.pi * 38 * t) > -0.2).astype(float)
    env = np.minimum(1, t / 0.004) * np.minimum(1, (0.14 - t) / 0.02)
    return hp * gate * env


def bang() -> np.ndarray:
    """쾅: 도장이 책상에 닿는 둔탁한 타격 (0.45초)."""
    n = int(SR * 0.45)
    t = np.arange(n) / SR
    f = 55 + 140 * np.exp(-t * 30)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)
    click = rng.uniform(-1, 1, n) * np.exp(-t * 90) * 0.7
    return body + click


if __name__ == "__main__":
    save("pop.wav", pop())
    save("chijik.wav", chijik(), 0.6)
    save("bang.wav", bang(), 0.9)
    print("pop.wav, chijik.wav, bang.wav 생성")
