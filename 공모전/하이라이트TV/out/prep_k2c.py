"""v4: K2c 전처리. 1280x720 -> 1920x1080(lanczos), 사원증 가짜 글자 -> 흰 빈 카드, 커피봉지 얼룩 채도 정리(추적),
우상단 핑크/주황 번짐 완화, 색 레시피 colorbalance=rm=-0.05 (C16c 와 같은 톤). 출력 PNG: out\\_work\\frames_v2\\K2c\\%04d.png
사용: python out/prep_k2c.py [test t1,t2,...]
"""
import os, sys, subprocess
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import prep_v2 as pv

W, H = 1920, 1080
RAW = os.path.join(HERE, "_work", "k2c", "raw")
FIX = os.path.join(HERE, "_work", "k2c", "fix")
OUTD = os.path.join(HERE, "_work", "frames_v2", "K2c")
N = 116  # 0..4.8s (115 프레임 + 여유)

CARD_BOX = (1360, 850, 1510, 990)
# 커피봉지 키프레임 (시간 s, 박스@1920)
BAG_KF = [(0.0, (700, 650, 810, 830)), (3.6, (510, 600, 620, 820)), (4.95, (440, 590, 570, 780))]


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


# 사원증 흰 종이 영역(눈금 확대 화면에서 직접 읽음, 시간 s -> (x0, x1, y0, y1))
CARD_KF = [(2.5, (1394, 1466, 928, 955)), (2.8, (1393, 1462, 925, 955)), (3.0, (1386, 1452, 922, 952)),
           (3.15, (1384, 1450, 918, 950)), (3.5, (1380, 1446, 872, 916)), (3.8, (1378, 1446, 869, 914)),
           (4.0, (1376, 1444, 866, 905)), (4.2, (1380, 1448, 862, 880)), (4.3, (1395, 1470, 858, 868))]


def clean_card(a, t):
    if t < CARD_KF[0][0] or t > CARD_KF[-1][0]:
        return 0
    ts = [k[0] for k in CARD_KF]
    for (t0, b0), (t1, b1) in zip(CARD_KF[:-1], CARD_KF[1:]):
        if t0 <= t <= t1:
            u = (t - t0) / (t1 - t0)
            bx = [b0[i] + (b1[i] - b0[i]) * u for i in range(4)]
            break
    x0, x1, y0, y1 = bx
    quad = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    return pv.blank_card(a, quad, thr=16, protect=True)


# v4.1 봉지 박스 키프레임 (시간 s -> (x0,y0,x1,y1)@1920). 눈금 확대 화면에서 직접 읽음. 카메라가 1.0s 이후 움직이므로 비선형.
BAG_BOX_KF = [(0.0, (705, 647, 800, 835)), (1.0, (703, 647, 802, 835)), (2.0, (686, 641, 785, 830)), (2.5, (639, 632, 735, 829)),
              (3.0, (580, 622, 690, 822)), (3.6, (508, 599, 615, 816)), (4.3, (449, 585, 567, 813)), (4.8, (436, 588, 567, 816))]


def bag_box(t):
    ts = [k_[0] for k_ in BAG_BOX_KF]
    if t <= ts[0]:
        return BAG_BOX_KF[0][1]
    if t >= ts[-1]:
        return BAG_BOX_KF[-1][1]
    for (t0, b0), (t1, b1) in zip(BAG_BOX_KF[:-1], BAG_BOX_KF[1:]):
        if t0 <= t <= t1:
            u = (t - t0) / (t1 - t0)
            u = u * u * (3 - 2 * u)
            return tuple(b0[i] + (b1[i] - b0[i]) * u for i in range(4))


def fix_bag(a, t, seed=0):
    """v4.1: 봉지 라벨(원본에 이미 뭉개진 회색 패치와 하얀 번짐)을 봉지와 같은 크라프트지 색의 평평한 면(약한 노이즈 포함)으로 덮는다.
    라벨 영역 = 봉지 박스 안 (x 0.04-0.84w, y 0.27-0.88h) 타원형 + 페더 약 10px. 채우는 색은 라벨 영역 밖 갈색 픽셀의 다중 스케일 정규화 평균.
    마룬(소매)·살색(팔)·크림(소매) 픽셀은 건드리지 않는다."""
    bx0, by0, bx1, by1 = [int(round(v)) for v in bag_box(t)]
    pad = 18
    x0, y0, x1, y1 = max(0, bx0 - pad), max(0, by0 - pad), min(W, bx1 + pad), min(H, by1 + pad)
    roi = a[y0:y1, x0:x1].astype(np.float32)
    sat, lum = pv.hsv_arrays(roi)
    r, g, b = roi[..., 0], roi[..., 1], roi[..., 2]
    bw, bh = bx1 - bx0, by1 - by0
    yy, xx = np.mgrid[0:roi.shape[0], 0:roi.shape[1]].astype(np.float32)
    cx_, cy_ = (bx0 - x0) + 0.44 * bw, (by0 - y0) + 0.575 * bh
    ell = (((xx - cx_) / (0.46 * bw)) ** 2 + ((yy - cy_) / (0.34 * bh)) ** 2) <= 1.0
    boxm = (xx >= bx0 - x0) & (xx < bx1 - x0) & (yy >= by0 - y0) & (yy < by1 - y0)
    maroon = (g - b < 4) & (r - g > 14)
    skin = (r > g + 28) & (g > b + 12) & (lum > 130) & (sat > 0.22) & (lum < 215)
    cream = (lum > 215)
    pr = ndi.binary_opening(maroon | skin | cream, iterations=4)   # 작은 얼룩(라벨 하이라이트)은 보호하지 않음, 팔·소매 같은 큰 덩어리만
    protect = ndi.binary_dilation(pr, iterations=2)
    kraft = (r - b > 22) & (r >= g - 1) & (r - g < 40) & (sat > 0.27) & (lum > 40) & (lum < 135)
    src = (kraft & boxm & ~ndi.binary_dilation(ell, iterations=6) & ~protect).astype(np.float32)
    if src.sum() < 150:
        return
    base = roi.copy()
    filled = np.zeros(roi.shape[:2], bool)
    for sg in (8.0, 16.0, 32.0, 64.0):
        wb = ndi.gaussian_filter(src, sg)
        cur = np.stack([ndi.gaussian_filter(roi[..., c] * src, sg) / np.maximum(wb, 1e-4) for c in range(3)], -1)
        use = (wb > 0.03) & ~filled
        base[use] = cur[use]
        filled |= use
    hf = roi - np.stack([ndi.gaussian_filter(roi[..., c], 1.5) for c in range(3)], -1)
    sd = float(hf[src > 0.5].std())
    rng = np.random.RandomState(777 + seed)
    nz = ndi.gaussian_filter(rng.randn(*roi.shape[:2]).astype(np.float32), 0.7)[..., None] * sd * 1.2
    zone = (ell & boxm & ~protect).astype(np.float32)
    al = ndi.gaussian_filter(zone, 4.0)[..., None]
    al = np.clip(al * 1.25, 0, 1)
    a[y0:y1, x0:x1] = np.clip(roi * (1 - al) + (base + nz) * al, 0, 255).astype(np.uint8)


def fix_pink_corner(a):
    """우상단 핑크/주황 번짐: 해당 영역 채도 -35%, 약간 어둡게(페더)."""
    x0, y0, x1, y1 = 1250, 0, 1920, 560
    roi = a[y0:y1, x0:x1].astype(np.float32)
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    mx = np.clip((xx - 1250) / 250.0, 0, 1)
    my = np.clip((560 - yy) / 220.0, 0, 1)
    m = (mx * my)[..., None]
    lum = (roi * np.array([0.299, 0.587, 0.114], np.float32)).sum(-1, keepdims=True)
    pink = np.clip(((roi[..., 0] - roi[..., 1]) - 30) / 40.0, 0, 1)[..., None]  # 분홍/주황 정도
    k = m * (0.30 + 0.25 * pink)
    out = roi * (1 - k) + lum * k
    out *= (1 - 0.10 * m)
    a[y0:y1, x0:x1] = np.clip(out, 0, 255).astype(np.uint8)


def process(i, a):
    t = i / 24.0
    clean_card(a, t)
    fix_bag(a, t, i)
    fix_pink_corner(a)
    return a


def main():
    os.makedirs(FIX, exist_ok=True)
    os.makedirs(OUTD, exist_ok=True)
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        ts = [float(x) for x in sys.argv[2].split(",")]
        os.makedirs(os.path.join(HERE, "_work", "k2c", "t"), exist_ok=True)
        for t in ts:
            i = int(round(t * 24))
            a = np.asarray(Image.open(os.path.join(RAW, "%04d.png" % (i + 1))).convert("RGB")).copy()
            process(i, a)
            Image.fromarray(a).save(os.path.join(HERE, "_work", "k2c", "t", "k2c_%.2f.png" % t))
        return
    for i in range(N):
        a = np.asarray(Image.open(os.path.join(RAW, "%04d.png" % (i + 1))).convert("RGB")).copy()
        process(i, a)
        Image.fromarray(a).save(os.path.join(FIX, "%04d.png" % (i + 1)))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(FIX, "%04d.png"), "-vf", "colorbalance=rm=-0.05",
                    "-start_number", "1", os.path.join(OUTD, "%04d.png")], check=True)
    print("done", len(os.listdir(OUTD)))


if __name__ == "__main__":
    main()
