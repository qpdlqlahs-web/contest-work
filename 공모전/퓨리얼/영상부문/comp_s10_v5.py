# -*- coding: utf-8 -*-
"""
S10 start frame: re-plate official PPA-300 (3) (door side, closed) onto img/S10scene2_1.png
(made from img/S10_seed.png: (3) at scale 0.853, x358-1060, y812-1400). Same procedure as comp_s18.py.
Also registers official (4) (door open) onto (3) so cuts 10-2 / 11-1~3 can reuse the same coordinates.
out: img/S10_start.png, img/S10_product_layer.png (RGBA), prints the (3)/(4) -> frame transforms
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
from comp_s18 import contact_band

DIR = os.path.join(HERE, '..', 'refs', 'assets', '02. 퓨리얼 유로체인저 직수정수기 PPA-300')
PHOTO = os.path.join(DIR, 'PPA-300 (3).jpg')
PHOTO4 = os.path.join(DIR, 'PPA-300 (4).jpg')
SCENE = os.path.join(HERE, 'img', 'S10scene2_1.png')
OUT = os.path.join(HERE, 'img', 'S10_start_v5.png')
OUT_LAYER = os.path.join(HERE, 'img', 'S10_product_layer_v5.png')
DBG = os.environ.get('KF1_DBG')
OW, OH = 1080, 1920
LIT_TARGET = np.array([0xC3, 0xBF, 0xB8]) / 255.0      # v4 lit face (scene-matched)
CAP = np.array([0xC8, 0xC4, 0xBD]) / 255.0
COUNTER_TARGET = np.array([0x63, 0x5E, 0x58]) / 255.0    # ENV-1 counter mean (same as KF2BG_v3)


def main():
    scene = np.asarray(Image.open(SCENE).convert('RGB').resize((OW, OH), Image.LANCZOS)).astype(np.float64) / 255
    C, A = cutout(PHOTO)
    C = C / 255.0
    ys, xs = np.nonzero(A > 0.5)
    bx0, bx1, by0, by1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    S0 = 0.6664                                                # seed v2: frame = 0.6664*photo + (454.15, 764.77)
    T0 = (454.15, 764.77)
    yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float64)

    # ---------------- 1. registration
    gs = gradmag(lum(scene))
    gp_src = gradmag(lum(C) * A + 0.58 * (1 - A))
    inner = ndi.binary_erosion(A > 0.5, iterations=4).astype(float)
    WIN = (470, 840, 1080, 1380)
    gs_w = gs[WIN[1]:WIN[3], WIN[0]:WIN[2]]

    def score(p):
        s, tx, ty = p
        gp = warp(gp_src, s, tx, ty, win=WIN)
        m = warp(inner, s, tx, ty, order=0, win=WIN) > 0.5
        a, b = gp[m], gs_w[m]
        a = a - a.mean(); b = b - b.mean()
        return -(a * b).sum() / np.sqrt((a * a).sum() * (b * b).sum() + 1e-12)

    best = None
    for s in np.arange(S0 - 0.02, S0 + 0.0201, 0.005):
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
    pts = {'lever': (30, 50), 'nozzle': (80, 160), 'tray': (60, 600), 'foot_L': (230, 655), 'foot_R': (660, 655),
           'vent_top': (600, 140), 'vent_bot': (600, 490), 'handle': (215, 310), 'top_R': (720, 10)}
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
    concav &= yy > (s * (by0 + 0.86 * (by1 - by0)) + ty)          # gaps between tray and feet only
    fill |= concav
    dad = xx < 440                                               # Dad's face/body/hands: keep AI pixels
    fill &= ~dad
    print('dad/product overlap px:', int((solid & dad).sum()))
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

    # ---------------- 3. counter top -> same tone as S10 v4 (#635E58 family, sat -50 %), top surface only
    ctr = np.clip((xx - 452) / 4 + 0.5, 0, 1) * np.clip((yy - 1336) / 4 + 0.5, 0, 1) * np.clip((1508 - yy) / 4 + 0.5, 0, 1)
    ref = (ctr > 0.99) & (yy > 1395) & ~ndi.binary_dilation(solid, iterations=20)
    cur = plate[ref].mean(0)
    gain = COUNTER_TARGET / cur
    lw = np.array([0.2126, 0.7152, 0.0722])
    hue_only = gain / gain.dot(lw)
    hl = np.clip((lum(plate) - 0.32) / 0.25, 0, 1)[..., None]
    lifted = plate * (gain * (1 - hl) + hue_only * hl)
    Ll = lum(lifted)[..., None]
    lifted = Ll + (lifted - Ll) * 0.5
    plate = plate * (1 - ctr[..., None]) + lifted * ctr[..., None]
    hx = lambda v: '#%02X%02X%02X' % tuple((np.clip(v, 0, 1) * 255).round().astype(int))
    print('counter ref', hx(cur), '->', hx(plate[ref].mean(0)))
    # shadows: underside band #2E2B28 55 % (14 px, blur 10), tray contact 75 %, feet contact 70 % (4 px blur)
    has = solid.any(0)
    ybot = np.where(has, OH - 1 - np.argmax(solid[::-1], 0), -1)
    gl0 = ybot[has].max(); xs_s = np.nonzero(has)[0]
    band = ((yy >= gl0 - 7) & (yy <= gl0 + 6) & (xx >= xs_s.min() + 10) & (xx <= xs_s.max() - 10)).astype(float)
    band = gblur(band, 10); band /= max(band.max(), 1e-6)
    col = np.array([0x2E, 0x2B, 0x28]) / 255.0
    plate = plate * (1 - 0.55 * band[..., None]) + col * 0.55 * band[..., None]
    cb = contact_band(solid, tol=8, down=4, up=2)
    tray_x = s * (bx0 + 0.30 * (bx1 - bx0)) + tx                    # tray = front 30 % of the side view
    cbt = gblur(cb * (xx < tray_x), 4); cbf = gblur(cb * (xx >= tray_x), 4)
    cbt /= max(cbt.max(), 1e-6); cbf /= max(cbf.max(), 1e-6)
    plate = plate * (1 - 0.75 * cbt[..., None]) * (1 - 0.70 * cbf[..., None])

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
    G = Lg + (G - Lg) * 0.83                                       # saturation like v4 (-8 % then -10 %)
    cream = (AL > 0.95) & (chrome < 0.1)
    top = G[cream][lum(G)[cream] >= np.percentile(lum(G)[cream], 95)].mean(0)
    G = np.minimum(G * (LIT_TARGET / top), CAP)
    top_after = G[cream][lum(G)[cream] >= np.percentile(lum(G)[cream], 95)].mean(0)

    # ---------------- 5. composite, specks (upper-right third), grain once
    Gs = gblur(G, 0.5)
    a = AL[..., None]
    comp = Gs * a + plate * (1 - a)
    edge = np.clip(AL - ndi.grey_erosion(AL, size=(3, 3)), 0, 1)[..., None]
    comp = comp * (1 - 0.15 * edge) + gblur(plate, 3) * 0.15 * edge
    Lm = lum(comp)
    th = Lm - ndi.grey_opening(Lm, size=(9, 9))
    zone = (xx >= 2000)
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
    # ---------------- 6. official (4) -> (3) photo registration (body features, door/filter excluded)
    C4, A4 = cutout(PHOTO4)
    g3 = gradmag(lum(C) * A + 1 - A); g4 = gradmag(lum(C4 / 255.0) * A4 + 1 - A4)
    py, px = np.mgrid[0:1000, 0:1000]
    reg = (((px < 275) & (py > 180) & (py < 410)) | ((px < 275) & (py > 750) & (py < 880)) |
           ((px > 270) & (px < 890) & (py > 165) & (py < 262)) | ((px > 735) & (px < 805) & (py > 790) & (py < 875)))

    def sc4(p):
        k, ox, oy = p                                         # (4) coords = k * (3) coords + o
        mat = np.array([k, k]); off = np.array([oy, ox])
        w = ndi.affine_transform(g4, mat, off, output_shape=(1000, 1000), order=1)
        a_, b_ = w[reg], g3[reg]
        a_ = a_ - a_.mean(); b_ = b_ - b_.mean()
        return -(a_ * b_).sum() / np.sqrt((a_ * a_).sum() * (b_ * b_).sum() + 1e-12)
    bb = None
    for k in np.arange(0.97, 1.031, 0.01):
        for ox in range(-30, 31, 3):
            for oy in range(-30, 31, 3):
                v = sc4((k, ox, oy))
                if bb is None or v < bb[0]:
                    bb = (v, (k, ox, oy))
    r4 = minimize(sc4, bb[1], method='Nelder-Mead', options=dict(xatol=0.02, fatol=1e-6))
    k, ox, oy = r4.x
    # frame = s*(3) + t ;  (3) = ((4) - o) / k  ->  frame = (s/k)*(4) + (t - s*o/k)
    s4 = s / k; t4 = (tx - s * ox / k, ty - s * oy / k)
    print('(3)->frame: scale %.4f offset (%.2f, %.2f)' % (s, tx, ty))
    print('(4)->(3): (4) = %.4f*(3) + (%.2f, %.2f), NCC %.3f' % (k, ox, oy, -r4.fun))
    print('(4)->frame: scale %.4f offset (%.2f, %.2f)' % (s4, *t4))
    # head/product ratio helper
    print('product height px: %.1f' % (s * (by1 - by0)))
    if DBG:
        A4w = np.clip(warp(A4, s4, *t4), 0, 1); C4w = np.clip(warp(C4 / 255.0, s4, *t4), 0, 1)
        Image.fromarray(((C4w * A4w[..., None] + comp * (1 - A4w[..., None])) * 255).astype(np.uint8)).save(os.path.join(DBG, 's10_p4_check.png'))
        ov = (scene * 255).astype(np.uint8).copy()
        ov[ndi.binary_dilation(solid) & ~solid] = [255, 0, 0]
        ov[spill] = [0, 255, 0]
        Image.fromarray(ov).save(os.path.join(DBG, 's10_overlay.png'))


if __name__ == '__main__':
    main()
