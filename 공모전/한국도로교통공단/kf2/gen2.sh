#!/bin/bash
cd "$(dirname "$0")/.."
NT="No text, no letters anywhere except the number 30 if a speed sign is visible."
gen(){ id=$1; ar=$2; refs=""; for r in $3; do refs="$refs --image-references $r"; done
  ( url=$(higgsfield generate create nano_banana_flash --prompt "$4 $NT" $refs --aspect_ratio $ar --resolution 2k --wait 2>&1 | grep -o 'https://[^ ]*\.png' | tail -1)
    [ -n "$url" ] && curl -s -o "kf2/$id.png" "$url" && echo "$id ok" || echo "$id FAIL" ) & }
gen A03e 16:9 "keyframes_ad/A03.png" "Edit this image. Same camera, same street, buildings, lighting and clay style. The red rabbit-car has accelerated TOWARD the camera and is now very close in the right foreground, large and partly cut off by the right frame edge, with motion blur and a clay dust puff, smug face; the plain green car (no shell) is further back in the middle, still calmly driving toward the camera."
gen A07e 16:9 "keyframes_ad/A07.png" "Edit this image. Same camera, same school-zone street, red road, sidewalk and lighting. The red rabbit-car has sped TOWARD the camera and is now very close in the left foreground, large and partly cut off by the left frame edge, with motion blur and a clay dust puff; the grandmother on the sidewalk has jumped back, startled, clutching her bag."
gen A15s 16:9 "kf2/A15e.png" "Edit this image. Keep the camera, street, red road and the speed enforcement camera pole exactly the same. Move the red rabbit-car much further back up the road so it is small in the distance, driving toward the camera, with its long rabbit ears standing straight up and a smug, cocky face; no skid marks."
gen A10e 16:9 "kf2/A10s.png" "Edit this image. Keep the camera, street, crosswalk, the pedestrian signal (bottom green walking-person lamp lit, top red lamp off) and the turtle-car behind the stop line exactly the same. The grandmother and the boy have walked further across the zebra crosswalk to the right and are now about two-thirds of the way across, still holding hands, mid-step."
wait
