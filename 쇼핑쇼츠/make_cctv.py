#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
「현관 CCTV」 시리즈 조립기.

assets/clips/<EP>/episode.json 의 타임라인대로 이미지·영상 컷을 이어 붙이고
CCTV 오버레이(타임스탬프·REC·노이즈·비네팅), 액운 자막, 타격 흔들림, PPL 카드를 입혀
output/<EP>/<EP>_youtube.mp4 (+ 클립용) 를 만든다.

  python make_cctv.py EP01
  python make_cctv.py EP01 --preview     프레임 미리보기 PNG만 (빠름)
"""
from __future__ import annotations

import argparse
import json
import math
import random
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_short import (ROOT, W, H, UI_ZONES, Fonts, enc, find_ffmpeg, fit, draw_lines,  # noqa: E402
                        load_config, prog, fade, fmt_count, star, run, wrap)

FPS = 30
CIRCLED = {"①": "1", "②": "2", "③": "3", "④": "4", "⑤": "5"}
GLYPH_FALLBACK = {"×": "x", "·": "/", "…": "..."}   # 글꼴에 글리프가 없을 때만 쓰는 대체 (갈무리11은 세 글자 모두 있음)
CTX: dict = {}        # build()가 채우는 실행 맥락 (ffmpeg, clips 폴더) - 증거 사진·썸네일에서 사용
NO_CAPS = False       # --thumb: 자막·도장 없이 그린다
NOISE_TILES = 6


# ----------------------------------------------------------------------------- 소스

def cover(im: Image.Image) -> Image.Image:
    """9:16 화면을 꽉 채우도록 키우고 가운데를 자른다."""
    return ImageOps.fit(im.convert("RGB"), (W, H), Image.LANCZOS)


DUMMY = False   # --dummy: 없는 이미지·영상은 단색 더미로 대체 (조립 점검용)


def load_still(path: Path) -> Image.Image:
    if DUMMY and not path.exists():
        h = sum(map(ord, path.stem)) % 360
        im = Image.new("HSV", (W, H), (h * 255 // 360, 60, 120)).convert("RGB")
        ImageDraw.Draw(im).ellipse([340, 700, 740, 1100], fill=(200, 200, 200))
        ImageDraw.Draw(im).text((60, 900), path.name, fill=(255, 255, 255))
        return im
    return cover(Image.open(path))


class DummySource:
    def __init__(self, path: Path, dur: float):
        self.base = load_still(path)
        self.i = 0

    def next(self) -> Image.Image:
        self.i += 1
        return self.base.rotate(math.sin(self.i / 6) * 1.2, resample=Image.BILINEAR)

    def close(self):
        pass


class VideoSource:
    """ffmpeg로 1080x1920·30fps RGB 프레임을 순서대로 읽는다."""

    def __init__(self, ff: str, path: Path, start: float, dur: float, speed: float = 1.0):
        """speed < 1 이면 슬로모션 (0.5 = 절반 속도). dur는 화면에 보이는 길이."""
        vf = (f"setpts={1 / speed:.4f}*PTS," if speed != 1 else "") + \
             f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}"
        self.proc = subprocess.Popen(
            [ff, "-loglevel", "error", "-ss", f"{start}", "-t", f"{dur * speed}", "-i", str(path),
             "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        self.last: Image.Image | None = None

    def next(self) -> Image.Image:
        buf = self.proc.stdout.read(W * H * 3)
        if len(buf) == W * H * 3:
            self.last = Image.frombytes("RGB", (W, H), buf)
        return self.last or Image.new("RGB", (W, H))

    def close(self):
        self.proc.stdout.close()
        self.proc.wait()


def zoom_scale(t: float, z: dict | None) -> float:
    """현재 줌 배율. "from" 이 있으면 from -> to (줌아웃 가능), 없으면 기존처럼 1 -> to."""
    if not z:
        return 1.0
    k = prog(t, z.get("at", 0), z.get("dur", 0.4))
    a = z.get("from", 1.0)
    return a + (z.get("to", 1.6) - a) * k


def zoomed(base: Image.Image, t: float, z: dict | None) -> Image.Image:
    """CCTV 디지털 줌: z = {"at":초, "dur":초, "to":배율, "from":시작 배율(선택, 줌아웃용), "cx":0~1, "cy":0~1}"""
    if not z:
        return base
    s = zoom_scale(t, z)
    if s <= 1.001:
        return base
    cw, ch = W / s, H / s
    cx, cy = z.get("cx", 0.5) * W, z.get("cy", 0.5) * H
    x0 = min(max(cx - cw / 2, 0), W - cw)
    y0 = min(max(cy - ch / 2, 0), H - ch)
    return base.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))


def bounced(im: Image.Image, t: float, spec: dict | None) -> Image.Image:
    """'통통' 흔들림: spec = {"at":[초,...], "amp":px(기본 6), "len":초(기본 0.22)}. 위로 튕겼다 두 번 잦아든다. 1.2% 안쪽 크롭으로 모서리를 가린다."""
    if not spec:
        return im
    amp, ln = spec.get("amp", 6), spec.get("len", 0.22)
    for h in spec.get("at", []):
        d = t - h
        if 0 <= d < ln:
            dy = -amp * (1 - d / ln) * abs(math.sin(d / ln * math.pi * 2))
            mx, my = W * 0.012, H * 0.012
            return im.resize((W, H), Image.BILINEAR, box=(mx, my + dy, W - mx, H - my + dy))
    return im


def shaken(im: Image.Image, t: float, hits: list[float]) -> Image.Image:
    """타격 순간 0.25초 동안 화면 흔들림."""
    for h in hits:
        d = t - h
        if 0 <= d < 0.25:
            a = int(28 * (1 - d / 0.25))
            dx = int(a * math.sin(d * 90))
            dy = int(a * 0.6 * math.cos(d * 70))
            out = Image.new("RGB", (W, H))
            out.paste(im, (dx, dy))
            return out
    return im


# ----------------------------------------------------------------------------- 적외선 룩

IR_DEFAULT = {
    "falloff": 0.75,      # 적외선 조명 감쇠 강도 (0=없음, 1=가장자리 완전 검정)
    "falloff_power": 2.2, # 클수록 중앙 밝은 영역이 좁고 가장자리가 빠르게 어두워짐
    "center_y": 0.46,     # 조명 중심 높이 (0~1)
    "gamma": 1.25,        # >1 이면 중간톤이 어두워짐
    "black": 0.07,        # 이 밝기 이하는 0으로 뭉갬 (블랙 크러시)
    "gain": 1.12,         # 전체 밝기 보정
    "bloom": 0.45,        # 하이라이트 번짐 강도
    "bloom_thr": 0.62,    # 번짐 임계값 (0~1)
    "bloom_radius": 26,   # 번짐 블러 반경(px)
    "grain": 0.05,        # 입자 노이즈 세기 (0~1, 어두운 곳에서 더 보임)
    "block": 0.35,        # 압축 블록 느낌 혼합 (0=없음)
    "block_quality": 22,  # JPEG 품질(낮을수록 블록 심함)
}


class IRLook:
    """흑백 적외선 CCTV 질감: 채도 0 + 중앙 조명 감쇠 + 블룸 + 블랙 크러시 + 입자/블록."""

    def __init__(self, params: dict | None = None):
        self.p = {**IR_DEFAULT, **(params or {})}
        self._mask = None

    def mask(self):
        if self._mask is None:
            p = self.p
            yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
            dx = (xx / W - 0.5) / 0.5
            dy = (yy / H - p["center_y"]) / 0.62
            r = np.sqrt(dx * dx + dy * dy)
            m = np.clip(1 - p["falloff"] * np.clip(r, 0, 1.6) ** p["falloff_power"] * 0.8, 0.0, 1.0)
            self._mask = m.astype(np.float32)
        return self._mask

    def apply(self, im: Image.Image, frame: int) -> Image.Image:
        p = self.p
        g = np.asarray(im.convert("L"), dtype=np.float32) / 255.0
        g = np.clip((g - p["black"]) / (1 - p["black"]), 0, 1) ** p["gamma"] * p["gain"]
        g = np.clip(g, 0, 1)
        if p["bloom"] > 0:
            hi = np.clip((g - p["bloom_thr"]) / (1 - p["bloom_thr"]), 0, 1)
            small = Image.fromarray((hi * 255).astype(np.uint8)).resize((W // 4, H // 4), Image.BILINEAR)
            small = small.filter(ImageFilter.GaussianBlur(p["bloom_radius"] / 4))
            bl = np.asarray(small.resize((W, H), Image.BILINEAR), dtype=np.float32) / 255.0
            g = np.clip(g + bl * p["bloom"], 0, 1)
        g = g * self.mask()
        if p["grain"] > 0:
            rng = np.random.default_rng(1000 + frame)
            n = rng.standard_normal((H // 2, W // 2)).astype(np.float32)
            n = np.repeat(np.repeat(n, 2, 0), 2, 1)
            g = np.clip(g + n * p["grain"] * (0.45 + 0.55 * (1 - g)), 0, 1)
        out = Image.fromarray((g * 255).astype(np.uint8)).convert("RGB")
        if p["block"] > 0:
            import io
            buf = io.BytesIO()
            out.save(buf, "JPEG", quality=int(p["block_quality"]))
            buf.seek(0)
            out = Image.blend(out, Image.open(buf).convert("RGB"), min(1.0, p["block"]))
        return out


# ----------------------------------------------------------------------------- 오버레이

class Overlay:
    def __init__(self, cfg: dict, fonts: Fonts, ep: dict):
        self.cfg, self.fonts, self.ep = cfg, fonts, ep
        rng = random.Random(7)
        self.noise = []
        for _ in range(NOISE_TILES):
            n = Image.effect_noise((W // 2, H // 2), 40).resize((W, H), Image.NEAREST)
            self.noise.append(Image.merge("RGBA", (n, n, n, n.point(lambda v: 26))))
        vig = Image.new("L", (W, H), 0)
        ImageDraw.Draw(vig).ellipse([-W * 0.25, -H * 0.12, W * 1.25, H * 1.12], fill=255)
        vig = vig.filter(ImageFilter.GaussianBlur(160))
        self.vignette = Image.merge("RGBA", (Image.new("L", (W, H), 0),) * 3 + (vig.point(lambda v: int((255 - v) * 0.55)),))
        self.rng = rng
        self.v5 = bool(ep.get("typo_v5", bool(ep.get("ai_label"))))
        self._noise_hi = None
        self._ink = None
        self._warned: set = set()
        irk = ep.get("ir_look")   # true / {파라미터} / 없음·false = 꺼짐 (config.json "ir_look" 은 기본 파라미터)
        self.ir = IRLook({**(cfg.get("ir_look") or {}), **(irk if isinstance(irk, dict) else {})}) if irk else None

    # ---- v5 글꼴 (osd / radio / doc). 없으면 heavy(Pretendard)로 대체하고 경고 1회
    EXPECT = {"osd": "Galmuri", "radio": "BlackHanSans", "doc": "NanumMyeongjo"}

    def fk(self, kind: str) -> str:
        if kind in self.EXPECT:
            ok = kind in self.fonts.paths and self.EXPECT[kind] in self.fonts.paths[kind]
            if not ok:
                if kind not in self._warned:
                    print(f"[경고] 글꼴 '{kind}'({self.EXPECT[kind]})를 찾지 못해 Pretendard로 대체합니다.")
                    self._warned.add(kind)
                return "heavy"
        return kind

    def has_glyph(self, kind: str, ch: str) -> bool:
        key = ("g", kind, ch)
        if key not in self._warned:
            ft = self.fonts.get(kind, 40)
            self._warned.add(key)
            self._glyph = getattr(self, "_glyph", {})
            self._glyph[key] = bytes(ft.getmask(ch)) != bytes(ft.getmask("􏿾"))
        return self._glyph[key]

    def safe_text(self, text: str, kind: str) -> str:
        """글꼴에 없는 글자는 경고하고 ①②③은 (1)(2)(3)으로 바꾼다 (원·사각형은 직접 그리는 쪽을 쓸 것)."""
        out = ""
        for ch in text:
            if ch.strip() and not self.has_glyph(kind, ch):
                if ("m", kind, ch) not in self._warned:
                    print(f"[경고] 글꼴 '{kind}'에 글리프 없음: {ch!r} -> 대체")
                    self._warned.add(("m", kind, ch))
                ch = GLYPH_FALLBACK.get(ch) or (CIRCLED.get(ch, "") and f"({CIRCLED[ch]})") or ch
            out += ch
        return out

    def cctv(self, im: Image.Image, t: float, frame: int, clock_override: str | None = None,
             boost: float = 0.0, site: bool = False, rec_fast: bool = False,
             morning: bool = False, clock_add: int = 0) -> Image.Image:
        f = self.fonts
        out = im.convert("RGBA")
        out.alpha_composite(self.noise[frame % NOISE_TILES])
        if boost > 0:  # 줌 확대 때 블록 노이즈 강화 (알파 26 -> 60)
            if self._noise_hi is None:
                self._noise_hi = []
                for _ in range(NOISE_TILES):
                    n = Image.effect_noise((W // 6, H // 6), 70).resize((W, H), Image.NEAREST)
                    self._noise_hi.append(Image.merge("RGBA", (n, n, n, Image.new("L", (W, H), 255))))
            out.alpha_composite(fade(self._noise_hi[frame % NOISE_TILES].copy(), (60 - 26) / 255 * boost))
        # 스캔라인
        if frame % 3 == 0 and self.ep.get("scanline", True):   # episode.json "scanline": false 면 흰 스캔라인 끔(EP10 v2)
            y = (frame * 37) % H
            ImageDraw.Draw(out).rectangle([0, y, W, y + 3], fill=(255, 255, 255, 18))
        out.alpha_composite(self.vignette)
        d = ImageDraw.Draw(out)
        hh, mm, ss = (int(x) for x in (clock_override or self.ep.get("clock", "03:14:07")).split(":"))
        sec = ss + int(t) + clock_add
        clock = f"{hh:02d}:{mm + sec // 60:02d}:{sec % 60:02d}"
        if self.v5:   # A: CAM·날짜·시각·REC도 갈무리 (osd)
            ok = self.fk("osd")
            mono = f.get(ok, int(self.cfg.get("osd_size", 40)))
            line = self.safe_text(f"{getattr(self, 'cam_seg', None) or self.ep.get('cam', 'CAM 01')}   {self.ep.get('date', '2026-10-03')}   {clock}", ok)
        else:
            mono = f.get("bold", 40)
            line = f"{getattr(self, 'cam_seg', None) or self.ep.get('cam', 'CAM 01')}   {self.ep.get('date', '2026-10-03')}   {clock}"
        sw = 4 if (self.v5 and morning) else 3
        if self.v5 and morning:   # 컬러(밝은) 컷: CAM 줄 뒤에 알파 110 판
            plate = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(plate).rounded_rectangle([44, 160, 1036, 224], radius=10, fill=(0, 0, 0, 110))
            out.alpha_composite(plate)
            d = ImageDraw.Draw(out)
        d.text((60, 172), line, font=mono, fill=(235, 235, 235), stroke_width=sw, stroke_fill=(0, 0, 0))
        blink = int(t * 10) % 2 == 0 if rec_fast else int(t * 2) % 2 == 0
        if blink:
            d.ellipse([870, 178, 900, 208], fill=(230, 40, 40))
        if blink or not rec_fast:
            d.text((912, 172), "REC", font=mono, fill=(235, 235, 235), stroke_width=sw, stroke_fill=(0, 0, 0))
        if site and self.site_text():
            self.site_label(d, out, self.site_text(), sw)
        return out

    def site_text(self) -> str:
        v = self.ep.get("site_label")
        return v.get("text", "") if isinstance(v, dict) else (v or "")

    def site_label(self, d, out, text: str, sw: int = 3):
        """① 현장 라벨: 노란 공사 줄무늬 아이콘 + osd 34px 흰 글자."""
        ic = Image.new("RGBA", (24, 24), (255, 200, 0, 255))
        idr = ImageDraw.Draw(ic)
        for off in range(-24, 30, 12):
            idr.line([(off, 24), (off + 24, 0)], fill=(20, 20, 20, 255), width=5)
        idr.rectangle([0, 0, 23, 23], outline=(0, 0, 0, 255), width=2)
        ft = self.fonts.get(self.fk("osd"), 34)
        text = self.safe_text(text, self.fk("osd"))
        if self.v5:   # E: 알파 110 판을 깔아 밝은 배경에서도 읽히게 (별도 RGBA 레이어로 합성)
            layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ld = ImageDraw.Draw(layer)
            ld.rounded_rectangle([54, 230, 96 + d.textlength(text, font=ft) + 14, 280], radius=8, fill=(0, 0, 0, 110))
            out.alpha_composite(layer)
            d = ImageDraw.Draw(out)
        out.alpha_composite(ic, (60, 244))
        d.text((96, 236), text, font=ft, fill=(255, 255, 255), stroke_width=sw, stroke_fill=(0, 0, 0))

    def ai_label(self, out: Image.Image, text: str, size: int | None = None, alpha: int | None = None):
        """② AI 연출 라벨: 우상단 오른쪽 끝 x=1020, y=236, 반투명 검은 박스. 항상 맨 위 레이어."""
        kind = self.fk("osd")
        size = int(size or self.cfg.get("ai_label_size", 34))
        ft = self.fonts.get(kind, size)
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        tw = d.textlength(text, font=ft)
        x1 = 1020
        d.rounded_rectangle([x1 - tw - 28, 236 - 6, x1, 236 + size + 14], radius=8,
                            fill=(0, 0, 0, alpha if alpha is not None else (190 if self.v5 else 150)))
        d.text((x1 - 14, 236), text, font=ft, fill=(255, 255, 255), anchor="ra")
        out.alpha_composite(layer)

    def ai_label_obj(self, out: Image.Image, spec: dict, t: float):
        """② 객체형: {"big":{"text":"AI 상황극","size":44,"until":3.0,"alpha":200},"text":"AI 연출","size":34,"alpha":190}
        0~until 은 큰 라벨, until 뒤 0.15초 동안 큰 라벨이 작은 크기로 줄어든 다음 상시 라벨."""
        big = spec.get("big")
        size, alpha = int(spec.get("size", 34)), int(spec.get("alpha", 190))
        text = spec.get("text", self.cfg.get("ai_label", "AI 연출"))
        if big:
            until, bs = float(big.get("until", 3.0)), int(big.get("size", 44))
            if t < until:
                return self.ai_label(out, big["text"], bs, int(big.get("alpha", 200)))
            if t < until + 0.15:
                k = (t - until) / 0.15
                return self.ai_label(out, big["text"], round(bs + (size - bs) * k),
                                     round(int(big.get("alpha", 200)) + (alpha - int(big.get("alpha", 200))) * k))
        self.ai_label(out, text, size, alpha)

    def zoom_label(self, out: Image.Image, t: float, text: str, until: float):
        """③ 판독 확대 라벨 (osd 40px 노랑, 3Hz 깜빡임)."""
        if t >= until or int(t * 6) % 2 == 1:
            return
        kind = self.fk("osd")
        ft = self.fonts.get(kind, 40)
        text = self.safe_text(text, kind)
        d = ImageDraw.Draw(out, "RGBA")
        tw = d.textlength(text, font=ft)
        d.rectangle([60, 296, 60 + tw + 28, 296 + 54], fill=(0, 0, 0, 130), outline=(255, 210, 60, 255), width=3)
        d.text((74, 300), text, font=ft, fill=(255, 210, 60), stroke_width=2, stroke_fill=(0, 0, 0))

    def caption(self, out: Image.Image, text: str, t: float, at: float, y: int, size=66,
                fill=(255, 255, 255), box=(0, 0, 0, 170)):
        k = prog(t, at, 0.15)
        if k <= 0:
            return
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        font, lines = fit(d, self.fonts, "heavy", text, 760, 2, size, 44)  # 오른쪽 버튼 영역(x>950) 피하기
        lh = int(font.size * 1.24)
        bw = max(d.textlength(ln, font=font) for ln in lines) + 60
        bh = lh * len(lines) + 34
        x0 = (W - bw) / 2
        d.rounded_rectangle([x0, y, x0 + bw, y + bh], radius=18, fill=box)
        draw_lines(d, lines, font, W // 2, y + 17, fill)
        out.alpha_composite(fade(layer, k))

    def ink_mask(self) -> Image.Image:
        if self._ink is None:
            n = Image.effect_noise((500, 500), 90)
            self._ink = n.point(lambda v: 255 if v > 95 else 70).filter(ImageFilter.GaussianBlur(0.8))
        return self._ink

    def stamp_circle(self, out, text, t, at, cx, cy, kind, dia, color):
        """결재 도장: 원형 테두리 + 굵은 명조 글자 + 거친 잉크 질감, 쾅 찍히는 0.18초."""
        k = prog(t, at, 0.18)
        s = 1.5 - 0.5 * k
        kind = self.fk(kind)
        D = int(dia * s)
        font = self.fonts.get(kind, int(dia * 0.5 * s))
        layer = Image.new("RGBA", (D + 40, D + 40), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        c = (D + 40) / 2
        col = color + (255,)
        d.ellipse([20, 20, 20 + D, 20 + D], outline=col, width=max(4, int(11 * s)))
        d.ellipse([20 + 16 * s, 20 + 16 * s, 20 + D - 16 * s, 20 + D - 16 * s], outline=col, width=max(2, int(3 * s)))
        d.text((c, c), self.safe_text(text, kind), font=font, fill=col, anchor="mm")
        layer = layer.rotate(-12, resample=Image.BICUBIC)
        a = ImageChops.multiply(layer.getchannel("A"), self.ink_mask().crop((0, 0) + layer.size))
        layer.putalpha(a)
        full = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        full.paste(layer, (int(cx - layer.width / 2), int(cy - layer.height / 2)))
        out.alpha_composite(fade(full, min(1.0, k * 1.5)))

    def stamp(self, out: Image.Image, text: str, t: float, at: float, cx: int, cy: int, color=(232, 52, 52),
              font: str | None = None, shape: str | None = None, dia: int = 220, plate: bool = False,
              size: int | None = None):
        """도장 찍히듯 커졌다 작아지며 등장. size: 글자 크기(선택, 기본 osd 99 / heavy 92)."""
        if t < at:
            return
        if shape == "circle":
            self.stamp_circle(out, text, t, at, cx, cy, font or "doc", dia,
                              color if color != (232, 52, 52) else (200, 30, 30))
            return
        k = prog(t, at, 0.18)
        s = 1.6 - 0.6 * k
        osd_stamp = bool(font) and self.fk(font) == "osd"
        if plate and color == (232, 52, 52):
            color = (240, 50, 50)
        font = self.fonts.get(self.fk(font) if font else "heavy", int((size or (99 if osd_stamp else 92)) * s))
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        tw = d.textlength(text, font=font)
        pad = int(26 * s)
        box = [cx - tw / 2 - pad, cy - font.size / 2 - pad, cx + tw / 2 + pad, cy + font.size / 2 + pad]
        if plate:   # D: 어두운 판 + 검정 외곽 글자 (중간 회색 배경에서도 읽히게)
            d.rounded_rectangle(box, radius=int(14 * s), fill=(0, 0, 0, 120))
        d.rounded_rectangle(box, radius=int(14 * s), outline=color + (255,), width=int(9 * s))
        if plate:
            d.text((cx, cy), text, font=font, fill=color + (255,), anchor="mm", stroke_width=int((3 if self.v5 else 5) * s),
                   stroke_fill=(0, 0, 0))
        else:
            d.text((cx, cy), text, font=font, fill=color + (255,), anchor="mm")
        layer = layer.rotate(-8, center=(cx, cy), resample=Image.BICUBIC)
        out.alpha_composite(fade(layer, min(1.0, k * 1.5)))

    def alert(self, out: Image.Image, t: float, at: float, box: list[float], until: float | None = None):
        """CCTV 움직임 감지: 빨간 박스 + 경고 문구가 깜빡인다. box = [x0,y0,x1,y1] (0~1). until: 이 초 이후에는 그리지 않음(선택)"""
        if t < at or (until is not None and t >= until) or int((t - at) * 6) % 2 == 1:
            return
        d = ImageDraw.Draw(out)
        x0, y0, x1, y1 = box[0] * W, box[1] * H, box[2] * W, box[3] * H
        d.rectangle([x0, y0, x1, y1], outline=(240, 40, 40), width=7)
        f = self.fonts.get(self.fk("osd"), 40) if self.v5 else self.fonts.get("heavy", 44)
        label = "움직임 감지"
        tw = d.textlength(label, font=f)
        d.rectangle([x0, y0 - 66, x0 + tw + 82, y0], fill=(240, 40, 40))
        tx, ty = x0 + 16, y0 - 33  # 경고 삼각형 (폰트 기호 대신 직접 그림)
        d.polygon([(tx + 20, ty - 20), (tx, ty + 17), (tx + 40, ty + 17)], fill="white")
        d.text((tx + 20, ty + 4), "!", font=self.fonts.get(self.fk("osd"), 30) if self.v5 else self.fonts.get("heavy", 30),
               fill=(240, 40, 40), anchor="mm")
        d.text((tx + 54, ty), label, font=f, fill="white", anchor="lm")

    def replay(self, out: Image.Image, t: float, speed: float, y: int = 248):
        """y = 아이콘 위쪽 (기본 248 = 기존 위치, v5는 episode "replay_y": 300)."""
        if int(t * 3) % 2 == 1:
            return
        d = ImageDraw.Draw(out)
        if self.v5:
            f = self.fonts.get(self.fk("osd"), 40)
            d.polygon([(62, y + 3), (62, y + 39), (92, y + 21)], fill=(255, 210, 60), outline=(0, 0, 0))
        else:
            f = self.fonts.get("heavy", 46)
            d.polygon([(62, y), (62, y + 42), (96, y + 21)], fill=(255, 210, 60), outline=(0, 0, 0))
        d.text((110 if not self.v5 else 104, y + 21), f"REPLAY  {speed:g}x", font=f, fill=(255, 210, 60), anchor="lm",
               stroke_width=3, stroke_fill=(0, 0, 0))

    def radio_caption(self, out: Image.Image, text: str, t: float, at: float, y: int, size=66,
                      badge: str | None = None, kind: str = "radio", cont: bool = False):
        """④ 무전 자막: radio 글꼴, 왼쪽 무전기 아이콘, 작전 번호 배지(노란 원), 등장 0.1초 '치직' 글리치."""
        if t < at:
            return
        k = 1.0 if cont else prog(t, at, 0.15)   # cont: 앞 세그먼트에서 이어지는 자막 (글리치·페이드 없음)
        kind = self.fk(kind)
        text = self.safe_text(text, kind)
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        pad, icon, gap = 30, 40, 14
        bd = 88 if badge else 0
        bg_ = 8 if badge else 0
        font, lines = fit(d, self.fonts, kind, text, 880 - bd - bg_ - 2 * pad - icon - gap, 2, size, 48)
        lh = int(font.size * 1.24)
        tw = max(d.textlength(ln, font=font) for ln in lines)
        bw = tw + 2 * pad + icon + gap
        bh = lh * len(lines) + 34
        total = bd + bg_ + bw
        xl = min((W - total) / 2, 940 - total)
        xb = xl + bd + bg_
        d.rounded_rectangle([xb, y, xb + bw, y + bh], radius=18, fill=(0, 0, 0, 170))
        ix, iy = xb + pad, y + bh / 2   # 무전기 아이콘 (흰 선)
        d.rounded_rectangle([ix + 6, iy - 10, ix + 30, iy + 18], radius=5, outline="white", width=3)
        d.line([(ix + 24, iy - 10), (ix + 24, iy - 22)], fill="white", width=3)
        for j in range(3):
            d.line([(ix + 12, iy - 4 + j * 6), (ix + 24, iy - 4 + j * 6)], fill="white", width=2)
        tx = xb + pad + icon + gap + tw / 2
        draw_lines(d, lines, font, tx, y + 17, (255, 255, 255))
        if badge:   # 원은 직접 그리고 숫자는 ASCII (검은고딕에 ①②③ 글리프 없음)
            cy = y + bh / 2
            d.ellipse([xl, cy - bd / 2, xl + bd, cy + bd / 2], fill=(255, 210, 0, 255), outline=(0, 0, 0, 255), width=4)
            num = CIRCLED.get(str(badge), str(badge))
            d.text((xl + bd / 2, cy + 2), num, font=self.fonts.get(kind, 58), fill=(0, 0, 0), anchor="mm")
        dt = t - at
        if 0 <= dt < 0.1 and not cont:  # 치직 글리치: 좌우 6px 흔들림 + 노이즈 줄
            dx = 6 if int(dt * FPS) % 2 == 0 else -6
            sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            sh.paste(layer, (dx, 0))
            layer = sh
            gd = ImageDraw.Draw(layer)
            for _ in range(3):
                gy = y + self.rng.randint(0, int(bh))
                gd.rectangle([xl, gy, xl + total, gy + 3], fill=(255, 255, 255, 140))
        out.alpha_composite(fade(layer, max(k, 0.6)))

    def tag(self, out: Image.Image, text: str, t: float, at: float, cx: int, cy: int):
        """⑤ 마스코트 명찰: 흰 사원증 카드 + 클립, 0.15초 튕김."""
        if t < at:
            return
        kind = "heavy" if self.v5 else self.fk("osd")
        text = self.safe_text(text, kind)
        ft = self.fonts.get(kind, 38 if self.v5 else 36)
        tmp = ImageDraw.Draw(Image.new("RGBA", (4, 4)))
        tw = tmp.textlength(text, font=ft)
        cw, ch = int(tw + 56), 84
        pad = 30
        card = Image.new("RGBA", (cw + 2 * pad, ch + 2 * pad), (0, 0, 0, 0))
        d = ImageDraw.Draw(card)
        d.rounded_rectangle([pad, pad + 8, pad + cw, pad + 8 + ch], radius=10, fill=(250, 250, 250, 255),
                            outline=(60, 60, 60, 255), width=3)
        d.rounded_rectangle([pad + cw / 2 - 22, pad - 8, pad + cw / 2 + 22, pad + 26], radius=7,
                            outline=(120, 120, 120, 255), width=5)  # 클립
        d.rounded_rectangle([pad + cw / 2 - 12, pad + 6, pad + cw / 2 + 12, pad + 18], radius=4, fill=(40, 40, 40, 255))
        d.text((pad + cw / 2, pad + 8 + ch / 2 + 2), text, font=ft, fill=(10, 10, 10), anchor="mm")
        dt = t - at
        sc = 0.8 + 0.3 * (dt / 0.075) if dt < 0.075 else 1.1 - 0.1 * min(1, (dt - 0.075) / 0.075)
        nw, nh = int(card.width * sc), int(card.height * sc)
        card = card.resize((nw, nh), Image.BICUBIC)
        full = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        full.paste(card, (int(cx - nw / 2), int(cy - nh / 2)))
        out.alpha_composite(full)

    def worklog(self, out: Image.Image, t: float, wl: dict):
        """⑥ 작업일지 결재 카드 (x 140-940, y 560-1160/결재 칸이 없으면 1060). 슬라이드업 0.15초.
        본문 줄은 0.15초 간격으로 순차 등장(줄1 at+0.15, 줄2 at+0.35), 도장은 stamps로."""
        at = wl.get("at", 0.0)
        if t < at:
            return
        k = prog(t, at, 0.15)
        kind = self.fk("doc")
        ap = wl.get("approval", ["반장", "본부"])
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        x0, y0, x1, y1 = 140, 560, 940, (1160 if ap else 1060)
        d.rounded_rectangle([x0 + 8, y0 + 12, x1 + 8, y1 + 12], radius=10, fill=(0, 0, 0, 90))
        d.rounded_rectangle([x0, y0, x1, y1], radius=10, fill=(245, 240, 225, 255), outline=(150, 145, 130, 255), width=3)
        ev = wl.get("evidence")   # 증거 사진: 카드 왼쪽 위, 제목·본문은 오른쪽/아래로 비킨다
        d.text((x0 + (352 if ev else 56), y0 + 52), self.safe_text(wl.get("title", ""), kind), font=self.fonts.get(kind, 40),
               fill=(90, 85, 70))
        d.line([(x0 + (346 if ev else 50), y0 + 112), (x1 - 50, y0 + 112)], fill=(90, 85, 70), width=4)
        yy = y0 + ((wl.get("body_y", 252)) if ev else 150)
        f54 = self.fonts.get(kind, 54)
        for i, ln in enumerate(wl.get("lines", [])[:4]):
            if wl.get("seq", True) and t < at + 0.15 + 0.2 * i:
                yy += 110
                continue
            d.text((x0 + 56, yy), self.safe_text(ln, kind), font=f54, fill=(20, 20, 20))
            d.line([(x0 + 50, yy + 70), (x1 - 50, yy + 70)], fill=(170, 165, 150), width=2)
            yy += 110
        f40 = self.fonts.get(kind, 40)
        if ap:  # 결재 칸: ☐ 글리프(나눔명조에 없음) 대신 사각형을 직접 그린다
            ay = y1 - 110
            d.line([(x0 + 50, ay - 20), (x1 - 50, ay - 20)], fill=(150, 145, 130), width=3)
            d.text((x0 + 56, ay), "결재:", font=f40, fill=(20, 20, 20))
            x = x0 + 56 + d.textlength("결재:", font=f40) + 26
            for who in ap:
                d.text((x, ay), who, font=f40, fill=(20, 20, 20))
                x += d.textlength(who, font=f40) + 12
                d.rectangle([x, ay + 2, x + 44, ay + 46], outline=(20, 20, 20), width=3)
                x += 44 + 36
        if ev:
            self.evidence(layer, ev, x0 + 190, y0 + 112)
        shift = int(120 * (1 - k))
        out.alpha_composite(fade(layer, k), (0, shift))

    def evidence_img(self, ev: dict) -> Image.Image:
        """증거 사진 원본 = 지정 enhance 세그먼트의 마지막 보정 단계 패널."""
        name = ev.get("from", "").split()[0]
        seg = next((sg for sg in self.ep["segments"] if sg.get("type") == "enhance" and sg.get("name") == name), None)
        if seg is None:
            raise SystemExit(f"[오류] worklog.evidence.from '{ev.get('from')}' 에 해당하는 enhance 세그먼트가 없습니다.")
        return enhance_source(seg).final_img()

    def evidence(self, layer: Image.Image, ev: dict, cx: int, cy: int):
        """판독 캡처를 3도 기울여 클립으로 집은 사진 + osd 26px 라벨."""
        w, h = ev.get("size", [260, 160])
        pad = 8
        card = Image.new("RGBA", (w + 2 * pad + 40, h + 2 * pad + 40), (0, 0, 0, 0))
        cd = ImageDraw.Draw(card)
        ox, oy = 20, 20
        cd.rectangle([ox + 5, oy + 6, ox + w + 2 * pad + 5, oy + h + 2 * pad + 6], fill=(0, 0, 0, 80))
        cd.rectangle([ox, oy, ox + w + 2 * pad, oy + h + 2 * pad], fill=(250, 250, 250, 255), outline=(120, 120, 110, 255))
        card.paste(self.evidence_img(ev).resize((w, h), Image.BILINEAR).convert("RGBA"), (ox + pad, oy + pad))
        mx = ox + (w + 2 * pad) // 2
        cd.rounded_rectangle([mx - 20, oy - 16, mx + 20, oy + 22], radius=7, outline=(110, 110, 110, 255), width=5)  # 클립
        cd.rounded_rectangle([mx - 11, oy - 2, mx + 11, oy + 8], radius=3, fill=(40, 40, 40, 255))
        card = card.rotate(-ev.get("tilt", 3), resample=Image.BICUBIC, expand=True)
        layer.alpha_composite(card, (int(cx - card.width / 2), int(cy - card.height / 2)))
        kind = self.fk("osd")
        ImageDraw.Draw(layer).text((cx, cy + h // 2 + pad + ev.get("label_dy", 6)), self.safe_text(ev.get("label", "첨부"), kind),
                                   font=self.fonts.get(kind, ev.get("label_size", 26)), fill=(40, 38, 30), anchor="ma")

    def product_tag(self, out: Image.Image, text: str, t: float, y: int = 300):
        """상품 앞쪽 노출 태그(2026-10-11): 좌상단 작은 어두운 판 + 흰 글자, 왼쪽에서 0.15초 슬라이드인.
        AI 화면 속 물건에 붙이지 않고 화면 모서리에만 둔다(상품을 AI로 그리지 않는 원칙)."""
        k = prog(t, 0, 0.15)
        if k <= 0:
            return
        ft = self.fonts.get("bold", 38)
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        tw = d.textlength(text, font=ft)
        d.rounded_rectangle([54, y, 54 + tw + 40, y + 62], radius=12, fill=(0, 0, 0, 175))
        d.rectangle([54, y + 10, 60, y + 52], fill=(255, 210, 60, 255))
        d.text((78, y + 31), text, font=ft, fill=(255, 255, 255), anchor="lm")
        out.alpha_composite(fade(layer, k), (-int(80 * (1 - k)), 0))

    def disclosure(self, out: Image.Image, plate: bool = False):
        d = ImageDraw.Draw(out)
        if self.v5 and plate:   # 밝은(컬러) 컷: 알파 110 판을 깔아 광고 표시 대비 확보
            ft = self.fonts.get("bold", int(self.cfg.get("disclosure_size", 34)))
            tw = d.textlength(self.cfg["disclosure_on_video"], font=ft)
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(lay).rounded_rectangle([W / 2 - tw / 2 - 24, 1430, W / 2 + tw / 2 + 24, 1440 + 34 + 24],
                                                  radius=10, fill=(0, 0, 0, 110))
            out.alpha_composite(lay)
            d = ImageDraw.Draw(out)
        if self.v5:
            d.text((W // 2, 1440), self.cfg["disclosure_on_video"],
                   font=self.fonts.get("bold", int(self.cfg.get("disclosure_size", 34))),
                   fill=(235, 235, 235), anchor="ma", stroke_width=3, stroke_fill=(0, 0, 0))
            return
        d.text((W // 2, 1440), self.cfg["disclosure_on_video"], font=self.fonts.get("regular", 32),
               fill=(220, 220, 220), anchor="ma", stroke_width=3, stroke_fill=(0, 0, 0))


# ----------------------------------------------------------------------------- PPL 카드

PPL_V6_EXTRA = 40   # 2상품 카드 v6 레이아웃(typo v2.1 FAIL 수정): 카드 높이 +40


def ppl_card(out: Image.Image, ep: dict, fonts: Fonts, cfg: dict, t: float, platform: str, dur: float) -> None:
    """PPL 카드. 끝 0.45초 동안 사라져서 첫 장면(조용한 현관)으로 자연스럽게 반복 재생된다."""
    p = ep["product"]
    c = cfg["colors"]
    k = prog(t, 0.15, 0.35) * (1 - prog(t, dur - 0.45, 0.35))
    if k <= 0:
        return
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x0, x1, top = 110, 930, 330
    ch = 900 + (PPL_V6_EXTRA if (ep.get("product_alt") and platform != "clip" and ep.get("ppl_layout") == "v6") else 0)
    d.rounded_rectangle([x0, top, x1, top + ch], radius=40, fill=(247, 243, 236, 250))
    d.rounded_rectangle([W // 2 - 150, top - 44, W // 2 + 150, top + 44], radius=44, fill=(232, 52, 52, 255))
    d.text((W // 2, top), ep.get("ppl_label", "PPL 타임"), font=fonts.get("heavy", 50), fill="white", anchor="mm")
    y = top + 90
    alt = ep.get("product_alt") if platform != "clip" else None
    if alt:
        ppl_two(d, ep, p, alt, fonts, c, x0, x1, top, platform, ch)
        ppl_notice(d, ep, fonts, cfg, top, ch)
        shift = int(60 * (1 - k))
        out.alpha_composite(fade(layer, k), (0, shift))
        return
    font, lines = fit(d, fonts, "heavy", p.get("short", p["name"]), x1 - x0 - 80, 2, 66, 46)
    y = draw_lines(d, lines, font, W // 2, y, c["ink"]) + 6
    font, lines = fit(d, fonts, "bold", p["role"], x1 - x0 - 80, 2, 44, 34)
    y = draw_lines(d, lines, font, W // 2, y, c["muted"]) + 34
    d.text((W // 2, y), f"{p['price']:,}원", font=fonts.get("heavy", 112), fill=c["accent"], anchor="ma")
    y += 150
    rv = f"리뷰 {p['reviews']:,}개"
    rt = f"{p['rating']:.2f}"
    f1, f2 = fonts.get("heavy", 56), fonts.get("heavy", 56)
    total = d.textlength(rv, font=f1) + 60 + 46 + 12 + d.textlength(rt, font=f2)
    x = (W - total) / 2
    d.text((x, y), rv, font=f1, fill=c["ink"])
    x += d.textlength(rv, font=f1) + 60
    star(d, x + 23, y + 32, 23, c.get("star", "#F2A900"))
    d.text((x + 58, y), rt, font=f2, fill=c["ink"])
    y += 110
    d.line([(x0 + 60, y), (x1 - 60, y)], fill=c.get("line", "#E8E2D8"), width=3)
    y += 34
    if ep.get("ppl_notes_lines"):   # 선택: ※ 문구를 줄마다 따로 (긴 문구가 한 줄 28px로 줄어드는 것 방지)
        for nt in ep.get("ppl_notes", [])[:2]:
            f, ln = fit(d, fonts, "bold", nt, x1 - x0 - 80, 1, 38, 28)
            d.text((W // 2, y), ln[0], font=f, fill=c["ink"], anchor="ma")
            y += 48
    else:
        notes = "   ".join(ep.get("ppl_notes", []))
        if notes:
            f, ln = fit(d, fonts, "bold", notes, x1 - x0 - 80, 1, 40, 28)
            d.text((W // 2, y), ln[0], font=f, fill=c["ink"], anchor="ma")
    cta = ppl_cta(ep, platform)
    if cta:
        d.rounded_rectangle([x0 + 50, top + 900 - 170, x1 - 50, top + 900 - 90], radius=40, fill=c["dark_bg"])
        d.text((W // 2, top + 900 - 130), cta, font=fonts.get("heavy", 44), fill=c["highlight"], anchor="mm")
    d.text((W // 2, top + 900 - 60), f"{ep.get('price_date', '')} 상품 페이지 기준",
           font=fonts.get("regular", 32 if ep.get("typo_v5", bool(ep.get("ai_label"))) else 30),
           fill=c["muted"], anchor="ma")
    ppl_notice(d, ep, fonts, cfg, top)
    shift = int(60 * (1 - k))
    out.alpha_composite(fade(layer, k), (0, shift))


def ppl_notice(d, ep: dict, fonts: Fonts, cfg: dict, top: int, ch: int = 900) -> None:
    """⑨ PPL 카드 최하단 AI 연출 고지 (episode "ai_notice_ppl": true, 문구는 config.json).
    32px 이상 + 어두운 박스로 대비 확보."""
    if not ep.get("ai_notice_ppl", bool(ep.get("ai_label"))):   # v5 에피소드(ai_label 사용)는 기본 켬
        return
    text = cfg.get("ai_notice_ppl", "영상 속 장면은 AI 연출이며 실제 제품의 성능과 다릅니다. 기능·사용법은 상품 페이지 확인")
    size = max(32, int(cfg.get("ai_notice_size", 32)))
    font = fonts.get("bold", size)   # J: 두께만 올림 (SemiBold)
    lines = wrap(d, text, font, 780)
    lh = int(size * 1.3)
    y0 = top + ch + 18
    bh = lh * len(lines) + 24
    d.rounded_rectangle([110, y0, 930, y0 + bh], radius=16, fill=(0, 0, 0, 190))
    y = y0 + 12
    for ln in lines:
        d.text((W // 2, y), ln, font=font, fill=(235, 235, 235), anchor="ma", stroke_width=2, stroke_fill=(0, 0, 0))
        y += lh


def ppl_cta(ep: dict, platform: str) -> str:
    """틱톡엔 설명란 링크가 없어서 '다른 곳 링크' 안내 대신 검색 안내를 기본으로 쓴다."""
    default = {"tiktok": "네이버·쿠팡에서 위 상품명 검색"}.get(platform, "")
    return ep.get("ppl_cta", {}).get(platform, default)


def ppl_two(d, ep: dict, p: dict, alt: dict, fonts: Fonts, c: dict, x0: int, x1: int, top: int,
            platform: str = "youtube", ch: int = 900) -> None:
    """두 판매처 상품을 각각 정확한 정보로 보여 준다 (서로 다른 상품이면 이름·가격·리뷰를 따로)."""
    font, lines = fit(d, fonts, "heavy", ep.get("ppl_headline", p["role"]), x1 - x0 - 80, 2, 58, 42)
    y = draw_lines(d, lines, font, W // 2, top + 86, c["ink"]) + 18
    v5 = bool(ep.get("typo_v5", bool(ep.get("ai_label"))))
    bh, gap_, chip_w, chip_fs = (192, 212, 112, 34) if v5 else (200, 222, 96, 30)
    v6 = ep.get("ppl_layout") == "v6"
    if v6:
        bh, gap_ = 235, 245
    for q in (p, alt):
        d.rounded_rectangle([x0 + 40, y, x1 - 40, y + bh], radius=26, fill=(255, 255, 255, 255),
                            outline=c.get("line", "#E8E2D8"), width=3)
        tag = q.get("store", "")
        d.rounded_rectangle([x0 + 66, y + 24, x0 + 66 + chip_w, y + 70], radius=23,
                            fill=(3, 199, 90, 255) if tag == "네이버" else (52, 106, 255, 255))
        d.text((x0 + 66 + chip_w // 2, y + 47), tag, font=fonts.get("heavy", chip_fs),
               fill=(20, 20, 20) if (v5 and tag == "네이버") else "white", anchor="mm")
        nm = q.get("short", q["name"])
        if v6:   # 상품명 27px(안 되면 26) 행간 1.3 최대 2줄 / 상품명-가격 간격 10px / 옵션은 가격 줄 앞
            nx = x0 + 84 + chip_w
            f, ln = fit(d, fonts, "bold", nm, (x1 - 60) - nx, 2, 27, 26)
            lh = int(f.size * 1.3)
            for li, t_ in enumerate(ln[:2]):
                d.text((nx, y + 44 + li * lh), t_, font=f, fill=c["ink"], anchor="lm")
            pb = y + 44 + lh + f.size // 2 + 10 + 56      # 상품명 블록 하단 + 10 + 가격 윗면~기준선
            px = x0 + 66
            if q.get("option"):
                of = fonts.get("bold", 34)
                d.text((px, pb), q["option"], font=of, fill=c["ink"], anchor="ls")
                px += d.textlength(q["option"], font=of) + 14
            d.text((px, pb), f"{q['price']:,}원", font=fonts.get("heavy", 70), fill=c["accent"], anchor="ls")
            meta = f"리뷰 {q['reviews']:,}개" + (f" · ★{q['rating']:.2f}" if q.get("rating") else "")
            d.text((x0 + 66, pb + 46), meta, font=fonts.get("bold", 36), fill=c["ink"], anchor="ls")
            y += gap_
            continue
        f, ln = fit(d, fonts, "bold", nm, x1 - x0 - 270 - (chip_w - 96), 1, 38, 28)
        if ln[-1].endswith("…") and len(ln) == 1:   # 한 줄에 안 들어가는 긴 상품명은 2줄로 (단어 생략 방지)
            f, ln = fit(d, fonts, "bold", nm, x1 - x0 - 270 - (chip_w - 96), 2, 28, 24)
            d.text((x0 + 84 + chip_w, y + 30), ln[0], font=f, fill=c["ink"], anchor="lm")
            if len(ln) > 1:
                d.text((x0 + 84 + chip_w, y + 30 + int(f.size * 1.1)), ln[1], font=f, fill=c["ink"], anchor="lm")
        else:
            d.text((x0 + 84 + chip_w, y + 47), ln[0], font=f, fill=c["ink"], anchor="lm")
        d.text((x0 + 66, y + (128 if v5 else 134)), f"{q['price']:,}원", font=fonts.get("heavy", 70), fill=c["accent"], anchor="ls")
        meta = f"리뷰 {q['reviews']:,}개" + (f" · ★{q['rating']:.2f}" if q.get("rating") else "")
        d.text((x0 + 66, y + 180 + (2 if v5 else 0)), meta, font=fonts.get("bold", 36 if v5 else 34), fill=c["ink"], anchor="ls")
        y += gap_
    if v5:   # H: ※ 줄은 줄마다 따로, heavy 36 가운데 (첫 줄 강조색) - 마지막 웃음이 카드에서 가장 약하지 않게
        yy = y + 4 - 8
        for i, note in enumerate(ep.get("ppl_notes", [])[:2]):
            f, ln = fit(d, fonts, "heavy", note, x1 - x0 - 80, 1, 36, 28)
            d.text((W // 2, yy), ln[0], font=f, fill=(201, 58, 32) if i == 0 else c["ink"], anchor="ma")
            yy += 45
    else:
        notes = "   ".join(ep.get("ppl_notes", []))
        if notes:
            f, ln = fit(d, fonts, "bold", notes, x1 - x0 - 80, 1, 34, 26)
            d.text((W // 2, y + 8), ln[0], font=f, fill=c["ink"], anchor="ma")
    cta = ppl_cta(ep, platform)
    if cta:
        d.rounded_rectangle([x0 + 50, top + ch - 170, x1 - 50, top + ch - 90], radius=40, fill=c["dark_bg"])
        d.text((W // 2, top + ch - 130), cta, font=fonts.get("heavy", 44), fill=c["highlight"], anchor="mm")
    d.text((W // 2, top + ch - 60), f"{ep.get('price_date', '')} 각 상품 페이지 기준", font=fonts.get("regular", 34 if v5 else 30),
           fill=(70, 70, 70) if v5 else c["muted"], anchor="ma")


# ----------------------------------------------------------------------------- 조립

def open_video(ff: str, path: Path, start: float, dur: float, speed: float = 1.0):
    if DUMMY and not path.exists():
        return DummySource(path, dur)
    return VideoSource(ff, path, start, dur, speed)


def particles(base: Image.Image, lt: float, pc: dict) -> Image.Image:
    """③ 훅 털 입자: 0~until초 동안 가는 털 조각이 떠다니고 화면이 8Hz로 살짝 흔들린다(shake px)."""
    until = pc.get("until", 0.8)
    t0 = pc.get("from", 0.0)       # 이 초부터 시작(선택). 없으면 컷 시작부터
    if lt >= until or lt < t0:
        return base
    lt = lt - t0
    until = until - t0
    sh = pc.get("shake", 4)
    if sh:
        dx = int(sh * math.sin(2 * math.pi * 8 * lt))
        moved = Image.new("RGB", (W, H))
        moved.paste(base, (dx, 0))
        base = moved
    rnd = random.Random(pc.get("seed", 11))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    fadek = 1 - prog(lt, until - 0.2, 0.2)
    for _ in range(pc.get("n", 45)):
        x0, y0 = rnd.uniform(0, W), rnd.uniform(300, 1500)
        vx, vy = rnd.uniform(-40, 40), rnd.uniform(-90, -20)
        ln, ang = rnd.uniform(14, 34), rnd.uniform(0, math.pi)
        x = x0 + vx * lt + 12 * math.sin(lt * 7 + x0)
        y = y0 + vy * lt
        dx, dy = math.cos(ang) * ln, math.sin(ang) * ln
        d.line([(x - dx, y - dy), (x, y), (x + dx * 0.5, y + dy * 0.2 + 5)], fill=(235, 235, 235, int(190 * fadek)), width=2)
    out = base.convert("RGBA")
    out.alpha_composite(layer)
    return out.convert("RGB")


def frame_drop(out: Image.Image, lt: float, rnd: random.Random) -> None:
    """⑪ 프레임 드롭 정지 컷: 가로 노이즈 바 + 가로로 밀린 줄."""
    for _ in range(3):
        y = rnd.randint(200, H - 300)
        h = rnd.randint(10, 46)
        dx = rnd.randint(-40, 40)
        strip = out.crop((0, y, W, y + h))
        out.paste(strip, (dx, y))
    d = ImageDraw.Draw(out, "RGBA")
    for _ in range(4):
        y = rnd.randint(160, H - 200)
        d.rectangle([0, y, W, y + rnd.randint(3, 14)], fill=(255, 255, 255, rnd.randint(70, 150)))


def swap_frame(stills: list, lt: float, seg: dict) -> Image.Image:
    """⑧ 이미지 N장 교차. swap초 간격 하드컷 + 교차마다 회전 흔들림(swap_rot도, 기본 ±2도, 점점 0으로).
    hold_last > 0 이면 마지막 hold_last초는 마지막 이미지를 정지(미세 줌인 hold_zoom)."""
    dur = seg["dur"]
    hold = seg.get("hold_last", 0.0)
    if hold and lt >= dur - hold:
        return zoomed(stills[-1], lt, {"at": dur - hold, "dur": hold, "to": 1 + seg.get("hold_zoom", 0.04)})
    tail = seg.get("tail_dur", 0.0)   # 마지막 이미지는 순환에서 빼고 마지막 tail_dur초만 정지로 보여 준다 (예: 와이드 0.1초)
    if tail and lt >= dur - tail:
        return stills[-1]
    if tail:
        stills = stills[:-1]
    durs = seg.get("durs")            # 이미지별 노출 시간 목록(초). 없으면 swap 간격으로 균등 교차
    if durs:
        edges, acc = [], 0.0
        for dd in durs:
            acc += dd
            edges.append(acc)
        step = next((i for i, e in enumerate(edges) if lt < e), len(durs) - 1)
        swap = durs[step]
        t_in = lt - (edges[step] - swap)
        base = stills[step % len(stills)]
        ang = (1 if step % 2 == 0 else -1) * seg.get("swap_rot", 2.0) * (1 - t_in / max(swap, 0.01))
    else:
        swap = seg.get("swap", 0.3)
        step = int(lt / swap)
        base = stills[step % len(stills)]
        ang = (1 if step % 2 == 0 else -1) * seg.get("swap_rot", 2.0) * (1 - (lt - step * swap) / swap)
    if abs(ang) < 0.05:
        return base
    rot = base.rotate(ang, resample=Image.BILINEAR)  # 회전으로 생긴 검은 모서리는 4% 안쪽 크롭으로 가린다
    return rot.resize((W, H), Image.BILINEAR, box=(W * 0.04, H * 0.04, W * 0.96, H * 0.96))



# ----------------------------------------------------------------------------- ⑫ 판독 확대 (type: "enhance")

_PREV: dict = {}   # 직전 세그먼트의 마지막 베이스 프레임·감지 박스 (판독 화면 배경용)
YELLOW = (255, 210, 60)


class EnhanceSource:
    """판독 패널에 쓸 소스(이미지 N장 또는 영상 정지 프레임) + 단계별 화질 뭉개기 캐시.

    단계 [시작초, 블록px]: 블록 크기는 '패널 출력 px' 기준이라 소스 해상도와 무관하게 같은 결과.
    min_block(기본 12): 어떤 단계도 이보다 작은 블록은 쓰지 않는다 -> 마지막 단계에서도 얼굴 이목구비가 안 읽힌다."""

    def __init__(self, seg: dict, ff: str, clips: Path):
        self.seg, self.ff, self.clips = seg, ff, clips
        px, py, self.pw, self.ph = seg.get("panel", [40, 520, 1000, 610])
        self.rect = (px, py, self.pw, self.ph)
        self.minb = max(1, int(seg.get("min_block", 12)))
        self.stages = [[float(a), int(b)] for a, b in seg.get("stages", [[0.0, 30], [0.4, 20], [0.8, 13]])]
        for st in self.stages:
            if st[1] < self.minb:
                print(f"[경고] {seg.get('name', '')}: 블록 {st[1]}px < min_block {self.minb} -> {self.minb}px로 올림")
                st[1] = self.minb
        self.raw: dict[str, Image.Image] = {}
        self.cache: dict = {}
        rng = np.random.default_rng(5)
        self.noise = [Image.fromarray(rng.integers(0, 256, (self.ph, self.pw), dtype=np.uint8)).convert("RGB")
                      for _ in range(4)]
        c = seg.get("crop") or [0, 0, 0, 0]
        if len(c) != 4 or c[2] <= 0 or c[3] <= 0:
            print(f"[경고] {seg.get('name', '')}: crop 미지정 -> 이미지 전체(패널 비율로 가운데 자름)")

    def _load(self, name: str) -> Image.Image:
        if name in self.raw:
            return self.raw[name]
        if name == "@src":
            path = self.clips / self.seg["src"]
            if DUMMY and not path.exists():
                im = Image.new("RGB", (496, 864), (90, 90, 90))
                ImageDraw.Draw(im).ellipse([250, 400, 420, 480], fill=(200, 200, 200))
            else:
                r = subprocess.run([self.ff, "-loglevel", "error", "-ss", str(self.seg.get("freeze", 0)), "-i", str(path),
                                    "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True)
                import io
                im = Image.open(io.BytesIO(r.stdout)).convert("RGB")
        else:
            path = self.clips / name
            if DUMMY and not path.exists():
                im = load_still(path)
            else:
                im = Image.open(path).convert("RGB")
        x, y, w, h = (self.seg.get("crop") or [0, 0, 0, 0])
        iw, ih = im.size
        if w <= 0 or h <= 0:
            aw = self.pw / self.ph
            if iw / ih > aw:
                w, h = round(ih * aw), ih
            else:
                w, h = iw, round(iw / aw)
            x, y = (iw - w) // 2, (ih - h) // 2
        self.raw[name] = im.crop((x, y, x + w, y + h))
        return self.raw[name]

    def frame_at(self, lt: float) -> str:
        for ins in self.seg.get("inserts", []):
            if ins["at"] <= lt < ins["at"] + ins["dur"]:
                return ins["file"]
        fr = self.seg.get("frames") or ["@src"]
        return fr[int(lt / max(self.seg.get("frame_swap", 0.33), 0.01)) % len(fr)]

    def stage_at(self, lt: float) -> int:
        return max([i for i, (t, _) in enumerate(self.stages) if lt >= t] or [0])

    def stage_img(self, name: str, si: int) -> Image.Image:
        key = (name, si)
        if key in self.cache:
            return self.cache[key]
        import io
        b = self.stages[si][1]
        im = self._load(name).resize((self.pw, self.ph), Image.LANCZOS)
        small = im.resize((max(1, round(self.pw / b)), max(1, round(self.ph / b))), Image.BOX)   # 블록 모자이크
        im = small.resize((self.pw, self.ph), Image.NEAREST)
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=18)                                                       # JPEG 재압축 1회
        buf.seek(0)
        im = Image.open(buf).convert("RGB").filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=0))  # 과보정 테두리
        arr = np.asarray(im, dtype=np.float32).copy()
        arr[1::2] *= 1 - 40 / 255                                                              # 스캔라인(2px 간격, 알파 40)
        im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
        self.cache[key] = im
        return im

    def final_img(self) -> Image.Image:
        """마지막 단계 패널 (작업일지 증거 사진·썸네일용, 노이즈·플래시 없음)."""
        return self.stage_img(self.frame_at(self.stages[-1][0] + 0.001), len(self.stages) - 1)


def enhance_source(seg: dict) -> EnhanceSource:
    reg = CTX.setdefault("es", {})
    k = seg.get("name", id(seg))
    if k not in reg:
        reg[k] = EnhanceSource(seg, CTX["ff"], CTX["clips"])
    return reg[k]


def enhance_bg(prev: Image.Image | None) -> Image.Image:
    """직전 와이드 마지막 프레임 정지, 밝기 40%, 가우시안 블러 6px."""
    if prev is None:
        return Image.new("RGB", (W, H))
    return Image.blend(prev.filter(ImageFilter.GaussianBlur(6)), Image.new("RGB", (W, H)), 0.6)


def draw_enhance(ov: "Overlay", out: Image.Image, seg: dict, lt: float, es: EnhanceSource, pbox, frame: int):
    """⑫ 판독 UI: 패널 + 보정 단계 연출 + 상·하단 UI 줄 + 결과 문구. out은 RGBA."""
    px, py, pw, ph = es.rect
    si = es.stage_at(lt)
    st_t = es.stages[si][0]
    n = len(es.stages)
    panel = es.stage_img(es.frame_at(lt), si)
    dt = lt - st_t
    if si > 0 and dt < 0.06:
        panel = Image.blend(panel, Image.new("RGB", panel.size, (255, 255, 255)), 80 / 255)
    panel = Image.blend(panel, es.noise[frame % len(es.noise)], 35 / 255)
    d = ImageDraw.Draw(out, "RGBA")
    k = prog(lt, 0, 0.15)
    if k < 1:   # 진입: 감지 박스 -> 패널로 커지고, 박스 네 모서리에서 흰 선 4개가 패널 모서리로 뻗는다
        bx0, by0, bx1, by1 = pbox
        x0, y0 = bx0 + (px - bx0) * k, by0 + (py - by0) * k
        x1, y1 = bx1 + (px + pw - bx1) * k, by1 + (py + ph - by1) * k
        w_, h_ = max(2, int(x1 - x0)), max(2, int(y1 - y0))
        out.paste(panel.resize((w_, h_), Image.BILINEAR).convert("RGBA"), (int(x0), int(y0)))
        d.rectangle([x0 - 1, y0 - 1, x1 + 1, y1 + 1], outline=(255, 255, 255, 255), width=2)
        for (cx_, cy_), (tx_, ty_) in zip([(bx0, by0), (bx1, by0), (bx0, by1), (bx1, by1)],
                                          [(px, py), (px + pw, py), (px, py + ph), (px + pw, py + ph)]):
            d.line([(cx_, cy_), (cx_ + (tx_ - cx_) * k, cy_ + (ty_ - cy_) * k)], fill=(255, 255, 255, 255), width=3)
        return
    out.paste(panel.convert("RGBA"), (px, py))
    if si > 0 and dt < 0.12:   # 위 -> 아래 스캔 바
        sy = py + int(dt / 0.12 * (ph - 12))
        d.rectangle([px, sy, px + pw, sy + 12], fill=(255, 255, 255, 170))
    d.rectangle([px - 1, py - 1, px + pw + 1, py + ph + 1], outline=(255, 255, 255, 255), width=2)
    for cx_, cy_ in [(px + 36, py + 36), (px + pw - 36, py + 36), (px + 36, py + ph - 36), (px + pw - 36, py + ph - 36)]:
        d.line([(cx_ - 18, cy_), (cx_ + 18, cy_)], fill=(255, 255, 255, 230), width=2)
        d.line([(cx_, cy_ - 18), (cx_, cy_ + 18)], fill=(255, 255, 255, 230), width=2)
    mx, my = px + pw // 2, py + ph // 2
    for a, b in [((mx - 60, my), (mx - 12, my)), ((mx + 12, my), (mx + 60, my)),
                 ((mx, my - 60), (mx, my - 12)), ((mx, my + 12), (mx, my + 60))]:
        d.line([a, b], fill=(255, 255, 255, 120), width=1)
    ui = seg.get("ui", {})
    if ui.get("pause_icon"):
        for bx in (px + 76, px + 94):
            d.rectangle([bx, py + 16, bx + 10, py + 46], fill=(255, 255, 255, 255))
    kind = ov.fk("osd")
    f36, f34 = ov.fonts.get(kind, 36), ov.fonts.get(kind, 34)
    if ui.get("top_l"):
        d.text((px, py - 50), ov.safe_text(ui["top_l"], kind), font=f36, fill=YELLOW, stroke_width=3, stroke_fill=(0, 0, 0))
    if ui.get("top_r"):
        d.text((px + pw, py - 50), ov.safe_text(ui["top_r"], kind), font=f36, fill=YELLOW, anchor="ra",
               stroke_width=3, stroke_fill=(0, 0, 0))
    by = py + ph + 20
    if ui.get("progress", True):
        d.rectangle([px, by, px + 420, by + 14], outline=(255, 255, 255, 255), width=2, fill=(0, 0, 0, 120))
        d.rectangle([px + 2, by + 2, px + 2 + int(416 * (si + 1) / n), by + 12], fill=YELLOW + (255,))
        d.text((px + pw, by - 10), f"보정 {si + 1}/{n}", font=f34, fill=(255, 255, 255), anchor="ra",
               stroke_width=3, stroke_fill=(0, 0, 0))
    if ui.get("result") and lt >= es.stages[-1][0] + 0.15:
        text = ov.safe_text(ui["result"], kind)
        size = 38
        while size > 28 and d.textlength(text, font=ov.fonts.get(kind, size)) > pw - 48:
            size -= 2
        f = ov.fonts.get(kind, size)
        tw = d.textlength(text, font=f)
        cy = py + ph + 70
        d.rounded_rectangle([W / 2 - tw / 2 - 24, cy, W / 2 + tw / 2 + 24, cy + size + 24], radius=8, fill=(0, 0, 0, 190))
        d.text((W / 2, cy + 12), text, font=f, fill=(255, 255, 255), anchor="ma")


def render_segment(seg: dict, ep: dict, ov: Overlay, ff: str, clips: Path, t0: float, frame0: int,
                   platform: str = "youtube"):
    """한 컷의 프레임을 차례로 돌려준다 (전체 시간 기준 t)."""
    dur = seg["dur"]
    ov.cam_seg = seg.get("cam")   # 컷별 카메라 이름(선택). 없으면 episode.json cam
    n = round(dur * FPS)
    src = None
    still = None
    stills = None
    dsrc = None
    speed = seg.get("speed", 1.0)
    dis = seg.get("dissolve")
    es = enh_bg = None
    prev_alerts: list = []
    pbox = None
    if seg["type"] == "enhance":
        CTX.update(ff=ff, clips=clips)
        es = enhance_source(seg)
        enh_bg = enhance_bg(_PREV.get("base"))
        prev_alerts = [al for al in _PREV.get("alerts", []) if "until" not in al]   # until이 있는 박스는 이미 꺼진 것
        pb = prev_alerts[-1]["box"] if prev_alerts else [0.4, 0.45, 0.6, 0.55]
        pbox = (pb[0] * W, pb[1] * H, pb[2] * W, pb[3] * H)
    elif seg["type"] == "video":
        # src_dur: 원본에서 읽을 길이(초). 없으면 dur*speed. 아주 짧게 주면 마지막 프레임이 정지로 유지된다(프리즈)
        vdur = seg["src_dur"] / speed if seg.get("src_dur") else dur
        src = open_video(ff, clips / seg["file"], seg.get("start", 0), vdur, speed)
    elif seg.get("files"):
        stills = [load_still(clips / f) for f in seg["files"]]
    else:
        still = load_still(clips / seg["file"])
    if dis:  # 이미지(크롭 줌아웃) -> 영상 클립 디졸브: 영상은 dissolve.at초부터 재생
        dsrc = open_video(ff, clips / dis["file"], dis.get("start", 0), max(dur - dis.get("at", 0.8), 0.1),
                          dis.get("speed", 1.0))
    slv = ep.get("site_label")
    sl = ([slv.get("from", 0.0), slv.get("until", 10.0)] if isinstance(slv, dict)
          else ep.get("site_label_range", [0.0, 10.0]))
    ai = ep.get("ai_label", ov.cfg.get("ai_label_default", False))
    ir = ov.ir
    # 시계 점프 누적: 앞 컷들의 frame_drop.clock_jump(객체형)를 합쳐 이후 컷의 시계에 계속 반영한다 (되돌아가지 않음)
    clock_carry = 0
    for sg in ep["segments"]:
        if sg is seg:
            break
        if isinstance(sg.get("frame_drop"), dict):
            clock_carry += int(sg["frame_drop"].get("clock_jump", 1))
    try:
        for i in range(n):
            lt = i / FPS
            gt = t0 + lt
            base = enh_bg if es else (src.next() if src else (swap_frame(stills, lt, seg) if stills else still))
            if seg.get("dim"):
                dk = prog(lt, 0, 0.3) * (1 - prog(lt, dur - 0.45, 0.35)) if seg.get("ppl") else prog(lt, 0, 0.3)
                base = Image.blend(base, Image.new("RGB", (W, H)), seg["dim"] * dk)
            z = seg.get("zoom")
            if not stills or not seg.get("hold_last"):
                base = zoomed(base, lt, z)
            if dsrc and lt >= dis.get("at", 0.8):
                v = dsrc.next()
                kk = min(1.0, (lt - dis.get("at", 0.8)) / max(dis.get("dur", 0.6), 0.01))
                base = Image.blend(base, v, kk)
            base = shaken(base, lt, seg.get("hits", []))
            base = bounced(base, lt, seg.get("bounce"))
            boost = 0.0
            if z and ("from" in z or z.get("noise")):
                boost = min(1.0, max(0.0, (zoom_scale(lt, z) - 1) / 1.5))
            site = bool(ov.site_text()) and sl[0] <= gt < sl[1] and not seg.get("ppl") \
                and seg.get("site_label", True)
            if seg.get("particles"):
                base = particles(base, lt, seg["particles"] if isinstance(seg["particles"], dict) else {})
            if ir and not seg.get("color") and not es:
                base = ir.apply(base, frame0 + i)
            fd = seg.get("frame_drop")
            fd_new = isinstance(fd, dict)   # {"frames":2,"clock_jump":1}: 노이즈 바는 처음 N프레임만, 시계는 이 컷부터 N칸 건너뜀
            _PREV["base"], _PREV["alerts"] = base, ([] if es else seg.get("alerts", []))
            out = ov.cctv(base, lt if seg.get("clock") else gt, frame0 + i, seg.get("clock"), boost, site,
                          (i < fd.get("frames", 2)) if fd_new else bool(fd),
                          bool(seg.get("color", bool(seg.get("clock")))), clock_carry + (int(fd.get("clock_jump", 1)) if fd_new else 0))
            if fd and (not fd_new or i < fd.get("frames", 2)):
                frame_drop(out, lt, random.Random(frame0 + i))
            if es:
                for al in prev_alerts:   # 직전 와이드의 감지 박스는 그대로 둔다
                    ov.alert(out, lt, 0, al["box"])
                draw_enhance(ov, out, seg, lt, es, pbox, frame0 + i)
            if seg.get("zoom_label"):
                ov.zoom_label(out, lt, seg["zoom_label"], seg.get("zoom_label_until", 0.9))
            for al in seg.get("alerts", []):
                ov.alert(out, lt, al.get("at", 0), al["box"], al.get("until"))
            if speed < 1:   # 슬로 구간만 REPLAY 표시 (1 초과 배속은 표시 안 함)
                ov.replay(out, lt, speed, ep.get("replay_y", 248))
            if seg.get("worklog"):
                ov.worklog(out, lt, seg["worklog"])
            for cap in ([] if NO_CAPS else seg.get("captions", [])):
                cap = {**cap, "y": cap.get("y", seg.get("caption_y", 1230))} if seg.get("caption_y") and "y" not in cap else cap
                if cap.get("radio") or cap.get("font") or cap.get("badge"):
                    ov.radio_caption(out, cap["text"], lt, cap.get("at", 0), cap.get("y", 1230), cap.get("size", 66),
                                     cap.get("badge"), cap.get("font", "radio"), bool(cap.get("cont")))
                else:
                    ov.caption(out, cap["text"], lt, cap.get("at", 0), cap.get("y", 1230), cap.get("size", 66))
            for st in ([] if NO_CAPS else seg.get("stamps", [])):
                ov.stamp(out, st["text"], lt, st["at"], st.get("x", 540), st.get("y", 760),
                         font=st.get("font"), shape=st.get("shape"), dia=st.get("dia", 220),
                         plate=bool(st.get("plate")), size=st.get("size"))
            for tg in seg.get("tags", []):
                ov.tag(out, tg["text"], lt, tg.get("at", 0), tg.get("x", 640), tg.get("y", 820))
            pt = ep.get("product_tag")   # {"text":..., "from":초, "until":초, "y":px(선택)} 전체 시간 기준
            if pt and not NO_CAPS and not seg.get("ppl") and pt.get("from", 0) <= gt < pt.get("until", 1e9):
                ov.product_tag(out, pt["text"], gt - pt.get("from", 0), pt.get("y", 300))
            if seg.get("ppl"):
                ppl_card(out, ep, ov.fonts, ov.cfg, lt, platform, dur)
            ov.disclosure(out, bool(seg.get("color")))
            if isinstance(ai, dict):   # ② 객체형 (0~3초 'AI 상황극' 큰 라벨 -> 'AI 연출')
                ov.ai_label_obj(out, ai, gt)
            elif ai:  # ② AI 연출 라벨: 모든 프레임, 최상단 레이어
                ov.ai_label(out, ai if isinstance(ai, str) else ov.cfg.get("ai_label", "AI 연출"))
            yield out.convert("RGB")
    finally:
        if src:
            src.close()
        if dsrc:
            dsrc.close()


def make_thumb(ep: dict, ov: Overlay, ff: str, clips: Path, out_dir: Path, ep_id: str) -> int:
    """--thumb: episode.json "thumbnail" 로 썸네일 1장.
    {"seg":"판독1","t":1.9,"circles":[[x,y,반지름],...],"ai_tag":"AI 상황극","text":["줄1","줄2"]}
    seg 생략 시 "src"의 첫 단어, t 생략 시 그 세그먼트 마지막 프레임. 빨간 원 선 8px (230,40,40), 좌상단 AI 태그 osd 44."""
    global NO_CAPS
    th = ep.get("thumbnail") or {}
    segs = ep["segments"]
    name = th.get("seg") or str(th.get("src", "")).split()[0]
    idx = next((i for i, sg in enumerate(segs) if sg.get("name") == name), None)
    if idx is None:
        print(f"[오류] 썸네일 세그먼트 '{name}' 를 찾지 못했습니다 (thumbnail.seg).")
        return 1
    seg = segs[idx]
    lt = float(th.get("t", seg["dur"] - 1 / FPS))
    t0 = sum(sg["dur"] for sg in segs[:idx])
    NO_CAPS = True
    CTX.update(ff=ff, clips=clips)
    try:
        if seg["type"] == "enhance" and idx > 0:   # 배경(직전 와이드 마지막 프레임)을 얻으려고 앞 컷을 한 번 훑는다
            for _ in render_segment(segs[idx - 1], ep, ov, ff, clips, t0 - segs[idx - 1]["dur"], 0):
                pass
        fr = None
        for k, f in enumerate(render_segment(seg, ep, ov, ff, clips, t0, 0)):
            fr = f
            if k >= round(lt * FPS):
                break
    finally:
        NO_CAPS = False
    im = fr.convert("RGBA")
    d = ImageDraw.Draw(im, "RGBA")
    circles = th.get("circles")
    if not isinstance(circles, list):
        print("[참고] thumbnail.circles 가 좌표 목록([[x,y,r],...])이 아니라 원 없이 만듭니다.")
        circles = []
    for cx, cy, r in circles:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(230, 40, 40, 255), width=8)
    kind = ov.fk("osd")
    tag = ov.safe_text(th.get("ai_tag", "AI 상황극"), kind)
    ft = ov.fonts.get(kind, 44)
    tw = d.textlength(tag, font=ft)
    d.rounded_rectangle([40, 56, 40 + tw + 40, 56 + 44 + 28], radius=8, fill=(0, 0, 0, 220))
    d.text((60, 70), tag, font=ft, fill=(255, 255, 255))
    ty = th.get("text_y", 1490)
    rk = ov.fk("radio")
    for j, line in enumerate(th.get("text", [])):
        d.text((W // 2, ty + j * 104), ov.safe_text(line, rk), font=ov.fonts.get(rk, 88), fill=(255, 255, 255),
               anchor="ma", stroke_width=9, stroke_fill=(0, 0, 0))
    p = out_dir / f"{ep_id}_thumb.jpg"
    im.convert("RGB").save(p, quality=92)
    print(f"썸네일: {p.relative_to(ROOT)}  ({seg['name']} {lt:.2f}초)")
    return 0


def build(ep_id: str, preview: bool, only: str | None = None, frames: list[float] | None = None,
          thumb: bool = False) -> int:
    cfg = load_config()
    fonts = Fonts(cfg)
    ff = find_ffmpeg(cfg)
    clips = ROOT / "assets" / "clips" / ep_id
    ep = json.loads((clips / "episode.json").read_text(encoding="utf-8"))
    out_dir = ROOT / "output" / ep_id
    out_dir.mkdir(parents=True, exist_ok=True)
    ov = Overlay(cfg, fonts, ep)
    total = sum(s["dur"] for s in ep["segments"])
    CTX.update(ff=ff, clips=clips)
    CTX.pop("es", None)
    _PREV.clear()
    if thumb:
        return make_thumb(ep, ov, ff, clips, out_dir, ep_id)

    if frames:  # 검수용: 전체 시간(초)의 원본 해상도 프레임 PNG
        fdir = out_dir / "frames"
        fdir.mkdir(exist_ok=True)
        t0 = 0.0
        for seg in ep["segments"]:
            for k, fr in enumerate(render_segment(seg, ep, ov, ff, clips, t0, 0)):
                for ft in frames:
                    if abs(t0 + k / FPS - ft) < 0.5 / FPS:
                        fr.save(fdir / f"{ep_id}_t{ft:05.2f}.png")
            t0 += seg["dur"]
        print(f"프레임: {fdir}")
        return 0
    if preview:
        sheet = []
        t0 = 0.0
        for seg in ep["segments"]:
            for k, fr in enumerate(render_segment(seg, ep, ov, ff, clips, t0, 0)):
                if k == round(seg.get("preview_at", seg["dur"] * 0.7) * FPS):
                    sheet.append(fr)
                    break
            t0 += seg["dur"]
        tw, th = 270, 480
        im = Image.new("RGB", (len(sheet) * (tw + 16) + 16, th + 32), "white")
        for i, fr in enumerate(sheet):
            f = fr.convert("RGBA")
            ovl = Image.new("RGBA", f.size, (0, 0, 0, 0))
            for z in UI_ZONES:
                ImageDraw.Draw(ovl).rectangle(z, fill=(230, 40, 40, 70))
            im.paste(Image.alpha_composite(f, ovl).convert("RGB").resize((tw, th)), (16 + i * (tw + 16), 16))
        p = out_dir / f"{ep_id}_preview.png"
        im.save(p)
        print(f"미리보기: {p.relative_to(ROOT)}")
        return 0

    audio = build_audio(ep, ff, clips, out_dir, total)
    platforms = ["youtube", "tiktok"] + (["clip"] if ep["product"].get("aff_type", "쇼핑커넥트") == "쇼핑커넥트" else [])
    if only:
        platforms = [only]
    for platform in platforms:
        silent = out_dir / "_video.mp4"
        proc = subprocess.Popen([ff, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                                 "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", *enc(FPS), "-an", str(silent)],
                                stdin=subprocess.PIPE)
        t0, frame = 0.0, 0
        for seg in ep["segments"]:
            for fr in render_segment(seg, ep, ov, ff, clips, t0, frame, platform):
                proc.stdin.write(fr.tobytes())
                frame += 1
            t0 += seg["dur"]
        proc.stdin.close()
        if proc.wait() != 0:
            print("[ffmpeg 오류] 영상 인코딩 실패")
            return 1
        final = out_dir / f"{ep_id}_{platform}.mp4"
        run([ff, "-y", "-loglevel", "error", "-i", str(silent), "-i", str(audio), "-map", "0:v", "-map", "1:a",
             "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", f"{total:.2f}", "-movflags", "+faststart",
             str(final)], ROOT)
        silent.unlink(missing_ok=True)
        write_upload_text(ep, cfg, platform, out_dir / f"{ep_id}_{platform}.txt")
        print(f"   완료: {final.relative_to(ROOT)}  ({total:.1f}초)")
    audio.unlink(missing_ok=True)
    return 0


def has_audio(ff: str, path: Path) -> bool:
    """소리 없이 만든 클립(Kling sound off)은 무음 처리하려고 오디오 트랙 유무를 확인."""
    r = subprocess.run([ff, "-hide_banner", "-i", str(path)], capture_output=True)
    return b"Audio:" in r.stderr


def build_audio(ep: dict, ff: str, clips: Path, out_dir: Path, total: float) -> Path:
    """컷별 소리 조각(영상 컷 = 원본 소리, 슬로모션이면 느리게 / 이미지 컷 = 무음)을 이어 붙이고
    CCTV 잡음 + 자동 효과음(감지 경보·도장·다시보기)을 섞는다."""
    sfx_dir = ROOT / "assets" / "sfx"
    parts, events, holds, t0 = [], [], [], 0.0
    for i, seg in enumerate(ep["segments"]):
        wav = out_dir / f"_a{i}.wav"
        vol, speed = seg.get("audio_vol", 1.0), seg.get("speed", 1.0)
        if seg["type"] == "video" and vol > 0 and has_audio(ff, clips / seg["file"]):
            af = f"volume={vol}" + (f",atempo={speed}" if speed != 1 else "") + ",apad"
            run([ff, "-y", "-loglevel", "error", "-ss", f"{seg.get('start', 0)}", "-t", f"{seg['dur'] * speed}",
                 "-i", str(clips / seg["file"]), "-vn", "-ac", "2", "-ar", "48000", "-af", af,
                 "-t", f"{seg['dur']}", str(wav)], ROOT)
        else:
            run([ff, "-y", "-loglevel", "error", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                 "-t", f"{seg['dur']}", str(wav)], ROOT)
        parts.append(wav)
        for al in seg.get("alerts", []):
            if not al.get("silent"):   # silent: true 인 보조 박스는 경고음 생략
                events.append(("beep.wav", t0 + al.get("at", 0), 0.8))
        for st in seg.get("stamps", []):
            circle = st.get("shape") == "circle" and (sfx_dir / "bang.wav").exists()
            events.append(("bang.wav" if circle else "stamp.wav", t0 + st["at"], 0.9 if circle else 0.5))
        for cp in seg.get("captions", []):
            if cp.get("radio") and not cp.get("cont"):  # 무전 자막 등장 '치직'
                events.append(("chijik.wav", t0 + cp.get("at", 0), 0.5))
        if seg["type"] == "enhance" and seg.get("sfx_auto", True):   # sfx_auto:false 면 자동 효과음 생략(정적 구간용). 보정 단계마다 '치익', 진입 '타닥', 결과 문구 '삑삑삑'
            for st_t, _ in seg.get("stages", []):
                events.append(("chiik.wav", t0 + st_t, 0.7))
            events.append(("tadak.wav", t0 + 0.15, 0.6))
            if seg.get("ui", {}).get("result") and seg.get("stages"):
                events.append(("beep3.wav", t0 + seg["stages"][-1][0] + 0.15, 0.6))
        if seg.get("speed", 1.0) < 1:
            events.append(("rewind.wav", t0, 0.9))
        for s in seg.get("sfx", []):
            events.append((s["file"], t0 + s["at"], s.get("vol", 1.0)))
        if seg.get("hold_last") and seg.get("hold_mute"):  # 정지 구간: BGM 완전 정지 + 효과음 제거
            holds.append((t0 + seg["dur"] - seg["hold_last"], t0 + seg["dur"]))
        t0 += seg["dur"]
    lst = out_dir / "_a.txt"
    lst.write_text("".join(f"file '{w.name}'\n" for w in parts), encoding="utf-8")
    base = out_dir / "_base.wav"
    run([ff, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst.name, "-c", "copy", base.name], out_dir)

    inputs, filt = [str(base)], []
    hum = sfx_dir / "hum.wav"
    if hum.exists():
        inputs.append(str(hum))
        filt.append(f"[{len(inputs) - 1}:a]volume={ep.get('ambience_vol', 1.0)}[amb]")
    bgm = sfx_dir / ep["bgm"] if ep.get("bgm") else None
    if bgm and bgm.exists():
        # 배경음악: 반복 재생, 기본 음량 낮게, 'bgm_mute' 구간(초)은 거의 끄기(들킨 순간 정적 등), 끝 1초 페이드
        inputs.append(str(bgm))
        vol = ep.get("bgm_vol", 0.35)
        mutes = "+".join(f"between(t,{a_},{b_})" for a_, b_ in ep.get("bgm_mute", [])) or "0"
        hm = "".join(f"*(1-between(t,{a_:.2f},{b_:.2f}))" for a_, b_ in holds)
        filt.append(f"[{len(inputs) - 1}:a]aloop=loop=-1:size=2147483647,atrim=0:{total:.2f},"
                    f"volume='{vol}*(1-0.9*({mutes})){hm}':eval=frame,afade=t=out:st={total - 1:.2f}:d=1[bgm]")
    events = [e for e in events if (sfx_dir / e[0]).exists() and not any(a_ <= e[1] < b_ for a_, b_ in holds)]

    for k, (f, at, v) in enumerate(events):
        inputs.append(str(sfx_dir / f))
        filt.append(f"[{len(inputs) - 1}:a]aresample=48000,adelay={int(at * 1000)}:all=1,volume={v}[e{k}]")
    has_bgm = bool(bgm and bgm.exists())
    labels = "[0:a]" + ("[amb]" if hum.exists() else "") + ("[bgm]" if has_bgm else "") +              "".join(f"[e{k}]" for k in range(len(events)))
    n = 1 + hum.exists() + has_bgm + len(events)
    filt.append(f"{labels}amix=inputs={n}:normalize=0:duration=first,alimiter=limit={ep.get('limiter', 0.9)}{':level=disabled' if 'limiter' in ep else ''}[a]")
    audio = out_dir / "_audio.wav"
    cmd = [ff, "-y", "-loglevel", "error"]
    for i in inputs:
        cmd += ["-i", i]
    run(cmd + ["-filter_complex", ";".join(filt), "-map", "[a]", "-t", f"{total:.2f}", str(audio)], ROOT)
    for f in [base, lst, *parts]:
        f.unlink(missing_ok=True)
    return audio


def write_upload_text(ep: dict, cfg: dict, platform: str, out: Path) -> None:
    p = ep["product"]
    if platform == "tiktok":  # 캡션 그대로 붙여넣기용 (링크 대신 검색 안내)
        alt = ep.get("product_alt")
        disc = [cfg["disclosure_text"][p.get("aff_type", "쇼핑커넥트")]] + (
            [cfg["disclosure_text"][alt["aff_type"]]] if alt else [])
        names = " / ".join(q.get("short", q["name"]) for q in (p, alt) if q)
        L = [ep.get("title", ""), *([ep["desc_first_line"]] if ep.get("desc_first_line") else []), *disc,
             f"검색: {names}", "※ AI로 만든 연출 영상이에요.", " ".join(ep.get("hashtags", []))]
        if ep.get("upload_checks"):
            L += ["", "[업로드 전 체크]", *[f"- {c}" for c in ep["upload_checks"]]]
        out.write_text("\n".join(L) + "\n", encoding="utf-8-sig")
        return
    L = ["[제목 후보]"] + [f"- {x}" for x in ep.get("titles", [ep.get("title", "")])]
    aeo = ep.get("aeo_line")
    alt = ep.get("product_alt") if platform != "clip" else None
    disc = [cfg["disclosure_text"][p.get("aff_type", "쇼핑커넥트")]] +            ([cfg["disclosure_text"][alt["aff_type"]]] if alt else [])
    dfl = ep.get("desc_first_line")   # 설명란 맨 첫 줄 (AI 상황극 고지)
    L += ["", "[설명란에 붙여넣기]", *([dfl] if dfl else []), *([aeo, ""] if aeo else []), *disc,
          f"※ 가격·리뷰 수·평점은 {ep.get('price_date', '')} 상품 페이지 기준이며 변동될 수 있어요.", "",
          f"오늘의 경비원: {p['name']} | {p['price']:,}원 | 리뷰 {p['reviews']:,}개 · 평점 {p['rating']:.2f}"]
    if alt:
        L += [f"쿠팡 대안: {alt['name']}{(' | 옵션 ' + alt['option']) if alt.get('option') else ''} | {alt['price']:,}원 | 리뷰 {alt['reviews']:,}개"]
    if platform == "youtube":
        L += ["", f"▶ {p.get('store', '네이버')}: {p['link']}"] + ([f"▶ {alt.get('store', '쿠팡')}: {alt['link']}"] if alt else [])
    else:
        L += ["▶ 화면의 상품 스티커를 누르면 바로 볼 수 있어요"]
    L += ["※ 영상 속 장면은 AI로 만든 연출이며, 실제 효과와는 관계없어요.", "", " ".join(ep.get("hashtags", [])),
          "", "[고정 댓글 — 대가성 문구를 첫 번째 댓글로 달고 맨 위에 고정 (쇼츠·클립 공통)]",
          *disc, ""]
    if platform == "youtube":  # 영수 님 방식: 댓글에도 상품 링크
        L += [f"▶ {p.get('store', '네이버')} {p.get('short', p['name'])} {p['link']}"] +              ([f"▶ {alt.get('store', '쿠팡')} {alt.get('short', alt['name'])} {alt['link']}"] if alt else []) + [""]
    L += [ep.get("pinned_comment", ""), "", "=" * 40]
    L += ["[채널 맞춤설정 → 링크에 등록할 링크]" if platform == "youtube" else "[쇼핑커넥트 스티커로 연결할 상품]",
          f"[네이버] {p['name']}: {p['link']}"] + ([f"[쿠팡] {alt['name']}: {alt['link']}"] if alt else []) +          ["", "[업로드 전 체크]",
          "- 상품 페이지에서 가격·리뷰 수·평점이 영상과 같은지 (다르면 episode.json 고치고 다시 제작)",
          "- 브랜드커넥트에서 이 상품이 아직 '진행 중'인지", *[f"- {c}" for c in ep.get("upload_checks", [])]]
    if platform == "youtube":
        L += ["- 위 [고정 댓글]을 달고 맨 위에 고정 (대가성 문구 포함 필수)",
              "- '유료 프로모션 포함' 체크", "- '변경되거나 합성된 콘텐츠(AI)' 체크", "- 채널 링크에 위 링크가 등록돼 있는지 (영상 번호 붙여서)",
              "- 릴스·틱톡도 이 파일 그대로 (각 앱의 AI 콘텐츠 표시 켜기)"]
    else:
        L += ["- 쇼핑커넥트 상품 태그(스티커) 연결 → 본문 맨 앞에 [광고]가 자동으로 붙는지 확인 (안 붙으면 직접 [광고] 입력)",
              "- 네이버TV로도 올리면 제목 맨 앞에 [광고] 직접 입력",
              "- 위 [고정 댓글]을 첫 번째 댓글로 달고 고정 (대가성 문구 그대로, 해시태그 사이에 숨기지 않기)",
              "- 클립 업로드 화면에 AI 콘텐츠 표시 항목이 있으면 켜기"]
    out.write_text("\n".join(L) + "\n", encoding="utf-8-sig")


def main() -> int:
    ap = argparse.ArgumentParser(description="현관 CCTV 시리즈 조립기")
    ap.add_argument("ep", help="에피소드 ID (assets/clips/<ID>/episode.json)")
    ap.add_argument("--preview", action="store_true", help="컷별 미리보기 PNG만 만들기")
    ap.add_argument("--frames", help="콤마로 구분한 초 목록: 해당 시점 원본 프레임 PNG를 output/<EP>/frames 에 저장")
    ap.add_argument("--thumb", action="store_true", help="썸네일 1장 (episode.json thumbnail: seg·t·circles·ai_tag)")
    ap.add_argument("--dummy", action="store_true", help="없는 이미지·영상을 단색 더미로 대체 (점검용)")
    ap.add_argument("--only", choices=["youtube", "tiktok", "clip"], help="이 플랫폼 파일만 만들기")
    a = ap.parse_args()
    global DUMMY
    DUMMY = a.dummy
    return build(a.ep, a.preview, a.only, [float(x) for x in a.frames.split(",")] if a.frames else None, a.thumb)


if __name__ == "__main__":
    sys.exit(main())
