# 클립 전처리: in-out / 배속 / 프리즈 / 1080x1920 Lanczos + 약한 샤픈. C08 물보라는 splash_c08.py 가 이어서 합성.
import subprocess, sys, os, shutil, glob, json

HERE = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")
BASE = HERE.rsplit("/", 1)[0]
SRC = BASE + "/clips"
OUT = HERE + "/clips"
TMP = os.environ.get("CLIP_TMP", "C:/Users/one/AppData/Local/Temp/claude/C--Users-one-Desktop--/78455281-bfb1-4500-a2a1-02eb5397fe60/scratchpad/clipwork")
SHARP = "unsharp=5:5:0.5:5:5:0.0"   # 약한 샤픈(루마만, 0.5)
UP = "scale=1080:1920:flags=lanczos"


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        print(r.stderr)
        raise SystemExit(1)


def extract(name, trim_end=None, trim_start=0.0, speed=1.0, method="mci"):
    """원본 -> 속도 조절 -> 업스케일 -> PNG 시퀀스. speed<1 슬로(minterpolate), >1 빠르게."""
    d = f"{TMP}/{name}"
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    vf = []
    if trim_end is not None or trim_start:
        vf.append(f"trim=start={trim_start}" + (f":end={trim_end}" if trim_end else ""))
    vf.append("setpts=PTS-STARTPTS")
    if speed < 1:
        vf.append("tpad=stop_mode=clone:stop=3")   # 끝 프레임 복제(minterpolate 가 마지막 구간을 못 만드는 것 보정)
        vf.append(f"setpts=PTS/{speed}")
        if method == "mci":
            vf.append("minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1")
        else:
            vf.append("minterpolate=fps=24:mi_mode=blend")
    elif speed > 1:
        vf.append(f"setpts=PTS/{speed}")
        vf.append("fps=24")
    vf += [UP, SHARP]
    run(["ffmpeg", "-v", "error", "-y", "-i", f"{SRC}/{name}.mp4", "-vf", ",".join(vf), "-an", f"{d}/f%03d.png"])
    return sorted(glob.glob(d + "/f*.png"))


def encode(frames, outname):
    """프레임 경로 리스트(중복 허용) -> 24fps CRF12 H.264, 오디오 없음."""
    lst = f"{TMP}/{outname}_list.txt"
    with open(lst, "w", encoding="utf-8") as f:
        for p in frames:
            f.write(f"file '{p}'\nduration {1/24:.6f}\n")
        f.write(f"file '{frames[-1]}'\n")
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-vf", "fps=24,format=yuv420p",
         "-frames:v", str(len(frames)), "-c:v", "libx264", "-preset", "slow", "-crf", "12", "-r", "24", "-an", "-movflags", "+faststart", f"{OUT}/{outname}.mp4"])


def freeze(frames, idx, n):
    """idx 위치 프레임을 n프레임 더 삽입(프리즈)"""
    return frames[:idx + 1] + [frames[idx]] * n + frames[idx + 1:]


if __name__ == "__main__":
    which = sys.argv[1:] or ["C01", "C04", "C08", "C11", "C14"]
    method = os.environ.get("SLOW", "mci")
    os.makedirs(TMP, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    if "C01" in which:   # 0.50-3.00s, 1.25x -> 2.0s (48f)
        fr = extract("C01", trim_start=0.5, trim_end=3.0, speed=1.25)[:48]
        encode(fr, "C01"); print("C01", len(fr))
    if "C04" in which:   # 0-2.40s, 0.8x -> 3.0s(72f), 원본 f55(1-based) 위치에서 0.8s(19f) 프리즈 -> 91f
        fr = extract("C04", trim_end=2.40, speed=0.8, method=method)[:72]
        idx = round((55 - 1) / 0.8)
        fr = freeze(fr, idx, 19)
        encode(fr, "C04"); print("C04", len(fr), "freeze idx", idx)
    if "C08" in which:   # 0-2.625s, 0.75x -> 3.5s(84f) + 마지막 프레임 0.3s(7f) 프리즈 -> 91f. 물보라는 splash_c08.py
        fr = extract("C08", trim_end=2.625, speed=0.75, method=method)[:84]
        fr = fr + [fr[-1]] * 7
        json.dump(fr, open(f"{TMP}/C08_frames.json", "w")); print("C08 base", len(fr))
    if "C11" in which:   # 0-3.0s 그대로(72f) + 마지막 0.8s(19f) 프리즈 -> 91f
        fr = extract("C11", trim_end=3.0, speed=1.0)[:72]
        fr = fr + [fr[-1]] * 19
        encode(fr, "C11"); print("C11", len(fr))
    if "C14" in which:   # 전체 0.8x -> 3.8s (91f)
        fr = extract("C14", speed=0.8, method=method)[:91]
        encode(fr, "C14"); print("C14", len(fr))
