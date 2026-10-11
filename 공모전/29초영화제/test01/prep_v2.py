# -*- coding: utf-8 -*-
"""시험 1 2차: P7c 기반 준비. 하늘 확장 없음(1440x2560 -> 1080x1920 단순 축소).
기존 물빛 기둥을 분리(E)해 P7a/P7c 바탕에서 70% 줄이고, 렌더에서 v에 맞춰 되살린다.
결과: test01/build_v2/"""
import os, json
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter, median_filter, zoom

ROOT = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(ROOT, '..', 'img')
B = os.path.join(ROOT, 'build_v2'); os.makedirs(B, exist_ok=True)
B1 = os.path.join(ROOT, 'build')
W, H = 1080, 1920
S = 2560 / 1920.0

def load(n): return np.asarray(Image.open(os.path.join(IMG, n)).convert('RGB')).astype(np.float32) / 255.
def s2l(c): return np.where(c <= 0.04045, c / 12.92, ((np.clip(c, 0, None) + 0.055) / 1.055) ** 2.4)
def l2s(c):
    c = np.clip(c, 0, None); return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(c, 1 / 2.4) - 0.055)
def luma(a): return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
def save(a, n): Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8)).save(os.path.join(B, n))

src = load('P7c_1.png')
# 1.333배 축소: 저역통과 후 LANCZOS
P = np.stack([np.asarray(Image.fromarray(gaussian_filter(src[..., c], 0.5), 'F').resize((W, H), Image.LANCZOS)) for c in range(3)], -1)
P = np.clip(P, 0, 1).astype(np.float32)

# ---------------- 지평선(출력 좌표)
Ls = gaussian_filter(luma(P), 1.0)
ridge = np.full(W, 1000.0)
for x in range(W):
    c = Ls[:, x]
    for y in range(820, 1100):
        if c[y] < 0.88 * c[y - 6] and c[y + 3] < 0.88 * c[y - 6]:
            ridge[x] = y - 0.5; break
ridge = median_filter(ridge, 5, mode='nearest')
yy = np.arange(H)[:, None]
H7 = np.clip((yy - ridge[None, :]) / 1.4 + 0.5, 0, 1).astype(np.float32)

# A5: 지평선 바로 위 행(능선-3px)에서 휘도 최대 열
Lrow = gaussian_filter(np.array([Ls[int(ridge[x]) - 3, x] for x in range(W)]), 5)
a5_x = int(np.argmax(Lrow))

# ---------------- 물 마스크
poly_src = [(0, 1400), (330, 1395), (420, 1366), (1100, 1366), (1160, 1395), (1440, 1405), (1440, 2560), (0, 2560)]
m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).polygon([(x / S, y / S) for x, y in poly_src], fill=255)
WATER = gaussian_filter(np.asarray(m).astype(np.float32) / 255., 3)
WATER_TOP = 1366 / S
BRIDGE_Y = 1370 / S

# ---------------- 기존 물빛 기둥 E 분리 (표시 공간: 눈에 보이는 밝기 기준 70% 감소)
small = P[::4, ::4]
bg_s = np.stack([median_filter(small[..., c], size=(1, 121), mode='nearest') for c in range(3)], -1)
bg = np.stack([zoom(bg_s[..., c], 4, order=1)[:H, :W] for c in range(3)], -1)
bg = gaussian_filter(bg, (6, 6, 0))
E = np.clip(P - bg, 0, None) * WATER[..., None]
Ey = luma(E)
rows = np.arange(int(WATER_TOP) + 10, H)
cxs = np.array([(Ey[r] * np.arange(W)).sum() / max(Ey[r].sum(), 1e-6) for r in rows])
col_x = float(np.median(cxs[:300]))
wid = 30 + 0.45 * np.clip(yy - WATER_TOP, 0, None)
cm = np.exp(-((np.arange(W)[None, :] - col_x) / wid) ** 2)
E = gaussian_filter(E * cm[..., None], (0.6, 0.6, 0))
base_lin = s2l(np.clip(P - 0.70 * E, 0, 1))      # 기둥 70% 감소 바탕
# 감독 결정: A5 열이 가장자리 25% 안쪽이면 물빛 기둥 x 우선
edge = (a5_x < 0.25 * W) or (a5_x > 0.75 * W)
SUN_X = col_x if edge else float(a5_x)
RIDGE_Y = float(ridge[int(round(SUN_X))])
print('A5 col', a5_x, 'edge', edge, 'column x', col_x, 'SUN_X', SUN_X, 'ridge', RIDGE_Y)

# ---------------- 불빛 마스크
L7 = luma(P); Lb = gaussian_filter(L7, 5)
lights = np.clip((L7 - Lb - 0.10) / 0.15, 0, 1) * (L7 > 0.5) * H7 * (1 - WATER)
lights = np.clip(gaussian_filter(lights.astype(np.float32), 1.0) * 1.6, 0, 1)

# ---------------- P7a: -1.3EV, 차갑게, 지평선 글로우 70% 감소 (기둥 감소 바탕에서)
yy2, xx2 = np.mgrid[0:H, 0:W].astype(np.float32)
# 이 플레이트는 지평선 왼쪽이 가장 밝다 → 글로우 맵 중심은 A5 열(실제 글로우 위치)
gx = float(a5_x)
dy = yy2 - RIDGE_Y
G = np.exp(-((xx2 - gx) / 520) ** 2 - (np.where(dy < 0, dy / 560, dy / 300)) ** 2)
G = np.maximum(G, 0.55 * np.exp(-(np.where(dy < 0, dy / 300, dy / 160)) ** 2))
warm = np.clip((base_lin[..., 0] - base_lin[..., 2]) / (base_lin[..., 0] + 1e-4), 0, 1)
gfrac = np.clip(G * (0.55 + 0.45 * warm), 0, 0.92)
P7a_lin = base_lin * (2 ** -1.3) * (1 - 0.70 * gfrac)[..., None]
P7a_lin = P7a_lin * np.array([0.80, 0.92, 1.12])
Yl = luma(P7a_lin)[..., None]
P7a_lin = Yl + (P7a_lin - Yl) * 0.82
P7a_lin = P7a_lin * (1 - lights[..., None]) + base_lin * 1.05 * lights[..., None]
P7a = l2s(P7a_lin); P7b = l2s(base_lin)   # P7b 자리 = 기둥 70% 줄인 P7c

for n, a in [('P7a', P7a), ('P7b', P7b)]:
    np.save(os.path.join(B, n + '.npy'), np.clip(a, 0, 1).astype(np.float32)); save(a, n + '.png')
save(P, 'P7c_scaled.png')
np.save(os.path.join(B, 'colE.npy'), E.astype(np.float32))
save(E * 1.5, 'colE_x1.5.png')
np.save(os.path.join(B, 'H7.npy'), H7); save(np.repeat(H7[..., None], 3, 2), 'H7.png')
np.save(os.path.join(B, 'water.npy'), WATER); save(np.repeat(WATER[..., None], 3, 2), 'water.png')
np.save(os.path.join(B, 'lights.npy'), lights.astype(np.float32))
np.save(os.path.join(B, 'ridge_out.npy'), ridge.astype(np.float32))
# 캐릭터 스프라이트는 1차와 동일 원본 → 복사 사용(코어 재채색은 render에서 v2 규칙으로)
for n in ['sun_core_rgb', 'sun_core_a', 'sun_corona', 'moon_rgb', 'moon_a']:
    np.save(os.path.join(B, n + '.npy'), np.load(os.path.join(B1, n + '.npy')))
meta = dict(plate='P7c_1.png', S=S, X0=0, Y0=0, SUN_X=SUN_X, RIDGE_Y=RIDGE_Y, A5_x=a5_x, A5_edge=bool(edge),
            column_x=col_x, BRIDGE_Y=float(BRIDGE_Y), WATER_TOP=float(WATER_TOP), GLOW_X=gx,
            horizon_pct=float(np.median(ridge) / H * 100), circles=json.load(open(os.path.join(B1, 'meta.json')))['circles'])
json.dump(meta, open(os.path.join(B, 'meta.json'), 'w'), indent=1)
print(json.dumps({k: v for k, v in meta.items() if k != 'circles'}, indent=1))

# ================= v2 캐릭터: 코어 그라데이션(가장자리 #FE9C00 띠 = 반지름 8%) + 코로나 재채색(1.5배)
from scipy.ndimage import maximum_filter
def hx(h): return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255.
Sb = load('Sblank_1.png'); cx, cy, r = meta['circles']['Sblank']
SPR, SUN_D, SS = 1000, 300, 2
k = (2 * r) / (SUN_D * SS)
Ssp = np.clip(np.stack([np.asarray(Image.fromarray(gaussian_filter(Sb[..., c], 1.0), 'F').transform((SPR, SPR), Image.AFFINE,
        (k, 0, cx - k * SPR / 2, 0, k, cy - k * SPR / 2), resample=Image.BICUBIC)) for c in range(3)], -1), 0, 1)
g = np.mgrid[0:SPR, 0:SPR].astype(np.float32); C = SPR / 2 - 0.5
rr = np.hypot(g[1] - C, g[0] - C) / (SUN_D * SS / 2)
Lsp = luma(Ssp); detail = np.clip(Lsp / (gaussian_filter(Lsp, 30) + 1e-3), 0.6, 1.4)
stops = [(0.0, hx('#FFF1CF')), (0.42, hx('#FFD978')), (0.92, hx('#FFC24A')), (1.0, hx('#FE9C00'))]
def grad(t):
    t = np.clip(t, 0, 1); out = np.zeros(t.shape + (3,), np.float32)
    for (t0, c0), (t1, c1) in zip(stops[:-1], stops[1:]):
        mm = (t >= t0) & (t <= t1); u = ((t - t0) / (t1 - t0))[mm][:, None]
        out[mm] = c0 * (1 - u) + c1 * u
    return out
tg = np.hypot(g[1] - C + 0.10 * SUN_D, g[0] - C + 0.12 * SUN_D) / (SUN_D * SS / 2)
tg = np.where(rr > 0.92, rr, np.minimum(tg, 0.92))       # 가장자리 8% 띠는 실제 반지름 기준으로 고정
coreRGB = np.clip(grad(tg) * (detail[..., None] ** 0.55), 0, 1)
np.save(os.path.join(B, 'sun_core_rgb.npy'), coreRGB.astype(np.float32))
cor0 = Ssp * np.clip((rr - 0.985) / 0.03, 0, 1)[..., None]
Lc = luma(cor0)
Lt = gaussian_filter(np.maximum(Lc, maximum_filter(Lc, 5) * 0.9), 1.0)     # 굵기 약 1.5배
op = np.clip(Lt * 1.5, 0, 1) ** 0.75                                        # 불투명도 1.5배
u = np.clip(Lt, 0, 1) ** 0.8
corRGB = (hx('#FE9C00')[None, None] * (1 - u[..., None]) + hx('#FFC24A')[None, None] * u[..., None]) * op[..., None]
np.save(os.path.join(B, 'sun_corona.npy'), corRGB.astype(np.float32))
Image.fromarray((np.clip(np.concatenate([coreRGB * (rr < 1)[..., None] + corRGB, Ssp], 1), 0, 1) * 255).astype(np.uint8)).resize((1000, 500)).save(os.path.join(B, 'sun_v2_vs_v1src.png'))
print('sun sprites v2 saved')
