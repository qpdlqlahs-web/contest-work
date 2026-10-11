# -*- coding: utf-8 -*-
"""cut 16 stills (new files only):
 S16-1_v2.png : S16-1_1 + sill props (pot, tumbler, kettle) cut from K5_last, amber #F2B66D multiply 35 %
 S16-2_v3.png : S16-2v2_1, child masked; background gaussian 14 px + exposure -0.3 EV (mask-aware blur)
 S16-3_v2.png : S16-3_1 + sill props, no amber (OFF), neutral gain matched to the sill
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

IMG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img')
LW = np.array([0.2126, 0.7152, 0.0722])
W, H = 1536, 2752


def load(n, size=None):
    im = Image.open(os.path.join(IMG, n)).convert('RGB')
    if size and im.size != size:
        im = im.resize(size, Image.LANCZOS)
    return np.asarray(im).astype(np.float64) / 255


def save(a, n):
    Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8)).save(os.path.join(IMG, n))


def gb(a, s):
    return ndi.gaussian_filter(a, s) if a.ndim == 2 else np.stack([ndi.gaussian_filter(a[..., c], s) for c in range(3)], -1)


def gm(L):
    L = gb(L, 1.5)
    return np.hypot(ndi.sobel(L, 0), ndi.sobel(L, 1))


def register(src, dst, box, rng=24, step=2):
    """translation src->dst on gradient NCC inside box (x0,y0,x1,y1) (window frame / sill edges)."""
    x0, y0, x1, y1 = box
    gs, gd = gm(src @ LW), gm(dst @ LW)
    B = gd[y0:y1, x0:x1]; best = (-9, 0, 0)
    for dy in range(-rng, rng + 1, step):
        for dx in range(-rng, rng + 1, step):
            A = gs[y0 - dy:y1 - dy, x0 - dx:x1 - dx] if (y0 - dy >= 0 and x0 - dx >= 0) else None
            if A is None or A.shape != B.shape:
                continue
            aa, bb = A - A.mean(), B - B.mean()
            v = (aa * bb).sum() / np.sqrt((aa * aa).sum() * (bb * bb).sum() + 1e-12)
            if v > best[0]:
                best = (v, dx, dy)
    return best


def props(dst_name, out_name, amber, erode=0, contact=0.35, cblur=4):
    k5 = load('K5_last.png', (W, H))
    d = load(dst_name)
    v, dx, dy = register(k5, d, (0, 1150, 240, 2050))
    src = np.stack([ndi.shift(k5[..., c], (dy, dx), order=1, mode='nearest') for c in range(3)], -1)
    # props: hand-traced outline in K5 (1536x2752) coords, refined: bright neutral pixels connected to the
    # outline border (window/wall seen around the props) are removed; enclosed chrome highlights stay
    yy, xx = np.mgrid[0:H, 0:W]
    P = [(105,1735),(112,1712),(130,1702),(168,1700),(200,1708),(220,1706),(238,1715),(244,1740),(243,1800),
         (232,1825),(222,1840),(200,1848),(192,1852),(192,1884),(170,1893),(150,1890),(152,1912),(132,1934),
         (60,1938),(25,1926),(18,1892),(10,1858),(14,1836),(35,1822),(65,1812),(72,1800),(92,1800),(100,1812),(105,1810)]
    pm = Image.new('L', (W, H), 0)
    ImageDraw.Draw(pm).polygon([(x + dx, y + dy) for x, y in P], fill=255)
    poly = np.asarray(pm) > 0
    Ls = src @ LW
    satS = (src.max(2) - src.min(2))
    bgc = poly & (gb(Ls, 1.0) > 0.78) & (satS < 0.07)
    border = poly & ~ndi.binary_erosion(poly, iterations=2)
    lab, n = ndi.label(bgc | (border & bgc))
    touch = np.unique(lab[border & bgc]); touch = touch[touch > 0]
    m = poly & ~np.isin(lab, touch)
    m = ndi.binary_opening(m, iterations=1)
    lab, n = ndi.label(m); sz = ndi.sum(m, lab, range(1, n + 1)); m = np.isin(lab, np.where(sz > 800)[0] + 1)
    m = ndi.binary_fill_holes(m) & poly
    if erode:
        m = ndi.binary_erosion(m, iterations=erode)
    # contact shadow band just under the bases on the sill
    base = np.zeros((H, W), bool)
    for (x0, x1, yb) in [(22, 150, 1934), (148, 192, 1889), (190, 226, 1846)]:
        base |= (xx >= x0 + dx) & (xx <= x1 + dx) & (yy >= yb + dy - 3) & (yy <= yb + dy + 4)
    shadow = gb(base.astype(float), cblur)
    shadow = shadow / max(shadow.max(), 1e-6) * (1 - m)
    sill_ref = np.median(src[(xx < 240) & (yy > 1700) & (yy < 1950) & (Ls > 0.8)], 0)
    a = gb(m.astype(float), 1.0)
    # tone: neutral gain so the K5 sill white matches the target sill white
    Ld = d @ LW
    sel = (xx < 240) & (yy > 1850) & (yy < 1950) & ~poly & (Ld > 0.6)
    tgt_white = np.median(d[sel], 0) if sel.sum() > 200 else sill_ref
    gain = tgt_white / sill_ref
    if amber:
        gain = np.ones(3)               # S16-1: amber multiply as instructed (sill already warm)
    p = src * gain
    if amber:
        am = np.array([0xF2, 0xB6, 0x6D]) / 255.0
        p = p * (1 - 0.35) + p * am * 0.35
    o = d.copy()
    o = o * (1 - contact * shadow[..., None])
    o = o * (1 - a[..., None]) + p * a[..., None]
    save(o, out_name)
    print('%s: K5 props shift (%d,%d) ncc %.3f, prop px %d, gain %s%s' % (out_name, dx, dy, v, m.sum(), gain.round(3),
          ', amber x35 %' if amber else ''))


CHILD = [(110,95),(150,80),(190,92),(205,120),(212,170),(210,215),(207,236),(215,240),(260,240),(320,245),(355,250),
         (375,252),(390,255),(405,265),(445,278),(452,290),(442,301),(400,303),(385,309),(360,306),(300,312),(255,325),
         (248,340),(246,400),(250,480),(248,545),(238,550),(232,620),(222,700),(212,826),(70,826),(68,700),(65,600),
         (62,550),(45,545),(38,500),(30,440),(25,400),(30,330),(45,280),(65,250),(80,236),(72,200),(75,150),(90,110)]


def s16_2():
    a = load('S16-2v2_1.png')
    poly = Image.new('L', (W, H), 0)
    ImageDraw.Draw(poly).polygon([(2 * x, 1100 + 2 * y) for x, y in CHILD], fill=255)
    poly = np.asarray(poly) > 0
    mx, mn = a.max(2), a.min(2); sat = (mx - mn) / np.maximum(mx, 1e-6)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    hue = np.degrees(np.arctan2(np.sqrt(3) * (g - b), 2 * r - g - b)) % 360
    L = a @ LW
    clothes = (sat > 0.68) & (hue > 12) & (hue < 48) & (mx > 0.18)
    yy, xx = np.mgrid[0:H, 0:W]
    hair = (L < 0.13) & ((b - r) < 0.035) & ((yy < 1585) | ((xx > 640) & (xx < 915) & (yy > 1645) & (yy < 1715)))
    core = ndi.binary_erosion(poly, iterations=40)
    navy = ((b - r) > 0.025) & (L < 0.35) & ~clothes
    fg = poly & (clothes | hair | core) & ~navy
    fg = ndi.binary_closing(fg, iterations=3)
    fg = ndi.binary_fill_holes(fg)
    fg = ndi.binary_opening(fg, iterations=2)
    lab, n = ndi.label(fg); sz = ndi.sum(fg, lab, range(1, n + 1)); fg = lab == (np.argmax(sz) + 1)
    alpha = np.clip(gb(fg.astype(float), 1.3), 0, 1)
    # mask-aware background blur (child pixels excluded so they do not bleed), then -0.3 EV
    bgw = 1 - np.clip(gb(fg.astype(float), 2), 0, 1)
    bl = gb(a * bgw[..., None], 14) / np.maximum(gb(bgw, 14), 1e-4)[..., None]
    bl = np.clip(bl ** 2.2 * 2 ** -0.3, 0, 1) ** (1 / 2.2)
    nz = gb(np.random.default_rng(16).normal(0, 1, (H, W)), 0.7)[..., None] * 0.006   # keep grain on the blurred bg
    o = (bl + nz) * (1 - alpha[..., None]) + a * alpha[..., None]
    save(o, 'S16-2_v3.png')
    Image.fromarray((alpha * 255).astype(np.uint8)).save(os.path.join(IMG, 'S16-2_v3_childmask.png'))
    print('S16-2_v3: child mask %d px; bg blur 14 px, -0.3 EV; remote buttons: no symbols found' % fg.sum())


if __name__ == '__main__' and '--s163v3' in sys.argv:
    props('S16-3_1.png', 'S16-3_v3.png', amber=False, erode=2, contact=0.50, cblur=4)
    sys.exit()
if __name__ == '__main__':
    props('S16-1_1.png', 'S16-1_v2.png', amber=True)
    props('S16-3_1.png', 'S16-3_v2.png', amber=False)
    s16_2()
