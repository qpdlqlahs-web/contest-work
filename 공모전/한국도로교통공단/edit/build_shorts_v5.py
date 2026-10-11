"""Shorts v5 (9:16, 24 fps): ONE continuous piece of the song (chorus 2 -> end, no audio splices),
one shot per lyric line, 3-frame soft cuts, colour matching, flash composited on the camera's flash unit.
usage: python edit/build_shorts_v5.py [out.mp4]"""
import os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw

os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")
OUT = sys.argv[1] if len(sys.argv) > 1 else "edit/shorts_v5.mp4"
FPS, W, H = 24, 1080, 1920
SONG = "거북이 모드.wav"
FONT = r"C\:/Windows/Fonts/NotoSansCJKkr-Black.otf"   # SIL OFL
BAR0, BAR = 0.348, 60 / 136 * 4
bar = lambda k: BAR0 + BAR * k
S0 = 56.70                       # song time where the short starts (just before chorus 2 downbeat)
SONG_OUT = 111.30                # song time where the short ends
END_AT = bar(59)                 # end card after the last sung line
SOFT = 3
B = 2 * BAR / 4                  # bridge vocals start half a bar late
TMP = "edit/tmp_s5"; os.makedirs(TMP, exist_ok=True)
SPEEDO = f"{TMP}/speedo.png"     # vertical crop of the dashboard still (needle exactly 30)
im = Image.open("keyframes_ad/A06.png"); w, h = im.size; cw = round(h * 9 / 16); cx = round(w * 0.47)
im.crop((cx - cw // 2, 0, cx + cw // 2, h)).save(SPEEDO)

# (source, in-point, song start, song end, options). options: cx = crop centre x for 16:9 sources,
# patch = boxes copied from the first frame, still = image with slow push-in
SHOTS = [
    ("clips/S01.mp4", 0.0, S0, 59.05, {}),                                   # 거북이 모드 ON! (shell pops on)
    (SPEEDO, 0, 59.05, bar(34), {"still": True}),                            # 삼십! 삼십!
    ("clips/S04.mp4", 0.0, bar(34), bar(36), {}),                            # 할머니도 아이도 천천히 건너요
    ("clips/S05.mp4", 0.0, bar(36), bar(38), {}),                            # 거북이 모드 ON! 삼십! 삼십!
    ("clips/S06.mp4", 0.0, bar(38), bar(40) + B, {}),                        # 여기서부턴 느려도 멋져요
    ("clips/S07.mp4", 0.0, bar(40) + B, bar(42) + B, {}),                    # 안전띠는 찰칵
    ("clips/S08.mp4", 0.0, bar(42) + B, bar(44) + B, {}),                    # 돌기 전엔 깜빡
    ("clips/S09.mp4", 0.0, bar(44) + B, bar(46), {}),                        # 킥보드엔 헬멧
    ("clips_ad/A17.mp4", 0.0, bar(46), bar(48), {"cx": 1010, "raw_end": 3.1}),          # 거북이 모드 ON
    ("clips_ad/V6.mp4", 0.0, bar(48), bar(50), {"cx": 1050}),                           # 할머니도 아이도 (hands held, walk signal)
    ("clips_ad/A20.mp4", 0.0, bar(50), bar(52), {"cx": 1450}),                           # 거북이 모드 ON
    ("clips_ad/N2.mp4", 0.0, bar(52), bar(54), {"cx": 1180}),                            # 여기서부턴 느려도 멋져요
    ("clips/S10.mp4", 0.0, bar(54), 97.87, {"flash": (805, 470, 2.08)}),                 # 토끼는 찰칵 (flash at 97.72)
    ("kf2/S10e.png", 0, 97.87, 98.76, {"still": True}),                    # caught: ears drop
    ("clips/S11.mp4", 2.5, 98.76, 100.16, {}),                                           # 거북이는 씨익
    ("clips/S12.mp4", 0.0, 100.16, END_AT, {"overlay": "edit/s12_fill.png"}),             # (English SCHOOL text on the sign painted out)                                          # 이 동네에선 거북이가 이겨요
]
FLASH_T = 97.72
LYRICS = [(56.96, 58.95, "거북이 모드 ON!"), (59.05, 60.30, "삼십! 삼십!"),
          (61.36, 64.20, "할머니도 아이도 천천히 건너요"), (64.30, 67.70, "거북이 모드 ON! 삼십! 삼십!"),
          (67.84, 71.60, "여기서부턴 느려도 멋져요"),
          (72.08, 75.30, "안전띠는 찰칵! 뒷자리도 찰칵!"), (75.42, 78.80, "돌기 전엔 깜빡! 깜빡이 깜빡!"),
          (78.94, 81.60, "킥보드엔 헬멧! 꼭! 꼭! 꼭!"),
          (81.84, 86.30, "거북이 모드 ON! 삼십! 삼십!"), (86.40, 89.20, "할머니도 아이도 천천히 건너요"),
          (89.28, 92.70, "거북이 모드 ON! 삼십! 삼십!"), (92.80, 96.40, "여기서부턴 느려도 멋져요"),
          (97.22, 98.70, "토끼는 찰칵~"), (98.76, 100.10, "거북이는 씨익~"), (100.16, END_AT, "이 동네에선 거북이가 이겨요")]

def run(args): subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)
fr = lambda t: int(round((t - S0) * FPS))   # song time -> output frame index

def src_filter(path, opt):
    """crop/scale filter that turns a source into 1080x1920"""
    if path.startswith("clips_ad/"):
        x0 = max(0, min(1928 - 605, opt["cx"] - 302))
        return f"crop=605:1076:{x0}:0,scale={W}:{H}:flags=lanczos,setsar=1"
    return f"scale={W}:{H}:flags=lanczos,setsar=1"

# 1. colour statistics
def mean_rgb(path, cin, dur, opt):
    if opt.get("still"):
        return np.array(Image.open(path).convert("RGB").resize((36, 64))).reshape(-1, 3).mean(0)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{cin:.3f}", "-t", f"{dur:.3f}", "-i", path, "-vf",
                          src_filter(path, opt) + ",fps=4,scale=36:64", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, 3).mean(0)
stats = [mean_rgb(p, c, min(b - a, opt.get("raw_end", 5.0) - c), opt) for p, c, a, b, opt in SHOTS]
target = np.median(np.array(stats), axis=0)
gains = [np.clip(target / s, 0.93, 1.07) for s in stats]

# 2. flash bloom sprite
R = 220
yy, xx = np.mgrid[-R:R, -R:R]
d = np.sqrt(xx ** 2 + yy ** 2) / R
a = np.clip(np.clip(1 - d, 0, 1) ** 2.2 + np.exp(-(yy / 8.0) ** 2) * np.clip(1 - np.abs(xx) / R, 0, 1) ** 1.5 * 0.8, 0, 1)
Image.fromarray(np.dstack([np.full_like(a, 255), np.full_like(a, 252), np.full_like(a, 240), a * 255]).astype(np.uint8),
                "RGBA").save(f"{TMP}/bloom.png")

# 3. shots
parts, starts = [], []
for i, (path, cin, a, b, opt) in enumerate(SHOTS):
    n = fr(b) - fr(a) + SOFT
    out = f"{TMP}/{i:02d}.mp4"
    g = gains[i]
    cm = f"colorchannelmixer=rr={g[0]:.3f}:gg={g[1]:.3f}:bb={g[2]:.3f}"
    if opt.get("still"):
        z = f"zoompan=z='1+0.05*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={W}x{H}:fps={FPS}"
        run(["-i", path, "-vf", f"scale=-2:3840,{z},{cm}", "-frames:v", str(n), "-pix_fmt", "yuv420p", out])
    else:
        avail = opt.get("raw_end", 5.04) - cin
        need = n / FPS
        vf = src_filter(path, opt)
        if need > avail + 0.02:
            vf += f",setpts=PTS*{need / avail:.4f},minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1"
        vf += f",fps={FPS},{cm}"
        ins = ["-ss", f"{cin:.3f}", "-i", path]
        if opt.get("patch"):
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{cin:.3f}", "-i", path, "-frames:v", "1", f"{TMP}/p_{i}.png"], check=True)
            base = Image.open(f"{TMP}/p_{i}.png").convert("RGBA"); lay = Image.new("RGBA", base.size, (0, 0, 0, 0))
            for (x0, y0, x1, y1) in opt["patch"]:
                m = Image.new("L", base.size, 0); ImageDraw.Draw(m).rectangle((x0 + 8, y0 + 8, x1 - 8, y1 - 8), fill=255)
                lay = Image.composite(base, lay, m)
            lay.save(f"{TMP}/p_{i}.png")
            ins += ["-loop", "1", "-i", f"{TMP}/p_{i}.png"]
            fc = f"[0][1]overlay=0:0:shortest=0,{vf}[o]"
        elif opt.get("overlay"):
            ins += ["-loop", "1", "-i", opt["overlay"]]
            fc = f"[0][1]overlay=0:0:shortest=0,{vf}[o]"
        elif opt.get("flash"):
            fx, fy, raw_t = opt["flash"]
            lt = raw_t - cin            # shot-local time of the flash (shot starts one frame early)
            lt += 1 / FPS
            ins += ["-loop", "1", "-i", f"{TMP}/bloom.png"]
            fc = (f"[0][1]overlay={fx - R}:{fy - R}:shortest=0:enable='between(t,{lt:.3f},{lt + 0.34:.3f})',"
                  f"{vf},eq=brightness='if(between(t,{lt:.3f},{lt + 0.25:.3f}),0.35*(1-(t-{lt:.3f})/0.25),0)':eval=frame[o]")
        else:
            fc = f"[0]{vf}[o]"
        run([*ins, "-filter_complex", fc, "-map", "[o]", "-frames:v", str(n), "-an", "-pix_fmt", "yuv420p", out])
    parts.append(out); starts.append(a)

# 4. end card
last_raw = END_AT - 100.16
run(["-ss", f"{last_raw:.3f}", "-i", "clips/S12.mp4", "-i", "edit/s12_fill.png", "-frames:v", "1", "-filter_complex",
     f"[0][1]overlay=0:0,scale={W}:{H}:flags=lanczos,colorchannelmixer=rr={gains[-1][0]:.3f}:gg={gains[-1][1]:.3f}:bb={gains[-1][2]:.3f}",
     f"{TMP}/last.png"])
logo = Image.open("refs/koroad_logo.png").convert("RGBA")
logo = logo.resize((720, round(720 * logo.height / logo.width)), Image.LANCZOS)
card = Image.new("RGBA", (logo.width + 80, logo.height + 60), (0, 0, 0, 0))
ImageDraw.Draw(card).rounded_rectangle((0, 0, card.width - 1, card.height - 1), 34, fill=(255, 255, 255, 240))
card.alpha_composite(logo, (40, 30)); card.save(f"{TMP}/logo_card.png")
nend = fr(SONG_OUT) - fr(END_AT)
run(["-loop", "1", "-i", f"{TMP}/last.png", "-loop", "1", "-i", f"{TMP}/logo_card.png", "-filter_complex",
     f"[0]fps={FPS},format=yuv420p,"
     f"drawtext=fontfile='{FONT}':text='이 동네에선':fontsize=96:fontcolor=white:borderw=8:bordercolor=0x2e5e1e:x=(w-tw)/2:y=300:alpha='min(1,max(0,(t-0.2)/0.4))',"
     f"drawtext=fontfile='{FONT}':text='거북이가 이겨요':fontsize=124:fontcolor=0xffe14d:borderw=10:bordercolor=0x2e5e1e:x=(w-tw)/2:y=425:alpha='min(1,max(0,(t-0.5)/0.4))',"
     f"drawtext=fontfile='{FONT}':text='어린이·노인 보호구역은':fontsize=62:fontcolor=white:borderw=6:bordercolor=0x2e5e1e:x=(w-tw)/2:y=600:alpha='min(1,max(0,(t-1.2)/0.4))',"
     f"drawtext=fontfile='{FONT}':text='시속 30km':fontsize=84:fontcolor=0xffe14d:borderw=8:bordercolor=0x2e5e1e:x=(w-tw)/2:y=680:alpha='min(1,max(0,(t-1.4)/0.4))'[bg];"
     f"[1]format=rgba,fade=t=in:st=1.9:d=0.4:alpha=1[lg];[bg][lg]overlay=(W-w)/2:1640,"
     f"fade=t=out:st={nend / FPS - 1.0:.3f}:d=1.0", "-frames:v", str(nend), "-pix_fmt", "yuv420p", f"{TMP}/99.mp4"])
parts.append(f"{TMP}/99.mp4"); starts.append(END_AT)

# 5. join with soft cuts centred on bar lines
ins, fc, prev = [], [], "[p0]"
for p in parts: ins += ["-i", p]
fc += [f"[{k}:v]settb=AVTB,setpts=PTS-STARTPTS,format=yuv420p[p{k}]" for k in range(len(parts))]
for k in range(1, len(parts)):
    off = (fr(starts[k]) - 1) / FPS
    fc.append(f"{prev}[p{k}]xfade=transition=fade:duration={SOFT / FPS:.4f}:offset={off:.4f}[v{k}]"); prev = f"[v{k}]"
run([*ins, "-filter_complex", ";".join(fc), "-map", prev, "-c:v", "libx264", "-crf", "15", "-pix_fmt", "yuv420p",
     "-r", str(FPS), f"{TMP}/video.mp4"])

# 6. audio: one continuous piece of the song + shutter on the flash
dur = SONG_OUT - S0
run(["-ss", f"{S0}", "-t", f"{dur:.3f}", "-i", SONG, "-i", "audio/shutter_st.wav", "-filter_complex",
     f"[0]aformat=sample_rates=48000:channel_layouts=stereo,afade=t=in:d=0.02[s];"
     f"[1]aformat=sample_rates=48000:channel_layouts=stereo,volume=1.4,adelay={int((FLASH_T - S0) * 1000)}:all=1[f];"
     f"[s][f]amix=inputs=2:normalize=0,afade=t=out:st={dur - 1.2:.3f}:d=1.2,"
     f"loudnorm=I=-14:TP=-2:LRA=11,alimiter=limit=0.72:level=false[a]",
     "-map", "[a]", "-ar", "48000", "-t", f"{dur:.3f}", f"{TMP}/audio.wav"])

# 7. captions (above the Shorts UI) + mux
dt = ",".join(f"drawtext=fontfile='{FONT}':text='{c}':fontsize=66:fontcolor=white:borderw=7:bordercolor=0x2e5e1e:"
              f"x=(w-tw)/2:y=1330:enable='between(t,{s - S0:.2f},{e - S0:.2f})'" for s, e, c in LYRICS)
run(["-i", f"{TMP}/video.mp4", "-i", f"{TMP}/audio.wav", "-vf", dt, "-c:v", "libx264", "-crf", "17", "-preset", "slow",
     "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", "-shortest", OUT])
print("done", round(dur, 2), "s ->", OUT)
