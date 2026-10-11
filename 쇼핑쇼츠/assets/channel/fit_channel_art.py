#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""클링 원본 -> 유튜브 업로드용 크기.
  배너 2560x1440: 시상대가 모든 기기에서 보이는 가운데 1546x423 안에 들어오게 줄이고,
                  빈 가장자리는 같은 그림을 흐리게 늘려서 채운다.
  프로필 800x800.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
BW, BH = 2560, 1440
SAFE = (BW - 1546) // 2, (BH - 423) // 2, (BW + 1546) // 2, (BH + 423) // 2

# 원본(2720x1536)에서 시상대+선물 영역의 세로 범위와 가로 중심
PODIUM_TOP, PODIUM_BOTTOM, PODIUM_CX = 580, 1100, 1360
SCALE = 0.8

src = Image.open(HERE / "kling_banner.png").convert("RGB")
cover = max(BW / src.width, BH / src.height)
bg = src.resize((round(src.width * cover), round(src.height * cover)), Image.LANCZOS)
bg = bg.crop(((bg.width - BW) // 2, (bg.height - BH) // 2, (bg.width + BW) // 2, (bg.height + BH) // 2))
bg = bg.filter(ImageFilter.GaussianBlur(40))

fg = src.resize((round(src.width * SCALE), round(src.height * SCALE)), Image.LANCZOS)
ox = BW // 2 - round(PODIUM_CX * SCALE)
oy = BH // 2 - round((PODIUM_TOP + PODIUM_BOTTOM) / 2 * SCALE)
feather = 120
mask = Image.new("L", fg.size, 0)
ImageDraw.Draw(mask).rectangle([feather, feather, fg.width - feather, fg.height - feather], fill=255)
mask = mask.filter(ImageFilter.GaussianBlur(feather / 2))
bg.paste(fg, (ox, oy), mask)
bg.save(HERE / "banner_2560x1440.png", optimize=True)

Image.open(HERE / "kling_profile.png").convert("RGB").resize((800, 800), Image.LANCZOS).save(
    HERE / "profile_800.png", optimize=True)
print("safe area", SAFE, "podium y", oy + round(PODIUM_TOP * SCALE), "-", oy + round(PODIUM_BOTTOM * SCALE))
