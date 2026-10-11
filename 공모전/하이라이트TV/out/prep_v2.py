"""v2 전처리: K1/K2b 재처리 (명찰 블러 -> 인쇄 지우기, K2b 커피봉지 -> 타일 클론, K2b 드라마 색), C19a 간판, C19c 배경/렌즈.
원본(clips, img)은 읽기만 한다. 출력은 out\\_work\\v2\\ (prep 원본은 덮어쓰지 않는다).
사용: python out/prep_v2.py clips|stills
"""
import os, sys, subprocess
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
from scipy import ndimage as ndi
import scipy.sparse as sp
from scipy.sparse.linalg import spsolve

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "prep"))
import preprocess as pp  # purple_fix, K2B_BADGE, lerp_box, feather_blur, STILL 함수

OUT = os.path.join(HERE, "_work", "v2")
W, H = 1920, 1080


def hsv_arrays(roi):
    r, g, b = roi[..., 0], roi[..., 1], roi[..., 2]
    mx = roi.max(-1)
    mn = roi.min(-1)
    sat = (mx - mn) / np.maximum(mx, 1)
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    return sat, lum


def gblur(x, s):
    return ndi.gaussian_filter(x, s)


def fill_print(a, box, feather=1.5, dil=2):
    """카드 안 인쇄(글자·사진·붉은 띠)를 카드 바탕색으로 지운다.
    흰색/연회색(카드·블라우스) 영역 안에 완전히 갇힌 비-흰색 덩어리 = 인쇄. 상자 경계에 닿는 것(끈·손·소매)은 건드리지 않는다."""
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    roi = a[y0:y1, x0:x1].astype(np.float32)
    sat, lum = hsv_arrays(roi)
    white = (sat < 0.22) & (lum > 130)
    white = ndi.binary_opening(white, iterations=1) | white
    filled = ndi.binary_fill_holes(white)
    holes = filled & ~white
    if not holes.any():
        return 0
    # 상자 가장자리에 닿는 덩어리는 제외 (이미 fill_holes 가 열린 영역은 구멍으로 보지 않는다)
    holes = ndi.binary_dilation(holes, iterations=dil)
    holes &= ndi.binary_dilation(filled, iterations=1)
    wf = white.astype(np.float32)
    base = np.zeros_like(roi)
    wb = gblur(wf, 5.0)
    for c in range(3):
        base[..., c] = gblur(roi[..., c] * wf, 5.0) / np.maximum(wb, 1e-3)
    alpha = gblur(holes.astype(np.float32), feather)[..., None]
    alpha = np.clip(alpha * 1.4, 0, 1) * (wb[..., None] > 0.05)
    a[y0:y1, x0:x1] = np.clip(roi * (1 - alpha) + base * alpha, 0, 255).astype(np.uint8)
    return int(holes.sum())


# ---------------------------------------------------------------- K2b 커피봉지 제거 (타일 클론)
BAG_BOX = (688, 500, 812, 690)
TILE_PITCH = 62


def bag_mask(a):
    x0, y0, x1, y1 = BAG_BOX
    roi = a[y0:y1, x0:x1].astype(np.float32)
    sat, lum = hsv_arrays(roi)
    r, g, b = roi[..., 0], roi[..., 1], roi[..., 2]
    m = ((r - b) > 14) & ((r - b) / np.maximum(lum, 1) > 0.27) & (lum < 112) & (r >= g - 2)
    m = ndi.binary_closing(m, iterations=4)
    m = ndi.binary_opening(m, iterations=3)
    lab, n = ndi.label(m)
    if n == 0:
        return None
    sizes = ndi.sum(m, lab, range(1, n + 1))
    m = lab == (int(np.argmax(sizes)) + 1)
    m = ndi.binary_fill_holes(ndi.binary_closing(m, iterations=3))
    ys, xs = np.where(m)
    top, bot = ys.min(), ys.max()
    # 왼쪽 가장자리(위쪽 60% 행의 중앙값)로 컵 그림자 돌출 제거, 행 단위로 양 끝 사이를 채움(라벨 포함)
    rows = np.arange(top, bot + 1)
    lefts, rights = [], []
    for y in rows:
        xx = np.where(m[y])[0]
        lefts.append(xx.min() if len(xx) else -1)
        rights.append(xx.max() if len(xx) else -1)
    lefts, rights = np.array(lefts), np.array(rights)
    n60 = max(1, int(len(rows) * 0.6))
    left_ref = int(np.median(lefts[:n60][lefts[:n60] >= 0]))
    out = np.zeros_like(m)
    for i, y in enumerate(rows):
        if lefts[i] < 0:
            continue
        l = max(lefts[i], left_ref - 6)
        out[y, l:rights[i] + 1] = True
    out = ndi.binary_dilation(out, iterations=4)
    full = np.zeros((H, W), bool)
    full[y0:y1, x0:x1] = out
    return full, y0 + top, y0 + bot


def poisson_fill(a, mask, guide):
    """seamless clone: mask 안을 guide의 기울기로 채우고 경계는 a의 값에 맞춘다 (채널별 이산 푸아송)"""
    ys, xs = np.where(mask)
    y0, y1, x0, x1 = ys.min() - 2, ys.max() + 3, xs.min() - 2, xs.max() + 3
    m = mask[y0:y1, x0:x1]
    idx = -np.ones(m.shape, int)
    pts = np.argwhere(m)
    idx[m] = np.arange(len(pts))
    n = len(pts)
    rows, cols, vals = [], [], []
    A = a[y0:y1, x0:x1].astype(np.float64)
    G = guide[y0:y1, x0:x1].astype(np.float64)
    b = np.zeros((n, 3))
    for k, (y, x) in enumerate(pts):
        rows.append(k); cols.append(k); vals.append(4.0)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            yy, xx = y + dy, x + dx
            b[k] += G[y, x] - G[yy, xx]
            if m[yy, xx]:
                rows.append(k); cols.append(idx[yy, xx]); vals.append(-1.0)
            else:
                b[k] += A[yy, xx]
    M = sp.csr_matrix((vals, (rows, cols)), shape=(n, n))
    from scipy.sparse.linalg import splu
    lu = splu(M.tocsc())
    res = np.stack([lu.solve(b[:, c]) for c in range(3)], 1)
    out = a.copy()
    for k, (y, x) in enumerate(pts):
        out[y0 + y, x0 + x] = np.clip(res[k], 0, 255)
    return out


def remove_bag(a):
    r_ = bag_mask(a)
    if r_ is None:
        return None
    full, top, bot = r_
    ys, xs = np.where(full)
    # 행별 오른쪽 끝, 주전자 왼쪽 가장자리(윗부분 행의 오른쪽 끝)
    xr = {}
    for y in range(ys.min(), ys.max() + 1):
        xx = np.where(full[y])[0]
        if len(xx):
            xr[y] = xx.max()
    yk = top + 22
    x_k = xr.get(yk, xr[min(xr)]) - 6
    src = a.copy()
    y_counter = bot - 20
    out = a.astype(np.float32).copy()
    for y, x in zip(ys, xs):
        if x >= x_k and y < bot - 8:  # 주전자가 가려진 부분: 마스크 오른쪽 바깥 질감으로 연장
            sx, sy = xr[y] + 9, y
        elif y < y_counter:  # 타일 벽: 봉지 위쪽 타일 줄을 피치만큼 아래로 복제
            k_ = int(np.ceil((y - (top - 8)) / TILE_PITCH))
            sx, sy = x, y - k_ * TILE_PITCH
        else:  # 카운터 상판: 봉지 바닥 아래쪽을 거울 복제
            sx, sy = x, min(H - 1, 2 * (bot + 4) - y)
        out[y, x] = src[sy, min(W - 1, sx)]
    res = poisson_fill(a, full, np.clip(out, 0, 255).astype(np.uint8))
    a[:] = res
    return (top, bot)


# ---------------------------------------------------------------- 색
def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


G_K2B = dict(gain=(1.10, 0.985, 0.915), hl=0.22, rose=0.10, bright=1.04)


def grade_drama_k2b(a, p=G_K2B):
    x = a.astype(np.float32)
    x *= np.array(p["gain"], np.float32)
    x *= p["bright"]
    lum = (x * np.array([0.299, 0.587, 0.114], np.float32)).sum(-1, keepdims=True)
    # 하이라이트 -> #F2B880 계열
    L0 = 0.299 * 242 + 0.587 * 184 + 0.114 * 128
    hl_t = lum * (np.array([242, 184, 128], np.float32) / L0)
    th = smooth(120, 235, lum) * p["hl"]
    x = x * (1 - th) + hl_t * th
    # 그림자 쪽으로 장밋빛 림(#E8798A) 약하게
    L1 = 0.299 * 232 + 0.587 * 121 + 0.114 * 138
    rose_t = lum * (np.array([232, 121, 138], np.float32) / L1)
    ts = (1 - smooth(10, 90, lum)) * p["rose"]
    x = x * (1 - ts) + rose_t * ts
    return np.clip(x, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------- 클립
K1_PRINT_BOX = (1285, 675, 1405, 815)


# ---------------------------------------------------------------- K2b 봉지: 클린 플레이트 합성 (v3)
from scipy.optimize import minimize
PLATE_PATH = os.path.join(ROOT, "img", "K2Se_clean_1.png")
ALIGN_ROI = (740, 380, 1060, 680)   # 봉지 오른쪽 정적 배경(타일·주전자·커피머신). 플레이트의 왼쪽(사모님 재구성)은 제외


def load_plate():
    im = Image.open(PLATE_PATH).convert("RGB")
    if im.size != (W, H):
        im = im.resize((W, H), Image.LANCZOS)
    return np.asarray(im).astype(np.float32)


def _gray(x):
    return 0.299 * x[..., 0] + 0.587 * x[..., 1] + 0.114 * x[..., 2]


def _warp(plate, k, tx, ty, box):
    """클립 좌표 (x,y) -> 플레이트 좌표 c+(x-c)*k+t. box=(x0,y0,x1,y1) 영역만 출력."""
    x0, y0, x1, y1 = box
    cx, cy = 960.0, 540.0
    out = np.zeros((y1 - y0, x1 - x0) + plate.shape[2:], np.float32)
    # ndi.affine_transform: out(o) = in(M o + offset), o 는 (row, col)
    off = np.array([cy + (y0 - cy) * k + ty, cx + (x0 - cx) * k + tx])
    M = np.array([[k, 0], [0, k]])
    if plate.ndim == 2:
        return ndi.affine_transform(plate, M, offset=off, output_shape=out.shape, order=1, mode="nearest")
    return np.stack([ndi.affine_transform(plate[..., c], M, offset=off, output_shape=out.shape[:2], order=1, mode="nearest")
                     for c in range(plate.shape[2])], -1)


def align_plate(a, plate, mask_excl, init=(1.0, 0.0, 0.0)):
    """클립 프레임 a 와 플레이트의 (스케일 k, 이동 tx, ty) 를 정적 배경에서 추정(마스크 제외)."""
    x0, y0, x1, y1 = ALIGN_ROI
    g_clip = _gray(a[y0:y1, x0:x1].astype(np.float32))
    g_clip = ndi.gaussian_filter(g_clip, 1.2)
    w = (~mask_excl[y0:y1, x0:x1]).astype(np.float32)
    pg = ndi.gaussian_filter(_gray(plate), 1.2)

    def cost(v):
        k, tx, ty = v
        wp = _warp(pg, k, tx, ty, ALIGN_ROI)
        d = (wp - g_clip) ** 2
        return float((d * w).sum() / max(w.sum(), 1))
    best = None
    starts = (init[0],) if init != (1.0, 0.0, 0.0) else (1.0, 0.98, 1.02)
    for k0 in starts:
        r = minimize(cost, [k0, init[1], init[2]], method="Powell", options=dict(xtol=1e-3, ftol=1e-4, maxiter=40))
        if best is None or r.fun < best.fun:
            best = r
    return tuple(best.x), float(best.fun)


def plate_remove_bag(a, plate, state):
    """봉지 실루엣을 클린 플레이트 조각으로 교체(하이브리드).
    - 위치/푸시인 오프셋은 프레임별 추정(봉지 오른쪽 정적 배경에 정합: 주전자·커피머신·타일 잔차 <=0.5px)
    - 플레이트에서 사모님 숄/블라우스가 들어온 부분(왼쪽 아래)은 신뢰하지 않고 v2 타일 복제(remove_bag) 결과를 쓴다
    - 둘레 링 통계로 색을 맞추고(평균만, 채널 오프셋 제한), 그레인 보정, 페더 10px"""
    r_ = bag_mask(a)
    if r_ is None:
        return None
    full, top, bot = r_
    base_v2 = a.copy()
    remove_bag(base_v2)               # 신뢰 불가 영역/경계용 v2 결과 (타일·카운터 복제 + 푸아송)
    m = full.copy()                   # 봉지 실루엣(+4px)
    k, tx, ty = state.get("p", (1.0, 0.0, 0.0))
    (k, tx, ty), err = align_plate(a, plate, ndi.binary_dilation(full, iterations=12), (k, tx, ty))
    state["p"] = (k, tx, ty)
    ys, xs = np.where(full)
    box = (max(0, xs.min() - 40), max(0, ys.min() - 40), min(W, xs.max() + 41), min(H, ys.max() + 41))
    wp = _warp(plate, k, tx, ty, box)
    A2 = base_v2[box[1]:box[3], box[0]:box[2]].astype(np.float32)   # v2 결과
    A = a[box[1]:box[3], box[0]:box[2]].astype(np.float32)          # 원본 클립(봉지 있음)
    mm = m[box[1]:box[3], box[0]:box[2]]
    # 플레이트의 사모님(숄 마룬/블라우스 크림) 영역 = 신뢰 불가
    r, g, b = wp[..., 0], wp[..., 1], wp[..., 2]
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    maroon = (r > g * 1.45) & (r > b * 1.15) & (lum < 125)
    cream = (lum > 165) & ((r - b) > 26) & ((r - g) < 22)
    mar_o = ndi.binary_opening(maroon, iterations=2)
    near = ndi.binary_dilation(mar_o, iterations=45)
    woman = ndi.binary_dilation(mar_o, iterations=14) | ndi.binary_dilation(ndi.binary_opening(cream & near, iterations=1), iterations=8)
    trust = ~woman
    # 색 맞춤은 신뢰 영역 둘레에서(평균+오프셋 제한). 링 = 봉지 마스크 바깥 6~18px
    ring = ndi.binary_dilation(mm, iterations=14) & ~ndi.binary_dilation(mm, iterations=5) & trust
    wp2 = wp.copy()
    if ring.sum() > 200:
        for c in range(3):
            off = float(np.clip(A[..., c][ring].mean() - wp[..., c][ring].mean(), -18, 18))
            wp2[..., c] = wp[..., c] + off
    # 그레인 맞춤
    hf = lambda x: x - ndi.gaussian_filter(x, 1.5)
    sd_clip = np.mean([hf(A2[..., c])[ring].std() for c in range(3)]) if ring.sum() > 200 else 0
    sd_plate = np.mean([hf(wp2[..., c])[mm & trust].std() for c in range(3)]) if (mm & trust).any() else 0
    add = max(0.0, np.sqrt(max(sd_clip ** 2 - sd_plate ** 2, 0)))
    rng = np.random.RandomState(1234 + state.get("n", 0))
    wp2 += rng.randn(*wp2.shape[:2], 1).astype(np.float32) * add
    # 합성 마스크: 봉지 안쪽 & 신뢰 영역, 페더 ~10px. 나머지는 v2 결과(이미 봉지 제거됨)
    al_p = ndi.gaussian_filter((ndi.binary_erosion(mm, iterations=3) & trust).astype(np.float32), 6.5)[..., None]
    # 주전자 바깥으로 제한: 주전자 왼쪽 가장자리(마스크 윗부분 오른쪽 끝)부터 오른쪽은 v2 결과(주전자 질감 연장)를 쓴다
    xr_rows = {}
    for yy_ in range(top, min(top + 40, H)):
        xx_ = np.where(full[yy_])[0]
        if len(xx_):
            xr_rows[yy_] = xx_.max()
    x_k = (xr_rows.get(top + 22) or max(xr_rows.values())) - 6
    xs_box = np.arange(box[0], box[2])[None, :, None].astype(np.float32)
    al_p = al_p * np.clip((x_k + 3 - xs_box) / 6.0, 0, 1)
    out = A2 * (1 - al_p) + wp2 * al_p
    res = base_v2.copy()
    res[box[1]:box[3], box[0]:box[2]] = np.clip(out, 0, 255).astype(np.uint8)
    a[:] = res
    state["n"] = state.get("n", 0) + 1
    return (k, tx, ty, err, float(trust[mm].mean()))


# 사원증 사각형 키프레임 (원본 시간 s -> [TL, TR, BR, BL], 1920x1080 좌표). 격자 확대 화면에서 직접 읽음.
K2B_CARD = [
    (0.50, [(1444, 703), (1480, 709), (1472, 835), (1437, 823)]),
    (1.00, [(1453, 703), (1488, 705), (1473, 837), (1441, 815)]),
    (1.50, [(1470, 685), (1493, 693), (1475, 825), (1448, 805)]),
    (2.00, [(1457, 687), (1498, 695), (1482, 827), (1442, 808)]),
    (2.50, [(1444, 693), (1502, 703), (1493, 835), (1430, 822)]),
    (3.00, [(1460, 703), (1495, 708), (1482, 837), (1449, 825)]),
    (3.50, [(1462, 703), (1498, 712), (1482, 852), (1448, 833)]),
    (4.00, [(1473, 708), (1510, 718), (1495, 858), (1457, 838)]),
    (4.50, [(1477, 715), (1520, 722), (1502, 860), (1462, 843)]),
    (4.96, [(1482, 717), (1527, 723), (1510, 862), (1470, 845)]),
]
K1_CARD = [
    (1.30, [(1311, 682), (1372, 682), (1371, 774), (1310, 774)]),
    (1.60, [(1316, 684), (1376, 684), (1375, 775), (1315, 775)]),
    (1.90, [(1315, 687), (1378, 688), (1378, 781), (1316, 782)]),
    (2.20, [(1316, 687), (1379, 687), (1378, 784), (1316, 785)]),
    (2.50, [(1310, 691), (1372, 691), (1371, 786), (1310, 786)]),
    (2.80, [(1303, 695), (1362, 692), (1359, 789), (1301, 789)]),
    (3.05, [(1297, 695), (1356, 692), (1353, 790), (1295, 790)]),
]


def interp_quad(kf, t):
    ts = [k[0] for k in kf]
    if t <= ts[0]:
        return np.array(kf[0][1], float)
    if t >= ts[-1]:
        return np.array(kf[-1][1], float)
    for (t0, q0), (t1, q1) in zip(kf[:-1], kf[1:]):
        if t0 <= t <= t1:
            u = (t - t0) / (t1 - t0)
            return np.array(q0, float) * (1 - u) + np.array(q1, float) * u


def poly_mask(corners, shape_hw, erode=0):
    im = Image.new("L", (shape_hw[1], shape_hw[0]), 0)
    ImageDraw.Draw(im).polygon([tuple(p) for p in corners], fill=255)
    m = np.asarray(im) > 0
    if erode:
        m = ndi.binary_erosion(m, iterations=erode)
    return m


def blank_card(a, quad, thr=20, protect=True):
    """사원증 인쇄(글자·사진·띠)를 카드 바탕색으로 지워 흰 빈 카드로 만든다.
    가림물(손·소매·우산 손잡이 = 아주 어두운 부분, 살색)은 건드리지 않는다. 카드 테두리는 2px 안쪽까지만 칠한다."""
    full = poly_mask(quad, (H, W))
    inner = ndi.binary_erosion(full, iterations=2)
    ys, xs = np.where(full)
    y0, y1, x0, x1 = max(0, ys.min() - 8), ys.max() + 9, max(0, xs.min() - 8), xs.max() + 9
    roi = a[y0:y1, x0:x1].astype(np.float32)
    im = inner[y0:y1, x0:x1]
    sat, lum = hsv_arrays(roi)
    r, g, b = roi[..., 0], roi[..., 1], roi[..., 2]
    basepx = im & (sat < 0.12) & (lum > 150)
    base = np.median(roi[basepx], axis=0) if basepx.sum() > 30 else np.array([212, 212, 218], np.float32)
    diff = np.abs(roi - base).max(-1)
    skin = (r > g + 8) & (g > b + 8) & (lum > 100) & (sat > 0.14)
    occl = ((lum < 24) | skin) if protect else np.zeros_like(skin)
    occl = ndi.binary_dilation(occl, iterations=2)
    printm = im & (diff > thr) & ~occl
    printm = ndi.binary_dilation(printm, iterations=1) & im & ~occl
    wf = (basepx | (im & ~printm & ~occl & (diff <= thr))).astype(np.float32)
    wb = gblur(wf, 6.0)
    fillc = np.zeros_like(roi)
    for c in range(3):
        fillc[..., c] = gblur(roi[..., c] * wf, 6.0) / np.maximum(wb, 1e-3)
    fillc = np.where(wb[..., None] > 0.03, fillc, base)
    al = np.clip(gblur(printm.astype(np.float32), 0.9) * 1.7, 0, 1)[..., None]
    a[y0:y1, x0:x1] = np.clip(roi * (1 - al) + fillc * al, 0, 255).astype(np.uint8)
    return int(printm.sum())


def soft_blur_bag(a, sigma=7.0, feather_sigma=7.0):
    """v1 방식 복귀(약한 σ + 페더 약 20px): 봉지 실루엣을 약하게 흐리고 가장자리를 넓게 섞는다. 실루엣은 프레임별 추적."""
    r_ = bag_mask(a)
    if r_ is None:
        return False
    full, top, bot = r_
    ys, xs = np.where(full)
    x0, x1, y0, y1 = max(0, xs.min() - 40), min(W, xs.max() + 41), max(0, ys.min() - 40), min(H, ys.max() + 41)
    roi = a[y0:y1, x0:x1].astype(np.float32)
    bl = np.stack([ndi.gaussian_filter(roi[..., c], sigma) for c in range(3)], -1)
    al = ndi.gaussian_filter(ndi.binary_dilation(full[y0:y1, x0:x1], iterations=5).astype(np.float32), feather_sigma)[..., None]
    al = np.clip(al * 1.15, 0, 1)
    a[y0:y1, x0:x1] = np.clip(roi * (1 - al) + bl * al, 0, 255).astype(np.uint8)
    return True


PLATE = None
BAG_MODE = "cloneblur"   # v3: 클린 플레이트 정합 실패(아래 기록)로 v1 방식 약블러+페더 복귀
PSTATE = {}


def process_clip(name, limit=None, only_frames=None, out_name=None, save_png=None):
    s, e = 12, 120
    src = os.path.join(ROOT, "clips", name + ".mp4")
    vf_dec = (f"trim=start_frame={s}:end_frame={e},setpts=PTS-STARTPTS,"
              f"scale={W}:{H}:flags=lanczos:in_color_matrix=bt709:in_range=tv,format=rgb24")
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-vf", vf_dec, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                           stdout=subprocess.PIPE)
    out = os.path.join(OUT, (out_name or name + "_v2") + ".mp4")
    enc = None
    if save_png is None:
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                                "-framerate", "24", "-i", "-", "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
                                "-an", "-c:v", "libx264", "-preset", "slow", "-crf", "12", "-r", "24", "-colorspace", "bt709",
                                "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv", "-movflags", "+faststart", out],
                               stdin=subprocess.PIPE)
    fsz = W * H * 3
    n = 0
    while True:
        buf = dec.stdout.read(fsz)
        if len(buf) < fsz:
            break
        a = np.frombuffer(buf, np.uint8).reshape(H, W, 3).copy()
        t = (s + n) / 24.0
        if only_frames is None or n in only_frames:
            if name == "K1":
                pp.purple_fix(a)
                if 1.25 <= t <= 3.05:
                    blank_card(a, interp_quad(K1_CARD, t), thr=18, protect=(t < 2.1 or t > 2.62))
            if name == "K2b":
                if PLATE is not None:
                    info = plate_remove_bag(a, PLATE, PSTATE)
                    if n % 20 == 0:
                        print("plate align n=%d" % n, info)
                elif BAG_MODE == "blur":
                    soft_blur_bag(a)
                elif BAG_MODE == "cloneblur":   # v2 타일 복제로 봉지를 지운 뒤 그 자리를 약블러+페더 20px 로 풀어 직사각형 흔적을 숨김
                    r_ = bag_mask(a)
                    remove_bag(a)
                    if r_ is not None:
                        full_, _t, _b = r_
                        ys_, xs_ = np.where(full_)
                        x0_, x1_, y0_, y1_ = max(0, xs_.min() - 40), min(W, xs_.max() + 41), max(0, ys_.min() - 40), min(H, ys_.max() + 41)
                        roi_ = a[y0_:y1_, x0_:x1_].astype(np.float32)
                        bl_ = np.stack([ndi.gaussian_filter(roi_[..., c], 2.5) for c in range(3)], -1)
                        al_ = ndi.gaussian_filter(ndi.binary_dilation(full_[y0_:y1_, x0_:x1_], iterations=3).astype(np.float32), 7.0)[..., None]
                        a[y0_:y1_, x0_:x1_] = np.clip(roi_ * (1 - al_) + bl_ * al_, 0, 255).astype(np.uint8)
                else:
                    remove_bag(a)
                blank_card(a, interp_quad(K2B_CARD, t), thr=18, protect=(t < 0.95))
                a = grade_drama_k2b(a)
            if save_png is not None:
                Image.fromarray(a).save(os.path.join(save_png, f"{name}_{n:04d}.png"))
        if enc is not None:
            enc.stdin.write(a.tobytes())
        n += 1
        if limit and n >= limit:
            break
    if enc is not None:
        enc.stdin.close()
        enc.wait()
    dec.stdout.close()
    dec.terminate()
    print("clip", name, n, "->", out)



# ---------------------------------------------------------------- 정지 컷 (C19a 간판, C19c 배경·렌즈)
def sunset_gradient(h, w):
    top = np.array([0xF2, 0xB8, 0x80], np.float32)
    bot = np.array([0xE8, 0x79, 0x8A], np.float32)
    t = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    # 위쪽 금빛 -> 아래쪽 장밋빛, 가로로 약한 밝기 변화(보케 느낌)
    g = top * (1 - t) + bot * t
    xx = np.linspace(0, 1, w, dtype=np.float32)[None, :, None]
    rng = np.random.RandomState(11)
    low = rng.rand(9, 16).astype(np.float32)
    low = np.asarray(Image.fromarray((low * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)).astype(np.float32)[..., None] / 255
    low = gblur(low, 40)
    low = (low - low.mean()) / (low.std() + 1e-6)
    return g * (1 + 0.05 * low) * (0.92 + 0.10 * (1 - np.abs(xx - 0.5) * 1.0))


def fix_c19c(arr):
    a = arr.astype(np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    mxc, mnc = a.max(-1), a.min(-1)
    satc = (mxc - mnc) / np.maximum(mxc, 1)
    bg = (r > g + 14) & (b >= g - 5) & (lum < 125) & (lum > 14) & (satc > 0.40)
    bg = ndi.binary_opening(bg, iterations=2)
    bg = ndi.binary_closing(bg, iterations=3)
    lab, n = ndi.label(bg)
    keep = np.zeros_like(bg)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])).tolist()) - {0}
    for k in range(1, n + 1):  # 이미지 가장자리에 닿는 큰 덩어리만 배경 (입술·손 그림자 제외)
        if (lab == k).sum() > 20000:
            keep |= lab == k
    # 배경과 맞닿은 어두운 중성 덩어리 (양옆 아래 모서리의 소매 x<338, x>1582 는 제외)
    xx_ = np.arange(a.shape[1])[None, :]
    yy_ = np.arange(a.shape[0])[:, None]
    dark = (lum < 48) & (xx_ >= 338) & (xx_ <= 1582) & (yy_ > 880)
    dlab, dn = ndi.label(dark)
    near = ndi.binary_dilation(keep, iterations=16)
    for k in range(1, dn + 1):
        comp = dlab == k
        if comp.sum() < 25:
            continue
        if (comp & near).sum() > 0.5 * comp.sum():
            keep |= comp
    keep = ndi.binary_closing(keep, iterations=3, border_value=1)
    # 가장자리 어두운 테두리(배경과 섞인 픽셀)도 걷어냄: 배경 바로 바깥 3px 중 어두운 픽셀
    skin = (r > g + 25) & (g > b + 10) & (lum > 110)
    skin_near = ndi.binary_dilation(skin, iterations=5)
    fr = ndi.binary_dilation(keep, iterations=3, border_value=0) & ~keep & (lum < 95) & skin_near
    keep = keep | fr
    nk, nn = ndi.label(~keep)
    for k in range(1, nn + 1):  # 배경 속에 남은 작은 점 덩어리 정리
        c_ = nk == k
        if c_.sum() < 1500:
            keep |= c_
    keep = ndi.binary_erosion(keep, iterations=1, border_value=1)
    m = gblur(keep.astype(np.float32), 3.0)[..., None]   # v3: 머리카락 가장자리 2~3px 페더
    grad = sunset_gradient(a.shape[0], a.shape[1])
    # 배경 밝기: 피사체 노출과 어울리도록 약간 낮춤
    out = a * (1 - m) + grad * 0.82 * m
    # v3: 렌즈 탈색 원복 (노을 배경이라 주황 렌즈가 반사로 읽힘)
    return np.clip(out, 0, 255).astype(np.uint8), keep


pp.STILL_RECIPE.setdefault("C17c", pp.STILL_RECIPE["C17b"])   # v4: C17c 는 C17b 와 같은 색 레시피


def process_still_v2(name):
    full = Image.open(os.path.join(ROOT, "img", name + "_1.png")).convert("RGB")
    im = full.resize((W, H), Image.LANCZOS)
    arr = np.asarray(im).copy()
    if name == "C19a":
        pp.feather_blur(arr, (1613, 188, 1677, 211), 4.5, feather=4, strength=0.92)
    if name == "C19c":
        arr, _ = fix_c19c(arr)
    if name == "C16c":  # v3: 커피봉지 라벨/사원증 블러를 약하게 + 페더 20px (v1 σ12/페더10 의 뭉침 완화)
        pp.feather_blur(arr, (706, 698, 772, 808), 8, feather=20)
        pp.feather_blur(arr, (1428, 846, 1494, 872), 6, feather=20)
    os.makedirs(os.path.join(OUT, "stills"), exist_ok=True)
    tmp = os.path.join(OUT, "stills", name + "_in.png")
    Image.fromarray(arr).save(tmp)
    out = os.path.join(OUT, "stills", name + ".png")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-vf", pp.STILL_RECIPE[name], "-frames:v", "1", out], check=True)
    print("still", name, "->", out)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    mode = sys.argv[1]
    if "--plate" in sys.argv and os.path.exists(PLATE_PATH):
        PLATE = load_plate()
        sys.argv.remove("--plate")
        print("클린 플레이트 사용:", PLATE_PATH)
    if mode == "clips":
        names = sys.argv[2:] or ["K1", "K2b"]
        for nme in names:
            process_clip(nme)
    elif mode == "stills":
        for nme in (sys.argv[2:] or ["C19a", "C19c", "C16c", "C17c"]):
            process_still_v2(nme)
    elif mode == "test":
        # python prep_v2.py test K2b 0,24,48,72,100
        nme = sys.argv[2]
        fr = set(int(x) for x in sys.argv[3].split(","))
        os.makedirs(os.path.join(OUT, "t"), exist_ok=True)
        process_clip(nme, only_frames=fr, save_png=os.path.join(OUT, "t"), limit=max(fr) + 1)
