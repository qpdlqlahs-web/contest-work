"""하이라이트TV 「나, 주연」 소스 전처리 (정지 컷 + Kling 클립). 원본은 읽기만 한다.
사용: python prep/preprocess.py stills | clips | all  [이름...]
"""
import os, sys, subprocess, tempfile, shutil
import numpy as np
from PIL import Image, ImageFilter, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "img")
CLIPS = os.path.join(ROOT, "clips")
OUT_S = os.path.join(ROOT, "prep", "stills")
OUT_C = os.path.join(ROOT, "prep", "clips")
TMP = os.path.join(ROOT, "prep", "_tmp")
FFMPEG = "ffmpeg"
W, H = 1920, 1080

# ---------- 색 레시피 (재생성_편집목록.md) ----------
DRAMA = "colorbalance=rm=-0.04:gm=0.05:gh=0.03,eq=gamma=1.12"
DRAMA7 = "colorbalance=rm=-0.04:gm=0.07:gh=0.03,eq=gamma=1.12"
COFFEE = "colorbalance=gm=-0.03:rh=0.02,eq=gamma=0.93"
REAL = "eq=brightness=-0.05,colorbalance=gm=0.02"
STILL_RECIPE = {
    "C02": COFFEE, "C03": COFFEE,
    "C04": DRAMA, "C05": "colorbalance=gm=0.02", "C06b": "colorbalance=gm=0.02",
    "C07": REAL, "C08": DRAMA, "C09": DRAMA7, "C10": DRAMA, "C11b": DRAMA7,
    "C12": DRAMA, "C13b": DRAMA, "C14": DRAMA, "C15": DRAMA7, "C15b": DRAMA,
    "C16c": "colorbalance=rm=-0.05",
    "C17b": "colorbalance=rm=-0.06:gm=0.04,eq=gamma=1.05",
    "C18": DRAMA, "C19a": DRAMA, "C19b": DRAMA, "C19c": DRAMA,
    "C20": REAL, "C21": REAL, "K4Sb": REAL,
}
# 블러: (x0, y0, x1, y1) @1920x1080 (정사각 축소 기준 좌표), sigma
STILL_BLUR = {
    "C02": [((688, 508, 785, 664), 12)],
    "C03": [((410, 580, 545, 795), 12)],
    "C14": [((720, 972, 870, 1002), 12), ((1083, 963, 1203, 1035), 12)],
    "C19a": [((1606, 182, 1690, 220), 12)],
    "C16c": [((700, 690, 778, 815), 12), ((1424, 842, 1498, 874), 10)],
}
# 16:9가 아닌 원본 (2752x1536) 은 가운데 16:9로 자른다.


def feather_blur(arr, box, sigma, feather=8, strength=1.0):
    """arr: HxWx3 uint8 (제자리 수정). box: x0,y0,x1,y1. 경계 페더 + 가우시안 블러."""
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    m = int(sigma * 3 + feather + 2)
    X0, Y0, X1, Y1 = max(0, x0 - m), max(0, y0 - m), min(arr.shape[1], x1 + m), min(arr.shape[0], y1 + m)
    roi = Image.fromarray(arr[Y0:Y1, X0:X1])
    blur = np.asarray(roi.filter(ImageFilter.GaussianBlur(sigma))).astype(np.float32)
    mask = Image.new("L", (X1 - X0, Y1 - Y0), 0)
    ImageDraw.Draw(mask).rectangle([x0 - X0, y0 - Y0, x1 - X0 - 1, y1 - Y0 - 1], fill=255)
    mask = np.asarray(mask.filter(ImageFilter.GaussianBlur(feather / 2.0))).astype(np.float32) / 255.0
    mask = np.clip(mask * 1.0, 0, 1)[..., None] * strength
    orig = arr[Y0:Y1, X0:X1].astype(np.float32)
    arr[Y0:Y1, X0:X1] = np.clip(orig * (1 - mask) + blur * mask, 0, 255).astype(np.uint8)


def remove_spot(arr, cx, cy, r, feather=6):
    """마스크 정규화 확산으로 작은 반사점을 주변 피부색으로 메운다."""
    m = int(r * 3 + feather + 10)
    X0, Y0 = max(0, cx - m), max(0, cy - m)
    X1, Y1 = min(arr.shape[1], cx + m), min(arr.shape[0], cy + m)
    roi = arr[Y0:Y1, X0:X1].astype(np.float32)
    yy, xx = np.mgrid[Y0:Y1, X0:X1]
    d = np.hypot(xx - cx, yy - cy)
    hole = (d <= r + 2).astype(np.float32)
    w = 1 - hole
    out = np.zeros_like(roi)
    wb = np.asarray(Image.fromarray((w * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r * 0.9))).astype(np.float32) / 255
    for c in range(3):
        ch = Image.fromarray(np.clip(roi[..., c] * w, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r * 0.9))
        out[..., c] = np.asarray(ch).astype(np.float32) / np.maximum(wb, 1e-3) * (wb > 0.02) + roi[..., c] * (wb <= 0.02)
    alpha = np.clip((r + feather - d) / feather, 0, 1)[..., None]
    arr[Y0:Y1, X0:X1] = np.clip(roi * (1 - alpha) + out * alpha, 0, 255).astype(np.uint8)


def load_1080(name):
    im = Image.open(os.path.join(IMG, name + "_1.png")).convert("RGB")
    w, h = im.size
    crop_info = None
    if abs(w / h - 16 / 9) > 0.002:
        nw = int(round(h * 16 / 9))
        x0 = (w - nw) // 2
        im = im.crop((x0, 0, x0 + nw, h))
        crop_info = (w, nw, x0)
    return im.resize((W, H), Image.LANCZOS), crop_info


def conv_box(box, crop_info):
    """정사각 축소(전체폭→1920) 좌표를 16:9 크롭 후 좌표로 변환."""
    if not crop_info:
        return box
    w, nw, x0 = crop_info
    f = (w / 1920.0)
    s = 1920.0 / nw
    x0b, y0b, x1b, y1b = box
    return ((x0b * f - x0) * s, y0b, (x1b * f - x0) * s, y1b)


def fix_c18(img):
    """C18: 시곗바늘 12시(분침) 유지 + 시침을 6시 방향으로 합성 => 6:00. 2560x1440에서 작업."""
    # 허브 중심 (2560 기준)
    cx, cy = 1289, 537
    big = img.resize((2560, 1440), Image.LANCZOS) if img.size != (2560, 1440) else img
    return big, (cx, cy)


def process_still(name):
    os.makedirs(TMP, exist_ok=True)
    full = Image.open(os.path.join(IMG, name + "_1.png")).convert("RGB")
    if name == "C18":
        a = np.asarray(full).astype(np.float32)
        cx, cy = 1289, 537
        # 시침(6시 방향, 분침보다 짧고 굵게)을 슈퍼샘플링으로 그린다
        col = a[cy - 120:cy - 100, cx - 3:cx + 4].reshape(-1, 3).mean(0)  # 분침 색 샘플
        ss = 4
        L = 130  # 길이(px, 2560 기준) — 분침 약 190px의 약 0.68
        wd = 19
        pad = 40
        lay = Image.new("L", ((wd + pad * 2) * ss, (L + pad * 2) * ss), 0)
        d = ImageDraw.Draw(lay)
        d.rounded_rectangle([pad * ss, pad * ss, (pad + wd) * ss, (pad + L) * ss], radius=int(wd * ss * 0.25), fill=255)
        lay = lay.resize((wd + pad * 2, L + pad * 2), Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.7))
        al = np.asarray(lay).astype(np.float32)[..., None] / 255.0
        ox = int(round(cx - (wd / 2.0) - pad)); oy = int(round(cy - pad))
        reg = a[oy:oy + al.shape[0], ox:ox + al.shape[1]]
        a[oy:oy + al.shape[0], ox:ox + al.shape[1]] = reg * (1 - al) + col * al
        # 허브를 다시 위에 얹는다(원본 허브 픽셀 복원)
        orig = np.asarray(full).astype(np.float32)
        yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
        hub = (np.hypot(xx - cx, yy - cy) <= 15).astype(np.float32)
        hubm = np.asarray(Image.fromarray((hub * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.0))).astype(np.float32)[..., None] / 255
        a = a * (1 - hubm) + orig * hubm
        full = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    w, h = full.size
    crop_info = None
    if abs(w / h - 16 / 9) > 0.002:
        nw = int(round(h * 16 / 9)); x0 = (w - nw) // 2
        full = full.crop((x0, 0, x0 + nw, h)); crop_info = (w, nw, x0)
    im = full.resize((W, H), Image.LANCZOS)
    arr = np.asarray(im).copy()
    for box, sg in STILL_BLUR.get(name, []):
        feather_blur(arr, conv_box(box, crop_info), sg, feather=10)
    if name == "C21":
        remove_spot(arr, 899, 246, 15, feather=8)
    tmp_in = os.path.join(TMP, name + "_in.png")
    Image.fromarray(arr).save(tmp_in)
    out = os.path.join(OUT_S, name + ".png")
    subprocess.run([FFMPEG, "-v", "error", "-y", "-i", tmp_in, "-vf", STILL_RECIPE[name], "-frames:v", "1", out], check=True)
    print("still", name, "->", out)


# ---------- 클립 ----------
def lerp_box(kf, t):
    ts = [k[0] for k in kf]
    if t <= ts[0]:
        return kf[0][1]
    if t >= ts[-1]:
        return kf[-1][1]
    for (t0, b0), (t1, b1) in zip(kf[:-1], kf[1:]):
        if t0 <= t <= t1:
            u = (t - t0) / (t1 - t0)
            return tuple(b0[i] + (b1[i] - b0[i]) * u for i in range(4))


# K2b 명찰 키프레임: (원본시간 s, 박스@1920). 패딩 포함.
K2B_BADGE = [
    (0.0, (1424, 684, 1494, 836)),
    (0.5, (1424, 713, 1497, 852)),
    (1.0, (1430, 679, 1507, 836)),
    (1.5, (1435, 674, 1510, 836)),
    (2.0, (1424, 679, 1518, 845)),
    (2.5, (1419, 684, 1518, 852)),
    (3.0, (1435, 695, 1513, 863)),
    (3.5, (1438, 700, 1518, 863)),
    (4.0, (1438, 695, 1518, 868)),
    (4.5, (1451, 700, 1539, 877)),
    (5.04, (1451, 700, 1539, 877)),
]
K2B_BAG = (690, 505, 800, 665)

K1_BADGE_BOX = (1290, 696, 1400, 802)


def purple_fix(a):
    """K1 우상단 보라 번짐 (1650-1920, 0-360): 국소 채도 감소 + 비네팅. ROI만 처리."""
    x0, y0, x1, y1 = 1450, 0, 1920, 520
    roi = a[y0:y1, x0:x1].astype(np.float32)
    yy, xx = np.mgrid[y0:y1, x0:x1]
    # 기준 영역 (1650-1920, 0-360) 안쪽 100%, 바깥 쪽으로 페더
    fx = np.clip((xx - 1480) / 170.0, 0, 1)
    fy = np.clip((420 - yy) / 160.0, 0, 1)
    m = (fx * fy)[..., None]
    lum = (roi * np.array([0.2126, 0.7152, 0.0722], np.float32)).sum(-1, keepdims=True)
    sat_amt = 0.55
    des = roi * (1 - sat_amt * m) + lum * (sat_amt * m)
    # 비네팅: 우상단 코너에서 방사형 어둡게
    dd = np.hypot((xx - 1920) / 420.0, (yy - 0) / 420.0)
    vig = 1 - 0.16 * np.clip(1 - dd, 0, 1) ** 1.2
    des = des * vig[..., None]
    a[y0:y1, x0:x1] = np.clip(des, 0, 255).astype(np.uint8)


CLIP_CFG = {
    # name: (src, start_frame, end_frame(exclusive), recipe, hold_frames)
    "K1": dict(src="K1.mp4", s=12, e=120, recipe=None, hold=0),
    "K2b": dict(src="K2b.mp4", s=12, e=120, recipe="colorbalance=rm=-0.04:gm=0.05", hold=0),
    "K3": dict(src="K3.mp4", s=0, e=120, recipe=DRAMA, hold=0),
    "K4": dict(src="K4.mp4", s=0, e=73, recipe=REAL, hold=10),
}


def process_clip(name, limit=None):
    cfg = CLIP_CFG[name]
    os.makedirs(TMP, exist_ok=True)
    src = os.path.join(CLIPS, cfg["src"])
    out = os.path.join(OUT_C, name + ".mp4")
    s, e = cfg["s"], cfg["e"]
    vf_dec = (f"trim=start_frame={s}:end_frame={e},setpts=PTS-STARTPTS,"
              f"scale={W}:{H}:flags=lanczos:in_color_matrix=bt709:in_range=tv,format=rgb24")
    dec = subprocess.Popen([FFMPEG, "-v", "error", "-i", src, "-vf", vf_dec, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                           stdout=subprocess.PIPE)
    vf_enc = (cfg["recipe"] + "," if cfg["recipe"] else "") + \
             "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p"
    enc = subprocess.Popen([FFMPEG, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-framerate", "24", "-i", "-", "-vf", vf_enc, "-an", "-c:v", "libx264", "-preset", "slow",
                            "-crf", "12", "-r", "24", "-colorspace", "bt709", "-color_primaries", "bt709",
                            "-color_trc", "bt709", "-color_range", "tv", "-movflags", "+faststart", out],
                           stdin=subprocess.PIPE)
    fsz = W * H * 3
    n = 0
    last = None
    while True:
        buf = dec.stdout.read(fsz)
        if len(buf) < fsz:
            break
        a = np.frombuffer(buf, np.uint8).reshape(H, W, 3).copy()
        t = (s + n) / 24.0  # 원본 시간
        if name == "K1":
            purple_fix(a)
            # 명찰 무늬: 1.3~3.0s (지시 2.0~2.6s 보다 넓힘), 양 끝 4프레임 램프
            t0, t1, ramp = 1.45, 3.0, 3 / 24.0
            if t0 - ramp <= t <= t1 + ramp:
                st = min(1.0, (t - (t0 - ramp)) / ramp, ((t1 + ramp) - t) / ramp)
                st = max(0.0, st)
                if st > 0:
                    feather_blur(a, K1_BADGE_BOX, 10, feather=12, strength=st)
        if name == "K2b":
            feather_blur(a, K2B_BAG, 12, feather=14)
            feather_blur(a, lerp_box(K2B_BADGE, t), 10, feather=12)
        enc.stdin.write(a.tobytes())
        last = a
        n += 1
        if limit and n >= limit:
            break
    for _ in range(cfg["hold"]):
        enc.stdin.write(last.tobytes())
    enc.stdin.close()
    enc.wait()
    dec.stdout.close()
    dec.terminate()
    print("clip", name, "frames", n, "+hold", cfg["hold"], "->", out)


if __name__ == "__main__":
    os.makedirs(OUT_S, exist_ok=True); os.makedirs(OUT_C, exist_ok=True)
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    names = sys.argv[2:]
    if mode in ("stills", "all"):
        for n in (names or STILL_RECIPE.keys()):
            if n in STILL_RECIPE:
                process_still(n)
    if mode in ("clips", "all"):
        for n in (names or CLIP_CFG.keys()):
            if n in CLIP_CFG:
                process_clip(n)
    shutil.rmtree(TMP, ignore_errors=True)
