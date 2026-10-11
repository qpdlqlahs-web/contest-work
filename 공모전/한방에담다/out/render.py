# -*- coding: utf-8 -*-
"""「약방에 감초」 v1 렌더러. 1080x1920 / 30fps. 모든 글자·인장·효과는 여기서 합성(AI가 그린 글자 없음).

사용:
  python render.py                      # 전체 렌더 -> _work/video_noaudio.mp4 (+ 음원 믹스 후 yakbang_v1.mp4)
  python render.py --c06 경로.png        # C06 소스만 교체해서 다시 렌더 (SRC['C06'] 한 줄이 전부)
  python render.py --frames 0,45,300     # 지정 프레임만 PNG로 _check/_test/ 에 저장
  python render.py --sheet               # 1초 간격 콘택트시트용 프레임 저장
"""
import sys, math, subprocess, argparse, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from timeline import *

OUT = ROOT / "out"
FONTS = OUT / "fonts"
PREP = ROOT / "prep"

# ===================== 소스 (C06은 이 줄 하나만 바꾸면 됨) =====================
SRC = {
    "C02": PREP / "stills/C02c_1.png",
    "C03a": PREP / "stills/C03a_1.png",
    "C03b": PREP / "stills/C03b_1.png",
    "C03d": PREP / "stills/C03d_1.png",
    "C05": PREP / "stills/C05_1.png",
    "C06": PREP / "fix/C06_final3.png",          # <- AD 판정에 따라 교체되는 파일
    "C07": PREP / "stills/C07_1.png",
    "C09": PREP / "stills/C09d_1.png",
    "C10": PREP / "stills/C10d_1.png",
    "C12": PREP / "stills/C12_1.png",
    "C13": PREP / "stills/C13_1.png",
    "C15": PREP / "stills/C15_1.png",
    "C01": PREP / "clips/C01.mp4", "C04": PREP / "clips/C04.mp4", "C08": PREP / "clips/C08.mp4",
    "C11": PREP / "clips/C11.mp4", "C14": PREP / "clips/C14.mp4",
}

INK = (30, 26, 22); HANJI = (243, 233, 210); SEAL = (179, 38, 30); INJU = (200, 55, 45)
YEL = (232, 182, 76); WHITE = (255, 255, 255)

# ===================== 텍스트 유틸 =====================
_fc = {}


def font(name, size, wght=None):
    k = (name, size, wght)
    if k not in _fc:
        f = ImageFont.truetype(str(FONTS / name), size)
        if wght:
            f.set_variation_by_axes([wght])
        _fc[k] = f
    return _fc[k]


def F_HAH(s): return font("Hahmlet-VF.ttf", s, 900)
def F_JUA(s): return font("Jua-Regular.ttf", s)
def F_BHS(s): return font("BlackHanSans-Regular.ttf", s)
def F_PRE(s): return font("Pretendard-SemiBold.otf", s)
def F_NSB(s): return font("NotoSerifCJKkr-Black.otf", s)


_cmaps = {}


def _cmap(path):
    if path not in _cmaps:
        from fontTools.ttLib import TTFont
        t = TTFont(path, fontNumber=0)
        _cmaps[path] = set(t.getBestCmap().keys())
    return _cmaps[path]


def seg_split(text, fnt, fb):
    """글꼴에 없는 글자(한자 등)는 Noto Serif CJK KR Black 으로 대체"""
    cm = _cmap(fnt.path)
    segs = []
    for ch in text:
        use = fnt if (ch == " " or ord(ch) in cm) else fb
        if segs and segs[-1][1] is use:
            segs[-1][0] += ch
        else:
            segs.append([ch, use])
    return segs


def mlen(text, fnt, fb):
    return sum(f.getlength(t) for t, f in seg_split(text, fnt, fb))


def mdraw(draw, x, ybase, text, fnt, fb, **kw):
    for t, f in seg_split(text, fnt, fb):
        draw.text((x, ybase), t, font=f, anchor="ls", **kw)
        x += f.getlength(t)


def lines_layout(lines, fnt, gap, fb=None):
    ws = [mlen(l, fnt, fb or fnt) for l in lines]
    asc, desc = fnt.getmetrics()
    lh = int((asc + desc) * gap)
    return ws, lh


def outlined(lines, fnt_fn, size, fill, ink, sw, gap=1.0, ss=2, pad=None):
    """외곽선 글자 스프라이트 (RGBA uint8). 반환 (arr, line_info)"""
    fnt = fnt_fn(size * ss)
    fb = F_NSB(size * ss)
    ws, lh = lines_layout(lines, fnt, gap, fb)
    asc = fnt.getmetrics()[0]
    pad = (sw + 6) * ss if pad is None else pad * ss
    Wd = int(max(ws) + 2 * pad); Hd = int(lh * len(lines) + 2 * pad)
    m_all = Image.new("L", (Wd, Hd), 0); m_fill = Image.new("L", (Wd, Hd), 0)
    da, df = ImageDraw.Draw(m_all), ImageDraw.Draw(m_fill)
    infos = []
    for i, l in enumerate(lines):
        x = (Wd - ws[i]) / 2
        y = pad + i * lh
        mdraw(da, x, y + asc, l, fnt, fb, fill=255, stroke_width=sw * ss, stroke_fill=255)
        mdraw(df, x, y + asc, l, fnt, fb, fill=255)
        infos.append((x / ss, y / ss, fnt))
    w1, h1 = Wd // ss, Hd // ss
    ma = np.asarray(m_all.resize((w1, h1), Image.LANCZOS), dtype=np.float32) / 255
    mf = np.asarray(m_fill.resize((w1, h1), Image.LANCZOS), dtype=np.float32) / 255
    fillc = np.array(fill, np.float32); inkc = np.array(ink, np.float32)
    mf = np.minimum(mf, ma)
    rgb = fillc * mf[..., None] + inkc * (1 - mf[..., None])
    arr = np.dstack([rgb, ma * 255]).astype(np.uint8)
    return arr, dict(w=w1, h=h1, lh=lh / ss, pad=pad / ss, ws=[w / ss for w in ws], fnt=fnt, fb=fb, ss=ss)


def over(base, spr, x, y, op=1.0):
    h, w = spr.shape[:2]
    x0 = max(x, 0); y0 = max(y, 0); x1 = min(x + w, W); y1 = min(y + h, H)
    if x1 <= x0 or y1 <= y0 or op <= 0:
        return
    s = spr[y0 - y:y1 - y, x0 - x:x1 - x]
    a = s[..., 3:4].astype(np.float32) / 255.0 * op
    reg = base[y0:y1, x0:x1].astype(np.float32)
    base[y0:y1, x0:x1] = (reg * (1 - a) + s[..., :3].astype(np.float32) * a + 0.5).astype(np.uint8)


def screen(base, spr, x, y, op=1.0):
    """밝은 합성(반짝이·김)"""
    h, w = spr.shape[:2]
    x0 = max(x, 0); y0 = max(y, 0); x1 = min(x + w, W); y1 = min(y + h, H)
    if x1 <= x0 or y1 <= y0 or op <= 0:
        return
    s = spr[y0 - y:y1 - y, x0 - x:x1 - x]
    a = s[..., 3:4].astype(np.float32) / 255.0 * op
    reg = base[y0:y1, x0:x1].astype(np.float32)
    add = s[..., :3].astype(np.float32) * a
    base[y0:y1, x0:x1] = np.clip(255 - (255 - reg) * (255 - add) / 255, 0, 255).astype(np.uint8)


def scaled(spr, s, rot=0.0):
    im = Image.fromarray(spr, "RGBA")
    if s != 1.0:
        im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BICUBIC)
    if rot:
        im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    return np.asarray(im)


def paste_c(base, spr, cx, cy, s=1.0, rot=0.0, op=1.0):
    a = scaled(spr, s, rot) if (s != 1.0 or rot) else spr
    over(base, a, int(cx - a.shape[1] / 2), int(cy - a.shape[0] / 2), op)


def clamp01(x): return max(0.0, min(1.0, x))
def ease_out_back(x, k=1.9):
    x = clamp01(x); c1 = k; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def pop_anim(t, t0, t1, dur_in=0.2, dur_out=0.15):
    """등장(오버슈트 스케일)/퇴장(페이드) -> (scale, opacity)"""
    if t < t0 or t > t1 + dur_out:
        return None
    ti = t - t0
    s = 0.25 + 0.75 * ease_out_back(ti / dur_in) if ti < dur_in else 1.0
    op = min(1.0, ti / 0.06)
    if t > t1:
        op = max(0.0, 1 - (t - t1) / dur_out)
    return s, op


# ===================== 프리렌더 스프라이트 =====================
SP = {}   # 이름 -> (arr, info)


def caption_box(lines, size=44, maxw=860, padx_=30, pady_=18, gap_=1.12):
    fnt = F_PRE(size * 2); fb = F_NSB(size * 2)
    ws = [mlen(l, fnt, fb) for l in lines]
    asc, desc = fnt.getmetrics()
    lh = int((asc + desc) * gap_)
    padx, pady = padx_ * 2, pady_ * 2
    Wd = int(max(ws) + 2 * padx); Hd = int(lh * len(lines) + 2 * pady)
    im = Image.new("RGBA", (Wd, Hd), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, Wd - 1, Hd - 1], radius=22 * 2, fill=INK + (int(255 * 0.72),))
    # 글자는 별도 마스크 → 흰색
    m = Image.new("L", (Wd, Hd), 0); dm = ImageDraw.Draw(m)
    for i, l in enumerate(lines):
        mdraw(dm, (Wd - ws[i]) / 2, pady + i * lh + asc, l, fnt, fb, fill=255)
    box = np.asarray(im.resize((Wd // 2, Hd // 2), Image.LANCZOS)).astype(np.float32)
    mm = np.asarray(m.resize((Wd // 2, Hd // 2), Image.LANCZOS), dtype=np.float32)[..., None] / 255
    a0 = box[..., 3:4] / 255
    rgb = box[..., :3] * (1 - mm) + 255 * mm
    a = np.maximum(a0, mm)
    out = np.dstack([rgb, a * 255]).astype(np.uint8)
    assert out.shape[1] <= maxw + 4, (lines, out.shape[1])
    return out


def seal(chars, size, glyph, dims=None, seed=1):
    """인주 레드 사각 인장(흰 글자)"""
    w, h = dims or (size, size)
    ss = 3
    im = Image.new("L", (w * ss, h * ss), 0)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w * ss - 1, h * ss - 1], radius=int(10 * ss), fill=255)
    box = np.asarray(im.resize((w, h), Image.LANCZOS), dtype=np.float32) / 255
    gl = Image.new("L", (w * ss, h * ss), 0); dg = ImageDraw.Draw(gl)
    fnt = F_NSB(glyph * ss)
    n = len(chars)
    if h >= w:   # 한 글자 또는 세로
        for i, c in enumerate(chars):
            bb = fnt.getbbox(c); cw = bb[2] - bb[0]; chh = bb[3] - bb[1]
            cx = (w * ss - cw) / 2 - bb[0]; cy = (h * ss / n) * i + ((h * ss / n) - chh) / 2 - bb[1]
            dg.text((cx, cy), c, font=fnt, fill=255)
    else:        # 가로
        tot = sum(fnt.getlength(c) for c in chars)
        x = (w * ss - tot) / 2
        for c in chars:
            bb = fnt.getbbox(c)
            dg.text((x, (h * ss - (bb[3] - bb[1])) / 2 - bb[1]), c, font=fnt, fill=255)
            x += fnt.getlength(c)
    g = np.asarray(gl.resize((w, h), Image.LANCZOS), dtype=np.float32) / 255
    # 안쪽 테두리선
    ib = Image.new("L", (w * ss, h * ss), 0); di = ImageDraw.Draw(ib)
    di.rounded_rectangle([9 * ss, 9 * ss, w * ss - 10 * ss, h * ss - 10 * ss], radius=5 * ss, outline=255, width=3 * ss)
    inner = np.asarray(ib.resize((w, h), Image.LANCZOS), dtype=np.float32) / 255
    rng = np.random.default_rng(seed)
    noise = rng.random((h, w)).astype(np.float32)
    from scipy.ndimage import gaussian_filter
    noise = gaussian_filter(noise, 1.2); noise = (noise - noise.mean()) / (noise.std() + 1e-6)
    ink_a = np.clip(0.93 + noise * 0.04, 0.82, 1.0)
    ink = np.array(SEAL, np.float32); paper = np.array(HANJI, np.float32)
    mark = np.clip(g + inner * 0.55, 0, 1)[..., None]
    rgb = ink * (1 - mark) + paper * mark
    a = box * ink_a
    return np.dstack([rgb, a * 255]).astype(np.uint8)


def build_sprites():
    SP["seal_gun"] = seal("君", 225, 165, seed=3)
    SP["seal_sin"] = seal("臣", 225, 165, seed=5)
    SP["seal_gc"] = seal("甘草", 0, 78, dims=(210, 132), seed=9)
    for k, txt, sz in [("sfx_tak", ["탁!"], 130), ("sfx_gc", ["감초!"], 140), ("sfx_ppae", ["빼꼼"], 112),
                       ("sfx_kung", ["쿵!"], 126), ("sfx_splash", ["첨벙!"], 128)]:
        SP[k] = outlined(txt, F_BHS, sz, INJU, WHITE, 8)[0]
    SP["title"] = outlined(["약방에 감초"], F_HAH, 150, INK, HANJI, 7)[0]
    SP["end1"] = outlined(["약방엔 감초,"], F_HAH, 124, INK, HANJI, 7)[0]
    SP["end2"] = outlined(["약령시엔"], F_HAH, 124, INK, HANJI, 7)[0]
    SP["end3"] = outlined(["쉼 한 첩"], F_HAH, 124, INK, HANJI, 7)[0]
    SP["bubble"] = bubble(["이 탕은 계절", "약재 전용!"])
    SP["cap_c02"] = caption_box(["서울한방진흥센터 2F", "서울약령시한의약박물관"])
    SP["cap_c04"] = caption_box(["약재 약 380종을 만나는 곳"])
    SP["cap_c06"] = caption_box(["君臣佐使 — 박물관에서 소개하는", "처방 구성 원리"])
    SP["cap_c08"] = caption_box(["2F 약초 족욕", "약쑥·감국 등 계절 약재"])
    SP["cap_c10"] = caption_box(["두한족열 — 예부터 전하는 건강 습관", "(센터 안내)"])
    SP["cap_c11"] = caption_box(["1F 전통의상 체험"])
    SP["cap_c12"] = caption_box(["'널리 구제한다' — 조선시대 백성을", "돌보던 의료·구휼기관"])
    SP["cap_c13"] = caption_box(["별관 한방카페"])
    SP["loc"] = caption_box(["서울한방진흥센터", "서울 동대문구 약령중앙로 26", "1호선 제기동역 2번 출구"], size=44)
    SP["ai"] = caption_box(["이 영상은 생성형 AI로 만든 이미지·영상·음악을 활용했습니다.",
                             "장면은 실제 시설을 바탕으로 한 일러스트 표현입니다."], size=29, maxw=900)
    # 현판(보제원): 세로 한자 + 한글 소형 (한지 위 먹글씨)
    SP["plaque"] = plaque()
    # 김/반짝이 스프라이트
    SP["puff"] = [puff(230 + 40 * (i % 3), i) for i in range(6)]
    SP["star"] = star(150)
    SP["dot"] = dot(20)


def bubble(lines):
    arr, info = outlined(lines, F_BHS, 104, INJU, WHITE, 3, gap=1.05)
    w, h = info["w"] + 90, info["h"] + 70
    ss = 2
    im = Image.new("L", (w * ss, h * ss + 70 * ss), 0); d = ImageDraw.Draw(im)
    d.rounded_rectangle([6 * ss, 6 * ss, (w - 6) * ss, (h - 6) * ss], radius=60 * ss, fill=255)
    tail = [(w * 0.18 * ss, (h - 10) * ss), (w * 0.30 * ss, (h - 10) * ss), (w * 0.14 * ss, (h + 62) * ss)]
    d.polygon(tail, fill=255)
    m = np.asarray(im.resize((w, h + 70), Image.LANCZOS), dtype=np.float32) / 255
    # 외곽선 = 마스크 팽창 차
    from scipy.ndimage import binary_dilation, gaussian_filter
    dil = gaussian_filter(binary_dilation(m > 0.5, iterations=6).astype(np.float32), 0.8)
    paper = np.array([255, 248, 232], np.float32)
    rgb = np.array(INK, np.float32) * (1 - m[..., None]) + paper * m[..., None]
    bub = np.dstack([rgb, dil * 255]).astype(np.uint8)
    canvas = Image.fromarray(bub, "RGBA")
    canvas.alpha_composite(Image.fromarray(arr, "RGBA"), ((w - arr.shape[1]) // 2, (h - arr.shape[0]) // 2 + 2))
    return np.asarray(canvas)


def plaque():
    """C12 현판: 普濟院(세로) + 보제원. 먹 + 약간의 번짐. 한지 위에 multiply 합성용 RGBA."""
    w, h = 470, 650
    ss = 2
    im = Image.new("L", (w * ss, h * ss), 0); d = ImageDraw.Draw(im)
    fh = F_NSB(150 * ss)
    y = 30 * ss
    for c in "普濟院":
        bb = fh.getbbox(c)
        d.text(((w * ss - (bb[2] - bb[0])) / 2 - bb[0], y - bb[1]), c, font=fh, fill=255)
        y += 160 * ss
    fk = F_NSB(78 * ss)
    t = "보제원"
    bb = fk.getbbox(t)
    d.text(((w * ss - (bb[2] - bb[0])) / 2 - bb[0], (h - 96) * ss - bb[1]), t, font=fk, fill=255)
    m = np.asarray(im.resize((w, h), Image.LANCZOS), dtype=np.float32) / 255
    from scipy.ndimage import gaussian_filter
    m = np.clip(gaussian_filter(m, 0.7) * 1.05, 0, 1)
    rgb = np.zeros((h, w, 3), np.float32); rgb[:] = (52, 36, 24)
    return np.dstack([rgb, m * 235]).astype(np.uint8)


def puff(sz, seed):
    from scipy.ndimage import gaussian_filter
    rng = np.random.default_rng(seed)
    a = np.zeros((sz, sz), np.float32)
    yy, xx = np.mgrid[:sz, :sz]
    for _ in range(5):
        cx, cy = rng.uniform(0.3, 0.7, 2) * sz; r = rng.uniform(0.14, 0.26) * sz
        a += np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * r * r)))
    a = gaussian_filter(a, sz * 0.05); a = np.clip(a / a.max(), 0, 1) ** 1.5
    rgb = np.full((sz, sz, 3), 255, np.uint8)
    return np.dstack([rgb, (a * 255).astype(np.uint8)])


def star(sz):
    ss = 2
    im = Image.new("L", (sz * ss, sz * ss), 0); d = ImageDraw.Draw(im)
    c = sz * ss / 2
    pts = []
    for i in range(8):
        r = c * (1.0 if i % 2 == 0 else 0.13)
        ang = math.pi / 4 * i - math.pi / 2
        pts.append((c + r * math.cos(ang), c + r * math.sin(ang)))
    d.polygon(pts, fill=255)
    from scipy.ndimage import gaussian_filter
    m = np.asarray(im.resize((sz, sz), Image.LANCZOS), dtype=np.float32) / 255
    m = np.clip(m + gaussian_filter(m, sz * 0.05) * 0.8, 0, 1)
    rgb = np.zeros((sz, sz, 3), np.uint8); rgb[:] = (255, 236, 170)
    return np.dstack([rgb, (m * 255).astype(np.uint8)])


def dot(sz):
    yy, xx = np.mgrid[:sz, :sz]; c = sz / 2
    a = np.clip(1 - np.hypot(xx - c, yy - c) / c, 0, 1) ** 1.2
    rgb = np.zeros((sz, sz, 3), np.uint8); rgb[:] = (255, 226, 140)
    return np.dstack([rgb, (a * 255).astype(np.uint8)])


# ===================== 가사(노래방식) =====================
LYRIC_BAND = {   # 컷 -> 가사 블록 중심 y (캐릭터 얼굴을 피하는 위치)
    "C01": 230, "C02": 1450, "C04": 560, "C05": 560,
    "C03a": 560, "C03b": 1450, "C03d": 1450,
    "C06": 1485, "C07": 560, "C08": 560, "C09": 1450, "C10": 1450, "C11": 1450,
    "C12": 1100, "C13": 560, "C14": 330, "C15": None,
}
LYRIC_CX = 500    # 우측 140px 비움 -> 가로 안전영역(60~940)의 중심


def build_lyrics():
    res = []
    for lines, a, b in LYRICS:
        t_on = a - SONG_START; t_off = b - SONG_START
        # 한 줄이 너무 길면 두 줄로 나눔
        L = []
        for l in lines:
            if F_JUA(76).getlength(l) > 860 and " " in l:
                parts = l.split(" ")
                best = min(range(1, len(parts)), key=lambda k: abs(F_JUA(76).getlength(" ".join(parts[:k])) - F_JUA(76).getlength(" ".join(parts[k:]))))
                L += [" ".join(parts[:best]), " ".join(parts[best:])]
            else:
                L.append(l)
        size = 76
        emph = L == ["그럼 나는 뭐지?"]
        if emph:
            size = 100
        wh, info = outlined(L, F_JUA, size, WHITE, INK, 6, gap=1.08)
        yl, _ = outlined(L, F_JUA, size, YEL, INK, 6, gap=1.08)
        # 글자별 가중치와 x 위치(블록 좌표)
        chars = []
        for li, l in enumerate(L):
            for ci, c in enumerate(l):
                xs = mlen(l[:ci], info["fnt"], info["fb"]) / info["ss"] + (info["w"] - info["ws"][li]) / 2
                xe = mlen(l[:ci + 1], info["fnt"], info["fb"]) / info["ss"] + (info["w"] - info["ws"][li]) / 2
                wgt = 0.0 if c == " " else (0.35 if c in "()?!,~" else 1.0)
                chars.append((li, xs, xe, wgt))
        res.append(dict(L=L, wh=wh, yl=yl, info=info, chars=chars, t_on=t_on, t_off=t_off, emph=emph))
    return res


def lyric_mask(ly, t):
    """채움 진행률 -> 줄별 경계 x (블록 좌표). 반환 [x or None per line]"""
    a = ly["t_on"]; b = ly["t_off"] - 0.06
    p = clamp01((t - a) / max(b - a, 0.1))
    tw = sum(c[3] for c in ly["chars"])
    acc = 0.0
    nl = len(ly["L"])
    bx = [0.0] * nl
    target = p * tw
    for li, xs, xe, w in ly["chars"]:
        if w == 0:
            if acc <= target: bx[li] = max(bx[li], xe)
            continue
        if acc + w <= target + 1e-9:
            bx[li] = max(bx[li], xe)
        elif acc < target:
            frac = (target - acc) / w
            bx[li] = max(bx[li], xs + (xe - xs) * frac)
        acc += w
    return bx


def draw_lyric(base, ly, t, cy, vis_end):
    if t < ly["t_on"] - 0.12 or t > vis_end + 0.12:
        return
    info = ly["info"]
    wh, yl = ly["wh"], ly["yl"]
    comp = wh.copy()
    bx = lyric_mask(ly, t)
    lh = info["lh"]; pad = info["pad"]
    for li, x in enumerate(bx):
        if x <= 0:
            continue
        y0 = int(pad + li * lh - 4); y1 = int(pad + (li + 1) * lh + 4)
        y0 = max(0, y0); y1 = min(comp.shape[0], y1)
        xi = int(min(x + 2, comp.shape[1]))
        # 채움 영역: 노란 글자(외곽선은 동일 -> 그냥 교체)
        comp[y0:y1, :xi] = yl[y0:y1, :xi]
    op = clamp01((t - (ly["t_on"] - 0.12)) / 0.1) * clamp01((vis_end + 0.12 - t) / 0.1)
    slide = int(14 * (1 - clamp01((t - (ly["t_on"] - 0.12)) / 0.12)))
    x = int(LYRIC_CX - comp.shape[1] / 2); y = int(cy - comp.shape[0] / 2) + slide
    if ly["emph"]:
        s = 1.0 + 0.06 * math.sin((t - ly["t_on"]) * 14) * math.exp(-(t - ly["t_on"]) * 2.0)
        paste_c(base, comp, LYRIC_CX, cy, s, 0, op)
    else:
        over(base, comp, x, y, op)


# ===================== 컷별 장면 =====================
def cut_at(f):
    for cid, a, b in CUTS:
        if fr(a) <= f < fr(b):
            return cid, a, b
    return CUTS[-1]


_still = {}
_clip = {}


def get_still(cid):
    if cid not in _still:
        _still[cid] = Image.open(SRC[cid]).convert("RGB")
        assert _still[cid].size == (W, H), (cid, _still[cid].size)
    return _still[cid]


def kb(img, u, z0, z1, cx=0.5, cy=0.5, cx1=None, cy1=None, ox=0.0, oy=0.0):
    """Ken Burns. u=0..1"""
    z = z0 + (z1 - z0) * u
    if cx1 is not None: cx = cx + (cx1 - cx) * u
    if cy1 is not None: cy = cy + (cy1 - cy) * u
    w = W / z; h = H / z
    x0 = (W - w) * cx + ox; y0 = (H - h) * cy + oy
    x0 = min(max(x0, 0), W - w); y0 = min(max(y0, 0), H - h)
    return np.asarray(img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + w, y0 + h)))


def load_clip(cid):
    if cid not in _clip:
        _clip.clear()
        p = subprocess.run(["ffmpeg", "-v", "error", "-i", str(SRC[cid]), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                           capture_output=True)
        a = np.frombuffer(p.stdout, np.uint8).reshape(-1, H, W, 3)
        _clip[cid] = a
    return _clip[cid]


def shake(arr, T, t_land, amp=6, dur=0.2):
    d = T - t_land
    if d < 0 or d > dur:
        return arr
    k = math.exp(-d / (dur * 0.45))
    dx = int(round(amp * k * math.sin(d * 70))); dy = int(round(amp * k * math.cos(d * 55)))
    if dx == 0 and dy == 0:
        return arr
    p = np.pad(arr, ((abs(dy), abs(dy)), (abs(dx), abs(dx)), (0, 0)), mode="edge")
    return p[abs(dy) - dy:abs(dy) - dy + H, abs(dx) - dx:abs(dx) - dx + W].copy()


def seal_drop(base, spr, cx, cy, T, t_land, rot=0.0, hold_end=1e9):
    t0 = t_land - 0.22
    if T < t0 or T > hold_end:
        return
    if T < t_land:
        e = ((T - t0) / 0.22) ** 2
        s = 1.7 - 0.7 * e
        y = cy - (1 - e) * 650
        op = clamp01((T - t0) / 0.07)
        paste_c(base, spr, cx, y, s, rot, op)
    else:
        d = T - t_land
        s = 1.0 + 0.10 * math.exp(-d * 14) * math.cos(d * 40)
        paste_c(base, spr, cx, cy, s, rot, 1.0)


def steam(base, T, spots, seed=0, strength=0.5, period=2.6, rise=260):
    """spots: [(x, y, n)] 위로 흐르는 반투명 김"""
    for si, (x, y, n) in enumerate(spots):
        for k in range(n):
            ph = (T / period + k / n + si * 0.37) % 1.0
            spr = SP["puff"][(si * 3 + k) % 6]
            sc = 0.55 + 0.9 * ph
            xx = x + math.sin((ph + k) * 5.1 + si) * 22 + (k - n / 2) * 18
            yy = y - ph * rise
            op = strength * math.sin(math.pi * ph) ** 1.2
            a = scaled(spr, sc)
            screen(base, a, int(xx - a.shape[1] / 2), int(yy - a.shape[0] / 2), op)


def sparkles(base, T, t0, centers, n=9):
    if T < t0:
        return
    d = T - t0
    rng = random.Random(4)
    for i in range(n):
        cx, cy, r = centers[i % len(centers)]
        ang = rng.uniform(0, 6.28); rad = rng.uniform(0.3, 1.0) * r
        x = cx + math.cos(ang) * rad; y = cy + math.sin(ang) * rad * 0.9
        ph = rng.uniform(0, 6.28); sp = rng.uniform(2.5, 4.5)
        tw = max(0.0, math.sin(d * sp + ph)) ** 2 * clamp01(d / 0.15)
        sc = (0.35 + 0.55 * rng.random()) * (0.6 + 0.6 * tw)
        a = scaled(SP["star"], sc, rot=rng.uniform(-15, 15))
        screen(base, a, int(x - a.shape[1] / 2), int(y - a.shape[0] / 2), 0.95 * tw)
    # 도장 순간 파편
    if d < 0.7:
        rng2 = random.Random(11)
        for i in range(16):
            ang = rng2.uniform(0, 6.28); sp = rng2.uniform(140, 380)
            x = 518 + math.cos(ang) * sp * d; y = 935 + math.sin(ang) * sp * d + 260 * d * d
            a = scaled(SP["dot"], rng2.uniform(0.4, 1.0))
            screen(base, a, int(x - a.shape[1] / 2), int(y - a.shape[0] / 2), 0.9 * (1 - d / 0.7))


def cloud_sway(arr, T):
    """C07 비구름 0.5Hz 흔들기: 타원 페더 영역만 가로 변위"""
    cx, cy = 585, 944
    x0, x1, y0, y1 = cx - 190, cx + 190, cy - 130, cy + 110
    dx = 8.0 * math.sin(2 * math.pi * 0.5 * T)
    reg = arr[y0:y1, x0:x1].astype(np.float32)
    sh = int(round(dx))
    moved = np.roll(reg, sh, axis=1)
    yy, xx = np.mgrid[y0:y1, x0:x1]
    m = np.clip(1 - (((xx - cx) / 185.0) ** 2 + ((yy - cy) / 118.0) ** 2), 0, 1)
    m = np.clip(m * 3.0, 0, 1)[..., None]
    arr[y0:y1, x0:x1] = (reg * (1 - m) + moved * m).astype(np.uint8)


def rain(base, T):
    rng = random.Random(21)
    for i in range(9):
        x = 520 + rng.uniform(0, 130); ph = (T * 1.25 + rng.random()) % 1.0
        y = 1010 + ph * 100
        a = np.zeros((26, 4, 4), np.uint8); a[..., :3] = (170, 190, 205); a[..., 3] = 200
        over(base, a, int(x), int(y), 0.8 * math.sin(math.pi * ph))


def flash(arr, T, t0, amt=0.22, dur=0.16):
    d = T - t0
    if 0 <= d < dur:
        k = amt * (1 - d / dur)
        return np.clip(arr.astype(np.float32) * (1 - k) + 255 * k, 0, 255).astype(np.uint8)
    return arr


# ===================== 프레임 렌더 =====================
LY = None


def render_frame(f):
    T = f / FPS
    cid, b0, b1 = cut_at(f)
    f0 = fr(b0); n = fr(b1) - f0
    tl = (f - f0) / FPS                  # 컷 내 시간
    u = (f - f0) / max(n - 1, 1)

    # ---- 배경 ----
    if cid in ("C01", "C04", "C08", "C11", "C14"):
        clip = load_clip(cid)
        i = int(round(tl * CLIP_SPEED[cid] * 24))
        i = min(i, len(clip) - 1)
        arr = clip[i].copy()
    else:
        img = get_still(cid)
        if cid == "C02":
            arr = kb(img, u, 1.0, 1.035, 0.5, 0.55)
        elif cid == "C05":
            arr = kb(img, u, 1.0, 1.03, 0.5, 0.6, 0.58, 0.62)
        elif cid in ("C03a", "C03b", "C03d"):
            punch = 0.10 * math.exp(-tl * 11) * (1 + 0.15 * math.cos(tl * 30))
            arr = kb(img, u, 1.03 + punch, 1.07 + punch * 0.3, 0.5, 0.5)
        elif cid == "C06":
            arr = kb(img, u, 1.02, 1.035, 0.5, 0.6)
        elif cid == "C07":
            arr = kb(img, u, 1.0, 1.035, 0.5, 0.65)
        elif cid == "C09":
            arr = kb(img, u, 1.03, 1.03, 0.47, 0.5, 0.53, 0.5)           # 좌우 패럴랙스 1.5%
        elif cid == "C10":
            arr = kb(img, u, 1.0, 1.03, 0.5, 0.55)
        elif cid == "C12":
            arr = kb(img, u, 1.0, 1.02, 0.5, 0.5)
        elif cid == "C13":
            arr = kb(img, u, 1.0, 1.03, 0.5, 0.45)
        elif cid == "C15":
            arr = kb(img, u, 1.02, 1.0, 0.5, 0.5)
        else:
            arr = kb(img, u, 1.0, 1.0)
    arr = np.array(arr, dtype=np.uint8, copy=True)

    # ---- 컷별 그래픽(배경에 붙는 것) ----
    if cid == "C05":
        if T >= STAMP_GAMCHO_T - 0.22:
            seal_drop(arr, SP["seal_gc"], 520, 936, T, STAMP_GAMCHO_T, rot=-4)
        sparkles(arr, T, STAMP_GAMCHO_T, [(700, 1160, 330), (520, 900, 200)], 9)
    if cid == "C06":
        seal_drop(arr, SP["seal_gun"], 277, 750, T, STAMP_GUN_T, rot=-3)
        seal_drop(arr, SP["seal_sin"], 825, 750, T, STAMP_SIN_T, rot=3)
        arr = shake(arr, T, STAMP_GUN_T); arr = shake(arr, T, STAMP_SIN_T)
    if cid == "C07":
        cloud_sway(arr, T); rain(arr, T)
    if cid == "C10":
        steam(arr, T, [(430, 1010, 3), (640, 1010, 3), (545, 960, 3)], strength=0.42)
    if cid == "C13":
        steam(arr, T, [(356, 1380, 2), (551, 1318, 2), (745, 1362, 2)], strength=0.40, rise=190)
    if cid == "C12":
        pa = pop_anim(T, bt(92) + 0.10, 1e9, 0.35)
        if pa:
            s, op = pa
            # 현판 안쪽 영역 중심. 먹글씨는 multiply 느낌으로 진하게
            paste_c(arr, SP["plaque"], 535, 640, 0.9 + 0.1 * s, 0, op)

    # ---- 효과음 글자 / 말풍선 / 타이틀 (스프라이트 위치는 컷별) ----
    def sfx(name, t0, t1, x, y, rot=0):
        pa = pop_anim(T, t0, t1, 0.18, 0.12)
        if pa:
            s, op = pa
            wob = rot + 2.5 * math.sin((T - t0) * 22) * math.exp(-(T - t0) * 5)
            paste_c(arr, SP[name], x, y, s, wob, op)

    if cid == "C01":
        sfx("sfx_tak", 0.02, 0.75, 300, 640, 8)
        sfx("sfx_gc", 0.95, bt(4), 700, 560, -6)
    if cid == "C03a": sfx("sfx_ppae", bt(36), bt(40) - 0.05, 640, 1000, 6)
    if cid == "C03b": sfx("sfx_ppae", bt(40), bt(44) - 0.05, 700, 880, -6)
    if cid == "C03d": sfx("sfx_ppae", bt(44), bt(48) - 0.05, 300, 790, 6)
    if cid == "C06":
        sfx("sfx_kung", STAMP_GUN_T, STAMP_GUN_T + 0.85, 277, 530, -6)
    if cid == "C08":
        sfx("sfx_splash", SPLASH_T - 0.05, bt(69) - 0.02, 600, 1230, -6)
    if cid == "C09":
        pa = pop_anim(T, bt(69) + 0.45, bt(76) - 0.1, 0.3, 0.15)
        if pa:
            s, op = pa
            wob = 1.2 * math.sin((T - bt(69)) * 6)
            bb = SP["bubble"]
            paste_c(arr, bb, 400, 540, s, wob, op)
    if cid == "C02":
        pa = pop_anim(T, bt(4) + 0.03, bt(10.4), 0.3, 0.2)
        if pa:
            s, op = pa
            paste_c(arr, SP["title"], 500, 400, s, 0, op)

    # ---- 캡션(정보) : 상단 14~20% ----
    def cap(name, t0, t1, cy=330):
        if t0 <= T <= t1:
            op = clamp01((T - t0) / 0.15) * clamp01((t1 - T) / 0.15 + 0.0)
            spr = SP[name]
            over(arr, spr, int(LYRIC_CX - spr.shape[1] / 2), int(cy - spr.shape[0] / 2), op)

    cap("cap_c02", bt(10.6), bt(15.9))
    cap("cap_c04", bt(16.3), bt(23.8))
    cap("cap_c06", STAMP_GUN_T + 0.95, bt(55.8), cy=170)
    cap("cap_c08", bt(60.3), bt(66.6))
    cap("cap_c10", bt(76.4), bt(83.8))
    cap("cap_c11", bt(84.4), bt(91.8))
    cap("cap_c12", bt(92.4), bt(99.8), cy=170)
    cap("cap_c13", bt(100.4), bt(107.8))

    # ---- 가사 ----
    cy = LYRIC_BAND.get(cid)
    if cy is not None:
        for idx, ly in enumerate(LY):
            nxt = LY[idx + 1]["t_on"] - 0.04 if idx + 1 < len(LY) else 1e9
            vis_end = min(ly["t_off"] + 0.45, nxt)
            if ly["t_on"] - 0.12 <= T <= vis_end + 0.12:
                # 컷 경계에서 위치가 바뀌는 건 컷 전환과 동시이므로 문제 없음
                draw_lyric(arr, ly, T, cy, vis_end)
                break

    # ---- 엔딩 ----
    if cid == "C15":
        t1 = END_LINE1[0] - SONG_START - 0.05
        t2 = END_LINE2[0] - SONG_START - 0.05
        t3 = 65.82 - SONG_START - 0.05
        for name, tt, y in [("end1", t1, 400), ("end2", t2, 555), ("end3", t3, 710)]:
            pa = pop_anim(T, tt, 1e9, 0.28)
            if pa:
                s, op = pa
                paste_c(arr, SP[name], LYRIC_CX + 20, y, s, 0, op)
        tl_ = 56.9
        if T >= tl_:
            op = clamp01((T - tl_) / 0.3)
            spr = SP["loc"]
            over(arr, spr, int(LYRIC_CX - spr.shape[1] / 2), 805, op)
        ta = 54.2
        if T >= ta:
            op = clamp01((T - ta) / 0.3)
            spr = SP["ai"]
            over(arr, spr, int(LYRIC_CX - spr.shape[1] / 2), 1572 - spr.shape[0], op)

    # ---- 섹션 전환 펀치 ----
    for sb in (48, 60, 92, 108):
        arr = flash(arr, T, bt(sb))
    return arr


def main():
    global LY
    ap = argparse.ArgumentParser()
    ap.add_argument("--c06"); ap.add_argument("--frames"); ap.add_argument("--sheet", action="store_true")
    ap.add_argument("--out", default=str(OUT / "_work" / "video_noaudio.mp4"))
    a = ap.parse_args()
    if a.c06:
        SRC["C06"] = Path(a.c06)
    build_sprites()
    LY = build_lyrics()
    if a.frames or a.sheet:
        d = OUT / "_check" / "_test"; d.mkdir(parents=True, exist_ok=True)
        fl = [int(x) for x in a.frames.split(",")] if a.frames else list(range(0, NF, FPS))
        for f in fl:
            Image.fromarray(render_frame(f)).save(d / f"f{f:04d}.png")
        print("saved", len(fl))
        return
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-vf", "scale=in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p",
           "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-profile:v", "high", "-level", "4.2",
           "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
           "-movflags", "+faststart", a.out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(NF):
        p.stdin.write(render_frame(f).tobytes())
        if f % 150 == 0:
            print("frame", f, flush=True)
    p.stdin.close(); p.wait()
    print("done")


if __name__ == "__main__":
    main()
