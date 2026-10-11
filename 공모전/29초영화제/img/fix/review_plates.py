# -*- coding: utf-8 -*-
"""플레이트 편집 독립 검수 자료 만들기 (plate_edits.json v2.2 기준)

만든 사람과 다른 검수자가 판정할 수 있도록, 편집 항목마다
  (1) 원본 | 편집본 확대 크롭  (2) 1080 프레임 축소본 크롭  (3) 폰 크기(가로 405px) 전체 화면에 영역 표시
를 한 장으로 묶고, 자동 수치를 붙여 검수표(review/검수표.md)를 만든다.
자동 수치는 판정 보조일 뿐이다. 최종 판정은 검수자가 눈으로 한다.

사용:  python review_plates.py            # 전체
       python review_plates.py P1 P6      # 일부만
출력:  img/fix/review/<편집ID>.png, <플레이트>_phone.png, <플레이트>_diff.png, 검수표.md
"""
import os, sys, json
import numpy as np, cv2
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.dirname(HERE)
OUT = os.path.join(HERE, 'review')

# 플레이트 -> (원본, 편집본 후보들: 앞에 있는 것이 우선)
FILES = {
    'P1': ('P1_1.png', ['P1_1_fix.png']),
    'P4b': ('P4b_1.png', ['P4b_1_sdfix.png', 'P4b_1_fix.png']),
    'P5c': ('P5c_1.png', ['P5c_1_fix.png']),
    'P6': ('P6_1.png', ['P6_1_fix.png']),
    'P8': ('P8_1.png', ['P8_1_fix.png']),
    'P3': ('P3_1.png', ['P3_1_fix.png']),
    'P2clean': ('P2clean_1.png', ['P2clean_1_fix.png', 'P2c_clean.png']),
}
PHONE_W = 405            # 폰 화면에서 1080 프레임이 차지하는 대략의 너비(pt)


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


def gblur(a, s):
    return cv2.GaussianBlur(a, (0, 0), s) if s > 0 else a


def luma(a):
    return a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722


def find(name):
    for d in (HERE, IMG):
        p = os.path.join(d, name)
        if os.path.exists(p):
            return p
    return None


def box_of(e, W, H):
    if 'region' in e:
        x0, y0, x1, y1 = e['region']
    elif 'point' in e:
        r = e.get('radius', 10)
        x0, y0, x1, y1 = e['point'][0] - r, e['point'][1] - r, e['point'][0] + r, e['point'][1] + r
    else:
        return None
    return max(0, x0), max(0, y0), min(W - 1, x1), min(H - 1, y1)


# ---------------------------------------------------------------- 자동 수치
def ring(box, W, H, w):
    x0, y0, x1, y1 = box
    m = np.zeros((H, W), bool)
    m[max(0, y0 - w):min(H, y1 + 1 + w), max(0, x0 - w):min(W, x1 + 1 + w)] = True
    m[y0:y1 + 1, x0:x1 + 1] = False
    return m


def inside(box, W, H):
    x0, y0, x1, y1 = box
    m = np.zeros((H, W), bool)
    m[y0:y1 + 1, x0:x1 + 1] = True
    return m


def hp_std(a, m):
    hp = luma(a) - gblur(luma(a), 1.2)
    v = hp[m]
    return float(1.4826 * np.median(np.abs(v - np.median(v)))) if v.size else 0.0


def edge_density(a, m):
    """글자 획 지표: Canny 엣지 화소 비율(%)."""
    g = u8(luma(a))
    e = cv2.Canny(g, 40, 100) > 0
    return 100.0 * float(e[m].mean()) if m.any() else 0.0


def lap_var(a, m):
    """세부 묘사 지표(얼굴 식별 가능성): 라플라시안 분산."""
    L = cv2.Laplacian(gblur(luma(a), 0.7), cv2.CV_32F)
    return float(L[m].var()) if m.any() else 0.0


def peak_contrast(a, box, W, H):
    """하늘 점 잔존: 영역 안 최대 루마 - 주변 중앙값."""
    L = gblur(luma(a), 0.8)
    return float(L[inside(box, W, H)].max() - np.median(L[ring(box, W, H, 12)]))


def seam(a, box, W, H):
    """경계 단차: 영역 안쪽 6px 띠와 바깥 6px 띠의 루마 중앙값 차이."""
    x0, y0, x1, y1 = box
    L = luma(a)
    inn = inside(box, W, H) & ~inside((x0 + 6, y0 + 6, x1 - 6, y1 - 6), W, H)
    out = ring(box, W, H, 6)
    if not inn.any() or not out.any():
        return 0.0
    return abs(float(np.median(L[inn]) - np.median(L[out])))


def sat_blue(a, m):
    v = a[m].reshape(-1, 3)
    mx, mn = v.max(1), v.min(1)
    sat = float(((mx - mn) / (mx + 1e-3)).mean())
    return sat, float((v[:, 2] - v[:, 0]).mean())


def metrics(e, a, b, W, H):
    """항목 종류별 지표와 자동 판정(OK / 확인). 기준은 보수적으로 잡았다."""
    box = box_of(e, W, H)
    if box is None:
        return [], '수동'
    m = inside(box, W, H); rg = ring(box, W, H, 24)
    rows, flags = [], []
    op, tgt = e.get('op'), e.get('target', '')
    n_in, n_rg = hp_std(b, m), hp_std(b, rg)
    nr = n_in / (n_rg + 1e-3)
    rows.append('노이즈 안/밖 %.2f' % nr)
    if not 0.6 <= nr <= 1.6:
        flags.append('노이즈 차이')
    sb, sa = seam(a, box, W, H), seam(b, box, W, H)
    rows.append('경계 단차 %.1f→%.1f' % (sb, sa))
    if sa > max(6.0, sb * 1.5 + 2):
        flags.append('경계')
    if 'point' in e:
        pb, pa = peak_contrast(a, box, W, H), peak_contrast(b, box, W, H)
        rows.append('점 대비 %.1f→%.1f' % (pb, pa))
        if pa > 6:
            flags.append('점 잔존')
    elif op in ('clone',) or ('글' in tgt or '표지' in tgt or '엠블럼' in tgt or '번호판' in tgt):
        db, da = edge_density(a, m), edge_density(b, m)
        rows.append('엣지 %.1f%%→%.1f%%' % (db, da))
        if da > max(2.0, db * 0.4):
            flags.append('획 잔존')
    if op == 'blur':
        lb, la = lap_var(a, m), lap_var(b, m)
        rows.append('세부 %.0f→%.0f (%.0f%%)' % (lb, la, 100 * la / (lb + 1e-3)))
        if la > lb * 0.35:
            flags.append('블러 약함')
    if op == 'recolor':
        s, bl = sat_blue(b, m)
        rows.append('채도 %.2f, 청-적 %.1f' % (s, bl))
        if s > 0.25 or bl > 8:
            flags.append('색 잔존')
    if op == 'cover':
        L = gblur(luma(b[box[1]:box[3] + 1, box[0]:box[2] + 1]), 1.0)
        st = np.abs(np.diff(L, axis=0)).mean() / (np.abs(np.diff(L, axis=1)).mean() + 1e-6)
        rows.append('가로줄 %.2f' % st)
        if st > 1.3:
            flags.append('수면 흔적')
    return rows, ('확인: ' + ', '.join(flags)) if flags else 'OK'


# ---------------------------------------------------------------- 검수 이미지
def label(img, caption, h=22):
    s = Image.new('RGB', (img.width, img.height + h), (40, 40, 40))
    s.paste(img, (0, h)); text(ImageDraw.Draw(s), (4, 5), caption, fill=(255, 255, 255))
    return s


def hstack(ims, gap=10):
    W = sum(i.width for i in ims) + gap * (len(ims) - 1); H = max(i.height for i in ims)
    s = Image.new('RGB', (W, H), (40, 40, 40)); x = 0
    for i in ims:
        s.paste(i, (x, 0)); x += i.width + gap
    return s


def vstack(ims, gap=10):
    W = max(i.width for i in ims); H = sum(i.height for i in ims) + gap * (len(ims) - 1)
    s = Image.new('RGB', (W, H), (40, 40, 40)); y = 0
    for i in ims:
        s.paste(i, (0, y)); y += i.height + gap
    return s


def crop_pair(a, b, box, target_px=420):
    W, H = a.shape[1], a.shape[0]
    x0, y0, x1, y1 = box
    m = max(24, (x1 - x0) // 3, (y1 - y0) // 3)
    X0, Y0, X1, Y1 = max(0, x0 - m), max(0, y0 - m), min(W, x1 + 1 + m), min(H, y1 + 1 + m)
    z = target_px / max(X1 - X0, Y1 - Y0)
    rs = Image.NEAREST if z >= 1 else Image.LANCZOS
    out = []
    for im in (a, b):
        t = Image.fromarray(u8(im[Y0:Y1, X0:X1]))
        out.append(t.resize((max(1, int(t.width * z)), max(1, int(t.height * z))), rs))
    return out, z


def frame1080(a):
    return np.asarray(Image.fromarray(u8(a)).resize((1080, 1920), Image.LANCZOS)).astype(np.float32)


def phone(a, box=None, s0=0.75):
    im = Image.fromarray(u8(frame1080(a))).resize((PHONE_W, int(PHONE_W * 16 / 9)), Image.LANCZOS)
    if box is not None:
        k = s0 * PHONE_W / 1080
        x0, y0, x1, y1 = [int(round(v * k)) for v in box]
        ImageDraw.Draw(im).rectangle((x0 - 3, y0 - 3, x1 + 3, y1 + 3), outline=(255, 60, 60), width=2)
    return im


def edit_sheet(e, a, b, rows, verdict):
    W, H = a.shape[1], a.shape[0]
    box = box_of(e, W, H)
    (ca, cb), z = crop_pair(a, b, box)
    a1, b1 = frame1080(a), frame1080(b)
    box1 = tuple(int(round(v * 0.75)) for v in box)
    (da, db), z1 = crop_pair(a1, b1, box1, target_px=260)
    top = hstack([label(ca, '원본 x%.2g' % z), label(cb, '편집본 x%.2g' % z)])
    mid = hstack([label(da, '1080 원본 x%.2g' % z1), label(db, '1080 편집본 x%.2g' % z1),
                  label(phone(b, box), '폰 %dpx (편집본)' % PHONE_W)])
    head = Image.new('RGB', (max(top.width, mid.width), 44), (20, 20, 20))
    d = ImageDraw.Draw(head)
    text(d, (6, 4), '%s  %s  [%s]' % (e['id'], e.get('target', ''), e.get('op', '')), fill=(255, 255, 255))
    text(d, (6, 24), ' | '.join(rows) + '   => ' + verdict, fill=(255, 220, 120))
    return vstack([head, top, mid])


def diff_map(a, b):
    """편집 영역 밖의 의도치 않은 변화를 찾기 위한 차이 지도(1080 축소, 4배 증폭)."""
    d = np.abs(luma(b) - luma(a)) * 4
    im = Image.fromarray(np.clip(d, 0, 255).astype(np.uint8)).resize((540, 960), Image.LANCZOS)
    return im.convert('RGB')


# ---------------------------------------------------------------- 메인
def review_plate(pid, plate, rows_md):
    orig, fixes = FILES.get(pid, (plate.get('source_file'), []))
    pa = find(orig) if orig else None
    pb = next((find(f) for f in fixes if find(f)), None)
    if not pa or not pb:
        rows_md.append('| %s | — | — | 파일 없음 (%s / %s) | — | | |' % (pid, orig, ' 또는 '.join(fixes)))
        print('  건너뜀: 파일 없음')
        return
    a, b = load(pa), load(pb)
    if a.shape != b.shape:
        rows_md.append('| %s | — | — | 크기 다름 %s vs %s | — | | |' % (pid, a.shape, b.shape))
        return
    H, W = a.shape[:2]
    print('  %s vs %s' % (os.path.basename(pa), os.path.basename(pb)))
    # 영역 밖 변화
    allm = np.zeros((H, W), bool)
    for e in plate.get('edits', []):
        bx = box_of(e, W, H)
        if bx:
            allm |= inside((bx[0] - 60, bx[1] - 60, bx[2] + 60, bx[3] + 60), W, H)
    ch = (np.abs(b - a).max(2) > 3) & ~allm
    if ch.any():
        ys, xs = np.where(ch)
        out_txt = '영역 밖 변화 %.1f%% (bbox x%d–%d y%d–%d) → 하늘 통일 등 의도한 변화인지 diff 지도로 확인' % (
            100 * ch.mean(), xs.min(), xs.max(), ys.min(), ys.max())
    else:
        out_txt = '영역 밖 변화 없음'
    hstack([label(diff_map(a, b), '%s |차이|x4 (편집 영역 밖도 표시)' % pid)]).save(
        os.path.join(OUT, '%s_diff.png' % pid))
    hstack([label(phone(a), '원본 폰 %dpx' % PHONE_W), label(phone(b), '편집본 폰 %dpx' % PHONE_W)]).save(
        os.path.join(OUT, '%s_phone.png' % pid))
    rows_md.append('| %s | 전체 | — | %s | `%s_phone.png`, `%s_diff.png` | | |' % (pid, out_txt, pid, pid))
    for e in plate.get('edits', []):
        if box_of(e, W, H) is None:
            rows_md.append('| %s | %s | %s | 영역 좌표 없음 → 전체 화면에서 확인 | `%s_phone.png` | | |' % (
                e['id'], e.get('target', ''), e.get('op', ''), pid))
            continue
        rows, verdict = metrics(e, a, b, W, H)
        edit_sheet(e, a, b, rows, verdict).save(os.path.join(OUT, '%s.png' % e['id']))
        rows_md.append('| %s | %s | %s | %s | %s · `%s.png` | | |' % (
            e['id'], e.get('target', ''), e.get('op', ''), '<br>'.join(rows), verdict, e['id']))
        print('   %-6s %s  %s' % (e['id'], verdict, '; '.join(rows)))


def main():
    os.makedirs(OUT, exist_ok=True)
    spec = json.load(open(os.path.join(IMG, 'plate_edits.json'), encoding='utf-8'))
    plates = spec['plates']
    sel = sys.argv[1:] or [k for k in FILES if k in plates or k in ('P3', 'P2clean')]
    md = ['# 플레이트 편집 독립 검수표', '',
          '- 기준: 제작명세서 3-4, `plate_edits.json` %s. 좌표는 원본 1440×2560.' % spec.get('version', ''),
          '- 검수자는 편집을 만든 사람과 달라야 한다. 자동 수치는 참고용이고, 판정은 이미지를 보고 한다.',
          '- 공통 합격 기준: 1080 축소본과 폰 크기(가로 %dpx)에서 **글자·얼굴·로고가 보이지 않는다**, 편집 흔적(경계·타일 반복·번짐)이 눈에 띄지 않는다, 영역 밖이 의도 없이 바뀌지 않았다.' % PHONE_W,
          '- 판정 칸: 통과 / 수정(무엇을) / 재생성.', '',
          '| ID | 대상 | 방법 | 자동 수치 | 자동 판정 · 이미지 | 검수자 판정 | 메모 |',
          '|---|---|---|---|---|---|---|']
    for pid in sel:
        print('==', pid)
        review_plate(pid, plates.get(pid, {'edits': []}), md)
    md += ['', '## P2 (서울달) — 수동 검수', '',
           '- 채택본 P2c_2 기준. `plate_edits.json`의 P2-02 좌표는 탈락한 P2c_1 기준이라 자동 검수에서 뺐다.',
           '- 볼 것: `compare/P2_full_orig_fix_P2a_P2b.png`, `compare/P2c-04_alpha_and_checker.png`',
           '- 기준: 기구 표면에 크레이터·로고·글자 없음 / 링 곤돌라·그물·단일 케이블 / 옛 반사 기둥 흔적 없음 / 새 반사가 기구 아래(1080 x≈562)에 있음 / 컷아웃 가장자리에 하늘색 테두리(헤일로) 없음',
           '', '| ID | 판정 | 메모 |', '|---|---|---|',
           '| P2-01 옛 반사 지움 | | |', '| P2-02 새 반사 | | |', '| P2-03 기구 표면 | | |', '| P2a·P2b 합성 | | |']
    with open(os.path.join(OUT, '검수표.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(md) + '\n')
    print('\n검수표: img/fix/review/검수표.md  (이미지는 같은 폴더)')


if __name__ == '__main__':
    main()
