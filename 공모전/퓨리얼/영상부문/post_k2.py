# -*- coding: utf-8 -*-
"""
K2 post: clips/K2_raw.mp4 (Kling, 720x1280, 24 fps, 121 f) -> clips/K2_final.mp4 (1080x1920, 24 fps, 49 f = 2.04 s)
 1. stream-break detection (column high-pass under the nozzle, row coverage); 49 frames before it, no retime
 2. lanczos upscale, per-frame re-plate with KF2_product_layer.png (official (3)); glass + stream kept from Kling
 3. glass interior check: LF of the see-through area vs the start frame (KF2_final_start_v4) -> no rectangle
 4. drift (product patches), exposure tracking, grain matched to Kling, flicker report
 5. clips/K2_check.png (6 frames)
"""
import os, sys, glob, shutil, subprocess, tempfile
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from comp_k1 import gblur, lum
from post_k1 import ncc_shift, gm, run

CLIPS = os.path.join(HERE, 'clips'); IMG = os.path.join(HERE, 'img')
V3 = '--v3' in sys.argv     # director: source frames 0-30 only (stream still full), mci ~1.6x to 49 frames
V2 = '--v2' in sys.argv or V3   # director: frames 1-45 only, mci-stretched to 49 frames
RAW = os.path.join(CLIPS, 'K2_raw.mp4')
TAG = '_v3' if V3 else ('_v2' if V2 else '')
OUT = os.path.join(CLIPS, 'K2_final%s.mp4' % TAG)
CHECK = os.path.join(CLIPS, 'K2_check%s.png' % TAG)
USE = 31 if V3 else 45
OW, OH, FPS, NF = 1080, 1920, 24, 49
TMP = os.environ.get('K2_TMP') or tempfile.mkdtemp(prefix='k2post_')


def coverage(fr_l):
    reg = fr_l[440:630, 215:270]
    hp = reg - ndi.median_filter(reg, size=(1, 15))
    return (np.abs(hp).max(1) > 10).mean()


def main():
    rawdir = os.path.join(TMP, 'raw'); outdir = os.path.join(TMP, 'out')
    for d in (rawdir, outdir):
        shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    run(['ffmpeg', '-v', 'error', '-i', RAW, os.path.join(rawdir, 'f%03d.png')])
    raws = sorted(glob.glob(os.path.join(rawdir, '*.png')))
    cov = np.array([coverage(np.asarray(Image.open(p).convert('L')).astype(float)) for p in raws])
    brk = next(i for i in range(len(cov) - 1) if cov[i] < 0.8 and cov[i + 1] < 0.8)   # first sustained break
    print('stream breaks at frame %d (coverage %.2f); first <1.0 at %d; using frames 1..%d'
          % (brk + 1, cov[brk], int(np.argmax(cov < 1.0)) + 1, NF))
    assert NF <= brk, 'not enough frames before the break'
    if V2:
        intdir = os.path.join(TMP, 'int'); shutil.rmtree(intdir, ignore_errors=True); os.makedirs(intdir)
        stretch = (NF + 1) / (USE - 1)          # overshoot so all 49 output frames are interpolated, none cloned
        run(['ffmpeg', '-v', 'error', '-i', RAW, '-vf',
             "select='lt(n,%d)',setpts=%.6f*(PTS-STARTPTS),minterpolate=fps=%d:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1"
             % (USE, stretch, FPS), '-frames:v', str(NF), '-vsync', 'cfr', os.path.join(intdir, 'i%03d.png')])
        raws = sorted(glob.glob(os.path.join(intdir, '*.png')))
        print('v2: frames 1..%d -> %d frames (mci, x%.3f; nominal 49/45 = x%.3f)' % (USE, len(raws), stretch, NF / USE))

    start = np.asarray(Image.open(os.path.join(IMG, 'KF2_final_start_v4.png')).convert('RGB')).astype(np.float64) / 255
    lay = np.asarray(Image.open(os.path.join(IMG, 'KF2_product_layer.png'))).astype(np.float64) / 255
    yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float64)
    glass = (xx >= 266) & (xx <= 454) & (yy >= 950) & (yy <= 1292)
    stream = (xx >= 338) & (xx <= 378) & (yy >= 625) & (yy <= 960)
    keep_b = glass | stream
    keep = np.maximum(np.clip(gblur(keep_b.astype(float), 1.5) * 1.3, 0, 1), keep_b * 1.0)
    AL = lay[..., 3]
    LRGB = gblur(lay[..., :3], 0.7)
    a_lay = np.clip(gblur(AL, 0.5), 0, 1) * (1 - keep)
    g_start = gm(lum(start))
    track = [(560, 330, 760, 420), (780, 800, 900, 900), (600, 1300, 760, 1390)]
    expo_reg = (AL > 0.95) & ~ndi.binary_dilation(keep_b, iterations=20)
    door = (xx > 700) & (xx < 950) & (yy > 700) & (yy < 1000) & (AL > 0.99)
    inner = (xx >= 290) & (xx <= 430) & (yy >= 975) & (yy <= 1120)          # see-through area above the water
    rng = np.random.default_rng(909)
    stats = []
    for i in range(NF):
        fr = np.asarray(Image.open(raws[i]).convert('RGB').resize((OW, OH), Image.LANCZOS)).astype(np.float64) / 255
        g = gm(lum(fr))
        sh = [ncc_shift(g, g_start, r)[0] for r in track]
        dx = float(np.mean([s[0] for s in sh])); dy = float(np.mean([s[1] for s in sh]))
        if abs(dx) > 1 or abs(dy) > 1:
            Lr = np.stack([ndi.shift(LRGB[..., c], (dy, dx), order=1) for c in range(3)], -1)
            La = ndi.shift(a_lay, (dy, dx), order=1)
        else:
            Lr, La = LRGB, a_lay
        ex = np.clip(lum(fr)[expo_reg].mean() / lum(start)[expo_reg].mean(), 0.95, 1.05)
        nk = (lum(fr) - gblur(lum(fr), 1.5))[door].std()
        o = fr * (1 - La[..., None]) + np.clip(Lr * ex, 0, 1) * La[..., None]
        nl = (lum(o) - gblur(lum(o), 1.5))[door].std()
        gr = gblur(rng.normal(0, 1, (OH, OW)), 0.6); gr /= gr.std()
        o = np.clip(o + gr[..., None] * (np.sqrt(max(nk ** 2 - nl ** 2, 0)) * La[..., None] + 0.0012), 0, 1)
        Image.fromarray((o * 255 + 0.5).astype(np.uint8)).save(os.path.join(outdir, 'o%03d.png' % (i + 1)))
        lf_in = gblur(lum(o), 20)[inner].mean() / gblur(lum(start), 20)[inner].mean() - 1
        stats.append((dx, dy, ex, nk, (lum(o) - gblur(lum(o), 1.5))[door].std(),
                      lum(o)[AL > 0.95].mean(), lum(o)[AL < 0.05].mean(), lf_in))
    st = np.array(stats)
    print('drift dx %.2f..%.2f dy %.2f..%.2f px; exposure %.3f..%.3f' % (st[:, 0].min(), st[:, 0].max(), st[:, 1].min(),
          st[:, 1].max(), st[:, 2].min(), st[:, 2].max()))
    print('noise (door hf std) kling %.4f..%.4f -> out %.4f..%.4f' % (st[:, 3].min(), st[:, 3].max(), st[:, 4].min(), st[:, 4].max()))
    print('flicker: max frame-to-frame lum change product %.4f, background %.4f'
          % (np.abs(np.diff(st[:, 5])).max(), np.abs(np.diff(st[:, 6])).max()))
    print('glass see-through LF vs start frame: %+.1f%% .. %+.1f%%' % (100 * st[:, 7].min(), 100 * st[:, 7].max()))
    run(['ffmpeg', '-v', 'error', '-y', '-framerate', str(FPS), '-i', os.path.join(outdir, 'o%03d.png'),
         '-c:v', 'libx264', '-preset', 'slow', '-crf', '14', '-pix_fmt', 'yuv420p', '-r', str(FPS), OUT])
    pr = subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-show_entries',
                         'stream=width,height,r_frame_rate,nb_read_frames:format=duration', '-of', 'default=nw=1', OUT],
                        capture_output=True, text=True).stdout
    print(pr.strip().replace('\n', ' | '))
    picks = np.linspace(1, NF, 6).round().astype(int)
    strip = Image.new('RGB', (280 * 6, 1040), (20, 20, 20))
    for j, k in enumerate(picks):
        im = Image.open(os.path.join(outdir, 'o%03d.png' % k))
        strip.paste(im.resize((270, 480)), (j * 280, 0))
        strip.paste(im.crop((240, 600, 480, 1300)).resize((270, 540)), (j * 280, 500))
    strip.save(CHECK)
    print('check frames:', list(picks))


if __name__ == '__main__':
    main()
