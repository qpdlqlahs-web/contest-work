# -*- coding: utf-8 -*-
"""
K1 hero start frame composite (A' 정전 점검의 아침, cut 6)
plate  : img/KF1BG_1.png (1536x2752)
product: refs/assets/02. .../PPA-300 (2).jpg  (3/4 view, guide 4-2) - never mirrored
output : img/KF1_start.png (1080x1920)
         img/KF1_product_layer.png (RGBA product layer, same coords, for re-plating in 4-6 step 3)

Usage: python comp_k1.py [--zoom 1.5]
"""
import sys, os
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
PLATE = os.path.join(HERE, 'img', 'KF1BG_1.png')
PROD = os.path.join(HERE, '..', 'refs', 'assets', '02. 퓨리얼 유로체인저 직수정수기 PPA-300', 'PPA-300 (2).jpg')
OUT = os.path.join(HERE, 'img', 'KF1_start.png')
OUT_LAYER = os.path.join(HERE, 'img', 'KF1_product_layer.png')

OW, OH = 1080, 1920
ZOOM = 1.5                      # plate -> output magnification (cap 1.5)
if '--zoom' in sys.argv:
    ZOOM = float(sys.argv[sys.argv.index('--zoom') + 1])
    OUT = OUT.replace('.png', '_z%.2f.png' % ZOOM)
    OUT_LAYER = OUT_LAYER.replace('.png', '_z%.2f.png' % ZOOM)

# ---------------------------------------------------------------- scale
# Plate scale at the backsplash: counter->upper-cabinet gap (guide 60 cm) = 665 px at x~950
#   -> 1.11 px/mm on the wall plane. Product stands 10-25 cm in front of the wall -> ~1.19 px/mm.
#   340 mm * 1.19 = 405 px.  Cross-check: faucet (assumed 30 cm) measures ~355 px -> ratio 1.14 (34/30=1.13).
PROD_H_PLATE = 405.0
PHOTO_BBOX = (139, 78, 817, 925)          # product bbox in official photo (x0,y0,x1,y1), 847 px tall
S_PLATE = PROD_H_PLATE / (PHOTO_BBOX[3] - PHOTO_BBOX[1])
# anchor: near-side rear foot (photo 780,852) sits on counter at plate (1060,1600), back end ~ at L-corner
ANCHOR_PHOTO = (780, 852)
ANCHOR_PLATE = (1060, 1580)   # ~9 cm in front of the wall junction; far-side rear ~1-3 cm from tiles

# ---------------------------------------------------------------- crop (plate coords)
CW, CH = OW / ZOOM, OH / ZOOM
prod_cx = ANCHOR_PLATE[0] + ((PHOTO_BBOX[0] + PHOTO_BBOX[2]) / 2 - ANCHOR_PHOTO[0]) * S_PLATE
prod_cy = ANCHOR_PLATE[1] + ((PHOTO_BBOX[1] + PHOTO_BBOX[3]) / 2 - ANCHOR_PHOTO[1]) * S_PLATE
CX0 = round(prod_cx - 0.635 * CW)         # product centre on the right third
CY0 = round(prod_cy - 0.60 * CH)
CROP = (CX0, CY0, CX0 + CW, CY0 + CH)


def to_out(xp, yp):
    return (xp - CX0) * ZOOM, (yp - CY0) * ZOOM


def lum(a):
    return a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722


def gblur(a, s):
    if a.ndim == 2:
        return ndi.gaussian_filter(a, s)
    return np.stack([ndi.gaussian_filter(a[..., c], s) for c in range(a.shape[2])], -1)


def softlight(a, b):
    return np.where(b <= 0.5, a - (1 - 2 * b) * a * (1 - a), a + (2 * b - 1) * (np.sqrt(a) - a))


# ================================================================ 1. matte (white bg)
def cutout(path=None):
    P = np.asarray(Image.open(path or PROD).convert("RGB")).astype(np.float64)
    d = (255 - P).max(2)
    near_white = d <= 5
    lab, _ = ndi.label(near_white)
    border = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, border[border > 0])
    fg = ~bg                                 # interior specular (#FBFBFD) stays: not border-connected
    fg = ndi.binary_fill_holes(fg)
    # soft edge: alpha from colour distance to white vs nearest interior colour
    inner = ndi.binary_erosion(fg, iterations=3)
    _, (iy, ix) = ndi.distance_transform_edt(~inner, return_indices=True)
    F = P[iy, ix]
    W = np.full_like(P, 255.0)
    num = ((W - P) * (W - F)).sum(2)
    den = ((W - F) ** 2).sum(2)
    a_est = np.clip(num / np.maximum(den, 1e-6), 0, 1)
    band = ndi.binary_dilation(fg, iterations=2) & ~ndi.binary_erosion(fg, iterations=2)
    alpha = fg.astype(np.float64)
    ok = band & (den > 400)                  # reliable where interior colour is not near white
    alpha[ok] = a_est[ok]
    alpha[band & ~ok & ~fg] = 0
    alpha = np.clip(alpha, 0, 1)
    # tiny 0.6px feather (~1px at full photo res) and kill isolated specks
    alpha = gblur(alpha, 0.6)
    alpha[alpha < 0.02] = 0
    # defringe: un-premultiply white
    a3 = alpha[..., None]
    C = np.where(a3 > 0.05, (P - (1 - a3) * W) / np.maximum(a3, 1e-3), F)
    C = np.where(band[..., None], np.clip(C, 0, 255), P)
    C = np.where((alpha > 0)[..., None] & band[..., None], np.minimum(C, F + 25), C)  # no white rim
    return np.clip(C, 0, 255), alpha


def main():
    plate = Image.open(PLATE).convert('RGB')
    # ------------------------------------------------ 2. crop + upscale plate
    crop = plate.crop(tuple(round(v) for v in CROP)).resize((OW, OH), Image.LANCZOS)
    crop = crop.filter(ImageFilter.UnsharpMask(radius=2, percent=35, threshold=2))
    BG = np.asarray(crop).astype(np.float64) / 255.0

    # ------------------------------------------------ 3. product layer at output res
    C, A = cutout()
    s = S_PLATE * ZOOM
    x0, y0, x1, y1 = PHOTO_BBOX
    pad = 6
    sub = (x0 - pad, y0 - pad, x1 + pad, y1 + pad)
    Cimg = Image.fromarray(C.astype(np.uint8)).crop(sub)
    Aimg = Image.fromarray((A * 255).astype(np.uint8)).crop(sub)
    nw, nh = round(Cimg.width * s), round(Cimg.height * s)
    Cimg = Cimg.resize((nw, nh), Image.LANCZOS)
    Aimg = Aimg.resize((nw, nh), Image.LANCZOS)
    ox, oy = to_out(ANCHOR_PLATE[0] - (ANCHOR_PHOTO[0] - sub[0]) * S_PLATE,
                    ANCHOR_PLATE[1] - (ANCHOR_PHOTO[1] - sub[1]) * S_PLATE)
    ox, oy = round(ox), round(oy)

    def photo_to_out(px, py):
        return ox + (px - sub[0]) * s, oy + (py - sub[1]) * s

    PL = np.zeros((OH, OW, 3)); AL = np.zeros((OH, OW))
    PL[oy:oy + nh, ox:ox + nw] = np.asarray(Cimg) / 255.0
    AL[oy:oy + nh, ox:ox + nw] = np.asarray(Aimg) / 255.0
    yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float64)

    # badge rectangle (left untouched by reflections / grading tricks)
    bx0, by0 = photo_to_out(290, 728); bx1, by1 = photo_to_out(370, 770)
    badge = (xx >= bx0) & (xx <= bx1) & (yy >= by0) & (yy <= by1)

    # chrome mask: neutral pixels (cream has R-B ~ 15-30)
    rb = (PL[..., 0] - PL[..., 2]) * 255
    chrome = np.clip((9 - rb) / 6, 0, 1) * (AL > 0)
    chrome = gblur(chrome, 0.7) * (AL > 0)
    chrome[badge] = 0

    # ------------------------------------------------ 4. grade product (OFF, 5600K sun from ESE, above)
    # light travels NW and down (from the wall beam diagonal ~45 deg): south-facing door side = key,
    # top = 3/4 key, west-facing front column (nozzle front, rib niche, tray) = ambient only.
    py, px = np.mgrid[0:1000, 0:1000].astype(np.float64)
    sh = np.ones((1000, 1000)) * 1.025                                  # door side / body (key)
    col = (px < 395)
    sh[col] = 0.80                                                      # front column (side strip, tray)
    niche = (px >= 262) & (px < 395) & (py > 285) & (py < 835)
    sh[niche] = 0.66                                                    # rib niche faces west
    head = (px < 395) & (py < 300)
    sh[head] = (0.70 + 0.30 * np.clip((px - 190) / 200, 0, 1))[head]   # rounded nozzle head front->side
    sh *= 1.0 - 0.12 * np.clip((py - 790) / 110, 0, 1)                 # underside roll-off
    sh *= 1.0 - 0.07 * np.clip((py - 200) / 600, 0, 1) * (px >= 395)    # door face: sun from above
    sh *= 1.0 - 0.06 * np.clip((140 - py) / 60, 0, 1) * (px >= 395)    # wave tops slightly under key
    sh = gblur(sh, 3.0)
    shI = Image.fromarray(np.clip(sh / 1.2 * 255, 0, 255).astype(np.uint8)).crop(sub).resize((nw, nh), Image.BILINEAR)
    shade = np.ones((OH, OW))
    shade[oy:oy + nh, ox:ox + nw] = np.asarray(shI) / 255.0 * 1.2
    pl, pr = photo_to_out(x0, 0)[0], photo_to_out(x1, 0)[0]
    pt, pb = photo_to_out(0, y0)[1], photo_to_out(0, y1)[1]
    u = np.clip((xx - pl) / (pr - pl), 0, 1)          # 0 = front/left, 1 = back/right (window side)
    v = np.clip((yy - pt) / (pb - pt), 0, 1)          # 0 = top, 1 = base
    G = PL * shade[..., None]
    # chrome: kill white-studio reflection -> room reflection (soft light 32%) + darken, keep speculars
    room = gblur(BG, 20)
    ch_new = softlight(G, room) * 0.82
    spec = np.clip((lum(PL) - 0.93) / 0.05, 0, 1)[..., None]
    ch_new = ch_new * (1 - spec) + G * spec
    G = G * (1 - 0.9 * chrome[..., None]) + (0.32 * ch_new + 0.68 * G * 0.86) * (0.9 * chrome[..., None])
    # window-side rim: thin warm-white edge along right/top silhouette
    edge = np.clip(AL - ndi.grey_erosion(AL, size=(5, 5)), 0, 1)
    rim = edge * np.clip((u - 0.55) / 0.45, 0, 1) * (1 - chrome)
    G = G + rim[..., None] * 0.06 * np.array([1.0, 0.98, 0.94])
    # never brighter than scene highlight #F4EBDD
    G = np.minimum(G, np.array([0xF4, 0xEB, 0xDD]) / 255.0)
    G[badge] = np.minimum(PL[badge] * shade[badge][..., None], 1)

    # ------------------------------------------------ 5. shadows on plate
    out = BG.copy()
    L = lum(BG)
    litness = np.clip((L - 0.30) / 0.35, 0, 1)
    # ground line through official contact points (tray bottom, near feet)
    pts = [photo_to_out(250, 925), photo_to_out(480, 906), photo_to_out(780, 852)]
    gx = np.array([p[0] for p in pts]); gy = np.array([p[1] for p in pts])
    ground = np.interp(np.arange(OW), gx, gy)
    colmask = (AL > 0.5)
    ybot = np.where(colmask.any(0), OH - 1 - np.argmax(colmask[::-1], 0), -1).astype(np.float64)

    # (a) contact/occlusion: under the body down to the ground line + small dark band
    occ = np.zeros((OH, OW))
    has = ybot > 0
    top_band = np.where(has, np.minimum(ybot, ground) - 4, 0)
    occ += ((yy >= top_band[None, :]) & (yy <= ground[None, :] + 3) & has[None, :]).astype(float)
    occ = gblur(occ, 2.5)
    # feet points (darker)
    for fx, fy in [(480, 906), (780, 852), (250, 925)]:
        cx, cy = photo_to_out(fx, fy)
        occ += 0.9 * np.exp(-(((xx - cx) / 14) ** 2 + ((yy - cy - 2) / 4.5) ** 2))
    occ = np.clip(occ, 0, 1)
    out = out * (1 - 0.68 * occ[..., None])

    # (b) soft AO halo on counter around base (sky/fill occlusion)
    halo = np.zeros((OH, OW))
    halo[((yy >= (ground - 18)[None, :]) & (yy <= (ground + 10)[None, :]) &
          (xx >= gx[0] - 40) & (xx <= gx[-1] + 50))] = 1
    halo = gblur(halo, 14)
    out = out * (1 - 0.30 * halo[..., None])

    # (c)+(d) cast shadow, ray-cast with a simple light model.
    #   light travel dir (world): west 0.50, north(to wall) 0.707, down 0.50  (wall beam diagonal ~45 deg)
    #   d(x): distance of the silhouette column from the north wall (cm): front/left ~19, back/right ~4
    PXCM = 17.0                     # output px per cm at product depth (1.19 px/mm plate * zoom)
    WALLCM = 16.7                   # output px per cm on the wall plane
    DEPTHCM = 2.5                   # output px per cm of counter depth (foreshortened)
    jx0, jy0 = to_out(600, 1597); jx1, jy1 = to_out(1100, 1560)
    jslope = (jy1 - jy0) / (jx1 - jx0)
    junction = jy0 + (xx - jx0) * jslope
    jline = lambda x: jy0 + (x - jx0) * jslope
    sil = (AL > 0.4)
    ys_, xs_ = np.nonzero(sil)
    gnd = ground[xs_]
    d_cm = np.maximum((gnd - jline(xs_)) / DEPTHCM - 4.0, 1.0)   # near-side contact line minus half body
    h_cm = np.clip((gnd - ys_) / PXCM, 0, None)
    on_wall = 1.414 * h_cm > d_cm
    cnt = np.zeros((OH, OW)); wal = np.zeros((OH, OW))
    # counter hits
    m = ~on_wall
    tx = np.round(xs_[m] - h_cm[m] * PXCM).astype(int)
    ty = np.round(gnd[m] - 1.414 * h_cm[m] * DEPTHCM).astype(int)
    k = (tx >= 0) & (tx < OW) & (ty >= 0) & (ty < OH)
    np.add.at(cnt, (ty[k], tx[k]), 1.0)
    # wall hits
    m = on_wall
    wx = xs_[m] - 0.707 * d_cm[m] * PXCM
    wh = h_cm[m] - 0.707 * d_cm[m]
    tx = np.round(wx).astype(int)
    ty = np.round(jline(wx) - wh * WALLCM).astype(int)
    k = (tx >= 0) & (tx < OW) & (ty >= 0) & (ty < OH)
    np.add.at(wal, (ty[k], tx[k]), 1.0)
    cnt = gblur(np.clip(ndi.grey_dilation(cnt, size=(3, 7)), 0, 1), 5)
    wal = gblur(np.clip(ndi.grey_dilation(wal, size=(5, 5)), 0, 1), 9)
    on_counter = np.clip((yy - junction) / 5, 0, 1)
    shadow = np.clip(cnt * on_counter + wal * (1 - on_counter), 0, 1)
    out = out * (1 - 0.58 * (shadow * litness)[..., None])

    # ------------------------------------------------ 6. composite + light wrap
    wdk = (1 - lum(G))[..., None] ** 2                                 # only the darks
    G = G + wdk * 0.06 * (np.array([0.20, 0.17, 0.145]) - G)          # warm lifted blacks like the plate
    Gs = gblur(G, 0.75)                               # match upscaled plate acuity
    a = AL[..., None]
    comp = Gs * a + out * (1 - a)
    wrap_src = gblur(out, 5)
    wrap = np.clip(edge * 1.5, 0, 1)[..., None] * 0.18
    comp = comp * (1 - wrap) + np.maximum(comp, wrap_src) * wrap

    # ------------------------------------------------ 7. global look: low sat + 35mm grain
    Lc = lum(comp)[..., None]
    comp = Lc + (comp - Lc) * 0.93
    rng = np.random.default_rng(605)
    g = rng.normal(0, 1, (OH, OW))
    g = gblur(g, 0.65) * 2.2
    gc = gblur(rng.normal(0, 1, (OH, OW, 3)), 1.0) * 0.6
    amp = (0.020 + 0.030 * np.clip(1 - np.abs(Lc[..., 0] - 0.45) / 0.45, 0, 1))[..., None]
    comp = comp + (g[..., None] + gc) * amp * 0.5
    comp = np.clip(comp, 0, 1)

    Image.fromarray((comp * 255 + 0.5).astype(np.uint8)).save(OUT)
    layer = np.dstack([np.clip(Gs, 0, 1), AL])
    Image.fromarray((layer * 255 + 0.5).astype(np.uint8), 'RGBA').save(OUT_LAYER)

    # report numbers
    lit = G[(AL > 0.95) & (chrome < 0.1) & ~badge]
    top = np.percentile(lum(lit), 95)
    sel = lit[lum(lit) >= top]
    print('crop plate (x0,y0,x1,y1):', [round(v, 1) for v in CROP], 'zoom', ZOOM)
    print('product out bbox: x %.0f-%.0f  y %.0f-%.0f  height %.0f px = %.1f%% of frame'
          % (pl, pr, pt, pb, pb - pt, 100 * (pb - pt) / OH))
    print('product centre x = %.1f%% of width' % (100 * (pl + pr) / 2 / OW))
    print('lit-face top-5%% mean: #%02X%02X%02X' % tuple((sel.mean(0) * 255).round().astype(int)))
    print('nozzle (photo 257,330) ->', [round(v) for v in photo_to_out(257, 330)],
          ' tray top (photo 260,820) ->', [round(v) for v in photo_to_out(260, 820)])


if __name__ == '__main__':
    main()
