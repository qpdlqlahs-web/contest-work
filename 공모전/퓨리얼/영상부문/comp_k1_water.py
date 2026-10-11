# -*- coding: utf-8 -*-
"""
K1 final start frame (guide 4-6 step 3, re-plate after the water edit).
in : img/KF1water_1.png (AI edit of KF1_start_v3: glass + stream), img/KF1_start_v3.png, img/KF1_product_layer_v3.png
out: img/KF1_final_start.png (1080x1920, Kling K1 start frame)
Method: the approved v3 frame (official product layer) everywhere, except the glass + stream patch taken from
the AI edit after aligning it to v3 (AI output is ~0.8 % stretched horizontally). This removes the AI's
badge loss, dial letters and ghost glass by construction. The badge part seen through the glass is restored
at reduced opacity.
"""
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from comp_k1 import gblur, lum

IMG = os.path.join(HERE, 'img')
OW, OH = 1080, 1920
DBG = os.environ.get('KF1_DBG')
V2 = '--v2' in sys.argv          # round 5: official badge 75 % inside the glass + badge overlay export


def gm(x):
    x = ndi.gaussian_filter(x, 1.2)
    return np.hypot(ndi.sobel(x, 0), ndi.sobel(x, 1))


def patch_shift(ga, gb, r):
    x0, y0, x1, y1 = r
    B = gb[y0:y1, x0:x1]; bv, bd = -9, (0, 0)
    for dy in np.arange(-6, 6.01, 0.5):
        for dx in np.arange(-6, 6.01, 0.5):
            A = ndi.shift(ga[y0 - 8:y1 + 8, x0 - 8:x1 + 8], (-dy, -dx), order=1)[8:-8, 8:-8]
            aa, bb = A - A.mean(), B - B.mean()
            v = (aa * bb).sum() / np.sqrt((aa * aa).sum() * (bb * bb).sum() + 1e-12)
            if v > bv:
                bv, bd = v, (dx, dy)
    return bd, bv


def main():
    ai = np.asarray(Image.open(os.path.join(IMG, 'KF1water_1.png')).convert('RGB')
                    .resize((OW, OH), Image.LANCZOS)).astype(np.float64) / 255
    v3 = np.asarray(Image.open(os.path.join(IMG, 'KF1_start_v3.png')).convert('RGB')).astype(np.float64) / 255
    lay = np.asarray(Image.open(os.path.join(IMG, 'KF1_product_layer_v3.png'))).astype(np.float64) / 255
    AL = lay[..., 3]
    yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float64)

    # ---------------- 1. align AI edit to v3 (x' = ax*x + bx, y' = ay*y + by), patches away from the glass
    ga, gb = gm(lum(ai)), gm(lum(v3))
    patches = [(80, 1100, 260, 1300), (100, 200, 400, 500), (560, 860, 700, 920), (860, 1290, 960, 1360),
               (650, 1100, 720, 1200), (870, 950, 960, 1000), (700, 300, 1000, 600), (60, 1500, 400, 1700),
               (600, 1450, 1000, 1650)]
    X, Y, DX, DY, Wt = [], [], [], [], []
    for r in patches:
        (dx, dy), v = patch_shift(ga, gb, r)
        if v > 0.5:
            X.append((r[0] + r[2]) / 2); Y.append((r[1] + r[3]) / 2); DX.append(dx); DY.append(dy); Wt.append(v)
    X, Y, DX, DY, Wt = map(np.array, (X, Y, DX, DY, Wt))
    Ax = np.stack([X, np.ones_like(X)], 1) * Wt[:, None]
    kx, cx = np.linalg.lstsq(Ax, DX * Wt, rcond=None)[0]
    Ay = np.stack([Y, np.ones_like(Y)], 1) * Wt[:, None]
    ky, cy = np.linalg.lstsq(Ay, DY * Wt, rcond=None)[0]
    res = np.sqrt(np.mean((DX - (kx * X + cx)) ** 2 + (DY - (ky * Y + cy)) ** 2))
    print('AI->v3 align: x shift = %.4f*x %+.2f, y shift = %.4f*y %+.2f (fit rms %.2f px, %d patches)'
          % (kx, cx, ky, cy, res, len(X)))
    # AI pixel for v3 coord (x,y) is at (x + kx*x + cx, y + ky*y + cy)
    mat = np.array([1 + ky, 1 + kx]); off = np.array([cy, cx])
    aia = np.stack([ndi.affine_transform(ai[..., c], mat, off, order=3, mode='nearest') for c in range(3)], -1)
    aia = np.clip(aia, 0, 1)

    # ---------------- 2. keep masks: stream + glass (+ its contact on the tray)
    d = gblur(np.abs(aia - v3).mean(2), 1.0)
    # stream: thin bright column below the nozzle
    noz_bot = 800
    st = (d > 0.06) & (xx > 405) & (xx < 460) & (yy > noz_bot - 15) & (yy < 1170)
    lab, n = ndi.label(st)
    if n:
        sz = ndi.sum(st, lab, range(1, n + 1)); st = lab == (np.argmax(sz) + 1)
    st = ndi.binary_dilation(st, iterations=2)
    st &= ~((AL > 0.5) & (yy < noz_bot + 2))                    # stream starts under the official nozzle
    # glass: bbox of changes in the glass zone, filled rounded rectangle
    gz = (d > 0.05) & (xx > 350) & (xx < 520) & (yy > 1020) & (yy < 1305)
    cols = np.where(gz.sum(0) > 25)[0]; rows = np.where(gz.sum(1) > 20)[0]
    gx0, gx1, gy0, gy1 = cols.min(), cols.max(), rows.min(), rows.max()
    gx1 = min(gx1, 513)                                        # the ghost glass starts right of the real one
    rr = 10
    gl = ((xx >= gx0) & (xx <= gx1) & (yy >= gy0) & (yy <= gy1)).astype(float)
    gl = ndi.binary_dilation(gl > 0, iterations=2)
    print('glass bbox x %d-%d y %d-%d; stream px %d' % (gx0, gx1, gy0, gy1, st.sum()))
    keep = np.clip(gblur((gl | st).astype(float), 1.2) * 1.3, 0, 1)
    keep = np.maximum(keep, (gl | st) * 1.0)

    # close the small gap between the official nozzle bottom and the stream top (stream leaves the nozzle)
    core = (d > 0.10) & st & (yy < 1000)
    sc = np.where(core.any(0))[0]
    if len(sc):
        y_t = int(np.nonzero(core.any(1))[0].min())
        sc = np.where(core[y_t:y_t + 6].any(0))[0]
        nozcol = AL[:y_t, sc.min():sc.max() + 1] > 0.5
        y_n = int(np.nonzero(nozcol.any(1))[0].max()) if nozcol.any() else y_t
        if 0 < y_t - y_n <= 15:
            src_rows = aia[y_t + 1:y_t + 4, sc.min() - 2:sc.max() + 3].mean(0)
            for y in range(y_n + 1, y_t + 1):
                aia[y, sc.min() - 2:sc.max() + 3] = src_rows
            st[y_n + 1:y_t + 1, sc.min() - 2:sc.max() + 3] = True
            keep = np.maximum(keep, st * 1.0)
        print('stream top y %d, nozzle bottom y %d' % (y_t, y_n))

    # ---------------- 3. compose: v3 + AI patch, badge seen through the glass at reduced opacity
    out = v3 * (1 - keep[..., None]) + aia * keep[..., None]
    bx0, bx1, by0, by1 = 465, 545, 1180, 1228
    badge_reg = (xx >= bx0) & (xx <= bx1) & (yy >= by0) & (yy <= by1)
    bmask = gblur((badge_reg & (AL > 0.5)).astype(float), 1.0)
    if V2:
        # official badge plate (dark rounded plate + letters) from the v3 frame, 75 % / blur 1 px inside the glass
        plate_m = (badge_reg & (lum(v3) < 0.42))
        plate_m = ndi.binary_closing(plate_m, iterations=3)
        plate_m = ndi.binary_fill_holes(plate_m)
        lab, n = ndi.label(plate_m)
        if n:
            sz = ndi.sum(plate_m, lab, range(1, n + 1)); plate_m = lab == (np.argmax(sz) + 1)
        plate_m = ndi.binary_dilation(plate_m, iterations=2)
        bm = np.clip(gblur(plate_m.astype(float), 0.8), 0, 1)
        thru = gblur(v3, 1.0)
        alpha = bm * (0.75 * keep + 1.0 * (1 - keep))
        out = out * (1 - alpha[..., None]) + thru * alpha[..., None]
        ov = np.dstack([np.where(bm[..., None] > 0, thru, 0), alpha])
        Image.fromarray((ov * 255 + 0.5).astype(np.uint8), 'RGBA').save(os.path.join(IMG, 'KF1_badge_overlay.png'))
        ys_, xs_ = np.nonzero(bm > 0.5)
        print('badge overlay: x %d-%d y %d-%d, alpha 0.75 in glass / 1.0 outside' % (xs_.min(), xs_.max(), ys_.min(), ys_.max()))
    else:
        bdark = np.clip((0.45 - lum(v3)) / 0.3, 0, 1) * bmask           # only the dark badge plate/letters
        thru = gblur(v3, 0.8)
        t = 0.55 * bdark * keep
        out = out * (1 - t[..., None]) + thru * t[..., None]

    # grain only on the AI patch (v3 already carries the frame grain)
    rng = np.random.default_rng(66)
    g = gblur(rng.normal(0, 1, (OH, OW)), 0.6) * 2.1
    amp = (0.004 + 0.004 * np.clip(1 - np.abs(lum(out) - 0.5) / 0.5, 0, 1))[..., None]
    out = np.clip(out + g[..., None] * amp * keep[..., None], 0, 1)
    Image.fromarray((out * 255 + 0.5).astype(np.uint8)).save(os.path.join(IMG, 'KF1_final_start_v2.png' if V2 else 'KF1_final_start.png'))
    if DBG:
        Image.fromarray((keep * 255).astype(np.uint8)).save(os.path.join(DBG, 'kw_keep.png'))


if __name__ == '__main__':
    main()
