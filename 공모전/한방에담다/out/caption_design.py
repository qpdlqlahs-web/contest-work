# v4 캡션 디자인 A안(타이포 팀 확정, 감독 승인) - mock_caption.py 의 paper()/label() 그리기 로직을 그대로 사용, 칩 분리·크기 인자만 추가
import os, random, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from pathlib import Path
F = str(Path(__file__).resolve().parent / "fonts") + "/"

INK = (30, 26, 22)
INK2 = (74, 59, 44)
HANJI = (243, 233, 210)
SEAL = (179, 38, 30)
GREEN = (46, 107, 94)
YEL = (232, 182, 76)
BORDER = (201, 169, 110)

def hahmlet(size, wght):
    f = ImageFont.truetype(F + "Hahmlet-VF.ttf", size)
    try:
        f.set_variation_by_axes([wght])
    except Exception as e:
        print("var fail", e)
    return f

JUA = lambda s: ImageFont.truetype(F + "Jua-Regular.ttf", s)
PRET = lambda s: ImageFont.truetype(F + "Pretendard-SemiBold.otf", s)

def tw(font, t):
    b = font.getbbox(t)
    return b[2] - b[0]

def paper(w, h, base, alpha, seed=3):
    rnd = random.Random(seed)
    im = Image.new("RGBA", (w, h), base + (alpha,))
    px = im.load()
    for y in range(h):
        for x in range(w):
            n = rnd.randint(-5, 5)
            r, g, b, a = px[x, y]
            px[x, y] = (max(0, min(255, r + n)), max(0, min(255, g + n)), max(0, min(255, b + n)), a)
    d = ImageDraw.Draw(im)
    for _ in range(int(w * h / 2500)):  # fine hanji fibres
        x, y = rnd.randint(0, w), rnd.randint(0, h)
        L = rnd.randint(6, 22)
        d.line([(x, y), (x + L, y + rnd.randint(-3, 3))], fill=(base[0] - 18, base[1] - 20, base[2] - 24, 34), width=1)
    return im

def label(main, sub=None, chip=None, variant="A", main_size=50, chip_sep=False):
    """Returns RGBA label image. variant A: hanji label + seal chip. B: deep-green tag."""
    fm = hahmlet(main_size, 700)
    fs = hahmlet(40, 600)
    fc = hahmlet(34, 800)
    padx, pady, gap = 28, 16, 16
    lh_m, lh_s = 62, 50
    chip_w = (tw(fc, chip) + 24) if chip else 22
    chip_h = 54 if chip else 22
    w_main = chip_w + gap + tw(fm, main)
    w_sub = tw(fs, sub) if sub else 0
    W = max(w_main, w_sub) + padx * 2
    H = pady * 2 + lh_m + (lh_s + 4 if sub else 0)
    W = min(W, 880)
    if variant == "A":
        bg = paper(W, H, HANJI, 240)
        tcol, scol = INK, INK2
        ccol, ctext = SEAL, HANJI
    else:
        bg = Image.new("RGBA", (W, H), GREEN + (235,))
        tcol, scol = HANJI, (220, 208, 182)
        ccol, ctext = YEL, INK
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, W - 1, H - 1], 10, fill=255)
    lab = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    lab.paste(bg, (0, 0), mask)
    d = ImageDraw.Draw(lab)
    if variant == "A":
        d.rounded_rectangle([1, 1, W - 2, H - 2], 10, outline=BORDER + (200,), width=2)
    # main line, centred
    x0 = (W - w_main) // 2
    cy = pady + lh_m // 2
    chip_img = None; chip_c = None
    if chip and chip_sep:
        chip_img = Image.new("RGBA", (chip_w + 2, chip_h + 2), (0, 0, 0, 0))
        cd_ = ImageDraw.Draw(chip_img)
        cd_.rounded_rectangle([1, 1, chip_w, chip_h], 6, fill=ccol + (255,))
        cd_.text((1 + chip_w / 2, 1 + chip_h / 2 + 1), chip, font=fc, fill=ctext, anchor="mm")
        chip_c = (x0 + chip_w / 2 + 20, cy + 20)          # sh 좌표계(여백 20px 포함)
    elif chip:
        d.rounded_rectangle([x0, cy - chip_h // 2, x0 + chip_w, cy + chip_h // 2], 6, fill=ccol)
        d.text((x0 + chip_w / 2, cy + 1), chip, font=fc, fill=ctext, anchor="mm")
    else:
        d.rounded_rectangle([x0, cy - 11, x0 + 22, cy + 11], 3, fill=ccol)
    d.text((x0 + chip_w + gap, cy + 2), main, font=fm, fill=tcol, anchor="lm")
    if sub:
        d.text((W / 2, pady + lh_m + 4 + lh_s / 2), sub, font=fs, fill=scol, anchor="mm")
    # soft shadow
    sh = Image.new("RGBA", (W + 40, H + 40), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([20, 26, W + 20, H + 26], 12, fill=(30, 26, 22, 95))
    sh = sh.filter(ImageFilter.GaussianBlur(8))
    sh.alpha_composite(lab, (20, 20))
    if chip_sep:
        return sh, chip_img, chip_c
    return sh



def loc_card():
    """위치 카드: 주문구 서울한방진흥센터(50/700)+주홍 점, 부문구 2줄(40/600). 폭 760, 높이 210."""
    fm, fs = hahmlet(50, 700), hahmlet(40, 600)
    W, H = 760, 210
    bg = paper(W, H, HANJI, 240, seed=9)
    mask = Image.new("L", (W, H), 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, W - 1, H - 1], 10, fill=255)
    card = Image.new("RGBA", (W, H), (0, 0, 0, 0)); card.paste(bg, (0, 0), mask)
    cd = ImageDraw.Draw(card)
    cd.rounded_rectangle([1, 1, W - 2, H - 2], 10, outline=BORDER + (200,), width=2)
    name_w = tw(fm, "서울한방진흥센터")
    x0 = (W - (16 + 16 + name_w)) // 2
    cd.rectangle([x0, 46, x0 + 16, 62], fill=SEAL)
    cd.text((x0 + 32, 56), "서울한방진흥센터", font=fm, fill=INK, anchor="lm")
    cd.text((W / 2, 118), "서울 동대문구 약령중앙로 26", font=fs, fill=INK2, anchor="mm")
    cd.text((W / 2, 168), "1호선 제기동역 2번 출구", font=fs, fill=INK2, anchor="mm")
    sh = Image.new("RGBA", (W + 40, H + 40), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([20, 26, W + 20, H + 26], 12, fill=(30, 26, 22, 95))
    sh = sh.filter(ImageFilter.GaussianBlur(8)); sh.alpha_composite(card, (20, 20))
    return sh


# 문구 구조(사양표): 이름 -> (주문구, 부문구, 칩, 주문구 크기)
CAPTIONS = {
    "cap_c02": ("서울약령시한의약박물관", None, "2F", 50),
    "cap_c04": ("약재 약 380종을 만나는 곳", None, None, 50),
    "cap_c06": ("군신좌사", "박물관에서 소개하는 처방 구성 원리", None, 50),
    "cap_c08": ("약초 족욕", "약쑥·감국 등 계절 약재", "2F", 50),
    "cap_c10": ("두한족열", "예부터 전하는 건강 습관 (센터 안내)", None, 50),
    "cap_c11": ("전통의상 체험", None, "1F", 50),
    "cap_c12": ("조선시대 백성을 돌보던 의료·구휼기관", None, None, 46),
    "cap_c13": ("한방카페", None, "별관", 50),
}


def build_captions():
    out = {}
    for k, (m, sb, chip, size) in CAPTIONS.items():
        r = label(m, sb, chip, "A", main_size=size, chip_sep=True)
        out[k] = r
    out["loc"] = (loc_card(), None, None)
    return out
