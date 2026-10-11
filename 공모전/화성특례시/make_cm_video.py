"""Album-art style video for a CM song (1920x1080, 30 fps): square album art (left) + synced lyrics,
song info, progress bar and the official Hwaseong slogan BI (right). Everything is drawn locally.
usage: python make_cm_video.py A|B"""
import json, math, os, random, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

os.chdir(os.path.dirname(os.path.abspath(__file__)))
SONG = sys.argv[1]
W, H, FPS = 1920, 1080, 30
FB, FBD, FM = ("C:/Windows/Fonts/NotoSansCJKkr-Black.otf", "C:/Windows/Fonts/NotoSansCJKkr-Bold.otf",
               "C:/Windows/Fonts/NotoSansCJKkr-Medium.otf")
HS_BLUE, HS_ORANGE = (0, 70, 150), (220, 110, 45)

def cutout(path, tol=28):
    """white-background illustration -> RGBA (flood fill from the border, keeps inner whites)"""
    im = Image.open(path).convert("RGB")
    a = np.array(im).astype(int)
    white = (a.min(axis=2) > 255 - tol)
    h, w = white.shape
    mask = np.zeros_like(white)
    stack = [(0, x) for x in range(w)] + [(h - 1, x) for x in range(w)] + [(y, 0) for y in range(h)] + [(y, w - 1) for y in range(h)]
    while stack:
        y, x = stack.pop()
        if mask[y, x] or not white[y, x]: continue
        mask[y, x] = True
        if y > 0: stack.append((y - 1, x))
        if y < h - 1: stack.append((y + 1, x))
        if x > 0: stack.append((y, x - 1))
        if x < w - 1: stack.append((y, x + 1))
    alpha = Image.fromarray(np.where(mask, 0, 255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1))
    out = im.convert("RGBA"); out.putalpha(alpha)
    return out.crop(out.getbbox())

def fit(im, box_w, box_h):
    s = min(box_w / im.width, box_h / im.height)
    return im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)

def text_c(d, xy, s, font, fill, stroke=None, sw=0):
    d.text(xy, s, font=font, fill=fill, anchor="mm", stroke_width=sw, stroke_fill=stroke)

def radial(size, c_in, c_out, cx=0.5, cy=0.5, r=0.75):
    yy, xx = np.mgrid[0:size[1], 0:size[0]]
    d = np.clip(np.sqrt(((xx / size[0] - cx) / r) ** 2 + ((yy / size[1] - cy) / r) ** 2), 0, 1)[..., None]
    return Image.fromarray((np.array(c_in) * (1 - d) + np.array(c_out) * d).astype(np.uint8))

def slogan_card(width):
    bi = Image.open("refs/BI/slogan_01.png").convert("RGBA"); bi = bi.crop(bi.getbbox())   # official file, unmodified (scaled only)
    bi = fit(bi, width - 60, 10_000)
    card = Image.new("RGBA", (bi.width + 60, bi.height + 44), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((0, 0, card.width - 1, card.height - 1), 26, fill=(255, 255, 255, 250))
    card.alpha_composite(bi, (30, 22))
    return card

# ---------------------------------------------------------------- album art (2000 x 2000)
S = 2000
random.seed(7)
if SONG == "A":
    TITLE, SUB = "지구에도 화성이 있다", "레트로 스페이스 디스코"
    AUDIO = "audio/A1.mp3"
    art = radial((S, S), (52, 30, 96), (6, 8, 30), 0.35, 0.3, 1.1).convert("RGBA")
    d = ImageDraw.Draw(art)
    for _ in range(420):                                     # stars
        x, y, r = random.randrange(S), random.randrange(S), random.choice([1, 1, 2, 2, 3, 4])
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, random.randint(120, 255)))
    # Mars (no rings - Mars has none) with craters, glow and its two small moons Phobos & Deimos
    pr, px, py = 470, 1440, 930
    glow = Image.new("RGBA", (S, S), (0, 0, 0, 0)); ImageDraw.Draw(glow).ellipse((px - pr - 90, py - pr - 90, px + pr + 90, py + pr + 90), fill=(255, 120, 60, 120))
    art.alpha_composite(glow.filter(ImageFilter.GaussianBlur(60)))
    planet = radial((2 * pr, 2 * pr), (245, 140, 70), (150, 50, 30), 0.35, 0.3, 0.9).convert("RGBA")
    pd = ImageDraw.Draw(planet)
    for cx, cy, cr in [(270, 340, 64), (560, 240, 40), (490, 580, 86), (220, 650, 36), (700, 470, 50), (380, 470, 28)]:
        pd.ellipse((cx - cr, cy - cr, cx + cr, cy + cr), fill=(170, 70, 40, 160))
        pd.ellipse((cx - cr + 8, cy - cr + 6, cx + cr - 2, cy + cr - 6), fill=(200, 95, 55, 120))
    pm = Image.new("L", planet.size, 0); ImageDraw.Draw(pm).ellipse((0, 0, 2 * pr - 1, 2 * pr - 1), fill=255)
    art.paste(planet, (px - pr, py - pr), pm)
    for mx, my, mr in [(860, 560, 42), (1890, 470, 28)]:
        moon = radial((2 * mr, 2 * mr), (190, 175, 160), (95, 85, 80), 0.35, 0.3, 0.9)
        mm = Image.new("L", moon.size, 0); ImageDraw.Draw(mm).ellipse((0, 0, 2 * mr - 1, 2 * mr - 1), fill=255)
        art.paste(moon, (mx - mr, my - mr), mm)
    # Korio singing
    k = fit(cutout("refs/korio/084_sing.jpg"), 860, 980)
    art.alpha_composite(k, (70, S - k.height - 60))
    title_y, title_col, title_stroke = 230, (255, 225, 90), (40, 20, 80)
else:
    TITLE, SUB = "알콩달콩 화성", "코리요의 동요팝"
    AUDIO = "audio/B1.mp3"
    sky = np.zeros((S, S, 3))
    for y in range(S):
        t = y / S
        top, mid, bot = np.array([255, 196, 140]), np.array([255, 150, 120]), np.array([80, 150, 210])
        sky[y] = top * (1 - t / 0.55) + mid * (t / 0.55) if t < 0.55 else mid * (1 - (t - 0.55) / 0.45) + bot * ((t - 0.55) / 0.45)
    art = Image.fromarray(sky.astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(art)
    d.ellipse((1150, 700, 1550, 1100), fill=(255, 235, 170, 255))                     # sunset (궁평항 노을)
    d.rectangle((0, 1000, S, S), fill=(64, 140, 200, 255))                            # sea
    for k_ in range(14):
        y = 1030 + k_ * 34; d.line((1180 - k_ * 6, y, 1520 + k_ * 6, y), fill=(255, 220, 160, 200 - k_ * 10), width=8)
    d.polygon([(0, 1480), (700, 1240), (1200, 1420), (S, 1300), (S, S), (0, S)], fill=(242, 214, 160, 255))   # sea road (제부도 바닷길)
    for x, y in [(200, 260), (520, 180), (1700, 300), (1820, 160)]:
        d.ellipse((x - 120, y - 40, x + 120, y + 40), fill=(255, 255, 255, 200)); d.ellipse((x - 60, y - 80, x + 80, y + 20), fill=(255, 255, 255, 200))
    egg = fit(cutout("refs/korio/254_egg.jpg"), 760, 900); art.alpha_composite(egg, (120, S - egg.height - 330))
    ak = fit(cutout("refs/korio/267_alkong.jpg"), 780, 780); art.alpha_composite(ak, (S - ak.width - 110, S - ak.height - 340))
    title_y, title_col, title_stroke = 330, (255, 255, 255), (220, 90, 40)

dd = ImageDraw.Draw(art)
text_c(dd, (S // 2, title_y), TITLE, ImageFont.truetype(FB, 200 if len(TITLE) > 7 else 230), title_col, title_stroke, 16)
card = slogan_card(640); art.alpha_composite(card, (S - card.width - 70, S - card.height - 70))
art.convert("RGB").save(f"out/albumart_{SONG}.png")

# ---------------------------------------------------------------- lyrics + timing
LY = json.load(open(f"lyrics_{SONG}.json", encoding="utf-8"))
LINES, BPM, BEAT0, VOC_END = LY["lines"], LY["bpm"], LY["beat0"], LY["vocal_end"]
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", AUDIO],
                           capture_output=True, text=True).stdout)
TOTAL = dur + LY.get("tail", 0.5)
CREDITS = ["음원 : Suno AI(Pro, 상업적 이용권)로 생성 · 작사·기획 : 출품자",
           "캐릭터 : 화성특례시 '코리요' (공공누리 1유형)",
           "로고 : 화성특례시 BI · 슬로건 (공공누리 4유형, 출처 화성특례시)",
           "폰트 : Noto Sans CJK KR (SIL OFL)"]

# ---------------------------------------------------------------- static layers
bg = radial((W, H), (46, 30, 88), (8, 8, 26), 0.25, 0.2, 1.2) if SONG == "A" else radial((W, H), (120, 70, 80), (24, 34, 66), 0.25, 0.2, 1.2)
bd = ImageDraw.Draw(bg); random.seed(3)
for _ in range(160):
    x, y, r = random.randrange(W), random.randrange(H), random.choice([1, 1, 2])
    bd.ellipse((x - r, y - r, x + r, y + r), fill=(200, 200, 230) if SONG == "A" else (255, 220, 200))
AW = 860
art_s = art.convert("RGB").resize((AW, AW), Image.LANCZOS)
amask = Image.new("L", (AW, AW), 0); ImageDraw.Draw(amask).rounded_rectangle((0, 0, AW - 1, AW - 1), 34, fill=255)
shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(shadow).rounded_rectangle((110 + 18, 110 + 26, 110 + AW + 18, 110 + AW + 26), 40, fill=(0, 0, 0, 150))
bg = Image.alpha_composite(bg.convert("RGBA"), shadow.filter(ImageFilter.GaussianBlur(24))).convert("RGB")
small_card = slogan_card(420)
F_T, F_S, F_L, F_N, F_C, F_TIME = (ImageFont.truetype(FB, 64), ImageFont.truetype(FBD, 30), ImageFont.truetype(FB, 54),
                                   ImageFont.truetype(FBD, 36), ImageFont.truetype(FM, 25), ImageFont.truetype(FBD, 24))
RX = 1040                      # right panel left edge
RC = (RX + W - 80) // 2        # right panel centre

def ease(x): return 0.5 - 0.5 * math.cos(math.pi * max(0.0, min(1.0, x)))

def frame(t):
    im = bg.copy()
    beat = ((t - BEAT0) * BPM / 60) % 1 if t > BEAT0 else 0
    pulse = 1 + 0.012 * math.exp(-beat * 6) if t < VOC_END + 1 else 1
    s = round(AW * pulse); a = art_s if s == AW else art_s.resize((s, s), Image.BILINEAR)
    m = amask if s == AW else amask.resize((s, s))
    im.paste(a, (110 + (AW - s) // 2, 110 + (AW - s) // 2), m)
    d = ImageDraw.Draw(im)
    d.text((RX, 150), TITLE, font=F_T, fill=(255, 255, 255))
    d.text((RX, 238), f"화성특례시 AI CM송  ·  {SUB}", font=F_S, fill=(255, 205, 120))
    # lyrics: current line big, previous / next dim
    cur = max([i for i, l in enumerate(LINES) if l[0] <= t] or [-1])
    if t < VOC_END + 0.6:
        for off, (fy, font, base) in {-1: (430, F_N, 90), 0: (530, F_L, 255), 1: (630, F_N, 120)}.items():
            i = cur + off
            if 0 <= i < len(LINES):
                st = LINES[i][0]; fade = ease((t - st) / 0.25) if off == 0 else 1
                col = (255, 255, 255, int(base * (0.35 + 0.65 * fade))) if off == 0 else (220, 220, 235, base)
                lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(lay).text((RC, fy), LINES[i][1], font=font, fill=col, anchor="mm")
                im.paste(lay, (0, 0), lay)
    else:                                                                    # credits after the vocals
        k = ease((t - VOC_END - 0.6) / 0.8)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        for j, c in enumerate(CREDITS):
            ld.text((RX, 400 + j * 52), c, font=F_C, fill=(235, 235, 245, int(230 * k)))
        im.paste(lay, (0, 0), lay)
    # progress bar
    y = 790; d.rounded_rectangle((RX, y, W - 80, y + 10), 5, fill=(70, 70, 95))
    d.rounded_rectangle((RX, y, RX + (W - 80 - RX) * min(1, t / dur), y + 10), 5, fill=HS_ORANGE)
    d.text((RX, y + 24), f"{int(t // 60)}:{int(t % 60):02d}", font=F_TIME, fill=(200, 200, 215))
    d.text((W - 80, y + 24), f"{int(dur // 60)}:{int(dur % 60):02d}", font=F_TIME, fill=(200, 200, 215), anchor="ra")
    im.paste(small_card, (W - 80 - small_card.width, H - 60 - small_card.height), small_card)
    if t > TOTAL - 0.8: im = Image.blend(im, Image.new("RGB", (W, H)), ease((t - (TOTAL - 0.8)) / 0.8))
    if t < 0.4: im = Image.blend(Image.new("RGB", (W, H)), im, ease(t / 0.4))
    return im

os.makedirs("out", exist_ok=True)
n = round(TOTAL * FPS)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-i", AUDIO, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "320k", "-af", f"apad=pad_dur={TOTAL - dur + 0.1:.2f},afade=t=out:st={(TOTAL - 0.8) if TOTAL - dur < 1 else (dur - 0.12):.2f}:d={0.8 if TOTAL - dur < 1 else 0.3}",
                        "-t", f"{TOTAL:.3f}", "-movflags", "+faststart", f"out/{SONG}_{TITLE.replace(' ', '')}.mp4"], stdin=subprocess.PIPE)
for i in range(n):
    enc.stdin.write(frame(i / FPS).tobytes())
enc.stdin.close(); enc.wait()
print("done", TITLE, round(TOTAL, 2), "s")
