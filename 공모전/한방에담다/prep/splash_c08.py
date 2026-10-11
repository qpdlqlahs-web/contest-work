# C08 물보라 합성 (clips_prep.py C08 실행 후). 좌표는 지시서의 1440x2560 기준 -> 1080x1920 = x0.75
# 물보라: 출력 3.33~3.8s, 정점 3.4s, 중심 (430,1780), 폭 360, 물방울 y1600까지, 물방울 8개 + 파문 2개
# 감초 반사: 클립에서 실제 반사는 (약 x520-720, y1870-2090 @1440) 에 있어 파문이 안 덮음 -> σ15 블러를 3.0~3.4s 에 걸쳐 램프
import json, math, os, random, sys
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import clips_prep as cp

K = 0.75
FPS = 24
CX, CY = 430 * K, 1780 * K        # 물보라 중심 (1080 좌표) = (322.5, 1335)
SS = 3                              # 슈퍼샘플
RX0, RY0, RX1, RY1 = 90, 1100, 600, 1460   # 레이어 작업 영역(1080 좌표)
random.seed(8)

# 물방울 8개: (dx, 최대 높이, 시작 오프셋(초), 비행시간, 반경)
DROPS = [(-128, 70, 0.00, 0.40, 5), (-92, 126, 0.01, 0.46, 10), (-58, 84, 0.03, 0.40, 6),
         (-22, 135, 0.00, 0.47, 12), (14, 100, 0.02, 0.43, 7), (44, 128, 0.01, 0.46, 9),
         (84, 76, 0.04, 0.38, 5.5), (128, 112, 0.02, 0.44, 8),
         (-105, 98, 0.05, 0.41, 3.5), (30, 90, 0.06, 0.40, 3.5), (108, 130, 0.03, 0.45, 3.5)]  # 마지막 3개: 작은 위성 방울
SC = 1.4   # 지시서 폭 360px(@1440) 그대로면 폰에서 안 보여(클립 속 탕이 정지컷보다 작음) 1.4배 확대
DROPS = [(d[0] * SC, min(d[1] * SC, 150), d[2], d[3], d[4] * (SC ** 0.8)) for d in DROPS]
T_START = 3.33
UA = 0.28   # 정점 도달 비율(빠르게 솟고 천천히 떨어짐) -> 정점 ~3.45s 부근에서 최대 높이


def drop_pos(d, t):
    dx, h, off, T, r = d
    u = (t - (T_START + off)) / T
    if u <= 0 or u >= 1:
        return None
    hh = h * (1 - ((UA - u) / UA) ** 2) if u < UA else h * (1 - ((u - UA) / (1 - UA)) ** 2)
    return CX + dx * (0.25 + 0.75 * u) * 1.0, CY - hh, u


def S(v):
    return v * SS


def draw_layer(t):
    W, H = (RX1 - RX0) * SS, (RY1 - RY0) * SS
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ox, oy = RX0, RY0

    def P(x, y):
        return ((x - ox) * SS, (y - oy) * SS)

    # --- 파문 2개: 납작한 타원 링
    for (st, rmax, life) in [(T_START, 135 * SC, 0.50), (T_START + 0.07, 100 * SC, 0.46)]:
        p = (t - st) / life
        if p <= 0 or p >= 1:
            continue
        e = 1 - (1 - p) ** 2
        rx = 14 + (rmax - 14) * e
        ry = rx * 0.23
        a = (1 - p) ** 1.1
        ring = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        rd = ImageDraw.Draw(ring)
        cx, cy = P(CX, CY)
        w = max(1, int(S(5.5 * (1 - 0.6 * p))))
        # 그림자 링(호박색, 약간 아래) + 하이라이트 링(흰색)
        rd.ellipse([cx - S(rx), cy - S(ry) + S(3), cx + S(rx), cy + S(ry) + S(3)], outline=(150, 80, 20, int(150 * a)), width=w + SS)
        rd.ellipse([cx - S(rx), cy - S(ry), cx + S(rx), cy + S(ry)], outline=(255, 248, 225, int(215 * a)), width=w)
        # 링 안쪽 은은한 밝은 면
        rd.ellipse([cx - S(rx * 0.92), cy - S(ry * 0.92), cx + S(rx * 0.92), cy + S(ry * 0.92)], fill=(255, 235, 190, int(38 * a)))
        lay = Image.alpha_composite(lay, ring)

    # --- 중앙 물기둥(돔 + 둥근 물기둥 5개): 3.33~3.4 솟고 이후 가라앉음
    pm = (t - T_START) / 0.42
    if 0 < pm < 1:
        k = math.sin(math.pi * pm / 0.35 * 0.5) if pm < 0.35 else (1 - (pm - 0.35) / 0.65) ** 1.5
        hgt = 52 * SC * k
        wid = (46 + 24 * pm) * SC
        mound = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        md = ImageDraw.Draw(mound)
        cx, cy = P(CX, CY)
        lw = max(1, int(round(S(2))))
        md.pieslice([cx - S(wid), cy - S(hgt * 0.55), cx + S(wid), cy + S(hgt * 0.55)], 180, 360, fill=(255, 214, 150, 105), outline=(165, 90, 28, 150), width=lw)
        for i, (fx, fk) in enumerate(((-0.62, 0.62), (-0.30, 0.9), (0.02, 1.0), (0.34, 0.84), (0.66, 0.58))):
            fh = hgt * fk
            fw = S((7.5 - 2.5 * abs(fx)) * SC ** 0.8)
            fxp = cx + S(wid * fx * (0.8 + 0.2 * pm))
            md.ellipse([fxp - fw, cy - S(fh) - fw, fxp + fw, cy - S(2) + fw * 0.4], fill=(255, 218, 156, 118), outline=(165, 90, 28, 165), width=lw)
            md.ellipse([fxp - fw * 0.55, cy - S(fh) - fw * 0.7, fxp - fw * 0.05, cy - S(fh) + fw * 0.2], fill=(255, 255, 248, 235))
        md.arc([cx - S(wid * 0.8), cy - S(hgt * 0.5), cx - S(wid * 0.2), cy + S(hgt * 0.3)], 190, 270, fill=(255, 255, 245, 220), width=max(1, int(round(S(2.5)))))
        mound = mound.filter(ImageFilter.GaussianBlur(S(0.5)))
        lay = Image.alpha_composite(lay, mound)

    # --- 물방울: 서브프레임 4샘플 모션 블러(1/48s 셔터), 둥근 방울 + 하이라이트
    acc = np.zeros((H, W, 4), np.float32)
    NS = 4
    for si in range(NS):
        ts = t - (1 / FPS) * 0.5 * (si / (NS - 1))
        dl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dd = ImageDraw.Draw(dl)
        for d in DROPS:
            pos = drop_pos(d, ts)
            if not pos:
                continue
            x, y, u = pos
            r = d[4] * 1.3 * (0.9 + 0.2 * math.sin(math.pi * u)) * (1 - 0.3 * max(0, u - 0.8) / 0.2)
            pos2 = drop_pos(d, ts - 0.02)
            spn = min(1.0, (math.hypot(x - pos2[0], y - pos2[1]) / 6.0) if pos2 else 0.0)   # 속도에 따라 세로로 늘어남
            a = 1.0 if u < 0.9 else (1 - u) / 0.1
            cxp, cyp = P(x, y)
            rr = S(r)
            lw = max(1, int(round(S(1.8))))
            ry = rr * (1.05 + 0.55 * spn)
            rxx = rr * (1 - 0.12 * spn)
            dd.ellipse([cxp - rxx, cyp - ry, cxp + rxx, cyp + ry], fill=(255, 216, 152, int(100 * a)), outline=(165, 90, 28, int(170 * a)), width=lw)
            hr = rr * 0.36
            hx, hy = cxp - rr * 0.38, cyp - rr * 0.42
            dd.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=(255, 255, 250, int(240 * a)))
            dd.ellipse([cxp + rr * 0.1, cyp + rr * 0.25, cxp + rr * 0.62, cyp + rr * 0.7], fill=(255, 240, 200, int(110 * a)))
        arr = np.asarray(dl, np.float32)
        acc += arr / NS
    dl = Image.fromarray(np.clip(acc, 0, 255).astype(np.uint8), "RGBA")
    dl = dl.filter(ImageFilter.GaussianBlur(S(0.4)))
    lay = Image.alpha_composite(lay, dl)
    return lay.resize((RX1 - RX0, RY1 - RY0), Image.LANCZOS)


# 감초 반사 블러(σ15) — 실제 반사 위치(1080 좌표)
RCX, RCY, RRX, RRY = 463, 1482, 110, 96


def reflect_amount(t):
    return float(np.clip((t - 2.9) / 0.4, 0, 1))


def reflect_blur(img, amt):
    """감초 반사 제거(σ15 블러 대체): 타원 좌/우 물 띠(행별 중앙값, 꽃·잎·창 반사 제외)를 가로 보간해 채우고,
    원본 σ15 블러를 15% 섞어 질감 유지. 타원 마스크 페더, amt(0~1)만큼 적용."""
    if amt <= 0.001:
        return img
    x0, y0, x1, y1 = RCX - 190, RCY - 190, RCX + 190, RCY + 190
    crop = img.crop((x0, y0, x1, y1))
    arr = np.asarray(crop, np.float32)
    from scipy.ndimage import gaussian_filter, gaussian_filter1d
    H, W = arr.shape[:2]
    lo, ro = 190 - RRX - 40, 190 + RRX + 18        # 좌/우 샘플 띠 시작
    def rowmed(a):                                   # 잎(녹색)·꽃(노랑) 픽셀 제외한 행별 중앙값
        ok = (a[..., 1] < a[..., 0] * 0.85) & (a[..., 2] < a[..., 1] * 0.85) & (a[..., 0] > 125)
        b = np.where(ok[..., None], a, np.nan)
        with np.errstate(all="ignore"):
            med = np.nanmedian(b, axis=1)
        allmed = np.median(a, axis=1)
        med = np.where(np.isnan(med), allmed, med)
        for c in range(3):                           # 비어있는 행은 위아래 보간
            v = med[:, c]; idx = np.arange(len(v)); good = ~np.isnan(v)
            med[:, c] = np.interp(idx, idx[good], v[good])
        return med
    L = rowmed(arr[:, lo:lo + 30])
    R = rowmed(arr[:, ro:ro + 30])
    L = gaussian_filter1d(L, 10, axis=0)
    R = gaussian_filter1d(R, 10, axis=0)
    rows = np.arange(H) + y0
    wR = np.clip((rows - 1440) / 40.0, 0, 1)[:, None]   # 위쪽 행은 우측 띠에 밝은 반사가 있어 좌측만 사용
    xs = np.linspace(0, 1, W)[None, :, None]
    Rm = L * (1 - wR) + R * wR
    fill = L[:, None, :] * (1 - xs) + Rm[:, None, :] * xs
    b15 = np.asarray(crop.filter(ImageFilter.GaussianBlur(15)), np.float32)
    rep = 0.85 * fill + 0.15 * b15
    m = Image.new("L", crop.size, 0)
    ImageDraw.Draw(m).ellipse([190 - RRX, 190 - RRY, 190 + RRX, 190 + RRY], fill=255)
    m = np.asarray(m.filter(ImageFilter.GaussianBlur(18)), np.float32)[..., None] / 255.0 * amt
    out = arr * (1 - m) + rep * m
    img = img.copy()
    img.paste(Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)), (x0, y0))
    return img


def build(check_dir):
    base = json.load(open(f"{cp.TMP}/C08_frames.json"))
    outdir = f"{cp.TMP}/C08_final"
    os.makedirs(outdir, exist_ok=True)
    out = []
    cache = {}
    for i, path in enumerate(base):
        t = i / FPS
        key = (path, round(t, 3) if t < 3.8 else 0)
        img = Image.open(path).convert("RGB")
        img = reflect_blur(img, reflect_amount(t))
        if t >= T_START - 1e-6:
            lay = draw_layer(t)
            img.paste(lay, (RX0, RY0), lay)
        p = f"{outdir}/f{i:03d}.png"
        img.save(p)
        out.append(p)
    return out


if __name__ == "__main__":
    frames = build(None)
    cp.encode(frames, "C08")
    # 0.1초 간격 확인 이미지(중심부 확대 + 전체)
    chk = os.path.join(os.path.dirname(cp.OUT), "_check")
    os.makedirs(chk, exist_ok=True)
    tiles = []
    for ti in range(30, 39):
        fi = min(round(ti / 10 * FPS), len(frames) - 1)
        im = Image.open(frames[fi]).convert("RGB")
        im.crop((60, 1080, 660, 1680)).save(f"{chk}/C08_t{ti/10:.1f}s_crop.jpg", quality=92)
        im.resize((540, 960)).save(f"{chk}/C08_t{ti/10:.1f}s_full.jpg", quality=88)
    print("done", len(frames))
