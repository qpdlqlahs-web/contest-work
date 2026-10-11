#!/bin/bash
# ad video clips: Kling 3.0 pro, 16:9, 5s, image-to-video from keyframes_ad/
cd "$(dirname "$0")/.."
PRE="Claymation stop-motion animation, handmade plasticine with fingerprint texture, characters keep their exact designs, cars only have faces on the windshield, no text appearing."
declare -A M
M[A01]="Slow aerial push-in over the cozy clay neighborhood in morning light; tiny clay people walk, a bird flies across."
M[A02]="The red rabbit-car roars down the alley far too fast, flower pots wobble, laundry flaps wildly, a clay dust trail swirls behind it."
M[A03]="The red rabbit-car overtakes the plain green car laughing smugly, ears flapping; the green car keeps driving calmly and never grows a shell. Camera tracks sideways."
M[A04]="Slow low-angle push-in toward the 30 speed sign and the school-zone sign; little clay flowers sway in the breeze."
M[A06]="The speedometer needle swings down from 60 and settles exactly on 30; the clay turtle bobblehead nods happily."
M[A07]="The red rabbit-car speeds recklessly through the school zone; the grandmother on the sidewalk jumps back startled, clutching her bag."
M[A08]="The boy raises his hand high and waves while he and his grandmother step onto the crosswalk hand in hand, smiling."
M[A09]="The turtle-car waits behind the stop line, blinks slowly and smiles warmly, nodding as if to say go ahead."
M[A10]="Grandma walks slowly across holding the boy's hand while the pedestrian light blinks; the turtle-car waits patiently, smiling."
M[A11]="Grandma bows her head in thanks and the boy waves; the turtle-car winks back cheerfully."
M[A12]="The boy pulls the seatbelt across and clicks it into the buckle with a tiny spark, then grins at grandma, who nods proudly."
M[A13]="The left turn signal blinks on and off in rhythm while the turtle-car winks in sync, then it slowly turns left."
M[A14]="The boy clips his helmet strap, taps the helmet three times proudly, then pushes off on the kick scooter."
M[A15]="The rabbit-car speeds forward, the roadside camera fires a bright white flash, the rabbit-car brakes hard, its ears droop and its mouth drops open."
M[A16]="The mascot wags its index finger no-no at the embarrassed rabbit-car, whose ears droop even lower; then the mascot puts its hands on its hips."
M[A17]="The turtle-shell cars parade slowly along the road while the schoolchildren on the sidewalk wave happily."
M[A18]="Everyone waves at the camera together: the mascot waves, the boy hops with a thumbs up, grandma waves, the turtle-car bounces; slight camera pull-back."
M[A19]="Grandma and the boy dance joyfully with arms up while the turtle-car bounces to the beat behind them."
M[A20]="The mascot dances like a parade leader, arms raised, swaying side to side; the turtle-shell cars behind bounce along slowly."
M[A21]="The line of schoolchildren crosses the crosswalk safely while the turtle-shell cars wait patiently; slow high-angle camera drift."
M[A22]="The turtle-car's face slowly breaks into a sly satisfied grin and raises one eyebrow; a small puff of clay dust rises. Gentle push-in."
run(){ id=$1; shift
  ( url=$("$@" --wait --wait-timeout 40m 2>&1 | grep -o 'https://[^ ]*\.mp4' | tail -1)
    [ -n "$url" ] && curl -s -o "clips_ad/$id.mp4" "$url" && echo "$id ok" || echo "$id FAIL" ) & }
run A05 higgsfield generate create kling3_0 --start-image keyframes_ad/A05a.png --end-image keyframes_ad/A05b.png --prompt "$PRE The plain green car rolls slowly forward onto the red school-zone road; a turtle shell grows and clicks onto its roof with clay sparkle puffs; its eyes turn proud and determined." --duration 5 --mode pro --aspect_ratio 16:9 --sound off
for k in "${!M[@]}"; do
  [ -f "clips_ad/$k.mp4" ] && continue
  run $k higgsfield generate create kling3_0 --start-image keyframes_ad/$k.png --prompt "$PRE ${M[$k]}" --duration 5 --mode pro --aspect_ratio 16:9 --sound off
done
wait
