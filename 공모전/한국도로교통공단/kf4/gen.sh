#!/bin/bash
cd "$(dirname "$0")/.."
PRE="Claymation stop-motion animation, handmade plasticine with fingerprint texture, characters keep their exact designs, cars only have faces on the windshield, no text appearing, no new objects appear, no traffic lights appear."
( url=$(higgsfield generate create nano_banana_flash --prompt "Edit this image. Keep EVERYTHING identical (camera, framing, grandmother, boy, crosswalk, school building, lighting, clay style). Only make the small name plaque on the school building completely blank (plain beige clay, no letters). No text anywhere." --image-references keyframes_ad/A08.png --aspect_ratio 16:9 --resolution 2k --wait 2>&1 | grep -o 'https://[^ ]*\.png' | tail -1)
  curl -s -o kf4/A08.png "$url" && echo "A08 kf ok"
  url=$(higgsfield generate create kling3_0 --start-image kf4/A08.png --aspect_ratio 16:9 --duration 5 --mode pro --sound off --prompt "$PRE Static locked-off camera. Holding hands, the grandmother and the boy step slowly onto the crosswalk; the boy raises his free hand high and waves, both smiling. The school plaque stays blank." --wait --wait-timeout 40m 2>&1 | grep -o 'https://[^ ]*\.mp4' | tail -1)
  [ -n "$url" ] && mv -f clips_ad/A08.mp4 clips_ad/_old3/A08.mp4 && curl -s -o clips_ad/A08.mp4 "$url" && echo "A08 clip ok" || echo "A08 FAIL" ) &
( url=$(higgsfield generate create kling3_0 --start-image kf3/N1_start.png --aspect_ratio 16:9 --duration 5 --mode pro --sound off --prompt "$PRE Static locked-off camera, the background never moves. Both cars face and drive toward screen-left. The turtle-car drives slowly and calmly to the left. The red rabbit-car speeds up from behind, overtakes the turtle-car and races out of the frame on the left, leaving a clay dust cloud. Nothing else changes." --wait --wait-timeout 40m 2>&1 | grep -o 'https://[^ ]*\.mp4' | tail -1)
  [ -n "$url" ] && mv -f clips_ad/N1.mp4 clips_ad/_old3/N1.mp4 && curl -s -o clips_ad/N1.mp4 "$url" && echo "N1 clip ok" || echo "N1 FAIL" ) &
wait
