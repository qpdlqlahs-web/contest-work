# -*- coding: utf-8 -*-
"""
퓨리얼 영상부문 A' 「정전 점검의 아침」 편집 스크립트 (v2: 크리에이티브 리뷰 7.3 REVISE 반영)
  python edit_aprime.py                 -> out/Aprime_v2_master.mp4, out/Aprime_v2.mp4, out/Aprime_v2_contact.png
  python edit_aprime.py --check DIR f1 f2 ...  -> 지정 프레임만 PNG로 (검수용)

타임라인 원칙
  - 곡 「퓨리얼, 진짜 물」(42.0s). 편집 시각 = 곡 시각 + OFFSET.
  - OFFSET: 곡 0.511s의 첫 강박(인트로 히트)을 컷 6 하드컷(4.000s)에 맞춘다.
    기획표는 SRT(+4.0s) 기준이었으나, 보컬 스템 분석 결과 실제 가사가 SRT보다 약 0.4~0.5s 늦어
    곡을 0.511s 앞당겨 배치했다. 모든 컷 경계는 곡 비트(117.45 BPM) 위의 가사 온셋에 맞춘다.
  - 쇼츠 UI: 모든 글자는 y<=1440, 오른쪽 x<=940.
"""
import os, sys, json, subprocess, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy import ndimage, signal
from scipy.io import wavfile

VER = 'v4_1'   # v4_1: 16.54s 점프컷 보강(착 클릭 + S10-2 펀치 6f). v4: 정지 컷 5개를 Kling 영상(v05/v07/v10/v14/v16)으로 교체. v3: 필수 문구 52px 두 줄, 컷 8 접지 그림자·하단 톤, 컷 10 줌, '아…' y520, 엔딩 블록 -40px
ROOT = os.path.dirname(os.path.abspath(__file__))
PAR = os.path.dirname(ROOT)
IMG = os.path.join(ROOT, 'img')
CLIPS = os.path.join(ROOT, 'clips')
FONTS = os.path.join(ROOT, 'fonts')
OUT = os.path.join(ROOT, 'out')
SONG = os.path.join(PAR, '최종제출', '퓨리얼_진짜물.wav')
REF = os.path.join(PAR, 'refs', 'assets')
P300 = os.path.join(REF, '02. 퓨리얼 유로체인저 직수정수기 PPA-300')
BACK = os.path.join(P300, 'PPA-300_제품 뒷면.jpg')
FRONT = os.path.join(P300, 'PPA-300 (1).jpg')
BI = os.path.join(REF, '10. 퓨리얼 로고', '퓨리얼_BI.png')
NOTICE = os.path.join(ROOT, 'proposals', 'type', '03_notice_A4_flat.png')

W, H, FPS = 1080, 1920, 24
OFFSET = 3.489          # edit = song + OFFSET
SR = 48000
SAFE_Y = 1440
SAFE_X = 940


def F(song_t):
    return int(round((song_t + OFFSET) * FPS))


def pick(*names):
    """앞에 있는 파일이 있으면 그것을 쓴다(수정본 우선)."""
    for n in names:
        if os.path.exists(os.path.join(IMG, n)):
            return n
    raise FileNotFoundError(names)


# ---------------------------------------------------------------- 소재 (경로만 바꾸면 교체됨)
SRC = dict(
    S01='S01_comp_v2.png', S02='S02_comp_v2.png',
    S03a='S03-1_fix.png', S03b='S03-2_fix.png', S04='S04_fix.png', S05='S05_comp.png',
    S07a='S07-1fix2_1.png', S07b='S07-2_1.png', ENV='ENV1_final.jpg',
    S10a='S10_start_v5.png', S10b='S10-2_comp.png',
    S10hi='S10scene2_1.png',      # S10_start_v5의 원본 장면(1536x2752). 아빠 바스트 크롭용(같은 인물·구도)
    S11a='S11-1_comp.png', S11b='S11-2_v4.png', S11c='S11-3_v3.png',
    S12a='S12-1_v2.png', S12b='S12-2v2_1.png',
    S13a='S13-1_v2.png', S13b='S13-2_fix.png', S13c='S13-3_v2.png',
    S14='S14v3_1.png',
    S16a=pick('S16-1_v2.png', 'S16-1_1.png'),
    S16b=pick('S16-2_v3.png', 'S16-2v2_1.png'),
    S16c=pick('S16-3_v3.png', 'S16-3_v2.png', 'S16-3_1.png'),
    S18='S18_start_v2.png',
)
CLIP = dict(K1='K1_final_v2.mp4', K2='K2_final_v3.mp4', K3='K3_final.mp4',
            K4='K4_final.mp4', K5='K5_final.mp4',
            V05='v05_final.mp4', V07='v07_final.mp4', V10='v10_final.mp4',   # v4: 사용자 승인 교체 영상
            V14='v14_final.mp4', V16='v16_final.mp4')
K4_SKIP = 14            # K4 앞 0.58s(정지 구간)를 건너뛰어 '드는 동작'을 두 번째 "퓨리얼"에 맞춤

# 컷 11 '톡' 클로즈업: S11-1_comp의 필터 03(검정 라벨) 중심, 2.2배
TOK_CENTER = (655, 1180)   # 제품 윗면이 정보 자막 뒤에 오지 않게 아래로
TOK_Z = 2.2
# 컷 11 끝: 아빠 바스트(S10scene2_1 원본 좌표). 얼굴 중심 약 (440,1250)
BUST_CENTER = (400, 1450)
BUST_Z = (2.02, 2.02 * 1.08)

# ---------------------------------------------------------------- 컷 경계 (프레임)
B = dict(
    c1=0, c2=12, c3=34, c3b=43, c4=53, c5=72,          # 훅: 기획표 그대로(0.5/1.4/1.8/2.2/3.0/4.0s)
    c6=F(0.511),                                       # (톡!) 인트로 히트          = 4.000s
    c7=F(3.553), c7b=F(5.039),                         # "아침에" / 두 번째 "꿀꺽"(빈 컵 + 캬!)
    c8=F(6.037),                                       # "전기 없이"
    c9=F(8.011),                                       # "직수로"
    c10=F(10.054), c10b=F(13.026),                     # "바로" 끝 박 / "뚝딱"
    c11=F(14.025),                                     # "필터도"      S11-1
    c11b=F(15.047),                                    # "톡"          필터 03 클로즈업 펀치인
    c11c=F(17.043),                                    # "착"          S11-2
    c11d=F(17.298),                                    #  8분음        S11-3
    c11e=F(17.554),                                    #  박           아빠 바스트 줌
    c12=F(19.528), c12b=F(20.294),                     # "복잡한" / "비우고"
    c13=F(21.06), c13b=F(21.548), c13c=F(22.036),      # "깨끗함은" 잔 1→2→3
    c14=F(22.547), c14b=F(25.565),                     # 후렴 진입(밴드 재진입, 딩동) / 인서트
    c15=F(27.051),                                     # "퓨리얼 퓨리얼, 물 한 잔도"
    c16=F(31.045), c16b=F(32.531), c16c=F(33.042),     # "일상은 비우고": 고개 듦(아…) / 리모컨 / 창빛
    c17=F(33.553),                                     # "가치를 채우다"
    c18=F(36.037),                                     # 간주
    c19=F(38.545),                                     # "퓨리얼! 퓨리얼!"
    c20=F(42.0),                                       # 곡 끝 -> 단독 엔드카드 2.5s
)
B['c10b'] = B['c10'] + 72                            # v4: v10 영상 72프레임(3.0s) -> S10-2 구간에서 1프레임 흡수
B['end'] = B['c20'] + int(2.5 * FPS)
NFR = B['end']
CUT_STARTS = [B['c%d' % i] for i in range(1, 21)] + [NFR]

# ---------------------------------------------------------------- 색
C_TEXT = (0xFB, 0xF7, 0xF0)
C_BI = (0x09, 0x71, 0xCE)
C_DARK = (0x3A, 0x3F, 0x45)
C_END1 = (0x5E, 0x63, 0x6A)
C_END2 = (0x23, 0x27, 0x2C)
C_SUB = (0x50, 0x55, 0x5B)
C_BEAM = np.array([0xF4, 0xEB, 0xDD], np.float32)
CREAM_TOP = np.array([247, 240, 228], np.float32)
CREAM_BOT = np.array([232, 227, 217], np.float32)


# ================================================================= 유틸
_font_cache = {}


def font(rel, size):
    k = (rel, size)
    if k not in _font_cache:
        path, _, inst = rel.partition('#')
        ft = ImageFont.truetype(os.path.join(FONTS, path), size)
        if inst:
            ft.set_variation_by_name(inst)
        _font_cache[k] = ft
    return _font_cache[k]


PRET_M = 'Pretendard/Pretendard-Medium.otf'
PRET_SB = 'Pretendard/Pretendard-SemiBold.otf'
PRET_B = 'Pretendard/Pretendard-Bold.otf'
NOTO_R = 'NotoSerifKR/NotoSerifKR-Regular.otf'
NOTO_SB = 'NotoSerifKR/NotoSerifKR-SemiBold.otf'
NOTO_B = 'NotoSerifKR/NotoSerifKR[wght].ttf#Bold'   # Google Fonts 공식 가변 글꼴(OFL), Bold 인스턴스
DSEG_B = 'DSEG/DSEG7Classic-Bold.ttf'


def text_width(text, ft, track):
    return sum(ft.getlength(c) for c in text) + track * (len(text) - 1)


def draw_tracked(dr, x, baseline, text, ft, fill, track, stroke=0):
    for c in text:
        dr.text((x, baseline), c, font=ft, fill=fill, anchor='ls', stroke_width=stroke, stroke_fill=fill)
        x += ft.getlength(c) + track
    return x


def ease_io(t):
    t = min(max(t, 0.0), 1.0)
    return 0.5 - 0.5 * math.cos(math.pi * t)


def ease_out(t):
    t = min(max(t, 0.0), 1.0)
    return 1 - (1 - t) ** 3


def lerp(a, b, t):
    return a + (b - a) * t


def shadowed(layer, s1=(0, 2, 2.0, 0.45), s2=(0, 5, 12.0, 0.32)):
    """텍스트 RGBA 레이어에 그림자 2중을 깐다."""
    a = np.asarray(layer.split()[3]).astype(np.float32) / 255.0
    out = np.zeros((layer.size[1], layer.size[0]), np.float32)
    for dx, dy, r, op in (s2, s1):
        sh = ndimage.gaussian_filter(a, r)
        sh = ndimage.shift(sh, (dy, dx), order=1)
        out = out + sh * op * (1 - out)
    sh_img = Image.new('RGBA', layer.size, (0, 0, 0, 0))
    sh_img.putalpha(Image.fromarray(np.clip(out * 255, 0, 255).astype(np.uint8)))
    return Image.alpha_composite(sh_img, layer)


def with_alpha(img, k):
    if k >= 0.999:
        return img
    r, g, b, a = img.split()
    a = a.point(lambda v: int(v * max(k, 0.0)))
    return Image.merge('RGBA', (r, g, b, a))


def bbox_check(name, layer):
    """쇼츠 UI 안전영역 검사(글자 레이어의 불투명 영역)."""
    a = np.asarray(layer.split()[3]) > 40
    ys, xs = np.nonzero(a)
    if len(xs) == 0:
        return
    x1, y1 = xs.max(), ys.max()
    flag = '' if (y1 <= SAFE_Y and x1 <= SAFE_X) else '  <-- 안전영역 초과'
    print('  [safe] %-14s x %4d-%4d  y %4d-%4d%s' % (name, xs.min(), x1, ys.min(), y1, flag))


# ================================================================= 소재 로딩
_img_cache = {}


def load(name):
    if name not in _img_cache:
        _img_cache[name] = Image.open(os.path.join(IMG, name)).convert('RGB')
    return _img_cache[name]


def view(im, z=1.0, ox=0.0, oy=0.0, center=None):
    """9:16 커버 축소 + 줌 z + 팬. 원본 해상도에서 바로 리샘플."""
    w, h = im.size
    s = max(W / w, H / h) * z
    hw, hh = W / 2 / s, H / 2 / s
    if center is None:
        cx, cy = w / 2 + ox * w, h / 2 + oy * h
    else:
        cx, cy = center
    cx = min(max(cx, hw), w - hw)
    cy = min(max(cy, hh), h - hh)
    a = 1.0 / s
    out = im.transform((W, H), Image.AFFINE, (a, 0, cx - hw, 0, a, cy - hh), resample=Image.BICUBIC)
    return out, (cx - hw, cy - hh, s)


def cutout_white(path, thr=244):
    a = np.asarray(Image.open(path).convert('RGB')).astype(np.int16)
    white = (a.min(2) >= thr) & ((a.max(2) - a.min(2)) <= 10)
    lab, _ = ndimage.label(white)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    edge = edge[edge > 0]
    fg = ~np.isin(lab, edge)
    fg = ndimage.binary_opening(fg, iterations=2)
    lab2, n = ndimage.label(fg)
    if n > 1:
        sizes = ndimage.sum(fg, lab2, range(1, n + 1))
        fg = lab2 == (np.argmax(sizes) + 1)
    fg = ndimage.binary_fill_holes(fg)
    fg = ndimage.binary_erosion(fg, iterations=1)
    al = ndimage.gaussian_filter(fg.astype(np.float32), 0.7)
    ys, xs = np.nonzero(fg)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    rgba = np.dstack([a.astype(np.uint8), (al * 255).astype(np.uint8)])[y0 - 2:y1 + 2, x0 - 2:x1 + 2]
    return Image.fromarray(rgba, 'RGBA')


def contact_shadow(w, strength=130, blur=10, height=28):
    sh = Image.new('L', (w + 80, height + 60), 0)
    ImageDraw.Draw(sh).ellipse([30, 30, w + 50, 30 + height], fill=strength)
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    out = Image.new('RGBA', sh.size, (30, 28, 26, 0))
    out.putalpha(sh)
    return out


def paint_microwave_clock(im):
    """컷 1(ON): 전자레인지 표시창에 켜진 10:00 (DSEG7, #8FE6CF). 컷 2부터는 꺼진 원본."""
    im = im.copy()
    x0, y0, x1, y1 = 442, 975, 457, 984            # S01_comp_v2 표시창(실측)
    sc = 8
    big = Image.new('RGBA', ((x1 - x0) * sc, (y1 - y0) * sc), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    ft = ImageFont.truetype(os.path.join(FONTS, DSEG_B), int((y1 - y0) * sc * 0.78))
    tw = d.textlength('10:00', font=ft)
    d.text(((big.size[0] - tw) / 2, big.size[1] * 0.5), '10:00', font=ft, fill=(0x8F, 0xE6, 0xCF, 235), anchor='lm')
    small = big.resize((x1 - x0, y1 - y0), Image.LANCZOS)
    glow = small.filter(ImageFilter.GaussianBlur(1.6))
    base = im.convert('RGBA')
    base.alpha_composite(with_alpha(glow, 0.8), (x0, y0))
    base.alpha_composite(small, (x0, y0))
    return base.convert('RGB')


def neutralize_phones(im):
    """컷 12-2: 바구니 안 휴대폰과 케이블 커넥터만 블러(출력 기준 6px)로 중립화."""
    s = 1536 / 1080.0
    blurred = im.filter(ImageFilter.GaussianBlur(6 * s))
    m = Image.new('L', im.size, 0)
    d = ImageDraw.Draw(m)
    d.polygon([(0, 1360), (370, 1280), (540, 1160), (650, 1150), (975, 1610), (950, 1720), (820, 1770),
               (810, 1960), (620, 1975), (470, 1995), (300, 1990), (0, 1910)], fill=255)
    for cx, cy, r in [(785, 1148, 60), (1120, 1212, 70), (1300, 1328, 70), (1505, 1565, 75)]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(10))
    return Image.composite(blurred, im, m)


# ================================================================= 클립
class Clip:
    def __init__(self, name):
        self.path = os.path.join(CLIPS, name)
        self.p = None
        self.idx = -1
        self.last = None

    def _open(self):
        if self.p:
            self.p.kill()
        self.p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', self.path, '-f', 'rawvideo',
                                   '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE,
                                  stderr=subprocess.DEVNULL)
        self.idx = -1

    def get(self, i):
        if self.p is None or i < self.idx:
            self._open()
        while self.idx < i:
            buf = self.p.stdout.read(W * H * 3)
            if len(buf) < W * H * 3:
                break
            self.last = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
            self.idx += 1
        return Image.fromarray(self.last)


# ================================================================= 그레이드·그레인
def grade(arr, mode):
    """가벼운 LUT. OFF = 5600K 쿨 뉴트럴, ON = 3000K 웜. 공통: 그림자 #3A3F45 쪽으로 살짝, 하이라이트 롤오프.
    K2: 세피아 기 보정(쿨 시프트 + 채도 -15% + 그림자 #3A3F45 강하게)."""
    x = arr
    sh = np.array([58, 63, 69], np.float32)
    lumw = np.array([0.299, 0.587, 0.114], np.float32)
    if mode == 'ON':
        x = x * np.array([1.035, 1.0, 0.955], np.float32)
    elif mode == 'OFF':
        x = x * np.array([0.985, 1.0, 1.018], np.float32)
        l = x @ lumw
        x = x + (l[..., None] - x) * 0.05
    elif mode == 'K2':
        x = x * np.array([0.955, 0.995, 1.05], np.float32)
        l = x @ lumw
        x = x + (l[..., None] - x) * 0.15
        k2 = (1 - np.clip(x, 0, 255) / 255.0) ** 2 * 0.16
        x = x + (sh - x) * k2
    k = (1 - np.clip(x, 0, 255) / 255.0) ** 3 * 0.07
    x = x + (sh - x) * k
    x = np.where(x > 236, 236 + (x - 236) * 0.62, x)
    return x


class Grain:
    def __init__(self, n=12, sigma=3.6, seed=7):
        rng = np.random.default_rng(seed)
        self.bank = []
        for _ in range(n):
            g = rng.standard_normal((H, W)).astype(np.float32)
            g = ndimage.gaussian_filter(g, 0.65)
            g = g / g.std() * sigma
            self.bank.append(g)

    def apply(self, arr, f, k=1.0):
        g = self.bank[(f * 7) % len(self.bank)]
        l = arr.mean(2) / 255.0
        wgt = (0.45 + 2.2 * l * (1 - l)) * k
        return arr + (g * wgt)[..., None]


# ================================================================= 그래픽 스프라이트
BAR_W, BAR_H = 56, 8


def info_caption(lines, bar_y=230, x=96, size=76, lead=92):
    """제품 정보 자막: Pretendard Bold 76, 자간 -2%, 좌정렬 x96, 위 BI블루 막대 56x8."""
    ft = font(PRET_B, size)
    tr = -0.02 * size
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cap = -ft.getbbox('H', anchor='ls')[1]
    base = bar_y + BAR_H + 40 + cap
    for i, t in enumerate(lines):
        draw_tracked(d, x, base + i * lead, t, ft, C_TEXT + (255,), tr)
    return shadowed(layer)


def bar_sprite(frac, bar_y=230, x=96):
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    w = max(1, int(round(BAR_W * frac)))
    ImageDraw.Draw(layer).rectangle([x, bar_y, x + w - 1, bar_y + BAR_H - 1], fill=C_BI + (255,))
    return layer


def dialogue(lines, baselines, cxs, size=72, rel=PRET_SB, scrim_a=0.40, track=-0.01):
    """대사: Pretendard SemiBold 72, #FBF7F0, 그림자 2중, 줄마다 타원 스크림."""
    ft = font(rel, size)
    tr = track * size
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    sc = Image.new('L', (W, H), 0)
    ds = ImageDraw.Draw(sc)
    for t, bl, cx in zip(lines, baselines, cxs):
        tw = text_width(t, ft, tr)
        draw_tracked(d, cx - tw / 2, bl, t, ft, C_TEXT + (255,), tr)
        ds.ellipse([cx - tw / 2 - 90, bl - size - 50, cx + tw / 2 + 90, bl + 50], fill=255)
    out = shadowed(layer)
    if scrim_a > 0:
        sc = sc.filter(ImageFilter.GaussianBlur(40))
        a = np.asarray(sc).astype(np.float32) / 255.0 * scrim_a
        scr = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        scr.putalpha(Image.fromarray((a * 255).astype(np.uint8)))
        out = Image.alpha_composite(scr, out)
    return out, layer


def boxed_line(text, cx, baseline, size=72, rel=PRET_SB, box=C_DARK, box_a=0.80, pad=(24, 40)):
    """둥근 박스 자막: SemiBold 72, #3A3F45 80% 박스, 패딩 위아래 24 / 좌우 40."""
    ft = font(rel, size)
    tr = -0.01 * size
    tw = text_width(text, ft, tr)
    asc = -ft.getbbox('포', anchor='ls')[1]
    desc = ft.getbbox('…돼', anchor='ls')[3]
    x0 = cx - tw / 2 - pad[1]
    x1 = cx + tw / 2 + pad[1]
    y0 = baseline - asc - pad[0]
    y1 = baseline + max(desc, 8) + pad[0]
    k = 2
    big = Image.new('RGBA', (W * k, H * k), (0, 0, 0, 0))
    ImageDraw.Draw(big).rounded_rectangle([x0 * k, y0 * k, x1 * k, y1 * k], radius=int((y1 - y0) / 2 * k),
                                          fill=box + (int(255 * box_a),))
    layer = big.resize((W, H), Image.LANCZOS)
    d = ImageDraw.Draw(layer)
    draw_tracked(d, cx - tw / 2, baseline, text, ft, C_TEXT + (255,), tr)
    return layer


def outage_caption():
    """'10:00 정전': 시계 숫자는 DSEG7 Classic Bold, '정전'은 Pretendard SemiBold 84. 좌상단 x96."""
    ftk = font(PRET_SB, 84)
    cap = -ftk.getbbox('정', anchor='ls')[1]
    size = 84
    for s in range(50, 110):
        fd = font(DSEG_B, s)
        bb = fd.getbbox('0', anchor='ls')
        if -bb[1] >= cap * 0.98:
            size = s
            break
    fd = font(DSEG_B, size)
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    bl = 382
    x = draw_tracked(d, 96, bl, '10:00', fd, C_TEXT + (255,), 0.01 * size)
    draw_tracked(d, x + 30, bl, '정전', ftk, C_TEXT + (255,), -0.01 * 84)
    return shadowed(layer, s1=(0, 2, 2.0, 0.5), s2=(0, 6, 14.0, 0.38))


def chip_sprite(text, size=46, h=88, padx=38):
    """칩: Pretendard SemiBold 46 흰 글자, #0971CE 알약 h88 r44 (2배로 그려 축소)."""
    k = 2
    ft = font(PRET_SB, size * k)
    tr = -0.01 * size * k
    tw = text_width(text, ft, tr)
    pw, ph = int(tw + 2 * padx * k), h * k
    pad = 24 * k
    im = Image.new('RGBA', (pw + 2 * pad, ph + 2 * pad), (0, 0, 0, 0))
    sh = Image.new('L', im.size, 0)
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 6 * k, pad + pw, pad + ph + 6 * k], radius=ph // 2, fill=90)
    sh = sh.filter(ImageFilter.GaussianBlur(9 * k))
    shl = Image.new('RGBA', im.size, (0, 0, 0, 0))
    shl.putalpha(sh)
    im = Image.alpha_composite(im, shl)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([pad, pad, pad + pw, pad + ph], radius=ph // 2, fill=C_BI + (255,))
    asc = -ft.getbbox('무', anchor='ls')[1]
    draw_tracked(d, pad + padx * k, pad + ph / 2 + asc / 2 - 2 * k, text, ft, (255, 255, 255, 255), tr)
    im = im.resize((im.size[0] // k, im.size[1] // k), Image.LANCZOS)
    return im, pad // k, pw // k, ph // k


# ================================================================= 컷별 준비
class Assets:
    def __init__(self):
        self.s01 = paint_microwave_clock(load(SRC['S01']))
        _img_cache['S12b_neutral'] = neutralize_phones(load(SRC['S12b']))
        # 컷 4: 안내문(타이포 시안 03, 나눔 계열)을 잉크로 빈 A4 위에 곱한다
        nt = Image.open(NOTICE).convert('RGB')
        na = np.asarray(nt).astype(np.float32)
        paper = np.median(na.reshape(-1, 3), axis=0)
        ink = np.clip(na / paper, 0, 1)
        self.ink = Image.fromarray((ink * 255).astype(np.uint8))
        self.a4_src = np.array([[1080, 1053], [1388, 1052], [1389, 1494], [1081, 1494]], np.float32)  # S04_fix 실측
        # 컷 8: 공식 뒷면 컷아웃(화면 높이 40%) + ENV1 블러 배경
        back = cutout_white(BACK)
        sc = 0.40 * H / back.size[1]
        self.back = back.resize((int(back.size[0] * sc), int(back.size[1] * sc)), Image.LANCZOS)
        ba = np.asarray(self.back).astype(np.float32)
        ba[..., :3] *= 0.975
        self.back = Image.fromarray(np.clip(ba, 0, 255).astype(np.uint8), 'RGBA')
        al = np.asarray(self.back.split()[3]).astype(np.float32) / 255
        pad = 60
        alp = np.pad(al, pad)
        sh = ndimage.gaussian_filter(alp, 18) * 0.38
        self.back_sh = Image.new('RGBA', (alp.shape[1], alp.shape[0]), (14, 18, 24, 0))
        self.back_sh.putalpha(Image.fromarray((sh * 255).astype(np.uint8)))
        self.back_pad = pad
        cw = int(self.back.size[0] * 1.1)                       # 접지 그림자: 폭 1.1배, 블러 18, 불투명 35%
        self.back_contact = contact_shadow(cw, strength=int(255 * 0.35), blur=18, height=30)
        self.back_contact_dx = (cw - self.back.size[0]) // 2
        env, _ = view(load(SRC['ENV']), z=1.12)
        env = env.filter(ImageFilter.GaussianBlur(26))
        ea = np.asarray(env).astype(np.float32) * np.array([0.74, 0.77, 0.82], np.float32)
        gy = np.clip((np.arange(H, dtype=np.float32) - H * 0.70) / (H * 0.30), 0, 1)[:, None, None]
        ea = ea * (1 - 0.85 * gy) + np.array([0x6F, 0x6A, 0x64], np.float32) * (0.85 * gy)   # 하단 30% 상판 톤
        self.env = Image.fromarray(np.clip(ea, 0, 255).astype(np.uint8))
        # 컷 19·20 배경
        g = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
        cream = CREAM_TOP * (1 - g) + CREAM_BOT * g
        self.cream = np.repeat(cream, W, axis=1)
        self.cream19 = self.beam_bg()
        bi = Image.open(BI).convert('RGBA')
        bi = bi.crop(bi.getbbox())
        bw = 480
        self.bi = bi.resize((bw, int(round(bi.size[1] * bw / bi.size[0]))), Image.LANCZOS)
        self.bi_y = 1400 - self.bi.size[1] - 4            # 엔딩 블록 -40px: BI 하단 <= 1400
        fr = cutout_white(FRONT)
        self.front19 = fr.resize((int(fr.size[0] * 560 / fr.size[1]), 560), Image.LANCZOS)
        self.front20 = fr.resize((int(fr.size[0] * 520 / fr.size[1]), 520), Image.LANCZOS)   # 문구를 y≈900으로 올리며 축소
        # 텍스트 레이어
        self.cap_outage = outage_caption()
        self.cap_back = info_caption(['전기료 0원 · 무전원'])
        self.cap_filter = info_caption(['필터 셀프 교체'])
        self.kya, kya_t = dialogue(['캬!'], [560], [720], size=80, rel=PRET_B, scrim_a=0.36)
        self.dlg_a, la = dialogue(['목말라'], [980], [835])
        self.dlg_b, lb = dialogue(['정전인데…?'], [600], [560])
        self.ah, ah_t = dialogue(['아…'], [520], [540], size=72, rel=PRET_SB, scrim_a=0.31)
        self.dlg_pot = boxed_line('포트가 안 돼서…', 668, 1060)   # 박스 오른쪽 끝 x<=940, 코드·플러그 피함
        self.chips = [chip_sprite(t) for t in ['무전원', '직수', '셀프 교체', '렌탈료 없음']]
        self.end_l1, self.end_l2, self.end_sub = self.ending_layers()
        self.card = self.card_layer()
        self.s18_last = None
        print('안전영역 검사')
        for n, ly in [('10:00 정전', self.cap_outage), ('정보:무전원', self.cap_back), ('정보:필터', self.cap_filter),
                      ('캬!', kya_t), ('목말라', la), ('정전인데', lb), ('아…', ah_t), ('포트', self.dlg_pot),
                      ('엔딩1', self.end_l1), ('엔딩2', self.end_l2), ('서브', self.end_sub), ('엔드카드', self.card)]:
            bbox_check(n, ly)
        print('  [safe] BI            x %4d-%4d  y %4d-%4d' % (96, 96 + self.bi.size[0], self.bi_y, self.bi_y + self.bi.size[1]))

    def beam_bg(self):
        """컷 19 배경: 크림 + 창빛 사선 그라데이션(#F4EBDD 30%, 스크린)."""
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        ang = math.radians(32)
        d = (xx - 980) * math.cos(ang) + (yy - 120) * math.sin(ang)   # 오른쪽 위 창에서 내려오는 띠
        perp = -(xx - 980) * math.sin(ang) + (yy - 120) * math.cos(ang)
        band = np.exp(-(perp / 210.0) ** 2) * np.clip(1 - d / 1500.0, 0, 1) * np.clip((d + 300) / 300.0, 0, 1)
        base = self.cream * 0.925
        a = base / 255.0
        b = C_BEAM / 255.0
        screen = (1 - (1 - a) * (1 - b)) * 255.0
        return base + (self.cream - base) * band[..., None] + (screen - self.cream) * (0.30 * band)[..., None]

    def ending_layers(self):
        """엔딩: 1행 Noto Serif KR SemiBold 104 #5E636A, 2행 Bold 104 #23272C(SemiBold + 1px 스트로크),
        서브 Pretendard 46 두 줄."""
        out = []
        for text, rel, col, bl, stroke in [('전기가 나가자,', NOTO_SB, C_END1, 964, 0),
                                           ('진짜가 들어왔다.', NOTO_B, C_END2, 1088, 0)]:
            ly = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            draw_tracked(ImageDraw.Draw(ly), 96, bl, text, font(rel, 104), col + (255,), -0.027 * 104, stroke=stroke)
            out.append(ly)
        ly = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ly)
        draw_tracked(d, 98, 1160, '전기료 0원 무전원 직수 정수기,', font(PRET_M, 46), C_SUB + (255,), -0.01 * 46)
        draw_tracked(d, 98, 1218, '퓨리얼 유로체인저', font(PRET_SB, 46), C_END2 + (255,), -0.01 * 46)
        out.append(ly)
        return out

    def card_layer(self):
        """필수 문구 엔드카드: Pretendard Medium 48, 자간 -1%, #3A3F45, 가운데 + PPA-300 정면(공식 (1))."""
        ly = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        fr = self.front20
        fx = (W - fr.size[0]) // 2
        fy = 240
        cs = contact_shadow(fr.size[0] + 10, strength=120, blur=10, height=26)
        ly.alpha_composite(cs, (fx - 35, fy + fr.size[1] - 45))
        ly.alpha_composite(fr, (fx, fy))
        d = ImageDraw.Draw(ly)
        # 필수 문구(원문 그대로, 줄만 나눔): 52px, 가운데, 행간 1.35, 블록 x140~940 / y860~1000
        t = '이 영상은 생성형 AI를 기반으로 제작되었습니다.'
        lines = ['이 영상은 생성형 AI를', '기반으로 제작되었습니다.']
        assert ' '.join(lines) == t
        ft = font(PRET_M, 52)
        cap = -ft.getbbox('이', anchor='ls')[1]
        bl = 862 + cap
        for i, ln in enumerate(lines):
            tw = text_width(ln, ft, -0.01 * 52)
            draw_tracked(d, (W - tw) / 2, bl + i * round(52 * 1.35), ln, ft, C_DARK + (255,), -0.01 * 52)
        return ly


# ================================================================= 프레임 렌더
def lin(f, f0, f1, a, b):
    t = (f - f0) / max(1, (f1 - f0 - 1))
    return lerp(a, b, min(max(t, 0), 1))


def warp_notice(A, frame, org):
    ox, oy, s = org
    q = (A.a4_src - np.array([ox, oy], np.float32)) * s
    qw = q[1, 0] - q[0, 0]
    tex = A.ink.resize((int(qw * 1.25), int(qw * 1.25 * A.ink.size[1] / A.ink.size[0])), Image.LANCZOS)
    tw, th = tex.size
    dst = [(0, 0), (tw, 0), (tw, th), (0, th)]
    M = []
    rhs = []
    for (x, y), (u, v) in zip(q, dst):
        M.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); rhs.append(u)
        M.append([0, 0, 0, x, y, 1, -v * x, -v * y]); rhs.append(v)
    coef = np.linalg.solve(np.array(M, np.float64), np.array(rhs, np.float64))
    ink = tex.transform((W, H), Image.PERSPECTIVE, tuple(coef), resample=Image.BICUBIC, fillcolor=(255, 255, 255))
    ink = ink.filter(ImageFilter.GaussianBlur(0.7))
    a = np.asarray(frame).astype(np.float32) * (np.asarray(ink).astype(np.float32) / 255.0)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def fade_in(f, f0, n=3):
    return min(1.0, (f - f0 + 1) / float(n))


def info_sprites(sp, A, cap, f, f0, f_end=None):
    k = min(1.0, (f - f0) / 4)
    out = 1.0
    if f_end is not None:
        out = min(1.0, max(0.0, (f_end - f) / 3.0))
    if f >= f0 + 0:
        sp.append((bar_sprite(ease_out(k)), out))
        sp.append((cap, k * out, int(round(-12 * (1 - ease_out(k))))))


def render_base(A, clips, f):
    """(PIL RGB, grade mode, sprites[list of (RGBA, alpha, pos)]) 반환."""
    sp = []
    mode = 'OFF'
    b = B
    if f < b['c3']:                                   # 컷 1·2: 같은 구도 연속 줌, '뚝'에서 ON→OFF 플립
        z = lin(f, 0, b['c3'], 1.0, 1.025)
        jolt = {b['c2']: 4, b['c2'] + 1: -2}.get(f, 0)
        if f < b['c2']:
            im, _ = view(A.s01, z, oy=0.0)
            mode = 'ON'
        else:
            im, _ = view(load(SRC['S02']), z, oy=jolt / 1920.0)
            if f >= b['c2'] + 2:
                sp.append((A.cap_outage, 1.0 if f >= b['c2'] + 3 else 0.6))
        return im, mode, sp
    if f < b['c3b']:
        im, _ = view(load(SRC['S03a']), lin(f, b['c3'], b['c3b'], 1.02, 1.04), ox=-0.005)
        return im, mode, sp
    if f < b['c4']:
        im, _ = view(load(SRC['S03b']), lin(f, b['c3b'], b['c4'], 1.03, 1.05), ox=0.01)
        return im, mode, sp
    if f < b['c5']:                                   # 컷 4: 안내문 푸시인(가독성 위해 2.05→2.30)
        t = (f - b['c4']) / (b['c5'] - b['c4'] - 1)
        z = lerp(2.05, 2.30, ease_out(t))
        im, org = view(load(SRC['S04']), z, center=(1234, 1273))
        im = warp_notice(A, im, org)
        return im, mode, sp
    if f < b['c6']:                                   # 컷 5: 대사(화자 옆)
        im = clips['V05'].get(f - b['c5'])            # v4: 영상(줌 없음)
        sp.append((A.dlg_a, fade_in(f, b['c5'])))
        if f >= b['c5'] + 10:
            sp.append((A.dlg_b, fade_in(f, b['c5'] + 10)))
        return im, mode, sp
    if f < b['c7']:                                   # 컷 6: K1
        return clips['K1'].get(f - b['c6']), mode, sp
    if f < b['c8']:                                   # 컷 7: 꽉 찬 컵 -> 빈 컵(펀치인 3%) + 캬!
        z = lin(f, b['c7'], b['c8'], 1.0, 1.03)
        if f < b['c7b']:
            im, _ = view(load(SRC['S07a']), z)
        else:
            im = clips['V07'].get(f - b['c7b'])       # v4: 영상(줌 없음)
            t = (f - b['c7b']) / 4.0
            s = lerp(1.25, 1.0, ease_out(t)) if t < 1 else 1.0
            kya = A.kya if s == 1.0 else A.kya.resize((int(W * s), int(H * s)), Image.LANCZOS)
            cx, cy = 720, 530
            sp.append((kya, fade_in(f, b['c7b'], 2), (int(cx - cx * s), int(cy - cy * s))))
        return im, mode, sp
    if f < b['c9']:                                   # 컷 8: 공식 뒷면(화면 40%) 틸트 다운
        t = ease_io((f - b['c8']) / (b['c9'] - b['c8'] - 1))
        bg = A.env
        bgy = int(round(-40 * t))
        canvas = Image.new('RGB', (W, H))
        canvas.paste(bg, (0, bgy))
        if bgy < 0:
            canvas.paste(bg.crop((0, H + bgy - 1, W, H)), (0, H + bgy - 1))
        cv = canvas.convert('RGBA')
        top = int(round(640 - 130 * t))
        px = 620 - A.back.size[0] // 2
        cv.alpha_composite(A.back_sh, (px + 14 - A.back_pad, top + 22 - A.back_pad))
        cs = A.back_contact
        cv.alpha_composite(cs, (px - 30 - A.back_contact_dx, top + A.back.size[1] - 60))
        cv.alpha_composite(A.back, (px, top))
        if f >= b['c8'] + 1:
            info_sprites(sp, A, A.cap_back, f, b['c8'] + 1)
        return cv.convert('RGB'), mode, sp
    if f < b['c10']:                                  # 컷 9: K2 (세피아 기 재보정)
        return clips['K2'].get(f - b['c9']), 'K2', sp
    if f < b['c11']:                                  # 컷 10: 문 닫힘 -> 열림 ("뚝딱")
        if f < b['c10b']:                             # v4: v10 영상 3.0s(줌 없음)
            return clips['V10'].get(f - b['c10']), mode, sp
        d = f - b['c10b']
        if d < 6:                                     # v4_1: 점프컷 보강 펀치 1.04→1.0 (6프레임)
            z = lerp(1.04, 1.0, ease_out((d + 1) / 6.0))
        else:
            z = lin(f, b['c10b'] + 6, b['c11'], 1.0, 1.02)
        im, _ = view(load(SRC['S10b']), z, ox=-0.004)
        return im, mode, sp
    if f < b['c12']:                                  # 컷 11: S11-1 -> 톡(필터 03 클로즈업) -> 착(S11-2, S11-3) -> 아빠 바스트
        if f < b['c11b']:
            im, _ = view(load(SRC['S11a']), lin(f, b['c11'], b['c11b'], 1.0, 1.02))
        elif f < b['c11c']:
            d = f - b['c11b']
            if d < 4:                                 # 펀치인 4프레임
                z = lerp(1.02, TOK_Z, ease_out((d + 1) / 4.0))
                cx = lerp(540, TOK_CENTER[0], ease_out((d + 1) / 4.0))
                cy = lerp(960, TOK_CENTER[1], ease_out((d + 1) / 4.0))
            else:
                z = lin(f, b['c11b'] + 4, b['c11c'], TOK_Z, TOK_Z * 1.03)
                cx, cy = TOK_CENTER
            im, _ = view(load(SRC['S11a']), z, center=(cx, cy))
        elif f < b['c11d']:
            im, _ = view(load(SRC['S11b']), 1.0)
        elif f < b['c11e']:
            im, _ = view(load(SRC['S11c']), 1.0)
        else:
            z = lerp(BUST_Z[0], BUST_Z[1], ease_io((f - b['c11e']) / (b['c12'] - b['c11e'] - 1)))
            im, _ = view(load(SRC['S10hi']), z, center=BUST_CENTER)
        if f >= b['c11'] + 1 and f < b['c11e']:
            info_sprites(sp, A, A.cap_filter, f, b['c11'] + 1, f_end=b['c11e'])
        return im, mode, sp
    if f < b['c13']:                                  # 컷 12: 패럴랙스 대용(팬+줌), 휴대폰 중립화
        if f < b['c12b']:
            im, _ = view(load(SRC['S12a']), lin(f, b['c12'], b['c12b'], 1.05, 1.065),
                         ox=lin(f, b['c12'], b['c12b'], -0.012, 0.004))
        else:
            im, _ = view(load('S12b_neutral'), lin(f, b['c12b'], b['c13'], 1.06, 1.035),
                         ox=lin(f, b['c12b'], b['c13'], 0.008, -0.004))
        return im, mode, sp
    if f < b['c14']:                                  # 컷 13: 잔 1 -> 2 -> 3, 연속 푸시
        z = lin(f, b['c13'], b['c14'], 1.0, 1.04)
        n = SRC['S13a'] if f < b['c13b'] else (SRC['S13b'] if f < b['c13c'] else SRC['S13c'])
        im, _ = view(load(n), z)
        return im, mode, sp
    if f < b['c15']:                                  # 컷 14: K4 + 플러그 인서트 + 대사 박스
        if f < b['c14b']:
            return clips['K4'].get(K4_SKIP + f - b['c14']), mode, sp
        im = clips['V14'].get(f - b['c14b'])          # v4: 영상(줌 없음)
        sp.append((A.dlg_pot, fade_in(f, b['c14b'])))
        return im, mode, sp
    if f < b['c16']:                                  # 컷 15: K5 (+마지막 프레임 7f 연장), 미세 푸시
        i = min(f - b['c15'], 88)
        im = clips['K5'].get(i)
        z = lin(f, b['c15'], b['c16'], 1.0, 1.025)
        im, _ = view(im, z)
        if f == b['c16'] - 1:
            A.k5_last = im
        return im, mode, sp
    if f < b['c17']:                                  # 컷 16: 전기 복귀(플리커) + 아… -> 리모컨 -> 다시 창빛
        if f < b['c16b']:
            im = clips['V16'].get(f - b['c16'])       # v4: 영상(줌 없음), 첫 3프레임 플리커 유지
            mode = 'ON'
            d = f - b['c16']
            if d == 0:
                im = Image.fromarray(np.clip(np.asarray(im).astype(np.float32) * 1.28 + 10, 0, 255).astype(np.uint8))
            elif d == 1:
                prev = getattr(A, 'k5_last', None)
                if prev is None:
                    prev, _ = view(clips['K5'].get(88), 1.025)
                im = Image.fromarray((np.asarray(prev).astype(np.float32) * 0.82).astype(np.uint8))
                mode = 'OFF'
            elif d == 2:
                im = Image.fromarray((np.asarray(im).astype(np.float32) * 0.9).astype(np.uint8))
            if d >= 4:
                sp.append((A.ah, fade_in(f, b['c16'] + 4, 4)))
        elif f < b['c16c']:
            im, _ = view(load(SRC['S16b']), lin(f, b['c16b'], b['c16c'], 1.02, 1.04))
            mode = 'ON'
        else:
            im, _ = view(load(SRC['S16c']), lin(f, b['c16c'], b['c17'], 1.0, 1.02))
        return im, mode, sp
    if f < b['c18']:                                  # 컷 17: K3
        return clips['K3'].get(f - b['c17']), mode, sp
    if f < b['c19']:                                  # 컷 18: 정면 히어로 풀백 + 칩 4개(박자마다)
        im, _ = view(load(SRC['S18']), lin(f, b['c18'], b['c19'], 1.04, 1.0), ox=0.0)
        if f == b['c19'] - 1:
            A.s18_last = im
        pops = [B['c18'] + 2, F(36.548), F(37.036), F(37.547)]
        y = 230
        for (spr, pad, pw, ph), p0 in zip(A.chips, pops):
            if f >= p0:
                t = (f - p0) / 5.0
                s = lerp(0.86, 1.0, ease_out(t)) if t < 1 else 1.0
                a = min(1.0, (f - p0 + 1) / 3)
                spr2 = spr if s >= 0.999 else spr.resize((max(1, int(spr.size[0] * s)), max(1, int(spr.size[1] * s))), Image.LANCZOS)
                cx = 930 - pw / 2                      # 오른쪽 끝 x930
                cy = y + ph / 2
                sp.append((spr2, a, (int(cx - spr2.size[0] / 2), int(cy - spr2.size[1] / 2))))
            y += ph + 20
        return im, mode, sp
    return None, 'GFX', sp


def render_gfx(A, f):
    """컷 19·20 그래픽 (numpy float)."""
    b = B
    if f < b['c20']:
        src = A.s18_last
        if src is None:
            src, _ = view(load(SRC['S18']), 1.0)
            A.s18_last = src
        if not hasattr(A, 'end_bg'):
            bl = np.asarray(src.filter(ImageFilter.GaussianBlur(40))).astype(np.float32)
            A.end_bg = A.cream19 * 0.94 + bl * 0.06
        d = f - b['c19']
        NT = 4                                        # 블러 전환 4프레임
        if d < NT:
            t = ease_io((d + 1) / float(NT))
            blur = src.filter(ImageFilter.GaussianBlur(40 * t))
            s = np.asarray(blur).astype(np.float32)
            arr = grade(s, 'OFF') * (1 - t) + A.end_bg * t
        else:
            arr = A.end_bg.copy()
        sp = []
        fade_out = 1.0 - max(0, (f - (b['c20'] - 6))) / 6.0
        # 위쪽 1/3: PPA-300 정면(공식 (1)), 오른쪽 1/3
        if d >= NT - 1:
            k = ease_out((d - NT + 2) / 8.0) * fade_out
            fr = A.front19
            fx, fy = 800 - fr.size[0] // 2, 150
            cs = contact_shadow(fr.size[0] + 10, strength=110, blur=9, height=22)
            sp.append((cs, k, (fx - 35, fy + fr.size[1] - 42)))
            sp.append((fr, k, (fx, fy + int(round(12 * (1 - k))))))
        for ly, p0 in [(A.end_l1, b['c19'] + NT + 1), (A.end_l2, F(39.056)), (A.end_sub, F(39.544))]:
            if f >= p0:
                k = ease_out((f - p0 + 1) / 8) * fade_out
                dy = int(round(10 * (1 - ease_out((f - p0 + 1) / 10))))
                sp.append((ly, k, (0, dy)))
        pbi = F(40.44)                                # 마지막 아카펠라 "퓨리얼!"에 BI, 스케일 0.9→1.0
        if f >= pbi:
            t = ease_out((f - pbi + 1) / 6)
            s = lerp(0.90, 1.0, t)
            bi = A.bi if s >= 0.999 else A.bi.resize((int(A.bi.size[0] * s), int(A.bi.size[1] * s)), Image.LANCZOS)
            x = 96 + (A.bi.size[0] - bi.size[0]) // 2
            y = A.bi_y + (A.bi.size[1] - bi.size[1]) // 2
            sp.append((bi, min(1.0, (f - pbi + 1) / 3) * fade_out, (x, y)))
        return arr, sp
    arr = A.cream.copy()
    return arr, [(A.card, 1.0)]


def composite(arr, sprites):
    if not sprites:
        return arr
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert('RGBA')
    for item in sprites:
        spr, a = item[0], item[1]
        pos = (0, 0)
        if len(item) > 2:
            pos = item[2] if isinstance(item[2], tuple) else (item[2], 0)
        if a <= 0:
            continue
        s = with_alpha(spr, a)
        x, y = pos
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(W, x + s.size[0]), min(H, y + s.size[1])
        if x1 <= x0 or y1 <= y0:
            continue
        im.alpha_composite(s.crop((x0 - x, y0 - y, x1 - x, y1 - y)), (x0, y0))
    return np.asarray(im.convert('RGB')).astype(np.float32)


def render_frame(A, clips, grain, f):
    base, mode, sp = render_base(A, clips, f)
    if base is not None:
        arr = grade(np.asarray(base).astype(np.float32), mode)
    else:
        arr, sp = render_gfx(A, f)
    arr = composite(arr, sp)
    arr = grain.apply(arr, f, 0.8 if base is None else 1.0)
    return np.clip(arr + 0.5, 0, 255).astype(np.uint8)


# ================================================================= 오디오
def synth_audio(path):
    sr0, song = wavfile.read(SONG)
    song = song.astype(np.float32) / 32768.0
    assert sr0 == SR
    N = int(NFR / FPS * SR)
    mix = np.zeros((N, 2), np.float32)
    rng = np.random.default_rng(3)

    def put(sig, t0, gain=1.0):
        i0 = int(round(t0 * SR))
        if sig.ndim == 1:
            sig = np.stack([sig, sig], 1)
        i1 = min(N, i0 + len(sig))
        if i1 > i0:
            mix[i0:i1] += sig[:i1 - i0] * gain

    def db(x):
        return 10 ** (x / 20)

    def bandnoise(n, lo, hi):
        x = rng.standard_normal(n).astype(np.float32)
        sos = signal.butter(4, [lo, hi], btype='band', fs=SR, output='sos')
        return signal.sosfilt(sos, x).astype(np.float32)

    def room_ir(rt60, lp=5000):
        nir = int(rt60 * SR)
        ti = np.arange(nir) / SR
        ir = rng.standard_normal((nir, 2)).astype(np.float32) * np.exp(-ti * 6.91 / rt60)[:, None]
        sos = signal.butter(2, lp, btype='low', fs=SR, output='sos')
        ir = signal.sosfilt(sos, ir, axis=0)
        return ir / np.sqrt((ir ** 2).sum(0, keepdims=True))

    def reverb(x, rt60, wet, lp=5000):
        if x.ndim == 1:
            x = np.stack([x, x], 1)
        ir = room_ir(rt60, lp)
        w = np.stack([signal.fftconvolve(x[:, c], ir[:, c]) for c in range(2)], 1).astype(np.float32)
        out = np.zeros_like(w)
        out[:len(x)] += x
        return out + w * wet

    def tv_murmur(dur):
        n = int(dur * SR)
        x = bandnoise(n, 260, 3200)
        t = np.arange(n) / SR
        env = 0.55 + 0.45 * np.sin(2 * np.pi * 4.3 * t + 1.1) * np.sin(2 * np.pi * 1.7 * t + 0.3)
        env *= 0.7 + 0.3 * np.sin(2 * np.pi * 0.9 * t)
        x = x * env
        return x / (np.abs(x).max() + 1e-9)

    # 0.0–0.5 TV 웅성 + 냉장고 웅~
    n0 = int(0.5 * SR)
    t = np.arange(n0) / SR
    hum = (np.sin(2 * np.pi * 60 * t) * 0.5 + np.sin(2 * np.pi * 120 * t) * 0.35 + np.sin(2 * np.pi * 180 * t) * 0.1)
    hum += bandnoise(n0, 40, 400) * 0.6
    hum = hum / np.abs(hum).max()
    put(tv_murmur(0.5) * db(-24), 0.0)
    put(hum * db(-30), 0.0)
    # 0.5 뚝 (차단기): 클릭 + 저역 썸프
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    thump = np.sin(2 * np.pi * (78 - 30 * t) * t) * np.exp(-t / 0.07)
    click = bandnoise(n, 1500, 9000) * np.exp(-t / 0.004)
    put((thump * 0.9 + click * 0.8) * db(-7), 0.5)
    # 냉장고가 꺼지는 소리: 압축기 '덜컥' + 내려가는 웅~ + 짧은 주방 잔향(0.5→약 1.6s)
    n = int(0.55 * SR)
    t = np.arange(n) / SR
    wind = np.sin(2 * np.pi * np.cumsum(60 - 70 * t) / SR) * np.exp(-t / 0.18)
    wind += bandnoise(n, 60, 500) * np.exp(-t / 0.12) * 0.5
    clunk = bandnoise(n, 120, 900) * np.exp(-np.maximum(t - 0.30, 0) / 0.02) * (t >= 0.30) * 0.9
    fridge = reverb((wind + clunk) / 2.0, 0.9, 0.55, lp=3000)
    put(fridge * db(-27), 0.52)
    # 정적 구간 룸톤 (-62 dBFS)
    rt = bandnoise(int(3.6 * SR), 80, 2000)
    rt = rt / np.abs(rt).max()
    fade = np.ones(len(rt), np.float32)
    fade[:2400] = np.linspace(0, 1, 2400)
    put(rt * fade * db(-60), 0.5)
    # 시계 초침(아주 작게): 0.97 ~ 3.97s 사이 1초 간격, 틱/톡 교대
    for i, tt in enumerate([0.97, 1.97, 2.97]):
        n = int(0.06 * SR)
        t = np.arange(n) / SR
        f0 = 3300 if i % 2 == 0 else 2700
        tick = np.sin(2 * np.pi * f0 * t) * np.exp(-t / 0.006) + bandnoise(n, 2500, 8000) * np.exp(-t / 0.0015) * 0.8
        put(reverb(tick, 0.35, 0.25, lp=6000) * db(-24), tt)   # 순간 라우드니스 약 -36 LUFS
    # 4.0 (톡!) 물방울
    n = int(0.25 * SR)
    t = np.arange(n) / SR
    fr = 1500 * np.exp(-t / 0.025) + 520
    ph = 2 * np.pi * np.cumsum(fr) / SR
    tok = np.sin(ph) * np.exp(-t / 0.05) + bandnoise(n, 2000, 8000) * np.exp(-t / 0.003) * 0.4
    put(tok * db(-9), 4.0 - 0.006)
    # 곡: 0.48s부터(0.511 강박 직전), 편집 3.969s 시작. 딩동 구간 -6dB 덕킹 0.4s
    s0 = int(0.48 * SR)
    seg = song[s0:].copy()
    seg[:720] *= np.linspace(0, 1, 720)[:, None]
    td = B['c14'] / FPS
    tseg = np.arange(len(seg)) / SR + 0.48 + OFFSET
    g = np.ones(len(seg), np.float32)
    lo = db(-6)
    a0, a1, b0, b1 = td - 0.03, td, td + 0.40, td + 0.55
    g = np.where((tseg >= a0) & (tseg < a1), 1 + (lo - 1) * (tseg - a0) / 0.03, g)
    g = np.where((tseg >= a1) & (tseg < b0), lo, g)
    g = np.where((tseg >= b0) & (tseg < b1), lo + (1 - lo) * (tseg - b0) / 0.15, g)
    put(seg * g[:, None], 0.48 + OFFSET)
    # 컷 14 딩동(합성 초인종): 띵(E5) - 동(C5), 종 배음
    def bell(freq, dur=1.1):
        n = int(dur * SR)
        t = np.arange(n) / SR
        x = np.zeros(n, np.float32)
        for mult, amp, dec in [(1.0, 1.0, 0.55), (2.0, 0.35, 0.30), (2.76, 0.22, 0.20), (5.4, 0.08, 0.08)]:
            x += amp * np.sin(2 * np.pi * freq * mult * t) * np.exp(-t / dec)
        x *= np.minimum(1, t / 0.003)
        return x / np.abs(x).max()
    dd = np.zeros(int(1.6 * SR), np.float32)
    b1s = bell(659.25)
    b2s = bell(523.25)
    dd[:len(b1s)] += b1s
    o = int(0.42 * SR)
    dd[o:o + len(b2s)] += b2s[:len(dd) - o]
    put(reverb(dd, 0.6, 0.3, lp=7000) * db(-14), td)
    # 엔드카드 잔향: 마지막 아카펠라 "퓨리얼!"을 인공 잔향으로 늘린다
    tail_src = song[int(40.2 * SR):].copy()
    ir = room_ir(2.4, 4500)
    wet = np.stack([signal.fftconvolve(tail_src[:, c], ir[:, c]) for c in range(2)], 1).astype(np.float32)
    tw = np.arange(len(wet)) / SR + 40.2 + OFFSET
    g = np.clip((tw - (41.35 + OFFSET)) / 0.35, 0, 1)
    g *= np.clip((NFR / FPS - 0.05 - tw) / 1.8, 0, 1)
    put(wet * g[:, None] * 0.55, 40.2 + OFFSET)
    # v4_1: 16.54s 점프컷 '착' 클릭(60ms, 곡 대비 -8dB)
    tc = B['c10b'] / FPS
    i0 = int((tc - OFFSET - 0.25) * SR)
    ref = np.sqrt(np.mean(song[i0:i0 + int(0.5 * SR)] ** 2))
    n = int(0.06 * SR)
    t = np.arange(n) / SR
    clk = (np.sin(2 * np.pi * 1850 * t) * np.exp(-t / 0.012) * 0.6
           + bandnoise(n, 1200, 7000) * np.exp(-t / 0.004)
           + np.sin(2 * np.pi * 420 * t) * np.exp(-t / 0.02) * 0.5)
    clk[-int(0.005 * SR):] *= np.linspace(1, 0, int(0.005 * SR))
    clk = clk / np.sqrt(np.mean(clk ** 2)) * ref * db(-8)
    put(clk, tc - 0.004)
    # 컷 16: TV 소리 복귀(곡 아래 작게) -> 아이가 끄면 뚝 끊김
    t16, t16c = B['c16'] / FPS, B['c16c'] / FPS
    put(tv_murmur(t16c - t16) * db(-27), t16)
    n = int(0.05 * SR)
    t = np.arange(n) / SR
    put(bandnoise(n, 1500, 6000) * np.exp(-t / 0.006) * db(-24), t16c)
    mix[-int(0.05 * SR):] *= np.linspace(1, 0, int(0.05 * SR))[:, None]
    raw = path.replace('.wav', '_raw.wav')
    wavfile.write(raw, SR, mix)
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', raw, '-af',
                        'loudnorm=I=-14:TP=-1.0:LRA=11:print_format=json', '-f', 'null', '-'],
                       capture_output=True, text=True, encoding='utf-8', errors='ignore')
    js = r.stderr[r.stderr.rfind('{'):r.stderr.rfind('}') + 1]
    m = json.loads(js)
    af = ('loudnorm=I=-14:TP=-1.0:LRA=11:measured_I={input_i}:measured_TP={input_tp}:measured_LRA={input_lra}:'
          'measured_thresh={input_thresh}:offset={target_offset}:linear=true').format(**m)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', raw, '-af', af, '-ar', str(SR), '-c:a', 'pcm_s16le', path],
                   check=True)
    os.remove(raw)
    return m


# ================================================================= 메인
def cut_of(f):
    for i in range(20):
        if CUT_STARTS[i] <= f < CUT_STARTS[i + 1]:
            return i + 1
    return 20


def contact_frames():
    """컷마다 대표 1프레임 (자막이 다 뜬 시점)."""
    reps = {}
    for i in range(20):
        a, b = CUT_STARTS[i], CUT_STARTS[i + 1]
        reps[i + 1] = max(a, b - 4)
    reps[2] = B['c3'] - 3
    reps[7] = B['c8'] - 3
    reps[11] = B['c11b'] + 10
    reps[14] = B['c15'] - 3
    reps[16] = B['c16b'] - 4
    reps[19] = B['c20'] - 8
    return reps


def make_contact(thumbs, path):
    tw, th, lab = 216, 384, 34
    cols, rows = 5, 4
    sheet = Image.new('RGB', (tw * cols + 6 * (cols + 1), (th + lab) * rows + 6 * (rows + 1) + 60), (24, 26, 29))
    d = ImageDraw.Draw(sheet)
    d.text((10, 16), "A' 정전 점검의 아침 · Aprime_%s · 컷별 대표 프레임 (검수 전)" % VER, font=font(PRET_SB, 26),
           fill=(240, 236, 228))
    for k in range(1, 21):
        f, im = thumbs[k]
        c, r = (k - 1) % cols, (k - 1) // cols
        x = 6 + c * (tw + 6)
        y = 60 + 6 + r * (th + lab + 6)
        sheet.paste(im.resize((tw, th), Image.LANCZOS), (x, y))
        a, b = CUT_STARTS[k - 1] / FPS, CUT_STARTS[k] / FPS
        d.text((x + 4, y + th + 6), 'C%02d  %.2f–%.2f  (f%d)' % (k, a, b, f), font=font(PRET_M, 18),
               fill=(220, 216, 208))
    sheet.save(path)


def main():
    os.makedirs(OUT, exist_ok=True)
    A = Assets()
    clips = {k: Clip(v) for k, v in CLIP.items()}
    grain = Grain()
    if len(sys.argv) > 2 and sys.argv[1] == '--check':
        d = sys.argv[2]
        os.makedirs(d, exist_ok=True)
        for s in sys.argv[3:]:
            f = int(s)
            if f >= B['c19']:
                render_base(A, clips, B['c19'] - 1)
            if B['c16'] <= f < B['c16'] + 3:
                render_base(A, clips, B['c16'] - 1)
            Image.fromarray(render_frame(A, clips, grain, f)).save(os.path.join(d, 'f%04d.png' % f))
        return
    print('frames', NFR, 'dur', NFR / FPS)
    print('cuts', [(i + 1, CUT_STARTS[i], round(CUT_STARTS[i] / FPS, 3)) for i in range(20)])
    wav = os.path.join(OUT, 'Aprime_%s_mix.wav' % VER)
    m = synth_audio(wav)
    print('loudness in', m['input_i'], 'LUFS')
    master = os.path.join(OUT, 'Aprime_%s_master.mp4' % VER)
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (W, H),
           '-r', str(FPS), '-i', '-', '-i', wav,
           '-map', '0:v', '-map', '1:a',
           '-c:v', 'libx264', '-profile:v', 'high', '-preset', 'slow', '-crf', '14', '-pix_fmt', 'yuv420p',
           '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709',
           '-x264-params', 'keyint=48:min-keyint=1',
           '-c:a', 'aac', '-b:a', '192k', '-ar', str(SR),
           '-movflags', '+faststart', '-t', '%.4f' % (NFR / FPS), master]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=open(os.path.join(OUT, '_ffmpeg_%s.log' % VER), 'w'))
    reps = contact_frames()
    thumbs = {}
    for f in range(NFR):
        fr = render_frame(A, clips, grain, f)
        p.stdin.write(fr.tobytes())
        k = cut_of(f)
        if reps.get(k) == f:
            thumbs[k] = (f, Image.fromarray(fr))
        if f % 96 == 0:
            print('frame', f, flush=True)
    p.stdin.close()
    p.wait()
    make_contact(thumbs, os.path.join(OUT, 'Aprime_%s_contact.png' % VER))
    deliver(master, os.path.join(OUT, 'Aprime_%s.mp4' % VER))
    print('done')


def deliver(master, out, kbps=17000):
    """배포본: H.264 high 2패스 약 17Mbps(최대 20Mbps), 오디오 AAC 192k 그대로 복사."""
    log = os.path.join(OUT, '_x264pass')
    base = ['ffmpeg', '-v', 'error', '-y', '-i', master, '-c:v', 'libx264', '-profile:v', 'high', '-preset', 'slow',
            '-b:v', '%dk' % kbps, '-maxrate', '20000k', '-bufsize', '34000k', '-pix_fmt', 'yuv420p',
            '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709',
            '-x264-params', 'keyint=48:min-keyint=1', '-passlogfile', log]
    subprocess.run(base + ['-pass', '1', '-an', '-f', 'mp4', os.devnull], check=True)
    subprocess.run(base + ['-pass', '2', '-c:a', 'copy', '-movflags', '+faststart', out], check=True)
    for fn in os.listdir(OUT):
        if fn.startswith('_x264pass'):
            os.remove(os.path.join(OUT, fn))


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--audio':      # 오디오만 다시 만들어 두 파일에 다시 입힌다(영상 복사)
        wav = os.path.join(OUT, 'Aprime_%s_mix.wav' % VER)
        synth_audio(wav)
        for fn in ['Aprime_%s_master.mp4' % VER, 'Aprime_%s.mp4' % VER]:
            src = os.path.join(OUT, fn)
            tmp = src.replace('.mp4', '_tmp.mp4')
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-i', wav, '-map', '0:v', '-map', '1:a',
                            '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', str(SR),
                            '-movflags', '+faststart', tmp], check=True)
            os.replace(tmp, src)
    elif len(sys.argv) > 1 and sys.argv[1] == '--deliver':
        deliver(os.path.join(OUT, 'Aprime_%s_master.mp4' % VER), os.path.join(OUT, 'Aprime_%s.mp4' % VER))
    else:
        main()
