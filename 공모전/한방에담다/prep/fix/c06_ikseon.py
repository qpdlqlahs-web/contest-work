import numpy as np, sys
from PIL import Image, ImageDraw, ImageFilter
src, out = sys.argv[1], sys.argv[2]
img = Image.open(src).convert('RGB'); a = np.array(img).astype(float)
H, W, _ = a.shape
x0, x1, y0, y1 = 60, 440, 480, 1312
# 1) erase old crown shadow: per-row linear wall estimate from clean columns
wall = a.copy()
for y in range(y0, y1):
    l = a[y, 40:100].mean(0); r = a[y, 395:430].mean(0)
    t = (np.arange(x0, x1) - 70) / (412 - 70)
    wall[y, x0:x1] = l[None] * (1 - t[:, None]) + r[None] * t[:, None]
L = a.mean(2); WL = wall.mean(2)
m = np.zeros((H, W)); m[y0:y1, x0:x1] = (WL[y0:y1, x0:x1] - L[y0:y1, x0:x1]) > 18
mk = Image.fromarray((m * 255).astype('uint8')).filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(4))
mk = np.array(mk)[..., None] / 255.0
rng = np.random.default_rng(1); wall += rng.normal(0, 1.2, wall.shape)
a = a * (1 - mk) + wall * mk
# 2) draw Joseon king silhouette (ikseongwan + round-collar robe)
s = Image.new('L', (W, H), 0); d = ImageDraw.Draw(s)
cx = 262
d.ellipse((cx-58, 640, cx+58, 770), fill=255)                 # head
d.chord((cx-66, 600, cx+66, 720), 180, 360, fill=255)          # rounded cap dome
d.rectangle((cx-66, 658, cx+66, 690), fill=255)                # cap band
for sx in (-1, 1):                                              # two upright rounded wings at back
    wx = cx + sx*40
    d.ellipse((wx-24, 548, wx+24, 622), fill=255)
    d.rectangle((wx-14, 590, wx+14, 640), fill=255)
d.rectangle((cx-22, 760, cx+22, 800), fill=255)                # neck
d.polygon([(cx-80, 790), (cx+80, 790), (cx+150, 860), (cx+165, 1295), (cx-165, 1295), (cx-150, 860)], fill=255)  # robe
d.ellipse((cx-150, 790, cx-50, 900), fill=255); d.ellipse((cx+50, 790, cx+150, 900), fill=255)  # shoulders
sm = np.array(s.filter(ImageFilter.GaussianBlur(5)))[..., None] / 255.0
# shadow strength sampled from right gat shadow ratio (~0.62 of wall)
a = a * (1 - sm * 0.38)
Image.fromarray(np.clip(a, 0, 255).astype('uint8')).save(out)
