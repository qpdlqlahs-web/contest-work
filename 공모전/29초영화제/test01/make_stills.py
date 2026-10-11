import subprocess, os
from PIL import Image, ImageDraw, ImageFont
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import sys
TAG = sys.argv[1] if len(sys.argv) > 1 else 'v1'
OUT = {'v1': 'out', 'v2': 'out/v2', 'v3': 'out/v3', 'v31': 'out/v31'}[TAG]
FR = {'v1': 'frames', 'v2': 'frames_v2', 'v3': 'frames_v3', 'v31': 'frames_v31'}[TAG]
VERS = ('sig',) if TAG == 'v31' else ('sig', 'nosig')
fnt = ImageFont.truetype('../fonts/Galmuri/Galmuri11-Bold.ttf', 22)
keys = {'C07': [30, 47, 49, 52, 60, 70, 90], 'C10': [5, 15, 22, 23, 24, 26, 40, 52, 70, 78]}
base = {'C07': 360, 'C10': 542}
for clip, fs in keys.items():
    for v in VERS:
        sel = '+'.join(f'eq(n\,{f})' for f in fs)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{OUT}/{clip}_{v}.mp4', '-vf', f"select='{sel}'", '-fps_mode', 'passthrough', f'{OUT}/stills/_{clip}_{v}_%02d.png'], check=True)
        for i, f in enumerate(fs):
            os.replace(f'{OUT}/stills/_{clip}_{v}_{i+1:02d}.png', f'{OUT}/stills/{clip}_{v}_f{base[clip]+f}.png')
for clip, n in (('C07', 96), ('C10', 82)):
    for v in VERS:
        fs = list(range(0, n, 5)); cols = 10; tw, th = 216, 384
        rows = (len(fs) + cols - 1) // cols
        sheet = Image.new('RGB', (cols * tw, rows * (th + 30)), (16, 16, 20)); d = ImageDraw.Draw(sheet)
        for i, f in enumerate(fs):
            im = Image.open(f'{FR}/{clip}_{v}/{f:03d}.png').resize((tw, th), Image.LANCZOS)
            x, y = (i % cols) * tw, (i // cols) * (th + 30)
            sheet.paste(im, (x, y + 30)); d.text((x + 6, y + 4), f'f{base[clip]+f}', font=fnt, fill=(230, 230, 230))
        sheet.save(f'{OUT}/contact/{clip}_{v}_contact_4.8fps.jpg', quality=90)
