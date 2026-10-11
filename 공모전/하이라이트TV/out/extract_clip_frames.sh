#!/bin/bash
# prep\clips 의 4개 클립을 PNG 시퀀스로 풀어 out\_work\frames 에 둔다 (render_video.py 가 사용)
cd "$(dirname "$0")/.."
for k in K1 K2b K3 K4; do mkdir -p out/_work/frames/$k; ffmpeg -v error -y -i prep/clips/$k.mp4 -vsync 0 out/_work/frames/$k/%04d.png; done
