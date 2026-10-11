"""Motion QA: consecutive frames of clips at a fixed rate so direction, sliding and morphs are visible.
usage: python qa/motion_strip.py OUT.jpg FPS clip1[:start:end] clip2[:start:end] ..."""
import subprocess, sys, os, tempfile
from PIL import Image, ImageDraw

out, fps, specs = sys.argv[1], float(sys.argv[2]), sys.argv[3:]
rows = []
with tempfile.TemporaryDirectory() as td:
    for n, spec in enumerate(specs):
        path, *rng = spec.split(":")
        a = float(rng[0]) if rng else 0.0
        b = float(rng[1]) if len(rng) > 1 else 5.0
        pat = os.path.join(td, f"{n}_%03d.jpg")
        vf = f"fps={fps},scale=200:-2"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(a), "-t", str(b - a), "-i", path, "-vf", vf, pat], check=True)
        frames = sorted(f for f in os.listdir(td) if f.startswith(f"{n}_"))
        ims = []
        for k, f in enumerate(frames):
            im = Image.open(os.path.join(td, f)).convert("RGB")
            ImageDraw.Draw(im).text((3, 3), f"{os.path.basename(path)[:8]} {a + k / fps:.2f}", fill="white", stroke_width=2, stroke_fill="black")
            ims.append(im)
        rows.append(ims)
    w, h = rows[0][0].size
    cols = max(len(r) for r in rows)
    sheet = Image.new("RGB", (w * cols, h * len(rows)), "white")
    for r, ims in enumerate(rows):
        for c, im in enumerate(ims):
            sheet.paste(im.resize((w, h)), (c * w, r * h))
    sheet.save(out, quality=82)
print(out, len(rows), "rows x", cols)
