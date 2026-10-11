# -*- coding: utf-8 -*-
"""
K3 / K4 / K5 post (no product, no re-plate). Kling raws are 716x1284 (not exactly 9:16):
scale to width 1080 (lanczos) -> 1080x1937, centre crop to 1080x1920.
  K3_final.mp4 : source frames 50-109 (60 f), 1.0x                       -> 60 f (2.50 s)
  K4_final.mp4 : source frames 0-90 (91 f), mci                            -> 98 f (4.08 s)
  K5_final.mp4 : source frames 72-120 (49 f), mci (1.5x, fallback 1.3x)  -> + last frame hold with 2 % push-in -> 89 f
Grain: measured on flat areas per clip, topped up to a common level (dynamic, per frame). Flicker: frame-to-frame mean
luminance change. Check strips clips/K3_check.png, K4_check.png, K5_check.png.
Usage: python post_k345.py [K3 K4 K5] [--k5 1.3]
"""
import os, sys, glob, shutil, subprocess, tempfile
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
CLIPS = os.path.join(HERE, 'clips')
OW, OH, FPS = 1080, 1920, 24
TARGET_GRAIN = 0.0028          # hf std on flat areas, same level as K1/K2 finals (0.0023-0.0035)
TMP = os.environ.get('K345_TMP') or tempfile.mkdtemp(prefix='k345_')
LW = np.array([0.2126, 0.7152, 0.0722])


def run(cmd):
    subprocess.run(cmd, check=True)


def extract(name, first, count, target, extra=''):
    """frames first..first+count-1 -> `target` frames (mci if target > count), scaled+cropped to 1080x1920."""
    d = os.path.join(TMP, name, 'src'); shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    vf = "select='between(n,%d,%d)',setpts=PTS-STARTPTS" % (first, first + count - 1)
    if target > count:
        stretch = (target + 1) / (count - 1)        # overshoot: every output frame is interpolated, no cloned tail
        vf += ",setpts=%.6f*PTS,minterpolate=fps=%d:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1" % (stretch, FPS)
    else:
        stretch = 1.0
    vf += ",scale=1080:-2:flags=lanczos,crop=1080:1920"
    run(['ffmpeg', '-v', 'error', '-i', os.path.join(CLIPS, name + '_raw.mp4'), '-vf', vf,
         '-frames:v', str(target), '-vsync', 'cfr', os.path.join(d, 'f%03d.png')])
    fs = sorted(glob.glob(os.path.join(d, '*.png')))
    return fs, stretch


def lum(a):
    return a @ LW


def hf_flat(a):
    L = lum(a)
    hf = L - ndi.gaussian_filter(L, 1.5)
    g = np.hypot(ndi.sobel(ndi.gaussian_filter(L, 2), 0), ndi.sobel(ndi.gaussian_filter(L, 2), 1))
    flat = g < np.percentile(g, 30)
    return hf[flat].std()


def finish(name, frames, hold=0, push=0.0):
    out = os.path.join(TMP, name, 'out'); shutil.rmtree(out, ignore_errors=True); os.makedirs(out)
    rng = np.random.default_rng(abs(hash(name)) % 2 ** 31)
    seq = [(p, 1.0) for p in frames]
    if hold:
        seq += [(frames[-1], 1.0 + push * (k + 1) / hold) for k in range(hold)]
    stats = []
    for i, (p, z) in enumerate(seq):
        a = np.asarray(Image.open(p).convert('RGB')).astype(np.float64) / 255
        if z != 1.0:                                 # push-in on the held frame (centre zoom, lanczos)
            im = Image.open(p).convert('RGB')
            w, h = round(OW / z), round(OH / z)
            im = im.crop(((OW - w) // 2, (OH - h) // 2, (OW - w) // 2 + w, (OH - h) // 2 + h)).resize((OW, OH), Image.LANCZOS)
            a = np.asarray(im).astype(np.float64) / 255
        n0 = hf_flat(a)
        g = ndi.gaussian_filter(rng.normal(0, 1, (OH, OW)), 0.6); g /= g.std()
        add = np.sqrt(max(TARGET_GRAIN ** 2 - n0 ** 2, 0))
        wl = (0.6 + 0.4 * np.clip(1 - np.abs(lum(a) - 0.5) / 0.5, 0, 1))[..., None]
        o = np.clip(a + g[..., None] * add * wl, 0, 1)
        Image.fromarray((o * 255 + 0.5).astype(np.uint8)).save(os.path.join(out, 'o%03d.png' % (i + 1)))
        stats.append((n0, hf_flat(o), lum(o).mean()))
    st = np.array(stats)
    dst = os.path.join(CLIPS, name + '_final.mp4')
    run(['ffmpeg', '-v', 'error', '-y', '-framerate', str(FPS), '-i', os.path.join(out, 'o%03d.png'),
         '-c:v', 'libx264', '-preset', 'slow', '-crf', '14', '-pix_fmt', 'yuv420p', '-r', str(FPS), dst])
    pr = subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-show_entries',
                         'stream=width,height,nb_read_frames:format=duration', '-of', 'default=nw=1', dst],
                        capture_output=True, text=True).stdout.strip().replace('\n', ' | ')
    dl = np.abs(np.diff(st[:, 2]))
    print('%s: %s | grain %.4f..%.4f -> %.4f..%.4f | flicker max %.4f (median %.4f)'
          % (name, pr, st[:, 0].min(), st[:, 0].max(), st[:, 1].min(), st[:, 1].max(), dl.max(), np.median(dl)))
    picks = np.linspace(1, len(seq), 6).round().astype(int)
    strip = Image.new('RGB', (280 * 6, 490), (20, 20, 20))
    for j, k in enumerate(picks):
        strip.paste(Image.open(os.path.join(out, 'o%03d.png' % k)).resize((270, 480)), (j * 280, 5))
    strip.save(os.path.join(CLIPS, name + '_check.png'))
    return out


def main():
    todo = [a for a in sys.argv[1:] if a in ('K3', 'K4', 'K5')] or ['K3', 'K4', 'K5']
    k5 = float(sys.argv[sys.argv.index('--k5') + 1]) if '--k5' in sys.argv else 1.5
    if 'K3' in todo:
        fs, _ = extract('K3', 50, 60, 60)
        finish('K3', fs)
    if 'K4' in todo:
        fs, st = extract('K4', 0, 91, 98)
        print('K4 stretch x%.3f' % st)
        finish('K4', fs)
    if 'K5' in todo:
        n = int(round(49 * k5))
        if k5 >= 1.45:
            n = 73
        hold = 89 - n
        fs, st = extract('K5', 72, 49, n)
        print('K5: %d interpolated frames (x%.3f) + %d hold frames with 2 %% push-in' % (len(fs), st, hold))
        finish('K5', fs, hold=hold, push=0.02)


if __name__ == '__main__':
    main()
