# -*- coding: utf-8 -*-
"""
K1 post: clips/K1_raw.mp4 (Kling, 720x1280, 24 fps, 121 f) -> clips/K1_final.mp4 (1080x1920, 24 fps, 73 f)
 1. stream-break detection under the nozzle (column high-pass peak + row coverage)
 2. usable frames 1..N -> slowed to 73 frames with ffmpeg minterpolate (mci)
 3. lanczos upscale to 1080x1920
 4. per-frame re-plate: KF1_product_layer_v3.png + KF1_badge_overlay.png, glass + stream kept from Kling,
    per-frame drift (dial/foot patches) and exposure tracking
 5. grain unified (Kling noise level measured, dynamic grain), flicker report
 6. clips/K1_check.png (6 frames)
Usage: python post_k1.py
"""
import os, sys, glob, shutil, subprocess, tempfile
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from comp_k1 import gblur, lum

CLIPS = os.path.join(HERE, 'clips'); IMG = os.path.join(HERE, 'img')
RAW = os.path.join(CLIPS, 'K1_raw.mp4')
V2 = '--v2' in sys.argv   # round 2: badge behind the glass (75 %, blur 1, +3 px refraction) under the rim highlight,
                          #          foam highlights (>= 85 %) in the water -35 %
OUT = os.path.join(CLIPS, 'K1_final_v2.mp4' if V2 else 'K1_final.mp4')
CHECK = os.path.join(CLIPS, 'K1_check_v2.png' if V2 else 'K1_check.png')
OW, OH, FPS = 1080, 1920, 24
TARGET_FRAMES = 73                      # 3.05 s * 24 = 73.2 -> 73 frames (3.042 s)
TMP = os.environ.get('K1_TMP') or tempfile.mkdtemp(prefix='k1post_')


def run(cmd):
    subprocess.run(cmd, check=True)


def stream_metric(frame_l):
    """frame_l: 720x1280 luminance. high-pass peak of the column profile between nozzle and glass rim."""
    reg = frame_l[545:690, 255:320]
    prof = reg.mean(0)
    hp = prof - ndi.median_filter(prof, size=15)
    rowpk = (reg - ndi.median_filter(reg, size=(1, 15))).max(1)
    return hp.max(), (rowpk > 12).mean()


def ncc_shift(ga, gb, r, rng=3.0, step=0.5):
    x0, y0, x1, y1 = r
    B = gb[y0:y1, x0:x1]; bv, bd = -9, (0.0, 0.0)
    for dy in np.arange(-rng, rng + 1e-6, step):
        for dx in np.arange(-rng, rng + 1e-6, step):
            A = ndi.shift(ga[y0 - 6:y1 + 6, x0 - 6:x1 + 6], (-dy, -dx), order=1)[6:-6, 6:-6]
            aa, bb = A - A.mean(), B - B.mean()
            v = (aa * bb).sum() / np.sqrt((aa * aa).sum() * (bb * bb).sum() + 1e-12)
            if v > bv:
                bv, bd = v, (dx, dy)
    return bd, bv


def gm(x):
    x = ndi.gaussian_filter(x, 1.5)
    return np.hypot(ndi.sobel(x, 0), ndi.sobel(x, 1))


def main():
    os.makedirs(TMP, exist_ok=True)
    rawdir = os.path.join(TMP, 'raw'); intdir = os.path.join(TMP, 'int'); outdir = os.path.join(TMP, 'out')
    for d in (rawdir, intdir, outdir):
        shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    run(['ffmpeg', '-v', 'error', '-i', RAW, os.path.join(rawdir, 'f%03d.png')])
    raws = sorted(glob.glob(os.path.join(rawdir, '*.png')))

    # ---------------- 1. stream break
    ok = []
    for p in raws:
        pk, cov = stream_metric(np.asarray(Image.open(p).convert('L')).astype(float))
        ok.append(pk > 20 and cov > 0.9)
    ok = np.array(ok)
    brk = next(i for i in range(len(ok) - 1) if not ok[i] and not ok[i + 1])   # first sustained loss
    use = brk                                      # frames 0..use-1 (1-based 1..use)
    stretch = (TARGET_FRAMES + 1) / (use - 1)       # minterpolate stops at the last source pts: overshoot 2 frames so all 73 are real
    print('stream breaks at frame %d (1-based); usable 1..%d = %d frames (%.2f s); stretch x%.3f'
          % (brk + 1, use, use, use / FPS, stretch))

    # ---------------- 2. slow-down with motion-compensated interpolation
    run(['ffmpeg', '-v', 'error', '-i', RAW, '-vf',
         "select='lt(n,%d)',setpts=%.6f*(PTS-STARTPTS),minterpolate=fps=%d:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,"
         "tpad=stop_mode=clone:stop=4" % (use, stretch, FPS), '-frames:v', str(TARGET_FRAMES), '-vsync', 'cfr', os.path.join(intdir, 'i%03d.png')])
    ints = sorted(glob.glob(os.path.join(intdir, '*.png')))
    print('interpolated frames:', len(ints))

    # ---------------- 3/4. upscale + re-plate
    start = np.asarray(Image.open(os.path.join(IMG, 'KF1_final_start_v2.png')).convert('RGB')).astype(np.float64) / 255
    lay = np.asarray(Image.open(os.path.join(IMG, 'KF1_product_layer_v3.png'))).astype(np.float64) / 255
    bad = np.asarray(Image.open(os.path.join(IMG, 'KF1_badge_overlay.png'))).astype(np.float64) / 255
    yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float64)
    # keep (Kling): glass + stream column (same geometry as comp_k1_water.py, a little wider for wobble)
    glass = (xx >= 349) & (xx <= 515) & (yy >= 1019) & (yy <= 1306)
    stream = (xx >= 408) & (xx <= 460) & (yy >= 797) & (yy <= 1040)
    keep_b = glass | stream
    keep = np.maximum(np.clip(gblur(keep_b.astype(float), 1.2) * 1.3, 0, 1), keep_b * 1.0)
    AL = lay[..., 3]
    LRGB = gblur(lay[..., :3], 0.7)                               # match Kling's upscaled acuity
    a_lay = np.clip(gblur(AL, 0.5), 0, 1) * (1 - keep)
    BRGB, BA = bad[..., :3], bad[..., 3]
    g_start = gm(lum(start))
    track = [(560, 860, 700, 920), (860, 1290, 960, 1360)]       # dial, right foot
    expo_reg = (AL > 0.95) & ~ndi.binary_dilation(keep_b, iterations=20) & (yy < 1250)
    door = (xx > 700) & (xx < 880) & (yy > 1000) & (yy < 1200)    # flat door face for noise level
    rng = np.random.default_rng(605)
    # v2 geometry: glass silhouette (right wall at x~501), water interior, rim/wall highlight band
    glass_sil = np.clip(gblur(((xx >= 358) & (xx <= 501) & (yy >= 1040) & (yy <= 1300)).astype(float), 1.0), 0, 1)
    water = gblur(((xx >= 368) & (xx <= 492) & (yy >= 1100) & (yy <= 1288)).astype(float), 2.0)
    rim_band = gblur(((xx >= 492) & (xx <= 509) & (yy >= 1030) & (yy <= 1300)).astype(float), 1.0)
    Ba_full = np.clip(BA / np.maximum(BA.max(), 1e-6), 0, 1)                 # overlay mask without its old 0.75 zone
    Ba_full = np.where(BA > 0.01, np.maximum(Ba_full, (BA > 0.5) * 1.0), 0)
    stats = []
    for i, p in enumerate(ints):
        fr = np.asarray(Image.open(p).convert('RGB').resize((OW, OH), Image.LANCZOS)).astype(np.float64) / 255
        g = gm(lum(fr))
        sh = [ncc_shift(g, g_start, r)[0] for r in track]
        dx = float(np.mean([s[0] for s in sh])); dy = float(np.mean([s[1] for s in sh]))
        if abs(dx) > 1 or abs(dy) > 1:                            # follow camera drift
            Lr = np.stack([ndi.shift(LRGB[..., c], (dy, dx), order=1) for c in range(3)], -1)
            La = ndi.shift(a_lay, (dy, dx), order=1)
            Br = np.stack([ndi.shift(BRGB[..., c], (dy, dx), order=1) for c in range(3)], -1)
            Ba = ndi.shift(BA, (dy, dx), order=1)
        else:
            Lr, La, Br, Ba = LRGB, a_lay, BRGB, BA
        # exposure tracking: Kling product pixels vs the start frame
        ex = np.clip(lum(fr)[expo_reg].mean() / lum(start)[expo_reg].mean(), 0.95, 1.05)
        # Kling noise on a flat face -> grain for the layer so both read the same
        hf = lum(fr) - gblur(lum(fr), 1.5)
        nk = hf[door].std()
        o = fr * (1 - La[..., None]) + np.clip(Lr * ex, 0, 1) * La[..., None]
        if not V2:
            o = o * (1 - Ba[..., None]) + np.clip(Br * ex, 0, 1) * Ba[..., None]
        else:
            # (a) foam: highlights >= 85 % inside the water/glass interior lowered by 35 %
            Lo = lum(o)
            wfoam = gblur(np.clip((Lo - 0.82) / 0.06, 0, 1), 1.0) * water
            o = o * (1 - 0.35 * wfoam[..., None])
            # (b) badge: in front of the ribs outside the glass, behind the glass inside its silhouette
            Bin = np.stack([ndi.shift(gblur(Br[..., c], 1.0), (0, 3), order=1) for c in range(3)], -1)
            Ain = ndi.shift(gblur(Ba_full, 1.0), (0, 3), order=1) * 0.75 * glass_sil
            Aout = Ba_full * (1 - glass_sil)
            o = o * (1 - Aout[..., None]) + np.clip(Br * ex, 0, 1) * Aout[..., None]
            o = o * (1 - Ain[..., None]) + np.clip(Bin * ex, 0, 1) * Ain[..., None]
            # (c) glass rim / wall highlight back on top
            Lf = lum(fr)
            hmask = np.clip((Lf - gblur(Lf, 4) - 0.015) / 0.04, 0, 1) * rim_band
            o = o * (1 - hmask[..., None]) + fr * hmask[..., None]
            # the wall line must also cross the badge: carry the wall's highlight profile (measured just
            # above the badge) down through the badge rows, screen-blended
            prof = (Lf - gblur(Lf, 4))[1110:1170, 488:512].mean(0).clip(0, None)
            line = np.zeros((OH, OW)); line[1172:1236, 488:512] = prof[None, :]
            line = gblur(line, 0.7) * 1.6
            o = 1 - (1 - o) * (1 - np.clip(line, 0, 0.6)[..., None])
        gr = gblur(rng.normal(0, 1, (OH, OW)), 0.6)
        gr = gr / gr.std()
        hf_l = lum(o) - gblur(lum(o), 1.5)
        nl = hf_l[door].std()
        add_l = np.sqrt(max(nk ** 2 - nl ** 2, 0)) * 1.0          # top up the layer to Kling's noise level
        o = o + gr[..., None] * (add_l * La[..., None] + 0.0012)   # + very light uniform dynamic grain everywhere
        o = np.clip(o, 0, 1)
        Image.fromarray((o * 255 + 0.5).astype(np.uint8)).save(os.path.join(outdir, 'o%03d.png' % (i + 1)))
        hf_o = lum(o) - gblur(lum(o), 1.5)
        stats.append((dx, dy, ex, nk, hf_o[door].std(), lum(o)[AL > 0.95].mean(), lum(o)[~(AL > 0.05)].mean()))
    st = np.array(stats)
    print('drift dx %.2f..%.2f dy %.2f..%.2f (px); exposure %.3f..%.3f' % (st[:, 0].min(), st[:, 0].max(),
          st[:, 1].min(), st[:, 1].max(), st[:, 2].min(), st[:, 2].max()))
    print('noise (door hf std) kling %.4f..%.4f -> out %.4f..%.4f' % (st[:, 3].min(), st[:, 3].max(), st[:, 4].min(), st[:, 4].max()))
    print('flicker: max frame-to-frame lum change product %.4f, background %.4f'
          % (np.abs(np.diff(st[:, 5])).max(), np.abs(np.diff(st[:, 6])).max()))

    # ---------------- encode
    run(['ffmpeg', '-v', 'error', '-y', '-framerate', str(FPS), '-i', os.path.join(outdir, 'o%03d.png'),
         '-c:v', 'libx264', '-preset', 'slow', '-crf', '14', '-pix_fmt', 'yuv420p', '-r', str(FPS), OUT])
    pr = subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-show_entries',
                         'stream=width,height,r_frame_rate,nb_read_frames:format=duration', '-of', 'default=nw=1', OUT],
                        capture_output=True, text=True).stdout
    print(pr.strip().replace('\n', ' | '))

    # ---------------- check strip (6 frames, full frame + nozzle/glass crop)
    picks = np.linspace(1, len(ints), 6).round().astype(int)
    tiles = []
    for k in picks:
        im = Image.open(os.path.join(outdir, 'o%03d.png' % k))
        full = im.resize((270, 480))
        crop = im.crop((330, 760, 620, 1340)).resize((270, 540))
        t = Image.new('RGB', (270, 1040), (20, 20, 20)); t.paste(full, (0, 0)); t.paste(crop, (0, 500))
        tiles.append(t)
    strip = Image.new('RGB', (270 * 6 + 50, 1040), (20, 20, 20))
    for j, t in enumerate(tiles):
        strip.paste(t, (j * 280, 0))
    strip.save(CHECK)
    print('check frames:', list(picks))


if __name__ == '__main__':
    main()
