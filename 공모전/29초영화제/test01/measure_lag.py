# -*- coding: utf-8 -*-
"""기둥 반복 주기 측정: 프레임 간 평균 절대차 MAD(lag). 기준: MAD(24) >= 0.95 * MAD(12).
사용: T1V=3|31 python measure_lag.py
 (a) 실제 렌더 프레임(그레인 전 PNG) C07 sig f48~95, 기둥 영역
 (b) 기둥 레이어 단독(고정 배경 0.2, v=0.8, mix=1), t=0~143, 플레이트 물결 포함"""
import os, sys, json
import numpy as np
from PIL import Image
os.environ.setdefault('T1V', '31')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render as R

tag = os.environ['T1V']
R.init()
m = R.G['meta']; sx = int(round(m['SUN_X'])); wt = int(m['WATER_TOP'])
ys, xs = slice(wt + 15, 1900), slice(sx - 130, sx + 130)
res = {}
# (a)
fr = os.path.join(R.ROOT, {'3': 'frames_v3', '31': 'frames_v31'}[tag], 'C07_sig')
F = {f: np.asarray(Image.open(os.path.join(fr, f'{f:03d}.png'))).astype(np.float32)[ys, xs] / 255. for f in range(48, 96)}
def mad(L, t0s): return float(np.mean([np.abs(F[t + L] - F[t]).mean() for t in t0s]))
t0 = range(48, 72)
res['a_frames'] = {L: mad(L, t0) for L in (12, 24)}
# (b)
if 'gran' not in R.G:
    R.G['gran'] = np.load(os.path.join(R.B, 'gran_v31.npy' if R.V31 else 'gran.npy'))
    R.G['col_target'] = np.load(os.path.join(R.B, 'col_target.npy'))
    if R.V31:
        Fz = np.load(os.path.join(R.B, 'fields_v31.npz'))
        for k in Fz.files: R.G[k] = Fz[k]
seq = {}
for t in range(0, 144):
    bg = R.plate(1.0, float(t), 0.0)
    out = R.signal_column(bg, 0.8, float(t), 1.0)
    seq[t] = out[ys, xs]
def mad2(L): return float(np.mean([np.abs(seq[t + L] - seq[t]).mean() for t in range(0, 96)]))
res['b_layer'] = {L: mad2(L) for L in (12, 24, 37, 48)}
for k in ('a_frames', 'b_layer'):
    d = res[k]; d['ratio_24_12'] = d[24] / d[12]; d['pass'] = d['ratio_24_12'] >= 0.95
print(tag, json.dumps(res, indent=1))
json.dump(res, open(os.path.join(R.B, f'lag_{tag}.json'), 'w'), indent=1)
