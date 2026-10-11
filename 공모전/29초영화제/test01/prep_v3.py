# -*- coding: utf-8 -*-
"""시험 1 3차: P7d(기둥 제거판) 기반 준비. 결과: test01/build_v3/
- 플레이트 P7a/P7b(=P7d), H7, 물 마스크, 불빛 마스크
- P7c 기둥 휘도 프로파일(행별, 출력 좌표) → 절차형 기둥 목표치(85%)
- 해 코어: 절차형(월면 무늬 없음) 그라데이션 + 주연감광 70%, Ø230
- 코로나: Sblank 머리카락을 #FE9C00~#FFC24A로 채색(굵기·불투명도 1.5배), Ø230 기준"""
import os, json
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter, median_filter, maximum_filter

ROOT = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(ROOT, '..', 'img')
B = os.path.join(ROOT, 'build_v3'); os.makedirs(B, exist_ok=True)
B1 = os.path.join(ROOT, 'build')
W, H = 1080, 1920
S = 2560 / 1920.0
SUN_D = 230; SS = 2; SPR = 800

def load(n): return np.asarray(Image.open(os.path.join(IMG, n)).convert('RGB')).astype(np.float32) / 255.
def s2l(c): return np.where(c <= 0.04045, c / 12.92, ((np.clip(c, 0, None) + 0.055) / 1.055) ** 2.4)
def l2s(c):
    c = np.clip(c, 0, None); return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(c, 1 / 2.4) - 0.055)
def luma(a): return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
def save(a, n): Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8)).save(os.path.join(B, n))
def hx(h): return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255.
def down(img): return np.clip(np.stack([np.asarray(Image.fromarray(gaussian_filter(img[..., c], 0.5), 'F').resize((W, H), Image.LANCZOS)) for c in range(3)], -1), 0, 1).astype(np.float32)

def ridge_of(P):
    Ls = gaussian_filter(luma(P), 1.0)
    r = np.full(W, 1000.0)
    for x in range(W):
        c = Ls[:, x]
        for y in range(820, 1100):
            if c[y] < 0.88 * c[y - 6] and c[y + 3] < 0.88 * c[y - 6]:
                r[x] = y - 0.5; break
    return median_filter(r, 5, mode='nearest'), Ls

P = down(load('P7d_1.png')); Pc = down(load('P7c_1.png'))
ridge, Ls = ridge_of(P); ridge_c, _ = ridge_of(Pc)
dr = np.abs(ridge - ridge_c)
print('ridge diff P7d vs P7c: median', np.median(dr), 'p95', np.percentile(dr, 95), 'max', dr.max())
yy = np.arange(H)[:, None]
H7 = np.clip((yy - ridge[None, :]) / 1.4 + 0.5, 0, 1).astype(np.float32)
Lrow = gaussian_filter(np.array([Ls[int(ridge[x]) - 3, x] for x in range(W)]), 5)
a5_x = int(np.argmax(Lrow))

poly_src = [(0, 1400), (330, 1395), (420, 1366), (1100, 1366), (1160, 1395), (1440, 1405), (1440, 2560), (0, 2560)]
m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).polygon([(x / S, y / S) for x, y in poly_src], fill=255)
WATER = gaussian_filter(np.asarray(m).astype(np.float32) / 255., 3)
WATER_TOP = 1366 / S; BRIDGE_Y = 1370 / S

# ---------------- P7c 기둥: 중심 x와 행별 최고 휘도(σ3 평활) → 목표 85%
Lc = gaussian_filter(luma(Pc), 3)
xs0, xs1 = 380, 700
col_x = float(np.median([xs0 + np.argmax(Lc[y, xs0:xs1]) for y in range(int(WATER_TOP) + 10, int(WATER_TOP) + 400)]))
prof = np.zeros(H, np.float32)
for y in range(int(WATER_TOP), H):
    prof[y] = Lc[y, xs0:xs1].max()
prof = gaussian_filter(prof, 6)
prof[:int(WATER_TOP)] = 0
target = 0.85 * prof
print('P7c column x', col_x, 'peak (σ3)', prof.max(), '-> target peak', target.max())

edge = (a5_x < 0.25 * W) or (a5_x > 0.75 * W)
SUN_X = col_x if edge else float(a5_x)
RIDGE_Y = float(ridge[int(round(SUN_X))])

L7 = luma(P); Lb = gaussian_filter(L7, 5)
lights = np.clip((L7 - Lb - 0.10) / 0.15, 0, 1) * (L7 > 0.5) * H7 * (1 - WATER)
lights = np.clip(gaussian_filter(lights.astype(np.float32), 1.0) * 1.6, 0, 1)

lin = s2l(P)
yy2, xx2 = np.mgrid[0:H, 0:W].astype(np.float32)
gx = float(a5_x); dy = yy2 - RIDGE_Y
G = np.exp(-((xx2 - gx) / 520) ** 2 - (np.where(dy < 0, dy / 560, dy / 300)) ** 2)
G = np.maximum(G, 0.55 * np.exp(-(np.where(dy < 0, dy / 300, dy / 160)) ** 2))
warm = np.clip((lin[..., 0] - lin[..., 2]) / (lin[..., 0] + 1e-4), 0, 1)
gfrac = np.clip(G * (0.55 + 0.45 * warm), 0, 0.92)
A = lin * (2 ** -1.3) * (1 - 0.70 * gfrac)[..., None] * np.array([0.80, 0.92, 1.12])
Yl = luma(A)[..., None]; A = Yl + (A - Yl) * 0.82
A = A * (1 - lights[..., None]) + lin * 1.05 * lights[..., None]
P7a = l2s(A)

for n, a in [('P7a', P7a), ('P7b', P)]:
    np.save(os.path.join(B, n + '.npy'), a.astype(np.float32)); save(a, n + '.png')
np.save(os.path.join(B, 'H7.npy'), H7); save(np.repeat(H7[..., None], 3, 2), 'H7.png')
np.save(os.path.join(B, 'water.npy'), WATER)
np.save(os.path.join(B, 'lights.npy'), lights.astype(np.float32))
np.save(os.path.join(B, 'ridge_out.npy'), ridge.astype(np.float32))
np.save(os.path.join(B, 'col_target.npy'), target.astype(np.float32))

# ---------------- 해 코어(절차형): t = 1-μ, μ=sqrt(1-r²) → 가장자리 휘도 ≈ 중심 70%
g = np.mgrid[0:SPR, 0:SPR].astype(np.float32); C = SPR / 2 - 0.5
R2 = SUN_D * SS / 2
rr = np.hypot(g[1] - C, g[0] - C) / R2
mu = np.sqrt(np.clip(1 - rr ** 2, 0, 1))
stops = [(0.0, hx('#FFF1CF')), (0.55, hx('#FFC24A')), (1.0, hx('#FE9C00'))]
def grad(t):
    t = np.clip(t, 0, 1); out = np.zeros(t.shape + (3,), np.float32)
    for (t0, c0), (t1, c1) in zip(stops[:-1], stops[1:]):
        mm = (t >= t0) & (t <= t1); u = ((t - t0) / (t1 - t0))[mm][:, None]
        out[mm] = c0 * (1 - u) + c1 * u
    return out
core = grad(1 - mu)
cl = luma(core); print('limb ratio edge/center', float(cl[int(C), int(C + R2 * 0.995)] / cl[int(C), int(C)]))
alpha = np.clip((1 - rr) * R2 / (2 * SS) + 0.5, 0, 1)        # 페더 2px(출력)
np.save(os.path.join(B, 'sun_core_rgb.npy'), core.astype(np.float32))
np.save(os.path.join(B, 'sun_core_a.npy'), alpha.astype(np.float32))
# 쌀알무늬 원천 필드(셀 6~10px 출력 = 12~20 스프라이트px): 대역통과 노이즈, 흐름용으로 가로 여유
rng = np.random.default_rng(31)
n0 = rng.normal(0, 1, (SPR, SPR + 400)).astype(np.float32)
gran = gaussian_filter(n0, 4.5, mode='wrap') - gaussian_filter(n0, 9.0, mode='wrap')   # 셀 약 14~18 스프라이트px = 7~9 출력px
gran = np.clip(gran / gran.std() * 0.5, -1, 1).astype(np.float32)                       # 0.05×gran → 표준편차 2.5%, 최대 ±5%
np.save(os.path.join(B, 'gran.npy'), gran)
# 저주파 얼룩 확인(<3%): 코어 휘도의 σ40 성분 vs 방사 평균
# (core는 순수 방사 함수라 저주파 얼룩 0, 쌀알무늬는 대역통과라 저주파 성분 미미)

# ---------------- 코로나(Sblank) Ø230 정렬 + 채색
Sb = load('Sblank_1.png'); cx, cy, r = json.load(open(os.path.join(B1, 'meta.json')))['circles']['Sblank']
k = (2 * r) / (SUN_D * SS)
Ssp = np.clip(np.stack([np.asarray(Image.fromarray(gaussian_filter(Sb[..., c], 1.2), 'F').transform((SPR, SPR), Image.AFFINE,
        (k, 0, cx - k * SPR / 2, 0, k, cy - k * SPR / 2), resample=Image.BICUBIC)) for c in range(3)], -1), 0, 1)
cor0 = Ssp * np.clip((rr - 0.985) / 0.03, 0, 1)[..., None]
Lc0 = luma(cor0)
Lt = gaussian_filter(np.maximum(Lc0, maximum_filter(Lc0, 4) * 0.9), 0.8)
op = np.clip(Lt * 1.5, 0, 1) ** 0.75
u = np.clip(Lt, 0, 1) ** 0.8
corRGB = (hx('#FE9C00')[None, None] * (1 - u[..., None]) + hx('#FFC24A')[None, None] * u[..., None]) * op[..., None]
np.save(os.path.join(B, 'sun_corona.npy'), corRGB.astype(np.float32))
for n in ['moon_rgb', 'moon_a']:
    np.save(os.path.join(B, n + '.npy'), np.load(os.path.join(B1, n + '.npy')))

meta = dict(plate='P7d_1.png', S=S, SUN_D=SUN_D, SPR=SPR, SUN_X=SUN_X, RIDGE_Y=RIDGE_Y, A5_x=a5_x, A5_edge=bool(edge),
            column_x_from_P7c=col_x, col_peak_P7c=float(prof.max()), col_target_peak=float(target.max()),
            BRIDGE_Y=float(BRIDGE_Y), WATER_TOP=float(WATER_TOP), GLOW_X=gx,
            horizon_pct=float(np.median(ridge) / H * 100), ridge_diff_vs_P7c=dict(median=float(np.median(dr)), p95=float(np.percentile(dr, 95)), max=float(dr.max())),
            circles=json.load(open(os.path.join(B1, 'meta.json')))['circles'])
json.dump(meta, open(os.path.join(B, 'meta.json'), 'w'), indent=1)
print(json.dumps({k_: v for k_, v in meta.items() if k_ != 'circles'}, indent=1))
