# -*- coding: utf-8 -*-
"""KF2_final_start_v3 -> v4: (1) left glass wall below the water line rebuilt along the wall curve,
(2) grey block where the stream crosses the front rim filled with stream texture over a continuous rim."""
import os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

IMG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img')
a = np.asarray(Image.open(os.path.join(IMG, 'KF2_final_start_v3.png')).convert('RGB')).astype(np.float64)
o = a.copy()

# (1) left wall: column profile from just above the water (rows 1072-1088), shifted along the taper
SLOPE = 0.075                                   # wall line moves right 0.075 px per row going down (measured)
x0, x1 = 258, 297
prof = a[1072:1089, x0:x1].mean(0)              # (39, 3)
xs = np.arange(x0, x1)
for y in range(1126, 1252):
    sh = (y - 1080) * SLOPE
    row = np.stack([np.interp(xs - sh, xs, prof[:, c]) for c in range(3)], -1)
    # keep the water interior right of the wall: blend weight falls off past the dark wall line
    wall_x = 282 + sh
    w = np.clip((wall_x + 5 - xs) / 4, 0, 1)
    # vertical blend at the top (meniscus) and bottom (thick base)
    v = min(np.clip((y - 1126) / 12, 0, 1), np.clip((1251 - y) / 10, 0, 1))
    w = (w * v)[:, None]
    # keep the plate's own fine grain outside the glass
    o[y, x0:x1] = a[y, x0:x1] * (1 - w) + (row + (a[y, x0:x1] - ndi.uniform_filter1d(a[y, x0:x1], 5, axis=0)) * 0.5) * w

# (2) rim x stream crossing: continuous rim from both sides + stream difference from just above
ys, ye, cs, ce = 955, 971, 349, 368
L = a[ys:ye, cs - 4:cs].mean(1); R = a[ys:ye, ce:ce + 4].mean(1)
t = (np.arange(cs, ce) - (cs - 1)) / (ce - cs + 1)
rim = L[:, None, :] * (1 - t[None, :, None]) + R[:, None, :] * t[None, :, None]
above = a[938:952, cs:ce].mean(0)               # stream + background just above the rim
bg_above = np.concatenate([a[938:952, cs - 4:cs], a[938:952, ce:ce + 4]], 1).mean((0, 1))
sdiff = above - bg_above
alpha = np.clip(np.abs(sdiff).mean(1) / max(np.abs(sdiff).mean(1).max(), 1e-6) * 1.3, 0, 1)
patch = rim + sdiff[None] * alpha[None, :, None] * 0.9
# keep the thin front-rim highlight on top of the stream
hl = np.clip((a[ys:ye, cs - 6:cs].mean(1).mean(1) - a[ys:ye, cs - 6:cs].mean() - 6) / 20, 0, 1)
patch = patch * (1 - 0.5 * hl[:, None, None]) + rim * 0.5 * hl[:, None, None]
fw = np.ones((ye - ys, ce - cs))
fw[:2] = 0.5; fw[-2:] = 0.5; fw[:, :2] = 0.6; fw[:, -2:] = 0.6
o[ys:ye, cs:ce] = a[ys:ye, cs:ce] * (1 - fw[..., None]) + patch * fw[..., None]

Image.fromarray(np.clip(o + 0.5, 0, 255).astype(np.uint8)).save(os.path.join(IMG, 'KF2_final_start_v4.png'))
print('saved KF2_final_start_v4.png')
