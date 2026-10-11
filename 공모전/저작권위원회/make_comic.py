"""6컷 만화 「출처만 쓰면 괜찮다며?!」 조립: AI 패널(img/P1~P6, 2400x1792) + 직접 쓴 대사·효과음·제목·필수 표기.
대사/글자는 전부 로컬에서 Noto Sans CJK KR(SIL OFL)로 입력 (AI 생성 글자 사용 안 함)."""
import os
from PIL import Image, ImageDraw, ImageFont

os.chdir(os.path.dirname(os.path.abspath(__file__)))
FB, FBD = "C:/Windows/Fonts/NotoSansCJKkr-Black.otf", "C:/Windows/Fonts/NotoSansCJKkr-Bold.otf"
INK, PAPER = (40, 34, 60), (255, 255, 255)
AI_NOTE = "본 작품은 생성형 AI를 활용해 제작되었습니다"

def font(path, size): return ImageFont.truetype(path, size)

def text_block(d, box, text, size, fill=INK, path=FBD, spacing=0.28):
    x0, y0, x1, y1 = box
    f = font(path, size)
    lines = text.split("\n")
    lh = size * (1 + spacing)
    total = lh * len(lines) - size * spacing
    y = (y0 + y1) / 2 - total / 2
    for ln in lines:
        d.text(((x0 + x1) / 2, y + size / 2), ln, font=f, fill=fill, anchor="mm")
        y += lh

def bubble(im, box, text, size, tail=None, fill=PAPER, outline=INK, tcol=INK, path=FBD, r=60):
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = box
    if tail:                                     # tail first, then body covers its base
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        tx, ty = tail
        bx = min(max(tx, x0 + r), x1 - r)
        base = [(bx - 45, cy), (bx + 45, cy)]
        d.polygon([base[0], (tx, ty), base[1]], fill=fill, outline=outline)
        d.line([base[0], (tx, ty), base[1]], fill=outline, width=8, joint="curve")
    d.rounded_rectangle(box, r, fill=fill, outline=outline, width=8)
    if tail:                                     # hide the tail base line inside the body
        d.polygon([(bx - 37, cy), (tx + (bx - tx) * 0.0, cy), (bx + 37, cy)], fill=fill)
        d.rounded_rectangle((x0 + 8, y0 + 8, x1 - 8, y1 - 8), r - 8, fill=fill)
    text_block(d, box, text, size, fill=tcol, path=path)

def top_box(im, text, size=86, y=(40, 250)):
    d = ImageDraw.Draw(im)
    d.rectangle((30, y[0], im.width - 30, y[1]), fill=PAPER, outline=INK, width=8)
    text_block(d, (30, y[0], im.width - 30, y[1]), text, size, path=FB)

P = {n: Image.open(f"img/P{n}.png").convert("RGB") for n in range(1, 7)}

# --- 1컷
im = P[1]; d = ImageDraw.Draw(im)
top_box(im, "복붙이의 블로그 시간 ♪", 108, y=(14, 258))
bubble(im, (90, 320, 1310, 660), "멋진 사진 퍼 오고~\n출처: 인터넷! 이 정도면 됐지?", 78, tail=(640, 800))

# --- 2컷
im = P[2]; d = ImageDraw.Draw(im)
top_box(im, "땡!! 출처 표시는 기본,\n이용 허락·조건이 먼저야!", 94, y=(60, 300))
bubble(im, (860, 840, 1240, 1010), "삐익!!", 84, fill=(255, 225, 60), tcol=(210, 30, 40), path=FB, r=40)   # 영문 효과음을 덮어 한글로
bubble(im, (1900, 330, 2330, 520), "헉?!", 90, tail=(1800, 640), path=FB)

# --- 3컷
im = P[3]
bubble(im, (960, 90, 2340, 600), "그럼 AI한테 시키면 되지!\nAI야, 저 그림이랑\n똑같이 그려 줘!", 92, tail=(1720, 720))   # 복붙이 대사 → 말풍선 하나로(화자 명확)

# --- 4컷
im = P[4]
top_box(im, "그것도 땡! 남의 작품을 똑같이·비슷하게\n따라 하게 시키는 건 피해야 해!", 92, y=(30, 330))
bubble(im, (80, 390, 640, 600), "머쓱…", 90, tail=(740, 700))

# --- 5컷 (상단 박스가 없어 직접 그림)
im = P[5]
top_box(im, "공유마당에서 이용 조건을 확인하고 쓰거나,\n직접 만들어 봐!", 88, y=(15, 290))
bubble(im, (690, 330, 1380, 600), "오호~ 무료여도\n조건 확인!", 76, tail=(720, 820))

# --- 6컷
im = P[6]; d = ImageDraw.Draw(im)
import numpy as np                                                                   # 배경 노트북 덮개의 작은 마크: 주변 덮개 그라데이션(평면 근사)으로 채움
a = np.array(im).astype(float); y0, y1, x0, x1 = 880, 1035, 290, 450
yy, xx = np.mgrid[y0:y1, x0:x1]
inner = (yy >= 905) & (yy < 1010) & (xx >= 318) & (xx < 422)
A = np.c_[xx[~inner], yy[~inner], np.ones((~inner).sum())]
for c in range(3):
    coef, *_ = np.linalg.lstsq(A, a[y0:y1, x0:x1, c][~inner], rcond=None)
    plane = coef[0] * xx + coef[1] * yy + coef[2]
    blk = a[y0:y1, x0:x1, c]; blk[inner] = plane[inner]
im = P[6] = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(im)
top_box(im, "그린카드! 창작자 존중이\nK-저작권 매너야!", 104, y=(36, 410))
bubble(im, (40, 440, 1230, 720), "복붙이 → 창작이 레벨 업!\n직접 그리고, AI 쓴 건 표시!", 70, tail=(820, 770))

# --- 조립 (2000 x 2650)
W, M, G = 2000, 40, 30
pw = (W - 2 * M - G) // 2; ph = round(pw * 1792 / 2400)
HEAD, FOOT = 330, 170
H = HEAD + 3 * ph + 2 * G + FOOT
page = Image.new("RGB", (W, H), (242, 238, 252))
d = ImageDraw.Draw(page)
d.text((W // 2, 135), "출처만 쓰면 괜찮다며?!", font=font(FB, 112), fill=INK, anchor="mm", stroke_width=6, stroke_fill=PAPER)
d.text((W // 2, 250), "복붙이의 K-저작권 매너 대작전 (6컷)", font=font(FBD, 50), fill=(150, 90, 200), anchor="mm")
for i in range(6):
    x = M + (i % 2) * (pw + G); y = HEAD + (i // 2) * (ph + G)
    page.paste(P[i + 1].resize((pw, ph), Image.LANCZOS), (x, y))
    d.rectangle((x, y, x + pw - 1, y + ph - 1), outline=INK, width=4)
    d.ellipse((x + 14, y + ph - 70, x + 70, y + ph - 14), fill=INK)
    d.text((x + 42, y + ph - 42), str(i + 1), font=font(FB, 36), fill=PAPER, anchor="mm")
d.text((M, H - 125), "기획·글: 출품자(Claude 보조)  |  그림: 생성형 AI 이미지 + 편집  |  폰트: Noto Sans CJK KR (SIL OFL)",
       font=font(FBD, 26), fill=(110, 100, 140), anchor="lm")
d.text((W - M, H - 55), AI_NOTE, font=font(FB, 46), fill=INK, anchor="rm")          # 필수 표기: 우측 하단
os.makedirs("out", exist_ok=True)
page.save("out/만화_출처만쓰면괜찮다며.png", optimize=True)
for n, im in P.items(): im.save(f"out/panel_{n}.png")
print(page.size)
