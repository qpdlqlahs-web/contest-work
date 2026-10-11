#!/bin/bash
# usage: gen.sh  (generates 9:16 shorts keyframes in parallel)
cd "$(dirname "$0")/.."
STYLE="Claymation stop-motion film still, Aardman-like plasticine with visible fingerprint texture, miniature handmade clay Korean neighborhood diorama, soft warm daylight, shallow depth of field, vertical 9:16 composition. Characters must match the reference lineup image exactly (same designs, colors, faces). Cars have a face only on the windshield. No text, no letters, no words anywhere."
declare -A P
P[S01]="Low angle: the green turtle-car drives onto a red-painted Korean school-zone road past a round speed-limit sign showing only the number 30 and a yellow sign with a child silhouette; the turtle shell on its roof is snapping into place with little clay sparkle puffs; its face is proud and determined."
P[S02]="Extreme close-up of a cute clay car speedometer, the needle pointing exactly at 30, a tiny clay turtle bobblehead on the dashboard nodding, warm light."
P[S03]="On a street, the red rabbit-car pulls alongside the green turtle-car, laughing smugly, its long rabbit ears flapping in the wind, speed lines made of thin clay strands behind it."
P[S04]="Zebra crosswalk in front of a small clay elementary school: the boy in the yellow jacket raises one hand high while holding his grandmother's hand; the grandmother walks slowly with her cloth bag; the green turtle-car waits behind the stop line in the background, smiling kindly."
P[S05]="Wide shot of a school-zone street: a row of several clay cars in different colors, all now wearing turtle shells on their roofs, stopped politely behind the stop line; the green turtle-car is first in line, smiling."
P[S06]="On the sidewalk after crossing: the grandmother gives a big thumbs up and the boy jumps for joy, tiny clay confetti in the air, the green turtle-car in the soft-focus background."
P[S07]="Inside the turtle-car's back seat: the boy pulls his seatbelt across and clicks it into the buckle, a small clay spark at the buckle; the grandmother beside him is also buckled up and smiling; cozy clay car interior."
P[S08]="Front three-quarter view of the green turtle-car at an intersection, its orange turn-signal lamp glowing brightly, its windshield face winking one eye in sync with the blink."
P[S09]="The boy stands on an electric kick scooter on the sidewalk, putting on a bright yellow bicycle helmet and fastening the chin strap, grinning with confidence."
P[S10]="The red rabbit-car speeding is caught by a roadside speed camera that fires a big bright white flash; the rabbit-car's ears droop in shock, eyes wide, mouth open, buck teeth showing."
P[S11]="Close-up of the green turtle-car's windshield face with a sly, satisfied grin and happy half-closed eyes, a small puff of clay dust, golden late-afternoon light."
for k in "${!P[@]}"; do
  ( url=$(higgsfield generate create nano_banana_flash --prompt "$STYLE ${P[$k]}" --image-references chars/lineup_v2.png --aspect_ratio 9:16 --resolution 2k --wait 2>&1 | grep -o 'https://[^ ]*\.png' | tail -1)
    [ -n "$url" ] && curl -s -o "keyframes/$k.png" "$url" && echo "$k ok" || echo "$k FAIL" ) &
done
( url=$(higgsfield generate create nano_banana_flash --prompt "$STYLE Group photo pose on the sidewalk next to the school-zone crosswalk at sunset: the mascot from the second reference image (traffic-light visor helmet, green suit, seatbelt, bare peach hands) waves happily, standing with the grandmother, the boy, and the green turtle-car, all smiling at camera; leave empty sky space in the top third for a title." --image-references chars/lineup_v2.png --image-references refs/hodungi.png --aspect_ratio 9:16 --resolution 2k --wait 2>&1 | grep -o 'https://[^ ]*\.png' | tail -1)
  [ -n "$url" ] && curl -s -o "keyframes/S12.png" "$url" && echo "S12 ok" || echo "S12 FAIL" ) &
wait
