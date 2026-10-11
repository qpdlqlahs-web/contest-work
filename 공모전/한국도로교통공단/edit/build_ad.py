"""Ad video (16:9, ~93s): Kling clips on the bar grid of 거북이 모드.wav (136 BPM).
Music = instrumental stem for story parts, original mix for jingle parts; dissolves between shots,
crossfaded music joins, synthesized SFX, no narration. usage: python edit/build_ad.py [out.mp4]"""
import subprocess, os, sys
from PIL import Image, ImageDraw
os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")
BAR0, BAR = 0.348, 60 / 136 * 4
bar = lambda k: BAR0 + BAR * k
FULL, INST = "거북이 모드.wav", "audio/inst.wav"
FONT = r"C\:/Windows/Fonts/NotoSansCJKkr-Black.otf"   # SIL OFL: free for commercial use
OUT = sys.argv[1] if len(sys.argv) > 1 else "edit/ad_v3.mp4"
FPS, B2 = 30, BAR * 2
# instrumental beds use only bars without vocal-removal holes (measured: bars 23-29, 32-40 are solid)
SEGS = [(INST, bar(23), bar(29)), (FULL, 0.15, bar(15)), (INST, bar(32), bar(40)), (FULL, bar(40), 111.56)]
XJ = [0.20, 0.08, 0.05]   # equal-power crossfade at each join (last join is the same song position)
HOLD, END = 1.0, 111.56 - 105.94
D, Q = 0.30, 0.10   # dissolve / quick dissolve (montage) lengths
# (source, in-point, duration, transition-after). "@path" = still image with slow push-in
cut = [("A01", 0.0, B2 + BAR, D), ("A02", 0.3, B2, D), ("A03", 2.9, BAR, D),   # A03: only the forward-moving part
       ("A04", 0, 6.2 - 0.15, D), ("A05", 0, bar(7) - 6.2, D), ("@keyframes_ad/A06.png", 0, B2, D),
       ("A08", 0.3, B2, D), ("A09", 0.3, B2, D), ("A10", 0.3, B2, D),
       ("A11", 0.3, B2, D), ("A07", 0.3, B2, Q), ("A15", 1.6, B2, D), ("A16", 0.2, B2 + 0.8, D, 3.0),   # A16 before the ears pop up
       ("A12", 0.3, B2, Q), ("A13", 0.3, B2, Q), ("A14", 0.3, B2 - 0.8, D),
       ("A17", 0.0, B2, D, 3.1, "crop=iw*0.86:ih*0.86:0:0"), ("A19", 0.3, B2, D), ("A20", 0.3, B2, D), ("A21", 0.3, B2, D),
       ("A15", 1.9, bar(56) - bar(54), Q), ("A22", 2.3, BAR, D), ("A18", 0, 105.94 - bar(57), D)]
total = sum(b - a for _, a, b in SEGS)
assert abs(total - sum(c[2] for c in cut) - END) < 0.05

def run(args): subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)

os.makedirs("edit/tmp_ad", exist_ok=True)
parts, starts, t = [], [], 0.0
for i, (c, cin, dur, tr, *mx) in enumerate(cut):
    xf = (mx[1] + ",") if len(mx) > 1 else ""
    out, L = f"edit/tmp_ad/{i:02d}.mp4", dur + tr
    nf = round(L * FPS)
    if c.startswith("@"):
        z = f"zoompan=z='1+0.06*on/{nf}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={nf}:s=1920x1080:fps={FPS}"
        run(["-i", c[1:], "-vf", f"scale=3840:-2,{z}", "-frames:v", str(nf), "-pix_fmt", "yuv420p", out])
    else:
        avail = (mx[0] if mx else 5.04) - cin
        speed = f"setpts=PTS*{L / avail:.4f}," if L > avail else ""
        run(["-ss", str(cin), "-i", f"clips_ad/{c}.mp4", "-vf", f"{speed}{xf}scale=1920:1080,fps={FPS},setpts=PTS-STARTPTS",
             "-frames:v", str(nf), "-an", "-pix_fmt", "yuv420p", out])
    parts.append(out); starts.append(t); t += dur

def tmap(i, raw):
    """timeline time of a raw clip time for shot i (accounts for in-point and slow-down)"""
    c, cin, dur, tr, *mx = cut[i]
    avail = (mx[0] if mx else 5.04) - cin
    k = (dur + tr) / avail if dur + tr > avail else 1.0
    return starts[i] + (raw - cin) * k
RAW_FLASH_A15 = 2.75  # raw time in clips_ad/A15.mp4 when the car passes under the camera
FLASHES = [tmap(11, RAW_FLASH_A15), tmap(20, RAW_FLASH_A15)]

# end card: freeze A18 last frame + tagline + logo
run(["-sseof", "-0.1", "-i", "clips_ad/A18.mp4", "-frames:v", "1", "edit/tmp_ad/last.png"])
logo = Image.open("refs/koroad_logo.png").convert("RGBA")
logo = logo.resize((640, round(640 * logo.height / logo.width)))
card = Image.new("RGBA", (logo.width + 70, logo.height + 50), (0, 0, 0, 0))
ImageDraw.Draw(card).rounded_rectangle((0, 0, card.width - 1, card.height - 1), 30, fill=(255, 255, 255, 235))
card.alpha_composite(logo, (35, 25)); card.save("edit/tmp_ad/logo_card.png")
run(["-loop", "1", "-i", "edit/tmp_ad/last.png", "-loop", "1", "-i", "edit/tmp_ad/logo_card.png", "-filter_complex",
     f"[0]scale=1920:1080,fps={FPS},"
     f"drawtext=fontfile='{FONT}':text='이 동네에선':fontsize=84:fontcolor=white:borderw=8:bordercolor=0x2e5e1e:x=(w-tw)/2:y=90:alpha='min(1,t/0.4)',"
     f"drawtext=fontfile='{FONT}':text='거북이가 이겨요':fontsize=112:fontcolor=0xffe14d:borderw=10:bordercolor=0x2e5e1e:x=(w-tw)/2:y=195:alpha='min(1,max(0,(t-0.3)/0.4))'[bg];"
     "[bg][1]overlay=(W-w)/2:H-h-60:enable='gte(t,0.8)',format=yuv420p",
     "-frames:v", str(round((END + HOLD) * FPS)), "edit/tmp_ad/99.mp4"])
parts.append("edit/tmp_ad/99.mp4")

# video: chained dissolves (each part already carries its transition overlap)
ins, fc, prev = [], [], "[p0]"
for p in parts: ins += ["-i", p]
fc += [f"[{k}:v]fps={FPS},settb=AVTB,format=yuv420p,setsar=1[p{k}]" for k in range(len(parts))]
for k in range(1, len(parts)):
    tr = cut[k - 1][3]
    fc.append(f"{prev}[p{k}]xfade=transition=fade:duration={tr}:offset={starts[k] if k < len(starts) else total - END:.4f}[v{k}]")
    prev = f"[v{k}]"
run([*ins, "-filter_complex", ";".join(fc), "-map", prev, "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p",
     "-t", f"{total + HOLD:.4f}", "edit/tmp_ad/video.mp4"])

# music bed: segments placed on the timeline, equal-power crossfades centred on each join
ins, fl, mix, pos = [], [], [], 0.0
for i, (src, a, b) in enumerate(SEGS):
    pre = XJ[i - 1] / 2 if i > 0 else 0
    post = XJ[i] / 2 if i < len(SEGS) - 1 else 0
    ins += ["-i", src]
    ln = (b - a) + pre + post
    fi = f"afade=t=in:d={pre * 2:.3f}:curve=qsin," if pre else ""
    fo = f"afade=t=out:st={ln - post * 2:.4f}:d={post * 2:.3f}:curve=qsin," if post else ""
    fl.append(f"[{i}]atrim={a - pre:.4f}:{b + post:.4f},asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo,"
              f"{fi}{fo}adelay={int(round((pos - pre) * 1000))}:all=1[m{i}]")
    mix.append(f"[m{i}]"); pos += b - a
# SFX events (file, time in ad seconds, volume)
SFX = [("audio/whoosh.wav", starts[1] + 0.2, 0.9),          # A02 rabbit-car roars down the alley
       ("audio/whoosh.wav", starts[2] + 0.6, 0.7),          # A03 overtake
       ("audio/click_shell.wav", starts[4] + 3.5, 1.2),     # A05 shell clicks into place
       ("audio/whoosh.wav", starts[10] + 0.3, 0.9),         # A07 speeding through the zone
       ("audio/whoosh.wav", starts[11] + 0.15, 0.85),       # A15 rabbit-car rushes at the camera (also fills a vocal-only rest)
       ("audio/shutter_st.wav", FLASHES[0], 1.3),           # A15 camera flash
       ("audio/shutter_st.wav", FLASHES[1], 1.1),           # outro "토끼는 찰칵" flash
       ("audio/ticks.wav", starts[14] + 0.1, 0.8)]          # A13 turn signal
k = len(SEGS)
for j, (f, at, vol) in enumerate(SFX):
    ins += ["-i", f]
    fl.append(f"[{k + j}]aformat=sample_rates=48000:channel_layouts=stereo,volume={vol},adelay={int(at * 1000)}:all=1[s{j}]")
    mix.append(f"[s{j}]")
fl.append("".join(mix) + f"amix=inputs={len(mix)}:normalize=0,apad=pad_dur={HOLD},"
          f"afade=t=out:st={total + HOLD - 1.5:.3f}:d=1.5,loudnorm=I=-16:TP=-2:LRA=11,alimiter=limit=0.70:level=false[a]")
run([*ins, "-filter_complex", ";".join(fl), "-map", "[a]", "-ar", "48000", "-t", f"{total + HOLD:.4f}", "edit/tmp_ad/audio.wav"])

# captions: opening title + lyrics in vocal parts + closing line
s2 = SEGS[0][2] - SEGS[0][1]; s3 = s2 + SEGS[1][2] - SEGS[1][1]; s4 = s3 + SEGS[2][2] - SEGS[2][1]
w = lambda st: s2 + (st - 0.15)
v = lambda st: s4 + (st - bar(40))
LYR = [(w(0.2), w(5.9), "딩! 보호구역에 진입했습니다"), (w(6.2), w(12.6), "거북이 모드를 켭니다"),
       (w(bar(7)), w(bar(9)), "거북이 모드 ON! 삼십! 삼십!"), (w(bar(9)), w(bar(11)), "할머니도 아이도 천천히 건너요"),
       (w(bar(11)), w(bar(13)), "거북이 모드 ON! 삼십! 삼십!"), (w(bar(13)), s3, "여기서부턴 느려도 멋져요"),
       (v(bar(40)) + 0.8, v(bar(42)) + 0.8, "안전띠는 찰칵! 뒷자리도 찰칵!"), (v(bar(42)) + 0.8, v(bar(44)) + 0.8, "돌기 전엔 깜빡! 깜빡이 깜빡!"),
       (v(bar(44)) + 0.8, v(bar(46)), "킥보드엔 헬멧! 꼭! 꼭! 꼭!"),
       (v(bar(46)), v(bar(48)), "거북이 모드 ON! 삼십! 삼십!"), (v(bar(48)), v(bar(50)), "할머니도 아이도 천천히 건너요"),
       (v(bar(50)), v(bar(52)), "거북이 모드 ON! 삼십! 삼십!"), (v(bar(52)), v(bar(54)), "여기서부턴 느려도 멋져요"),
       (v(96.7), v(100.94), "토끼는 찰칵~ 거북이는 씨익~"), (v(100.94), v(105.94), "이 동네에선 거북이가 이겨요")]
flash = "+".join(f"if(between(t,{f:.3f},{f + 0.3:.3f}),0.55*(1-(t-{f:.3f})/0.3),0)" for f in FLASHES)
dt = [f"eq=brightness='{flash}':eval=frame"] + [f"drawtext=fontfile='{FONT}':text='{c}':fontsize=56:fontcolor=white:borderw=6:bordercolor=0x2e5e1e:"
      f"x=(w-tw)/2:y=h-130:enable='between(t,{a:.2f},{b:.2f})'" for a, b, c in LYR]
dt.append(f"drawtext=fontfile='{FONT}':text='어린이와 어르신이 함께 사는':fontsize=60:fontcolor=white:borderw=7:bordercolor=0x2e5e1e:"
          f"x=(w-tw)/2:y=h-250:alpha='if(lt(t,0.5),t/0.5,if(gt(t,4.1),max(0,(4.8-t)/0.7),1))':enable='lt(t,4.8)'")
dt.append(f"drawtext=fontfile='{FONT}':text='우리 동네':fontsize=96:fontcolor=0xffe14d:borderw=9:bordercolor=0x2e5e1e:"
          f"x=(w-tw)/2:y=h-175:alpha='if(lt(t,0.9),max(0,(t-0.4)/0.5),if(gt(t,4.1),max(0,(4.8-t)/0.7),1))':enable='lt(t,4.8)'")
dt.append(f"drawtext=fontfile='{FONT}':text='어린이·노인 보호구역은 시속 30km':fontsize=56:fontcolor=white:borderw=6:bordercolor=0x2e5e1e:"
          f"x=(w-tw)/2:y=h-340:alpha='min(1,max(0,(t-{total - END + 0.5:.2f})/0.4))':enable='gte(t,{total - END + 0.5:.2f})'")
run(["-i", "edit/tmp_ad/video.mp4", "-i", "edit/tmp_ad/audio.wav", "-vf", ",".join(dt), "-c:v", "libx264", "-crf", "18",
     "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k", "-shortest", OUT])
print("done", round(total + HOLD, 2), "s ->", OUT)
