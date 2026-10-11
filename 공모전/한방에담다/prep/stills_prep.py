# 정지 컷 전처리: 1440x2560 원본에서 블러/라벨색 덮기/하늘 클론/배경 블러 -> 1080x1920 PNG (원본 불변)
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")
BASE = HERE.rsplit("/", 1)[0]
SRC = BASE + "/img"
OUT = HERE + "/stills"
CHK = HERE + "/_check"
os.makedirs(OUT, exist_ok=True)
os.makedirs(CHK, exist_ok=True)
PAD = 120


def load(n):
    return Image.open(f"{SRC}/{n}.png").convert("RGB")


def rect_mask(size, boxes, grow=8, feather=10):
    """boxes 합집합 마스크(0~1). 이미지 가장자리에 걸친 박스는 가장자리까지 100% 유지(패딩 후 블러)."""
    w, h = size
    m = Image.new("L", (w + 2 * PAD, h + 2 * PAD), 0)
    d = ImageDraw.Draw(m)
    for (x0, y0, x1, y1) in boxes:
        a = x0 - grow if x0 > 0 else -PAD
        b = y0 - grow if y0 > 0 else -PAD
        c = x1 + grow if x1 < w else w + PAD
        e = y1 + grow if y1 < h else h + PAD
        d.rectangle([a + PAD, b + PAD, c + PAD, e + PAD], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(feather))
    return np.asarray(m.crop((PAD, PAD, PAD + w, PAD + h)), np.float32) / 255.0


def blur_boxes(im, boxes, sigma=12, grow=8, feather=10):
    bl = np.asarray(im.filter(ImageFilter.GaussianBlur(sigma)), np.float32)
    m = rect_mask(im.size, boxes, grow, feather)[..., None]
    out = np.asarray(im, np.float32) * (1 - m) + bl * m
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def label_fill(im, boxes, thr=140, pad=6):
    """박스 안에서 밝은 라벨 종이 영역(+가짜 글자 구멍)을 찾아 라벨색(중앙값)으로 덮는다. 라벨 밖(나무)은 건드리지 않는다."""
    arr = np.asarray(im, np.float32).copy()
    H, W = arr.shape[:2]
    lum = arr @ np.array([0.299, 0.587, 0.114], np.float32)
    total = np.zeros((H, W), np.float32)
    fillimg = arr.copy()
    for (x0, y0, x1, y1) in boxes:
        x0, y0, x1, y1 = max(0, x0 - pad), max(0, y0 - pad), min(W, x1 + pad), min(H, y1 + pad)
        sub = lum[y0:y1, x0:x1]
        t = float(np.percentile(sub, 50))                 # 2-means 로 박스별 밝기 임계 결정(라벨 종이 vs 나무)
        for _ in range(12):
            hi, lo = sub[sub > t], sub[sub <= t]
            if len(hi) == 0 or len(lo) == 0: break
            t = (hi.mean() + lo.mean()) / 2
        thr = t
        bright = sub > thr
        bright = ndi.binary_closing(bright, iterations=6)
        bright = ndi.binary_fill_holes(bright)
        lab, n = ndi.label(bright)
        if n == 0:
            continue
        sizes = ndi.sum(bright, lab, range(1, n + 1))
        keep = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s > 150])
        keep = ndi.binary_dilation(keep, iterations=3)
        if keep.sum() == 0:
            continue
        region = arr[y0:y1, x0:x1]
        core = (sub > thr + 12) & keep
        col = np.median(region[core], axis=0) if core.sum() > 20 else np.median(region[keep], axis=0)
        total[y0:y1, x0:x1] = np.maximum(total[y0:y1, x0:x1], keep.astype(np.float32))
        fillimg[y0:y1, x0:x1][keep] = col
    m = ndi.gaussian_filter(total, 2.0)[..., None]
    out = arr * (1 - m) + fillimg * m
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)), total


def save(im, name):
    im.resize((1080, 1920), Image.LANCZOS).save(f"{OUT}/{name}.png")


def checkjpg(im, name, crop=None, boxes=None):
    v = im.copy()
    if boxes:
        d = ImageDraw.Draw(v)
        for b in boxes:
            d.rectangle(b, outline=(255, 0, 0), width=4)
    if crop:
        v = v.crop(crop)
    else:
        v = v.resize((540, 960), Image.LANCZOS)
    v.save(f"{CHK}/{name}.jpg", quality=90)


# ---------------------------------------------------------------- 컷별 처리
def c02c():
    save(load("C02c_1"), "C02c_1")           # PASS, 편집 지시 없음 -> 리사이즈만


def c03a():
    im = load("C03a_1")
    B = [(0, 0, 520, 560), (1180, 0, 1440, 420)]
    save(blur_boxes(im, B, 12), "C03a_1")
    return B


def c03b():
    im = load("C03b_1")
    B = [(220, 180, 480, 1220), (1040, 0, 1440, 700)]      # 원본(반전 전) 좌표
    im = blur_boxes(im, B, 12)
    im = im.transpose(Image.FLIP_LEFT_RIGHT)               # 좌우 반전은 블러 후
    save(im, "C03b_1")
    return B


def c03d():
    im = load("C03d_1")
    B = [(0, 1870, 100, 1968), (0, 2138, 100, 2248), (0, 2412, 100, 2528), (798, 2152, 1002, 2306)]
    out, _ = label_fill(im, B)
    # 라벨 안에 남을 수 있는 글자 흔적을 약한 σ4 블러로 정리(박스 안 라벨 영역만)
    save(out, "C03d_1")
    return B, out


def c05():
    save(load("C05_1"), "C05_1")


def c06():
    im = load("C06_1")
    B = [(40, 2150, 1420, 2560)]
    save(blur_boxes(im, B, 12, grow=6, feather=12), "C06_1")
    return B


def c07():
    im = load("C07_1")
    B = [(0, 250, 260, 1700), (1180, 250, 1440, 1700)]
    save(blur_boxes(im, B, 12), "C07_1")
    return B


def c09d():
    save(load("C09d_1"), "C09d_1")


def c10d():
    im = load("C10d_1")
    save(im, "C10d_1")
    # 썸네일 1.2배 펀치: 캐릭터 3인 중심(중앙 x720, y1330)으로 1200x2133 크롭 -> 1080x1920
    cw, chh = 1200, 2133
    cx, cy = 720, 1330
    x0 = int(cx - cw / 2); y0 = int(cy - chh / 2)
    x0 = min(max(0, x0), 1440 - cw); y0 = min(max(0, y0), 2560 - chh)
    th = im.crop((x0, y0, x0 + cw, y0 + chh)).resize((1080, 1920), Image.LANCZOS)
    th.save(f"{OUT}/C10d_thumb.png")
    return (x0, y0, x0 + cw, y0 + chh)


def c12():
    im = load("C12_1")
    lb = [(140, 1740, 300, 1860), (1140, 1740, 1290, 1860)]       # 책상 서랍 라벨 -> 라벨색
    bb = [(1370, 560, 1440, 1020)]                                 # 우측 가장자리 종이 -> σ12 블러
    im, _ = label_fill(im, lb)
    im = blur_boxes(im, bb, 12)
    save(im, "C12_1")
    return lb + bb


def c13():
    im = load("C13_1")
    arr = np.asarray(im, np.float32)
    H, W = arr.shape[:2]
    # 보호 마스크: 쑥 머리(은녹색 잎)가 y1450 위로 튀어나온 부분. 연한 은녹색(G>=R-6)만 선택
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    prot = np.zeros((H, W), bool)
    reg = (slice(1300, 1560), slice(560, 1000))
    cand = (g >= r - 4) & (g > 110) & (b > 90) & (b < g + 20)
    prot[reg] = cand[reg]
    prot = ndi.binary_opening(prot, iterations=2)
    lab, n = ndi.label(prot)
    if n:
        sizes = ndi.sum(prot, lab, range(1, n + 1))
        prot = lab == (1 + int(np.argmax(sizes)))
    prot = ndi.binary_closing(prot, iterations=12)
    prot = ndi.binary_fill_holes(prot)
    prot = ndi.binary_dilation(prot, iterations=6)
    protf = ndi.gaussian_filter(prot.astype(np.float32), 4)
    # 배경 영역: y<1450 에서 아래쪽 경계를 y1400~1500 으로 페더
    yy = np.arange(H, dtype=np.float32)[:, None]
    region = np.clip((1500 - yy) / 100.0, 0, 1) * np.ones((1, W), np.float32)
    region = ndi.gaussian_filter(region, 3)
    m = (region * (1 - protf))[..., None]
    bl = np.asarray(im.filter(ImageFilter.GaussianBlur(20)), np.float32)
    out = arr * (1 - m) + bl * m
    out = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
    save(out, "C13_1")
    Image.fromarray((protf * 255).astype(np.uint8)).resize((360, 640)).save(f"{CHK}/C13_protect_mask.jpg")
    return out


def c15():
    im = load("C15_1")
    arr = np.asarray(im, np.float32)
    H, W = arr.shape[:2]
    bx0, by0, bx1, by1 = 560, 110, 880, 250
    g = 24
    y0, y1 = by0 - g, by1 + g
    # 좌/우 이웃 하늘 띠(행별 평균)를 가로 선형 보간 -> 그라데이션 유지 클론, 미세 입자 노이즈 보강
    L = arr[y0:y1, bx0 - 120:bx0 - 40].mean(axis=1)
    R = arr[y0:y1, bx1 + 40:bx1 + 120].mean(axis=1)
    xs = np.linspace(0, 1, (bx1 + g) - (bx0 - g))[None, :, None]
    fill = L[:, None, :] * (1 - xs) + R[:, None, :] * xs
    rng = np.random.default_rng(15)
    sd = arr[40:100, 100:400].std()                      # 깨끗한 하늘의 입자 크기
    fill = fill + rng.normal(0, min(sd, 2.0), fill.shape)
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).rectangle([bx0 - 6, by0 - 6, bx1 + 6, by1 + 6], fill=255)
    m = np.asarray(m.filter(ImageFilter.GaussianBlur(10)), np.float32)[y0:y1, bx0 - g:bx1 + g, None] / 255.0
    out = arr.copy()
    seg = out[y0:y1, bx0 - g:bx1 + g]
    out[y0:y1, bx0 - g:bx1 + g] = seg * (1 - m) + fill * m
    out = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
    save(out, "C15_1")
    return out


if __name__ == "__main__":
    c02c()
    B = c03a(); checkjpg(Image.open(f"{OUT}/C03a_1.png"), "C03a_1", boxes=[tuple(int(v * 0.75) for v in b) for b in B])
    c03b()
    B3d, o3d = c03d()
    c05(); c06(); c07(); c09d()
    c10d()
    c12(); c13(); c15()
    print("stills done")
