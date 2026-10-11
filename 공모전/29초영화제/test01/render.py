# -*- coding: utf-8 -*-
"""무료 시험 1: C07 + C10 해 합성 렌더러 (Kling 없음, K3 대체본 사용).
사용: python render.py [all|C07|C10|K3] [sig|nosig|both] [--frames a,b,c]"""
import os, sys, json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter, map_coordinates

ROOT = os.path.dirname(os.path.abspath(__file__))
_TV = os.environ.get('T1V', '1')
V31 = _TV == '31'
V3 = _TV in ('3', '31')
V2 = _TV in ('2', '3', '31')      # v3는 v2 얼굴 크기·신호 세기 설정을 이어받는다
B = os.path.join(ROOT, {'1': 'build', '2': 'build_v2', '3': 'build_v3', '31': 'build_v3'}[_TV])
SUN_R = 115.0 if V3 else 150.0
FONT = os.path.join(ROOT, '..', 'fonts', 'Galmuri', 'Galmuri11-Bold.ttf')
W, H = 1080, 1920
SS = 2

def hexc(h): h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255.
def s2l(c): return np.where(c <= 0.04045, c / 12.92, ((np.clip(c, 0, None) + 0.055) / 1.055) ** 2.4)
def l2s(c):
    c = np.clip(c, 0, None)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(c, 1 / 2.4) - 0.055)
def luma(a): return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
def screen(a, b): return 1 - (1 - a) * (1 - np.clip(b, 0, 1))
def sstep(x): x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)
def ease_io(x): x = np.clip(x, 0, 1); return np.where(x < 0.5, 4 * x ** 3, 1 - (-2 * x + 2) ** 3 / 2) if isinstance(x, np.ndarray) else (4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2)
def ease_out(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def ease_in(x): x = min(max(x, 0), 1); return x ** 3
def lerp(a, b, t): return a + (b - a) * t

# =========================================================== 공용 자료(워커마다 1회 로드)
G = {}
def init():
    if G: return
    m = json.load(open(os.path.join(B, 'meta.json')))
    G['meta'] = m
    if V2 and not V3: G['colE'] = np.load(os.path.join(B, 'colE.npy'))
    for n in ['P7a', 'P7b', 'H7', 'water', 'lights', 'ridge_out', 'sun_core_rgb', 'sun_core_a', 'sun_corona',
              'moon_rgb', 'moon_a']:
        G[n] = np.load(os.path.join(B, n + '.npy'))
    G['P7a_l'] = s2l(G['P7a']); G['P7b_l'] = s2l(G['P7b'])
    F = np.load(os.path.join(B, 'fields.npz'))
    for k in F.files: G[k] = F[k]
    G['font96'] = ImageFont.truetype(FONT, 96); G['font48'] = ImageFont.truetype(FONT, 48)
    G['osd_base'] = None

def MY0(m): return int(m.get('WATER_TOP', 1320)) - 20

def make_fields():
    """반복 사용 노이즈 필드(시드 고정)를 만든다."""
    init_meta = json.load(open(os.path.join(B, 'meta.json')))
    rng = np.random.default_rng(29)
    yw0 = int(init_meta['BRIDGE_Y']) - 12
    hh = H - yw0
    def nf(shape, sig):
        a = gaussian_filter(rng.normal(0, 1, shape).astype(np.float32), sig, mode='wrap')
        return (a / a.std()).astype(np.float32)
    out = dict(
        yw0=np.array(yw0),
        RIP1=nf((hh, W), (2.2, 16)), RIP2=nf((hh, W), (2.2, 16)), RIP3=nf((hh, W), (4, 30)),
        STR1=nf((hh, W), (1.0, 9)), STR2=nf((hh, W), (1.0, 9)),
        MIST=(0.6 * nf((H - MY0(init_meta), W * 2), (9, 70)) + 0.4 * nf((H - MY0(init_meta), W * 2), (22, 150))),
        SDX1=nf((1000, 1000), 22), SDX2=nf((1000, 1000), 22), SDY1=nf((1000, 1000), 22), SDY2=nf((1000, 1000), 22),
        CDX=nf((1000, 1000), 14), CDY=nf((1000, 1000), 14),
    )
    # 물비늘 반짝임 점
    n = 420
    out['SPK'] = np.stack([rng.normal(0, 1, n), rng.random(n), rng.random(n) * 2 * np.pi,
                           rng.uniform(0.18, 0.42, n), rng.uniform(0.5, 1.0, n)], 1).astype(np.float32)
    # 코로나 플리커: 주기 0.7~1.3s(17~31f) 무작위 사인 3개
    out['FLK'] = np.stack([rng.uniform(17, 31, 3), rng.uniform(0, 2 * np.pi, 3), rng.uniform(0.6, 1.0, 3)], 1).astype(np.float32)
    np.savez(os.path.join(B, 'fields.npz'), **out)

# =========================================================== 얼굴 리그 (PIL 벡터, 4배 그려서 축소)
if V2:   # 얼굴 크기 1.4배(D 기준 확대), 위치 간격은 약 1.15배
    FS = 1.4
    FACE_SUN = dict(eye_dx=0.152, eye_dy=-0.018, eye_r=0.056, mouth_y=0.069, mouth_w=0.114, blush=(0.19, 0.05))
    FACE_MOON = dict(eye_dx=0.163, eye_dy=-0.048, eye_w=0.055, eye_h=0.0625, mouth_y=0.107, mouth_w=0.14, e5=(0.20, 0.040, 0.046))
else:
    FS = 1.0
    FACE_SUN = dict(eye_dx=0.185, eye_dy=-0.022, eye_r=0.056, mouth_y=0.084, mouth_w=0.114, blush=(0.235, 0.062))
    FACE_MOON = dict(eye_dx=0.198, eye_dy=-0.058, eye_w=0.055, eye_h=0.0625, mouth_y=0.13, mouth_w=0.14, e5=(0.245, 0.030, 0.034))

class Pen:
    """D(지름) 단위 좌표로 그리는 4배 슈퍼샘플 캔버스. 원점 = 원 중심."""
    def __init__(self, D, half, k=4):
        self.D = D; self.k = k; self.half = half
        self.N = int(2 * half * k)
        self.img = Image.new('L', (self.N, self.N), 0)
        self.d = ImageDraw.Draw(self.img)
    def p(self, x, y): return ((x * self.D + self.half) * self.k, (y * self.D + self.half) * self.k)
    def s(self, v): return v * self.D * self.k
    def ellipse(self, cx, cy, rx, ry, fill=255):
        x0, y0 = self.p(cx - rx, cy - ry); x1, y1 = self.p(cx + rx, cy + ry)
        self.d.ellipse([x0, y0, x1, y1], fill=fill)
    def poly(self, pts, fill=255): self.d.polygon([self.p(*q) for q in pts], fill=fill)
    def line(self, pts, w, fill=255):
        P = [self.p(*q) for q in pts]; ww = max(1, int(round(self.s(w))))
        self.d.line(P, fill=fill, width=ww, joint='curve')
        r = ww / 2
        for q in (P[0], P[-1]): self.d.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=fill)
    def rect_clear(self, pts): self.d.polygon([self.p(*q) for q in pts], fill=0)
    def get(self):
        a = np.asarray(self.img.resize((self.N // self.k, self.N // self.k), Image.BOX)).astype(np.float32) / 255.
        return a

def bez(p0, p1, p2, p3, n=24):
    t = np.linspace(0, 1, n)[:, None]
    P = (1 - t) ** 3 * np.array(p0) + 3 * (1 - t) ** 2 * t * np.array(p1) + 3 * (1 - t) * t ** 2 * np.array(p2) + t ** 3 * np.array(p3)
    return [tuple(q) for q in P]

def arc_pts(cx, cy, w, h, up=True, n=20):
    """∩(up=True) 또는 ∪ 모양 호."""
    t = np.linspace(-1, 1, n)
    ys = cy + (-1 if up else 1) * h * (1 - t ** 2)
    return list(zip(cx + t * w / 2, ys))

def eye_disc(pen, cx, cy, r, o, lid_slope=0.0, gaze=(0, 0), ry=None):
    """둥근 눈 + 윗눈꺼풀. o=열림(0~1). 반환: (눈 마스크, 캐치라이트 마스크 좌표 정보)"""
    ry = ry or r
    gx, gy = gaze
    ex, ey = cx + gx * r * 0.42, cy + gy * r * 0.30
    if o < 0.12:   # 감은 눈: 아래로 처진 짧은 곡선
        pen.line(arc_pts(cx, cy + ry * 0.15, r * 2.1, ry * 0.35, up=False), r * 0.36)
        return None
    pen.ellipse(ex, ey, r, ry)
    if o < 0.999:
        lid = cy - ry + (1 - o) * 2 * ry      # 눈꺼풀 선 y (중심 기준 좌우 기울기)
        L, R = cx - r * 1.6, cx + r * 1.6
        pen.rect_clear([(L, cy - 3 * ry), (R, cy - 3 * ry), (R, lid + lid_slope * r * 1.6), (L, lid - lid_slope * r * 1.6)])
        pen.line([(cx - r * 1.12, lid - lid_slope * r * 1.12), (cx + r * 1.12, lid + lid_slope * r * 1.12)], r * 0.30)
    return (ex, ey)

def sun_face(st, D=None):
    D = D or (460 if V3 else 600) * FS
    """해 얼굴: normal 합성용 RGBA(스프라이트 2배 공간, 크기 1000). st=표정 상태 dict."""
    half = 250   # 얼굴 영역 ±250 스프라이트 px (=±0.417D)
    f = FACE_SUN
    dark = Pen(D, half); hi = Pen(D, half); tongue = Pen(D, half); blush = Pen(D, half)
    e = st['expr']; o = st.get('o', 1.0); gaze = st.get('gaze', (0, 0)); mo = st.get('mouth', 1.0)
    cl = []
    for side in (-1, 1):
        cx, cy, r = side * f['eye_dx'], f['eye_dy'], f['eye_r']
        if e == 'S1' or (e == 'S0' and st.get('happy', False)):
            dark.line(arc_pts(cx, cy + r * 0.25, r * 2.3, r * 0.95, up=True), r * 0.40)
        elif e == 'S5':
            c = eye_disc(dark, cx, cy, r, o, lid_slope=-0.10 * side, gaze=(0, 0.3))
            if c: cl.append((c, r))
        elif e == 'S4':
            c = eye_disc(dark, cx, cy, r, o, lid_slope=-0.24 * side, gaze=gaze)
            if c: cl.append((c, r))
        else:   # S0
            c = eye_disc(dark, cx, cy, r, o, gaze=gaze)
            if c: cl.append((c, r))
    for (ex, ey), r in cl:
        hi.ellipse(ex + r * 0.32, ey - r * 0.36, r * 0.30, r * 0.30)
        hi.ellipse(ex - r * 0.34, ey + r * 0.38, r * 0.12, r * 0.12, fill=170)
    my, mw = f['mouth_y'], f['mouth_w']
    if e == 'S0':
        dark.line(arc_pts(0, my - 0.01, mw, 0.028, up=False), 0.016)
    elif e == 'S5':   # 하품하는 작은 입: 세로 타원, mo로 크기
        ry = 0.022 + 0.030 * mo; rx = 0.020 + 0.010 * mo
        dark.ellipse(0, my + 0.01, rx, ry)
        tongue.ellipse(0, my + 0.01 + ry * 0.45, rx * 0.70, ry * 0.45)
    elif e == 'S1':   # 크게 벌려 부르는 입: D자(윗변 약간 휘고 아래 반원)
        w = 0.15 * (0.85 + 0.15 * mo); h = 0.035 + 0.075 * mo
        pts = [(x, my - 0.012 + 0.010 * (1 - (2 * x / w) ** 2)) for x in np.linspace(-w / 2, w / 2, 16)]
        pts += [(w / 2 * math.cos(a), my - 0.012 + h * math.sin(a)) for a in np.linspace(0, math.pi, 24)]
        dark.poly(pts)
        tongue.ellipse(0, my - 0.012 + h * 0.78, w * 0.26, h * 0.30)
    elif e == 'S4':   # 음흉한 웃음: 오른쪽이 올라간 비대칭 초승달
        k = st.get('grin', 1.0)
        top = bez((-0.065, my + 0.010), (-0.02, my + 0.035), (0.03, my + 0.030), (0.075, my - 0.022 * k))
        bot = bez((0.075, my - 0.022 * k), (0.04, my + 0.055 + 0.01 * k), (-0.02, my + 0.060), (-0.065, my + 0.010))
        dark.poly(top + bot)
        dark.line([(0.075, my - 0.022 * k), (0.088, my - 0.036 * k)], 0.010)
    b = 0.0
    for side in (-1, 1):
        blush.ellipse(side * f['blush'][0], f['blush'][1], 0.050, 0.028)
    A = dark.get(); Hh = hi.get(); T = tongue.get(); Bl = gaussian_filter(blush.get(), 7)
    T = T * A
    # 눈 광택: 아래쪽이 약간 밝은 갈색
    N = A.shape[0]
    yy = (np.arange(N)[:, None] - N / 2) / D
    base = hexc('#3A1E0A')[None, None] * (1 + 0.0 * yy[..., None])
    rgb = base * np.ones((N, N, 1), np.float32)
    rgb = rgb * (1 - T[..., None]) + hexc('#D9603E')[None, None] * T[..., None]
    # 합성: 볼터치 → 눈/입 → 하이라이트
    out_rgb = hexc('#FF8F6A')[None, None] * np.ones((N, N, 1), np.float32)
    out_a = Bl * 0.28
    out_rgb = out_rgb * (1 - A[..., None]) + rgb * A[..., None]; out_a = out_a * (1 - A) + A
    Hh = Hh * A if True else Hh
    out_rgb = out_rgb * (1 - Hh[..., None]) + Hh[..., None]; out_a = np.maximum(out_a, Hh)
    return out_rgb.astype(np.float32), out_a.astype(np.float32), half

def moon_face(st, D=None):
    """달 얼굴: multiply 70% 맵 + 캐치라이트(normal). 반환 (mul_mask, catch_mask, half)"""
    D = D or 400 * FS
    half = 170 if V2 else 130
    f = FACE_MOON
    dk = Pen(D, half); hi = Pen(D, half)
    e = st['expr']; o = st.get('o', 1.0); gaze = st.get('gaze', (0, 0)); ph = st.get('phase', 0)
    my, mw = f['mouth_y'], f['mouth_w']
    for side in (-1, 1):
        cx, cy = side * f['eye_dx'], f['eye_dy']
        if e == 'E6':
            c = eye_disc(dk, cx, cy, f['eye_w'], o, lid_slope=-0.12 * side, gaze=gaze, ry=f['eye_h'])
            if c: hi.ellipse(c[0] + f['eye_w'] * 0.35, c[1] + f['eye_h'] * 0.05, f['eye_w'] * 0.22, f['eye_w'] * 0.22)
        elif e == 'E5':
            e5 = f['e5']; dk.ellipse(side * e5[0] + gaze[0] * 0.01, cy + 0.01, e5[1], e5[2])
        elif e == 'E2':
            r = 0.078
            if o < 0.12:
                dk.line(arc_pts(cx, cy + 0.01, r * 2, r * 0.3, up=False), 0.02)
            else:
                dk.ellipse(cx, cy, r, r * o)
                hi.ellipse(cx + r * 0.36, cy - r * 0.36 * o, r * 0.24, r * 0.24 * o)
        elif e == 'E4':
            dk.line(arc_pts(cx, cy + 0.02, 0.13, 0.058, up=True), 0.026)
        else:  # M0
            c = eye_disc(dk, cx, cy, f['eye_w'], o, gaze=gaze, ry=f['eye_h'])
    if e == 'E6':   # 한쪽 입꼬리만 올라간 미소
        dk.line(bez((-0.055, my + 0.005), (-0.02, my + 0.03), (0.035, my + 0.025), (0.072, my - 0.018)), 0.018)
    elif e == 'E5':  # 꼬불꼬불 지그재그
        xs = np.linspace(-0.08, 0.08, 9)
        pts = [(x, my + 0.004 + (0.016 if (i + ph) % 2 else -0.012)) for i, x in enumerate(xs)]
        dk.line(pts, 0.016)
    elif e == 'E2':
        dk.ellipse(0, my + 0.025, 0.030 * st.get('mouth', 1), 0.038 * st.get('mouth', 1))
    elif e == 'E4':
        w, h = 0.16, 0.09
        pts = [(x, my - 0.025) for x in np.linspace(-w / 2, w / 2, 10)]
        pts += [(w / 2 * math.cos(a), my - 0.025 + h * math.sin(a)) for a in np.linspace(0, math.pi, 24)]
        dk.poly(pts)
    else:
        dk.line(arc_pts(0, my, mw, 0.03, up=False), 0.016)
    M = gaussian_filter(dk.get(), 0.9); C = hi.get()
    return M.astype(np.float32), C.astype(np.float32), half

# =========================================================== 해 스프라이트(표면 움직임 + 얼굴)
def sun_sprite(t, st):
    """t: 전역 시간(프레임). 반환 premult RGB, alpha, corona RGB (1000x1000, 2배 공간)"""
    rgb = G['sun_core_rgb']; a = G['sun_core_a']; cor = G['sun_corona']
    N = rgb.shape[0]
    ph = 2 * np.pi * t / 48.0          # 표면 변위 주기 48f
    amp = 3.0 * SS                      # 3px(출력) = 6px(스프라이트)
    dx = amp * (G['SDX1'] * np.cos(ph) + G['SDX2'] * np.sin(ph))
    dy = amp * (G['SDY1'] * np.cos(ph) + G['SDY2'] * np.sin(ph))
    yy, xx = np.mgrid[0:N, 0:N].astype(np.float32)
    # 가장자리 원형은 유지하고 내부 질감만 흐르게: 반경 0.97 바깥은 변위 감쇠
    C = N / 2 - 0.5; rr = np.hypot(xx - C, yy - C) / 300.
    k = np.clip((1.0 - rr) / 0.06, 0, 1)
    core = np.stack([map_coordinates(rgb[..., c], [yy + dy * k, xx + dx * k], order=1, mode='nearest') for c in range(3)], -1)
    # 코로나: 더 큰 변위(불꽃 일렁임) + 밝기 플리커 ±10%
    ca = 5.0 * SS
    cdx = ca * (G['CDX'] * np.cos(ph * 1.7) + G['SDX2'] * np.sin(ph * 1.7)) * np.clip((rr - 0.95) / 0.1, 0, 1)
    cdy = ca * (G['CDY'] * np.cos(ph * 1.7) + G['SDY1'] * np.sin(ph * 1.7)) * np.clip((rr - 0.95) / 0.1, 0, 1)
    corona = np.stack([map_coordinates(cor[..., c], [yy + cdy - 1.5 * SS * np.sin(ph * 2), xx + cdx], order=1, mode='constant') for c in range(3)], -1)
    flk = G['FLK']; fl = sum(w_ * np.sin(2 * np.pi * t / P + p) for P, p, w_ in flk) / flk[:, 2].sum()
    corona = corona * (1 + 0.10 * fl)
    # 얼굴(normal)
    frgb, fa, half = sun_face(st)
    s0 = int(C - half + 0.5); sl = (slice(s0, s0 + frgb.shape[0]), slice(s0, s0 + frgb.shape[1]))
    fa = fa * a[sl]
    core[sl] = core[sl] * (1 - fa[..., None]) + frgb * fa[..., None]
    core = gaussian_filter(core, (0.7, 0.7, 0)); aa = gaussian_filter(a, 0.7)
    return core * aa[..., None], aa, gaussian_filter(corona, (0.7, 0.7, 0))

def moon_sprite(st, cover, sky_col, rim_v, rim_dir):
    rgb = G['moon_rgb'].copy(); a = G['moon_a']
    N = rgb.shape[0]; C = N / 2 - 0.5; R = 200.0
    yy, xx = np.mgrid[0:N, 0:N].astype(np.float32)
    d = np.hypot(xx - C, yy - C)
    # 얼굴 multiply 70% (+ 2f 디졸브 지원)
    def facemaps(s):
        M, Cc, half = moon_face(s); return M, Cc, half
    M, Cc, half = facemaps(st)
    if 'mix' in st:   # 표정 디졸브
        M2, C2, _ = facemaps(st['mix'][0]); k = st['mix'][1]
        M = M * (1 - k) + M2 * k; Cc = Cc * (1 - k) + C2 * k
    s0 = int(C - half + 0.5); sl = (slice(s0, s0 + M.shape[0]), slice(s0, s0 + M.shape[1]))
    eyec = hexc('#5A5A66')
    mul = 1 - 0.70 * M[..., None] * (1 - eyec[None, None])
    rgb[sl] = rgb[sl] * mul
    rgb[sl] = rgb[sl] * (1 - 0.55 * Cc[..., None]) + 0.92 * 0.55 * Cc[..., None]
    # 라이트랩 8px(출력) 25%
    ew = np.clip(1 - (R - d) / (8 * SS), 0, 1) ** 1.5 * (d < R)
    rgb = rgb * (1 - 0.25 * ew[..., None]) + sky_col[None, None] * 0.25 * ew[..., None]
    # 웜 림 #FFC24A 10% × v (해 쪽)
    if rim_v > 0:
        ang = np.arctan2(yy - C, xx - C)
        dirw = np.clip(np.cos(ang - rim_dir), 0, 1) ** 1.5
        rw = np.clip(1 - (R - d) / (12 * SS), 0, 1) * (d < R) * dirw
        k = ((0.22 if V2 else 0.10) * rim_v * rw)[..., None]
        rgb = rgb * (1 - k) + hexc('#FFC24A')[None, None] * k
    # 대기 덮기
    rgb = rgb * (1 - cover) + sky_col[None, None] * cover
    rgb = gaussian_filter(rgb, (0.6, 0.6, 0)); aa = gaussian_filter(a, 0.6)
    return rgb * aa[..., None], aa

def place(chs, cx, cy, sx, sy, rot, box):
    """스프라이트(2배 공간) 채널 목록을 프레임 영역 box로 변환 샘플."""
    x0, y0, x1, y1 = box
    N = chs[0].shape[0]; C = N / 2 - 0.5
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    dx = xx - cx; dy = yy - cy
    c, s = math.cos(rot), math.sin(rot)
    u = (c * dx + s * dy) / sx; v = (-s * dx + c * dy) / sy
    qx = C + u * SS; qy = C + v * SS
    return [map_coordinates(ch, [qy, qx], order=1, mode='constant', cval=0.0) for ch in chs]

def clipbox(cx, cy, half):
    return (max(0, int(cx - half)), max(0, int(cy - half)), min(W, int(cx + half) + 1), min(H, int(cy + half) + 1))

# =========================================================== v3.1 비주기 물결(37/61/97f, 최소공배수 218,929f)
PERIODS = (37.0, 61.0, 97.0)
def nonperiodic(prefix, t, weights, off=0, n=None):
    acc = None; norm = math.sqrt(sum(w * w for w in weights))
    for i, (Pd, w) in enumerate(zip(PERIODS, weights)):
        ph = 2 * np.pi * t / Pd + 1.3 * i
        A_ = G[f'{prefix}A{i}']; B_ = G[f'{prefix}B{i}']
        if n is not None: A_ = A_[off:off + n]; B_ = B_[off:off + n]
        term = w * (A_ * np.cos(ph) + B_ * np.sin(ph))
        acc = term if acc is None else acc + term
    return acc / norm

# =========================================================== 플레이트(K3 대체본)
def plate(mix, trip, ev=0.0, mist_t=None, kcol=0.0, warm=0.0):
    """mix: P7a(0)→P7b(1). trip: 물결 시간(프레임). ev: 추가 노출(차가운 그레이드).
    kcol: (v2) 70% 줄여 둔 기존 물빛 기둥을 되살리는 양(0~0.7). warm: 되살린 기둥의 금빛 착색 비율."""
    lin = G['P7a_l'] * (1 - mix) + G['P7b_l'] * mix
    img = l2s(lin)
    if V2 and not V3 and kcol > 0:
        E = G['colE'] * (kcol * (0.45 + 0.55 * mix))
        if warm > 0:
            Ey = luma(E)[..., None]
            E = E * (1 - warm) + Ey * np.array([1.15, 0.92, 0.62], np.float32) * warm
        img = np.clip(img + E, 0, 1)
    # 물결 변위(다리 아래 물만, 원근으로 아래쪽이 크다)
    yw0 = int(G['yw0']); hh = H - yw0
    ph = 2 * np.pi * trip / 48.0
    fy = np.arange(hh, dtype=np.float32)[:, None] / hh
    A = 2.6 * fy ** 1.2 * G['water'][yw0:]
    if V31:
        dxf = A * 1.25 * nonperiodic('R', trip, (0.75, 0.55, 0.45))
        dyf = 0.35 * A * 1.25 * nonperiodic('R', trip + 17.0, (0.55, 0.75, 0.45))
    else:
        dxf = A * (G['RIP1'] * np.cos(ph) + G['RIP2'] * np.sin(ph) + 0.6 * G['RIP3'] * np.sin(ph * 0.5 + 1.0))
        dyf = 0.35 * A * (G['RIP2'] * np.cos(ph) - G['RIP1'] * np.sin(ph))
    yy, xx = np.mgrid[yw0:H, 0:W].astype(np.float32)
    sub = img[yw0:]
    img[yw0:] = np.stack([map_coordinates(sub[..., c], [yy - yw0 + dyf, xx + dxf], order=1, mode='nearest') for c in range(3)], -1)
    # 물안개 드리프트(신호와 무관, 기본 차가운 안개 6%)
    mt = trip if mist_t is None else mist_t
    img = screen(img, mist_layer(mt)[..., None] * 0.06 * np.array([0.80, 0.86, 0.95]))
    if ev != 0.0:
        lin = s2l(img)
        k = 2 ** ev
        gains = np.array([1 - 0.16 * (-ev / 2.5), 1 - 0.05 * (-ev / 2.5), 1 + 0.10 * (-ev / 2.5)])
        dark = lin * k * gains
        L = G['lights'][..., None]
        lin = dark * (1 - L) + lin * L
        img = l2s(lin)
    return np.clip(img, 0, 1).astype(np.float32)

_mist_cache = {}
def mist_layer(t):
    """물 위 안개 밀도(0~1), 다리 아래~중간 물 영역, 수평 드리프트."""
    key = round(float(t), 2)
    if key in _mist_cache: return _mist_cache[key]
    M = G['MIST']; off = (0.9 * t) % W
    i0 = int(off); fr = off - i0
    win = M[:, i0:i0 + W] * (1 - fr) + M[:, i0 + 1:i0 + 1 + W] * fr
    full = np.zeros((H, W), np.float32)
    y0 = MY0(G['meta'])
    fy = (np.arange(y0, H)[:, None] - G['meta']['BRIDGE_Y'])
    band = np.exp(-((fy - 140) / 170.) ** 2) + 0.35 * np.exp(-((fy - 380) / 120.) ** 2)
    if '_wsoft' not in G: G['_wsoft'] = gaussian_filter(G['water'], 22)
    full[y0:] = np.clip(win * 0.5 + 0.35, 0, 1) ** 1.6 * band * G['_wsoft'][y0:]
    _mist_cache.clear(); _mist_cache[key] = full
    return full

# =========================================================== 신호 v
def signal_glitter(img, v, t):
    """① 해 아래 물비늘 기둥 + 절차형 반짝임 점."""
    if v <= 0.002: return img
    sx = G['meta']['SUN_X']; yw0 = int(G['yw0'])
    hh = H - yw0
    ys = np.arange(yw0, H, dtype=np.float32)[:, None]; xs = np.arange(W, dtype=np.float32)[None]
    depth = np.clip((ys - yw0) / hh, 0, 1)
    sig = 10 + 55 * depth ** 1.1
    col = np.exp(-((xs - sx) / sig) ** 2)
    ph = 2 * np.pi * t / 24.0
    st = G['STR1'] * np.cos(ph) + G['STR2'] * np.sin(ph)
    streak = np.clip(st * 0.55 + 0.15, 0, 1.5) ** 1.5
    wat = G['water'][yw0:]
    soft = col * (0.20 + 0.80 * streak) * wat * (0.55 + 0.45 * depth)
    lay = np.zeros((hh, W, 3), np.float32)
    lay += soft[..., None] * hexc('#FFC27A')[None, None] * 0.85
    # 반짝임 점
    S = G['SPK']; acc = np.zeros((hh, W), np.float32)
    py = yw0 + (S[:, 1] ** 0.8) * hh
    psig = 10 + 55 * np.clip((py - yw0) / hh, 0, 1) ** 1.1
    px = sx + S[:, 0] * psig * 0.9
    tw = np.clip(np.sin(2 * np.pi * t * S[:, 3] / 2.0 + S[:, 2]), 0, 1) ** 6 * S[:, 4]
    ok = (px >= 1) & (px < W - 1) & (py >= yw0) & (py < H - 1)
    iy = (py[ok] - yw0).astype(int); ix = px[ok].astype(int)
    np.add.at(acc, (iy, ix), tw[ok] * 9.0)
    acc = gaussian_filter(acc, (0.8, 2.2)) * wat
    lay += np.clip(acc, 0, 1.5)[..., None] * hexc('#FFF2D6')[None, None]
    out = img.copy()
    out[yw0:] = screen(out[yw0:], lay * v)
    return out

def horizon_glow(img, v):
    """② 지평선 글로우 +0.3EV × v"""
    if v <= 0.002: return img
    yy, xx = G['_yx'] if '_yx' in G else G.setdefault('_yx', np.mgrid[0:H, 0:W].astype(np.float32))
    sx = G['meta']['SUN_X']; ry = G['meta']['RIDGE_Y']
    dy = yy - ry
    m = np.exp(-((xx - sx) / 420.) ** 2 - (np.where(dy < 0, dy / 330., dy / 110.)) ** 2) * (1 - 0.5 * G['H7'])
    lin = s2l(img) * (2 ** ((0.5 if V2 else 0.3) * v * m))[..., None]
    return l2s(lin).astype(np.float32)

def mist_backlight(img, v, t):
    """③ 물안개 역광 screen 15% × v"""
    if v <= 0.002: return img
    M = mist_layer(t)
    xx = np.arange(W, dtype=np.float32)[None]
    wb = 0.45 + 0.55 * np.exp(-((xx - G['meta']['SUN_X']) / 380.) ** 2)
    k = np.clip(M * wb * 2.2, 0, 1)
    return screen(img, k[..., None] * hexc('#F6B98A')[None, None] * 0.15 * v)

# =========================================================== OSD
PX0, PY0, PAD = 60, 270, 40          # 패널 x 60–460, y 270–460
def osd_static(inv=False):
    key = 'osd_inv' if inv else 'osd'
    if key in G: return G[key]
    bg = hexc('#B8D88B'); fg = hexc('#1E2A14')
    if inv: bg, fg = fg, bg
    w, h = 400 + 2 * PAD, 190 + 2 * PAD
    big = 4
    def rr(x0, y0, x1, y1, rad):
        m = Image.new('L', (w * big, h * big), 0)
        ImageDraw.Draw(m).rounded_rectangle([x0 * big, y0 * big, x1 * big - 1, y1 * big - 1], radius=rad * big, fill=255)
        return np.asarray(m.resize((w, h), Image.BOX)).astype(np.float32) / 255.
    m = rr(PAD, PAD, PAD + 400, PAD + 190, 14)
    inner = rr(PAD + 6, PAD + 6, PAD + 394, PAD + 184, 9)
    rgb = np.zeros((h, w, 3), np.float32); rgb[:] = hexc('#20242B')
    shade = gaussian_filter(inner, 2.0)                 # 안쪽 그림자 2px
    lcd = bg[None, None] * (0.80 + 0.20 * shade[..., None])
    rgb = rgb * (1 - inner[..., None]) + lcd * inner[..., None]
    dots = np.zeros((h, w), np.float32)                 # 꺼진 도트 6%
    def grid(ya, yb, p):
        for yy_ in range(ya, yb, p):
            for xx_ in range(72, 448, p):
                dots[yy_ - PY0 + PAD:yy_ - PY0 + PAD + p - 1, xx_ - PX0 + PAD:xx_ - PX0 + PAD + p - 1] = 1
    grid(300, 396, 8); grid(404, 452, 4)
    dots *= inner
    rgb = rgb * (1 - 0.06 * dots[..., None]) + fg[None, None] * 0.06 * dots[..., None]
    glow = gaussian_filter(m, 12) * (1 - m)
    G[key] = (rgb, m, glow, fg)
    return G[key]

def text_mask(s, font, cells, x, base, w, h):
    """안티앨리어싱 없이 칸 고정 배치(패널 로컬 좌표). 반환 마스크(h,w)"""
    img = Image.new('1', (w, h), 0); d = ImageDraw.Draw(img); d.fontmode = '1'
    cx = x
    for ch, cw in zip(s, cells):
        if ch != ' ':
            bb = font.getmask(ch).getbbox()
            ink = (bb[2] - bb[0]) if bb else cw
            off = int(round(((cw - ink) / 2 - (bb[0] if bb else 0)) / 8.0)) * 8
            d.text((cx + off - PX0 + PAD, base - PY0 + PAD), ch, font=font, fill=1, anchor='ls')
        cx += cw
    return np.asarray(img).astype(np.float32)

def draw_osd(frame, st, rng):
    rgb, m, glow, fg = osd_static(st.get('inv', False))
    h, w = m.shape
    layer = rgb.copy()
    if st.get('digits', True):
        t = st['time']
        if not st.get('colon', True): t = t[:2] + ' ' + t[3:]
        tm = text_mask(t, G['font96'], [64, 64, 32, 64, 64], 84, 386, w, h)
        layer = layer * (1 - tm[..., None]) + fg[None, None] * tm[..., None]
    lab = st.get('label', '')
    if lab:
        cells = [48 if c != ' ' else 24 for c in lab]
        lm = text_mask(lab, G['font48'], cells, 84, 444, w, h)
        layer = layer * (1 - lm[..., None]) + fg[None, None] * lm[..., None]
    if st.get('glitch'):
        nz = (rng.random(((452 - 404) // 4, (448 - 84) // 4)) > 0.55).astype(np.float32)
        nz = np.kron(nz, np.ones((4, 4), np.float32))
        ya, xa = 404 - PY0 + PAD, 84 - PX0 + PAD
        sub = layer[ya:ya + nz.shape[0], xa:xa + nz.shape[1]]
        sub[:] = sub * (1 - nz[..., None]) + fg[None, None] * nz[..., None]
    if st.get('ff'):
        tri = Image.new('L', (w * 4, h * 4), 0); d = ImageDraw.Draw(tri)
        bx, by = (PAD - PX0) * 4, (PAD - PY0) * 4
        tw_, th_, x_s, y_c = (36, 44, 378, 304) if V3 else (20, 24, 400, 304)
        for x_a in (x_s, x_s + tw_):
            d.polygon([(bx + x_a * 4, by + y_c * 4), (bx + (x_a + tw_) * 4, by + (y_c - th_ / 2) * 4), (bx + (x_a + tw_) * 4, by + (y_c + th_ / 2) * 4)], fill=255)
        tri = np.asarray(tri.resize((w, h), Image.BOX)).astype(np.float32) / 255.
        layer = layer * (1 - tri[..., None]) + fg[None, None] * tri[..., None]
    sx, sy = st.get('shake', (0, 0))
    x0, y0 = PX0 - PAD + sx, PY0 - PAD + sy
    reg = frame[y0:y0 + h, x0:x0 + w]
    reg[:] = screen(reg, glow[..., None] * 0.20 * hexc('#B8D88B')[None, None])
    reg[:] = reg * (1 - m[..., None]) + layer * m[..., None]
    return frame

# =========================================================== VHS
def vhs(img, t, rng, strength=1.0, rewind=True):
    out = img.copy()
    # 프레임 세로 지터 ±1~2px
    jy = int(rng.integers(-2, 3)) if strength > 0.5 else 0
    if jy: out = np.roll(out, jy, 0)
    # 행별 수평 지터
    rows = gaussian_filter(rng.normal(0, 1, H), 2) * 1.6 * strength
    # 트래킹 띠: 되감기 동안 아래→위로 흐름
    band_y = (H + 200) - ((t * 61) % (H + 400))
    yy = np.arange(H, dtype=np.float32)
    band = np.exp(-((yy - band_y) / 55.) ** 2) * strength
    band2 = np.exp(-((yy - ((band_y + 900) % (H + 400) - 200)) / 25.) ** 2) * 0.6 * strength
    bands = np.clip(band + band2, 0, 1)
    rows = rows + bands * rng.normal(0, 1, H) * 14
    # 수평 지터 + 색수차 3px
    R = _shift_rows(out[..., 0], rows + 3 * strength); Bc = _shift_rows(out[..., 2], rows - 3 * strength); Gc = _shift_rows(out[..., 1], rows)
    o2 = np.stack([R, Gc, Bc], -1)
    # 색 번짐(수평)
    Yo = luma(o2)[..., None]
    chroma = gaussian_filter(o2 - Yo, (0, 3.0, 0))
    o2 = Yo + chroma * 0.9
    # 띠 안의 밝기 노이즈·흰 줄
    nz = rng.random((H, W)).astype(np.float32)
    streak = (nz > 0.985).astype(np.float32) * bands[:, None]
    streak = gaussian_filter(streak, (0.5, 6))
    o2 = o2 + (streak * 1.4 + (nz - 0.5) * 0.10 * bands[:, None])[..., None]
    # 주사선 8%
    o2[1::2] *= (1 - 0.08 * strength)
    # 헤드 스위칭 노이즈(아래 14px)
    hs = 14
    o2[-hs:] = np.roll(o2[-hs:], int(rng.integers(8, 24)), 1) * 0.85 + rng.random((hs, W, 1)).astype(np.float32) * 0.12
    # 검정 띄움 + 약간 탈채도
    Yo = luma(o2)[..., None]
    o2 = Yo + (o2 - Yo) * (1 - 0.12 * strength)
    o2 = o2 * (1 - 0.04 * strength) + 0.03 * strength
    return np.clip(o2, 0, 1).astype(np.float32)

def _shift_rows(ch, shifts):
    """행마다 수평 이동(선형 보간)."""
    Hh, Ww = ch.shape
    xs = np.arange(Ww, dtype=np.float32)[None] - shifts[:, None]
    x0 = np.floor(xs).astype(int); fr = xs - x0
    x0c = np.clip(x0, 0, Ww - 1); x1c = np.clip(x0 + 1, 0, Ww - 1)
    r = np.arange(Hh)[:, None]
    return ch[r, x0c] * (1 - fr) + ch[r, x1c] * fr

# =========================================================== 타임라인
def hm(minutes):
    m = int(round(minutes)) % (24 * 60); return f'{m // 60:02d}:{m % 60:02d}'

def sun_state_C07(f, t):
    """C07 로컬 f(0~95). 반환 위치/변형/표정."""
    ry = G['meta']['RIDGE_Y']; sx = G['meta']['SUN_X']
    y_hid = ry + (185 if V3 else 240); y_up = ry - (58 if V3 else 75 if V2 else 45)
    flo_y = 4 * math.sin(2 * math.pi * t / 58.0); flo_r = math.radians(1.5) * math.sin(2 * math.pi * t / 77.0)
    if f < 6: cy = y_hid
    elif f < 48:
        u = (f - 6) / 41.0
        cy = lerp(y_hid, y_up, ease_io(u) if u < 1 else 1)
    else: cy = y_up
    k_float = sstep((f - 30) / 18.0)
    cy += flo_y * k_float; rot = flo_r * k_float
    sxk = syk = 1.0
    if 48 <= f < 58:   # 홉: 3f 상승 -24 → 5f 복귀 → 2f 스쿼시
        g = f - 48
        if g < 3: cy += -24 * ease_out((g + 1) / 3.0)
        elif g < 8: cy += -24 * (1 - ease_in((g - 2) / 5.0))
        else:
            sq = [(1.08, 0.92), (1.03, 0.97)][g - 8]; sxk, syk = sq
            cy += SUN_R * (1 - syk)
    # 표정
    if f < 48:
        o = 0.38; mo = 0.35
        if 18 <= f < 24: o = lerp(0.38, 0.04, sstep((f - 18) / 3.0)) if f < 21 else lerp(0.04, 0.38, sstep((f - 21) / 3.0))
        if 26 <= f < 44:   # 하품
            u = (f - 26) / 18.0; mo = 0.35 + 0.65 * math.sin(math.pi * u); o = 0.38 - 0.30 * math.sin(math.pi * u)
        st = dict(expr='S5', o=o, mouth=mo)
    elif f < 89:
        mo = 1.0
        if 53 <= f < 69: mo = 1.0 if ((f - 53) // 4) % 2 == 0 else 0.45     # 교-대-요~
        st = dict(expr='S1', mouth=mo)
    else:
        o = 1.0
        if f in (92, 93, 94): o = [0.5, 0.05, 0.5][f - 92]
        st = dict(expr='S0', o=o, gaze=(0, 0))
    return cx_c(sx), cy, sxk, syk, rot, st

def cx_c(x): return x

def sun_state_C10(f, t):
    ry = G['meta']['RIDGE_Y']; sx = G['meta']['SUN_X']
    y_up = ry - (58 if V3 else 75 if V2 else 45)
    cy = y_up + 4 * math.sin(2 * math.pi * t / 58.0); rot = math.radians(1.5) * math.sin(2 * math.pi * t / 77.0)
    sxk = syk = 1.0
    # 곁눈: f0-9 달 쪽(왼쪽 위), f10-12 전환, f12-21 카메라
    if f < 10: gz = (-1.0, -0.55); grin = 1.0; tilt = 0
    else:
        u = sstep((f - 10) / 3.0); gz = (lerp(-1.0, 0.15, u), lerp(-0.55, 0.05, u)); grin = 1.0 + 0.4 * u
        tilt = math.radians(5) * u
    rot += tilt
    st = dict(expr='S4', o=0.58, gaze=gz, grin=grin)
    if f >= 22:   # 쏙 5f: y +360, 세로 1.2배
        u = min((f - 22 + 1) / 5.0, 1.0)
        cy += 360 * ease_in(u) ** 0.9
        syk = 1 + 0.2 * sstep(u * 1.5); sxk = 1 - 0.08 * sstep(u * 1.5)
    return sx, cy, sxk, syk, rot, st

def moon_state(clip, f, t):
    cx, cy = 260.0, 640.0
    cy += 6 * math.sin(2 * math.pi * t / 58.0); rot = math.radians(2) * math.sin(2 * math.pi * t / 77.0)
    if clip == 'C07':
        if f < 64:
            o = 0.5
            if f in (20, 21, 22): o = [0.25, 0.0, 0.25][f - 20]
            st = dict(expr='E6', o=o, gaze=(0.5, 0.1) if f < 48 else (0.9, 0.3))
        else:
            st = dict(expr='E5', phase=(f // 3) % 2, gaze=(0.3, 0))
            if f < 72:
                rr = np.random.default_rng(f)
                cx += rr.uniform(-1.6, 1.6); cy += rr.uniform(-1.6, 1.6)
    else:
        if f < 23:
            st = dict(expr='E6', o=0.5, gaze=(0.8, 0.3))
        else:
            st = dict(expr='E2', o=1.0, mouth=1.0)
            # 3f 틸트(오버슈트) → 유지 → 천천히 복귀
            g = f - 23
            if g < 3: tl = -11 * ease_out((g + 1) / 3.0)
            elif g < 6: tl = lerp(-11, -8, (g - 2) / 3.0)
            elif g < 22: tl = -8 * (1 - sstep((g - 6) / 16.0))
            else: tl = 0
            rot += math.radians(tl)
            if g < 3: cy -= 6 * ease_out((g + 1) / 3.0)
            elif g < 8: cy -= 6 * (1 - sstep((g - 2) / 6.0))
            if f >= 50:
                k = min((f - 50 + 1) / 2.0, 1.0)
                st = dict(expr='E2', o=1.0, mouth=1.0, mix=(dict(expr='E4'), k)) if k < 1 else dict(expr='E4')
    return cx, cy, 1.0, 1.0, rot, st

def osd_state(clip, f, rng):
    g = (360 if clip == 'C07' else 542) + f
    colon = (g % 24) < 12
    if clip == 'C07':
        if g <= 376:
            u = (g - 360) / 16.0
            mins = lerp(210, 441, 1 - (1 - u) ** 2.2)
            return dict(time=hm(mins), label='달 출근', colon=True)
        if g < 408: return dict(time='07:21', label='달 출근', colon=colon)
        return dict(time='07:22', label='해 출근', colon=colon, inv=(g == 408))
    else:
        if g < 564: return dict(time='07:22', label='해 출근', colon=colon)
        if g <= 568:
            return dict(time='07:22', label='해 출근', colon=colon, shake=(int(rng.integers(-2, 3)), int(rng.integers(-2, 3))))
        if g <= 616:
            u = (g - 569) / 47.0
            mins = lerp(442, 382, ease_io(u))
            return dict(time=hm(mins), label='', colon=True, glitch=(g <= 571), ff=((g - 569) // 3) % 2 == 0)
        on = {617: False, 618: False, 619: True, 620: True, 621: False, 622: False, 623: True}[g]
        return dict(time='06:22', label='', colon=True, digits=on)

def clip_plate_params(clip, f):
    """(mix, ripple_t, ev, vhs_strength)"""
    if clip == 'K3R':
        tau = 95 * (1 - f / 47.0); return sstep(tau / 95.0) * 0.92 + 0.08 * (tau / 95.0), 96 * (1 - f / 47.0), 0.0, 0.0
    if clip in ('C07', 'K3'):
        return sstep(f / 95.0) * 0.92 + 0.08 * (f / 95.0), float(f), 0.0, 0.0
    if f <= 26: return 1.0, 96.0 + f, 0.0, 0.0
    if f <= 74:
        u = (f - 27) / 47.0
        tau = 95 * (1 - u)                          # K3 원본 시간(끝→0), 2배속
        mix = sstep(tau / 95.0) * 0.92 + 0.08 * (tau / 95.0)
        trip = 123 * (1 - u)
        ev = -2.5 * sstep((f - 63) / 11.0) if f >= 63 else 0.0
        return mix, trip, ev, 1.0
    return 0.0, 0.0, -2.5, 0.35

# =========================================================== 프레임 렌더
def render_frame(clip, f, sig=True):
    init()
    t_glob = (360 if clip == 'C07' else 542) + f
    rng = np.random.default_rng(1000 * (1 if clip == 'C07' else 2) + f)
    mix, trip, ev, vst = clip_plate_params(clip, f)
    if clip in ('K3', 'K3R'):
        return plate(mix, trip, ev, kcol=0.7 * mix)
    H7 = G['H7']
    # ---- 해: 서브프레임 위치(셔터 180°, 8샘플)
    sfun = sun_state_C07 if clip == 'C07' else sun_state_C10
    samples = [f + (i + 0.5) / 8 * 0.5 - 0.25 for i in range(8)]
    def sun_at(ff):
        fi = int(math.floor(ff)); fr = ff - fi
        a = sfun(fi, t_glob - f + fi); b = sfun(fi + 1, t_glob - f + fi + 1)
        return [lerp(a[i], b[i], fr) for i in range(5)]
    poses = [sun_at(s) for s in samples]
    spread = max(abs(p[1] - poses[0][1]) + abs(p[0] - poses[0][0]) for p in poses)
    if spread < 0.4: poses = [sfun(f, t_glob)[:5]]
    st = sfun(f, t_glob)[5]
    core_p, core_a, corona = sun_sprite(t_glob, st)
    cys = [p[1] for p in poses]
    half = 310
    box = (max(0, int(poses[0][0] - half)), max(0, int(min(cys) - half)), min(W, int(poses[0][0] + half) + 1), min(H, int(max(cys) + half) + 1))
    acc = None
    for (cx, cy, sxk, syk, rot) in poses:
        o = place([core_p[..., 0], core_p[..., 1], core_p[..., 2], core_a, corona[..., 0], corona[..., 1], corona[..., 2]], cx, cy, sxk, syk, rot, box)
        acc = o if acc is None else [x + y for x, y in zip(acc, o)]
    acc = [x / len(poses) for x in acc]
    x0, y0, x1, y1 = box
    Pc = np.stack(acc[:3], -1); Ac = acc[3]; Cor = np.stack(acc[4:], -1)
    Hb = H7[y0:y1, x0:x1]
    vis = float((Ac * (1 - Hb)).sum() / max(Ac.sum(), 1e-3)) if Ac.sum() > 1 else 0.0
    # 전체 원판 면적 대비(영역 밖으로 나간 부분 포함) → 원판 면적 상수로 정규화
    disc_area = math.pi * 150 ** 2
    vis = min(1.0, float((Ac * (1 - Hb)).sum() / disc_area))
    v = vis if sig else 0.0
    # 플레이트(v2: 기존 물빛 기둥은 sig면 v에, nosig면 디졸브에 따라 복원)
    bg = plate(mix, trip, ev, kcol=(0.7 * vis if sig else 0.7 * mix), warm=(0.5 if sig else 0.0))
    # ---- 하늘 단계 신호 ②
    if sig: bg = horizon_glow(bg, vis)
    comp = bg.copy()
    # ---- 달(하늘 층의 자식)
    msky = bg[480:800, 100:420].reshape(-1, 3)
    Ls = float(luma(bg[480:800, 100:420]).mean())
    La, Lb = G['_La'] if '_La' in G else G.setdefault('_La', (float(luma(G['P7a'][480:800, 100:420]).mean()), float(luma(G['P7b'][480:800, 100:420]).mean())))
    cover = float(np.clip(0.18 + 0.12 * (Ls - La) / (Lb - La), 0.08, 0.35))
    sky_col = msky.mean(0)
    mcx, mcy, _, _, mrot, mst = moon_state('C07' if clip == 'C07' else 'C10', f, t_glob)
    rim_dir = math.atan2(G['meta']['RIDGE_Y'] - 60 - mcy, G['meta']['SUN_X'] - mcx) - mrot
    mp, ma = moon_sprite(mst, cover, sky_col, v, rim_dir)
    # 모션블러(달): 틸트·떨림 구간만
    def moon_at(ff):
        fi = int(math.floor(ff)); fr = ff - fi
        a = moon_state('C07' if clip == 'C07' else 'C10', fi, t_glob - f + fi); b = moon_state('C07' if clip == 'C07' else 'C10', fi + 1, t_glob - f + fi + 1)
        return [lerp(a[i], b[i], fr) for i in range(5)]
    mposes = [moon_at(s) for s in samples]
    mspread = max(abs(p[1] - mposes[0][1]) + abs(p[0] - mposes[0][0]) + 100 * abs(p[4] - mposes[0][4]) for p in mposes)
    if mspread < 0.4: mposes = [[mcx, mcy, 1, 1, mrot]]
    mbox = clipbox(mcx, mcy, 300)
    macc = None
    for (cx, cy, a_, b_, rot) in mposes:
        o = place([mp[..., 0], mp[..., 1], mp[..., 2], ma], cx, cy, 1, 1, rot, mbox)
        macc = o if macc is None else [x + y for x, y in zip(macc, o)]
    macc = [x / len(mposes) for x in macc]
    mx0, my0, mx1, my1 = mbox
    yy, xx = np.mgrid[my0:my1, mx0:mx1].astype(np.float32)
    d = np.hypot(xx - mcx, yy - mcy)
    from scipy.special import erfc
    mcol = np.array([0.95, 0.92, 0.82]) * (1 - cover) + sky_col * cover
    g1 = 0.5 * erfc((d - 100) / (30 * 1.4142)) * 0.35
    g2 = 0.5 * erfc((d - 160) / (80 * 1.4142)) * 0.20
    reg = comp[my0:my1, mx0:mx1]
    reg[:] = screen(reg, g1[..., None] * mcol[None, None] + g2[..., None] * hexc('#F3E9C6')[None, None] * 0.9)
    Mp = np.stack(macc[:3], -1); Ma = macc[3]
    reg[:] = reg * (1 - Ma[..., None]) + Mp
    # ---- 해 글로우(screen, 도시 위로 30% 번짐) → 코어(alpha) → 코로나(screen)
    gx0, gy0, gx1, gy1 = 0, 0, W, H
    yy, xx = G['_yx'] if '_yx' in G else G.setdefault('_yx', np.mgrid[0:H, 0:W].astype(np.float32))
    d = np.hypot(xx - poses[0][0], yy - np.mean(cys))
    R = 150.0 * (sum(p[3] for p in poses) / len(poses))
    dd = np.maximum(d - R, 0)
    glow = 0.50 * np.exp(-dd / 38.0) + 0.26 * np.exp(-dd / 150.0) + 0.10 * np.exp(-dd / 420.0)
    rim = 0.55 * np.exp(-dd / 9.0) * (d > R - 2) / (1 + spread / 6.0)
    gH = H7
    kv = min(1.0, vis * 1.25)
    # 도시 위 번짐은 능선 바로 아래(약 25px)에서만 30% → 가려진 원판의 유령이 생기지 않게
    if '_bleed' not in G:
        below = np.maximum(yy - G['ridge_out'][None, :], 0)
        G['_bleed'] = ((1 - gH) + gH * 0.30 * np.exp(-below / 25.0)).astype(np.float32)
    gl = (glow[..., None] * hexc('#FFB45A')[None, None] * G['_bleed'][..., None] + rim[..., None] * hexc('#FFD98F')[None, None] * (1 - gH)[..., None]) * kv
    comp = screen(comp, gl)
    # 지평선 근처 대기 흐림(해 아랫부분을 지평선 색으로 살짝 섞기)
    ridge = G['ridge_out'][x0:x1][None]
    ys = np.arange(y0, y1, dtype=np.float32)[:, None]
    hz = 0.32 * np.exp(-np.maximum(ridge - ys, 0) / 26.0)
    reg = comp[y0:y1, x0:x1]
    sun_rgb = Pc / np.maximum(Ac, 1e-4)[..., None]
    sun_rgb = sun_rgb * (1 - hz[..., None]) + bg[y0:y1, x0:x1] * hz[..., None]
    Av = Ac * (1 - Hb)
    reg[:] = reg * (1 - Av[..., None]) + sun_rgb * Av[..., None]
    if V2:   # 코로나 머리카락: 채색본을 알파(normal)로 얹어 밝은 하늘에서도 색이 남게
        ca = np.clip(Cor[..., 0], 0, 1) * (1 - Hb) * (1 - 0.6 * hz)
        ccol = Cor / np.maximum(Cor[..., :1], 1e-3)
        reg[:] = reg * (1 - 0.9 * ca[..., None]) + ccol * 0.9 * ca[..., None]
    else:
        reg[:] = screen(reg, Cor * (1 - Hb)[..., None] * (1 - 0.6 * hz[..., None]))
    if V2:   # 가장자리보다 밝은 바깥 글로우가 코어 가장자리를 덮는다(광원감)
        from scipy.special import erfc
        og = 0.5 * erfc((d - 1.2 * R) / (40 * 1.4142)) * 0.25 * kv
        comp = screen(comp, og[..., None] * hexc('#FFE6B0')[None, None] * G['_bleed'][..., None])
    # ---- 물 위 신호 ①③
    if sig:
        comp = signal_glitter(comp, v, t_glob)
        comp = mist_backlight(comp, v, trip)
    # ---- 후처리: VHS
    if vst > 0:
        comp = vhs(comp, t_glob, rng, strength=vst)
    # ---- OSD
    comp = draw_osd(comp, osd_state(clip, f, rng), rng)
    return np.clip(comp, 0, 1), vis

# =========================================================== v3 전용 (render.py에 병합됨, 원본 보관용)
def add_hair(corona, t, C, R2):
    """정수리 머리털 3가닥: 밑동 폭 0.07D → 끝 0, 길이 0.25D, 끝이 말림. 색 #FFC24A→#FE9C00."""
    N = corona.shape[0]; D = 2 * R2; k = 3
    big = Image.new('L', (N * 2, N * 2), 0); dr = ImageDraw.Draw(big)
    tip = Image.new('L', (N * 2, N * 2), 0); dt = ImageDraw.Draw(tip)
    specs = [(-104, 0.22, -1, 0.0), (-88, 0.25, 1, 1.7), (-72, 0.21, 1, 3.1)]   # 각도(도), 길이(D), 말림 방향, 위상
    for ang, ln, curl, phs in specs:
        a0 = math.radians(ang + 6 * math.sin(2 * math.pi * t / 31.0 + phs))
        bx, by = C + math.cos(a0) * R2 * 0.94, C + math.sin(a0) * R2 * 0.94
        L_ = ln * D
        pts_c, pts_l, pts_r = [], [], []
        for i in range(25):
            u = i / 24
            bend = a0 + curl * math.radians(55) * u ** 1.6
            if i == 0: x_, y_ = bx, by
            else:
                x_ = pts_c[-1][0] + math.cos(bend) * L_ / 24; y_ = pts_c[-1][1] + math.sin(bend) * L_ / 24
            pts_c.append((x_, y_))
            wdt = 0.07 * D * (1 - u) ** 0.9 / 2 + 0.6
            nx, ny = -math.sin(bend), math.cos(bend)
            pts_l.append((x_ + nx * wdt, y_ + ny * wdt)); pts_r.append((x_ - nx * wdt, y_ - ny * wdt))
        poly = [(p[0] * 2, p[1] * 2) for p in pts_l + pts_r[::-1]]
        dr.polygon(poly, fill=255)
        dt.polygon([(p[0] * 2, p[1] * 2) for p in (pts_l[12:] + pts_r[12:][::-1])], fill=255)
    m_ = np.asarray(big.resize((N, N), Image.BOX)).astype(np.float32) / 255.
    tp = gaussian_filter(np.asarray(tip.resize((N, N), Image.BOX)).astype(np.float32) / 255., 3)
    m_ = gaussian_filter(m_, 0.6)
    col = hexc('#FFC24A')[None, None] * (1 - tp[..., None]) + hexc('#FE9C00')[None, None] * tp[..., None]
    a_ = (m_ * 0.95)[..., None]
    return corona * (1 - a_) + col * a_

def sun_sprite_v3(t, st):
    """절차형 코어(쌀알무늬 ±5%, 셀 6~10px, 초당 2px 흐름 + 노이즈 변위 3px/48f) + 구면 얼굴 + 코어 블룸."""
    core = G['sun_core_rgb']; a = G['sun_core_a']; cor = G['sun_corona']; gran = G['gran']
    N = core.shape[0]; C = N / 2 - 0.5; R2 = SUN_R * SS
    yy, xx = np.mgrid[0:N, 0:N].astype(np.float32)
    ph = 2 * np.pi * t / 48.0; amp = 3.0 * SS
    dx = amp * (G['SDX1'][:N, :N] * np.cos(ph) + G['SDX2'][:N, :N] * np.sin(ph))
    dy = amp * (G['SDY1'][:N, :N] * np.cos(ph) + G['SDY2'][:N, :N] * np.sin(ph))
    flow = t * (2.0 / 24.0) * SS
    gr = map_coordinates(gran, [yy + dy, xx + dx + 200 - flow], order=1, mode='wrap')
    rr = np.hypot(xx - C, yy - C) / R2
    mu = np.sqrt(np.clip(1 - rr ** 2, 0, 1))
    if V31:
        amp_ = 0.03 + 0.02 * sstep((rr - 0.35) / 0.15)        # 중심 40% 안 ±3% → 바깥 ±5%
        body = core * (1 + amp_ * gr * (0.4 + 0.6 * mu))[..., None]
    else:
        body = core * (1 + 0.05 * gr * (0.4 + 0.6 * mu))[..., None]
    ca = 5.0 * SS * 230 / 300
    ring = np.clip((rr - 0.95) / 0.1, 0, 1)
    cdx = ca * (G['CDX'][:N, :N] * np.cos(ph * 1.7) + G['SDX2'][:N, :N] * np.sin(ph * 1.7)) * ring
    cdy = ca * (G['CDY'][:N, :N] * np.cos(ph * 1.7) + G['SDY1'][:N, :N] * np.sin(ph * 1.7)) * ring
    corona = np.stack([map_coordinates(cor[..., c], [yy + cdy - 1.2 * SS * np.sin(ph * 2), xx + cdx], order=1, mode='constant') for c in range(3)], -1)
    flk = G['FLK']; fl = sum(w_ * np.sin(2 * np.pi * t / P + p) for P, p, w_ in flk) / flk[:, 2].sum()
    corona = corona * (1 + 0.10 * fl)
    if V31: corona = add_hair(corona, t, C, R2)
    frgb, fa, half = sun_face(st)
    s0 = int(C - half + 0.5); n = frgb.shape[0]
    fy, fx = np.mgrid[0:n, 0:n].astype(np.float32)
    px, py = fx + s0 - C, fy + s0 - C
    rho = np.hypot(px, py) / R2
    k = 1 + 0.25 * np.clip(rho, 0, 1.2) ** 2
    sx_, sy_ = px * k + C - s0, py * k + C - s0
    frgb = np.stack([map_coordinates(frgb[..., c], [sy_, sx_], order=1, mode='constant') for c in range(3)], -1)
    fa = map_coordinates(fa, [sy_, sx_], order=1, mode='constant')
    sig_ = 0.7 * SS
    fa = gaussian_filter(fa, sig_); frgb = gaussian_filter(frgb, (sig_, sig_, 0))
    sl = (slice(s0, s0 + n), slice(s0, s0 + n))
    fa = fa * a[sl] * 0.90
    out = body.copy()
    out[sl] = out[sl] * (1 - fa[..., None]) + frgb * fa[..., None]
    bloom = gaussian_filter(body[sl], (6, 6, 0))
    fm = np.clip(gaussian_filter(fa, 4) * 1.6, 0, 1)
    out[sl] = screen(out[sl], bloom * 0.13 * fm[..., None])
    return out * a[..., None], a, corona

COLG = 1.0
COLG31 = 0.78    # v3.1: 중심선(#FFF1CF 35%)을 얹은 뒤 합계가 목표(P7c 85%)에 맞도록
def signal_column(img, v, t, mix):
    """1 100% 절차형 반사 기둥. 폭 0.5D(지평선)->0.9D(아래), #FFC24A->#FE9C00, 은빛 반짝임 30%.
    v=1에서 행별 최고 휘도 = P7c 기둥의 85%(col_target)."""
    if v <= 0.002: return img
    m = G['meta']; sx = m['SUN_X']; wt = int(m['WATER_TOP'])
    D = 2 * SUN_R
    ys = np.arange(wt, H, dtype=np.float32)[:, None]; xs = np.arange(W, dtype=np.float32)[None]
    depth = np.clip((ys - wt) / (H - wt), 0, 1)
    wid = D * (0.5 + 0.4 * depth)
    sig = wid / 2.355
    shape = np.exp(-0.5 * ((xs - sx) / sig) ** 2)
    yw0 = int(G['yw0']); off = wt - yw0
    ph = 2 * np.pi * t / 24.0
    st = nonperiodic('S', t, (0.7, 0.5, 0.4), off, H - wt) if V31 else (G['STR1'] * np.cos(ph) + G['STR2'] * np.sin(ph))[off:off + (H - wt)]
    streak = np.clip(0.95 + 0.45 * st, 0.35, 1.35)
    dd = depth[:, 0] ** 0.8
    colr = hexc('#FFC24A')[None] * (1 - dd[:, None]) + hexc('#FE9C00')[None] * dd[:, None]
    T = G['col_target'][wt:H] * v
    if V31:   # 지평선 근처 0~120px −10% (120~150px에서 원래대로)
        yl = np.arange(H - wt, dtype=np.float32)
        T = T * (1 - 0.10 * (1 - sstep((yl - 120) / 30.0)))
    xc = int(round(sx))
    Lb = luma(img[wt:H, xc - 3:xc + 4]).mean(1)
    Lc = luma(colr)
    a_ = np.clip((T - Lb) / np.maximum((1 - Lb) * Lc, 1e-3), 0, 1.0)
    warm = (a_[:, None] * shape * streak * (COLG31 if V31 else COLG))[..., None] * colr[:, None, :]
    S = G['SPK']; acc = np.zeros((H - wt, W), np.float32)
    py = wt + (S[:, 1] ** 0.85) * (H - wt)
    pd = np.clip((py - wt) / (H - wt), 0, 1)
    px = sx + S[:, 0] * (D * (0.5 + 0.4 * pd)) / 2.355 * 0.9
    tw = np.clip(np.sin(2 * np.pi * t * S[:, 3] / 2.0 + S[:, 2]), 0, 1) ** 5 * S[:, 4]
    ok = (px >= 1) & (px < W - 1) & (py >= wt) & (py < H - 1)
    np.add.at(acc, ((py[ok] - wt).astype(int), px[ok].astype(int)), tw[ok] * 7.0)
    acc = np.clip(gaussian_filter(acc, (0.8, 2.4)), 0, 1.2)
    silver = (acc * (0.30 / 0.70) * 1.6 * a_[:, None] * np.clip(shape * 1.3, 0, 1))[..., None] * hexc('#EEF2F8')[None, None]
    lay = (warm + silver) * G['water'][wt:H][..., None]
    out = img.copy()
    out[wt:H] = screen(out[wt:H], lay)
    if V31:   # 중심선: 기둥 폭의 20%에 #FFF1CF 35%
        core_ = np.exp(-0.5 * ((xs - sx) / (0.2 * wid / 2.355)) ** 2)
        kk = (0.35 * core_ * np.clip(a_[:, None] * streak, 0, 1) * G['water'][wt:H])[..., None]
        out[wt:H] = out[wt:H] * (1 - kk) + hexc('#FFF1CF')[None, None] * kk
    return out

def sky_band(img, mix):
    """하늘 반사: 넓고 흐린 띠(최대 6%, 신호와 무관)."""
    m = G['meta']; wt = int(m['WATER_TOP'])
    ys = np.arange(wt, H, dtype=np.float32)[:, None]; xs = np.arange(W, dtype=np.float32)[None]
    depth = np.clip((ys - wt) / (H - wt), 0, 1)
    b = np.exp(-((xs - m['SUN_X']) / 300.) ** 2) * np.exp(-depth * 2.2) * G['water'][wt:H] * (0.06 * (0.4 + 0.6 * mix))
    out = img.copy(); out[wt:H] = screen(out[wt:H], b[..., None] * hexc('#F6B98A')[None, None]); return out

def vhs_v3(img, t, rng, strength=1.0):
    out = img.copy()
    jy = int(rng.choice([-2, -1, 1, 2])) if strength > 0.5 else 0
    if jy: out = np.roll(out, jy, 0)
    yy = np.arange(H, dtype=np.float32)
    rows = gaussian_filter(rng.normal(0, 1, H), 2) * 1.6 * strength
    bands = np.zeros(H, np.float32)
    for (hgt, speed, phase, push) in ((84, 61, 0, 1), (64, 47, 900, -1)):
        yc = (H + 200) - ((t * speed + phase) % (H + 400))
        bm = sstep((hgt / 2 - np.abs(yy - yc)) / 6.0) * strength
        shift = push * rng.uniform(12, 20) + rng.normal(0, 2.5, H)
        rows = rows + bm * shift
        bands = np.maximum(bands, bm)
    R = _shift_rows(out[..., 0], rows + 5 * strength); Bc = _shift_rows(out[..., 2], rows - 5 * strength); Gc = _shift_rows(out[..., 1], rows)
    o2 = np.stack([R, Gc, Bc], -1)
    Yo = luma(o2)[..., None]
    o2 = Yo + gaussian_filter(o2 - Yo, (0, 3.0, 0)) * 0.9
    nz = rng.random((H, W)).astype(np.float32)
    streak = gaussian_filter((nz > 0.985).astype(np.float32) * bands[:, None], (0.5, 6))
    o2 = o2 + (streak * 1.4 + (nz - 0.5) * 0.12 * bands[:, None])[..., None]
    o2[1::2] *= (1 - 0.12 * strength)
    hs = 24
    o2[-hs:] = np.roll(o2[-hs:], int(rng.integers(10, 30)), 1) * 0.8 + rng.random((hs, W, 1)).astype(np.float32) * 0.15
    Yo = luma(o2)[..., None]
    o2 = Yo + (o2 - Yo) * (1 - 0.12 * strength)
    o2 = o2 * (1 - 0.04 * strength) + 0.03 * strength
    return np.clip(o2, 0, 1).astype(np.float32)

def render_frame_v3(clip, f, sig=True):
    init()
    from scipy.special import erfc
    if 'gran' not in G:
        G['gran'] = np.load(os.path.join(B, 'gran_v31.npy' if V31 else 'gran.npy')); G['col_target'] = np.load(os.path.join(B, 'col_target.npy'))
        if V31:
            G['sun_corona'] = np.load(os.path.join(B, 'sun_corona_v31.npy'))
            F = np.load(os.path.join(B, 'fields_v31.npz'))
            for k_ in F.files: G[k_] = F[k_]
    t_glob = (360 if clip == 'C07' else 542) + f
    rng = np.random.default_rng(1000 * (1 if clip == 'C07' else 2) + f)
    mix, trip, ev, vst = clip_plate_params(clip, f)
    H7 = G['H7']; ry = G['meta']['RIDGE_Y']; D = 2 * SUN_R
    sfun0 = sun_state_C07 if clip == 'C07' else sun_state_C10
    def sfun(ff, tt):
        p = list(sfun0(ff, tt))
        dist = abs(p[1] - ry)
        p[3] = p[3] * (1 - 0.04 * (1 - sstep((dist - 0.6 * D) / 20.0)))
        return p
    samples = [f + (i + 0.5) / 8 * 0.5 - 0.25 for i in range(8)]
    def sun_at(ff):
        fi = int(math.floor(ff)); fr = ff - fi
        a = sfun(fi, t_glob - f + fi); b = sfun(fi + 1, t_glob - f + fi + 1)
        return [lerp(a[i], b[i], fr) for i in range(5)]
    poses = [sun_at(s) for s in samples]
    spread = max(abs(p[1] - poses[0][1]) + abs(p[0] - poses[0][0]) for p in poses)
    if spread < 0.4: poses = [sfun(f, t_glob)[:5]]
    st = sfun(f, t_glob)[5]
    core_p, core_a, corona = sun_sprite_v3(t_glob, st)
    cys = [p[1] for p in poses]; half = 250
    box = (max(0, int(poses[0][0] - half)), max(0, int(min(cys) - half)), min(W, int(poses[0][0] + half) + 1), min(H, int(max(cys) + half) + 1))
    acc = None
    for (cx, cy, sxk, syk, rot) in poses:
        o = place([core_p[..., 0], core_p[..., 1], core_p[..., 2], core_a, corona[..., 0], corona[..., 1], corona[..., 2]], cx, cy, sxk, syk, rot, box)
        acc = o if acc is None else [x + y for x, y in zip(acc, o)]
    acc = [x / len(poses) for x in acc]
    x0, y0, x1, y1 = box
    Pc = np.stack(acc[:3], -1); Ac = acc[3]; Cor = np.stack(acc[4:], -1)
    Hb = H7[y0:y1, x0:x1]
    vis = min(1.0, float((Ac * (1 - Hb)).sum() / (math.pi * SUN_R ** 2)))
    v = vis if sig else 0.0
    bg = plate(mix, trip, ev)
    bg = sky_band(bg, mix)
    if sig: bg = horizon_glow(bg, vis)
    comp = bg.copy()
    msky = bg[480:800, 100:420].reshape(-1, 3)
    Ls = float(luma(bg[480:800, 100:420]).mean())
    La, Lb = G['_La'] if '_La' in G else G.setdefault('_La', (float(luma(G['P7a'][480:800, 100:420]).mean()), float(luma(G['P7b'][480:800, 100:420]).mean())))
    cover = float(np.clip(0.18 + 0.12 * (Ls - La) / (Lb - La), 0.08, 0.35))
    sky_col = msky.mean(0)
    mclip = 'C07' if clip == 'C07' else 'C10'
    mcx, mcy, _, _, mrot, mst = moon_state(mclip, f, t_glob)
    rim_dir = math.atan2(ry - 60 - mcy, G['meta']['SUN_X'] - mcx) - mrot
    mp, ma = moon_sprite(mst, cover, sky_col, v, rim_dir)
    def moon_at(ff):
        fi = int(math.floor(ff)); fr = ff - fi
        a = moon_state(mclip, fi, t_glob - f + fi); b = moon_state(mclip, fi + 1, t_glob - f + fi + 1)
        return [lerp(a[i], b[i], fr) for i in range(5)]
    mposes = [moon_at(s) for s in samples]
    mspread = max(abs(p[1] - mposes[0][1]) + abs(p[0] - mposes[0][0]) + 100 * abs(p[4] - mposes[0][4]) for p in mposes)
    if mspread < 0.4: mposes = [[mcx, mcy, 1, 1, mrot]]
    mbox = clipbox(mcx, mcy, 300); macc = None
    for (cx, cy, a_, b_, rot) in mposes:
        o = place([mp[..., 0], mp[..., 1], mp[..., 2], ma], cx, cy, 1, 1, rot, mbox)
        macc = o if macc is None else [x + y for x, y in zip(macc, o)]
    macc = [x / len(mposes) for x in macc]
    mx0, my0, mx1, my1 = mbox
    yy, xx = np.mgrid[my0:my1, mx0:mx1].astype(np.float32)
    d = np.hypot(xx - mcx, yy - mcy)
    mcol = np.array([0.95, 0.92, 0.82]) * (1 - cover) + sky_col * cover
    g1 = 0.5 * erfc((d - 100) / (30 * 1.4142)) * 0.35
    g2 = 0.5 * erfc((d - 160) / (80 * 1.4142)) * 0.20
    reg = comp[my0:my1, mx0:mx1]
    reg[:] = screen(reg, g1[..., None] * mcol[None, None] + g2[..., None] * hexc('#F3E9C6')[None, None] * 0.9)
    reg[:] = reg * (1 - macc[3][..., None]) + np.stack(macc[:3], -1)
    yy, xx = G['_yx'] if '_yx' in G else G.setdefault('_yx', np.mgrid[0:H, 0:W].astype(np.float32))
    gcx = float(np.mean([p[0] for p in poses])); gcy = float(np.mean(cys))
    syk_m = float(np.mean([p[3] for p in poses]))
    d = np.hypot(xx - gcx, (yy - gcy) / max(syk_m, 0.5))
    glow = 0.40 * 0.5 * erfc((d - SUN_R) / (40 * 1.4142)) + 0.20 * 0.5 * erfc((d - SUN_R) / (120 * 1.4142))
    if '_bleed3' not in G:
        below = np.maximum(yy - G['ridge_out'][None, :], 0)
        G['_bleed3'] = ((1 - H7) + H7 * 0.25 * np.clip(1 - below / 24.0, 0, 1) ** 1.5).astype(np.float32)
    kv = min(1.0, vis * 1.25)
    comp = screen(comp, (glow * kv * G['_bleed3'])[..., None] * hexc('#FFC24A')[None, None])
    reg = comp[y0:y1, x0:x1]
    sun_rgb = Pc / np.maximum(Ac, 1e-4)[..., None]
    ys = np.arange(y0, y1, dtype=np.float32)[:, None]
    R_eff = SUN_R * syk_m
    wb = sstep((ys - (gcy + 0.35 * R_eff)) / (0.30 * R_eff))
    sun_rgb = l2s(s2l(sun_rgb) * (2 ** (-0.4 * wb))[..., None])
    sun_rgb = sun_rgb * (1 - 0.40 * wb[..., None]) + hexc('#F08A00')[None, None] * (luma(sun_rgb)[..., None] / 0.52) * 0.40 * wb[..., None]
    Av = Ac * (1 - Hb)
    reg[:] = reg * (1 - Av[..., None]) + np.clip(sun_rgb, 0, 1) * Av[..., None]
    ca = np.clip(Cor[..., 0], 0, 1) * (1 - Hb)
    ccol = Cor / np.maximum(Cor[..., :1], 1e-3)
    reg[:] = reg * (1 - 0.9 * ca[..., None]) + ccol * 0.9 * ca[..., None]
    if sig:
        comp = signal_column(comp, v, t_glob, mix)
        comp = mist_backlight(comp, v, trip)
    if vst > 0:
        comp = vhs_v3(comp, t_glob, rng, strength=vst)
    comp = draw_osd(comp, osd_state(clip, f, rng), rng)
    return np.clip(comp, 0, 1), vis

def out_dir(clip, sig):
    d = os.path.join(ROOT, {'1': 'frames', '2': 'frames_v2', '3': 'frames_v3', '31': 'frames_v31'}[_TV], f'{clip}_{"sig" if sig else "nosig"}'); os.makedirs(d, exist_ok=True); return d

def job(args):
    clip, f, sig = args
    r = (render_frame_v3 if V3 and not clip.startswith('K3') else render_frame)(clip, f, sig)
    if clip in ('K3', 'K3R'):
        img, vis = r, 0
    else:
        img, vis = r
    Image.fromarray((img * 255 + 0.5).astype(np.uint8)).save(os.path.join(out_dir(clip, sig), f'{f:03d}.png'), compress_level=1)
    return clip, f, sig, vis

LEN = {'C07': 96, 'C10': 82, 'K3': 96, 'K3R': 48}

if __name__ == '__main__':
    from multiprocessing import Pool
    which = sys.argv[1] if len(sys.argv) > 1 else 'all'
    ver = sys.argv[2] if len(sys.argv) > 2 else 'both'
    frames = None
    if '--frames' in sys.argv: frames = [int(x) for x in sys.argv[sys.argv.index('--frames') + 1].split(',')]
    if not os.path.exists(os.path.join(B, 'fields.npz')) or '--fields' in sys.argv: make_fields()
    clips = ['C07', 'C10', 'K3'] if which == 'all' else which.split(',')
    sigs = {'both': [True, False], 'sig': [True], 'nosig': [False]}[ver]
    tasks = []
    for c in clips:
        for s in (sigs if not c.startswith('K3') else [True]):
            for f in (frames if frames else range(LEN[c])):
                tasks.append((c, f, s))
    with Pool(min(12, len(tasks))) as p:
        res = p.map(job, tasks, chunksize=1)
    vlog = {}
    for c, f, s, vis in res:
        if s: vlog.setdefault(c, {})[f] = round(vis, 3)
    json.dump(vlog, open(os.path.join(B, f'v_log_{which.replace(",", "_")}.json'), 'w'))
    print('done', len(tasks))
