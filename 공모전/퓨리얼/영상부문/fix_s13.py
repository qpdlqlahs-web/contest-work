# -*- coding: utf-8 -*-
"""
S13-2_fix / S13-1_fix: remove glasses from img/S13-3_v2.png by hand (Nano edit failed).
 S13-2: front glass removed (its shadow band + caustic relit, middle glass right half rebuilt by mirroring)
 S13-1: middle glass removed from S13-2 as well (back glass right half rebuilt by mirroring)
Table under a removed glass: low frequency = push-pull from clean lit table, detail = wood-grain HF copied from
lit table further down. Coordinates are in the 1536x2752 original.
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
LW = np.array([0.2126, 0.7152, 0.0722])
DBG = os.environ.get('KF1_DBG')


def gb(a, s):
    if a.ndim == 2:
        return ndi.gaussian_filter(a, s)
    return np.stack([ndi.gaussian_filter(a[..., c], s) for c in range(a.shape[2])], -1)


def pushpull(I, W):
    if W.all() or min(W.shape) < 4:
        if not W.any():
            return np.zeros_like(I)
        return np.where(W[..., None], I, I[W].mean(0))
    H, Wd = W.shape
    h2, w2 = (H + 1) // 2, (Wd + 1) // 2
    Ip = np.zeros((h2 * 2, w2 * 2, 3)); Wp = np.zeros((h2 * 2, w2 * 2))
    Ip[:H, :Wd] = I * W[..., None]; Wp[:H, :Wd] = W
    Is = Ip.reshape(h2, 2, w2, 2, 3).sum((1, 3)); Ws = Wp.reshape(h2, 2, w2, 2).sum((1, 3))
    Ic = np.where(Ws[..., None] > 0, Is / np.maximum(Ws, 1e-9)[..., None], 0)
    up = ndi.zoom(pushpull(Ic, Ws > 0), (2, 2, 1), order=1)[:H, :Wd]
    return np.where(W[..., None], I, up)


def poly(pts, shape):
    m = Image.new('L', (shape[1], shape[0]), 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    return np.asarray(m) > 0


def glass_mask(shape, x0, x1, ytop, ybot, rim=14, pad=4):
    """straight-sided glass seen slightly from above: rect + elliptic rim top and base bottom."""
    H, W = shape
    Y, X = np.mgrid[0:H, 0:W]
    cx, rx = (x0 + x1) / 2, (x1 - x0) / 2 + pad
    m = (X >= x0 - pad) & (X <= x1 + pad) & (Y >= ytop) & (Y <= ybot)
    m |= ((X - cx) / rx) ** 2 + ((Y - ytop) / rim) ** 2 <= 1
    m |= ((X - cx) / rx) ** 2 + ((Y - ybot) / (rim + 2)) ** 2 <= 1
    return m


def relight(img, zone, mode, pct, win=(281, 41)):
    """shadow (mode='lift') or caustic (mode='drop') removal by low-frequency gain toward the local lit level."""
    lf = gb(img, 5)
    sm = lf[::4, ::4]
    ref = np.stack([ndi.percentile_filter(sm[..., c], pct, size=(win[0] // 4, win[1] // 4)) for c in range(3)], -1)
    ref = ndi.zoom(ref, (4, 4, 1), order=1)[:img.shape[0], :img.shape[1]]
    ref = gb(ref, 8)
    g = ref / np.maximum(lf, 1e-3)
    if mode == 'lift':
        g = np.clip(g, 1.0, 3.0); w = np.clip((g.dot(LW) - 1.06) / 0.15, 0, 1)
    else:
        g = np.clip(g, 0.45, 1.0); w = np.clip((0.94 - g.dot(LW)) / 0.12, 0, 1)
    w = gb(w * zone, 4)
    g = gb(g, 4)
    return img * (1 + (g - 1) * w[..., None])


def harmonic(F, hole, valid, iters=800):
    """Laplace relaxation inside `hole`; only `valid` (table) pixels act as boundary (glass = no-flux)."""
    ys, xs = np.nonzero(hole)
    y0, y1, x0, x1 = max(ys.min() - 2, 0), ys.max() + 3, max(xs.min() - 2, 0), xs.max() + 3
    sub = F[y0:y1, x0:x1].copy(); h = hole[y0:y1, x0:x1]
    v = (valid[y0:y1, x0:x1] | h).astype(float)
    wv = np.maximum(ndi.uniform_filter(v, 3), 1e-6)
    for _ in range(iters):
        avg = np.stack([ndi.uniform_filter(sub[..., c] * v, 3) for c in range(3)], -1) / wv[..., None]
        sub[h] = avg[h]
    out = F.copy(); out[y0:y1, x0:x1] = sub
    return out


def fill_table(img, hole, known, hf_shift=(0, -600), ytab=1690, ):
    """table part of a hole: LF = push-pull start + harmonic relaxation (seamless at the hole border),
    fine grain (sigma-3 ratio detail, shadow edges excluded) copied from the same depth band further left,
    amplitude matched to the surrounding table."""
    H, W, _ = img.shape
    Y, X = np.mgrid[0:H, 0:W]
    lf10 = gb(img, 10)
    kt = known & (Y > 1683 + (X - 860) * 0.037 + 12)
    LF0 = gb(pushpull(lf10, kt), 6)                                     # spans the remaining glasses too
    tab = Y > 1683 + (X - 860) * 0.037 + 12
    F = np.where(kt[..., None], lf10, LF0)                               # glass footprints carry LF0
    LF = harmonic(F, hole, tab)
    lf3 = gb(img, 3)
    rel = np.clip(img / np.maximum(lf3, 1e-3) - 1, -0.3, 0.3)
    # grain source: first valid candidate offset (table, not glass/hole, no shadow edge nearby)
    L4 = gb(img, 4).dot(LW)
    edge = np.hypot(ndi.sobel(L4, 0), ndi.sobel(L4, 1))
    okmap = kt & ~ndi.binary_dilation(edge > 0.10, iterations=4)
    src = np.zeros_like(img); got = np.zeros((H, W), bool)
    for dx in (hf_shift[1], hf_shift[1] - 60, hf_shift[1] + 60, hf_shift[1] - 130, hf_shift[1] + 130,
               hf_shift[1] - 200, hf_shift[1] - 270, hf_shift[1] - 340):
        sx = np.clip(X + dx, 0, W - 1)
        ok = okmap[Y, sx] & ~got
        src[ok] = rel[Y, sx][ok]; got |= ok
    print('fill_table: grain source coverage %.1f %%' % (100 * got[hole].mean()))
    soft = np.clip((Y - 1950) / 200, 0, 1)[..., None]                   # table nearer the camera is softer (DOF)
    src = src * (1 - soft) + gb(src, 1.6) * soft * 1.6
    ring = ndi.binary_dilation(hole, iterations=30) & ~ndi.binary_dilation(hole, iterations=3) & kt
    srcband = ndi.shift(hole.astype(float), (-hf_shift[0], -hf_shift[1]), order=0) > 0.5
    a_ring = rel[ring].std(); a_src = rel[np.roll(np.roll(hole, hf_shift[0], 0), hf_shift[1], 1)].std()
    k = np.clip(a_ring / max(a_src, 1e-6), 0.7, 1.8)
    out = img.copy()
    out[hole] = (LF * (1 + src * k))[hole]
    print('fill_table: grain amp ring %.4f src %.4f -> x%.2f' % (a_ring, a_src, k))
    return out


def fill_bg(img, hole, known):
    """blurred background above the table edge: push-pull + light noise."""
    F = pushpull(gb(img, 2), known)
    F = gb(F, 4)
    nz = gb(np.random.default_rng(13).normal(0, 1, img.shape[:2]), 0.8)[..., None] * 0.01
    out = img.copy(); out[hole] = (F + nz)[hole]
    return out


def mirror_into(img, region, xc):
    H, W, _ = img.shape
    Y, X = np.mgrid[0:H, 0:W]
    xs = np.clip(2 * xc - X, 0, W - 1)
    m = img[Y, xs]
    out = img.copy(); out[region] = m[region]
    return out


def feather(new, old, hole, r=5.0):
    a = np.clip(gb(hole.astype(float), r) * 1.4, 0, 1)
    a = np.maximum(a, hole * 1.0)[..., None]
    return old * (1 - a) + new * a


def main():
    a = np.asarray(Image.open(os.path.join(IMG, 'S13-3_v2.png')).convert('RGB')).astype(np.float64) / 255
    H, W, _ = a.shape
    Y, X = np.mgrid[0:H, 0:W].astype(np.float64)
    TABLE_EDGE = 1683 + (X - 860) * 0.037                             # measured far table edge
    g_back = glass_mask((H, W), 880, 1092, 1540, 1930)
    g_mid = glass_mask((H, W), 1008, 1264, 1556, 2030)
    g_front = glass_mask((H, W), 1160, 1458, 1588, 2150)

    # ================= S13-2 : remove the front glass
    b = a.copy()
    # (1) its shadow band (below the middle glass shadow) and its caustic streak in front
    bound = 2143 + (1000 - X) * 0.07
    zs = ((Y > bound) & (Y < 2420) & (X < 1215)).astype(float)
    zs = gb(zs, 6) * (1 - g_front)
    b = relight(b, zs, 'lift', 85)
    zc = poly([(1125, 2150), (1290, 2150), (1300, 2480), (1120, 2480)], (H, W)).astype(float)
    zc = gb(zc, 10)
    b = relight(b, zc, 'drop', 45, win=(161, 201))
    # (2) the glass itself
    hole = ndi.binary_dilation(g_front, iterations=3)
    hole |= (X >= 1455) & (Y >= 1758) & (Y <= 1812)                       # the glass's grey reflection on the right
    mid_part = hole & g_mid
    rest = hole & ~g_mid
    known = ~hole & ~g_mid & ~g_back
    b2 = mirror_into(b, mid_part, 1136)
    bg_part = rest & (Y < TABLE_EDGE)
    tb_part = rest & (Y >= TABLE_EDGE)
    b2 = fill_bg(b2, bg_part, known & (Y < TABLE_EDGE - 2))
    b2 = fill_table(b2, tb_part, known)
    # soft blend of the table edge zone (blurred line) between bg and table fills
    band = rest & (np.abs(Y - TABLE_EDGE) < 10)
    sm = gb(b2, 3)
    b2[band] = sm[band]
    s2 = feather(b2, b, hole)
    Image.fromarray((np.clip(s2, 0, 1) * 255 + 0.5).astype(np.uint8)).save(os.path.join(IMG, 'S13-2_fix.png'))

    # ================= S13-1 : also remove the middle glass
    c = s2.copy()
    bound_m = 2078 + (1000 - X) * 0.06                                    # middle shadow: between back and front bands
    zs = ((Y > bound_m) & (Y < bound + 6) & (X < 1080)).astype(float)
    zs = gb(zs, 6) * (1 - g_mid)
    c = relight(c, zs, 'lift', 85)
    zc = poly([(975, 2040), (1085, 2040), (1090, 2380), (965, 2380)], (H, W)).astype(float)
    zc = gb(zc, 10)
    c = relight(c, zc, 'drop', 45, win=(161, 201))
    hole = ndi.binary_dilation(g_mid, iterations=3)
    back_part = hole & g_back
    rest = hole & ~g_back
    known = ~hole & ~g_back
    c2 = mirror_into(c, back_part, 986)
    c2 = fill_bg(c2, rest & (Y < TABLE_EDGE), known & (Y < TABLE_EDGE - 2))
    c2 = fill_table(c2, rest & (Y >= TABLE_EDGE), known, hf_shift=(0, -560))
    band = rest & (np.abs(Y - TABLE_EDGE) < 10)
    sm = gb(c2, 3); c2[band] = sm[band]
    s1 = feather(c2, c, hole)
    Image.fromarray((np.clip(s1, 0, 1) * 255 + 0.5).astype(np.uint8)).save(os.path.join(IMG, 'S13-1_fix.png'))
    print('saved S13-2_fix.png, S13-1_fix.png (%dx%d)' % (W, H))


if __name__ == '__main__':
    main()
