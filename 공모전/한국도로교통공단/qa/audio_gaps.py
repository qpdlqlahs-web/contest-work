"""Flag audible dropouts in a finished video/audio: 50 ms windows that sit far below the
local 2 s median loudness. usage: python qa/audio_gaps.py file [threshold_db=14]"""
import subprocess, sys
import numpy as np

SR, WIN = 22050, 0.05
path = sys.argv[1]
thr = float(sys.argv[2]) if len(sys.argv) > 2 else 14.0
y = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                                 capture_output=True).stdout, dtype=np.float32)
h = int(WIN * SR)
db = np.array([20 * np.log10(np.sqrt(np.mean(y[i:i + h] ** 2)) + 1e-9) for i in range(0, len(y) - h, h)])
half = int(1.0 / WIN)
flags = []
for i, v in enumerate(db):
    med = np.median(db[max(0, i - half):i + half])
    if med > -40 and v < med - thr:
        flags.append((i * WIN, v, med))
# merge consecutive windows into events
events, cur = [], None
for t, v, med in flags:
    if cur and t - cur[1] <= WIN * 1.5:
        cur[1] = t; cur[2] = min(cur[2], v)
    else:
        if cur: events.append(cur)
        cur = [t, t, v, med]
if cur: events.append(cur)
# the source song itself has short staccato rests (<=0.1 s, >= -40 dB); only report what is worse
total = len(db) * WIN
bad = [e for e in events if 0.3 < e[0] < total - 3 and (e[1] + WIN - e[0] >= 0.15 or e[2] < -42)]
print(f"{path}: {len(bad)} real dropout(s) (>=0.15 s or deeper than -42 dB; {len(events) - len(bad)} normal staccato rests ignored)")
for a, b, v, med in bad:
    print(f"  {a:6.2f}-{b + WIN:6.2f}s  min {v:5.1f} dB  (local median {med:5.1f} dB)")
