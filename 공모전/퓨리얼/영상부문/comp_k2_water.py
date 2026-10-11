# -*- coding: utf-8 -*-
"""
K2 start frame (guide 4-6 step 3): re-plate after the water edit.
in : img/KF2water_1.png (AI edit of KF2_comp), img/KF2_comp.png (official (3) composite), img/KF2_product_layer.png
out: img/KF2_final_start.png (1080x1920)
Everything comes from KF2_comp except the glass + stream taken from the AI edit (after alignment).
The AI glass is 11.6 cm tall against the 340 mm product -> scaled about its base to 10 cm (ratio 3.4).
"""
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from comp_k1 import gblur, lum
from comp_k1_water import gm, patch_shift

IMG = os.path.join(HERE, 'img')
OW, OH = 1080, 1920
PX_PER_MM = 1.6 * 689 / 340.0
V3 = '--v3' in sys.argv      # round 3: LF match of the see-through background inside the glass, block inpaint, smooth rim join
V2 = '--v2' in sys.argv or V3      # round 2: silhouette mask (no halo), stream through the rim, rim on top, contact, bubbles, bg -0.2 EV
BG_EV = -0.2                 # official (3) bbox height 689 px at scale 1.6 = 340 mm


def main():
    ai = np.asarray(Image.open(os.path.join(IMG, 'KF2water_1.png')).convert('RGB').resize((OW, OH), Image.LANCZOS)) / 255.0
    base = np.asarray(Image.open(os.path.join(IMG, 'KF2_comp.png')).convert('RGB')) / 255.0
    yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float64)
    # ---- align AI -> comp (translation, product patches away from the glass)
    ga, gb_ = gm(lum(ai)), gm(lum(base))
    sh = []
    for r in [(560, 330, 760, 420), (780, 800, 900, 900), (600, 1300, 760, 1390), (330, 1290, 480, 1380), (700, 1200, 1000, 1290)]:
        (dx, dy), v = patch_shift(ga, gb_, r)
        if v > 0.5:
            sh.append((dx, dy))
    dx, dy = np.median(np.array(sh), 0) if sh else (0, 0)
    ai = np.stack([ndi.shift(ai[..., c], (-dy, -dx), order=1, mode='nearest') for c in range(3)], -1)
    print('AI->comp shift (%.1f, %.1f) from %d patches' % (dx, dy, len(sh)))

    # ---- glass and stream from the AI edit
    gx0, gx1, gtop, gbase = 252, 468, 896, 1281
    glass = (xx >= gx0) & (xx <= gx1) & (yy >= gtop) & (yy <= gbase + 4)
    d = gblur(np.abs(ai - base).mean(2), 1.0)
    stream = (d > 0.05) & (xx > 330) & (xx < 380) & (yy > 600) & (yy < gtop + 10)
    lab, n = ndi.label(stream)
    if n:
        sz = ndi.sum(stream, lab, range(1, n + 1)); stream = lab == (np.argmax(sz) + 1)
    stream = ndi.binary_dilation(stream, iterations=2)
    h_ai = gbase - gtop
    target = 100 * PX_PER_MM
    k = target / h_ai
    cx = (gx0 + gx1) / 2
    # scale the glass patch about its base centre
    mat = [1 / k, 1 / k]; off = [gbase - gbase / k, cx - cx / k]
    gl_rgb = np.stack([ndi.affine_transform(ai[..., c], mat, off, order=3, mode='nearest') for c in range(3)], -1)
    gl_a = ndi.affine_transform(glass.astype(float), mat, off, order=1)
    gl_a = np.clip(gblur(gl_a, 0.8) * 1.2, 0, 1)
    new_top = gbase - h_ai * k
    # extend the stream below row 880 (old glass rim there) with the column profile of rows 820-880
    stream &= yy < 880
    prof = ai[820:880].copy()
    for y in range(880, int(new_top) + 20):
        ai[y] = np.where(stream[879][:, None], prof[(y - 880) % 60], ai[y])
    stream[880:int(new_top) + 20] = stream[879]
    st_a = np.clip(gblur(stream.astype(float), 0.8) * 1.3, 0, 1) * (1 - gl_a)
    if not V2:
        out = base * (1 - gl_a[..., None]) + gl_rgb * gl_a[..., None]
        out = out * (1 - st_a[..., None]) + ai * st_a[..., None]
        cm = (((xx - cx) / ((gx1 - gx0) * k * 0.5)) ** 2 + ((yy - gbase - 1) / 3.0) ** 2 <= 1).astype(float)
        cm = gblur(cm, 2.5) * (1 - gl_a * 0.7)
        out = out * (1 - 0.35 * cm[..., None])
    else:
        rim_y = int(round(new_top)) + 1                       # top of the rim after scaling
        wl, wr = cx - 91 + 2, cx + 91 - 2                     # outer glass walls
        sil = ((xx >= wl) & (xx <= wr) & (yy >= rim_y) & (yy <= gbase + 3)).astype(float)
        gl_a = np.clip(gblur(sil, 1.2 if V3 else 0.7) * 1.15, 0, 1) * (yy >= rim_y - 1)
        water_y = gbase - (gbase - 1105) * k                  # AI water surface after scaling
        # stream below row 870: the AI stream's mean column profile, added as a difference over whatever is
        # behind it (glass / water), so its width matches the stream above and it stays transparent
        cols = np.nonzero(stream[860])[0]
        c0, c1 = cols.min() - 3, cols.max() + 4
        P = ai[820:870, c0:c1].mean(0); Bp = base[820:870, c0:c1].mean(0)
        diff = P - Bp
        dcol = np.abs(diff).mean(1); acol = np.clip((dcol - 0.012) / max(dcol.max() - 0.012, 1e-6) * 1.5, 0, 1)
        # power-outage feel: background (everything except the product layer) -0.2 EV, before glass/stream
        lay = np.asarray(Image.open(os.path.join(IMG, 'KF2_product_layer.png'))).astype(np.float64)[..., 3] / 255
        dimb = np.clip(base ** 2.2 * 2 ** BG_EV, 0, 1) ** (1 / 2.2)
        base_d = base * lay[..., None] + dimb * (1 - lay[..., None])
        if V3:
            # glass = real plate behind it (base_d) + high-frequency detail of the AI glass (rim, walls, water line,
            # bubbles, highlights). The AI's own see-through background (brighter, rectangular) is dropped entirely.
            hp = gl_rgb - gblur(gl_rgb, 8)
            inner = sil > 0.5
            water = inner & (yy >= water_y)
            wall_l = (np.abs(xx - wl) <= 7) & water
            # left wall below water: use the wall's own profile from above the water line (no bright step)
            wy0, wy1 = int(rim_y) + 25, int(water_y) - 6
            x0w, x1w = int(wl) - 7, int(wl) + 8
            prof = hp[wy0:wy1, x0w:x1w].mean(0)
            hp[int(water_y) + 4:int(gbase) - 30, x0w:x1w] = prof[None]
            ramp = np.clip((yy - water_y) / 4, 0, 1) * wall_l
            tint = np.where(water[..., None], np.array([0.988, 0.992, 0.996]), 1.0)  # water: slightly darker / cooler
            gl_rgb = np.clip(base_d * tint + hp, 0, 1)
        out = base_d * (1 - gl_a[..., None]) + gl_rgb * gl_a[..., None]
        st_top = stream & (yy < 870)
        sa = np.clip(gblur(st_top.astype(float), 0.8) * 1.3, 0, 1) * (1 - gl_a)
        ai_d = ai + (base_d - base)
        # upper stream (AI rows) also as a difference layer -> same look/width as the continuation below
        diff_rows = (ai - base) * sa[..., None] * np.isin(xx, np.arange(0, OW))[..., None]
        add = np.zeros_like(out)
        y_end = int(water_y)
        for y in range(870, y_end + 1):
            att = 1.0 - 0.15 * np.clip((y - rim_y + 2) / 12, 0, 1) if V3 else (0.85 if y >= rim_y else 1.0)
            fade = np.clip((y_end - y) / 6, 0, 1)
            add[y, c0:c1] = diff * (acol * att * (0.4 + 0.6 * fade))[:, None]
        add = add + diff_rows
        jz = (((np.abs(yy - rim_y) <= 12) & (not V3)) | (np.abs(yy - 870) <= 12)) & (xx >= c0) & (xx < c1)
        addv = np.stack([ndi.gaussian_filter1d(add[..., c], 2.0, axis=0) for c in range(3)], -1)   # vertical only
        add = np.where(jz[..., None], addv, add)
        out = np.clip(out + add, 0, 1)
        st_a = np.zeros((OH, OW)); st_a[600:y_end + 1, c0:c1] = acol[None, :]
        st_a = np.maximum(st_a, sa)
        # front rim highlight back on top of the stream
        Lg = lum(gl_rgb)
        rimband = (yy >= rim_y) & (yy <= rim_y + 9) & (xx >= wl) & (xx <= wr)
        hl = np.clip((Lg - gblur(Lg, 3) - 0.01) / 0.05, 0, 1) * rimband
        hl = np.maximum(hl, rimband * 0.55 * np.clip((Lg - 0.6) / 0.2, 0, 1))
        out = out * (1 - hl[..., None]) + gl_rgb * hl[..., None]
        # bubbles: highlights >= 85 % inside the water -20 %
        wat = (yy > water_y + 3) & (yy < gbase - 8) & (xx > wl + 6) & (xx < wr - 6)
        bub = gblur(np.clip((lum(out) - 0.82) / 0.06, 0, 1), 0.7) * wat
        out = out * (1 - 0.20 * bub[..., None])
        # contact shadow under the glass base: stronger, two scales
        cm1 = (((xx - cx) / (91 * 0.95)) ** 2 + ((yy - gbase - 1) / 2.5) ** 2 <= 1).astype(float)
        cm2 = (((xx - cx) / (91 * 1.1)) ** 2 + ((yy - gbase - 2) / 5.0) ** 2 <= 1).astype(float)
        cm = 0.6 * gblur(cm1, 1.5) + 0.3 * gblur(cm2, 5)
        out = out * (1 - np.clip(cm, 0, 0.75)[..., None] * (1 - 0.6 * gl_a[..., None]))
        print('v2: rim y %d, water y %.0f, stream cols %d-%d, bg %+.1f EV' % (rim_y, water_y, cols.min(), cols.max(), BG_EV))
        st_a = np.maximum(st_a, gl_a)
    rng = np.random.default_rng(92)
    g = gblur(rng.normal(0, 1, (OH, OW)), 0.6) * 2.1
    out = np.clip(out + g[..., None] * 0.004 * np.maximum(gl_a, st_a)[..., None], 0, 1)
    Image.fromarray((out * 255 + 0.5).astype(np.uint8)).save(os.path.join(IMG, 'KF2_final_start_v3.png' if V3 else ('KF2_final_start_v2.png' if V2 else 'KF2_final_start.png')))
    print('glass: AI %d px (%.1f cm) -> %.0f px (10 cm), scale %.3f; product/glass = %.2f; new rim y %.0f'
          % (h_ai, h_ai / PX_PER_MM / 10, target, k, 340 / 100, new_top))


if __name__ == '__main__':
    main()
