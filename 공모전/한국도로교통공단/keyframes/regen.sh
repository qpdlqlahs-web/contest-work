#!/bin/bash
# regenerate selected keyframes with per-character refs: gen <id> "<refs space-separated>" "<prompt>"
cd "$(dirname "$0")/.."
STYLE="Claymation stop-motion film still, Aardman-like plasticine with visible fingerprint texture, miniature handmade clay Korean neighborhood diorama, soft warm daylight, shallow depth of field, vertical 9:16 composition. Match the reference character images exactly. Cars have a face only on the windshield. No text, no letters, no words."
gen(){ id=$1; refs=""; for r in $2; do refs="$refs --image-references chars/$r.png"; done
  ( url=$(higgsfield generate create nano_banana_flash --prompt "$STYLE $3" $refs --aspect_ratio 9:16 --resolution 2k --wait 2>&1 | grep -o 'https://[^ ]*\.png' | tail -1)
    [ -n "$url" ] && curl -s -o "keyframes/$id.png" "$url" && echo "$id ok" || echo "$id FAIL" ) & }
gen S01 "turtle" "ONLY the green turtle-car in this shot, no people, no other characters. Low angle: it drives onto a red-painted Korean school-zone road, passing a round speed-limit sign showing only the number 30 and a yellow sign with a child silhouette; the turtle shell on its roof is snapping into place with little clay sparkle puffs; its face is proud and determined."
gen S03 "turtle rabbit" "ONLY the two cars, no people. On a street, the red rabbit-car pulls alongside the green turtle-car, laughing smugly, its long rabbit ears flapping in the wind, speed lines made of thin clay strands behind it; the turtle-car looks calm."
gen S04 "grandma boy turtle" "ONLY these three characters. Zebra crosswalk in front of a small clay elementary school: the boy in the yellow jacket raises one hand high while holding his grandmother's hand; the grandmother walks slowly with her cloth bag; the green turtle-car waits behind the stop line in the background, smiling kindly."
gen S09 "boy" "ONLY the boy, no other characters. He stands on an electric kick scooter on a school-zone sidewalk, putting on a bright yellow bicycle helmet and fastening the chin strap, grinning with confidence."
gen S11 "turtle" "ONLY the green turtle-car, empty background street. Close-up of its windshield face with a sly, satisfied grin and happy half-closed eyes, a small puff of clay dust, golden late-afternoon light."
gen S12 "hodungi grandma boy turtle" "Medium shot, characters large in frame filling the lower two thirds: the mascot (traffic-light visor helmet, green suit, seatbelt, bare peach hands) waves happily, standing with the grandmother, the boy, and the green turtle-car, all smiling at camera, on the sidewalk by a school-zone crosswalk at sunset. No rabbit-car. Clean warm sky in the top third for a title."
wait
