# -*- coding: utf-8 -*-
"""P4b 수면·부두 제거: Seedream 편집 결과를 편집 영역에만 합친다 (P4-01, P4-02)

Seedream은 편집하지 않은 곳도 미세하게(색·선명도·위치) 바꾸므로 결과를 통째로 쓰지 않는다.
절차: 기준 플레이트에 정렬(ECC, 편집 영역 제외) → 주변 고리에서 색 맞춤 → 마스크 영역만 합성
       → 그레인 맞춤 → 검사 수치와 비교 이미지.

사용:  python merge_p4b.py                       # img/P4b_sd_*.png 전부를 후보로
       python merge_p4b.py ..\\P4b_sd_2.png       # 특정 후보만
       python merge_p4b.py --pick 2              # 후보 2번을 채택본으로 저장
기준:  img/fix/P4b_1_fix.png (안내판 블러·하늘 통일 반영본). 없으면 img/P4b_1.png
출력:  img/fix/P4b_sd<n>_merged.png (후보별), 채택 시 img/fix/P4b_1_sdfix.png
       비교 이미지 img/fix/compare/P4b_sd<n>_*.png, 수치 img/fix/compare/P4b_sd_report.txt
좌표는 원본 1440x2560 px.
"""
import os, sys, glob, re
import numpy as np, cv2
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.dirname(HERE)
CMP = os.path.join(HERE, 'compare')
os.makedirs(CMP, exist_ok=True)
RNG = np.random.default_rng(2911)

R_WATER = (0, 1261, 314, 1440)       # P4-01 수면
R_DOCK = (0, 1216, 422, 1280)        # P4-02 부두 선
MARGIN = 24                          # 영역 밖으로 넓히는 폭(Seedream이 경계를 다르게 그린 부분까지)
FEATHER = 16                         # 명세 P4-02: 경계 페더 16px
RING = 60                            # 색 맞춤·이음 검사에 쓰는 바깥 고리 폭


def _font(size=15):
    """한글 라벨용 글꼴: 프로젝트 fonts 폴더 → 윈도 맑은 고딕 → 기본."""
    import glob as _g
    from PIL import ImageFont
    root = os.path.dirname(IMG)
    cands = sorted(_g.glob(os.path.join(root, 'fonts', 'Pretendard', '**', '*.[ot]tf'), recursive=True))
    cands += sorted(_g.glob(os.path.join(root, 'fonts', '**', '*.[ot]tf'), recursive=True))
    cands += ['C:/Windows/Fonts/malgun.ttf', '/usr/share/fonts/truetype/nanum/NanumGothic.ttf']
    for p in cands:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            pass
    return ImageFont.load_default()


FONT = None


def text(d, xy, s, fill=(255, 255, 255)):
    global FONT
    if FONT is None:
        FONT = _font()
    d.text(xy, s, fill=fill, font=FONT)


def load(p):
    return np.asarray(Image.open(p).convert('RGB')).astype(np.float32)


def u8(a):
    return np.clip(a + 0.5, 0, 255).astype(np.uint8)


def save(a, p):
    Image.fromarray(u8(a)).save(p)


def gblur(a, s):
    return cv2.GaussianBlur(a, (0, 0), s) if s > 0 else a


def luma(a):
    return a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722


def edit_mask(shape):
    m = np.zeros(shape[:2], np.uint8)
    for x0, y0, x1, y1 in (R_WATER, R_DOCK):
        m[y0:y1 + 1, x0:x1 + 1] = 1
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * MARGIN + 1, 2 * MARGIN + 1))
    hard = cv2.dilate(m, k)
    soft = np.clip(gblur(hard.astype(np.float32), FEATHER / 2.5), 0, 1)
    soft = np.maximum(soft, m.astype(np.float32))           # 원래 영역 안은 항상 1
    return hard, soft


def ring_mask(hard, w):
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * w + 1, 2 * w + 1))
    return (cv2.dilate(hard, k) > 0) & (hard == 0)


def align(base, cand, hard):
    """편집 영역 밖에서 ECC(affine)로 후보를 기준에 맞춘다. 0.5배 축소로 계산."""
    s = 0.5
    g0 = cv2.resize(luma(base), None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    g1 = cv2.resize(luma(cand), None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (81, 81))
    valid = (cv2.dilate(hard, k) == 0).astype(np.uint8)
    valid = cv2.resize(valid, (g0.shape[1], g0.shape[0]), interpolation=cv2.INTER_NEAREST)
    warp = np.eye(2, 3, dtype=np.float32)
    crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 200, 1e-6)
    try:
        cc, warp = cv2.findTransformECC(gblur(g0, 1.5), gblur(g1, 1.5), warp,
                                        cv2.MOTION_AFFINE, crit, valid, 5)
    except cv2.error as e:
        print('  ECC 실패, 정렬 없이 진행:', str(e).splitlines()[-1])
        return cand, None, 0.0
    warp[:, 2] /= s
    out = cv2.warpAffine(cand, warp, (base.shape[1], base.shape[0]),
                         flags=cv2.INTER_LANCZOS4 | cv2.WARP_INVERSE_MAP,
                         borderMode=cv2.BORDER_REFLECT)
    return out, warp, float(cc)


def color_match(base, cand, ring):
    """고리 영역의 채널별 평균·표준편차를 기준에 맞추는 선형 보정(전체 후보에 적용)."""
    b = base[ring].reshape(-1, 3); c = cand[ring].reshape(-1, 3)
    gain = np.clip((b.std(0) + 1e-3) / (c.std(0) + 1e-3), 0.7, 1.4)
    off = b.mean(0) - c.mean(0) * gain
    return cand * gain + off, gain, off


def noise_std(a, mask):
    hp = a - gblur(a, 1.2)
    v = hp[mask].reshape(-1, 3)
    med = np.median(v, 0)
    return 1.4826 * np.median(np.abs(v - med), 0)


def regrain(out, ref_std, m):
    sel = m > 0.5
    if not sel.any():
        return out
    need = np.sqrt(np.clip(np.asarray(ref_std) ** 2 - noise_std(out, sel) ** 2, 0, None))
    n = RNG.standard_normal(out.shape).astype(np.float32)
    l = RNG.standard_normal(out.shape[:2]).astype(np.float32)[..., None]
    n = gblur(0.6 * l + 0.8 * n, 0.6)
    n /= n.reshape(-1, 3).std(0) + 1e-6
    return out + n * need * m[..., None]


# ---------------------------------------------------------------- 검사 수치
def streak_ratio(a, box):
    """수면 반사의 가로 줄무늬 지표: 세로 방향 기울기 / 가로 방향 기울기(루마).
    물결·반사 줄은 가로로 길어서 값이 커진다. 숲 사면은 1 안팎."""
    x0, y0, x1, y1 = box
    g = gblur(luma(a[y0:y1 + 1, x0:x1 + 1]), 1.0)
    gy = np.abs(np.diff(g, axis=0)).mean(); gx = np.abs(np.diff(g, axis=1)).mean()
    return float(gy / (gx + 1e-6))


def seam_step(a, hard):
    """경계 바로 안쪽 6px 띠와 바깥 6px 띠의 루마 중앙값 차이(구간별 최대)."""
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (13, 13))
    inner = (hard > 0) & (cv2.erode(hard, k) == 0)
    outer = (cv2.dilate(hard, k) > 0) & (hard == 0)
    L = luma(a)
    worst = 0.0
    ys = np.where(inner.any(1))[0]
    for y0 in range(ys.min(), ys.max() + 1, 40):          # 40px 높이 구간마다
        sl = slice(y0, y0 + 40)
        i, o = L[sl][inner[sl]], L[sl][outer[sl]]
        if len(i) > 30 and len(o) > 30:
            worst = max(worst, abs(float(np.median(i) - np.median(o))))
    return worst


def bright_blobs(a, box, thr=150):
    """영역 안 밝은 점(불빛) 개수와 평균 크기. 먼 시가지 불빛이 생겼는지 확인용."""
    x0, y0, x1, y1 = box
    m = (luma(a[y0:y1 + 1, x0:x1 + 1]) > thr).astype(np.uint8)
    n, _, st, _ = cv2.connectedComponentsWithStats(m, 8)
    areas = st[1:, cv2.CC_STAT_AREA]
    return int(n - 1), float(areas.mean()) if len(areas) else 0.0


# ---------------------------------------------------------------- 비교 이미지
def sheet(images, labels, box, path, zoom=2):
    x0, y0, x1, y1 = box
    tiles = []
    for im in images:
        t = Image.fromarray(u8(im[y0:y1, x0:x1]))
        tiles.append(t.resize((t.width * zoom, t.height * zoom), Image.NEAREST))
    W, H = tiles[0].size
    s = Image.new('RGB', (len(tiles) * (W + 10) - 10, H + 24), (40, 40, 40))
    d = ImageDraw.Draw(s)
    for i, (t, lb) in enumerate(zip(tiles, labels)):
        s.paste(t, (i * (W + 10), 24)); text(d, (i * (W + 10) + 4, 6), lb)
    s.save(path)


def full_sheet(images, labels, path, w=540):
    h = int(w * 16 / 9)
    s = Image.new('RGB', (len(images) * (w + 12) - 12, h + 24), (40, 40, 40))
    d = ImageDraw.Draw(s)
    for i, (im, lb) in enumerate(zip(images, labels)):
        s.paste(Image.fromarray(u8(im)).resize((w, h), Image.LANCZOS), (i * (w + 12), 24))
        text(d, (i * (w + 12) + 4, 6), lb)
    s.save(path)


# ---------------------------------------------------------------- 메인
def base_plate():
    for p in (os.path.join(HERE, 'P4b_1_fix.png'), os.path.join(IMG, 'P4b_1.png')):
        if os.path.exists(p):
            return p
    sys.exit('기준 플레이트가 없다: img/fix/P4b_1_fix.png 또는 img/P4b_1.png')


def cand_no(p):
    m = re.search(r'(\d+)\D*$', os.path.basename(p))
    return m.group(1) if m else os.path.splitext(os.path.basename(p))[0]


def process(base, bpath, cpath, log):
    no = cand_no(cpath)
    c = load(cpath)
    H, W = base.shape[:2]
    if c.shape[:2] != (H, W):
        ar_b, ar_c = W / H, c.shape[1] / c.shape[0]
        if abs(ar_b - ar_c) / ar_b > 0.01:
            log.append('후보 %s: 비율이 다르다(%dx%d). 9:16으로 다시 받는다' % (no, c.shape[1], c.shape[0]))
            return None
        c = np.asarray(Image.fromarray(u8(c)).resize((W, H), Image.LANCZOS)).astype(np.float32)
    hard, soft = edit_mask(base.shape)
    ring = ring_mask(hard, RING)
    ca, warp, cc = align(base, c, hard)
    cm, gain, off = color_match(base, ca, ring)
    out = base * (1 - soft[..., None]) + cm * soft[..., None]
    out = regrain(out, noise_std(base, ring), soft)
    np.clip(out, 0, 255, out=out)

    box = (0, 1150, 520, 1520)
    bx = (R_WATER[0], R_WATER[1], R_WATER[2], R_WATER[3])
    outside = np.abs(out - base)[soft == 0].max() if (soft == 0).any() else 0
    raw_out = np.abs(ca - base)[ring].mean()
    n0, s0 = bright_blobs(base, bx); n1, s1 = bright_blobs(out, bx)
    rep = [
        '후보 %s  (%s)' % (no, os.path.basename(cpath)),
        '  정렬 ECC 상관 %.4f, 이동 (%.1f, %.1f)px, 배율 %.4f' % (
            cc, *(warp[:, 2] if warp is not None else (0, 0)),
            float(np.sqrt(abs(np.linalg.det(warp[:, :2])))) if warp is not None else 1.0),
        '  색 맞춤 gain %s offset %s  (gain이 0.85~1.15 밖이면 Seedream이 톤을 크게 바꾼 것)' % (
            np.round(gain, 3), np.round(off, 1)),
        '  편집 영역 밖 최대 변화 %.1f (0이어야 한다)' % outside,
        '  고리 영역 원본 대비 평균 차(정렬·색 맞춤 전) %.1f' % raw_out,
        '  가로 줄무늬 지표 수면영역: 기준 %.2f -> 결과 %.2f  (숲 사면이면 1.3 이하 기대)' % (
            streak_ratio(base, bx), streak_ratio(out, bx)),
        '  경계 단차(루마 중앙값, 구간 최대): 기준 %.1f -> 결과 %.1f  (6 이하 기대)' % (
            seam_step(base, hard), seam_step(out, hard)),
        '  밝은 점(불빛) 수면영역: 기준 %d개 평균 %.0fpx -> 결과 %d개 평균 %.0fpx' % (n0, s0, n1, s1),
    ]
    log += rep
    print('\n'.join(rep))
    save(out, os.path.join(HERE, 'P4b_sd%s_merged.png' % no))
    sheet([base, ca, out], ['BASE', 'SEEDREAM %s (정렬)' % no, 'MERGED'], box,
          os.path.join(CMP, 'P4b_sd%s_crop.png' % no))
    full_sheet([base, out], ['BASE', 'MERGED sd%s' % no], os.path.join(CMP, 'P4b_sd%s_full.png' % no))
    # 1080 프레임 축소본에서 폰 크기(가로 405)
    ph = [np.asarray(Image.fromarray(u8(im)).resize((1080, 1920), Image.LANCZOS)).astype(np.float32)
          for im in (base, out)]
    full_sheet(ph, ['BASE 1080', 'MERGED 1080'], os.path.join(CMP, 'P4b_sd%s_phone.png' % no), w=405)
    return out


def main():
    args = sys.argv[1:]
    if args[:1] == ['--pick']:
        no = args[1]
        src = os.path.join(HERE, 'P4b_sd%s_merged.png' % no)
        if not os.path.exists(src):
            sys.exit('먼저 후보 %s를 합성한다: python merge_p4b.py' % no)
        Image.open(src).save(os.path.join(HERE, 'P4b_1_sdfix.png'))
        print('채택: P4b_1_sdfix.png <- ', os.path.basename(src))
        return
    bpath = base_plate()
    base = load(bpath)
    print('기준:', os.path.relpath(bpath, IMG))
    cands = args or sorted(glob.glob(os.path.join(IMG, 'P4b_sd_*.png')))
    if not cands:
        sys.exit('후보가 없다. Seedream 결과를 img/P4b_sd_1.png, P4b_sd_2.png ... 로 저장한다')
    log = ['기준 ' + os.path.relpath(bpath, IMG)]
    for p in cands:
        process(base, bpath, p, log)
        log.append('')
    with open(os.path.join(CMP, 'P4b_sd_report.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(log))
    print('\n비교 이미지: img/fix/compare/P4b_sd*_crop.png, *_full.png, *_phone.png')
    print('채택: python merge_p4b.py --pick <번호>')


if __name__ == '__main__':
    main()
