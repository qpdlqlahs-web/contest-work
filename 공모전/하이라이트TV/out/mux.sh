#!/bin/bash
# usage: mux.sh main|short outname
cd "$(dirname "$0")/.."
m=$1; o=$2
J=$(ffmpeg -hide_banner -i out/_work/${m}_mix.wav -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
IL=$(echo "$J" | grep input_i | sed 's/[^-0-9.]//g'); TP=$(echo "$J" | grep input_tp | sed 's/[^-0-9.]//g'); LRA=$(echo "$J" | grep input_lra | sed 's/[^-0-9.]//g'); TH=$(echo "$J" | grep input_thresh | sed 's/[^-0-9.]//g'); OFF=$(echo "$J" | grep target_offset | sed 's/[^-0-9.]//g')
echo "measured $IL $TP $LRA $TH $OFF"
ffmpeg -v error -y -i out/_work/${m}_video.mp4 -i out/_work/${m}_mix.wav -map 0:v -map 1:a -c:v copy \
 -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$IL:measured_TP=$TP:measured_LRA=$LRA:measured_thresh=$TH:offset=$OFF:linear=true,aresample=48000" \
 -c:a aac -b:a 320k -shortest -movflags +faststart out/$o
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,duration,bit_rate,sample_rate,channels -of compact out/$o
ffmpeg -hide_banner -nostats -i out/$o -af ebur128=peak=true -f null - 2>&1 | tail -12 | grep -E "I:|LRA:|Peak:"
