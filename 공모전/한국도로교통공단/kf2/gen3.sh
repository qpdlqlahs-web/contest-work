#!/bin/bash
cd "$(dirname "$0")/.."
NT="No text, no letters anywhere except the number 30 if a speed sign is visible."
gen(){ id=$1; ar=$2; refs=""; for r in $3; do refs="$refs --image-references $r"; done
  ( url=$(higgsfield generate create nano_banana_flash --prompt "$4 $NT" $refs --aspect_ratio $ar --resolution 2k --wait 2>&1 | grep -o 'https://[^ ]*\.png' | tail -1)
    [ -n "$url" ] && curl -s -o "kf2/$id.png" "$url" && echo "$id ok" || echo "$id FAIL" ) & }
gen A15s 16:9 "kf2/A15e.png" "Edit this image. Keep EVERYTHING exactly the same - the camera angle, the street, the red road, the grey pole with its horizontal arm, the WHITE rectangular camera housing and the small dark square flash unit on the arm, the signboards. Only change the red rabbit-car: move it much further back up the road so it is small in the distance, driving toward the camera, with its long rabbit ears standing straight up and a smug, cocky face; remove the skid marks."
gen A10e 16:9 "kf2/A10s.png" "Edit this image. Keep EVERYTHING exactly the same - camera, street, zebra crosswalk, the pedestrian signal (bottom green walking-person lamp lit, top red lamp off), trees, houses and the turtle-car waiting behind the stop line. Only remove the grandmother and the boy completely, so the crosswalk is empty (they have finished crossing and left the frame)."
wait
