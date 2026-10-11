# -*- coding: utf-8 -*-
"""Nano seeds: clean official cutouts on grey (150,146,140) 1080x1920, same method as KF1_seed.png.
S18_seed.png : official (1) front,  height 860 px, centre x 330, base line y 1500 (upper-right third empty)
S10_seed.png : official (3) door side, width 65 % of frame (702 px), right two-thirds, base y 1400 (left third empty)
"""
import os, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from comp_k1 import cutout
DIR = os.path.join(HERE, '..', 'refs', 'assets', '02. 퓨리얼 유로체인저 직수정수기 PPA-300')
BG = np.array([150, 146, 140]) / 255.0
OW, OH = 1080, 1920


def place(photo, out, mode, val, anchor_x, base_y, ax='center'):
    C, A = cutout(os.path.join(DIR, photo))
    ys, xs = np.nonzero(A > 0.5)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    s = val / (y1 - y0) if mode == 'h' else val / (x1 - x0)
    pad = 4
    Ci = Image.fromarray(C.astype(np.uint8)).crop((x0 - pad, y0 - pad, x1 + pad, y1 + pad))
    Ai = Image.fromarray((A * 255).astype(np.uint8)).crop((x0 - pad, y0 - pad, x1 + pad, y1 + pad))
    nw, nh = round(Ci.width * s), round(Ci.height * s)
    Ci = np.asarray(Ci.resize((nw, nh), Image.LANCZOS)) / 255.0
    Ai = np.asarray(Ai.resize((nw, nh), Image.LANCZOS)) / 255.0
    w = (x1 - x0) * s; h = (y1 - y0) * s
    left = anchor_x - w / 2 if ax == 'center' else anchor_x - w
    top = base_y - h
    ox, oy = round(left - pad * s), round(top - pad * s)
    canvas = np.ones((OH, OW, 3)) * BG
    a = Ai[..., None]
    canvas[oy:oy + nh, ox:ox + nw] = Ci * a + canvas[oy:oy + nh, ox:ox + nw] * (1 - a)
    Image.fromarray((canvas * 255 + 0.5).astype(np.uint8)).save(os.path.join(HERE, 'img', out))
    print('%s: %s bbox(photo) %dx%d, scale %.4f -> x %.0f-%.0f y %.0f-%.0f (w %.0f, h %.0f)'
          % (out, photo, x1 - x0, y1 - y0, s, left, left + w, top, base_y, w, h))


if __name__ == '__main__' and '--s10v2' not in sys.argv:
    place('PPA-300 (1).jpg', 'S18_seed.png', 'h', 860, 330, 1500, 'center')
    place('PPA-300 (3).jpg', 'S10_seed.png', 'w', 702, 1060, 1400, 'right')


def place_affine(photo, out, s, tx, ty):
    """frame = s * photo + (tx, ty)  (same convention as comp_s10*.py)"""
    from comp_k1_v2 import warp
    C, A = cutout(os.path.join(DIR, photo))
    AL = np.clip(warp(A, s, tx, ty), 0, 1)
    PL = np.clip(warp(C / 255.0, s, tx, ty, order=3), 0, 1)
    canvas = np.ones((OH, OW, 3)) * BG
    canvas = PL * AL[..., None] + canvas * (1 - AL[..., None])
    Image.fromarray((canvas * 255 + 0.5).astype(np.uint8)).save(os.path.join(HERE, 'img', out))
    ys, xs = np.nonzero(AL > 0.5)
    print('%s: %s scale %.4f offset (%.2f, %.2f) -> bbox x %d-%d y %d-%d' % (out, photo, s, tx, ty, xs.min(), xs.max(), ys.min(), ys.max()))


if __name__ == '__main__' and '--s10v2' in sys.argv:
    place_affine('PPA-300 (3).jpg', 'S10_seed_v2.png', 0.6664, 454.15, 764.77)
