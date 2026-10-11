"""숏폼 「퍼가요 말고 허락부터」 1080x1920 30fps: 6컷 패널(무료 생성 이미지)을 가사에 맞춰 줌/팬(켄번스) + 가사 자막
+ 필수 표기(하단 상시). 영상 생성 크레딧 0. usage: python make_short.py [--still t1 t2 ...]"""
import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

os.chdir(os.path.dirname(os.path.abspath(__file__)))
W, H, FPS = 1080, 1920, 30
FB, FBD = "C:/Windows/Fonts/NotoSansCJKkr-Black.otf", "C:/Windows/Fonts/NotoSansCJKkr-Bold.otf"
INK, BG, ACC = (40, 34, 60), (242, 238, 252), (150, 90, 200)
AUDIO = "audio/S1.wav"
AI_NOTE = "본 작품은 생성형 AI를 활용해 제작되었습니다"
DUR = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", AUDIO],
                           capture_output=True, text=True).stdout)
TOTAL = DUR + 1.5

def f(p, s): return ImageFont.truetype(p, s)

# ---------------------------------------------------------------- clean art (no comic text) + fixes
art = {n: Image.open(f"img/P{n}.png").convert("RGB") for n in range(1, 7)}
art["cs"] = Image.open("img/charsheet.png").convert("RGB")
d = ImageDraw.Draw(art[1])                                                             # 1컷 화면 라벨
d.rounded_rectangle((1462, 1274, 1640, 1326), 8, fill=(255, 236, 170))
d.text((1551, 1300), "출처: 인터넷", font=f(FBD, 30), fill=INK, anchor="mm")
d = ImageDraw.Draw(art[2])                                                             # 2컷 영문 효과음 → 한글
d.rounded_rectangle((860, 840, 1240, 1010), 40, fill=(255, 225, 60), outline=INK, width=8)
d.text((1050, 925), "삐익!!", font=f(FB, 84), fill=(210, 30, 40), anchor="mm")
a = np.array(art[6]).astype(float); y0, y1, x0, x1 = 880, 1035, 290, 450                # 6컷 배경 노트북 마크 제거
yy, xx = np.mgrid[y0:y1, x0:x1]; inner = (yy >= 905) & (yy < 1010) & (xx >= 318) & (xx < 422)
A = np.c_[xx[~inner], yy[~inner], np.ones((~inner).sum())]
for c in range(3):
    coef, *_ = np.linalg.lstsq(A, a[y0:y1, x0:x1, c][~inner], rcond=None)
    blk = a[y0:y1, x0:x1, c]; blk[inner] = (coef[0] * xx + coef[1] * yy + coef[2])[inner]
art[6] = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

# scenes: (start, key, crop_from, crop_to)  — crops are 4:3 rects in source pixels
SC = [
    # 시각은 기술 검수(보컬 에너지·재인식·마찰음 3중 확인) 실측값으로 맞춤 / 크롭은 AI 테두리·반쯤 걸린 얼굴 제외
    (0.00, 1, (200, 265, 2140, 1720), (300, 600, 1500, 1500)),        # 퍼가요~
    (1.90, 2, (300, 320, 2120, 1685), (150, 350, 1350, 1250)),        # 잠깐만! (호루라기)
    (4.60, 1, (1050, 800, 2030, 1535), (1150, 900, 1850, 1425)),      # 사진 한 장 → 출처: 인터넷 라벨
    (8.75, 5, (60, 280, 2076, 1792), (0, 650, 1200, 1550)),          # 누가 만든 건지 봐요 (돋보기) — 상단 흰 띠 제외
    (12.60, 2, (120, 340, 1500, 1375), (250, 400, 1250, 1150)),       # 출처만 쓰면? 아니죠 (레드카드)
    (16.10, 5, (850, 400, 2350, 1525), (1000, 500, 2300, 1475)),      # 공유마당 이용 조건 확인
    (19.95, 4, (320, 350, 2160, 1730), (1190, 450, 2330, 1305)),      # 퍼가요 말고 허락부터! — 우측 테두리 제외
    (24.10, 6, (330, 460, 2070, 1765), (600, 900, 1500, 1575)),       # 쓸 때는 출처까지 (스케치북)
    (27.65, 3, (150, 80, 2330, 1715), (300, 250, 2200, 1675)),        # AI한테 시킬 때도 (새 3컷: 액자 가리킴)
    (31.20, 4, (750, 700, 1850, 1525), (950, 880, 1650, 1405)),       # NO! (로봇 X)
    (32.50, 6, (700, 600, 2100, 1650), (330, 460, 2070, 1765)),       # 창작자에게 박수
    (36.05, "cs", (780, 300, 2060, 1260), (750, 240, 2070, 1230)),      # 오늘부터 우리 모두
]
LINES = [(0.25, "퍼가요~♡"), (2.90, "…잠깐만!"), (4.60, "마음에 쏙 든 사진 한 장,\n노래 한 소절"),
         (8.75, "복붙 전에 잠깐 멈춰,\n누가 만든 건지 봐요"), (12.60, "출처만 쓰면 괜찮다?\n아니죠, 허락이 먼저"),
         (16.10, "무료로 쓰고 싶다면\n공유마당 이용 조건 확인!"), (19.95, "퍼가요 말고 허락부터!\n(허락부터!)"),
         (24.10, "쓸 때는 출처까지!\n(출처까지!)"), (27.65, "AI한테 시킬 때도\n남의 작품 그대로는 NO!"),
         (32.50, "창작자에게 박수 짝짝,\nK-저작권 매너!"), (36.05, "오늘부터 우리 모두\n저작권 매너인!")]
VOC_END = 39.5
PX, PY, PW, PH = 0, 330, 1080, 810            # picture window

def ease(x): x = max(0.0, min(1.0, x)); return 0.5 - 0.5 * math.cos(math.pi * x)
def lerp(a, b, k): return tuple(a[i] + (b[i] - a[i]) * k for i in range(4))

def scene_img(i, t):
    st, key, c0, c1 = SC[i]
    en = SC[i + 1][0] if i + 1 < len(SC) else TOTAL
    k = ease((t - st) / max(0.1, en - st))
    box = lerp(c0, c1, k)
    return art[key].crop(tuple(round(v) for v in box)).resize((PW, PH), Image.BILINEAR)

base = Image.new("RGB", (W, H), BG)
bd = ImageDraw.Draw(base)
bd.text((W // 2, 150), "퍼가요 말고 허락부터", font=f(FB, 84), fill=INK, anchor="mm", stroke_width=5, stroke_fill=(255, 255, 255))
bd.text((W // 2, 252), "K-저작권 매너송", font=f(FBD, 44), fill=ACC, anchor="mm")
bd.rectangle((PX, PY - 6, PX + PW, PY + PH + 6), fill=INK)
bd.text((W // 2, PY + PH + 50), AI_NOTE, font=f(FBD, 34), fill=INK, anchor="mm")   # 필수 표기: 그림 바로 아래 상시(쇼츠 하단 UI 밖)

def caption(d, text, y, size, fill):
    fnt = f(FB, size)
    while max(fnt.getlength(s) for s in text.split("\n")) > W - 100: fnt = fnt.font_variant(size=fnt.size - 2)
    d.multiline_text((W // 2, y), text, font=fnt, fill=fill, anchor="mm", align="center", spacing=int(fnt.size * 0.3),
                     stroke_width=4, stroke_fill=(255, 255, 255))

def frame(t):
    im = base.copy()
    i = max(j for j, s in enumerate(SC) if s[0] <= t)
    pic = scene_img(i, t)
    if i > 0 and t - SC[i][0] < 0.22:                                                  # 짧은 크로스페이드
        pic = Image.blend(scene_img(i - 1, t), pic, ease((t - SC[i][0]) / 0.22))
    im.paste(pic, (PX, PY))
    d = ImageDraw.Draw(im)
    if t < DUR:
        cur = max([j for j, l in enumerate(LINES) if l[0] <= t] or [-1])
        if cur >= 0:
            k = ease((t - LINES[cur][0]) / 0.2)
            col = tuple(int(255 + (c - 255) * k) for c in INK)
            caption(d, LINES[cur][1], 1400, 74, col)
        if cur + 1 < len(LINES):
            caption(d, LINES[cur + 1][1].replace("\n", " "), 1580, 40, (95, 86, 125))
    else:                                                                              # 엔딩 카드
        k = ease((t - DUR) / 0.5)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.rectangle((0, PY + PH + 90, W, H - 130), fill=(*BG, int(255 * k)))
        ld.text((W // 2, 1420), "허락부터, 출처까지", font=f(FB, 80), fill=(*INK, int(255 * k)), anchor="mm")
        ld.text((W // 2, 1540), "오늘부터 K-저작권 매너!", font=f(FB, 64), fill=(*ACC, int(255 * k)), anchor="mm")
        im.paste(lay, (0, 0), lay)
    if t < 5.0:                                                                        # 초반 상단 표기 5초(쇼츠 하단 UI 가림 대비)
        k = 1 - ease((t - 4.5) / 0.5)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle((90, PY + 24, W - 90, PY + 96), 20, fill=(40, 34, 60, int(215 * k)))
        ld.text((W // 2, PY + 60), AI_NOTE, font=f(FBD, 34), fill=(255, 255, 255, int(255 * k)), anchor="mm")
        im.paste(lay, (0, 0), lay)
    if t > TOTAL - 0.6: im = Image.blend(im, Image.new("RGB", (W, H), BG), ease((t - (TOTAL - 0.6)) / 0.6))
    return im

if __name__ == "__main__":
    os.makedirs("out", exist_ok=True)
    if "--still" in sys.argv:
        for t in [float(x) for x in sys.argv[sys.argv.index("--still") + 1:]]:
            frame(t).save(f"out/s_{t:05.2f}.png")
        sys.exit()
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                            "-i", "-", "-i", AUDIO, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
                            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
                            "-af", f"volume=2.5dB,apad=pad_dur={TOTAL - DUR + 0.1:.2f},afade=t=out:st={DUR - 0.51:.2f}:d=0.45",
                            "-t", f"{TOTAL:.3f}", "-movflags", "+faststart", "out/숏폼_퍼가요말고허락부터.mp4"], stdin=subprocess.PIPE)
    for n in range(round(TOTAL * FPS)):
        enc.stdin.write(frame(n / FPS).tobytes())
    enc.stdin.close(); enc.wait()
    print("done", round(TOTAL, 2))
