"""「나, 주연」 영상 렌더러 (본편 16:9 / 숏폼 9:16).
사용: python out/render_video.py main|short [--frames a:b] [--png outdir]   (--png: 지정 프레임만 PNG 저장, 검토용)
출력: out/_work/<mode>_video.mp4 (영상만; 오디오는 build_audio.py 후 mux)
"""
import os, sys, math, functools, subprocess, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
from scipy.interpolate import PchipInterpolator

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ed_timeline import *

ROOT = os.path.dirname(HERE)
FR = os.path.join(HERE, "_work", "frames")
FR_V2 = os.path.join(HERE, "_work", "frames_v2")
CLIP_DIR = {"K1": os.path.join(FR_V2, "K1"), "K2b": os.path.join(FR_V2, "K2b"),
            "K3": os.path.join(FR, "K3"), "K4": os.path.join(FR, "K4")}
V2_STILLS_DIR = os.path.join(HERE, "_work", "v2", "stills")
V2_STILLS = {"C19a", "C19c", "C16c"}
DRAMA_STILLS = {"C04", "C08", "C09", "C10", "C11b", "C12", "C13b", "C14", "C15", "C15b", "C16c", "C17b", "C18",
                "C19a", "C19b", "C19c"}
MAGENTA_STILLS = {"C09", "C10", "C17b"}
SYS_FONT = os.path.join(ROOT, "..", "퓨리얼", "영상부문", "fonts")
F_PRET_B = os.path.join(SYS_FONT, "Pretendard", "Pretendard-Bold.otf")
F_PRET_R = os.path.join(SYS_FONT, "Pretendard", "Pretendard-Regular.otf")
F_HAH_BLACK = os.path.join(HERE, "fonts", "Hahmlet-Black.ttf")
F_HAH_BOLD = os.path.join(HERE, "fonts", "Hahmlet-Bold.ttf")
F_BHS = os.path.join(ROOT, "..", "저작권위원회", "fonts", "BlackHanSans", "BlackHanSans-Regular.ttf")
F_GM_B = os.path.join(ROOT, "fonts", "GmarketSans", "GmarketSansTTFBold.ttf")
F_GM_M = os.path.join(ROOT, "fonts", "GmarketSans", "GmarketSansTTFMedium.ttf")

MODE = "main"
W, H = 1920, 1080
SHORT_MODE = False
S_V = 1920 / 1080.0  # 세로 확대 배율 (608 -> 1080)

CLIP_FPS = 24
CLIP_N = {"K1": 108, "K2b": 108, "K3": 120, "K4": 83}


def set_mode(m):
    global MODE, W, H, SHORT_MODE
    MODE = m
    SHORT_MODE = (m == "short")
    W, H = (1080, 1920) if SHORT_MODE else (1920, 1080)


def segs():
    return SHORT if SHORT_MODE else MAIN


def total_frames():
    return int(round((SHORT_DUR if SHORT_MODE else MAIN_DUR) * FPS))


# ------------------------------------------------------------------ 기본 유틸
def ease_io(u):
    u = min(1, max(0, u))
    return u * u * (3 - 2 * u)


def ease_out(u):
    u = min(1, max(0, u))
    return 1 - (1 - u) ** 3


@functools.lru_cache(maxsize=None)
def font(path, size):
    return ImageFont.truetype(path, size)


def _lum(x):
    return (x * np.array([0.299, 0.587, 0.114], np.float32)).sum(-1, keepdims=True)


def _smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def drama_unify(arr, hl=0.16, rose=0.06):
    """드라마 모드 통일: 하이라이트를 금빛 키(#F2B880 계열)로, 그림자를 장밋빛 림(#E8798A) 쪽으로 살짝."""
    x = arr.astype(np.float32)
    lum = _lum(x)
    L0 = 0.299 * 242 + 0.587 * 184 + 0.114 * 128
    th = _smooth(120, 235, lum) * hl
    x = x * (1 - th) + lum * (np.array([242, 184, 128], np.float32) / L0) * th
    L1 = 0.299 * 232 + 0.587 * 121 + 0.114 * 138
    ts = (1 - _smooth(10, 90, lum)) * rose
    x = x * (1 - ts) + lum * (np.array([232, 121, 138], np.float32) / L1) * ts
    return np.clip(x, 0, 255)


def magenta_reduce(arr, k=0.55):
    """마젠타 쏠림 감소: (R+B)/2 가 G 보다 클 때 그 초과분을 G 쪽으로 이동(휘도 유지)."""
    x = arr.astype(np.float32)
    mag = np.maximum((x[..., 0] + x[..., 2]) / 2 - x[..., 1] - 6, 0)[..., None]
    d = mag * k
    x[..., 1:2] += d * 0.62
    x[..., 0:1] -= d * 0.22
    x[..., 2:3] -= d * 0.40
    return np.clip(x, 0, 255)


def hl_press(arr, amt=0.05):
    x = arr.astype(np.float32)
    return np.clip(x * (1 - amt * _smooth(150, 255, x)), 0, 255)


@functools.lru_cache(maxsize=40)
def load_still(name):
    if name in V2_STILLS:
        path = os.path.join(V2_STILLS_DIR, name + ".png")
    else:
        path = os.path.join(ROOT, "prep", "stills", name + ".png")
    im = Image.open(path).convert("RGB")
    if name in DRAMA_STILLS:
        a = np.asarray(im)
        a = drama_unify(a)
        if name in MAGENTA_STILLS:
            a = magenta_reduce(a)
        im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return im


def load_clip_frame(clip, idx):
    idx = max(1, min(CLIP_N[clip], idx))
    im = Image.open(os.path.join(CLIP_DIR[clip], "%04d.png" % idx)).convert("RGB")
    if clip == "K3":
        im = Image.fromarray(hl_press(np.asarray(im), 0.05).astype(np.uint8))
    return im


def clip_image(clip, ts):
    """소스 시간 ts(초) -> 24fps 프레임 선형 블렌드"""
    x = ts * CLIP_FPS
    i0 = int(math.floor(x))
    a = x - i0
    n = CLIP_N[clip]
    i0c = min(i0, n - 1)
    im0 = load_clip_frame(clip, i0c + 1)
    if a < 0.02 or i0c >= n - 1:
        return im0
    im1 = load_clip_frame(clip, i0c + 2)
    return Image.blend(im0, im1, a)


def seg_index(f):
    ss = segs()
    for i, s in enumerate(ss):
        a = fk(s[2])
        b = fk(s[3]) if s[3] is not None else 10 ** 9
        if a <= f < b:
            return i
    return len(ss) - 1


def seg_cx(o, tl, seg_len):
    """세로 크롭 시작 x. pan=(x0,x1,dur) -> dur 초 동안(ease in-out) 이동, dur=None 이면 컷 전체 동안 ease-out."""
    pan = o.get("pan")
    if pan is None:
        return o.get("cx", 656)
    x0, x1, dur = pan
    if dur is None:
        e = ease_out(tl / max(seg_len, 1e-6))
    else:
        e = ease_io(min(1.0, tl / dur))
    return x0 + (x1 - x0) * e


def seg_start_f(s):
    return fk(s[2])


def seg_end_f(s):
    return fk(s[3]) if s[3] is not None else total_frames()


def opt(s):
    return s[4] if len(s) > 4 else {}


# ------------------------------------------------------------------ 화면 구성
def make_view(img, z=1.0, fx=0.5, fy=0.5, dx=0.0, dy=0.0, cx=656):
    """원본 1920x1080 이미지에서 출력 W,H 뷰를 만든다."""
    if not SHORT_MODE:
        bw, bh = 1920 / z, 1080 / z
        x0 = (1920 - bw) * fx + dx
        y0 = (1080 - bh) * fy + dy
        if z == 1.0 and dx == 0 and dy == 0:
            return img
        return img.resize((1920, 1080), Image.LANCZOS, box=(x0, y0, x0 + bw, y0 + bh))
    bw, bh = 608 / z, 1080 / z
    x0 = cx + (608 - bw) * fx + dx
    y0 = (1080 - bh) * fy + dy
    x0 = min(max(x0, 0), 1920 - bw)
    out = img.resize((1080, 1920), Image.LANCZOS, box=(x0, y0, x0 + bw, y0 + bh))
    return out.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=0))


def hit_params(tl, seg_len):
    """줌히트: 2% 확대 + 4프레임 2px 흔들림 + 1프레임 흰 플래시 30%. 이후 서서히 1.5% 추가 확대"""
    u = tl / max(seg_len, 1e-6)
    z = 1.02 + 0.015 * u
    fidx = int(round(tl * FPS))
    dx = dy = 0.0
    flash = 0.0
    if fidx < 4:
        rnd = random.Random(1000 + fidx)
        dx = rnd.choice([-2, -1, 1, 2]) * 0.0 + rnd.uniform(-2, 2)
        dy = rnd.uniform(-2, 2)
    if fidx == 0:
        flash = 0.30
    return z, dx, dy, flash


def sat_adjust(img, k):
    arr = np.asarray(img).astype(np.float32)
    lum = (arr * np.array([0.299, 0.587, 0.114], np.float32)).sum(2, keepdims=True)
    arr = lum + (arr - lum) * k
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


@functools.lru_cache(maxsize=4)
def vig_texture(w, h):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2) / 1.414
    vig = 1 - 0.40 * np.clip(r, 0, 1) ** 2.2
    rng = np.random.RandomState(7)
    low = rng.rand(h // 8 + 1, w // 8 + 1).astype(np.float32)
    low = np.asarray(Image.fromarray((low * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)).astype(np.float32) / 255
    fine = rng.rand(h, w).astype(np.float32)
    paper = 1 + (low - 0.5) * 0.08 + (fine - 0.5) * 0.04
    return (vig * paper)[..., None]


SEPIA_TARGET = np.array([0xA8, 0x8E, 0x66], np.float32)  # 중간톤 목표 (v3: #A88E66)
SEPIA_MIX_GRAY = 0.30   # 원본에서 채도를 뺀 영상과 70:30
SEPIA_BLACK = 0.0       # v3: 블랙 들어 올림 0
SEPIA_LREF = 124.0      # 입력 중간 밝기 (이 밝기가 중간톤 목표색이 된다)
SEPIA_CONTRAST = 1.12   # v3: 대비 +12%


def sepia_grade(img, s):
    if s <= 0.001:
        return img
    arr = np.asarray(img).astype(np.float32)
    lum = (arr * np.array([0.299, 0.587, 0.114], np.float32)).sum(2, keepdims=True)
    t = (SEPIA_TARGET - SEPIA_MIX_GRAY * SEPIA_LREF) / (1 - SEPIA_MIX_GRAY)
    tinted = SEPIA_BLACK + (lum / SEPIA_LREF) * (t - SEPIA_BLACK)
    sep = (1 - SEPIA_MIX_GRAY) * tinted + SEPIA_MIX_GRAY * lum
    sep = (sep - 128.0) * SEPIA_CONTRAST + 128.0
    sep = np.clip(sep, 0, 255) * vig_texture(img.size[0], img.size[1])
    out = arr * (1 - s) + sep * s
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


# ------------------------------------------------------------------ 글자 레이어
def text_layer(text, fpath, size, fill, stroke=0, stroke_fill=(0, 0, 0), shadow=None):
    """-> (RGBA 이미지, (기준선 중앙 x, 기준선 y)) shadow=(dx,dy,blur,alpha,color)"""
    f = font(fpath, size)
    tw = int(f.getlength(text))
    pad = stroke + 6 + (int(abs(shadow[0]) + abs(shadow[1]) + shadow[2] * 3) if shadow else 0)
    w = tw + pad * 2
    h = int(size * 1.7) + pad * 2
    by = pad + int(size * 1.15)
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if shadow:
        sdx, sdy, sblur, salpha, scol = shadow
        sl = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(sl).text((w / 2 + sdx, by + sdy), text, font=f, fill=scol + (int(255 * salpha),),
                                stroke_width=stroke, stroke_fill=scol + (int(255 * salpha),), anchor="ms")
        if sblur:
            sl = sl.filter(ImageFilter.GaussianBlur(sblur))
        lay = Image.alpha_composite(lay, sl)
    d = ImageDraw.Draw(lay)
    d.text((w / 2, by), text, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill, anchor="ms")
    return lay, (w / 2, by)


def put(base, layer, x, y, alpha=1.0):
    if alpha <= 0:
        return
    if alpha < 1:
        layer = layer.copy()
        a = layer.getchannel("A").point(lambda v: int(v * alpha))
        layer.putalpha(a)
    base.paste(layer, (int(round(x)), int(round(y))), layer)


def put_center(base, layer, cx, cy, alpha=1.0, scale=1.0, rot=0.0):
    if scale != 1.0:
        layer = layer.resize((max(1, int(layer.width * scale)), max(1, int(layer.height * scale))), Image.LANCZOS)
    if rot:
        layer = layer.rotate(rot, resample=Image.BICUBIC, expand=True)
    put(base, layer, cx - layer.width / 2, cy - layer.height / 2, alpha)


def put_text(base, text, fpath, size, fill, cx, baseline, stroke=0, stroke_fill=(0, 0, 0), shadow=None, alpha=1.0,
             scale=1.0, rot=0.0, anchor_left=False):
    lay, (ax, ay) = text_layer(text, fpath, size, fill, stroke, stroke_fill, shadow)
    if anchor_left:
        # cx 를 글자 왼쪽 끝으로 사용
        pad = ax - font(fpath, size).getlength(text) / 2
        put(base, lay, cx - pad, baseline - ay, alpha)
        return
    if rot or scale != 1.0:
        put_center(base, lay, cx, baseline - ay + lay.height / 2, alpha, scale, rot)
    else:
        put(base, lay, cx - ax, baseline - ay, alpha)


def wrap_text(text, fpath, size, maxw):
    f = font(fpath, size)
    if f.getlength(text) <= maxw:
        return [text]
    words = text.split(" ")
    best = None
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        m = max(f.getlength(a), f.getlength(b))
        if best is None or m < best[0]:
            best = (m, [a, b])
    return best[1] if best else [text]


SEPIA_TEXT_CX_SHORT = 590   # 숏폼: 흰 사원증(x 164–267)·목걸이 줄을 피하도록 오른쪽으로
AI_TEXT = "본 영상은 생성형 AI(이미지·영상·음악)를 활용해 제작되었습니다."
AI_MAIN_SIZE, AI_MAIN_X, AI_MAIN_BASE = 30, 96, 1010


def ai_main_bbox():
    """본편 중간 AI 고지의 화면 영역 (x0, y0, x1, y1)"""
    w = font(F_PRET_R, AI_MAIN_SIZE).getlength(AI_TEXT)
    return (AI_MAIN_X, AI_MAIN_BASE - int(AI_MAIN_SIZE * 0.95), AI_MAIN_X + w, AI_MAIN_BASE + int(AI_MAIN_SIZE * 0.25))


def subtitle(base, text, ai_visible=False):
    if SHORT_MODE:
        size, stroke, cx, by, maxw = 64, 6, 480, 1380, 840
    else:
        size, stroke, cx, by, maxw = 54, 6, 960, 1000, 1728
    lines = wrap_text(text, F_PRET_B, size, maxw)
    lead = int(size * 1.32)
    if ai_visible and not SHORT_MODE:
        # AI 고지와 가로로 겹치는 자막은 40px 이상 위로 띄운다
        f = font(F_PRET_B, size)
        sw = max(f.getlength(l) for l in lines) + 2 * stroke
        ax0, ay0, ax1, ay1 = ai_main_bbox()
        if cx - sw / 2 < ax1 + 40:
            by = min(by, ay0 - 40 - int(size * 0.3) - stroke)
    for i, ln in enumerate(lines):
        y = by - (len(lines) - 1 - i) * lead
        put_text(base, ln, F_PRET_B, size, (255, 255, 255, 255), cx, y, stroke=stroke, stroke_fill=(0, 0, 0, 255))


def ai_notice(base, mode="mid", alpha=1.0):
    if mode == "end":
        if SHORT_MODE:
            size = 34
            lines = ["본 영상은 생성형 AI(이미지·영상·음악)를", "활용해 제작되었습니다."]
            for i, ln in enumerate(lines):
                put_text(base, ln, F_PRET_R, size, (255, 255, 255, 190), 540, 1170 + i * 46,
                         shadow=(0, 1, 3, 0.8, (0, 0, 0)), alpha=alpha)
        else:
            put_text(base, AI_TEXT, F_PRET_R, 28, (255, 255, 255, 178), 960, 1030, shadow=(0, 1, 3, 0.8, (0, 0, 0)), alpha=alpha)
    elif SHORT_MODE:
        size = 36
        lines = ["본 영상은 생성형 AI(이미지·영상·음악)를", "활용해 제작되었습니다."]
        bar = Image.new("RGBA", (1000, 108), (0, 0, 0, int(255 * 0.55)))
        put(base, bar, 40, 1408, alpha)
        for i, ln in enumerate(lines):
            put_text(base, ln, F_PRET_R, size, (255, 255, 255, 190), 60, 1452 + i * 46, shadow=(0, 1, 3, 0.6, (0, 0, 0)),
                     alpha=alpha, anchor_left=True)
    else:
        put_text(base, AI_TEXT, F_PRET_R, AI_MAIN_SIZE, (255, 255, 255, 178), AI_MAIN_X, AI_MAIN_BASE,
                 shadow=(0, 1, 3, 0.9, (0, 0, 0)), alpha=alpha, anchor_left=True)


# ------------------------------------------------------------------ 로고 / 버그 / 명찰
@functools.lru_cache(maxsize=1)
def logo_src():
    im = Image.open(os.path.join(ROOT, "assets", "highlighttv_logo.png")).convert("RGBA")
    return im.crop((257, 369, 1664, 711))  # 1407x342


@functools.lru_cache(maxsize=64)
def logo_w(width):
    src = logo_src()
    h = int(round(width * src.height / src.width))
    return src.resize((int(width), h), Image.LANCZOS)


def with_alpha(layer, a):
    layer = layer.copy()
    layer.putalpha(layer.getchannel("A").point(lambda v: int(v * a)))
    return layer


def glint_on(layer, pos, strength=0.9, band=0.22):
    """레이어 위에 흰 글린트를 얹는다. pos 0..1 (대각선 이동). 로고 알파를 약간 번지게 한 곳에만."""
    w, h = layer.size
    pad = 10
    big = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    big.paste(layer, (pad, pad))
    a = big.getchannel("A")
    soft = a.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(4))
    sw, sh = big.size
    yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32)
    d = (xx + yy * 0.6) / (sw + sh * 0.6)
    bandm = np.exp(-((d - (-0.2 + pos * 1.4)) / band * 2) ** 2) * strength
    ga = (np.asarray(soft).astype(np.float32) / 255 * bandm * 255).clip(0, 255).astype(np.uint8)
    white = Image.new("RGBA", big.size, (255, 255, 255, 255))
    white.putalpha(Image.fromarray(ga))
    return Image.alpha_composite(big, white)


def bug_layer(width, opacity=0.85, shadow=False, rot=0.0, glint=None, soft=False):
    lg = with_alpha(logo_w(int(round(width))), opacity)
    if glint is not None:
        lg = glint_on(lg, glint)
    if soft:  # 그림자 0 2px 6px 검정 40% (숏폼 버그 가독성). soft=(알파, 시그마) 로 세기 조절
        sa, ss = soft if isinstance(soft, tuple) else (0.40, 3.0)
        pad = 24
        base_ = Image.new("RGBA", (lg.width + 2 * pad, lg.height + 2 * pad), (0, 0, 0, 0))
        blk = Image.new("RGBA", lg.size, (0, 0, 0, 255))
        blk.putalpha(lg.getchannel("A").point(lambda v: int(v * sa)))
        sh_ = Image.new("RGBA", base_.size, (0, 0, 0, 0))
        sh_.paste(blk, (pad, pad + 2), blk)
        sh_ = sh_.filter(ImageFilter.GaussianBlur(ss))
        base_ = Image.alpha_composite(base_, sh_)
        base_.paste(lg, (pad, pad), lg)
        lg = base_
    if shadow:
        pad = 24
        base = Image.new("RGBA", (lg.width + 2 * pad, lg.height + 2 * pad), (0, 0, 0, 0))
        sh = Image.new("RGBA", base.size, (0, 0, 0, 0))
        sh_a = lg.getchannel("A")
        blk = Image.new("RGBA", lg.size, (0, 0, 0, 255))
        blk.putalpha(sh_a.point(lambda v: int(v * 0.5)))
        sh.paste(blk, (pad, pad + 8), blk)
        sh = sh.filter(ImageFilter.GaussianBlur(4))
        base = Image.alpha_composite(base, sh)
        base.paste(lg, (pad, pad), lg)
        lg = base
    if rot:
        lg = lg.rotate(rot, resample=Image.BICUBIC, expand=True)
    return lg


@functools.lru_cache(maxsize=64)
def plate_img(scale100):
    """둥근 사각형 190x64 명찰 판 (#1A1A22, 금색 2px #E2B04A), 안쪽 흰 로고 너비 150."""
    sc = scale100 / 100.0
    ss = 3
    w, h = int(190 * sc * ss), int(64 * sc * ss)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    r = int(14 * sc * ss)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=(0xE2, 0xB0, 0x4A, 255))
    bw = max(2, int(2 * sc * ss))
    d.rounded_rectangle([bw, bw, w - 1 - bw, h - 1 - bw], radius=max(1, r - bw), fill=(0x1A, 0x1A, 0x22, 255))
    im = im.resize((int(190 * sc), int(64 * sc)), Image.LANCZOS)
    return im


def sparkle_layer(size, k):
    """4각 별 반짝임. k 0..1..0"""
    s = int(size)
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = s / 2
    L = c * k
    t = max(1.0, s * 0.06 * k)
    d.polygon([(c, c - L), (c + t, c - t), (c + L, c), (c + t, c + t), (c, c + L), (c - t, c + t), (c - L, c), (c - t, c - t)],
              fill=(255, 250, 225, 255))
    glow = im.filter(ImageFilter.GaussianBlur(s * 0.06))
    out = Image.alpha_composite(glow, im)
    return out


# ------------------------------------------------------------------ 타이틀 / 로어서드 / 캡션 / 라벨
@functools.lru_cache(maxsize=8)
def title_layer(size):
    text = "나, 주연"
    f = font(F_HAH_BLACK, size)
    tw = int(f.getlength(text))
    pad = 40
    w, h = tw + 2 * pad, int(size * 1.6) + 2 * pad
    by = pad + int(size * 1.15)
    # 마스크
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).text((w / 2, by), text, font=f, fill=255, anchor="ms")
    # 그라데이션 (세로) 글자 높이 기준
    top, bot = by - int(size * 0.95), by + int(size * 0.25)
    ys = np.arange(h, dtype=np.float32)
    t = np.clip((ys - top) / max(bot - top, 1), 0, 1)
    c1, c2, c3 = np.array([0xFF, 0xF1, 0xC1], np.float32), np.array([0xE2, 0xB0, 0x4A], np.float32), np.array([0x9C, 0x6B, 0x1E], np.float32)
    col = np.where(t[:, None] < 0.5, c1 + (c2 - c1) * (t[:, None] / 0.5), c2 + (c3 - c2) * ((t[:, None] - 0.5) / 0.5))
    grad = np.repeat(col[:, None, :], w, axis=1).astype(np.uint8)
    gimg = Image.fromarray(grad, "RGB").convert("RGBA")
    gimg.putalpha(mask)
    # 외곽선 3px + 그림자 8px 60%
    st = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(st).text((w / 2, by), text, font=f, fill=(0x3B, 0x2A, 0x1A, 255), stroke_width=3, stroke_fill=(0x3B, 0x2A, 0x1A, 255), anchor="ms")
    sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sh_a = st.getchannel("A").point(lambda v: int(v * 0.6))
    blk = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    blk.putalpha(sh_a)
    sh.paste(blk, (0, 8), blk)
    sh = sh.filter(ImageFilter.GaussianBlur(4))
    out = Image.alpha_composite(sh, st)
    out = Image.alpha_composite(out, gimg)
    return out, (w / 2, by), mask


def title_frame(base, tl, cx, baseline):
    size = 160 if SHORT_MODE else 180
    lay, (ax, ay), mask = title_layer(size)
    # 0.2초 빛 스윕 (등장 직후)
    sweep_t = (tl - 0.12) / 0.2
    if 0 <= sweep_t <= 1:
        w, h = lay.size
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        d = (xx + yy * 0.5) / (w + h * 0.5)
        bandm = np.exp(-((d - (-0.15 + sweep_t * 1.3)) / 0.12) ** 2)
        ga = (np.asarray(mask).astype(np.float32) / 255 * bandm * 230).clip(0, 255).astype(np.uint8)
        wh = Image.new("RGBA", (w, h), (255, 255, 255, 255))
        wh.putalpha(Image.fromarray(ga))
        lay = Image.alpha_composite(lay, wh)
    pop = 1.0
    if tl < 0.12:
        pop = 1.0 + 0.10 * (1 - tl / 0.12)
    if pop != 1.0:
        l2 = lay.resize((int(lay.width * pop), int(lay.height * pop)), Image.LANCZOS)
        put(base, l2, cx - ax * pop, baseline - ay * pop)
    else:
        put(base, lay, cx - ax, baseline - ay)


def lowerthird(base, tl):
    l1, l2 = "나주연(49) · 경리과장", "일일드라마 시청 25년차"
    s1, s2 = (44, 36) if SHORT_MODE else (40, 32)
    f1, f2 = font(F_GM_B, s1), font(F_GM_M, s2)
    w = int(max(f1.getlength(l1), f2.getlength(l2))) + 56
    h = s1 + s2 + 44
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rectangle([0, 0, w, h], fill=(0, 0, 0, 153))
    d.text((28, 22 + s1 - 4), l1, font=f1, fill=(255, 255, 255, 255), anchor="ls")
    d.text((28, 22 + s1 - 4 + 8 + s2 + 4), l2, font=f2, fill=(255, 255, 255, 255), anchor="ls")
    x0, y0 = (60, 1240) if SHORT_MODE else (96, 822)
    x = x0
    if tl < 0.25:
        x = x0 - (w + x0) * (1 - ease_out(tl / 0.25))
    put(base, lay, x, y0)


def pop_scale(tl, dur=0.15, peak=1.2):
    if tl < 0:
        return 0.0
    if tl >= dur:
        return 1.0
    return peak + (1.0 - peak) * (tl / dur)


def byeongmat_caption(base, text, cx, cy, tl, size=None):
    size = size or (72 if SHORT_MODE else 64)
    sc = pop_scale(tl)
    if sc <= 0:
        return
    put_text(base, text, F_BHS, size, (0xFF, 0xE1, 0x4D, 255), cx, cy, stroke=7, stroke_fill=(0, 0, 0, 255), scale=sc, rot=4.0 * 1.0)


def label_tag(base, text, tip_xy, tag_cy, tl):
    """흰 둥근 태그 + 3px 화살표선 (tip_xy: 가리킬 점, 16:9 좌표를 이미 출력 좌표로 변환한 값)"""
    sc = pop_scale(tl, 0.2, 1.15)
    if sc <= 0:
        return
    size = 44 if not SHORT_MODE else 52
    f = font(F_GM_B, size)
    tw = int(f.getlength(text))
    padx, pady = 22, 12
    w, h = tw + padx * 2, int(size * 1.25) + pady
    ss = 2
    lay = Image.new("RGBA", (w * ss, (h + 60) * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle([0, 0, w * ss - 1, h * ss - 1], radius=14 * ss, fill=(255, 255, 255, 255))
    d.text((w * ss / 2, (h * 0.5 + size * 0.36) * ss), text, font=font(F_GM_B, size * ss), fill=(0, 0, 0, 255), anchor="ms")
    # 화살표선 (태그 아래 중앙에서 아래로)
    cxl = w * ss / 2
    d.line([(cxl, h * ss), (cxl, (h + 40) * ss)], fill=(255, 255, 255, 255), width=3 * ss)
    d.polygon([(cxl - 9 * ss, (h + 34) * ss), (cxl + 9 * ss, (h + 34) * ss), (cxl, (h + 54) * ss)], fill=(255, 255, 255, 255))
    lay = lay.resize((w, h + 60), Image.LANCZOS)
    tipx, tipy = tip_xy
    x = tipx - w / 2
    y = tipy - (h + 56)
    if sc != 1.0:
        lay = lay.resize((int(lay.width * sc), int(lay.height * sc)), Image.LANCZOS)
        x = tipx - lay.width / 2
        y = tipy - lay.height + 4
    shd = Image.new("RGBA", lay.size, (0, 0, 0, 0))
    put(base, lay, x, y)


def rating_circle(base, tl):
    d = 64
    ss = 3
    im = Image.new("RGBA", (d * ss, d * ss), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    dr.ellipse([0, 0, d * ss - 1, d * ss - 1], fill=(255, 255, 255, 255))
    dr.text((d * ss / 2, d * ss / 2 + 12 * ss), "15", font=font(F_GM_B, 34 * ss), fill=(0, 0, 0, 255), anchor="ms")
    im = im.resize((d, d), Image.LANCZOS)
    put(base, im, 96, 54)


# ------------------------------------------------------------------ 엔드카드
def end_frame(tl):
    base = Image.new("RGB", (W, H), (0x12, 0x10, 0x17))
    if SHORT_MODE:
        cx, copy_cy, size, logo_w_px, logo_cy = 540, 640, 72, 820, 900
    else:
        cx, copy_cy, size, logo_w_px, logo_cy = 960, 330, 76, 760, 600
    # 카피 (0.4초 페이드)
    a = min(1.0, max(0.0, (tl - 0.25) / 0.4))
    lead = int(size * (1.38 if SHORT_MODE else 1.35))
    for i, ln in enumerate(["당신의 내일도,", "다음 회가 기다려지게."]):
        by = copy_cy - lead / 2 + i * lead + size * 0.35
        put_text(base, ln, F_HAH_BOLD, size, (255, 255, 255, 255), cx, by, alpha=a, shadow=(0, 3, 4, 0.35, (0, 0, 0)))
    # 로고 (1.0초 뒤 0.3초 페이드 + 글린트)
    la = min(1.0, max(0.0, (tl - 1.0) / 0.3))
    if la > 0:
        lg = logo_w(logo_w_px)
        g = (tl - 1.35) / 0.5
        lay = lg
        if 0 <= g <= 1:
            lay = glint_on(lg, g, strength=0.9, band=0.2)
            ox = (lay.width - lg.width) // 2
        else:
            ox = 0
        put_center(base, lay, cx, logo_cy, la)
    ai_notice(base, "end")
    return base


# ------------------------------------------------------------------ K4 합성
HAND_KF = [(0.875, 1390, 424), (1.125, 1421, 294), (1.25, 1470, 179), (1.375, 1487, 78), (1.5, 1479, 43),
           (1.625, 1413, 14), (1.75, 1433, 29), (1.875, 1421, 58), (2.0, 1384, 72), (2.125, 1315, 187),
           (2.25, 1147, 369), (2.375, 1095, 455), (2.5, 1060, 540), (3.0, 1040, 555)]
_hx = PchipInterpolator([k[0] for k in HAND_KF], [k[1] for k in HAND_KF])
_hy = PchipInterpolator([k[0] for k in HAND_KF], [k[2] for k in HAND_KF])
P_CHEST = (1040, 555)
TAU_GRAB0, TAU_SNATCH0, TAU_SNATCH1, TAU_ATTACH = 1.30, 1.42, 1.58, 2.50


def k4_map(x, y):
    if not SHORT_MODE:
        return x, y
    cx = 850
    return (x - cx) * S_V, y * S_V


def k4_scale():
    return S_V if SHORT_MODE else 1.0


BUG_X_MAIN = 1614
SHORT_BUG_X, SHORT_BUG_Y, SHORT_BUG_W = 740, 260, 200   # v3 엄격 기준: 오른쪽 끝 <=940, y>=260
BOX_XMAX, BOX_YMIN = 940, 250                           # K4 비행 경로 제한(판 포함, 회전 후 바운딩 박스)
TILT_MAX = 6.0


def bug_bar_alpha(t, a=17.1, b=21.0, f=0.2):
    if t < a or t >= b:
        return 0.0
    return min(1.0, (t - a) / f, (b - t) / f)


def bug_soft(t):
    """숏폼 버그 그림자: 밝은 블라인드 구간(17.1–21.0s)에서는 0 2px 10px 검정 60%"""
    if 17.1 <= t < 21.0:
        return (0.60, 5.0)
    return (0.40, 3.0)


def bug_origin():
    return (SHORT_BUG_X + SHORT_BUG_W / 2, SHORT_BUG_Y + SHORT_BUG_W * 342 / 1407 / 2) if SHORT_MODE else (BUG_X_MAIN + 105.0, 44 + 25.5)


def plate_scale():
    return 1.4 if SHORT_MODE else 1.0


def clamp_short(cx, cy, wdt, pa, tau, hand_dx, hand_dy):
    """숏폼: 명찰/버그(판 포함) 경로를 회전 후 바운딩 박스 기준 x<=940, y>=250 안으로 제한.
    손끝이 밖이면 손 쪽으로 기울며(최대 6도) 떨리다 손이 들어오면 따라붙음."""
    PS = plate_scale()
    w = max(wdt, 190 * PS) if pa > 0.001 else wdt   # 판은 알파만 변하고 크기는 일정
    h = max(wdt * 342 / 1407, 64 * PS) if pa > 0.001 else wdt * 342 / 1407
    # 1차: 회전 없이 clamp 해서 손끝이 밖인지 판단
    out_x, out_y = cx - (BOX_XMAX - w / 2), (BOX_YMIN + h / 2) - cy
    outside = max(out_x, out_y)
    rot = 0.0
    if outside > 3:
        side = -1.0 if out_x > 0 else 1.0
        rot = side * (TILT_MAX - 1.5) + 1.5 * math.sin(tau * 70.0)   # 합계 |rot| <= 6
        rot = max(-TILT_MAX, min(TILT_MAX, rot))
    th = math.radians(abs(rot))
    bw_ = w * math.cos(th) + h * math.sin(th)
    bh_ = w * math.sin(th) + h * math.cos(th)
    mg = 12  # 그림자·글로우 여유
    cxc = min(cx, BOX_XMAX - mg - bw_ / 2)
    cyc = max(cy, BOX_YMIN + mg + bh_ / 2)
    return cxc, cyc, rot


def bug_width():
    return SHORT_BUG_W if SHORT_MODE else 210


def bug_state(tau, sub=0.0):
    """K4 로컬 시간 tau에서 명찰 그래픽의 상태: (cx, cy, 판_알파, 로고너비, 그림자, 회전, 글린트)"""
    tau = tau + sub
    ox, oy = bug_origin()
    BW = bug_width()
    S = k4_scale()
    if tau < TAU_SNATCH0:
        rot = 0.0
        if tau >= TAU_GRAB0:
            fr = int((tau - TAU_GRAB0) * FPS)
            rot = ([6, -6, 4, -3] if not SHORT_MODE else [4, -4, 3, -2])[min(fr, 3)] if fr < 4 else 0
        return ox, oy, 0.0, BW, False, rot, None
    hand = lambda t: k4_map(float(_hx(min(t, 3.0))), float(_hy(min(t, 3.0))))
    off = lambda t: (0 * S, 30 * S)
    off_end = (-20 * S, 15 * S)

    def ride(t):
        hx, hy = hand(t)
        u = ease_io((t - 1.6) / 0.9)
        dx = (0 * (1 - u) + off_end[0] * u)
        dy = (30 * S * (1 - u) + off_end[1] * u)
        return hx + dx, hy + dy


    PS = plate_scale()
    if tau < TAU_SNATCH1:
        u = ease_io((tau - TAU_SNATCH0) / (TAU_SNATCH1 - TAU_SNATCH0))
        rx, ry = ride(tau)
        cx, cy = ox + (rx - ox) * u, oy + (ry - oy) * u
        wdt = BW * (1 + 0.2 * u)
        rot = 0.0
        if SHORT_MODE:
            cx, cy, rot = clamp_short(cx, cy, wdt, 0.0, tau, rx - cx, ry - cy)
        return cx, cy, 0.0, wdt, True, rot, None
    if tau < TAU_ATTACH:
        cx, cy = ride(tau)
        pa = ease_io((tau - 1.8) / 0.5)
        wdt = BW * 1.2 + (150 * PS - BW * 1.2) * pa
        rot = 0.0
        if SHORT_MODE:
            cx, cy, rot = clamp_short(cx, cy, wdt, pa, tau, 0, 0)
        return cx, cy, pa, wdt, True, rot, None
    cx, cy = k4_map(*P_CHEST)
    return cx, cy, 1.0, 150 * PS, False, 0.0, None


def draw_bug_state(base, st):
    cx, cy, pa, wdt, shadow, rot, gl = st
    S = plate_scale()
    if pa > 0:
        pl = plate_img(int(round(S * 100)))
        # 그림자
        if shadow:
            pad = 24
            sh = Image.new("RGBA", (pl.width + 2 * pad, pl.height + 2 * pad), (0, 0, 0, 0))
            blk = Image.new("RGBA", pl.size, (0, 0, 0, 255))
            blk.putalpha(pl.getchannel("A").point(lambda v: int(v * 0.5 * pa)))
            sh.paste(blk, (pad, pad + int(8 * S)), blk)
            sh = sh.filter(ImageFilter.GaussianBlur(4 * S))
            put_center(base, sh, cx, cy)
        put_center(base, pl, cx, cy, pa)
        lg = bug_layer(wdt, opacity=1.0, shadow=False, rot=rot)
        put_center(base, lg, cx, cy, 1.0)
    else:
        if SHORT_MODE:
            lg = bug_layer(wdt, opacity=1.0, shadow=shadow, rot=rot, glint=gl, soft=not shadow)
        else:
            lg = bug_layer(wdt, opacity=0.85, shadow=shadow, rot=rot, glint=gl)
        put_center(base, lg, cx, cy)


def k4_overlay(base, tau):
    moving = (TAU_SNATCH0 - 0.05 <= tau <= TAU_SNATCH1 + 0.05) or (2.0 <= tau <= TAU_ATTACH + 0.02)
    if tau < TAU_SNATCH0 - 0.05 or not moving:
        draw_bug_state(base, bug_state(tau))
    else:
        # 모션 블러: 하위 프레임 14장 평균 (셔터 180도)
        acc = None
        n = 14
        for i in range(n):
            sub = (-0.5 + (i + 0.5) / n) * (1.0 / FPS) * 0.5
            lay = Image.new("RGBA", base.size, (0, 0, 0, 0))
            tmp = Image.new("RGB", base.size, (0, 0, 0))
            # 알파 누적을 위해 흑/백 두 배경에 그려 알파 복원
            blk = Image.new("RGB", base.size, (0, 0, 0))
            wht = Image.new("RGB", base.size, (255, 255, 255))
            st = bug_state(tau, sub)
            draw_bug_state(blk, st)
            draw_bug_state(wht, st)
            b = np.asarray(blk).astype(np.float32)
            w = np.asarray(wht).astype(np.float32)
            a = 1 - (w - b).mean(2) / 255.0
            a = np.clip(a, 0, 1)
            rgb = b / np.maximum(a[..., None], 1e-3)
            pm = np.concatenate([b, a[..., None] * 255], axis=2)
            acc = pm if acc is None else acc + pm
        acc /= n
        a = np.clip(acc[..., 3:4] / 255.0, 0, 1)
        premul = acc[..., :3]
        under = np.asarray(base).astype(np.float32)
        out = under * (1 - a) + premul
        base.paste(Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)))
    # 부착 반짝임
    if TAU_ATTACH <= tau < TAU_ATTACH + 0.4:
        k = math.sin(math.pi * (tau - TAU_ATTACH) / 0.4)
        S = plate_scale()
        cx, cy, *_ = bug_state(TAU_ATTACH + 0.1)
        sp = sparkle_layer(int(150 * S), k)
        put_center(base, sp, cx + 80 * S, cy - 26 * S)


# ------------------------------------------------------------------ 프레임 합성
def tr(x, y, cx):
    """16:9 좌표 -> 출력 좌표 (세로는 크롭 변환)"""
    if not SHORT_MODE:
        return x, y
    return (x - cx) * S_V, y * S_V


def bug_on_intervals():
    if not SHORT_MODE:
        return [(tk(19), tk(80)), (tk(88), None)]
    return [(tk(19.5), None)]


def render_frame(f):
    ss = segs()
    i = seg_index(f)
    s = ss[i]
    name, kind = s[0], s[1]
    o = opt(s)
    f0, f1 = seg_start_f(s), seg_end_f(s)
    tl = (f - f0) / FPS
    seg_len = (f1 - f0) / FPS
    t = f / FPS
    cx_crop = o.get("cx", 656)
    sat_k = 1.0

    # ---------- 베이스
    if kind == "black":
        base = render_base_only(i, tl_override=tl)
    elif kind == "end":
        base = end_frame(tl)
        if tl < 0.3:  # K4 마지막 프레임 -> 엔드카드 디졸브
            prev = render_frame(f0 - 1)
            base = Image.blend(prev, base, ease_io(tl / 0.3))
    else:
        base = render_base_only(i, tl_override=tl)
        if o.get("sat_hit") is not None and t >= tk(o["sat_hit"]):
            k = 1 + 0.2 * ease_io((t - tk(o["sat_hit"])) / 0.2)
            base = sat_adjust(base, k)
    if kind in ("still", "clip"):
        # C08 크로스페이드 (회색 -> 금빛)
        xf = o.get("xfade")
        if xf and tl < xf:
            prev = render_base_only(i - 1, tl_override=None, t_clamp_end=True)
            base = Image.blend(prev, base, ease_io(tl / xf))
        # 줌히트 흰 플래시
        if o.get("fx") == "hit":
            _, _, _, flash = hit_params(tl, seg_len)
            if flash:
                base = Image.blend(base, Image.new("RGB", base.size, (255, 255, 255)), flash)
        # 세피아 (K4: 부착 시점에서 0.4초에 걸쳐 원색 복귀)
        if o.get("sepia"):
            if name == "K4":
                sa = 1 - ease_io((tl - TAU_ATTACH) / 0.4)
            else:
                sa = 1.0
            base = sepia_grade(base, sa)

    base = base.convert("RGB")

    # ---------- 오버레이
    kk = (lambda k: tk(k))
    cx_now = seg_cx(o, tl, seg_len)
    if not SHORT_MODE:
        ai_vis = kk(1) <= t < kk(21)   # AI 고지(중간): 0.6s ~ C08 끝
        if ai_vis:
            ai_notice(base)
        if name == "C04":
            title_frame(base, tl, 1400, 905)
        subs = {"C05": "나 과장, 커피.", "C09": "정신 차려, 나 과장!", "C10": "물벼락, 미리 봤습니다.",
                "C11b": "이 돈 받고, 떠나요.", "C14": "…영수증 첨부해 주세요.", "C16c": "어디서 감히!",
                "C17b": "아까운 김치를 왜.", "C20": "과장님 거예요."}
        if name in subs:
            subtitle(base, subs[name], ai_visible=ai_vis)
        if name == "C06b" and tl >= 0.5:
            label_tag(base, "행인 3", (1644, 275), 215, tl - 0.5)
        if name == "C07" and tl >= 0.3:
            lowerthird(base, tl - 0.3)
        if name == "C10":
            byeongmat_caption(base, "(일일드라마 시청 25년차)", 1420, 210, tl)
        if name == "C17b":
            byeongmat_caption(base, "(시청 25년차)", 1380, 215, tl)
        if tk(19) <= t < tk(19) + 3.0:
            rating_circle(base, t - tk(19))
        if name == "C08" and 0.30 <= tl < 0.65:
            k = math.sin(math.pi * (tl - 0.30) / 0.35)
            put_center(base, sparkle_layer(190, k), 1262, 300)
    else:
        if kk(1) <= t < kk(11):
            ai_notice(base)
        if name == "C04":
            title_frame(base, tl, 540, 1016)
        subs = {"C05": "나 과장, 커피.", "C09": "정신 차려, 나 과장!", "C10": "물벼락, 미리 봤습니다.",
                "C11b": "이 돈 받고, 떠나요.", "C14": "…영수증 첨부해 주세요."}
        if name in subs:
            subtitle(base, subs[name])
        if name == "C07" and tl >= 0.3:
            lowerthird(base, tl - 0.3)
        if name == "C06b" and tl >= 2.3:   # 약 8.4초: 팬이 거의 끝나 주연이 화면 안에 들어온 뒤 라벨 팝
            tx, ty = tr(1644, 275, cx_now)
            label_tag(base, "행인 3", (tx, ty), 0, tl - 2.3)
        if name == "C10":
            byeongmat_caption(base, "(일일드라마 시청 25년차)", 480, 520, tl, size=58)
        if name == "C08" and 0.20 <= tl < 0.55:
            k = math.sin(math.pi * (tl - 0.20) / 0.35)
            gx, gy = tr(1262, 300, cx_now)
            put_center(base, sparkle_layer(260, k), gx, gy)

    # 세피아 프리즈 문구 (v3: 외곽선 3px #2A2118 + 그림자 0 4px 12px 65%)
    if name in ("C22", "K4"):
        t_rel = t - tk(92 if not SHORT_MODE else 39)
        if 0 <= t_rel < 1.6:
            a = min(1.0, t_rel / 0.3)
            if SHORT_MODE:
                put_text(base, "다음 이 시간에", F_HAH_BOLD, 84, (0xF3, 0xE6, 0xC8, 255), SEPIA_TEXT_CX_SHORT, 1290, alpha=a,
                         stroke=3, stroke_fill=(0x2A, 0x21, 0x18, 255), shadow=(0, 4, 12, 0.65, (0, 0, 0)))
            else:
                put_text(base, "다음 이 시간에", F_HAH_BOLD, 96, (0xF3, 0xE6, 0xC8, 255), 960, 900, alpha=a,
                         stroke=3, stroke_fill=(0x2A, 0x21, 0x18, 255), shadow=(0, 4, 12, 0.65, (0, 0, 0)))

    # 채널 버그
    if kind in ("still", "clip"):
        bug_draw(base, name, t, tl)
    return base


def bug_draw(base, name, t, tl):
    on = False
    for a, b in bug_on_intervals():
        if t >= a and (b is None or t < b):
            on = True
            ta = a
    if not on:
        return
    if name == "K4":
        draw_k4 = True
    else:
        draw_k4 = False
    if draw_k4:
        k4_overlay(base, tl)
        return
    if name == "C22":
        # 정지 구간은 기본 버그 그대로
        pass
    BW = bug_width()
    x, y = (SHORT_BUG_X, SHORT_BUG_Y) if SHORT_MODE else (BUG_X_MAIN, 44)
    # 켜짐 연출 0.25초: 0 -> 115 -> 100 %, 글린트
    ta_on = None
    for a, b in bug_on_intervals():
        if t >= a and (b is None or t < b):
            ta_on = a
    dt = t - ta_on
    sc = 1.0
    gl = None
    if dt < 0.25:
        u = dt / 0.25
        sc = (u / 0.5) * 1.15 if u < 0.5 else 1.15 - 0.15 * ((u - 0.5) / 0.5)
        gl = u
    elif dt < 0.55:
        gl = (dt - 0.25) / 0.3 if False else None
    if sc <= 0.01:
        return
    if SHORT_MODE:
        bar_a = bug_bar_alpha(t)
        if bar_a > 0:  # v3.1: 17.1-21.0s 검정 30% 둥근 사각 바(패딩 10, 반경 8), 0.2초 페이드
            bw_ = int(BW + 20); bh_ = int(BW * 342 / 1407 + 20)
            bar = Image.new("RGBA", (bw_ * 3, bh_ * 3), (0, 0, 0, 0))
            ImageDraw.Draw(bar).rounded_rectangle([0, 0, bw_ * 3 - 1, bh_ * 3 - 1], radius=24, fill=(0, 0, 0, int(255 * 0.30)))
            bar = bar.resize((bw_, bh_), Image.LANCZOS)
            put_center(base, bar, x + BW / 2, y + BW * 342 / 1407 / 2, bar_a)
        lg = bug_layer(BW * sc, opacity=1.0, shadow=False, glint=gl, soft=bug_soft(t))
    else:
        lg = bug_layer(BW * sc, opacity=0.85, shadow=False, glint=gl)
    put_center(base, lg, x + BW / 2, y + BW * 342 / 1407 / 2)


def render_base_only(i, tl_override=None, t_clamp_end=False, seg_len_override=None):
    ss = segs()
    s = ss[i]
    name, kind = s[0], s[1]
    o = opt(s)
    f0, f1 = seg_start_f(s), seg_end_f(s)
    seg_len = (f1 - f0) / FPS
    if t_clamp_end or tl_override is None:
        tl = max(0.0, seg_len - 1.0 / FPS)
    else:
        tl = tl_override
    cx = seg_cx(o, tl, seg_len)
    fx, fy = o.get("focus", (0.5, 0.5))
    u = min(1.0, tl / max(seg_len, 1e-6))
    if kind == "black":
        if o.get("under"):  # 첫 0.57초: 스팅 아래 C04 ECU를 밝기 18%로 깔고 비네트
            im = make_view(load_still(o["under"]), 1.0, 0.5, 0.5, 0, 0, o.get("cx", 400))
            a_ = np.asarray(im).astype(np.float32) * 0.18
            yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
            r_ = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / 1.414
            a_ *= (1 - 0.75 * np.clip(r_, 0, 1) ** 1.6)[..., None]
            return Image.fromarray(np.clip(a_, 0, 255).astype(np.uint8))
        return Image.new("RGB", (W, H), (0, 0, 0))
    if kind == "end":
        return end_frame(tl)
    if kind == "clip":
        img = clip_image(name, o.get("src", 0.0) + tl)
        z = 1.0
        dx = dy = 0.0
        return make_view(img, z, 0.5, 0.5, dx, dy, cx)
    img = load_still(o.get("still", name))
    fx_ = o.get("fx", "none")
    z, dx, dy = 1.0, 0.0, 0.0
    if fx_ == "kb":
        z = 1.0 + 0.06 * u
    elif fx_ == "kb_rev":
        z = 1.06 - 0.06 * u
    elif fx_ == "hit":
        z, dx, dy, _ = hit_params(tl, seg_len)
        z *= o.get("zoom", 1.0)
    elif fx_ == "none":
        z = 1.0 + 0.0 * u
    if o.get("sat_hit") is not None:
        th = tk(o["sat_hit"]) - f0 / FPS
        if tl >= th:
            z *= 1.0 + 0.02 * ease_out((tl - th) / 0.12)
    return make_view(img, z, fx, fy, dx, dy, cx)


# ------------------------------------------------------------------ 실행
def _worker(f):
    return f, render_frame(f).tobytes()


def main():
    mode = sys.argv[1]
    set_mode(mode)
    args = sys.argv[2:]
    n = total_frames()
    rng = range(n)
    pngdir = None
    if "--frames" in args:
        a, b = args[args.index("--frames") + 1].split(":")
        rng = range(int(a), int(b))
    if "--times" in args:
        ts = [float(x) for x in args[args.index("--times") + 1].split(",")]
        rng = [int(round(x * FPS)) for x in ts]
    if "--png" in args:
        pngdir = args[args.index("--png") + 1]
    import multiprocessing as mp
    if pngdir:
        os.makedirs(pngdir, exist_ok=True)
        with mp.Pool(10, initializer=set_mode, initargs=(mode,)) as pool:
            for f, buf in pool.imap(_worker, list(rng), chunksize=1):
                Image.frombytes("RGB", (W, H), buf).save(os.path.join(pngdir, "%s_%05d.png" % (mode, f)))
        return
    out = os.path.join(HERE, "_work", mode + "_video.mp4")
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H), "-r", "30", "-i", "-",
           "-vf", "scale=in_range=full:out_range=tv:out_color_matrix=bt709:flags=lanczos+accurate_rnd+full_chroma_int,format=yuv420p",
           "-c:v", "libx264", "-preset", "slow", "-crf", "13", "-profile:v", "high", "-pix_fmt", "yuv420p",
           "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
           "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with mp.Pool(12, initializer=set_mode, initargs=(mode,)) as pool:
        for k, (f, buf) in enumerate(pool.imap(_worker, list(rng), chunksize=8)):
            p.stdin.write(buf)
            if k % 100 == 0:
                print("frame", f, flush=True)
    p.stdin.close()
    p.wait()
    print("done", out)


if __name__ == "__main__":
    main()
