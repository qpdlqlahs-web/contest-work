#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""「새벽3시CCTV」 채널 배너: 경비실 모니터 벽(CCTV 12칸) + 가운데 안전 영역에 채널명.
  python assets/channel/make_banner.py  ->  assets/channel/banner_cctv_2560x1440.png
회차가 늘면 FEEDS에 새 컷을 추가해서 다시 돌리면 된다.
"""
import random
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from make_short import Fonts, load_config  # noqa: E402

BW, BH = 2560, 1440
SAFE = ((BW - 1546) // 2, (BH - 423) // 2, (BW + 1546) // 2, (BH + 423) // 2)
COLS, ROWS, GAP = 4, 3, 18
PW = (BW - 40 - GAP * (COLS - 1)) // COLS
PH = (BH - 40 - GAP * (ROWS - 1)) // ROWS
CLIPS = ROOT / "assets" / "clips"


def frame_from_video(path: Path, t: float) -> Image.Image:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", str(path), "-frames:v", "1",
                          "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
    from io import BytesIO
    return Image.open(BytesIO(raw)).convert("RGB")


# (카메라 이름, 시각, 소스) — 소스가 None이면 "신호 없음"
FEEDS = [
    ("CAM 01 현관", "03:14:07", lambda: Image.open(CLIPS / "EP01" / "master.png")),
    ("CAM 02 거실", "03:15:22", lambda: Image.open(CLIPS / "EP02" / "master.png")),
    ("CAM 03", "--:--:--", None),
    ("CAM 01 현관", "03:14:09", lambda: frame_from_video(CLIPS / "EP01" / "EP01_hit_bill.mp4", 1.35)),
    ("CAM 01 현관", "03:14:15", lambda: frame_from_video(CLIPS / "EP01" / "EP01_hit_chicken.mp4", 2.0)),
    ("CAM 01 현관", "03:14:12", lambda: frame_from_video(CLIPS / "EP01" / "EP01_hit_calendar.mp4", 1.8)),
    ("CAM 04", "--:--:--", None),
    ("CAM 01 현관", "03:14:19", lambda: Image.open(CLIPS / "EP01" / "intruder.png")),
    ("CAM 05", "--:--:--", None),
    ("CAM 01 현관", "03:14:20", lambda: frame_from_video(CLIPS / "EP01" / "EP01_intruder.mp4", 1.0)),
    ("CAM 02 거실", "03:15:22", lambda: Image.open(CLIPS / "EP02" / "master.png")),
    ("CAM 06", "--:--:--", None),
]


def panel(fonts: Fonts, name: str, clock: str, src) -> Image.Image:
    rng = random.Random(hash(name + clock))
    if src is None:
        n = Image.effect_noise((PW // 3, PH // 3), 90).resize((PW, PH), Image.NEAREST).convert("RGB")
        im = Image.blend(n, Image.new("RGB", (PW, PH), (20, 22, 24)), 0.45)
        d = ImageDraw.Draw(im)
        d.text((PW // 2, PH // 2), "신호 없음", font=fonts.get("heavy", 54), fill=(230, 230, 230),
               anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
    else:
        im = ImageOps.fit(src().convert("L").convert("RGB"), (PW, PH), Image.LANCZOS, centering=(0.5, 0.42))
        tint = Image.new("RGB", (PW, PH), (200, 214, 204))
        im = Image.composite(im, Image.blend(im, tint, 0.12), Image.new("L", (PW, PH), 200))
        n = Image.effect_noise((PW, PH), 30).convert("RGB")
        im = Image.blend(im, n, 0.06)
    d = ImageDraw.Draw(im)
    f = fonts.get("bold", 28)
    d.text((16, 12), name, font=f, fill=(235, 235, 235), stroke_width=3, stroke_fill=(0, 0, 0))
    d.text((PW - 16, 12), clock, font=f, fill=(235, 235, 235), anchor="ra", stroke_width=3, stroke_fill=(0, 0, 0))
    if src is not None:
        d.ellipse([16, PH - 40, 38, PH - 18], fill=(230, 40, 40))
        d.text((46, PH - 29), "REC", font=f, fill=(235, 235, 235), anchor="lm", stroke_width=3, stroke_fill=(0, 0, 0))
    d.rectangle([0, 0, PW - 1, PH - 1], outline=(70, 74, 78), width=4)
    return im


def main():
    cfg = load_config()
    fonts = Fonts(cfg)
    wall = Image.new("RGB", (BW, BH), (8, 9, 10))
    for i, (name, clock, src) in enumerate(FEEDS):
        r, c = divmod(i, COLS)
        wall.paste(panel(fonts, name, clock, src), (20 + c * (PW + GAP), 20 + r * (PH + GAP)))

    # 가운데 안전 영역(모든 기기에서 보이는 1546x423)에 채널명
    x0, y0, x1, y1 = SAFE
    shade = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    ImageDraw.Draw(shade).rounded_rectangle([x0 + 60, y0 + 40, x1 - 60, y1 - 40], radius=36, fill=(6, 7, 8, 228))
    out = wall.convert("RGBA")
    out.alpha_composite(shade.filter(ImageFilter.GaussianBlur(2)))
    d = ImageDraw.Draw(out)
    cy = (y0 + y1) // 2
    d.ellipse([x0 + 150, cy - 98, x0 + 196, cy - 52], fill=(235, 40, 40))
    d.text((x0 + 214, cy - 75), "REC  03:14 AM", font=fonts.get("heavy", 46), fill=(235, 235, 235), anchor="lm")
    d.text(((x0 + x1) // 2, cy + 40), "새벽3시CCTV", font=fonts.get("heavy", 170), fill=(255, 255, 255), anchor="mm")
    out = out.convert("RGB")
    p = HERE / "banner_cctv_2560x1440.png"
    out.save(p, optimize=True)
    # 확인용: 모바일에서 보이는 영역 표시
    chk = out.resize((1280, 720))
    ImageDraw.Draw(chk).rectangle([x0 // 2, y0 // 2, x1 // 2, y1 // 2], outline=(255, 0, 0), width=2)
    chk.save(HERE / "_banner_check.png")
    print(p)


if __name__ == "__main__":
    main()
