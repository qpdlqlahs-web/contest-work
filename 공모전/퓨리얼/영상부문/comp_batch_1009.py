# -*- coding: utf-8 -*-
"""
Product composite batch (2026-10-09), guide ch.4 + 5-1.
  S01_comp.png  : S01v2_1 (ON wide, fridge doodles removed) + official (2), h = 1.3 x microwave, ON colour #ECCEAA
  S02_comp.png  : same frame OFF: 3000K->5600K, strip light / pendant / TV switched off, product OFF colour
  S05_comp.png  : S05v4_1 + official (2) on the back-right counter, defocused like the background
  S10-2_comp.png: S10_start_v5 with official (4) (door open) at v5 coords (0.6722, 454.94/762.72)
  S11-1_comp.png: 10-2 tight crop 1.2x
  S11-2_comp.png / S11-3_comp.png: filter 03 lifted halfway / aligned with 01-02 height (same 1.2x crop)
  KF2_comp.png  : KF2BG_v3 + official (3) at 1.6x (nozzle head -> tray ~54 % of frame height)
Usage: python comp_batch_1009.py [s01 s05 s10 kf2]   (default: all)
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from comp_k1 import cutout, gblur, lum
from comp_k1_v2 import warp
from comp_s18 import contact_band

IMG = os.path.join(HERE, 'img')
DIR = os.path.join(HERE, '..', 'refs', 'assets', '02. 퓨리얼 유로체인저 직수정수기 PPA-300')
OW, OH = 1080, 1920
LW = np.array([0.2126, 0.7152, 0.0722])
yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float64)
hx = lambda v: '#%02X%02X%02X' % tuple((np.clip(v, 0, 1) * 255).round().astype(int))
_cut = {}


def cut(n):
    if n not in _cut:
        C, A = cutout(os.path.join(DIR, 'PPA-300 (%s).jpg' % n))
        _cut[n] = (C / 255.0, A)
    return _cut[n]


def load(name, size=(OW, OH)):
    im = Image.open(os.path.join(IMG, name)).convert('RGB')
    if im.size != size:
        im = im.resize(size, Image.LANCZOS)
    return np.asarray(im).astype(np.float64) / 255


def save(a, name):
    Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8)).save(os.path.join(IMG, name))


def grain(a, seed, amp=0.006):
    g = gblur(np.random.default_rng(seed).normal(0, 1, a.shape[:2]), 0.6) * 2.1
    w = amp * (0.6 + 0.4 * np.clip(1 - np.abs(lum(a) - 0.5) / 0.5, 0, 1))
    return np.clip(a + (g * w)[..., None], 0, 1)


def chrome_mask(PL, AL):
    rb = (PL[..., 0] - PL[..., 2]) * 255
    return gblur(np.clip((9 - rb) / 6, 0, 1) * (AL > 0), 0.8)


def grade(PL, AL, lit, light='right', dodge=0.08, burn=0.15, sat=0.92, room=None, cast=None):
    """official layer -> scene: directional dodge/burn, chrome room reflection, lit face top-5 % -> `lit`."""
    solid = AL > 0.5
    xs = xx[solid]
    u = np.clip((xx - xs.min()) / max(xs.max() - xs.min(), 1), 0, 1)
    if light == 'left':
        u = 1 - u
    G = PL.copy()
    G = G / (1 - dodge * np.clip((u - 0.6) / 0.4, 0, 1) ** 1.2)[..., None]
    G = G * (1 - burn * np.clip((0.45 - u) / 0.45, 0, 1) ** 1.2)[..., None]
    ch = chrome_mask(PL, AL)
    if room is not None:
        rm = gblur(room, 12)
        sl = np.where(rm <= 0.5, G - (1 - 2 * rm) * G * (1 - G), G + (2 * rm - 1) * (np.sqrt(np.clip(G, 0, 1)) - G))
        spec = np.clip((lum(PL) - 0.93) / 0.05, 0, 1)[..., None]
        G = G * (1 - 0.3 * ch[..., None] * (1 - spec)) + sl * 0.3 * ch[..., None] * (1 - spec)
    Lg = lum(G)[..., None]
    G = Lg + (G - Lg) * sat
    if cast is not None:
        G = G * cast
    cream = (AL > 0.95) & (ch < 0.1)
    Lc = lum(G)[cream]
    top = G[cream][Lc >= np.percentile(Lc, 95)].mean(0)
    G = G * (np.asarray(lit) / top)
    return np.clip(G, 0, 1)


def comp_layer(plate, G, AL, blur=0.5):
    Gs = gblur(G, blur) if blur > 0 else G
    a = gblur(AL, blur * 0.8)[..., None] if blur > 0.6 else AL[..., None]
    out = Gs * a + plate * (1 - a)
    edge = np.clip(AL - ndi.grey_erosion(AL, size=(3, 3)), 0, 1)[..., None]
    return out * (1 - 0.12 * edge) + gblur(plate, 3) * 0.12 * edge


def shadows(plate, AL, contact=0.65, cblur=3, cast=0.35, cast_dir=(-0.4, 0.05), cast_blur=20, ao=0.25):
    solid = AL > 0.5
    cb = gblur(contact_band(solid, tol=6, down=3, up=1), cblur); cb /= max(cb.max(), 1e-6)
    has = solid.any(0)
    ybot = np.where(has, OH - 1 - np.argmax(solid[::-1], 0), -1)
    gl = ybot[has].max(); xs_ = np.nonzero(has)[0]
    # soft occlusion halo along the base
    halo = ((yy >= gl - 4) & (yy <= gl + 3) & (xx >= xs_.min()) & (xx <= xs_.max())).astype(float)
    halo = gblur(halo, max(cblur * 3, 4)); halo /= max(halo.max(), 1e-6)
    out = plate * (1 - ao * halo[..., None]) * (1 - contact * cb[..., None])
    if cast > 0:
        ys, xs = np.nonzero(solid[::2, ::2]); ys = ys * 2; xs = xs * 2
        h = np.clip(gl - ys, 0, None)
        tx = np.round(xs + cast_dir[0] * h).astype(int); ty = np.round(gl + cast_dir[1] * h).astype(int)
        k = (tx >= 0) & (tx < OW) & (ty >= 0) & (ty < OH)
        c = np.zeros((OH, OW)); np.add.at(c, (ty[k], tx[k]), 1.0)
        c = gblur(np.clip(ndi.grey_dilation(c, size=(5, 5)), 0, 1), cast_blur)
        c = np.clip(c / max(c.max(), 1e-6) * 1.15, 0, 1) * np.clip((yy - (gl - 6)) / 6, 0, 1)
        out = out * (1 - cast * c[..., None])
    return out


def place(n, s, tx, ty):
    C, A = cut(n)
    return np.clip(warp(C, s, tx, ty, order=3), 0, 1), np.clip(warp(A, s, tx, ty), 0, 1)


def bbox_tf(n, height, cx, base):
    """uniform scale so the photo bbox height = height, bbox centre x = cx, bbox bottom = base."""
    C, A = cut(n)
    ys, xs = np.nonzero(A > 0.5)
    s = height / (ys.max() + 1 - ys.min())
    return s, cx - s * (xs.min() + xs.max() + 1) / 2, base - s * (ys.max() + 1)


# ====================================================================== S01 / S02
def fix_fridge(a):
    """remove two doodles on the fridge drawings (coords in the 1536x2752 original)."""
    H, W, _ = a.shape
    Y, X = np.mgrid[0:H, 0:W]
    out = a.copy()
    # 1) handwriting-like scribble right of the house roof -> paper, then a copy of the blue cloud
    x0, x1, y0, y1 = 394, 431, 1319, 1349
    sub = a[y0:y1 + 1, x0:x1 + 1]
    keep_o = ((sub[..., 0] - sub[..., 2]) > 0.18) & (sub.mean(2) > 0.55)       # yellow tape stays
    keep_o = ndi.binary_dilation(keep_o, iterations=1)
    hole = np.zeros((H, W), bool); hole[y0:y1 + 1, x0:x1 + 1] = ~keep_o
    redm = ndi.binary_dilation((a[..., 0] - a[..., 1]) > 0.12, iterations=1)
    hole &= ~((X <= 402) & redm)
    win = (slice(y0 - 12, y1 + 13), slice(x0 - 12, x1 + 4))
    w_a = a[win].copy(); w_h = hole[win]
    paper = ~w_h & (w_a.mean(2) > 0.565)                                    # known paper only (not fridge)
    kn = paper.copy(); todo = w_h.copy()
    for _ in range(200):                                                     # onion-peel fill
        wt = gblur(kn.astype(float), 1.5)
        est = gblur(w_a * kn[..., None], 1.5) / np.maximum(wt, 1e-9)[..., None]
        new = todo & (wt > 0.15)
        w_a = np.where(new[..., None], est, w_a)
        kn |= new; todo &= ~new
        if not todo.any():
            break
    w_a = np.where(w_h[..., None], gblur(w_a, 1.0), w_a)
    nz = ndi.gaussian_filter(np.random.default_rng(7).normal(0, 1, w_h.shape), 0.6) * 0.012
    w_a = np.where(w_h[..., None], w_a + nz[..., None], w_a)
    out[win] = w_a
    red = ((a[..., 0] - a[..., 1]) > 0.12)                        # roof (red) pixels only
    roof = (X <= 402) & (Y >= 1336) & (X >= x0) & (Y <= y1) & ndi.binary_dilation(red, iterations=1)
    out[roof] = a[roof]
    cl = a[1318:1338, 325:363]                                   # blue cloud tile
    cm = np.clip(((cl[..., 2] - cl[..., 0]) - 0.06) / 0.08, 0, 1)
    cm = ndi.gaussian_filter(cm, 0.6)[..., None]
    py, px = 1321, 395
    out[py:py + 20, px:px + 38] = out[py:py + 20, px:px + 38] * (1 - cm) + cl * cm
    # 2) 'A'-like legs under the small star figure: row-wise paper interpolation
    for y in range(1286, 1301):
        L = a[y, 366:369].mean(0); R = a[y, 387:390].mean(0)
        t = (np.arange(369, 387) - 368) / 19.0
        out[y, 369:387] = L[None] * (1 - t[:, None]) + R[None] * t[:, None]
    return out


def s01_s02():
    big = np.asarray(Image.open(os.path.join(IMG, 'S01v2_1.png')).convert('RGB')).astype(np.float64) / 255
    big = fix_fridge(big)
    Image.fromarray((big * 255 + 0.5).astype(np.uint8)).save(os.path.join(IMG, 'S01v2_fridgefix.png'))
    plate = np.asarray(Image.fromarray((big * 255 + 0.5).astype(np.uint8)).resize((OW, OH), Image.LANCZOS)) / 255.0
    k = OW / 1536.0
    # microwave body 97 px (1536) -> product 1.3x = 126 px -> 88.6 px at 1080
    s, tx, ty = bbox_tf('2', 126 * k, 1372 * k, 1479 * k)
    PL, AL = place('2', s, tx, ty)
    print('S01: product (2) scale %.4f t=(%.1f, %.1f) h=%.1f px' % (s, tx, ty, 126 * k))
    # ---- S01 (ON): flat warm ceiling light, lit face #ECCEAA
    pl1 = shadows(plate, AL, contact=0.6, cblur=1.5, cast=0.18, cast_dir=(-0.2, 0.08), cast_blur=6, ao=0.25)
    G1 = grade(PL, AL, np.array([0xEC, 0xCE, 0xAA]) / 255, light='right', dodge=0.04, burn=0.10, sat=0.9, room=plate)
    out1 = comp_layer(pl1, G1, AL, blur=0.7)
    save(grain(out1, 101), 'S01_comp.png')
    # ---- S02 (OFF)
    p2 = off_grade(plate)
    pl2 = shadows(p2, AL, contact=0.6, cblur=1.5, cast=0.3, cast_dir=(-0.55, 0.05), cast_blur=8, ao=0.25)
    G2 = grade(PL, AL, np.array([0xF1, 0xE9, 0xDC]) / 255, light='right', dodge=0.10, burn=0.18, sat=0.92, room=p2)
    out2 = comp_layer(pl2, G2, AL, blur=0.7)
    save(grain(out2, 102), 'S02_comp.png')
    print('S02: ceiling %s -> %s, window %s -> %s' % (hx(plate[100:250, 200:850].mean((0, 1))), hx(p2[100:250, 200:850].mean((0, 1))),
                                                     hx(plate[730:960, 960:1000].mean((0, 1))), hx(p2[730:960, 960:1000].mean((0, 1)))))


def off_grade(p):
    """3000K ON frame -> 5600K OFF: lamps & TV off, window light only (1080 coords)."""
    k = OW / 1536.0
    lin = p ** 2.2
    # white balance: ceiling (lit by the lamps) -> slightly cool neutral
    ref = lin[int(100 * k):int(350 * k), int(300 * k):int(1200 * k)].reshape(-1, 3).mean(0)
    tgt = np.array([0.97, 1.0, 1.04]) * ref.dot(LW)
    wb = tgt / ref
    lin = lin * wb
    # lights off: global -1.1 stop, window glass & sheer curtain (very bright) protected
    L = (p ** 2.2 * wb).dot(LW)
    keep = np.clip((L - 0.45) / 0.35, 0, 1)
    win = np.zeros((OH, OW))
    win[int(1015 * k):int(1455 * k), int(1350 * k):int(1445 * k)] = 1          # kitchen window
    win[int(820 * k):int(2000 * k), int(1455 * k):] = 1                         # sheer curtain right edge
    win = gblur(win, 6) * keep
    ex = 0.47 * (1 - win) + 1.0 * win
    lin = lin * ex[..., None]
    o = np.clip(lin, 0, 1) ** (1 / 2.2)
    # strip light under the cabinets: diffuser unlit
    strip = np.zeros((OH, OW))
    strip[int(902 * k):int(929 * k), int(624 * k):int(1076 * k)] = 1
    strip = gblur(strip, 1.2)
    unlit = gblur(o, 8) * 0.85
    o = o * (1 - strip[..., None]) + unlit * strip[..., None]
    # pendant drum shade: linen lit only from outside
    sh = Image.new('L', (OW, OH), 0)
    ImageDraw.Draw(sh).rectangle([943 * k, 1030 * k, 1138 * k, 1150 * k], fill=255)
    ImageDraw.Draw(sh).ellipse([943 * k, 1138 * k, 1138 * k, 1165 * k], fill=255)
    sh = gblur(np.asarray(sh) / 255.0, 1.0)
    Ls = lum(o)[..., None]
    linen = (Ls + (o - Ls) * 0.4) * 0.55
    rim = np.clip(((yy - 1140 * k) / (8 * k)), 0, 1)[..., None]
    linen = linen * (1 - 0.35 * rim)
    o = o * (1 - sh[..., None]) + linen * sh[..., None]
    # TV screen: black glass with a faint window reflection gradient
    tv = Image.new('L', (OW, OH), 0)
    ImageDraw.Draw(tv).polygon([(38 * k, 1488 * k), (196 * k, 1468 * k), (196 * k, 1848 * k), (38 * k, 1995 * k)], fill=255)
    tv = gblur(np.asarray(tv) / 255.0, 0.8)
    g = np.clip((xx - 38 * k) / (158 * k), 0, 1) * 0.5 + np.clip((1700 * k - yy) / (250 * k), 0, 1) * 0.5
    scr = np.array([0x10, 0x12, 0x15]) / 255 + (np.array([0x2A, 0x2E, 0x34]) / 255 - np.array([0x10, 0x12, 0x15]) / 255) * g[..., None] * 0.6
    o = o * (1 - tv[..., None]) + scr * tv[..., None]
    # blue-grey shadows (#3A3F45 lift), saturation -18 %
    Lo = lum(o)[..., None]
    o = Lo + (o - Lo) * 0.82
    o = o + (np.array([0x3A, 0x3F, 0x45]) / 255 - o) * 0.10 * np.clip(1 - Lo / 0.35, 0, 1)
    return np.clip(o, 0, 1)


# ====================================================================== S05
def s05():
    plate = load('S05v4_1.png')
    k = OW / 1536.0
    # cabinet bottom -> counter at the back corner: 410 px / 60 cm (1536) -> 6.8 px/cm at the wall,
    # product ~10 cm in front of the tiles -> ~7.1 px/cm -> 34 cm = 240 px (1536) = 169 px (1080)
    s, tx, ty = bbox_tf('2', 240 * k, 780 * k, 1652 * k)
    PL, AL = place('2', s, tx, ty)
    pl = shadows(plate, AL, contact=0.6, cblur=2.5, cast=0.35, cast_dir=(-0.5, 0.04), cast_blur=14, ao=0.3)
    G = grade(PL, AL, np.array([0xE4, 0xDF, 0xD6]) / 255, light='right', dodge=0.10, burn=0.20, sat=0.88, room=plate,
              cast=np.array([0.985, 1.0, 1.02]))
    out = comp_layer(pl, G, AL, blur=1.3)                        # background defocus (tile grout ~3 px soft)
    if os.environ.get('S05_LAYER_ONLY'):
        lay = np.dstack([np.clip(gblur(G, 1.3), 0, 1), np.clip(gblur(AL, 1.04), 0, 1)])
        Image.fromarray((lay * 255 + 0.5).astype(np.uint8), 'RGBA').save(os.path.join(IMG, 'S05_product_layer.png'))
        return
    save(grain(out, 105), 'S05_comp.png')
    ys, xs = np.nonzero(AL > 0.5)
    print('S05: (2) scale %.4f, bbox x %d-%d y %d-%d (h %d px); Dad head ~158 px (1080) -> image ratio %.2f'
          % (s, xs.min(), xs.max(), ys.min(), ys.max(), ys.max() - ys.min(), (ys.max() - ys.min()) / 158.0))


# ====================================================================== S10-2 / S11
S3, T3 = 0.6665, (454.94, 764.76)
S4, T4 = 0.6722, (454.94, 762.72)
F03 = (330, 466, 462, 884)          # filter 03 box in photo (4): x0, y0, x1, y1


def filter03_mask():
    """filter 03 silhouette in photo (4): detected neck/thread (neutral white or dark rings vs cream chroma ~0.14),
    straight cylinder body below the shoulder (the label text defeats colour detection there)."""
    C, A = cut('4')
    ch = C.max(2) - C.min(2); L = C.mean(2)
    m = np.zeros(A.shape, bool)
    fil = (ch < 0.06) | (L < 0.35)
    for y in range(466, 546):
        row = fil[y, 300:500]; c = 97
        if not row[c]:
            continue
        l = c
        while l > 0 and row[l - 1]: l -= 1
        r = c
        while r < 199 and row[r + 1]: r += 1
        m[y, 300 + l:300 + r + 1] = True
    for y in range(546, 883):
        inset = int(round(10 - np.sqrt(max(0, 100 - (max(0, y - 872)) ** 2)))) if y > 872 else 0
        m[y, 336 + inset:464 - inset] = True
    m = ndi.binary_closing(m, iterations=2)
    m = ndi.binary_fill_holes(m)
    return m


TILT = 0.0   # deg, filter 03 tilt while floating (S11-2 v4)


def photo4_variant(lift):
    """photo (4) with filter 03 moved up by `lift` px (photo coords). Returns C, A, filter alpha (moved)."""
    C, A = cut('4')
    F = filter03_mask()
    Fd = ndi.binary_dilation(F, iterations=2)
    Cn, An = C.copy(), A.copy()
    if lift is None or lift:
        H, W = F.shape
        rows = np.nonzero(Fd.any(1))[0]
        for y in rows:
            xs = np.nonzero(Fd[y])[0]
            xl, xr = xs.min() - 3, xs.max() + 3
            if y <= 848:                                          # inside the product body: row interpolation
                L = C[y, xl - 2:xl + 1].mean(0); R = C[y, xr:xr + 3].mean(0)
                t = (np.arange(xl, xr + 1) - xl) / max(xr - xl, 1)
                Cn[y, xl:xr + 1] = L[None] * (1 - t[:, None]) + R[None] * t[:, None]
                An[y, xl:xr + 1] = np.maximum(A[y, xl:xr + 1] * (~Fd[y, xl:xr + 1]), np.minimum(A[y, xl], A[y, xr]))
            else:                                                 # below the base: background
                Cn[y, xs] = 1.0; An[y, xs] = 0.0
        if lift is None:
            return Cn, An
        if TILT:
            cy_, cx_ = 675.0, 398.0                                   # filter 03 centre (photo 4)
            Fr = ndi.rotate(F.astype(float), TILT, reshape=False, order=1) if False else None
            th = np.deg2rad(TILT); cth, sth = np.cos(th), np.sin(th)
            Yp, Xp = np.mgrid[0:F.shape[0], 0:F.shape[1]].astype(float)
            sy = cy_ + (Yp - cy_) * cth - (Xp - cx_) * sth
            sx = cx_ + (Yp - cy_) * sth + (Xp - cx_) * cth
            F = ndi.map_coordinates(F.astype(float), [sy, sx], order=1) > 0.5
            C = np.stack([ndi.map_coordinates(C[..., c], [sy, sx], order=3, mode='nearest') for c in range(3)], -1)
        Fs = np.roll(F, -lift, axis=0)
        Cs = np.roll(C, -lift, axis=0)
        fa = gblur(Fs.astype(float), 0.6)
        Cn = Cn * (1 - fa[..., None]) + Cs * fa[..., None]
        An = np.maximum(An, fa)
    return Cn, An


def s10_s11():
    v5 = load('S10_start_v5.png')
    lay5 = np.asarray(Image.open(os.path.join(IMG, 'S10_product_layer_v5.png'))).astype(np.float64) / 255
    C3, A3o = cut('3')
    PL3 = np.clip(warp(C3, S3, *T3, order=1), 0, 1); A3 = lay5[..., 3]
    C4, A4o = cut('4')
    A4 = np.clip(warp(A4o, S4, *T4), 0, 1)
    # ---- product-free plate: v5 outside (3) ; where (3) was and (4) will not cover -> fill from outside
    s3 = A3 > 0.02
    known = ~ndi.binary_dilation(s3, iterations=2)
    fill = ndi.binary_dilation(s3, iterations=2)
    work = v5.copy()
    for _ in range(300):
        est = gblur(work * known[..., None], 2.0) / np.maximum(gblur(known.astype(float), 2.0), 1e-6)[..., None]
        work = np.where(fill[..., None], est, work)
    plate = np.where(fill[..., None], work, v5)
    # keep the v5 contact shadows/counter under the base: rows below the base line come from v5
    base = np.nonzero((A3 > 0.5).any(1))[0].max()
    under = (yy > base + 1) & fill
    plate = np.where(under[..., None], v5, plate)
    # ---- grade transfer (3)->(4): channel gains + low-frequency shading measured on the v5 layer
    cream = (A3 > 0.95) & (chrome_mask(PL3, A3) < 0.1)
    Ls = lambda im: lum(im) + 0 * im[..., 0]
    PL3s = Ls(PL3)[..., None] + (PL3 - Ls(PL3)[..., None]) * 0.83
    gains = lay5[..., :3][cream].mean(0) / PL3s[cream].mean(0)
    w = ndi.binary_erosion(A3 > 0.9, iterations=3).astype(float)
    nb = lambda im: gblur(im * w, 18) / np.maximum(gblur(w, 18), 1e-4)
    shade = nb(lum(lay5[..., :3])) / np.maximum(nb(lum(PL3s * gains)), 1e-3)
    shade = np.clip(shade, 0.8, 1.2)
    print('S10-2: (3)->v5 channel gains', gains.round(3))

    def render(lift, name):
        Cv, Av = photo4_variant(lift)
        PL = np.clip(warp(Cv, S4, *T4, order=3), 0, 1); AL = np.clip(warp(Av, S4, *T4), 0, 1)
        Lp = lum(PL)[..., None]
        G = (Lp + (PL - Lp) * 0.83) * gains * shade[..., None]
        G = np.minimum(G, np.array([0xC8, 0xC4, 0xBD]) / 255 * 1.05)  # filters are white plastic: allow a bit more
        pl = plate.copy()
        # filter 03 contact shadow only when it stands on the counter
        if lift == 0 or lift is None:
            fx0 = S4 * F03[0] + T4[0]; fx1 = S4 * F03[2] + T4[0]; fyb = S4 * 880 + T4[1]
            band = ((xx >= fx0) & (xx <= fx1) & (yy >= fyb - 2) & (yy <= fyb + 3)).astype(float)
            band = gblur(band, 4); band /= max(band.max(), 1e-6)
            if lift == 0:
                pl = pl * (1 - 0.7 * band[..., None])
        else:   # floating filter: faint soft shadow on the cabinet behind (light from the left window)
            Fm = np.roll(filter03_mask(), -lift, axis=0).astype(float)
            Fw = np.clip(warp(Fm, S4, T4[0] + 6, T4[1] + 5), 0, 1)
            sh = gblur(Fw, 6) * 0.18
            G = G * (1 - sh[..., None] * (1 - np.clip(warp(np.roll(filter03_mask(), -lift, axis=0).astype(float), S4, *T4), 0, 1))[..., None])
        out = comp_layer(pl, G, AL, blur=0.5)
        if name is None:
            return out, gains
        out = grain(out, 1100 + lift, amp=0.004)
        save(out, name)
        return out

    if os.environ.get('S11_ALT'):
        return render
    full = render(0, 'S10-2_comp.png')
    # tight crop 1.2x (900x1600 window) shared by 11-1..11-3
    cx0, cy0, cw, ch = 180, 310, 900, 1600

    def crop(a, name):
        im = Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8)).crop((cx0, cy0, cx0 + cw, cy0 + ch))
        im.resize((OW, OH), Image.LANCZOS).save(os.path.join(IMG, name))
    crop(full, 'S11-1_comp.png')
    # 11-2: halfway (03 top 470 -> ~390), 11-3: tops aligned with 01/02 caps (~310)
    a2 = render(80, '_S11-2_full.png'); crop(a2, 'S11-2_comp.png')
    a3 = render(160, '_S11-3_full.png'); crop(a3, 'S11-3_comp.png')
    print('S11 crop: x %d-%d y %d-%d (1.2x); filter 03 lift: 11-2 = 80 px photo (%.0f px frame), 11-3 = 160 px (%.0f px)'
          % (cx0, cx0 + cw, cy0, cy0 + ch, 80 * S4, 160 * S4))


# ====================================================================== KF2
def kf2():
    plate = load('KF2BG_v3.png')
    s, tx, ty = 1.6, 72.0, 13.0                                  # nozzle (180,365) -> (360, 597); tray bottom 865 -> 1397
    PL, AL = place('3', s, tx, ty)
    pl = shadows(plate, AL, contact=0.7, cblur=3, cast=0.35, cast_dir=(0.45, -0.02), cast_blur=24, ao=0.3)
    G = grade(PL, AL, np.array([0xF1, 0xE9, 0xDC]) / 255, light='left', dodge=0.10, burn=0.15, sat=0.92, room=plate)
    out = comp_layer(pl, G, AL, blur=0.6)
    if os.environ.get('KF2_LAYER_ONLY'):
        Gs = gblur(G, 0.6)
        Image.fromarray((np.dstack([np.clip(Gs, 0, 1), AL]) * 255 + 0.5).astype(np.uint8), 'RGBA').save(
            os.path.join(IMG, 'KF2_product_layer.png'))
        return
    save(grain(out, 909), 'KF2_comp.png')
    ys, xs = np.nonzero(AL > 0.5)
    print('KF2: (3) scale %.2f t=(%.0f,%.0f); head top y %.0f, tray bottom y %.0f -> %.1f %% of frame; nozzle (%.0f, %.0f)'
          % (s, tx, ty, ty + s * 215, ty + s * 865, 100 * s * 650 / OH, tx + s * 180, ty + s * 390))


def s11_alt():
    """cut 11 alternative (director decision): official single-filter photos 1/2/3 line up on the counter in front of
    the open product; nothing near the socket, no rotation."""
    os.environ['S11_ALT'] = '1'
    render = s10_s11()
    base, gains = render(None, None)                    # S10-2 with the standing filter 03 removed (no duplicate 03)
    fdir = os.path.join(HERE, '..', 'refs', 'assets', '09. 퓨리얼 필터', '1. 정품 필터')
    cuts = []
    for n in (1, 2, 3):
        C, A = cutout(os.path.join(fdir, '%d번 필터.jpg' % n))
        cuts.append((C / 255.0, A))
    # scale: real size unknown -> match filter 03 in official (4): 412 px tall there -> 0.6722 * 412 = 277 px,
    # placed ~8 cm nearer the camera than the product base -> x1.05
    Hf = 277 * 1.05
    base_y = 1418.0
    centers = [688.0, 792.0, 896.0]

    def frame(k, name):
        out = base.copy()
        layers = []
        for i in range(k):
            C, A = cuts[i]
            ys, xs = np.nonzero(A > 0.5)
            s = Hf / (ys.max() + 1 - ys.min())
            tx = centers[i] - s * (xs.min() + xs.max() + 1) / 2
            ty = base_y - s * (ys.max() + 1)
            PL = np.clip(warp(C, s, tx, ty, order=3), 0, 1); AL = np.clip(warp(A, s, tx, ty), 0, 1)
            layers.append((PL, AL))
        for PL, AL in layers:                            # shadows first (contact 70 %, soft cast to the right 30 %)
            out = shadows(out, AL, contact=0.7, cblur=3, cast=0.30, cast_dir=(0.35, -0.03), cast_blur=14, ao=0.25)
        for PL, AL in layers:
            Lp = lum(PL)[..., None]
            G = (Lp + (PL - Lp) * 0.83) * gains
            solid = AL > 0.5; xs_ = xx[solid]
            u = np.clip((xx - xs_.min()) / max(xs_.max() - xs_.min(), 1), 0, 1)
            G = G * (1.04 - 0.14 * u)[..., None]          # window light from the left
            body = (AL > 0.95) & ((PL.max(2) - PL.min(2)) < 0.05)
            top = G[body][lum(G)[body] >= np.percentile(lum(G)[body], 95)].mean(0)
            G = G * (np.array([0xC9, 0xC7, 0xC3]) / 255 / top)   # white plastic ~ product lit face (#C3BFB7) level
            out = comp_layer(out, np.clip(G, 0, 1), AL, blur=0.5)
        out = grain(out, 1200 + k, amp=0.004)
        im = Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8)).crop((180, 310, 1080, 1910))
        im.resize((OW, OH), Image.LANCZOS).save(os.path.join(IMG, name))
        print('%s: %d filters, height %.0f px, base y %.0f, centres %s (1.2x crop as S11-1)' % (name, k, Hf, base_y, centers[:k]))
    frame(2, 'S11-2_alt.png')
    frame(3, 'S11-3_alt.png')


def round3():
    """design round 3: S01 v2 (tray contact 60 %), S02 v2 (cabinet warm spill -600 K / -0.3 EV), S11-2 v3, S11-3 v3."""
    big = np.asarray(Image.open(os.path.join(IMG, 'S01v2_fridgefix.png')).convert('RGB')).astype(np.float64) / 255
    plate = np.asarray(Image.fromarray((big * 255 + 0.5).astype(np.uint8)).resize((OW, OH), Image.LANCZOS)) / 255.0
    k = OW / 1536.0
    s, tx, ty = bbox_tf('2', 126 * k, 1372 * k, 1479 * k)
    PL, AL = place('2', s, tx, ty)

    def tray_contact(pl, op):
        cx, cy = s * 265 + tx, s * 926 + ty                       # tray bottom of official (2)
        m = (((xx - cx) / (s * 118)) ** 2 + ((yy - cy) / 2.2) ** 2 <= 1).astype(float)
        m = gblur(m, 1.5); m /= max(m.max(), 1e-6)
        return pl * (1 - op * m[..., None])
    pl1 = shadows(plate, AL, contact=0.6, cblur=1.5, cast=0.18, cast_dir=(-0.2, 0.08), cast_blur=6, ao=0.25)
    pl1 = tray_contact(pl1, 0.60)
    G1 = grade(PL, AL, np.array([0xEC, 0xCE, 0xAA]) / 255, light='right', dodge=0.04, burn=0.10, sat=0.9, room=plate)
    save(grain(comp_layer(pl1, G1, AL, blur=0.7), 101), 'S01_comp_v2.png')
    # ---- S02 v2
    p2 = off_grade(plate)
    # warm spill on the upper cabinets / ceiling around the lamps: -600 K, -0.3 EV (soft mask on warmth)
    reg = np.zeros((OH, OW)); reg[int(870 * k):int(1240 * k), int(150 * k):int(1340 * k)] = 1
    reg[int(380 * k):int(870 * k), int(450 * k):int(1250 * k)] = 1
    reg = gblur(reg, 25)
    warm = np.clip(((p2[..., 0] - p2[..., 2]) - 0.035) / 0.05, 0, 1)
    warm = gblur(warm, 6) * reg
    sh = Image.new('L', (OW, OH), 0)                              # keep the pendant shade itself out of it
    ImageDraw.Draw(sh).rectangle([943 * k, 1030 * k, 1138 * k, 1165 * k], fill=255)
    warm *= 1 - gblur(np.asarray(sh) / 255.0, 2)
    wb = np.array([0.94, 1.0, 1.075]); wb = wb / wb.dot(LW)          # -600 K
    lin = p2 ** 2.2
    adj = np.clip(lin * wb * 2 ** -0.3, 0, 1) ** (1 / 2.2)
    p2v = p2 * (1 - warm[..., None]) + adj * warm[..., None]
    print('S02 v2 warm-spill mask mean %.3f; cabinet %s -> %s' % (warm.mean(), hx(p2[700:860, 300:900].mean((0, 1))),
                                                                  hx(p2v[700:860, 300:900].mean((0, 1)))))
    pl2 = shadows(p2v, AL, contact=0.6, cblur=1.5, cast=0.3, cast_dir=(-0.55, 0.05), cast_blur=8, ao=0.25)
    pl2 = tray_contact(pl2, 0.60)
    G2 = grade(PL, AL, np.array([0xF1, 0xE9, 0xDC]) / 255, light='right', dodge=0.10, burn=0.18, sat=0.92, room=p2v)
    save(grain(comp_layer(pl2, G2, AL, blur=0.7), 102), 'S02_comp_v2.png')
    # ---- S11-2 v3: filter 03 levitates straight up ~150 px (in the 1.2x crop) from its own spot
    os.environ['S11_ALT'] = '1'
    render = s10_s11()
    lift = int(round(150 / 1.2 / S4))                             # 150 crop px -> 125 frame px -> photo px
    out, _ = render(lift, None)
    # faint contact shadow left on the counter under the floating filter
    fx0 = S4 * F03[0] + T4[0]; fx1 = S4 * F03[2] + T4[0]; fyb = S4 * 880 + T4[1]
    cx = (fx0 + fx1) / 2
    m = (((xx - cx) / ((fx1 - fx0) * 0.5)) ** 2 + ((yy - fyb) / 7) ** 2 <= 1).astype(float)
    m = gblur(m, 10); m /= max(m.max(), 1e-6)
    Fl = np.clip(warp(np.roll(filter03_mask(), -lift, axis=0).astype(float), S4, *T4), 0, 1)
    out = out * (1 - 0.25 * (m * (1 - Fl))[..., None])
    out = grain(out, 1310, amp=0.004)

    def crop(a, name):
        im = Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8)).crop((180, 310, 1080, 1910))
        im.resize((OW, OH), Image.LANCZOS).save(os.path.join(IMG, name))
    crop(out, 'S11-2_v3.png')
    crop(load('S10_start_v5.png'), 'S11-3_v3.png')
    print('S11-2 v3: lift %d photo px = %.0f frame px = %.0f crop px' % (lift, lift * S4, lift * S4 * 1.2))


def round4():
    """S11-2 v4: filter lowered by 35 % of its height (clear gap under the sockets), tilted 3 deg,
    soft shadow on the counter right below (30 %, blur 15 px)."""
    global TILT
    TILT = 3.0
    os.environ['S11_ALT'] = '1'
    render = s10_s11()
    fh = F03[3] - F03[1]
    lift = int(round(150 / 1.2 / S4)) - int(round(0.35 * fh))
    out, _ = render(lift, None)
    fx0 = S4 * F03[0] + T4[0]; fx1 = S4 * F03[2] + T4[0]; fyb = S4 * 880 + T4[1]
    cx = (fx0 + fx1) / 2
    m = (((xx - cx) / ((fx1 - fx0) * 0.55)) ** 2 + ((yy - fyb) / 8) ** 2 <= 1).astype(float)
    m = gblur(m, 15); m /= max(m.max(), 1e-6)
    Fl = np.clip(warp(np.roll(filter03_mask(), -lift, axis=0).astype(float), S4, *T4), 0, 1)
    out = out * (1 - 0.30 * (m * (1 - Fl))[..., None])
    out = grain(out, 1410, amp=0.004)
    im = Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8)).crop((180, 310, 1080, 1910))
    im.resize((OW, OH), Image.LANCZOS).save(os.path.join(IMG, 'S11-2_v4.png'))
    print('S11-2 v4: lift %d photo px (%.0f frame px, %.0f crop px), tilt %.0f deg' % (lift, lift * S4, lift * S4 * 1.2, TILT))
    # S13-1 v2: right third exposure -5 %
    a = np.asarray(Image.open(os.path.join(IMG, 'S13-1_fix.png')).convert('RGB')).astype(np.float64) / 255
    H, W, _ = a.shape
    X = np.mgrid[0:H, 0:W][1]
    w = np.clip((X - 2 * W / 3 + 40) / 80, 0, 1)[..., None]
    lin = a ** 2.2
    b = (lin * (1 - 0.05 * w)) ** (1 / 2.2)
    Image.fromarray((np.clip(b, 0, 1) * 255 + 0.5).astype(np.uint8)).save(os.path.join(IMG, 'S13-1_v2.png'))
    print('S13-1 v2: right third -5 %% exposure (80 px feather at x %d)' % (2 * W // 3))


if __name__ == '__main__':
    if 'round4' in sys.argv:
        round4(); sys.exit()
    if 'round3' in sys.argv:
        round3(); sys.exit()
    if 's11alt' in sys.argv:
        s11_alt(); sys.exit()
    todo = sys.argv[1:] or ['s01', 's05', 's10', 'kf2']
    if 's01' in todo: s01_s02()
    if 's05' in todo: s05()
    if 's10' in todo: s10_s11()
    if 'kf2' in todo: kf2()
