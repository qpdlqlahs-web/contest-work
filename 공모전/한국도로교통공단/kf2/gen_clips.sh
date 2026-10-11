#!/bin/bash
# round-2 clips: first/last-frame locked motion (Kling 3.0 pro 5s, no sound)
cd "$(dirname "$0")/.."
PRE="Claymation stop-motion animation, handmade plasticine with fingerprint texture, characters keep their exact designs, cars only have faces on the windshield, no text appearing. Static locked-off camera unless stated."
mkdir -p clips_ad/_old2 clips/_old2
for c in A03 A07 A10 A14 A15 A16; do [ -f clips_ad/$c.mp4 ] && mv -f clips_ad/$c.mp4 clips_ad/_old2/; done
[ -f clips/S10.mp4 ] && mv -f clips/S10.mp4 clips/_old2/
run(){ out=$1; shift
  ( url=$("$@" --duration 5 --mode pro --sound off --wait --wait-timeout 40m 2>&1 | grep -o 'https://[^ ]*\.mp4' | tail -1)
    [ -n "$url" ] && curl -s -o "$out" "$url" && echo "$out ok" || echo "$out FAIL" ) & }
K="higgsfield generate create kling3_0"
run clips_ad/A10.mp4 $K --start-image kf2/A10s.png --end-image kf2/A10e.png --aspect_ratio 16:9 --prompt "$PRE The grandmother and the boy walk slowly hand in hand to the right along the zebra crosswalk and leave the frame on the right side. The background, crosswalk and pedestrian signal never move; the bottom green lamp stays lit and the top red lamp stays dark. The turtle-car waits behind the stop line, smiling."
run clips_ad/A15.mp4 $K --start-image kf2/A15s.png --end-image kf2/A15e.png --aspect_ratio 16:9 --prompt "$PRE The red rabbit-car speeds forward toward the camera along the red road and, as it passes the speed enforcement camera, brakes hard; its long ears flop down and its smug face turns shocked. The car only moves forward, never backward. The camera pole never moves."
run clips_ad/A16.mp4 $K --start-image kf2/A16.png --aspect_ratio 16:9 --prompt "$PRE The mascot wags its index finger in a playful no-no at the embarrassed red rabbit-car, then puts its hands on its hips and nods; the rabbit-car stays parked, its drooping ears sag a little lower and it sighs. The car does not drive."
run clips_ad/A03.mp4 $K --start-image keyframes_ad/A03.png --end-image kf2/A03e.png --aspect_ratio 16:9 --prompt "$PRE The red rabbit-car accelerates past the calm plain green car (no shell) and speeds toward the camera, laughing smugly with a clay dust puff. Both cars only move forward toward the camera."
run clips_ad/A07.mp4 $K --start-image keyframes_ad/A07.png --end-image kf2/A07e.png --aspect_ratio 16:9 --prompt "$PRE The red rabbit-car speeds toward the camera along the red school-zone road right past the grandmother, who jumps back startled clutching her bag. The car only moves forward toward the camera."
run clips_ad/A14.mp4 $K --start-image kf2/A14n.png --aspect_ratio 16:9 --prompt "$PRE The young woman taps her yellow helmet proudly, then holds the handlebar with both hands and rides forward inside the bicycle lane. The camera slowly tracks backward with her. The banners stay blank."
run clips/S10.mp4 $K --start-image kf2/S10s.png --end-image kf2/S10e.png --aspect_ratio 9:16 --prompt "$PRE The red rabbit-car speeds forward toward the camera along the red road and, as it passes the speed enforcement camera, brakes hard; its long ears flop down and its smug face turns shocked. The car only moves forward, never backward. The camera pole never moves."
wait
