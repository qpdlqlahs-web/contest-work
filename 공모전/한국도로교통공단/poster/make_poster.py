"""A2 portrait poster (420x594 mm @ 300 dpi = 4961x7016 px). Typography is set here (no AI text).
usage: python poster/make_poster.py HERO.png OUT.png [hero_anchor_y 0..1]"""
import sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")
HERO, OUT = sys.argv[1], sys.argv[2]
ANCHOR = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
W, H = 4961, 7016
FB = "C:/Windows/Fonts/NotoSansCJKkr-Black.otf"
FBD = "C:/Windows/Fonts/NotoSansCJKkr-Bold.otf"
GREEN, YELLOW, CREAM = (46, 94, 30), (255, 225, 77), (255, 248, 235)

def cover(im, w, h, ay=0.5):
    s = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = (im.width - w) // 2; y = int((im.height - h) * ay)
    return im.crop((x, y, x + w, y + h))

def text(d, xy, s, font, fill, stroke, sw, anchor="mm"):
    d.text(xy, s, font=font, fill=fill, stroke_width=sw, stroke_fill=stroke, anchor=anchor)

canvas = cover(Image.open(HERO).convert("RGB"), W, H, ANCHOR)
canvas = canvas.filter(ImageFilter.UnsharpMask(radius=3, percent=60, threshold=2))
# soft top gradient for headline legibility
grad = Image.new("L", (1, H)); grad.putdata([int(max(0, 1 - y / (H * 0.30)) * 70) for y in range(H)])
canvas = Image.composite(Image.new("RGB", (W, H), (60, 40, 20)), canvas, grad.resize((W, H)))
d = ImageDraw.Draw(canvas)

# headline
text(d, (W / 2, 520), "이 동네에선", ImageFont.truetype(FB, 420), "white", GREEN, 26)
text(d, (W / 2, 1060), "거북이가 이겨요", ImageFont.truetype(FB, 640), YELLOW, GREEN, 34)
text(d, (W / 2, 1520), "어린이·노인 보호구역은 시속 30km", ImageFont.truetype(FBD, 220), "white", GREEN, 16)

# bottom panel: 4 safety rules with clay-scene icons
panel_h, panel_y = 1300, H - 1300 - 470
panel = Image.new("RGBA", (W - 360, panel_h), (0, 0, 0, 0))
ImageDraw.Draw(panel).rounded_rectangle((0, 0, panel.width - 1, panel_h - 1), 120, fill=CREAM + (236,))
canvas.paste(panel, (180, panel_y), panel)
ICONS = [("keyframes_ad/A06.png", (0.50, 0.60, 0.80), "시속 30km"), ("keyframes_ad/A12.png", (0.40, 0.55, 0.90), "전 좌석 안전띠"),
         ("keyframes_ad/A13.png", (0.52, 0.56, 0.85), "회전 전 깜빡이"), ("kf3/A14f.png", (0.50, 0.33, 0.62), "킥보드엔 헬멧")]
D = 780; gap = (W - 360 - 4 * D) / 5
ft = ImageFont.truetype(FB, 140)
for k, (p, (cx, cy, sf), cap) in enumerate(ICONS):
    src = Image.open(p).convert("RGB")
    side = int(min(src.width, src.height) * sf)
    x0 = int(min(max(cx * src.width - side / 2, 0), src.width - side)); y0 = int(min(max(cy * src.height - side / 2, 0), src.height - side))
    ic = src.crop((x0, y0, x0 + side, y0 + side)).resize((D, D), Image.LANCZOS)
    m = Image.new("L", (D, D), 0); ImageDraw.Draw(m).ellipse((0, 0, D - 1, D - 1), fill=255)
    x = int(180 + gap + k * (D + gap)); y = panel_y + 100
    ring = Image.new("RGBA", (D + 40, D + 40), (0, 0, 0, 0)); ImageDraw.Draw(ring).ellipse((0, 0, D + 39, D + 39), fill=GREEN + (255,))
    canvas.paste(ring, (x - 20, y - 20), ring)
    canvas.paste(ic, (x, y), m)
    text(ImageDraw.Draw(canvas), (x + D / 2, y + D + 200), cap, ft, GREEN, CREAM, 0)

# footer: KOROAD CI on a white card
logo = Image.open("refs/koroad_logo.png").convert("RGBA")
lw = 1700; logo = logo.resize((lw, round(lw * logo.height / logo.width)), Image.LANCZOS)
card = Image.new("RGBA", (lw + 160, logo.height + 120), (0, 0, 0, 0))
ImageDraw.Draw(card).rounded_rectangle((0, 0, card.width - 1, card.height - 1), 60, fill=(255, 255, 255, 245))
card.alpha_composite(logo, (80, 60))
canvas.paste(card, ((W - card.width) // 2, H - 470 + (470 - card.height) // 2 - 10), card)

canvas.save(OUT, dpi=(300, 300), optimize=True)
canvas.resize((W // 6, H // 6), Image.LANCZOS).save(OUT.replace(".png", "_preview.jpg"), quality=88)
print(OUT, canvas.size, os.path.getsize(OUT) // 1024, "KB")
