"""글꼴 체계 비교 시안 (출품 파일은 읽기만 함). 결과: proposals/type/*.png
글꼴은 전부 SIL OFL 1.1, fonts/ 폴더(공식 출처에서 받은 원본 + 라이선스 파일)만 사용."""
import math, os, subprocess, tempfile
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.abspath(os.path.join(HERE, "..", "..")))

NOTO_B, NOTO_BD = "C:/Windows/Fonts/NotoSansCJKkr-Black.otf", "C:/Windows/Fonts/NotoSansCJKkr-Bold.otf"
F = {"title": "fonts/BagelFatOne/BagelFatOne-Regular.ttf",       # 제목·컷 번호·엔딩
     "narr": "fonts/DoHyeon/DoHyeon-Regular.ttf",                # 내레이션·부제
     "talk": "fonts/Jua/Jua-Regular.ttf",                        # 대사·자막
     "sfx": "fonts/BlackHanSans/BlackHanSans-Regular.ttf",       # 효과음
     "sb": "fonts/Pretendard/Pretendard-SemiBold.otf",           # 크레딧
     "b": "fonts/Pretendard/Pretendard-Bold.otf",                # 필수 표기(영상)
     "xb": "fonts/Pretendard/Pretendard-ExtraBold.otf"}          # 필수 표기(만화)·대체 글리프
FALLBACK = F["xb"]                                               # · … → 등 디스플레이체에 없는 기호
INK, PAPER, BG, ACC = (40, 34, 60), (255, 255, 255), (242, 238, 252), (150, 90, 200)
RED, YEL, HL, SHADOW = (226, 48, 72), (255, 226, 80), (255, 233, 130), (206, 190, 238)


@lru_cache(None)
def font(path, size): return ImageFont.truetype(path, int(size))

@lru_cache(None)
def _notdef(path): return bytes(font(path, 40).getmask("\U000F0000"))

@lru_cache(None)
def has(path, ch): return ch.isspace() or bytes(font(path, 40).getmask(ch)) != _notdef(path)

def gfont(path, ch, size): return font(path, size) if has(path, ch) else font(FALLBACK, size)

def base_off(path, size):                                         # 한글 시각 중심 → 기준선 거리
    _, t, _, b = font(path, size).getbbox("한글", anchor="ls")
    return -(t + b) / 2


# ---------------------------------------------------------------- 조판기: 자간·대체 글리프·외곽선·그림자·형광펜
def layout(runs, path, size, track=0.0):
    if isinstance(runs, str): runs = [(runs,)]
    out, x = [], 0.0
    for run in runs:
        col = run[1] if len(run) > 1 else None
        hl = run[2] if len(run) > 2 else None
        for ch in run[0]:
            fnt = gfont(path, ch, size); a = fnt.getlength(ch)
            out.append((x, a, ch, fnt, col, hl)); x += a + track * size
    return out, (x - track * size if out else 0)

def line_w(runs, path, size, track=0.0): return layout(runs, path, size, track)[1]

def fit(lines, path, size, maxw, track=0.0):
    while max(line_w(l, path, size, track) for l in lines) > maxw: size -= 1
    return size

def draw_line(d, xc, yc, runs, path, size, track=0.0, fill=INK, strokes=(), shadow=None):
    """strokes: ((굵기, 색), ...) 바깥→안 순서. shadow: (dx, dy, 색, 굵기)"""
    gl, w = layout(runs, path, size, track)
    x0, by = xc - w / 2, yc + base_off(path, size)
    for gx, a, ch, fnt, col, hl in gl:
        if hl: d.rectangle((x0 + gx - 2, by - size * 0.40, x0 + gx + a + 2, by + size * 0.10), fill=hl)
    passes = ([shadow] if shadow else []) + [(0, 0, c, sw) for sw, c in strokes]
    for dx, dy, c, sw in passes:
        for gx, a, ch, fnt, col, hl in gl:
            d.text((x0 + gx + dx, by + dy), ch, font=fnt, fill=c, anchor="ls", stroke_width=sw, stroke_fill=c)
    for gx, a, ch, fnt, col, hl in gl:
        d.text((x0 + gx, by), ch, font=fnt, fill=col or fill, anchor="ls")

def draw_block(d, box, lines, path, size, leading=1.25, **kw):
    x0, y0, x1, y1 = box
    lh = size * leading; yc = (y0 + y1) / 2 - lh * (len(lines) - 1) / 2
    for i, ln in enumerate(lines): draw_line(d, (x0 + x1) / 2, yc + i * lh, ln, path, size, **kw)

def sfx(im, center, spec, path, angle=0.0, fill=RED, strokes=((22, INK), (12, PAPER)), track=-0.04, shadow=None):
    """글자별 크기·높낮이·기울기를 달리한 효과음. spec: [(글자, 크기, dy, 회전)]"""
    big = max(s for _, s, _, _ in spec)
    adv = [gfont(path, ch, s).getlength(ch) for ch, s, _, _ in spec]
    total = sum(adv) + track * big * (len(spec) - 1)
    side = int(total + big * 3); layer = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    passes = ([(strokes[0][0] if strokes else 0, shadow[2], shadow[:2])] if shadow else []) \
        + [(sw, c, (0, 0)) for sw, c in strokes] + [(0, fill, (0, 0))]
    for sw, c, (ox, oy) in passes:
        x = side / 2 - total / 2
        for (ch, s, dy, rot), a in zip(spec, adv):
            g = Image.new("RGBA", (int(s * 2.6), int(s * 2.6)), (0, 0, 0, 0)); gc = g.width / 2
            ImageDraw.Draw(g).text((gc, gc), ch, font=gfont(path, ch, s), fill=c, anchor="mm", stroke_width=sw, stroke_fill=c)
            g = g.rotate(rot, resample=Image.BICUBIC)
            layer.alpha_composite(g, (int(x + a / 2 - gc + ox), int(side / 2 + dy - gc + oy)))
            x += a + track * big
    layer = layer.rotate(angle, resample=Image.BICUBIC)
    im.paste(layer, (int(center[0] - side / 2), int(center[1] - side / 2)), layer)

def star(c, rin, rout, n, rot=0.0, jitter=()):
    pts = []
    for i in range(2 * n):
        t = rot + math.pi * i / n; r = rout if i % 2 == 0 else rin
        j = jitter[i % len(jitter)] if jitter else 1.0
        pts.append((c[0] + r[0] * j * math.cos(t), c[1] + r[1] * j * math.sin(t)))
    return pts


# ---------------------------------------------------------------- 현재 방식 (make_comic.py 그대로)
def cur_block(d, box, text, size, fill=INK, path=NOTO_BD, spacing=0.28):
    x0, y0, x1, y1 = box; f = font(path, size); lines = text.split("\n")
    lh = size * (1 + spacing); y = (y0 + y1) / 2 - (lh * len(lines) - size * spacing) / 2
    for ln in lines: d.text(((x0 + x1) / 2, y + size / 2), ln, font=f, fill=fill, anchor="mm"); y += lh

def bubble_shape(d, box, tail=None, fill=PAPER, outline=INK, r=60):
    x0, y0, x1, y1 = box
    if tail:
        cy = (y0 + y1) / 2; tx, ty = tail; bx = min(max(tx, x0 + r), x1 - r)
        d.polygon([(bx - 45, cy), (tx, ty), (bx + 45, cy)], fill=fill, outline=outline)
        d.line([(bx - 45, cy), (tx, ty), (bx + 45, cy)], fill=outline, width=8, joint="curve")
    d.rounded_rectangle(box, r, fill=fill, outline=outline, width=8)
    if tail:
        d.polygon([(bx - 37, cy), (tx, cy), (bx + 37, cy)], fill=fill)
        d.rounded_rectangle((x0 + 8, y0 + 8, x1 - 8, y1 - 8), r - 8, fill=fill)

def cur_panel2():
    im = Image.open("img/P2.png").convert("RGB"); d = ImageDraw.Draw(im)
    d.rectangle((30, 60, im.width - 30, 300), fill=PAPER, outline=INK, width=8)
    cur_block(d, (30, 60, im.width - 30, 300), "땡!! 출처 표시는 기본,\n이용 허락·조건이 먼저야!", 94, path=NOTO_B)
    bubble_shape(d, (860, 840, 1240, 1010), fill=(255, 225, 60), r=40)
    cur_block(d, (860, 840, 1240, 1010), "삐익!!", 84, fill=(210, 30, 40), path=NOTO_B)
    bubble_shape(d, (1900, 330, 2330, 520), tail=(1800, 640))
    cur_block(d, (1900, 330, 2330, 520), "헉?!", 90, path=NOTO_B)
    return im


# ---------------------------------------------------------------- 제안 방식
def sfx_whistle(im):                                              # '삐익!!' — 영문 FWEET! 를 덮는 폭발 풍선 + 검은고딕
    d = ImageDraw.Draw(im)
    d.polygon(star((1056, 912), (172, 104), (232, 150), 13, rot=0.12, jitter=(1, .93, 1.06, .97, .9, 1.04)),
              fill=YEL, outline=INK, width=8)
    sfx(im, (1056, 908), [("삐", 122, 6, 4), ("익", 140, -4, -3), ("!", 140, -6, -9), ("!", 140, -10, -15)],
        F["sfx"], angle=7, fill=RED, strokes=((20, INK), (11, PAPER)), track=-0.05)

def prop_panel2():
    im = Image.open("img/P2.png").convert("RGB"); d = ImageDraw.Draw(im)
    box = (30, 60, im.width - 30, 300)                            # 내레이션: 도현체, 핵심어 형광펜, 감탄사 빨강
    d.rectangle(box, fill=PAPER, outline=INK, width=8)
    draw_block(d, box, [[("땡!!", RED), (" 출처 표시는 기본,",)],
                        [("이용 ",), ("허락·조건", None, HL), ("이 먼저야!",)]], F["narr"], 100, leading=1.12)
    sfx_whistle(im)
    c, tail = (2112, 445), (1800, 650)                             # '헉?!' — 놀람(가시) 풍선 + 주아체 떨림 조판
    d.polygon([(1975, 410), tail, (2005, 500)], fill=PAPER, outline=INK)
    d.line([(1975, 410), tail, (2005, 500)], fill=INK, width=8, joint="curve")
    d.polygon(star(c, (198, 104), (232, 132), 21, rot=0.05), fill=PAPER, outline=INK, width=8)
    sfx(im, (c[0] + 4, c[1] + 4), [("헉", 140, 0, 6), ("?", 126, -6, -6), ("!", 126, -12, -12)],
        F["talk"], angle=0, fill=INK, strokes=(), track=-0.02)
    return im


# ---------------------------------------------------------------- 숏폼 13초 프레임
W, H, PY, PH = 1080, 1920, 330, 810
AI_NOTE = "본 작품은 생성형 AI를 활용해 제작되었습니다"

def ease(x): x = max(0.0, min(1.0, x)); return 0.5 - 0.5 * math.cos(math.pi * x)

def cur_frame13():
    tmp = os.path.join(tempfile.gettempdir(), "_cur13.png")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "13.0", "-i", "최종제출/숏폼부문_퍼가요말고허락부터.mp4",
                    "-frames:v", "1", tmp], check=True)
    return Image.open(tmp).convert("RGB")

def prop_frame13():
    art = Image.open("img/P2.png").convert("RGB"); sfx_whistle(art)
    st, en, c0, c1 = 12.60, 16.10, (120, 340, 1500, 1375), (250, 400, 1250, 1150)   # make_short.py SC[4]
    k = ease((13.0 - st) / (en - st)); box = tuple(round(c0[i] + (c1[i] - c0[i]) * k) for i in range(4))
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    t = "퍼가요 말고 허락부터"                                         # 제목: Bagel Fat One 스티커(흰 외곽선 + 보라 그림자)
    s = fit([t], F["title"], 92, W - 110)
    draw_line(d, W / 2, 148, t, F["title"], s, strokes=((10, PAPER),), shadow=(0, 8, SHADOW, 10))
    sub = "K-저작권 매너송"; sw = line_w(sub, F["narr"], 46)             # 부제: 도현체 알약 배지
    d.rounded_rectangle((W / 2 - sw / 2 - 30, 252 - 36, W / 2 + sw / 2 + 30, 252 + 36), 36, fill=ACC)
    draw_line(d, W / 2, 252, sub, F["narr"], 46, fill=PAPER)
    d.rectangle((0, PY - 6, W, PY + PH + 6), fill=INK)
    im.paste(art.crop(box).resize((W, PH), Image.BILINEAR), (0, PY))
    draw_line(d, W / 2, PY + PH + 50, AI_NOTE, F["b"], 34, track=-0.01)  # 필수 표기: Pretendard Bold
    lines = [[("출처만 쓰면 괜찮다?",)], [("아니죠, ",), ("허락", RED), ("이 먼저",)]]   # 자막: 주아체 + 두꺼운 외곽선
    s = fit(lines, F["talk"], 92, W - 100, -0.02)
    draw_block(d, (0, 1400, W, 1400), lines, F["talk"], s, leading=1.28, track=-0.02,
               strokes=((12, PAPER),), shadow=(0, 7, SHADOW, 12))
    nxt = "무료로 쓰고 싶다면 공유마당 이용 조건 확인!"                       # 다음 줄 미리보기: 같은 서체, 작게·연하게
    draw_line(d, W / 2, 1592, nxt, F["talk"], fit([nxt], F["talk"], 44, W - 100, -0.02), track=-0.02, fill=(128, 118, 160))
    return im


# ---------------------------------------------------------------- 비교판
def labels(d, x, y, w, head, sub, accent):
    d.rounded_rectangle((x, y, x + w, y + 96), 18, fill=accent)
    d.text((x + 28, y + 30), head, font=font(F["xb"], 38), fill=PAPER, anchor="lm")
    d.text((x + 28, y + 72), sub, font=font(F["sb"], 25), fill=PAPER, anchor="lm")

def comic_compare():
    a, b = cur_panel2(), prop_panel2()
    PW, M = 1400, 40; ph = round(PW * a.height / a.width)
    tb = (30, 40, 2370, 320); tbh = round(PW * (tb[3] - tb[1]) / (tb[2] - tb[0]))
    s1, s2 = (790, 740, 1310, 1090), (1660, 250, 2400, 700); ch = 440
    cw1 = round(ch * (s1[2] - s1[0]) / (s1[3] - s1[1])); cw2 = PW - cw1 - 20
    Wc = 2 * PW + 3 * M; Hc = 210 + ph + 30 + tbh + 30 + ch + 60
    pg = Image.new("RGB", (Wc, Hc), BG); d = ImageDraw.Draw(pg)
    d.text((M, 50), "2컷 식자 비교 — 대사(내레이션) 박스 · 효과음 '삐익!!' · 대사 '헉?!'", font=font(F["xb"], 40), fill=INK, anchor="lm")
    for i, (im, head, sub, acc) in enumerate([
            (a, "현재", "Noto Sans CJK KR Black 단일 (내레이션·효과음·대사 모두 같은 서체)", (120, 112, 140)),
            (b, "제안", "내레이션 Do Hyeon · 효과음 Black Han Sans · 대사 Jua  (모두 SIL OFL 1.1)", ACC)]):
        x = M + i * (PW + M); y = 90
        labels(d, x, y, PW, head, sub, acc); y += 120
        pg.paste(im.resize((PW, ph), Image.LANCZOS), (x, y)); y += ph + 30
        pg.paste(im.crop(tb).resize((PW, tbh), Image.LANCZOS), (x, y)); y += tbh + 30
        pg.paste(im.crop(s1).resize((cw1, ch), Image.LANCZOS), (x, y))
        c2 = im.crop(s2); c2 = c2.resize((cw2, round(cw2 * c2.height / c2.width)), Image.LANCZOS)
        pg.paste(c2.crop((0, 0, cw2, min(ch, c2.height))), (x + cw1 + 20, y))
        for r in [(x, 210, x + PW, 210 + ph), (x, 240 + ph, x + PW, 240 + ph + tbh)]: d.rectangle(r, outline=INK, width=3)
    d.text((M, Hc - 30), "아래 두 줄은 같은 위치 확대(내레이션 박스 / 효과음·놀람 풍선). 패널 원본 2400×1792 기준 조판 후 축소.",
           font=font(F["sb"], 24), fill=(110, 100, 140), anchor="lm")
    pg.save(os.path.join(HERE, "compare_comic_P2.png"), optimize=True)

def short_compare():
    a, b = cur_frame13(), prop_frame13()
    M = 40; Wc = 2 * W + 3 * M; Hc = 210 + H + 40
    pg = Image.new("RGB", (Wc, Hc), (226, 220, 240)); d = ImageDraw.Draw(pg)
    d.text((M, 50), "숏폼 13.0초 프레임 비교 (1080×1920)", font=font(F["xb"], 40), fill=INK, anchor="lm")
    for i, (im, head, sub, acc) in enumerate([
            (a, "현재 (제출 영상에서 추출)", "Noto Sans CJK KR Black/Bold 단일", (120, 112, 140)),
            (b, "제안", "제목 Bagel Fat One · 부제 Do Hyeon · 자막 Jua · 표기 Pretendard", ACC)]):
        x = M + i * (W + M)
        labels(d, x, 90, W, head, sub, acc); pg.paste(im, (x, 210)); d.rectangle((x, 210, x + W, 210 + H), outline=INK, width=3)
    pg.save(os.path.join(HERE, "compare_short_13s.png"), optimize=True)
    b.save(os.path.join(HERE, "proposal_short_13s.png"))

def type_sheet():
    Ws, rows = 2000, 8; RH = 230; pg = Image.new("RGB", (Ws, 180 + rows * RH + 60), BG); d = ImageDraw.Draw(pg)
    d.text((60, 70), "글꼴 체계 시트 — 「출처만 쓰면 괜찮다며?!」 · 「퍼가요 말고 허락부터」", font=font(F["xb"], 44), fill=INK, anchor="lm")
    d.text((60, 125), "전 글꼴 SIL OFL 1.1 · 공식 출처(google/fonts ofl, orioncactus/pretendard) 원본 + 라이선스 파일 동봉",
           font=font(F["sb"], 26), fill=(110, 100, 140), anchor="lm")
    R = [("제목", "Bagel Fat One · 자간 0 · 흰 외곽선 + 보라 그림자 · 90px 이상만"),
         ("부제", "Do Hyeon · 자간 0 · 보라 / 알약 배지"),
         ("내레이션", "Do Hyeon · 행간 112% · 감탄사 빨강·핵심어 형광펜"),
         ("대사", "Jua · 자간 -2% · 행간 125% · 외곽선 없음"),
         ("효과음", "Black Han Sans · 자간 -5% · 이중 외곽선 · 글자별 크기/기울기"),
         ("자막", "Jua · 현재 줄 92px + 흰 외곽선 12 / 다음 줄 44px 연보라"),
         ("컷 번호", "Bagel Fat One · 먹색 원 안 흰 숫자"),
         ("표기·크레딧", "Pretendard ExtraBold(표기) / SemiBold(크레딧) · 자간 -1%")]
    for i, (role, spec) in enumerate(R):
        y = 180 + i * RH; yc = y + RH / 2
        d.rounded_rectangle((40, y + 14, Ws - 40, y + RH - 14), 24, fill=PAPER)
        d.text((80, yc - 26), role, font=font(F["xb"], 40), fill=ACC, anchor="lm")
        d.text((80, yc + 30), spec, font=font(F["sb"], 22), fill=(110, 100, 140), anchor="lm")
        cx = 1330
        if i == 0: draw_line(d, cx, yc, "출처만 쓰면 괜찮다며?!", F["title"], 96, strokes=((9, PAPER),), shadow=(0, 7, SHADOW, 9))
        if i == 1: draw_line(d, cx, yc, "복붙이의 K-저작권 매너 대작전 (6컷)", F["narr"], 60, fill=ACC)
        if i == 2:
            d.rectangle((cx - 560, yc - 70, cx + 560, yc + 70), fill=PAPER, outline=INK, width=5)
            draw_block(d, (cx - 560, yc - 70, cx + 560, yc + 70), [[("그것도 땡!", RED), (" 남의 작품을 똑같이·비슷하게",)],
                       [("따라 하게 시키는 건 ",), ("피해야 해!", None, HL)]], F["narr"], 52, leading=1.12)
        if i == 3:
            bubble_shape(d, (cx - 420, yc - 80, cx + 420, yc + 80), r=50)
            draw_block(d, (cx - 420, yc - 80, cx + 420, yc + 80), ["멋진 사진 퍼 오고~", "출처: 인터넷! 이 정도면 됐지?"],
                       F["talk"], 54, leading=1.25, track=-0.02)
        if i == 4:
            sfx(pg, (cx - 200, yc), [("삐", 100, 6, 4), ("익", 116, -4, -3), ("!", 116, -6, -9), ("!", 116, -10, -15)],
                F["sfx"], angle=7, strokes=((16, INK), (9, PAPER)), track=-0.05)
            sfx(pg, (cx + 260, yc), [("짝", 100, 4, 8), ("짝", 110, -6, -6), ("!", 110, -4, -12)],
                F["sfx"], angle=-5, fill=(255, 170, 40), strokes=((16, INK), (9, PAPER)), track=-0.05)
        if i == 5:
            draw_line(d, cx, yc - 30, [("퍼가요 말고 ",), ("허락", RED), ("부터!",)], F["talk"], 80, track=-0.02,
                      strokes=((11, PAPER),), shadow=(0, 6, SHADOW, 11))
            draw_line(d, cx, yc + 62, "쓸 때는 출처까지! (출처까지!)", F["talk"], 38, track=-0.02, fill=(128, 118, 160))
        if i == 6:
            for n in range(6):
                x = cx - 375 + n * 150; d.ellipse((x - 46, yc - 46, x + 46, yc + 46), fill=INK)
                draw_line(d, x, yc, str(n + 1), F["title"], 54, fill=PAPER)
        if i == 7:
            draw_line(d, cx, yc - 30, AI_NOTE, F["xb"], 48, track=-0.01)
            draw_line(d, cx, yc + 42, "글꼴: Bagel Fat One · Do Hyeon · Jua · Black Han Sans · Pretendard (SIL OFL 1.1)",
                      F["sb"], 25, track=-0.01, fill=(110, 100, 140))
    pg.save(os.path.join(HERE, "type_system_sheet.png"), optimize=True)


if __name__ == "__main__":
    comic_compare(); short_compare(); type_sheet()
    print("ok", sorted(f for f in os.listdir(HERE) if f.endswith(".png")))
