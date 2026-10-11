#!/bin/bash
# QA-driven regeneration (Kling 3.0 pro, 5s, no sound)
cd "$(dirname "$0")/.."
PRE="Claymation stop-motion animation, handmade plasticine with fingerprint texture, characters keep their exact designs, cars only have faces on the windshield, no text appearing."
run(){ out=$1; shift
  ( url=$("$@" --duration 5 --mode pro --sound off --wait --wait-timeout 40m 2>&1 | grep -o 'https://[^ ]*\.mp4' | tail -1)
    [ -n "$url" ] && curl -s -o "$out" "$url" && echo "$out ok" || echo "$out FAIL" ) & }
# k OUT START_IMAGE ASPECT PROMPT [END_IMAGE]
k(){ if [ -n "$5" ]; then run "$1" higgsfield generate create kling3_0 --start-image "$2" --end-image "$5" --aspect_ratio "$3" --prompt "$PRE $4"
     else run "$1" higgsfield generate create kling3_0 --start-image "$2" --aspect_ratio "$3" --prompt "$PRE $4"; fi; }

k clips_ad/A03.mp4 keyframes_ad/A03.png 16:9 "Side-tracking shot: the plain green car drives steadily forward; the red rabbit-car comes from behind, overtakes it in one continuous fast move and races away ahead into the distance, ears flapping, clay dust trail. Both cars always move forward in the same direction. The green car never grows a shell."
k clips_ad/A04.mp4 keyframes_fix/A04.png 16:9 "Very slow low-angle push-in toward the 30 speed sign, the child-zone sign and the elderly-zone sign; little clay flowers sway gently; nothing else moves and the signs never change."
k clips_ad/A07.mp4 keyframes_ad/A07.png 16:9 "The red rabbit-car zooms fast from the background toward the camera along the red school-zone road with clay dust and speed lines, passing the grandmother on the sidewalk, who flinches and steps back startled, clutching her bag."
k clips_ad/A10.mp4 keyframes_ad/A10.png 16:9 "The grandmother and the boy walk slowly across the zebra crosswalk hand in hand while the pedestrian signal stays GREEN the whole time; the turtle-car waits patiently behind the stop line, smiling. The traffic light never changes color." keyframes_ad/A10.png
k clips_ad/A11.mp4 keyframes_fix/A11b.png 16:9 "On the far sidewalk the grandmother bows her head politely in thanks and the boy waves; the turtle-car, stopped behind the stop line, winks back cheerfully and does not move forward."
k clips_ad/A14.mp4 keyframes_fix/A14.png 16:9 "The young woman pauses in the bicycle lane and taps her yellow helmet proudly, then puts both hands on the handlebar and rides off safely along the bicycle lane."
k clips_ad/A15.mp4 keyframes_ad/A15.png 16:9 "The rabbit-car speeds along the red road, the enforcement camera's flash unit fires a bright white flash, the rabbit-car brakes hard, its long ears droop down and its mouth drops open in shock. The camera pole stays still."
k clips_ad/A17.mp4 keyframes_fix/A17b.png 16:9 "The turtle-shell cars parade slowly along the road while the schoolchildren on the sidewalk wave happily. The children always stay on the sidewalk."
k clips_ad/A21.mp4 keyframes_fix/A21.png 16:9 "The line of schoolchildren walks across the zebra crosswalk safely while the turtle-shell cars wait patiently behind the stop line; slow high-angle camera drift."
k clips/S05.mp4 keyframes_fix/S05.png 9:16 "The row of turtle-shell cars waits patiently and blinks in sync; the mascot waves its small yellow safety flag and gives a thumbs up; grandma and the boy walk along the sidewalk."
k clips/S09.mp4 keyframes_fix/S09.png 9:16 "The young woman pauses in the bicycle lane and taps her yellow helmet proudly, then puts both hands on the handlebar and rides off safely along the bicycle lane."
k clips/S10.mp4 keyframes_fix/S10.png 9:16 "The rabbit-car speeds along the red road, the enforcement camera's flash unit fires a bright white flash, the rabbit-car brakes hard, its long ears droop down and its mouth drops open in shock. The camera pole stays still."
wait
