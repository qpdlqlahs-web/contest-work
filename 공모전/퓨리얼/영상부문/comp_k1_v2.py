# -*- coding: utf-8 -*-
"""
K1 start frame v2: re-plate the official product photo onto the AI scene (KF1scene_1.png).
scene  : img/KF1scene_1.png (1536x2752, generated from KF1_seed.png; AI redrew the product)
product: official PPA-300 (2).jpg via comp_k1.cutout() (clean matte, no grading), never mirrored
output : img/KF1_start_v2.png (1080x1920), img/KF1_product_layer_v2.png (RGBA, same coords)

Usage: python comp_k1_v2.py [--debug]
"""
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from scipy.optimize import minimize

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from comp_k1 import cutout, PHOTO_BBOX, gblur, lum   # same clean matte as v1

SCENE = os.path.join(HERE, 'img', 'KF1scene_1.png')
V3 = '--v3' in sys.argv          # design-team round 2: gap clean, contact+cast shadow, sat -8%, right-edge dodge
OUT = os.path.join(HERE, 'img', 'KF1_start_v3.png' if V3 else 'KF1_start_v2.png')
OUT_LAYER = os.path.join(HERE, 'img', 'KF1_product_layer_v3.png' if V3 else 'KF1_product_layer_v2.png')
DEBUG = '--debug' in sys.argv
DBG = os.environ.get('KF1_DBG', HERE)
OW, OH = 1080, 1920
LIT_TARGET = np.array([0xF1, 0xE9, 0xDC]) / 255.0
CAP = np.array([0xF4, 0xEB, 0xDD]) / 255.0

# seed placement (KF1_seed.png): product bbox 317..983 x 544..1375 -> photo scale ~0.983
S0 = 832.0 / (PHOTO_BBOX[3] - PHOTO_BBOX[1])
T0 = (317 - PHOTO_BBOX[0] * S0, 544 - PHOTO_BBOX[1] * S0)


def warp(img, s, tx, ty, order=1, cval=0.0, win=(0, 0, OW, OH)):
    """photo -> output: out = s*photo + t (uniform scale + translation only). win=(x0,y0,x1,y1)."""
    x0, y0, x1, y1 = win
    mat = np.array([1 / s, 1 / s])
    off = np.array([(y0 - ty) / s, (x0 - tx) / s])
    shp = (y1 - y0, x1 - x0)
    if img.ndim == 2:
        return ndi.affine_transform(img, mat, off, output_shape=shp, order=order, cval=cval)
    return np.stack([ndi.affine_transform(img[..., c], mat, off, output_shape=shp, order=order,
                                          cval=cval) for c in range(img.shape[2])], -1)


def gradmag(g, s=1.2):
    g = gblur(g, s)
    return np.hypot(ndi.sobel(g, 1), ndi.sobel(g, 0))


def main():
    scene = np.asarray(Image.open(SCENE).convert('RGB').resize((OW, OH), Image.LANCZOS)).astype(np.float64) / 255
    C, A = cutout()
    C = C / 255.0

    # ------------------------------------------------ 1. registration (gradient NCC, interior features)
    gs = gradmag(lum(scene))
    ph = lum(C) * A + 0.58 * (1 - A)                      # photo on neutral grey like the seed
    gp_src = gradmag(ph)
    inner = ndi.binary_erosion(A > 0.5, iterations=4).astype(float)
    region = None

    WIN = (260, 480, 1040, 1440)
    gs_w = gs[WIN[1]:WIN[3], WIN[0]:WIN[2]]

    def score(p):
        s, tx, ty = p
        gp = warp(gp_src, s, tx, ty, win=WIN)
        w = warp(inner, s, tx, ty, order=0, win=WIN)
        m = w > 0.5
        a, b = gp[m], gs_w[m]
        a = a - a.mean(); b = b - b.mean()
        return -(a * b).sum() / np.sqrt((a * a).sum() * (b * b).sum() + 1e-12)

    best = None
    for s in np.arange(S0 - 0.03, S0 + 0.0301, 0.01):
        for dx in range(-20, 21, 5):
            for dy in range(-20, 21, 5):
                p = (s, T0[0] + dx, T0[1] + dy)
                v = score(p)
                if best is None or v < best[0]:
                    best = (v, p)
    res = minimize(score, best[1], method='Nelder-Mead',
                   options=dict(xatol=0.02, fatol=1e-5, initial_simplex=[
                       best[1], (best[1][0] + 0.004, best[1][1], best[1][2]),
                       (best[1][0], best[1][1] + 2, best[1][2]), (best[1][0], best[1][1], best[1][2] + 2)]))
    s, tx, ty = res.x
    print('registration: s=%.4f tx=%.2f ty=%.2f  NCC=%.4f (grid %.4f)' % (s, tx, ty, -res.fun, -best[0]))

    # local residuals: patch-wise shift search on gradients (lever, badge, tray, feet, top-right, vents)
    gp = warp(gp_src, s, tx, ty)
    pts = {'lever': (190, 128), 'nozzle': (257, 320), 'badge': (330, 748), 'tray': (200, 840),
           'foot_L': (478, 880), 'foot_R': (778, 836), 'top_wave': (640, 100), 'vent_top': (735, 265),
           'door_handle': (462, 470), 'back_edge': (812, 500)}
    errs = {}
    for k, (px_, py_) in pts.items():
        cx, cy = int(s * px_ + tx), int(s * py_ + ty)
        r = 28
        a = gp[cy - r:cy + r, cx - r:cx + r]
        bestv, bd = -9, (0, 0)
        for dy in np.arange(-6, 6.01, 0.5):
            for dx in np.arange(-6, 6.01, 0.5):
                b = ndi.shift(gs[cy - r - 8:cy + r + 8, cx - r - 8:cx + r + 8], (-dy, -dx), order=1)[8:-8, 8:-8]
                aa, bb = a - a.mean(), b - b.mean()
                v = (aa * bb).sum() / np.sqrt((aa * aa).sum() * (bb * bb).sum() + 1e-12)
                if v > bestv:
                    bestv, bd = v, (dx, dy)
        errs[k] = (round(float(bd[0]), 1), round(float(bd[1]), 1), round(float(bestv), 2))
    print('local residual (dx,dy,ncc):', errs)

    # ------------------------------------------------ 2. warp clean layer
    AL = np.clip(warp(A, s, tx, ty, order=1), 0, 1)
    PL = np.clip(warp(C, s, tx, ty, order=3), 0, 1)
    yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float64)

    # ------------------------------------------------ 3. remove AI product outside the official matte
    # AI silhouette estimate: ring pixels that look like product (close to inner-edge product colour,
    # far from the background a bit further out). Fill those from the outside (diffusion inpaint).
    solid = AL > 0.5
    ring = ndi.binary_dilation(solid, iterations=14) & ~ndi.binary_dilation(solid, iterations=1)
    far = ndi.binary_dilation(solid, iterations=30) & ~ndi.binary_dilation(solid, iterations=18)
    _, (iy, ix) = ndi.distance_transform_edt(~ndi.binary_erosion(solid, iterations=2), return_indices=True)
    prod_col = scene[iy, ix]
    _, (fy, fx) = ndi.distance_transform_edt(~far, return_indices=True)
    bg_col = gblur(scene, 2)[fy, fx]
    dp = np.linalg.norm(scene - prod_col, axis=2)
    db = np.linalg.norm(scene - bg_col, axis=2)
    spill = ring & (dp < db * 0.8) & (dp < 0.12)
    # keep only spill connected to the matte boundary (not random background bits)
    lab, n = ndi.label(spill | ndi.binary_dilation(solid, iterations=1))
    keep = np.unique(lab[solid])
    spill = spill & np.isin(lab, keep[keep > 0])
    # always clean a 1-2px rim just outside the matte (AI edge antialiasing / halo)
    fill = spill | (ndi.binary_dilation(solid, iterations=2) & (AL < 0.5))
    fill = ndi.binary_dilation(fill, iterations=1) & ~(AL > 0.98)
    # under-base gaps (between tray/feet/body): keep the AI contact shadow, never lighten it
    concav = ndi.binary_closing(np.pad(solid, 130), structure=np.ones((1, 241 if V3 else 81)))[130:-130, 130:-130] & ~solid
    concav &= yy > (s * 780 + ty)
    fill = fill | concav
    known = ~fill & ~(AL > 0.5)
    work = scene.copy()
    for it in range(400):                                    # diffusion fill from known neighbours
        bl = gblur(work * known[..., None], 2.0)
        wt = gblur(known.astype(float), 2.0)[..., None]
        est = bl / np.maximum(wt, 1e-6)
        work = np.where(fill[..., None], est, work)
    # add back a little texture/grain-free; grain is added globally at the end
    plate = np.where(fill[..., None], work, scene)
    # gap tone: darker toward the body underside; min() keeps AI shadow, removes AI cream body
    d_up = ndi.distance_transform_edt(~solid)
    f = ((0.22 + 0.78 * np.clip((d_up - 1) / 16, 0, 1)) if V3 else
         (0.38 + 0.62 * np.clip((d_up - 1) / 14, 0, 1)))[..., None]     # v3: no pale smear beside feet
    tone = work * f
    gap = np.where(lum(scene)[..., None] < lum(tone)[..., None], scene, tone)
    plate = np.where(concav[..., None], gap, plate)
    print('spill px removed:', int(spill.sum()), ' rim px:', int(fill.sum()))
    if V3:
        # contact band under tray and feet: 65 %, blur 4 px
        P = lambda px_, py_: (s * px_ + tx, s * py_ + ty)
        cmask = np.zeros((OH, OW))
        for (px_, py_, rx, ry) in [(265, 926, 114, 7), (478, 909, 22, 5.5), (778, 855, 22, 5.5)]:
            cx, cy = P(px_, py_)
            cmask = np.maximum(cmask, (((xx - cx) / (rx * s)) ** 2 + ((yy - cy) / ry) ** 2 <= 1).astype(float))
        cmask = np.maximum(cmask, concav.astype(float))
        cmask = gblur(cmask, 4)
        plate = plate * (1 - 0.65 * cmask[..., None])
        # cast shadow toward screen left-front (window light from the right): 35 %, blur 30 px
        pts_ = [P(250, 925), P(480, 906), P(780, 852)]
        gx = np.array([p[0] for p in pts_]); gy = np.array([p[1] for p in pts_])
        ground = np.interp(np.arange(OW), gx, gy)
        ys_, xs_ = np.nonzero(AL[::2, ::2] > 0.4); ys_ = ys_ * 2; xs_ = xs_ * 2
        h = np.clip(ground[xs_] - ys_, 0, None)
        txs = np.round(xs_ - 0.45 * h).astype(int); tys = np.round(ground[xs_] + 0.08 * h).astype(int)
        k = (txs >= 0) & (txs < OW) & (tys >= 0) & (tys < OH)
        cast = np.zeros((OH, OW)); np.add.at(cast, (tys[k], txs[k]), 1.0)
        cast = gblur(np.clip(ndi.grey_dilation(cast, size=(5, 5)), 0, 1), 30)
        cast = np.clip(cast / max(cast.max(), 1e-6) * 1.15, 0, 1)
        # only on the peninsula counter top (left edge (445,1210)->(10,1480), front edge (0,1485)->(700,1450))
        left_ln = 1210 + (xx - 445) * (1480 - 1210) / (10 - 445)
        left_ln = np.where(xx > 445, 1150, left_ln)
        front_ln = 1485 + xx * (1450 - 1485) / 700
        ctop = np.clip((yy - left_ln) / 3 + 0.5, 0, 1) * np.clip((front_ln - yy) / 3 + 0.5, 0, 1)
        plate = plate * (1 - 0.35 * (cast * ctop)[..., None])

    # ------------------------------------------------ 4. light/colour from the AI render (low frequency only)
    w_in = ndi.binary_erosion(AL > 0.9, iterations=3).astype(float)
    sig = 10.0
    def nblur(img):
        return gblur(img * w_in[..., None], sig) / np.maximum(gblur(w_in, sig), 1e-4)[..., None]
    lo_scene = nblur(scene)
    lo_photo = nblur(PL)
    ratio = lo_scene / np.maximum(lo_photo, 1e-3)
    ratio_l = (lum(lo_scene) / np.maximum(lum(lo_photo), 1e-3))[..., None]
    # mostly luminance shading, a little of the AI colour cast
    ratio = ratio_l * (1 + 0.5 * (ratio / np.maximum(ratio_l, 1e-3) - 1))
    # chrome & badge: keep official detail but take shading only softly (their low-freq is unreliable)
    rb = (PL[..., 0] - PL[..., 2]) * 255
    chrome = np.clip((9 - rb) / 6, 0, 1) * (AL > 0)
    chrome = gblur(chrome, 0.8)
    ratio = ratio * (1 - 0.5 * chrome[..., None]) + np.clip(ratio_l, 0.5, 1.2) * 0.5 * chrome[..., None]
    G = PL * ratio
    # chrome: replace white-studio reflection with room (soft light of blurred plate), keep speculars
    room = gblur(plate, 18)
    sl = np.where(room <= 0.5, G - (1 - 2 * room) * G * (1 - G), G + (2 * room - 1) * (np.sqrt(np.clip(G, 0, 1)) - G))
    spec = np.clip((lum(PL) - 0.93) / 0.05, 0, 1)[..., None]
    G = G * (1 - 0.3 * chrome[..., None] * (1 - spec)) + sl * 0.3 * chrome[..., None] * (1 - spec)
    # tone: lit face (top 5% of cream, non-chrome) -> #F1E9DC, curve keeps shadows
    cream = (AL > 0.95) & (chrome < 0.1)
    Lc = lum(G)[cream]
    top = G[cream][Lc >= np.percentile(Lc, 95)].mean(0)
    gain = LIT_TARGET / np.maximum(top, 1e-3)
    G = G * gain
    if V3:
        Lg = lum(G)[..., None]
        G = Lg + (G - Lg) * 0.92                                      # product saturation -8 %
        top = G[cream][lum(G)[cream] >= np.percentile(lum(G)[cream], 95)].mean(0)
        G = G * (LIT_TARGET / np.maximum(top, 1e-3))                  # lit face back on #F1E9DC
        pr_ = s * PHOTO_BBOX[2] + tx; pw_ = s * (PHOTO_BBOX[2] - PHOTO_BBOX[0])
        wd = np.clip((xx - (pr_ - 0.12 * pw_)) / (0.12 * pw_), 0, 1) ** 1.5 * (AL > 0)
        G = G / (1 - 0.10 * wd[..., None])                           # dodge 10 % on the window-side edge
    G = np.minimum(G, CAP)
    # badge rectangle: official pixels with the local shading only (no colour games)
    bx0, by0 = s * 290 + tx, s * 728 + ty
    bx1, by1 = s * 370 + tx, s * 770 + ty
    badge = (xx >= bx0) & (xx <= bx1) & (yy >= by0) & (yy <= by1)
    G[badge] = np.clip(PL[badge] * ratio_l[badge] * gain.mean(), 0, 1)

    # ------------------------------------------------ 5. acuity match + composite
    Gs = gblur(G, 0.5)
    a = AL[..., None]
    comp = Gs * a + plate * (1 - a)
    edge = np.clip(AL - ndi.grey_erosion(AL, size=(3, 3)), 0, 1)[..., None]
    comp = comp * (1 - 0.15 * edge) + gblur(plate, 3) * 0.15 * edge      # 1px light wrap

    # ------------------------------------------------ 6. white speck cleanup (upper-right wall + anywhere outside product)
    Lm = lum(comp)
    zone = (xx >= 560) & (yy <= 1200)                         # upper-right wall / window side only
    th = Lm - ndi.grey_opening(Lm, size=(9, 9))               # white top-hat: small bright dots
    specks = (th > 0.05) & (AL < 0.01) & zone
    lab, n = ndi.label(specks)
    sizes = ndi.sum(specks, lab, range(1, n + 1))
    small = np.isin(lab, np.where(sizes <= 40)[0] + 1)
    small = ndi.binary_dilation(small, iterations=2) & (AL < 0.01)
    medc = np.stack([ndi.median_filter(comp[..., c], size=11) for c in range(3)], -1)
    comp = np.where(small[..., None], medc, comp)
    print('specks removed:', int(n if n else 0), 'components, px', int(small.sum()))

    # ------------------------------------------------ 7. grain once, whole frame
    rng = np.random.default_rng(6060)
    g = gblur(rng.normal(0, 1, (OH, OW)), 0.6) * 2.1             # unit-std fine grain
    Lc2 = lum(comp)[..., None]
    amp = (0.004 + 0.004 * np.clip(1 - np.abs(Lc2[..., 0] - 0.5) / 0.5, 0, 1))[..., None]   # ~1-2/255 like the clean AI plate
    comp = np.clip(comp + g[..., None] * amp, 0, 1)

    Image.fromarray((comp * 255 + 0.5).astype(np.uint8)).save(OUT)
    Image.fromarray((np.dstack([np.clip(Gs, 0, 1), AL]) * 255 + 0.5).astype(np.uint8), 'RGBA').save(OUT_LAYER)
    top_after = G[cream][lum(G)[cream] >= np.percentile(lum(G)[cream], 95)].mean(0)
    print('lit face top5%%: #%02X%02X%02X' % tuple((top_after * 255).round().astype(int)))
    ys_, xs_ = np.nonzero(AL > 0.5)
    print('product bbox x %d-%d y %d-%d (h %d)' % (xs_.min(), xs_.max(), ys_.min(), ys_.max(), ys_.max() - ys_.min()))
    print('nozzle', (round(s * 257 + tx), round(s * 330 + ty)), 'tray top', (round(s * 260 + tx), round(s * 820 + ty)))
    if DEBUG:
        ov = (scene * 255).astype(np.uint8).copy()
        e = (ndi.binary_dilation(solid, iterations=1) & ~solid)
        ov[e] = [255, 0, 0]
        ov[spill] = (ov[spill] * 0.5 + np.array([0, 255, 0]) * 0.5).astype(np.uint8)
        Image.fromarray(ov).save(os.path.join(DBG, 'kf1v2_overlay.png'))


if __name__ == '__main__':
    main()
