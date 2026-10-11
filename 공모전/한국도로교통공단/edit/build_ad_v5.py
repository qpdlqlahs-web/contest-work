"""Ad v5 (16:9, 24 fps): the FULL song uncut (no audio splices), one unique shot per lyric line,
cuts on bar lines with 3-frame soft cuts, interpolated slow-downs, per-shot colour matching,
enforcement-camera flash composited on the flash unit itself. usage: python edit/build_ad_v5.py [out.mp4]"""
import json, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")
OUT = sys.argv[1] if len(sys.argv) > 1 else "edit/ad_v5.mp4"
FPS, W, H = 24, 1920, 1080
SONG = "거북이 모드.wav"
SONG_END = 111.56
FONT = r"C\:/Windows/Fonts/NotoSansCJKkr-Black.otf"   # SIL OFL
BAR0, BAR = 0.348, 60 / 136 * 4
bar = lambda k: BAR0 + BAR * k
SOFT = 3            # frames of dissolve at every cut ("soft cut")
END_AT = bar(59)    # end card starts after the last sung line (104.47)
TOTAL = 112.5
TMP = "edit/tmp_v5"; os.makedirs(TMP, exist_ok=True)

# (source, clip in-point, timeline start, timeline end, extra filter). "@png" = still with slow push-in.
SHOTS = [
    ("A04", 0.0, 0.0, bar(2), None),                     # 띵! 보호구역에 진입했습니다
    ("A05", 0.0, bar(2), bar(5), {"xf": "crop=1640:922:60:80"}),   # crop out clay wall reliefs that look like letters                  # 거북이 모드를 켭니다 (transformation)
    ("N2", 0.0, bar(5), bar(7), None),                   # instrumental: turtle-car proudly at 30
    ("@keyframes_ad/A06.png", 0, bar(7), bar(9), None),   # ON 삼십 삼십 (needle exactly 30)
    ("A08", 0.0, bar(9), bar(11), None),                 # 할머니도 아이도 천천히 건너요
    ("A09", 0.0, bar(11), bar(13), None),                # ON 삼십 삼십
    ("A21", 0.0, bar(13), bar(15), None),                # 여기서부턴 느려도 멋져요
    ("V1", 0.0, bar(15), bar(17), None),                 # 키가 작아 안 보일까 봐
    ("V2", 0.0, bar(17), bar(19), {"patch": [(730, 0, 870, 885)]}),   # remove a traffic light that pops in mid-shot                 # 손을 번쩍 들었어요
    ("V3", 0.0, bar(19), bar(21), None),                 # 차가 섰나 한 번 더 보고
    ("V4", 0.0, bar(21), bar(23), {"patch": [(1400, 40, 1610, 390)]}),   # 왼쪽 오른쪽 건너요 (signal turns red at raw 3.0 -> hold frame-0 signal)
    ("V5", 0.0, bar(23), bar(25), {"patch": [(1280, 80, 1452, 238)]}),   # 걸음이 좀 느려도 괜찮아 (top red lamp kept dark)
    ("A10", 0.0, bar(25), bar(27), None),                # 초록불 끝까지 기다려줘요
    ("V6", 0.0, bar(27), bar(29), None),                 # 우리 손주 손 꼭 잡고
    ("A11", 0.0, bar(29), bar(32), None),                # 천천히 가도 다 도착해요
    ("A02", 0.0, bar(32), bar(34), None),                # chorus 2: rabbit-car ignores the zone
    ("A07", 0.0, bar(34), bar(36), {"xf": "crop=1800:1013:128:30"}),   # crop out a bin with letter-like graphics                # ...speeds past grandma
    ("A16", 0.2, bar(36), bar(38), {"raw_end": 3.0}),    # 삼십! 삼십! - mascot warns the rabbit-car (same street as the camera)
    ("A20", 0.0, bar(38), bar(40) + 2 * BAR / 4, None),  # 여기서부턴 느려도 멋져요 (mascot parade)
    ("A12", 0.0, bar(40) + 2 * BAR / 4, bar(42) + 2 * BAR / 4, None),        # 안전띠는 찰칵
    ("A13", 0.0, bar(42) + 2 * BAR / 4, bar(44) + 2 * BAR / 4, None),        # 돌기 전엔 깜빡
    ("A14", 0.0, bar(44) + 2 * BAR / 4, bar(46), None),  # 킥보드엔 헬멧
    ("A19", 0.0, bar(46), bar(48), None),                # chorus 3
    ("A01", 0.0, bar(48), bar(50), None),
    ("A17", 0.0, bar(50), bar(52), {"xf": "crop=iw*0.86:ih*0.86:0:0", "raw_end": 3.1}),
    ("N3", 0.0, bar(52), bar(54), {"raw_end": 3.4}),  # (a green walk signal enters frame after 3.6)
    ("A15", 1.13, bar(54), 98.76, None),                 # 토끼는 찰칵 (flash at raw 3.2 = 97.72)
    ("A22", 2.3, 98.76, 100.16, None),                   # 거북이는 씨익
    ("A18", 0.0, 100.16, END_AT, None),                  # 이 동네에선 거북이가 이겨요
]
FLASH_T, FLASH_XY = 97.72, (1125, 326)   # timeline time / position of the flash unit (output pixels)
LYRICS = [(0.10, 5.50, "딩! 보호구역에 진입했습니다"), (6.84, 9.00, "거북이 모드를 켭니다"),
          (12.38, 16.20, "거북이 모드 ON! 삼십! 삼십!"), (16.76, 19.55, "할머니도 아이도 천천히 건너요"),
          (19.64, 23.10, "거북이 모드 ON! 삼십! 삼십!"), (23.20, 26.70, "여기서부턴 느려도 멋져요"),
          (27.52, 30.60, "키가 작아 안 보일까 봐"), (30.78, 34.40, "손을 번쩍 들었어요"),
          (34.62, 37.50, "차가 섰나 한 번 더 보고"), (37.64, 40.90, "왼쪽 오른쪽 건너요"),
          (41.14, 44.60, "걸음이 좀 느려도 괜찮아"), (44.72, 48.10, "초록불 끝까지 기다려줘요"),
          (48.28, 51.40, "우리 손주 손 꼭 잡고"), (51.52, 55.80, "천천히 가도 다 도착해요"),
          (56.96, 61.20, "거북이 모드 ON! 삼십! 삼십!"), (61.36, 64.20, "할머니도 아이도 천천히 건너요"),
          (64.30, 67.70, "거북이 모드 ON! 삼십! 삼십!"), (67.84, 71.60, "여기서부턴 느려도 멋져요"),
          (72.08, 75.30, "안전띠는 찰칵! 뒷자리도 찰칵!"), (75.42, 78.80, "돌기 전엔 깜빡! 깜빡이 깜빡!"),
          (78.94, 81.60, "킥보드엔 헬멧! 꼭! 꼭! 꼭!"),
          (81.84, 86.30, "거북이 모드 ON! 삼십! 삼십!"), (86.40, 89.20, "할머니도 아이도 천천히 건너요"),
          (89.28, 92.70, "거북이 모드 ON! 삼십! 삼십!"), (92.80, 96.40, "여기서부턴 느려도 멋져요"),
          (97.22, 98.70, "토끼는 찰칵~"), (98.76, 100.10, "거북이는 씨익~"), (100.16, END_AT, "이 동네에선 거북이가 이겨요")]

def run(args): subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)
fr = lambda t: int(round(t * FPS))

def mean_rgb(path, t0, dur):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t0:.3f}", "-t", f"{dur:.3f}", "-i", path, "-vf",
                          "fps=4,scale=64:36", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, 3).mean(0)

# ---- 1. per-shot colour statistics -> gains toward the median look (clamped, gentle)
stats = []
for src, cin, a, b, opt in SHOTS:
    p = src[1:] if src.startswith("@") else f"clips_ad/{src}.mp4"
    stats.append(np.array(Image.open(p).convert("RGB").resize((64, 36))).reshape(-1, 3).mean(0) if src.startswith("@")
                 else mean_rgb(p, cin, min(b - a, (opt or {}).get("raw_end", 5.0) - cin)))
target = np.median(np.array(stats), axis=0)
gains = [np.clip(target / s, 0.93, 1.07) for s in stats]

# ---- 2. flash bloom sprite (radial glow + horizontal streak)
R = 300
yy, xx = np.mgrid[-R:R, -R:R]
d = np.sqrt(xx ** 2 + yy ** 2) / R
glow = np.clip(1 - d, 0, 1) ** 2.2
streak = np.exp(-(yy / 10.0) ** 2) * np.clip(1 - np.abs(xx) / R, 0, 1) ** 1.5 * 0.8
a = np.clip(glow + streak, 0, 1)
sprite = np.dstack([np.full_like(a, 255), np.full_like(a, 252), np.full_like(a, 240), a * 255]).astype(np.uint8)
Image.fromarray(sprite, "RGBA").save(f"{TMP}/bloom.png")

# ---- 3. render each shot (exact frame count + SOFT overlap frames, except the last)
parts, starts = [], []
for i, (src, cin, a, b, opt) in enumerate(SHOTS):
    opt = opt or {}
    xf = opt.get("xf", None)
    n = fr(b) - fr(a) + SOFT
    out = f"{TMP}/{i:02d}.mp4"
    g = gains[i]
    cm = f"colorchannelmixer=rr={g[0]:.3f}:gg={g[1]:.3f}:bb={g[2]:.3f}"
    if src.startswith("@"):
        z = f"zoompan=z='1+0.06*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={W}x{H}:fps={FPS}"
        run(["-i", src[1:], "-vf", f"scale=3840:-2,{z},{cm}", "-frames:v", str(n), "-pix_fmt", "yuv420p", out])
    else:
        avail = opt.get("raw_end", 5.04) - cin
        need = n / FPS
        slow = need / avail if need > avail + 0.02 else 1.0
        vf = (xf + "," if xf else "") + f"scale={W}:{H}:flags=lanczos,setsar=1"
        if slow > 1.0:
            vf += f",setpts=PTS*{slow:.4f},minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1"
        vf += f",fps={FPS},{cm}"
        if src == "A15":   # flash fires from the flash unit itself
            lt = FLASH_T - (fr(a) - 1) / FPS   # shot-local time (shot starts one frame before its bar)
            vf_full = (f"[0]{vf}[v];[1]format=rgba,fade=t=out:st={lt + 0.06:.3f}:d=0.30:alpha=1[bl];"
                       f"[v][bl]overlay={FLASH_XY[0] - R}:{FLASH_XY[1] - R}:enable='between(t,{lt:.3f},{lt + 0.36:.3f})',"
                       f"eq=brightness='if(between(t,{lt:.3f},{lt + 0.25:.3f}),0.35*(1-(t-{lt:.3f})/0.25),0)':eval=frame[o]")
            run(["-ss", f"{cin:.3f}", "-i", f"clips_ad/{src}.mp4", "-loop", "1", "-i", f"{TMP}/bloom.png",
                 "-filter_complex", vf_full, "-map", "[o]", "-frames:v", str(n), "-an", "-pix_fmt", "yuv420p", out])
        elif opt.get("patch"):
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{cin:.3f}", "-i", f"clips_ad/{src}.mp4", "-frames:v", "1",
                            f"{TMP}/p_{i}.png"], check=True)
            base = Image.open(f"{TMP}/p_{i}.png").convert("RGBA")
            lay = Image.new("RGBA", base.size, (0, 0, 0, 0))
            for (x0, y0, x1, y1) in opt["patch"]:
                m = Image.new("L", base.size, 0)
                ImageDraw.Draw(m).rectangle((x0 + 8, y0 + 8, x1 - 8, y1 - 8), fill=255)
                m = m.filter(ImageFilter.GaussianBlur(4))
                lay = Image.composite(base, lay, m)
            lay.save(f"{TMP}/p_{i}.png")
            run(["-ss", f"{cin:.3f}", "-i", f"clips_ad/{src}.mp4", "-loop", "1", "-i", f"{TMP}/p_{i}.png",
                 "-filter_complex", f"[0][1]overlay=0:0:shortest=0,{vf}[o]", "-map", "[o]", "-frames:v", str(n), "-an",
                 "-pix_fmt", "yuv420p", out])
        else:
            run(["-ss", f"{cin:.3f}", "-i", f"clips_ad/{src}.mp4", "-vf", vf, "-frames:v", str(n), "-an",
                 "-pix_fmt", "yuv420p", out])
    parts.append(out); starts.append(a)

# ---- 4. end card: freeze of the exact last frame of the A18 shot + tagline + logo
last_raw = END_AT - 100.16
run(["-ss", f"{last_raw:.3f}", "-i", "clips_ad/A18.mp4", "-frames:v", "1", "-vf",
     f"scale={W}:{H}:flags=lanczos,colorchannelmixer=rr={gains[-1][0]:.3f}:gg={gains[-1][1]:.3f}:bb={gains[-1][2]:.3f}",
     f"{TMP}/last.png"])
logo = Image.open("refs/koroad_logo.png").convert("RGBA")
logo = logo.resize((600, round(600 * logo.height / logo.width)), Image.LANCZOS)
card = Image.new("RGBA", (logo.width + 70, logo.height + 50), (0, 0, 0, 0))
ImageDraw.Draw(card).rounded_rectangle((0, 0, card.width - 1, card.height - 1), 28, fill=(255, 255, 255, 240))
card.alpha_composite(logo, (35, 25)); card.save(f"{TMP}/logo_card.png")
nend = fr(TOTAL) - fr(END_AT)
run(["-loop", "1", "-i", f"{TMP}/last.png", "-loop", "1", "-i", f"{TMP}/logo_card.png", "-filter_complex",
     f"[0]fps={FPS},format=yuv420p,"
     f"drawtext=fontfile='{FONT}':text='이 동네에선':fontsize=84:fontcolor=white:borderw=8:bordercolor=0x2e5e1e:x=(w-tw)/2:y=80:alpha='min(1,max(0,(t-0.2)/0.4))',"
     f"drawtext=fontfile='{FONT}':text='거북이가 이겨요':fontsize=116:fontcolor=0xffe14d:borderw=10:bordercolor=0x2e5e1e:x=(w-tw)/2:y=185:alpha='min(1,max(0,(t-0.5)/0.4))',"
     f"drawtext=fontfile='{FONT}':text='어린이·노인 보호구역은 시속 30km':fontsize=54:fontcolor=white:borderw=6:bordercolor=0x2e5e1e:x=(w-tw)/2:y=330:alpha='min(1,max(0,(t-1.2)/0.4))'[bg];"
     f"[1]format=rgba,fade=t=in:st=1.8:d=0.4:alpha=1[lg];[bg][lg]overlay=(W-w)/2:H-h-60,"
     f"fade=t=out:st={nend / FPS - 1.0:.3f}:d=1.0", "-frames:v", str(nend), "-pix_fmt", "yuv420p", f"{TMP}/99.mp4"])
parts.append(f"{TMP}/99.mp4"); starts.append(END_AT)

# ---- 5. join: every cut is a SOFT-frame dissolve centred on the bar line (each part carries SOFT
#         extra frames, the incoming shot starts one frame before the bar). The end card is a freeze
#         of the A18 frame at the cut, so that join is visually seamless.
ins, fc, prev = [], [], "[p0]"
for p in parts: ins += ["-i", p]
fc += [f"[{k}:v]settb=AVTB,setpts=PTS-STARTPTS,format=yuv420p[p{k}]" for k in range(len(parts))]
for k in range(1, len(parts)):
    off = (fr(starts[k]) - 1) / FPS
    fc.append(f"{prev}[p{k}]xfade=transition=fade:duration={SOFT / FPS:.4f}:offset={off:.4f}[v{k}]")
    prev = f"[v{k}]"
run([*ins, "-filter_complex", ";".join(fc), "-map", prev, "-c:v", "libx264", "-crf", "15", "-preset", "medium",
     "-pix_fmt", "yuv420p", "-r", str(FPS), f"{TMP}/video.mp4"])

# ---- 6. audio: the whole song, untouched, + shutter on the flash; loudness for web
run(["-i", SONG, "-i", "audio/shutter_st.wav", "-filter_complex",
     f"[0]aformat=sample_rates=48000:channel_layouts=stereo[s];"
     f"[1]aformat=sample_rates=48000:channel_layouts=stereo,volume=1.4,adelay={int(FLASH_T * 1000)}:all=1[f];"
     f"[s][f]amix=inputs=2:normalize=0,apad=whole_dur={TOTAL},afade=t=out:st={TOTAL - 1.0}:d=1.0,"
     f"loudnorm=I=-16:TP=-2:LRA=11,alimiter=limit=0.70:level=false[a]",
     "-map", "[a]", "-ar", "48000", "-t", f"{TOTAL}", f"{TMP}/audio.wav"])

# ---- 7. lyric captions + mux
dt = ",".join(f"drawtext=fontfile='{FONT}':text='{c}':fontsize=56:fontcolor=white:borderw=6:bordercolor=0x2e5e1e:"
              f"x=(w-tw)/2:y=h-130:enable='between(t,{s:.2f},{e:.2f})'" for s, e, c in LYRICS)
run(["-i", f"{TMP}/video.mp4", "-i", f"{TMP}/audio.wav", "-vf", dt, "-c:v", "libx264", "-crf", "17", "-preset", "slow",
     "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", "-shortest", OUT])
json.dump({"shots": [(s[0], round(s[2], 3), round(s[3], 3)) for s in SHOTS], "gains": [g.round(3).tolist() for g in gains]},
          open(f"{TMP}/manifest.json", "w"), ensure_ascii=False, indent=1)
print("done", TOTAL, "s ->", OUT)
