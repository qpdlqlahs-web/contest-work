# -*- coding: utf-8 -*-
"""v3: C04 서랍 얼룩 -> 패치 복제 대신 '거리 DOF 블러'. 원본 클립(prep\clips\C04.mp4)에서 x0~560,y1150~1600 전경을
넓게(페더 ~100px) 부드럽게 흐리고, 카메라에 가까울수록(좌하단) 강하게. 감초(왼쪽 경계 추적)는 제외. 감초 팔 번짐은 원본 그대로."""
import numpy as np, subprocess
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
W, H = 1080, 1920
Y0, Y1, X0, X1 = 820, 1800, 0, 720
poly = [(120, 1185), (556, 1185), (556, 1700), (120, 1700)]
mk = Image.new("L", (W, H), 0); ImageDraw.Draw(mk).polygon(poly, fill=255)
M0 = gaussian_filter(np.asarray(mk, np.float32) / 255, 80)
M0 = np.clip(M0 * 1.7, 0, 1)[Y0:Y1, X0:X1]
yy, xx = np.mgrid[Y0:Y1, X0:X1]
near = np.clip(((yy - 1150) / 500.0) * 0.6 + ((600 - xx) / 600.0) * 0.4, 0, 1)      # 좌하단일수록 1
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(ROOT / "prep/clips/C04.mp4"), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
out_path = ROOT / "out/_work/C04_dof_v3.mp4"
enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "24", "-i", "-",
                        "-c:v", "libx264", "-preset", "slow", "-crf", "12", "-pix_fmt", "yuv420p", "-an", str(out_path)], stdin=subprocess.PIPE)
i = 0
while True:
    buf = dec.stdout.read(W * H * 3)
    if len(buf) < W * H * 3: break
    fr = np.frombuffer(buf, np.uint8).reshape(H, W, 3).astype(np.float32)
    xc = min(556.0, float(np.interp(i, [0, 10, 20, 30, 50, 70, 90], [598, 565, 545, 550, 560, 580, 590])) - 28)
    cut = np.clip((xc + 12 - np.arange(X0, X1)) / 24.0, 0, 1)[None, :]
    reg = fr[Y0:Y1, X0:X1]
    b1 = gaussian_filter(reg, (8, 8, 0)); b2 = gaussian_filter(reg, (14, 14, 0)); b3 = gaussian_filter(reg, (19, 19, 0))
    E = (M0 * cut) * (0.6 + 0.4 * near)                      # 0(선명)~1(최대 흐림), 좌하단·내부일수록 큼
    E3 = E[..., None]
    lv = np.where(E3 < 0.4, reg * (1 - E3 / 0.4) + b1 * (E3 / 0.4),
         np.where(E3 < 0.7, b1 * (1 - (E3 - 0.4) / 0.3) + b2 * ((E3 - 0.4) / 0.3), b2 * (1 - (E3 - 0.7) / 0.3) + b3 * ((E3 - 0.7) / 0.3)))
    bl = lv; m = 1.0
    out = fr.copy(); out[Y0:Y1, X0:X1] = bl
    enc.stdin.write(np.clip(out, 0, 255).astype(np.uint8).tobytes())
    i += 1
enc.stdin.close(); enc.wait(); print("frames", i)
