# -*- coding: utf-8 -*-
"""v2: C04 클립의 서랍 블러 얼룩을, 원본(블러 전) 시작 프레임 C04S_1 의 선명한 상자로 대체(라벨 글자는 한지색 빈 라벨로).
카메라가 가로로 패닝(0→-103px)하므로 패치를 프레임별로 이동(하단 좌측 위상상관으로 측정한 값 보간). 원본 파일은 건드리지 않음."""
import numpy as np, subprocess
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import gaussian_filter, binary_closing, binary_fill_holes, binary_dilation
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
W, H = 1080, 1920
src = np.array(Image.open(ROOT / "img/C04S_1.png").convert("RGB").resize((W, H), Image.LANCZOS)).astype(np.float32)

# --- 라벨(가짜 글자) 지우기: 라벨 4개 대략 bbox(1080 좌표)
boxes = [(535, 1280, 580, 1342), (462, 1325, 512, 1395), (362, 1385, 423, 1470), (228, 1462, 308, 1555)]
for (x0, y0, x1, y1) in boxes:
    reg = src[y0:y1, x0:x1]
    lum = reg.mean(2); sat = reg.max(2) - reg.min(2)
    paper = (lum > 150) & (sat < 70)
    paper = binary_fill_holes(binary_closing(paper, iterations=4))
    if paper.sum() < 30:
        continue
    col = np.median(reg[(lum > 170) & (sat < 60)], axis=0) if ((lum > 170) & (sat < 60)).sum() > 20 else np.array([225., 215., 195.])
    m = gaussian_filter(binary_dilation(paper, iterations=1).astype(np.float32), 0.8)[..., None]
    grad = (np.linspace(-6, 6, reg.shape[0])[:, None, None] * np.array([1, 1, 1]))
    fill = col + grad
    src[y0:y1, x0:x1] = reg * (1 - m) + fill * m
src = np.clip(src, 0, 255)
# 소스에서 감초(x>=570, y1080~1440)를 지움: 왼쪽 상자 열(x-135)을 오른쪽으로 복제 + 페더
dm = np.zeros((H, W), np.float32); dm[1070:1450, 566:720] = 1; dm = gaussian_filter(dm, 6)[..., None]
_s = 0.93; _cx, _cy = 525.0, 1300.0; _a = 1 / _s
_co = (_a, 0, _cx - (_cx + 135) * _a, 0, _a, _cy - (_cy - 28) * _a)
_rp = np.asarray(Image.fromarray(src.astype(np.uint8)).transform((W, H), Image.AFFINE, _co, resample=Image.BICUBIC)).astype(np.float32)
rep = np.zeros_like(src); rep[:, 566:720] = _rp[:, 566:720]
src = src * (1 - dm) + rep * dm

# --- 마스크(프레임0 좌표)
poly = [(176, 1185), (556, 1185), (556, 1700), (200, 1700), (168, 1500)]
mk = Image.new("L", (W, H), 0); ImageDraw.Draw(mk).polygon(poly, fill=255)
mask0 = gaussian_filter(np.asarray(mk, np.float32) / 255, 7)

keys = [0, 15, 30, 45, 60, 72, 90]; dxs = [0, -21, -42, -65, -86, -96, -103]
def dx_of(i): return float(np.interp(i, keys, dxs))

def shift_x(a, dx):
    s = int(round(dx))
    out = np.empty_like(a)
    if s < 0:
        out[:, :s] = a[:, -s:]; out[:, s:] = a[:, -1:]
    elif s > 0:
        out[:, s:] = a[:, :-s]; out[:, :s] = a[:, :1]
    else:
        out = a.copy()
    return out

dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(ROOT / "prep/clips/C04.mp4"), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
out_path = ROOT / "out/_work/C04_fixed.mp4"
enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "24", "-i", "-",
                        "-c:v", "libx264", "-preset", "slow", "-crf", "12", "-pix_fmt", "yuv420p", "-an", str(out_path)], stdin=subprocess.PIPE)
i = 0
while True:
    buf = dec.stdout.read(W * H * 3)
    if len(buf) < W * H * 3: break
    fr = np.frombuffer(buf, np.uint8).reshape(H, W, 3).astype(np.float32)
    d = dx_of(i)
    p = shift_x(src, d)
    xc = min(556.0, float(np.interp(i, [0, 10, 20, 30, 50, 70, 90], [598, 565, 545, 550, 560, 580, 590])) - 28)
    cut = np.clip((xc + 12 - np.arange(W)) / 24.0, 0, 1)[None, :]
    m = (mask0 * cut)[..., None]
    # 패치는 원본 시작 프레임 색감과 클립 색감 차이를 보정(좌측 선명 영역 평균으로 게인)
    ref_c = fr[1500:1700, 100:170].mean((0, 1)); ref_s = p[1500:1700, 100:170].mean((0, 1))
    gain = np.clip(ref_c / (ref_s + 1e-3), 0.9, 1.1)
    y0, y1, x0, x1 = 1100, 1760, 60, 720            # 저주파는 클립에서, 고주파(상자 디테일)는 패치에서 -> 밝기 이음새 제거
    pc = p[y0:y1, x0:x1]; fc = fr[y0:y1, x0:x1]
    adj = pc - gaussian_filter(pc, (18, 18, 0)) + gaussian_filter(fc, (18, 18, 0))
    mm = m[y0:y1, x0:x1]
    outf = fr.copy(); outf[y0:y1, x0:x1] = fc * (1 - mm) + adj * mm
    enc.stdin.write(np.clip(outf, 0, 255).astype(np.uint8).tobytes())
    i += 1
enc.stdin.close(); enc.wait(); print("frames", i)
