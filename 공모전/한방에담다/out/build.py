# -*- coding: utf-8 -*-
"""전체 빌드: 오디오 믹스 -> 영상 렌더 -> 합치기. C06 교체 시: python build.py --c06 새파일.png"""
import subprocess, sys
from pathlib import Path
here = Path(__file__).resolve().parent
args = sys.argv[1:]
subprocess.run([sys.executable, "-X", "utf8", "make_audio.py"], cwd=here, check=True)
subprocess.run([sys.executable, "-X", "utf8", "render.py"] + args, cwd=here, check=True)
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", "_work/video_noaudio.mp4", "-i", "_work/mix_final.wav",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-ac", "2", "-t", "59.8",
                "-movflags", "+faststart", "yakbang_v1.mp4"], cwd=here, check=True)
