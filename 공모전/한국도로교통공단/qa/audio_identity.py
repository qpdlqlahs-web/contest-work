"""C1 proof: the video's audio is one continuous, unedited piece of the source song.
Aligns globally, then checks loudness-envelope correlation in 2 s windows (a splice shows up as a drop).
usage: python qa/audio_identity.py video song_start_seconds"""
import subprocess, sys
import numpy as np
SR = 8000
def load(p, ss=0.0):
    return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-ss", str(ss), "-i", p, "-vn", "-ac", "1", "-ar", str(SR),
                                         "-f", "f32le", "-"], capture_output=True).stdout, dtype=np.float32)
v = load(sys.argv[1]); s = load("거북이 모드.wav", float(sys.argv[2]))
seg = SR * 15
lag = int(np.argmax(np.correlate(v[:seg + SR // 2], s[:seg], mode="valid")))
v = v[lag:]; n = min(len(v), len(s)) - SR * 3          # ignore the faded tail
h = SR // 20
env = lambda y: np.array([np.sqrt(np.mean(y[i:i + h] ** 2)) for i in range(0, n - h, h)])
ev, es = env(v), env(s)
k = 40; out = []
for i in range(0, len(ev) - k, k // 2):
    if es[i:i + k].std() > 1e-4: out.append((i * h / SR, np.corrcoef(ev[i:i + k], es[i:i + k])[0, 1]))
c = np.array([x for _, x in out])
print(f"{sys.argv[1]}: lag {lag / SR * 1000:.1f} ms | envelope corr over {len(c)} windows: min {c.min():.3f}, median {np.median(c):.3f}")
print("  lowest windows (video time s, corr):", [(round(t, 1), round(x, 3)) for t, x in sorted(out, key=lambda z: z[1])[:4]])
