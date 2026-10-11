# -*- coding: utf-8 -*-
"""29초영화제 배경 플레이트 후처리 (v2.2, plate_edits.json 기준)

사용:  python edit_plates.py            # 전체
       python edit_plates.py P1 P8      # 일부만
원본은 건드리지 않고 img/fix/<이름>_fix.png 로 저장, 비교 크롭은 img/fix/compare/.
좌표는 모두 원본 1440x2560 px.
"""
import os, sys, json
import numpy as np, cv2
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.dirname(HERE)
CMP = os.path.join(HERE, 'compare')
os.makedirs(CMP, exist_ok=True)
NAVY = np.array([0x0C, 0x18, 0x34], np.float32)        # 밤하늘 통일 목표
RNG = np.random.default_rng(2910)


# ---------------------------------------------------------------- 기본 도구
def load(n):
    return np.asarray(Image.open(os.path.join(IMG, n)).convert('RGB')).astype(np.float32)


def save(a, n):
    Image.fromarray(np.clip(a + 0.5, 0, 255).astype(np.uint8)).save(os.path.join(HERE, n))


def u8(a):
    return np.clip(a + 0.5, 0, 255).astype(np.uint8)


def gblur(a, s):
    return cv2.GaussianBlur(a, (0, 0), s) if s > 0 else a


def rect_mask(shape, r, inset=0):
    m = np.zeros(shape[:2], np.float32)
    x0, y0, x1, y1 = r
    m[y0 + inset:y1 + 1 - inset, x0 + inset:x1 + 1 - inset] = 1
    return m


def feather(m, px):
    """바깥으로 px 만큼 부드럽게(안쪽 값은 1 유지)."""
    if px <= 0:
        return m
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * px + 1, 2 * px + 1))
    d = cv2.dilate(m, k)
    return np.maximum(m, gblur(d, px / 2.0)) if False else np.clip(gblur(d, px / 2.5), 0, 1) * (d > 0) + 0 * m


def soft(m, s):
    return np.clip(gblur(m.astype(np.float32), s), 0, 1)


def mix(a, b, m):
    m = m[..., None] if m.ndim == 2 else m
    return a * (1 - m) + b * m


def noise_std(a, box):
    """box 주변의 고주파 잔차 표준편차(채널별, MAD 추정)."""
    x0, y0, x1, y1 = box
    p = a[max(0, y0):y1, max(0, x0):x1]
    hp = p - gblur(p, 1.2)
    med = np.median(hp.reshape(-1, 3), 0)
    return 1.4826 * np.median(np.abs(hp.reshape(-1, 3) - med), 0)


def grain(shape, std, corr=0.6):
    n = RNG.standard_normal(shape[:2] + (3,)).astype(np.float32)
    # 채널 간 상관(루마 그레인) 60%
    l = RNG.standard_normal(shape[:2]).astype(np.float32)[..., None]
    n = 0.6 * l + 0.8 * n
    n = gblur(n, corr)
    n /= n.reshape(-1, 3).std(0) + 1e-6
    return n * np.asarray(std, np.float32)


def regrain(out, ref_std, m, hp_sigma=1.2):
    """편집 영역의 잔존 노이즈를 재서 모자란 만큼 그레인을 더한다."""
    ys, xs = np.where(m > 0.5)
    if len(ys) == 0:
        return out
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    cur = noise_std(out, (x0, y0, x1, y1))
    need = np.sqrt(np.clip(np.asarray(ref_std) ** 2 - cur ** 2, 0, None))
    g = grain(out.shape, need)
    return out + g * m[..., None]


def tex_fill(a, hole, src_shift, s_low=6, flip=False):
    """cv2.inpaint(구조·색) 저주파 + 소스 패치(질감) 고주파 합성."""
    m8 = (hole > 0.5).astype(np.uint8) * 255
    inp = cv2.inpaint(u8(a), m8, 7, cv2.INPAINT_TELEA).astype(np.float32)
    dx, dy = src_shift
    M = np.float32([[1, 0, dx], [0, 1, dy]])
    src = cv2.warpAffine(a, M, (a.shape[1], a.shape[0]), flags=cv2.INTER_NEAREST,
                         borderMode=cv2.BORDER_REFLECT)          # dst(x) = a(x - d)
    if flip:
        src = src[:, ::-1]
    hf = src - gblur(src, s_low)
    return gblur(inp, s_low) + hf


def to_lin(a):
    x = a / 255.0
    return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)


def to_srgb(l):
    l = np.clip(l, 0, None)
    x = np.where(l <= 0.0031308, l * 12.92, 1.055 * np.power(l, 1 / 2.4) - 0.055)
    return x * 255.0


def luma(a):
    return a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722


# ---------------------------------------------------------------- 비교 이미지
def compare(before, after, box, name, zoom=None, label=''):
    x0, y0, x1, y1 = box
    m = max(30, (x1 - x0) // 4, (y1 - y0) // 4)
    X0, Y0 = max(0, x0 - m), max(0, y0 - m)
    X1, Y1 = min(before.shape[1], x1 + m), min(before.shape[0], y1 + m)
    b = Image.fromarray(u8(before[Y0:Y1, X0:X1]))
    c = Image.fromarray(u8(after[Y0:Y1, X0:X1]))
    w, h = b.size
    if zoom is None:
        zoom = max(1, min(6, int(560 / max(w, h))))
        if max(w, h) > 760:
            zoom = 760 / max(w, h)
    W, H = int(w * zoom), int(h * zoom)
    rs = Image.LANCZOS if zoom < 1 else Image.NEAREST
    b, c = b.resize((W, H), rs), c.resize((W, H), rs)
    sheet = Image.new('RGB', (2 * W + 12, H + 26), (40, 40, 40))
    sheet.paste(b, (0, 26)); sheet.paste(c, (W + 12, 26))
    d = ImageDraw.Draw(sheet)
    d.text((4, 6), 'BEFORE ' + label, fill=(255, 255, 255))
    d.text((W + 16, 6), 'AFTER x%.2g' % zoom, fill=(255, 255, 255))
    sheet.save(os.path.join(CMP, name + '.png'))


def compare_full(before, after, name):
    b = Image.fromarray(u8(before)).resize((540, 960), Image.LANCZOS)
    c = Image.fromarray(u8(after)).resize((540, 960), Image.LANCZOS)
    s = Image.new('RGB', (1092, 960), (40, 40, 40))
    s.paste(b, (0, 0)); s.paste(c, (552, 0))
    s.save(os.path.join(CMP, name + '.png'))


# ---------------------------------------------------------------- 하늘 통일
def sky_mask(a, y_max, blue_min=4, lum_max=110):
    g = gblur(luma(a), 2)
    gx = cv2.Sobel(g, cv2.CV_32F, 1, 0); gy = cv2.Sobel(g, cv2.CV_32F, 0, 1)
    gm = np.hypot(gx, gy)
    cand = (gm < 6) & (g < lum_max) & ((a[..., 2] - a[..., 0]) > blue_min)
    cand[y_max:] = False
    cand = cv2.morphologyEx(cand.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(cand, 8)
    keep = np.zeros_like(cand)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_TOP] <= 2 or st[i, cv2.CC_STAT_AREA] > 20000:
            keep[lab == i] = 1
    keep = cv2.morphologyEx(keep, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
    return soft(cv2.erode(keep, np.ones((5, 5), np.uint8)).astype(np.float32), 6)


def unify_sky(a, y_h, top_frac=0.6, name=''):
    m = sky_mask(a, y_h)
    yu = int(y_h * top_frac)
    sel = m[:yu] > 0.9
    cur = np.median(a[:yu][sel], 0)
    off = np.clip(NAVY - cur, -40, 40)
    y = np.arange(a.shape[0], dtype=np.float32)
    w = np.clip((y_h - y) / max(1, (y_h - yu)), 0, 1)
    w = w * w * (3 - 2 * w)                               # smoothstep
    out = a + off[None, None, :] * (m * w[:, None])[..., None]
    after = np.median(out[:yu][sel], 0)
    print('  sky %s: before #%02X%02X%02X -> after #%02X%02X%02X (offset %s)' % (
        (name,) + tuple(u8(cur)) + tuple(u8(after)) + (np.round(off, 1),)))
    return out, m


# ================================================================ 플레이트별
def do_P1():
    a = load('P1_1.png'); o = a.copy()
    ref = noise_std(a, (700, 2150, 1400, 2290))
    # P1-01 간판: 무늬 없는 발광 패널 -----------------------------------
    # 주 간판(기울어진 사각): 위 네온선 아래 ~ 아래 네온선 위
    poly = np.array([[979, 2315], [1306, 2346], [1306, 2388], [979, 2357]], np.int32)
    pm = np.zeros(a.shape[:2], np.float32); cv2.fillPoly(pm, [poly], 1)
    # 패널 좌표계: u(가로 0..1), v(세로 0..1)
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]].astype(np.float32)
    u = np.clip((xx - 979) / (1306 - 979), 0, 1)
    top = 2315 + (2346 - 2315) * u; bot = 2357 + (2388 - 2357) * u
    v = np.clip((yy - top) / (bot - top), 0, 1)
    # 네온선의 실제 색을 기준으로, 조금 어두운 확산 패널
    neon = np.median(a[2343:2350, 990:1000].reshape(-1, 3), 0)
    base = np.array([240, 241, 244], np.float32)
    prof = (0.90 + 0.10 * np.clip(np.sin(np.pi * v), 0, 1) ** 0.7) * (0.93 + 0.07 * np.sin(np.pi * np.clip(u * 0.9 + 0.05, 0, 1)))
    # LED 라이트박스 특유의 아주 옅은 세로 얼룩(주기 ~22px)
    panel = base[None, None, :] * prof[..., None]
    pmask = soft(pm, 1.4)
    o = mix(o, panel, pmask)
    # 블룸: 패널 빛이 주변으로 번짐(가산 12%)
    bloom = gblur(panel * pmask[..., None], 9)
    o = o + 0.12 * bloom * (1 - pmask[..., None])
    # 오른쪽 작은 글씨 줄(패널 오른쪽 끝 아래 부분)도 같은 패널에 포함됨
    # 파란 라이트박스: 가로 중앙값으로 점 글자 제거(파랑/흰 경계 유지)
    bx0, by0, bx1, by1 = 866, 2301, 976, 2352
    blk = a[by0:by1, bx0:bx1]
    # 첫 점 글자 왼쪽의 깨끗한 바탕 열(x 869~877)로 행별 색을 정하고 가로로 편다
    prof_c = a[by0:by1, 869:878].mean(1)
    hb = np.repeat(prof_c[:, None, :], bx1 - bx0, 1)
    hb = cv2.GaussianBlur(hb, (0, 0), sigmaX=4, sigmaY=0.8)
    bm = np.zeros(a.shape[:2], np.float32); bm[by0 + 2:by1 - 2, bx0 + 3:bx1 - 3] = 1
    bm = soft(bm, 1.5)
    full = o.copy(); full[by0:by1, bx0:bx1] = hb
    o = mix(o, full, bm)
    m_all = np.maximum(pmask, bm)
    o = regrain(o, ref * 0.8, (m_all > 0.5).astype(np.float32) * m_all)
    compare(a, o, (845, 2298, 1312, 2413), 'P1-01_sign')
    # P1-02/03 하늘 점 ----------------------------------------------------
    for pid, (px, py) in (('P1-02', (1335, 567)), ('P1-03', (1302, 627))):
        h = np.zeros(a.shape[:2], np.float32); cv2.circle(h, (px, py), 16, 1, -1)
        fill = tex_fill(o, h, (-40, 0))
        hm = soft(h, 2.5)
        o = mix(o, fill, hm)
        compare(a, o, (px - 10, py - 10, px + 10, py + 10), pid + '_skydot', zoom=6)
    save(o, 'P1_1_fix.png'); compare_full(a, o, 'P1_full')
    return {'P1-01': 'done', 'P1-02': 'done', 'P1-03': 'done'}


def do_P4b():
    a = load('P4b_1.png'); o = a.copy()
    H, W = a.shape[:2]
    ref = noise_std(a, (430, 1260, 680, 1440))
    # P4-01/02 수면·부두 -> 어두운 숲 사면 ------------------------------
    # 로컬 시도 결과(타일 이음, 평평한 검은 덩어리, 인공적인 수관선)가 자연스럽지 않아
    # Seedream 편집으로 넘긴다. 시험용으로만 LOCAL_COVER=True.
    if LOCAL_COVER:
        o = _p4_local_cover(a, o, ref)
    r = (1220, 1777, 1327, 1955)
    bl = gblur(o, 6)
    m = soft(rect_mask(a.shape, r, inset=7), 3)
    o = mix(o, bl, m)
    o = regrain(o, noise_std(a, (1224, 1800, 1237, 1940)), m)   # 판 여백의 노이즈
    compare(a, o, r, 'P4-03_sign_blur')
    o, sm = unify_sky(o, 980, name='P4b')
    save(o, 'P4b_1_fix.png'); compare_full(a, o, 'P4b_full')
    return {'P4-01': 'needs_seedream', 'P4-02': 'needs_seedream', 'P4-03': 'done'}


LOCAL_COVER = False


def _p4_local_cover(a, o, ref):
    H, W = a.shape[:2]
    xs = np.arange(W, dtype=np.float32)
    rng = np.random.default_rng(7)
    edge = 1236 + 0.010 * xs                       # 기본 능선(오른쪽이 살짝 낮음)
    # 수관(나무 꼭대기) 요철: 폭 8~26px 가우시안 봉우리
    bumps = np.zeros(W, np.float32)
    x = -10.0
    while x < 470:
        wdt = rng.uniform(8, 24); hgt = rng.uniform(4, 13)
        bumps += hgt * np.exp(-0.5 * ((xs - x) / (wdt / 2.2)) ** 2)
        x += rng.uniform(7, 18)
    edge = edge - bumps + 8
    # 기존 숲 경계(x>=380)와 이어지게
    yy = np.arange(H)[:, None].astype(np.float32)
    fm = (yy >= edge[None, :]).astype(np.float32)
    fm[:, 430:] = 0
    fm[1500:] = 0
    # x 360~430 구간은 오른쪽으로 갈수록 기존 숲으로 넘김
    ramp = np.clip((430 - xs) / 70.0, 0, 1)
    fm *= ramp[None, :]
    fm = np.clip(gblur(fm, 2.2), 0, 1)
    # 아래쪽은 원래 숲(검은 사면)과 섞이도록 y 1440~1500 서서히 페이드
    yfade = np.clip((1500 - yy) / 60.0, 0, 1)
    fm *= yfade
    # 질감: 오른쪽 숲(x 430~690, y 1240~1470) 타일, 좌우 반전 교대
    src = a[1240:1470, 430:690].copy()
    tile = np.concatenate([src[:, ::-1], src, src[:, ::-1]], 1)   # 780px
    canopy = np.zeros_like(a)
    th = tile.shape[0]
    for y0 in range(1200, 1520, th - 20):
        hgt = min(th, H - y0)
        canopy[y0:y0 + hgt, 0:780] = tile[:hgt]
    # 저주파는 주변 숲 톤(아주 어두운 녹회)으로 고정, 고주파만 패치에서
    lowref = np.median(a[1300:1440, 450:650].reshape(-1, 3), 0)
    canopy = lowref[None, None, :] + (canopy - gblur(canopy, 14)) * 0.9
    # 능선 바로 아래 아주 옅은 림(뒤 시가지 불빛 번짐)
    rim = np.clip((yy - edge[None, :]) / 10.0, 0, 1)
    rimg = np.exp(-np.clip(yy - edge[None, :], 0, None) / 7.0) * (yy >= edge[None, :])
    glow = gblur(a, 6)[..., :] * 0
    canopy = canopy + 10 * rimg[..., None] * np.array([1.0, 0.9, 0.8], np.float32)
    o = mix(o, canopy, fm)
    o = regrain(o, ref, fm)
    compare(a, o, (0, 1150, 470, 1520), 'P4-01-02_water_cover_LOCAL_TRIAL')
    return o


def do_P5c():
    a = load('P5c_1.png'); o = a.copy()
    for pid, r, s in (('P5-01', (838, 1357, 941, 1478), 10),
                      ('P5-02', (531, 1363, 627, 1453), 9),
                      ('P5-03', (941, 1344, 1030, 1434), 9)):
        ref = noise_std(a, (r[0] - 40, r[3] + 10, r[2] + 40, r[3] + 80))
        bl = gblur(o, s)
        m = soft(rect_mask(a.shape, r), 5)
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25))
        m = np.clip(gblur(cv2.dilate(rect_mask(a.shape, r), k), 12 / 2.5), 0, 1)
        o = mix(o, bl, m)
        o = regrain(o, ref, m)
        compare(a, o, r, pid + '_face_blur', zoom=3)
    # P5-04 파란 액체 -> 무광 스테인리스 --------------------------------
    hsv = cv2.cvtColor(u8(o), cv2.COLOR_RGB2HSV).astype(np.float32)
    hue, sat = hsv[..., 0] * 2, hsv[..., 1] / 255.0
    blue = np.clip((sat - 0.04) / 0.12, 0, 1) * np.clip(1.6 - np.abs(hue - 205) / 35, 0, 1)
    zone = np.zeros(a.shape[:2], np.float32)
    zone[2036:2470, 0:1440] = 1            # 탁자 윗면(림 아래). 지정 영역 x883~ 왼쪽의 같은 파란 액체 포함, 파란 의자 제외
    zone = soft(zone, 4)
    bm = soft(blue * zone, 3)
    L = luma(o)
    grey = np.array([0x8E, 0x93, 0x99], np.float32) / luma(np.array([[[0x8E, 0x93, 0x99]]], np.float32))[0, 0]
    steel = L[..., None] * grey[None, None, :]
    steel = mix(steel, o, np.full(L.shape, 0.0, np.float32))
    # 채도 -85%: 원래 색 15% 남김
    steel = steel * 0.85 + (o * 0.15 + (L[..., None] - luma(o)[..., None]) * 0) * 1.0
    steel = steel * 0.85 / 0.85
    hl = np.clip((L - 190) / 50, 0, 1)
    warm = np.array([0xFF, 0xB1, 0x5C], np.float32)
    steel = mix(steel, steel * 0.9 + warm * 0.1, hl)
    # 무광: 아주 밝은 반짝임만 살짝 눌러 준다
    steel = np.where(steel > 225, 225 + (steel - 225) * 0.5, steel)
    o = mix(o, steel, bm)
    compare(a, o, (690, 1990, 1440, 2470), 'P5-04_recolor')
    o, sm = unify_sky(o, 900, name='P5c')
    save(o, 'P5c_1_fix.png'); compare_full(a, o, 'P5c_full')
    return {'P5-01': 'done', 'P5-02': 'done', 'P5-03': 'done', 'P5-04': 'done'}


def do_P6():
    a = load('P6_1.png'); o = a.copy()
    # P6-01 엠블럼: 같은 높이 옆 차체면으로
    r = (417, 2029, 458, 2052)
    h = soft(rect_mask(a.shape, (r[0] - 3, r[1] - 3, r[2] + 3, r[3] + 3)), 0.1)
    fill = tex_fill(o, h, (52, 0), s_low=4)
    hm = soft(rect_mask(a.shape, (r[0] - 3, r[1] - 3, r[2] + 3, r[3] + 3)), 3)
    ref = noise_std(a, (340, 2010, 520, 2070))
    o = mix(o, fill, hm); o = regrain(o, ref, hm)
    compare(a, o, r, 'P6-01_emblem', zoom=5)
    # P6-02 번호판 블러
    r = (378, 2099, 467, 2135)
    m = np.clip(gblur(cv2.dilate(rect_mask(a.shape, r), np.ones((7, 7), np.uint8)), 2.5), 0, 1)
    o = mix(o, gblur(o, 6), m); o = regrain(o, noise_std(a, (340, 2060, 520, 2095)), m)
    compare(a, o, r, 'P6-02_plate_blur', zoom=5)
    # P6-03 정류장 표지 제거: 지붕선 위는 오른쪽 밤하늘(+75px) 클론, 지붕면은 인페인트
    r = (22, 1632, 83, 1738)
    hole = rect_mask(a.shape, (16, 1626, 92, 1742))
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]].astype(np.float32)
    roof_y = 1712.0 - xx * 4.0 / 100.0                      # 쉘터 지붕 윗선(왼쪽 1712 → 오른쪽 1708)
    skyp = hole * (yy < roof_y - 1)
    roofp = hole * (yy >= roof_y - 1)
    M = np.float32([[1, 0, -75], [0, 1, 10]])               # 오른쪽 75px, 위 10px 하늘
    clone = cv2.warpAffine(o, M, (a.shape[1], a.shape[0]), flags=cv2.INTER_NEAREST, borderMode=cv2.BORDER_REFLECT)
    sky_fill = o.copy(); sky_fill = mix(sky_fill, clone, skyp)
    # 지붕 띠: 행마다 양옆 깨끗한 지붕 열(x 12~15, x 88~91)을 선형 보간 + 오른쪽 지붕(x 86~111) 질감
    roof_fill = o.copy()
    L0, R0 = 12, 96
    lo = gblur(o, 1.0)
    rf = lambda x: 1712.0 - x * 4.0 / 100.0
    for y in range(1700, 1745):
        for x in range(14, 95):
            v = y - rf(x)
            yl, yr = int(round(rf(L0) + v)), int(round(rf(R0) + v))
            cl = o[yl, L0 - 2:L0 + 2].mean(0); cr = o[yr, R0 - 2:R0 + 2].mean(0)
            w = (x - L0) / float(R0 - L0)
            t = (x - (r[0] - 4)) % 50
            xs_ = 86 + (t if t < 25 else 49 - t)
            roof_fill[y, x] = cl * (1 - w) + cr * w
    fill = mix(sky_fill, roof_fill, soft(roofp, 0.8))
    o = mix(o, fill, soft(hole, 1.5))
    hm = soft(hole, 2.0)
    o = regrain(o, noise_std(a, (90, 1600, 160, 1690)), hm)
    compare(a, o, r, 'P6-03_stop_sign', zoom=3)
    # P6-04 도로 표지 제거: 같은 기둥의 위쪽을 수직 클론
    r = (1376, 1843, 1411, 1920)
    h = rect_mask(a.shape, (r[0] - 3, r[1] - 4, r[2] + 3, r[3] + 4))
    fill = tex_fill(o, h, (0, -88), s_low=3)
    M = np.float32([[1, 0, 0], [0, 1, 88]])
    clone = cv2.warpAffine(o, M, (a.shape[1], a.shape[0]), borderMode=cv2.BORDER_REFLECT)
    pole = np.zeros(a.shape[:2], np.float32); pole[:, 1388:1400] = 1
    pole = soft(pole, 1.5)
    fill = mix(fill, clone, pole)
    hm = soft(h, 2.5)
    o = mix(o, fill, hm); o = regrain(o, noise_std(a, (1340, 1700, 1440, 1830)), hm)
    compare(a, o, r, 'P6-04_road_sign', zoom=3)
    # P6-05 행선지 표시기: 어두운 빈 유리창, 매끈한 테두리
    roi = (340, 1700, 620, 1830)
    sub = luma(o[roi[1]:roi[3], roi[0]:roi[2]])
    blk = (sub < 14).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(blk, 8)
    i = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
    pts = np.column_stack(np.where(lab == i))[:, ::-1].astype(np.float32) + np.float32([roi[0], roi[1]])
    rect = cv2.minAreaRect(pts)
    (cx, cy), (rw, rh), ang = rect
    box = cv2.boxPoints(((cx, cy), (rw + 2, rh + 2), ang))
    print('  P6-05 display rect', np.round(rect[0], 1), np.round(rect[1], 1), round(ang, 2))
    ss = 4                                    # 안티앨리어싱
    big = np.zeros((a.shape[0] * 1, a.shape[1] * 1), np.float32)
    def poly_mask(bx, grow):
        c = np.mean(bx, 0)
        bx2 = c + (bx - c) * (1 + grow / np.array([rw, rh]).max())
        m = np.zeros((roi[3] - roi[1]) * ss, np.float32).reshape(-1, 1) * np.zeros((1, (roi[2] - roi[0]) * ss), np.float32)
        p = ((bx2 - np.float32([roi[0], roi[1]])) * ss).astype(np.int32)
        cv2.fillPoly(m, [p], 1)
        m = cv2.resize(m, (roi[2] - roi[0], roi[3] - roi[1]), interpolation=cv2.INTER_AREA)
        full = np.zeros(a.shape[:2], np.float32); full[roi[1]:roi[3], roi[0]:roi[2]] = m
        return full
    inner = poly_mask(box, 0)
    outer = poly_mask(box, 9)
    # 1) 테두리 링(오렌지 가장자리)을 주변 차체로 메우기
    ring = np.clip(outer - inner * 0.0, 0, 1)
    hole = ((outer > 0.02)).astype(np.float32)
    inp = cv2.inpaint(u8(o), (hole * 255).astype(np.uint8), 9, cv2.INPAINT_TELEA).astype(np.float32)
    o2 = mix(o, inp, soft(hole, 1.5))
    # 2) 어두운 유리면: 위가 아주 살짝 밝은 그라데이션 + 얇은 반사
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]].astype(np.float32)
    t = np.clip((yy - (cy - rh / 2)) / max(rh, 1), 0, 1)
    glass = np.stack([10 + 6 * (1 - t), 12 + 7 * (1 - t), 16 + 9 * (1 - t)], -1)
    # 내부 프레임(어두운 회색 1~2px)
    frame = np.clip(poly_mask(box, 2) - inner, 0, 1)
    frame_col = np.array([34, 38, 44], np.float32)
    o2 = mix(o2, frame_col[None, None, :] * np.ones_like(o2), frame * 0.9)
    o2 = mix(o2, glass, inner)
    # smooth: 링 영역에 σ1.5 + 언샤프 0.3
    sm = gblur(o2, 1.5)
    us = o2 + 0.3 * (o2 - gblur(o2, 2.0))
    zone = soft(poly_mask(box, 6) - poly_mask(box, -3), 1.0)
    o2 = mix(o2, (sm + us) * 0.5, zone * 0.6)
    pm = soft(outer, 1.0)
    o = mix(o, o2, pm)
    o = regrain(o, noise_std(a, (300, 1640, 640, 1700)), pm)
    bx0, by0 = box.min(0).astype(int); bx1, by1 = box.max(0).astype(int)
    compare(a, o, (bx0, by0, bx1, by1), 'P6-05_dest_display', zoom=2)
    o, sm_ = unify_sky(o, 560, name='P6')
    save(o, 'P6_1_fix.png'); compare_full(a, o, 'P6_full')
    return {'P6-01': 'done', 'P6-02': 'done', 'P6-03': 'done', 'P6-04': 'done', 'P6-05': 'done'}


def ridge_y(gray):
    g = gblur(gray, 2)
    d = g[:-3] - g[3:]
    return np.array([1150 + np.argmax(d[1150:1450, x]) + 1.5 for x in range(0, 1440, 8)])


def do_P8():
    a = load('P8_1.png'); ref7 = load('P7d_1.png')
    H, W = a.shape[:2]
    ref = noise_std(a, (300, 300, 1100, 900))
    # 정합: P7d 기준 위로 19px(원본) = 1080 프레임 −14.25px, 가로 −2px
    DX, DY = -2, -19
    M = np.float32([[1, 0, DX], [0, 1, DY]])
    o = cv2.warpAffine(a, M, (W, H), flags=cv2.INTER_NEAREST, borderMode=cv2.BORDER_REFLECT)
    # 아래 19줄·오른쪽 2열: 반사로 채운 뒤 노이즈 재부여
    edge_m = np.zeros((H, W), np.float32); edge_m[H + DY - 2:] = 1; edge_m[:, W + DX - 1:] = 1
    o = regrain(o, noise_std(a, (0, 2380, 1440, 2540)), edge_m)
    d = ridge_y(luma(o)) - ridge_y(luma(ref7))
    print('  P8 ridge diff vs P7d (orig px): median %.1f, |d|<=5 share %.2f' % (np.median(d), np.mean(np.abs(d) <= 5)))
    # 하늘 점 (정합 후 좌표)
    for pid, (px, py) in (('P8-01', (220, 461)), ('P8-02', (868, 271))):
        qx, qy = px + DX, py + DY
        h = np.zeros((H, W), np.float32); cv2.circle(h, (qx, qy), 11, 1, -1)
        fill = tex_fill(o, h, (-36, 0))
        o = mix(o, fill, soft(h, 2.5))
        compare(cv2.warpAffine(a, M, (W, H), flags=cv2.INTER_NEAREST, borderMode=cv2.BORDER_REFLECT),
                o, (qx - 10, qy - 10, qx + 10, qy + 10), pid + '_skydot', zoom=6)
    pre = o.copy()
    # 주황 잔광 −70% (저주파 성분만: 가로등·창문 불빛은 유지) ----------
    lab = cv2.cvtColor(np.clip(o / 255.0, 0, 1).astype(np.float32), cv2.COLOR_RGB2LAB)
    Lc, A, B = lab[..., 0], lab[..., 1], lab[..., 2]
    A_lo, B_lo = gblur(A, 45), gblur(B, 45)
    warm = np.clip(B_lo, 0, None)                    # 노랑~주황 축
    warmA = np.clip(A_lo, 0, None)
    # 잔광 위치 가중: 지평선 주변 (y 900~1700) 넓은 띠
    yy = np.arange(H, dtype=np.float32)[:, None]
    band = np.clip(1 - np.abs(yy - 1290) / 520, 0, 1) ** 0.6
    B2 = B - 0.70 * warm * band
    A2 = A - 0.70 * warmA * band
    lab2 = np.stack([Lc, A2, B2], -1)
    o = cv2.cvtColor(lab2, cv2.COLOR_LAB2RGB) * 255.0
    # 채도 −25%
    Lm = luma(o)[..., None]
    o = Lm + (o - Lm) * 0.75
    # P8-03 왼쪽 주황 잔광: 위 저주파 보정으로 처리(나무·가로등은 클론하지 않고 유지)
    compare(pre, o, (0, 1301, 333, 1368), 'P8-03_orange_glow')
    o, sm = unify_sky(o, 1150, top_frac=0.55, name='P8')
    compare(pre, o, (0, 1050, 1440, 1500), 'P8_horizon_wide')
    save(o, 'P8_1_fix.png'); compare_full(a, o, 'P8_full')
    return {'P8-01': 'done', 'P8-02': 'done', 'P8-03': 'done', 'P8-04': 'done'}


def do_P3():
    a = load('P3_1.png')
    o, sm = unify_sky(a, 720, name='P3')
    save(o, 'P3_1_fix.png'); compare_full(a, o, 'P3_full')
    return {}


def ev05(a):
    lin = to_lin(a) * (2 ** 0.5)
    # 하이라이트 롤오프(0.8 넘는 값만 부드럽게 압축)
    lin = np.where(lin > 0.8, 0.8 + 0.2 * np.tanh((lin - 0.8) / 0.2), lin)
    return to_srgb(lin)


def do_P2clean():
    a = load('P2clean_1.png')
    o = ev05(a)
    save(o, 'P2clean_1_fix.png'); compare_full(a, o, 'P2clean_full')
    return {}


# ---------------------------------------------------------------- P2 기구 (P2c_2 채택본)
P2_ENV = (547, 739, 951, 1149)        # 기낭 bbox
P2_CX = 749
P2_WATER_Y = 1696                      # 수면 시작(물가선)
P2_GROUND_Y = 1662                     # 케이블 지면 고정점
P2_GONDOLA_BOTTOM = 1262               # 곤돌라 아래 끝(케이블 시작)


def p2_matte():
    """P2c_2(+0.5EV)와 P2clean(+0.5EV, 정렬)의 차이로 RGBA 컷아웃을 만든다."""
    I = ev05(load('P2c_2.png'))
    Bs = ev05(load('P2clean_1.png'))
    H, W = I.shape[:2]
    gI = cv2.cvtColor(u8(I), cv2.COLOR_RGB2GRAY).astype(np.float32)
    gB = cv2.cvtColor(u8(Bs), cv2.COLOR_RGB2GRAY).astype(np.float32)
    (dx, dy), _ = cv2.phaseCorrelate(gI[1300:1700], gB[1300:1700])
    best = None
    for sgn in (1, -1):
        M = np.float32([[1, 0, sgn * dx], [0, 1, sgn * dy]])
        Bw = cv2.warpAffine(Bs, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        err = np.abs(Bw - I)[1300:1650, 900:1400].mean()
        if best is None or err < best[0]:
            best = (err, Bw)
    B = best[1]
    x0, y0, x1, y1 = P2_ENV
    cx, cy, rx, ry = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2, (y1 - y0) / 2
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    rr = np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)
    env_core = (rr <= 0.985).astype(np.float32)
    hint = (rr <= 1.0 + 60 / rx).astype(np.float32)            # 기낭 + 빛 번짐 60px
    hint[1050:P2_GONDOLA_BOTTOM + 6, 575:925] = 1               # 매다는 줄 + 곤돌라
    D = I - B
    cable = np.zeros((H, W), np.float32)
    for y in range(P2_GONDOLA_BOTTOM - 8, P2_GROUND_Y + 4):
        seg = luma(D[y:y + 1, P2_CX - 8:P2_CX + 9])[0]
        xc = P2_CX - 8 + int(np.argmax(seg))
        cable[y, xc - 3:xc + 4] = 1
    hint = np.maximum(hint, cable)
    hint = soft(hint, 2.0)
    nf = 6.0                                                    # 노이즈 바닥
    Dp = np.sign(D) * np.clip(np.abs(D) - nf, 0, None)
    ap = np.where(Dp > 0, Dp / np.maximum(255 - B, 1), -Dp / np.maximum(B, 1))
    alpha = np.clip(ap.max(2), 0, 1)
    alpha = np.maximum(alpha, env_core)                         # 기낭 본체는 불투명
    alpha *= hint
    gz = np.zeros((H, W), np.float32); gz[1150:P2_GONDOLA_BOTTOM, 640:860] = 1
    solid = ((luma(I) > 90) & (gz > 0)).astype(np.float32)
    alpha = np.maximum(alpha, cv2.dilate(solid, np.ones((3, 3), np.uint8)) * 0.98)
    alpha = np.clip(alpha, 0, 1)
    a3 = alpha[..., None]
    F = np.where(a3 > 1e-3, (I - (1 - a3) * B) / np.maximum(a3, 1e-3), I)
    F = np.clip(F, 0, 255)
    return I, B, F, alpha, rr


def p2_envelope_color(F, rr):
    """기낭만 #F3E9C6 쪽으로 살짝(40%) 보정. 셰이딩(휘도)은 유지, 곤돌라·줄·케이블 제외."""
    tgt = np.array([0xF3, 0xE9, 0xC6], np.float32)
    env = soft((rr <= 1.0).astype(np.float32), 1.5)
    env[P2_ENV[3] + 2:] = 0
    L = luma(F)[..., None]
    Lt = luma(tgt[None, None, :])[0, 0]
    tinted = L * (tgt / Lt)[None, None, :]
    return mix(F, np.clip(tinted, 0, 255), env * 0.4)


def p2_reflection(H, W, cx, intensity=0.25, seed=5):
    """절차형 수면 반사: #F3E9C6 25%, 폭≈205px, 위→아래 감쇠, 가로 물결 대시, 37/61px 주기 변위."""
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    disp = 6 * np.sin(2 * np.pi * yy / 37.0) + 4 * np.sin(2 * np.pi * yy / 61.0 + 1.3)
    n = rng.standard_normal((H, W)).astype(np.float32)
    n = cv2.GaussianBlur(n, (0, 0), sigmaX=14, sigmaY=1.6)
    n /= n[P2_WATER_Y:].std() + 1e-6
    dash = 1 / (1 + np.exp(-(n - 0.35) * 3.0))
    xw = np.exp(-0.5 * ((xx + disp - cx) / 62.0) ** 2)
    t = np.clip((yy - P2_WATER_Y) / (H - P2_WATER_Y), 0, 1)
    vprof = np.clip((yy - P2_WATER_Y) / 14.0, 0, 1) * (1 - 0.65 * t)
    a = cv2.GaussianBlur(intensity * xw * dash * vprof, (0, 0), 0.8)
    return a, np.array([0xF3, 0xE9, 0xC6], np.float32)


def p2_comp(clean, F, alpha, dy, cable, ref_std, name):
    H, W = clean.shape[:2]
    M = np.float32([[1, 0, 0], [0, 1, dy]])
    Fs = cv2.warpAffine(F, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    As = cv2.warpAffine(alpha, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    out = clean.copy()
    if cable is not None:              # 이동 합성: 곤돌라 아래 ~ 지면 고정점까지 같은 굵기·색으로 다시 긋기
        cF, cA = cable
        for y in range(max(0, P2_GONDOLA_BOTTOM - 4 + dy), P2_GROUND_Y + 1):
            sl = slice(P2_CX - 3, P2_CX + 4)
            out[y, sl] = out[y, sl] * (1 - cA[:, None]) + cF * cA[:, None]
    ra, rc = p2_reflection(H, W, P2_CX)
    out = out + (255 - out) * (ra[..., None] * rc[None, None, :] / 255.0)    # 스크린 합성
    out = regrain(out, ref_std, (ra > 0.01).astype(np.float32))
    out = out * (1 - As[..., None]) + Fs * As[..., None]
    save(out, name)
    return out


def do_P2c():
    I, B, F, alpha, rr = p2_matte()
    F2 = p2_envelope_color(F, rr)
    H, W = I.shape[:2]
    Image.fromarray(np.dstack([u8(F2), u8(alpha * 255)]), 'RGBA').save(os.path.join(HERE, 'P2_balloon_cut.png'))
    clean = ev05(load('P2clean_1.png'))                          # 빈 배경 = P2clean +0.5EV
    save(clean, 'P2c_clean.png')
    rows = []
    for y in range(1400, 1600):
        xc = P2_CX - 8 + int(np.argmax(alpha[y, P2_CX - 8:P2_CX + 9]))
        rows.append((F2[y, xc - 3:xc + 4], alpha[y, xc - 3:xc + 4]))
    cF = np.mean([r[0] for r in rows], 0); cA = np.mean([r[1] for r in rows], 0)
    noc = alpha.copy(); noc[P2_GONDOLA_BOTTOM:] = 0                # 케이블은 따로 다시 긋는다
    ref = noise_std(clean, (900, 1900, 1300, 2400))
    o0 = p2_comp(clean, F2, alpha, 0, None, ref, 'P2c_2_fix.png')
    top_a = int(round(2560 * 0.25))                               # 꼭대기 = 화면 높이 75%(아래에서)
    dy_a = top_a - P2_ENV[1]
    dy_b = dy_a - 520                                             # 1080 프레임 390px = 원본 520px
    oa = p2_comp(clean, F2, noc, dy_a, (cF, cA), ref, 'P2a_fix.png')
    ob = p2_comp(clean, F2, noc, dy_b, (cF, cA), ref, 'P2b_fix.png')
    print('  P2 dy_a %d (top %d), dy_b %d (top %d)' % (dy_a, P2_ENV[1] + dy_a, dy_b, P2_ENV[1] + dy_b))
    orig = load('P2c_2.png')
    compare(orig, o0, (440, 680, 1060, 1300), 'P2c-01_balloon_color')
    compare(orig, o0, (380, 1640, 1120, 2559), 'P2c-02_reflection')
    compare(orig, o0, (700, 1240, 800, 1680), 'P2c-03_cable', zoom=2)
    chk = ((np.indices((H, W)).sum(0) // 16) % 2 * 60 + 60).astype(np.float32)[..., None] * np.ones(3, np.float32)
    over = chk * (1 - alpha[..., None]) + F2 * alpha[..., None]
    s = Image.new('RGB', (620 * 2 + 12, 1100), (40, 40, 40))
    s.paste(Image.fromarray(u8(np.dstack([alpha * 255] * 3)[600:1700, 440:1060])), (0, 0))
    s.paste(Image.fromarray(u8(over[600:1700, 440:1060])), (632, 0))
    s.save(os.path.join(CMP, 'P2c-04_alpha_and_checker.png'))
    s = Image.new('RGB', (540 * 4 + 36, 960), (40, 40, 40))
    for i, im in enumerate((orig, o0, oa, ob)):
        s.paste(Image.fromarray(u8(im)).resize((540, 960), Image.LANCZOS), (i * 552, 0))
    s.save(os.path.join(CMP, 'P2_full_orig_fix_P2a_P2b.png'))
    return {'P2-01': 'done', 'P2-02': 'done', 'P2-03': 'done'}


PLATES = {'P1': do_P1, 'P4b': do_P4b, 'P5c': do_P5c, 'P6': do_P6, 'P8': do_P8,
          'P3': do_P3, 'P2clean': do_P2clean, 'P2c': do_P2c}

if __name__ == '__main__':
    sel = sys.argv[1:] or list(PLATES)
    for k in sel:
        print('==', k)
        st = PLATES[k]()
        print('  status', st)
