"""EP10 크루 정지 레이어 추출 (무료). C5_start_v3.png -> crew/*.png (RGBA, 원본 해상도)
마스크: u2net.onnx (rembg 공식 GitHub 릴리스 danielgatis/rembg v0.0.0)를 onnxruntime으로 직접 실행. 뭉치는 타원 소프트 마스크.
사용: python ep10_sprites.py <u2net.onnx 경로>"""
import sys, numpy as np, onnxruntime as ort
from PIL import Image, ImageFilter, ImageDraw
HERE = __file__.rsplit("\\", 1)[0].rsplit("/", 1)[0]
MODEL = sys.argv[1] if len(sys.argv) > 1 else "u2net.onnx"
sess = ort.InferenceSession(MODEL)
def matte(img):
    w, h = img.size
    x = np.asarray(img.convert("RGB").resize((320, 320), Image.LANCZOS), np.float32) / 255.
    x = x / max(x.max(), 1e-6)
    x = ((x - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]).transpose(2, 0, 1)[None].astype(np.float32)
    o = sess.run(None, {sess.get_inputs()[0].name: x})[0][0, 0]
    o = (o - o.min()) / (o.max() - o.min() + 1e-9)
    return Image.fromarray((o * 255).astype(np.uint8)).resize((w, h), Image.LANCZOS)
src = Image.open(f"{HERE}/C5_start_v3.png").convert("RGB")
ox, oy = 150, 900
boxes = {"boss": (300, 960, 480, 1300), "yeosa": (490, 1040, 650, 1290), "kong": (600, 955, 850, 1285)}
out = f"{HERE}/crew"
for k, b in boxes.items():
    c = src.crop(b)
    m = matte(c)
    m = m.point(lambda v: 0 if v < 40 else (255 if v > 215 else int((v - 40) * 255 / 175)))
    arr = np.asarray(m); ys, xs = np.where(arr > 128)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    rgba = Image.merge("RGBA", (*c.convert("L").split() * 1, m)) if False else None
    g = c.convert("L")
    spr = Image.merge("RGBA", (g, g, g, m)).crop((x0, y0, x1, y1))
    spr.save(f"{out}/{k}.png"); print(k, spr.size)
# 뭉치: 타원 소프트 마스크
cb = (ox + 335, oy + 430, ox + 525, oy + 565)
c = src.crop(cb); g = c.convert("L")
m = Image.new("L", c.size, 0); ImageDraw.Draw(m).ellipse([22, 26, c.width - 22, c.height - 22], fill=255)
m = m.filter(ImageFilter.GaussianBlur(9))
Image.merge("RGBA", (g, g, g, m)).save(f"{out}/clump.png"); print("clump", c.size)
