# -*- coding: utf-8 -*-
"""v2 전체 빌드. 선행: python prep_c14b.py, python fix_c04.py (한 번만). C06 교체: python build_v2.py --c06 새파일.png"""
import subprocess, sys
from pathlib import Path
here = Path(__file__).resolve().parent
args = sys.argv[1:]
subprocess.run([sys.executable, "-X", "utf8", "make_audio_v2.py"], cwd=here, check=True)
subprocess.run([sys.executable, "-X", "utf8", "render_v2.py"] + args, cwd=here, check=True)
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", "_work/video_noaudio_v2.mp4", "-i", "_work/mix_final_v2.wav",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-ac", "2", "-t", "59.8",
                "-movflags", "+faststart", "yakbang_v2.mp4"], cwd=here, check=True)
