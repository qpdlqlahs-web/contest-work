# -*- coding: utf-8 -*-
"""
Still -> Kling clips post (full length, trimming after the design call).
  v10 / v05 : lanczos 1080x1920, per-frame re-plate of the official product layer (drift tracked, exposure tracked),
              occluders (people in front of the product) kept from Kling, grain matched
  v07 / v14 / v16 : lanczos to width 1080, centre crop 9:16 (raws are 716x1284), grain unified
out: clips/<name>_final_full.mp4 + clips/<name>_check_full.png
Usage: python post_v.py [v05 v07 v10 v14 v16]
"""
import os, sys, glob, shutil, subprocess, tempfile
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from comp_k1 import gblur, lum
from post_k1 import ncc_shift, gm, run
from post_k345 import hf_flat

CLIPS = os.path.join(HERE, 'clips'); IMG = os.path.join(HERE, 'img')
OW, OH, FPS = 1080, 1920, 24
TARGET_GRAIN = 0.0028
TMP = os.environ.get('V_TMP') or tempfile.mkdtemp(prefix='vpost_')
CFG = {
    'v10': dict(start='S10_start_v5.png', layer='S10_product_layer_v5.png',
                track=[(560, 960, 700, 1060), (760, 1000, 900, 1120), (900, 1250, 1040, 1350)]),
    'v05': dict(start='S05_comp.png', layer='S05_product_layer.png',
                track=[(520, 1000, 640, 1100), (430, 900, 560, 1000), (640, 1120, 760, 1200)]),
}


FINAL = '--final' in sys.argv
CUT = {'v05': (0, 24, 24), 'v07': (0, 24, 24), 'v10': (0, 61, 72), 'v14': (0, 36, 36), 'v16': (0, 36, 36)}


def frames(name):
    d = os.path.join(TMP, name, 'src'); shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    vf = 'scale=1080:-2:flags=lanczos,crop=1080:1920'
    extra = []
    if FINAL:
        first, count, target = CUT[name]
        pre = "select='between(n,%d,%d)',setpts=PTS-STARTPTS" % (first, first + count - 1)
        if target > count:
            stretch = (target + 1) / (count - 1)        # overshoot: no cloned tail frames
            pre += ",setpts=%.6f*PTS,minterpolate=fps=%d:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1" % (stretch, FPS)
            print('%s: frames %d-%d -> %d (mci x%.3f)' % (name, first, first + count - 1, target, stretch))
        vf = pre + ',' + vf
        extra = ['-frames:v', str(target)]
    run(['ffmpeg', '-v', 'error', '-i', os.path.join(CLIPS, name + '_raw.mp4'), '-vf', vf] + extra +
        ['-vsync', 'cfr', os.path.join(d, 'f%03d.png')])
    return sorted(glob.glob(os.path.join(d, '*.png')))


def encode(name, outdir, n):
    dst = os.path.join(CLIPS, name + ('_final.mp4' if FINAL else '_final_full.mp4'))
    run(['ffmpeg', '-v', 'error', '-y', '-framerate', str(FPS), '-i', os.path.join(outdir, 'o%03d.png'),
         '-c:v', 'libx264', '-preset', 'slow', '-crf', '14', '-pix_fmt', 'yuv420p', '-r', str(FPS), dst])
    pr = subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-show_entries',
                         'stream=width,height,nb_read_frames:format=duration', '-of', 'default=nw=1', dst],
                        capture_output=True, text=True).stdout.strip().replace('\n', ' | ')
    picks = np.linspace(1, n, 6).round().astype(int)
    strip = Image.new('RGB', (280 * 6, 490), (20, 20, 20))
    for j, k in enumerate(picks):
        strip.paste(Image.open(os.path.join(outdir, 'o%03d.png' % k)).resize((270, 480)), (j * 280, 5))
    if not FINAL:
        strip.save(os.path.join(CLIPS, name + '_check_full.png'))
    return pr


def add_grain(o, rng, extra_mask=None, extra=0.0):
    n0 = hf_flat(o)
    g = gblur(rng.normal(0, 1, o.shape[:2]), 0.6); g /= g.std()
    add = np.sqrt(max(TARGET_GRAIN ** 2 - n0 ** 2, 0))
    amt = add + (extra * extra_mask if extra_mask is not None else 0)
    if np.ndim(amt) == 2:
        amt = amt[..., None]
    return np.clip(o + g[..., None] * amt, 0, 1), n0


def replate(name):
    c = CFG[name]
    fs = frames(name)
    out = os.path.join(TMP, name, 'out'); shutil.rmtree(out, ignore_errors=True); os.makedirs(out)
    start = np.asarray(Image.open(os.path.join(IMG, c['start'])).convert('RGB')).astype(np.float64) / 255
    lay = np.asarray(Image.open(os.path.join(IMG, c['layer']))).astype(np.float64) / 255
    LRGB, AL = lay[..., :3], lay[..., 3]
    g_start = gm(lum(start))
    solid = AL > 0.5
    expo = ndi.binary_erosion(AL > 0.95, iterations=4)
    rng = np.random.default_rng(1000 + int(name[1:]))
    st = []
    for i, p in enumerate(fs):
        fr = np.asarray(Image.open(p).convert('RGB')).astype(np.float64) / 255
        g = gm(lum(fr))
        sh = [ncc_shift(g, g_start, r, rng=4.0)[0] for r in c['track']]
        dx = float(np.median([s[0] for s in sh])); dy = float(np.median([s[1] for s in sh]))
        if abs(dx) > 1 or abs(dy) > 1:
            Lr = np.stack([ndi.shift(LRGB[..., k], (dy, dx), order=1) for k in range(3)], -1)
            La = ndi.shift(AL, (dy, dx), order=1)
            So = ndi.shift(solid.astype(float), (dy, dx), order=0) > 0.5
        else:
            Lr, La, So = LRGB, AL, solid
        ex = np.clip(lum(fr)[expo].mean() / max(lum(start)[expo].mean(), 1e-6), 0.92, 1.08)
        Lx = np.clip(Lr * ex, 0, 1)
        # occluders: strong difference inside the product, connected to the product outline
        dif = gblur(np.abs(fr - Lx).mean(2), 2.0)
        occ = So & (dif > 0.16)
        occ = ndi.binary_opening(occ, iterations=2)
        edge = So & ~ndi.binary_erosion(So, iterations=3)
        lab, n = ndi.label(occ)
        keep = np.unique(lab[edge & occ]); keep = keep[keep > 0]
        occ = np.isin(lab, keep)
        sz = occ.sum()
        if sz < 300:
            occ[:] = False
        occ_a = np.clip(gblur(ndi.binary_dilation(occ, iterations=2).astype(float), 1.5), 0, 1)
        a = La * (1 - occ_a)
        o = fr * (1 - a[..., None]) + Lx * a[..., None]
        Lo = lum(o); hf = Lo - gblur(Lo, 1.5)
        gg = np.hypot(ndi.sobel(gblur(Lo, 2), 0), ndi.sobel(gblur(Lo, 2), 1))
        flat = gg < np.percentile(gg, 30)
        nk = hf[flat & (a < 0.05)].std(); nl = hf[flat & (a > 0.9)].std() if (flat & (a > 0.9)).sum() > 500 else nk
        top = np.sqrt(max(nk ** 2 - nl ** 2, 0))
        o, n0 = add_grain(o, rng, extra_mask=a, extra=top)
        Image.fromarray((o * 255 + 0.5).astype(np.uint8)).save(os.path.join(out, 'o%03d.png' % (i + 1)))
        st.append((dx, dy, ex, n0, hf_flat(o), lum(o)[solid].mean(), lum(o)[~ndi.binary_dilation(solid, iterations=30)].mean(), sz))
    st = np.array(st)
    pr = encode(name, out, len(fs))
    print('%s: %s | drift dx %.2f..%.2f dy %.2f..%.2f | expo %.3f..%.3f | grain %.4f..%.4f -> %.4f..%.4f | '
          'flicker prod %.4f bg %.4f | occluded frames %d (max %d px)'
          % (name, pr, st[:, 0].min(), st[:, 0].max(), st[:, 1].min(), st[:, 1].max(), st[:, 2].min(), st[:, 2].max(),
             st[:, 3].min(), st[:, 3].max(), st[:, 4].min(), st[:, 4].max(), np.abs(np.diff(st[:, 5])).max(),
             np.abs(np.diff(st[:, 6])).max(), int((st[:, 7] >= 300).sum()), int(st[:, 7].max())))


def plain(name):
    fs = frames(name)
    out = os.path.join(TMP, name, 'out'); shutil.rmtree(out, ignore_errors=True); os.makedirs(out)
    rng = np.random.default_rng(2000 + int(name[1:]))
    st = []
    for i, p in enumerate(fs):
        fr = np.asarray(Image.open(p).convert('RGB')).astype(np.float64) / 255
        o, n0 = add_grain(fr, rng)
        Image.fromarray((o * 255 + 0.5).astype(np.uint8)).save(os.path.join(out, 'o%03d.png' % (i + 1)))
        st.append((n0, hf_flat(o), lum(o).mean()))
    st = np.array(st)
    pr = encode(name, out, len(fs))
    print('%s: %s | grain %.4f..%.4f -> %.4f..%.4f | flicker %.4f'
          % (name, pr, st[:, 0].min(), st[:, 0].max(), st[:, 1].min(), st[:, 1].max(), np.abs(np.diff(st[:, 2])).max()))


if __name__ == '__main__':
    todo = [a for a in sys.argv[1:] if a.startswith('v')] or ['v10', 'v05', 'v07', 'v14', 'v16']
    for n in todo:
        (replate if n in CFG else plain)(n)
    if FINAL:
        rows = []
        for n in ['v05', 'v07', 'v10', 'v14', 'v16']:
            d = os.path.join(TMP, n, 'out'); fs = sorted(glob.glob(os.path.join(d, '*.png')))
            if fs:
                rows.append((n, [fs[0], fs[len(fs) // 2], fs[-1]]))
        strip = Image.new('RGB', (len(rows) * 3 * 190 + (len(rows) - 1) * 20, 330), (20, 20, 20))
        x = 0
        for n, three in rows:
            for p in three:
                strip.paste(Image.open(p).resize((180, 320)), (x, 5)); x += 190
            x += 20
        strip.save(os.path.join(CLIPS, 'v_check.png'))
