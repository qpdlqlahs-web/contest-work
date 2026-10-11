"""Album-art style video for the Pureal CM song (1920x1080, 30 fps): square album art (left) + synced lyrics,
song info, progress bar and the official Pureal BI (right). Product photos / BI come from the official contest
brand-asset pack (scaled only). Everything else is drawn locally.
usage: python make_cm_video.py"""
import json, math, os, random, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

os.chdir(os.path.dirname(os.path.abspath(__file__)))
W, H, FPS = 1920, 1080, 30
FB, FBD, FM = ("C:/Windows/Fonts/NotoSansCJKkr-Black.otf", "C:/Windows/Fonts/NotoSansCJKkr-Bold.otf",
               "C:/Windows/Fonts/NotoSansCJKkr-Medium.otf")
ASSETS = "refs/assets"
NAVY, BLUE, PINK = (22, 38, 92), (0, 98, 205), (226, 96, 148)
TITLE, SUB = "퓨리얼, 진짜 물", "퓨리얼 정수기 브랜드 CM송  ·  시티팝 징글"
AUDIO = "audio/A2_42s.wav"
AI_NOTE = "이 영상은 생성형 AI를 기반으로 제작되었습니다."

def cutout(path, tol=14):
    """white-background product photo -> RGBA (flood fill from the border, keeps inner whites)"""
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

def vgrad(w, h, stops):
    """vertical gradient through [(pos, rgb), ...]"""
    col = np.zeros((h, 3))
    for y in range(h):
        t = y / (h - 1)
        for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
            if p0 <= t <= p1:
                k = (t - p0) / (p1 - p0); col[y] = np.array(c0) * (1 - k) + np.array(c1) * k; break
    return Image.fromarray(np.repeat(col[:, None, :], w, axis=1).astype(np.uint8))

def bi_card(width):
    bi = Image.open(f"{ASSETS}/10. 퓨리얼 로고/퓨리얼_BI.png").convert("RGBA"); bi = bi.crop(bi.getbbox())   # official BI, unmodified (scaled only)
    bi = fit(bi, width - 64, 10_000)
    card = Image.new("RGBA", (bi.width + 64, bi.height + 48), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((0, 0, card.width - 1, card.height - 1), 24, fill=(255, 255, 255, 245))
    card.alpha_composite(bi, (32, 24))
    return card

# ---------------------------------------------------------------- album art (2000 x 2000)
S, HORIZON = 2000, 1330
random.seed(11)
art = vgrad(S, S, [(0, (176, 186, 246)), (0.42, (236, 206, 238)), (HORIZON / S, (255, 222, 230)),
                   (HORIZON / S + 0.001, (214, 218, 250)), (1, (150, 172, 232))]).convert("RGBA")
cmask = Image.new("L", (S, S), 0); cd = ImageDraw.Draw(cmask)                 # clouds: blur the alpha only (no dark halo)
for cx, cy, sc in [(330, 700, 1.0), (1650, 620, 1.2), (1050, 900, 0.8), (160, 1120, 0.7), (1850, 1080, 0.8)]:
    for dx, dy, rx, ry in [(0, 0, 230, 110), (-160, 40, 150, 80), (170, 30, 170, 90), (60, -70, 150, 100)]:
        cd.ellipse((cx + (dx - rx) * sc, cy + (dy - ry) * sc, cx + (dx + rx) * sc, cy + (dy + ry) * sc), fill=150)
clouds = Image.new("RGBA", (S, S), (255, 246, 252, 255)); clouds.putalpha(cmask.filter(ImageFilter.GaussianBlur(34)))
art.alpha_composite(clouds)
d = ImageDraw.Draw(art)
for _ in range(90):                                                            # sparkles in the sky
    x, y, r = random.randrange(S), random.randrange(80, HORIZON - 80), random.choice([2, 3, 4, 6])
    d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, random.randint(140, 230)))
    if r >= 4: d.line((x - 4 * r, y, x + 4 * r, y), fill=(255, 255, 255, 120), width=2); d.line((x, y - 4 * r, x, y + 4 * r), fill=(255, 255, 255, 120), width=2)
rip = Image.new("L", (S, S), 0); rd = ImageDraw.Draw(rip)                    # soft water ripples
for k_ in range(18):
    y = HORIZON + 40 + k_ * 34 + k_ * k_ * 0.8
    for _ in range(3):
        x0 = random.randrange(-100, S); ln = random.randrange(120, 380) + k_ * 12
        rd.ellipse((x0, y - 4 - k_ * 0.3, x0 + ln, y + 4 + k_ * 0.3), fill=random.randint(60, 110))
ripl = Image.new("RGBA", (S, S), (255, 255, 255, 255)); ripl.putalpha(rip.filter(ImageFilter.GaussianBlur(4)))
art.alpha_composite(ripl)

lineup = fit(cutout(f"{ASSETS}/02. 퓨리얼 유로체인저 직수정수기 PPA-300/PPA-300 (13).jpg"), 1640, 900)
lx, ly = (S - lineup.width) // 2, HORIZON + 230 - lineup.height
refl = lineup.transpose(Image.FLIP_TOP_BOTTOM)
ra = np.array(refl.getchannel("A")).astype(float) * np.linspace(0.38, 0, refl.height)[:, None]
refl.putalpha(Image.fromarray(ra.astype(np.uint8))); refl = refl.filter(ImageFilter.GaussianBlur(3))
art.alpha_composite(refl, (lx, ly + lineup.height + 6))
shadow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
ImageDraw.Draw(shadow).ellipse((lx + 40, ly + lineup.height - 30, lx + lineup.width - 40, ly + lineup.height + 30), fill=(60, 60, 120, 90))
art.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(18)))
art.alpha_composite(lineup, (lx, ly))

dd = ImageDraw.Draw(art)
text_c(dd, (S // 2, 250), TITLE, ImageFont.truetype(FB, 210), NAVY, (255, 255, 255), 18)
text_c(dd, (S // 2, 455), "Pure하게  Real하게", ImageFont.truetype(FB, 104), (255, 255, 255), PINK, 12)
card = bi_card(560); art.alpha_composite(card, ((S - card.width) // 2, S - card.height - 70))
os.makedirs("out", exist_ok=True)
art.convert("RGB").save("out/albumart.png")

# ---------------------------------------------------------------- lyrics + timing (vocal onsets measured on the demucs vocal stem)
LY = json.load(open("lyrics.json", encoding="utf-8"))
LINES, BPM, BEAT0, VOC_END = LY["lines"], LY["bpm"], LY["beat0"], LY["vocal_end"]
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", AUDIO],
                           capture_output=True, text=True).stdout)
TOTAL = dur + LY.get("tail", 0.5)
CREDITS = ["음원 : Suno AI v6 (Pro, 상업적 이용권)로 생성",
           "작사·기획 : CM공방",
           "제품 이미지·로고 : 퓨리얼 공식 브랜드 자산 (콘테스트 제공)",
           "폰트 : Noto Sans CJK KR (SIL OFL)"]

# ---------------------------------------------------------------- static layers
bg = radial((W, H), (246, 244, 255), (206, 212, 246), 0.3, 0.25, 1.2)
AW = 860
art_s = art.convert("RGB").resize((AW, AW), Image.LANCZOS)
amask = Image.new("L", (AW, AW), 0); ImageDraw.Draw(amask).rounded_rectangle((0, 0, AW - 1, AW - 1), 34, fill=255)
sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(sh).rounded_rectangle((110 + 14, 100 + 22, 110 + AW + 14, 100 + AW + 22), 40, fill=(60, 60, 120, 90))
bg = Image.alpha_composite(bg.convert("RGBA"), sh.filter(ImageFilter.GaussianBlur(22))).convert("RGB")
ImageDraw.Draw(bg).text((110 + AW // 2, 1012), AI_NOTE, font=ImageFont.truetype(FM, 24), fill=(95, 105, 150), anchor="mm")
small_card = bi_card(330)
F_T, F_S, F_L, F_N, F_C, F_TIME = (ImageFont.truetype(FB, 66), ImageFont.truetype(FBD, 30), ImageFont.truetype(FB, 54),
                                   ImageFont.truetype(FBD, 36), ImageFont.truetype(FM, 26), ImageFont.truetype(FBD, 24))
RX = 1040                      # right panel left edge
RC = (RX + W - 80) // 2        # right panel centre

def ease(x): return 0.5 - 0.5 * math.cos(math.pi * max(0.0, min(1.0, x)))

def frame(t):
    im = bg.copy()
    beat = ((t - BEAT0) * BPM / 60) % 1 if t > BEAT0 else 0
    pulse = 1 + 0.012 * math.exp(-beat * 6) if t < VOC_END + 0.3 else 1
    s = round(AW * pulse); a = art_s if s == AW else art_s.resize((s, s), Image.BILINEAR)
    m = amask if s == AW else amask.resize((s, s))
    im.paste(a, (110 + (AW - s) // 2, 100 + (AW - s) // 2), m)
    d = ImageDraw.Draw(im)
    d.text((RX, 140), TITLE, font=F_T, fill=NAVY)
    d.text((RX, 230), SUB, font=F_S, fill=PINK)
    cur = max([i for i, l in enumerate(LINES) if l[0] <= t] or [-1])
    if t < VOC_END + 0.6:
        for off, (fy, font, base) in {-1: (420, F_N, 110), 0: (520, F_L, 255), 1: (620, F_N, 140)}.items():
            i = cur + off
            if 0 <= i < len(LINES):
                st = LINES[i][0]; fade = ease((t - st) / 0.25) if off == 0 else 1
                col = (*NAVY, int(base * (0.35 + 0.65 * fade))) if off == 0 else (95, 105, 150, base)
                fnt = font
                while fnt.getlength(LINES[i][1]) > W - 80 - RX - 40: fnt = fnt.font_variant(size=fnt.size - 2)   # keep inside the panel
                lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(lay).text((RC, fy), LINES[i][1], font=fnt, fill=col, anchor="mm")
                im.paste(lay, (0, 0), lay)
    else:                                                                    # credits after the vocals
        k = ease((t - VOC_END - 0.6) / 0.8)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        for j, c in enumerate(CREDITS):
            ld.text((RX, 380 + j * 54), c, font=F_C, fill=(*NAVY, int(235 * k)))
        im.paste(lay, (0, 0), lay)
    y = 780; d.rounded_rectangle((RX, y, W - 80, y + 10), 5, fill=(190, 196, 228))
    d.rounded_rectangle((RX, y, RX + (W - 80 - RX) * min(1, t / dur), y + 10), 5, fill=BLUE)
    tc = min(t, dur); d.text((RX, y + 24), f"{int(tc // 60)}:{int(tc % 60):02d}", font=F_TIME, fill=(95, 105, 150))
    d.text((W - 80, y + 24), f"{int(dur // 60)}:{int(dur % 60):02d}", font=F_TIME, fill=(95, 105, 150), anchor="ra")
    im.paste(small_card, (W - 80 - small_card.width, H - 70 - small_card.height), small_card)
    if t > TOTAL - 0.8: im = Image.blend(im, Image.new("RGB", (W, H)), ease((t - (TOTAL - 0.8)) / 0.8))
    if t < 0.4: im = Image.blend(Image.new("RGB", (W, H)), im, ease(t / 0.4))
    return im

if __name__ == "__main__":
    import sys
    if "--still" in sys.argv:                                                  # QA stills only
        for t in [float(x) for x in sys.argv[sys.argv.index("--still") + 1:]]:
            frame(t).save(f"out/still_{t:05.2f}.png")
        sys.exit()
    n = round(TOTAL * FPS)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-i", AUDIO, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-tune", "stillimage",
                            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
                            "-af", f"apad=pad_dur={TOTAL - dur + 0.1:.2f}", "-t", f"{TOTAL:.3f}", "-movflags", "+faststart",
                            "out/퓨리얼_진짜물.mp4"], stdin=subprocess.PIPE)
    for i in range(n):
        enc.stdin.write(frame(i / FPS).tobytes())
    enc.stdin.close(); enc.wait()
    print("done", TITLE, round(TOTAL, 2), "s")
