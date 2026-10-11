"""6컷 만화 v2 「출처만 쓰면 괜찮다며?!」 — 스타일 가이드 v2 1장(만화)·0장(공통) 구현.
결과: out/v2/만화_v2.png (2000폭). 최종제출 폴더는 읽지도 쓰지도 않는다.

단위 규칙
- 페이지 요소(여백·테두리·배지·제목부·하단 띠·필수 표기)는 최종 2000폭 px.
- 패널 안 요소(띠·말풍선·꼬리·외곽선·효과음)는 원화 해상도에 맞춘 작업 캔버스 px(가이드 수치 그대로).
  작업 캔버스 = 패널 938×704 × SS(2.5) = 2345×1760. 원화 크롭(약 2200~2390폭)과 거의 같은 배율이라
  가이드의 원화 기준 수치를 그대로 쓰고, 모든 컷이 같은 크기로 보이게 한다. 최종 글자 = 캔버스 글자 / 2.5.
- 페이지 전체를 SS배(5000폭)로 그린 뒤 한 번만 축소해 선·도형까지 매끄럽게 만든다.
"""
import math, os, sys
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "proposals", "type"))
import make_type_proposal as T          # 조판 함수: 자간·대체 글리프(Pretendard ExtraBold)·외곽선·형광펜·효과음
os.chdir(ROOT)

# ============================================================== 6컷 원화 상수 (원화 교체 시 여기만 다시 실측)
P6_SRC = "img/P6.png"                   # 2026-10-07 확정 새 원화(이전 원화는 img/_P6_v1.png)
P6_CROP = (6, 0, 2395, 1792)            # 원본 px. 테두리 없는 풀블리드 원화 → 4:3에 맞춰 좌우 6px씩만 덜어냄
P6_BAND = (0, 292)                      # 상단 흰 여백 띠(0–279) + 아래 잉크선(281–288)까지 덮음
P6_MARK = None                          # 노트북 덮개 마크: 새 원화는 이미 지워져 있어 끔. (원본 x0,y0,x1,y1 바깥, 안쪽) 형식
P6_LAYOUT = dict(                       # 아래 좌표는 작업 캔버스(2345×1760) px
    bok_center=(705, 192),              # 복붙이 타원 중심(띠 왼쪽, 먼저 읽힘)
    bok_tail=dict(mouth=(1297, 1190), tip=(1240, 850), bend=0.0),     # 입을 일직선으로 겨눔, 이젤 모서리 오른쪽을 지나 머리 윤곽 바로 위에서 멈춤
    chips=[((440, 838), -4), ((440, 1068), 3), ((470, 1402), -2)],     # '퍼가요~♡' 댓글 칩(아이콘 무리 위, 그림 액자 왼쪽): (중심, 기울기)
    label=((742, 1178), -3),                                          # '그림: 복붙이' 라벨(액자 아래 왼쪽, 복붙이 팔 왼쪽)
    fairy_x=1240,                       # 요정 대사 줄무늬 시작 x(복붙이 타원 오른쪽)
    fairy_tail=dict(base_x=1860, aim=(1925, 760)),
)

# ============================================================== 공통 규격
INK, BG, PURPLE = (0x28, 0x22, 0x3C), (0xF2, 0xEE, 0xFC), (0x96, 0x5A, 0xC8)
YEL, RED, LINE, WHITE = (0xFF, 0xD8, 0x4A), (0xE5, 0x48, 0x4D), (0xD9, 0xD1, 0xF0), (255, 255, 255)
F = T.F                                  # title=Bagel Fat One, narr=Do Hyeon, talk=Jua, sfx=Black Han Sans, b/xb/sb=Pretendard
AI_NOTE = "본 작품은 생성형 AI를 활용해 제작되었습니다"   # 한 글자도 바꾸지 않는다
MANNER = ["남의 작품을 똑같이·비슷하게 따라 하게 시키지 않기", "쓸 땐 이용 허락·조건 먼저", "AI 활용 사실 밝히기"]   # ③ 10/8 감독 결정(법적 의무 오해 방지, 숏폼과 통일)
MANNER_LINES = [["남의 작품을 똑같이·비슷하게", "따라 하게 시키지 않기"], ["쓸 땐 이용", "허락·조건 먼저"], ["AI 활용", "사실 밝히기"]]

SS = 2.5                                 # 마스터 배율
W, M, GC, GR = 2000, 48, 28, 56          # 페이지 폭, 좌우 여백, 열 간격, 행 간격 (최종 px)
PW, PH = (W - 2 * M - GC) // 2, 704      # 938 × 704
HEAD, BORDER = 300, 6
CW, CH = round(PW * SS), round(PH * SS)  # 2345 × 1760 작업 캔버스
BI = BORDER * SS                         # 패널 테두리가 덮는 캔버스 폭(15)

TALK, LEAD, TRK = 84, 1.26, -0.02        # 대사: Jua 84(최종 33.6px), 행간 126%, 자간 −2%
LW = 12                                  # 말풍선 선
BAND_LINE = 10                           # 띠 아래 잉크선

CROP = {1: (90, 59, 2310, 1724), 2: (133, 91, 2270, 1693), 3: (83, 62, 2314, 1735),
        4: (70, 49, 2329, 1743), 5: (0, 0, 2389, 1792), 6: P6_CROP}
BAND = {1: (59, 276), 2: (91, 326), 4: (49, 350), 5: (0, 278), 6: P6_BAND}
SRC = {n: f"img/P{n}.png" for n in range(1, 6)}; SRC[6] = P6_SRC
FWEET = (930, 870, 1155, 975)            # 2컷 영문 효과음(원본 px) — '삐익!!'이 완전히 덮어야 함


# ============================================================== 기하 도우미
def scale_of(n): return CW / (CROP[n][2] - CROP[n][0])
def to_cv(n, x, y): s = scale_of(n); return ((x - CROP[n][0]) * s, (y - CROP[n][1]) * s)
def band_h(n): return round((BAND[n][1] - CROP[n][1]) * scale_of(n))

def unit(dx, dy):
    L = math.hypot(dx, dy) or 1.0
    return dx / L, dy / L

def offset_poly(pts, d, miter_limit=6.0):
    """다각형을 바깥으로 d만큼 키운 윤곽(마이터 결합, 한계 넘으면 베벨). 잉크 테두리용."""
    n = len(pts)
    area = 0.5 * sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n))
    sg = 1 if area > 0 else -1
    nor = []
    for i in range(n):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
        ux, uy = unit(x1 - x0, y1 - y0); nor.append((sg * uy, -sg * ux))
    out = []
    for i in range(n):
        a, b = nor[i - 1], nor[i]
        bx, by = a[0] + b[0], a[1] + b[1]; bl = math.hypot(bx, by)
        if bl < 1e-6:
            out.append((pts[i][0] + d * b[0], pts[i][1] + d * b[1])); continue
        bx, by = bx / bl, by / bl
        m = d / max(bx * b[0] + by * b[1], 1e-6)
        if m > miter_limit * d:
            out += [(pts[i][0] + d * a[0], pts[i][1] + d * a[1]), (pts[i][0] + d * b[0], pts[i][1] + d * b[1])]
        else:
            out.append((pts[i][0] + bx * m, pts[i][1] + by * m))
    return out

def ell_box(c, a, b): return (c[0] - a, c[1] - b, c[0] + a, c[1] + b)

def ell_point(c, a, b, toward):
    """타원 중심에서 toward 방향으로 나간 반직선과 타원 경계의 교점, 그 점의 바깥 법선."""
    ux, uy = unit(toward[0] - c[0], toward[1] - c[1])
    t = 1 / math.sqrt((ux / a) ** 2 + (uy / b) ** 2)
    px, py = c[0] + ux * t, c[1] + uy * t
    nx, ny = unit((px - c[0]) / a ** 2, (py - c[1]) / b ** 2)
    return (px, py), (nx, ny)

def bez(p0, p1, p2, k=28):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in (i / k for i in range(k + 1))]


# ============================================================== 말풍선 묶음(외곽선을 합집합으로 그림)
class Group:
    """여러 도형(타원·꼬리·연결목)을 한 덩어리로: 잉크(바깥 확장) → 흰 채움 순서라 겹친 곳에 선이 남지 않는다."""
    def __init__(self, lw=LW, fill=WHITE): self.lw, self.fill, self.shapes = lw, fill, []
    def ellipse(self, c, a, b): self.shapes.append(("e", (c, a, b))); return self
    def poly(self, pts, miter=6.0): self.shapes.append(("p", (pts, miter))); return self
    def draw(self, d):
        for kind, s in self.shapes:
            if kind == "e": d.ellipse(ell_box(s[0], s[1] + self.lw, s[2] + self.lw), fill=INK)
            else: d.polygon(offset_poly(s[0], self.lw, s[1]), fill=INK)
        for kind, s in self.shapes:
            if kind == "e": d.ellipse(ell_box(*s), fill=self.fill)
            else: d.polygon(s[0], fill=self.fill)

def text_metrics(lines, path, size, leading, track):
    ws = [T.line_w(l, path, size, track) for l in lines]
    asc = -T.font(path, size).getbbox("한글", anchor="ls")[1]
    return ws, asc

def fit_ellipse(lines, path=F["talk"], size=TALK, leading=LEAD, track=TRK, pad=None):
    """가이드 타원 = 텍스트 가로 +24%, 세로 +40%. 글자 모서리가 선(LW)+여유에 닿으면 같은 비율로 키운다."""
    ws, asc = text_metrics(lines, path, size, leading, track)
    n = len(lines); lh = size * leading
    a0, b0 = 1.24 * max(ws) / 2, 1.40 * ((n - 1) * lh + size) / 2
    m = LW + (pad if pad is not None else 0.20 * size)
    corners = []
    for i, w in enumerate(ws):
        yc = (i - (n - 1) / 2) * lh
        corners += [(w / 2, yc - asc / 2 - 2), (w / 2, yc + asc / 2 + 2)]
    k = 1.0
    while any((x / (k * a0 - m)) ** 2 + (y / (k * b0 - m)) ** 2 > 1 for x, y in corners): k += 0.01
    QA["k"].append(round(k, 2))
    return a0 * k, b0 * k, k

def ink_tip(build, tip, idx, d=LW):
    """뾰족한 꼬리의 잉크 끝(마이터)이 정확히 tip에 오도록 흰 꼬리 끝을 그만큼 당긴다."""
    pts = build(tip); o = offset_poly(pts, d, 1e9)[idx]
    return build((2 * tip[0] - o[0], 2 * tip[1] - o[1]))

def curved_tail(c, a, b, tip, mouth=None, base=70, bend=0.12):
    """휜 쐐기 꼬리: 밑변 70, 잉크 끝이 tip. mouth를 주면 밑변 중심·끝·입이 한 직선(입을 정확히 겨눔). bend>0 이면 왼쪽으로 휨."""
    return ink_tip(lambda t: _curved(c, a, b, t, base, bend, mouth), tip, 28)

def ell_hit(c, a, b, start, u):
    """start에서 u 방향으로 가다 처음 만나는 타원 경계점과 바깥 법선."""
    px, py = start[0] - c[0], start[1] - c[1]
    A = (u[0] / a) ** 2 + (u[1] / b) ** 2; B = 2 * (px * u[0] / a ** 2 + py * u[1] / b ** 2)
    C = (px / a) ** 2 + (py / b) ** 2 - 1
    t = (-B - math.sqrt(max(B * B - 4 * A * C, 0))) / (2 * A)
    hx, hy = start[0] + u[0] * t, start[1] + u[1] * t
    return (hx, hy), unit((hx - c[0]) / a ** 2, (hy - c[1]) / b ** 2)

def _curved(c, a, b, tip, base, bend, mouth=None):
    if mouth: (px, py), (nx, ny) = ell_hit(c, a, b, tip, unit(tip[0] - mouth[0], tip[1] - mouth[1]))
    else: (px, py), (nx, ny) = ell_point(c, a, b, tip)
    tx, ty = -ny, nx
    inset = LW + 8                                   # 밑변을 타원 안으로 넣어 흰 채움이 선을 덮게 함
    L = (px - tx * base / 2 - nx * inset, py - ty * base / 2 - ny * inset)
    R = (px + tx * base / 2 - nx * inset, py + ty * base / 2 - ny * inset)
    vx, vy = tip[0] - px, tip[1] - py; ln = math.hypot(vx, vy); ux, uy = vx / ln, vy / ln
    ox, oy = -uy * bend * ln, ux * bend * ln
    c1 = ((L[0] + tip[0]) / 2 + ox, (L[1] + tip[1]) / 2 + oy)
    c2 = ((R[0] + tip[0]) / 2 + ox, (R[1] + tip[1]) / 2 + oy)
    pts = bez(L, c1, tip) + bez(R, c2, tip)[::-1][1:]
    return pts

def draw_text_block(d, center, lines, path=F["talk"], size=TALK, leading=LEAD, track=TRK, fill=INK, dy=0, **kw):
    said(lines); x, y = center
    T.draw_block(d, (x, y + dy, x, y + dy), lines, path, size, leading=leading, track=track, fill=fill, **kw)

def balloon(d, center, lines, tail=None, size=TALK, extra=()):
    """복붙이 타원 말풍선. tail=dict(tip, mouth, bend). extra=(Group에 더할 도형들) — 연결 타원 등."""
    a, b, k = fit_ellipse(lines, size=size)
    g = Group().ellipse(center, a, b)
    if tail: g.poly(curved_tail(center, a, b, tail["tip"], tail.get("mouth"), bend=tail.get("bend", 0.12)), miter=1e9)
    for s in extra: g.shapes.append(s)
    g.draw(d)
    return a, b, k

def link_neck(c1, c2, w=46):
    ux, uy = unit(c2[0] - c1[0], c2[1] - c1[1]); px, py = -uy * w / 2, ux * w / 2
    return ("p", ([(c1[0] + px, c1[1] + py), (c2[0] + px, c2[1] + py), (c2[0] - px, c2[1] - py), (c1[0] - px, c1[1] - py)], 6.0))


# ============================================================== 상단 띠 · 요정 대사
def cover_band(d, bh):
    d.rectangle((0, 0, CW, bh), fill=WHITE)
    d.rectangle((0, bh, CW, bh + BAND_LINE), fill=INK)

def referee_stripes(im, x, y0, y1, w=24, step=12):
    """왼쪽 24px 심판 줄무늬: 12px 간격으로 잉크/흰색이 교차하는 사선."""
    col = Image.new("RGB", (w, int(y1 - y0)), WHITE); cd = ImageDraw.Draw(col)
    for k in range(-w, col.height + w, 2 * step):
        cd.polygon([(0, k), (w, k - w), (w, k - w + step), (0, k + step)], fill=INK)
    im.paste(col, (int(x), int(y0)))

def fairy_tail(d, bh, base_x, aim, base=70, length=120):
    """각진 꼬리: 띠 아래 잉크선을 뚫고 요정을 가리킨다(밑변 70, 길이 120)."""
    y = bh - 2
    ux, uy = unit(aim[0] - base_x, aim[1] - (bh + BAND_LINE))
    tip = (base_x + ux * length, bh + BAND_LINE + uy * length)     # 잉크 끝 = 띠 아래선에서 120
    tri = ink_tip(lambda t: [(base_x - base / 2, y), t, (base_x + base / 2, y)], tip, 1, BAND_LINE)
    d.polygon(offset_poly(tri, BAND_LINE, 1e9), fill=INK)
    d.rectangle((base_x - base, bh - 3 * BAND_LINE, base_x + base, bh - 1), fill=WHITE)   # 띠 안으로 번진 잉크 정리
    d.polygon(tri, fill=WHITE)
    return tip

def fairy_box(im, d, bh, x, lines, tail_x, aim, size=TALK):
    """흰 띠 + 왼쪽 24px 심판 줄무늬 + 각진 꼬리. 글자는 줄무늬 오른쪽에 왼쪽 정렬."""
    fairy_tail(d, bh, tail_x, aim)
    referee_stripes(im, max(x, BI), 0, bh)
    said(lines); ws, _ = text_metrics(lines, F["talk"], size, LEAD, TRK)
    tx = max(x, BI) + 24 + 44
    yc0 = (BI + bh) / 2 - size * LEAD * (len(lines) - 1) / 2
    for i, (ln, w) in enumerate(zip(lines, ws)):
        T.draw_line(d, tx + w / 2, yc0 + i * size * LEAD, ln, F["talk"], size, track=TRK, fill=INK)
    return tx + max(ws)


# ============================================================== 감정 풍선
def spike_balloon(im, d, c, rx, ry, text_spec, tail_tip=None):
    """헉?!: 14각 가시형(내경 0.78) + 짧은 쐐기 꼬리. 글자는 Jua, 글자별 기울기."""
    pts = T.star(c, (rx * 0.78, ry * 0.78), (rx, ry), 14, rot=-math.pi / 2 + 0.11)
    g = Group().poly(pts, miter=4)
    if tail_tip:
        ux, uy = unit(tail_tip[0] - c[0], tail_tip[1] - c[1]); px, py = -uy, ux
        b0 = (c[0] + ux * ry * 0.55, c[1] + uy * ry * 0.55)
        g.poly(ink_tip(lambda t: [(b0[0] + px * 30, b0[1] + py * 30), t, (b0[0] - px * 30, b0[1] - py * 30)], tail_tip, 1), miter=1e9)
    g.draw(d)
    T.sfx(im, (c[0] + 2, c[1] + 2), text_spec, F["talk"], angle=0, fill=INK, strokes=(), track=-0.02)

def covers(pts, rect, margin=8):
    m = Image.new("L", (CW, CH), 0); ImageDraw.Draw(m).polygon(pts, fill=255)
    x0, y0, x1, y1 = rect
    return m.crop((int(x0) - margin, int(y0) - margin, int(x1) + margin + 1, int(y1) + margin + 1)).getextrema()[0] == 255

def burst(im, d, c, rin, rout, spec, must_cover=None):
    """삐익!!: #FFD84A 12각 폭발형(−8°) + 효과음 규격(Black Han Sans, 빨강 + 흰 11 + 잉크 20, 자간 −5%, 전체 7°).
    must_cover(사각형)가 있으면 그 영역이 폭발형 채움 안에 완전히 들어갈 때까지 같은 비율로 키운다."""
    k = 1.0
    while True:
        pts = T.star(c, (rin[0] * k, rin[1] * k), (rout[0] * k, rout[1] * k), 12, rot=math.radians(-8),
                     jitter=(1, .9, 1.07, .95, .88, 1.05, .97, .92))
        if not must_cover or covers(pts, must_cover): break
        k += 0.02
    QA["burst_k"] = k
    Group(fill=YEL).poly(pts, miter=4).draw(d)
    T.sfx(im, c, spec, F["sfx"], angle=7, fill=RED, strokes=((20, INK), (11, WHITE)), track=-0.05)
    return pts

def outline_word(im, c, runs, size, angle=0.0, path=F["talk"]):
    """머쓱…: 풍선 없이 흰 외곽선 10px 글자."""
    said([runs])
    w = T.line_w(runs, path, size, TRK); lay = Image.new("RGBA", (int(w + size * 2), int(size * 2.6)), (0, 0, 0, 0))
    T.draw_line(ImageDraw.Draw(lay), lay.width / 2, lay.height / 2, runs, path, size, track=TRK, fill=INK, strokes=((10, WHITE),))
    lay = lay.rotate(angle, resample=Image.BICUBIC, expand=True)
    im.paste(lay, (int(c[0] - lay.width / 2), int(c[1] - lay.height / 2)), lay)


# ============================================================== 컷별 식자
def load_panel(n):
    im = Image.open(SRC[n]).convert("RGB")
    if n == 6 and P6_MARK: im = remove_mark(im, *P6_MARK)
    return im.crop(CROP[n]).resize((CW, CH), Image.LANCZOS)

def remove_mark(im, outer, inner):
    """(v1 유지용) 덮개 마크를 주변 그라데이션 평면 근사로 채움. 새 6컷 원화에는 쓰지 않는다(P6_MARK=None)."""
    import numpy as np
    a = np.array(im).astype(float); x0, y0, x1, y1 = outer; ix0, iy0, ix1, iy1 = inner
    yy, xx = np.mgrid[y0:y1, x0:x1]; inn = (yy >= iy0) & (yy < iy1) & (xx >= ix0) & (xx < ix1)
    A = np.c_[xx[~inn], yy[~inn], np.ones((~inn).sum())]
    for ch in range(3):
        coef, *_ = np.linalg.lstsq(A, a[y0:y1, x0:x1, ch][~inn], rcond=None)
        blk = a[y0:y1, x0:x1, ch]; blk[inn] = (coef[0] * xx + coef[1] * yy + coef[2])[inn]
    return Image.fromarray(np.clip(a, 0, 255).astype("uint8"))

QA = {"text": {}, "k": []}                 # 자체 점검용 기록
CUR = [0]                                  # 지금 조판 중인 컷 번호

def said(lines):
    """조판한 글자를 컷별로 기록 → 가이드 확정 대사와 한 글자씩 대조."""
    for ln in lines:
        QA["text"].setdefault(CUR[0], []).append(ln if isinstance(ln, str) else "".join(r[0] for r in ln))
    return lines

GUIDE_TEXT = {                             # 스타일 가이드 1장 '대사(최종)' (읽는 순서, 공백 무시하고 대조)
    1: "출처: 인터넷" + "복붙이의 블로그 시간 ♪" + "퍼가요~♡ 출처: 인터넷! 이 정도면 됐지?",
    2: "땡!! 출처 표시는 기본, 이용 허락·조건이 먼저야!",
    3: "그럼 AI한테 시키면 되지! AI야, 저 그림이랑 똑같이 그려 줘!",
    4: "그럼… 살~짝 비슷하게만?" + "그것도 땡! 남의 작품 표현을 똑같이·비슷하게 따라 하게 시키는 건 피해야 해!" + "머쓱…",
    5: "공유마당에서 이용 조건을 확인하고 쓰거나, 직접 만들어 봐!" + "오호~ 무료여도 조건 확인!",
    6: "내 그림도 퍼 간다고?! 허락부터 받아 줘요!" + "퍼가요~♡" * 3 + "그림: 복붙이"
       + "그린카드! 만들어 보니 알겠지? 창작자 존중이 K-저작권 매너!",
}

P1_LABEL = dict(center=(1560, 1341), size=(355, 86), angle=-3.6)   # 1컷 노트북 사진 아래 빈 라벨 → '출처: 인터넷'(캔버스 px)

def photo_label(im, center, size, angle, text="출처: 인터넷", fs=70):
    """원화의 빈 살구색 라벨을 같은 색·같은 기울기로 조금 넓혀 다시 그리고 Jua 28px로 '출처: 인터넷'(숏폼과 같은 문구)."""
    w, h = size; src = im.crop((1470, 1305, 1600, 1345)).convert("RGB")
    col = tuple(sorted(src.getdata(), key=sum)[len(src.getdata()) * 3 // 4])    # 라벨 안쪽 살구색(밝은 쪽 분위수)
    lay = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((10, 10, 10 + w, 10 + h), 10, fill=col, outline=INK, width=8)
    runs = said([text])[0]
    assert T.line_w(runs, F["talk"], fs, TRK) <= w - 36, "라벨 글자 넘침"
    T.draw_line(d, 10 + w / 2, 10 + h / 2 + 2, runs, F["talk"], fs, track=TRK, fill=INK)
    paste_center(im, lay, center, angle)

def panel1():
    im = load_panel(1); d = ImageDraw.Draw(im); bh = band_h(1)
    photo_label(im, **P1_LABEL)
    cover_band(d, bh)
    narr = said(["복붙이의 블로그 시간 ♪"])[0]; nw = T.line_w(narr, F["narr"], TALK)       # 내레이션: 잉크 채움 + 흰 Do Hyeon, 좌상단
    d.rectangle((0, 0, BI + 52 + nw + 52, bh + BAND_LINE), fill=INK)
    T.draw_line(d, BI + 52 + nw / 2, (BI + bh) / 2, narr, F["narr"], TALK, fill=WHITE)
    A, B = (1235, 128), (905, 447)                                           # 퍼가요~♡(띠 안) → 출처: 인터넷!(아래), 연결
    la = [[("퍼가요~♡",)]]; lb = ["출처: 인터넷!", "이 정도면 됐지?"]
    aa, ab, _ = fit_ellipse(la); ba, bb, _ = fit_ellipse(lb)
    g = Group().ellipse(A, aa, ab).ellipse(B, ba, bb)
    g.shapes.append(link_neck(A, B))
    g.poly(curved_tail(B, ba, bb, (846, 678), bend=0.10), miter=1e9)
    g.draw(d)
    draw_text_block(d, A, la); draw_text_block(d, B, lb)
    QA[1] = dict(A=(A, aa, ab), B=(B, ba, bb))
    return im

HAND_P2 = (690, 730, 873, 986)            # 2컷 요정 손·호루라기 영역(캔버스). FWEET(x≥875) 바로 왼쪽

def keep_front(im, orig, box, seeds, dark=120):
    """box 안에서 벽(시드에서 번지는 영역, 진한 윤곽선에서 멈춤)이 아닌 것 = 앞에 있는 손·호루라기 → 원화 픽셀로 되살린다.
    폭발형이 FWEET를 다 덮으면서도 손을 가리지 않게(폭발형이 손 뒤로 들어간 것처럼) 만드는 합성."""
    from PIL import ImageFilter
    x0, y0, x1, y1 = box
    lum = orig.crop(box).convert("L").point(lambda v: 0 if v < dark else 255)
    for sx, sy in seeds:
        if lum.getpixel((sx - x0, sy - y0)) == 255: ImageDraw.floodfill(lum, (sx - x0, sy - y0), 128, thresh=0)
    mk = lum.point(lambda v: 0 if v == 128 else 255)
    mk = mk.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(0.7))
    im.paste(orig.crop(box), (x0, y0), mk)
    QA["front_mask"] = mk

def panel2():
    im = load_panel(2); orig = im.copy(); d = ImageDraw.Draw(im); bh = band_h(2)
    cover_band(d, bh)
    fairy_box(im, d, bh, BI, [[("땡!!", RED), (" 출처 표시는 기본,",)],
                              [("이용 ",), ("허락·조건", None, YEL), ("이 먼저야!",)]],
              tail_x=850, aim=(700, 650))
    x0, y0 = to_cv(2, FWEET[0], FWEET[1]); x1, y1 = to_cv(2, FWEET[2], FWEET[3])
    c = ((x0 + x1) / 2 + 22, (y0 + y1) / 2 + 2)
    pts = burst(im, d, c, (172, 108), (226, 150), [("삐", 112, 6, 4), ("익", 128, -4, -3), ("!", 128, -6, -9), ("!", 128, -10, -15)],
                must_cover=(x0, y0, x1, y1))
    QA["fweet"] = ((x0, y0, x1, y1), pts)
    keep_front(im, orig, HAND_P2, seeds=[(868, 760), (870, 790), (868, 830), (862, 980), (850, 745), (871, 900)])   # 요정 손·호루라기는 폭발형 앞으로
    spike_balloon(im, d, (1735, 392), 196, 128, [("헉", 120, 0, 6), ("?", 108, -6, -6), ("!", 108, -12, -12)],
                  tail_tip=(1712, 548))
    return im

def panel3():
    im = load_panel(3); d = ImageDraw.Draw(im)
    A, B = (1215, 205), (1830, 395)                                          # 두 박자: 생각 → 명령
    la, lb = ["그럼 AI한테", "시키면 되지!"], ["AI야, 저 그림이랑", "똑같이 그려 줘!"]
    aa, ab, _ = fit_ellipse(la); ba, bb, _ = fit_ellipse(lb)
    g = Group().ellipse(A, aa, ab).ellipse(B, ba, bb)
    g.shapes.append(link_neck(A, B))
    g.poly(curved_tail(B, ba, bb, (1660, 600), bend=0.12), miter=1e9)
    g.draw(d)
    draw_text_block(d, A, la); draw_text_block(d, B, lb)
    QA[3] = dict(A=(A, aa, ab), B=(B, ba, bb))
    return im

def panel4():
    im = load_panel(4); d = ImageDraw.Draw(im); bh = band_h(4)
    cover_band(d, bh)
    c = (392, 170); lines = ["그럼… 살~짝", "비슷하게만?"]                         # 복붙이가 먼저 → 띠 왼쪽
    a, b, _ = balloon(d, c, lines, tail=dict(tip=(630, 660), bend=0.10))
    draw_text_block(d, c, lines)
    fairy_box(im, d, bh, 790, [[("그것도 ",), ("땡!", RED), (" 남의 작품 표현을 ",), ("똑같이·비슷하게", None, YEL)],
                               [("따라 하게 시키는 건 피해야 해!",)]],
              tail_x=1330, aim=(1560, 760))
    outline_word(im, (250, 606), [("머쓱…",)], 130, angle=6)          # 최종 52px
    QA[4] = dict(A=(c, a, b))
    return im

def panel5():
    im = load_panel(5); d = ImageDraw.Draw(im); bh = band_h(5)
    cover_band(d, bh)
    fairy_box(im, d, bh, BI, [[("공유마당", None, YEL), ("에서 이용 조건을 확인하고 쓰거나,",)], [("직접 만들어 봐!",)]],
              tail_x=1395, aim=(1620, 720))
    c = (995, 455); lines = ["오호~ 무료여도", "조건 확인!"]
    a, b, _ = balloon(d, c, lines, tail=dict(tip=(812, 710), bend=-0.12))
    draw_text_block(d, c, lines)
    QA[5] = dict(A=(c, a, b))
    return im

def comment_chip(size=75):
    """'퍼가요~♡' 댓글 칩 — 숏폼 v2 mini_chip과 같은 모양(흰 둥근 사각, 잉크 선, 아래 그림자, Jua, ♡ 빨강).
    숏폼(1080폭, 글자 46)을 만화 글자 30px(캔버스 75)에 맞춰 같은 비율로 키움."""
    from PIL import ImageFilter
    k = size / 46
    runs = [("퍼가요~",), ("♡", RED)]; said([runs])
    gl, w = T.layout(runs, F["talk"], size, TRK)
    bw, bh_, r, lw, px = round(w + 56 * k), round(74 * k), round(22 * k), round(5 * k), 28 * k
    lay = Image.new("RGBA", (bw + 60, bh_ + 70), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((30, 30 + 8 * k, 30 + bw, 30 + 8 * k + bh_), r, fill=(*INK, 90))
    lay = lay.filter(ImageFilter.GaussianBlur(5 * k)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((30, 30, 30 + bw, 30 + bh_), r, fill=WHITE, outline=INK, width=lw)
    by = 30 + bh_ / 2 + T.base_off(F["talk"], size)
    for gx, a, ch, fnt, col, hl in gl: d.text((30 + px + gx, by), ch, font=fnt, fill=col or INK, anchor="ls")
    return lay

def paste_center(im, lay, c, rot=0.0):
    if rot: lay = lay.rotate(rot, resample=Image.BICUBIC, expand=True)
    im.paste(lay, (round(c[0] - lay.width / 2), round(c[1] - lay.height / 2)), lay)
    return (c[0] - lay.width / 2, c[1] - lay.height / 2, c[0] + lay.width / 2, c[1] + lay.height / 2)

def name_label(text="그림: 복붙이", size=70):
    """그림 이름표: 흰 종이 라벨 + 잉크 선, Jua(최종 28px)."""
    runs = said([text])[0]; w = T.line_w(runs, F["talk"], size, TRK)
    bw, bh_ = round(w + 2 * 24), round(size * 1.40)
    lay = Image.new("RGBA", (bw + 24, bh_ + 24), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((12, 12, 12 + bw, 12 + bh_), 14, fill=WHITE, outline=INK, width=8)
    T.draw_line(d, 12 + bw / 2, 12 + bh_ / 2, runs, F["talk"], size, track=TRK, fill=INK)
    return lay

def panel6():
    im = load_panel(6); d = ImageDraw.Draw(im); bh = band_h(6); L = P6_LAYOUT
    cover_band(d, bh)
    boxes = [paste_center(im, comment_chip(), c, rot) for c, rot in L["chips"]]   # 댓글이 그림 쪽으로 몰려옴
    boxes.append(paste_center(im, name_label(), *L["label"]))
    QA["p6_boxes"] = boxes
    c = L["bok_center"]; lines = ["내 그림도 퍼 간다고?!", "허락부터 받아 줘요!"]
    a, b, _ = balloon(d, c, lines, tail=L["bok_tail"])
    draw_text_block(d, c, lines)
    QA["text"][6] = QA["text"][6][4:] + QA["text"][6][:4]   # 대조는 대사만(칩·라벨은 별도 확인)
    fairy_box(im, d, bh, L["fairy_x"], [[("그린카드! 만들어 보니 알겠지?",)],
                                        [("창작자 존중", None, YEL), ("이 K-저작권 매너!",)]],
              tail_x=L["fairy_tail"]["base_x"], aim=L["fairy_tail"]["aim"])
    QA[6] = dict(A=(c, a, b))
    return im


# ============================================================== 페이지 조립
def S(v): return round(v * SS)

def title_block(pg, d):
    t = [("출처만 쓰면 괜찮다며",), ("?!", RED)]
    target = S(W * 0.68)                                                       # 제목 폭 = 페이지의 68%
    size = S(100)
    while T.line_w(t, F["title"], size + 1) <= target: size += 1
    cx, cy = S(W / 2), S(104)
    w = T.line_w(t, F["title"], size); QA["title"] = (round(size / SS, 1), round(w / SS / W * 100, 1))
    by = cy + T.base_off(F["title"], size)
    asc = -T.font(F["title"], size).getbbox("출", anchor="ls")[1]
    bar_h = S(30); top = by - asc / 3 - bar_h / 2 + S(4)                        # 글자 아래 1/3 높이에 30px 노랑 바
    d.rectangle((cx - w / 2 - S(14), top, cx + w / 2 + S(14), top + bar_h), fill=YEL)
    T.draw_line(d, cx, cy, t, F["title"], size, fill=INK)
    sub = "퍼가요 말고 허락부터!"; fs = S(40); sw = T.line_w(sub, F["narr"], fs)  # 부제: 보라 알약, 흰 40, 패딩 14/32
    ph = fs + 2 * S(14); pw = sw + 2 * S(32); py = S(228)
    d.rounded_rectangle((cx - pw / 2, py - ph / 2, cx + pw / 2, py + ph / 2), ph / 2, fill=PURPLE)
    T.draw_line(d, cx, py, sub, F["narr"], fs, fill=WHITE)

def badge(d, x, y, n):
    """컷 번호: 지름 44, 흰 링 4, 숫자 24(Black Han Sans — Bagel은 90px 이상 규칙). 좌하단 꼭짓점 중심."""
    r = S(22); d.ellipse((x - r, y - r, x + r, y + r), fill=WHITE)
    r2 = S(18); d.ellipse((x - r2, y - r2, x + r2, y + r2), fill=INK)
    T.draw_line(d, x, y, str(n), F["sfx"], S(24), fill=WHITE)

def manner_band(d, top):
    """'AI 창작 매너 3' 띠: 잉크 바탕, 흰 Do Hyeon, 번호 원(노랑). 세 항목 모두 두 줄(줄 길이 균형), 항목 사이 간격을 같게."""
    x0, x1, h = S(M), S(W - M), S(172); d.rectangle((x0, top, x1, top + h), fill=INK)
    cy = top + h / 2; pad = S(48)
    lab = [("AI 창작 매너 ",), ("3", YEL)]; ls = S(54); lw_ = T.line_w(lab, F["narr"], ls)
    T.draw_line(d, x0 + pad + lw_ / 2, cy, lab, F["narr"], ls, fill=WHITE)
    dx = x0 + pad + lw_ + S(44); d.rectangle((dx, top + S(36), dx + S(3), top + h - S(36)), fill=PURPLE)
    items = MANNER_LINES
    fs, r, gap_t = S(36), S(22), S(16)
    gws = [2 * r + gap_t + max(T.line_w(l, F["narr"], fs) for l in it) for it in items]   # 번호 원 + 두 줄 묶음 폭
    edge = S(60)                                                             # 구분선 뒤·오른끝 앞 여백
    gap = (x1 - (dx + S(3)) - 2 * edge - sum(gws)) / 2                       # 항목 사이 간격은 같게
    QA["manner_gap"] = round(gap / SS, 1)
    xs = [dx + S(3) + edge]
    for g in gws[:-1]: xs.append(xs[-1] + g + gap)
    for i, it in enumerate(items):
        gw, x = gws[i], xs[i]
        d.ellipse((x, cy - r, x + 2 * r, cy + r), fill=YEL)
        T.draw_line(d, x + r, cy, str(i + 1), F["narr"], S(30), fill=INK)
        lh = fs * 1.3; y0 = cy - lh / 2
        for j, ln in enumerate(it):
            lw2 = T.line_w(ln, F["narr"], fs)
            assert gap > S(40), "매너 띠 간격 부족"
            T.draw_line(d, x + 2 * r + gap_t + lw2 / 2, y0 + j * lh, ln, F["narr"], fs, fill=WHITE)
    assert "".join(" ".join(i) for i in items).replace(" ", "") == "".join(MANNER).replace(" ", "")
    return top + h

def build():
    panels = {}
    for n, fn in enumerate((panel1, panel2, panel3, panel4, panel5, panel6), 1):
        CUR[0] = n; panels[n] = fn()
    rows_bottom = HEAD + 3 * PH + 2 * GR
    band_top = rows_bottom + GR
    H = band_top + 172 + 30 + 29 + 52
    pg = Image.new("RGB", (S(W), S(H)), BG); d = ImageDraw.Draw(pg)
    title_block(pg, d)
    for i in range(6):
        x = M + (i % 2) * (PW + GC); y = HEAD + (i // 2) * (PH + GR)
        pg.paste(panels[i + 1], (S(x), S(y)))
        d.rectangle((S(x), S(y), S(x + PW) - 1, S(y + PH) - 1), outline=INK, width=S(BORDER))
    for i in range(6):
        x = M + (i % 2) * (PW + GC); y = HEAD + (i // 2) * (PH + GR)
        badge(d, S(x), S(y + PH), i + 1)
    manner_band(d, S(band_top))
    nf = T.font(F["b"], S(40))
    d.text((S(W - M), S(H - 52)), AI_NOTE, font=nf, fill=INK, anchor="rs")       # 필수 표기: 우측 하단, 기준선 H−52
    out = pg.resize((W, H), Image.LANCZOS)
    os.makedirs("out/v2", exist_ok=True)
    out.save("out/v2/만화_v2.png", optimize=True)
    return out, panels, pg


def qa_checks():
    """FWEET 완전 가림(폭발형 채움이 FWEET 사각형+8px 포함) + 대사 문구가 가이드와 글자 단위로 같은지."""
    rect, pts = QA["fweet"]
    assert covers(pts, rect), "FWEET가 폭발형 밖으로 나옴"
    for n, want in GUIDE_TEXT.items():
        got = "".join(QA["text"].get(n, [])).replace(" ", ""); want = want.replace(" ", "")
        assert got == want, f"{n}컷 문구 불일치: {got} != {want}"
    return True


if __name__ == "__main__":
    out, panels, pg = build()
    print("saved", out.size, "burst k", round(QA["burst_k"], 2), "ellipse k", QA["k"], "title(px,%)", QA["title"],
          "manner gap", QA["manner_gap"], "QA:", qa_checks())
    if len(sys.argv) > 1:                              # QA 이미지: 스크래치 폴더에 컷별 확대본
        qd = sys.argv[1]; os.makedirs(qd, exist_ok=True)
        for n, im in panels.items(): im.resize((CW // 2, CH // 2), Image.LANCZOS).save(os.path.join(qd, f"p{n}.png"))
        for i in range(6):
            x = M + (i % 2) * (PW + GC); y = HEAD + (i // 2) * (PH + GR)
            out.crop((x - 30, y - 10, x + PW + 10, y + PH + 30)).save(os.path.join(qd, f"f{i + 1}.png"))
