# -*- coding: utf-8 -*-
"""시험 1 v3.1 소재 (build_v3에 *_v31로 추가, v3 소재는 그대로 둔다)
- sun_corona_v31.npy: Sblank 코로나를 바깥 방향으로 1.4배 늘림(밑동은 원판 가장자리에 고정) + 채색
- gran_v31.npy: 쌀알무늬 셀 1.3배
- fields_v31.npz: 비주기 물결용 3층 필드(주기 37/61/97f에 쓰는 cos/sin 짝)"""
import os, json
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, maximum_filter, map_coordinates

ROOT = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(ROOT, '..', 'img')
B = os.path.join(ROOT, 'build_v3'); B1 = os.path.join(ROOT, 'build')
W, H = 1080, 1920
SUN_D = 230; SS = 2; SPR = 800
def luma(a): return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
def hx(h): return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255.

# ---- 코로나 1.4배(바깥 방향)
Sb = np.asarray(Image.open(os.path.join(IMG, 'Sblank_1.png')).convert('RGB')).astype(np.float32) / 255.
cx, cy, r = json.load(open(os.path.join(B1, 'meta.json')))['circles']['Sblank']
k = (2 * r) / (SUN_D * SS)
Ssp = np.clip(np.stack([np.asarray(Image.fromarray(gaussian_filter(Sb[..., c], 1.2), 'F').transform((SPR, SPR), Image.AFFINE,
        (k, 0, cx - k * SPR / 2, 0, k, cy - k * SPR / 2), resample=Image.BICUBIC)) for c in range(3)], -1), 0, 1)
g = np.mgrid[0:SPR, 0:SPR].astype(np.float32); C = SPR / 2 - 0.5; R2 = SUN_D * SS / 2
dx, dy = g[1] - C, g[0] - C
rr = np.hypot(dx, dy) / R2
rs = np.where(rr > 1.0, 1.0 + (rr - 1.0) / 1.4, rr)          # 바깥쪽 길이 1.4배
sc = rs / np.maximum(rr, 1e-6)
Sx = C + dx * sc; Sy = C + dy * sc
Sst = np.stack([map_coordinates(Ssp[..., c], [Sy, Sx], order=1, mode='constant') for c in range(3)], -1)
cor0 = Sst * np.clip((rr - 0.985) / 0.03, 0, 1)[..., None]
Lc0 = luma(cor0)
Lt = gaussian_filter(np.maximum(Lc0, maximum_filter(Lc0, 5) * 0.9), 0.8)   # 굵기도 함께 키움
op = np.clip(Lt * 1.5, 0, 1) ** 0.75
u = np.clip(Lt, 0, 1) ** 0.8
corRGB = (hx('#FE9C00')[None, None] * (1 - u[..., None]) + hx('#FFC24A')[None, None] * u[..., None]) * op[..., None]
corRGB = corRGB * np.clip((1.7 - rr) / 0.3, 0, 1)[..., None]   # 원본 경계 흔적 제거
np.save(os.path.join(B, 'sun_corona_v31.npy'), corRGB.astype(np.float32))

# ---- 쌀알무늬 셀 1.3배
rng = np.random.default_rng(31)
n0 = rng.normal(0, 1, (SPR, SPR + 400)).astype(np.float32)
gran = gaussian_filter(n0, 4.5 * 1.3, mode='wrap') - gaussian_filter(n0, 9.0 * 1.3, mode='wrap')
gran = np.clip(gran / gran.std() * 0.5, -1, 1).astype(np.float32)
np.save(os.path.join(B, 'gran_v31.npy'), gran)

# ---- 비주기 물결 필드 3층 × (cos, sin)
m = json.load(open(os.path.join(B, 'meta.json')))
yw0 = int(m['BRIDGE_Y']) - 12; hh = H - yw0
rng = np.random.default_rng(3761)
def nf(shape, sig):
    a = gaussian_filter(rng.normal(0, 1, shape).astype(np.float32), sig, mode='wrap'); return (a / a.std()).astype(np.float32)
out = {}
for i, sig in enumerate([(2.2, 16), (2.2, 16), (4, 30)]):
    out[f'RA{i}'] = nf((hh, W), sig); out[f'RB{i}'] = nf((hh, W), sig)
for i in range(3):
    out[f'SA{i}'] = nf((hh, W), (1.0, 9)); out[f'SB{i}'] = nf((hh, W), (1.0, 9))
np.savez(os.path.join(B, 'fields_v31.npz'), **out)
Image.fromarray((np.clip(corRGB, 0, 1) * 255).astype(np.uint8)).save(os.path.join(B, 'corona_v31_preview.png'))
print('v31 assets saved')
