"""Shorts (9:16, ~53s): clips on the bar grid of 거북이 모드.wav (136 BPM), short dissolves,
crossfaded song joins, lyric captions. usage: python edit/build_shorts.py [out.mp4]"""
import subprocess, os, sys
from PIL import Image, ImageDraw
os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")
BAR0, BAR = 0.348, 60 / 136 * 4
bar = lambda k: BAR0 + BAR * k
SONG = "거북이 모드.wav"
FONT = r"C\:/Windows/Fonts/NotoSansCJKkr-Black.otf"   # SIL OFL: free for commercial use
OUT = sys.argv[1] if len(sys.argv) > 1 else "edit/shorts_v3.mp4"
FPS, B2 = 30, BAR * 2
SEGS = [(0.15, bar(15)), (bar(40), bar(46)), (bar(54), 111.56)]
D, Q = 0.15, 0.04   # soft / near-hard transition
# speedometer: vertical crop of the ad keyframe whose needle reads exactly 30
SPEEDO = "edit/tmp/speedo_9x16.png"
os.makedirs("edit/tmp", exist_ok=True)
im = Image.open("keyframes_ad/A06.png"); w, h = im.size; cw = round(h * 9 / 16); cx = round(w * 0.47)
im.crop((cx - cw // 2, 0, cx + cw // 2, h)).save(SPEEDO)
# (source, in-point, duration, transition-after); "@path" = still with slow push-in
cut = [("S03b", 0, 6.2 - 0.15, D), ("S01", 0, bar(7) - 6.2, D), ("@" + SPEEDO, 0, B2, D), ("S04", 0, B2, D),
       ("S05", 0.5, B2, D), ("S06", 0.5, B2 + 0.8, D),
       ("S07", 0.5, B2, Q), ("S08", 0.5, B2, Q), ("S09", 0.3, B2 - 0.8, D),
       ("S10", 0.3, 1.95, Q), ("@kf2/S10e.png", 0, B2 - 1.95, Q), ("S11", 3.0, BAR, D),
       ("S12", 0, 105.94 - bar(57), D)]   # S10: forward part only, then a photo freeze on the flash
total = sum(b - a for a, b in SEGS)
END = total - sum(c[2] for c in cut)

def run(args): subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)

parts, starts, t = [], [], 0.0
for i, (c, cin, dur, tr) in enumerate(cut):
    out, L = f"edit/tmp/{i:02d}.mp4", dur + tr
    nf = round(L * FPS)
    if c.startswith("@"):
        z = f"zoompan=z='1+0.06*on/{nf}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={nf}:s=1080x1920:fps={FPS}"
        run(["-i", c[1:], "-vf", f"scale=-2:3840,{z}", "-frames:v", str(nf), "-pix_fmt", "yuv420p", out])
    else:
        avail = 5.04 - cin
        speed = f"setpts=PTS*{L / avail:.4f}," if L > avail else ""
        run(["-ss", str(cin), "-i", f"clips/{c}.mp4", "-vf", f"{speed}scale=1080:1920,fps={FPS},setpts=PTS-STARTPTS",
             "-frames:v", str(nf), "-an", "-pix_fmt", "yuv420p", out])
    parts.append(out); starts.append(t); t += dur
def tmap(i, raw):
    c, cin, dur, tr = cut[i]
    avail = 5.04 - cin
    k = (dur + tr) / avail if dur + tr > avail else 1.0
    return starts[i] + (raw - cin) * k
RAW_FLASH_S10 = 2.4   # raw time in clips/S10.mp4 when the car passes under the camera
FLASH = starts[10]   # the freeze-frame starts exactly on the flash

# end card: freeze last frame of S12 + tagline + logo
run(["-sseof", "-0.1", "-i", "clips/S12.mp4", "-frames:v", "1", "edit/tmp/last.png"])
logo = Image.open("refs/koroad_logo.png").convert("RGBA")
logo = logo.resize((760, round(760 * logo.height / logo.width)))
card = Image.new("RGBA", (logo.width + 80, logo.height + 60), (0, 0, 0, 0))
ImageDraw.Draw(card).rounded_rectangle((0, 0, card.width - 1, card.height - 1), 36, fill=(255, 255, 255, 235))
card.alpha_composite(logo, (40, 30)); card.save("edit/tmp/logo_card.png")
run(["-loop", "1", "-i", "edit/tmp/last.png", "-loop", "1", "-i", "edit/tmp/logo_card.png", "-filter_complex",
     f"[0]scale=1080:1920,fps={FPS},"
     f"drawtext=fontfile='{FONT}':text='이 동네에선':fontsize=96:fontcolor=white:borderw=8:bordercolor=0x2e5e1e:x=(w-tw)/2:y=330:alpha='min(1,t/0.4)',"
     f"drawtext=fontfile='{FONT}':text='거북이가 이겨요':fontsize=122:fontcolor=0xffe14d:borderw=10:bordercolor=0x2e5e1e:x=(w-tw)/2:y=460:alpha='min(1,max(0,(t-0.3)/0.4))'[bg];"
     "[bg][1]overlay=(W-w)/2:1580:enable='gte(t,0.8)',format=yuv420p",
     "-frames:v", str(round(END * FPS)), "edit/tmp/99.mp4"])
parts.append("edit/tmp/99.mp4")
ins, fc, prev = [], [], "[p0]"
for p in parts: ins += ["-i", p]
fc += [f"[{k}:v]fps={FPS},settb=AVTB,format=yuv420p,setsar=1[p{k}]" for k in range(len(parts))]
for k in range(1, len(parts)):
    off = starts[k] if k < len(starts) else total - END
    fc.append(f"{prev}[p{k}]xfade=transition=fade:duration={cut[k - 1][3]}:offset={off:.4f}[v{k}]"); prev = f"[v{k}]"
run([*ins, "-filter_complex", ";".join(fc), "-map", prev, "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p",
     "-t", f"{total:.4f}", "edit/tmp/video.mp4"])
# audio: song segments with 0.2s crossfades + camera shutter on the flash
XA, fl, mix, pos = 0.20, [], [], 0.0
for i, (a, b) in enumerate(SEGS):
    pre = XA / 2 if i > 0 else 0; post = XA / 2 if i < len(SEGS) - 1 else 0; ln = b - a + pre + post
    fl.append(f"[0]atrim={a - pre:.4f}:{b + post:.4f},asetpts=PTS-STARTPTS,"
              f"afade=t=in:d={max(pre * 2, 0.01):.3f},afade=t=out:st={ln - max(post * 2, 0.01):.4f}:d={max(post * 2, 0.01):.3f},"
              f"adelay={int((pos - pre) * 1000)}:all=1[m{i}]")
    mix.append(f"[m{i}]"); pos += b - a
fl.append(f"[1]aformat=sample_rates=48000:channel_layouts=stereo,volume=1.2,adelay={int(FLASH * 1000)}:all=1[sf]")
fl.append("".join(mix) + f"[sf]amix=inputs={len(mix) + 1}:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.84:level=false[a]")
run(["-i", SONG, "-i", "audio/shutter_st.wav", "-filter_complex", ";".join(fl), "-map", "[a]", "-ar", "48000",
     "-t", f"{total:.4f}", "edit/tmp/audio.wav"])
# lyric captions (shorts time)
_b = SEGS[0][1] - SEGS[0][0]; _c = _b + SEGS[1][1] - SEGS[1][0]
s = lambda st: st - 0.15
CAPS = [(0.05, 5.75, "딩! 보호구역에 진입했습니다"), (6.05, 12.4, "거북이 모드를 켭니다"),
        (s(bar(7)), s(bar(9)), "거북이 모드 ON! 삼십! 삼십!"), (s(bar(9)), s(bar(11)), "할머니도 아이도 천천히 건너요"),
        (s(bar(11)), s(bar(13)), "거북이 모드 ON! 삼십! 삼십!"), (s(bar(13)), _b, "여기서부턴 느려도 멋져요"),
        (_b + 0.8, _b + 4.33, "안전띠는 찰칵! 뒷자리도 찰칵!"), (_b + 4.33, _b + 7.86, "돌기 전엔 깜빡! 깜빡이 깜빡!"),
        (_b + 7.86, _c, "킥보드엔 헬멧! 꼭! 꼭! 꼭!"),
        (_c + 1.06, _c + 5.26, "토끼는 찰칵~ 거북이는 씨익~"), (_c + 5.26, total - END, "이 동네에선 거북이가 이겨요")]
caps = f"eq=brightness='if(between(t,{FLASH:.3f},{FLASH + 0.3:.3f}),0.55*(1-(t-{FLASH:.3f})/0.3),0)':eval=frame," + ",".join(f"drawtext=fontfile='{FONT}':text='{c}':fontsize=68:fontcolor=white:borderw=7:bordercolor=0x2e5e1e:"
                f"x=(w-tw)/2:y=1360:enable='between(t,{a:.2f},{b:.2f})'" for a, b, c in CAPS)
run(["-i", "edit/tmp/video.mp4", "-i", "edit/tmp/audio.wav", "-vf", caps, "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
     "-c:a", "aac", "-b:a", "256k", "-shortest", OUT])
print("done", round(total, 2), "s ->", OUT)
