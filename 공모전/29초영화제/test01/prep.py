# -*- coding: utf-8 -*-
"""무료 시험 ① 준비: 플레이트 리프레임(P7a/P7b), H7, 물 마스크, 해 x, 캐릭터 스프라이트.
원본 img\ 는 읽기만 한다. 결과는 test01\build\ 에 저장."""
import os, json
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter, median_filter, binary_erosion

ROOT = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(ROOT, '..', 'img')
B = os.path.join(ROOT, 'build'); os.makedirs(B, exist_ok=True)
W, H = 1080, 1920

def load(n):
    return np.asarray(Image.open(os.path.join(IMG, n)).convert('RGB')).astype(np.float32) / 255.

def s2l(c): return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
def l2s(c):
    c = np.clip(c, 0, None)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(c, 1 / 2.4) - 0.055)
def luma(a): return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
def save(a, n):
    Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8)).save(os.path.join(B, n))

# ---------------------------------------------------------------- 1. 지평선(원본 좌표)
P = load('P7b_1.png'); SH, SW = P.shape[:2]
Ls = gaussian_filter(luma(P), 1.2)
ridge = np.full(SW, 1100.0)
for x in range(SW):
    c = Ls[:, x]
    for y in range(880, 1300):
        if c[y] < 0.88 * c[y - 8] and c[y + 4] < 0.88 * c[y - 8]:
            ridge[x] = y; break
ridge = median_filter(ridge, 7, mode='nearest')
# 해 x: 지평선 바로 위 행(능선 - 4px)에서 휘도가 가장 높은 열 (A5)
Lrow = np.array([Ls[int(ridge[x]) - 4, x] for x in range(SW)])
Lrow_s = gaussian_filter(Lrow, 6)
sun_sx = int(np.argmax(Lrow_s)); sun_sy = float(ridge[sun_sx])
print('sun src x', sun_sx, 'ridge y there', sun_sy, 'L', Lrow_s[sun_sx])

# ---------------------------------------------------------------- 2. 리프레임(하늘 확장)
S = 1.2                                  # 출력 1px = 원본 1.2px
X0 = SW - W * S                          # 오른쪽 정렬(해를 최대한 안쪽으로)
Y_H = 1250                               # 명세: 지평선 y≈1250
Y0 = sun_sy - Y_H * S                    # 음수 → 위쪽 하늘을 합성으로 늘린다
PAD = int(np.ceil(-Y0)) + 4
print('X0', X0, 'Y0', Y0, 'PAD', PAD)

def extend_sky(img):
    """위쪽으로 PAD행을 합성한다: 맨 위 행 색에서 짙은 남색 쪽으로 지수 수렴, 기울기 연속, 그레인 일치."""
    top = gaussian_filter(img[0:6].mean(0), (30, 0))           # (W,3)
    r0 = img[0:20].mean((0, 1)); r1 = img[100:120].mean((0, 1))
    slope = (r1 - r0) / 100.                                      # 아래로 갈수록 +
    target = np.array([0.055, 0.095, 0.215])                      # 천정 쪽 짙은 남색
    lam = np.clip((r0 - target) / np.maximum(slope, 1e-5), 150, 1200)
    d = np.arange(PAD, 0, -1)[:, None, None].astype(np.float32)   # 위로 떨어진 거리
    k = 1 - np.exp(-d / lam[None, None, :])
    ext = top[None] + (target[None, None] - top[None]) * k
    # 원본 그레인 측정 후 일치
    hp = img[0:200] - gaussian_filter(img[0:200], (3, 3, 0))
    sd = hp.std((0, 1))
    rng = np.random.default_rng(7)
    n = gaussian_filter(rng.normal(0, 1, ext.shape).astype(np.float32), (0.7, 0.7, 0))
    n /= n.std((0, 1)); ext = ext + n * sd
    out = np.concatenate([ext, img], 0)
    # 이음매 40행 블렌드(원본 쪽으로)
    bl = 40
    # 원본 맨 위 몇 행의 Seedream 테두리 흔적 제거: 0~bl행을 확장값과 섞는다
    for i in range(bl):
        a = (i / bl) ** 0.5
        base = top
        out[PAD + i] = (1 - a) * (base + (img[i] - gaussian_filter(img[i], (8, 0)))) + a * img[i]
    return out

def reframe(img):
    e = extend_sky(img)
    oy = PAD + Y0
    chans = []
    for c in range(3):
        ch = Image.fromarray(e[..., c].astype(np.float32), 'F')
        ch = ch.transform((W, H), Image.AFFINE, (S, 0, X0, 0, S, oy), resample=Image.BICUBIC)
        # 1.2배 축소이므로 미리 약하게 저역통과
        chans.append(np.asarray(ch))
    return np.clip(np.stack(chans, -1), 0, 1)

e_pre = gaussian_filter(P, (0.45, 0.45, 0))
P7b = reframe(e_pre)

def to_out_x(sx): return (sx - X0) / S
def to_out_y(sy): return (sy - Y0) / S
SUN_X = to_out_x(sun_sx); RIDGE_Y = to_out_y(sun_sy)
print('sun out x', SUN_X, 'ridge out y', RIDGE_Y)

# ---------------------------------------------------------------- 3. H7(도시=1) 출력 좌표
xs = X0 + (np.arange(W) + 0.5) * S - 0.5
r_out = to_out_y(np.interp(xs, np.arange(SW), ridge))
# 세밀화: 출력 해상도에서 열마다 다시 계단을 찾는다(r_out ±10 범위)
Lo = gaussian_filter(luma(P7b), 0.8)
for x in range(W):
    y0 = int(r_out[x]) - 10
    c = Lo[:, x]
    for y in range(max(y0, 6), int(r_out[x]) + 12):
        if c[y] < 0.9 * c[y - 5]:
            r_out[x] = y - 0.5; break
r_out = median_filter(r_out, 5, mode='nearest')
yy = np.arange(H)[:, None]
H7 = np.clip((yy - r_out[None, :]) / 1.6 + 0.5, 0, 1).astype(np.float32)   # 1.6px 페더
save(np.repeat(H7[..., None], 3, 2), 'H7.png')

# ---------------------------------------------------------------- 4. 물 마스크(원본 좌표 폴리곤 → 출력)
poly_src = [(670, 1165), (830, 1165), (1060, 1262), (1080, 1300), (1100, 1340), (1160, 1385),
            (1230, 1420), (1300, 1460), (1380, 1500), (1440, 1530), (1440, 2560), (0, 2560),
            (0, 1550), (100, 1500), (330, 1400), (400, 1300), (417, 1262)]
poly = [(to_out_x(x), to_out_y(y)) for x, y in poly_src]
m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).polygon(poly, fill=255)
WATER = gaussian_filter(np.asarray(m).astype(np.float32) / 255., 4)
BRIDGE_Y = to_out_y(1300)
save(np.repeat(WATER[..., None], 3, 2), 'water.png')

# ---------------------------------------------------------------- 5. 불빛 마스크(작은 따뜻한 점광원, 지평선 아래)
L7 = luma(P7b); Lb = gaussian_filter(L7, 6)
lights = np.clip((L7 - Lb - 0.10) / 0.15, 0, 1) * (L7 > 0.55) * H7 * (1 - WATER * 0.0)
lights = gaussian_filter(lights.astype(np.float32), 1.0)
lights = np.clip(lights * 1.6, 0, 1)

# ---------------------------------------------------------------- 6. P7a: -1.3EV, 차갑게, 글로우 70% 감소
lin = s2l(P7b)
yy2, xx2 = np.mgrid[0:H, 0:W].astype(np.float32)
# 글로우 맵: 해 위치 지평선 중심의 넓은 타원 + 지평선을 따라가는 띠 (위쪽 하늘과 물 반사 모두)
dy = (yy2 - RIDGE_Y)
G = np.exp(-((xx2 - SUN_X) / 430) ** 2 - (np.where(dy < 0, dy / 520, dy / 330)) ** 2)
G = np.maximum(G, 0.55 * np.exp(-(np.where(dy < 0, dy / 260, dy / 160)) ** 2))
# 글로우 비율: 각 픽셀에서 '글로우가 차지하는 몫' 추정 = 1 - (따뜻함 제거 후)/(현재)
warm = np.clip((lin[..., 0] - lin[..., 2]) / (lin[..., 0] + 1e-4), 0, 1)
gfrac = np.clip(G * (0.55 + 0.45 * warm), 0, 0.92)
P7a_lin = lin * (2 ** -1.3) * (1 - 0.70 * gfrac)[..., None]
# 차가운 보정(선형 채널 게인) + 따뜻한 색 약간 탈채도
P7a_lin = P7a_lin * np.array([0.80, 0.92, 1.12])
Y = (0.2126 * P7a_lin[..., 0] + 0.7152 * P7a_lin[..., 1] + 0.0722 * P7a_lin[..., 2])[..., None]
P7a_lin = Y + (P7a_lin - Y) * 0.82
# 이른 시간이라 강변 불빛은 켜진 채로: 원래 밝기 유지
P7a_lin = P7a_lin * (1 - lights[..., None]) + lin * 1.05 * lights[..., None]
P7a = l2s(P7a_lin)

# ---------------------------------------------------------------- 7. 원 맞춤
def fit_circle(img, thr, exclude_top=True):
    L = gaussian_filter(luma(img), 2)
    msk = L > thr
    ys, xs_ = np.nonzero(msk)
    cx, cy = xs_.mean(), ys.mean()
    pts = []
    for ang in np.linspace(0, 2 * np.pi, 720, endpoint=False):
        if exclude_top and (np.pi * 1.08 < ang < np.pi * 1.92):   # 위쪽(코로나 머리카락) 제외 (y 아래가 +)
            continue
        dx, dy_ = np.cos(ang), np.sin(ang)
        for r in range(200, 900):
            x = int(cx + dx * r); y = int(cy + dy_ * r)
            if x < 0 or y < 0 or x >= img.shape[1] or y >= img.shape[0] or L[y, x] < thr:
                pts.append((cx + dx * r, cy + dy_ * r)); break
    pts = np.array(pts)
    A = np.c_[2 * pts[:, 0], 2 * pts[:, 1], np.ones(len(pts))]
    b = (pts ** 2).sum(1)
    c = np.linalg.lstsq(A, b, rcond=None)[0]
    r = np.sqrt(c[2] + c[0] ** 2 + c[1] ** 2)
    return float(c[0]), float(c[1]), float(r)

info = {}
Sb = load('Sblank_1.png'); S0 = load('S0b_1.png'); Mb = load('Mblank_1.png'); M0 = load('M0_1.png')
# 해: 코어 가장자리는 밝은 노랑(L>0.55), 코로나 바깥은 주황 글로우라 L 0.55 경계가 코어 경계
for n, im, thr, ex in [('Sblank', Sb, 0.50, True), ('S0b', S0, 0.50, True), ('Mblank', Mb, 0.25, False), ('M0', M0, 0.25, False)]:
    info[n] = fit_circle(im, thr, ex); print(n, info[n])

# ---------------------------------------------------------------- 8. 해 스프라이트(코어/코로나), 출력 스케일 2배로 저장
SUN_D = 300; SS = 2                 # 슈퍼샘플 배율
SPR = 1000                          # 스프라이트 캔버스(2배 기준) → 출력 500px
def crop_aligned(img, cx, cy, r, D, canvas):
    """원 중심을 캔버스 중심에, 지름을 D(px)로 맞춘다."""
    k = (2 * r) / D
    out = []
    for c in range(3):
        ch = Image.fromarray(img[..., c], 'F').transform((canvas, canvas), Image.AFFINE,
                (k, 0, cx - k * canvas / 2, 0, k, cy - k * canvas / 2), resample=Image.BICUBIC)
        out.append(np.asarray(ch))
    return np.clip(np.stack(out, -1), 0, 1)

cx, cy, r = info['Sblank']
Ssp = crop_aligned(gaussian_filter(Sb, (1.0, 1.0, 0)), cx, cy, r, SUN_D * SS, SPR)
g = np.mgrid[0:SPR, 0:SPR].astype(np.float32); C = SPR / 2 - 0.5
rr = np.hypot(g[1] - C, g[0] - C) / (SUN_D * SS / 2)               # 1 = 코어 가장자리
core_a = np.clip((1 - rr) * (SUN_D * SS / 2) / 2.0 + 0.5 - 2 * SS / 2.0, 0, 1)  # r-2px 원형 마스크
# 코어 재채색: 원본의 플라스마 디테일(휘도 비)만 남기고 명세 그라데이션으로
Ls_ = luma(Ssp); detail = Ls_ / (gaussian_filter(Ls_, 30) + 1e-3)
detail = np.clip(detail, 0.6, 1.4)
stops = [(0.0, (0xFF, 0xF1, 0xCF)), (0.55, (0xFF, 0xC2, 0x4A)), (1.0, (0xFE, 0x9C, 0x00))]
def grad(t):
    t = np.clip(t, 0, 1); out = np.zeros(t.shape + (3,), np.float32)
    for (t0, c0), (t1, c1) in zip(stops[:-1], stops[1:]):
        m_ = (t >= t0) & (t <= t1); u = ((t - t0) / (t1 - t0))[m_][:, None]
        out[m_] = (np.array(c0) * (1 - u) + np.array(c1) * u) / 255.
    return out
# 중심을 살짝 위-왼쪽으로(광원감), 반경에 감마
tg = np.hypot(g[1] - C + 0.10 * SUN_D * SS / 2, g[0] - C + 0.12 * SUN_D * SS / 2) / (SUN_D * SS / 2)
coreRGB = grad(tg ** 1.25)
coreRGB = np.clip(coreRGB * (detail[..., None] ** 0.55), 0, 1)
# 디테일 노이즈(표면 변위용 원천)는 render에서 재샘플
np.save(os.path.join(B, 'sun_core_rgb.npy'), coreRGB.astype(np.float32))
np.save(os.path.join(B, 'sun_core_a.npy'), core_a.astype(np.float32))
# 코로나: 코어 원 바깥(r>0.985)의 원본 = 검은 배경 위 불꽃·글로우 → screen용
cor = Ssp * np.clip((rr - 0.985) / 0.03, 0, 1)[..., None]
np.save(os.path.join(B, 'sun_corona.npy'), cor.astype(np.float32))

# ---------------------------------------------------------------- 9. 달 스프라이트(Ø200, 2배)
MOON_D = 200; MSPR = 520
cx, cy, r = info['Mblank']
Msp = crop_aligned(gaussian_filter(Mb, (1.2, 1.2, 0)), cx, cy, r, MOON_D * SS, MSPR)
g = np.mgrid[0:MSPR, 0:MSPR].astype(np.float32); C = MSPR / 2 - 0.5
rr = np.hypot(g[1] - C, g[0] - C) / (MOON_D * SS / 2)
moon_a = np.clip((1 - rr) * (MOON_D * SS / 2) / 2.0 + 0.5 - 2 * SS / 2.0, 0, 1)
# 최고 휘도 92%
Lm = luma(Msp)[moon_a > 0.5]; Msp = Msp * (0.92 / np.percentile(Lm, 99.8))
np.save(os.path.join(B, 'moon_rgb.npy'), np.clip(Msp, 0, 1).astype(np.float32))
np.save(os.path.join(B, 'moon_a.npy'), moon_a.astype(np.float32))

# ---------------------------------------------------------------- 저장
np.save(os.path.join(B, 'P7a.npy'), P7a.astype(np.float32)); save(P7a, 'P7a.png')
np.save(os.path.join(B, 'P7b.npy'), P7b.astype(np.float32)); save(P7b, 'P7b_reframed.png')
np.save(os.path.join(B, 'H7.npy'), H7); np.save(os.path.join(B, 'water.npy'), WATER)
np.save(os.path.join(B, 'lights.npy'), lights.astype(np.float32))
np.save(os.path.join(B, 'ridge_out.npy'), r_out.astype(np.float32))
meta = dict(S=S, X0=X0, Y0=Y0, PAD=PAD, SUN_X=float(SUN_X), RIDGE_Y=float(RIDGE_Y),
            sun_src_x=sun_sx, sun_src_ridge=sun_sy, BRIDGE_Y=float(BRIDGE_Y), circles=info,
            ridge_out_at_sun=float(r_out[int(round(SUN_X))]))
json.dump(meta, open(os.path.join(B, 'meta.json'), 'w'), indent=1)
print(json.dumps(meta, indent=1))
