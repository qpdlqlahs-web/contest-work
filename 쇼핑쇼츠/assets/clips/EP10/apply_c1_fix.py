"""C1 시작 프레임 보정 (IR 핫스폿화). 무료, PIL+numpy(+scipy 불필요).
사용: python apply_c1_fix.py in.png out.png          (이미지)
      python apply_c1_fix.py in.mp4 out.mp4          (영상: ffmpeg 파이프, 전 프레임에 같은 마스크, 프레임마다 새 그레인)
마스크 C1_fix_mask.png(8bit, 255=전량 보정)가 같은 폴더에 없으면 자동 생성한다."""
import sys, os, subprocess
import numpy as np
from PIL import Image, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
MASK = os.path.join(HERE, "C1_fix_mask_v2.png")   # v2(10/10): 페더 40->90px, 바깥 확장 110px (v1 마스크 C1_fix_mask.png는 보존)
W, H = 1440, 2560
RECT = (280, 1330, 1170, 1900)      # x0,y0,x1,y1
FEET_Y, LEG_H = 1290, 105           # 다리 그림자: 발~1.5*다리높이(약 1450)까지 유지
KEEP_Y0 = FEET_Y + 1.5 * LEG_H      # 이 아래로 카펫 톤 페이드
FADE = 170
TONE_SLOPE, TONE_OFF = 0.42, 75     # L>=100 구간 톤 압축: 100->75 , 230->130
GRAIN = 7.0
HOT_BASE, HOT_PEAK, HOT_C = 84.0, 36.0, (725, 1600)   # v2: 경계 휘도를 주변 카펫(약 75~90)에 맞추려 base 96->84

def make_mask():
    m = Image.new("L", (W, H), 0)
    x0, y0, x1, y1 = RECT
    # 밝은 사각형 전체(약 x240~1200, y1300~1960)를 100% 덮도록 지시 영역을 바깥으로 확장, 바깥쪽 페더 약 80px+
    m.paste(255, (x0 - 110, y0 - 110, x1 + 110, y1 + 140))
    m = m.filter(ImageFilter.GaussianBlur(90))
    m.save(MASK)

def fix(rgb, rng):
    a = rgb.astype(np.float32)
    L = a.mean(axis=2)
    m = np.asarray(Image.open(MASK), np.float32)[..., None] / 255.0
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    # 1) 톤 압축 (그림자 구조 유지)
    Lt = np.where(L > 100, TONE_OFF + (L - 100) * TONE_SLOPE, L - (100 - L) * 0 - 25 * np.clip((100 - L) / 100, 0, 1) * 0)
    Lt = np.minimum(Lt, L)
    # 2) 둥근 핫스폿
    cx, cy = HOT_C
    g = np.exp(-(((xx - cx) / 330) ** 2 + ((yy - cy) / 300) ** 2))
    Hs = HOT_BASE + HOT_PEAK * g
    # 3) 발에서 1.5*다리높이 너머는 그림자 페이드
    w = np.clip(1 - (yy - KEEP_Y0) / FADE, 0, 1)
    Ln = w * Lt + (1 - w) * Hs
    # 4) 원본 미세 질감 일부 유지(고주파 *0.5) + 그레인
    low = np.asarray(Image.fromarray(L.clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3)), np.float32)
    hi = L - low
    Ln = Ln + 0.5 * hi + rng.normal(0, GRAIN, L.shape).astype(np.float32)
    d = (Ln - L)[..., None] * m
    return np.clip(a + d, 0, 255).astype(np.uint8)

def main():
    src, dst = sys.argv[1], sys.argv[2]
    if not os.path.exists(MASK): make_mask()
    if src.lower().endswith((".png", ".jpg")):
        Image.fromarray(fix(np.asarray(Image.open(src).convert("RGB")), np.random.default_rng(1))).save(dst)
        return
    pr = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate",
                         "-of", "csv=p=0", src], capture_output=True, text=True).stdout.strip().split(",")
    w, h = int(pr[0]), int(pr[1]); n, d = pr[2].split("/")
    global W, H
    # 마스크/좌표는 1440x2560 기준 -> 영상 크기에 맞춰 스케일
    sc = w / 1440.0
    rd = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-vf", "scale=1440:2560", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    wr = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1440x2560", "-r", f"{n}/{d}", "-i", "-",
                           "-i", src, "-map", "0:v", "-map", "1:a?", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", "-c:a", "copy", dst], stdin=subprocess.PIPE)
    rng = np.random.default_rng(7); sz = 1440 * 2560 * 3
    while True:
        buf = rd.stdout.read(sz)
        if len(buf) < sz: break
        wr.stdin.write(fix(np.frombuffer(buf, np.uint8).reshape(2560, 1440, 3), rng).tobytes())
    wr.stdin.close(); wr.wait()

if __name__ == "__main__":
    main()
