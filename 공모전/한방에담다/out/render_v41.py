# -*- coding: utf-8 -*-
"""「약방에 감초」 v4.1 렌더러 (v1 render.py 의 헬퍼를 재사용하고 컷·가사·레이아웃만 교체).
  python render_v2.py                 # 전체 렌더 -> _work/video_noaudio_v2.mp4
  python render_v2.py --c06 파일.png   # C06 소스 교체
  python render_v2.py --frames 0,30   # 테스트 프레임 -> _check/_test41/
"""
import sys, math, subprocess, argparse
import numpy as np
from PIL import Image, ImageOps
import render as R
from timeline_v41 import *
from render import (outlined, over, screen, scaled, paste_c, clamp01, pop_anim, F_JUA, F_PRE, F_HAH, F_BHS,
                    INK, HANJI, YEL, WHITE, INJU, seal_drop, steam, sparkles, cloud_sway, rain, flash, shake,
                    caption_box, mlen, bt as _bt)

from caption_design import build_captions
OUT = R.OUT; PREP = R.PREP
CAPS = None
C04F = PREP / "stills" / "C04F_1.png"
SP = R.SP
R.SRC["C04"] = OUT / "_work" / "C04_dof_v3.mp4"          # v3: 전경 DOF 블러본(fix_c04_v3.py)
R.SRC["C14"] = PREP / "clips" / "C14b.mp4"              # 재생성 클립(업스케일+샤픈, 0.8배속 3.8s)
R.SRC["C10"] = PREP / "stills" / "C10e_1.png"           # 수건 버전

CUTF = cut_frames()
LYRIC_BAND = {   # 가사 띠: 상단 y=540 / 하단 y=1440 / 예외 C12 y=1100, C06 y=1450
    "C01": 1440, "C02": 1440, "C04": 540, "C05": 540, "C03a": 540, "C03b": 1440, "C03d": 1440,
    "C06": 1450, "C07": 540, "C08": 1440, "C09": 1440, "C10": 1440, "C11": 1440,
    "C12": 1100, "C13": 540, "C14": 540, "C15": None,
}
LYRIC_CX = 500
TOP_SAFE, BOT_SAFE = 250, 1515


def cut_at(f):
    for cid, a, b in CUTF:
        if a <= f < b:
            return cid, a, b
    return CUTF[-1]


def band_at_t(T):
    return LYRIC_BAND.get(cut_at(int(T * FPS))[0])


# ---------------- 스프라이트 ----------------
def wrap_lines(text, size, maxw):
    fnt = F_PRE(size * 2)
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if mlen(t, fnt, fnt) / 2 <= maxw or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    lines.append(cur)
    return lines


def build_sprites_v2():
    R.build_sprites()
    SP["title"] = outlined(["약방에 감초"], F_HAH, 128, INK, HANJI, 6)[0]
    for k, t in [("end1", "약방엔 감초,"), ("end2", "약령시엔"), ("end3", "쉼 한 첩")]:
        SP[k] = outlined([t], F_HAH, 112, INK, HANJI, 6)[0]
    SP["cap_c02"] = caption_box(["2F 서울약령시한의약박물관"])
    SP["cap_c06"] = caption_box(["군신좌사 — 박물관에서 소개하는", "처방 구성 원리"], size=40)
    SP["cap_c12"] = caption_box(["조선시대 백성을 돌보던 의료·구휼기관"], size=40)
    ai = "이 영상은 생성형 AI로 만든 이미지·영상·음악을 활용했습니다. 장면은 실제 시설을 바탕으로 한 일러스트 표현입니다."
    SP["ai"] = caption_box(wrap_lines(ai, 34, 800), size=34, maxw=900, pady_=10, gap_=1.0)


# ---------------- 가사 (v4: 음절 단위 정렬 데이터 사용) ----------------
import json
PUNCT = "()?!,~"
LYR_SIZE = {"그럼 나는 뭐지?": 100, "서울한방진흥센터로": 96}


def build_lyrics_v4():
    data = json.load(open(OUT / "_work" / "lyrics_v41.json", encoding="utf8"))
    res = []
    for d in data:
        L = d["lines"]; size = LYR_SIZE.get(L[0], 76)
        wh, info = outlined(L, F_JUA, size, WHITE, INK, 6, gap=1.08)
        yl, _ = outlined(L, F_JUA, size, YEL, INK, 6, gap=1.08)
        if wh.shape[1] > 880:
            raise SystemExit(f"가사 폭 초과 {L} {wh.shape[1]}")
        ts = [t - SONG_START for t in d["t"]]; we = d["win"][1] - SONG_START
        ends = ts[1:] + [we]
        chars = []; si = 0
        for li, l in enumerate(L):
            off = (info["w"] - info["ws"][li]) / 2
            for ci, c in enumerate(l):
                xs = mlen(l[:ci], info["fnt"], info["fb"]) / info["ss"] + off
                xe = mlen(l[:ci + 1], info["fnt"], info["fb"]) / info["ss"] + off
                if c == " ":
                    chars.append((li, xs, xe, None, None)); continue
                if c in PUNCT:
                    chars.append((li, xs, xe, "p", None)); continue
                chars.append((li, xs, xe, ts[si], ends[si])); si += 1
        assert si == len(ts), (L, si, len(ts))
        res.append(dict(L=L, wh=wh, yl=yl, info=info, chars=chars, first=ts[0], last_end=we,
                        t_on=ts[0], t_off=we, emph=(L == ["그럼 나는 뭐지?"]), v3_on=d["v3_t_on"] - SONG_START))
    return res


def _char_fill(T, st, en):
    dur = max(en - st, 0.05)
    wipe = min(max(dur * 0.85, 0.10), 0.9)
    return clamp01((T - st) / wipe)


def fill_bounds(ph, T):
    nl = len(ph["L"]); bx = [0.0] * nl
    last_f = 0.0
    for li, xs, xe, st, en in ph["chars"]:
        if st is None:
            continue
        if st == "p":
            if last_f >= 1.0: bx[li] = max(bx[li], xe)
            continue
        f = _char_fill(T, st, en); last_f = f
        if f > 0:
            bx[li] = max(bx[li], xs + (xe - xs) * f)
    return bx


def fill_ratio(ph, T):
    sy = [c for c in ph["chars"] if c[3] not in (None, "p")]
    return sum(_char_fill(T, c[3], c[4]) for c in sy) / max(len(sy), 1)


def cut_boundaries():
    return [a / FPS for cid, a, b in CUTF[1:]]


PIN_LINES = {"군도 아냐 신도 아냐"}      # 컷을 걸쳐 가는 구절 중 띠 고정(점프 방지) 대상


def plan_visibility(LY):
    """자막: 첫 음절 0.2s 전 등장 ~ 마지막 음절 끝 0.2s 뒤까지. 연속 줄은 앞 줄 끝(+0.05)을 보장하고 다음 줄 등장을 그만큼 늦춤.
    띠가 바뀌는 컷: 90% 이상 채워졌으면 컷에서 끊기 / 컷 직전 막 시작한 구절은 시작을 컷에 맞춤 /
    그 외(걸쳐 가는 구절, v4.1)는 시작한 띠에 고정(pin)해 위치가 점프하지 않게 함."""
    bounds = [b for b in cut_boundaries() if band_at_t(b - 1e-3) != band_at_t(b + 1e-3)]
    n = len(LY)
    for i, ph in enumerate(LY):
        ph["vs"] = ph["first"] - 0.2; ph["ve"] = ph["last_end"] + 0.2
    for i in range(n - 1):
        cur, nxt = LY[i], LY[i + 1]
        if nxt["vs"] - 0.03 < cur["last_end"] + 0.05:
            cur["ve"] = cur["last_end"] + 0.05
            nxt["vs"] = max(nxt["vs"], cur["ve"] + 0.03)
        else:
            cur["ve"] = min(cur["ve"], nxt["vs"] - 0.03)
    for ph in LY:
        vs, ve = ph["vs"], ph["ve"]
        ph["hard_end"] = False; ph["hard_start"] = False; ph["pin"] = None
        for b in bounds:
            if vs < b < ve:
                if fill_ratio(ph, b) >= 0.9:
                    ve = b; ph["hard_end"] = True
                elif b <= ph["first"] + 0.5 and fill_ratio(ph, b) < 0.5:
                    vs = b; ph["hard_start"] = True
                elif not ph["hard_end"] and ph["pin"] is None and ph["L"][0] in PIN_LINES:
                    ph["pin"] = band_at_t(vs + 1e-3)
        ph["vs"], ph["ve"] = vs, ve
    return LY


def draw_lyric_v2(base, ph, T, cy):
    comp = ph["wh"].copy(); yl = ph["yl"]; info = ph["info"]
    bx = fill_bounds(ph, T)
    lh = info["lh"]; pad = info["pad"]
    for li, x in enumerate(bx):
        if x <= 0:
            continue
        y0 = max(0, int(pad + li * lh - 4)); y1 = min(comp.shape[0], int(pad + (li + 1) * lh + 4))
        xi = int(min(x + 2, comp.shape[1]))
        comp[y0:y1, :xi] = yl[y0:y1, :xi]
    h = comp.shape[0]
    cy = min(cy, BOT_SAFE - h / 2); cy = max(cy, TOP_SAFE + h / 2) if cy < 400 else cy
    fi = 0.0 if ph["hard_start"] else 0.1
    fo = 0.0 if ph["hard_end"] else 0.1
    op = clamp01((T - ph["vs"]) / fi) if fi else 1.0
    op *= clamp01((ph["ve"] + fo - T) / fo) if fo else 1.0
    slide = 0 if ph["hard_start"] else int(14 * (1 - clamp01((T - ph["vs"]) / 0.12)))
    if ph["emph"]:
        s = 1.0 + 0.06 * math.sin((T - ph["first"]) * 14) * math.exp(-(T - ph["first"]) * 2.0)
        paste_c(base, comp, LYRIC_CX, cy, s, 0, op)
    else:
        over(base, comp, int(LYRIC_CX - comp.shape[1] / 2), int(cy - h / 2) + slide, op)


# ---------------- 이미지 소스 가공 ----------------
_img = {}


def get_img(cid):
    if cid in _img:
        return _img[cid]
    im = R.get_still(cid)
    if cid == "C12":     # 현판을 아래로 60px(캡션이 y250 이하 안전영역 밖에 오도록) - 위쪽은 반사 확장
        c = Image.new("RGB", (W, H)); c.paste(im.crop((0, 0, W, H - 60)), (0, 60))
        c.paste(ImageOps.flip(im.crop((0, 0, W, 60))), (0, 0)); im = c
    if cid == "C13":     # 쑥 은녹색 채도를 C09에 맞춤(녹색 픽셀 채도 +18%)
        a = np.asarray(im).astype(np.float32)
        x0, y0, x1, y1 = 470, 1030, 780, 1350
        r = a[y0:y1, x0:x1]; Rr, G, B = r[..., 0], r[..., 1], r[..., 2]
        m = ((G > Rr + 3) & (G > B + 3)).astype(np.float32)[..., None]
        gray = r.mean(2, keepdims=True)
        r2 = gray + (r - gray) * 1.18
        a[y0:y1, x0:x1] = r * (1 - m) + r2 * m
        im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    _img[cid] = im
    return im


def pulse(T):
    bar = 4 * BEAT
    return 0.02 * math.exp(-(T % bar) * 7.0)


def kbp(img, u, z0, z1, T, cx=0.5, cy=0.5, cx1=None, cy1=None):
    p = 1.0 + pulse(T)
    return R.kb(img, u, z0 * p, z1 * p, cx, cy, cx1, cy1)


# ---------------- 프레임 ----------------
LY = None


def render_frame(f):
    T = f / FPS
    cid, f0, f1 = cut_at(f)
    n = f1 - f0
    tl = (f - f0) / FPS
    u = (f - f0) / max(n - 1, 1)

    if cid in ("C01", "C04", "C08", "C11", "C14"):
        clip = R.load_clip(cid)
        i = int(round(tl * CLIP_SPEED[cid] * 24))
        if cid == "C08":
            arr = R.kb(Image.fromarray(clip[min(i, len(clip) - 1)]), u, 1.06, 1.06, 0.5, 0.12)   # 하단 크롭을 더 줌
        elif cid == "C04" and (i >= len(clip) or (C04F.exists() and f >= fr(24))):
            if C04F.exists():       # v3: 박 #24(11.13s)에서 하드컷 -> 깨끗한 정지 이미지 + 2% 푸시인 + 마디 펄스
                hold0 = fr(24) - f0
                hu = clamp01((f - f0 - hold0) / max(1, n - hold0))
                still = Image.open(C04F).convert("RGB")
                if still.size != (W, H): still = still.resize((W, H), Image.LANCZOS)
                arr = kbp(still, hu, 1.0, 1.02, T, 0.5, 0.55, 0.62, 0.62)
            else:                   # 대체: 클립 마지막 프레임 프리즈
                hold0 = int(len(clip) / 24 * FPS)
                hu = clamp01((f - f0 - hold0) / max(1, n - hold0))
                arr = kbp(Image.fromarray(clip[-1]), hu, 1.0, 1.02, T, 0.5, 0.55, 0.62, 0.62)
        else:
            arr = clip[min(i, len(clip) - 1)].copy()
    else:
        img = get_img(cid)
        if cid == "C02": arr = kbp(img, u, 1.0, 1.035, T, 0.5, 0.55)
        elif cid == "C05": arr = kbp(img, u, 1.0, 1.03, T, 0.5, 0.6, 0.58, 0.62)
        elif cid in ("C03a", "C03b", "C03d"):
            punch = 0.10 * math.exp(-tl * 11) * (1 + 0.15 * math.cos(tl * 30))
            arr = R.kb(img, u, 1.03 + punch, 1.07 + punch * 0.3, 0.5, 0.5)
        elif cid == "C06": arr = kbp(img, u, 1.02, 1.035, T, 0.5, 0.6)
        elif cid == "C07": arr = kbp(img, u, 1.0, 1.035, T, 0.5, 0.65)
        elif cid == "C09": arr = kbp(img, u, 1.03, 1.03, T, 0.47, 0.5, 0.53, 0.5)
        elif cid == "C10": arr = kbp(img, u, 1.0, 1.03, T, 0.5, 0.55)
        elif cid == "C12": arr = kbp(img, u, 1.0, 1.02, T, 0.5, 0.5)
        elif cid == "C13": arr = kbp(img, u, 1.0, 1.03, T, 0.5, 0.45)
        elif cid == "C15": arr = kbp(img, u, 1.02, 1.0, T, 0.5, 0.5)
        else: arr = R.kb(img, u, 1.0, 1.0)
    arr = np.array(arr, dtype=np.uint8, copy=True)

    # ---- 제목 도장 "꽝" (0.0s) ----
    if cid in ("C01", "C02"):
        t1 = bt(10.4) - 0.12
        if T <= t1 + 0.18:
            if T < 0.1:
                s = 1.25 - 0.25 * (T / 0.1) ** 2
            else:
                d = T - 0.1; s = 1.0 + 0.08 * math.exp(-d * 14) * math.cos(d * 38)
            op = 1.0 if T <= t1 else clamp01(1 - (T - t1) / 0.18)
            paste_c(arr, SP["title"], 500, 350, s, 0, op)
        arr = shake(arr, T, 0.1)

    # ---- 그래픽 ----
    if cid == "C05":
        seal_drop(arr, SP["seal_gc"], 520, 936, T, STAMP_GAMCHO_T, rot=-4)
        sparkles(arr, T, STAMP_GAMCHO_T, [(700, 1160, 330), (520, 900, 200)], 9)
    if cid == "C06":
        seal_drop(arr, SP["seal_gun"], 277, 750, T, STAMP_GUN_T, rot=-3)
        seal_drop(arr, SP["seal_sin"], 825, 750, T, STAMP_SIN_T, rot=3)
        arr = shake(arr, T, STAMP_GUN_T); arr = shake(arr, T, STAMP_SIN_T)
    if cid == "C07":
        cloud_sway(arr, T); rain(arr, T)
    if cid == "C10":
        steam(arr, T, [(300, 1215, 2), (790, 1215, 2), (555, 790, 1)], strength=0.38, rise=230)
    if cid == "C13":
        steam(arr, T, [(356, 1380, 2), (745, 1360, 2)], strength=0.40, rise=190)
    if cid == "C12":
        pa = pop_anim(T, bt(92) + 0.10, 1e9, 0.35)
        if pa:
            s, op = pa
            paste_c(arr, SP["plaque"], 535, 700, 0.9 + 0.1 * s, 0, op)

    def sfx(name, t0, t1, x, y, rot=0):
        pa = pop_anim(T, t0, t1, 0.18, 0.12)
        if pa:
            s, op = pa
            wob = rot + 2.5 * math.sin((T - t0) * 22) * math.exp(-(T - t0) * 5)
            paste_c(arr, SP[name], x, y, s, wob, op)

    if cid == "C03a": sfx("sfx_ppae", bt(36), bt(40) - 0.05, 640, 1000, 6)
    if cid == "C03b": sfx("sfx_ppae", bt(40), bt(44) - 0.05, 700, 880, -6)
    if cid == "C03d": sfx("sfx_ppae", bt(44), bt(48) - 0.05, 300, 790, 6)
    if cid == "C06": sfx("sfx_kung", STAMP_GUN_T, STAMP_GUN_T + 0.5, 277, 530, -6)
    if cid == "C08": sfx("sfx_splash", SPLASH_T - 0.05, bt(69) - 0.02, 600, 1230, -6)
    if cid == "C09":
        pa = pop_anim(T, bt(69) + 0.45, bt(76) - 0.1, 0.3, 0.15)
        if pa:
            s, op = pa
            paste_c(arr, SP["bubble"], 400, 540, s, 1.2 * math.sin((T - bt(69)) * 6), op)

    def cap(name, t0, t1, top=270):
        """v4 캡션: 한지색 라벨. 등장 0.30s(위 16px에서 내려옴, ease-out cubic), 인장칩 0.12s 뒤 1.35->1.0(0.12s), 퇴장 0.20s(아래 8px)"""
        base, chip, cc = CAPS[name]
        if not (t0 <= T <= t1 + 0.2):
            return
        if T < t0 + 0.3:
            u = (T - t0) / 0.3; e = 1 - (1 - u) ** 3; op = e; dy = -16 * (1 - e)
        elif T <= t1:
            op = 1.0; dy = 0.0
        else:
            u = (T - t1) / 0.2; op = 1 - u; dy = 8 * u
        x = int(LYRIC_CX - base.shape[1] / 2); y = int(top - 20 + dy)
        over(arr, base, x, y, op)
        if chip is not None and T >= t0 + 0.12:
            cu = clamp01((T - t0 - 0.12) / 0.12); cs = 1.35 - 0.35 * cu
            paste_c(arr, chip, x + cc[0], y + cc[1], cs, 0, op)

    cap("cap_c02", 4.95, bt(15.9))
    cap("cap_c04", bt(16.3), bt(23.8))
    cap("cap_c06", STAMP_GUN_T + 0.58, bt(55.8))
    cap("cap_c08", bt(60.3), bt(66.6))
    cap("cap_c10", bt(76.4), bt(83.8))
    cap("cap_c11", bt(84.4), bt(91.8))
    cap("cap_c12", bt(92.4), bt(99.8), top=251)
    cap("cap_c13", bt(100.4), bt(107.8))

    # ---- 가사 ----
    cy = LYRIC_BAND.get(cid)
    if cy is not None:
        for ph in LY:
            if ph["vs"] <= T <= ph["ve"] + (0 if ph["hard_end"] else 0.1):
                draw_lyric_v2(arr, ph, T, ph['pin'] if ph.get('pin') else cy)
                break

    # ---- 엔딩 ----
    if cid == "C15":
        _d = json.load(open(OUT / "_work" / "lyrics_v41.json", encoding="utf8"))
        t1 = _d[-2]["t"][0] - SONG_START - 0.05          # 약방엔
        t2 = _d[-1]["t"][0] - SONG_START - 0.05          # 약령시엔
        t3 = _d[-1]["t"][4] - SONG_START - 0.05          # 쉼
        for name, tt, y in [("end1", t1, 335), ("end2", t2, 465), ("end3", t3, 595)]:
            pa = pop_anim(T, tt, 1e9, 0.28)
            if pa:
                s, op = pa
                paste_c(arr, SP[name], LYRIC_CX + 20, y, s, 0, op)
        if T >= 56.9:
            lb = CAPS["loc"][0]
            u = clamp01((T - 56.9) / 0.3); e = 1 - (1 - u) ** 3
            over(arr, lb, int(LYRIC_CX - lb.shape[1] / 2), int(700 - 20 - 16 * (1 - e)), e)
        if T >= 54.2:
            spr = SP["ai"]
            over(arr, spr, int(LYRIC_CX - spr.shape[1] / 2), 1500 - spr.shape[0], clamp01((T - 54.2) / 0.3))

    for sb in (48, 60, 92, 108):
        arr = flash(arr, T, bt(sb))
    return arr


def main():
    global LY, CAPS
    ap = argparse.ArgumentParser()
    ap.add_argument("--c06"); ap.add_argument("--frames"); ap.add_argument("--out", default=str(OUT / "_work" / "video_noaudio_v41.mp4"))
    a = ap.parse_args()
    if a.c06:
        R.SRC["C06"] = Path(a.c06)
    build_sprites_v2()
    CAPS = {k: (np.asarray(b), (np.asarray(c) if c is not None else None), cc) for k, (b, c, cc) in build_captions().items()}
    LY = plan_visibility(build_lyrics_v4())
    if a.frames:
        d = OUT / "_check" / "_test41"; d.mkdir(parents=True, exist_ok=True)
        for f in [int(x) for x in a.frames.split(",")]:
            Image.fromarray(render_frame(f)).save(d / f"f{f:04d}.png")
        print("saved")
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
    p.stdin.close(); p.wait(); print("done")


if __name__ == "__main__":
    from pathlib import Path
    main()
