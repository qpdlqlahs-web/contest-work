#!/bin/bash
# v4 본편: v3 와 같은 loudnorm 선형 게인(측정값 고정)으로 곡 구간 레벨을 v3 와 동일하게 유지
cd "$(dirname "$0")/.."
ffmpeg -v error -y -i out/_work/main_video.mp4 -i out/_work/main_mix.wav -map 0:v -map 1:a -c:v copy \
 -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=-13.72:measured_TP=-2.73:measured_LRA=4.80:measured_thresh=-23.77:offset=-1.46:linear=true,aresample=48000" \
 -c:a aac -b:a 320k -shortest -movflags +faststart out/naJuyeon_main_v4.mp4
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,duration,bit_rate -of compact out/naJuyeon_main_v4.mp4
