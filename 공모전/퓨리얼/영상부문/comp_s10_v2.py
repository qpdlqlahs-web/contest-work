# -*- coding: utf-8 -*-
"""
S10 v2 (design round 3): product scaled to 0.78x of the seed size (head:product ~ 1:1.5),
base line raised by 3 % of frame height, right (back) edge kept at x 1060.
The AI product left uncovered is removed with exemplar block inpainting (patch quilting).
Product: colour temp -300 K, exposure -8 %, sat -8 %; contact shadow 70 % / 4 px; cast shadow right-back 30 %.
Counter: lifted to the #635E58 family, then saturation -50 % (no pink cast).
out: img/S10_start_v2.png, img/S10_product_layer_v2.png ; prints (3)/(4) -> frame transforms
"""
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from scipy.signal import fftconvolve

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from comp_k1 import cutout, gblur, lum
from comp_k1_v2 import warp
from comp_s18 import contact_band

DIR = os.path.join(HERE, '..', 'refs', 'assets', '02. 퓨리얼 유로체인저 직수정수기 PPA-300')
PHOTO = os.path.join(DIR, 'PPA-300 (3).jpg')
SCENE = os.path.join(HERE, 'img', 'S10scene_1.png')
V4 = '--v4' in sys.argv     # round 5 (on top of v3): underside band #2E2B28 55 %/14 px/blur 10, base contact 75 %,
                            #   product sat -10 % and exposure -8 % relative to v3
V3 = '--v3' in sys.argv or V4   # round 4: window-side dodge 10 % / far-end burn 15 %, -5 % EV, underside band 40 %
TAG = 'v4' if V4 else ('v3' if V3 else 'v2')
OUT = os.path.join(HERE, 'img', 'S10_start_%s.png' % TAG)
OUT_LAYER = os.path.join(HERE, 'img', 'S10_product_layer_%s.png' % TAG)
DBG = os.environ.get('KF1_DBG')
OW, OH = 1080, 1920
LIT_TARGET = np.array([0xF1, 0xE9, 0xDC]) / 255.0
CAP = np.array([0xF4, 0xEB, 0xDD]) / 255.0
COUNTER_TARGET = np.array([0x63, 0x5E, 0x58]) / 255.0
# v1 registration of official (3) to the AI product (comp_s10.py): frame = s*photo + t
S_OLD, T_OLD = 0.8543, (282.93, 659.23)
SCALE = 0.78
RAISE = 0.03 * OH
K43, O43 = 0.9916, (0.00, 3.03)          # (4) = K43*(3) + O43  (photo coords, from comp_s10.py)


def axis_fill(img, hole, known, w_v=1.0, w_h=1.0, avg=3):
    """Fill hole pixels from the nearest known pixels along the 4 axis directions (inverse-square
    distance weights). Keeps vertical/horizontal background structure better than isotropic diffusion."""
    H, W, _ = img.shape
    src = gblur(img, 1.0)
    out = img.copy()
    acc = np.zeros_like(img); wsum = np.zeros((H, W))
    idx_y = np.arange(H)[:, None] * np.ones((1, W), int)
    idx_x = np.ones((H, 1), int) * np.arange(W)[None, :]
    for axis, wt in ((0, w_v), (1, w_h)):
        for rev in (False, True):
            k = known if not rev else (known[::-1] if axis == 0 else known[:, ::-1])
            ii = idx_y if axis == 0 else idx_x
            pos = np.where(k, ii, -1)
            last = np.maximum.accumulate(pos, axis=axis)
            if rev:
                last = (H - 1 - last if axis == 0 else W - 1 - last)
                last = last[::-1] if axis == 0 else last[:, ::-1]
                last = np.where((last >= (H if axis == 0 else W)) , -1, last)
            ok = (last >= 0) & ((last <= (H - 1)) if axis == 0 else (last <= (W - 1)))
            # entries where no known pixel exists in that direction
            if rev:
                ok &= (np.flip(np.maximum.accumulate(np.flip(np.where(known, 1, 0), axis), axis), axis) > 0)
            else:
                ok &= (np.maximum.accumulate(np.where(known, 1, 0), axis) > 0)
            lc = np.clip(last, 0, (H - 1) if axis == 0 else (W - 1))
            d = np.abs((idx_y if axis == 0 else idx_x) - lc).astype(float) + 1
            val = src[lc, idx_x] if axis == 0 else src[idx_y, lc]
            w = np.where(ok & hole, wt / d ** 2, 0)
            acc += val * w[..., None]; wsum += w
    fill = acc / np.maximum(wsum, 1e-12)[..., None]
    out[hole] = fill[hole]
    return out


def pushpull(I, W):
    """push-pull (pyramid) interpolation of I from pixels where W is True."""
    if W.all() or min(W.shape) < 4:
        if not W.any():
            return np.zeros_like(I) + 0.0
        return np.where(W[..., None], I, I[W].mean(0))
    H, Wd = W.shape
    h2, w2 = (H + 1) // 2, (Wd + 1) // 2
    Ip = np.zeros((h2 * 2, w2 * 2, 3)); Wp = np.zeros((h2 * 2, w2 * 2))
    Ip[:H, :Wd] = I * W[..., None]; Wp[:H, :Wd] = W
    Is = Ip.reshape(h2, 2, w2, 2, 3).sum((1, 3)); Ws = Wp.reshape(h2, 2, w2, 2).sum((1, 3))
    Ic = np.where(Ws[..., None] > 0, Is / np.maximum(Ws, 1e-9)[..., None], 0)
    coarse = pushpull(Ic, Ws > 0)
    up = ndi.zoom(coarse, (2, 2, 1), order=1)[:H, :Wd]
    return np.where(W[..., None], I, up)


def clone_fill(img, hole, dy, dx=0, feather=6):
    src = ndi.shift(img, (-dy, -dx, 0), order=1, mode='nearest')
    m = gblur(hole.astype(float), feather / 3)
    m = np.maximum(m, hole)
    return img * (1 - m[..., None]) + src * m[..., None]


def main():
    scene = np.asarray(Image.open(SCENE).convert('RGB').resize((OW, OH), Image.LANCZOS)).astype(np.float64) / 255
    C, A = cutout(PHOTO); C = C / 255.0
    ys, xs = np.nonzero(A > 0.5)
    bx0, bx1, by0, by1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float64)

    # ---------------- old (AI) product footprint
    AL0 = np.clip(warp(A, S_OLD, *T_OLD), 0, 1)
    solid0 = AL0 > 0.5
    ring = ndi.binary_dilation(solid0, iterations=16) & ~ndi.binary_dilation(solid0, iterations=1)
    far = ndi.binary_dilation(solid0, iterations=34) & ~ndi.binary_dilation(solid0, iterations=20)
    _, (iy, ix) = ndi.distance_transform_edt(~ndi.binary_erosion(solid0, iterations=2), return_indices=True)
    _, (fy, fx) = ndi.distance_transform_edt(~far, return_indices=True)
    dp = np.linalg.norm(scene - scene[iy, ix], axis=2)
    db = np.linalg.norm(scene - gblur(scene, 2)[fy, fx], axis=2)
    spill = ring & (dp < db * 0.8) & (dp < 0.14)
    lab, _ = ndi.label(spill | ndi.binary_dilation(solid0, iterations=1))
    keep = np.unique(lab[solid0]); spill &= np.isin(lab, keep[keep > 0])
    old = ndi.binary_dilation(solid0 | spill, iterations=3)
    # old AI contact shadows / reflections under tray & feet (they belong to the big product)
    old |= (yy > T_OLD[1] + S_OLD * by1 - 30) & (yy < T_OLD[1] + S_OLD * by1 + 230) & \
           (xx > T_OLD[0] + S_OLD * bx0 - 10) & (xx < T_OLD[0] + S_OLD * bx1 + 10)

    # ---------------- new placement: 0.78x, right edge kept, base raised 3 %
    s = S_OLD * SCALE
    right = T_OLD[0] + S_OLD * bx1
    base = T_OLD[1] + S_OLD * by1 - RAISE
    tx, ty = right - s * bx1, base - s * by1
    AL = np.clip(warp(A, s, tx, ty), 0, 1)
    PL = np.clip(warp(C, s, tx, ty, order=3), 0, 1)
    solid = AL > 0.5
    dad = ((xx < 352) & (yy < 1300)) | (xx < 290)                   # Dad's head/torso & hands
    hole = old & ~(AL > 0.98) & ~dad
    valid = ~old & ~ndi.binary_dilation(solid, iterations=2) & ~dad
    print('new: s=%.4f t=(%.2f, %.2f)  hole px=%d' % (s, tx, ty, hole.sum()))

    # ---------------- inpaint the uncovered AI product
    # counter part (below the counter/back line): vertical clone of counter texture from in front
    ctr_line = 1335.0
    h_ctr = hole & (yy >= ctr_line)
    h_bg = hole & (yy < ctr_line)
    known = ~hole & ~ndi.binary_dilation(solid, iterations=2) & ~dad
    plate = axis_fill(scene, h_bg, known, w_v=1.0, w_h=1.0)
    # counter: low frequency by push-pull from the surrounding clean counter (removes the old product's
    # sheen/reflection); native granite texture kept where the AI drew counter, cloned where it drew product
    old_body = ndi.binary_dilation(solid0 | spill, iterations=3)
    old_body |= (yy > T_OLD[1] + S_OLD * by1 - 40) & (yy < T_OLD[1] + S_OLD * by1 + 95) &                 (xx > T_OLD[0] + S_OLD * bx0 - 30) & (xx < T_OLD[0] + S_OLD * bx1 + 10)   # contact/feet streaks
    counter_area = (yy >= ctr_line) & (xx >= 292)
    kc = counter_area & ~h_ctr & ~ndi.binary_dilation(solid, iterations=3) & ~dad
    lowf = gblur(pushpull(gblur(scene, 3), kc), 10)
    hf_native = scene - gblur(scene, 5)
    tex = ndi.shift(scene, (-260, 0, 0), order=1, mode='nearest'); hf_clone = tex - gblur(tex, 5)
    hf = np.where(old_body[..., None], hf_clone, hf_native)
    cm = np.maximum(gblur(h_ctr.astype(float), 4), h_ctr)[..., None]
    plate = plate * (1 - cm) + (lowf + hf) * cm
    rng0 = np.random.default_rng(77)
    nz = gblur(rng0.normal(0, 1, (OH, OW)), 0.7)[..., None] * 0.012
    plate = np.where(h_bg[..., None], plate + nz, plate)               # re-grain the smooth fill
    print('inpaint px: background %d (axis fill), counter %d (clone)' % (h_bg.sum(), h_ctr.sum()))

    # ---------------- counter: lift to #635E58 family, then saturation -50 %
    left_edge = 335 - (yy - 1000) * 0.14
    left_edge = np.where(yy < 1150, np.maximum(left_edge, 354), left_edge + 8)
    top_lim = 1372 - RAISE
    bx_ = np.clip((xx - 380) / 40, 0, 1)                              # smooth blend, no seam at x 400
    wy = np.clip((yy - 1150) / 190, 0, 1) * (1 - bx_) + np.clip((yy - top_lim) / 6 + 0.5, 0, 1) * bx_
    ctr = np.clip((xx - left_edge) / 3 + 0.5, 0, 1) * wy
    ref = (ctr > 0.99) & (yy > 1480) & ~ndi.binary_dilation(solid, iterations=30)
    cur = plate[ref].mean(0)
    gain = COUNTER_TARGET / cur
    lw = np.array([0.2126, 0.7152, 0.0722])
    hue_only = gain / gain.dot(lw)
    hl = np.clip((lum(plate) - 0.32) / 0.25, 0, 1)[..., None]
    lifted = plate * (gain * (1 - hl) + hue_only * hl)
    lifted = np.where(lifted > 0.85, 0.85 + 0.15 * (1 - np.exp(-(lifted - 0.85) / 0.15)), lifted)
    Ll = lum(lifted)[..., None]
    lifted = Ll + (lifted - Ll) * 0.5                                  # saturation -50 %
    plate = plate * (1 - ctr[..., None]) + lifted * ctr[..., None]
    hx = lambda v: '#%02X%02X%02X' % tuple((np.clip(v, 0, 1) * 255).round().astype(int))
    print('counter ref', hx(cur), '->', hx(plate[ref].mean(0)))

    # ---------------- shadows: contact 70 % / 4 px, cast right-back 30 %
    cb = gblur(contact_band(solid, tol=8, down=4, up=2), 4); cb /= max(cb.max(), 1e-6)
    has = solid.any(0)
    ybot = np.where(has, OH - 1 - np.argmax(solid[::-1], 0), -1).astype(float)
    gap = ndi.binary_closing(np.pad(solid, 130), structure=np.ones((1, 241)))[130:-130, 130:-130] & ~solid
    gap &= yy > ty + s * (by0 + 0.86 * (by1 - by0))
    cb = np.maximum(cb, gblur(gap.astype(float), 2) * 0.9)
    plate = plate * (1 - (0.75 if V4 else 0.70) * cb[..., None])
    if V3:   # soft occlusion band under the body between tray and feet: 40 %, blur 12 px
        gl0 = ybot[has].max()
        xs_s = np.nonzero(has)[0]
        if V4:   # dark band under the body: #2E2B28, 55 %, 14 px tall, blur 10 px (normal blend)
            band = ((yy >= gl0 - 7) & (yy <= gl0 + 6) & (xx >= xs_s.min() + 10) & (xx <= xs_s.max() - 10)).astype(float)
            band = gblur(band, 10); band /= max(band.max(), 1e-6)
            col = np.array([0x2E, 0x2B, 0x28]) / 255.0
            plate = plate * (1 - 0.55 * band[..., None]) + col * 0.55 * band[..., None]
        else:
            band = ((yy >= gl0 - 6) & (yy <= gl0 + 5) & (xx >= xs_s.min() + 10) & (xx <= xs_s.max() - 10)).astype(float)
            band = gblur(band, 12); band /= max(band.max(), 1e-6)
            plate = plate * (1 - 0.40 * band[..., None])
    gl = ybot[has].max()
    ys_, xs_ = np.nonzero(solid[::2, ::2]); ys_ *= 2; xs_ *= 2
    h = np.clip(gl - ys_, 0, None)
    txs = np.round(xs_ + 0.40 * h).astype(int); tys = np.round(gl - 0.10 * h).astype(int)
    k = (txs >= 0) & (txs < OW) & (tys >= 0) & (tys < OH)
    cast = np.zeros((OH, OW)); np.add.at(cast, (tys[k], txs[k]), 1.0)
    cast = gblur(np.clip(ndi.grey_dilation(cast, size=(5, 5)), 0, 1), 20)
    cast = np.clip(cast / max(cast.max(), 1e-6) * 1.15, 0, 1) * np.clip((yy - (gl - 70)) / 10, 0, 1)
    plate = plate * (1 - 0.30 * cast[..., None])

    # faint reflection of the new product on the semi-gloss counter (AI scene had one for the old product)
    gl_ = ybot[has].max()
    fl = np.zeros((OH, OW)); fc = np.zeros((OH, OW, 3))
    hgt = int(gl_ - (ty + s * by0)) + 2
    src_a = AL[int(gl_) - hgt:int(gl_)][::-1]; src_c = PL[int(gl_) - hgt:int(gl_)][::-1]
    fl[int(gl_):int(gl_) + hgt] = src_a; fc[int(gl_):int(gl_) + hgt] = src_c
    fade = np.clip(1 - (yy - gl_) / 140, 0, 1) * (yy > gl_)
    fl = gblur(fl * fade, 6); fc = gblur(fc, 6)
    plate = plate * (1 - 0.07 * fl[..., None]) + fc * 0.07 * fl[..., None]

    # ---------------- product grade: AI low-freq light (from the old placement, re-mapped), -300 K, -8 % EV
    w_in = ndi.binary_erosion(AL0 > 0.9, iterations=3).astype(float)
    PL0 = np.clip(warp(C, S_OLD, *T_OLD, order=1), 0, 1)
    nbl = lambda im: gblur(im * w_in, 28) / np.maximum(gblur(w_in, 28), 1e-4)
    R0 = np.clip(nbl(lum(scene)) / np.maximum(nbl(lum(PL0)), 1e-3), 0.7, 1.25)
    m = S_OLD / s                                   # new frame q -> old frame: m*(q - t_new) + t_old
    R = ndi.affine_transform(R0, [m, m], [T_OLD[1] - m * ty, T_OLD[0] - m * tx], output_shape=(OH, OW),
                             order=1, mode='nearest')[..., None]
    G = PL * R
    rb = (PL[..., 0] - PL[..., 2]) * 255
    chrome = gblur(np.clip((9 - rb) / 6, 0, 1) * (AL > 0), 0.8)
    room = gblur(plate, 18)
    sl = np.where(room <= 0.5, G - (1 - 2 * room) * G * (1 - G), G + (2 * room - 1) * (np.sqrt(np.clip(G, 0, 1)) - G))
    spec = np.clip((lum(PL) - 0.93) / 0.05, 0, 1)[..., None]
    G = G * (1 - 0.3 * chrome[..., None] * (1 - spec)) + sl * 0.3 * chrome[..., None] * (1 - spec)
    Lg = lum(G)[..., None]
    G = Lg + (G - Lg) * 0.92                                         # sat -8 %
    cream = (AL > 0.95) & (chrome < 0.1)
    top = G[cream][lum(G)[cream] >= np.percentile(lum(G)[cream], 95)].mean(0)
    G = np.minimum(G * (LIT_TARGET / top), CAP)
    wb = np.array([0.968, 1.0, 1.04]); wb = wb / wb.dot(lw)          # -300 K (cooler), luminance-neutral
    G = np.clip(G ** 2.2 * wb, 0, 1) ** (1 / 2.2)
    G = G * 0.92                                                     # exposure -8 %
    if V3:   # window light from the left (nozzle side): dodge 10 % left, burn 15 % toward the far right end
        xl_, xr_ = xx[solid].min(), xx[solid].max()
        u = np.clip((xx - xl_) / (xr_ - xl_), 0, 1)
        dodge = np.clip((0.35 - u) / 0.35, 0, 1) ** 1.2
        burn = np.clip((u - 0.55) / 0.45, 0, 1) ** 1.3
        G = G / (1 - 0.10 * dodge[..., None])
        G = G * (1 - 0.15 * burn[..., None])
        G = np.minimum(G * 0.95, CAP)                                    # exposure -5 %
    if V4:
        Lg4 = lum(G)[..., None]
        G = (Lg4 + (G - Lg4) * 0.90) * 0.92                              # sat -10 %, exposure -8 % (vs v3)
    top_after = G[cream][lum(G)[cream] >= np.percentile(lum(G)[cream], 95)].mean(0)

    # ---------------- composite + grain once
    Gs = gblur(G, 0.5)
    a = AL[..., None]
    comp = Gs * a + plate * (1 - a)
    edge = np.clip(AL - ndi.grey_erosion(AL, size=(3, 3)), 0, 1)[..., None]
    comp = comp * (1 - 0.15 * edge) + gblur(plate, 3) * 0.15 * edge
    rng = np.random.default_rng(1010)
    g = gblur(rng.normal(0, 1, (OH, OW)), 0.6) * 2.1
    amp = (0.004 + 0.004 * np.clip(1 - np.abs(lum(comp) - 0.5) / 0.5, 0, 1))[..., None]
    comp = np.clip(comp + g[..., None] * amp, 0, 1)
    Image.fromarray((comp * 255 + 0.5).astype(np.uint8)).save(OUT)
    Image.fromarray((np.dstack([np.clip(Gs, 0, 1), AL]) * 255 + 0.5).astype(np.uint8), 'RGBA').save(OUT_LAYER)

    ys_, xs_ = np.nonzero(solid)
    s4 = s / K43; t4 = (tx - s * O43[0] / K43, ty - s * O43[1] / K43)
    print('lit face top5%%: %s | product bbox x %d-%d y %d-%d (w %d = %.1f%%, h %d)' % (
        hx(top_after), xs_.min(), xs_.max(), ys_.min(), ys_.max(), xs_.max() - xs_.min() + 1,
        100 * (xs_.max() - xs_.min() + 1) / OW, ys_.max() - ys_.min() + 1))
    print('nozzle (photo 182,390) -> y %.0f' % (ty + s * 390))
    print('(3)->frame: scale %.4f offset (%.2f, %.2f)' % (s, tx, ty))
    print('(4)->frame: scale %.4f offset (%.2f, %.2f)' % (s4, *t4))
    if DBG:
        Image.fromarray((hole * 255).astype(np.uint8)).save(os.path.join(DBG, 's10v2_hole.png'))


if __name__ == '__main__':
    main()
