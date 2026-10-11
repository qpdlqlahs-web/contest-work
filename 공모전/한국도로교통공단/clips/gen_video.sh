#!/bin/bash
# image-to-video for shorts shots (Kling 3.0 pro; S01 hero on Seedance 2.5)
cd "$(dirname "$0")/.."
PRE="Claymation stop-motion animation, handmade plasticine with fingerprint texture, characters keep their exact designs, cars only have faces on the windshield, no text appearing."
declare -A M
M[S02]="The speedometer needle swings down from 60 and settles exactly on 30; the little clay turtle bobblehead nods happily. Subtle slow push-in."
M[S03]="The red rabbit-car zooms past the turtle-car laughing, its rabbit ears flapping wildly; the turtle-car keeps a calm steady pace. Camera tracks sideways with them."
M[S04]="Holding grandma's hand, the boy raises his other hand high and waves while they cross the zebra crossing slowly; grandma smiles; the turtle-car behind them waits and nods kindly."
M[S05]="The row of turtle-shell cars waits patiently and blinks in sync; the mascot lifts its stop sign and gives a thumbs up; grandma and the boy walk along the sidewalk."
M[S06]="Grandma gives a big thumbs up and the boy jumps for joy as clay confetti falls; the turtle-car in the background bounces happily."
M[S07]="The boy pulls the seatbelt across and clicks it into the buckle with a tiny spark, then grins at grandma, who nods proudly."
M[S08]="The orange turn signal blinks on and off in rhythm while the turtle-car winks in sync, then it slowly turns left."
M[S09]="The boy clips the yellow helmet strap under his chin, taps the helmet three times proudly, then pushes off on the kick scooter."
M[S10]="The red rabbit-car speeds forward, the roadside camera fires a bright white flash, the rabbit-car brakes hard, its rabbit ears droop down in shock and its mouth drops open."
M[S11]="The turtle-car's face slowly breaks into a sly satisfied grin and raises its eyebrows once; a small puff of clay dust rises. Gentle push-in."
M[S12]="Everyone waves at the camera together: the mascot waves both hands, the boy hops, grandma waves, the turtle-car bounces; warm sunset light; slight camera pull-back."
run(){ id=$1; shift
  ( url=$("$@" --wait --wait-timeout 25m 2>&1 | grep -o 'https://[^ ]*\.mp4' | tail -1)
    [ -n "$url" ] && curl -s -o "clips/$id.mp4" "$url" && echo "$id ok" || echo "$id FAIL" ) & }
run S01 higgsfield generate create seedance_2_5 --mode omni_reference --start-image keyframes/S01.png --prompt "$PRE The green turtle-car rolls forward onto the red school-zone road; as it passes the 30 sign, the turtle shell on its roof pops up and clicks down firmly with clay sparkle puffs, and the car slows down proudly, blinking. Low angle, slow push-in." --duration 5 --resolution 720p --aspect_ratio 9:16 --generate_audio false
for k in "${!M[@]}"; do
  run $k higgsfield generate create kling3_0 --start-image keyframes/$k.png --prompt "$PRE ${M[$k]}" --duration 5 --mode pro --aspect_ratio 9:16 --sound off
done
wait
