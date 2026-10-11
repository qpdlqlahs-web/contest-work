# -*- coding: utf-8 -*-
"""
S18 start frame: re-plate official PPA-300 (1) (front) onto the AI scene img/S18scene_1.png
(made from img/S18_seed.png). Same procedure as comp_k1_v2.py --v3.
out: img/S18_start.png (1080x1920), img/S18_product_layer.png (RGBA, same coords)
"""
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from scipy.optimize import minimize

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from comp_k1 import cutout, gblur, lum
from comp_k1_v2 import warp, gradmag

DIR = os.path.join(HERE, '..', 'refs', 'assets', '02. 퓨리얼 유로체인저 직수정수기 PPA-300')
PHOTO = os.path.join(DIR, 'PPA-300 (1).jpg')
SCENE = os.path.join(HERE, 'img', 'S18scene_1.png')
V2 = '--v2' in sys.argv          # round 3: contact shadow 60 %/4 px under the base, window-side edge dodge 8 %
OUT = os.path.join(HERE, 'img', 'S18_start_v2.png' if V2 else 'S18_start.png')
OUT_LAYER = os.path.join(HERE, 'img', 'S18_product_layer_v2.png' if V2 else 'S18_product_layer.png')


def contact_band(solid, tol=7, down=4, up=2):
    """thin band under the lowest silhouette points (tray/feet that touch the counter)."""
    H, W = solid.shape
    has = solid.any(0)
    ybot = np.where(has, H - 1 - np.argmax(solid[::-1], 0), -1)
    gmax = ybot[has].max()
    m = np.zeros((H, W))
    for x in np.nonzero(has & (ybot >= gmax - tol))[0]:
        m[max(ybot[x] - up, 0):ybot[x] + down + 1, x] = 1
    return m
DBG = os.environ.get('KF1_DBG')
OW, OH = 1080, 1920
LIT_TARGET = np.array([0xF1, 0xE9, 0xDC]) / 255.0
CAP = np.array([0xF4, 0xEB, 0xDD]) / 255.0
COUNTER_TARGET = np.array([0x63, 0x5E, 0x58]) / 255.0    # ENV-1 counter mean (same as KF2BG_v3)


def main():
    scene = np.asarray(Image.open(SCENE).convert('RGB').resize((OW, OH), Image.LANCZOS)).astype(np.float64) / 255
    C, A = cutout(PHOTO)
    C = C / 255.0
    ys, xs = np.nonzero(A > 0.5)
    bx0, bx1, by0, by1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    S0 = 860.0 / (by1 - by0)                                   # seed: h 860, centre x 330, base y 1500
    T0 = (330 - (bx1 - bx0) * S0 / 2 - bx0 * S0, 1500 - 860 - by0 * S0)
    yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float64)

    # ---------------- 1. registration
    gs = gradmag(lum(scene))
    gp_src = gradmag(lum(C) * A + 0.58 * (1 - A))
    inner = ndi.binary_erosion(A > 0.5, iterations=4).astype(float)
    WIN = (120, 560, 560, 1580)
    gs_w = gs[WIN[1]:WIN[3], WIN[0]:WIN[2]]

    def score(p):
        s, tx, ty = p
        gp = warp(gp_src, s, tx, ty, win=WIN)
        m = warp(inner, s, tx, ty, order=0, win=WIN) > 0.5
        a, b = gp[m], gs_w[m]
        a = a - a.mean(); b = b - b.mean()
        return -(a * b).sum() / np.sqrt((a * a).sum() * (b * b).sum() + 1e-12)

    best = None
    for s in np.arange(S0 - 0.04, S0 + 0.0401, 0.01):
        for dx in range(-25, 26, 5):
            for dy in range(-30, 31, 5):
                p = (s, T0[0] + dx, T0[1] + dy)
                v = score(p)
                if best is None or v < best[0]:
                    best = (v, p)
    b0 = best[1]
    res = minimize(score, b0, method='Nelder-Mead', options=dict(xatol=0.02, fatol=1e-5, initial_simplex=[
        b0, (b0[0] + 0.004, b0[1], b0[2]), (b0[0], b0[1] + 2, b0[2]), (b0[0], b0[1], b0[2] + 2)]))
    s, tx, ty = res.x
    print('registration: s=%.4f tx=%.2f ty=%.2f NCC=%.4f (seed s=%.4f t=(%.1f,%.1f))' % (s, tx, ty, -res.fun, S0, *T0))
    gp = warp(gp_src, s, tx, ty)
    pts = {'lever_top': (141, 30), 'lever_mid': (141, 110), 'nozzle': (141, 240), 'badge': (141, 760),
           'tray_L': (40, 850), 'tray_R': (240, 850), 'arch_L': (20, 300), 'arch_R': (262, 300)}
    errs = {}
    for k, (px_, py_) in pts.items():
        px_ += bx0; py_ += by0
        cx, cy = int(s * px_ + tx), int(s * py_ + ty)
        r = 24
        a = gp[cy - r:cy + r, cx - r:cx + r]
        bestv, bd = -9, (0, 0)
        for dy in np.arange(-8, 8.01, 0.5):
            for dx in np.arange(-8, 8.01, 0.5):
                b = ndi.shift(gs[cy - r - 10:cy + r + 10, cx - r - 10:cx + r + 10], (-dy, -dx), order=1)[10:-10, 10:-10]
                aa, bb = a - a.mean(), b - b.mean()
                v = (aa * bb).sum() / np.sqrt((aa * aa).sum() * (bb * bb).sum() + 1e-12)
                if v > bestv:
                    bestv, bd = v, (dx, dy)
        errs[k] = (float(bd[0]), float(bd[1]), round(float(bestv), 2))
    print('local residual (dx,dy,ncc):', errs)

    AL = np.clip(warp(A, s, tx, ty), 0, 1)
    PL = np.clip(warp(C, s, tx, ty, order=3), 0, 1)
    solid = AL > 0.5

    # ---------------- 2. remove AI product outside the official matte (diffusion inpaint)
    ring = ndi.binary_dilation(solid, iterations=16) & ~ndi.binary_dilation(solid, iterations=1)
    far = ndi.binary_dilation(solid, iterations=34) & ~ndi.binary_dilation(solid, iterations=20)
    _, (iy, ix) = ndi.distance_transform_edt(~ndi.binary_erosion(solid, iterations=2), return_indices=True)
    _, (fy, fx) = ndi.distance_transform_edt(~far, return_indices=True)
    dp = np.linalg.norm(scene - scene[iy, ix], axis=2)
    db = np.linalg.norm(scene - gblur(scene, 2)[fy, fx], axis=2)
    spill = ring & (dp < db * 0.8) & (dp < 0.14)
    lab, _ = ndi.label(spill | ndi.binary_dilation(solid, iterations=1))
    keep = np.unique(lab[solid]); spill &= np.isin(lab, keep[keep > 0])
    fill = spill | (ndi.binary_dilation(solid, iterations=2) & (AL < 0.5))
    fill = ndi.binary_dilation(fill, iterations=1) & ~(AL > 0.98)
    concav = ndi.binary_closing(np.pad(solid, 130), structure=np.ones((1, 241)))[130:-130, 130:-130] & ~solid
    concav &= yy > (s * (by0 + 0.93 * (by1 - by0)) + ty)          # gaps between tray and feet only
    fill |= concav
    known = ~fill & ~solid
    work = scene.copy()
    for _ in range(400):
        est = gblur(work * known[..., None], 2.0) / np.maximum(gblur(known.astype(float), 2.0), 1e-6)[..., None]
        work = np.where(fill[..., None], est, work)
    plate = np.where(fill[..., None], work, scene)
    d_up = ndi.distance_transform_edt(~solid)
    tone = work * (0.22 + 0.78 * np.clip((d_up - 1) / 16, 0, 1))[..., None]
    gap = np.where(lum(scene)[..., None] < lum(tone)[..., None], scene, tone)   # keep AI contact shadow
    plate = np.where(concav[..., None], gap, plate)
    print('spill px:', int(spill.sum()), 'filled px:', int(fill.sum()))

    # ---------------- 3. counter top -> ENV-1 tone (#635E58), counter surface only
    back = 1290 + (xx - 0) * (1220 - 1290) / 1080
    front = 1530 + (1080 - xx) * (1920 - 1530) / (1080 - 430)
    ctr = np.clip((yy - back) / 8 + 0.5, 0, 1) * np.clip((front - yy) / 4 + 0.5, 0, 1)
    ref = (ctr > 0.99) & (yy > 1500) & ~ndi.binary_dilation(solid, iterations=40)
    cur = plate[ref].mean(0)
    gain = COUNTER_TARGET / cur
    lifted = plate * gain
    lifted = np.where(lifted > 0.85, 0.85 + 0.15 * (1 - np.exp(-(lifted - 0.85) / 0.15)), lifted)
    plate = plate * (1 - ctr[..., None]) + lifted * ctr[..., None]
    hx = lambda v: '#%02X%02X%02X' % tuple((np.clip(v, 0, 1) * 255).round().astype(int))
    print('counter ref', hx(cur), '->', hx(plate[ref].mean(0)), 'gain', gain.round(3))
    if V2:
        cb = gblur(contact_band(solid), 4)
        cb = cb / max(cb.max(), 1e-6)
        plate = plate * (1 - 0.60 * cb[..., None])

    # ---------------- 4. product grade: AI low-frequency light (heavily smoothed, AI material differs)
    w_in = ndi.binary_erosion(AL > 0.9, iterations=3).astype(float)
    sig = 28.0
    nbl = lambda img: gblur(img * w_in, sig) / np.maximum(gblur(w_in, sig), 1e-4)
    ratio_l = np.clip(nbl(lum(scene)) / np.maximum(nbl(lum(PL)), 1e-3), 0.7, 1.25)[..., None]
    G = PL * ratio_l
    rb = (PL[..., 0] - PL[..., 2]) * 255
    chrome = gblur(np.clip((9 - rb) / 6, 0, 1) * (AL > 0), 0.8)
    room = gblur(plate, 18)
    sl = np.where(room <= 0.5, G - (1 - 2 * room) * G * (1 - G), G + (2 * room - 1) * (np.sqrt(np.clip(G, 0, 1)) - G))
    spec = np.clip((lum(PL) - 0.93) / 0.05, 0, 1)[..., None]
    G = G * (1 - 0.3 * chrome[..., None] * (1 - spec)) + sl * 0.3 * chrome[..., None] * (1 - spec)
    Lg = lum(G)[..., None]
    G = Lg + (G - Lg) * 0.92                                       # saturation -8 %
    cream = (AL > 0.95) & (chrome < 0.1)
    top = G[cream][lum(G)[cream] >= np.percentile(lum(G)[cream], 95)].mean(0)
    G = G * (LIT_TARGET / top)
    if V2:
        xr = xx[solid].max(); xl = xx[solid].min(); pw = xr - xl
        wd = np.clip((xx - (xr - 0.15 * pw)) / (0.15 * pw), 0, 1) ** 1.5 * (AL > 0)
        G = G / (1 - 0.08 * wd[..., None])                              # dodge 8 % window side
    G = np.minimum(G, CAP)
    top_after = G[cream][lum(G)[cream] >= np.percentile(lum(G)[cream], 95)].mean(0)

    # ---------------- 5. composite, specks (upper-right third), grain once
    Gs = gblur(G, 0.5)
    a = AL[..., None]
    comp = Gs * a + plate * (1 - a)
    edge = np.clip(AL - ndi.grey_erosion(AL, size=(3, 3)), 0, 1)[..., None]
    comp = comp * (1 - 0.15 * edge) + gblur(plate, 3) * 0.15 * edge
    Lm = lum(comp)
    th = Lm - ndi.grey_opening(Lm, size=(9, 9))
    zone = (xx >= 720) & (yy <= 1100)
    specks = (th > 0.05) & (AL < 0.01) & zone & False      # no speck pass needed on S18 (stone tile texture)
    lab, n = ndi.label(specks)
    if n:
        sizes = ndi.sum(specks, lab, range(1, n + 1))
        small = ndi.binary_dilation(np.isin(lab, np.where(sizes <= 40)[0] + 1), iterations=2)
        medc = np.stack([ndi.median_filter(comp[..., c], size=11) for c in range(3)], -1)
        comp = np.where(small[..., None], medc, comp)
    rng = np.random.default_rng(1818)
    g = gblur(rng.normal(0, 1, (OH, OW)), 0.6) * 2.1
    amp = (0.004 + 0.004 * np.clip(1 - np.abs(lum(comp) - 0.5) / 0.5, 0, 1))[..., None]
    comp = np.clip(comp + g[..., None] * amp, 0, 1)
    Image.fromarray((comp * 255 + 0.5).astype(np.uint8)).save(OUT)
    Image.fromarray((np.dstack([np.clip(Gs, 0, 1), AL]) * 255 + 0.5).astype(np.uint8), 'RGBA').save(OUT_LAYER)
    ys_, xs_ = np.nonzero(solid)
    print('lit face top5%%: %s | specks %d | product bbox x %d-%d y %d-%d h %d' %
          (hx(top_after), n, xs_.min(), xs_.max(), ys_.min(), ys_.max(), ys_.max() - ys_.min() + 1))
    if DBG:
        ov = (scene * 255).astype(np.uint8).copy()
        ov[ndi.binary_dilation(solid) & ~solid] = [255, 0, 0]
        ov[spill] = [0, 255, 0]
        Image.fromarray(ov).save(os.path.join(DBG, 's18_overlay.png'))


if __name__ == '__main__':
    main()
